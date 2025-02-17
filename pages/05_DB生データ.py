from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px
from dateutil.relativedelta import relativedelta


df = pd.read_excel("./注文DB.xlsx", sheet_name="Sheet1", header=0, usecols="A:DZ")

df["新 報酬率(パートナー)"].fillna(0, inplace=True)
df["新 報酬率(自社)"].fillna(0, inplace=True)

df[["新 報酬率(パートナー)", "新 報酬率(自社)","合計金額"]] = df[["新 報酬率(パートナー)", "新 報酬率(自社)","合計金額"]].astype(int)  # 金額や数量を整数型に変換


df["月"] = df["注文日"].dt.month.astype(str)  # "月"の列を追加
df["年"] = df["注文日"].dt.year.astype(str)  # "年"の列を追加
df["年月"] = df['注文日'].dt.strftime('%Y/%m')
df["年月日"] = df['注文日'].dt.strftime('%Y/%m/%d')
df["日付"] = df['注文日'].dt.strftime('%d')

df["自社報酬分"] = (df["合計金額"]*df["新 報酬率(自社)"] /100).astype(int)# 列を追加


st.title("■注文DBデータ集計")
st.write("注文DBよりテストアカウント,キャンセル,未課金,未入金を除いた生データ。分割決済や計上月を考慮していない注文月ベースのデータのため、実際の会計上の売上とは異なる。")

pivot_table = pd.pivot_table(df, index=["新 業務提携者（従属）"], columns=["年月"],values=["合計金額","自社報酬分"],  aggfunc="sum", margins=True)
pivot_table

df1 = df.groupby(["年月", "新 業務提携者（従属）"]).sum(numeric_only=True)

fig = px.bar(df1.reset_index(), x="年月", y="合計金額", color="新 業務提携者（従属）", title="金額", barmode="stack")
fig.update_yaxes(tickformat=",",range=(0, 100000000),dtick=10000000)
st.subheader("全体売上分")
st.plotly_chart(fig, use_container_width=True)

fig = px.bar(df1.reset_index(), x="年月", y="自社報酬分", color="新 業務提携者（従属）", title="金額", barmode="stack")
fig.update_yaxes(tickformat=",",range=(0, 100000000),dtick=10000000)
st.subheader("自社利益相当分(売上*自社報酬率％")
st.plotly_chart(fig, use_container_width=True)



today = date.today()  # 今日の日付を取得
this_year = today.year  # 年を取り出し
this_month = today.month  # 月を取り出し
one_month_ago = (today - relativedelta(months=1)).strftime('%m')
this_ym = format(date.today(), '%Y/%m')

col1, col2 =  st.columns([2, 1])
with col1:
    st.subheader("当月　日別/パートナー別注文　金額動向")
    tougetu_df = df[(df["年月"] == this_ym)]
    pivot_table = pd.pivot_table(tougetu_df , index=["年月日"],columns="新 業務提携者（従属）",values=["合計金額"],  aggfunc="sum", margins=True)
    pivot_table
with col2:
    fig = px.bar(tougetu_df .reset_index(), x="日付", y="合計金額", color="新 業務提携者（従属）", title="金額", barmode="stack")
    fig.update_yaxes(tickformat=",",range=(0, 2000000),dtick=100000)
    fig.update_xaxes(dtick=2,range=(0, 31))
    st.subheader("")
    st.plotly_chart(fig, use_container_width=True)
#s = '2023/4/1 20:30'
#s_format = '%Y/%m/%d %H:%M'
#dt = date.strptime(s,s_format)
#print(dt)
#df["年月日"].dt.strptime('%Y/%m/%d')
#tougetu_df=["年月日"].strptime(tougetu_df["年月日"]"%Y-%m-%d",)
#print(tougetu_df["年月日"].strptime)

col1, col2 =  st.columns([2, 1])
with col1:
    st.subheader("当月　日別/パートナー別注文 数量動向")
    tougetu_df = df[(df["年月"] == this_ym)]
    pivot_table = pd.pivot_table(tougetu_df , index=["年月日"],columns="新 業務提携者（従属）",values=["数量"],  aggfunc="sum", margins=True)
    pivot_table
with col2:
    fig = px.bar(tougetu_df .reset_index(), x="日付", y="数量", color="新 業務提携者（従属）", title="数量", barmode="stack")
    fig.update_yaxes(tickformat=",",range=(0, 30),dtick=2)
    fig.update_xaxes(dtick=2,range=(0, 31))
    st.subheader("")
    st.plotly_chart(fig, use_container_width=True)