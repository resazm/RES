# 決算発表予定を取得する代替方法

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time

class EarningsScheduleScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_yahoo_finance_jp_earnings(self, date_str=None):
        """
        Yahoo Finance Japan から決算発表予定を取得
        date_str: 'YYYY-MM-DD' 形式の日付文字列
        """
        try:
            if not date_str:
                date_str = datetime.now().strftime('%Y-%m-%d')
            
            # Yahoo Finance JPの決算カレンダーURL
            url = f"https://finance.yahoo.co.jp/stocks/schedule/?date={date_str}"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 決算発表予定のテーブルを探す
            earnings_data = []
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')[1:]  # ヘッダーをスキップ
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 3:
                        # 銘柄コード、会社名、時間などを抽出
                        stock_info = {
                            'date': date_str,
                            'company': cols[0].get_text(strip=True),
                            'code': cols[1].get_text(strip=True) if len(cols) > 1 else '',
                            'time': cols[2].get_text(strip=True) if len(cols) > 2 else ''
                        }
                        earnings_data.append(stock_info)
            
            return pd.DataFrame(earnings_data)
            
        except Exception as e:
            print(f"Yahoo Finance JPからの取得に失敗: {e}")
            return pd.DataFrame()
    
    def get_traders_web_earnings(self, date_str=None):
        """
        トレーダーズウェブから決算発表予定を取得
        """
        try:
            if not date_str:
                date_str = datetime.now().strftime('%Y%m%d')
            else:
                # YYYY-MM-DD を YYYYMMDD に変換
                date_str = date_str.replace('-', '')
            
            url = f"https://www.traders.co.jp/domestic_stocks/stocks_data/kessan_schedule/kessan_schedule.asp?date={date_str}"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            earnings_data = []
            # テーブル構造に応じて調整が必要
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # ヘッダーをスキップ
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        stock_info = {
                            'date': date_str,
                            'code': cols[0].get_text(strip=True),
                            'company': cols[1].get_text(strip=True),
                            'time': cols[2].get_text(strip=True) if len(cols) > 2 else ''
                        }
                        earnings_data.append(stock_info)
            
            return pd.DataFrame(earnings_data)
            
        except Exception as e:
            print(f"トレーダーズウェブからの取得に失敗: {e}")
            return pd.DataFrame()
    
    def get_earnings_for_date_range(self, start_date, end_date):
        """
        指定期間の決算発表予定を取得
        """
        all_earnings = []
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current_date <= end_date_dt:
            date_str = current_date.strftime('%Y-%m-%d')
            print(f"取得中: {date_str}")
            
            # Yahoo Finance JPから取得
            yahoo_data = self.get_yahoo_finance_jp_earnings(date_str)
            if not yahoo_data.empty:
                yahoo_data['source'] = 'Yahoo Finance JP'
                all_earnings.append(yahoo_data)
            
            # レート制限のため少し待機
            time.sleep(1)
            
            current_date += timedelta(days=1)
        
        if all_earnings:
            return pd.concat(all_earnings, ignore_index=True)
        else:
            return pd.DataFrame()

# 使用例
def main():
    scraper = EarningsScheduleScraper()
    
    # 今日の決算発表予定を取得
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"今日（{today}）の決算発表予定を取得中...")
    
    earnings_today = scraper.get_yahoo_finance_jp_earnings(today)
    
    if not earnings_today.empty:
        print("\n=== 本日の決算発表予定 ===")
        print(earnings_today.to_string(index=False))
        
        # CSVファイルに保存
        filename = f"earnings_schedule_{today.replace('-', '')}.csv"
        earnings_today.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\nデータを {filename} に保存しました")
    else:
        print("データが取得できませんでした")
    
    # 特定の日付範囲で取得する場合
    # start_date = "2024-06-17"
    # end_date = "2024-06-21"
    # weekly_earnings = scraper.get_earnings_for_date_range(start_date, end_date)
    # print(weekly_earnings)

if __name__ == "__main__":
    main()


# APIを使用する方法（推奨）
"""
より安定した方法として、以下のAPIサービスの利用を検討してください：

1. Alpha Vantage API
2. Financial Modeling Prep API
3. Quandl API
4. IEX Cloud API

例：Alpha Vantage を使用した場合
"""

def get_earnings_with_api():
    """
    Alpha Vantage APIを使用した決算情報取得例
    """
    import requests
    
    # APIキーが必要（無料プランあり）
    API_KEY = "YOUR_API_KEY"
    symbol = "7203.T"  # トヨタの例
    
    url = f"https://www.alphavantage.co/query"
    params = {
        'function': 'EARNINGS_CALENDAR',
        'symbol': symbol,
        'apikey': API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data
    except Exception as e:
        print(f"API取得エラー: {e}")
        return None

# 必要なライブラリのインストール
"""
pip install requests beautifulsoup4 pandas lxml
"""