import faicons as fa
import plotly.express as px

from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_plotly

app_ui = ui.page_fluid(
    ui.div(
        ui.card(
            ui.card_header(
                ui.div(
                    "RiverFlow hydrographs of main rivers in Pakistan",
                    class_="mx-auto font-weight-bold text-center",
                    style="font-size: 1.5rem;",
                ),
                class_="d-flex justify-content-between align-items-center",
            ),
            ui.div(
                ui.div(
                    ui.div(
                        "Select Station:",
                        class_="d-inline-block",
                        style="font-weight: bold; margin-right: 5px; margin-left: 5px; margin-bottom: 15px;",

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
                    style="width: 250px;"
                ),
                ui.div(
                    ui.div(
                        "Select Year:",
                        class_="d-inline-block",
                        style="font-weight: bold; margin-right: 5px; margin-left: 5px; margin-bottom: 15px",
                    ),
                    ui.input_select(
                        id="years",
                        label=None,
                        choices=[
                            2023,
                            2022,
                            2021,
                            2020,
                            2019,
                            2018,
                            2017,
                            2016,
                            2015,
                            2014,
                        ],
                    ),
                    class_="d-flex align-items-center",
                    style="width: 150px; margin-left: 20px; margin-right: 20px;"

                ),
                class_="d-flex flex-row ",
            ),
            full_screen=False,
            class_="mt-3",
        ),
        class_="container mt-5",
        style="max-width: 1000px;",
    )
)

# def server(input, output, session):

app = App(app_ui, server=None)
