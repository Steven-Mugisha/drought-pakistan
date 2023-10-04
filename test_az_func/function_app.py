import azure.functions as func
import logging
from get_riverflow_data import individual_year_data

app = func.FunctionApp()

@app.timer_trigger(schedule="0 */5 * * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def aztimer(myTimer: func.TimerRequest) -> None:
    
    if myTimer.past_due:
        logging.info('The timer is past due!')



    result = individual_year_data("https://www.wapda.gov.pk/river-flow", threshold_days=60)

    logging.info('Python timer trigger function executed.')