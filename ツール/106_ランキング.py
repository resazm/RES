import streamlit as st
import requests
from lxml import html
import datetime
import re

# ===== ヘルパー関数 =====
st.set_page_config(layout="wide")


def get_today():
    now = datetime.datetime.now()
    w = ['月', '火', '水', '木', '金', '土', '日'][now.weekday()]
    return f"{now.month}/{now.day}({w})"

def get_today_for_wordpress():
    now = datetime.datetime.now()
    y, m, d = now.year, now.month, now.day
    return f"{y}/{m:02d}/{d:02d} 15:30時点"

def search_xpath(html_text, xpath_list):
    tree = html.fromstring(html_text)
    results = []
    for xp in xpath_list:
        elements = tree.xpath(xp)
        if not elements:
            results.append('')
            continue
        el = elements[0]
        if isinstance(el, str):
            results.append(el.strip())
        else:
            results.append(el.text_content().strip())
    return results

def build_yahoo_ranking(url, top_n):
    """Yahoo!ファイナンスのランキングを取得（新HTML構造対応）"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    tree = html.fromstring(response.text)
    
    result = ''
    
    # tbody内のtr要素を取得
    rows = tree.xpath('//tbody/tr')
    
    for i in range(min(top_n, len(rows))):
        row = rows[i]
        
        # 銘柄名（最初のtd内のaタグ）
        name_elements = row.xpath('.//td[1]//a/text()')
        name = name_elements[0].strip() if name_elements else ''
        
        # コード（最初のtd内のliタグ）
        code_elements = row.xpath('.//td[1]//li/text()')
        code = code_elements[0].strip() if code_elements else ''
        
        # 騰落率（3番目のtd内の2つ目のStyledNumber__value__3rXW）
        rate_elements = row.xpath('.//td[3]//span[@class="StyledNumber__value__3rXW"]/text()')
        if len(rate_elements) >= 2:
            rate_text = rate_elements[1].strip()
            # %記号の確認
            has_percent = row.xpath('.//td[3]//span[@class="StyledNumber__suffix__2SD5" and text()="%"]')
            rate = f"{rate_text}%" if has_percent else rate_text
        else:
            rate = ''
        
        if code and name and rate:
            result += f'{i + 1}位<{code}>{name}({rate})\n'
    
    return result

def build_yahoo_ranking_html(url, top_n, title):
    """Yahoo!ファイナンスのランキングをHTML形式で取得（新HTML構造対応）"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    tree = html.fromstring(response.text)
    
    rows_html = ''
    
    # tbody内のtr要素を取得
    rows = tree.xpath('//tbody/tr')
    
    for i in range(min(top_n, len(rows))):
        row = rows[i]
        
        # 銘柄名（最初のtd内のaタグ）
        name_elements = row.xpath('.//td[1]//a/text()')
        name = name_elements[0].strip() if name_elements else ''
        
        # コード（最初のtd内のliタグ）
        code_elements = row.xpath('.//td[1]//li/text()')
        code = code_elements[0].strip() if code_elements else ''
        
        # 騰落率（3番目のtd内の2つ目のStyledNumber__value__3rXW）
        rate_elements = row.xpath('.//td[3]//span[@class="StyledNumber__value__3rXW"]/text()')
        if len(rate_elements) >= 2:
            rate_text = rate_elements[1].strip()
            # %記号の確認
            has_percent = row.xpath('.//td[3]//span[@class="StyledNumber__suffix__2SD5" and text()="%"]')
            rate = f"{rate_text}%" if has_percent else rate_text
        else:
            rate = ''
        
        if code and name and rate:
            rows_html += f"<tr>\n<td>{i + 1}位</td>\n<td>{name}</td>\n<td>{code}</td>\n<td>{rate}</td>\n</tr>\n"

    return f"""
<h2 class="widget-title"> {title}</h2>
<p class="date">{get_today_for_wordpress()}</p>
<table class="krank rank_d" style="height: auto;" width="358">
<tbody>
{rows_html}</tbody>
</table>
"""

def build_minkabu_contribution(url, div_index, top_n):
    """みんかぶの寄与度ランキングを取得"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    tree = html.fromstring(response.text)
    
    result = ''
    
    # div[1]が寄与度上位、div[2]が寄与度下位
    # tr[1]はヘッダーなので、tr[2]から開始
    for i in range(2, top_n + 2):
        # XPath作成
        code_xpath = f'//*[@id="contribution_content"]/div[1]/div[{div_index}]/div[2]/table/tbody/tr[{i}]/td[1]/div[1]'
        name_xpath = f'//*[@id="contribution_content"]/div[1]/div[{div_index}]/div[2]/table/tbody/tr[{i}]/td[1]/div[2]/a'
        contrib_xpath = f'//*[@id="contribution_content"]/div[1]/div[{div_index}]/div[2]/table/tbody/tr[{i}]/td[3]/div[2]/span'
        
        code_elements = tree.xpath(code_xpath)
        name_elements = tree.xpath(name_xpath)
        contrib_elements = tree.xpath(contrib_xpath)
        
        code = code_elements[0].text_content().strip().replace(' ', '') if code_elements else ''
        name = name_elements[0].text_content().strip() if name_elements else ''
        contribution = contrib_elements[0].text_content().strip() if contrib_elements else ''
        
        # 括弧が既にある場合は削除
        if contribution.startswith('(') and contribution.endswith(')'):
            contribution = contribution[1:-1]
        
        if code and name and contribution:
            result += f'{i - 1}位<{code}>{name}({contribution})\n'
    
    return result

def get_ranking_text():
    date = get_today()
    output = f'★{date} のランキング （15:30現在）\n└────────────────\n'

    up_url = 'https://finance.yahoo.co.jp/stocks/ranking/up?market=all'
    output += f'\n□{date} 値上がり率\n\n'
    output += build_yahoo_ranking(up_url, 5)

    down_url = 'https://finance.yahoo.co.jp/stocks/ranking/down?market=all&term=daily'
    output += f'\n□{date} 値下がり率\n\n'
    output += build_yahoo_ranking(down_url, 5)

    # みんかぶの寄与度ランキング
    contrib_url = 'https://fu.minkabu.jp/chart/nikkei225/contribution'
    output += f'\n□{date} 寄与度上位\n\n'
    output += build_minkabu_contribution(contrib_url, 1, 5)

    output += f'\n□{date} 寄与度下位\n\n'
    output += build_minkabu_contribution(contrib_url, 2, 5)

    return output

# ===== Streamlitアプリ部分 =====

st.title("📈 今日の株式ランキング")
st.write("Yahoo!ファイナンスとみんかぶから最新のランキングを取得します。")

generate_html = st.checkbox("📄 WordPress用HTMLも生成する")

if st.button("🔍 ランキングを取得"):
    with st.spinner("データを取得中..."):
        try:
            ranking_text = get_ranking_text()

            # 2列レイアウト
            left_col, right_col = st.columns(2)

            with left_col:
                st.success("テキスト形式のランキング（5位まで）")
                st.code(ranking_text)

            if generate_html:
                up_url = 'https://finance.yahoo.co.jp/stocks/ranking/up?market=all'
                down_url = 'https://finance.yahoo.co.jp/stocks/ranking/down?market=all&term=daily'
                up_html = build_yahoo_ranking_html(up_url, 3, '値上がり率ランキング')
                down_html = build_yahoo_ranking_html(down_url, 3, '値下がり率ランキング')

                with right_col:
                    st.success("HTML形式ランキング（3位まで）")
                    st.subheader("📈 値上がり率ランキング HTML")
                    st.code(up_html, language='html')
                    st.subheader("📉 値下がり率ランキング HTML")
                    st.code(down_html, language='html')

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")