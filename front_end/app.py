import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from flow_percentiles import create_percentile_dataframe
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

st.markdown("<h1 style='font-size: 30px;'>RiverFlow hydrographs of main rivers in Pakistan</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, .18, .18])

# Varaibles for selection:
name_rivers = ['Chenab_at_Marala', 'Indus_at_Tarbela','Jhelum_at_Mangla', 'Kabul_at_Nowshera']

recent_years = [2019,2018,2017]

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
    
def station_datasets(selected_station) -> pd.DataFrame:
    """Load the station data set from the directory and selects the year of interest"""

    station_df = pd.read_csv(f"{path}/flows/"+selected_station+".csv")
    year_subset_df = station_df[station_df["Year"] == selected_year]
    year_subset_df["Year"] = year_subset_df["Year"].astype(str)
    year_subset_df = year_subset_df.set_index(pd.Index(range(1, 366)))
    return year_subset_df

if selected_year != "Select Year":
    riverflow_df = station_datasets(selected_station)
    # st.write(riverflow_df)

with col1:  
  
    try:
        Plot_dataframe = create_percentile_dataframe(selected_station)
        # set the index from 1 to 365
        Plot_dataframe = Plot_dataframe.set_index(pd.Index(range(1, 366)))

        # Create the traces
        traces = []
        fill_colors = ['brown', 'saddlebrown', 'moccasin', 'lawngreen', 'paleturquoise', 'blue']

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
        # x-axis as months:
        months = [calendar.month_abbr[i] for i in range(1, 13)]
        x_tickvals = [i for i in range(1, 13)]

        layout = go.Layout(
            width=600,
            height=650,
            title=f'{selected_station} Flow Percentiles (cfs)',
            xaxis=dict(
                title='Days of the Year',
                titlefont=dict(size=15, color='black'),
                tickmode='array',
                # ticktext=months,
                showticklabels=True,
                showgrid=False,
                # dtick=1,
                showline=True,
                linewidth=1,
                linecolor='black',
                mirror=True,
                tickfont=dict(color='black',size=15),
            ),

            yaxis=dict(
                title='Daily discharge (CFS)',
                tickmode='array',
                tickformat='.0f',
                tickvals=[Plot_dataframe.iloc[:, 0].min(), 1000, 10000, 100000, Plot_dataframe.iloc[:, -1].max()],
                type='log',
                tick0=Plot_dataframe.iloc[:, 0].min(),
                dtick=(Plot_dataframe.iloc[:, -1].max() - Plot_dataframe.iloc[:, 0].min()) / 10,
                showgrid=False,
                titlefont=dict(size=15, color='black'),
                showline=True,
                linewidth=1,
                linecolor='black',
                mirror=True,
                tickfont=dict(color='black',size=15)
            ),
            margin=dict(l=40, r=40, t=40, b=40),  # Add margin to create space around the plot
            showlegend=True
        )

        # Create the trace for the new line plot
        Line_trace = go.Scatter(
            x=riverflow_df.index,
            y=riverflow_df.iloc[:, 1],
            line=dict(color='black', width=3),
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
