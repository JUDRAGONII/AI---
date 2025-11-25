"""
全面 API 驗證腳本（增強版）
測試所有資料來源的 API 是否可用，包含 Finnhub 和 FMP
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加專案根目錄
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import API_KEYS
from loguru import logger

# 配置簡化日誌
logger.remove()
logger.add(sys.stdout, format="<level>{message}</level>", level="INFO")

def test_fred_api():
    """測試 FRED API (宏觀經濟)"""
    print("\n" + "="*80)
    print("📊 測試 FRED API (宏觀經濟資料)")
    print("="*80)
    
    api_key = API_KEYS.get('fred', '')
    
    if not api_key:
        print("❌ 未設定 FRED_API_KEY")
        return False
    
    print(f"✓ API Key 已設定: {api_key[:10]}...")
    
    try:
        from fredapi import Fred
        print("✓ fredapi 套件已安裝")
        
        fred = Fred(api_key=api_key)
        
        # 測試取得 GDP 資料
        print("📡 測試取得 GDP 資料...")
        data = fred.get_series('GDP', observation_start='2023-01-01', observation_end='2024-01-01')
        
        if not data.empty:
            print(f"✅ FRED API 可用！成功取得 {len(data)} 筆 GDP 資料")
            print(f"   最新資料: {data.index[-1]} = {data.iloc[-1]}")
            return True
        else:
            print("⚠️ API 回應為空")
            return False
            
    except ImportError:
        print("❌ fredapi 套件未安裝")
        print("   請執行: pip install fredapi")
        return False
    except Exception as e:
        print(f"❌ FRED API 測試失敗: {e}")
        return False

def test_alpha_vantage_api():
    """測試 Alpha Vantage API (新聞)"""
    print("\n" + "="*80)
    print("📰 測試 Alpha Vantage API (金融新聞)")
    print("="*80)
    
    api_key = API_KEYS.get('alpha_vantage', '')
    
    if not api_key:
        print("❌ 未設定 ALPHA_VANTAGE_API_KEY")
        return False
    
    print(f"✓ API Key 已設定: {api_key[:10]}...")
    
    try:
        import requests
        
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'NEWS_SENTIMENT',
            'apikey': api_key,
            'limit': 5
        }
        
        print("📡 測試取得新聞資料...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'feed' in data and len(data['feed']) > 0:
                print(f"✅ Alpha Vantage API 可用！成功取得 {len(data['feed'])} 則新聞")
                print(f"   最新新聞: {data['feed'][0].get('title', 'N/A')[:60]}...")
                return True
            else:
                print(f"⚠️ API 回應異常: {data}")
                return False
        else:
            print(f"❌ HTTP 錯誤: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Alpha Vantage API 測試失敗: {e}")
        return False

def test_yfinance():
    """測試 yfinance (免費，不需要 Key)"""
    print("\n" + "="*80)
    print("💰 測試 yfinance (黃金、匯率、股票)")
    print("="*80)
    
    try:
        import yfinance as yf
        print("✓ yfinance 套件已安裝")
        
        # 測試黃金
        print("📡 測試取得黃金價格 (GLD)...")
        ticker = yf.Ticker("GLD")
        hist = ticker.history(period="5d")
        
        if not hist.empty:
            print(f"✅ yfinance 可用！成功取得 {len(hist)} 筆黃金資料")
            print(f"   最新收盤價: ${hist['Close'].iloc[-1]:.2f}")
            
            # 測試台幣匯率
            print("📡 測試取得匯率 (TWD=X)...")
            ticker = yf.Ticker("TWD=X")
            hist = ticker.history(period="5d")
            
            if not hist.empty:
                print(f"✅ 匯率資料可用！USD/TWD = {hist['Close'].iloc[-1]:.4f}")
            
            return True
        else:
            print("⚠️ yfinance 回應為空")
            return False
            
    except ImportError:
        print("❌ yfinance 套件未安裝")
        print("   請執行: pip install yfinance")
        return False
    except Exception as e:
        print(f"❌ yfinance 測試失敗: {e}")
        return False

def test_tiingo_api():
    """測試 Tiingo API (美股)"""
    print("\n" + "="*80)
    print("📈 測試 Tiingo API (美股資料)")
    print("="*80)
    
    api_key = API_KEYS.get('tiingo', '')
    
    if not api_key:
        print("⚠️ 未設定 TIINGO_API_KEY (可選，有 yfinance 備援)")
        return None
    
    print(f"✓ API Key 已設定: {api_key[:10]}...")
    
    try:
        import requests
        
        url = "https://api.tiingo.com/tiingo/daily/AAPL/prices"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {api_key}'
        }
        params = {
            'startDate': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        }
        
        print("📡 測試取得 AAPL 股價...")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                print(f"✅ Tiingo API 可用！成功取得 {len(data)} 筆資料")
                print(f"   最新收盤價: ${data[-1]['close']:.2f}")
                return True
            else:
                print("⚠️ API 回應為空")
                return False
        else:
            print(f"❌ HTTP 錯誤: {response.status_code}")
            print(f"   回應: {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"❌ Tiingo API 測試失敗: {e}")
        return False

def test_finnhub_api():
    """測試 Finnhub API (股票、新聞)"""
    print("\n" + "="*80)
    print("📊 測試 Finnhub API (股票、新聞、財報)")
    print("="*80)
    
    api_key = API_KEYS.get('finnhub', '')
    
    if not api_key:
        print("⚠️ 未設定 FINNHUB_API_KEY (可選)")
        return None
    
    print(f"✓ API Key 已設定: {api_key[:10]}...")
    
    try:
        import requests
        
        # 測試取得股票報價
        url = "https://finnhub.io/api/v1/quote"
        params = {
            'symbol': 'AAPL',
            'token': api_key
        }
        
        print("📡 測試取得 AAPL 即時報價...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'c' in data and data['c'] > 0:  # 'c' 是當前價格
                print(f"✅ Finnhub API 可用！")
                print(f"   當前價格: ${data['c']:.2f}")
                print(f"   今日變化: {data.get('dp', 0):.2f}%")
                return True
            else:
                print(f"⚠️ API 回應異常: {data}")
                return False
        else:
            print(f"❌ HTTP 錯誤: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Finnhub API 測試失敗: {e}")
        return False

def test_fmp_api():
    """測試 FMP API (財報資料)"""
    print("\n" + "="*80)
    print("💼 測試 FMP API (財報、股票資料)")
    print("="*80)
    
    api_key = API_KEYS.get('fmp', '')
    
    if not api_key:
        print("⚠️ 未設定 FMP_API_KEY (可選)")
        return None
    
    print(f"✓ API Key 已設定: {api_key[:10]}...")
    
    try:
        import requests
        
        # 測試取得股票報價
        url = f"https://financialmodelingprep.com/api/v3/quote/AAPL"
        params = {
            'apikey': api_key
        }
        
        print("📡 測試取得 AAPL 報價...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                quote = data[0]
                print(f"✅ FMP API 可用！")
                print(f"   當前價格: ${quote.get('price', 0):.2f}")
                print(f"   市值: ${quote.get('marketCap', 0):,.0f}")
                return True
            else:
                print(f"⚠️ API 回應異常: {data}")
                return False
        else:
            print(f"❌ HTTP 錯誤: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FMP API 測試失敗: {e}")
        return False

def test_twstock():
    """測試 twstock (台股，免費)"""
    print("\n" + "="*80)
    print("🇹🇼 測試 twstock (台股資料)")
    print("="*80)
    
    try:
        import twstock
        print("✓ twstock 套件已安裝")
        
        print("📡 測試取得台積電 (2330) 資料...")
        stock = twstock.Stock('2330')
        
        # 取得最近一個月資料
        now = datetime.now()
        data = stock.fetch(now.year, now.month)
        
        if data and len(data) > 0:
            print(f"✅ twstock 可用！成功取得 {len(data)} 筆資料")
            print(f"   最新收盤價: NT${data[-1].close}")
            return True
        else:
            print("⚠️ twstock 回應為空")
            return False
            
    except ImportError:
        print("⚠️ twstock 套件未安裝 (可選，有 yfinance 備援)")
        print("   可執行: pip install twstock")
        return None
    except Exception as e:
        print(f"❌ twstock 測試失敗: {e}")
        return False

def main():
    """執行所有 API 測試"""
    print("\n" + "🔍 開始驗證所有 API..." + "\n")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # 測試各個 API
    results['FRED (宏觀經濟)'] = test_fred_api()
    results['Alpha Vantage (新聞)'] = test_alpha_vantage_api()
    results['yfinance (黃金/匯率/股票)'] = test_yfinance()
    results['Tiingo (美股)'] = test_tiingo_api()
    results['Finnhub (股票/新聞)'] = test_finnhub_api()
    results['FMP (財報/股票)'] = test_fmp_api()
    results['twstock (台股)'] = test_twstock()
    
    # 總結報告
    print("\n" + "="*80)
    print("📋 API 驗證總結")
    print("="*80)
    
    available = 0
    unavailable = 0
    optional = 0
    
    for name, status in results.items():
        if status is True:
            print(f"✅ {name:<35} 可用")
            available += 1
        elif status is False:
            print(f"❌ {name:<35} 不可用")
            unavailable += 1
        else:  # None
            print(f"⚠️  {name:<35} 未設定 (可選)")
            optional += 1
    
    print("\n" + "-"*80)
    print(f"總計: {available} 可用 | {unavailable} 不可用 | {optional} 可選")
    
    # 建議
    print("\n💡 建議:")
    if unavailable > 0:
        print("   請檢查以下項目:")
        print("   1. 確認 config/.env 檔案中的 API Keys 是否正確")
        print("   2. 確認必要的 Python 套件已安裝 (pip install -r requirements.txt)")
        print("   3. 確認 API Keys 是否有效且未過期")
    else:
        print("   ✨ 所有必要的 API 都已正常運作！")
    
    print("\n")

if __name__ == '__main__':
    main()
