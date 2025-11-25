// 策略執行偏差熱力圖 - 繁體中文因子名稱
import { useState } from 'react'
import { Activity, AlertTriangle, TrendingUp } from 'lucide-react'

export default function DeviationHeatmap() {
    // 因子中英文對照
    const factorLabels = {
        value: '價值',
        quality: '品質',
        momentum: '動能',
        size: '規模',
        volatility: '波動率',
        growth: '成長'
    }

    // 目標因子配置
    const targetFactors = { value: 25, quality: 20, momentum: 20, size: 15, volatility: 10, growth: 10 }

    // 實際因子曝險（模擬每週數據）
    const weeklyData = [
        { week: 'W1', value: 28, quality: 18, momentum: 22, size: 14, volatility: 9, growth: 9 },
        { week: 'W2', value: 30, quality: 17, momentum: 20, size: 15, volatility: 10, growth: 8 },
        { week: 'W3', value: 27, quality: 19, momentum: 21, size: 13, volatility: 11, growth: 9 },
        { week: 'W4', value: 26, quality: 20, momentum: 23, size: 14, volatility: 8, growth: 9 },
        { week: 'W5', value: 29, quality: 19, momentum: 19, size: 15, volatility: 10, growth: 8 },
        { week: 'W6', value: 31, quality: 18, momentum: 21, size: 14, volatility: 9, growth: 7 },
        { week: 'W7', value: 28, quality: 21, momentum: 20, size: 13, volatility: 10, growth: 8 },
        { week: 'W8', value: 27, quality: 20, momentum: 22, size: 15, volatility: 9, growth: 7 }
    ]

    const calculateDeviation = (actual, target) => ((actual - target) / target * 100).toFixed(1)
    const getDeviationColor = (deviation) => {
        const absDeviation = Math.abs(deviation)
        if (absDeviation < 5) return 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
        if (absDeviation < 10) return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300'
        if (absDeviation < 20) return 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300'
        return 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
    }

    const currentWeek = weeklyData[weeklyData.length - 1]
    const calculateOverallDeviation = (data) => {
        const factors = ['value', 'quality', 'momentum', 'size', 'volatility', 'growth']
        const deviations = factors.map(factor => Math.abs((data[factor] - targetFactors[factor]) / targetFactors[factor] * 100))
        return (deviations.reduce((a, b) => a + b, 0) / factors.length).toFixed(1)
    }
    const overallDeviation = calculateOverallDeviation(currentWeek)

    return (
        <div className="p-8 space-y-8">
            <div>
                <h1 className="text-3xl font-bold flex items-center gap-3"><Activity className="w-8 h-8 text-blue-600" />策略執行偏差熱力圖</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">因子偏離度視覺化 | 策略執行監控 | 再平衡提醒</p>
            </div>

            <div className="card bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
                <div className="flex items-center justify-between">
                    <div><h3 className="text-lg font-bold mb-2">整體策略偏差</h3><p className="text-sm text-gray-600 dark:text-gray-400">當前投資組合與目標策略的偏離程度</p></div>
                    <div className="text-center">
                        <div className={`text-5xl font-bold ${overallDeviation < 5 ? 'text-green-600' : overallDeviation < 10 ? 'text-yellow-600' : overallDeviation < 15 ? 'text-orange-600' : 'text-red-600'}`}>{overallDeviation}%</div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">平均偏差</div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card">
                    <h3 className="text-xl font-bold mb-4">目標因子配置</h3>
                    <div className="space-y-3">
                        {Object.entries(targetFactors).map(([factor, value]) => (
                            <FactorBar key={factor} label={factorLabels[factor]} value={value} isTarget />
                        ))}
                    </div>
                </div>

                <div className="card">
                    <h3 className="text-xl font-bold mb-4">實際因子曝險（本週）</h3>
                    <div className="space-y-3">
                        {Object.entries(currentWeek).filter(([key]) => key !== 'week').map(([factor, value]) => (
                            <FactorBar key={factor} label={factorLabels[factor]} value={value} target={targetFactors[factor]} />
                        ))}
                    </div>
                </div>
            </div>

            <div className="card">
                <h3 className="text-xl font-bold mb-4">8週偏差趨勢熱力圖</h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-gray-200 dark:border-gray-700">
                                <th className="px-4 py-3 text-left font-medium">因子</th>
                                <th className="px-4 py-3 text-center font-medium">目標%</th>
                                {weeklyData.map((data, i) => (
                                    <th key={i} className="px-4 py-3 text-center font-medium">{data.week}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {Object.entries(targetFactors).map(([factor, target]) => (
                                <tr key={factor} className="border-b border-gray-200 dark:border-gray-700">
                                    <td className="px-4 py-3 font-medium">{factorLabels[factor]}</td>
                                    <td className="px-4 py-3 text-center font-bold">{target}%</td>
                                    {weeklyData.map((data, i) => {
                                        const actual = data[factor]
                                        const deviation = calculateDeviation(actual, target)
                                        return (
                                            <td key={i} className="px-2 py-2">
                                                <div className={`p-2 rounded text-center font-medium ${getDeviationColor(deviation)}`}>
                                                    <div className="text-xs">{actual}%</div>
                                                    <div className="text-[10px]">({deviation > 0 ? '+' : ''}{deviation}%)</div>
                                                </div>
                                            </td>
                                        )
                                    })}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div className="mt-4 flex items-center gap-4 text-xs">
                    <span className="font-medium">偏差程度：</span>
                    <div className="flex items-center gap-2"><div className="w-4 h-4 bg-green-200 rounded"></div><span>&lt;5% 良好</span></div>
                    <div className="flex items-center gap-2"><div className="w-4 h-4 bg-yellow-200 rounded"></div><span>5-10% 注意</span></div>
                    <div className="flex items-center gap-2"><div className="w-4 h-4 bg-orange-200 rounded"></div><span>10-20% 警告</span></div>
                    <div className="flex items-center gap-2"><div className="w-4 h-4 bg-red-200 rounded"></div><span>&gt;20% 嚴重</span></div>
                </div>
            </div>

            <div className="card">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2"><AlertTriangle className="w-6 h-6 text-orange-600" />再平衡建議</h3>
                <div className="space-y-3">
                    {Object.entries(currentWeek).filter(([key]) => key !== 'week').map(([factor, actual]) => {
                        const target = targetFactors[factor]
                        const deviation = parseFloat(calculateDeviation(actual, target))
                        if (Math.abs(deviation) < 10) return null
                        return <RebalanceAlert key={factor} factor={factorLabels[factor]} target={target} actual={actual} deviation={deviation} />
                    }).filter(Boolean)}

                    {Object.entries(currentWeek).filter(([key]) => key !== 'week').every(([factor, actual]) => Math.abs(calculateDeviation(actual, targetFactors[factor])) < 10) && (
                        <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg text-center">
                            <p className="text-green-800 dark:text-green-300">✅ 目前投資組合策略執行良好，無需調整</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

function FactorBar({ label, value, target, isTarget = false }) {
    const deviation = target ? ((value - target) / target * 100).toFixed(1) : 0
    const width = (value / 35 * 100).toFixed(0)
    return (
        <div>
            <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">{label}</span>
                <div className="flex items-center gap-2">
                    <span className="font-bold">{value}%</span>
                    {!isTarget && deviation !== 0 && (
                        <span className={`text-xs px-2 py-0.5 rounded ${Math.abs(deviation) < 5 ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' : Math.abs(deviation) < 10 ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400' : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'}`}>
                            {deviation > 0 ? '+' : ''}{deviation}%
                        </span>
                    )}
                </div>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                <div className={`h-3 rounded-full ${isTarget ? 'bg-gray-400' : Math.abs(deviation) < 10 ? 'bg-blue-600' : 'bg-orange-600'}`} style={{ width: `${width}%` }} />
            </div>
        </div>
    )
}

function RebalanceAlert({ factor, target, actual, deviation }) {
    const action = deviation > 0 ? '減少' : '增加'
    const amount = Math.abs(actual - target).toFixed(1)
    return (
        <div className="p-4 border border-orange-200 dark:border-orange-700 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
            <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                    <div className="font-bold mb-1">{factor} 因子偏離 {Math.abs(deviation).toFixed(1)}%</div>
                    <div className="text-sm"><strong>建議：</strong>{action} {factor} 因子曝險約 {amount}%（目標{target}% → 實際{actual}%）</div>
                </div>
            </div>
        </div>
    )
}
