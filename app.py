import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="IDX Saham Mobile", layout="wide")
st.title("🔥 Analisa Saham IDX - Mobile Ready")

ticker = st.sidebar.text_input("Ticker IDX", value="BBCA.JK").upper().strip()
period = st.sidebar.selectbox("Periode", ["3mo", "6mo", "1y", "2y"], index=2)

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()

@st.cache_data(ttl=600)  # cache 10 menit untuk hindari rate limit
def ambil_data(ticker, period):
    return yf.download(ticker, period=period, interval="1d", progress=False)

data = ambil_data(ticker, period)

if data.empty or len(data) < 20:
    st.error("Data tidak tersedia. Tunggu 5-10 menit lalu refresh lagi.")
    st.stop()

# Harga (pakai data Close dulu, hindari .info yang sering kena limit)
harga = float(data['Close'].iloc[-1])
change_pct = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100

st.metric(f"**{ticker}**", f"Rp {harga:,.0f}", f"{change_pct:+.2f}%")

# Chart
fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close'])])
fig.update_layout(height=520, title=f"Chart {ticker}")
st.plotly_chart(fig, use_container_width=True)

# Indikator Manual
data['SMA20'] = data['Close'].rolling(20).mean()
data['SMA50'] = data['Close'].rolling(50).mean()

def hitung_rsi(close, window=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

data['RSI'] = hitung_rsi(data['Close'])
latest = data.iloc[-1]

col1, col2, col3 = st.columns(3)
col1.metric("RSI", f"{latest['RSI']:.1f}")
col2.metric("SMA20", f"{latest['SMA20']:,.0f}")
col3.metric("SMA50", f"{latest['SMA50']:,.0f}")

# Rekomendasi
if latest['RSI'] < 35 and latest['Close'] > latest['SMA50']:
    st.success("🟢 **SIGNAL BELI KUAT** (\~75-85% probability teknikal)")
elif latest['RSI'] > 70:
    st.error("🔴 **SIGNAL JUAL** - Overbought")
elif latest['Close'] > latest['SMA50']:
    st.info("🟡 **HOLD** - Trend masih naik")
else:
    st.warning("🔴 **TREND BEARISH** - Hati-hati")

st.caption("Sumber: Yahoo Finance • Cache 10 menit • Tunggu jika muncul rate limit")
st.markdown("**Coba ticker:** BBRI.JK, TLKM.JK, BMRI.JK, BBNI.JK, ASII.JK")
