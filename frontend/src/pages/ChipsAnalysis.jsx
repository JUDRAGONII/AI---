// 籌碼分析頁面組件
import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, Users, DollarSign, AlertTriangle, Info } from 'lucide-react'

export default function ChipsAnalysis() {
    const [stockCode, setStockCode] = useState('2330')
    const [market, setMarket] = useState('tw')
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState(null)
    const [error, setError] = useState(null)

    useEffect(() => {
        fetchChipsData()
    }, []) // 只在初始載入時執行一次

    const fetchChipsData = async () => {
        setLoading(true)
        setError(null)

        try {
            const response = await fetch(`http://localhost:5000/api/chips/${stockCode}/all?market=${market}`)

            if (!response.ok) {
                console.log('API失敗，使用mock數據')
                setData(getMockData())
                setLoading(false)
                return
            }

            const result = await response.json()
            setData(result)
        } catch (err) {
            console.error('獲取籌碼數據失敗:', err)
            setData(getMockData())
        } finally {
            setLoading(false)
        }
    }

    const getMockData = () => ({
        stock_code: stockCode,
        institutional: {
            foreign: {
                net_shares: 4500,
                net_value: 2652000,
                consecutive_days: 3,
                trend: '買超'
            },
            trust: {
                net_shares: -800,
                net_value: -472000,
                consecutive_days: -2,
                trend: '賣超'
            },
            dealer: {
                net_shares: 200,
                net_value: 118000,
                consecutive_days: 1,
                trend: '買超'
            },
            summary: {
                total_net_shares: 3900,
                dominant_force: '外資',
                overall_trend: '多頭',
                signal_strength: 62.5
            }
        },
        margin: {
            margin: {
                balance: 68500,
                quota: 100000,
                usage_pct: 68.5,
                change: 500,
                change_pct: 0.73,
                trend: '增加'
            },
            short: {
                balance: 12000,
                quota: 20000,
                usage_pct: 60.0,
                change: -300,
                change_pct: -2.44,
                trend: '減少'
            },
            ratio: {
                margin_short_ratio: 5.71,
                interpretation: '偏多'
            },
            signal: {
                overall: '偏多但需注意融資風險',
                warnings: ['融資使用率偏高'],
                risk_level: '中'
            }
        }
    })

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">載入籌碼數據中...</p>
                </div>
            </div>
        )
    }

    if (!data) return null

    const inst = data.institutional || {}
    const margin = data.margin || {}

    return (
        <div className="p-6 max-w-7xl mx-auto">
            {/* 標題與搜尋 */}
            <div className="mb-6">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                    籌碼分析
                </h1>
                <p className="text-gray-600 dark:text-gray-400">三大法人進出與融資融券追蹤</p>

                <div className="mt-4 flex gap-3">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            股票代碼
                        </label>
                        <input
                            type="text"
                            value={stockCode}
                            onChange={(e) => setStockCode(e.target.value)}
                            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg 
                                     bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                                     focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="例: 2330"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            市場
                        </label>
                        <select
                            value={market}
                            onChange={(e) => setMarket(e.target.value)}
                            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                                     bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                                     focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="tw">台股</option>
                            <option value="us">美股</option>
                        </select>
                    </div>
                    <div className="flex items-end">
                        <button
                            onClick={fetchChipsData}
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            查詢
                        </button>
                    </div>
                </div>
            </div>

            {/* 綜合判斷警示 */}
            {inst.summary && (
                <div className={`mb-6 p-4 rounded-lg border-l-4 ${inst.summary.overall_trend === '多頭'
                    ? 'bg-green-50 dark:bg-green-900/20 border-green-500'
                    : inst.summary.overall_trend === '空頭'
                        ? 'bg-red-50 dark:bg-red-900/20 border-red-500'
                        : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-500'
                    }`}>
                    <div className="flex items-start gap-3">
                        <AlertTriangle className={`w-6 h-6 mt-0.5 ${inst.summary.overall_trend === '多頭' ? 'text-green-600' :
                            inst.summary.overall_trend === '空頭' ? 'text-red-600' : 'text-yellow-600'
                            }`} />
                        <div className="flex-1">
                            <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                                籌碼綜合判斷: {inst.summary.overall_trend || '中性'}
                            </h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                主導力量: {inst.summary.dominant_force || '無明顯主力'} |
                                訊號強度: {inst.summary.signal_strength?.toFixed(1) || 0}分
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* 三大法人分析 */}
            {inst.foreign && inst.trust && inst.dealer && (
                <div className="mb-6">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                        <Users className="w-6 h-6" />
                        三大法人買賣超
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {/* 外資 */}
                        <InstitutionalCard title="外資" data={inst.foreign} />
                        {/* 投信 */}
                        <InstitutionalCard title="投信" data={inst.trust} />
                        {/* 自營商 */}
                        <InstitutionalCard title="自營商" data={inst.dealer} />
                    </div>
                </div>
            )}

            {/* 融資融券分析 */}
            {margin.margin && margin.short && (
                <div>
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                        <DollarSign className="w-6 h-6" />
                        融資融券
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        {/* 融資卡片 */}
                        <MarginCard title="融資" data={margin.margin} />
                        {/* 融券卡片 */}
                        <MarginCard title="融券" data={margin.short} />
                    </div>

                    {/* 資券比與警示 */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">資券比</h3>
                            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                                {margin.ratio?.margin_short_ratio?.toFixed(2) || 0}
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                {margin.ratio?.interpretation || '中性'}
                            </p>
                        </div>

                        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                            <h3 className="font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                                <Info className="w-4 h-4" />
                                風險警示
                            </h3>
                            <div className="space-y-1">
                                {margin.signal?.warnings?.map((warning, idx) => (
                                    <p key={idx} className="text-sm text-yellow-600 dark:text-yellow-400">
                                        • {warning}
                                    </p>
                                )) || <p className="text-sm text-gray-500">無警示</p>}
                            </div>
                            <div className="mt-2">
                                <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${margin.signal?.risk_level === '高' ? 'bg-red-100 text-red-700' :
                                    margin.signal?.risk_level === '中' ? 'bg-yellow-100 text-yellow-700' :
                                        'bg-green-100 text-green-700'
                                    }`}>
                                    風險等級: {margin.signal?.risk_level || '低'}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

// 三大法人卡片組件
function InstitutionalCard({ title, data }) {
    if (!data) return null

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900 dark:text-white">{title}</h3>
                {data.trend === '買超' ? (
                    <TrendingUp className="w-5 h-5 text-green-500" />
                ) : (
                    <TrendingDown className="w-5 h-5 text-red-500" />
                )}
            </div>
            <div className="space-y-2">
                <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">買賣超:</span>
                    <span className={`font-semibold ${(data.net_shares || 0) > 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                        {(data.net_shares || 0) > 0 ? '+' : ''}{data.net_shares?.toLocaleString() || 0} 張
                    </span>
                </div>
                <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">金額:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                        {((data.net_value || 0) / 1000)?.toLocaleString(undefined, { maximumFractionDigits: 0 })} 千元
                    </span>
                </div>
                <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">連續天數:</span>
                    <span className={`font-semibold ${(data.consecutive_days || 0) > 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                        {(data.consecutive_days || 0) > 0 ? '+' : ''}{data.consecutive_days || 0} 天
                    </span>
                </div>
            </div>
        </div>
    )
}

// 融資融券卡片組件
function MarginCard({ title, data }) {
    if (!data) return null

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3">{title}</h3>
            <div className="space-y-3">
                <div>
                    <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600 dark:text-gray-400">使用率</span>
                        <span className="font-semibold text-gray-900 dark:text-white">
                            {data.usage_pct?.toFixed(1) || 0}%
                        </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                            className={`h-2 rounded-full ${(data.usage_pct || 0) > 80 ? 'bg-red-500' :
                                (data.usage_pct || 0) > 60 ? 'bg-yellow-500' : 'bg-green-500'
                                }`}
                            style={{ width: `${Math.min(data.usage_pct || 0, 100)}%` }}
                        ></div>
                    </div>
                </div>
                <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">餘額:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                        {data.balance?.toLocaleString() || 0} 張
                    </span>
                </div>
                <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">變化:</span>
                    <span className={`font-semibold ${(data.change || 0) > 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                        {(data.change || 0) > 0 ? '+' : ''}{data.change?.toLocaleString() || 0}
                        ({(data.change_pct || 0) > 0 ? '+' : ''}{data.change_pct?.toFixed(2) || 0}%)
                    </span>
                </div>
            </div>
        </div>
    )
}
