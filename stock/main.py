from datetime import datetime
import yfinance as yf

myStock = {
    "XGRO.TO": 40,
    "ZBAL.TO": 250,
    "XCNS.TO": 115,
    "XEQT.TO": 30,
    "GBAL.TO": 35,
    "ITA": 5,
    "VBAL.TO": 45
}
celi = 134.81
comptant = 145.44
total = 0

usd_cad = yf.Ticker("CAD=X")
rate = yf.Ticker("CAD=X").fast_info["lastPrice"]

for stock, qty in myStock.items():
    t = yf.Ticker(stock)
    price = t.fast_info["lastPrice"]

    if t.fast_info.get("currency") == "USD":
        price *= rate

    total += price * qty

    print(f"{stock}: {qty} shares at {price:.2f} {t.fast_info.get('currency')} each → {price * qty:.2f} CAD")
total += celi + comptant
print(f"\nTOTAL: {total:.2f} CAD as of {datetime.now()}")