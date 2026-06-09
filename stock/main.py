from datetime import datetime, timedelta
import logging
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
total = []
yesterdayTotal = 0
usd_cad = yf.Ticker("CAD=X")
rate = yf.Ticker("CAD=X").fast_info["lastPrice"]


def getTotalByDate(date_str):
    total = 0
    
    target_date = datetime.strptime(date_str, "%Y-%m-%d")

    test_stock = list(myStock.keys())[0]
    t_test = yf.Ticker(test_stock)
    
    trading_date = target_date
    history = t_test.history(start=trading_date.strftime("%Y-%m-%d"), 
                             end=(trading_date + timedelta(days=1)).strftime("%Y-%m-%d"), 
                             interval="1d")
    
    while history.empty:
        trading_date = trading_date - timedelta(days=1)
        history = t_test.history(start=trading_date.strftime("%Y-%m-%d"), 
                                 end=(trading_date + timedelta(days=1)).strftime("%Y-%m-%d"), 
                                 interval="1d")
    

    start_str = trading_date.strftime("%Y-%m-%d")
    end_str = (trading_date + timedelta(days=1)).strftime("%Y-%m-%d")
    
    for stock, qty in myStock.items():
        t = yf.Ticker(stock)
        stock_hist = t.history(start=start_str, end=end_str, interval="1d")["Close"]
        
        if not stock_hist.empty:
            price = stock_hist.iloc[-1]
            
            if t.fast_info.get("currency") == "USD":
                price *= rate
                
            total += price * qty
            
    return total + celi + comptant

logging.getLogger('yfinance').setLevel(logging.CRITICAL)
for date in range(1, 9):
    date_str = f"2026-06-{date:02d}"
    total.append(getTotalByDate(date_str))
    print(f"\nTOTAL: {total[-1]:.2f} CAD as of {date_str}")
for i in range(1, len(total)):
    gain = total[i] - total[i-1]
    print(f"GAIN from {i-1} to {i}: {gain:.2f} CAD")

# print(ita["last"].iloc[0:10])
#     print(f"{stock}: {qty} shares at {price:.2f} {t.fast_info.get('currency')} each → {price * qty:.2f} CAD")
# total += celi + comptant 
# yesterdayTotal += celi + comptant
# print(f"\nTOTAL: {total:.2f} CAD as of {datetime.now()}")
# print(f"YESTERDAY TOTAL: {yesterdayTotal:.2f} CAD")
# print(f"GAIN: {total - yesterdayTotal:.2f} CAD")