import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

st.set_page_config(layout="wide")

st.title("RiverFlow hydrographs of main rivers in Pakistan")

# st.sidebar.info(
#     """
#         - Data were downoloaded here: <http://www.wapda.gov.pk/index.php/river-flow-data>
    
#     """
# )
@st.cache_data
def get_data():
    riverflow_df = pd.read_csv("/Users/mugisha/Desktop/clone/Drought_Pakistan/mainInflowrivers.csv")
    name_rivers = ['INDUS', 'KABUL', 'JEHLUM', 'CHENAB']
    years = ["All Years","2022","2023"]
    return riverflow_df, name_rivers, years

riverflow_df,name_rivers,years = get_data()

col1, col2, col3 = st.columns([.2, .15, 1.5])

with col1:
    selected_station = st.selectbox(
        "Select Station",
        name_rivers,
        index=name_rivers.index("INDUS"),
    )
with col2:
    selected_year = st.selectbox(
        "Select Year",
        years,
        index=years.index("All Years")
    )
@st.cache_data
def get_filtered_data(df,year):
    df["Year"] = df["Year"].astype(str)
    filtered_df = df[df["Year"] == year]
    return filtered_df

if selected_year != "All Years":
    df_ToPlot = get_filtered_data(riverflow_df, selected_year)
else:
    df_ToPlot = riverflow_df

try:
    # fig = px.area(df_ToPlot, x="Date", y=selected_station, title=selected_station, color="Year",
    #               color_discrete_sequence=['darkorange'])
    fig = px.line(df_ToPlot, x="Date", y=selected_station, title=selected_station, color="Year")
    fig.update_traces(line_width=3)
    fig.update_layout(
        width=1000,
        height=500,
        yaxis_title="Riverflow in cfs",
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis=dict(tickfont=dict(size=16)),
        yaxis=dict(tickfont=dict(size=16))
    )
    st.plotly_chart(fig)

except ValueError as e:
    st.error(str(e))
