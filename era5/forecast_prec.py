#!/usr/bin/env python
from ecmwfapi import ECMWFDataServer
import time
import os
import ecmwfapi


def forecast_prec():
    while True:
        try:
            c = ECMWFDataServer()
            c.retrieve(
                {  
                 
                    })
                   
    
            if os.path.exists("test.nc"):
                print("File saved successfully")
            else:
                print("Error: File not saved")
            return

        except ecmwfapi.api.APIException as e:
            print(e)
            msg = str(e)
            if "USER_QUEUED_LIMIT_EXCEEDED" not in msg:
                raise

        time.sleep(10)

if __name__ == "__main__":
    forecast_prec()




    #  "dataset": "interim",
    #                 "date": "2023-01-01/to/2023-01-02",
    #                 "expver": "prod",
    #                 "area": "32.5/69/32.3/69.2",
    #                 "grid": "0.5/0.5",
    #                 "levtype": "sfc",
    #                 "origin": "cwao",
    #                 "param": "228228",
    #                 "step": "24",
    #                 "time": "00:00:00",
    #                 "type": "cf",
    #                 "format": "netcdf",
    #                 "target": "test.nc"