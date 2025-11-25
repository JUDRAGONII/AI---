// 大戶同步率分析儀頁面 (Shareholder Analysis)
// 這是系統的核心功能之一，整合 TDCC 集保中心數據
import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Users, DollarSign, AlertTriangle } from 'lucide-react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { db } from '../supabase'

export default function ShareholderAnalysis() {
    const [stockCode, setStockCode] = useState('2330')  // 預設台積電
    const [loading, setLoading] = useState(true)
    const [shareholderData, setShareholderData] = useState(null)
    const [latestData, setLatestData] = useState(null)

    useEffect(() => {
        loadShareholderData()
    }, [stockCode])

    const loadShareholderData = async () => {
        setLoading(true)
        try {
            // 從資料庫獲取股權分散資料
            const data = await db.queryShareholderDispersion(stockCode, 52)

            if (data && data.length > 0) {
                // 反轉資料（從舊到新）
                const reversedData = [...data].reverse()
                setShareholderData(reversedData)
                setLatestData(data[0])  // 最新一筆
            }
        } catch (error) {
            console.error('載入籌碼資料失敗:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-xl">載入中...</div>
            </div>
        )
    }

    // 計算同步率評級
    const getSyncRating = (syncIndex) => {
        if (!syncIndex) return { label: '無資料', color: 'gray', icon: null }

        if (syncIndex > 0.7) return {
            label: '極高同步',
            color: 'green',
            icon: <TrendingUp className="w-5 h-5" />,
            description: '大戶一致買進，強勢訊號'
        }
        if (syncIndex > 0.6) return {
            label: '高同步',
            color: 'blue',
            icon: <TrendingUp className="w-5 h-5" />,
            description: '大戶持續加碼'
        }
        if (syncIndex >= 0.4) return {
            label: '中性',
            color: 'yellow',
            icon: <DollarSign className="w-5 h-5" />,
            description: '大戶分歧，觀望為主'
        }
        return {
            label: '低同步',
            color: 'red',
            icon: <TrendingDown className="w-5 h-5" />,
            description: '大戶退場，謹慎為宜'
        }
    }

    const rating = getSyncRating(latestData?.synchronization_index)

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">大戶同步率分析儀</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        TDCC 集保中心權威數據 | 追蹤聰明錢流向
                    </p>
                </div>

                {/* 股票選擇器 */}
                <div className="flex items-center gap-3">
                    <label className="text-sm font-medium">股票代碼</label>
                    <input
                        type="text"
                        value={stockCode}
                        onChange={(e) => setStockCode(e.target.value)}
                        className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                        placeholder="2330"
                    />
                    <button
                        onClick={loadShareholderData}
                        className="btn btn-primary"
                    >
                        查詢
                    </button>
                </div>
            </div>

            {shareholderData ? (
                <>
                    {/* 關鍵指標卡片 */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        {/* 同步率指標 */}
                        <div className="card">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    同步率指標
                                </h3>
                                {rating.icon}
                            </div>
                            <div className="space-y-2">
                                <div className="text-3xl font-bold">
                                    {(latestData?.synchronization_index * 100).toFixed(1)}%
                                </div>
                                <div className={`text-sm font-medium text-${rating.color}-600`}>
                                    {rating.label}
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-400">
                                    {rating.description}
                                </div>
                            </div>
                        </div>

                        {/* 總股東數 */}
                        <div className="card">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    總股東數
                                </h3>
                                <Users className="w-5 h-5" />
                            </div>
                            <div className="text-2xl font-bold">
                                {latestData?.total_shareholders?.toLocaleString()}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                                最新統計
                            </div>
                        </div>

                        {/* 大戶比例 */}
                        <div className="card">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    大戶比例 (400張+)
                                </h3>
                                <DollarSign className="w-5 h-5" />
                            </div>
                            <div className="text-2xl font-bold">
                                {latestData?.large_holders_percentage?.toFixed(2)}%
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                                持股 40 萬股以上
                            </div>
                        </div>

                        {/* 資金流向 */}
                        <div className="card">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">
                                    資金流向
                                </h3>
                                {latestData?.smart_money_flow === 'INFLOW' ? (
                                    <TrendingUp className="w-5 h-5 text-green-600" />
                                ) : latestData?.smart_money_flow === 'OUTFLOW' ? (
                                    <TrendingDown className="w-5 h-5 text-red-600" />
                                ) : (
                                    <DollarSign className="w-5 h-5 text-yellow-600" />
                                )}
                            </div>
                            <div className={`text-2xl font-bold ${latestData?.smart_money_flow === 'INFLOW' ? 'text-green-600' :
                                    latestData?.smart_money_flow === 'OUTFLOW' ? 'text-red-600' :
                                        'text-yellow-600'
                                }`}>
                                {latestData?.smart_money_flow === 'INFLOW' ? '流入' :
                                    latestData?.smart_money_flow === 'OUTFLOW' ? '流出' :
                                        '中性'}
                            </div>
                        </div>
                    </div>

                    {/* 同步率趨勢圖 */}
                    <div className="card">
                        <h2 className="text-2xl font-bold mb-4">同步率歷史趨勢（52週）</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={shareholderData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis
                                    dataKey="data_date"
                                    tick={{ fontSize: 12 }}
                                    angle={-45}
                                    textAnchor="end"
                                    height={80}
                                />
                                <YAxis domain={[0, 1]} tickFormatter={(value) => `${(value * 100).toFixed(0)}%`} />
                                <Tooltip
                                    formatter={(value) => `${(value * 100).toFixed(2)}%`}
                                    labelFormatter={(label) => `日期: ${label}`}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="synchronization_index"
                                    stroke="#3b82f6"
                                    strokeWidth={2}
                                    name="同步率"
                                    dot={{ r: 2 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    {/* 大戶持股比例趨勢 */}
                    <div className="card">
                        <h2 className="text-2xl font-bold mb-4">大戶持股比例變化</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={shareholderData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis
                                    dataKey="data_date"
                                    tick={{ fontSize: 12 }}
                                    angle={-45}
                                    textAnchor="end"
                                    height={80}
                                />
                                <YAxis tickFormatter={(value) => `${value.toFixed(1)}%`} />
                                <Tooltip
                                    formatter={(value) => `${value.toFixed(2)}%`}
                                />
                                <Legend />
                                <Line
                                    type="monotone"
                                    dataKey="large_holders_percentage"
                                    stroke="#10b981"
                                    strokeWidth={2}
                                    name="大戶比例"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    {/* 分析說明 */}
                    <div className="card bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                        <div className="flex items-start gap-3">
                            <AlertTriangle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-1" />
                            <div className="space-y-2">
                                <h3 className="font-bold text-blue-900 dark:text-blue-100">如何解讀大戶同步率？</h3>
                                <div className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                                    <p><strong>極高同步 (&gt;70%)</strong>：大戶一致買進，通常是強勢訊號，但需注意是否已過度擁擠</p>
                                    <p><strong>高同步 (60-70%)</strong>：大戶持續加碼，趨勢穩定向上</p>
                                    <p><strong>中性 (40-60%)</strong>：大戶分歧，建議觀望或配合其他指標判斷</p>
                                    <p><strong>低同步 (&lt;40%)</strong>：大戶退場，需謹慎操作</p>
                                    <p className="mt-2"><strong>資料來源</strong>：TDCC 集保結算所，每週五更新</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            ) : (
                <div className="card text-center py-12">
                    <p className="text-gray-500 dark:text-gray-400">
                        無籌碼資料，請輸入其他股票代碼或稍後再試
                    </p>
                </div>
            )}
        </div>
    )
}
