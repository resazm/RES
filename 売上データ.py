from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px

#pd.options.display.float_format = '{:,}'.format

df = pd.read_excel("./8期9期売上データ.xlsx", sheet_name="Sheet1", header=0, usecols="A:R")

#df = df.dropna()  # 空白データがある行を除外
df[["パートナー報酬率％", "自社報酬率％", "利用金額", "即時売上", "総計", "合計金額"]] = df[["パートナー報酬率％", "自社報酬率％", "利用金額", "即時売上", "総計", "合計金額"]].astype(int)  # 金額や数量を整数型に変換
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
this_ym = format(date.today(), '%Y/%m')


# タイトル表示
st.title(f"{this_year}年{this_month}月")


# 4カラム表示
col1, col2, col3, col4 = st.columns(4)

# 今年の購入回数
this_year_counts = df.loc[df["売上計上月"].dt.year == this_year, "売上計上月"].count()
col1.metric("📝今年のデータ件数", f"{this_year_counts}回")
# 今年の購入額
this_year_purchase = df.loc[df["売上計上月"].dt.year == this_year, "合計金額"].sum()
this_year_purchase = '{:,}'.format(this_year_purchase)
col2.metric("💰今年の合計金額", f"{this_year_purchase}円")

# 今月の購入回数
this_month_counts = df.loc[df["年月"] == this_ym, "売上計上月"].count()
this_month_counts = '{:,}'.format(this_month_counts)
col3.metric("📝今月のデータ件数", f"{this_month_counts}回")

# 今月の購入額
this_month_purchase = df.loc[df["年月"] == this_ym, "合計金額"].sum()
this_month_purchase = '{:,}'.format(this_month_purchase)
col4.metric("💰今月の合計金額", f"{this_month_purchase}円")

# 2カラム表示 (1:2)
col1, col2 = st.columns([1, 2])
# 購入数TOP10
many_df = df.groupby(by="会社").sum(numeric_only=True).sort_values(by="合計金額", ascending=False).reset_index()
col1.subheader("8.9期TOP10")
col1.table(many_df[["会社", "総計", "合計金額"]].iloc[:10])
# パートナー別金額
department_group_df = df.groupby(["会社", "年月"]).sum(numeric_only=True)
fig = px.bar(department_group_df.reset_index(), x="合計金額", y="会社", color="年月", orientation="h")
col2.subheader("パートナー別金額")
col2.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns([1, 3])
# 直近3件の購入
any_df = df.groupby(by="年月").sum(numeric_only=True).sort_values(by="年月", ascending=False).reset_index()
col1.subheader("8.9期月別")
col1.table(any_df[["年月", "合計金額"]])

# 月ごとの購入金額推移
month_group_df = df.groupby(["年月", "会社"]).sum(numeric_only=True)
fig = px.bar(month_group_df.reset_index(), x="年月", y="合計金額", color="会社", title="月別金額")
col2.subheader("8.9期月別")
col2.plotly_chart(fig, use_container_width=True)



st.sidebar.title("データ分析ツール")

# 詳細表示
with st.expander("詳細データ"):
   # 表示する期間の入力
   min_date = df["売上計上月"].min().date()
   max_date = df["売上計上月"].max().date()
   start_date, end_date = st.slider(
      "表示する期間を入力",
      min_value=min_date,
      max_value=max_date,
      value=(min_date, max_date),
      format="YYYY/MM/DD")

   col1, col2 =  st.columns([4, 1])

   # 表示する部署の選択
   departments = df["会社"].unique()
   select_departments = col1.multiselect("表示会社", options=departments, default=departments)

   df["売上計上月"] = df["売上計上月"].apply(lambda x: x.date())
   detail_df = df[(start_date <= df["売上計上月"]) & (df["売上計上月"] <= end_date) & (df["会社"].isin(select_departments))]

   productname_group_df = detail_df.groupby(["会社", "売上計上月"]).sum(numeric_only=True)
   view_h = len(productname_group_df)*15
   fig = px.bar(productname_group_df.reset_index(), x="合計金額", y="会社", color="売上計上月", orientation="h", title="パートナー別金額", height=view_h+300, width=600)
   fig.update_layout(yaxis={'categoryorder':'total ascending'})
   col1.plotly_chart(fig, use_container_width=True)

   col2.subheader("一覧")
   col2.dataframe(detail_df, height=view_h+200)










