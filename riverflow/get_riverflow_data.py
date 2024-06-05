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
import os
import logging
import pandas as pd

from dotenv import load_dotenv

load_dotenv()
RIVERFLOW_FILE = os.getenv("riverflow_db_dir")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_year_riverflow_table(url, year) -> pd.DataFrame:
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
                table.append(row)

            # for each item create a list of each item:
            # table_data = []
            # for item in temp_table:
            #     table_data = [item]

            # list to contain the scrapped table data text:

            # table_data = []
            for row in table.find_elements(By.TAG_NAME, "tr"):
                row_values = []
                for cell in row.find_elements(By.TAG_NAME, "td"):
                    row_values.append(cell.text.strip())
                if row_values:
                    table_data.append(row_values)

            # generate the dataframe for the scraped table data:
            output_table = create_main_scrapped_table()
            for row in table_data[:]:
                output_table.loc[len(output_table)] = row
                output_table = output_table.iloc[::-1]
            logger.info(f" The length of the table {len(output_table)}")

        except Exception as e:
            logger.error(f"------------Error: {e}------------")
            import traceback

            traceback.print_exc()

    return output_table

def scrape_riverflow_data(url, threshold_days=60):
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
    recent_years_riverflow_df = pd.read_csv(RIVERFLOW_FILE, index_col="Date")
    recent_years_riverflow_df.index = pd.to_datetime(recent_years_riverflow_df.index, format="%Y-%m-%d")

    # check if we need to start from the previous year:
    if (
        str(recent_years_riverflow_df.index[-1].year) == str(previous_year)
        and str(recent_years_riverflow_df.index[-1]).split()[0] != f"{previous_year}-12-30"
    ):
        logger.info(f"Last date in the dataframe { str(recent_years_riverflow_df.index[-1]).split()[0]}")
        logger.info("The previous year riveflow needs to be scrapped and filled.")
        previous_year_table = get_year_riverflow_table(url, previous_year)
        previous_year_table = year_specific_dataframe(previous_year_table, previous_year)
        previous_year_table = previous_year_table.applymap(custom_str_to_int) * 1000

        # previous_year_df = get_previous_year_data(url, previous_year)
        # previous_year_df.index = pd.to_datetime(previous_year_df.index)
        # previous_year_df = previous_year_df[
        #     previous_year_df.index > recent_years_riverflow_df.index[-1]
        # ]

    # if current_year:
    #     current_year_table = get_year_riverflow_table(url, current_year)

    #     # if  (len(current_year_table) > threshold_days) & (len(current_year_table) == delta.days):
    #     if len(current_year_table) > threshold_days:
    #         current_year_table = year_specific_dataframe(
    #             current_year_table, current_year
    #         )
    #         # select the last index in the old and new dataframes:
    #         last_date_new_data = current_year_table.index[-1]
    #         last_date = recent_years_riverflow_df.index[-1]

    #         if last_date != last_date_new_data:
    #             before_threshold_day = pd.to_datetime(last_date) - pd.Timedelta(
    #                 days=threshold_days
    #             )
    #             before_threshold_day = before_threshold_day.strftime("%Y-%m-%d")
    #             recent_years_riverflow_df = recent_years_riverflow_df[
    #                 recent_years_riverflow_df.index < before_threshold_day
    #             ]
    #             data_to_append = current_year_table[
    #                 current_year_table.index > before_threshold_day
    #             ]
    #             data_to_append = data_to_append.applymap(custom_str_to_int) * 1000
    #             data_to_append.index = pd.to_datetime(data_to_append.index)
    #             data_to_append["Year"] = data_to_append.index.year
    #             data_to_append.index = pd.to_datetime(data_to_append.index).strftime(
    #                 "%Y-%m-%d"
    #             )

    #             recent_years_riverflow_df = pd.concat(
    #                 [recent_years_riverflow_df, data_to_append], axis=0
    #             )
    #             logger.info(" ------------ Dataframes updated. ------------ ")

    #             # saving the data to csv:
    #             recent_years_riverflow_df.to_csv("riverflow.csv")
    #             logger.info(" ------------ Data saved to csv. ------------ ")

    #         # else:
    #         #     logger.info("Table data is not equal to the number of days since 1st of January")

    #     elif len((current_year_table) < threshold_days):
    #         logger.info(
    #             "Data available is less than the threshold days but equal to the number of days since 1st of January"
    #         )
    #         logger.info(f" The current year table length is: {len(current_year_table)}")
    #         logger.info("Get the previous year data to fill the gap")

    #         previous_year_table = get_year_riverflow_table(url, previous_year)
    #         previous_year_table = year_specific_dataframe(
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

    #         last_date = recent_years_riverflow_df.index[-1]

    #         # Then get the last rows of the combined table equal to the threshold days:
    #         before_threshold_day = pd.to_datetime(last_date) - pd.Timedelta(
    #             days=threshold_days
    #         )
    #         before_threshold_day = before_threshold_day.strftime("%Y-%m-%d")
    #         recent_years_riverflow_df = recent_years_riverflow_df[
    #             recent_years_riverflow_df.index < before_threshold_day
    #         ]
    #         data_to_append = combined_table[combined_table.index > before_threshold_day]
    #         data_to_append = data_to_append.applymap(custom_str_to_int) * 1000
    #         data_to_append.index = pd.to_datetime(data_to_append.index)
    #         data_to_append["Year"] = data_to_append.index.year
    #         data_to_append.index = pd.to_datetime(data_to_append.index).strftime(
    #             "%Y-%m-%d"
    #         )
    #         recent_years_riverflow_df = pd.concat(
    #             [recent_years_riverflow_df, data_to_append], axis=0
    #         )
    #         recent_years_riverflow_df["Year"] = recent_years_riverflow_df.index.year
    #         logger.info(" ------------ Dataframes updated. ------------ ")

    #         # saving the data to csv:
    #         recent_years_riverflow_df.to_csv(RIVERFLOW_FILE)
    #         logger.info(" ------------ Data saved to csv. ------------ ")
    #     else:
    #         logger.info("No data at all")

    # else:
    #     logger.info(" ------------ Current year not found. ----------- ")

    # return current_year_table


def custom_str_to_int(value):
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


def create_main_scrapped_table() -> pd.DataFrame:
    """
    Creates an empty dataframe with predefined columns.
    """

    COLUMN_NAMES = ["Date", "Level (Feet) Indus At Tarbela", "indus_at_tarbela (cfs)", "Outflow Indus At Tarbela",
                    "kabul_at_nowshera (cfs)", "Level (Feet) Jehlum At Mangla", "jhelum_at_mangal (cfs)", "Outflow Jehlum At Mangla",
                    "cheanab_at_marala (cfs)", "Current Year", "Last Year", "Avg: Last 10-Years"]

    output_table = pd.DataFrame(columns=COLUMN_NAMES)
    return output_table


def year_specific_dataframe(main_scrapped_table: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    Filters and transforms the dataframe for a specific year.
    """

    COLUMNS = ["Date", "indus_at_tarbela (cfs)", "kabul_at_nowshera (cfs)", "jhelum_at_mangal (cfs)", "cheanab_at_marala (cfs)"]

    riverflow_data = main_scrapped_table[COLUMNS]

    riverflow_data = riverflow_data.copy()
    riverflow_data["Date"] = riverflow_data["Date"].apply(lambda x: x.replace(" ", "-"))
    riverflow_data["Date"] = [f"{date_str}-{year}" for date_str in riverflow_data["Date"]]
    riverflow_data["Date"] = pd.to_datetime(riverflow_data["Date"], format="%d-%b-%Y").dt.strftime("%Y-%m-%d")
    riverflow_data.set_index("Date", inplace=True)
    riverflow_data.index = pd.to_datetime(riverflow_data.index).strftime("%Y-%m-%d")

    return riverflow_data.sort_index(ascending=True)

if __name__ == "__main__":
    url = "https://www.wapda.gov.pk/river-flow"
    scrape_riverflow_data(url, threshold_days=60)
