import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor

# ページ設定
st.set_page_config(page_title="Yahoo!ニュースカテゴリ別スクレイピング", layout="wide")
st.title("📡 カテゴリ別ニュース取得ツール")
st.write("カテゴリ別に記事をスクレイピングし、キーワードでフィルタします。")

# カテゴリとURL
categories = {
    "日本株": "https://finance.yahoo.co.jp/news/stocks",
    "市況・概況": "https://finance.yahoo.co.jp/news/market",
    "FX": "https://finance.yahoo.co.jp/news/fx",
    "外国株": "https://finance.yahoo.co.jp/news/world",
    "決算速報": "https://finance.yahoo.co.jp/news/settlement"
}

# ✅ カテゴリ選択・ページ数
st.markdown("### ✅ カテゴリとページ数を選択")
selected_categories = {}
cols = st.columns(5)
for idx, (name, url) in enumerate(categories.items()):
    with cols[idx]:
        if st.checkbox(name, value=True):
            pages = st.number_input(f"{name}のページ数", 1, 10, 2, 1, key=f"pg_{name}")
            selected_categories[name] = {"url": url, "pages": pages}

# 🔍 キーワード設定
st.markdown("### 🔍 キーワード検索")
keyword_input = st.text_input("カンマ区切りで入力（例：日経平均, 円安, 決算）", "日経平均, 円安, 決算")
keywords = [k.strip() for k in keyword_input.split(",") if k.strip()]
filter_mode = st.selectbox("検索対象", ["タイトルのみ", "本文のみ", "タイトルと本文"])

# 記事詳細の取得
def fetch_article_detail(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")
        time_elem = soup.find("p", class_=re.compile("time"))
        pub_time = time_elem.text.strip().replace("配信", "").strip() if time_elem else "不明"
        body_elem = soup.find(class_=re.compile("textArea"))
        body = unicodedata.normalize('NFKC', body_elem.text.strip()) if body_elem else ""
        return pub_time, body
    except Exception as e:
        return "不明", ""

# カテゴリの記事一覧取得
def fetch_articles(name, url, pages):
    articles = []
    for page in range(1, pages + 1):
        list_url = url if page == 1 else f"{url}?page={page}"
        try:
            res = requests.get(list_url, timeout=10)
            soup = BeautifulSoup(res.content, "html.parser")
            elems = soup.find_all(href=re.compile("finance.yahoo.co.jp/news/detail"))
            for elem in elems:
                title = elem.text.strip()
                link = elem.attrs["href"]
                pub_time, body = fetch_article_detail(link)
                articles.append({
                    "タイトル": title,
                    "URL": link,
                    "公開日時": pub_time,
                    "本文": body
                })
        except Exception as e:
            print(f"[{name}] ページ取得エラー:", e)
    return name, articles

# フィルタ関数
def match_keywords(article, keywords, mode):
    title = article["タイトル"]
    body = article["本文"]
    if not keywords:
        return True
    if mode == "タイトルのみ":
        return any(k in title for k in keywords)
    elif mode == "本文のみ":
        return any(k in body for k in keywords)
    else:
        return any(k in title or k in body for k in keywords)

# 🔘 実行
if st.button("🧲 ニュースを取得"):
    if not selected_categories:
        st.warning("カテゴリを1つ以上選んでください。")
    else:
        st.info("取得中...（少し時間がかかる場合があります）")
        results = {}

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(fetch_articles, name, info["url"], info["pages"])
                for name, info in selected_categories.items()
            ]
            for future in futures:
                name, articles = future.result()
                results[name] = articles

        # 🔽 表示（カテゴリ別に5カラム）
        st.markdown("## 🗂️ 結果表示")
        col_outs = st.columns(5)
        for i, (cat, articles) in enumerate(results.items()):
            with col_outs[i]:
                st.subheader(cat)
                filtered = [a for a in articles if match_keywords(a, keywords, filter_mode)]
                if not filtered:
                    st.write("📭 該当記事なし")
                else:
                    for art in filtered:
                        st.markdown(f"**[{art['タイトル']}]({art['URL']})**")
                        st.caption(f"🕒 {art['公開日時']}")
                        with st.expander("📖 本文を表示"):
                            st.write(art["本文"])
                        st.markdown("---")

