
import pandas as pd
import numpy as np
import requests, io
from bs4 import BeautifulSoup as bs 
from tqdm import tqdm


################ This code returns a table #####################
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

riverflowDataframe = pd.DataFrame(columns=columnsNames)


for row in data[4:]:
    riverflowDataframe.loc[len(riverflowDataframe)] = row

print(riverflowDataframe)

##############################################################################################################################



