// 投資組合優化分析頁面 (Portfolio Optimization)
// 蒙地卡羅模擬、效率前緣、優化建議
import { useState } from 'react'
import {
    ScatterChart, Scatter, LineChart, Line,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    ReferenceLine
} from 'recharts'
import { Target, Zap, TrendingUp, AlertTriangle } from 'lucide-react'

export default function PortfolioOptimization() {
    const [simulationCount, setSimulationCount] = useState(5000)
    const [running, setRunning] = useState(false)

    // 模擬效率前緣資料
    const efficientFrontier = Array.from({ length: 50 }, (_, i) => ({
        risk: 5 + i * 0.5,
        return: 3 + Math.sqrt(i) * 1.5 + (Math.random() - 0.5) * 0.5
    }))

    // 模擬蒙地卡羅模擬結果
    const monteCarloResults = Array.from({ length: 200 }, () => ({
        risk: 8 + Math.random() * 20,
        return: 5 + Math.random() * 15,
        sharpe: 0.5 + Math.random() * 1.5
    }))

    // 當前投資組合
    const currentPortfolio = { risk: 12.5, return: 10.2, sharpe: 0.82 }

    // 最優投資組合
    const optimalPortfolio = { risk: 10.8, return: 11.5, sharpe: 1.06 }

    const runOptimization = () => {
        setRunning(true)
        setTimeout(() => setRunning(false), 2000)
    }

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">投資組合優化分析</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        蒙地卡羅模擬、效率前緣、最佳配置建議
                    </p>
                </div>

                <button
                    onClick={runOptimization}
                    disabled={running}
                    className="btn btn-primary flex items-center gap-2"
                >
                    <Zap className="w-5 h-5" />
                    {running ? '運算中...' : '執行優化'}
                </button>
            </div>

            {/* 控制參數 */}
            <div className="card">
                <h2 className="text-xl font-bold mb-4">優化參數</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                        <label className="block text-sm font-medium mb-2">模擬次數</label>
                        <select
                            value={simulationCount}
                            onChange={(e) => setSimulationCount(parseInt(e.target.value))}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                        >
                            <option value="1000">1,000 次</option>
                            <option value="5000">5,000 次</option>
                            <option value="10000">10,000 次</option>
                            <option value="50000">50,000 次</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">優化目標</label>
                        <select className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                            <option>最大化夏普比率</option>
                            <option>最小化波動率</option>
                            <option>目標報酬率</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">約束條件</label>
                        <select className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                            <option>無約束</option>
                            <option>單一持股上限20%</option>
                            <option>僅多頭部位</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* 投資組合比較 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <PortfolioCard
                    title="當前投資組合"
                    portfolio={currentPortfolio}
                    icon={<Target className="w-6 h-6" />}
                    color="blue"
                />
                <PortfolioCard
                    title="最優投資組合"
                    portfolio={optimalPortfolio}
                    icon={<TrendingUp className="w-6 h-6" />}
                    color="green"
                    isOptimal
                />
            </div>

            {/* 效率前緣圖 */}
            <div className="card">
                <h2 className="text-2xl font-bold mb-4">效率前緣 (Efficient Frontier)</h2>
                <ResponsiveContainer width="100%" height={400}>
                    <ScatterChart>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis
                            dataKey="risk"
                            name="風險 (波動率)"
                            unit="%"
                            label={{ value: '風險 (%)', position: 'insideBottom', offset: -5 }}
                        />
                        <YAxis
                            dataKey="return"
                            name="報酬率"
                            unit="%"
                            label={{ value: '預期報酬 (%)', angle: -90, position: 'insideLeft' }}
                        />
                        <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                        <Legend />

                        {/* 蒙地卡羅模擬點 */}
                        <Scatter
                            name="模擬投資組合"
                            data={monteCarloResults}
                            fill="#94a3b8"
                            fillOpacity={0.3}
                        />

                        {/* 效率前緣線 */}
                        <Scatter
                            name="效率前緣"
                            data={efficientFrontier}
                            fill="#3b82f6"
                            line={{ stroke: '#3b82f6', strokeWidth: 3 }}
                        />

                        {/* 當前投資組合 */}
                        <Scatter
                            name="當前組合"
                            data={[currentPortfolio]}
                            fill="#ef4444"
                            shape="star"
                        />

                        {/* 最優投資組合 */}
                        <Scatter
                            name="最優組合"
                            data={[optimalPortfolio]}
                            fill="#10b981"
                            shape="triangle"
                        />
                    </ScatterChart>
                </ResponsiveContainer>
            </div>

            {/* 優化建議 */}
            <div className="card bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 border-green-200 dark:border-green-800">
                <div className="flex items-start gap-3">
                    <AlertTriangle className="w-6 h-6 text-green-600 dark:text-green-400 flex-shrink-0 mt-1" />
                    <div>
                        <h3 className="font-bold text-lg mb-3">優化建議</h3>
                        <div className="space-y-2 text-sm">
                            <p>✅ 將台積電持股比例從 20% 降至 15%</p>
                            <p>✅ 增加 0050 ETF 持股至 30%</p>
                            <p>✅ 新增債券型 ETF（建議 10%）以降低整體波動</p>
                            <p>✅ 預期可提升夏普比率從 0.82 至 1.06</p>
                            <p>✅ 風險（波動率）可降低 1.7%，報酬率提升 1.3%</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* 詳細配置建議 */}
            <div className="card">
                <h2 className="text-2xl font-bold mb-4">最優配置調整建議</h2>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead className="bg-gray-50 dark:bg-gray-800">
                            <tr>
                                <th className="px-4 py-3 text-left">股票</th>
                                <th className="px-4 py-3 text-right">當前權重</th>
                                <th className="px-4 py-3 text-right">建議權重</th>
                                <th className="px-4 py-3 text-right">變化</th>
                                <th className="px-4 py-3 text-right">建議動作</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            <OptimizationRow code="2330" name="台積電" current={20} optimal={15} />
                            <OptimizationRow code="2317" name="鴻海" current={18} optimal={18} />
                            <OptimizationRow code="0050" name="元大台灣50" current={25} optimal={30} />
                            <OptimizationRow code="2882" name="國泰金" current={15} optimal={12} />
                            <OptimizationRow code="00679B" name="債券ETF" current={0} optimal={10} isNew />
                            <OptimizationRow code="其他" name="現金" current={22} optimal={15} />
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}

// 投資組合卡片
function PortfolioCard({ title, portfolio, icon, color, isOptimal = false }) {
    const colorClasses = {
        blue: 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-700',
        green: 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-700'
    }

    return (
        <div className={`card ${colorClasses[color]}`}>
            <div className="flex items-center gap-3 mb-4">
                {icon}
                <h3 className="text-xl font-bold">{title}</h3>
                {isOptimal && (
                    <span className="ml-auto px-3 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-400">
                        推薦
                    </span>
                )}
            </div>

            <div className="grid grid-cols-3 gap-4">
                <div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">預期報酬</div>
                    <div className="text-2xl font-bold">{portfolio.return}%</div>
                </div>
                <div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">風險</div>
                    <div className="text-2xl font-bold">{portfolio.risk}%</div>
                </div>
                <div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">夏普比率</div>
                    <div className="text-2xl font-bold">{portfolio.sharpe}</div>
                </div>
            </div>
        </div>
    )
}

// 優化建議行
function OptimizationRow({ code, name, current, optimal, isNew = false }) {
    const change = optimal - current
    const action = change > 0 ? '增持' : change < 0 ? '減持' : '維持'
    const actionColor = change > 0 ? 'text-green-600' : change < 0 ? 'text-red-600' : 'text-gray-600'

    return (
        <tr className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <td className="px-4 py-3">
                <div className="font-medium">{code}</div>
                <div className="text-xs text-gray-500">{name}</div>
            </td>
            <td className="px-4 py-3 text-right">{current}%</td>
            <td className="px-4 py-3 text-right font-medium">{optimal}%</td>
            <td className={`px-4 py-3 text-right font-medium ${actionColor}`}>
                {change > 0 ? '+' : ''}{change.toFixed(1)}%
            </td>
            <td className="px-4 py-3 text-right">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${isNew ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400' :
                    change > 0 ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' :
                        change < 0 ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400' :
                            'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                    }`}>
                    {isNew ? '新增' : action}
                </span>
            </td>
        </tr>
    )
}
