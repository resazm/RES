import streamlit as st

pg = st.navigation([st.Page("100_メディア別ニュース取得ツール1.py"), 
                    st.Page("100_メディア別ニュース取得ツール2.py"), 
                    st.Page("101_LMEデータ取得.py"),
                    st.Page("102_銀行口座ウォーターフォールチャート作成ツール.py"), 
                    st.Page("103_日経平均.py"), 
                    st.Page("104_yfinanceデータ取得.py"), 
                    st.Page("105_LP分析.py"),
                    st.Page("106_ランキング.py"),
                    st.Page("107_経済指標.py")])
pg.run()