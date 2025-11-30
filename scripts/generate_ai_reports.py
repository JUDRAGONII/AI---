"""
AI報告生成器腳本
自動生成每日市場分析報告與個股分析
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# 添加ai_clients到path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from ai_clients import get_gemini_client
    import psycopg2
    from psycopg2 import extras
    from dotenv import load_dotenv
except ImportError as e:
    print(f"缺少必要套件: {e}")
    sys.exit(1)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env'))


def get_db():
    """獲取資料庫連接"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '15432')),
        database=os.getenv('DB_NAME', 'quant_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )


def get_market_data():
    """從資料庫獲取市場數據"""
    conn = get_db()
    cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    # 獲取最新黃金價格
    cursor.execute("""
        SELECT close_price, trade_date 
        FROM commodity_prices 
        WHERE commodity_code = 'GOLD' 
        ORDER BY trade_date DESC LIMIT 1
    """)
    gold = cursor.fetchone()
    
    # 獲取最新USD/TWD匯率
    cursor.execute("""
        SELECT rate, trade_date 
        FROM exchange_rates 
        WHERE base_currency = 'USD' AND quote_currency = 'TWD' 
        ORDER BY trade_date DESC LIMIT 1
    """)
    forex = cursor.fetchone()
    
    # 獲取台股數量
    cursor.execute("SELECT COUNT(*) as count FROM tw_stock_info")
    tw_count = cursor.fetchone()['count']
    
    # 獲取美股數量  
    cursor.execute("SELECT COUNT(*) as count FROM us_stock_info")
    us_count = cursor.fetchone()['count']
    
    cursor.close()
    conn.close()
    
    return {
        'gold': float(gold['close_price']) if gold else None,
        'gold_date': str(gold['trade_date']) if gold else None,
        'usdtwd': float(forex['rate']) if forex else None,
        'forex_date': str(forex['trade_date']) if forex else None,
        'tw_stock_count': tw_count,
        'us_stock_count': us_count,
        # 模擬數據（待整合真實API）
        'taiex': 17234,
        'sp500': 4567,
        'nasdaq': 14123,
        'vix': 15.8
    }


def generate_daily_market_report():
    """生成每日市場分析報告"""
    print("=" * 60)
    print("🤖 開始生成每日市場分析報告")
    print("=" * 60)
    
    try:
        # 測試AI連接
        print("1️⃣ 測試AI連接...")
        client = get_gemini_client()
        test_result = client.test_connection()
        
        if test_result['status'] != 'success':
            print(f"❌ AI連接失敗: {test_result.get('message')}")
            return None
        
        print(f"✅ AI連接成功: {test_result.get('model')}")
        
        # 獲取市場數據
        print("\n2️⃣ 獲取市場數據...")
        market_data = get_market_data()
        print(f"✅ 數據獲取完成:")
        print(f"   - 台股: {market_data['tw_stock_count']}支")
        print(f"   - 美股: {market_data['us_stock_count']}支")
        print(f"   - 黃金: ${market_data['gold']}")
        print(f"   - USD/TWD: {market_data['usdtwd']}")
        
        # 生成AI報告
        print("\n3️⃣ 生成AI市場分析...")
        report = client.generate_market_overview(market_data)
        
        # 儲存報告
        report_dir = Path(__file__).parent / 'reports' / 'daily'
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_filename = f"market_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = report_dir / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# 每日市場分析報告\n\n")
            f.write(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"---\n\n")
            f.write(report)
        
        print(f"\n✅ 報告已儲存: {report_path}")
        print(f"\n4️⃣ 報告預覽:")
        print("=" * 60)
        print(report[:500] + "..." if len(report) > 500 else report)
        print("=" * 60)
        
        return {
            'success': True,
            'report_path': str(report_path),
            'report_content': report,
            'market_data': market_data
        }
        
    except Exception as e:
        print(f"\n❌ 報告生成失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def generate_stock_analysis_report(stock_code: str, market: str = 'tw'):
    """生成單一股票深度分析報告"""
    print("=" * 60)
    print(f"🤖 開始生成個股分析報告: {stock_code}")
    print("=" * 60)
    
    try:
        # 測試AI連接
        print("1️⃣ 測試AI連接...")
        client = get_gemini_client()
        
        # 從資料庫獲取股票資訊
        print(f"\n2️⃣ 獲取股票資訊 ({stock_code})...")
        conn = get_db()
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        
        if market == 'tw':
            cursor.execute("SELECT * FROM tw_stock_info WHERE stock_code = %s", (stock_code,))
        else:
            cursor.execute("SELECT * FROM us_stock_info WHERE symbol = %s", (stock_code,))
        
        stock = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not stock:
            print(f"❌ 找不到股票: {stock_code}")
            return None
        
        stock_data = dict(stock)
        print(f"✅ 股票資訊獲取成功: {stock_data.get('stock_name', stock_data.get('company_name'))}")
        
        # 模擬技術指標與因子數據（待整合真實API）
        print("\n3️⃣ 準備分析數據...")
        technical_indicators = {
            'rsi': 58.5,
            'macd': {'macd': 1.25, 'signal': 0.95, 'histogram': 0.30},
            'ma': {'ma20': 580, 'ma60': 575},
            'bollinger': {'upper': 600, 'middle': 580, 'lower': 560}
        }
        
        factor_scores = {
            'value': 75,
            'quality': 82,
            'momentum': 65,
            'growth': 70,
            'size': 90,
            'volatility': 55
        }
        
        # 生成AI分析
        print(f"\n4️⃣ 生成AI深度分析...")
        analysis = client.generate_stock_analysis(stock_data, technical_indicators, factor_scores)
        
        # 儲存報告
        report_dir = Path(__file__).parent / 'reports' / 'stocks'
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_filename = f"stock_analysis_{stock_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = report_dir / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# 個股深度分析報告 - {stock_code}\n\n")
            f.write(f"**股票名稱**: {stock_data.get('stock_name', stock_data.get('company_name'))}\n")
            f.write(f"**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"---\n\n")
            f.write(analysis)
        
        print(f"\n✅ 報告已儲存: {report_path}")
        print(f"\n5️⃣ 報告預覽:")
        print("=" * 60)
        print(analysis[:500] + "..." if len(analysis) > 500 else analysis)
        print("=" * 60)
        
        return {
            'success': True,
            'report_path': str(report_path),
            'report_content': analysis,
            'stock_data': stock_data
        }
        
    except Exception as e:
        print(f"\n❌ 報告生成失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    print("\n🚀 AI報告生成器")
    print("=" * 60)
    
    # 檢查命令列參數
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'market':
            # 生成市場報告
            result = generate_daily_market_report()
        elif command == 'stock':
            # 生成個股報告
            if len(sys.argv) < 3:
                print("用法: python generate_ai_reports.py stock <股票代碼> [市場]")
                sys.exit(1)
            stock_code = sys.argv[2]
            market = sys.argv[3] if len(sys.argv) > 3 else 'tw'
            result = generate_stock_analysis_report(stock_code, market)
        else:
            print(f"未知命令: {command}")
            print("可用命令: market, stock")
            sys.exit(1)
    else:
        # 預設生成市場報告
        print("預設執行: 生成每日市場報告\n")
        result = generate_daily_market_report()
    
    print("\n" + "=" * 60)
    if result and result.get('success'):
        print("✅ 報告生成成功!")
    else:
        print("❌ 報告生成失敗")
    print("=" * 60)
