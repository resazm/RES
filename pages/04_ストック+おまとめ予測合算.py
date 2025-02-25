from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px

# 現在の年月を取得
today = date.today()  # 今日の日付を取得
this_year = today.year  # 年を取り出し
this_month = today.month  # 月を取り出し
this_ym = format(date.today(), '%Y/%m')


st.set_page_config(
   page_title="",
   layout="wide",
)


st.title("■月額会費・分割商品・おまとめ継続　売上予測")

st.write("")

ki9 = ["2025年02月", "2025年03月", "2025年04月", "2025年05月", "2025年06月", "2025年07月"] 

#全体分
df= pd.read_excel("./月額_分割統合.xlsx", sheet_name="結合+おまとめ", header=0, usecols="A:G")
keijo = df["計上月"].unique()
select_keijo = st.multiselect("計上月", options=keijo,default=ki9)

type1 = df["タイプ1"].unique()
select_type1= st.multiselect("タイプ1", options=type1,default=type1)

departments = df["新 業務提携者（従属）"].unique()
select_departments = st.multiselect("表示会社", options=departments, default=departments)


detail_df = df[(df["計上月"].isin(select_keijo))&(df["タイプ1"].isin(select_type1))&(df["新 業務提携者（従属）"].isin(select_departments))]

fig = px.bar(detail_df, x="計上月", y="合計金額", color="タイプ2", barmode="group")
fig.update_yaxes(tickformat=",",range=(0, 20000000),dtick=2000000)
st.subheader("")
st.plotly_chart(fig, use_container_width=True)





df1=detail_df[(detail_df["タイプ2"] == "全体売上")] # 条件式で抽出

fig = px.bar(df1, x="計上月", y="合計金額", color="タイプ1", barmode="stack")
fig.update_yaxes(tickformat=",",range=(0, 20000000),dtick=2000000)
st.subheader("")
st.plotly_chart(fig, use_container_width=True)

col1, col2 =  st.columns([1, 1])
#全体分テーブル
with col1:
   st.subheader("全体売上分")
   df2=detail_df[(detail_df["タイプ2"] == "全体売上")] # 条件式で抽出
   pivot_table = pd.pivot_table(df2, index=["タイプ1","新 業務提携者（従属）"], columns=["計上月"],values=["合計金額"],  aggfunc="sum", margins=True)
   pivot_table

#自社分テーブル
with col2:
   st.subheader("自社利益分(売上*自社報酬率％)")
   df3=detail_df[(detail_df["タイプ2"] == "自社分")] # 条件式で抽出
   pivot_table= pd.pivot_table(df3, index=["タイプ1","新 業務提携者（従属）"], columns=["計上月"],values=["合計金額"],  aggfunc="sum", margins=True)
   pivot_table


st.write("*******************************")