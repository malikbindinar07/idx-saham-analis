import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pandas_ta as ta
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

st.set_page_config(page_title="IDX Saham Pro", layout="wide")
st.title("🔥 Analisa Saham IDX Realtime")

ticker = st.sidebar.text_input("Ticker Saham (contoh: BBCA.JK)", "BBCA.JK").upper()
period = st.sidebar.selectbox("Periode", ["6mo", "1y", "2y", "5y"], index=2)

@st.cache_data(ttl=300)
def get_data(ticker, period):
    return yf.download(ticker, period=period, interval="1d")

data = get_data(ticker, period)

if data.empty:
    st.error("Data tidak ditemukan")
    st.stop()

# Current Price
current = yf.Ticker(ticker).info
harga = current.get('regularMarketPrice') or data['Close'][-1]
change = current.get('regularMarketChangePercent', 0)

st.metric(f"{ticker}", f"Rp {harga:,.0f}", f"{change:+.2f}%")

# Chart
fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close'])])
st.plotly_chart(fig, use_container_width=True)

# Indikator
data['RSI'] = ta.rsi(data['Close'], 14)
data['SMA50'] = ta.sma(data['Close'], 50)
data['MACD'] = ta.macd(data['Close'])['MACD_12_26_9']

latest = data.iloc[-1]

col1, col2 = st.columns(2)
col1.metric("RSI", f"{latest['RSI']:.1f}", "Oversold < 35")
col2.metric("Trend", "Bullish" if latest['Close'] > latest['SMA50'] else "Bearish")

# Rekomendasi Sederhana
if latest['RSI'] < 35 and latest['Close'] > latest['SMA50']:
    st.success("🟢 **SIGNAL BELI KUAT** - Probability tinggi")
elif latest['RSI'] > 70:
    st.error("🔴 **SIGNAL JUAL**")
else:
    st.warning("🟡 HOLD")

st.caption("Data realtime dari Yahoo Finance • Mobile Friendly")
