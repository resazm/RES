import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("LME金属価格ダッシュボード")

# 金属の選択肢
metal_dict = {
    "Copper": "LME_Cu_cash",
    "Aluminium": "LME_Al_cash",
    "Nickel": "LME_Ni_cash"
}
metal = st.selectbox("金属を選択してください", list(metal_dict.keys()))

# 期間選択
start_date = st.date_input("開始日", value=pd.to_datetime("2022-01-01"))
end_date = st.date_input("終了日", value=date.today())

# データ取得関数
def fetch_lme_data(metal_field):
    url = f"https://www.westmetall.com/en/markdaten.php?action=table&field={metal_field}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")

    all_rows = []
    for table in tables:
        rows = table.find_all("tr")
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) >= 4:
                raw_date = cols[0].get_text(strip=True)
                try:
                    date_obj = datetime.strptime(raw_date, "%d. %B %Y")
                    date_str = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue
                try:
                    cash_price = float(cols[1].get_text(strip=True).replace(",", ""))
                    three_month = float(cols[2].get_text(strip=True).replace(",", ""))
                    stock = float(cols[3].get_text(strip=True).replace(",", ""))
                except ValueError:
                    continue
                all_rows.append([date_str, cash_price, three_month, stock])

    all_rows.sort(reverse=False)
    df = pd.DataFrame(all_rows, columns=["Date", "Cash-Settlement", "3-month", "Stock"])
    df["Date"] = pd.to_datetime(df["Date"])
    return df

# ボタンクリックでデータ取得・表示
if st.button("データ取得開始"):
    st.write(f"期間: {start_date} 〜 {end_date}")
    with st.spinner("データ取得中…"):
        df = fetch_lme_data(metal_dict[metal])
        df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

        if df.empty:
            st.warning("指定期間のデータがありません。")
        else:
            st.success(f"{len(df)}件のデータを取得しました。")
            st.dataframe(df)

            # 差分列を追加
            df["Difference"] = df["3-month"] - df["Cash-Settlement"]

            # ===== メインチャート =====
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df["Date"],
                y=df["Cash-Settlement"],
                mode='lines',
                name='Cash-Settlement',
                line=dict(color='blue')
            ))

            fig.add_trace(go.Scatter(
                x=df["Date"],
                y=df["3-month"],
                mode='lines',
                name='3-month',
                line=dict(color='green')
            ))

            fig.add_trace(go.Scatter(
                x=df["Date"],
                y=df["Stock"],
                mode='lines',
                name='Stock',
                yaxis='y2',
                line=dict(color='red')
            ))

            fig.update_layout(
                title=f"{metal} Price & Stock",
                xaxis=dict(title='Date'),
                yaxis=dict(title='Price (USD/ton)'),
                yaxis2=dict(title='Stock (ton)', overlaying='y', side='right'),
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # ===== 差分チャート（色分け） =====
            df_pos = df[df["Difference"] >= 0]
            df_neg = df[df["Difference"] < 0]

            diff_fig = go.Figure()

            diff_fig.add_trace(go.Bar(
                x=df_pos["Date"],
                y=df_pos["Difference"],
                name="Positive Diff",
                marker_color='orange'
            ))

            diff_fig.add_trace(go.Bar(
                x=df_neg["Date"],
                y=df_neg["Difference"],
                name="Negative Diff",
                marker_color='skyblue'
            ))

            diff_fig.update_layout(
                title=f"{metal} 3-month - Cash Difference",
                xaxis=dict(title="Date"),
                yaxis=dict(title="Difference (USD)"),
                barmode='relative',
                height=300,
                margin=dict(t=40)
            )

            st.plotly_chart(diff_fig, use_container_width=True)
