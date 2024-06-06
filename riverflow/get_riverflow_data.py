"""
    Author - Steven Mugisha Mizero
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from time import sleep
import os
import logging
import pandas as pd


from dotenv import load_dotenv

load_dotenv()
RIVERFLOW_FILE = os.getenv("riverflow_db_dir")
THRESHOLD_DAYS = 60

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_riverflow_table(url: str, year: str) -> pd.DataFrame:
    """
    reads the data from the website and returns a dataframe.
    """

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    with webdriver.Chrome(
        options=chrome_options, service=ChromeService(ChromeDriverManager().install())
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
            main_scrapped_df = main_scrapped_df.applymap(str_to_int) * 1000
            main_scrapped_df.index = pd.to_datetime(main_scrapped_df.index)
            main_scrapped_df["Year"] = main_scrapped_df.index.year

            logger.info(f" The length of the table {len(main_scrapped_df)}")

        except Exception as e:
            logger.error(f"Error while scrapping from the web: {e}")
            import traceback

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


def update_riverflow_data(url: str, THRESHOLD_DAYS):
    """
    This function returns the data for the current year and the previous year.
    """
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
        and str(prod_riverflow_dataset.index[-1]).split()[0] != f"{previous_year}-12-30"
    ):
        logger.info(
            f"Last date in the dataframe { str(prod_riverflow_dataset.index[-1]).split()[0]}"
        )
        logger.info("The previous year riveflow needs to be scrapped and filled.")
        previous_year_df = scrape_riverflow_table(url, previous_year)
        previous_year_df.index = pd.to_datetime(previous_year_df.index)
        previous_year_df = previous_year_df[
            previous_year_df.index > prod_riverflow_dataset.index[-1]
        ]

        prod_riverflow_dataset = pd.concat(
            [prod_riverflow_dataset, previous_year_df], axis=0
        )

    # if current_year:
    #     current_year_table = scrape_riverflow_table(url, current_year)

    #     # if  (len(current_year_table) > threshold_days) & (len(current_year_table) == delta.days):
    #     if len(current_year_table) > threshold_days:
    #         current_year_table = select_columns(
    #             current_year_table, current_year
    #         )
    #         # select the last index in the old and new dataframes:
    #         last_date_new_data = current_year_table.index[-1]
    #         last_date = prod_riverflow_dataset.index[-1]

    #         if last_date != last_date_new_data:
    #             before_threshold_day = pd.to_datetime(last_date) - pd.Timedelta(
    #                 days=threshold_days
    #             )
    #             before_threshold_day = before_threshold_day.strftime("%Y-%m-%d")
    #             prod_riverflow_dataset = prod_riverflow_dataset[
    #                 prod_riverflow_dataset.index < before_threshold_day
    #             ]
    #             data_to_append = current_year_table[
    #                 current_year_table.index > before_threshold_day
    #             ]
    #             data_to_append = data_to_append.applymap(str_to_int) * 1000
    #             data_to_append.index = pd.to_datetime(data_to_append.index)
    #             data_to_append["Year"] = data_to_append.index.year
    #             data_to_append.index = pd.to_datetime(data_to_append.index).strftime(
    #                 "%Y-%m-%d"
    #             )

    #             prod_riverflow_dataset = pd.concat(
    #                 [prod_riverflow_dataset, data_to_append], axis=0
    #             )
    #             logger.info(" ------------ Dataframes updated. ------------ ")

    #             # saving the data to csv:
    #             prod_riverflow_dataset.to_csv("riverflow.csv")
    #             logger.info(" ------------ Data saved to csv. ------------ ")

    #         # else:
    #         #     logger.info("Table data is not equal to the number of days since 1st of January")

    #     elif len((current_year_table) < threshold_days):
    #         logger.info(
    #             "Data available is less than the threshold days but equal to the number of days since 1st of January"
    #         )
    #         logger.info(f" The current year table length is: {len(current_year_table)}")
    #         logger.info("Get the previous year data to fill the gap")

    #         previous_year_table = scrape_riverflow_table(url, previous_year)
    #         previous_year_table = select_columns(
    #             previous_year_table, previous_year
    #         )
    #         last_date_new_data = previous_year_table.index[-1]
    #         logger.info(
    #             f" ------------------ Last date of new data is held here: {last_date_new_data} ------------- "
    #         )

    #         days_to_get_from_previous_year = threshold_days - len(current_year_table)

    #         # get the last rows of the previous year table equal to the days_to_get_from_previous_year:
    #         logger.info("Reading the last year table to match the threshold days")
    #         previous_year_table = previous_year_table.tail(
    #             days_to_get_from_previous_year
    #         )

    #         # concat the two dataframes:
    #         combined_table = pd.concat(
    #             [previous_year_table, current_year_table], axis=0
    #         )

    #         last_date = prod_riverflow_dataset.index[-1]

    #         # Then get the last rows of the combined table equal to the threshold days:
    #         before_threshold_day = pd.to_datetime(last_date) - pd.Timedelta(
    #             days=threshold_days
    #         )
    #         before_threshold_day = before_threshold_day.strftime("%Y-%m-%d")
    #         prod_riverflow_dataset = prod_riverflow_dataset[
    #             prod_riverflow_dataset.index < before_threshold_day
    #         ]
    #         data_to_append = combined_table[combined_table.index > before_threshold_day]
    #         data_to_append = data_to_append.applymap(str_to_int) * 1000
    #         data_to_append.index = pd.to_datetime(data_to_append.index)
    #         data_to_append["Year"] = data_to_append.index.year
    #         data_to_append.index = pd.to_datetime(data_to_append.index).strftime(
    #             "%Y-%m-%d"
    #         )
    #         prod_riverflow_dataset = pd.concat(
    #             [prod_riverflow_dataset, data_to_append], axis=0
    #         )
    #         prod_riverflow_dataset["Year"] = prod_riverflow_dataset.index.year
    #         logger.info(" ------------ Dataframes updated. ------------ ")

    #         # saving the data to csv:
    #         prod_riverflow_dataset.to_csv(RIVERFLOW_FILE)
    #         logger.info(" ------------ Data saved to csv. ------------ ")
    #     else:
    #         logger.info("No data at all")

    # else:
    #     logger.info(" ------------ Current year not found. ----------- ")

    # return current_year_table


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


if __name__ == "__main__":
    url = "https://www.wapda.gov.pk/river-flow"
    update_riverflow_data(url, THRESHOLD_DAYS)
