#!/usr/bin/env python3
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import logging
import argparse

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
    "--votes",
    help="How many votes should the question receive (default 1)",
    default = 1,
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

# Set Chrome to Incognito mode
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("incognito")
chrome_options.add_argument("headless")


# Slido settings
slido_id = args.id
slido_qid = args.qid

# How many votes should the question get?
votes = args.votes

# How long to wait until Slido loads?
load_delay = args.max_wait

# Loop through the voting
for i in range(votes):

    # Create Chrome driver and get URL
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f'https://app.sli.do/event/{slido_id}/live/questions?clusterId=eu1')

    # Wait for page to load
    try:
        el = WebDriverWait(driver, load_delay).until(EC.presence_of_element_located((By.XPATH, f'//*[@data-qid="{slido_qid}"]')))
        logger.info("Found question")

        btn = el.find_element("xpath", './/button')
        logger.info("Found button")

        driver.execute_script('arguments[0].click()', btn)
        logger.info("Button clicked")

        current_votes = btn.find_element("xpath", './/span').text
        print(f"Question upvoted. Votes: {current_votes}")

        logger.info("Wait before quitting browser")
        time.sleep(1)

        driver.quit()

    except TimeoutException:
        logger.warn("Loading slido webpage took too long")
