import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from flow_percentiles import create_percentile_dataframe

st.set_page_config(layout="wide")



st.title("RiverFlow hydrographs of main rivers in Pakistan")

# st.sidebar.info(
#     """
#         - Data were downoloaded here: <http://www.wapda.gov.pk/index.php/river-flow-data>
    
#     """
# )
@st.cache_data
def get_data(station:str) -> pd.DataFrame:
    riverflow_df = pd.read_csv("/Users/mugisha/Desktop/clone/Drought_Pakistan/riverflow_pakistan/flows/"+station+".csv")
    # name_rivers = ['INDUS', 'KABUL', 'JEHLUM', 'CHENAB']
    # years = ["All Years","2022","2023"]
    return riverflow_df

riverflow_df = get_data("indus_at_tarbela")

col1, col2, col3 = st.columns([.3, .15, 1.5])


# Varaibles for selection: 
name_rivers = ['Chenab_at_Marala','Indus_at_Tarbela', 'Jhelum_at_Mangla', 'Kabul_at_Nowshera']
with col1:
    
    selected_station = st.selectbox(
        "Select Station",
        name_rivers,
        index = name_rivers.index(name_rivers[0])
    )

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

    # st.plotly_chart(fig)
    container =st.container()
    with container:
        st.plotly_chart(fig, use_container_width=True, width=1, height=6)

except ValueError as e:
    st.error(str(e))




# with col2:
#     selected_year = st.selectbox(
#         "Select Year",
#         years,
#         index=years.index("All Years")
#     )


# @st.cache_data
# def get_filtered_data(df,year):
#     df["Year"] = df["Year"].astype(str)
#     filtered_df = df[df["Year"] == year]
#     return filtered_df

# if selected_year != "All Years":
#     df_ToPlot = get_filtered_data(riverflow_df, selected_year)
# else:
#     df_ToPlot = riverflow_df

# try:
#     # fig = px.area(df_ToPlot, x="Date", y=selected_station, title=selected_station, color="Year",
#     #               color_discrete_sequence=['darkorange'])
#     fig = px.line(df_ToPlot, x="Date", y=selected_station, title=selected_station, color="Year")
#     fig.update_traces(line_width=3)
#     fig.update_layout(
#         width=1000,
#         height=500,
#         yaxis_title="Riverflow in cfs",
#         margin=dict(l=50, r=50, t=50, b=50),
#         xaxis=dict(tickfont=dict(size=16)),
#         yaxis=dict(tickfont=dict(size=16))
#     )
#     st.plotly_chart(fig)

# except ValueError as e:
#     st.error(str(e))
