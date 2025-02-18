from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px
from dateutil.relativedelta import relativedelta

st.set_page_config(
   page_title="",
   layout="wide",
)

df = pd.read_excel("./注文DB.xlsx", sheet_name="Sheet1", header=0, usecols="A:EE")

df["新 報酬率(パートナー)"].fillna(0, inplace=True)
df["新 報酬率(自社)"].fillna(0, inplace=True)
df["オプトイン"].fillna("(空欄)", inplace=True)

df[["新 報酬率(パートナー)", "新 報酬率(自社)","合計金額"]] = df[["新 報酬率(パートナー)", "新 報酬率(自社)","合計金額"]].astype(int)  # 金額や数量を整数型に変換


df["月"] = df["注文日"].dt.month.astype(str)  # "月"の列を追加
df["年"] = df["注文日"].dt.year.astype(str)  # "年"の列を追加
df["年月"] = df['注文日'].dt.strftime('%Y/%m')
df["年月日"] = df['注文日'].dt.strftime('%Y/%m/%d')
df["日付"] = df['注文日'].dt.strftime('%d')

df["自社報酬分"] = (df["合計金額"]*df["新 報酬率(自社)"] /100).astype(int)# 列を追加


today = date.today()  # 今日の日付を取得
this_year = today.year  # 年を取り出し
this_month = today.month  # 月を取り出し
one_month_ago = (today - relativedelta(months=1)).strftime('%m')
this_ym = format(date.today(), '%Y/%m')

st.title("■当月注文DBデータ分析")

st.write("-----------------------")
col1, col2, col3, col4 = st.columns(4)
# 今年の購入回数
this_year_counts = df.loc[df["注文日"].dt.year == this_year, "数量"].sum()
col1.metric("📝今年の注文件数", f"{this_year_counts:,}回", border=True)

this_year_purchase = df.loc[df["注文日"].dt.year == this_year, "合計金額"].sum()
#this_year_purchase.tickformat=","
col2.metric("💰今年の注文金額合計", f"{this_year_purchase:,}円", border=True)

this_month_counts = df.loc[df["注文日"].dt.month == this_month, "数量"].sum()
col3.metric("📝今月の注文件数", f"{this_month_counts:,}回", border=True)

this_month_purchase = df.loc[df["注文日"].dt.month == this_month, "合計金額"].sum()
col4.metric("💰今月の注文金額合計", f"{this_month_purchase:,}円", border=True)
st.write("-----------------------")

col1, col2 =  st.columns([2, 1])
with col1:
    st.subheader("当月　日別/パートナー別注文動向（合計金額）")
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
    st.subheader("当月　日別/パートナー別注文動向（件数）")
    tougetu_df = df[(df["年月"] == this_ym)]
    pivot_table = pd.pivot_table(tougetu_df , index=["年月日"],columns="新 業務提携者（従属）",values=["数量"],  aggfunc="sum", margins=True)
    pivot_table
with col2:
    fig = px.bar(tougetu_df .reset_index(), x="日付", y="数量", color="新 業務提携者（従属）", title="数量", barmode="stack")
    fig.update_yaxes(tickformat=",",range=(0, 30),dtick=2)
    fig.update_xaxes(dtick=2,range=(0, 31))
    st.subheader("")
    st.plotly_chart(fig, use_container_width=True)


#fig = px.bar(tougetu_df .reset_index(), x="商品単価", y="数量",title="", barmode="stack")
#fig.update_yaxes(tickformat=",",range=(0, 30),dtick=2)
#fig.update_xaxes(dtick=50000,range=(0, 500000))
#st.subheader("")
#st.plotly_chart(fig, use_container_width=True)




st.subheader('当月　購入者分布')
st.map(tougetu_df[['latitude', 'longitude']])

st.subheader('当月　購入単価ヒストグラム')
fig = px.histogram(tougetu_df, x='商品単価', nbins=30)
fig.update_yaxes(tickformat=",",range=(0, 30),dtick=2)
fig.update_xaxes(dtick=10000,range=(0, 500000))
fig.update_layout(bargap=0.2)
st.plotly_chart(fig, use_container_width=True)

col1, col2=  st.columns([1,1])
with col1:
    st.subheader("当月　商品別集計")
    pivot_table = pd.pivot_table(tougetu_df , index=["新 業務提携者（従属）","商品名"],values=["合計金額","数量"],  aggfunc="sum").sort_values("数量",ascending=False)
    pivot_table
with col2:
    st.subheader("当月　受注経路集計")
    pivot_table = pd.pivot_table(tougetu_df , index=["受注経路","支払方法"],values=["合計金額","数量"],  aggfunc="sum").sort_values("数量",ascending=False)
    pivot_table

st.subheader("当月　オプトイン集計")
pivot_table = pd.pivot_table(tougetu_df , index=["オプトイン"],values=["合計金額","数量"],  aggfunc="sum").sort_values("数量",ascending=False)
pivot_table


st.write("-----------------------")

st.title("■注文DBデータ集計(2024.9~)")
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