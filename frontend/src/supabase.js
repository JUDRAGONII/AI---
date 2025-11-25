// Supabase Client 配置（模擬版本）
// 在開發階段使用模擬數據，實際部署時替換為真實 Supabase 配置

// 模擬的資料庫客戶端
export const db = {
    from: (table) => {
        return {
            select: (columns = '*') => {
                return {
                    eq: (column, value) => {
                        return Promise.resolve({ data: [], error: null })
                    },
                    limit: (count) => {
                        return Promise.resolve({ data: [], error: null })
                    },
                    order: (column, options) => {
                        return Promise.resolve({ data: [], error: null })
                    },
                    then: (callback) => {
                        return callback({ data: [], error: null })
                    }
                }
            },
            insert: (data) => {
                return Promise.resolve({ data: null, error: null })
            },
            update: (data) => {
                return {
                    eq: (column, value) => {
                        return Promise.resolve({ data: null, error: null })
                    }
                }
            },
            delete: () => {
                return {
                    eq: (column, value) => {
                        return Promise.resolve({ data: null, error: null })
                    }
                }
            }
        }
    }
}

// 如需使用真實 Supabase，請取消以下註釋並填入您的配置：
/*
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const db = createClient(supabaseUrl, supabaseAnonKey)
*/

export default db
