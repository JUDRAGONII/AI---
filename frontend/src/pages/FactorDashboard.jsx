// 因子投資儀表板 (Factor Dashboard)
// 展示六大因子分析，包含雷達圖、歷史趨勢、因子曝險等
import { useState, useEffect } from 'react'
import {
    RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { TrendingUp, TrendingDown, Target, Award } from 'lucide-react'
import { db } from '../supabase'

export default function FactorDashboard() {
    const [stockCode, setStockCode] = useState('2330')
    const [loading, setLoading] = useState(true)
    const [factorScores, setFactorScores] = useState(null)
    const [latestScore, setLatestScore] = useState(null)
    const [historicalData, setHistoricalData] = useState([])

    useEffect(() => {
        loadFactorData()
    }, [stockCode])

    const loadFactorData = async () => {
        setLoading(true)
        try {
            // 從資料庫獲取因子分數
            const data = await db.queryFactorScores(stockCode, 30)

            if (data && data.length > 0) {
                setFactorScores(data)
                setLatestScore(data[0])

                // 準備歷史趨勢資料（反轉為從舊到新）
                const reversed = [...data].reverse()
                setHistoricalData(reversed)
            }
        } catch (error) {
            console.error('載入因子資料失敗:', error)
        } finally {
            setLoading(false)
        }
    }

    // 準備雷達圖資料
    const prepareRadarData = (score) => {
        if (!score) return []

        return [
            { factor: '價值', score: score.value_score || 50, fullMark: 100 },
            { factor: '品質', score: score.quality_score || 50, fullMark: 100 },
            { factor: '動能', score: score.momentum_score || 50, fullMark: 100 },
            { factor: '規模', score: score.size_score || 50, fullMark: 100 },
            { factor: '波動率', score: score.volatility_score || 50, fullMark: 100 },
            { factor: '成長', score: score.growth_score || 50, fullMark: 100 },
        ]
    }

    // 因子評級
    const getFactorRating = (score) => {
        if (score >= 80) return { label: '優秀', color: 'green', icon: <Award className="w-4 h-4" /> }
        if (score >= 70) return { label: '良好', color: 'blue', icon: <TrendingUp className="w-4 h-4" /> }
        if (score >= 50) return { label: '中等', color: 'yellow', icon: <Target className="w-4 h-4" /> }
        return { label: '偏弱', color: 'red', icon: <TrendingDown className="w-4 h-4" /> }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-xl">載入中...</div>
            </div>
        )
    }

    const radarData = prepareRadarData(latestScore)

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">因子投資儀表板</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        六大因子綜合分析 | 量化投資決策依據
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
                    <button onClick={loadFactorData} className="btn btn-primary">
                        查詢
                    </button>
                </div>
            </div>

            {factorScores ? (
                <>
                    {/* 總分與評級 */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-7 gap-6">
                        {/* 總分 */}
                        <div className="lg:col-span-2 card bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30 border-blue-200 dark:border-blue-700">
                            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                                綜合分數
                            </h3>
                            <div className="text-5xl font-bold text-blue-600 dark:text-blue-400">
                                {latestScore?.total_score?.toFixed(1) || '--'}
                            </div>
                            <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                                / 100 分
                            </div>
                            <div className={`mt-3 inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium bg-${getFactorRating(latestScore?.total_score).color}-100 dark:bg-${getFactorRating(latestScore?.total_score).color}-900/30 text-${getFactorRating(latestScore?.total_score).color}-700 dark:text-${getFactorRating(latestScore?.total_score).color}-400`}>
                                {getFactorRating(latestScore?.total_score).icon}
                                {getFactorRating(latestScore?.total_score).label}
                            </div>
                        </div>

                        {/* 六大因子分數卡片 */}
                        <FactorScoreCard
                            title="價值"
                            score={latestScore?.value_score}
                            description="P/E, P/B, 殖利率"
                        />
                        <FactorScoreCard
                            title="品質"
                            score={latestScore?.quality_score}
                            description="ROE, ROA, 負債比"
                        />
                        <FactorScoreCard
                            title="動能"
                            score={latestScore?.momentum_score}
                            description="RSI, 相對報酬"
                        />
                        <FactorScoreCard
                            title="規模"
                            score={latestScore?.size_score}
                            description="市值大小"
                        />
                        <FactorScoreCard
                            title="波動率"
                            score={latestScore?.volatility_score}
                            description="風險指標"
                        />
                        <FactorScoreCard
                            title="成長"
                            score={latestScore?.growth_score}
                            description="營收/EPS CAGR"
                        />
                    </div>

                    {/* 六大因子雷達圖 */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div className="card">
                            <h2 className="text-2xl font-bold mb-4">因子 DNA 雷達圖</h2>
                            <ResponsiveContainer width="100%" height={400}>
                                <RadarChart data={radarData}>
                                    <PolarGrid />
                                    <PolarAngleAxis dataKey="factor" />
                                    <PolarRadiusAxis angle={90} domain={[0, 100]} />
                                    <Radar
                                        name="因子分數"
                                        dataKey="score"
                                        stroke="#3b82f6"
                                        fill="#3b82f6"
                                        fillOpacity={0.6}
                                    />
                                    <Tooltip />
                                    <Legend />
                                </RadarChart>
                            </ResponsiveContainer>
                            <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
                                <p>此雷達圖展示股票在六大因子的綜合表現</p>
                                <p>圓形越大代表該股票在各因子表現越均衡</p>
                            </div>
                        </div>

                        {/* 因子強弱分析 */}
                        <div className="card">
                            <h2 className="text-2xl font-bold mb-4">因子強弱排序</h2>
                            <div className="space-y-3">
                                {radarData
                                    .sort((a, b) => b.score - a.score)
                                    .map((item, index) => {
                                        const rating = getFactorRating(item.score)
                                        return (
                                            <div key={item.factor} className="flex items-center gap-3">
                                                <div className="text-2xl font-bold text-gray-400 w-8">
                                                    #{index + 1}
                                                </div>
                                                <div className="flex-1">
                                                    <div className="flex items-center justify-between mb-1">
                                                        <span className="font-medium">{item.factor}</span>
                                                        <span className="text-sm font-bold">{item.score.toFixed(1)}</span>
                                                    </div>
                                                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                                        <div
                                                            className={`bg-${rating.color}-500 h-2 rounded-full transition-all duration-500`}
                                                            style={{ width: `${item.score}%` }}
                                                        />
                                                    </div>
                                                </div>
                                                <div className={`px-2 py-1 rounded text-xs font-medium bg-${rating.color}-100 dark:bg-${rating.color}-900/30 text-${rating.color}-700 dark:text-${rating.color}-400`}>
                                                    {rating.label}
                                                </div>
                                            </div>
                                        )
                                    })}
                            </div>
                        </div>
                    </div>

                    {/* 歷史趨勢圖 */}
                    <div className="card">
                        <h2 className="text-2xl font-bold mb-4">因子分數歷史趨勢（30期）</h2>
                        <ResponsiveContainer width="100%" height={350}>
                            <LineChart data={historicalData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis
                                    dataKey="calculation_date"
                                    tick={{ fontSize: 11 }}
                                    angle={-45}
                                    textAnchor="end"
                                    height={80}
                                />
                                <YAxis domain={[0, 100]} />
                                <Tooltip />
                                <Legend />
                                <Line type="monotone" dataKey="value_score" stroke="#10b981" strokeWidth={2} name="價值" dot={{ r: 2 }} />
                                <Line type="monotone" dataKey="quality_score" stroke="#3b82f6" strokeWidth={2} name="品質" dot={{ r: 2 }} />
                                <Line type="monotone" dataKey="momentum_score" stroke="#f59e0b" strokeWidth={2} name="動能" dot={{ r: 2 }} />
                                <Line type="monotone" dataKey="growth_score" stroke="#8b5cf6" strokeWidth={2} name="成長" dot={{ r: 2 }} />
                                <Line type="monotone" dataKey="total_score" stroke="#ef4444" strokeWidth={3} name="總分" dot={{ r: 3 }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    {/* 因子說明 */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        <FactorExplanation
                            title="價值因子"
                            description="衡量股票價格相對於其內在價值的便宜程度"
                            indicators="P/E, P/B, 股息殖利率, EV/EBITDA"
                            interpretation="分數越高代表估值越便宜，適合價值型投資者"
                        />
                        <FactorExplanation
                            title="品質因子"
                            description="評估公司的財務健康度與獲利能力"
                            indicators="ROE, ROA, 負債權益比, 毛利率穩定性"
                            interpretation="分數越高代表公司品質越佳，長期穩定性越好"
                        />
                        <FactorExplanation
                            title="動能因子"
                            description="捕捉股價趨勢與市場情緒"
                            indicators="RSI, 相對大盤報酬率, 距52週高點"
                            interpretation="分數越高代表趨勢越強勁，動能投資機會"
                        />
                        <FactorExplanation
                            title="規模因子"
                            description="根據公司市值大小分類"
                            indicators="總市值"
                            interpretation="大型股穩定性高，小型股成長潛力大"
                        />
                        <FactorExplanation
                            title="波動率因子"
                            description="衡量股價波動風險"
                            indicators="年化歷史波動率"
                            interpretation="分數越高代表波動越低（風險越小）"
                        />
                        <FactorExplanation
                            title="成長因子"
                            description="評估公司成長潛力"
                            indicators="營收CAGR, EPS CAGR"
                            interpretation="分數越高代表成長性越強"
                        />
                    </div>
                </>
            ) : (
                <div className="card text-center py-12">
                    <p className="text-gray-500 dark:text-gray-400">
                        無因子資料，請輸入其他股票代碼或稍後再試
                    </p>
                </div>
            )}
        </div>
    )
}

// 因子分數卡片元件
function FactorScoreCard({ title, score, description }) {
    const rating = score >= 80 ? 'excellent' : score >= 70 ? 'good' : score >= 50 ? 'average' : 'weak'
    const colors = {
        excellent: 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-700 text-green-700 dark:text-green-400',
        good: 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-700 text-blue-700 dark:text-blue-400',
        average: 'bg-yellow-50 dark:bg-yellow-900/30 border-yellow-200 dark:border-yellow-700 text-yellow-700 dark:text-yellow-400',
        weak: 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-700 text-red-700 dark:text-red-400'
    }

    return (
        <div className={`card ${colors[rating]}`}>
            <h3 className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                {title}
            </h3>
            <div className="text-3xl font-bold">
                {score?.toFixed(1) || '--'}
            </div>
            <div className="text-xs mt-2 opacity-75">
                {description}
            </div>
        </div>
    )
}

// 因子說明元件
function FactorExplanation({ title, description, indicators, interpretation }) {
    return (
        <div className="card bg-gray-50 dark:bg-gray-800/50">
            <h3 className="font-bold text-lg mb-2">{title}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{description}</p>
            <div className="space-y-2 text-sm">
                <div>
                    <span className="font-medium">指標：</span>
                    <span className="text-gray-600 dark:text-gray-400">{indicators}</span>
                </div>
                <div>
                    <span className="font-medium">解讀：</span>
                    <span className="text-gray-600 dark:text-gray-400">{interpretation}</span>
                </div>
            </div>
        </div>
    )
}
