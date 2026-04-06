import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="IDX Saham Mobile", layout="wide")
st.title("🔥 Analisa Saham IDX - Mobile Ready")

ticker = st.sidebar.text_input("Ticker IDX (contoh: BBCA.JK)", value="BBCA.JK").upper().strip()
period = st.sidebar.selectbox("Periode Historis", ["1mo", "3mo", "6mo", "1y"], index=2)

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()

@st.cache_data(ttl=900)   # cache 15 menit biar tidak sering kena limit
def ambil_data(ticker, period):
    try:
        df = yf.download(ticker, period=period, interval="1d", progress=False)
        if df.empty:
            return None
        return df
    except:
        return None

data = ambil_data(ticker, period)

if data is None or data.empty or len(data) < 10:
    st.error("⚠️ Data sementara tidak tersedia dari Yahoo Finance.\n\nTunggu 5-10 menit lalu klik Refresh.")
    st.stop()

# Harga aman
harga = float(data['Close'].iloc[-1])
prev_harga = float(data['Close'].iloc[-2]) if len(data) > 1 else harga
change_pct = ((harga - prev_harga) / prev_harga) * 100

st.metric(f"**{ticker}**", f"Rp {harga:,.0f}", f"{change_pct:+.2f}%")

# Chart
fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'], high=data['High'],
                low=data['Low'], close=data['Close'])])
fig.update_layout(height=520, title=f"Chart {ticker}")
st.plotly_chart(fig, use_container_width=True)

# Indikator
data['SMA20'] = data['Close'].rolling(window=20).mean()
data['SMA50'] = data['Close'].rolling(window=50).mean()

def hitung_rsi(close, window=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
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
    st.success("🟢 **SIGNAL BELI KUAT** → Probability teknikal tinggi")
elif rsi > 70:
    st.error("🔴 **SIGNAL JUAL** → Overbought")
elif trend_bull:
    st.info("🟡 **HOLD** - Trend masih bullish")
else:
    st.warning("🔴 **TREND BEARISH** - Hati-hati")

st.caption("Data Yahoo Finance • Cache 15 menit • Versi stabil")
st.markdown("**Coba ticker populer:** BBRI.JK, TLKM.JK, BMRI.JK, BBNI.JK, ASII.JK")
