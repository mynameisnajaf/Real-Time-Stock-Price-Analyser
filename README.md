# 📈 Real-Time Stock Analyzer

A real-time stock analysis dashboard built with **Streamlit**, featuring live data, technical indicators, and efficient data structure implementations.

---

## 🚀 Features

- 📊 Live stock price tracking (Yahoo Finance API)
- ⏱ Auto-refresh dashboard
- 📉 Candlestick charts (Plotly)
- 📈 Moving averages & volatility
- 🔼 Trend detection
- 🧠 Efficient sliding window analysis using:
  - Heap (priority queue)
  - Lazy deletion technique
  - Deque for window management

---

## 🧠 Data Structures Used

### 1. Sliding Window (Deque)
Maintains last *k* prices efficiently.

### 2. Heaps (Min & Max)
- Track minimum and maximum prices
- Implemented with **lazy deletion** to support sliding window

### 3. Hash Map (Counter)
- Keeps track of valid elements in heap
- Enables efficient removal of outdated values

---

## ⚡ Complexity

| Operation | Time Complexity |
|----------|----------------|
| Add price | O(log k) |
| Get min/max | O(1) amortized |
| Moving average | O(1) |
| Volatility | O(k) |

---

## 🛠 Installation

```bash
git clone https://github.com/yourusername/stock-analyzer.git
cd stock-analyzer
pip install -r requirements.txt


## Visit site by using this QR-Code
<img width="1000" height="1000" alt="Stock Price Analyser" src="https://github.com/user-attachments/assets/beeb9bbf-db52-48be-8908-3dd105454547" />
