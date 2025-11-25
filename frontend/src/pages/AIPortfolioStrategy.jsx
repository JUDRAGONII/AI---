// AI 投資組合策略頁面
// 風險屬性評估、動態資產配置、增減倉建議
import { useState } from 'react'
import {
    PieChart, Pie, Cell, BarChart, Bar, LineChart, Line,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis
} from 'recharts'
import { Target, TrendingUp, Shield, Zap } from 'lucide-react'

export default function AIPortfolioStrategy() {
    const [riskProfile, setRiskProfile] = useState('moderate')

    // 風險屬性評估
    const riskAssessment = {
        aggressive: { label: '積極型', color: 'red', stocks: 80, bonds: 10, cash: 10 },
        moderate: { label: '穩健型', color: 'blue', stocks: 60, bonds: 25, cash: 15 },
        conservative: { label: '保守型', color: 'green', stocks: 30, bonds: 50, cash: 20 }
    }

    const currentProfile = riskAssessment[riskProfile]

    // 當前配置
    const currentAllocation = [
        { name: '股票', value: 65, target: currentProfile.stocks },
        { name: '債券', value: 20, target: currentProfile.bonds },
        { name: '現金', value: 15, target: currentProfile.cash }
    ]

    // AI 建議調整
    const rebalanceActions = [
        {
            action: '減持',
            asset: '台積電 (2330)',
            current: 20,
            target: 15,
            change: -5,
            reason: '持股佔比過高，建議降低單一標的風險',
            priority: 'high'
        },
        {
            action: '增持',
            asset: '債券ETF (00679B)',
            current: 20,
            target: 25,
            change: +5,
            reason: '債券比例偏低，增加可降低投資組合波動',
            priority: 'medium'
        },
        {
            action: '新增',
            asset: '美股ETF (00646)',
            current: 0,
            target: 10,
            change: +10,
            reason: '增加美股曝險，提升國際分散化',
            priority: 'medium'
        },
        {
            action: '減持',
            asset: '現金',
            current: 15,
            target: 15,
            change: 0,
            reason: '現金比例適中，無需調整',
            priority: 'low'
        }
    ]

    // 風險收益雷達圖
    const riskReturnRadar = [
        { metric: '預期報酬', current: 75, target: 85 },
        { metric: '風險控制', current: 60, target: 75 },
        { metric: '流動性', current: 80, target: 70 },
        { metric: '分散度', current: 50, target: 80 },
        { metric: '成本效率', current: 70, target: 75 },
        { metric: '稅務優化', current: 65, target: 70 }
    ]

    const COLORS = ['#3b82f6', '#10b981', '#f59e0b']

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">AI 投資組合策略</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                    智慧風險評估 | 動態資產配置 | 個人化投資建議
                </p>
            </div>

            {/* 風險屬性選擇 */}
            <div className="card">
                <h2 className="text-xl font-bold mb-4">您的風險屬性</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <RiskProfileCard
                        type="conservative"
                        label="保守型"
                        description="追求穩定收益，風險承受度低"
                        selected={riskProfile === 'conservative'}
                        onClick={() => setRiskProfile('conservative')}
                    />
                    <RiskProfileCard
                        type="moderate"
                        label="穩健型"
                        description="平衡風險與報酬"
                        selected={riskProfile === 'moderate'}
                        onClick={() => setRiskProfile('moderate')}
                    />
                    <RiskProfileCard
                        type="aggressive"
                        label="積極型"
                        description="追求高報酬，可承受高波動"
                        selected={riskProfile === 'aggressive'}
                        onClick={() => setRiskProfile('aggressive')}
                    />
                </div>
            </div>

            {/* 資產配置分析 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 當前 vs 目標配置 */}
                <div className="card">
                    <h2 className="text-xl font-bold mb-4">資產配置對比</h2>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={currentAllocation}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis unit="%" />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="value" fill="#3b82f6" name="當前配置" />
                            <Bar dataKey="target" fill="#10b981" name="目標配置" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* 風險收益雷達圖 */}
                <div className="card">
                    <h2 className="text-xl font-bold mb-4">投資組合健檢</h2>
                    <ResponsiveContainer width="100%" height={300}>
                        <RadarChart data={riskReturnRadar}>
                            <PolarGrid />
                            <PolarAngleAxis dataKey="metric" />
                            <PolarRadiusAxis angle={90} domain={[0, 100]} />
                            <Radar name="當前" dataKey="current" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                            <Radar name="目標" dataKey="target" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                            <Legend />
                        </RadarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* AI 調整建議 */}
            <div className="card">
                <div className="flex items-center gap-2 mb-4">
                    <Zap className="w-6 h-6 text-blue-600" />
                    <h2 className="text-xl font-bold">AI 智慧建議</h2>
                </div>
                <div className="space-y-3">
                    {rebalanceActions.map((item, index) => (
                        <RebalanceActionCard key={index} action={item} />
                    ))}
                </div>
            </div>

            {/* 執行摘要 */}
            <div className="card bg-gradient-to-r from-blue-50 to-green-50 dark:from-blue-900/20 dark:to-green-900/20">
                <h3 className="font-bold text-lg mb-3">📋 執行摘要</h3>
                <div className="space-y-2 text-sm">
                    <p>✅ 根據您的<strong>{currentProfile.label}</strong>風險屬性，AI 分析建議進行 <strong>3 項調整</strong></p>
                    <p>✅ 調整後預期年化報酬：<strong className="text-green-600">+10.5%</strong></p>
                    <p>✅ 預期波動率：<strong className="text-blue-600">12.3%</strong>（符合風險承受度）</p>
                    <p>✅ 夏普比率預期從 <strong>0.75</strong> 提升至 <strong>1.05</strong></p>
                    <p>💡 建議在未來 <strong>2週</strong> 內完成調整，分批執行以降低市場衝擊成本</p>
                </div>
            </div>
        </div>
    )
}

// 風險屬性卡片
function RiskProfileCard({ type, label, description, selected, onClick }) {
    const colors = {
        conservative: 'border-green-500',
        moderate: 'border-blue-500',
        aggressive: 'border-red-500'
    }

    return (
        <div
            onClick={onClick}
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${selected ? colors[type] + ' bg-blue-50 dark:bg-blue-900/20' : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
                }`}
        >
            <div className="flex items-center gap-2 mb-2">
                <Shield className="w-5 h-5" />
                <h3 className="font-bold">{label}</h3>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
            {selected && (
                <div className="mt-2">
                    <span className="text-xs px-2 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400">
                        已選擇
                    </span>
                </div>
            )}
        </div>
    )
}

// 再平衡動作卡片
function RebalanceActionCard({ action }) {
    const actionColors = {
        增持: 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/30',
        減持: 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/30',
        新增: 'text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/30',
        維持: 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700'
    }

    const priorityColors = {
        high: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
        medium: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400',
        low: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
    }

    const priorityLabels = {
        high: '高',
        medium: '中',
        low: '低'
    }

    return (
        <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${actionColors[action.action]}`}>
                        {action.action}
                    </span>
                    <h4 className="font-bold">{action.asset}</h4>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${priorityColors[action.priority]}`}>
                    優先度: {priorityLabels[action.priority]}
                </span>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-3 text-sm">
                <div>
                    <span className="text-gray-600 dark:text-gray-400">當前: </span>
                    <span className="font-medium">{action.current}%</span>
                </div>
                <div>
                    <span className="text-gray-600 dark:text-gray-400">目標: </span>
                    <span className="font-medium">{action.target}%</span>
                </div>
                <div>
                    <span className="text-gray-600 dark:text-gray-400">調整: </span>
                    <span className={`font-medium ${action.change > 0 ? 'text-green-600' : action.change < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                        {action.change > 0 ? '+' : ''}{action.change}%
                    </span>
                </div>
            </div>

            <p className="text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 p-2 rounded">
                💡 {action.reason}
            </p>
        </div>
    )
}
