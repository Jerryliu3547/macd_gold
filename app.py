# save this as app.py
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(layout="wide")
st.title("📈 Gold Price Analysis with Bollinger Bands & MACD")

# === 1. Load Gold Price Data ===
symbol = 'GLD'  # Gold ETF ticker
start_date = st.date_input("Start Date", pd.to_datetime("2022-01-01"))
end_date = pd.to_datetime("today")

@st.cache_data
def load_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    return data['Close']

gold_prices = load_data(symbol, start_date, end_date)

# === 2. MACD Calculation ===
def calculate_macd(prices, short_window=12, long_window=26, signal_window=9):
    ema_short = prices.ewm(span=short_window, adjust=False).mean()
    ema_long = prices.ewm(span=long_window, adjust=False).mean()
    macd_line = ema_short - ema_long
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    macd_hist = macd_line - signal_line
    return macd_line, signal_line, macd_hist

macd_line, signal_line, macd_hist = calculate_macd(gold_prices)

# === 3. Bollinger Bands Calculation ===
def calculate_bollinger_bands(prices, window=20, num_std=2):
    sma = prices.rolling(window=window).mean()
    std = prices.rolling(window=window).std()
    upper_band = sma + num_std * std
    lower_band = sma - num_std * std
    return sma, upper_band, lower_band

sma, upper_band, lower_band = calculate_bollinger_bands(gold_prices)

# === 4. Generate Buy/Sell Signals ===
buy_signals = (gold_prices < lower_band) & (macd_line > signal_line)
sell_signals = (gold_prices > upper_band) & (macd_line < signal_line)

# === 5. Plotting ===
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# Price with Bollinger Bands
ax1.plot(gold_prices, label='Gold Price', color='blue')
ax1.plot(sma, label='20-day SMA', color='orange')
ax1.plot(upper_band, label='Upper Band', color='green', linestyle='--')
ax1.plot(lower_band, label='Lower Band', color='red', linestyle='--')
ax1.plot(gold_prices[buy_signals], '^', markersize=10, color='green', label='Buy Signal')
ax1.plot(gold_prices[sell_signals], 'v', markersize=10, color='red', label='Sell Signal')
ax1.set_title('Gold Price with Bollinger Bands & Buy/Sell Signals')
ax1.set_ylabel('Price (USD)')
ax1.legend()
ax1.grid(True)

# MACD
ax2.plot(macd_line, label='MACD Line', color='purple')
ax2.plot(signal_line, label='Signal Line', color='gray')

if isinstance(macd_hist, pd.DataFrame):
    macd_hist = macd_hist.squeeze()
macd_hist = pd.to_numeric(macd_hist, errors='coerce').fillna(0)
colors = ['green' if val >= 0 else 'red' for val in macd_hist]
ax2.bar(macd_hist.index, macd_hist, color=colors, label='MACD Histogram', width=1)
ax2.axhline(0, color='black', linewidth=0.5, linestyle='--')
ax2.set_title('MACD Indicator with Histogram')
ax2.set_ylabel('MACD Value')
ax2.legend()
ax2.grid(True)

st.pyplot(fig)
