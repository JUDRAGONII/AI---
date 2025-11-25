-- ============================================
-- 專業金融資料庫完整架構 Schema
-- 服務於 AI 投資分析儀 (Gemini Quant)
-- 版本：V1.0
-- 日期：2025-11-22
-- ============================================

-- 啟用必要的擴展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================
-- 第一層：原始資料表（基礎資料）
-- ============================================

-- 1.1 台股基本資訊表
CREATE TABLE IF NOT EXISTS tw_stock_info (
    stock_code VARCHAR(10) PRIMARY KEY,
    stock_name VARCHAR(100) NOT NULL,
    industry VARCHAR(50),
    market VARCHAR(20),  -- 上市/上櫃
    listing_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE tw_stock_info IS '台股基本資訊表';
COMMENT ON COLUMN tw_stock_info.market IS '上市=TWSE, 上櫃=TPEX';

-- 1.2 台股日線價格表
CREATE TABLE IF NOT EXISTS tw_stock_prices (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open_price DECIMAL(10,2),
    high_price DECIMAL(10,2),
    low_price DECIMAL(10,2),
    close_price DECIMAL(10,2) NOT NULL,
    volume BIGINT,
    adjusted_close DECIMAL(10,2),
    turnover DECIMAL(18,2),  -- 成交金額
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(stock_code, trade_date),
    FOREIGN KEY (stock_code) REFERENCES tw_stock_info(stock_code) ON DELETE CASCADE
);

CREATE INDEX idx_tw_prices_code_date ON tw_stock_prices(stock_code, trade_date DESC);
CREATE INDEX idx_tw_prices_date ON tw_stock_prices(trade_date DESC);

COMMENT ON TABLE tw_stock_prices IS '台股日線價格資料';

-- 1.3 美股基本資訊表
CREATE TABLE IF NOT EXISTS us_stock_info (
    symbol VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(200),
    sector VARCHAR(100),
    industry VARCHAR(100),
    exchange VARCHAR(20),  -- NYSE, NASDAQ
    market_cap BIGINT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE us_stock_info IS '美股基本資訊表';

-- 1.4 美股日線價格表
CREATE TABLE IF NOT EXISTS us_stock_prices (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open_price DECIMAL(12,4),
    high_price DECIMAL(12,4),
    low_price DECIMAL(12,4),
    close_price DECIMAL(12,4) NOT NULL,
    volume BIGINT,
    adjusted_close DECIMAL(12,4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(symbol, trade_date),
    FOREIGN KEY (symbol) REFERENCES us_stock_info(symbol) ON DELETE CASCADE
);

CREATE INDEX idx_us_prices_symbol_date ON us_stock_prices(symbol, trade_date DESC);
CREATE INDEX idx_us_prices_date ON us_stock_prices(trade_date DESC);

COMMENT ON TABLE us_stock_prices IS '美股日線價格資料';

-- 1.5 黃金價格表
CREATE TABLE IF NOT EXISTS gold_prices (
    trade_date DATE PRIMARY KEY,
    open_price DECIMAL(10,2),
    high_price DECIMAL(10,2),
    low_price DECIMAL(10,2),
    close_price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE gold_prices IS '黃金現貨價格（XAU/USD）';

-- 1.6 匯率表
CREATE TABLE IF NOT EXISTS exchange_rates (
    id BIGSERIAL PRIMARY KEY,
    trade_date DATE NOT NULL,
    currency_pair VARCHAR(10) NOT NULL,  -- TWD/USD, EUR/USD
    rate DECIMAL(12,6) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(trade_date, currency_pair)
);

CREATE INDEX idx_exchange_date_pair ON exchange_rates(trade_date DESC, currency_pair);

COMMENT ON TABLE exchange_rates IS '匯率資料';

-- 1.7 宏觀經濟指標表
CREATE TABLE IF NOT EXISTS macro_indicators (
    id BIGSERIAL PRIMARY KEY,
    country_code VARCHAR(3) NOT NULL,  -- USA, TWN, CHN
    indicator_code VARCHAR(50) NOT NULL,  -- GDP, CPI, UNEMPLOYMENT
    indicator_name VARCHAR(200),
    date DATE NOT NULL,
    value DECIMAL(20,6),
    unit VARCHAR(50),  -- %, USD, etc.
    source VARCHAR(50),  -- FRED, World Bank
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(country_code, indicator_code, date)
);

CREATE INDEX idx_macro_country_indicator_date ON macro_indicators(country_code, indicator_code, date DESC);

COMMENT ON TABLE macro_indicators IS '宏觀經濟指標';

-- 1.8 金融新聞表
CREATE TABLE IF NOT EXISTS financial_news (
    id BIGSERIAL PRIMARY KEY,
    news_id VARCHAR(100) UNIQUE,
    title TEXT NOT NULL,
    content TEXT,
    source VARCHAR(100),
    url TEXT,
    published_at TIMESTAMPTZ,
    sentiment_score DECIMAL(3,2),  -- -1.0 到 1.0
    related_symbols TEXT[],  -- 相關股票代碼
    categories TEXT[],
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_news_published ON financial_news(published_at DESC);
CREATE INDEX idx_news_symbols ON financial_news USING GIN(related_symbols);
CREATE INDEX idx_news_sentiment ON financial_news(sentiment_score) WHERE sentiment_score IS NOT NULL;

COMMENT ON TABLE financial_news IS '金融新聞與情緒分析';

-- ============================================
-- 第二層：預計算表（效能優化核心）
-- ============================================

-- 2.1 技術指標預計算表
CREATE TABLE IF NOT EXISTS technical_indicators (
    id BIGSERIAL PRIMARY KEY,
    security_type VARCHAR(5) NOT NULL,  -- 'TW' or 'US'
    security_code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    
    -- 移動平均線
    ma_5 DECIMAL(12,4),
    ma_10 DECIMAL(12,4),
    ma_20 DECIMAL(12,4),
    ma_60 DECIMAL(12,4),
    ma_120 DECIMAL(12,4),
    ma_240 DECIMAL(12,4),
    
    -- RSI
    rsi_14 DECIMAL(5,2),
    rsi_21 DECIMAL(5,2),
    
    -- MACD
    macd DECIMAL(12,4),
    macd_signal DECIMAL(12,4),
    macd_histogram DECIMAL(12,4),
    
    -- 布林通道
    bb_upper DECIMAL(12,4),
    bb_middle DECIMAL(12,4),
    bb_lower DECIMAL(12,4),
    bb_width DECIMAL(8,4),
    
    -- KD 指標
    k_value DECIMAL(5,2),
    d_value DECIMAL(5,2),
    
    -- 成交量指標
    volume_ma_5 BIGINT,
    volume_ma_20 BIGINT,
    
    -- 波動率
    volatility_20d DECIMAL(8,4),
    volatility_60d DECIMAL(8,4),
    
    -- 相對強弱
    relative_strength_score DECIMAL(8,4),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(security_type, security_code, trade_date)
);

CREATE INDEX idx_tech_ind_security_date ON technical_indicators(security_type, security_code, trade_date DESC);
CREATE INDEX idx_tech_ind_date ON technical_indicators(trade_date DESC);

COMMENT ON TABLE technical_indicators IS '技術指標預計算表';

-- 2.2 量化因子分數表
CREATE TABLE IF NOT EXISTS quant_scores (
    id BIGSERIAL PRIMARY KEY,
    security_type VARCHAR(5) NOT NULL,
    security_code VARCHAR(10) NOT NULL,
    calculation_date DATE NOT NULL,
    
    -- 價值因子
    pe_ratio DECIMAL(10,2),
    pb_ratio DECIMAL(10,2),
    dividend_yield DECIMAL(6,4),
    ev_ebitda DECIMAL(10,2),
    value_score DECIMAL(5,2),  -- 0-100
    
    -- 品質因子
    roe DECIMAL(8,4),
    roa DECIMAL(8,4),
    debt_to_equity DECIMAL(10,2),
    gross_margin DECIMAL(8,4),
    quality_score DECIMAL(5,2),
    
    -- 動能因子
    rsi_14 DECIMAL(5,2),
    relative_return_1m DECIMAL(8,4),
    relative_return_3m DECIMAL(8,4),
    distance_from_52w_high DECIMAL(6,4),
    momentum_score DECIMAL(5,2),
    
    -- 規模因子
    market_cap BIGINT,
    size_score DECIMAL(5,2),
    
    -- 波動率因子
    volatility_1y DECIMAL(8,4),
    beta DECIMAL(6,4),
    volatility_score DECIMAL(5,2),
    
    -- 成長因子
    revenue_cagr_3y DECIMAL(8,4),
    eps_cagr_3y DECIMAL(8,4),
    growth_score DECIMAL(5,2),
    
    -- 綜合評分
    total_score DECIMAL(6,2),
    weight_config_id INTEGER DEFAULT 1,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(security_type, security_code, calculation_date)
);

CREATE INDEX idx_quant_security_date ON quant_scores(security_type, security_code, calculation_date DESC);
CREATE INDEX idx_quant_total_score ON quant_scores(total_score DESC, calculation_date DESC);

COMMENT ON TABLE quant_scores IS '量化六大因子分數表';

-- ============================================
-- 第三層：AI 快取層
-- ============================================

-- 3.1 AI 分析報告快取表
CREATE TABLE IF NOT EXISTS ai_reports (
    id BIGSERIAL PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL,  -- 'decision_template', 'daily_strategy', 'stock_analysis'
    security_type VARCHAR(5),
    security_code VARCHAR(10),
    user_id UUID,
    
    -- 報告內容
    title VARCHAR(500),
    content TEXT,
    content_json JSONB,
    
    -- AI 元數據
    model_version VARCHAR(50) DEFAULT 'gemini-2.5-pro',
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    
    -- 分析結果
    sentiment_score DECIMAL(3,2),
    confidence_level DECIMAL(3,2),
    key_insights TEXT[],
    risk_alerts TEXT[],
    
    -- 決策建議
    recommendation VARCHAR(20),  -- 'STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL'
    target_price DECIMAL(12,2),
    stop_loss DECIMAL(12,2),
    
    -- 時效性管理
    analysis_date DATE NOT NULL,
    valid_until DATE,
    is_outdated BOOLEAN DEFAULT FALSE,
    
    -- 準確度追蹤
    prediction_outcome VARCHAR(20),
    accuracy_score DECIMAL(5,2),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_ai_reports_type_date ON ai_reports(report_type, analysis_date DESC);
CREATE INDEX idx_ai_reports_security ON ai_reports(security_type, security_code, analysis_date DESC);
CREATE INDEX idx_ai_reports_validity ON ai_reports(is_outdated, valid_until) WHERE is_outdated = FALSE;

COMMENT ON TABLE ai_reports IS 'AI 分析報告快取（減少 70-80% API 使用）';

-- 3.2 因子相似度矩陣表
CREATE TABLE IF NOT EXISTS similarity_matrix (
    id BIGSERIAL PRIMARY KEY,
    source_type VARCHAR(5) NOT NULL,
    source_code VARCHAR(10) NOT NULL,
    target_type VARCHAR(5) NOT NULL,
    target_code VARCHAR(10) NOT NULL,
    calculation_date DATE NOT NULL,
    
    overall_similarity DECIMAL(6,4),
    value_similarity DECIMAL(6,4),
    quality_similarity DECIMAL(6,4),
    momentum_similarity DECIMAL(6,4),
    
    similarity_rank INTEGER,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(source_type, source_code, target_type, target_code, calculation_date)
);

CREATE INDEX idx_similarity_source_rank ON similarity_matrix(source_type, source_code, similarity_rank);

COMMENT ON TABLE similarity_matrix IS '因子相似度矩陣（相似資產發現）';

-- ============================================
-- 第四層：進階分析表
-- ============================================

-- 4.1 大戶籌碼分析表（TDCC 集保數據）
CREATE TABLE IF NOT EXISTS shareholder_dispersion (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    data_date DATE NOT NULL,
    
    -- 持股級距（單位：張）
    holders_1_999 INTEGER,
    holders_1k_5k INTEGER,
    holders_5k_10k INTEGER,
    holders_10k_15k INTEGER,
    holders_15k_20k INTEGER,
    holders_20k_30k INTEGER,
    holders_30k_40k INTEGER,
    holders_40k_50k INTEGER,
    holders_50k_100k INTEGER,
    holders_100k_200k INTEGER,
    holders_200k_400k INTEGER,
    holders_400k_600k INTEGER,
    holders_600k_800k INTEGER,
    holders_800k_1m INTEGER,
    holders_over_1m INTEGER,
    
    -- 統計數據
    total_shareholders INTEGER,
    shares_over_1m BIGINT,
    
    -- 計算指標
    large_holders_percentage DECIMAL(6,4),
    concentration_ratio DECIMAL(6,4),
    large_holders_change INTEGER,
    
    -- 核心指標
    synchronization_index DECIMAL(6,4),
    smart_money_flow VARCHAR(20),  -- 'INFLOW', 'OUTFLOW', 'NEUTRAL'
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(stock_code, data_date),
    FOREIGN KEY (stock_code) REFERENCES tw_stock_info(stock_code) ON DELETE CASCADE
);

CREATE INDEX idx_shareholder_code_date ON shareholder_dispersion(stock_code, data_date DESC);
CREATE INDEX idx_shareholder_sync ON shareholder_dispersion(synchronization_index DESC, data_date DESC);

COMMENT ON TABLE shareholder_dispersion IS '大戶籌碼分析（TDCC集保資料）';

-- 4.2 13F 機構持倉表
CREATE TABLE IF NOT EXISTS institutional_holdings_13f (
    id BIGSERIAL PRIMARY KEY,
    filing_date DATE NOT NULL,
    period_date DATE NOT NULL,
    
    manager_name VARCHAR(200) NOT NULL,
    manager_cik VARCHAR(20),
    symbol VARCHAR(10) NOT NULL,
    
    shares_held BIGINT,
    market_value BIGINT,
    portfolio_percentage DECIMAL(6,4),
    
    shares_change BIGINT,
    shares_change_pct DECIMAL(8,4),
    is_new_position BOOLEAN DEFAULT FALSE,
    is_sold_out BOOLEAN DEFAULT FALSE,
    
    position_type VARCHAR(20),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(manager_cik, symbol, period_date),
    FOREIGN KEY (symbol) REFERENCES us_stock_info(symbol) ON DELETE CASCADE
);

CREATE INDEX idx_13f_symbol_period ON institutional_holdings_13f(symbol, period_date DESC);
CREATE INDEX idx_13f_manager_period ON institutional_holdings_13f(manager_name, period_date DESC);
CREATE INDEX idx_13f_new_pos ON institutional_holdings_13f(period_date DESC) WHERE is_new_position = TRUE;

COMMENT ON TABLE institutional_holdings_13f IS '13F 機構持倉（橋水、巴菲特等）';

-- 4.3 投資組合績效快取表
CREATE TABLE IF NOT EXISTS portfolio_performance (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    calculation_date DATE NOT NULL,
    
    -- 報酬指標
    total_value DECIMAL(18,2),
    total_return DECIMAL(10,6),
    daily_return DECIMAL(10,6),
    mtd_return DECIMAL(10,6),
    ytd_return DECIMAL(10,6),
    
    -- 風險指標
    portfolio_beta DECIMAL(6,4),
    portfolio_volatility DECIMAL(8,4),
    sharpe_ratio DECIMAL(6,4),
    sortino_ratio DECIMAL(6,4),
    max_drawdown DECIMAL(8,4),
    
    -- 績效歸因
    factor_attribution JSONB,
    sector_attribution JSONB,
    
    -- 與基準比較
    vs_benchmark_return DECIMAL(10,6),
    tracking_error DECIMAL(8,4),
    information_ratio DECIMAL(6,4),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, calculation_date)
);

CREATE INDEX idx_port_perf_user_date ON portfolio_performance(user_id, calculation_date DESC);

COMMENT ON TABLE portfolio_performance IS '投資組合績效快取';

-- 4.4 策略回測結果表
CREATE TABLE IF NOT EXISTS backtest_results (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    strategy_name VARCHAR(200) NOT NULL,
    strategy_config JSONB,
    
    start_date DATE,
    end_date DATE,
    initial_capital DECIMAL(18,2),
    
    -- 績效指標
    final_value DECIMAL(18,2),
    total_return DECIMAL(10,6),
    cagr DECIMAL(8,4),
    sharpe_ratio DECIMAL(6,4),
    max_drawdown DECIMAL(8,4),
    win_rate DECIMAL(6,4),
    
    -- 交易統計
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    avg_win DECIMAL(10,6),
    avg_loss DECIMAL(10,6),
    
    trade_log JSONB,
    equity_curve JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_backtest_user ON backtest_results(user_id, created_at DESC);
CREATE INDEX idx_backtest_sharpe ON backtest_results(sharpe_ratio DESC);

COMMENT ON TABLE backtest_results IS '策略回測結果';

-- 4.5 行為金融指標表
CREATE TABLE IF NOT EXISTS behavioral_metrics (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    calculation_date DATE NOT NULL,
    
    -- 處置效應
    disposition_effect_score DECIMAL(6,4),
    avg_holding_period_winners INTEGER,
    avg_holding_period_losers INTEGER,
    
    -- 損失規避
    loss_aversion_index DECIMAL(6,4),
    
    -- 過度交易
    turnover_rate DECIMAL(8,4),
    trading_frequency_score DECIMAL(6,4),
    
    -- 羊群效應
    herd_behavior_score DECIMAL(6,4),
    contrarian_index DECIMAL(6,4),
    
    -- 過度自信
    overconfidence_score DECIMAL(6,4),
    prediction_accuracy DECIMAL(6,4),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, calculation_date)
);

CREATE INDEX idx_behavioral_user_date ON behavioral_metrics(user_id, calculation_date DESC);

COMMENT ON TABLE behavioral_metrics IS '行為金融指標';

-- 4.6 壓力測試結果表
CREATE TABLE IF NOT EXISTS stress_test_results (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    portfolio_snapshot_id INTEGER,
    test_date TIMESTAMPTZ NOT NULL,
    
    scenario_name VARCHAR(200) NOT NULL,
    scenario_type VARCHAR(50),  -- 'HISTORICAL', 'HYPOTHETICAL'
    scenario_config JSONB,
    
    expected_loss DECIMAL(18,2),
    expected_loss_pct DECIMAL(8,4),
    max_drawdown DECIMAL(8,4),
    value_at_risk_95 DECIMAL(18,2),
    conditional_var DECIMAL(18,2),
    
    stock_impacts JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_stress_test_user ON stress_test_results(user_id, test_date DESC);

COMMENT ON TABLE stress_test_results IS '壓力測試結果';

-- ============================================
-- 第五層：系統管理表
-- ============================================

-- 5.1 資料同步狀態表
CREATE TABLE IF NOT EXISTS sync_status (
    id SERIAL PRIMARY KEY,
    data_source VARCHAR(50) NOT NULL,  -- 'taiwan_stock', 'us_stock', 'gold', etc.
    source_identifier VARCHAR(100),  -- 股票代碼、指標代碼
    last_sync_date DATE,
    last_sync_timestamp TIMESTAMPTZ,
    sync_status VARCHAR(20) NOT NULL,  -- 'running', 'success', 'failed', 'pending'
    error_message TEXT,
    earliest_date DATE,
    latest_date DATE,
    total_records BIGINT DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(data_source, source_identifier)
);

CREATE INDEX idx_sync_status_source ON sync_status(data_source, sync_status);
CREATE INDEX idx_sync_status_updated ON sync_status(updated_at DESC);

COMMENT ON TABLE sync_status IS '資料同步狀態追蹤';

-- 5.2 系統配置表
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    config_type VARCHAR(20) DEFAULT 'string',  -- 'string', 'number', 'boolean', 'json'
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE system_config IS '系統配置參數';

-- 插入預設配置
INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('backfill_batch_size', '500', 'number', '資料回溯批次大小'),
('api_rate_limit_default', '1.0', 'number', '預設 API 請求間隔（秒）'),
('technical_indicators_enabled', 'true', 'boolean', '是否啟用技術指標計算'),
('ai_report_cache_days', '7', 'number', 'AI 報告快取天數')
ON CONFLICT (config_key) DO NOTHING;

-- ============================================
-- 建立觸發器函數
-- ============================================

-- 自動更新 updated_at 欄位
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 為相關表格建立觸發器
CREATE TRIGGER update_tw_stock_info_updated_at
    BEFORE UPDATE ON tw_stock_info
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_us_stock_info_updated_at
    BEFORE UPDATE ON us_stock_info
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_reports_updated_at
    BEFORE UPDATE ON ai_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at
    BEFORE UPDATE ON system_config
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 建立視圖（便於查詢）
-- ============================================

-- 最新台股價格視圖
CREATE OR REPLACE VIEW v_tw_stock_latest AS
SELECT 
    si.stock_code,
    si.stock_name,
    si.industry,
    si.market,
    sp.trade_date,
    sp.close_price,
    sp.volume,
    sp.adjusted_close
FROM tw_stock_info si
LEFT JOIN LATERAL (
    SELECT * FROM tw_stock_prices 
    WHERE stock_code = si.stock_code 
    ORDER BY trade_date DESC 
    LIMIT 1
) sp ON TRUE;

-- 最新美股價格視圖
CREATE OR REPLACE VIEW v_us_stock_latest AS
SELECT 
    si.symbol,
    si.company_name,
    si.sector,
    si.exchange,
    sp.trade_date,
    sp.close_price,
    sp.volume,
    sp.adjusted_close
FROM us_stock_info si
LEFT JOIN LATERAL (
    SELECT * FROM us_stock_prices 
    WHERE symbol = si.symbol 
    ORDER BY trade_date DESC 
    LIMIT 1
) sp ON TRUE;

-- ============================================
-- 完成訊息
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '=================================';
    RAISE NOTICE '資料庫架構建立完成！';
    RAISE NOTICE '總計 23 個核心表格';
    RAISE NOTICE '- 原始資料層：8 個表格';
    RAISE NOTICE '- 預計算層：2 個表格';
    RAISE NOTICE '- AI 快取層：2 個表格';
    RAISE NOTICE '- 進階分析層：6 個表格';
    RAISE NOTICE '- 系統管理層：2 個表格';
    RAISE NOTICE '- 視圖：2 個';
    RAISE NOTICE '=================================';
END $$;
