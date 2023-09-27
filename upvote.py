#!/usr/bin/env python3
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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

def upvote_question(slido_id, slido_qid, load_delay, max_votes, queue):
    # Set Chrome to Incognito mode
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("incognito")
    # chrome_options.add_argument("headless")

    # Create Chrome driver and get URL
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f'https://app.sli.do/event/{slido_id}/live/questions?clusterId=eu1')

    stop_voting = False

    # Wait for page to load
    try:
        el = WebDriverWait(driver, load_delay).until(EC.presence_of_element_located((By.ID, 'live-tab-questions')))
        logger.info("Page loaded")

        el = driver.find_element("id", 'live-tab-questions')
        el.click()

        for i in range(0,10):
            try:
                el.find_element("xpath", f'//*[@data-qid="{slido_qid}"]')
            except NoSuchElementException:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                continue
            else:
                break

        el = WebDriverWait(driver, load_delay).until(EC.presence_of_element_located((By.XPATH, f'//*[@data-qid="{slido_qid}"]')))
        logger.info("Found question")

        btn = el.find_element("xpath", './/button')
        logger.info("Found button")

        current_votes = btn.find_element("xpath", './/span').text
        logger.info("Found current votes")
        if int(current_votes) >= max_votes:
            stop_voting = True

        else:
            driver.execute_script('arguments[0].click()', btn)
            logger.info("Button clicked")

            current_votes = btn.find_element("xpath", './/span').text
            print(f"Question upvoted. Votes: {current_votes}")

        logger.info("Wait before quitting browser")
        time.sleep(1)

    except TimeoutException:
        logger.warning("Loading slido webpage took too long")
    except KeyboardInterrupt:
        pass
    finally:
        driver.quit()
        queue.put(stop_voting)


threads = list()
queue = queue.Queue()
logging.info("Using %d threads.", instance_count)

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
            if retval:
                instance_count = instance_count - 1
        except Empty:
            break

    if instance_count <= 0:
        break

