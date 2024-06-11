from shiny import App, reactive, render, ui

app_ui = ui.page_fixed(
)

def server(input, output, session):

# app = App(app_ui, server)