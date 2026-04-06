import heapq
import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from collections import deque, Counter
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import pytz

st.set_page_config(page_title="Real-Time Stock Analyzer", layout="wide")
st.title("📈 Real-Time Stock Analyzer")

MAX_HISTORY = 500

if "analyzers" not in st.session_state:
    st.session_state.analyzers = {}

# -----------------------------
# Sliding Window (Heap-Based)
# -----------------------------
class SlidingWindowAnalyzer:
    def __init__(self, window_size=20):
        self.window_size = window_size
        self.prices = deque()
        self.sum = 0

        self.min_heap = []
        self.max_heap = []
        self.count = Counter()

    def _clean_heap(self, heap, is_max=False):
        while heap:
            val = -heap[0] if is_max else heap[0]
            if self.count[val] > 0:
                break
            heapq.heappop(heap)

    def add_price(self, price):
        self.prices.append(price)
        self.sum += price

        heapq.heappush(self.min_heap, price)
        heapq.heappush(self.max_heap, -price)
        self.count[price] += 1

        if len(self.prices) > self.window_size:
            old = self.prices.popleft()
            self.sum -= old
            self.count[old] -= 1

    def moving_average(self):
        return self.sum / len(self.prices) if self.prices else 0

    def volatility(self):
        return float(np.std(self.prices)) if len(self.prices) > 1 else 0

    def min_price(self):
        self._clean_heap(self.min_heap)
        return self.min_heap[0] if self.min_heap else 0

    def max_price(self):
        self._clean_heap(self.max_heap, is_max=True)
        return -self.max_heap[0] if self.max_heap else 0

    def trend(self):
        if len(self.prices) < 2:
            return "No trend"
        if self.prices[-1] > self.prices[0]:
            return "Uptrend 📈"
        elif self.prices[-1] < self.prices[0]:
            return "Downtrend 📉"
        return "Sideways ➡️"


# -----------------------------
# Stock Analyzer
# -----------------------------
class StockAnalyzer:
    def __init__(self, symbol):
        self.symbol = symbol
        self.window = SlidingWindowAnalyzer()
        self.price_history = deque(maxlen=MAX_HISTORY)
        self.last_timestamp = None

    def update(self, price, timestamp):
        if self.last_timestamp == timestamp:
            return False

        self.last_timestamp = timestamp
        self.price_history.append(price)
        self.window.add_price(price)
        return True


# -----------------------------
# Fetch Data
# -----------------------------
@st.cache_data(ttl=60)
def fetch_stock_data(symbol):
    try:
        df = yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        return df
    except Exception:
        return pd.DataFrame()


# -----------------------------
# Sidebar
# -----------------------------
symbols_input = st.sidebar.text_input("Enter symbols:", "AAPL,MSFT,GOOGL")
refresh_interval = st.sidebar.slider("Refresh (sec)", 60, 300, 60)

if st.sidebar.button("🔄 Force Refresh"):
    st.cache_data.clear()
    st.rerun()

symbols = [s.strip().upper() for s in symbols_input.split(",") if s.strip()]

if len(symbols) > 5:
    st.warning("⚠️ Too many symbols may slow down the app.")

# -----------------------------
# Market Status
# -----------------------------
def is_market_open():
    et = pytz.timezone("America/New_York")
    now = datetime.now(et)

    if now.weekday() >= 5:
        return False

    open_time = now.replace(hour=9, minute=30, second=0)
    close_time = now.replace(hour=16, minute=0, second=0)

    return open_time <= now <= close_time


if not is_market_open():
    st.warning("⚠️ Market closed (holidays not included). Showing last data.")

st.caption("⏱ Timezone: New York (ET)")

# -----------------------------
# Auto Refresh
# -----------------------------
st_autorefresh(interval=refresh_interval * 1000, key="refresh")

# -----------------------------
# Dashboard
# -----------------------------
for symbol in symbols:
    if symbol not in st.session_state.analyzers:
        st.session_state.analyzers[symbol] = StockAnalyzer(symbol)

    analyzer = st.session_state.analyzers[symbol]

    data = fetch_stock_data(symbol)

    if data.empty:
        st.warning(f"No data for {symbol}")
        continue

    latest_price = data["Close"].iloc[-1].item()
    latest_timestamp = data.index[-1]

    updated = analyzer.update(latest_price, latest_timestamp)

    st.subheader(f"📊 {symbol}")

    if updated:
        st.success(f"Updated: {latest_timestamp}")
    else:
        st.info("Waiting for next candle...")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Price", f"${latest_price:.2f}")
    col1.caption(analyzer.window.trend())

    col2.metric("Min (Window)", f"${analyzer.window.min_price():.2f}")
    col3.metric("Max (Window)", f"${analyzer.window.max_price():.2f}")

    col4.metric("MA (20)", f"${analyzer.window.moving_average():.2f}")
    col4.caption(f"Volatility: {analyzer.window.volatility():.3f}")

    # Chart
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Price"
    ))

    if len(analyzer.price_history) >= 5:
        prices = list(analyzer.price_history)
        ma = pd.Series(prices).rolling(5).mean()

        fig.add_trace(go.Scatter(
            x=data.index[-len(ma):],
            y=ma,
            mode="lines",
            name="MA (5)"
        ))

    fig.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)
    st.divider()