import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time
import unicodedata

# ページ設定
st.set_page_config(page_title="Yahoo!ニューススクレイピング", layout="wide", initial_sidebar_state="collapsed")

st.title("📡 メディア別ニュース取得ツール")
st.write("🔍 下記、指定したキーワードで記事をスクレイピングします（編集可）")
st.write("　指定キーワードが記事のタイトルに含まれるものを取得します。2025/5/20 東作成")

# メディアとURL設定
media_sources = {
    "トレーダーズ・ウェブ": "https://finance.yahoo.co.jp/news/media/dzh",
    "ウエルスアドバイザー": "https://finance.yahoo.co.jp/news/media/mosf",
    "株探": "https://finance.yahoo.co.jp/news/media/stkms",
    "ロイター": "https://finance.yahoo.co.jp/news/media/reut"
}

# デフォルトキーワード設定
default_keywords = {
    "トレーダーズ・ウェブ": ["大引け概況"],
    "ウエルスアドバイザー": ["日経平均は"],
    "株探": ["日経平均"],
    "ロイター": ["午前の日経平均は"]
}

# ページ数入力
st.markdown("### 📄 検索するページ数")
num_pages = st.number_input("ページ数（1～20）", min_value=1, max_value=20, value=3, step=1)

# 🔧 メディアごとのチェックとキーワード入力
st.markdown("### ✅ スクレイピング対象のメディアと記事タイトルキーワードを選択")

selected_media = {}
custom_keywords = {}

for media in media_sources.keys():
    col1, col2 = st.columns([1, 3])
    with col1:
        use_media = st.checkbox(f"{media} を取得", value=True)
    if use_media:
        with col2:
            default = ", ".join(default_keywords[media])
            user_input = st.text_input(f"📝 {media} のキーワード", value=default, key=media)
            selected_media[media] = media_sources[media]
            custom_keywords[media] = [kw.strip() for kw in user_input.split(",") if kw.strip()]

# ニュース取得関数
def fetch_news(keywords_dict, max_page, active_sources):
    all_results = {}

    for media_name, base_url in active_sources.items():
        st.write(f"📰 {media_name} の記事を取得中...")
        keywords = keywords_dict.get(media_name, [])
        media_news = []

        for page in range(1, max_page + 1):
            url = base_url if page == 1 else f"{base_url}?vip=off&page={page}"
            try:
                req = requests.get(url, timeout=10)
                soup = BeautifulSoup(req.content, "html.parser")
                elems = soup.find_all(href=re.compile("finance.yahoo.co.jp/news/detail"))

                for elem in elems:
                    title = elem.text.strip()
                    link = elem.attrs['href']
                    pub_time = "不明"

                    if any(kw in title for kw in keywords):
                        try:
                            res_detail = requests.get(link, timeout=10)
                            soup_detail = BeautifulSoup(res_detail.content, "html.parser")

                            # 公開日時の取得
                            time_elem = soup_detail.find("p", class_=re.compile("time"))
                            if time_elem:
                                pub_time = time_elem.text.strip().replace("配信", "").strip()

                            # 本文取得
                            body_elem = soup_detail.find(class_=re.compile("textArea"))
                            if body_elem:
                                body = unicodedata.normalize('NFKC', body_elem.text.strip())
                                media_news.append({
                                    "タイトル": title,
                                    "URL": link,
                                    "公開日時": pub_time,
                                    "本文": body
                                })
                            time.sleep(1)
                        except Exception as e:
                            print(f"Error fetching detail page: {e}")
            except Exception as e:
                print(f"Error fetching list page: {e}")

        all_results[media_name] = media_news

    return all_results

# ニュース取得ボタン
if st.button("🧲 ニュースを取得"):
    if not selected_media:
        st.warning("⚠️ 少なくとも1つのメディアを選択してください。")
    else:
        results = fetch_news(custom_keywords, num_pages, selected_media)

        # カラム数を動的に分ける（選択メディア数）
        cols = st.columns(len(selected_media))
        for idx, media_name in enumerate(selected_media.keys()):
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
