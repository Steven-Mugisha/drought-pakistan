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


def create_percentile_dataframe() -> pd.DataFrame:

    # Creating a function max and min from percentiles values
    file = "/Users/mugisha/Desktop/clone/Drought_Pakistan/riverflow_pakistan/flows/indus_at_tarbela.csv"
    flow_data = pd.read_csv(file, index_col=0, parse_dates=True)
    name_of_river = file.split("/")[-1].split(".")[0]

    # Define data storages:
    list_of_values = []
    out_put_list = []

    for i in range(1, 366):
        out_put = fit_model(flow_data, i, window=10)
        out_put_list.append(out_put)

    for dataframe in out_put_list:
        # change values into a list
        values = dataframe.iloc[:, 0].values.tolist()
        clean_list = [x for x in values if not math.isnan(x)]
        list_of_values.append(clean_list)

    Plot_dataframe = pd.DataFrame(columns=[
                                  "min_value", "0.1_value", "0.25_value", "0.75_value", "0.9_value", "max_value"])
    for i, lst in enumerate(list_of_values):
        percentages = [0.1, 0.25, 0.75, 0.9]
        min_value = min(lst)
        max_value = max(lst)

        # create a list of values for each percentile and incldue the min and max values which are the min and max values all in a comphrensive list
        percentile_values = [
            min_value] + [np.percentile(lst, perc*100) for perc in percentages] + [max_value]
        # Plot_dataframe.loc[f'list{i+1}'] = percentile_values
        Plot_dataframe.loc[f'list{i+1}'] = percentile_values
        Plot_dataframe = Plot_dataframe.reset_index(drop=True)

    return Plot_dataframe


def plot_percentile_flow():
    # Get the data
    Plot_dataframe = create_percentile_dataframe()

    # set the index from 1 to 365
    Plot_dataframe = Plot_dataframe.set_index(pd.Index(range(1, 366)))

    # Create the traces

    traces = []
    fill_colors = ['brown', 'saddlebrown', 'moccasin',
                   'lawngreen', 'paleturquoise', 'blue']

    for j, col in enumerate(Plot_dataframe.columns):
        fill = 'tonexty' if j > 0 else 'none'
        fillcolor = fill_colors[j] if j < len(fill_colors) else None
        linecolor = 'red' if j == 0 else fillcolor
        traces.append(go.Scatter(
            x=Plot_dataframe.index,
            y=Plot_dataframe.iloc[:, j],
            name=col,
            fill=fill,
            fillcolor=fillcolor,
            line=dict(color=linecolor)
        ))

    # Set the layout
    layout = go.Layout(
        width=1200,
        height=600,
        title='Indus at Tarbela Dam Flow Percentiles (cfs)',
        xaxis=dict(title='', showticklabels=False, showgrid=False),

        yaxis=dict(
            title='Daily maximum and minimum discharge, in cubic feet per second',
            tickmode='array',
            tickformat='.0f',
            tickvals=[Plot_dataframe.iloc[:, 0].min(), 25000, 50000,
                      100000, 200000, 500000, Plot_dataframe.iloc[:, -1].max()],
            type='log',
            tick0=Plot_dataframe.iloc[:, 0].min(),
            dtick=(Plot_dataframe.iloc[:, -1].max() -
                   Plot_dataframe.iloc[:, 0].min()) / 10,
            showgrid=False,
            titlefont=dict(size=10)
        )
    )

    # Create the figure
    fig = go.Figure(data=traces, layout=layout)

    # Show the figure
    return pio.show(fig)


if __name__ == "__main__":
    plot_percentile_flow()
