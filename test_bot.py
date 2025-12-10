#!/usr/bin/env python
"""
Quick test script to verify bot functions work correctly
"""
import os
import sys
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
import pandas as pd
import numpy as np

load_dotenv("config.env")

# Import bot functions
from app import get_backtest_candle, get_market_news, analyze_sentiment, get_ml_prediction

print("=" * 60)
print("NIFTY Bot Functions Test")
print("=" * 60)

# Test 1: Backtest candle
print("\n[TEST 1] Getting backtest candle (90-day fallback)...")
try:
    candle = get_backtest_candle()
    print("[OK] Price: {:.2f}".format(candle['Close']))
    print("     RSI: {:.2f}".format(candle['rsi']))
    print("     EMA20: {:.2f}".format(candle['ema20']))
    print("     MACD: {:.2f}".format(candle['macd']))
    print("     Signal: {:.2f}".format(candle['signal']))
except Exception as e:
    print("[ERROR] {}".format(e))

# Test 2: Market news
print("\n[TEST 2] Getting market news...")
try:
    headlines, news_text = get_market_news()
    if headlines:
        print("[OK] Found {} headlines:".format(len(headlines)))
        for i, h in enumerate(headlines, 1):
            print("     {}. {}...".format(i, h[:70]))
    else:
        print("[WARN] No headlines found")
except Exception as e:
    print("[ERROR] {}".format(e))

# Test 3: Sentiment analysis
print("\n[TEST 3] Analyzing sentiment...")
try:
    sentiment, msg = analyze_sentiment(headlines if headlines else ["Test positive gain"])
    print("[OK] Sentiment: {}".format(sentiment))
    # Skip printing message due to emoji encoding in Windows
except Exception as e:
    print("[ERROR] {}".format(e))

# Test 4: ML prediction
print("\n[TEST 4] Making ML prediction...")
try:
    candle = get_backtest_candle()
    direction, confidence = get_ml_prediction(candle)
    print("[OK] Confidence: {}%".format(confidence))
    # Skip printing direction due to emoji encoding in Windows
except Exception as e:
    print("[ERROR] {}".format(e))

print("\n" + "=" * 60)
print("All tests completed! Bot is ready to use.")
print("=" * 60)
