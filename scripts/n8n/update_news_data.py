"""
N8N 自動化腳本 - 金融新聞爬蟲與摘要
用於每日定期執行 (例如每 4 小時)，更新最新市場新聞
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from loguru import logger
import time

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from api_clients.news_client import NewsClient
from data_loader import DatabaseConnector

def update_news_data():
    """更新金融新聞數據"""
    
    logger.info("=" * 60)
    logger.info("🚀 [N8N] 開始執行金融新聞更新")
    logger.info("=" * 60)
    
    db = DatabaseConnector()
    client = NewsClient()
    
    try:
        # 0. 確保新聞表存在
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS financial_news (
                id SERIAL PRIMARY KEY,
                news_id VARCHAR(255) UNIQUE,
                title TEXT,
                content TEXT,
                source VARCHAR(100),
                url TEXT,
                published_at TIMESTAMP,
                sentiment_score FLOAT,
                related_symbols TEXT[],
                categories TEXT[],
                market VARCHAR(10) DEFAULT 'GLOBAL',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_news_published_at ON financial_news(published_at DESC);
            CREATE INDEX IF NOT EXISTS idx_news_related_symbols ON financial_news USING GIN (related_symbols);
        """)
        
        # 1. 獲取市場焦點新聞
        logger.info("📰 獲取市場焦點新聞...")
        market_news = client.get_market_news(limit=20)
        
        # 2. 獲取重點持股新聞
        logger.info("🔍 獲取重點持股新聞...")
        # 這裡只抓最重要的幾檔，避免 API 額度耗盡 (Alpha Vantage 限制)
        key_stocks = ['AAPL', 'NVDA', 'TSLA', '2330', '2454'] 
        stock_news = []
        
        # 為了節省額度，這裡隨機選 2 檔或輪詢 (簡單起見，這次只抓前 2 檔 + TSMC)
        target_stocks = ['2330', 'AAPL']
        
        for symbol in target_stocks:
            try:
                news = client.get_stock_news(symbol, limit=5)
                stock_news.extend(news)
                time.sleep(12) # Alpha Vantage 5 req/min => 12s interval
            except Exception as e:
                logger.error(f"獲取 {symbol} 新聞失敗: {e}")
        
        # 合併新聞 (去重在 DB 層處理)
        all_news = market_news + stock_news
        
        logger.info(f"📋 共獲取 {len(all_news)} 則新聞，準備寫入資料庫...")
        
        # 3. 寫入資料庫
        inserted_count = 0
        skipped_count = 0
        
        for item in all_news:
            try:
                # 處理 list 轉 array string
                # related_symbols 是 list
                
                query = """
                    INSERT INTO financial_news 
                    (news_id, title, content, source, url, published_at, sentiment_score, related_symbols, categories, market)
                    VALUES (%(news_id)s, %(title)s, %(content)s, %(source)s, %(url)s, %(published_at)s, %(sentiment_score)s, %(related_symbols)s, %(categories)s, %(market)s)
                    ON CONFLICT (news_id) DO NOTHING
                """
                
                # 簡單判斷市場
                market = 'GLOBAL'
                symbols = item.get('related_symbols', [])
                if any('.TW' in s or s in ['2330', '2454'] for s in symbols):
                    market = 'TW'
                elif any(s in ['AAPL', 'NVDA', 'SPY'] for s in symbols):
                    market = 'US'
                
                params = {
                    'news_id': item['news_id'],
                    'title': item['title'],
                    'content': item['content'],
                    'source': item['source'],
                    'url': item['url'],
                    'published_at': item['published_at'],
                    'sentiment_score': item['sentiment_score'],
                    'related_symbols': list(set(item['related_symbols'])), # 去重
                    'categories': item.get('categories', []),
                    'market': market
                }
                
                # Execute singly to separate errors? Or batch?
                # Using execute_batch would be faster but single is safer for error counting
                # Given volume is small (<50), single is fine.
                
                # But DatabaseConnector usually expose execute_query.
                # psycopg2 params adaptation handles list -> array.
                
                db.execute_query(query, params)
                inserted_count += 1
                
            except Exception as e:
                # 可能是重複鍵或其他錯誤 (但用了 ON CONFLICT DO NOTHING)
                # logger.warning(f"寫入新聞失敗: {e}")
                skipped_count += 1
        
        logger.info("=" * 60)
        logger.info("📊 新聞更新統計")
        logger.info(f"   獲取總數: {len(all_news)}")
        logger.info(f"   成功處理: {inserted_count}") # 注意：這裡其實不算真正的 'inserted' 數量，因為 execute_query 不回傳受影響行數
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 腳本執行失敗: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == '__main__':
    update_news_data()
