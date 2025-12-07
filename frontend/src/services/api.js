// API配置 - 更新添加新端點
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

export const api = {
    // 股票相關
    stocks: {
        list: (market = 'tw', limit = 100) =>
            `${API_BASE_URL}/stocks/list?market=${market}&limit=${limit}`,

        detail: (code, market = 'tw') =>
            `${API_BASE_URL}/stocks/${code}?market=${market}`,

        search: (keyword, market = 'tw') =>
            `${API_BASE_URL}/stocks/search?keyword=${keyword}&market=${market}`,
    },

    // 價格相關
    prices: {
        history: (code, market = 'tw', days = 30) =>
            `${API_BASE_URL}/prices/${code}?market=${market}&days=${days}`,

        latest: (code, market = 'tw') =>
            `${API_BASE_URL}/prices/${code}/latest?market=${market}`,
    },

    // 商品價格（黃金等）- 新增
    commodity: {
        prices: (code, days = 30) =>
            `${API_BASE_URL}/commodity/${code}?days=${days}`,
    },

    // 匯率 - 新增
    forex: {
        rates: (pair, days = 30) =>
            `${API_BASE_URL}/forex/${pair}?days=${days}`,
    },

    // TDCC大戶持股 - 新增  
    tdcc: {
        data: (code, limit = 10) =>
            `${API_BASE_URL}/tdcc/${code}?limit=${limit}`,
    },

    // 市場總覽 - 新增
    market: {
        summary: () =>
            `${API_BASE_URL}/market/summary`,
    },

    // 因子分數
    factors: {
        scores: (code, market = 'tw') =>
            `${API_BASE_URL}/factors/${code}?market=${market}`,

        history: (code, market = 'tw', days = 90) =>
            `${API_BASE_URL}/factors/${code}/history?market=${market}&days=${days}`,
    },

    // 技術指標
    indicators: {
        data: (code, market = 'tw') =>
            `${API_BASE_URL}/indicators/${code}?market=${market}`,
    },

    // AI報告
    ai: {
        reports: (type = 'daily', limit = 10) =>
            `${API_BASE_URL}/ai/reports?type=${type}&limit=${limit}`,

        report: (id) => `${API_BASE_URL}/ai/report/${id}`,
    },

    // 投資組合
    portfolio: {
        list: (userId = 1) =>
            `${API_BASE_URL}/portfolio/list?user_id=${userId}`,

        holdings: (portfolioId) =>
            `${API_BASE_URL}/portfolio/${portfolioId}/holdings`,
    },

    // 系統配置
    config: {
        apiKeys: () => `${API_BASE_URL}/config/api-keys`,
        syncApiKeys: () => `${API_BASE_URL}/config/sync-api-keys`,
    },

    // 資料庫
    database: {
        tables: () => `${API_BASE_URL}/database/tables`,
        table: (name) => `${API_BASE_URL}/database/table/${name}`,
    },

    // 健康檢查
    health: () => `${API_BASE_URL}/health`,

    // 稅務試算 - 新增
    tax: {
        calculateTransaction: () => `${API_BASE_URL}/tax/calculate_transaction`,
        simulateDividend: () => `${API_BASE_URL}/tax/simulate_dividend`,
    },
};

// HTTP客戶端封裝
export const fetchAPI = async (url, options = {}) => {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || `HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};

export default { api, fetchAPI };
