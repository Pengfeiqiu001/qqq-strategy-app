import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# ----------------- 自动刷新设置 -----------------
# 每 5 分钟自动刷新（单位：毫秒）
st_autorefresh(interval=300000, key="refresh")

# ----------------- 页面设置 -----------------
st.set_page_config(page_title="QQQ 策略助手", layout="centered")
st.title("📊 QQQ 实时策略助手（基于 VIX + RSI）")
st.caption("数据来源：Yahoo Finance | 每 5 分钟自动更新")

# ----------------- RSI 计算函数 -----------------
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ----------------- 获取最新数据 -----------------
qqq = yf.download("QQQ", period="1mo", interval="1d", progress=False)
vix = yf.download("^VIX", period="1mo", interval="1d", progress=False)
qqq['RSI'] = compute_rsi(qqq['Close'])

# 最新行情数据
latest_close = qqq['Close'].iloc[-1]
latest_rsi = qqq['RSI'].iloc[-1]
latest_vix = vix['Close'].iloc[-1]

# ----------------- 展示行情 -----------------
st.metric("📈 当前 QQQ 收盘价", f"${latest_close.iloc[-1]:.2f}")
st.metric("📉 当前 VIX 指数", f"{latest_vix.iloc[-1]:.2f}")
st.metric("📊 当前 QQQ RSI(14)", f"{latest_rsi:.2f}")

# ----------------- 策略判断 -----------------
if latest_vix.iloc[0] > 30 and latest_rsi.iloc[0] < 30:
    st.success("✅ 满足买入条件：VIX > 30 且 RSI < 30")
    st.markdown("💡 **建议：可以考虑买入 QQQ 或 TQQQ**")
elif latest_vix.item() < 20 or latest_rsi.item() > 70:
    st.warning("📤 满足卖出条件：VIX < 20 或 RSI > 70")
    st.markdown("💡 **建议：考虑止盈或减仓**")
else:
    st.info("⏸ 当前不满足买/卖条件")
    st.markdown("💡 **建议：继续观望，等待信号**")

# ----------------- 可选图表展示 -----------------
with st.expander("📈 查看 RSI 与 VIX 历史图表"):
    fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

    # RSI 图
    ax[0].plot(qqq.index, qqq['RSI'], label='RSI(14)', color='blue')
    ax[0].axhline(30, color='gray', linestyle='--', label='RSI=30')
    ax[0].axhline(70, color='gray', linestyle='--', label='RSI=70')
    ax[0].set_ylabel("RSI")
    ax[0].legend()

    # VIX 图
    ax[1].plot(vix.index, vix['Close'], label='VIX', color='orange')
    ax[1].axhline(30, color='red', linestyle='--', label='VIX=30')
    ax[1].axhline(20, color='green', linestyle='--', label='VIX=20')
    ax[1].set_ylabel("VIX")
    ax[1].legend()

    plt.tight_layout()
    st.pyplot(fig)