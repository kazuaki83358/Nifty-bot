# 🤖 NIFTY Trading Bot

A Telegram bot that provides real-time NIFTY 50 market analysis with ML-powered predictions using Random Forest classifier.

## 📋 Features

- 📊 Real-time NIFTY 50 price data
- 📈 Technical indicators (RSI, EMA20, MACD, Signal Line)
- 🤖 Machine Learning predictions (UP/DOWN) with confidence scores
- 📦 Historical data fallback when market is closed
- ⚡ Built with Python-Telegram-Bot

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd nifty-bot
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `config.env` file:
```env
TELEGRAM_TOKEN=your_telegram_bot_token_here
```

### Running the Bot

```bash
python nifty_bot.py
```

## 📱 Bot Commands

- `/start` - Welcome message and bot info
- `/nifty` - Get latest NIFTY 50 analysis with ML prediction

## 🧠 Model Training

The bot uses a Random Forest classifier trained on historical NIFTY 50 data. To retrain the model:

1. Open `train_rf.ipynb` in Jupyter Notebook
2. Run all cells to fetch fresh data and train the model
3. The model will be saved as `nifty_rf.joblib`

### Model Features:
- RSI (Relative Strength Index)
- EMA20 (20-period Exponential Moving Average)
- MACD (Moving Average Convergence Divergence)
- Signal Line

## 📊 Technical Indicators

- **RSI**: Momentum indicator measuring speed and magnitude of price changes
- **EMA20**: Smoothed moving average giving more weight to recent prices
- **MACD**: Trend-following momentum indicator
- **Signal Line**: 9-period EMA of MACD

## 🛠️ Tech Stack

- **Python 3.11**
- **python-telegram-bot** - Telegram Bot API
- **yfinance** - Market data fetching
- **ta** - Technical analysis indicators
- **scikit-learn** - Machine learning model
- **pandas** - Data manipulation
- **numpy** - Numerical computing

## 📂 Project Structure

```
nifty-bot/
├── nifty_bot.py          # Main bot script
├── train_rf.ipynb        # Model training notebook
├── nifty_rf.joblib       # Trained ML model
├── config.env            # Configuration (not in repo)
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## ⚙️ Configuration

Edit `config.env`:
```env
TELEGRAM_TOKEN=your_bot_token
```

## 🔒 Security

- Never commit `config.env` or tokens to Git
- `.gitignore` is configured to exclude sensitive files
- Keep your bot token private

## 📈 Model Performance

The Random Forest classifier is trained on 6 months of hourly NIFTY 50 data with the following parameters:
- `n_estimators`: 200
- `max_depth`: 8
- `random_state`: 42

Check model accuracy in `train_rf.ipynb` after training.

## 🐛 Troubleshooting

### Market Closed Error
When market is closed, bot automatically fetches last 30 days of historical data for analysis.

### MACD/Signal showing 0.00
Ensure sufficient historical data is available. The bot requires at least 26 candles for MACD calculation.

### Version Warnings
scikit-learn version mismatch warnings are normal. Retrain the model with your current version if needed.

## 📝 License

MIT License - feel free to use and modify!

## 👨‍💻 Author

Nishant Rajput

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## ⭐ Show Your Support

Give a ⭐️ if this project helped you!
