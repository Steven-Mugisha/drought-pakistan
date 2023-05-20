import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from flow_percentiles import create_percentile_dataframe
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the desired logging level
logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")

st.title("RiverFlow hydrographs of main rivers in Pakistan")

col1, col2, col3 = st.columns([.3, .3, 1.5])

# Varaibles for selection: 
name_rivers = ['Chenab_at_Marala','Indus_at_Tarbela', 'Jhelum_at_Mangla', 'Kabul_at_Nowshera']
recent_years = ["Select Year",2010,2011]
with col1:
    
    selected_station = st.selectbox(
        "Select Station",
        name_rivers,
        index = name_rivers.index(name_rivers[0])
    )

with col2:
    selected_year = st.selectbox(
        "Select Year",
        recent_years,
        index = recent_years.index(recent_years[0])
    )

@st.cache_data
def get_data(selected_station) -> pd.DataFrame:
    riverflow_df = pd.read_csv("/Users/mugisha/Desktop/clone/Drought_Pakistan/riverflow_pakistan/flows/"+selected_station+".csv")
    riverflow_df =  riverflow_df[riverflow_df["Year"] == selected_year]
    return riverflow_df

if selected_year != "Select Year":
    riverflow_df = get_data(selected_station)
    print(riverflow_df)
# else:
#     logger.info(" !!!! You can get to me !!!")

# print(riverflow_df)

# @st.cache_data
# def selected_year_df(df,year):
#     df["Year"] = df["Year"].astype(str)
#     filtered_df = df[df["Year"] == year]
#     return filtered_df

# riverflow_df = get_data(selected_station)


try:
    Plot_dataframe = create_percentile_dataframe(selected_station)

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
            tickvals=[Plot_dataframe.iloc[:, 0].min(),1000,5000, 10000, 25000, 50000,
                      100000, 200000, Plot_dataframe.iloc[:, -1].max()],
            type='log',
            tick0=Plot_dataframe.iloc[:, 0].min(),
            dtick=(Plot_dataframe.iloc[:, -1].max() -
                   Plot_dataframe.iloc[:, 0].min()) / 10,
            showgrid=False,
            titlefont=dict(size=10)
        )
    )

    # Create the figure object
    fig = go.Figure(data=traces, layout=layout)


    # # Add the new line plot
    # Line_dataframe = df_ToPlot
    # traces.append(go.Scatter(
    #     x="Date",
    #     y=selected_station,  # Replace 'column_name' with the actual column you want to plot
    #     line=dict(color='black')  # Customize the line color if needed
    # ))
    # fig.add_trace(traces[-1])



    # st.plotly_chart(fig)
    container =st.container()
    with container:
        st.plotly_chart(fig, use_container_width=True, width=1, height=0)

except ValueError as e:
    st.error(str(e))
