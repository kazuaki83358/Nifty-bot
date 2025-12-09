import os
import threading
from flask import Flask
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler
import pandas as pd
import numpy as np
import ta
import joblib
import requests
import yfinance as yf

# ---------------------------------------------------
# LOAD ENV + MODEL
# ---------------------------------------------------
load_dotenv("config.env")
#TOKEN = os.getenv("TELEGRAM_TOKEN")

Token = "8073446746:AAGIEUzcLDA0rpVHBsa5xEOkblBjPxcagvI"
rf_model = joblib.load("nifty_rf.joblib")


# ---------------------------------------------------
# START COMMAND
# ---------------------------------------------------
def start(update, context):
    update.message.reply_text(
        "Bot is working! 🚀\nUse /nifty to get the latest NIFTY analysis."
    )


# ---------------------------------------------------
# BACKTEST MODE (when market closed)
# ---------------------------------------------------
def get_backtest_candle():
    try:
        df = yf.download("^NSEI", period="30d", progress=False)

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        df = df.reset_index().dropna()

        df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
        df["ema20"] = ta.trend.EMAIndicator(df["Close"], window=20).ema_indicator()
        macd = ta.trend.MACD(df["Close"])
        df["macd"] = macd.macd()
        df["signal"] = macd.macd_signal()

        df = df.dropna()
        return df.iloc[-1]

    except:
        # fallback values
        return pd.Series({
            "Close": 26000.0,
            "rsi": 50.0,
            "ema20": 26000.0,
            "macd": 0.0,
            "signal": 0.0
        })


# ---------------------------------------------------
# LIVE MARKET DATA (NSE realtime)
# ---------------------------------------------------
def get_nifty_analysis():
    url = "https://www.nseindia.com/api/chart-databyindex?index=NIFTY%2050&preopen=true"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/"
    }

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers, timeout=10)

    try:
        data = response.json()
    except:
        raise Exception("NSE did not return valid data")

    candles = data.get("grapthData", [])

    if len(candles) == 0:
        raise Exception("Market closed — no live candles")

    df = pd.DataFrame(candles, columns=["time", "Close"])
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df = df.dropna()

    df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
    df["ema20"] = ta.trend.EMAIndicator(df["Close"], window=20).ema_indicator()
    macd = ta.trend.MACD(df["Close"])
    df["macd"] = macd.macd()
    df["signal"] = macd.macd_signal()

    df = df.dropna()

    return df.iloc[-1]


# ---------------------------------------------------
# ML PREDICTION
# ---------------------------------------------------
def get_ml_prediction(row):
    rsi = float(row["rsi"])
    ema20 = float(row["ema20"])
    macd = float(row["macd"])
    signal = float(row["signal"])

    features = np.array([[rsi, ema20, macd, signal]])

    pred = rf_model.predict(features)[0]
    prob = rf_model.predict_proba(features)[0][pred]

    direction = "UP 🔼" if pred == 1 else "DOWN 🔽"
    return direction, round(prob * 100, 2)


# ---------------------------------------------------
# /nifty COMMAND
# ---------------------------------------------------
def nifty(update, context):
    update.message.reply_text("Fetching NIFTY data… ⏳")

    try:
        row = get_nifty_analysis()
        data_source = "📡 *Live Data*"
    except:
        row = get_backtest_candle()
        data_source = "📦 *Last Available Data*"

    direction, confidence = get_ml_prediction(row)

    msg = f"""
📊 *NIFTY Market Update*
-----------------------------
{data_source}
💰 *Price:* {row['Close']:.2f}
📈 *RSI:* {row['rsi']:.2f}
📉 *EMA20:* {row['ema20']:.2f}
📊 *MACD:* {row['macd']:.2f}
📊 *Signal:* {row['signal']:.2f}

🤖 *ML Prediction:* {direction}
📌 *Confidence:* {confidence}%
"""

    update.message.reply_text(msg, parse_mode="Markdown")


# ---------------------------------------------------
# FLASK HEALTH SERVER (For Render + UptimeRobot)
# ---------------------------------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"


def run_flask():
    app.run(host="0.0.0.0", port=10000)


# ---------------------------------------------------
# MAIN ENTRY
# ---------------------------------------------------
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("nifty", nifty))

    updater.start_polling()
    print("Bot is running...")
    updater.idle()


if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    main()
