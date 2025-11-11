from datetime import date
from dateutil.relativedelta import relativedelta
import pandas as pd
import streamlit as st
import plotly.express as px

# 現在の年月を取得
today = date.today()  # 今日の日付を取得
this_year = today.year  # 年を取り出し
this_month = today.month  # 月を取り出し
this_ym = format(date.today(), '%Y/%m')
one_month_later = format((today + relativedelta(months=+1)),'%Y/%m')

st.set_page_config(
   page_title="",
   layout="wide",
)


st.title("■月額会費と分割商品の売上予測　統合データ")

st.write("月額会費と分割商品の売上予測")
#全体分
df= pd.read_excel("./月額_分割統合.xlsx", sheet_name="結合", header=0, usecols="A:G")

df["計上月"] = df["計上月"].dt.strftime('%Y/%m')

keijo = df["計上月"].unique()
select_keijo = st.multiselect("計上月", options=keijo,default=keijo)

type1 = df["タイプ1"].unique()
select_type1= st.multiselect("タイプ1", options=type1,default=type1)

departments = df["新 業務提携者（従属）"].unique()
select_departments = st.multiselect("表示会社", options=departments, default=departments)

detail_df = df[(df["計上月"].isin(select_keijo))&(df["タイプ1"].isin(select_type1))&(df["新 業務提携者（従属）"].isin(select_departments))]


fig = px.bar(detail_df, x="計上月", y="合計金額", color="タイプ2", barmode="group")
fig.update_yaxes(tickformat=",",dtick=1000000)
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
st.write("以下詳細データ")
st.write("*******************************")

st.title("■月額会費データ詳細")
st.write("当月発生「月額会費」注文データ")


col1, col2,col3 =  st.columns([1,1,1])
with col1:
   col1.subheader("月額会費")
   df4=df[(df["タイプ1"] == "月額") & (df["計上月"] == one_month_later) & (df["タイプ2"] == "全体売上")] # 条件式で抽出
   pivot_table = pd.pivot_table(df4, index=(["新 業務提携者（従属）","自社報酬率"]), values=["合計金額"],  aggfunc="sum", margins=True)
   pivot_table

with col2:
   col2.subheader("月額会費（自社取り分）")
   df5=df[(df["タイプ1"] == "月額") & (df["計上月"] == one_month_later) & (df["タイプ2"] == "自社分")] # 条件式で抽出
   pivot_table = pd.pivot_table(df5, index=(["新 業務提携者（従属）","自社報酬率"]), values=["合計金額"],  aggfunc="sum", margins=True)
   pivot_table

with col3:
   #st.subheader("月額会費売上")
   month_group_df = df4.groupby(["新 業務提携者（従属）"]).sum(numeric_only=True)
   fig = px.bar(month_group_df.reset_index(), x="新 業務提携者（従属）", y="合計金額",color="新 業務提携者（従属）")
   fig.update_yaxes(tickformat=",",range=(0, 5000000),dtick=1000000)
   st.plotly_chart(fig, use_container_width=True)

st.write("*******************************")

st.write("-------------------------------------------------")

st.title("■分割商品データ詳細")
st.write("当月発生「分割商品」注文データ")

col1, col2 =  st.columns([2,1])

with col1:
   col1.subheader("分割（〇回目/□分割） 次月以降発生予測")
   df6=df[(df["タイプ1"] == "分割")  & (df["タイプ2"] == "全体売上")] # 条件式で抽出
   pivot_table = pd.pivot_table(df6, index=(["新 業務提携者（従属）","自社報酬率"]), columns="計上月",values=["合計金額"],  aggfunc="sum", margins=True)
   pivot_table
with col2:
   month_group_df2 = df6.groupby(["新 業務提携者（従属）"]).sum(numeric_only=True)
   fig = px.bar(month_group_df2.reset_index(), x="新 業務提携者（従属）", y="合計金額",color="新 業務提携者（従属）", title="")
   fig.update_yaxes(tickformat=",")
   st.plotly_chart(fig, use_container_width=True)
st.subheader("分割（自社取り分）")
df7=df[(df["タイプ1"] == "分割")  & (df["タイプ2"] == "自社分")] # 条件式で抽出
pivot_table = pd.pivot_table(df7, index=(["新 業務提携者（従属）","自社報酬率"]), columns="計上月",values=["合計金額"],  aggfunc="sum", margins=True)
pivot_table




#st.write("-------------------------------------------------")
#st.write("月額会費データ")
#df = pd.read_excel("./注文データベース202502月額会費ｷｬﾝｾﾙ未入金除き.xlsx", sheet_name="Sheet1", header=0, usecols="A:DZ")
##st.dataframe(df)
#st.write("-------------------------------------------------")
#st.write("分割データ")
#df_2 = pd.read_excel("./注文データベース202502分割ｷｬﾝｾﾙ未入金除き.xlsx", sheet_name="Sheet1", header=0, usecols="A:DZ")
#st.dataframe(df_2)
#st.write("-------------------------------------------------")



