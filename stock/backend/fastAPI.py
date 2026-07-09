from fastapi import FastAPI
from datetime import datetime, timedelta
import json
import logging
import time
import yfinance as yf
    
app = FastAPI()

with open("portfolio.json", "r") as f:
    myStock = json.load(f)
    
celi = 134.81
comptant = 145.44

@app.get("/")
def today_value():
    total = 0
    for b,x in myStock["cash"].items():
        total+= x
    return total

    