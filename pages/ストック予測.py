from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px

#pd.options.display.float_format = '{:,}'.format
st.title("■月額会費データ■")
df = pd.read_excel("./注文データベース202501月額会費ｷｬﾝｾﾙ未入金除き.xlsx", sheet_name="Sheet1", header=0, usecols="A:DZ")

#df = df.dropna()  # 空白データがある行を除外
#df[["パートナー報酬率％", "自社報酬率％", "利用金額", "即時売上", "総計", "合計金額"]] = df[["パートナー報酬率％", "自社報酬率％", "利用金額", "即時売上", "総計", "合計金額"]].astype(int)  # 金額や数量を整数型に変換
#df["月"] = df["売上計上月"].dt.month.astype(str)  # "月"の列を追加
#df["年"] = df["売上計上月"].dt.year.astype(str)  # "年"の列を追加
#df["年月"] = df['売上計上月'].dt.strftime('%Y/%m')


#st.set_page_config(
#   page_title="RES売上ダッシュボード",
#   layout="wide",
#)

# 現在の年月を取得
today = date.today()  # 今日の日付を取得
this_year = today.year  # 年を取り出し
this_month = today.month  # 月を取り出し
this_ym = format(date.today(), '%Y/%m')


# タイトル表示
#st.title(f"{this_year}年{this_month}月")

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

#st.subheader("データ一覧")
#pivot_table = pd.pivot_table(df, index=["新 業務提携者（従属）","新 報酬率(自社)"], values=["合計金額","数量"],  aggfunc="sum", margins=True)
#pivot_table

df["自社報酬分"] = (df["合計金額"]*df["新 報酬率(自社)"] /100).astype(int)# 列を追加

#df["新報酬率(自社)"].astype(str)  # 金額や数量を整数型に変換
#df["自社報酬率文字"] = (df["新報酬率(自社)"]).astype(str)# 列を追加



#df[["新報酬率(自社)"]].astype(int)  # 金額や数量を整数型に変換

#pivot_table = pd.pivot_table(df, index=(["新業務提携者（従属）","新報酬率(自社)2"]), values=["合計金額","数量"],  aggfunc="sum", margins=True)
#pivot_table

col1, col2 =  st.columns([1, 1])

with col1:
   col1.subheader("月額会費売上および自社取り分")
   pivot_table = pd.pivot_table(df, index=(["新 業務提携者（従属）","自社報酬率"]), values=["合計金額","自社報酬分","数量"],  aggfunc="sum", margins=True)
   pivot_table

#df = df.groupby(by=(["新業務提携者（従属）","新報酬率(自社)2"])).sum(numeric_only=True)
#st.subheader("当月発生月額会費分")
#st.table(df[["合計金額"]])

#df = df.groupby(by=(["新業務提携者（従属）","新報酬率(自社)2"])).sum(numeric_only=True)
#st.subheader("自社報酬分")
#st.table(df[["自社報酬分"]])

with col2:
   st.subheader("月額会費売上")
   month_group_df = df.groupby(["新 業務提携者（従属）"]).sum(numeric_only=True)
#month_group_df2 = df.groupby(["新業務提携者（従属）"]).sum(numeric_only=True)
   fig = px.bar(month_group_df.reset_index(), x="新 業務提携者（従属）", y="合計金額",color="新 業務提携者（従属）", title="")
#fig2 = px.bar(month_group_df.reset_index(), x="新業務提携者（従属）",  y="自社報酬分",color="新業務提携者（従属）", title="金額")
   fig.update_yaxes(tickformat="d")
   st.plotly_chart(fig, use_container_width=True)


#month_group_df2 = df.groupby(["新業務提携者（従属）"]).sum(numeric_only=True)
#fig = px.bar(df.reset_index(), x="新 業務提携者（従属）", y="自社報酬分",color="新 業務提携者（従属）", title="金額")
#fig2 = px.bar(month_group_df.reset_index(), x="新業務提携者（従属）",  y="自社報酬分",color="新業務提携者（従属）", title="金額")
#fig.update_yaxes(tickformat="d")
#st.subheader("パートナー別")
#st.plotly_chart(fig, use_container_width=True)


st.title("■分割商品データ■")
df_2 = pd.read_excel("./注文データベース202501分割ｷｬﾝｾﾙ未入金除き.xlsx", sheet_name="Sheet1", header=0, usecols="A:DZ")

df_2["自社報酬分"] = (df_2["合計金額"]*df_2["新 報酬率(自社)"] /100).astype(int)# 列を追加

df_2["2025年1月(自)"] = (df_2["2025年1月"]*df_2["新 報酬率(自社)"] /100).astype(int)# 列を追加
df_2["2025年2月(自)"] = (df_2["2025年2月"]*df_2["新 報酬率(自社)"] /100).astype(int)# 列を追加
df_2["2025年3月(自)"] = (df_2["2025年3月"]*df_2["新 報酬率(自社)"] /100).astype(int)# 列を追加
df_2["2025年4月(自)"] = (df_2["2025年4月"]*df_2["新 報酬率(自社)"] /100).astype(int)# 列を追加
df_2["2025年5月(自)"] = (df_2["2025年5月"]*df_2["新 報酬率(自社)"] /100).astype(int)# 列を追加
df_2["2025年6月(自)"] = (df_2["2025年6月"]*df_2["新 報酬率(自社)"] /100).astype(int)# 列を追加
st.subheader("分割（〇回目/□分割） 次月以降発生予測")
pivot_table2 = pd.pivot_table(df_2, index=(["新 業務提携者（従属）","自社報酬率"]), values=["2025年1月","2025年2月","2025年3月","2025年4月","2025年5月"],  aggfunc="sum", margins=True)
pivot_table2


st.subheader("分割（〇回目/□分割）うち自社取り分")
pivot_table3 = pd.pivot_table(df_2, index=(["新 業務提携者（従属）","自社報酬率"]), values=["2025年1月(自)","2025年2月(自)","2025年3月(自)","2025年4月(自)","2025年5月(自)"],  aggfunc="sum", margins=True)
pivot_table3



st.title("■統合データ■")
df_3 = pd.read_excel("./月額_分割統合.xlsx", sheet_name="Sheet1", header=0, usecols="A:O")

df_3=df_3.round(0)
st.subheader("次月以降　ストック分予測統合")
pivot_table4 = pd.pivot_table(df_3, index=(["新 業務提携者（従属）","自社報酬率"]), values=["2025年2月","2025年3月","2025年4月","2025年5月"],  aggfunc="sum", margins=True)
pivot_table4

st.subheader("次月以降　ストック分予測統合　うち自社取り分")
pivot_table5 = pd.pivot_table(df_3, index=(["新 業務提携者（従属）","自社報酬率"]), values=["2025年2月(自)","2025年3月(自)","2025年4月(自)","2025年5月(自)"],  aggfunc="sum", margins=True)
pivot_table5

#st.subheader("統合")
#group_df = df_3.groupby(["新 業務提携者（従属）"]).sum(numeric_only=True)
#fig = px.bar(group_df.reset_index(), x=["2025年2月","2025年3月","2025年4月","2025年5月"], y="合計金額",color="新 業務提携者（従属）", title="")
#fig.update_yaxes(tickformat="d")
#st.plotly_chart(fig, use_container_width=True)



st.title("■統合データ2■")
df_4 = pd.read_excel("./月額_分割統合.xlsx", sheet_name="Sheet2", header=0, usecols="A:F")

df_4=df_4.round(0)
st.subheader("次月以降　ストック分予測統合")
#pivot_table5 = pd.pivot_table(df_4, index=(["新 業務提携者（従属）","自社報酬率"]), , columns=["計上月"],values=["合計金額"],  aggfunc="sum", margins=True)
#pivot_table5

pivot_table5 = pd.pivot_table(df_4, index=["新 業務提携者（従属）","自社報酬率"], columns=["計上月"],values=["合計金額"],  aggfunc="sum", margins=True)
pivot_table5


#st.subheader("次月以降　ストック分予測統合　うち自社取り分")
#pivot_table5 = pd.pivot_table(df_3, index=(["新 業務提携者（従属）","自社報酬率"]), values=["2025年2月(自)","2025年3月(自)","2025年4月(自)","2025年5月(自)"],  aggfunc="sum", margins=True)
#pivot_table5

st.subheader("")
group2_df = df_4.groupby(["新 業務提携者（従属）","計上月"]).sum(numeric_only=True)
fig = px.bar(group2_df.reset_index(), x="計上月", y="合計金額",color="新 業務提携者（従属）", title="")
fig.update_yaxes(tickformat="d")
st.plotly_chart(fig, use_container_width=True)

