
import pandas as pd
import numpy as np
import requests, io
from bs4 import BeautifulSoup as bs 
from tqdm import tqdm
import json


def crawl_riverflow(): 
    wapdaUrl = "http://www.wapda.gov.pk/index.php/river-flow-data"
    page = requests.get(wapdaUrl)

    soup = bs(page.content, "html.parser")

    table =  soup.find("table")

    # Extract the data from the table
    data = []
    for row in table.find_all('tr'):
        row_data = []
        for cell in row.find_all('td'):
            row_data.append(cell.text.strip())
        data.append(row_data)


    # # print(riverflowList)
    columnsNames = ["Date","LEVEL (FEET) INDUS AT TARBELA","INFLOW INDUS AT TARBELA", "OUTFLOW INDUS AT TARBELA",
                    "INFLOW KABUL AT NOWSHERA", "LEVEL (FEET) JEHLUM AT MANGLA", "INFLOW JEHLUM AT MANGLA",
                    "OUTFLOW JEHLUM AT MANGLA", "INFLOW CHENAB AT MARALA", "CURRENT YEAR", "LAST YEAR", "AVG: Last 10-years" ]

    riverflow_df = pd.DataFrame(columns=columnsNames)


    for row in data[4:]:
        riverflow_df.loc[len(riverflow_df)] = row

    
    return riverflow_df

def main_rivers():
    riverflow_df = crawl_riverflow()
    inflow_df = riverflow_df[["Date","INFLOW INDUS AT TARBELA", "INFLOW KABUL AT NOWSHERA",
                                               "INFLOW JEHLUM AT MANGLA", "INFLOW CHENAB AT MARALA"]]
    
    split_index = inflow_df.index.get_loc((inflow_df['Date'] == '1-Jan').idxmax())
                                           
    # dataframe corresponding to the year of 2022
    rf_2022_df = inflow_df.loc[split_index + 1:].copy()
    dates_2022= [s.replace('/', '-') if '/' in s else s for s in rf_2022_df.Date]
    new_rf_2022_df= rf_2022_df.iloc[:,1:]
    new_rf_2022_df["Date"]= dates_2022
    rf_2022_reversed= new_rf_2022_df[::-1]
    final_2022_df= rf_2022_reversed.set_index("Date")
    final_2022_df.index = [pd.to_datetime(date_str + '-2022', format='%d-%b-%Y').strftime('%Y-%m-%d') for date_str in final_2022_df.index]


    # dataframe corresponding to the year of 2023
    rf_2023_df = inflow_df.loc[:split_index].copy()
    dates_2023= [s.replace('/', '-') if '/' in s else s for s in rf_2023_df.Date]
    new_rf_2023_df= rf_2023_df.iloc[:,1:]
    new_rf_2023_df["Date"]= dates_2023
    rf_2023_reversed= new_rf_2023_df[::-1]
    final_2023_df= rf_2023_reversed.set_index("Date")
    final_2023_df.index= [pd.to_datetime(date_str + '-2023', format='%d-%b-%Y').strftime('%Y-%m-%d') for date_str in final_2023_df.index]

    # combined dataframe for 2022 and 2023
    Inflow_combined_df= pd.concat([final_2022_df, final_2023_df], axis=0)
    Inflow_combined_df.reset_index(inplace=True)
    columns_names= ["Date","INDUS", "KABUL", "JEHLUM", "CHENAB"]
    Inflow_combined_df.columns= columns_names

    Inflow_combined_df['Year']= [year.split("-")[0] for year in list(Inflow_combined_df.Date)]
    Inflow_combined_df.to_csv("mainInflowrivers.csv", index=False)
    
    return print("Done")


if __name__ == "__main__":
    print(main_rivers())





