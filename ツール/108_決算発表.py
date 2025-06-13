import requests
from bs4 import BeautifulSoup
import streamlit as st
import re
import time
import random

st.title("決算発表予定企業検索")

def get_random_headers():
    """ランダムなUser-Agentとヘッダーを返す"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }

def fetch_companies_with_session(date_str):
    """セッションを使用してアクセスする方法"""
    session = requests.Session()
    headers = get_random_headers()
    session.headers.update(headers)
    
    # まずトップページにアクセスしてセッションを確立
    try:
        st.write("セッション確立中...")
        session.get("https://www.traders.co.jp/", timeout=10)
        time.sleep(2)  # 少し待機
        
        url = f"https://www.traders.co.jp/market_jp/earnings_calendar/all/all/1?term={date_str}"
        st.write(f"取得URL: {url}")
        
        res = session.get(url, timeout=15)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        
        return parse_companies_from_html(res.text)
        
    except requests.exceptions.RequestException as e:
        st.error(f"セッション方式でエラー: {e}")
        return []
    except Exception as e:
        st.error(f"予期せぬエラー: {e}")
        return []

def fetch_companies_with_proxy_headers(date_str):
    """プロキシ風のヘッダーを追加する方法"""
    headers = get_random_headers()
    # プロキシ経由のように見せかけるヘッダーを追加
    headers.update({
        "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        "X-Real-IP": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        "X-Forwarded-Proto": "https"
    })
    
    url = f"https://www.traders.co.jp/market_jp/earnings_calendar/all/all/1?term={date_str}"
    
    try:
        st.write(f"プロキシヘッダー方式で取得中: {url}")
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        res.encoding = res.apparent_encoding
        
        return parse_companies_from_html(res.text)
        
    except requests.exceptions.RequestException as e:
        st.error(f"プロキシヘッダー方式でエラー: {e}")
        return []
    except Exception as e:
        st.error(f"予期せぬエラー: {e}")
        return []

def parse_companies_from_html(html_content):
    """HTMLから企業情報を解析する共通関数"""
    soup = BeautifulSoup(html_content, "html.parser")
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
        # デバッグ情報を表示
        tables = soup.find_all("table")
        st.write(f"ページ内のテーブル数: {len(tables)}")
        for i, table in enumerate(tables):
            class_attr = table.get('class', [])
            st.write(f"テーブル {i+1}: クラス = {class_attr}")
            rows = table.find_all("tr")[:3]
            for j, row in enumerate(rows):
                st.write(f"   行 {j+1}: {row.get_text(strip=True)[:100]}...")

    unique_companies = list(dict.fromkeys(companies))
    st.write(f"**総件数: {len(unique_companies)} 件**")
    return unique_companies

def fetch_companies_alternative_approach(date_str):
    """代替アプローチ（複数URL試行）"""
    url_patterns = [
        f"https://www.traders.co.jp/market_jp/earnings_calendar/all/all/1?term={date_str}",
        f"https://www.traders.co.jp/market_jp/earnings_calendar?term={date_str}",
        f"https://www.traders.co.jp/market_jp/earnings_calendar/all?term={date_str}",
    ]

    for url in url_patterns:
        try:
            st.write(f"試行中: {url}")
            headers = get_random_headers()
            res = requests.get(url, headers=headers, timeout=15)
            res.raise_for_status()
            res.encoding = res.apparent_encoding
            
            companies = parse_companies_from_html(res.text)
            if companies:
                st.success(f"成功: {url} から {len(companies)} 件取得")
                return companies
            
            time.sleep(random.uniform(1, 3))  # ランダムな待機時間
            
        except Exception as e:
            st.write(f"URL {url} でエラー: {e}")
            continue

    return []

# Streamlit UI
input_date = st.date_input("日付を選択してください")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("通常方式"):
        formatted_date = input_date.strftime("%Y/%m/%d")
        with st.spinner("企業情報を取得中（通常方式）..."):
            companies = fetch_companies_alternative_approach(formatted_date)
        display_results(companies, input_date)

with col2:
    if st.button("セッション方式"):
        formatted_date = input_date.strftime("%Y/%m/%d")
        with st.spinner("企業情報を取得中（セッション方式）..."):
            companies = fetch_companies_with_session(formatted_date)
        display_results(companies, input_date)

with col3:
    if st.button("プロキシヘッダー方式"):
        formatted_date = input_date.strftime("%Y/%m/%d")
        with st.spinner("企業情報を取得中（プロキシヘッダー方式）..."):
            companies = fetch_companies_with_proxy_headers(formatted_date)
        display_results(companies, input_date)

def display_results(companies, input_date):
    """結果表示の共通関数"""
    if companies:
        month = input_date.strftime("%m").lstrip("0")
        day = input_date.strftime("%d").lstrip("0")
        weekday_jp = {"Mon": "月", "Tue": "火", "Wed": "水", "Thu": "木", "Fri": "金", "Sat": "土", "Sun": "日"}
        weekday = weekday_jp[input_date.strftime("%a")]
        display_date = f"{month}/{day}({weekday})"

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
        st.warning("決算予定表が見つかりませんでした。別の方式を試してください。")

# デバッグ情報
st.write("---")
st.write("**デバッグ情報:**")
formatted_date = input_date.strftime("%Y/%m/%d")
st.write(f"選択した日付: {input_date}")
st.write(f"フォーマット後: {formatted_date}")
st.write(f"生成されるURL: https://www.traders.co.jp/market_jp/earnings_calendar/all/all/1?term={formatted_date}")

# 使用上の注意
st.write("---")
st.write("**注意事項:**")
st.write("- Streamlit Cloud環境では403エラーが発生しやすいため、複数の方式を用意しています")
st.write("- セッション方式：事前にトップページにアクセスしてからデータを取得")
st.write("- プロキシヘッダー方式：プロキシ経由のように見せかけるヘッダーを追加")
st.write("- 一つの方式で失敗した場合は、他の方式をお試しください")