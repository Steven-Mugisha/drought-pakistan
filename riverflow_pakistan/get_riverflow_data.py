
""" Author - Steven Mugisha Mizero """

from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
from dotenv import load_dotenv
import os


# the path to the folder:
load_dotenv()
path = os.getenv("path")

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the desired logging level
logger = logging.getLogger(__name__)


def create_dataframe() -> pd.DataFrame:
    """ This function creates a dataframe with the following columns: """
    
    columns_names = ["Date", "LEVEL (FEET) INDUS AT TARBELA", "INFLOW INDUS AT TARBELA", "OUTFLOW INDUS AT TARBELA",
                        "INFLOW KABUL AT NOWSHERA", "LEVEL (FEET) JEHLUM AT MANGLA", "INFLOW JEHLUM AT MANGLA",
                            "OUTFLOW JEHLUM AT MANGLA", "INFLOW CHENAB AT MARALA",
                                 "CURRENT YEAR", "LAST YEAR", "AVG: Last 10-years"]
    
    output_table = pd.DataFrame(columns=columns_names)
    return output_table


def year_specific_dataframe(output_table,year) -> pd.DataFrame:
    """ This function edits the dataframe and changes the year column to the year specified in the function call. """

    output_table_subset = output_table[["Date","INFLOW INDUS AT TARBELA", "INFLOW KABUL AT NOWSHERA", "INFLOW JEHLUM AT MANGLA", "INFLOW CHENAB AT MARALA"]]
    columns_names = ["Date","indus_at_tarbela (cfs)", "kabul_at_nowshera (cfs)", "jhelum_at_mangal (cfs)", "cheanab_at_marala (cfs)"]
    output_table_subset.columns = columns_names

    output_table_subset["Date"] = output_table_subset["Date"].apply(lambda x: x.replace(" ", "-"))
    output_table_subset["Date"] = [date_str + f'-{year}' for date_str in output_table_subset["Date"]]
    output_table_subset["Date"] = [pd.to_datetime(date_str, format='%d-%b-%Y').strftime('%Y-%m-%d') for date_str in output_table_subset["Date"]]

    # set the index to be the date column:
    output_table_subset.set_index("Date", inplace=True)
    output_table_subset.index = pd.to_datetime(output_table_subset.index)
    output_table_subset.index = output_table_subset.index.strftime('%Y-%m-%d')
    out_put_year_df = output_table_subset.sort_index(ascending=True)

    return out_put_year_df


def get_year_riverflow_table(url, year) -> pd.DataFrame:

    """ reads the data from the website and returns a dataframe for a specific year."""

    # defining selenium variables:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # s = Service(f'{path}/chromedriver')

    with webdriver.Chrome(options=chrome_options, service=ChromeService(ChromeDriverManager().install())) as driver:
        driver.get(url)
        time.sleep(1)

        try:
            select_element = driver.find_element("css selector", ".MuiSelect-root.MuiSelect-select.MuiSelect-selectMenu.MuiSelect-outlined.MuiInputBase-input.MuiOutlinedInput-input")
            logger.info("Select element found.")

            # I want to see the options in the select element and log them out:
            select_element.click()
            time.sleep(1)
            select_options = driver.find_elements("css selector", ".MuiButtonBase-root.MuiListItem-root.MuiMenuItem-root.MuiMenuItem-gutters.MuiListItem-gutters.MuiListItem-button")
            logger.info("Select options found.")
            for option in select_options:
                # if option.text is equal to current year, then click it:
                if option.text == str(year):
                    option.click()
                    logger.info(f"Selected the year: {year} option clicked")
                    time.sleep(1)
                    # Now I want to get the table data:
                    page_source_overview = driver.page_source
                    soup = bs(page_source_overview, "html.parser")
                    time.sleep(5)
                    table = soup.find("table")
                    logger.info("------------ Table found ------------")

                    if table:
                        # the list of lists that will contain the table data
                        table_data = []
                        for row in table.find_all('tr'):
                            row_values = []
                            for cell in row.find_all('td'):
                                row_values.append(cell.text.strip())
                            if row_values:
                                table_data.append(row_values)
                            else:
                                logger.info("------------Table data not found ------------")
                    else:
                        logger.info("------------Table not found ------------ ")
                    
                    if table_data:
                        output_table = create_dataframe()
                        for row in table_data[:]:
                            output_table.loc[len(output_table)] = row
                            output_table = output_table.iloc[::-1]
                        logger.info(f" THE LENGTH OF THE TABLE {len(output_table)}")
        
                   
                else:
                    logger.info("Select option not clicked")

        except Exception as e:
            logger.error(f"------------Error: {e}------------")
        
        return output_table

def individual_year_data(url, threshold_days = 60):
    """ This function returns the data for the current year and the previous year """
    # the years to be used:
    current_year = datetime.now().year
    previous_year = current_year - 1

    # to check which days missing from the dataframe: 
    today = datetime.now()
    start_date = datetime(today.year, 1, 1)
    # The number of days since 1st of January:
    delta = today - start_date
    logger.info(f" ------------ The number of days since 1st of January: {delta.days} ------------ ")
    

    # the existing dataset:
    recentYearsRiverFlow_df = pd.read_csv(f"{path}/recentYearsRiverFlow.csv")
    # set the index to be the date column:
    recentYearsRiverFlow_df.set_index("Date", inplace=True)

    if current_year:
        current_year_table = get_year_riverflow_table(url, current_year)

        # if  (len(current_year_table) > threshold_days) & (len(current_year_table) == delta.days):
        if  (len(current_year_table) > threshold_days):
            current_year_table = year_specific_dataframe(current_year_table, current_year)
            # select the last index in the old and new dataframes:
            lastDate_newdata = current_year_table.index[-1]
            lastDate = recentYearsRiverFlow_df.index[-1]

            if lastDate != lastDate_newdata:
                before_threshold_day = pd.to_datetime(lastDate) - pd.Timedelta(days=threshold_days)
                before_threshold_day = before_threshold_day.strftime('%Y-%m-%d')
                recentYearsRiverFlow_df = recentYearsRiverFlow_df[recentYearsRiverFlow_df.index < before_threshold_day]
                data_to_append = current_year_table[current_year_table.index > before_threshold_day]
                # concat the dataframes:
                recentYearsRiverFlow_df = pd.concat([recentYearsRiverFlow_df, data_to_append], axis=0)
                logger.info(" ------------ Dataframes updated. ------------ ")


                # saving the data to csv:
                recentYearsRiverFlow_df.to_csv(f"{path}/recentYearsRiverFlow.csv")
                logger.info(" ------------ Data saved to csv. ------------ ")
    
            else:
                logger.info("Table data is not equal to the number of days since 1st of January")
        
        elif len((current_year_table) < threshold_days):
            logger.info("Data available is less than the threshold days but equal to the number of days since 1st of January")
            logger.info(f" The current year table length is: {len(current_year_table)}")
            logger.info("Get the previous year data to fill the gap")

            previous_year_table = get_year_riverflow_table(url, previous_year)
            previous_year_table = year_specific_dataframe(previous_year_table, previous_year)
            lastDate_newdata = previous_year_table.index[-1]
            logger.info(f" ------------------ Last date of new data is held here: {lastDate_newdata} ------------- ")

            days_to_get_from_previous_year = threshold_days - len(current_year_table)

            # get the last rows of the previous year table equal to the days_to_get_from_previous_year:
            logger.info(f" Reading the last year table to match the threshold days")
            previous_year_table = previous_year_table.tail(days_to_get_from_previous_year)
           
            # concat the two dataframes:
            combined_table = pd.concat([previous_year_table, current_year_table], axis=0)
            lastDate_combined_table = combined_table.index[-1]
            lastDate = recentYearsRiverFlow_df.index[-1]

            # Then get the last rows of the combined table equal to the threshold days:
            before_threshold_day = pd.to_datetime(lastDate) - pd.Timedelta(days=threshold_days)
            before_threshold_day = before_threshold_day.strftime('%Y-%m-%d')
            recentYearsRiverFlow_df = recentYearsRiverFlow_df[recentYearsRiverFlow_df.index < before_threshold_day]
            data_to_append = combined_table[combined_table.index > before_threshold_day]
            recentYearsRiverFlow_df = pd.concat([recentYearsRiverFlow_df, data_to_append], axis=0)
            logger.info(" ------------ Dataframes updated. ------------ ")
            

            # saving the data to csv:
            recentYearsRiverFlow_df.to_csv(f"{path}/recentYearsRiverFlow.csv")
        else:
            logger.info("No data at all")
                
    else:
        logger.info(" ------------ Current year not found. ----------- ")
    
    return current_year_table

if __name__ == "__main__":
    url = "https://www.wapda.gov.pk/river-flow"
    individual_year_data(url, threshold_days = 60)