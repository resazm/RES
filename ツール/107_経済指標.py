import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
from typing import Dict, List, Tuple
import re

class EconomicCalendarScraper:
    def __init__(self):
        self.url = "https://www.gaikaex.com/gaikaex/mark/calendar/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_data(self) -> pd.DataFrame:
        """経済指標データを取得してDataFrameとして返す"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            table = soup.find('table')
            if not table:
                st.error("テーブルが見つかりませんでした")
                return pd.DataFrame()
            
            rows = table.find_all('tr')
            data = []
            current_date = "" 
            
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                
                is_date_row = False
                if cells and cells[0].name == 'td' and (cells[0].has_attr('rowspan') or 'date' in cells[0].get('class', [])):
                    is_date_row = True

                date_idx = 0 
                time_idx = 1 if is_date_row else 0
                country_idx = 2 if is_date_row else 1
                indicator_idx = 3 if is_date_row else 2
                importance_idx = 4 if is_date_row else 3
                forecast_idx = 5 if is_date_row else 4
                result_idx = 6 if is_date_row else 5
                previous_idx = 7 if is_date_row else 6

                expected_min_cells = 8 if is_date_row else 7
                if len(cells) < expected_min_cells:
                    continue 

                if is_date_row:
                    date_cell_text = cells[date_idx].get_text(strip=True)
                    match = re.match(r'(\d+/\d+)\(', date_cell_text)
                    if match:
                        current_date = match.group(1)
                    else:
                        current_date = date_cell_text 

                time_str = cells[time_idx].get_text(strip=True)
                
                country_cell = cells[country_idx]
                country_img = country_cell.find('img')
                if country_img and country_img.get('alt'):
                    country = country_img.get('alt')
                else:
                    country = country_cell.get_text(strip=True)
                
                indicator = cells[indicator_idx].get_text(strip=True)
                
                importance_cell = cells[importance_idx]
                importance_text = importance_cell.get_text(strip=True)
                importance = importance_text.count('★')
                if importance == 0:
                    stars = importance_cell.find_all('span')
                    importance = len([s for s in stars if '★' in s.get_text()])
                
                forecast = cells[forecast_idx].get_text(strip=True)
                result = cells[result_idx].get_text(strip=True)
                previous = cells[previous_idx].get_text(strip=True)
                
                if indicator and indicator.strip() and indicator not in ['*', '--', '休場', '']:
                    data.append({
                        '発表日': current_date, 
                        '時刻': time_str,
                        '国': country,
                        '指標名': indicator,
                        '重要度': importance,
                        '予想': forecast,
                        '結果': result,
                        '前回': previous
                    })
            
            df_result = pd.DataFrame(data)
            if not df_result.empty:
                current_year = datetime.datetime.now().year
                if '発表日' in df_result.columns and pd.api.types.is_string_dtype(df_result['発表日']):
                    df_result['発表日'] = df_result['発表日'].apply(lambda x: f"{current_year}/{x}" if re.match(r'^\d+/\d+$', str(x)) else x)
                df_result['発表日'] = pd.to_datetime(df_result['発表日'], errors='coerce')
            return df_result
            
        except Exception as e:
            st.error(f"データ取得エラー: {str(e)}")
            return pd.DataFrame()

    def classify_country(self, country: str) -> str:
        """国を日本/海外に分類"""
        if country in ['日本', 'Japan']:
            return '日本'
        else:
            return '海外'
            
    def get_country_abbreviation(self, country_name: str) -> str:
        """国名から略称を返す"""
        country_abbr = {
            '日本': '日', 'Japan': '日',
            '米国': '米', 'USA': '米', 'United States': '米',
            'ユーロ': '欧', 'Euro Zone': '欧',
            'イギリス': '英', 'UK': '英', 'United Kingdom': '英',
            'ドイツ': '独', 'Germany': '独',
            'フランス': '仏', 'France': '仏',
            'カナダ': '加', 'Canada': '加',
            'オーストラリア': '豪', 'Australia': '豪',
            'ニュージーランド': 'NZ', 'New Zealand': 'NZ',
            '中国': '中', 'China': '中',
            'スイス': 'スイス',
            '韓国': '韓', 'South Korea': '韓',
            'インド': '印', 'India': '印',
            'ロシア': '露', 'Russia': '露',
            '香港': '香港', 
            '南アフリカ': '南ア', 
            'シンガポール': 'シンガポール',
            'トルコ': 'トルコ'
            # 必要に応じて追加
        }
        return country_abbr.get(country_name, '')

    def get_economic_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """経済指標データを結果発表済み・予定に分けて日本と海外に分類して返す"""
        if df.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
        df['地域'] = df['国'].apply(self.classify_country)
        
        result_data = df[df['結果'].notna() & (df['結果'] != '') & (df['結果'] != '*') & (df['結果'] != '--')].copy()
        scheduled_data = df[~df.index.isin(result_data.index) & 
                           (df['指標名'].notna()) & (df['指標名'] != '') & 
                           (df['指標名'] != '*') & (df['指標名'] != '休場')].copy()
        
        japan_results = result_data[result_data['地域'] == '日本'].copy()
        overseas_results = result_data[result_data['地域'] == '海外'].copy()
        
        japan_scheduled = scheduled_data[scheduled_data['地域'] == '日本'].copy()
        overseas_scheduled = scheduled_data[scheduled_data['地域'] == '海外'].copy()
        
        return japan_results, overseas_results, japan_scheduled, overseas_scheduled

st.set_page_config(
    page_title="経済指標カレンダー",
    page_icon="📊",
    layout="wide"
)

st.title("📊 経済指標カレンダー")
st.markdown("---")

st.header("⚙️ アプリケーション設定")
col_settings1, col_settings2, col_settings3, col_settings4 = st.columns(4)

with col_settings1:
    auto_refresh = st.checkbox("自動更新", value=False)
with col_settings2:
    show_all_data = st.checkbox("全データ表示", value=False)
with col_settings3:
    show_debug = st.checkbox("デバッグ情報表示", value=False)
with col_settings4:
    if st.button("データ更新"):
        st.session_state['force_refresh'] = True
    if 'force_refresh' not in st.session_state:
        st.session_state['force_refresh'] = False

st.markdown("---")

scraper = EconomicCalendarScraper()

@st.cache_data(ttl=3600)
def get_scraped_data():
    return scraper.fetch_data()

if auto_refresh or st.session_state['force_refresh']:
    st.cache_data.clear()
    with st.spinner("データを取得中..."):
        df = get_scraped_data()
    st.session_state['force_refresh'] = False
else:
    df = get_scraped_data()

if df.empty:
    st.warning("データを取得できませんでした。")

if show_debug:
    st.subheader("🔍 デバッグ情報")
    st.write("取得したデータの概要:")
    st.write(f"- 総行数: {len(df)}")
    st.write(f"- 列数: {len(df.columns)}")
    st.write("- 列名:", list(df.columns))
    
    result_mask = df['結果'].notna() & (df['結果'] != '') & (df['結果'] != '*') & (df['結果'] != '--')
    st.write(f"- 結果発表済み行数: {result_mask.sum()}")
    
    country_counts = df['国'].value_counts()
    st.write("- 国別データ数:")
    st.write(country_counts.head(10))
    
    st.write("- データサンプル (最初の5行):")
    st.dataframe(df.head())
    st.markdown("---")

if show_all_data:
    st.subheader("📋 全経済指標データ")
    st.dataframe(df, use_container_width=True)
    st.markdown("---")
    
japan_results, overseas_results, japan_scheduled, overseas_scheduled = scraper.get_economic_data(df)

# --- 指定日付の指標表示セクション (コピー形式に) ---
st.markdown("---")
st.header("🗓️ 日付指定で経済指標を表示 (コピー可能)")

jp_weekdays = ["月", "火", "水", "木", "金", "土", "日"]

if not df.empty and '発表日' in df.columns and not df['発表日'].empty:
    valid_dates = sorted(df['発表日'].dropna().dt.date.unique())
    if valid_dates:
        today = datetime.date.today()
        default_date = next((d for d in valid_dates if d >= today), valid_dates[0])
    else:
        default_date = datetime.date.today()
else:
    default_date = datetime.date.today()

selected_date = st.date_input(
    "表示したい日付を選択してください",
    value=default_date,
    min_value=datetime.date(2020, 1, 1), 
    max_value=datetime.date(datetime.datetime.now().year + 2, 12, 31) 
)

if selected_date:
    daily_data = df[df['発表日'].dt.date == selected_date].copy()
    
    output_text = "" # 出力するテキストを格納する変数
    
    if not daily_data.empty:
        weekday_jp = jp_weekdays[selected_date.weekday()]
        output_text += f"□{str(selected_date.month)}/{str(selected_date.day)}({weekday_jp})重要経済指標\n\n" # 1行空行

        # 日本
        japan_daily = daily_data[daily_data['地域'] == '日本'].sort_values('時刻')
        if not japan_daily.empty:
            output_text += "＜日本＞\n"
            for index, row in japan_daily.iterrows():
                # 時刻が'--:--'の場合は時刻部分を省略
                time_display_jp = f"({row['時刻']})" if row['時刻'] != '--:--' else ""
                output_text += f"(日){row['指標名']}{time_display_jp}\n"
        else:
            output_text += "＜日本＞\nこの日付の日本の経済指標はありません。\n" # 表示メッセージも調整
            
        output_text += "\n" # 1行空行

        # 海外
        overseas_daily = daily_data[daily_data['地域'] == '海外'].sort_values('時刻')
        if not overseas_daily.empty:
            output_text += "＜海外＞\n"
            for index, row in overseas_daily.iterrows():
                country_abbr = scraper.get_country_abbreviation(row['国'])
                # 時刻が'--:--'の場合は時刻部分を省略
                time_display_overseas = f"({row['時刻']})" if row['時刻'] != '--:--' else ""
                output_text += f"({country_abbr}){row['指標名']}{time_display_overseas}\n"
        else:
            output_text += "＜海外＞\nこの日付の海外の経済指標はありません。\n" # 表示メッセージも調整
            
    else:
        output_text = f"{str(selected_date.month)}/{str(selected_date.day)} の経済指標は見つかりませんでした。"

    # st.text_area で表示
    st.code(output_text)



# --- 元々のタブ表示セクション ---
st.markdown("---")
tab1, tab2 = st.tabs(["📊 結果発表済み", "📅 発表予定"])

with tab1:
    st.subheader("結果が発表された経済指標")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🇯🇵 日本")
        if not japan_results.empty:
            japan_sorted = japan_results.sort_values('重要度', ascending=False)
            display_cols = ['発表日', '時刻', '指標名', '重要度', '結果', '予想', '前回']
            st.dataframe(japan_sorted[display_cols], use_container_width=True, hide_index=True)
            st.info(f"日本: {len(japan_results)}件の結果発表")
        else:
            st.info("日本の経済指標結果はありません")
    
    with col2:
        st.subheader("🌍 海外")
        if not overseas_results.empty:
            overseas_sorted = overseas_results.sort_values('重要度', ascending=False)
            display_cols = ['発表日', '時刻', '国', '指標名', '重要度', '結果', '予想', '前回']
            st.dataframe(overseas_sorted[display_cols], use_container_width=True, hide_index=True)
            st.info(f"海外: {len(overseas_results)}件の結果発表")
        else:
            st.info("海外の経済指標結果はありません")

with tab2:
    st.subheader("発表予定の経済指標")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🇯🇵 日本")
        if not japan_scheduled.empty:
            japan_scheduled_sorted = japan_scheduled.sort_values(['発表日', '時刻'])
            display_cols = ['発表日', '時刻', '指標名', '重要度', '予想', '前回']
            st.dataframe(japan_scheduled_sorted[display_cols], use_container_width=True, hide_index=True)
            st.info(f"日本: {len(japan_scheduled)}件の発表予定")
        else:
            st.info("日本の発表予定はありません")
    
    with col2:
        st.subheader("🌍 海外")
        if not overseas_scheduled.empty:
            overseas_scheduled_sorted = overseas_scheduled.sort_values(['発表日', '時刻'])
            display_cols = ['発表日', '時刻', '国', '指標名', '重要度', '予想', '前回']
            st.dataframe(overseas_scheduled_sorted[display_cols], use_container_width=True, hide_index=True)
            st.info(f"海外: {len(overseas_scheduled)}件の発表予定")
        else:
            st.info("海外の発表予定はありません")
    

st.markdown("---")
st.caption(f"最終更新: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if auto_refresh:
    st.rerun()