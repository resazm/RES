from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px
from dateutil.relativedelta import relativedelta

#pd.options.display.float_format = '{:,}'.format

df = pd.read_excel("./8期9期売上データ.xlsx", sheet_name="Sheet1", header=0, usecols="A:R")

#df = df.dropna()  # 空白データがある行を除外
#df[["パートナー報酬率％", "自社報酬率％", "利用金額", "即時売上", "総計", "合計金額"]] = df[["パートナー報酬率％", "自社報酬率％", "利用金額", "即時売上", "総計", "合計金額"]].astype(int)  # 金額や数量を整数型に変換
df["月"] = df["売上計上月"].dt.month.astype(str)  # "月"の列を追加
df["年"] = df["売上計上月"].dt.year.astype(str)  # "年"の列を追加
df["年月"] = df['売上計上月'].dt.strftime('%Y/%m')



st.set_page_config(
   page_title="RES売上ダッシュボード",
   layout="wide",
)

# 現在の年月を取得
today = date.today()  # 今日の日付を取得
this_year = today.year  # 年を取り出し
this_month = today.month  # 月を取り出し
one_month_ago = (today - relativedelta(months=1)).strftime('%m')
this_ym = format(date.today(), '%Y/%m')


# タイトル表示
st.title("■主要パートナー別売上データ")
st.write(f"{this_year}年{one_month_ago}月時点")

# with st.expander("詳細データ"):
   # 表示する期間の入力
#   min_date = df["売上計上月"].min().date()
#   max_date = df["売上計上月"].max().date()
#   start_date, end_date = st.slider(
#      "表示する期間を入力",
#      min_value=min_date,
#      max_value=max_date,
#      value=(min_date, max_date),
#      format="YYYY/MM/DD")

ki9 = ["2024/12", "2025/01", "2025/02", "2025/03", "2025/04", "2025/05", "2025/06", "2025/07", "2025/08", "2025/09", "2025/10", "2025/11", "2025/12"] 

   # 表示する売上計上月の選択
keijo = df["年月"].unique()
select_keijo = st.multiselect("計上月", options=keijo, default=ki9)


   # 表示する部署の選択
departments = df["会社"].unique()
select_departments = st.multiselect("表示会社", options=departments, default=departments)

#df["売上計上月"] = df["売上計上月"].apply(lambda x: x.date())
#detail_df = df[(start_date <= df["売上計上月"]) & (df["売上計上月"] <= end_date) & (df["会社"].isin(select_departments))]

col1, col2 =  st.columns([2, 1])


detail_df = df[(df["年月"].isin(select_keijo)) & (df["会社"].isin(select_departments))]


   #productname_group_df = detail_df.groupby(["会社", "売上計上月"]).sum(numeric_only=True)
   #view_h = len(productname_group_df)*15
   #fig = px.bar(productname_group_df.reset_index(), x="合計金額", y="会社", color="売上計上月", orientation="h", title="パートナー別金額", height=view_h+300, width=600)
   #fig.update_layout(yaxis={'categoryorder':'total ascending'})
   #st.plotly_chart(fig, use_container_width=True)

month_group_df = detail_df.groupby(["年月", "会社"]).sum(numeric_only=True)
fig = px.bar(month_group_df.reset_index(), x="年月", y="合計金額", color="会社", title="月別金額")
fig.update_yaxes(tickformat=",",dtick=5000000)
#col1.subheader("月別計上")
col1.plotly_chart(fig, use_container_width=True)

#form_counts = detail_df.groupby(["会社","合計金額"]).sum(numeric_only=True)

fig = px.pie(detail_df, values="合計金額", names="会社", title='構成割合')
col2.plotly_chart(fig, use_container_width=True)




#with col2:
st.subheader("データ一覧")
pivot_table = pd.pivot_table(detail_df, index=["会社"], columns=["年月"],values=["合計金額"],  aggfunc="sum", margins=True)
pivot_table


#AA_df = detail_df.groupby(by="会社").sum(numeric_only=True).sort_values(by="合計金額", ascending=False).reset_index()
#col2.table(AA_df[["会社", "合計金額"]])




