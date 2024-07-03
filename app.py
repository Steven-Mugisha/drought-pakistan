# import faicons as fa
import os

import pandas as pd
import plotly.graph_objs as go
from dotenv import load_dotenv
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_plotly

from riverflow.flow_percentiles import percentiles

load_dotenv()
RIVERFLOW_FILE = os.getenv("riverflow_db_dir")

app_ui = ui.page_fluid(
    ui.div(
        ui.card(
            ui.card_header(
                ui.div(
                    "RiverFlow Hydrographs of Main Rivers in Pakistan",
                    class_="mx-auto font-weight-bold text-center",
                    style="font-size: 1.3rem;",
                ),
                class_="d-flex justify-content-between align-items-center",
            ),
            ui.div(
                ui.div(
                    ui.div(
                        "Select Station:",
                        class_="d-inline-block",
                        style="font-weight: bold; font-size: 13px; margin-right: 5px; margin-left: 5px; margin-bottom: 15px; white-space: nowrap;",
                    ),
                    ui.input_select(
                        id="stations",
                        label=None,
                        choices={
                            "indus_at_tarbela (cfs)": "INDUS_AT_TARBELA",
                            "kabul_at_nowshera (cfs)": "KABUL_AT_NOWSHERA",
                            "jhelum_at_mangal (cfs)": "JHELUM_AT_MANGAL",
                            "cheanab_at_marala (cfs)": "CHEANAB_AT_MARALA",
                        },
                    ),
                    class_="d-flex align-items-center",
                    style="width: 250px; font-size: 1px",
                ),
                ui.div(
                    ui.div(
                        "Select Year:",
                        class_="d-inline-block",
                        style="font-weight: bold; font-size: 13px; margin-right: 5px; margin-left: 5px; margin-bottom: 15px; white-space: nowrap;",
                    ),
                    ui.input_select(
                        id="Years",
                        label=None,
                        choices=[
                            2024,
                            2023,
                            2022,
                            2021,
                            2020,
                            2019,
                            2018,
                            2017,
                            2016,
                            2015,
                        ],
                    ),
                    class_="d-flex align-items-center",
                    style="width: 170px; margin-left: 20px; margin-right: 20px;",
                ),
                class_="d-flex flex-row justify-content-center align-items-center mt-3",
            ),
            ui.div(
                ui.div(
                    output_widget("riverflow_percentages"),
                    class_="d-flex justify-content-center",
                    style="width: 1000px; height: 600px;",
                ),
                class_="d-flex justify-content-center mt-4 mb-5",
                style="overflow-x: auto; overflow-y: hidden; white-space: nowrap; width: 100%;",
            ),
            full_screen=True,
            class_="mt-3 custom-class card-body bg-light border border-darkgrey p-2 mb-5 bg-white rounded",
        ),
        class_="container mt-5 mb-20",
        style="width: 1000px; ",
    ),
    ui.include_css("./styles.css"),
)


def selected_station_df(station: str, selected_year: str) -> pd.DataFrame:
    """Load the station dataset and select the station and year of interest."""
    try:
        station_df = pd.read_csv(RIVERFLOW_FILE, index_col=0, parse_dates=True)
        station_df = station_df[[station, "Year"]]
        year_subset_df = station_df[station_df["Year"] == int(selected_year)]
        year_subset_df = year_subset_df.set_index(
            pd.Index(range(1, len(year_subset_df) + 1))
        )
        return year_subset_df
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()


def server(input, ouput, session):
    @render_plotly
    def riverflow_percentages():

        selected_station = input.stations.get()
        plot_df = percentiles(selected_station)
        plot_df = plot_df.set_index(pd.Index(range(1, 366)))

        traces = []
        fill_colors = [
            "brown",
            "saddlebrown",
            "moccasin",
            "lawngreen",
            "paleturquoise",
            "blue",
        ]

        for j, col in enumerate(plot_df.columns):
            fill = "tonexty" if j > 0 else "none"
            fillcolor = fill_colors[j] if j < len(fill_colors) else None
            linecolor = "red" if j == 0 else fillcolor
            traces.append(
                go.Scatter(
                    x=plot_df.index,
                    y=plot_df.iloc[:, j],
                    name=col,
                    fill=fill,
                    fillcolor=fillcolor,
                    line=dict(color=linecolor),
                )
            )

        layout = go.Layout(
            width=900,
            height=600,
            title={
                "text": f"{selected_station.replace(' ', '_').upper().split('_(')[0]} Flow Percentiles (cfs)",
                "x": 0.5,
                "y": 0.99,
                "xanchor": "center",
                "yanchor": "top",
                "font": {"size": 15, "color": "black"},
            },
            plot_bgcolor="whitesmoke",
            xaxis=dict(
                title="Days of the Year",
                titlefont=dict(size=15, color="black"),
                tickmode="array",
                showticklabels=True,
                showgrid=False,
                showline=True,
                linewidth=1,
                linecolor="black",
                mirror=True,
                tickfont=dict(color="black", size=15),
            ),
            yaxis=dict(
                title="Daily Discharge (CFS)",
                tickmode="array",
                tickformat=".0f",
                tickvals=[
                    plot_df.iloc[:, 0].min(),
                    1000,
                    10000,
                    100000,
                    plot_df.iloc[:, -1].max(),
                ],
                type="log",
                tick0=plot_df.iloc[:, 0].min(),
                dtick=(plot_df.iloc[:, -1].max() - plot_df.iloc[:, 0].min()) / 10,
                showgrid=False,
                titlefont=dict(size=15, color="black"),
                showline=True,
                linewidth=1,
                linecolor="black",
                mirror=True,
                tickfont=dict(color="black", size=15),
            ),
            margin=dict(l=40, r=40, t=40, b=40),
            showlegend=True,
        )

        # current state of riverflow
        selected_year = input.Years.get()
        riverflow_df = selected_station_df(selected_station, selected_year)
        Line_trace = go.Scatter(
            x=riverflow_df.index,
            y=riverflow_df[selected_station],
            line=dict(color="black", width=5),
            name=selected_year,
        )
        traces.append(Line_trace)

        fig = go.Figure(data=traces, layout=layout)

        return fig


app = App(app_ui, server)
