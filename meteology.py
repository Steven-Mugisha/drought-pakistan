from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import logging
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import time


# Path: meteology.py
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_year_data(url):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")

    with webdriver.Chrome(
        options=chrome_options, service=ChromeService(ChromeDriverManager().install())
    ) as driver:
        try:
            driver.get(url)
            time.sleep(5)

            temporal_reso_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "select[name='temporalresolution']",
                    )
                )
            )

            driver.execute_script(
                "arguments[0].setAttribute('attribute_name', 'daily');",
                temporal_reso_input,
            )

            select = Select(temporal_reso_input)
            select.select_by_value("daily")

            submit_button = driver.find_element(By.CSS_SELECTOR, "input.submit")
            submit_button.click()
            time.sleep(30)
            # # driver.execute_script("arguments[0].click();", submit_button)

            # Wait for the "Export CSV" link to be clickable
            export_csv_link = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.ID, "output_csv_download"))
            )

            # Scroll to the element
            driver.execute_script("arguments[0].scrollIntoView(true);", export_csv_link)

            # Click the "Export CSV" link
            export_csv_link.click()
            time.sleep(30)

        except Exception as e:
            print(f"Error: {e}")


# test:
url = "https://qed.epa.gov/hms/meteorology/radiation/data_request/"
get_year_data(url)
