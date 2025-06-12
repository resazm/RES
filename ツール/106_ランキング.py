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
    html_text = requests.get(url).text
    result = ''
    for i in range(1, top_n + 1):
        xpaths = [
            f'//*[@id="item"]/div/table/tbody/tr[{i}]/td[1]/ul/li[1]',
            f'//*[@id="item"]/div/table/tbody/tr[{i}]/td[1]/a',
            f'//*[@id="item"]/div/table/tbody/tr[{i}]/td[3]/span[2]/span/span[1]'
        ]
        code, name, rate_raw = search_xpath(html_text, xpaths)
        rate = rate_raw if '%' in rate_raw else f'{rate_raw}%'
        if code and name and rate:
            result += f'{i}位<{code}>{name}({rate})\n'
    return result

def build_yahoo_ranking_html(url, top_n, title):
    html_text = requests.get(url).text
    rows = ''
    for i in range(1, top_n + 1):
        xpaths = [
            f'//*[@id="item"]/div/table/tbody/tr[{i}]/td[1]/ul/li[1]',
            f'//*[@id="item"]/div/table/tbody/tr[{i}]/td[1]/a',
            f'//*[@id="item"]/div/table/tbody/tr[{i}]/td[3]/span[2]/span/span[1]'
        ]
        code, name, rate_raw = search_xpath(html_text, xpaths)
        if not code or not name or not rate_raw:
            continue
        rate = rate_raw if '%' in rate_raw else rate_raw + '%'
        rows += f"<tr>\n<td>{i}位</td>\n<td>{name}</td>\n<td>{code}</td>\n<td>{rate}</td>\n</tr>\n"

    return f"""
<h2 class="widget-title"> {title}</h2>
<p class="date">{get_today_for_wordpress()}</p>
<table class="krank rank_d" style="height: auto;" width="358">
<tbody>
{rows}</tbody>
</table>
"""

def build_kabutan_ranking(url, top_n):
    html_text = requests.get(url).text
    result = ''
    for i in range(1, top_n + 1):
        code_xpath = f'//*[@id="main"]/div[2]/table/tbody/tr[{i}]/td[1]/a'
        name_xpath = f'//*[@id="main"]/div[2]/table/tbody/tr[{i}]/th'
        rate_xpath = f'//*[@id="main"]/div[2]/table/tbody/tr[{i}]/td[8]/span'

        code_html, name, rate_raw = search_xpath(html_text, [code_xpath, name_xpath, rate_xpath])
        match = re.search(r'(\d+)', code_html)
        code = match.group(1) if match else code_html
        rate = rate_raw if '%' in rate_raw else f'{rate_raw}%'
        if code and name and rate:
            result += f'{i}位<{code}>{name}({rate})\n'
    return result

def get_ranking_text():
    date = get_today()
    output = f'★ {date} のランキング （15:30現在）\n└────────────────\n'

    up_url = 'https://finance.yahoo.co.jp/stocks/ranking/up?market=all'
    output += f'\n□ {date} 値上がり率\n\n'
    output += build_yahoo_ranking(up_url, 5)

    down_url = 'https://finance.yahoo.co.jp/stocks/ranking/down?market=all&term=daily'
    output += f'\n□ {date} 値下がり率\n\n'
    output += build_yahoo_ranking(down_url, 5)

    kiyodo_up_url = 'https://kabutan.jp/warning/?mode=8_1&market=0&capitalization=-1&stc=kiyodo&stm=1&col=kiyodo'
    output += f'\n□ {date} 寄与度上位\n\n'
    output += build_kabutan_ranking(kiyodo_up_url, 5)

    kiyodo_down_url = 'https://kabutan.jp/warning/?mode=8_1&market=0&capitalization=-1&stc=kiyodo&stm=0&col=kiyodo'
    output += f'\n□ {date} 寄与度下位\n\n'
    output += build_kabutan_ranking(kiyodo_down_url, 5)

    return output

# ===== Streamlitアプリ部分 =====

st.title("📈 今日の株式ランキング")
st.write("Yahoo!ファイナンスとKabutanから最新のランキングを取得します。")

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
