import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.title("株価ローソク足チャート（表示改善版）")

# ユーザー入力
ticker = st.text_input("銘柄コードを入力（例：AAPL または 7974.T）", value="7974.T")
start_date = st.date_input("開始日", value=pd.to_datetime("2025-01-01"))
end_date = st.date_input("終了日", value=pd.to_datetime("2025-12-31"))

if st.button("株価データを取得"):
    try:
        # データ取得
        df = yf.download(ticker, start=start_date, end=end_date, group_by='ticker')

        if df.empty:
            st.warning("データが取得できませんでした。")
        else:
            # カラムが MultiIndex の場合は整形
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(0)

            # インデックスをリセットして Date カラムを追加
            df.reset_index(inplace=True)

            # ✅ 日付を文字列（YYYY-MM-DD）に変換して見やすく
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

            # 移動平均線（SMA20）計算
            df['SMA20'] = df['Close'].rolling(window=20).mean()

            # 表示用
            st.subheader("整形済みのデータ（1段カラム、日付整形済）")
            st.write(df.head())

            # ローソク足チャート + SMA20線
            fig = go.Figure(data=[
                go.Candlestick(
                    x=df['Date'],
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    increasing_line_color='red',
                    decreasing_line_color='blue',
                    name='ローソク足'
                ),
                go.Scatter(
                    x=df['Date'],
                    y=df['SMA20'],
                    mode='lines',
                    line=dict(color='orange', width=2),
                    name='SMA20'
                )
            ])

            # ✅ x軸の隙間・過密ラベルを改善
            fig.update_layout(
                title=f"{ticker} のローソク足チャート（SMA20付き）",
                xaxis_title="日付",
                yaxis_title="価格",
                xaxis_rangeslider_visible=False,
                xaxis=dict(
                    type='category',     # 隙間除去
                    #tickmode='auto',     # 自動で間引き
                    #nticks=40,           # 最大表示ラベル数
                    #tickangle=-45        # ラベルを斜め表示
                )
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
