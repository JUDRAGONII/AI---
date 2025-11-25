// Supabase 客戶端配置
import { createClient } from '@supabase/supabase-js'

// Supabase URL 和 API Key
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'http://localhost:8000'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'your-anon-key-here'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// 資料庫查詢函數
export const db = {
    // 查詢股票價格
    queryStockPrices: async (stockCode, market = 'tw', limit = 100) => {
        const table = market === 'tw' ? 'tw_stock_prices' : 'us_stock_prices'
        const idCol = market === 'tw' ? 'stock_code' : 'symbol'

        const { data, error } = await supabase
            .from(table)
            .select('*')
            .eq(idCol, stockCode)
            .order('trade_date', { ascending: false })
            .limit(limit)

        if (error) throw error
        return data
    },

    // 查詢因子分數
    queryFactorScores: async (stockCode, limit = 30) => {
        const { data, error } = await supabase
            .from('quant_scores')
            .select('*')
            .eq('security_id', stockCode)
            .order('calculation_date', { ascending: false })
            .limit(limit)

        if (error) throw error
        return data
    },

    // 查詢 AI 報告
    queryAIReports: async (reportType = null, limit = 10) => {
        let query = supabase
            .from('ai_reports')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(limit)

        if (reportType) {
            query = query.eq('report_type', reportType)
        }

        const { data, error } = await query
        if (error) throw error
        return data
    },

    // 查詢籌碼資料
    queryShareholderDispersion: async (stockCode, limit = 52) => {
        const { data, error } = await supabase
            .from('shareholder_dispersion')
            .select('*')
            .eq('stock_code', stockCode)
            .order('data_date', { ascending: false })
            .limit(limit)

        if (error) throw error
        return data
    }
}
