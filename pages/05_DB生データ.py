from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px
from dateutil.relativedelta import relativedelta


df = pd.read_excel("./注文DB.xlsx", sheet_name="Sheet1", header=0, usecols="A:DZ")

df[["新 報酬率(パートナー)", "新 報酬率(自社)","合計金額"]] = df[["新 報酬率(パートナー)", "新 報酬率(自社)","合計金額"]].astype(int)  # 金額や数量を整数型に変換

df["月"] = df["注文日"].dt.month.astype(str)  # "月"の列を追加
df["年"] = df["注文日"].dt.year.astype(str)  # "年"の列を追加
df["年月"] = df['注文日'].dt.strftime('%Y/%m')

df["自社報酬分"] = (df["合計金額"]*df["新 報酬率(自社)"] /100).astype(int)# 列を追加


st.title("■注文DBデータ集計")
st.write("注文DBよりテストアカウント,キャンセル,未課金,未入金を除いた生データ。分割決済や計上月を考慮していない注文月ベースのデータのため、実際の会計上の売上とは異なる。")

pivot_table = pd.pivot_table(df, index=["新 業務提携者（従属）"], columns=["年月"],values=["合計金額","自社報酬分"],  aggfunc="sum", margins=True)
pivot_table

df = df.groupby(["年月", "新 業務提携者（従属）"]).sum(numeric_only=True)

fig = px.bar(df.reset_index(), x="年月", y="合計金額", color="新 業務提携者（従属）", title="金額", barmode="stack")
fig.update_yaxes(tickformat=",",range=(0, 100000000),dtick=10000000)
st.subheader("全体売上分")
st.plotly_chart(fig, use_container_width=True)

fig = px.bar(df.reset_index(), x="年月", y="自社報酬分", color="新 業務提携者（従属）", title="金額", barmode="stack")
fig.update_yaxes(tickformat=",",range=(0, 100000000),dtick=10000000)
st.subheader("自社利益相当分(売上*自社報酬率％")
st.plotly_chart(fig, use_container_width=True)
