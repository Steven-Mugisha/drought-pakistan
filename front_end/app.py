import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from flow_percentiles import percentiles
import logging
import calendar
from dotenv import load_dotenv
import os

# the path to the folder:
load_dotenv()
path = os.getenv("path")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")


st.markdown(
    "<h1 style='font-size:40px; text-align: center;'>RiverFlow hydrographs of main rivers in Pakistan</h1>",
    unsafe_allow_html=True
)

st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2= st.columns([2, .4])

# Varaibles for selection:
name_rivers = ["indus_at_tarbela (cfs)","kabul_at_nowshera (cfs)","jhelum_at_mangal (cfs)","cheanab_at_marala (cfs)"]
recent_years = [2019,2018,2017,2016,2015,2014,2013,2012,2011,2010]

with col2:
    selected_station = st.selectbox(
        "Select Station",
        name_rivers,
        index=name_rivers.index(name_rivers[0])
    )

with col2:
    selected_year = st.selectbox(
        "Select Year",
        recent_years,
        index=recent_years.index(recent_years[0])
    )
    
def selected_station_df(station:str) -> pd.DataFrame:
    """ Load the station data set from the directory and selects the year of interest """

    directory = f"{path}/old_version_flow.csv"
    station_df = pd.read_csv(directory, index_col=0, parse_dates=True)
    station_df = station_df[station_df[station].notna()]
    year_subset_df = station_df[station_df["Year"] == selected_year]
    # year_subset_df["Year"] = year_subset_df["Year"].astype(str)
    year_subset_df = year_subset_df.set_index(pd.Index(range(1, len(year_subset_df)+1)))
 
    return year_subset_df

if selected_year != "Select Year":
    riverflow_df = selected_station_df(selected_station)

with col1:  
  
    try:
        plot_df = percentiles(selected_station)
        # set the index from 1 to 365
        plot_df = plot_df.set_index(pd.Index(range(1, 366)))

        # Create the traces
        traces = []
        fill_colors = ['brown', 'saddlebrown', 'moccasin', 'lawngreen', 'paleturquoise', 'blue']

        for j, col in enumerate(plot_df.columns):
            fill = 'tonexty' if j > 0 else 'none'
            fillcolor = fill_colors[j] if j < len(fill_colors) else None
            linecolor = 'red' if j == 0 else fillcolor
            traces.append(go.Scatter(
                x=plot_df.index,
                y=plot_df.iloc[:, j],
                name=col,
                fill=fill,
                fillcolor=fillcolor,
                line=dict(color=linecolor)
            ))
        # Set the layout
        # x-axis as months:
        months = [calendar.month_abbr[i] for i in range(1, 13)]
        x_tickvals = [i for i in range(1, 13)]

        layout = go.Layout(
            width=600,
            height=650,
            # title=f'{selected_station} Flow Percentiles (cfs)',
            title={'text': f'{selected_station} Flow Percentiles (cfs)', 'x': 0.5, 'y': 1, 'xanchor': 'center', 'yanchor': 'top',
                    'font': {'size': 20, 'color': 'black'} },
            xaxis=dict(title='Days of the Year', titlefont=dict(size=25, color='black'), tickmode='array', showticklabels=True,
                        showgrid=False, showline=True, linewidth=1, linecolor='black', mirror=True, tickfont=dict(color='black',size=20)),

            yaxis=dict(title='Daily discharge (CFS)', tickmode='array', tickformat='.0f',tickvals=[plot_df.iloc[:, 0].min(), 1000, 10000, 100000, plot_df.iloc[:, -1].max()],
                type='log', tick0=plot_df.iloc[:, 0].min(), dtick=(plot_df.iloc[:, -1].max() - plot_df.iloc[:, 0].min()) / 10, showgrid=False,
                titlefont=dict(size=25, color='black'), showline=True, linewidth=1, linecolor='black', mirror=True, tickfont=dict(color='black',size=20)),

            margin=dict(l=40, r=40, t=40, b=40),
            showlegend=True

            )
        
        # Create the trace for the new line plot
        Line_trace = go.Scatter(
            x=riverflow_df.index,
            y=riverflow_df.iloc[:, 1],
            line=dict(color='black', width=5),
            name="Selected Year"
        )
        traces.append(Line_trace)

        # Create the figure object
        fig = go.Figure(data=traces, layout=layout)

        # st.plotly_chart(fig)
        container = st.container()
        with container:
            st.plotly_chart(fig, use_container_width=True)

    except ValueError as e:
        st.error(str(e))




