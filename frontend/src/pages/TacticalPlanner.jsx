// 戰術目標規劃器 (Tactical Goal Planner)
// 短期作戰計畫設定、作戰報告室、停損停利追蹤
import { useState } from 'react'
import { Target, Calendar, Shield, TrendingDown, TrendingUp, CheckCircle } from 'lucide-react'

export default function TacticalPlanner() {
    const [activeTab, setActiveTab] = useState('planning') // planning, monitoring, completed

    // 戰術計畫列表
    const [tacticalPlans, setTacticalPlans] = useState([
        {
            id: 1,
            code: '2330',
            name: '台積電',
            action: 'buy',
            status: 'active',
            entry: 580,
            target: 620,
            stopLoss: 550,
            currentPrice: 592,
            shares: 100,
            startDate: '2024-11-20',
            targetDate: '2024-12-20',
            reason: '3奈米製程量產加速，AI晶片需求強勁',
            progress: 40,
            profit: 1200,
            profitPercent: 2.07
        },
        {
            id: 2,
            code: '2603',
            name: '長榮',
            action: 'buy',
            status: 'active',
            entry: 138,
            target: 165,
            stopLoss: 128,
            currentPrice: 145,
            shares: 500,
            startDate: '2024-11-15',
            targetDate: '2024-12-31',
            reason: '運價觸底反彈，紅海危機推升運費',
            progress: 25.9,
            profit: 3500,
            profitPercent: 5.07
        },
        {
            id: 3,
            code: '2454',
            name: '聯發科',
            action: 'sell',
            status: 'completed',
            entry: 850,
            target: 900,
            stopLoss: 820,
            exitPrice: 905,
            shares: 50,
            startDate: '2024-11-01',
            endDate: '2024-11-18',
            reason: '天璣9300獲小米採用，技術面突破',
            profit: 2750,
            profitPercent: 6.47,
            outcome: 'target_hit'
        }
    ])

    const activePlans = tacticalPlans.filter(p => p.status === 'active')
    const completedPlans = tacticalPlans.filter(p => p.status === 'completed')

    // 計算目標達成進度
    const calculateProgress = (plan) => {
        if (plan.action === 'buy') {
            return ((plan.currentPrice - plan.entry) / (plan.target - plan.entry) * 100).toFixed(1)
        } else {
            return ((plan.entry - plan.currentPrice) / (plan.entry - plan.target) * 100).toFixed(1)
        }
    }

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold flex items-center gap-3">
                    <Target className="w-8 h-8 text-blue-600" />
                    戰術目標規劃器
                </h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                    短期作戰計畫 | 停損停利追蹤 | 作戰報告室
                </p>
            </div>

            {/* 統計卡片 */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <StatCard label="進行中計畫" value={activePlans.length} color="blue" />
                <StatCard label="總投入資金" value={`$${(activePlans.reduce((sum, p) => sum + p.entry * p.shares, 0) / 1000).toFixed(0)}K`} color="purple" />
                <StatCard label="浮動損益" value={`$${(activePlans.reduce((sum, p) => sum + p.profit, 0) / 1000).toFixed(1)}K`} color="green" positive />
                <StatCard label="已完成計畫" value={completedPlans.length} color="gray" />
            </div>

            {/* 分頁 */}
            <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
                <button
                    onClick={() => setActiveTab('planning')}
                    className={`px-6 py-3 font-medium ${activeTab === 'planning' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600 dark:text-gray-400'}`}
                >
                    新建計畫
                </button>
                <button
                    onClick={() => setActiveTab('monitoring')}
                    className={`px-6 py-3 font-medium ${activeTab === 'monitoring' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600 dark:text-gray-400'}`}
                >
                    監控中 ({activePlans.length})
                </button>
                <button
                    onClick={() => setActiveTab('completed')}
                    className={`px-6 py-3 font-medium ${activeTab === 'completed' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600 dark:text-gray-400'}`}
                >
                    已完成 ({completedPlans.length})
                </button>
            </div>

            {/* 內容區域 */}
            {activeTab === 'planning' && <PlanningForm />}
            {activeTab === 'monitoring' && (
                <div className="space-y-4">
                    {activePlans.map(plan => (
                        <ActivePlanCard key={plan.id} plan={plan} />
                    ))}
                    {activePlans.length === 0 && (
                        <div className="card text-center py-12">
                            <p className="text-gray-500">目前沒有進行中的計畫</p>
                        </div>
                    )}
                </div>
            )}
            {activeTab === 'completed' && (
                <div className="space-y-4">
                    {completedPlans.map(plan => (
                        <CompletedPlanCard key={plan.id} plan={plan} />
                    ))}
                </div>
            )}
        </div>
    )
}

// 統計卡片
function StatCard({ label, value, color, positive = false }) {
    const colorClasses = {
        blue: 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400',
        purple: 'bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-400',
        green: 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400',
        gray: 'bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
    }

    return (
        <div className={`card ${colorClasses[color]}`}>
            <div className="text-sm mb-1">{label}</div>
            <div className={`text-3xl font-bold ${positive ? 'text-green-600' : ''}`}>{value}</div>
        </div>
    )
}

// 新建計畫表單
function PlanningForm() {
    return (
        <div className="card">
            <h3 className="text-xl font-bold mb-4">建立新的戰術計畫</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-medium mb-2">股票代碼</label>
                    <input type="text" placeholder="2330" className="w-full px-4 py-2 border rounded-lg dark:bg-gray-800" />
                </div>
                <div>
                    <label className="block text-sm font-medium mb-2">操作類型</label>
                    <select className="w-full px-4 py-2 border rounded-lg dark:bg-gray-800">
                        <option>買入</option>
                        <option>賣出</option>
                    </select>
                </div>
                <div>
                    <label className="block text-sm font-medium mb-2">進場價格</label>
                    <input type="number" placeholder="580" className="w-full px-4 py-2 border rounded-lg dark:bg-gray-800" />
                </div>
                <div>
                    <label className="block text-sm font-medium mb-2">目標價格</label>
                    <input type="number" placeholder="620" className="w-full px-4 py-2 border rounded-lg dark:bg-gray-800" />
                </div>
                <div>
                    <label className="block text-sm font-medium mb-2">停損價格</label>
                    <input type="number" placeholder="550" className="w-full px-4 py-2 border rounded-lg dark:bg-gray-800" />
                </div>
                <div>
                    <label className="block text-sm font-medium mb-2">股數</label>
                    <input type="number" placeholder="100" className="w-full px-4 py-2 border rounded-lg dark:bg-gray-800" />
                </div>
                <div className="md:col-span-2">
                    <label className="block text-sm font-medium mb-2">操作理由</label>
                    <textarea placeholder="說明您的交易邏輯..." rows={3} className="w-full px-4 py-2 border rounded-lg dark:bg-gray-800" />
                </div>
            </div>
            <div className="mt-4 flex justify-end">
                <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    建立計畫
                </button>
            </div>
        </div>
    )
}

// 進行中計畫卡片
function ActivePlanCard({ plan }) {
    const progress = parseFloat(((plan.currentPrice - plan.entry) / (plan.target - plan.entry) * 100).toFixed(1))
    const isProfit = plan.profit > 0
    const hitStopLoss = plan.currentPrice <= plan.stopLoss
    const hitTarget = plan.currentPrice >= plan.target

    return (
        <div className={`card ${hitStopLoss ? 'border-2 border-red-500' : hitTarget ? 'border-2 border-green-500' : ''}`}>
            <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-bold">{plan.code} - {plan.name}</h3>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${plan.action === 'buy' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                                : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                            }`}>
                            {plan.action === 'buy' ? '做多' : '做空'}
                        </span>
                        {hitStopLoss && (
                            <span className="px-3 py-1 rounded-full text-sm font-medium bg-red-500 text-white animate-pulse">
                                ⚠️ 觸及停損
                            </span>
                        )}
                        {hitTarget && (
                            <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-500 text-white">
                                ✅ 達成目標
                            </span>
                        )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{plan.reason}</p>

                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-3">
                        <PriceBox label="進場" price={plan.entry} />
                        <PriceBox label="當前" price={plan.currentPrice} highlight />
                        <PriceBox label="目標" price={plan.target} positive />
                        <PriceBox label="停損" price={plan.stopLoss} negative />
                        <PriceBox label="股數" price={plan.shares} unit="股" />
                    </div>

                    <div className="mb-3">
                        <div className="flex items-center justify-between text-sm mb-1">
                            <span>達成進度</span>
                            <span className="font-bold">{progress.toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                            <div
                                className={`h-3 rounded-full ${progress >= 100 ? 'bg-green-600' : progress >= 0 ? 'bg-blue-600' : 'bg-red-600'}`}
                                style={{ width: `${Math.min(Math.max(progress, 0), 100)}%` }}
                            />
                        </div>
                    </div>

                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className={`text-lg font-bold ${isProfit ? 'text-green-600' : 'text-red-600'}`}>
                                {isProfit ? '+' : ''}{plan.profit.toLocaleString()} ({isProfit ? '+' : ''}{plan.profitPercent}%)
                            </div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">
                                <Calendar className="w-4 h-4 inline mr-1" />
                                {plan.startDate} → {plan.targetDate}
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <button className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm">
                                手動平倉
                            </button>
                            <button className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg text-sm">
                                編輯
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

// 已完成計畫卡片
function CompletedPlanCard({ plan }) {
    const isProfit = plan.profit > 0

    return (
        <div className="card bg-gray-50 dark:bg-gray-800">
            <div className="flex items-center justify-between">
                <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                        <CheckCircle className="w-5 h-5 text-green-600" />
                        <h3 className="text-lg font-bold">{plan.code} - {plan.name}</h3>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${isProfit ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                                : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                            }`}>
                            {plan.outcome === 'target_hit' ? '達成目標' : plan.outcome === 'stop_loss' ? '停損出場' : '手動平倉'}
                        </span>
                    </div>

                    <div className="grid grid-cols-5 gap-3 mb-2">
                        <div className="text-sm">
                            <div className="text-gray-600 dark:text-gray-400">進場</div>
                            <div className="font-medium">${plan.entry}</div>
                        </div>
                        <div className="text-sm">
                            <div className="text-gray-600 dark:text-gray-400">出場</div>
                            <div className="font-medium">${plan.exitPrice}</div>
                        </div>
                        <div className="text-sm">
                            <div className="text-gray-600 dark:text-gray-400">股數</div>
                            <div className="font-medium">{plan.shares}股</div>
                        </div>
                        <div className="text-sm">
                            <div className="text-gray-600 dark:text-gray-400">損益</div>
                            <div className={`font-bold ${isProfit ? 'text-green-600' : 'text-red-600'}`}>
                                {isProfit ? '+' : ''}{plan.profit}
                            </div>
                        </div>
                        <div className="text-sm">
                            <div className="text-gray-600 dark:text-gray-400">報酬率</div>
                            <div className={`font-bold ${isProfit ? 'text-green-600' : 'text-red-600'}`}>
                                {isProfit ? '+' : ''}{plan.profitPercent}%
                            </div>
                        </div>
                    </div>

                    <div className="text-xs text-gray-600 dark:text-gray-400">
                        {plan.startDate} → {plan.endDate}
                    </div>
                </div>
            </div>
        </div>
    )
}

// 價格盒
function PriceBox({ label, price, positive = false, negative = false, highlight = false, unit = '' }) {
    return (
        <div className={`p-2 rounded ${highlight ? 'bg-blue-50 dark:bg-blue-900/20' : 'bg-gray-50 dark:bg-gray-800'}`}>
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{label}</div>
            <div className={`font-bold ${positive ? 'text-green-600' : negative ? 'text-red-600' : ''}`}>
                {unit ? price + unit : `$${price}`}
            </div>
        </div>
    )
}
