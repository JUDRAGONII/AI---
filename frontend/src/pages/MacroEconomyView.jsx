// 宏觀經濟與匯率分析頁面
import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, DollarSign, Globe, Activity, AlertCircle, RefreshCw, ArrowUpDown } from 'lucide-react'

export default function MacroEconomyView() {
    const [loading, setLoading] = useState(false)
    const [market, setMarket] = useState('tw')
    const [macroData, setMacroData] = useState(null)

    useEffect(() => {
        loadMacroData()
    }, [market])

    const loadMacroData = async () => {
        setLoading(true)
        try {
            const response = await fetch(`http://localhost:5000/api/macro/combined?market=${market}`)
            const result = await response.json()

            if (result.success) {
                setMacroData(result.data)
            }
        } catch (error) {
            console.error('載入宏觀數據失敗:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <RefreshCw className="w-12 h-12 mx-auto mb-4 text-blue-600 animate-spin" />
                    <p className="text-gray-600 dark:text-gray-400">載入宏觀數據...</p>
                </div>
            </div>
        )
    }

    if (!macroData) return null

    const { economy, forex } = macroData
    const primaryEconomy = economy.primary_economy
    const forexData = forex

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* 標題 */}
            <div className="flex items-center justify-between">
                <div>
                    <div className="flex items-center gap-3">
                        <Globe className="w-8 h-8 text-blue-600" />
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                            總體經濟環境掃描
                        </h1>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        宏觀經濟指標 × 匯率監控 × 市場影響評估
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
                        onClick={loadMacroData}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                    >
                        <RefreshCw className="w-4 h-4" />
                        刷新
                    </button>
                </div>
            </div>

            {/* 綜合評估卡片 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-6 border-l-4 border-blue-600">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white">經濟環境評估</h3>
                        <Activity className="w-6 h-6 text-blue-600" />
                    </div>
                    <div className="space-y-3">
                        <div>
                            <div className="text-3xl font-bold text-blue-600">{economy.overall_sentiment.score}/100</div>
                            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                {economy.overall_sentiment.interpretation}
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${economy.overall_sentiment.signal === 'positive' ? 'bg-green-100 text-green-700' :
                                    economy.overall_sentiment.signal === 'negative' ? 'bg-red-100 text-red-700' :
                                        'bg-yellow-100 text-yellow-700'
                                }`}>
                                {economy.overall_sentiment.sentiment}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg p-6 border-l-4 border-green-600">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white">匯率環境評估</h3>
                        <DollarSign className="w-6 h-6 text-green-600" />
                    </div>
                    <div className="space-y-3">
                        <div>
                            <div className="text-3xl font-bold text-green-600">{forexData.綜合評估.評分}/100</div>
                            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                {forexData.綜合評估.說明}
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${forexData.綜合評估.判斷 === '有利' ? 'bg-green-100 text-green-700' :
                                    forexData.綜合評估.判斷 === '不利' ? 'bg-red-100 text-red-700' :
                                        'bg-yellow-100 text-yellow-700'
                                }`}>
                                {forexData.綜合評估.判斷}
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* 經濟指標詳情 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-blue-600" />
                    {market === 'tw' ? '台灣經濟指標' : '美國經濟指標'}
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {market === 'tw' ? (
                        <>
                            <IndicatorCard
                                label="景氣對策信號"
                                value={primaryEconomy.景氣對策信號.燈號}
                                subtitle={`分數: ${primaryEconomy.景氣對策信號.分數}`}
                                trend={primaryEconomy.景氣對策信號.趨勢}
                            />
                            <IndicatorCard
                                label="CPI年增率"
                                value={`${primaryEconomy.CPI年增率.數值}%`}
                                subtitle={primaryEconomy.CPI年增率.評估}
                                trend={primaryEconomy.CPI年增率.趨勢}
                            />
                            <IndicatorCard
                                label="GDP成長率"
                                value={`${primaryEconomy.GDP成長率.數值}%`}
                                subtitle={primaryEconomy.GDP成長率.期間}
                                trend={primaryEconomy.GDP成長率.趨勢}
                            />
                            <IndicatorCard
                                label="外銷訂單"
                                value={`${primaryEconomy.外銷訂單.年增率}%`}
                                subtitle={primaryEconomy.外銷訂單.評估}
                                trend={primaryEconomy.外銷訂單.趨勢}
                            />
                            <IndicatorCard
                                label="央行利率"
                                value={`${primaryEconomy.央行利率.重貼現率}%`}
                                subtitle={primaryEconomy.央行利率.最新決策}
                                trend={primaryEconomy.央行利率.政策傾向}
                            />
                        </>
                    ) : (
                        <>
                            <IndicatorCard
                                label="Core PCE"
                                value={`${primaryEconomy.Core_PCE.年增率}%`}
                                subtitle={primaryEconomy.Core_PCE.評估}
                                trend={primaryEconomy.Core_PCE.趨勢}
                            />
                            <IndicatorCard
                                label="CPI"
                                value={`${primaryEconomy.CPI.年增率}%`}
                                subtitle={`核心: ${primaryEconomy.CPI.核心CPI}%`}
                                trend={primaryEconomy.CPI.趨勢}
                            />
                            <IndicatorCard
                                label="GDP成長率"
                                value={`${primaryEconomy.GDP成長率.數值}%`}
                                subtitle={primaryEconomy.GDP成長率.期間}
                                trend={primaryEconomy.GDP成長率.趨勢}
                            />
                            <IndicatorCard
                                label="非農就業"
                                value={`+${(primaryEconomy.非農就業.新增人數 / 1000).toFixed(0)}K`}
                                subtitle={`失業率: ${primaryEconomy.非農就業.失業率}%`}
                                trend={primaryEconomy.非農就業.評估}
                            />
                            <IndicatorCard
                                label="聯準會利率"
                                value={`${primaryEconomy.聯準會政策.聯邦基準利率}%`}
                                subtitle={primaryEconomy.聯準會政策.政策傾向}
                                trend={primaryEconomy.聯準會政策.FOMC最新聲明}
                            />
                        </>
                    )}
                </div>
            </div>

            {/* 匯率分析 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <ArrowUpDown className="w-5 h-5 text-green-600" />
                    USD/TWD 匯率監控
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                    {/* 當前匯率 */}
                    <div className="text-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">當前匯率</div>
                        <div className="text-3xl font-bold text-gray-900 dark:text-white">{forexData.當前匯率.rate}</div>
                        <div className="text-xs text-gray-500 mt-2">Bid: {forexData.當前匯率.bid} | Ask: {forexData.當前匯率.ask}</div>
                    </div>

                    {/* 趨勢判斷 */}
                    <div className="text-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">趨勢判斷</div>
                        <div className={`text-2xl font-bold ${forexData.趨勢分析.trend_signal === 'depreciation' ? 'text-red-600' :
                                forexData.趨勢分析.trend_signal === 'appreciation' ? 'text-green-600' :
                                    'text-yellow-600'
                            }`}>
                            {forexData.趨勢分析.趨勢判斷}
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mt-2">
                            20日變化: {forexData.趨勢分析.中期趨勢.變化率}%
                        </div>
                    </div>

                    {/* 美台利差 */}
                    <div className="text-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">美台利差</div>
                        <div className="text-3xl font-bold text-blue-600">{forexData.美台利差分析.利差}%</div>
                        <div className="text-xs text-gray-600 dark:text-gray-400 mt-2">{forexData.美台利差分析.利差狀態}</div>
                    </div>
                </div>

                {/* 技術面關鍵位 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                            <TrendingDown className="w-4 h-4 text-green-600" />
                            下檔支撐
                        </h3>
                        <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400">支撐1</span>
                                <span className="font-medium">{forexData.技術面關鍵位.下檔支撐.支撐1}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400">支撐2</span>
                                <span className="font-medium">{forexData.技術面關鍵位.下檔支撐.支撐2}</span>
                            </div>
                        </div>
                    </div>

                    <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-red-600" />
                            上檔壓力
                        </h3>
                        <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400">壓力1</span>
                                <span className="font-medium">{forexData.技術面關鍵位.上檔壓力.壓力1}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-600 dark:text-gray-400">壓力2</span>
                                <span className="font-medium">{forexData.技術面關鍵位.上檔壓力.壓力2}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* 市場影響評估 */}
            <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800 p-6">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                    <AlertCircle className="w-5 h-5 text-yellow-600" />
                    股市影響評估
                </h3>
                <div className="space-y-3">
                    <div className="flex items-center gap-4">
                        <span className="text-sm text-gray-600 dark:text-gray-400 w-24">整體影響:</span>
                        <span className={`px-3 py-1 rounded font-semibold ${forexData.股市影響評估.整體影響.includes('正面') ? 'bg-green-100 text-green-700' :
                                forexData.股市影響評估.整體影響.includes('負面') ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-700'
                            }`}>
                            {forexData.股市影響評估.整體影響}
                        </span>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300">{forexData.股市影響評估.說明}</p>
                    {forexData.股市影響評估.受惠產業 && forexData.股市影響評估.受惠產業.length > 0 && (
                        <div className="text-sm">
                            <span className="text-gray-600 dark:text-gray-400">受惠產業: </span>
                            <span className="text-gray-900 dark:text-white">{forexData.股市影響評估.受惠產業.join('、')}</span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

function IndicatorCard({ label, value, subtitle, trend }) {
    return (
        <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{label}</div>
            <div className="text-xl font-bold text-gray-900 dark:text-white mb-1">{value}</div>
            <div className="text-xs text-gray-500">{subtitle}</div>
            {trend && (
                <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                    趨勢: {trend}
                </div>
            )}
        </div>
    )
}
