"""
系統配置設定
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 載入環境變數
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# 專案根目錄
BASE_DIR = Path(__file__).parent.parent

# ==========================================
# 資料庫設定
# ==========================================
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 15432,  # 強制使用 15432
    'database': 'financial_data',
    'user': 'postgres',
    'password': '0824-003-a-8-Po', # 強制使用新密碼
}

# 資料庫連線字串
DATABASE_URL = f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"

# ==========================================
# API 金鑰設定
# ==========================================
API_KEYS = {
    'alpha_vantage': os.getenv('ALPHA_VANTAGE_API_KEY', ''),
    'fred': os.getenv('FRED_API_KEY', ''),
    'gold_api': os.getenv('GOLD_API_KEY', ''),
    'exchange_rate': os.getenv('EXCHANGE_RATE_API_KEY', ''),
    'tiingo': os.getenv('TIINGO_API_KEY', ''),
    'marketaux': os.getenv('MARKETAUX_API_KEY', ''),
    'gemini': os.getenv('GEMINI_API_KEY', ''),
    'finnhub': os.getenv('FINNHUB_API_KEY', ''),
    'fmp': os.getenv('FMP_API_KEY', ''),
}

# ==========================================
# API 限流設定
# ==========================================
API_RATE_LIMITS = {
    'twstock': {'delay': 0.5, 'daily_limit': None},
    'yfinance': {'delay': 0.2, 'daily_limit': None},
    'alpha_vantage': {'delay': 12, 'daily_limit': 500},   # 5 req/min
    'gold_api': {'delay': 900, 'daily_limit': 100},        # 100 req/month
    'exchange_rate_api': {'delay': 60, 'daily_limit': 1500},  # 1500 req/month
    'fred': {'delay': 0.5, 'daily_limit': None},
    'marketaux': {'delay': 90, 'daily_limit': 1000},       # 1000 req/month
    'tiingo': {'delay': 1.0, 'daily_limit': None},
    'finnhub': {'delay': 1.0, 'daily_limit': 60},          # 60 calls/minute (free tier)
    'fmp': {'delay': 0.3, 'daily_limit': 250},             # 250 calls/day (free tier)
}

# ==========================================
# 資料回溯設定
# ==========================================
BACKFILL_CONFIG = {
    'batch_size': int(os.getenv('BACKFILL_BATCH_SIZE', 500)),
    'parallel_workers': int(os.getenv('BACKFILL_PARALLEL_WORKERS', 3)),
    'start_dates': {
        'tw_stock': os.getenv('TW_STOCK_START_DATE', '1990-01-01'),
        'us_stock': os.getenv('US_STOCK_START_DATE', '1970-01-01'),
        'gold': os.getenv('GOLD_START_DATE', '1968-01-01'),
        'exchange_rate': os.getenv('EXCHANGE_RATE_START_DATE', '1990-01-01'),
        'macro': os.getenv('MACRO_START_DATE', '1960-01-01'),
        'news': os.getenv('NEWS_START_DATE', '2023-01-01'),
    }
}

# 分階段回溯策略
BACKFILL_PHASES = [
    {
        'name': 'Phase 1 - Foundation Data',
        'sources': [
            {'type': 'gold', 'start_date': BACKFILL_CONFIG['start_dates']['gold']},
            {'type': 'exchange_rate', 'pairs': ['TWD/USD'], 'start_date': BACKFILL_CONFIG['start_dates']['exchange_rate']},
        ],
        'estimated_days': 3,
        'priority': 0
    },
    {
        'name': 'Phase 2 - Macroeconomic Data',
        'sources': [
            {'type': 'macro', 'indicators': ['GDP', 'CPI', 'UNEMPLOYMENT', 'INTEREST_RATE'], 'start_date': BACKFILL_CONFIG['start_dates']['macro']},
        ],
        'estimated_days': 5,
        'priority': 1
    },
    {
        'name': 'Phase 3 - Taiwan Stocks',
        'sources': [
            {'type': 'taiwan_stock', 'priority': 'top_100', 'start_date': BACKFILL_CONFIG['start_dates']['tw_stock']},
            {'type': 'taiwan_stock', 'priority': 'all', 'start_date': BACKFILL_CONFIG['start_dates']['tw_stock']},
        ],
        'estimated_days': 14,
        'priority': 1
    },
    {
        'name': 'Phase 4 - US Stocks',
        'sources': [
            {'type': 'us_stock', 'list': 'SP500', 'start_date': BACKFILL_CONFIG['start_dates']['us_stock']},
            {'type': 'us_stock', 'list': 'NASDAQ100', 'start_date': '1985-01-01'},
        ],
        'estimated_days': 45,
        'priority': 2
    },
    {
        'name': 'Phase 5 - Financial News',
        'sources': [
            {'type': 'news', 'start_date': BACKFILL_CONFIG['start_dates']['news']},
        ],
        'estimated_days': 2,
        'priority': 3
    }
]

# ==========================================
# 計算排程設定
# ==========================================
CALCULATION_SCHEDULE = {
    'technical_indicators': {
        'hour': int(os.getenv('TECH_INDICATORS_SCHEDULE_HOUR', 17)),
        'minute': int(os.getenv('TECH_INDICATORS_SCHEDULE_MINUTE', 30)),
        'enabled': True
    },
    'quant_factors': {
        'hour': int(os.getenv('QUANT_FACTORS_SCHEDULE_HOUR', 18)),
        'minute': int(os.getenv('QUANT_FACTORS_SCHEDULE_MINUTE', 0)),
        'enabled': True
    },
    'portfolio_performance': {
        'hour': 18,
        'minute': 30,
        'enabled': True
    }
}

# ==========================================
# 日誌設定
# ==========================================
LOG_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'file': os.getenv('LOG_FILE', 'logs/financial_db.log'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# 確保日誌目錄存在
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# ==========================================
# AI 設定
# ==========================================
AI_CONFIG = {
    'report_cache_days': int(os.getenv('AI_REPORT_CACHE_DAYS', 7)),
    'model_version': 'gemini-2.5-pro',
}

# ==========================================
# 其他設定
# ==========================================
# 台股市場代碼
TW_MARKET_CODES = {
    'TWSE': '上市',
    'TPEX': '上櫃'
}

# 美股交易所代碼
US_EXCHANGES = {
    'NYSE': '紐約證券交易所',
    'NASDAQ': '納斯達克'
}

# 支援的貨幣對
SUPPORTED_CURRENCY_PAIRS = [
    'TWD/USD',
    'EUR/USD',
    'GBP/USD',
    'JPY/USD',
    'CNY/USD'
]

# 宏觀經濟指標代碼對應
MACRO_INDICATORS = {
    'GDP': 'Gross Domestic Product',
    'CPI': 'Consumer Price Index',
    'UNEMPLOYMENT': 'Unemployment Rate',
    'INTEREST_RATE': 'Interest Rate',
    'PPI': 'Producer Price Index',
    'RETAIL_SALES': 'Retail Sales'
}
