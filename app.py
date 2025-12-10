import os
from dotenv import load_dotenv
from flask import Flask, request
from telegram import Update
from telegram.ext import Dispatcher, CommandHandler
import pandas as pd
import numpy as np
import ta
import joblib
import requests
import yfinance as yf
import logging

# Load environment
load_dotenv("config.env")
TOKEN = os.getenv("TELEGRAM_TOKEN")
NEWS_KEY = os.getenv("NEWSDATA_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://localhost:5000")

# Load model
rf_model = joblib.load("nifty_rf.joblib")

# Flask app
app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------
# MARKET NEWS
# ---------------------------------------------------
def get_market_news():
    try:
        url = f"https://newsdata.io/api/1/news?apikey={NEWS_KEY}&q=nifty%2050%20OR%20sensex%20OR%20rbi%20OR%20interest%20rate&language=en&country=in"
        response = requests.get(url, timeout=6).json()

        articles = response.get("results", [])
        if not articles:
            return [], "No market news available."

        seen = set()
        unique_headlines = []
        for a in articles:
            title = a.get("title", "")
            if title and title not in seen:
                seen.add(title)
                unique_headlines.append(title)
                if len(unique_headlines) >= 2:
                    break

        if not unique_headlines:
            return [], "No relevant news found."

        text = "\n• " + "\n• ".join(unique_headlines)
        return unique_headlines, text

    except Exception as e:
        logger.error(f"[NEWS ERROR] {e}")
        return [], "News unavailable."


# ---------------------------------------------------
# SENTIMENT
# ---------------------------------------------------
def analyze_sentiment(headlines):
    if not headlines:
        return "Neutral", "🟡 Neutral — No major news impact."

    positive = ["gain", "up", "rise", "bull", "surge", "profit", "recovery"]
    negative = ["fall", "down", "drop", "loss", "war", "fear", "inflation", "selloff"]

    score = 0
    for h in headlines:
        text = h.lower()
        if any(w in text for w in positive):
            score += 1
        if any(w in text for w in negative):
            score -= 1

    if score > 0:
        return "Bullish", "🟢 Bullish sentiment — Positive news"
    elif score < 0:
        return "Bearish", "🔴 Bearish sentiment — Negative news"
    else:
        return "Neutral", "🟡 Neutral — Mixed news"


# ---------------------------------------------------
# BACKTEST MODE
# ---------------------------------------------------
def get_backtest_candle():
    for period in ["90d", "60d", "30d"]:
        try:
            df = yf.download("^NSEI", period=period, progress=False)

            if df.empty:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] for c in df.columns]

            df = df.reset_index().dropna(subset=["Close"])
            close = df["Close"]

            df["rsi"] = ta.momentum.RSIIndicator(close).rsi()
            df["ema20"] = ta.trend.EMAIndicator(close, 20).ema_indicator()
            macd_obj = ta.trend.MACD(close)
            df["macd"] = macd_obj.macd()
            df["signal"] = macd_obj.macd_signal()

            df = df.dropna().tail(1)

            if len(df):
                return df.iloc[-1]

        except:
            continue

    return pd.Series({
        "Close": 26000,
        "rsi": 50,
        "ema20": 26000,
        "macd": 0,
        "signal": 0
    })


# ---------------------------------------------------
# LIVE DATA
# ---------------------------------------------------
def get_nifty_analysis():
    url = "https://www.nseindia.com/api/chart-databyindex?index=NIFTY%2050&preopen=true"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com/"
    }

    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    data = session.get(url, headers=headers).json()

    candles = data.get("grapthData", [])

    if not candles:
        raise Exception("Market closed")

    df = pd.DataFrame(candles, columns=["time", "Close"])
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df = df.dropna()

    df["rsi"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
    df["ema20"] = ta.trend.EMAIndicator(df["Close"], 20).ema_indicator()
    macd = ta.trend.MACD(df["Close"])
    df["macd"] = macd.macd()
    df["signal"] = macd.macd_signal()

    df = df.dropna()
    return df.iloc[-1]


# ---------------------------------------------------
# ML PREDICTION
# ---------------------------------------------------
def get_ml_prediction(row):
    X = np.array([[row["rsi"], row["ema20"], row["macd"], row["signal"]]])
    pred = rf_model.predict(X)[0]
    prob = rf_model.predict_proba(X)[0][pred]
    direction = "UP 🔼" if pred == 1 else "DOWN 🔽"
    return direction, round(prob * 100, 2)


# ---------------------------------------------------
# TELEGRAM COMMANDS
# ---------------------------------------------------
def start(update, context):
    update.message.reply_text(
        "Bot is working! 🚀\nUse /nifty to get the latest NIFTY analysis."
    )


def nifty(update, context):
    update.message.reply_text("Fetching NIFTY data… ⏳")

    try:
        row = get_nifty_analysis()
        source = "📡 *Live Data*"
    except:
        row = get_backtest_candle()
        source = "📦 *Last Available Data*"

    headlines, news_text = get_market_news()
    sentiment, sentiment_msg = analyze_sentiment(headlines)
    direction, confidence = get_ml_prediction(row)

    reasons = []
    if row["rsi"] > 60: 
        reasons.append("RSI overbought")
    if row["rsi"] < 40: 
        reasons.append("RSI oversold")
    if row["macd"] > row["signal"]: 
        reasons.append("MACD bullish")
    else: 
        reasons.append("MACD bearish")
    reasons.append(f"News: {sentiment}")

    reason_text = " | ".join(reasons)

    msg = f"""
📊 *NIFTY Market Update*
-----------------------------
{source}
💰 *Price:* {row['Close']:.2f}
📈 *RSI:* {row['rsi']:.2f}
📉 *EMA20:* {row['ema20']:.2f}
📊 *MACD:* {row['macd']:.2f}
📊 *Signal:* {row['signal']:.2f}

📰 *Market News:*
{news_text}

📊 *Sentiment:* {sentiment_msg}

🤖 *ML Prediction:* {direction}
📌 *Confidence:* {confidence}%

🧠 *Reason:* {reason_text}
"""

    update.message.reply_text(msg, parse_mode="Markdown")


# ---------------------------------------------------
# FLASK ROUTES
# ---------------------------------------------------
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Render"""
    return {"status": "healthy", "bot": "active"}, 200


@app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook():
    """Telegram webhook endpoint"""
    try:
        from telegram import Bot
        bot = Bot(TOKEN)
        update = Update.de_json(request.get_json(), bot=bot)
        
        if update.message and update.message.text:
            if update.message.text == '/start':
                start(update, None)
            elif update.message.text == '/nifty':
                nifty(update, None)
        
        return "ok", 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "error", 400


@app.route('/', methods=['GET'])
def index():
    """Homepage"""
    return {
        "status": "Bot is running",
        "endpoints": {
            "health": "/health",
            "webhook": f"/webhook/{TOKEN}",
            "home": "/"
        }
    }, 200


# ---------------------------------------------------
# LOCAL POLLING MODE
# ---------------------------------------------------
def run_locally():
    """Run bot with polling (local development)"""
    from telegram.ext import Updater
    
    logger.info("Starting bot in polling mode (local)...")
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("nifty", nifty))

    updater.start_polling()
    logger.info("Bot is polling locally...")
    updater.idle()


# ---------------------------------------------------
# MAIN
# ---------------------------------------------------
if __name__ == "__main__":
    import sys
    
    # Check if running on Render or locally
    is_render = os.getenv("RENDER", "false").lower() == "true"
    
    if is_render:
        # Production: Run Flask with webhooks
        logger.info("Starting bot in webhook mode (Render)...")
        port = int(os.getenv("PORT", 10000))
        app.run(host="0.0.0.0", port=port, debug=False)
    else:
        # Local development: Run with polling
        run_locally()
