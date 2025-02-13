import streamlit as st

st.set_page_config(page_title="Streamlit App", page_icon="Bar Chart")

st.title("RES売上データ集計")
st.write("written in Python by higashi 2024.2")

st.write("----------------------------------------")
st.write("・パートナー別売上データ")
st.write("会計上のデータ(の一部)のパートナー別集計。役務提供月を計上月としている。")

st.write("・ストック予測")
st.write("月額会費と分割商品の売上予測")

st.write("・DB")
st.write("注文DBよりテストアカウント,キャンセル,未課金,未入金を除いた生データ。分割決済や計上月を考慮していない注文月ベースのデータのため、実際の会計上の売上とは異なる。")
st.write("----------------------------------------")