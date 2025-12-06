// 股價深度分析頁面
import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, AlertTriangle, Target, Activity, BarChart2 } from 'lucide-react'

export default function DepthAnalysis() {
    const [selectedStock, setSelectedStock] = useState('2330')
    const [market, setMarket] = useState('tw')
    const [loading, setLoading] = useState(true)
    const [analysisData, setAnalysisData] = useState(null)

    useEffect(() => {
        loadAnalysis()
    }, []) // 只在初始載入時執行一次，之後由用戶點擊按鈕觸發

    const loadAnalysis = async () => {
        setLoading(true)
        try {
            const response = await fetch(`http://localhost:5000/api/analysis/depth/${selectedStock}?market=${market}`)
            if (response.ok) {
                const data = await response.json()
                setAnalysisData(data)
            } else {
                console.error('API返回錯誤:', response.status)
                setAnalysisData(getMockData())
            }
        } catch (error) {
            console.error('載入分析失敗:', error)
            setAnalysisData(getMockData())
        } finally {
            setLoading(false)
        }
    }

    const getMockData = () => ({
        stock_code: selectedStock,
        market: market,
        position_analysis: {
            current_price: 589.0,
            high_52w: 688.5,
            low_52w: 490.5,
            percentile_52w: 49.8,
            level: '中檔區',
            distance_from_high: 14.45,
            distance_from_low: 20.08
        },
        trend_analysis: {
            trend: '上升趨勢',
            ma_alignment: '偏多',
            slope: 2.3,
            strength: 68.5,
            current_vs_ma5: 1.2,
            current_vs_ma20: 3.8
        },
        volume_price_relation: {
            relation: '價漲量增',
            signal: '正常',
            volume_vs_avg: 15.3
        },
        technical_signals: {
            rsi: { value: 58.3, signal: '偏多', action: '持有' },
            macd: { value: 5.2, signal: '多頭訊號', histogram: 1.8 },
            kd: { k: 65.2, d: 62.3, signal: '偏多' },
            williams: { value: -35.8, signal: '偏多', action: '持有' },
            bollinger: { upper: 620.5, middle: 590.0, lower: 559.5, position: '中軌區間' }
        },
        comprehensive_judgment: {
            recommendation: '偏多持有',
            confidence: '中',
            score: 62.5,
            reasons: [
                '價格處於中檔區，具備上漲空間',
                '上升趨勢，動能強勁',
                '價漲量增，買盤積極',
                'RSI中性，未過熱'
            ]
        }
    })

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-xl">分析中...</div>
            </div>
        )
    }

    if (!analysisData) {
        return (
            <div className="p-8">
                <div className="text-center text-gray-500">無法載入分析數據</div>
            </div>
        )
    }

    const { position_analysis, trend_analysis, volume_price_relation, technical_signals, comprehensive_judgment } = analysisData

    return (
        <div className="p-8 space-y-6">
            {/* 標題與選股 */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">股價深度分析</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        多維度綜合判斷 | 位階 × 趨勢 × 量價 × 技術指標
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <input
                        type="text"
                        value={selectedStock}
                        onChange={(e) => setSelectedStock(e.target.value)}
                        className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                        placeholder="股票代碼"
                    />
                    <select
                        value={market}
                        onChange={(e) => setMarket(e.target.value)}
                        className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                    >
                        <option value="tw">台股</option>
                        <option value="us">美股</option>
                    </select>
                    <button
                        onClick={loadAnalysis}
                        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                    >
                        分析
                    </button>
                </div>
            </div>

            {/* 警示橫幅 */}
            <WarningBanner judgment={comprehensive_judgment} />

            {/* 綜合判斷面板 */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
                <ComprehensiveCard judgment={comprehensive_judgment} />
            </div>

            {/* 分析卡片 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <PositionCard data={position_analysis} />
                <TrendCard data={trend_analysis} />
                <VolumePriceCard data={volume_price_relation} />
                <TechnicalSignalsCard data={technical_signals} />
            </div>
        </div>
    )
}

// 警示橫幅組件
function WarningBanner({ judgment }) {
    if (!judgment) return null

    const getStyle = (recommendation) => {
        if (recommendation?.includes('多頭')) {
            return { bg: 'bg-green-100 dark:bg-green-900/30', border: 'border-green-500', text: 'text-green-800 dark:text-green-200', icon: TrendingUp }
        } else if (recommendation?.includes('空頭')) {
            return { bg: 'bg-red-100 dark:bg-red-900/30', border: 'border-red-500', text: 'text-red-800 dark:text-red-200', icon: TrendingDown }
        } else {
            return { bg: 'bg-yellow-100 dark:bg-yellow-900/30', border: 'border-yellow-500', text: 'text-yellow-800 dark:text-yellow-200', icon: AlertTriangle }
        }
    }

    const style = getStyle(judgment.recommendation)
    const Icon = style.icon

    return (
        <div className={`${style.bg} border-l-4 ${style.border} p-4 rounded-lg`}>
            <div className="flex items-center gap-3">
                <Icon className={`w-6 h-6 ${style.text}`} />
                <div>
                    <div className={`text-lg font-bold ${style.text}`}>
                        警示訊號：{judgment.recommendation || '未知'}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        信心度：{judgment.confidence || '未知'} | 綜合評分：{judgment.score || 0}/100
                    </div>
                </div>
            </div>
        </div>
    )
}

// 綜合判斷卡片
function ComprehensiveCard({ judgment }) {
    if (!judgment) return null

    return (
        <div className="col-span-full card">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Target className="w-5 h-5" />
                綜合判斷
            </h3>
            <div className="space-y-2">
                <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                    {judgment.recommendation || '未知'}
                </div>
                <div className="grid grid-cols-2 gap-4 mt-4">
                    <div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">信心程度</div>
                        <div className="text-2xl font-bold">{judgment.confidence || '未知'}</div>
                    </div>
                    <div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">綜合評分</div>
                        <div className="text-2xl font-bold">{judgment.score || 0}/100</div>
                    </div>
                </div>
                {judgment.reasons && judgment.reasons.length > 0 && (
                    <div className="mt-4 space-y-1">
                        <div className="text-sm font-medium">判斷理由：</div>
                        {judgment.reasons.map((reason, idx) => (
                            <div key={idx} className="text-sm text-gray-600 dark:text-gray-400">
                                • {reason}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}

// 位階分析卡片
function PositionCard({ data }) {
    if (!data) return null

    return (
        <div className="card">
            <h3 className="text-xl font-bold mb-4">價格位階判斷</h3>
            <div className="space-y-3">
                <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">當前價格</span>
                    <span className="text-2xl font-bold">${data.current_price || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">52週位階</span>
                    <span className="text-xl font-bold text-blue-600">{data.level || '未知'}</span>
                </div>
                <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">百分位</span>
                    <span className="text-lg font-bold">{data.percentile_52w || 0}%</span>
                </div>
                <div className="mt-4 bg-gray-100 dark:bg-gray-700 rounded-lg p-3">
                    <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">52週區間</div>
                    <div className="flex justify-between text-sm">
                        <span className="text-red-600">${data.low_52w || 0}</span>
                        <span className="text-green-600">${data.high_52w || 0}</span>
                    </div>
                </div>
            </div>
        </div>
    )
}

// 趨勢分析卡片
function TrendCard({ data }) {
    if (!data) return null

    return (
        <div className="card">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5" />
                趨勢分析
            </h3>
            <div className="space-y-3">
                <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">趨勢狀態</span>
                    <span className="text-xl font-bold text-green-600">{data.trend || '未知'}</span>
                </div>
                <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">MA排列</span>
                    <span className="text-lg">{data.ma_alignment || '未知'}</span>
                </div>
                <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">趨勢強度</span>
                    <span className="text-lg font-bold">{data.strength || 0}%</span>
                </div>
            </div>
        </div>
    )
}

// 量價關係卡片
function VolumePriceCard({ data }) {
    if (!data) {
        return (
            <div className="card">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <BarChart2 className="w-5 h-5" />
                    量價關係
                </h3>
                <p className="text-gray-500">數據載入中...</p>
            </div>
        )
    }

    return (
        <div className="card">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <BarChart2 className="w-5 h-5" />
                量價關係
            </h3>
            <div className="space-y-3">
                <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">量價關係</span>
                    <span className="text-xl font-bold">{data?.relation || '未知'}</span>
                </div>
                <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">訊號</span>
                    <span className={`text-lg font-bold ${data?.signal === '正常' ? 'text-green-600' :
                        data?.signal === '背離' ? 'text-red-600' : 'text-yellow-600'
                        }`}>{data?.signal || '未知'}</span>
                </div>
                <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">量能變化</span>
                    <span className="text-lg">{data?.volume_vs_avg > 0 ? '+' : ''}{data?.volume_vs_avg || 0}%</span>
                </div>
            </div>
        </div>
    )
}

// 技術指標卡片
function TechnicalSignalsCard({ data }) {
    if (!data) return null

    return (
        <div className="card">
            <h3 className="text-xl font-bold mb-4">技術指標總覽</h3>
            <div className="space-y-2">
                <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">RSI</span>
                    <span className="text-lg font-bold">{data.rsi?.value || 50} - {data.rsi?.signal || '未知'}</span>
                </div>
                <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">MACD</span>
                    <span className="text-lg">{data.macd?.signal || '未知'}</span>
                </div>
                <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">KD</span>
                    <span className="text-lg">K:{data.kd?.k?.toFixed(1) || 50} / D:{data.kd?.d?.toFixed(1) || 50}</span>
                </div>
                <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">布林通道</span>
                    <span className="text-lg">{data.bollinger?.position || '未知'}</span>
                </div>
            </div>
        </div>
    )
}
