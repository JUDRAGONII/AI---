import { createClient } from '@supabase/supabase-js'

// Supabase 配置 - 從環境變數讀取
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'http://localhost:8000'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyAgCiAgICAicm9sZSI6ICJhbm9uIiwKICAgICJpc3MiOiAic3VwYWJhc2UtZGVtbyIsCiAgICAiaWF0IjogMTY0MTc2OTIwMCwKICAgICJleHAiOiAxNzk5NTM1NjAwCn0.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE'

// 建立 Supabase 客戶端
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true
    },
    realtime: {
        params: {
            eventsPerSecond: 10
        }
    }
})

// ============== Realtime 訂閱範例 ==============

/**
 * 訂閱指定表格的即時更新
 * @param {string} table - 表格名稱
 * @param {function} callback - 資料更新時的回調函數
 * @returns {Object} 訂閱物件（可用於取消訂閱）
 */
export function subscribe ToTable(table, callback) {
    const channel = supabase
        .channel(`public:${table}`)
        .on(
            'postgres_changes',
            {
                event: '*',  // '*' 表示監聽所有事件 (INSERT, UPDATE, DELETE)
                schema: 'public',
                table: table
            },
            (payload) => {
                console.log(`[Supabase Realtime] ${table} changed:`, payload)
                callback(payload)
            }
        )
        .subscribe()

    return channel
}

/**
 * 訂閱價格表的即時更新
 */
export function subscribeToStockPrices(callback) {
    return subscribeToTable('tw_stock_prices', callback)
}

/**
 * 取消訂閱
 * @param {Object} channel - subscribeToTable 返回的訂閱物件
 */
export function unsubscribe(channel) {
    if (channel) {
        supabase.removeChannel(channel)
    }
}

export default supabase
