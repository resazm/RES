import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import html

# ページ設定
st.set_page_config(page_title="Yahoo!ニューススクレイピング", layout="wide", initial_sidebar_state="collapsed")

st.title("\U0001f4e1 メディア別ニュース取得ツール")
st.write("対象メディア：トレーダーズ・ウェブ、ウエルスアドバイザー、株探、ロイター")

# 検索対象の選択
search_mode = st.radio(
    "\U0001f50d キーワードの検索対象を選択",
    ["タイトルに含まれる", "本文に含まれる", "どちらかに含まれる"],
    index=2,  # ←「どちらかに含まれる」を初期選択
    horizontal=True
)

# メディア設定
media_sources = {
    "トレーダーズ・ウェブ": "https://finance.yahoo.co.jp/news/media/dzh",
    "ウエルスアドバイザー": "https://finance.yahoo.co.jp/news/media/mosf",
    "株探": "https://finance.yahoo.co.jp/news/media/stkms",
    "ロイター": "https://finance.yahoo.co.jp/news/media/reut"
}

# デフォルトキーワード
default_keywords = {
    "トレーダーズ・ウェブ": "大引け概況",
    "ロイター": "午前の日経平均は",
    "ウエルスアドバイザー": "日経平均は",
    "株探": "値上がり"
}

# メディア別設定フォーム
st.markdown("### \U0001f4dd メディア選択・キーワード・ページ数・公開時間フィルタの設定")
media_cols = st.columns(4)
selected_media = {}

for idx, (media, url) in enumerate(media_sources.items()):
    with media_cols[idx]:
        enabled = st.checkbox(f" {media}", value=True)
        if enabled:
            keyword_input = st.text_input(f"キーワード ({media})", value=default_keywords[media], key=f"kw_{media}")
            page_num = st.number_input(f"ページ数 ({media})", min_value=1, max_value=10, value=1, key=f"pg_{media}")
            time_default = "12:00" if media == "ロイター" else ""
            time_filter = st.text_input(f"公開時間フィルタ（HH:MM以降、空欄で無効） ({media})", value=time_default, key=f"time_{media}")
            selected_media[media] = {
                "url": url,
                "keywords": [kw.strip() for kw in keyword_input.split(",") if kw.strip()],
                "pages": page_num,
                "time_filter": time_filter.strip()
            }

def parse_time(pub_time_str):
    # 公開日時テキストから時刻を抽出（例："15:45"をdatetime.timeオブジェクトで返す）
    m = re.search(r'(\d{1,2}):(\d{2})', pub_time_str)
    if m:
        hour, minute = int(m.group(1)), int(m.group(2))
        return datetime.time(hour, minute)
    return None

def highlight_keywords(text, keywords):
    # キーワードをHTMLでハイライト（背景黄色）して返す
    def repl(m):
        return f"<mark>{html.escape(m.group(0))}</mark>"
    for kw in keywords:
        # 正規表現でキーワードをエスケープし全て大文字・小文字区別なく検索
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        text = pattern.sub(repl, text)
    return text

def fetch_article_detail(link):
    try:
        res_detail = requests.get(link, timeout=10)
        soup_detail = BeautifulSoup(res_detail.content, "html.parser")

        time_elem = soup_detail.find("p", class_=re.compile("time"))
        pub_time = time_elem.text.strip().replace("配信", "").strip() if time_elem else "不明"

        body_elem = soup_detail.find(class_=re.compile("textArea"))
        body = unicodedata.normalize('NFKC', body_elem.text.strip()) if body_elem else ""

        return pub_time, body
    except Exception as e:
        print(f"Error fetching detail: {e}")
        return "不明", ""

def process_media(media_name, info, keywords, search_mode):
    base_url = info["url"]
    max_page = info["pages"]
    time_filter_str = info.get("time_filter", "")

    if time_filter_str:
        try:
            filter_hour, filter_minute = map(int, time_filter_str.split(":"))
            filter_time = datetime.time(filter_hour, filter_minute)
        except:
            filter_time = None
    else:
        filter_time = None

    media_news = []

    for page in range(1, max_page + 1):
        url = base_url if page == 1 else f"{base_url}?vip=off&page={page}"
        try:
            req = requests.get(url, timeout=10)
            soup = BeautifulSoup(req.content, "html.parser")
            elems = soup.find_all(href=re.compile("finance.yahoo.co.jp/news/detail"))

            # マルチスレッドで記事詳細を取得
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_elem = {executor.submit(fetch_article_detail, elem.attrs['href']): elem for elem in elems}
                for future in as_completed(future_to_elem):
                    elem = future_to_elem[future]
                    title = elem.text.strip()
                    link = elem.attrs['href']

                    try:
                        pub_time, body = future.result()
                    except:
                        pub_time, body = "不明", ""

                    # 公開時間フィルタ判定
                    pub_time_obj = parse_time(pub_time)
                    if filter_time and pub_time_obj and pub_time_obj < filter_time:
                        continue  # 指定時間より前の記事はスキップ

                    # キーワードマッチ判定
                    keyword_matched = False
                    if search_mode == "タイトルに含まれる":
                        keyword_matched = any(kw in title for kw in keywords)
                    elif search_mode == "本文に含まれる":
                        keyword_matched = any(kw in body for kw in keywords)
                    elif search_mode == "どちらかに含まれる":
                        keyword_matched = any(kw in title or kw in body for kw in keywords)

                    if keyword_matched:
                        # キーワードハイライト適用（HTMLマークアップ）
                        title_hl = highlight_keywords(html.escape(title), keywords)
                        body_hl = highlight_keywords(html.escape(body), keywords)

                        media_news.append({
                            "タイトル": title_hl,
                            "URL": link,
                            "公開日時": pub_time,
                            "本文": body_hl
                        })

            time.sleep(1)
        except Exception as e:
            print(f"Error fetching list page: {e}")

    return media_news

# ニュース取得ボタン
if st.button("\U0001fa99 ニュースを取得"):
    results = {}
    # 並列で各メディア処理
    with ThreadPoolExecutor(max_workers=len(selected_media)) as executor:
        futures = {
            executor.submit(process_media, media, info, info["keywords"], search_mode): media
            for media, info in selected_media.items()
        }
        for future in as_completed(futures):
            media_name = futures[future]
            try:
                results[media_name] = future.result()
            except Exception as e:
                results[media_name] = []
                st.error(f"{media_name} の処理中にエラーが発生しました: {e}")

    if not results:
        st.warning("⚠️ 取得対象のメディアがありません。")

    media_list = list(results.keys())
    cols = st.columns(len(media_list)) if media_list else []

    fixed_order = ["トレーダーズ・ウェブ", "ウエルスアドバイザー", "株探", "ロイター"]
    active_media = [m for m in fixed_order if m in results]
    cols = st.columns(len(active_media))


    for idx, media_name in enumerate(active_media):
        with cols[idx]:
            st.subheader(media_name)
            articles = results.get(media_name, [])
            if not articles:
                st.write("\U0001f4ed 該当記事なし")
            else:
                for article in articles:
                    st.markdown(f"### <a href='{article['URL']}' target='_blank'>{article['タイトル']}</a>", unsafe_allow_html=True)
                    st.caption(f"\U0001f552 公開日時: {article['公開日時']}")
                    st.markdown(article['本文'].replace("\n", "<br>"), unsafe_allow_html=True)
                    st.markdown("---")
