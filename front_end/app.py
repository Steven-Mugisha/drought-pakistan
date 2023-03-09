import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go


st.set_page_config(layout="wide")

st.title("RiverFlow hydrographs of main rivers in Pakistan")

st.sidebar.info(
    """
        - Data were downoloaded here: <http://www.wapda.gov.pk/index.php/river-flow-data>
    
    """
)


@st.cache_data
def get_data():

    riverflow_df = pd.read_csv("/Users/mugisha/Desktop/Drought_Pakistan/riverflow/mainInflowrivers.csv")
    name_rivers = ['INDUS', 'KABUL', 'JEHLUM', 'CHENAB']
    years = ["Year", "2022","2023"]
    
    return riverflow_df, name_rivers, years


riverflow_df,name_rivers,years = get_data()



col1, col2, col3 = st.columns([.3, 1, 1.5])
with col1:
    selected_station = st.selectbox(
        "Select Station",
        name_rivers,
        index=name_rivers.index("INDUS"),
    )

# # with col2:
# with st.expander("Acknowledgements"):
#     markdown = """
#     Data were downoloaded here - http://www.wapda.gov.pk/index.php/river-flow-data
#     """
#     st.markdown(markdown, unsafe_allow_html=True)


fig = px.line(riverflow_df, x = "Date", y = selected_station, title = selected_station,
              color_discrete_sequence=["red"])
fig.add_trace(
    go.Scatter(x=riverflow_df['Date'], y=riverflow_df[selected_station], mode='lines', name=selected_station)
)


fig.update_layout(
    width=1000,
    height=500,
    yaxis_title="Riverflow in cfs",
    margin=dict(l=50, r=50, t=50, b=50),
)


st.plotly_chart(fig)



