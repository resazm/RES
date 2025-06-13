import requests
from bs4 import BeautifulSoup
import streamlit as st
import re
import time

st.title("決算発表予定企業検索")

def fetch_companies(date_str):
    url = f"https://www.traders.co.jp/market_jp/earnings_calendar/all/all/1?term={date_str}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")

        st.write(f"取得URL: {url}")

        companies = []

        selectors_to_try = [
            "table.data_table.table.inner_elm tr.today",
            "table.data_table.table.inner_elm tr",
            "table.data_table tr.today",
            "table.data_table tr",
            ".data_table tr",
            "table tr"
        ]

        found_companies = False

        for selector in selectors_to_try:
            rows = soup.select(selector)
            if rows:
                st.write(f"セレクタ '{selector}' で {len(rows)} 行発見")
                for row in rows:
                    a_tags = row.find_all("a", href=True)
                    for a_tag in a_tags:
                        href = a_tag.get("href", "")
                        match = re.search(r"/stocks/([0-9A-Z]+)/$", href)
                        if match:
                            code = match.group(1)
                            name = a_tag.get_text(strip=True)
                            if name:
                                companies.append(f"<{code}>{name}")
                                found_companies = True
                if found_companies:
                    break

        if not found_companies:
            tables = soup.find_all("table")
            st.write(f"ページ内のテーブル数: {len(tables)}")
            for i, table in enumerate(tables):
                class_attr = table.get('class', [])
                st.write(f"テーブル {i+1}: クラス = {class_attr}")
                rows = table.find_all("tr")[:3]
                for j, row in enumerate(rows):
                    st.write(f"   行 {j+1}: {row.get_text(strip=True)[:100]}...")
        
        # ここから追加
        st.write(f"**総件数: {len(list(dict.fromkeys(companies)))} 件**") 
        # ここまで追加

        return list(dict.fromkeys(companies))

    except requests.exceptions.RequestException as e:
        st.error(f"データの取得中にエラーが発生しました: {e}")
        return []
    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {e}")
        return []

def fetch_companies_alternative_approach(date_str):
    url_patterns = [
        f"https://www.traders.co.jp/market_jp/earnings_calendar/all/all/1?term={date_str}",
        f"https://www.traders.co.jp/market_jp/earnings_calendar?term={date_str}",
        f"https://www.traders.co.jp/market_jp/earnings_calendar/all?term={date_str}",
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for url in url_patterns:
        try:
            st.write(f"試行中: {url}")
            res = requests.get(url, headers=headers, timeout=15)
            res.raise_for_status()
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.find_all("a", href=re.compile(r"/stocks/[0-9A-Z]+/$"))
            companies = []
            for link in links:
                href = link.get("href", "")
                match = re.search(r"/stocks/([0-9A-Z]+)/$", href)
                if match:
                    code = match.group(1)
                    name = link.get_text(strip=True)
                    if name:
                        companies.append(f"<{code}>{name}")
            if companies:
                st.success(f"成功: {url} から {len(companies)} 件取得")
                # ここから追加
                st.write(f"**総件数: {len(list(dict.fromkeys(companies)))} 件**")
                # ここまで追加
                return list(dict.fromkeys(companies))
            time.sleep(1)
        except Exception as e:
            st.write(f"URL {url} でエラー: {e}")
            continue

    return []

# Streamlit UI
input_date = st.date_input("日付を選択してください")

col1, col2 = st.columns(2)

with col1:
    if st.button("決算発表企業を表示（通常）"):
        formatted_date = input_date.strftime("%Y/%m/%d")

        month = input_date.strftime("%m").lstrip("0")
        day = input_date.strftime("%d").lstrip("0")
        weekday_jp = {"Mon": "月", "Tue": "火", "Wed": "水", "Thu": "木", "Fri": "金", "Sat": "土", "Sun": "日"}
        weekday = weekday_jp[input_date.strftime("%a")]
        display_date = f"{month}/{day}({weekday})"

        with st.spinner("企業情報を取得中..."):
            companies = fetch_companies(formatted_date)

        if companies:
            output_text_lines = []
            output_text_lines.append(f"□{display_date}の決算発表企業")
            output_text_lines.append("")
            for c in companies[:15]:
                output_text_lines.append(c)
            if len(companies) > 15:
                output_text_lines.append("")
                output_text_lines.append(f"<他{len(companies) - 15}件>")
            st.code("\n".join(output_text_lines), language="text")
        else:
            st.write("決算予定表が見つかりませんでした。")

# デバッグ情報
st.write("---")
st.write("デバッグ情報:")
formatted_date = input_date.strftime("%Y/%m/%d")
st.write(f"選択した日付: {input_date}")
st.write(f"フォーマット後: {formatted_date}")
st.write(f"生成されるURL: https://www.traders.co.jp/market_jp/earnings_calendar/all/all/1?term={formatted_date}")