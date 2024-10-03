import os
import ccxt.coinex
from dotenv import load_dotenv
import ccxt
import pandas as pd
import numpy as np
import time

# Load environment variables from the .env file
load_dotenv()

# Access environment variables
api_key = os.getenv('ACCESS_ID')
secret_key = os.getenv('SECRET_KEY')

print(f"API Key: {api_key}")
print(f"Secret Key: {secret_key}")

# Initialize the exchange (e.g., Binance, Kraken)
exchange = ccxt.coinex({
    'apiKey': api_key,
    'secret': secret_key,
})

# Define the symbol and timeframe for the market data (e.g., BTC/USDT, 1-hour candles)
symbol = 'BTC/USDT'
timeframe = '1h'

# Fetch the historical OHLCV data (Open, High, Low, Close, Volume)
def fetch_data(symbol, timeframe, limit=100):
    bars = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# Calculate Bollinger Bands
def calculate_bollinger_bands(df, window=20, num_std=2):
    df['SMA'] = df['close'].rolling(window).mean()
    df['std'] = df['close'].rolling(window).std()
    df['upper_band'] = df['SMA'] + (num_std * df['std'])
    df['lower_band'] = df['SMA'] - (num_std * df['std'])
    return df

# Check trading signals based on Bollinger Bands
def check_signals(df):
    if df['close'].iloc[-1] > df['upper_band'].iloc[-1]:
        return 'sell'
    elif df['close'].iloc[-1] < df['lower_band'].iloc[-1]:
        return 'buy'
    else:
        return 'hold'

# Place market orders
def place_order(symbol, side, amount):
    try:
        order = exchange.create_market_order(symbol, side, amount)
        print(f"Order executed: {side} {amount} {symbol}")
        return order
    except Exception as e:
        print(f"Order failed: {e}")
        return None

# Main function to run the bot
def run_bot():
    while True:
        # Fetch market data
        df = fetch_data(symbol, timeframe)
        
        # Calculate Bollinger Bands
        df = calculate_bollinger_bands(df)
        
        # Check for buy/sell signals
        signal = check_signals(df)
        print(f"Latest Signal: {signal}")
        
        # Execute trade based on the signal
        if signal == 'buy':
            place_order(symbol, 'buy', 0.001)  # Example: Buy 0.001 BTC
        elif signal == 'sell':
            place_order(symbol, 'sell', 0.001)  # Example: Sell 0.001 BTC
        
        # Wait for the next interval (e.g., 1 hour)
        time.sleep(3600)

# Run the bot
run_bot()
