// 策略回測實驗室 (Strategy Backtesting Lab)
// No-Code 策略建構器、回測引擎、績效報告
import { useState } from 'react'
import {
    LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { Play, Plus, Download, TrendingUp } from 'lucide-react'

export default function StrategyBacktesting() {
    const [strategyName, setStrategyName] = useState('MA交叉策略')
    const [running, setRunning] = useState(false)

    // 模擬回測結果
    const backtestResults = {
        totalReturn: 45.2,
        annualizedReturn: 12.8,
        sharpeRatio: 1.35,
        maxDrawdown: -15.3,
        winRate: 58.5,
        totalTrades: 127,
        winningTrades: 74,
        losingTrades: 53,
        avgWin: 5.2,
        avgLoss: -3.1
    }

    // 資產曲線
    const equityCurve = Array.from({ length: 100 }, (_, i) => ({
        date: `Day ${i + 1}`,
        equity: 100000 * (1 + (i * 0.005) + (Math.random() - 0.45) * 0.02),
        benchmark: 100000 * (1 + i * 0.003)
    }))

    // 月度報酬
    const monthlyReturns = Array.from({ length: 12 }, (_, i) => ({
        month: `${i + 1}月`,
        return: (Math.random() - 0.3) * 10
    }))

    const runBacktest = () => {
        setRunning(true)
        setTimeout(() => setRunning(false), 3000)
    }

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">策略回測實驗室</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        No-Code 策略建構 | 歷史回測 | 績效分析
                    </p>
                </div>

                <button
                    onClick={runBacktest}
                    disabled={running}
                    className="btn btn-primary flex items-center gap-2"
                >
                    <Play className="w-5 h-5" />
                    {running ? '回測中...' : '執行回測'}
                </button>
            </div>

            {/* 策略設定 */}
            <div className="card">
                <h2 className="text-xl font-bold mb-4">策略設定</h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium mb-2">策略名稱</label>
                        <input
                            type="text"
                            value={strategyName}
                            onChange={(e) => setStrategyName(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">股票代碼</label>
                        <input
                            type="text"
                            defaultValue="2330"
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">回測期間</label>
                        <select className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                            <option>近1年</option>
                            <option>近3年</option>
                            <option>近5年</option>
                            <option>全部歷史</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">初始資金</label>
                        <input
                            type="number"
                            defaultValue="100000"
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                        />
                    </div>
                </div>
            </div>

            {/* No-Code 策略建構器 */}
            <div className="card">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-bold">策略規則</h2>
                    <button className="btn btn-secondary flex items-center gap-2 text-sm">
                        <Plus className="w-4 h-4" />
                        新增規則
                    </button>
                </div>

                <div className="space-y-3">
                    <StrategyRule
                        condition="當 MA(5) 向上穿越 MA(20)"
                        action="買入 100%"
                    />
                    <StrategyRule
                        condition="當 MA(5) 向下穿越 MA(20)"
                        action="賣出 100%"
                    />
                    <StrategyRule
                        condition="當 RSI < 30"
                        action="買入 50%"
                    />
                </div>
            </div>

            {/* 績效總覽 */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <MetricCard label="總報酬率" value={`${backtestResults.totalReturn}%`} positive />
                <MetricCard label="年化報酬率" value={`${backtestResults.annualizedReturn}%`} positive />
                <MetricCard label="夏普比率" value={backtestResults.sharpeRatio} />
                <MetricCard label="最大回撤" value={`${backtestResults.maxDrawdown}%`} />
                <MetricCard label="勝率" value={`${backtestResults.winRate}%`} />
                <MetricCard label="總交易次數" value={backtestResults.totalTrades} />
                <MetricCard label="平均獲利" value={`${backtestResults.avgWin}%`} positive />
                <MetricCard label="平均虧損" value={`${backtestResults.avgLoss}%`} />
            </div>

            {/* 資產曲線 */}
            <div className="card">
                <h2 className="text-2xl font-bold mb-4">資產曲線</h2>
                <ResponsiveContainer width="100%" height={350}>
                    <LineChart data={equityCurve}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="equity" stroke="#3b82f6" strokeWidth={2} name="策略" dot={false} />
                        <Line type="monotone" dataKey="benchmark" stroke="#94a3b8" strokeWidth={2} name="基準" dot={false} strokeDasharray="5 5" />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* 月度報酬 */}
            <div className="card">
                <h2 className="text-2xl font-bold mb-4">月度報酬分布</h2>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={monthlyReturns}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis unit="%" />
                        <Tooltip />
                        <Bar dataKey="return" fill="#3b82f6" />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* 交易明細 */}
            <div className="card">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold">交易明細</h2>
                    <button className="btn btn-secondary flex items-center gap-2 text-sm">
                        <Download className="w-4 h-4" />
                        匯出 CSV
                    </button>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead className="bg-gray-50 dark:bg-gray-800">
                            <tr>
                                <th className="px-4 py-3 text-left">#</th>
                                <th className="px-4 py-3 text-left">日期</th>
                                <th className="px-4 py-3 text-left">交易</th>
                                <th className="px-4 py-3 text-right">價格</th>
                                <th className="px-4 py-3 text-right">股數</th>
                                <th className="px-4 py-3 text-right">金額</th>
                                <th className="px-4 py-3 text-right">損益</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            <TradeRow id={1} date="2024-10-15" type="買入" price={580} shares={100} amount={58000} />
                            <TradeRow id={2} date="2024-11-01" type="賣出" price={595} shares={100} amount={59500} pnl={1500} />
                            <TradeRow id={3} date="2024-11-10" type="買入" price={572} shares={100} amount={57200} />
                            <TradeRow id={4} date="2024-11-20" type="賣出" price={588} shares={100} amount={58800} pnl={1600} />
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}

// 策略規則卡片
function StrategyRule({ condition, action }) {
    return (
        <div className="flex items-center gap-4 p-4 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800/50">
            <div className="flex-1">
                <div className="font-medium mb-1">條件</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">{condition}</div>
            </div>
            <div className="text-2xl text-gray-400">→</div>
            <div className="flex-1">
                <div className="font-medium mb-1">動作</div>
                <div className="text-sm text-blue-600 dark:text-blue-400 font-medium">{action}</div>
            </div>
        </div>
    )
}

// 指標卡片
function MetricCard({ label, value, positive = false }) {
    const isNumber = typeof value === 'number'
    const textColor = positive ? 'text-green-600 dark:text-green-400' : ''

    return (
        <div className="card">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">{label}</div>
            <div className={`text-2xl font-bold ${textColor}`}>
                {isNumber ? value.toFixed(2) : value}
            </div>
        </div>
    )
}

// 交易記錄行
function TradeRow({ id, date, type, price, shares, amount, pnl = null }) {
    const isBuy = type === '買入'
    const typeColor = isBuy ? 'text-red-600' : 'text-green-600'

    return (
        <tr className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <td className="px-4 py-3">{id}</td>
            <td className="px-4 py-3">{date}</td>
            <td className={`px-4 py-3 font-medium ${typeColor}`}>{type}</td>
            <td className="px-4 py-3 text-right">${price}</td>
            <td className="px-4 py-3 text-right">{shares}</td>
            <td className="px-4 py-3 text-right">${amount.toLocaleString()}</td>
            <td className="px-4 py-3 text-right">
                {pnl !== null && (
                    <span className={pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                        {pnl >= 0 ? '+' : ''}{pnl.toLocaleString()}
                    </span>
                )}
            </td>
        </tr>
    )
}
