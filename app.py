import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="IDX Saham Mobile", layout="wide")
st.title("🔥 Analisa Saham IDX - Mobile Ready")

ticker = st.sidebar.text_input("Ticker IDX (contoh: BBCA.JK)", value="BBCA.JK").upper().strip()
period = st.sidebar.selectbox("Periode Historis", ["1mo", "3mo", "6mo", "1y"], index=1)

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()

@st.cache_data(ttl=900)
def ambil_data(ticker, period):
    try:
        df = yf.download(ticker, period=period, interval="1d", progress=False, timeout=20)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

data = ambil_data(ticker, period)

# === GUARD SUPER KUAT ===
if data is None or data.empty or len(data) < 5:
    st.warning("⚠️ Yahoo Finance sedang lambat atau rate limit.")
    st.info("Tunggu 5–10 menit lalu klik tombol **Refresh Data**")
    st.stop()

# Ambil harga dengan aman
try:
    harga = float(data['Close'].iloc[-1])
    prev_harga = float(data['Close'].iloc[-2]) if len(data) > 1 else harga
    change_pct = ((harga - prev_harga) / prev_harga) * 100
except:
    st.error("Data harga tidak valid. Coba refresh lagi.")
    st.stop()

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
    return 100 - (100 / (1 + rs))

data['RSI'] = hitung_rsi(data['Close'])
latest = data.iloc[-1]

col1, col2, col3 = st.columns(3)
col1.metric("RSI (14)", f"{latest['RSI']:.1f}")
col2.metric("SMA20", f"{latest.get('SMA20', 0):,.0f}")
col3.metric("SMA50", f"{latest.get('SMA50', 0):,.0f}")

# Rekomendasi
rsi = latest['RSI']
if pd.isna(rsi):
    st.info("Menunggu data RSI...")
else:
    trend_bull = latest['Close'] > latest['SMA50']
    if rsi < 35 and trend_bull:
        st.success("🟢 **SIGNAL BELI KUAT**")
    elif rsi > 70:
        st.error("🔴 **SIGNAL JUAL** - Overbought")
    elif trend_bull:
        st.info("🟡 **HOLD** - Trend Bullish")
    else:
        st.warning("🔴 **TREND BEARISH**")

st.caption("Sumber: Yahoo Finance • Tunggu jika muncul peringatan rate limit")
