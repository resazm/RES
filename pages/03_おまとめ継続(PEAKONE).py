from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px

today = date.today()  # 今日の日付を取得
this_year = today.year  # 年を取り出し
this_month = today.month  # 月を取り出し
this_ym = format(date.today(), '%Y/%m')

st.set_page_config(
   page_title="",
   layout="wide",
)

st.title("■PEAKONEおまとめ継続参考データ")

st.write("PEAKONEおまとめ継続")
st.write("※次回のおまとめ継続更新で解約せずに更新した場合")
#全体分
df1 = pd.read_excel("./PEAKONEおまとめ.xlsx", sheet_name="Sheet11", header=0, usecols="A:E")



st.subheader("役務提供月/計上月ベース")
df2=df1[(df1["タイプ2"] == "全体売上")] # 条件式で抽出
pivot_table = pd.pivot_table(df2, index=["商品名"], columns=["計上月"], values=["合計金額"],aggfunc="sum", margins=True)
pivot_table

fig = px.bar(df2, x="計上月", y="合計金額", color="商品名", barmode="stack")
fig.update_yaxes(tickformat=",",range=(0, 15000000),dtick=1000000)
st.subheader("")
st.plotly_chart(fig, use_container_width=True)


st.write("*******************************")
st.write("*******************************")


st.subheader("役務提供月/計上月ベース　自社利益分(売上*自社報酬率％)")
df3=df1[(df1["タイプ2"] == "自社分")] # 条件式で抽出
pivot_table = pd.pivot_table(df3, index=["商品名"], columns=["計上月"], values=["合計金額"],aggfunc="sum", margins=True)
pivot_table

fig = px.bar(df3, x="計上月", y="合計金額", color="商品名", barmode="stack")
fig.update_yaxes(tickformat=",",range=(0, 6000000),dtick=1000000)
st.subheader("")
st.plotly_chart(fig, use_container_width=True)

st.write("*******************************")
st.write("*******************************")

df4 = pd.read_excel("./PEAKONEおまとめ.xlsx", sheet_name="Sheet1-2", header=0, usecols="A:E")


st.subheader("注文日ベース　分割計上前発生時")
pivot_table = pd.pivot_table(df4, index=["商品名"], columns=["計上月"], values=["合計金額"],aggfunc="sum", margins=True)
pivot_table

fig = px.bar(df4, x="計上月", y="合計金額", color="商品名", barmode="stack")
fig.update_yaxes(tickformat=",",range=(0, 50000000),dtick=4000000)
st.subheader("")
st.plotly_chart(fig, use_container_width=True)



df4 = pd.read_excel("./PEAKONEおまとめ.xlsx", sheet_name="まとめ継続", header=0, usecols="A:AZ")
st.dataframe(df4)