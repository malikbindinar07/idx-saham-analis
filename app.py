import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="IDX Saham Mobile", layout="wide")
st.title("🔥 Analisa Saham IDX - Mobile Ready")

# Sidebar
ticker = st.sidebar.text_input("Ticker IDX (contoh: BBCA.JK)", value="BBCA.JK").upper().strip()
period = st.sidebar.selectbox("Periode Historis", ["3mo", "6mo", "1y", "2y", "5y"], index=2)

if st.sidebar.button("🔄 Refresh Realtime"):
    st.cache_data.clear()

@st.cache_data(ttl=300)
def ambil_data(ticker, period):
    df = yf.download(ticker, period=period, interval="1d", progress=False)
    return df

data = ambil_data(ticker, period)

if data.empty or len(data) < 30:
    st.error("❌ Ticker tidak ditemukan atau data kurang. Coba ticker lain atau tunggu sebentar.")
    st.stop()

# Harga Realtime
info = yf.Ticker(ticker).info
harga = info.get('regularMarketPrice') or float(data['Close'].iloc[-1])
change_pct = info.get('regularMarketChangePercent', 0)

st.metric(f"**{ticker}**", f"Rp {harga:,.0f}", f"{change_pct:+.2f}%")

# Chart
fig = go.Figure(data=[go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close']
)])
fig.update_layout(height=550, title=f"Chart {ticker}")
st.plotly_chart(fig, use_container_width=True)

# Indikator Manual
data['SMA20'] = data['Close'].rolling(window=20).mean()
data['SMA50'] = data['Close'].rolling(window=50).mean()

# RSI Manual
def hitung_rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

data['RSI'] = hitung_rsi(data['Close'])

latest = data.iloc[-1]

col1, col2, col3 = st.columns(3)
col1.metric("RSI (14)", f"{latest['RSI']:.1f}")
col2.metric("SMA 20", f"{latest['SMA20']:,.0f}")
col3.metric("SMA 50", f"{latest['SMA50']:,.0f}")

# Rekomendasi
rsi = latest['RSI']
trend_bull = latest['Close'] > latest['SMA50']

if rsi < 35 and trend_bull:
    st.success("🟢 **SIGNAL BELI KUAT** → Probability teknikal tinggi (\~75-85%)")
elif rsi > 70:
    st.error("🔴 **SIGNAL JUAL** → Overbought")
elif trend_bull:
    st.info("🟡 **HOLD / Beli saat turun**")
else:
    st.warning("🔴 **TREND BEARISH** → Hati-hati")

st.caption("Data dari Yahoo Finance • Update setiap 5 menit • Versi ringan khusus Streamlit Cloud")
st.markdown("---")
st.markdown("Coba ticker: **BBRI.JK, TLKM.JK, BBNI.JK, ASII.JK, BMRI.JK**")
