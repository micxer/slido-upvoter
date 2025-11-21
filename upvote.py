#!/usr/bin/env python3
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import logging
import argparse
import threading
import queue
from _queue import Empty

parser = argparse.ArgumentParser(
    prog="Slide Upvoter",
    description="Upvote your question in Slido",
)

parser.add_argument(
    "--id",
    help="The ID of the Slido board",
    required = True,
)
parser.add_argument(
    "--qid",
    help="The ID of the question to upvote",
    required = True,
    type = int,
)
parser.add_argument(
    "--max-wait",
    help="How many seconds to wait for the page to load (default 10)",
    default = 10,
    type = int,
)
parser.add_argument(
    "--max-votes",
    help="How many votes should the question receive (default 1)",
    default = 1,
    type = int,
)
parser.add_argument(
    "--parallel",
    help="How many instances should vote parallel (default 4)",
    default = 4,
    type = int,
)
parser.add_argument(
    "--sleep",
    help="How long to sleep between votes (default 5)",
    default = 5,
    type = int,
)
parser.add_argument("-v", "--verbose", action="store_true")  # on/off flag
args = parser.parse_args()

logging.basicConfig(format="%(asctime)s %(message)s")
if args.verbose:
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.getLogger().setLevel(logging.WARN)
logger = logging.getLogger(__name__)

# Slido settings
slido_id = args.id
slido_qid = args.qid

max_votes = args.max_votes
load_delay = args.max_wait
instance_count = args.parallel

class QuestionNotFoundException(Exception):
    pass

def upvote_question(slido_id, slido_qid, load_delay, max_votes, queue):
    with sync_playwright() as p:
        # Launch browser in incognito mode
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        stop_voting = False

        try:
            # Navigate to the Slido page
            page.goto(f'https://app.sli.do/event/{slido_id}/live/questions?clusterId=eu1')

            # Wait for page to load
            page.wait_for_selector('#live-tabpanel-questions', timeout=load_delay * 1000)
            logger.info("Page loaded")

            # Click questions tab
            questions_tab = page.locator('#live-tabpanel-questions')
            questions_tab.click()
            logger.info("Click questions tab")

            logger.info("Try to scroll the question into view")
            question_found = False

            for i in range(0, 10):
                try:
                    # Check if question exists
                    question_element = page.locator(f'[data-qid="{slido_qid}"]')
                    if question_element.count() > 0:
                        question_found = True
                        logger.info("Found")
                        break
                except Exception as e:
                    logger.warning(f"Exception occurred while searching for question element: {e}")

                logger.info("Not found, scrolling...")
                page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                page.wait_for_timeout(500)  # Small delay after scrolling

                if i == 9:
                    logger.warning("Question not found")
                    raise QuestionNotFoundException()

            if not question_found:
                raise QuestionNotFoundException()

            # Wait for the question element to be present
            question_element = page.wait_for_selector(f'[data-qid="{slido_qid}"]', timeout=load_delay * 1000)
            logger.info("Found question")

            # Find the button within the question element
            button = question_element.query_selector('button')
            if not button:
                logger.warning("Button not found in question")
                stop_voting = True
            else:
                logger.info("Found button")

                # Get current votes
                vote_span = button.query_selector('span')
                current_votes = vote_span.text_content() if vote_span else "0"
                logger.info(f'Found {current_votes} current votes')

                if int(current_votes) >= max_votes:
                    stop_voting = True
                else:
                    # Click the button to upvote
                    button.click()
                    logger.info("Button clicked")

                    # Get updated vote count
                    vote_span = button.query_selector('span')
                    current_votes = vote_span.text_content() if vote_span else "0"
                    print(f"Question upvoted. Votes: {current_votes}")

            logger.info("Wait before quitting browser")
            time.sleep(1)

        except PlaywrightTimeoutError:
            logger.warning("Loading slido webpage took too long")
        except KeyboardInterrupt:
            logger.warning("Stopping voting due to keyboard interrupt")
        except QuestionNotFoundException:
            stop_voting = True
        finally:
            context.close()
            browser.close()
            queue.put(stop_voting)


threads = list()
queue = queue.Queue()
sleep_time = args.sleep
logging.info("Using %d threads and sleep %d between thread starts", instance_count, sleep_time)

while True:
    for index in range(0, instance_count):
        logging.info("Create and start thread %d.", index)
        x = threading.Thread(target=upvote_question, args=(slido_id, slido_qid, load_delay, max_votes, queue))
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        thread.join()
        logging.info("Thread %d done", index)
        threads.remove(thread)

    while True:
        try:
            retval = queue.get_nowait()
            logger.info("Got return value %s", retval)
            if retval:
                instance_count = instance_count - 1
        except Empty:
            break

    if instance_count <= 0:
        break
    else:
        logging.info("Waiting %d seconds...", sleep_time)
        time.sleep(sleep_time)
