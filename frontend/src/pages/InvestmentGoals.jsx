// 投資目標追蹤 (Investment Goals)
// 財務目標設定、進度追蹤、所需報酬率計算
import { useState } from 'react'
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts'
import { Target, TrendingUp, Calendar, DollarSign, Plus } from 'lucide-react'

export default function InvestmentGoals() {
    const [goals] = useState([
        {
            id: 1,
            name: '退休基金',
            targetAmount: 20000000,
            currentAmount: 5850000,
            targetDate: '2045-12-31',
            monthlyContribution: 30000,
            requiredReturn: 6.5,
            onTrack: true
        },
        {
            id: 2,
            name: '購屋頭期款',
            targetAmount: 3000000,
            currentAmount: 1200000,
            targetDate: '2028-12-31',
            monthlyContribution: 25000,
            requiredReturn: 4.2,
            onTrack: true
        },
        {
            id: 3,
            name: '子女教育基金',
            targetAmount: 5000000,
            currentAmount: 850000,
            targetDate: '2035-12-31',
            monthlyContribution: 20000,
            requiredReturn: 7.8,
            onTrack: false
        }
    ])

    // 準備進度資料
    const progressData = goals.map(g => ({
        name: g.name,
        current: g.currentAmount,
        target: g.targetAmount,
        progress: (g.currentAmount / g.targetAmount) * 100
    }))

    // 預測資產成長曲線（以退休基金為例）
    const projectionCurve = Array.from({ length: 21 }, (_, i) => {
        const years = i
        const fv = 5850000 * Math.pow(1.065, years) + 30000 * 12 * ((Math.pow(1.065, years) - 1) / 0.065)
        return {
            year: 2025 + years,
            projected: fv,
            target: 20000000 * (years / 20)
        }
    })

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">投資目標追蹤</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        財務目標設定 | 進度監控 | 達成率分析
                    </p>
                </div>

                <button className="btn btn-primary flex items-center gap-2">
                    <Plus className="w-5 h-5" />
                    新增目標
                </button>
            </div>

            {/* 目標總覽 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="card bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30">
                    <div className="flex items-center gap-2 mb-3">
                        <Target className="w-5 h-5 text-blue-600" />
                        <h3 className="font-medium">活躍目標</h3>
                    </div>
                    <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">{goals.length}</div>
                </div>

                <div className="card bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/30 dark:to-green-800/30">
                    <div className="flex items-center gap-2 mb-3">
                        <TrendingUp className="w-5 h-5 text-green-600" />
                        <h3 className="font-medium">進度正常</h3>
                    </div>
                    <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                        {goals.filter(g => g.onTrack).length}
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/30 dark:to-purple-800/30">
                    <div className="flex items-center gap-2 mb-3">
                        <DollarSign className="w-5 h-5 text-purple-600" />
                        <h3 className="font-medium">目標總額</h3>
                    </div>
                    <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                        ${(goals.reduce((sum, g) => sum + g.targetAmount, 0) / 1000000).toFixed(1)}M
                    </div>
                </div>
            </div>

            {/* 目標清單 */}
            <div className="space-y-4">
                {goals.map(goal => (
                    <GoalCard key={goal.id} goal={goal} />
                ))}
            </div>

            {/* 資產成長預測 */}
            <div className="card">
                <h2 className="text-2xl font-bold mb-4">資產成長預測（退休基金範例）</h2>
                <ResponsiveContainer width="100%" height={350}>
                    <LineChart data={projectionCurve}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" />
                        <YAxis />
                        <Tooltip formatter={(value) => `$${(value / 1000000).toFixed(1)}M`} />
                        <Legend />
                        <Line
                            type="monotone"
                            dataKey="projected"
                            stroke="#3b82f6"
                            strokeWidth={3}
                            name="預測資產"
                            dot={false}
                        />
                        <Line
                            type="monotone"
                            dataKey="target"
                            stroke="#10b981"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            name="目標軌跡"
                            dot={false}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* 建議與提醒 */}
            <div className="card bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-700">
                <h3 className="font-bold text-lg mb-3">財務規劃建議</h3>
                <div className="space-y-2 text-sm">
                    <p>⚠️ 子女教育基金目前進度落後，建議每月定期定額提高至 35,000 元</p>
                    <p>✅ 退休基金進度良好，目前報酬率 6.8% 略高於所需的 6.5%</p>
                    <p>✅ 購屋頭期款預計可提前 1 年達成</p>
                    <p>💡 建議將額外收入優先分配至進度落後的目標</p>
                </div>
            </div>
        </div>
    )
}

// 目標卡片元件
function GoalCard({ goal }) {
    const progress = (goal.currentAmount / goal.targetAmount) * 100
    const remaining = goal.targetAmount - goal.currentAmount
    const yearsLeft = (new Date(goal.targetDate) - new Date()) / (1000 * 60 * 60 * 24 * 365)

    return (
        <div className="card">
            <div className="flex items-start justify-between mb-4">
                <div>
                    <h3 className="text-xl font-bold">{goal.name}</h3>
                    <div className="flex items-center gap-4 mt-2 text-sm text-gray-600 dark:text-gray-400">
                        <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            <span>{goal.targetDate}</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <Target className="w-4 h-4" />
                            <span>目標 ${(goal.targetAmount / 1000000).toFixed(1)}M</span>
                        </div>
                    </div>
                </div>

                <span className={`px-3 py-1 rounded-full text-xs font-medium ${goal.onTrack
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                        : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                    }`}>
                    {goal.onTrack ? '進度正常' : '需加速'}
                </span>
            </div>

            {/* 進度條 */}
            <div className="mb-4">
                <div className="flex items-center justify-between text-sm mb-2">
                    <span className="font-medium">當前進度</span>
                    <span className="font-bold">{progress.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                    <div
                        className={`h-3 rounded-full transition-all ${goal.onTrack ? 'bg-green-500' : 'bg-orange-500'
                            }`}
                        style={{ width: `${Math.min(progress, 100)}%` }}
                    />
                </div>
            </div>

            {/* 數據指標 */}
            <div className="grid grid-cols-4 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">當前金額</div>
                    <div className="font-bold">${(goal.currentAmount / 1000000).toFixed(2)}M</div>
                </div>
                <div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">剩餘金額</div>
                    <div className="font-bold">${(remaining / 1000000).toFixed(2)}M</div>
                </div>
                <div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">月定期定額</div>
                    <div className="font-bold">${goal.monthlyContribution.toLocaleString()}</div>
                </div>
                <div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">所需報酬率</div>
                    <div className="font-bold">{goal.requiredReturn}%</div>
                </div>
            </div>
        </div>
    )
}
