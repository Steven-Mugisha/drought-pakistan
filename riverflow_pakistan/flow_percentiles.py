import pandas as pd
import pickle
import xarray as xr
from scipy.stats import weibull_min, genextreme
from tqdm import tqdm
import os
import glob
import numpy as np

def fit_model(flow_data: pd.Series, doy, window=None):
    if window is not None:
        doy_min = (doy - window) % 365
        doy_max = (doy + window) % 365
        if doy_min > doy_max:
            day_list = list(range(doy_min, 366)) + list(range(1, doy_max+1))
        else:
            day_list = list(range(doy_min, doy_max + 1))
        flow_data_final = flow_data[flow_data.index.dayofyear.isin(day_list)]
    else:
        print(" Only one day of year is considered")
        # flow_data_final = flow_data[flow_data.index.dayofyear == doy]
        # params = genextreme.fit(flow_data_final, floc=0) # CHECK THIS
        # params = list(params)
    # return params, flow_data_final
    return flow_data_final




# change this and ask Taimoor is this needs to output a dataframe or a csv file
def create_percentlie_dataframe():
    path = "/Users/mugisha/Desktop/clone/Drought_Pakistan/flows/"
    all_files = glob.glob(path + "/*.csv")

    for file in all_files:
        flow_data = pd.read_csv(file, index_col=0, parse_dates=True)
        name_of_river = file.split("/")[-1].split(".")[0]
        columns=["1%", "10%","25%","75%","90%","99%"]
        percentile_dataframe = pd.DataFrame(columns=columns)
        list_percentiles = []
        for i in range(1, 366):
            out_put = fit_model(flow_data, i, window=10)
            list_percentiles.append(out_put.quantile([0.01, 0.1, 0.25, 0.75, 0.9, 0.99]))

        for j in list_percentiles:
            append_list = j.iloc[:,0].tolist()
            new_row = pd.DataFrame([append_list], columns=columns)
            percentile_dataframe = percentile_dataframe.append(new_row, ignore_index=True)
            
            # save each dataframe to a csv file:
            out_directory = "/Users/mugisha/Desktop/clone/Drought_Pakistan/riverflow_pakistan/percent_flows/"
            percentile_dataframe.to_csv(out_directory + name_of_river + ".csv", index=False)
    

if __name__ == "__main__":
    create_percentlie_dataframe()

