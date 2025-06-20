import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta # datetimeとtimedeltaをインポート

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
    df = df.sort_values("取引日").reset_index(drop=True) # インデックスをリセット

    # スライダー：小さい入出金を除外
    min_amount = st.slider("表示する最小金額（この金額未満は除外）", min_value=0, max_value=1000000, value=10000, step=1000)

    # --- 期間選択機能を追加 ---
    # `to_pydatetime()`でPythonのdatetimeオブジェクトに変換
    min_date = df["取引日"].min().to_pydatetime()
    max_date = df["取引日"].max().to_pydatetime()

    date_range = st.slider(
        "表示期間を選択してください",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD"
    )

    start_date = date_range[0]
    end_date = date_range[1]

    # 期首残高の計算ロジックを修正
    # 選択された期間の開始日より「厳密に前の日付」の最終残高を取得
    # スライダーが日付の0時0分0秒を返すため、比較を <= に変更し、
    # その日を含む期間での最初の残高を期首残高として扱うのがより直感的かもしれません。
    # しかし、ウォーターフォールチャートの期首残高は「期間に入る前の残高」なので、
    # ここでは選択開始日の0時0分0秒より前の残高を取得します。

    # 選択期間の開始日より前の取引データ
    initial_balance_records = df[df["取引日"] < start_date]

    if not initial_balance_records.empty:
        # 選択期間開始日より前の最後の残高を期首残高とする
        start_balance = initial_balance_records["残高"].iloc[-1]
    else:
        # 選択期間開始日より前の取引がない場合
        # データの最初の取引日とスライダーの開始日が同じ場合など
        # ここで `df["残高"].iloc[0]` を使うと、データ全体の最初の残高になってしまう可能性があります。
        # そこで、選択された期間内の最初の取引の残高を期首とします。
        # または、もしdfが空でないなら、データの最初の残高を初期値とみなす
        if not df.empty:
            start_balance = df["残高"].iloc[0]
        else:
            start_balance = 0 # データが全くない場合

    # 選択された期間でデータをフィルタリング (開始日を含め、終了日を含める)
    df_period_filtered = df[(df["取引日"] >= start_date) & (df["取引日"] <= end_date)].copy()

    # 期間フィルタリング後のデータに金額フィルタリングを適用
    df_filtered = df_period_filtered[df_period_filtered["金額"].abs() >= min_amount]

    # 期末残高は選択された期間の最後の取引日の残高とする
    if not df_period_filtered.empty:
        end_balance = df_period_filtered["残高"].iloc[-1]
    else:
        # 期間内に取引がない場合は期首残高と同じ、またはゼロ
        end_balance = start_balance

    # ラベルと金額
    labels = (
        ["期首残高"]
        + (df_filtered["取引日"].dt.strftime('%Y-%m-%d') + "：" + df_filtered["お取引内容"].astype(str)).tolist()
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
    st.subheader(f"フィルター後の取引明細（{start_date.strftime('%Y/%m/%d')} - {end_date.strftime('%Y/%m/%d')}、最新10件）")
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

    # Y軸の表記をカンマ区切りにする設定
    fig.update_layout(
        title=f"銀行口座ウォーターフォールチャート（{start_date.strftime('%Y/%m/%d')} - {end_date.strftime('%Y/%m/%d')}）",
        height=1200,
        xaxis_tickangle=+90,
        yaxis=dict(
            tickformat="," # カンマ区切り
        )
    )
    st.plotly_chart(fig, use_container_width=True)