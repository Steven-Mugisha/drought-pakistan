import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(layout="wide")

st.title("RiverFlow hydrographs of main river in Pakistan")

col1, col2, col3 = st.columns([1, 1, 1.5])

riverflow_df = pd.read_csv("/Users/mugisha/Desktop/Drought_Pakistan/riverflow/mainInflowrivers.csv")
name_rivers = ['INDUS', 'KABUL', 'JEHLUM', 'CHENAB']

years = ["Year", "2022","2023"]

with col1:
    selected_station = st.selectbox(
        "Select the a river",
        name_rivers,
        index=name_rivers.index("INDUS"),
    )

# with col2:
with st.expander("Acknowledgements"):
    markdown = """
    Data were downoloaded here - http://www.wapda.gov.pk/index.php/river-flow-data
    """
    st.markdown(markdown, unsafe_allow_html=True)


fig = px.line(riverflow_df, x = "Date", y = selected_station, title = selected_station)
fig.update_layout(
     xaxis= dict(),
     yaxis=dict(),
    autosize=False,
    margin=dict(
        autoexpand=False,
        l=100,
        r=20,
        t=110,
     
     )




    # xaxis=dict(
    #     showline=True,
    #     showgrid=False,
    #     showticklabels=True,
    #     linecolor='rgb(204, 204, 204)',
    #     linewidth=2,
    #     ticks='outside',
    #     tickfont=dict(
    #         family='Arial',
    #         size=12,
    #         color='rgb(82, 82, 82)',
        )




st.plotly_chart(fig)



