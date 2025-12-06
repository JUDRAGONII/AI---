// 市場脈搏綜合儀表板
// 整合宏觀、匯率、週期、情緒分析
import { useState, useEffect } from 'react'
import { Activity, TrendingUp, TrendingDown, Heart, RefreshCw, AlertCircle, CheckCircle, XCircle } from 'lucide-react'

export default function MarketPulse() {
    const [loading, setLoading] = useState(false)
    const [market, setMarket] = useState('tw')
    const [pulseData, setPulseData] = useState(null)

    useEffect(() => {
        loadMarketPulse()
    }, [market])

    const loadMarketPulse = async () => {
        setLoading(true)
        try {
            const response = await fetch(`http://localhost:5000/api/analysis/market_pulse?market=${market}`)
            const result = await response.json()

            if (result.success) {
                setPulseData(result.data)
            }
        } catch (error) {
            console.error('載入市場脈搏失敗:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <Heart className="w-16 h-16 mx-auto mb-4 text-red-500 animate-pulse" />
                    <p className="text-gray-600 dark:text-gray-400">偵測市場脈搏...</p>
                </div>
            </div>
        )
    }

    if (!pulseData) return null

    const { cycle_analysis, sentiment_analysis, market_health } = pulseData

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* 標題 */}
            <div className="flex items-center justify-between">
                <div>
                    <div className="flex items-center gap-3">
                        <Heart className="w-8 h-8 text-red-500" />
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                            市場脈搏
                        </h1>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        週期定位 × 情緒晴雨錶 × 綜合健康度
                    </p>
                </div>

                <div className="flex items-center gap-3">
                    <select
                        value={market}
                        onChange={(e) => setMarket(e.target.value)}
                        className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                    >
                        <option value="tw">台灣市場</option>
                        <option value="us">美國市場</option>
                    </select>
                    <button
                        onClick={loadMarketPulse}
                        className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 flex items-center gap-2"
                    >
                        <RefreshCw className="w-4 h-4" />
                        刷新
                    </button>
                </div>
            </div>

            {/* 市場健康度總覽 */}
            <div className="bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/20 dark:to-pink-900/20 rounded-lg p-8 border-l-4 border-red-500">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                            市場整體健康度
                        </h2>
                        <p className="text-gray-600 dark:text-gray-400">{market_health.interpretation}</p>
                    </div>
                    <div className="text-center">
                        <div className="text-6xl font-bold text-red-500">{market_health.score}</div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">健康評分</div>
                        <div className={`mt-3 px-4 py-2 rounded-full font-semibold ${market_health.signal === 'positive' ? 'bg-green-100 text-green-700' :
                                market_health.signal === 'negative' ? 'bg-red-100 text-red-700' :
                                    'bg-yellow-100 text-yellow-700'
                            }`}>
                            {market_health.status}
                        </div>
                    </div>
                </div>
            </div>

            {/* 週期與情緒雙欄 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 週期分析 */}
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-blue-600" />
                        週期定位
                    </h3>

                    <div className="space-y-4">
                        {/* 經濟週期 */}
                        <CycleCard
                            label="經濟週期"
                            stage={cycle_analysis.經濟週期.當前階段}
                            position={cycle_analysis.經濟週期.週期位置}
                            recommendation={cycle_analysis.經濟週期.投資建議}
                        />

                        {/* 股市週期 */}
                        <CycleCard
                            label="股市週期"
                            stage={cycle_analysis.股市週期.當前階段}
                            temperature={cycle_analysis.股市週期.市場溫度}
                            recommendation={cycle_analysis.股市週期.建議}
                        />

                        {/* 綜合評估 */}
                        <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">綜合評分</span>
                                <span className="text-2xl font-bold text-blue-600">{cycle_analysis.綜合評估.綜合評分}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-600 dark:text-gray-400">投資策略</span>
                                <span className={`px-3 py-1 rounded text-sm font-semibold ${cycle_analysis.綜合評估.風險等級 === 'low' ? 'bg-green-100 text-green-700' :
                                        cycle_analysis.綜合評估.風險等級 === 'high' ? 'bg-red-100 text-red-700' :
                                            'bg-yellow-100 text-yellow-700'
                                    }`}>
                                    {cycle_analysis.綜合評估.投資策略}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 情緒分析 */}
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                        <Heart className="w-5 h-5 text-red-500" />
                        情緒晴雨錶
                    </h3>

                    <div className="space-y-4">
                        {/* 恐懼貪婪指數 */}
                        <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg">
                            <div className="flex items-center justify-between mb-3">
                                <span className="font-semibold text-gray-900 dark:text-white">恐懼貪婪指數</span>
                                <span className="text-3xl font-bold text-purple-600">
                                    {sentiment_analysis.恐懼貪婪指數.指數}
                                </span>
                            </div>
                            <div className="mb-3">
                                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500"
                                        style={{ width: `${sentiment_analysis.恐懼貪婪指數.指數}%` }}
                                    />
                                </div>
                                <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mt-1">
                                    <span>極度恐懼</span>
                                    <span>中性</span>
                                    <span>極度貪婪</span>
                                </div>
                            </div>
                            <div className={`px-3 py-2 rounded text-center font-semibold ${sentiment_analysis.恐懼貪婪指數.信號.includes('fear') ? 'bg-blue-100 text-blue-700' :
                                    sentiment_analysis.恐懼貪婪指數.信號.includes('greed') ? 'bg-red-100 text-red-700' :
                                        'bg-gray-100 text-gray-700'
                                }`}>
                                {sentiment_analysis.恐懼貪婪指數.等級}
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 text-center">
                                {sentiment_analysis.恐懼貪婪指數.建議}
                            </p>
                        </div>

                        {/* VIX指數 */}
                        <SentimentIndicator
                            label="VIX恐慌指數"
                            value={sentiment_analysis.VIX恐慌指數.VIX數值}
                            level={sentiment_analysis.VIX恐慌指數.情緒等級}
                            signal={sentiment_analysis.VIX恐慌指數.投資建議}
                        />

                        {/* Put/Call比率 */}
                        <SentimentIndicator
                            label="Put/Call比率"
                            value={sentiment_analysis['Put/Call比率']['Put/Call比率']}
                            level={sentiment_analysis['Put/Call比率'].市場看法}
                            signal={sentiment_analysis['Put/Call比率'].操作建議}
                        />

                        {/* 融資餘額 */}
                        <SentimentIndicator
                            label="融資使用率"
                            value={`${sentiment_analysis.融資餘額.使用率}%`}
                            level={sentiment_analysis.融資餘額.水位評估}
                            signal={sentiment_analysis.融資餘額.風險等級}
                        />
                    </div>
                </div>
            </div>

            {/* 綜合操作建議 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-orange-500" />
                    綜合操作建議
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <RecommendationCard
                        title="倉位建議"
                        content={sentiment_analysis.綜合建議.倉位建議}
                        icon={<Activity className="w-5 h-5" />}
                    />
                    <RecommendationCard
                        title="操作方向"
                        content={sentiment_analysis.綜合建議.操作方向}
                        icon={sentiment_analysis.綜合建議.操作方向 === '加碼' ? <TrendingUp className="w-5 h-5" /> :
                            sentiment_analysis.綜合建議.操作方向 === '減碼' ? <TrendingDown className="w-5 h-5" /> :
                                <Activity className="w-5 h-5" />}
                    />
                    <RecommendationCard
                        title="風險等級"
                        content={sentiment_analysis.綜合建議.風險等級}
                        icon={sentiment_analysis.綜合建議.風險等級 === '低' ? <CheckCircle className="w-5 h-5" /> :
                            sentiment_analysis.綜合建議.風險等級 === '高' ? <XCircle className="w-5 h-5" /> :
                                <AlertCircle className="w-5 h-5" />}
                    />
                </div>

                <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                        <strong>理由：</strong>{sentiment_analysis.綜合建議.理由}
                    </p>
                </div>
            </div>
        </div>
    )
}

function CycleCard({ label, stage, position, temperature, recommendation }) {
    return (
        <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{label}</div>
            <div className="text-lg font-bold text-gray-900 dark:text-white mb-1">{stage}</div>
            {position && <div className="text-xs text-gray-600 dark:text-gray-400">位置: {position}</div>}
            {temperature !== undefined && <div className="text-xs text-gray-600 dark:text-gray-400">溫度: {temperature}/100</div>}
            {recommendation && <div className="text-xs text-blue-600 dark:text-blue-400 mt-2">{recommendation}</div>}
        </div>
    )
}

function SentimentIndicator({ label, value, level, signal }) {
    return (
        <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div>
                <div className="text-sm text-gray-600 dark:text-gray-400">{label}</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">{value}</div>
            </div>
            <div className="text-right">
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">{level}</div>
                <div className="text-xs text-gray-500">{signal}</div>
            </div>
        </div>
    )
}

function RecommendationCard({ title, content, icon }) {
    return (
        <div className="p-4 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700/50 dark:to-gray-800/50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
                <div className="text-blue-600">{icon}</div>
                <div className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</div>
            </div>
            <div className="text-xl font-bold text-gray-900 dark:text-white">{content}</div>
        </div>
    )
}
