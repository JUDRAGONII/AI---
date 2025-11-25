// 行為金融教練 (Behavioral Finance Coach)
// 非理性行為偵測、處置效應警示、損失規避提醒
import { useState } from 'react'
import {
    RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { Brain, AlertTriangle, TrendingDown, Award, Lightbulb } from 'lucide-react'

export default function BehavioralCoach() {
    // 行為偏誤評分
    const behaviorScores = [
        { behavior: '處置效應', score: 72, threshold: 60, status: 'warning' },
        { behavior: '損失規避', score: 65, threshold: 60, status: 'warning' },
        { behavior: '過度交易', score: 45, threshold: 60, status: 'good' },
        { behavior: '羊群效應', score: 38, threshold: 60, status: 'good' },
        { behavior: '過度自信', score: 68, threshold: 60, status: 'warning' },
        { behavior: '錨定效應', score: 55, threshold: 60, status: 'good' }
    ]

    // 雷達圖資料
    const radarData = behaviorScores.map(b => ({
        behavior: b.behavior,
        score: b.score,
        threshold: b.threshold
    }))

    // 交易分析
    const tradingAnalysis = {
        totalTrades: 45,
        winningTrades: 28,
        losingTrades: 17,
        avgHoldingWinners: 12, // 天
        avgHoldingLosers: 45, // 天
        winRate: 62.2,
        avgWin: 5.8,
        avgLoss: -3.2
    }

    // 偏誤警示
    const biasAlerts = [
        {
            type: 'disposition',
            severity: 'high',
            title: '處置效應偵測',
            description: '您持有虧損部位的時間（平均45天）遠長於獲利部位（平均12天）',
            impact: '可能錯失停損時機，放大虧損',
            suggestion: '建議: 設定明確停損點，獲利部位給予更多空間成長',
            score: 72
        },
        {
            type: 'loss_aversion',
            severity: 'medium',
            title: '損失規避傾向',
            description: '對虧損的反應強度是獲利的2.1倍',
            impact: '可能導致過度保守，錯失投資機會',
            suggestion: '建議: 以長期視角看待短期波動，專注投資邏輯而非情緒',
            score: 65
        },
        {
            type: 'overconfidence',
            severity: 'medium',
            title: '過度自信跡象',
            description: '您的預測準確率（62%）低於自我評估（85%）',
            impact: '可能承擔過高風險，低估市場不確定性',
            suggestion: '建議: 保持謙遜，多聽取他人意見，設定合理期望',
            score: 68
        }
    ]

    // 改善建議
    const improvements = [
        {
            area: '處置效應',
            current: 72,
            target: 50,
            actions: [
                '設定自動停損點，避免情緒化決策',
                '定期檢視虧損部位，客觀評估是否該賣出',
                '記錄每次不願停損的理由，反思是否合理'
            ]
        },
        {
            area: '損失規避',
            current: 65,
            target: 50,
            actions: [
                '練習以百分比而非絕對金額看待損益',
                '設定風險預算，在可承受範圍內接受虧損',
                '記住: 適度風險是獲取報酬的必要成本'
            ]
        }
    ]

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold flex items-center gap-3">
                    <Brain className="w-8 h-8" />
                    AI 行為金融教練
                </h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                    投資心理分析 | 非理性行為偵測 | 個人化改善建議
                </p>
            </div>

            {/* 整體評分 */}
            <div className="card bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="text-lg font-bold mb-2">投資心理健康度</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            基於 {tradingAnalysis.totalTrades} 筆交易的行為分析
                        </p>
                    </div>
                    <div className="text-center">
                        <div className="text-5xl font-bold text-orange-600">72</div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">/ 100 分</div>
                        <div className="mt-2 px-3 py-1 rounded-full text-xs font-medium bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400">
                            需要改善
                        </div>
                    </div>
                </div>
            </div>

            {/* 行為偏誤雷達圖 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card">
                    <h3 className="text-xl font-bold mb-4">行為偏誤分析</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <RadarChart data={radarData}>
                            <PolarGrid />
                            <PolarAngleAxis dataKey="behavior" />
                            <PolarRadiusAxis angle={90} domain={[0, 100]} />
                            <Radar name="您的分數" dataKey="score" stroke="#ef4444" fill="#ef4444" fillOpacity={0.5} />
                            <Radar name="健康閾值" dataKey="threshold" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />
                            <Legend />
                        </RadarChart>
                    </ResponsiveContainer>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-2 text-center">
                        💡 分數越低越好，低於60分表示行為健康
                    </p>
                </div>

                {/* 交易統計 */}
                <div className="card">
                    <h3 className="text-xl font-bold mb-4">交易行為統計</h3>
                    <div className="space-y-4">
                        <StatRow label="總交易次數" value={tradingAnalysis.totalTrades} />
                        <StatRow label="勝率" value={`${tradingAnalysis.winRate}%`} highlight />
                        <StatRow label="平均獲利" value={`+${tradingAnalysis.avgWin}%`} positive />
                        <StatRow label="平均虧損" value={`${tradingAnalysis.avgLoss}%`} negative />
                        <StatRow
                            label="獲利部位持有期"
                            value={`${tradingAnalysis.avgHoldingWinners} 天`}
                            highlight
                        />
                        <StatRow
                            label="虧損部位持有期"
                            value={`${tradingAnalysis.avgHoldingLosers} 天`}
                            warning
                        />
                    </div>
                    <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                        <p className="text-sm text-red-800 dark:text-red-400">
                            ⚠️ 警示: 虧損持有期是獲利的 <strong>3.75 倍</strong>，顯示明顯的處置效應
                        </p>
                    </div>
                </div>
            </div>

            {/* 偏誤警示 */}
            <div className="space-y-4">
                <h3 className="text-xl font-bold">偵測到的行為偏誤</h3>
                {biasAlerts.map((alert, index) => (
                    <BiasAlertCard key={index} alert={alert} />
                ))}
            </div>

            {/* 改善計畫 */}
            <div className="card">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <Award className="w-6 h-6 text-blue-600" />
                    個人化改善計畫
                </h3>
                <div className="space-y-6">
                    {improvements.map((item, index) => (
                        <ImprovementPlan key={index} plan={item} />
                    ))}
                </div>
            </div>

            {/* 每日提醒 */}
            <div className="card bg-gradient-to-r from-blue-50 to-green-50 dark:from-blue-900/20 dark:to-green-900/20">
                <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                    <Lightbulb className="w-5 h-5 text-blue-600" />
                    今日投資心理提醒
                </h3>
                <div className="space-y-2 text-sm">
                    <p>📌 <strong>交易前三問</strong>: 1) 這是理性分析還是情緒反應？2) 停損點在哪？3) 為什麼現在？</p>
                    <p>📌 <strong>虧損時記住</strong>: 承認錯誤不是失敗，固執己見才是</p>
                    <p>📌 <strong>獲利時記住</strong>: 不要過早獲利了結，給優質標的成長空間</p>
                    <p>📌 <strong>每日自省</strong>: 今天的決策是基於事實還是希望？</p>
                </div>
            </div>
        </div>
    )
}

// 偏誤警示卡片
function BiasAlertCard({ alert }) {
    const severityConfig = {
        high: { bg: 'bg-red-50 dark:bg-red-900/20', border: 'border-red-200 dark:border-red-700', icon: 'text-red-600' },
        medium: { bg: 'bg-orange-50 dark:bg-orange-900/20', border: 'border-orange-200 dark:border-orange-700', icon: 'text-orange-600' },
        low: { bg: 'bg-yellow-50 dark:bg-yellow-900/20', border: 'border-yellow-200 dark:border-yellow-700', icon: 'text-yellow-600' }
    }

    const config = severityConfig[alert.severity]

    return (
        <div className={`card ${config.bg} border-2 ${config.border}`}>
            <div className="flex items-start gap-4">
                <div className={`p-3 rounded-lg bg-white dark:bg-gray-800 ${config.icon}`}>
                    <AlertTriangle className="w-6 h-6" />
                </div>
                <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                        <h4 className="font-bold text-lg">{alert.title}</h4>
                        <span className="text-2xl font-bold text-red-600">{alert.score}</span>
                    </div>
                    <p className="text-sm mb-2">{alert.description}</p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                        <div className="p-2 bg-white dark:bg-gray-800 rounded">
                            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">影響</div>
                            <div className="text-sm font-medium">{alert.impact}</div>
                        </div>
                        <div className="p-2 bg-white dark:bg-gray-800 rounded">
                            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">建議</div>
                            <div className="text-sm font-medium text-green-700 dark:text-green-400">{alert.suggestion}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

// 統計行
function StatRow({ label, value, positive, negative, highlight, warning }) {
    let className = ''
    if (positive) className = 'text-green-600'
    if (negative) className = 'text-red-600'
    if (highlight) className = 'text-blue-600 font-bold'
    if (warning) className = 'text-orange-600 font-bold'

    return (
        <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
            <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
            <span className={`font-medium ${className}`}>{value}</span>
        </div>
    )
}

// 改善計畫
function ImprovementPlan({ plan }) {
    const progress = ((plan.target / plan.current) * 100).toFixed(0)

    return (
        <div>
            <div className="flex items-center justify-between mb-2">
                <h4 className="font-bold">{plan.area}</h4>
                <div className="text-sm">
                    <span className="text-gray-600 dark:text-gray-400">目標: </span>
                    <span className="font-medium">{plan.target}</span>
                    <span className="text-gray-600 dark:text-gray-400 mx-2">當前: </span>
                    <span className="font-medium text-orange-600">{plan.current}</span>
                </div>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-3">
                <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${progress}%` }}
                />
            </div>
            <ul className="space-y-1 text-sm">
                {plan.actions.map((action, i) => (
                    <li key={i} className="flex items-start gap-2">
                        <span className="text-blue-600">•</span>
                        <span>{action}</span>
                    </li>
                ))}
            </ul>
        </div>
    )
}
