import logging

import azure.functions as func

from riverflow.get_riverflow_data import update_riverflow_data

URL = "https://www.wapda.gov.pk/river-flow"

app = func.FunctionApp()


@app.schedule(
    schedule="*/5 * * * *", arg_name="myTimer", run_on_startup=True, use_monitor=False
)
def test_get_riverflow_data(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info("The timer is past due!")

    update_riverflow_data(URL)
    logging.info("Python timer trigger function executed.")