import pandas as pd
import pickle
import xarray as xr
from scipy.stats import weibull_min, genextreme
from tqdm import tqdm
import os
import glob
import numpy as np
import math
import plotly.graph_objs as go
import plotly.offline as pyo
import plotly.graph_objs as go
import plotly.io as pio
from dotenv import load_dotenv
import os

# the path to the folder:
load_dotenv()
path = os.getenv("path")


def fit_model(flow_data: pd.Series, doy, window=None) -> pd.DataFrame:
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

def percentiles(station_name: str) -> pd.DataFrame:
    """This function creates a DataFrame with the percentiles values for each day of the year for a given station."""
    
    def clean_nan(lst):
        return [x for x in lst if not math.isnan(x)]

    percentile_dataframe = pd.DataFrame(columns=["min", "10%", "25%", "75%", "90%", "max"])

    # load data
    # directory = f"{path}/old_version_flow.csv"
    directory = f"riverflow.csv"
    stations_flow_df = pd.read_csv(directory, index_col=0, parse_dates=True)
    station_serie = stations_flow_df[station_name]

    # Collect data and calculate percentiles
    model_values = [fit_model(station_serie, i, window=10) for i in range(1, 366)]
    list_of_values = [clean_nan(dataframe.values.tolist()) for dataframe in model_values]
    
    percentiles = [0.1, 0.25, 0.75, 0.9]
    for i, lst in enumerate(list_of_values):
        percentile_values = [min(lst)] + [np.percentile(lst, perc * 100) for perc in percentiles] + [max(lst)]
        percentile_dataframe.loc[f'list{i + 1}'] = percentile_values
        percentile_dataframe = percentile_dataframe.reset_index(drop=True)

    return percentile_dataframe

# if __name__ == "__main__":
#     percentiles("kabul_at_nowshera (cfs)")

