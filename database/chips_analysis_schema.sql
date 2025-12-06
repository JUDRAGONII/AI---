-- 籌碼分析資料庫擴展 Schema
-- 建立三大法人與融資融券相關表格

-- 1. 三大法人買賣超記錄表
CREATE TABLE IF NOT EXISTS institutional_trades (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    foreign_buy BIGINT DEFAULT 0,        -- 外資買進張數
    foreign_sell BIGINT DEFAULT 0,       -- 外資賣出張數
    foreign_net BIGINT,                  -- 外資買賣超（計算欄位）
    trust_buy BIGINT DEFAULT 0,          -- 投信買進張數
    trust_sell BIGINT DEFAULT 0,         -- 投信賣出張數
    trust_net BIGINT,                    -- 投信買賣超
    dealer_buy BIGINT DEFAULT 0,         -- 自營商買進張數
    dealer_sell BIGINT DEFAULT 0,        -- 自營商賣出張數
    dealer_net BIGINT,                   -- 自營商買賣超
    close_price DECIMAL(10, 2),          -- 當日收盤價（用於計算金額）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, trade_date)
);

-- 2. 三大法人持股變化表
CREATE TABLE IF NOT EXISTS institutional_holdings (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    foreign_holding BIGINT DEFAULT 0,    -- 外資持股張數
    trust_holding BIGINT DEFAULT 0,      -- 投信持股張數
    dealer_holding BIGINT DEFAULT 0,     -- 自營商持股張數
    total_shares BIGINT NOT NULL,        -- 股票總股數
    foreign_holding_pct DECIMAL(5, 2),   -- 外資持股比例
    trust_holding_pct DECIMAL(5, 2),     -- 投信持股比例
    dealer_holding_pct DECIMAL(5, 2),    -- 自營商持股比例
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, trade_date)
);

-- 3. 融資融券餘額表
CREATE TABLE IF NOT EXISTS margin_trading (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    margin_balance BIGINT DEFAULT 0,     -- 融資餘額（張數）
    margin_quota BIGINT DEFAULT 0,       -- 融資限額
    margin_today_buy BIGINT DEFAULT 0,   -- 今日融資買進
    margin_today_sell BIGINT DEFAULT 0,  -- 今日融資賣出
    short_balance BIGINT DEFAULT 0,      -- 融券餘額（張數）
    short_quota BIGINT DEFAULT 0,        -- 融券限額
    short_today_buy BIGINT DEFAULT 0,    -- 今日融券買進
    short_today_sell BIGINT DEFAULT 0,   -- 今日融券賣出
    margin_usage_pct DECIMAL(5, 2),      -- 融資使用率
    short_usage_pct DECIMAL(5, 2),       -- 融券使用率
    margin_short_ratio DECIMAL(8, 2),    -- 資券比（融資/融券）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, trade_date)
);

-- 建立索引提升查詢效能
CREATE INDEX IF NOT EXISTS idx_institutional_trades_stock_date 
    ON institutional_trades(stock_code, trade_date DESC);

CREATE INDEX IF NOT EXISTS idx_institutional_holdings_stock_date 
    ON institutional_holdings(stock_code, trade_date DESC);

CREATE INDEX IF NOT EXISTS idx_margin_trading_stock_date 
    ON margin_trading(stock_code, trade_date DESC);

-- 插入測試數據（台積電2330）
INSERT INTO institutional_trades (stock_code, trade_date, foreign_buy, foreign_sell, trust_buy, trust_sell, dealer_buy, dealer_sell, close_price)
VALUES 
    ('2330', CURRENT_DATE - INTERVAL '1 day', 5000, 3000, 1000, 500, 800, 600, 589.0),
    ('2330', CURRENT_DATE - INTERVAL '2 days', 4500, 3500, 1200, 800, 700, 600, 587.0),
    ('2330', CURRENT_DATE - INTERVAL '3 days', 6000, 2000, 1500, 600, 900, 700, 590.0)
ON CONFLICT (stock_code, trade_date) DO NOTHING;

-- 更新計算欄位
UPDATE institutional_trades 
SET foreign_net = foreign_buy - foreign_sell,
    trust_net = trust_buy - trust_sell,
    dealer_net = dealer_buy - dealer_sell
WHERE foreign_net IS NULL;

INSERT INTO margin_trading (stock_code, trade_date, margin_balance, margin_quota, short_balance, short_quota)
VALUES 
    ('2330', CURRENT_DATE - INTERVAL '1 day', 68000, 100000, 12000, 20000),
    ('2330', CURRENT_DATE - INTERVAL '2 days', 67500, 100000, 12500, 20000),
    ('2330', CURRENT_DATE - INTERVAL '3 days', 67000, 100000, 13000, 20000)
ON CONFLICT (stock_code, trade_date) DO NOTHING;

-- 更新計算欄位
UPDATE margin_trading 
SET margin_usage_pct = (margin_balance::DECIMAL / margin_quota) * 100,
    short_usage_pct = (short_balance::DECIMAL / short_quota) * 100,
    margin_short_ratio = margin_balance::DECIMAL / NULLIF(short_balance, 0)
WHERE margin_usage_pct IS NULL;

-- 查詢驗證
SELECT '三大法人買賣超記錄' AS table_name, COUNT(*) AS row_count FROM institutional_trades
UNION ALL
SELECT '融資融券餘額', COUNT(*) FROM margin_trading;
