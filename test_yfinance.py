"""
測試 yfinance 是否可用
"""
import yfinance as yf
from loguru import logger

logger.info("測試 yfinance...")

try:
    # 測試黃金 (GLD)
    logger.info("下載 GLD 資料...")
    ticker = yf.Ticker("GLD")
    df = ticker.history(period="1mo")
    if not df.empty:
        logger.success(f"GLD 下載成功: {len(df)} 筆")
        print(df.head())
    else:
        logger.error("GLD 下載失敗: 資料為空")

    # 測試匯率 (TWD=X)
    logger.info("下載 TWD=X 資料...")
    ticker = yf.Ticker("TWD=X")
    df = ticker.history(period="1mo")
    if not df.empty:
        logger.success(f"TWD=X 下載成功: {len(df)} 筆")
        print(df.head())
    else:
        logger.error("TWD=X 下載失敗: 資料為空")

except Exception as e:
    logger.error(f"yfinance 測試失敗: {e}")
