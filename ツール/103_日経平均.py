import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup

st.title("日経平均株価取得")

ticker = "^N225"

if st.button("日経平均を取得"):
    data = yf.download(ticker, period="5d", interval="1d")
    data = data.dropna()

    if len(data) >= 2:
        latest = float(data["Close"].iloc[-1])
        previous = float(data["Close"].iloc[-2])
        diff = latest - previous

        # 改良されたフォーマット関数
        def format_price(price, show_man=True):
            man = int(price) // 10000
            sen = int(price) % 10000
            rin = int(round((price - int(price)) * 100))
            if show_man and man > 0:
                return f"{man:,}万{sen:04,}円{rin:02}銭"
            else:
                return f"{sen:,}円{rin:02}銭"

        latest_str = format_price(latest)
        diff_str = format_price(abs(diff), show_man=False)  # 万の表示は省略
        sign = "+" if diff >= 0 else "-"

        st.subheader(f"{latest_str}（{sign}{diff_str}）")
    else:
        st.error("有効な株価データが2日分以上取得できませんでした。")



