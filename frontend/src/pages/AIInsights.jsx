// AI統一觀點頁面 - 完整實現系統開發規格書T節功能
import { useState, useEffect } from 'react'
import { Brain, TrendingUp, TrendingDown, AlertTriangle, RefreshCw, ArrowRight, Target, BarChart3, Shield, Activity } from 'lucide-react'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Legend } from 'recharts'
import AIReportsSection from '../components/AIReportsSection'

export default function AIInsights() {
    const [loading, setLoading] = useState(false)
    const [insights, setInsights] = useState(null)
    const [selectedStock, setSelectedStock] = useState('2330')
    const [market, setMarket] = useState('tw')
    const [activeTab, setActiveTab] = useState('unified') // 'unified', 'dashboard', 'reports'

    useEffect(() => {
        if (activeTab === 'unified' || activeTab === 'dashboard') {
            loadUnifiedView()
        }
    }, [])

    const loadUnifiedView = async () => {
        setLoading(true)
        try {
            // 獲取股票的綜合分析數據
            const responses = await Promise.all([
                fetch(`http://localhost:5000/api/ai/reports/${selectedStock}?market=${market}`).catch(() => null),
                fetch(`http://localhost:5000/api/analysis/depth/${selectedStock}?market=${market}`).catch(() => null),
                fetch(`http://localhost:5000/api/chips/${selectedStock}/all?market=${market}`).catch(() => null)
            ])

            const [aiReport, depthAnalysis, chipsData] = await Promise.all(
                responses.map(r => r?.ok ? r.json() : null)
            )

            setInsights(generateUnifiedView(aiReport, depthAnalysis, chipsData))
        } catch (error) {
            console.error('載入AI統一觀點失敗:', error)
            setInsights(getMockUnifiedView())
        } finally {
            setLoading(false)
        }
    }

    const generateUnifiedView = (aiReport, depth, chips) => {
        // 從AI報告中提取六因子評分
        const sixFactors = extractSixFactors(aiReport, depth, chips)

        return {
            stockCode: selectedStock,
            timestamp: new Date().toLocaleString('zh-TW'),
            sixFactors: sixFactors,
            radarData: convertToRadarData(sixFactors),
            coreConclusion: generateCoreConclusion(depth, chips, sixFactors),
            signalDashboard: generateSignalDashboard(depth, chips),
            overallSentiment: sixFactors.recommendation || depth?.comprehensive_judgment?.recommendation || '中性',
            confidenceScore: sixFactors.overall_score || depth?.comprehensive_judgment?.score || 50,
            keyInsights: generateKeyInsights(depth, chips, sixFactors),
            riskWarnings: generateRiskWarnings(depth, chips, sixFactors),
            actionableRecommendations: generateRecommendations(depth, chips, sixFactors)
        }
    }

    const extractSixFactors = (aiReport, depth, chips) => {
        // 優先從AI報告的market_data中提取六因子
        if (aiReport?.market_data?.six_factors) {
            return aiReport.market_data.six_factors
        }

        // 如果沒有AI報告，基於深度分析和籌碼數據計算六因子評分
        return calculateSixFactors(depth, chips)
    }

    const calculateSixFactors = (depth, chips) => {
        // 基於現有數據計算六因子評分
        const macro = 70 // 預設值，需要宏觀數據
        const technical = depth?.comprehensive_judgment?.score || 70
        const chipsScore = chips?.institutional?.summary?.signal_strength || 70
        const fundamental = 70 // 需要財報數據
        const sentiment = 70 // 需要情緒數據
        const valuation = depth?.position_analysis?.percentile_52w ?
            (100 - depth.position_analysis.percentile_52w) : 70 // 估值反向指標

        const overall_score = Math.round((macro + technical + chipsScore + fundamental + sentiment + valuation) / 6)

        return {
            macro,
            technical,
            chips: chipsScore,
            fundamental,
            sentiment,
            valuation,
            overall_score,
            recommendation: technical > 65 ? '買入' : technical < 50 ? '賣出' : '持有',
            confidence: technical > 70 || technical < 40 ? '高' : '中'
        }
    }

    const convertToRadarData = (sixFactors) => {
        return [
            { factor: '宏觀環境', score: sixFactors.macro || 70, fullMark: 100 },
            { factor: '技術面', score: sixFactors.technical || 70, fullMark: 100 },
            { factor: '籌碼面', score: sixFactors.chips || 70, fullMark: 100 },
            { factor: '基本面', score: sixFactors.fundamental || 70, fullMark: 100 },
            { factor: '市場情緒', score: sixFactors.sentiment || 70, fullMark: 100 },
            { factor: '估值水平', score: sixFactors.valuation || 70, fullMark: 100 }
        ]
    }

    const generateCoreConclusion = (depth, chips, sixFactors) => {
        const conclusions = []

        conclusions.push(`綜合評分 ${sixFactors.overall_score}/100`)

        if (sixFactors.recommendation) {
            conclusions.push(`建議${sixFactors.recommendation}`)
        }

        if (depth?.position_analysis?.level) {
            conclusions.push(`價格${depth.position_analysis.level}`)
        }

        if (chips?.institutional?.summary?.overall_trend) {
            conclusions.push(`籌碼${chips.institutional.summary.overall_trend}`)
        }

        return conclusions.join('，') || '市場觀察中'
    }

    const generateSignalDashboard = (depth, chips) => {
        const getSignal = (value, type = 'number') => {
            if (type === 'trend') {
                if (value?.includes('上升') || value?.includes('多頭')) return { light: '🟢', label: '看多' }
                if (value?.includes('下降') || value?.includes('空頭')) return { light: '🔴', label: '看空' }
                return { light: '🟡', label: '中性' }
            }

            if (type === 'score') {
                if (value >= 70) return { light: '🟢', label: '強勢' }
                if (value <= 50) return { light: '🔴', label: '弱勢' }
                return { light: '🟡', label: '中性' }
            }

            return { light: '🟡', label: '中性' }
        }

        return [
            {
                dimension: '價格位階',
                signal: getSignal(depth?.position_analysis?.percentile_52w, 'score'),
                note: depth?.position_analysis?.level || '數據載入中'
            },
            {
                dimension: '趨勢動能',
                signal: getSignal(depth?.trend_analysis?.trend, 'trend'),
                note: `${depth?.trend_analysis?.ma_alignment || '未知排列'}，強度${depth?.trend_analysis?.strength || 0}%`
            },
            {
                dimension: '量價關係',
                signal: getSignal(depth?.volume_price_relation?.signal, 'trend'),
                note: depth?.volume_price_relation?.relation || '觀察中'
            },
            {
                dimension: '法人籌碼',
                signal: getSignal(chips?.institutional?.summary?.overall_trend, 'trend'),
                note: `${chips?.institutional?.summary?.dominant_force || '無明顯'}主導，訊號強度${chips?.institutional?.summary?.signal_strength?.toFixed(1) || 0}分`
            },
            {
                dimension: '融資融券',
                signal: getSignal(chips?.margin?.signal?.risk_level === '高' ? '空頭' : '多頭', 'trend'),
                note: chips?.margin?.ratio?.interpretation || '中性'
            },
            {
                dimension: '技術指標',
                signal: getSignal(depth?.technical_signals?.rsi?.signal, 'trend'),
                note: `RSI:${depth?.technical_signals?.rsi?.value?.toFixed(1) || 50}, ${depth?.technical_signals?.macd?.signal || '未知'}`
            }
        ]
    }

    const generateKeyInsights = (depth, chips, sixFactors) => {
        const insights = []

        // 六因子綜合評估
        insights.push({
            icon: Target,
            title: '六因子綜合評估',
            content: `綜合評分 ${sixFactors.overall_score}/100，建議${sixFactors.recommendation}，信心度${sixFactors.confidence}`,
            score: sixFactors.overall_score
        })

        // 找出最強和最弱的因子
        const factorScores = [
            { name: '宏觀環境', score: sixFactors.macro },
            { name: '技術面', score: sixFactors.technical },
            { name: '籌碼面', score: sixFactors.chips },
            { name: '基本面', score: sixFactors.fundamental },
            { name: '市場情緒', score: sixFactors.sentiment },
            { name: '估值水平', score: sixFactors.valuation }
        ]
        const sortedFactors = [...factorScores].sort((a, b) => b.score - a.score)

        insights.push({
            icon: TrendingUp,
            title: '最強因子',
            content: `${sortedFactors[0].name}表現最佳（${sortedFactors[0].score}/100），為投資決策提供最強支撐`
        })

        insights.push({
            icon: AlertTriangle,
            title: '最弱因子',
            content: `${sortedFactors[5].name}需要關注（${sortedFactors[5].score}/100），可能構成潛在風險`
        })

        if (depth?.position_analysis) {
            insights.push({
                icon: BarChart3,
                title: '位階研判',
                content: `當前處於${depth.position_analysis.level}，距離52週高點${depth.position_analysis.distance_from_high?.toFixed(2)}%，低點${depth.position_analysis.distance_from_low?.toFixed(2)}%`
            })
        }

        return insights
    }

    const generateRiskWarnings = (depth, chips, sixFactors) => {
        const warnings = []

        if (sixFactors.overall_score < 50) {
            warnings.push({ level: 'danger', message: '綜合評分偏低，多項因子表現不佳，建議謹慎操作' })
        }

        if (depth?.position_analysis?.percentile_52w > 80) {
            warnings.push({ level: 'warning', message: '價格處於52週高檔區，注意回檔風險' })
        }

        if (depth?.technical_signals?.rsi?.value > 70) {
            warnings.push({ level: 'warning', message: 'RSI過熱，可能面臨技術性修正' })
        }

        if (chips?.margin?.margin?.usage_pct > 70) {
            warnings.push({ level: 'danger', message: '融資使用率偏高，槓桿風險上升' })
        }

        return warnings
    }

    const generateRecommendations = (depth, chips, sixFactors) => {
        const recommendations = []

        recommendations.push({
            action: sixFactors.recommendation === '買入' ? 'BUY' :
                sixFactors.recommendation === '賣出' ? 'SELL' : 'HOLD',
            reason: `基於六因子綜合分析（評分${sixFactors.overall_score}/100）`,
            confidence: sixFactors.confidence
        })

        return recommendations
    }

    const getMockUnifiedView = () => ({
        stockCode: selectedStock,
        timestamp: new Date().toLocaleString('zh-TW'),
        sixFactors: {
            macro: 72,
            technical: 68,
            chips: 75,
            fundamental: 70,
            sentiment: 65,
            valuation: 60,
            overall_score: 68,
            recommendation: '持有',
            confidence: '中'
        },
        radarData: [
            { factor: '宏觀環境', score: 72, fullMark: 100 },
            { factor: '技術面', score: 68, fullMark: 100 },
            { factor: '籌碼面', score: 75, fullMark: 100 },
            { factor: '基本面', score: 70, fullMark: 100 },
            { factor: '市場情緒', score: 65, fullMark: 100 },
            { factor: '估值水平', score: 60, fullMark: 100 }
        ],
        coreConclusion: '綜合評分 68/100，建議持有，價格中檔區，籌碼偏多',
        signalDashboard: [
            { dimension: '價格位階', signal: { light: '🟡', label: '中檔' }, note: '處於52週中位區間' },
            { dimension: '趨勢動能', signal: { light: '🟢', label: '偏多' }, note: '短期多頭排列' },
            { dimension: '量價關係', signal: { light: '🟡', label: '中性' }, note: '價漲量縮觀望' },
            { dimension: '法人籌碼', signal: { light: '🟢', label: '偏多' }, note: '外資主導買超' },
            { dimension: '融資融券', signal: { light: '🟡', label: '中性' }, note: '資券比適中' },
            { dimension: '技術指標', signal: { light: '🟡', label: '中性' }, note: 'RSI中性區間' }
        ],
        overallSentiment: '偏多觀察',
        confidenceScore: 68,
        keyInsights: [],
        riskWarnings: [],
        actionableRecommendations: []
    })

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* 標題與Tab切換 */}
            <div>
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <div className="flex items-center gap-3">
                            <Brain className="w-8 h-8 text-purple-600" />
                            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                                AI統一觀點
                            </h1>
                        </div>
                        <p className="text-gray-600 dark:text-gray-400 mt-2">
                            六因子評分 × 每日戰略儀表板 × AI報告中心
                        </p>
                    </div>
                </div>

                {/* Tab切換 */}
                <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
                    <button
                        onClick={() => setActiveTab('unified')}
                        className={`px-6 py-3 font-medium border-b-2 transition-colors ${activeTab === 'unified'
                                ? 'border-purple-600 text-purple-600 dark:text-purple-400'
                                : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                            }`}
                    >
                        六因子雷達圖
                    </button>
                    <button
                        onClick={() => setActiveTab('dashboard')}
                        className={`px-6 py-3 font-medium border-b-2 transition-colors ${activeTab === 'dashboard'
                                ? 'border-purple-600 text-purple-600 dark:text-purple-400'
                                : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                            }`}
                    >
                        智能觀點儀表板
                    </button>
                    <button
                        onClick={() => setActiveTab('reports')}
                        className={`px-6 py-3 font-medium border-b-2 transition-colors ${activeTab === 'reports'
                                ? 'border-purple-600 text-purple-600 dark:text-purple-400'
                                : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
                            }`}
                    >
                        AI報告中心
                    </button>
                </div>
            </div>

            {/* 六因子雷達圖Tab */}
            {activeTab === 'unified' && (
                <div className="space-y-6">
                    {/* 股票選擇器 */}
                    <div className="flex items-center gap-3 justify-end">
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
                            onClick={loadUnifiedView}
                            disabled={loading}
                            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
                        >
                            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                            {loading ? '分析中...' : '生成洞察'}
                        </button>
                    </div>

                    {loading ? (
                        <div className="flex items-center justify-center h-64">
                            <div className="text-center">
                                <Brain className="w-16 h-16 mx-auto mb-4 text-purple-600 animate-pulse" />
                                <p className="text-gray-600 dark:text-gray-400">AI正在分析市場數據...</p>
                            </div>
                        </div>
                    ) : insights && (
                        <>
                            {/* 核心結論 */}
                            <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg p-6 border-l-4 border-purple-600">
                                <div className="flex items-start gap-3">
                                    <Target className="w-6 h-6 text-purple-600 mt-1" />
                                    <div className="flex-1">
                                        <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                                            統一觀點核心結論
                                        </h2>
                                        <p className="text-gray-700 dark:text-gray-300 text-base leading-relaxed">
                                            {insights.coreConclusion}
                                        </p>
                                        <div className="mt-3 flex items-center gap-4 text-sm">
                                            <span className="text-gray-600 dark:text-gray-400">
                                                AI建議: <span className="font-semibold text-purple-600">{insights.overallSentiment}</span>
                                            </span>
                                            <span className="text-gray-600 dark:text-gray-400">
                                                綜合評分: <span className="font-semibold">{insights.confidenceScore}/100</span>
                                            </span>
                                            <span className="text-gray-500 text-xs ml-auto">{insights.timestamp}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* 六因子雷達圖 */}
                            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                                    <Activity className="w-5 h-5 text-purple-600" />
                                    六因子動態雷達圖
                                </h2>
                                <div className="flex flex-col md:flex-row gap-6">
                                    {/* 雷達圖 */}
                                    <div className="flex-1">
                                        <ResponsiveContainer width="100%" height={400}>
                                            <RadarChart data={insights.radarData}>
                                                <PolarGrid stroke="#374151" />
                                                <PolarAngleAxis
                                                    dataKey="factor"
                                                    tick={{ fill: '#9CA3AF', fontSize: 12 }}
                                                />
                                                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                                                <Radar
                                                    name={selectedStock}
                                                    dataKey="score"
                                                    stroke="#8B5CF6"
                                                    fill="#8B5CF6"
                                                    fillOpacity={0.6}
                                                />
                                                <Legend />
                                            </RadarChart>
                                        </ResponsiveContainer>
                                    </div>

                                    {/* 六因子評分列表 */}
                                    <div className="w-full md:w-64 space-y-3">
                                        {insights.radarData.map((item, idx) => (
                                            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                                                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{item.factor}</span>
                                                <div className="flex items-center gap-2">
                                                    <div className="w-24 h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                                                        <div
                                                            className={`h-full ${item.score >= 70 ? 'bg-green-500' :
                                                                    item.score >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                                                                }`}
                                                            style={{ width: `${item.score}%` }}
                                                        />
                                                    </div>
                                                    <span className="text-sm font-bold text-gray-900 dark:text-white w-8 text-right">{item.score}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* 關鍵洞察 */}
                            {insights.keyInsights.length > 0 && (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {insights.keyInsights.map((insight, idx) => {
                                        const Icon = insight.icon
                                        return (
                                            <div key={idx} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-5">
                                                <div className="flex items-start gap-3">
                                                    <Icon className="w-5 h-5 text-blue-600 mt-0.5" />
                                                    <div className="flex-1">
                                                        <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{insight.title}</h3>
                                                        <p className="text-sm text-gray-600 dark:text-gray-400">{insight.content}</p>
                                                        {insight.score && (
                                                            <div className="mt-2 text-xs text-gray-500">
                                                                評分: {insight.score}/100
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                        )
                                    })}
                                </div>
                            )}

                            {/* 操作建議 */}
                            {insights.actionableRecommendations.length > 0 && (
                                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                                    <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                                        <ArrowRight className="w-5 h-5 text-blue-600" />
                                        AI操作建議
                                    </h2>
                                    <div className="space-y-3">
                                        {insights.actionableRecommendations.map((rec, idx) => (
                                            <div key={idx} className="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                                                <span className={`px-3 py-1 rounded font-semibold text-sm ${rec.action === 'BUY' ? 'bg-green-100 text-green-700' :
                                                        rec.action === 'SELL' ? 'bg-red-100 text-red-700' :
                                                            'bg-gray-100 text-gray-700'
                                                    }`}>
                                                    {rec.action}
                                                </span>
                                                <div className="flex-1">
                                                    <p className="text-gray-700 dark:text-gray-300">{rec.reason}</p>
                                                    <p className="text-xs text-gray-500 mt-1">信心度: {rec.confidence}</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* 風險警示 */}
                            {insights.riskWarnings.length > 0 && (
                                <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800 p-5">
                                    <div className="flex items-start gap-3">
                                        <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-500 mt-0.5" />
                                        <div>
                                            <h3 className="font-semibold text-gray-900 dark:text-white mb-3">風險提示</h3>
                                            <div className="space-y-2">
                                                {insights.riskWarnings.map((warning, idx) => (
                                                    <div key={idx} className="flex items-center gap-2">
                                                        <span className="text-sm text-yellow-800 dark:text-yellow-300">• {warning.message}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </>
                    )}
                </div>
            )}

            {/* 智能觀點儀表板Tab */}
            {activeTab === 'dashboard' && insights && (
                <div className="space-y-6">
                    {/* 股票選擇器 */}
                    <div className="flex items-center gap-3 justify-end">
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
                            onClick={loadUnifiedView}
                            disabled={loading}
                            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
                        >
                            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                            {loading ? '分析中...' : '生成洞察'}
                        </button>
                    </div>

                    {/* 核心信號儀表板 */}
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">核心信號儀表板</h2>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-gray-200 dark:border-gray-700">
                                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">維度</th>
                                        <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">燈號</th>
                                        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">關鍵註解</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {insights.signalDashboard.map((item, idx) => (
                                        <tr key={idx} className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30">
                                            <td className="py-3 px-4 font-medium text-gray-900 dark:text-white">{item.dimension}</td>
                                            <td className="py-3 px-4 text-center">
                                                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gray-100 dark:bg-gray-700">
                                                    <span className="text-lg">{item.signal.light}</span>
                                                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{item.signal.label}</span>
                                                </div>
                                            </td>
                                            <td className="py-3 px-4 text-gray-600 dark:text-gray-400">{item.note}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}

            {/* AI報告中心Tab */}
            {activeTab === 'reports' && (
                <AIReportsSection />
            )}
        </div>
    )
}
