
"""
    Author - Steven Mugisha Mizero
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime, timedelta
import time


def scrape_wapda_riverflow_data() -> pd.DataFrame:

    wapdaUrl = "https://www.wapda.gov.pk/river-flow"

    # Defining selenium variables:
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    with webdriver.Chrome(options=chrome_options) as driver:
        driver.get(wapdaUrl)
        time.sleep(1)

        page_source_overview = driver.page_source
        soup = bs(page_source_overview, "html.parser")

        try:
            select_element = driver.find_element("css selector", ".MuiSelect-root.MuiSelect-select.MuiSelect-selectMenu.MuiSelect-outlined.MuiInputBase-input.MuiOutlinedInput-input")
            print("***------------Select element found.------------***")

            # I want to see the options in the select element and print them out:
            select_element.click()
            time.sleep(1)
            select_options = driver.find_elements("css selector", ".MuiButtonBase-root.MuiListItem-root.MuiMenuItem-root.MuiMenuItem-gutters.MuiListItem-gutters.MuiListItem-button")
            print("***------------Select options found.------------***")
            for option in select_options:
                # if option.text is equal to current year, then click it:
                if option.text == str(datetime.now().year):
                    option.click()
                    print("***------------Select option clicked.------------***")
                    time.sleep(1)
                    # Now I want to get the table data:
                    page_source_overview = driver.page_source
                    soup = bs(page_source_overview, "html.parser")
                    table = soup.find("table")
                    print("***------------Table found.------------***")
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

                            # # Reverse the table:
                            # output_table = output_table.iloc[::-1]

                    print(f"***------------Table data extracted.------------***")
                    print(f"***----THE LENGTH OF THE TABLE ==== {len(output_table)} ----***")

                    # check starting on 1st of January until today's date how many days using timedelta:
                    today = datetime.now()
                    start_date = datetime(today.year, 1, 1)
                    delta = today - start_date
                    print(f"***------------Number of days since 1st of January: {delta.days}------------***")

                    # check to see if the length of the table is equal to the number of days since 1st of January:
                    if len(output_table) == delta.days:
                        print("***------------Table data is equal to the number of days since 1st of January.------------***")
                        print(f"***------------Table data is equal to the number of days since 1st of January.------------***{len(output_table)}")

                        threshold_day = 60 
                        print("***------------Threshold day is 60.------------***")  
                        if len(output_table) < threshold_day:
                            option.text = str(datetime.now().year - 1)
                            option.click()
                            print("***------------Select option clicked.------------***")
                            time.sleep(1)
                            # Now I want to get the table data:
                            page_source_overview = driver.page_source
                            soup = bs(page_source_overview, "html.parser")
                            table = soup.find("table")
                            print("***------------Table found.------------***")
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

                            print("**** Creat the talbe for the previous year ****")
                            the_previous_year = option.text
                            riverflow_subset = output_table[["Date","INFLOW INDUS AT TARBELA", "INFLOW KABUL AT NOWSHERA", "INFLOW JEHLUM AT MANGLA", "INFLOW CHENAB AT MARALA"]]
                            columns_names = ["Date","indus_at_tarbela (cfs)", "kabul_at_nowshera (cfs)", "jhelum_at_mangal (cfs)", "cheanab_at_marala (cfs)"]
                            riverflow_subset.columns = columns_names
                            riverflow_subset["Date"] = riverflow_subset["Date"].apply(lambda x: x.replace(" ", "-"))
                            riverflow_subset["Date"] = [date_str + f'-{the_previous_year}' for date_str in riverflow_subset["Date"]]
                            riverflow_subset["Date"] = [pd.to_datetime(date_str, format='%d-%b-%Y').strftime('%Y-%m-%d') for date_str in riverflow_subset["Date"]]
                            riverflow_subset_reversed_previous_year = riverflow_subset.iloc[::-1]

                            print(f"***------------Table data extracted.------------***{riverflow_subset_reversed_previous_year}")

                        else:
                            continue
   
                        print("******** The current year table ********")
                        # if the length of output_table is less than 60 days, then we need to get the previous year's data:
                        currentYear = datetime.now().year
                        riverflow_subset = output_table[["Date","INFLOW INDUS AT TARBELA", "INFLOW KABUL AT NOWSHERA", "INFLOW JEHLUM AT MANGLA", "INFLOW CHENAB AT MARALA"]]
                        columns_names = ["Date","indus_at_tarbela (cfs)", "kabul_at_nowshera (cfs)", "jhelum_at_mangal (cfs)", "cheanab_at_marala (cfs)"]
                        riverflow_subset.columns = columns_names
                        riverflow_subset["Date"] = riverflow_subset["Date"].apply(lambda x: x.replace(" ", "-"))
                        riverflow_subset["Date"] = [date_str + f'-{currentYear}' for date_str in riverflow_subset["Date"]]
                        riverflow_subset["Date"] = [pd.to_datetime(date_str, format='%d-%b-%Y').strftime('%Y-%m-%d') for date_str in riverflow_subset["Date"]]
                        riverflow_subset_reversed = riverflow_subset.iloc[::-1]

                        print(f" ****-------  Here is the dataframe to be save \n {riverflow_subset_reversed} -------****")

                        # Combine the two dataframes and save the current
                        recentYearsRiverFlow_df = pd.read_csv("recentYearsRiverFlow.csv")

                        # check the last date in the recentYearsRiverFlow_df
                        lastDate = recentYearsRiverFlow_df["Date"].iloc[-1]
                        print(f"****--------------Last date of old data is held here: {lastDate}----------****")
                        lastDate_newdata = riverflow_subset_reversed["Date"].iloc[-1]
                        print(f"------------------Last date of new data is held here: {lastDate_newdata}-------------")
                        if lastDate != lastDate_newdata:
                            # Take the lastDate_newdata - 60 days and appned all values after that date to the recentYearsRiverFlow_df:
                            lastDate_newdata = pd.to_datetime(lastDate_newdata)
               
                            _60days_before = lastDate_newdata - pd.Timedelta(days=threshold_day)
                            _60days_before  = _60days_before .strftime('%Y-%m-%d')

                            print(f"------------------ Date of 60 days before is held here : {_60days_before}-------------")
                            print("------- Appending data for the last 60 days -------------")

                            # Drop all rows from the recentYearsRiverFlow_df that has date greater than _60days_before:
                            recentYearsRiverFlow_df = recentYearsRiverFlow_df[recentYearsRiverFlow_df["Date"] < _60days_before]
                            data_to_append = riverflow_subset_reversed[riverflow_subset_reversed["Date"] > _60days_before]
                            recentYearsRiverFlow_df = recentYearsRiverFlow_df.append(data_to_append, ignore_index=True)

                            # if the riverflow_subset_reversed_previous_year is not empty, then we need to concat the two tables:
                            if not riverflow_subset_reversed_previous_year.empty:
                                # concat the two tables:
                                recentYearsRiverFlow_df = pd.concat([recentYearsRiverFlow_df, riverflow_subset_reversed_previous_year], ignore_index=True)
                                print(f"***------------Table data extracted.------------***{recentYearsRiverFlow_df}")
                            else:
                                recentYearsRiverFlow_df.to_csv("recentYearsRiverFlow.csv", index=False)
                        else:
                            # do nothing
                            print("***------- No new data to append -------*****")

                    # or check the missing days:
                    elif len(output_table) < delta.days:
                        print("***------------Table data is less than the number of days since 1st of January.------------***")
                        print(f"***------------Table data is less than the number of days since 1st of January.------------***{len(output_table)}")

                        # from january 1st until today's date, get the missing days:
                        missing_days = []
                        for i in range(delta.days + 1):
                            day = start_date + timedelta(days=i)
                            day = day.strftime("%d-%m-%Y")
                            if day not in output_table["Date"].tolist():
                                missing_days.append(day)
                        print(f"***------------Missing days: {missing_days}------------***")
                    else:
                        print("***------------Table data is not equal to the number of days since 1st of January.------------***")
                        print(f"***------------Table data is not equal to the number of days since 1st of January.------------***{len(output_table)}")
                else:
                    print(" ***** Do nothing ****.")

          
        except:
            print("Select element not found.")
            
if __name__ == "__main__":
    scrape_wapda_riverflow_data()