# Deployment Guide - NIFTY Bot

## Local Development (Polling Mode)

Run locally with polling (checks Telegram messages every few seconds):

```bash
.\venv\Scripts\activate
python app.py
```

✅ Bot will run in **polling mode** - no webhook needed  
✅ Works for local testing  
✅ Perfect for development

---

## Production on Render (Webhook Mode)

Webhooks are better for production (instant message delivery, uses less CPU).

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Add Flask webhook support"
git push origin main
```

### Step 2: Create Render Web Service

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repo (nifty-bot)
4. Fill in:
   - **Name:** nifty-bot
   - **Environment:** Python 3.11
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`

### Step 3: Set Environment Variables

In Render dashboard, add these under "Environment":

```
TELEGRAM_TOKEN=<your_token>
NEWSDATA_KEY=<your_key>
WEBHOOK_URL=https://nifty-bot-XXXX.onrender.com
RENDER=true
```

(Replace `XXXX` with your Render app ID from the URL)

### Step 4: Set Telegram Webhook

Once deployed, run this in Python (locally):

```python
import requests

TOKEN = "your_token_here"
WEBHOOK_URL = "https://nifty-bot-XXXX.onrender.com/webhook/YOUR_TOKEN"

response = requests.post(
    f"https://api.telegram.org/bot{TOKEN}/setWebhook",
    json={"url": WEBHOOK_URL}
)

print(response.json())
```

### Step 5: Verify

Test the health endpoint:

```bash
curl https://nifty-bot-XXXX.onrender.com/health
```

Expected response:
```json
{"status": "healthy", "bot": "active"}
```

---

## How It Works

### Local Mode (Polling)
- Bot runs `updater.start_polling()`
- Checks Telegram every ~1 second for new messages
- No webhook needed
- Good for testing, but uses more CPU on production

### Production Mode (Webhook)
- Bot runs Flask server on port 10000
- Telegram sends updates to `/webhook/{TOKEN}` endpoint
- **Much faster** response times
- **Lower CPU** usage
- **More reliable** for production

---

## File Structure

```
nifty-bot/
├── app.py                 # Main app (Flask + polling)
├── nifty_rf.joblib       # ML model (trained)
├── config.env            # Environment variables (git-ignored)
├── requirements.txt      # Dependencies
├── render.yaml           # Render deployment config
├── .gitignore            # Protect secrets
└── README.md             # Documentation
```

---

## Health Endpoints

### Local (Polling Mode)
- Bot is running if you see "Scheduler started" in logs
- Test with `/nifty` command in Telegram

### Production (Webhook Mode)
- **Health Check:** `GET /health` → `{"status": "healthy"}`
- **Home:** `GET /` → Shows all endpoints
- **Telegram Webhook:** `POST /webhook/{TOKEN}`

---

## Troubleshooting

### "Bot is not responding"
- Check if app.py is running: `Get-Process python`
- Check logs for errors
- Ensure TELEGRAM_TOKEN is set in config.env

### "Webhook errors" on Render
- Verify WEBHOOK_URL in environment matches your Render domain
- Check that TELEGRAM_TOKEN is correct
- Run webhook setup script (see Step 4)

### "Market data not found"
- Market might be closed (9:15 AM - 3:30 PM IST only)
- Bot will fall back to 90-day historical data automatically

---

## Commands

Once running, Telegram users can use:

```
/start    - Bot introduction
/nifty    - Get latest NIFTY analysis with ML prediction
```

Response includes:
- Live or historical price
- Technical indicators (RSI, EMA20, MACD)
- Market sentiment from news
- ML prediction (UP/DOWN with confidence %)
