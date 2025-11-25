// 目標導向路徑校準儀 (Goal-Oriented Path Calibrator)
// 目標達成率監控、偏離警示、校準建議
import { useState } from 'react'
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { Target, AlertCircle, TrendingUp, Calendar } from 'lucide-react'

export default function GoalCalibrator() {
    // 投資目標
    const goals = [
        {
            id: 1,
            name: '退休基金',
            targetAmount: 10000000,
            currentAmount: 3500000,
            targetDate: '2045-01-01',
            monthlyContribution: 30000,
            expectedReturn: 8.0,
            riskTolerance: 'moderate'
        },
        {
            id: 2,
            name: '購屋頭期款',
            targetAmount: 3000000,
            currentAmount: 1200000,
            targetDate: '2028-12-31',
            monthlyContribution: 25000,
            expectedReturn: 6.0,
            riskTolerance: 'conservative'
        }
    ]

    const [selectedGoal, setSelectedGoal] = useState(goals[0])

    // 計算達成率
    const achievementRate = (selectedGoal.currentAmount / selectedGoal.targetAmount * 100).toFixed(1)

    // 計算距離目標日期
    const daysToTarget = Math.ceil((new Date(selectedGoal.targetDate) - new Date()) / (1000 * 60 * 60 * 24))
    const yearsToTarget = (daysToTarget / 365).toFixed(1)

    // 計算所需報酬率
    const yearsRemaining = parseFloat(yearsToTarget)
    const requiredReturn = (Math.pow(selectedGoal.targetAmount / selectedGoal.currentAmount, 1 / yearsRemaining) - 1) * 100

    // 偏離度分析
    const deviation = (selectedGoal.expectedReturn - requiredReturn).toFixed(2)
    const isOnTrack = parseFloat(deviation) >= 0

    // 投資預測路徑
    const projectionData = Array.from({ length: Math.min(parseInt(yearsRemaining) + 1, 20) }, (_, i) => {
        const year = new Date().getFullYear() + i
        const currentPath = selectedGoal.currentAmount * Math.pow(1 + selectedGoal.expectedReturn / 100, i)
        const requiredPath = selectedGoal.currentAmount * Math.pow(1 + requiredReturn / 100, i)
        const targetPath = i === parseInt(yearsRemaining) ? selectedGoal.targetAmount : null

        return {
            year: year,
            current: currentPath,
            required: requiredPath,
            target: targetPath
        }
    })

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <Target className="w-8 h-8 text-blue-600" />
                        目標導向路徑校準儀
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        投資目標追蹤 | 偏離警示 | 動態校準建議
                    </p>
                </div>

                <div className="flex gap-2">
                    {goals.map(goal => (
                        <button
                            key={goal.id}
                            onClick={() => setSelectedGoal(goal)}
                            className={`px-4 py-2 rounded-lg ${selectedGoal.id === goal.id ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                        >
                            {goal.name}
                        </button>
                    ))}
                </div>
            </div>

            {/* 目標概覽 */}
            <div className="card bg-gradient-to-r from-blue-50 to-green-50 dark:from-blue-900/20 dark:to-green-900/20">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">目標金額</div>
                        <div className="text-2xl font-bold">${(selectedGoal.targetAmount / 1000000).toFixed(1)}M</div>
                    </div>
                    <div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">當前金額</div>
                        <div className="text-2xl font-bold text-blue-600">${(selectedGoal.currentAmount / 1000000).toFixed(1)}M</div>
                    </div>
                    <div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">達成率</div>
                        <div className={`text-2xl font-bold ${isOnTrack ? 'text-green-600' : 'text-orange-600'}`}>
                            {achievementRate}%
                        </div>
                    </div>
                    <div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">剩餘時間</div>
                        <div className="text-2xl font-bold">{yearsToTarget} 年</div>
                    </div>
                </div>
            </div>

            {/* 路徑狀態 */}
            <div className={`card ${isOnTrack ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-700' : 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-700'} border-2`}>
                <div className="flex items-start gap-4">
                    {isOnTrack ? (
                        <TrendingUp className="w-8 h-8 text-green-600 flex-shrink-0" />
                    ) : (
                        <AlertCircle className="w-8 h-8 text-orange-600 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                        <h3 className={`text-xl font-bold mb-2 ${isOnTrack ? 'text-green-800 dark:text-green-300' : 'text-orange-800 dark:text-orange-300'}`}>
                            {isOnTrack ? '✅ 投資進度領先目標' : '⚠️ 投資進度落後，需要調整'}
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                            <div>
                                <span className="font-medium">預期報酬率：</span>
                                <span className="ml-2 font-bold text-lg">{selectedGoal.expectedReturn.toFixed(1)}%</span>
                            </div>
                            <div>
                                <span className="font-medium">所需報酬率：</span>
                                <span className="ml-2 font-bold text-lg">{requiredReturn.toFixed(1)}%</span>
                            </div>
                        </div>
                        <div className="mt-2">
                            <span className="font-medium">偏離度：</span>
                            <span className={`ml-2 font-bold text-lg ${isOnTrack ? 'text-green-600' : 'text-red-600'}`}>
                                {deviation > 0 ? '+' : ''}{deviation}%
                            </span>
                            {isOnTrack ? (
                                <span className="ml-2 text-sm">{' '}（超前 {Math.abs(deviation)}%，可考慮降低風險）</span>
                            ) : (
                                <span className="ml-2 text-sm">{' '}（落後 {Math.abs(deviation)}%，需要提高報酬率）</span>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* 投資路徑圖 */}
            <div className="card">
                <h3 className="text-xl font-bold mb-4">投資路徑預測</h3>
                <ResponsiveContainer width="100%" height={350}>
                    <LineChart data={projectionData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" />
                        <YAxis />
                        <Tooltip formatter={(value) => `$${(value / 1000000).toFixed(2)}M`} />
                        <Legend />
                        <Line type="monotone" dataKey="current" stroke="#3b82f6" strokeWidth={2} name="預期路徑" />
                        <Line type="monotone" dataKey="required" stroke="#f59e0b" strokeWidth={2} strokeDasharray="5 5" name="所需路徑" />
                        <Line type="monotone" dataKey="target" stroke="#10b981" strokeWidth={3} name="目標" connectNulls={false} />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* 校準建議 */}
            <div className="card">
                <h3 className="text-xl font-bold mb-4">AI 校準建議</h3>
                <div className="space-y-4">
                    {isOnTrack ? (
                        <>
                            <CalibrationAction
                                priority="low"
                                title="降低風險配置"
                                description={`目前預期報酬率(${selectedGoal.expectedReturn}%)已超過所需(${requiredReturn.toFixed(1)}%)，可考慮降低股票比重，增加債券配置以降低風險`}
                            />
                            <CalibrationAction
                                priority="low"
                                title="維持現狀"
                                description="繼續執行當前策略，定期檢視進度即可"
                            />
                        </>
                    ) : (
                        <>
                            <CalibrationAction
                                priority="high"
                                title="增加每月投入"
                                description={`建議每月投入從 $${selectedGoal.monthlyContribution.toLocaleString()} 增加至 $${(selectedGoal.monthlyContribution * 1.3).toLocaleString()}（+30%）`}
                            />
                            <CalibrationAction
                                priority="high"
                                title="提升投資報酬率"
                                description={`考慮調整資產配置，增加成長股比重，目標報酬率從 ${selectedGoal.expectedReturn}% 提升至 ${(selectedGoal.expectedReturn + 2).toFixed(1)}%`}
                            />
                            <CalibrationAction
                                priority="medium"
                                title="延後目標日期"
                                description={`若無法增加投入或提高報酬，建議將目標日期延後 ${Math.ceil(Math.abs(deviation) / 2)} 年`}
                            />
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}

// 校準行動
function CalibrationAction({ priority, title, description }) {
    const priorityConfig = {
        high: { bg: 'bg-red-50 dark:bg-red-900/20', border: 'border-red-200 dark:border-red-700', badge: 'bg-red-500 text-white' },
        medium: { bg: 'bg-orange-50 dark:bg-orange-900/20', border: 'border-orange-200 dark:border-orange-700', badge: 'bg-orange-500 text-white' },
        low: { bg: 'bg-blue-50 dark:bg-blue-900/20', border: 'border-blue-200 dark:border-blue-700', badge: 'bg-blue-500 text-white' }
    }

    const config = priorityConfig[priority]

    return (
        <div className={`p-4 rounded-lg border-2 ${config.bg} ${config.border}`}>
            <div className="flex items-start gap-3">
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${config.badge}`}>
                    {priority === 'high' ? '高優先' : priority === 'medium' ? '中優先' : '低優先'}
                </span>
                <div className="flex-1">
                    <div className="font-bold mb-1">{title}</div>
                    <div className="text-sm">{description}</div>
                </div>
            </div>
        </div>
    )
}
