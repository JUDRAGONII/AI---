// 情境分析與對沖策略生成器 (Scenario Analysis & Hedging Strategy Generator)
// 宏觀情境設定、損益模擬、對沖策略生成
import { useState } from 'react'
import {
    LineChart, Line, BarChart, Bar, ScatterChart, Scatter,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts'
import { Shield, TrendingDown, AlertCircle, Lightbulb, Activity } from 'lucide-react'

export default function ScenarioHedging() {
    const [selectedScenario, setSelectedScenario] = useState('recession')

    // 宏觀情境庫
    const scenarios = {
        recession: {
            name: '經濟衰退',
            description: '全球經濟增速放緩，企業獲利下降',
            assumptions: {
                gdpGrowth: -2.0,
                inflation: 1.5,
                interestRate: 2.0,
                stockMarket: -25,
                bondMarket: 15,
                commodities: -15
            }
        },
        inflation: {
            name: '通膨升溫',
            description: '物價持續上漲，央行激進升息',
            assumptions: {
                gdpGrowth: 1.5,
                inflation: 6.0,
                interestRate: 5.0,
                stockMarket: -15,
                bondMarket: -10,
                commodities: 25
            }
        },
        recovery: {
            name: '經濟復甦',
            description: '景氣回升，企業獲利成長',
            assumptions: {
                gdpGrowth: 4.0,
                inflation: 2.5,
                interestRate: 3.0,
                stockMarket: 20,
                bondMarket: -5,
                commodities: 10
            }
        },
        geopolitical: {
            name: '地緣政治危機',
            description: '國際衝突升級，避險情緒高漲',
            assumptions: {
                gdpGrowth: 0.5,
                inflation: 4.0,
                interestRate: 2.5,
                stockMarket: -20,
                bondMarket: 10,
                commodities: 30
            }
        }
    }

    const currentScenario = scenarios[selectedScenario]

    // 投資組合模擬損益
    const portfolioExposure = [
        { asset: '台股', currentWeight: 35, exposure: -8.75, hedged: -2.0 },
        { asset: '美股', currentWeight: 25, exposure: -6.25, hedged: -1.5 },
        { asset: '債券', currentWeight: 20, exposure: 3.0, hedged: 3.0 },
        { asset: '黃金', currentWeight: 10, exposure: 4.5, hedged: 4.5 },
        { asset: '現金', currentWeight: 10, exposure: 0, hedged: 0 }
    ]

    // 未對沖 vs 對沖後
    const totalExposure = portfolioExposure.reduce((sum, item) => sum + item.exposure, 0)
    const totalHedged = portfolioExposure.reduce((sum, item) => sum + item.hedged, 0)

    // AI推薦對沖策略
    const hedgingStrategies = [
        {
            id: 1,
            strategy: '購買看跌選擇權',
            target: '台股部位',
            cost: 15000,
            protection: '下跌20%以上保護',
            effectiveness: 85,
            recommendation: '高度推薦',
            implementation: '買入台指選擇權 Put 16000, 到期日3個月'
        },
        {
            id: 2,
            strategy: '增加黃金配置',
            target: '整體組合',
            cost: 0,
            protection: '降低整體波動',
            effectiveness: 65,
            recommendation: '建議執行',
            implementation: '將黃金配置從10%提升至15%，減少台股5%'
        },
        {
            id: 3,
            strategy: '反向ETF對沖',
            target: '美股部位',
            cost: 8000,
            protection: '部分對沖美股下跌',
            effectiveness: 70,
            recommendation: '可選執行',
            implementation: '買入反向ETF（如SQQQ）占美股部位10%'
        }
    ]

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold flex items-center gap-3">
                    <Shield className="w-8 h-8 text-blue-600" />
                    情境分析與對沖策略生成器
                </h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                    宏觀情境模擬 | 投資組合損益分析 | AI對沖策略推薦
                </p>
            </div>

            {/* 情境選擇 */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {Object.entries(scenarios).map(([key, scenario]) => (
                    <ScenarioCard
                        key={key}
                        id={key}
                        name={scenario.name}
                        description={scenario.description}
                        selected={selectedScenario === key}
                        onClick={() => setSelectedScenario(key)}
                    />
                ))}
            </div>

            {/* 情境假設 */}
            <div className="card">
                <h3 className="text-xl font-bold mb-4">情境假設</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <AssumptionBox label="GDP成長率" value={`${currentScenario.assumptions.gdpGrowth > 0 ? '+' : ''}${currentScenario.assumptions.gdpGrowth}%`} />
                    <AssumptionBox label="通膨率" value={`${currentScenario.assumptions.inflation}%`} />
                    <AssumptionBox label="利率" value={`${currentScenario.assumptions.interestRate}%`} />
                    <AssumptionBox label="股市變化" value={`${currentScenario.assumptions.stockMarket > 0 ? '+' : ''}${currentScenario.assumptions.stockMarket}%`} />
                    <AssumptionBox label="債市變化" value={`${currentScenario.assumptions.bondMarket > 0 ? '+' : ''}${currentScenario.assumptions.bondMarket}%`} />
                    <AssumptionBox label="商品變化" value={`${currentScenario.assumptions.commodities > 0 ? '+' : ''}${currentScenario.assumptions.commodities}%`} />
                </div>
            </div>

            {/* 損益模擬 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 未對沖損益 */}
                <div className="card">
                    <h3 className="text-xl font-bold mb-4">未對沖損益模擬</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={portfolioExposure}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="asset" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="exposure" name="損益%">
                                {portfolioExposure.map((entry, index) => (
                                    <Cell key={index} fill={entry.exposure >= 0 ? '#10b981' : '#ef4444'} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                    <div className="mt-4 text-center">
                        <div className={`text-3xl font-bold ${totalExposure >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {totalExposure >= 0 ? '+' : ''}{totalExposure.toFixed(2)}%
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">預期總損益</div>
                    </div>
                </div>

                {/* 對沖後損益 */}
                <div className="card">
                    <h3 className="text-xl font-bold mb-4">對沖後損益模擬</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={portfolioExposure}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="asset" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="hedged" name="損益%">
                                {portfolioExposure.map((entry, index) => (
                                    <Cell key={index} fill={entry.hedged >= 0 ? '#10b981' : '#ef4444'} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                    <div className="mt-4 text-center">
                        <div className={`text-3xl font-bold ${totalHedged >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {totalHedged >= 0 ? '+' : ''}{totalHedged.toFixed(2)}%
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">預期總損益（對沖後）</div>
                    </div>
                </div>
            </div>

            {/* 對沖效果 */}
            <div className="card bg-gradient-to-r from-blue-50 to-green-50 dark:from-blue-900/20 dark:to-green-900/20">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="text-lg font-bold mb-2">對沖保護效果</h3>
                        <p className="text-sm">
                            透過對沖策略，可將損失從 <strong className="text-red-600">{totalExposure.toFixed(2)}%</strong> 降低至
                            <strong className="text-orange-600"> {totalHedged.toFixed(2)}%</strong>
                        </p>
                    </div>
                    <div className="text-center">
                        <div className="text-4xl font-bold text-green-600">
                            {((totalExposure - totalHedged) / Math.abs(totalExposure) * 100).toFixed(0)}%
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">風險降低</div>
                    </div>
                </div>
            </div>

            {/* AI推薦對沖策略 */}
            <div className="space-y-4">
                <h3 className="text-xl font-bold flex items-center gap-2">
                    <Lightbulb className="w-6 h-6 text-blue-600" />
                    AI 推薦對沖策略
                </h3>
                {hedgingStrategies.map(strategy => (
                    <HedgingStrategyCard key={strategy.id} strategy={strategy} />
                ))}
            </div>
        </div>
    )
}

// 情境卡片
function ScenarioCard({ id, name, description, selected, onClick }) {
    return (
        <div
            onClick={onClick}
            className={`card cursor-pointer transition-all ${selected ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'hover:border-blue-400'
                }`}
        >
            <h4 className="font-bold mb-2">{name}</h4>
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

// 假設盒
function AssumptionBox({ label, value }) {
    return (
        <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{label}</div>
            <div className="font-bold text-lg">{value}</div>
        </div>
    )
}

// 對沖策略卡片
function HedgingStrategyCard({ strategy }) {
    const effectivenessColor = strategy.effectiveness >= 80 ? 'text-green-600' :
        strategy.effectiveness >= 65 ? 'text-blue-600' : 'text-orange-600'

    return (
        <div className="card">
            <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                        <h4 className="text-lg font-bold">{strategy.strategy}</h4>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${strategy.recommendation === '高度推薦' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' :
                                strategy.recommendation === '建議執行' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400' :
                                    'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                            }`}>
                            {strategy.recommendation}
                        </span>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                        <div className="text-sm">
                            <div className="text-gray-600 dark:text-gray-400">目標</div>
                            <div className="font-medium">{strategy.target}</div>
                        </div>
                        <div className="text-sm">
                            <div className="text-gray-600 dark:text-gray-400">成本</div>
                            <div className="font-medium">${strategy.cost.toLocaleString()}</div>
                        </div>
                        <div className="text-sm">
                            <div className="text-gray-600 dark:text-gray-400">保護程度</div>
                            <div className="font-medium">{strategy.protection}</div>
                        </div>
                        <div className="text-sm">
                            <div className="text-gray-600 dark:text-gray-400">有效性</div>
                            <div className={`font-bold ${effectivenessColor}`}>{strategy.effectiveness}%</div>
                        </div>
                    </div>

                    <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <div className="text-sm font-medium mb-1">執行方式</div>
                        <div className="text-sm">{strategy.implementation}</div>
                    </div>
                </div>
            </div>
        </div>
    )
}
