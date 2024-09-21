"""
This module scrapes riverflow data from - https://www.wapda.gov.pk/river-flow
Author - Steven Mugisha Mizero < mmirsteven@gmail.com >
"""

import logging
import os
import traceback
from datetime import datetime
from time import sleep

import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
RIVERFLOW_FILE = os.getenv("riverflow_db_dir")

def scrape_riverflow_table(url: str, year: str) -> pd.DataFrame:
    """
    Scrapes the table return a pandas dataframe with selected columns.
    """

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chromedriver_path = ChromeDriverManager().install()
    os.chmod(chromedriver_path, 0o755)

    with webdriver.Chrome(
        options=chrome_options, service=ChromeService(chromedriver_path)
    ) as driver:
        try:
            driver.get(url)
            # Use WebDriverWait to wait for the select element to be clickable
            select_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        ".MuiSelect-root.MuiSelect-select.MuiSelect-selectMenu.MuiSelect-outlined.MuiInputBase-input.MuiOutlinedInput-input",
                    )
                )
            )
            logger.info("Select element found.")

            # Click on the select element
            select_element.click()

            # Use WebDriverWait to wait for the year option to be clickable
            year_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//li[text()='{year}']"))
            )

            # Click on the year option
            year_option.click()
            # sleep to allow the page to load
            sleep(10)
            logger.info(f"Clicked year: {year} ")

            # Use WebDriverWait to wait for the table element to be present
            table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            logger.info("Table found.")

            table_data = []
            for row in table.text.split("\n")[1:]:
                row = row.split()
                row[0] = row[0] + " " + row[1]
                del row[1]
                table_data.append(row)

            main_scrapped_df = create_main_scrapped_table()
            for row in table_data:
                main_scrapped_df.loc[len(main_scrapped_df)] = row

            main_scrapped_df = select_columns(main_scrapped_df, year)
            main_scrapped_df = (
                main_scrapped_df.apply(lambda x: x.apply(str_to_int)) * 1000
            )
            main_scrapped_df.index = pd.to_datetime(main_scrapped_df.index)
            main_scrapped_df["Year"] = main_scrapped_df.index.year

            logger.info(f" The length of the scraped table {len(main_scrapped_df)}")

        except Exception as e:
            logger.error(f"Error while scrapping from the web: {e}")
            traceback.print_exc()

    return main_scrapped_df


def create_main_scrapped_table() -> pd.DataFrame:
    """
    Creates an empty dataframe with predefined columns.
    """

    COLUMN_NAMES = [
        "Date",
        "Level (Feet) Indus At Tarbela",
        "indus_at_tarbela (cfs)",
        "Outflow Indus At Tarbela",
        "kabul_at_nowshera (cfs)",
        "Level (Feet) Jehlum At Mangla",
        "jhelum_at_mangal (cfs)",
        "Outflow Jehlum At Mangla",
        "cheanab_at_marala (cfs)",
        "Current Year",
        "Last Year",
        "Avg: Last 10-Years",
    ]

    output_table = pd.DataFrame(columns=COLUMN_NAMES)
    return output_table


def update_riverflow_data(url: str):
    """
    This function returns the data for the current year and the previous year.
    """
    try:
        # the years to be used:
        current_year = datetime.now().year
        previous_year = current_year - 1

        # to check which days missing from the dataframe:
        today = datetime.now()
        start_date = datetime(today.year, 1, 1)
        delta = today - start_date
        logger.info(f"The number of days since 1st of January: {delta.days}")

        # loading RIVERFLOW_FILE:
        prod_riverflow_dataset = pd.read_csv(RIVERFLOW_FILE, index_col="Date")
        prod_riverflow_dataset.index = pd.to_datetime(
            prod_riverflow_dataset.index, format="%Y-%m-%d"
        )

        # check if we need to start from the previous year:
        if (
            str(prod_riverflow_dataset.index[-1].year) == str(previous_year)
            and str(prod_riverflow_dataset.index[-1]).split()[0]
            != f"{previous_year}-12-30"
        ):
            logger.info(
                f"Last date in the dataframe { str(prod_riverflow_dataset.index[-1]).split()[0]}"
            )
            logger.info(
                "The previous year riveflow table needs to be scrapped and filled."
            )

            # scrape the previous year data:
            previous_year_df = scrape_riverflow_table(url, previous_year)
            previous_year_df.index = pd.to_datetime(previous_year_df.index)
            previous_year_df = previous_year_df[
                previous_year_df.index > prod_riverflow_dataset.index[-1]
            ]

            # scrape the current year data:
            current_year_df = scrape_riverflow_table(url, current_year)
            current_year_df.index = pd.to_datetime(current_year_df.index)
            current_year_df = current_year_df[
                current_year_df.index > prod_riverflow_dataset.index[-1]
            ]

            prod_riverflow_dataset = pd.concat(
                [prod_riverflow_dataset, previous_year_df, current_year_df], axis=0
            )

            try:
                prod_riverflow_dataset.to_csv(RIVERFLOW_FILE)
                logger.info("Successfully saved the updated riverflow data.")
            except Exception as e:
                logger.error(f"Failed to save the updated riverflow data: {e}")
                traceback.print_exc()

        current_scraped_table = scrape_riverflow_table(url, current_year)
        current_scraped_table.index = pd.to_datetime(current_scraped_table.index)

        THRESHOLD_DAYS = 60
        threshold_date = pd.to_datetime(today) - pd.Timedelta(days=THRESHOLD_DAYS)
        threshold_date = threshold_date.strftime("%Y-%m-%d")

        if len(current_scraped_table):
            if len(current_scraped_table) >= THRESHOLD_DAYS:
                logger.info(
                    f"The current year scraped table length: {len(current_scraped_table)} while the number of days since 1st of January: {delta.days} ."
                )

                current_scraped_table = current_scraped_table[
                    current_scraped_table.index > threshold_date
                ]
                prod_riverflow_dataset = prod_riverflow_dataset[
                    prod_riverflow_dataset.index < threshold_date
                ]
                prod_riverflow_dataset = pd.concat(
                    [prod_riverflow_dataset, current_scraped_table], axis=0
                )

                try:
                    prod_riverflow_dataset.to_csv(RIVERFLOW_FILE)
                    logger.info("Successfully saved the updated riverflow data.")
                except Exception as e:
                    logger.error(f"Failed to save the updated riverflow data: {e}")
                    traceback.print_exc()

            elif len(current_scraped_table) < THRESHOLD_DAYS:

                days_to_get_from_previous_year = THRESHOLD_DAYS - len(
                    current_scraped_table
                )

                logger.info(
                    f"Days to get from the previous year: {days_to_get_from_previous_year}"
                )

                try:
                    last_year_date = f"{previous_year}-12-30"
                    start_date_from_previous_year = pd.to_datetime(
                        last_year_date
                    ) - pd.Timedelta(days=days_to_get_from_previous_year)

                    previous_year_df = scrape_riverflow_table(url, previous_year)
                    previous_year_df.index = pd.to_datetime(previous_year_df.index)

                    if previous_year_df.index[-1] == last_year_date:
                        logger.info(
                            "The last date of the previous year data is equal to the last date of the previous year."
                        )

                        previous_year_df = previous_year_df[
                            previous_year_df.index > start_date_from_previous_year
                        ]

                        prod_riverflow_dataset = prod_riverflow_dataset[
                            prod_riverflow_dataset.index < threshold_date
                        ]
                        prod_riverflow_dataset = pd.concat(
                            [
                                prod_riverflow_dataset,
                                previous_year_df,
                                current_scraped_table,
                            ],
                            axis=0,
                        )

                        try:
                            prod_riverflow_dataset.to_csv(RIVERFLOW_FILE)
                            logger.info(
                                "Successfully saved the updated riverflow data."
                            )
                        except Exception as e:
                            logger.error(
                                f"Failed to save the updated riverflow data: {e}"
                            )
                            traceback.print_exc()

                    # else:
                    #     # Todo: if the last date of the previous year data is not equal to the last date of the previous year.
                    #     logger.info(
                    #         f"The last date of the previous year data is {previous_year_df.index[-1]} not equal to {last_year_date}"
                    #     )
                    #     logger.info("The threshold days will not be applied.")

                    #     last_date_prod_riverflow_data = prod_riverflow_dataset.index[-1]
                    #     current_scraped_table = current_scraped_table[
                    #         current_scraped_table.index > last_date_prod_riverflow_data
                    #     ]

                    #     prod_riverflow_dataset = pd.concat(
                    #         [prod_riverflow_dataset, current_scraped_table], axis=0
                    #     )

                except Exception as e:
                    logger.error(
                        f"Error scrapping {THRESHOLD_DAYS - len(current_scraped_table)} number of days from {previous_year} year: {e}"
                    )
                    traceback.print_exc()
    except Exception as e:
        logger.error(f"Error while updating the riverflow data: {e}")
        traceback.print_exc()


def str_to_int(value):
    """
    Converts a string to an integer or float if possible on the scraped data.
    """
    try:
        parts = value.split(".")
        if len(parts) == 2:
            integer_part = int(parts[0])
            decimal_part = int(parts[1])
            return float(f"{integer_part}.{decimal_part}")
        else:
            return int(value)
    except ValueError:
        return value


def select_columns(main_scrapped_table: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    Filters and transforms the dataframe for a specific year.
    """

    COLUMNS = [
        "Date",
        "indus_at_tarbela (cfs)",
        "kabul_at_nowshera (cfs)",
        "jhelum_at_mangal (cfs)",
        "cheanab_at_marala (cfs)",
    ]

    riverflow_data = main_scrapped_table[COLUMNS]

    riverflow_data = riverflow_data.copy()
    riverflow_data["Date"] = riverflow_data["Date"].apply(lambda x: x.replace(" ", "-"))
    riverflow_data["Date"] = [
        f"{date_str}-{year}" for date_str in riverflow_data["Date"]
    ]
    riverflow_data["Date"] = pd.to_datetime(
        riverflow_data["Date"], format="%d-%b-%Y"
    ).dt.strftime("%Y-%m-%d")
    riverflow_data.set_index("Date", inplace=True)
    riverflow_data.index = pd.to_datetime(riverflow_data.index).strftime("%Y-%m-%d")

    return riverflow_data.sort_index(ascending=True)

# if __name__ == "__main__":
#     URL = "https://www.wapda.gov.pk/river-flow"
#     update_riverflow_data(URL)
