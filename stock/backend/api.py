from flask import Flask, jsonify
from datetime import datetime, timedelta
import logging
import time
import yfinance as yf

app = Flask(__name__)
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

# ----------------------------------------------------------------------
# Configuration du portfolio
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# Cache simple en mémoire pour éviter de spammer Yahoo Finance
# ----------------------------------------------------------------------
CACHE_DURATION = 300  # secondes (5 minutes)
_cache = {}  # { date_str: {"total": float, "timestamp": float} }


def getRate():
    return yf.Ticker("CAD=X").fast_info["lastPrice"]


def getTotalByDate(date_str):
    rate = getRate()
    total = 0
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    test_stock = list(myStock.keys())[0]
    t_test = yf.Ticker(test_stock)
    trading_date = target_date

    history = t_test.history(
        start=trading_date.strftime("%Y-%m-%d"),
        end=(trading_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        interval="1d"
    )
    while history.empty:
        trading_date -= timedelta(days=1)
        history = t_test.history(
            start=trading_date.strftime("%Y-%m-%d"),
            end=(trading_date + timedelta(days=1)).strftime("%Y-%m-%d"),
            interval="1d"
        )

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

    return round(total + celi + comptant, 2)


def getTotalCached(date_str):
    """Retourne le total depuis le cache si récent, sinon recalcule."""
    now = time.time()
    cached = _cache.get(date_str)
    if cached and (now - cached["timestamp"]) < CACHE_DURATION:
        return cached["total"], True  # True = depuis le cache

    total = getTotalByDate(date_str)
    _cache[date_str] = {"total": total, "timestamp": now}
    return total, False


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "Serveur portfolio actif"})


@app.route("/total")
def total_today():
    today = datetime.now().strftime("%Y-%m-%d")
    total, from_cache = getTotalCached(today)
    return jsonify({
        "date": today,
        "total": total,
        "from_cache": from_cache
    })


@app.route("/total/<date_str>")
def total_by_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Format de date invalide, utiliser YYYY-MM-DD"}), 400

    total, from_cache = getTotalCached(date_str)
    return jsonify({
        "date": date_str,
        "total": total,
        "from_cache": from_cache
    })


@app.route("/history/<int:days>")
def history(days):
    """Retourne le total des N derniers jours (depuis aujourd'hui)."""
    results = []
    today = datetime.now()
    for i in range(days):
        d = (today - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        try:
            total, _ = getTotalCached(d)
            results.append({"date": d, "total": total})
        except Exception:
            continue  # ignore les jours sans données (weekends, etc.)
    return jsonify(results)


if __name__ == "__main__":
    # host="0.0.0.0" permet d'accepter les connexions depuis le réseau local (ex: ESP32)
    app.run(host="0.0.0.0", port=5000, debug=False)