import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import unicodedata

# ページ設定
st.set_page_config(page_title="Yahoo!ニューススクレイピング", layout="wide")

st.title("📡 メディア別ニュース取得ツール")
st.write("トレーダーズ・ウェブ:[大引け概況]")
st.write("ウエルスアドバイザー:[日経平均は]")
st.write("株探:[日経平均])")
st.write("ロイター:[午前の日経平均は]")
st.write("のキーワードで記事をスクレイピング")



# メディア設定
media_sources = {
    "トレーダーズ・ウェブ": "https://finance.yahoo.co.jp/news/media/dzh",
    "ウエルスアドバイザー": "https://finance.yahoo.co.jp/news/media/mosf",
    "株探": "https://finance.yahoo.co.jp/news/media/stkms",
    "ロイター": "https://finance.yahoo.co.jp/news/media/reut"
}

media_keywords = {
    "トレーダーズ・ウェブ": ["大引け概況"],
    "ロイター": ["午前の日経平均は"],
    "ウエルスアドバイザー": ["日経平均は"],
    "株探": ["日経平均"]
}

def fetch_news():
    all_results = {}

    for media_name, base_url in media_sources.items():
        st.write(f"📰 {media_name} の記事を取得中...")
        keywords = media_keywords.get(media_name, [])
        media_news = []

        for page in [1, 2, 3]:
            url = base_url if page == 1 else f"{base_url}?vip=off&page={page}"
            req = requests.get(url)
            soup = BeautifulSoup(req.content, "html.parser")
            elems = soup.find_all(href=re.compile("finance.yahoo.co.jp/news/detail"))

            for elem in elems:
                title = elem.text.strip()
                link = elem.attrs['href']
                pub_time = "不明"

                # キーワードマッチ
                if any(kw in title for kw in keywords):
                    try:
                        res_detail = requests.get(link)
                        soup_detail = BeautifulSoup(res_detail.content, "html.parser")

                        # 公開時刻を取得（詳細ページの <p class="time_3Lu0">）
                        time_elem = soup_detail.find("p", class_=re.compile("time"))
                        if time_elem:
                            pub_time = time_elem.text.strip().replace("配信", "").strip()

                        # 本文
                        elems_detail = soup_detail.find(class_=re.compile("textArea"))
                        if elems_detail:
                            body = unicodedata.normalize('NFKC', elems_detail.text.strip())
                            media_news.append({
                                "タイトル": title,
                                "URL": link,
                                "公開日時": pub_time,
                                "本文": body
                            })
                        time.sleep(1)
                    except Exception as e:
                        print(f"Error fetching detail: {e}")

        all_results[media_name] = media_news

    return all_results

# ボタン
if st.button("🧲 ニュースを取得"):
    results = fetch_news()

    # カラム分割（最大4つ）
    media_list = list(media_sources.keys())
    cols = st.columns(4)

    for idx, media_name in enumerate(media_list):
        with cols[idx]:
            st.subheader(media_name)
            articles = results.get(media_name, [])
            if not articles:
                st.write("📭 該当記事なし")
            else:
                for article in articles:
                    st.markdown(f"### [{article['タイトル']}]({article['URL']})")
                    st.caption(f"🕒 公開日時: {article['公開日時']}")
                    st.write(article['本文'])
                    st.markdown("---")
