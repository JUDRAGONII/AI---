"""
金融新聞 API 客戶端
資料來源：Alpha Vantage News、Marketaux
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from api_clients.base_client import BaseAPIClient
from config.settings import API_KEYS
from loguru import logger


class NewsClient(BaseAPIClient):
    """金融新聞客戶端"""
    
    def __init__(self):
        super().__init__(
            api_name="金融新聞",
            api_key=API_KEYS.get('alpha_vantage'),
            base_url="https://www.alphavantage.co/query",
            rate_limit_delay=12,  # Alpha Vantage: 5 req/min
            daily_limit=500,
            cache_ttl=3600
        )
        
        self.marketaux_key = API_KEYS.get('marketaux')
    
    def get_news(
        self,
        topics: Optional[List[str]] = None,
        tickers: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        取得金融新聞
        
        Args:
            topics: 主題清單（如 ['technology', 'finance']）
            tickers: 股票代碼清單
            limit: 返回數量上限
        
        Returns:
            新聞清單
        """
        if not self.api_key:
            logger.error("未設定 Alpha Vantage API 金鑰")
            return []
        
        logger.info(f"取得金融新聞（limit={limit}）...")
        
        try:
            params = {
                'function': 'NEWS_SENTIMENT',
                'apikey': self.api_key,
                'limit': limit
            }
            
            if topics:
                params['topics'] = ','.join(topics)
            
            if tickers:
                params['tickers'] = ','.join(tickers)
            
            data = self.get(self.base_url, params=params)
            
            if data and 'feed' in data:
                news_items = []
                
                for item in data['feed'][:limit]:
                    # 解析情緒分數
                    sentiment_score = 0.0
                    if 'overall_sentiment_score' in item:
                        sentiment_score = float(item['overall_sentiment_score'])
                    
                    # 提取相關股票
                    related_symbols = []
                    if 'ticker_sentiment' in item:
                        related_symbols = [t['ticker'] for t in item['ticker_sentiment']]
                    
                    # 解析日期
                    pub_date = item.get('time_published', '')
                    try:
                        if pub_date:
                            dt = datetime.strptime(pub_date, '%Y%m%dT%H%M%S')
                            pub_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        pass

                    news_items.append({
                        'news_id': item.get('url', '')[:100],  # 使用 URL 作為 ID
                        'title': item.get('title', ''),
                        'content': item.get('summary', ''),
                        'source': item.get('source', ''),
                        'url': item.get('url', ''),
                        'published_at': pub_date,
                        'sentiment_score': sentiment_score,
                        'related_symbols': related_symbols,
                        'categories': item.get('topics', []),
                        'language': 'en'
                    })
                
                logger.success(f"成功取得 {len(news_items)} 則新聞")
                return news_items
                
        except Exception as e:
            logger.error(f"取得新聞失敗: {e}")
        
        return []
    
    def get_stock_news(self, symbol: str, limit: int = 20) -> List[Dict]:
        """
        取得特定股票的新聞
        
        Args:
            symbol: 股票代碼
            limit: 返回數量
        
        Returns:
            新聞清單
        """
        logger.info(f"取得 {symbol} 相關新聞...")
        return self.get_news(tickers=[symbol], limit=limit)
    
    def get_market_news(self, limit: int = 50) -> List[Dict]:
        """
        取得市場綜合新聞
       
        Args:
            limit: 返回數量
        
        Returns:
            新聞清單
        """
        logger.info("取得市場綜合新聞...")
        topics = ['financial_markets', 'economy_macro', 'technology']
        return self.get_news(topics=topics, limit=limit)


if __name__ == '__main__':
    client = NewsClient()
    
    # 測試取得市場新聞
    news = client.get_market_news(limit=10)
    for item in news[:3]:
        print(f"\n標題: {item['title']}")
        print(f"情緒: {item['sentiment_score']}")
        print(f"相關股票: {item['related_symbols']}")
