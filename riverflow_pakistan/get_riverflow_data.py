
"""
    Author - Steven Mugisha Mizero
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime
import time


def scrape_wapda_riverflow_data() -> pd.DataFrame:

    wapdaUrl = "https://www.wapda.gov.pk/river-flow"

    # Defining selenium variables:
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    with webdriver.Chrome(options=chrome_options) as driver:
        driver.get(wapdaUrl)
        time.sleep(10)

        page_source_overview = driver.page_source
        soup = bs(page_source_overview, "html.parser")
        table = soup.find("table")

    if table is not None:
        # Extract data from the table
        table_data = []
        for row in table.find_all('tr'):
            row_values = []
            for cell in row.find_all('td'):
                row_values.append(cell.text.strip())
            if row_values:
                table_data.append(row_values)


        if table_data:
            columnsNames = ["Date", "LEVEL (FEET) INDUS AT TARBELA", "INFLOW INDUS AT TARBELA", "OUTFLOW INDUS AT TARBELA",
                            "INFLOW KABUL AT NOWSHERA", "LEVEL (FEET) JEHLUM AT MANGLA", "INFLOW JEHLUM AT MANGLA",
                            "OUTFLOW JEHLUM AT MANGLA", "INFLOW CHENAB AT MARALA", "CURRENT YEAR", "LAST YEAR", "AVG: Last 10-years"]
            output_table = pd.DataFrame(columns=columnsNames)

            for row in table_data[:]:
                output_table.loc[len(output_table)] = row

            # Match the riverflow_df with the recentYearsRiverFlow_df
            currentYear = datetime.now().year
            riverflow_subset = output_table[["Date","INFLOW INDUS AT TARBELA", "INFLOW KABUL AT NOWSHERA", "INFLOW JEHLUM AT MANGLA", "INFLOW CHENAB AT MARALA"]]
            columns_names = ["Date","indus_at_tarbela (cfs)", "kabul_at_nowshera (cfs)", "jhelum_at_mangal (cfs)", "cheanab_at_marala (cfs)"]
            riverflow_subset.columns = columns_names
            riverflow_subset["Date"] = riverflow_subset["Date"].apply(lambda x: x.replace(" ", "-"))
            riverflow_subset["Date"] = [date_str + f'-{currentYear}' for date_str in riverflow_subset["Date"]]
            riverflow_subset["Date"] = [pd.to_datetime(date_str, format='%d-%b-%Y').strftime('%Y-%m-%d') for date_str in riverflow_subset["Date"]]
            riverflow_subset_reversed = riverflow_subset.iloc[::-1]

            # Combine the two dataframes and save the current
            recentYearsRiverFlow_df = pd.read_csv("recentYearsRiverFlow.csv")

            # check the last date in the recentYearsRiverFlow_df
            lastDate = recentYearsRiverFlow_df["Date"].iloc[-1]
            if lastDate != riverflow_subset_reversed["Date"].iloc[-1]:
                # append all values after the lastDate
                data_to_append = riverflow_subset_reversed[riverflow_subset_reversed["Date"] > lastDate]
                recentYearsRiverFlow_df = recentYearsRiverFlow_df.append(data_to_append, ignore_index=True)
                recentYearsRiverFlow_df.to_csv("recentYearsRiverFlow.csv", index=False)
            else:
                # do nothing
                print("No new data to append")

        else:
            print("Table is empty")
    else:
        print("Table not found")

if __name__ == "__main__":
    scrape_wapda_riverflow_data()
