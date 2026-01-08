from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
from plotly.subplots import make_subplots

st.set_page_config(
   page_title="",
   layout="wide",
)

df_kokyaku = pd.read_excel("./顧客DB.xlsx", sheet_name="Sheet1", header=0, usecols="A:CN")
df = pd.read_excel("./注文DB.xlsx", sheet_name="Sheet1", header=0, usecols="A:EC")

df["新 報酬率(パートナー)"].fillna(0, inplace=True)
df["新 報酬率(自社)"].fillna(0, inplace=True)
df["オプトイン"].fillna("(空欄)", inplace=True)
df_kokyaku["オプトイン"].fillna("(空欄)", inplace=True)

df[["新 報酬率(パートナー)", "新 報酬率(自社)","合計金額"]] = df[["新 報酬率(パートナー)", "新 報酬率(自社)","合計金額"]].astype(int)  # 金額や数量を整数型に変換


df["月"] = df["注文日"].dt.month.astype(str)  # "月"の列を追加
df["年"] = df["注文日"].dt.year.astype(str)  # "年"の列を追加
df["年月"] = df['注文日'].dt.strftime('%Y/%m')
df["年月日"] = df['注文日'].dt.strftime('%Y/%m/%d')
df["日付"] = df['注文日'].dt.strftime('%d')

df_kokyaku["月"] = df_kokyaku["顧客登録日"].dt.month.astype(str)  # "月"の列を追加
df_kokyaku["年"] = df_kokyaku["顧客登録日"].dt.year.astype(str)  # "年"の列を追加
df_kokyaku["年月"] = df_kokyaku["顧客登録日"].dt.strftime('%Y/%m')
df_kokyaku["年月日"] = df_kokyaku["顧客登録日"].dt.strftime('%Y/%m/%d')
df_kokyaku["日付"] = df_kokyaku["顧客登録日"].dt.strftime('%d')
df_kokyaku["日付2"] = df_kokyaku["顧客登録日"].dt.strftime('%m/%d')

df["自社報酬分"] = (df["合計金額"]*df["新 報酬率(自社)"] /100).astype(int)# 列を追加


today = date.today()  # 今日の日付を取得
this_year = today.year  # 年を取り出し
this_month = today.month  # 月を取り出し
one_month_ago = (today - relativedelta(months=1)) # 先月の月だけを取り出したいので


this_ym = format(date.today(), '%Y/%m')

st.title("■注文DB/顧客DBデータ分析　ダッシュボード")
st.write(f"{today}時点")
st.write("-----------------------")
st.subheader("🖥️顧客DB")
this_year_kokyaku = df_kokyaku.loc[df_kokyaku["顧客登録日"].dt.year == this_year, "顧客ID"].count()
st.metric("📝今年の新規顧客DB登録件数", f"{this_year_kokyaku}名", border=True)


col1, col2, col3= st.columns(3)
with col1:
    one_month_ago_kokyaku = df_kokyaku.loc[df_kokyaku["顧客登録日"].dt.month == one_month_ago.month, "顧客ID"].count()
    st.metric(f"📓{one_month_ago.month}月の新規顧客DB登録件数", f"{one_month_ago_kokyaku}名", border=True)
with col2:
    this_month_kokyaku = df_kokyaku.loc[df_kokyaku["顧客登録日"].dt.month == this_month, "顧客ID"].count()
    gap=(this_month_kokyaku-one_month_ago_kokyaku)
    gap=str(gap)
    st.metric(f"📓{this_month}月の新規顧客DB登録件数", f"{this_month_kokyaku}名", border=True, delta=gap +"名")

col1, col2, col3= st.columns(3)
with col1:
    grouped2 = df_kokyaku.groupby("年月").count()
    fig = px.bar(grouped2 .reset_index(), x="年月", y="顧客ID", barmode="stack",title=f"{this_year}年 月別 顧客DB登録件数")
    fig.update_layout(width=500,height=400)
    fig.update_yaxes(title="顧客DB登録件数",tickformat=",",linecolor='black',dtick=200)
    fig.update_xaxes(title="",range=(-1, 12),linecolor='black',)
    st.subheader("")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    df_kokyaku = df_kokyaku.loc[df_kokyaku["顧客登録日"].dt.month == this_month]
    grouped3 = df_kokyaku.groupby("日付").count()
    fig = px.bar(grouped3.reset_index(), x="日付", y="顧客ID", barmode="stack",title=f"{this_month}月 日別 顧客DB登録件数")
    fig.update_layout(width=500,height=400)
    fig.update_yaxes(title="顧客DB登録件数",tickformat=",",linecolor='black',dtick=20)
    fig.update_xaxes(range=(0, 31),linecolor='black',dtick=2)
    st.subheader("")
    st.plotly_chart(fig, use_container_width=True)


st.subheader(f"📓{this_month}月の顧客DB 新規登録者流入元TOP10")
col1, col2= st.columns([1,3])
with col1:
    df_kokyaku2= df_kokyaku.loc[(df_kokyaku["顧客登録日"].dt.month  == this_month)&(df_kokyaku["顧客登録日"].dt.year  == this_year)]
    grouped = df_kokyaku2.groupby("オプトイン").count()
    #grouped = grouped.assign(合計 = grouped.sum(axis=0))
    #grouped = pd.concat([grouped.sum(numeric_only=True)], ignore_index=True)
    grouped = grouped.sort_values(by="顧客ID", ascending=False)
    grouped["顧客ID"]
with col2:
#pivot_table = pd.pivot_table(grouped , index=["オプトイン"],columns="顧客ID",values=["顧客ID"],  aggfunc="sum", margins=True)
#pivot_table
    fig = px.bar(grouped.iloc[:10].sort_values(by="顧客ID", ascending=False).reset_index(), x="顧客ID", y="オプトイン", color="オプトイン", orientation="h")
    fig.update_layout(showlegend=True,plot_bgcolor="white")
    fig.update_xaxes(title="登録件数",linecolor='black',side="top",ticks='inside',gridcolor='lightgrey', gridwidth=10, griddash='dot',dtick=25) #,range=(0, 800)
    fig.update_yaxes(title="流入元",linecolor='black',gridcolor='lightgrey', gridwidth=1, griddash='dot')
    st.plotly_chart(fig, use_container_width=True)





st.write("-----------------------")
st.subheader("🖥️注文DB")
col1, col2, col3= st.columns(3)
# 今年
this_year_counts = df.loc[df["注文日"].dt.year == this_year, "数量"].sum()
col1.metric("📝今年の注文件数", f"{this_year_counts:,}件", border=True)

this_year_purchase = df.loc[df["注文日"].dt.year == this_year, "合計金額"].sum()
#this_year_purchase.tickformat=","
col2.metric("💰今年の注文金額合計", f"{this_year_purchase:,}円", border=True)

this_year_Reg = df.loc[df["顧客登録日"].dt.year  == this_year , "数量"].sum()
col3.metric("📓顧客登録日が今年の人の今年の注文件数累計", f"{this_year_Reg:,}件", border=True)
st.write("-----------------------")

# 先月
col1, col2, col3= st.columns(3)
last_month_counts = df.loc[df["注文日"].dt.month == one_month_ago.month, "数量"].sum()
col1.metric("📝先月の注文件数", f"{last_month_counts:,}件", border=True)

last_month_purchase = df.loc[df["注文日"].dt.month == one_month_ago.month, "合計金額"].sum()
col2.metric("💰先月の注文金額合計", f"{last_month_purchase:,}円", border=True)

last_month_Reg = df.loc[(df["顧客登録日"].dt.month  == one_month_ago.month)&(df["顧客登録日"].dt.year  == this_year)&(df["注文日"].dt.month  == one_month_ago.month), "数量"].sum()
col3.metric(f"📓顧客登録日が{one_month_ago.month}月の人の{one_month_ago.month}月中の注文件数", f"{last_month_Reg:,}件", border=True)

# 今月
col1, col2, col3= st.columns(3)
this_month_counts = df.loc[df["注文日"].dt.month == this_month, "数量"].sum()
gap=(this_month_counts-last_month_counts)
gap=str(gap)
col1.metric("📝今月の注文件数", f"{this_month_counts:,}件", border=True, delta=gap +"件")

this_month_purchase = df.loc[df["注文日"].dt.month == this_month, "合計金額"].sum()
gap=this_month_purchase-last_month_purchase
gap=int(gap)
gap=f"{gap:,}"
col2.metric("💰今月の注文金額合計", f"{this_month_purchase:,}円", border=True, delta=gap +"円")

this_month_Reg = df.loc[(df["顧客登録日"].dt.month  == this_month)&(df["顧客登録日"].dt.year  == this_year) , "数量"].sum()
gap=this_month_Reg-last_month_Reg
gap=int(gap)
gap=f"{gap:,}"
col3.metric(f"📓顧客登録日が{this_month}月の人の{this_month}月中の注文件数", f"{this_month_Reg:,}件", border=True, delta=gap +"件")


st.write("-----------------------")

col1, col2 =  st.columns([2, 1])
with col1:
    st.subheader("当月　日別/パートナー別注文動向（合計金額）")
    tougetu_df = df[(df["年月"] == this_ym)]
    pivot_table = pd.pivot_table(tougetu_df , index=["年月日"],columns="新 業務提携者（従属）",values=["合計金額"],  aggfunc="sum", margins=True)
    pivot_table
with col2:
    fig = px.bar(tougetu_df .reset_index(), x="日付", y="合計金額", color="新 業務提携者（従属）", title="金額", barmode="stack")
    fig.update_yaxes(tickformat=",")#,range=(0, 2000000)
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
    fig.update_yaxes(tickformat=",")
    fig.update_xaxes(dtick=2,range=(0, 31))
    st.subheader("")
    st.plotly_chart(fig, use_container_width=True)

col1, col2 =  st.columns([1, 3])
with col1:
    st.subheader("当月注文顧客の流入元")
    pivot_table = pd.pivot_table(tougetu_df, index=["オプトイン"],values=["合計金額","数量"],  aggfunc="sum").sort_values("合計金額",ascending=False)
    pivot_table
    #tougetu_df2 = tougetu_df.groupby("オプトイン").sum(numeric_only=True).iloc[:10].reset_index() #※トップ10だけ表示
    #pivot_table = pd.pivot_table(tougetu_df2, index=["オプトイン"],values=["合計金額","数量"],  aggfunc="sum").sort_values("合計金額",ascending=False)
    #pivot_table
with col2:
    #st.subheader("")
    #fig = px.bar(tougetu_df.sort_values(by="オプトイン", ascending=False), x="合計金額", y="オプトイン", color="オプトイン", orientation="h")
    #fig.update_layout(showlegend=False,plot_bgcolor="white")
    #fig.update_xaxes(title="当月注文金額合計",linecolor='black',side="top",ticks='inside',gridcolor='lightgrey', gridwidth=10, griddash='dot',tickformat=",",dtick=100000)
    #fig.update_yaxes(title="顧客流入元",linecolor='black',gridcolor='lightgrey', gridwidth=1, griddash='dot',categoryorder='total ascending',tickfont_size=7)
    #st.plotly_chart(fig, use_container_width=True)
    st.subheader("")
    tougetu_df2 = tougetu_df.groupby("オプトイン").sum(numeric_only=True).sort_values(by="合計金額", ascending=False).iloc[:20].reset_index() #※トップ20だけ表示
    fig2 = px.bar(tougetu_df2.sort_values(by="オプトイン", ascending=False), x="合計金額", y="オプトイン", color="オプトイン", orientation="h", title="オプトイン別 当月注文金額合計 TOP20")
    fig2.update_layout(showlegend=False,plot_bgcolor="white")
    fig2.update_xaxes(title="当月注文金額合計",linecolor='black',side="top",ticks='inside',gridcolor='lightgrey', gridwidth=10, griddash='dot',tickformat=",",dtick=200000)
    fig2.update_yaxes(title="顧客流入元",linecolor='black',gridcolor='lightgrey', gridwidth=1, griddash='dot',categoryorder='total ascending',tickfont_size=10)
    st.plotly_chart(fig2, use_container_width=True)

#fig = go.Figure()
#fig= make_subplots(specs=[[{"secondary_y": True}]])
#tougetu_df3 = tougetu_df.groupby("オプトイン").count().reset_index()
#fig.add_trace(go.Bar(x=tougetu_df3["合計金額"], y=tougetu_df3["オプトイン"]))
#fig.add_trace(go.Bar(x=tougetu_df3["数量"], y=tougetu_df3["オプトイン"]))
#fig.update_layout(legend=dict(orientation='h'))
#st.plotly_chart(fig, use_container_width=True)

st.subheader("上記　オプトインが「(空欄)」のデータ一覧")
st.dataframe(tougetu_df.loc[(df["オプトイン"]  == "(空欄)") ].reset_index())

col1, col2 =  st.columns([1, 1])
with col1:
    st.subheader('購入者分布(累計)')
    st.map(df[['latitude', 'longitude']])
with col2:
    st.subheader('当月　購入者分布')
    st.map(tougetu_df[['latitude', 'longitude']])



st.subheader('当月　購入単価ヒストグラム')
fig = px.histogram(tougetu_df, x='商品単価', nbins=100)
fig.update_yaxes(tickformat=",")
fig.update_xaxes(dtick=10000) #range=(0, 500000)
fig.update_layout(bargap=0.1)
st.plotly_chart(fig, use_container_width=True)




st.subheader("当月　商品別集計")
tougetu_df["商品単価"] = tougetu_df["商品単価"].astype(str) 
pivot_table = pd.pivot_table(tougetu_df , index=["新 業務提携者（従属）","商品名","商品単価"],values=["合計金額","数量"],  aggfunc="sum", margins=True).sort_values("数量",ascending=False)
pivot_table

#col1, col2=  st.columns(2)
#grouped_agg = tougetu_df.groupby(["新 業務提携者（従属）","オプトイン"]).sum(numeric_only=True)
#st.subheader("当月　オプトイン集計")
#pivot_table = pd.pivot_table(tougetu_df, index=["新 業務提携者（従属）","オプトイン"],values=["合計金額","数量"],  aggfunc="sum").sort_values("新 業務提携者（従属）",ascending=False)
#pivot_table

st.subheader("当月　受注経路集計")
pivot_table = pd.pivot_table(tougetu_df , index=["受注経路"],values=["合計金額","数量"],  aggfunc="sum", margins=True).sort_values("数量",ascending=False)
pivot_table 

st.write("-----------------------")

st.title("■注文DBデータ集計")
st.write("注文DBよりテストアカウント,キャンセル,未課金,未入金を除いた生データ。分割決済や計上月を考慮していない注文月ベースのデータのため、実際の会計上の売上とは異なる。")

pivot_table = pd.pivot_table(df, index=["新 業務提携者（従属）"], columns=["年月"],values=["合計金額","自社報酬分"],  aggfunc="sum", margins=True)
pivot_table

df1 = df.groupby(["年月", "新 業務提携者（従属）"]).sum(numeric_only=True)

col1, col2 =  st.columns([1, 1])
with col1:  
    fig = px.bar(df1.reset_index(), x="年月", y="合計金額", color="新 業務提携者（従属）", title="金額", barmode="stack")
    fig.update_yaxes(tickformat=",",range=(0, 100000000),dtick=10000000)
    st.subheader("全体売上分")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.bar(df1.reset_index(), x="年月", y="自社報酬分", color="新 業務提携者（従属）", title="金額", barmode="stack")
    fig.update_yaxes(tickformat=",",range=(0, 100000000),dtick=10000000)
    st.subheader("自社利益相当分(売上*自社報酬率％")
    st.plotly_chart(fig, use_container_width=True)


