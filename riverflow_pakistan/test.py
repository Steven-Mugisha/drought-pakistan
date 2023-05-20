
"""
    Author - Steven Mugisha Mizero
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime, timedelta
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the desired logging level
logger = logging.getLogger(__name__)


def create_dataframe() -> pd.DataFrame:
    """ This function creates a dataframe with the following columns: """
    
    columnsNames = ["Date", "LEVEL (FEET) INDUS AT TARBELA", "INFLOW INDUS AT TARBELA", "OUTFLOW INDUS AT TARBELA",
                        "INFLOW KABUL AT NOWSHERA", "LEVEL (FEET) JEHLUM AT MANGLA", "INFLOW JEHLUM AT MANGLA",
                            "OUTFLOW JEHLUM AT MANGLA", "INFLOW CHENAB AT MARALA",
                                 "CURRENT YEAR", "LAST YEAR", "AVG: Last 10-years"]
    
    output_table = pd.DataFrame(columns=columnsNames)
    return output_table


def year_specific_dataframe(output_table,year) -> pd.DataFrame:
    """ This function edits the dataframe and changes the year column to the year specified in the function call. """

    output_table_subset = output_table[["Date","INFLOW INDUS AT TARBELA", "INFLOW KABUL AT NOWSHERA", "INFLOW JEHLUM AT MANGLA", "INFLOW CHENAB AT MARALA"]]
    columns_names = ["Date","indus_at_tarbela (cfs)", "kabul_at_nowshera (cfs)", "jhelum_at_mangal (cfs)", "cheanab_at_marala (cfs)"]
    output_table_subset.columns = columns_names

    output_table_subset["Date"] = output_table_subset["Date"].apply(lambda x: x.replace(" ", "-"))
    output_table_subset["Date"] = [date_str + f'-{year}' for date_str in output_table_subset["Date"]]
    output_table_subset["Date"] = [pd.to_datetime(date_str, format='%d-%b-%Y').strftime('%Y-%m-%d') for date_str in output_table_subset["Date"]]
    output_table_subset = output_table_subset.iloc[::-1]

    return output_table_subset


def get_riverflow_table(url, year) -> pd.DataFrame:

    """ reads the data from the website and returns a dataframe with the following columns:"""

    # defining selenium variables:
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    with webdriver.Chrome(options=chrome_options) as driver:
        driver.get(url)
        time.sleep(1)

        try:
            select_element = driver.find_element("css selector", ".MuiSelect-root.MuiSelect-select.MuiSelect-selectMenu.MuiSelect-outlined.MuiInputBase-input.MuiOutlinedInput-input")
            logger.info("***------------Select element found.------------***")

            # I want to see the options in the select element and log them out:
            select_element.click()
            time.sleep(1)
            select_options = driver.find_elements("css selector", ".MuiButtonBase-root.MuiListItem-root.MuiMenuItem-root.MuiMenuItem-gutters.MuiListItem-gutters.MuiListItem-button")
            logger.info("***------------Select options found.------------***")
            for option in select_options:
                # if option.text is equal to current year, then click it:
                if option.text == str(year):
                    option.click()
                    logger.info("***------------Select option clicked.------------***")
                    time.sleep(1)
                    # Now I want to get the table data:
                    page_source_overview = driver.page_source
                    soup = bs(page_source_overview, "html.parser")
                    time.sleep(5)
                    table = soup.find("table")
                    logger.info("***------------Table found.------------***")

                    if table:
                        table_data = []
                        for row in table.find_all('tr'):
                            row_values = []
                            for cell in row.find_all('td'):
                                row_values.append(cell.text.strip())
                            if row_values:
                                table_data.append(row_values)
                            else:
                                logger.info("***------------Table data not found.------------***")
                    else:
                        logger.info("***------------Table not found.------------***")
                    
                    if table_data:
                        output_table = create_dataframe()
                        for row in table_data[:]:
                            output_table.loc[len(output_table)] = row
                            output_table = output_table.iloc[::-1]
                        logger.info(f"***----THE LENGTH OF THE TABLE ==== {len(output_table)} ----***")
                        # logger.info(f"***------------Table data extracted.------------***{output_table}")
                   
                else:
                    logger.info("***------------Select option not clicked.------------***")

        except Exception as e:
            logger.error(f"***------------Error: {e}------------***")
        
        return output_table

def individual_year_data(url, threshold_days = 60):
    """ This function returns the data for the current year and the previous year """
    # the years to be used:
    current_year = datetime.now().year
    previous_year = current_year - 1

    # to check which days are missing in any from the dataframe: 
    today = datetime.now()
    start_date = datetime(today.year, 1, 1)
    delta = today - start_date

    # all existing data:
    recentYearsRiverFlow_df = pd.read_csv("/Users/mugisha/Desktop/clone/Drought_Pakistan/riverflow_pakistan/recentYearsRiverFlow.csv")

    if current_year:
        current_year_table = get_riverflow_table(url, current_year)

        if  (len(current_year_table) > threshold_days) & (len(current_year_table) == delta.days):
            logger.info("***------------Table data is equal to the number of days since 1st of January.------------***")
            current_year_table = year_specific_dataframe(current_year_table, current_year)
            lastDate_newdata = current_year_table["Date"].iloc[-1]
            logger.info(f"------------------Last date of new data is held here: {lastDate_newdata}-------------")

            lastDate = recentYearsRiverFlow_df["Date"].iloc[-1]
            logger.info(f"****--------------Last date of old data is held here: {lastDate}----------****")

            if lastDate != lastDate_newdata:
                lastDate_newdata = pd.to_datetime(lastDate_newdata)
                threshold_days_before = lastDate_newdata - pd.Timedelta(days=threshold_days)
                threshold_days_before  = threshold_days_before.strftime('%Y-%m-%d')
                recentYearsRiverFlow_df = recentYearsRiverFlow_df[recentYearsRiverFlow_df["Date"] < threshold_days_before]
                data_to_append = current_year_table[current_year_table["Date"] > threshold_days_before]
                recentYearsRiverFlow_df = recentYearsRiverFlow_df.append(data_to_append, ignore_index=True)
                logger.info("***------------Data appended to the recentYearsRiverFlow_df.------------***")
                logger.info(f"***----{recentYearsRiverFlow_df} ----***")

                # saving the data to csv:
                recentYearsRiverFlow_df.to_csv("recentYearsRiverFlow.csv", index=False)
    
            else:
                logger.info("***------------Table data is not equal to the number of days since 1st of January.------------***")
        
        elif len((current_year_table) < threshold_days) & (len(current_year_table) == delta.days):
            logger.info("***------------Table data is equal to the number of days since 1st of January.------------***")
            logger.info("***------------ The current year doesn't have enough data defined by the threshold day.------------***")
            previous_year_table = get_riverflow_table(url, previous_year)
            previous_year_table = year_specific_dataframe(previous_year_table, previous_year)
            lastDate_newdata = previous_year_table["Date"].iloc[-1]
            logger.info(f"------------------Last date of new data is held here: {lastDate_newdata}-------------")

            days_to_get_from_previous_year = threshold_days - len(current_year_table)
            logger.info(f"------------------Days to get from previous year: {days_to_get_from_previous_year}-------------")
            # get the last rows of the previous year table equal to the days_to_get_from_previous_year:
            previous_year_table = previous_year_table.tail(days_to_get_from_previous_year)
            logger.info(f"------------------ I am reading the curent table to also get the available data -------------")
            current_year_table = year_specific_dataframe(current_year_table, current_year)
            logger.info(f"------------------ I am appending the previous year table to the current year table -------------")
            combined_table = previous_year_table.append(current_year_table, ignore_index=True)
            lastDate_combined_table = combined_table["Date"].iloc[-1]
            lastDate = recentYearsRiverFlow_df["Date"].iloc[-1]

            if lastDate != lastDate_combined_table:
                lastDate_combined_table = pd.to_datetime(lastDate_combined_table)
                threshold_days_before = lastDate_combined_table - pd.Timedelta(days=threshold_days)
                threshold_days_before  = threshold_days_before.strftime('%Y-%m-%d')
                recentYearsRiverFlow_df = recentYearsRiverFlow_df[recentYearsRiverFlow_df["Date"] < threshold_days_before]
                data_to_append = combined_table[combined_table["Date"] > threshold_days_before]
                recentYearsRiverFlow_df = recentYearsRiverFlow_df.append(data_to_append, ignore_index=True)
                logger.info("***------------Data appended to the recentYearsRiverFlow_df.------------***")
                logger.info(f"***----{recentYearsRiverFlow_df} ----***")
            
            else:
                logger.info("***------------Table data is not equal to the number of days since 1st of January.------------***")
            
            # saving the data to csv:
            recentYearsRiverFlow_df.to_csv("recentYearsRiverFlow.csv", index=False)
        else:
            logger.info("***------------Table data is not equal to the number of days since 1st of January.------------***")
                
    else:
        logger.info("***------------Current year not found.------------***")
    
    return current_year_table

if __name__ == "__main__":
    url = "https://www.wapda.gov.pk/river-flow"
    individual_year_data(url, threshold_days = 60)