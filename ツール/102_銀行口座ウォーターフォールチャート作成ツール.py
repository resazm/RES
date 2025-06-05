import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.title("銀行口座ウォーターフォールチャート作成ツール")

uploaded_file = st.file_uploader("みずほ・きらぼし銀行の弥生会計データ（Excel）をアップロードしてください", type=["xlsx"])

if uploaded_file:
    # Excelをヘッダー無しで読み込み
    df_raw = pd.read_excel(uploaded_file, header=None)
    num_cols = df_raw.shape[1]

    # 列名設定
    column_names = ["無視"] * num_cols
    column_names[0] = "取引日"
    column_names[19] = "お預り金額"
    column_names[21] = "お支払金額"
    column_names[23] = "残高"
    column_names[24] = "お取引内容"

    # データ本体（14行目〜）
    df_data = df_raw.iloc[13:].copy()
    df_data.columns = column_names
    df = df_data[["取引日", "お取引内容", "お支払金額", "お預り金額", "残高"]].copy()

    # 変換処理
    df["お支払金額"] = pd.to_numeric(df["お支払金額"], errors="coerce").fillna(0)
    df["お預り金額"] = pd.to_numeric(df["お預り金額"], errors="coerce").fillna(0)
    df["金額"] = df["お預り金額"] - df["お支払金額"]
    df["取引日"] = pd.to_datetime(df["取引日"], errors="coerce")
    df["残高"] = pd.to_numeric(df["残高"], errors="coerce")
    df = df.dropna(subset=["取引日"])
    df = df.sort_values("取引日")

    # スライダー：小さい入出金を除外
    min_amount = st.slider("表示する最小金額（この金額未満は除外）", min_value=0, max_value=1000000, value=10000, step=1000)
    df_filtered = df[df["金額"].abs() >= min_amount]

    # 開始・終了残高
    start_balance = df["残高"].iloc[0]
    end_balance = df["残高"].iloc[-1]

    # ラベルと金額
    labels = (
        ["期首残高"]
        + (df_filtered["お取引内容"].astype(str) + " (" + df_filtered["取引日"].dt.strftime('%Y-%m-%d') + ")").tolist()
        + ["期末残高"]
    )

    y_values = (
        [start_balance] +
        df_filtered["金額"].tolist() +
        [end_balance]
    )

    measures = (
        ["absolute"] + ["relative"] * len(df_filtered) + ["total"]
    )

    # 表示
    st.subheader("フィルター後の取引明細（最新10件）")
    st.dataframe(df_filtered[["取引日", "お取引内容", "金額", "残高"]].tail(10))

    # グラフ作成
    fig = go.Figure(go.Waterfall(
        name="口座変動",
        orientation="v",
        measure=measures,
        x=labels,
        y=y_values,
        text=[f"{v:,.0f}円" for v in y_values],
        connector={"line": {"color": "gray"}},
        increasing={"marker": {"color": "green"}},
        decreasing={"marker": {"color": "red"}},
        totals={"marker": {"color": "blue"}}
    ))

    fig.update_layout(title="銀行口座ウォーターフォールチャート（期首・期末含む）", height=1200,xaxis_tickangle=+90 )
    st.plotly_chart(fig, use_container_width=True)
