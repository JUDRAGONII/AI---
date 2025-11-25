// AI 假設情境模擬器 (What-If Simulator)
// 交易模擬、影響分析（風險/報酬/稅務）
import { useState } from 'react'
import {
    LineChart, Line, BarChart, Bar,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { Play, TrendingUp, DollarSign, AlertCircle, Lightbulb } from 'lucide-react'

export default function WhatIfSimulator() {
    const [scenario, setScenario] = useState({
        action: 'buy',
        stock: '2330',
        shares: 100,
        price: 580,
        targetDate: '2024-12-31'
    })

    const [simulationResult, setSimulationResult] = useState(null)

    // 當前投資組合
    const currentPortfolio = {
        totalValue: 1650000,
        stocks: 1350000,
        cash: 300000,
        holdings: [
            { code: '2330', shares: 1000, avgCost: 550, currentPrice: 580 },
            { code: '2317', shares: 2000, avgCost: 105, currentPrice: 110 }
        ]
    }

    const runSimulation = () => {
        // 模擬結果
        const result = {
            // 風險分析
            risk: {
                portfolioVolatility: scenario.action === 'buy' ? 13.5 : 11.2,
                beta: scenario.action === 'buy' ? 1.05 : 0.92,
                maxDrawdown: scenario.action === 'buy' ? -18.5 : -14.2,
                var95: scenario.action === 'buy' ? -85000 : -62000
            },
            // 報酬分析
            return: {
                expectedReturn: scenario.action === 'buy' ? 11.2 : 9.5,
                bestCase: scenario.action === 'buy' ? 25.5 : 18.2,
                worstCase: scenario.action === 'buy' ? -8.5 : -5.2,
                probabilityProfit: scenario.action === 'buy' ? 68 : 62
            },
            // 稅務影響
            tax: {
                capitalGainsTax: 0, // 台股免稅
                dividendTax: scenario.action === 'buy' ? 850 : 650,
                totalTax: scenario.action === 'buy' ? 850 : 650
            },
            // 其他影響
            other: {
                newTotalValue: scenario.action === 'buy' ? 1708000 : 1592000,
                cashRemaining: scenario.action === 'buy' ? 242000 : 358000,
                diversification: scenario.action === 'buy' ? 72 : 85,
                liquidityRatio: scenario.action === 'buy' ? 14.2 : 22.5
            }
        }

        setSimulationResult(result)
    }

    // 價格敏感度分析
    const sensitivityData = [
        { price: 520, profit: -6000, return: -10.3 },
        { price: 540, profit: -4000, return: -6.9 },
        { price: 560, profit: -2000, return: -3.4 },
        { price: 580, profit: 0, return: 0 },
        { price: 600, profit: 2000, return: 3.4 },
        { price: 620, profit: 4000, return: 6.9 },
        { price: 640, profit: 6000, return: 10.3 }
    ]

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">AI 假設情境模擬器</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                    What-If 分析 | 風險報酬評估 | 稅務影響試算
                </p>
            </div>

            {/* 情境設定 */}
            <div className="card">
                <h2 className="text-xl font-bold mb-4">設定模擬情境</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                    <div>
                        <label className="block text-sm font-medium mb-2">動作</label>
                        <select
                            value={scenario.action}
                            onChange={(e) => setScenario({ ...scenario, action: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                        >
                            <option value="buy">買入</option>
                            <option value="sell">賣出</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">股票代碼</label>
                        <input
                            type="text"
                            value={scenario.stock}
                            onChange={(e) => setScenario({ ...scenario, stock: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">股數</label>
                        <input
                            type="number"
                            value={scenario.shares}
                            onChange={(e) => setScenario({ ...scenario, shares: parseInt(e.target.value) })}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">預估價格</label>
                        <input
                            type="number"
                            value={scenario.price}
                            onChange={(e) => setScenario({ ...scenario, price: parseFloat(e.target.value) })}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">目標日期</label>
                        <input
                            type="date"
                            value={scenario.targetDate}
                            onChange={(e) => setScenario({ ...scenario, targetDate: e.target.value })}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                        />
                    </div>
                </div>

                <div className="mt-4 flex justify-end">
                    <button
                        onClick={runSimulation}
                        className="btn btn-primary flex items-center gap-2"
                    >
                        <Play className="w-5 h-5" />
                        執行模擬
                    </button>
                </div>
            </div>

            {/* 模擬結果 */}
            {simulationResult && (
                <>
                    {/* 影響總覽 */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        <ImpactCard
                            icon={<TrendingUp className="w-5 h-5" />}
                            label="預期報酬"
                            value={`${simulationResult.return.expectedReturn >= 0 ? '+' : ''}${simulationResult.return.expectedReturn.toFixed(1)}%`}
                            color={simulationResult.return.expectedReturn >= 0 ? 'green' : 'red'}
                            subtitle={`獲利機率 ${simulationResult.return.probabilityProfit}%`}
                        />
                        <ImpactCard
                            icon={<AlertCircle className="w-5 h-5" />}
                            label="風險變化"
                            value={`${simulationResult.risk.portfolioVolatility.toFixed(1)}%`}
                            color="orange"
                            subtitle={`Beta: ${simulationResult.risk.beta.toFixed(2)}`}
                        />
                        <ImpactCard
                            icon={<DollarSign className="w-5 h-5" />}
                            label="稅務成本"
                            value={`$${simulationResult.tax.totalTax.toLocaleString()}`}
                            color="blue"
                            subtitle="股利所得稅"
                        />
                        <ImpactCard
                            icon={<TrendingUp className="w-5 h-5" />}
                            label="新總資產"
                            value={`$${(simulationResult.other.newTotalValue / 1000000).toFixed(2)}M`}
                            color="purple"
                            subtitle={`剩餘現金 $${(simulationResult.other.cashRemaining / 1000).toFixed(0)}K`}
                        />
                    </div>

                    {/* 詳細分析 */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* 風險報酬分析 */}
                        <div className="card">
                            <h3 className="text-lg font-bold mb-4">風險報酬分析</h3>
                            <div className="space-y-3">
                                <AnalysisRow label="最佳情況" value={`+${simulationResult.return.bestCase}%`} positive />
                                <AnalysisRow label="預期情況" value={`+${simulationResult.return.expectedReturn}%`} />
                                <AnalysisRow label="最差情況" value={`${simulationResult.return.worstCase}%`} />
                                <AnalysisRow label="最大回撤" value={`${simulationResult.risk.maxDrawdown}%`} />
                                <AnalysisRow label="VaR (95%)" value={`$${simulationResult.risk.var95.toLocaleString()}`} />
                            </div>
                        </div>

                        {/* 價格敏感度 */}
                        <div className="card">
                            <h3 className="text-lg font-bold mb-4">價格敏感度分析</h3>
                            <ResponsiveContainer width="100%" height={200}>
                                <BarChart data={sensitivityData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="price" />
                                    <YAxis />
                                    <Tooltip />
                                    <Bar dataKey="profit" fill="#3b82f6" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* AI 建議 */}
                    <div className="card bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
                        <div className="flex items-start gap-3">
                            <Lightbulb className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
                            <div>
                                <h3 className="font-bold text-lg mb-3">AI 智慧建議</h3>
                                <div className="space-y-2 text-sm">
                                    {scenario.action === 'buy' ? (
                                        <>
                                            <p>✅ 此次買入將提升投資組合預期報酬至 <strong>{simulationResult.return.expectedReturn}%</strong></p>
                                            <p>⚠️ 但同時會增加波動率至 <strong>{simulationResult.risk.portfolioVolatility}%</strong></p>
                                            <p>💡 建議: 若願意承擔額外風險，可執行此交易</p>
                                            <p>💡 或考慮: 分批買入以降低單一時點風險</p>
                                            <p>⏰ 最佳執行時機: 等待回調至 <strong>$560</strong> 附近</p>
                                        </>
                                    ) : (
                                        <>
                                            <p>✅ 此次賣出將降低投資組合波動率至 <strong>{simulationResult.risk.portfolioVolatility}%</strong></p>
                                            <p>⚠️ 但預期報酬也會下降至 <strong>{simulationResult.return.expectedReturn}%</strong></p>
                                            <p>💡 建議: 若追求穩健，可執行此交易</p>
                                            <p>💡 稅務提醒: 此交易無資本利得稅，僅需注意股利所得稅</p>
                                            <p>⏰ 最佳執行時機: 等待反彈至 <strong>$600</strong> 以上</p>
                                        </>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    )
}

// 影響卡片
function ImpactCard({ icon, label, value, color, subtitle }) {
    const colorClasses = {
        green: 'bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400',
        red: 'bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400',
        orange: 'bg-orange-50 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
        blue: 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
        purple: 'bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400'
    }

    return (
        <div className={`card ${colorClasses[color]}`}>
            <div className="flex items-center gap-2 mb-2">
                {icon}
                <span className="text-sm font-medium">{label}</span>
            </div>
            <div className="text-2xl font-bold mb-1">{value}</div>
            <div className="text-xs opacity-75">{subtitle}</div>
        </div>
    )
}

// 分析行
function AnalysisRow({ label, value, positive = false }) {
    return (
        <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
            <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
            <span className={`font-medium ${positive ? 'text-green-600' : ''}`}>{value}</span>
        </div>
    )
}
