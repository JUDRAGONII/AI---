// 投資組合明細頁面 (Portfolio Details) - Treemap版本
import { useState } from 'react'
import { Treemap, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, Award, AlertCircle } from 'lucide-react'

export default function PortfolioDetails() {
    const [viewMode, setViewMode] = useState('holdings')
    const holdings = [
        { code: '2330', name: '台積電', shares: 1000, avgCost: 550, currentPrice: 580, value: 580000, weight: 35.2 },
        { code: '2317', name: '鴻海', shares: 2000, avgCost: 105, currentPrice: 110, value: 220000, weight: 13.4 },
        { code: '0050', name: '元大台灣50', shares: 500, avgCost: 130, currentPrice: 135, value: 67500, weight: 4.1 },
        { code: '2454', name: '聯發科', shares: 300, avgCost: 850, currentPrice: 880, value: 264000, weight: 16.0 },
        { code: '2882', name: '國泰金', shares: 3000, avgCost: 52, currentPrice: 55, value: 165000, weight: 10.0 },
        { code: '現金', name: '現金部位', shares: 1, avgCost: 350000, currentPrice: 350000, value: 350000, weight: 21.3 }
    ]

    const totalValue = holdings.reduce((sum, h) => sum + h.value, 0)
    const totalCost = holdings.reduce((sum, h) => sum + (h.shares * h.avgCost), 0)
    const totalReturn = ((totalValue - totalCost) / totalCost) * 100

    const sectorAllocation = [
        { sector: '半導體', value: 844000, percent: 51.2 },
        { sector: '金融', value: 165000, percent: 10.0 },
        { sector: '電子', value: 220000, percent: 13.4 },
        { sector: 'ETF', value: 67500, percent: 4.1 },
        { sector: '現金', value: 350000, percent: 21.3 }
    ]

    const performanceHistory = Array.from({ length: 12 }, (_, i) => ({ month: `${i + 1}月`, value: totalValue * (0.95 + i * 0.015), benchmark: totalValue * (0.97 + i * 0.01) }))
    const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#6b7280']

    return (
        <div className="p-8 space-y-8">
            <div className="flex items-center justify-between">
                <div><h1 className="text-3xl font-bold">投資組合明細</h1><p className="text-gray-600 dark:text-gray-400 mt-2">多層級視圖 | 績效歸因 | 風險分析</p></div>
                <div className="flex gap-2">
                    <button onClick={() => setViewMode('holdings')} className={`px-4 py-2 rounded-lg ${viewMode === 'holdings' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}>持股明細</button>
                    <button onClick={() => setViewMode('performance')} className={`px-4 py-2 rounded-lg ${viewMode === 'performance' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}>績效分析</button>
                    <button onClick={() => setViewMode('attribution')} className={`px-4 py-2 rounded-lg ${viewMode === 'attribution' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}>績效歸因</button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <SummaryCard label="總資產" value={`$${(totalValue / 1000000).toFixed(2)}M`} icon={<Award className="w-5 h-5" />} color="blue" />
                <SummaryCard label="總成本" value={`$${(totalCost / 1000000).toFixed(2)}M`} icon={<TrendingUp className="w-5 h-5" />} color="gray" />
                <SummaryCard label="損益" value={`$${((totalValue - totalCost) / 1000).toFixed(0)}K`} icon={totalReturn >= 0 ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />} color={totalReturn >= 0 ? "green" : "red"} />
                <SummaryCard label="報酬率" value={`${totalReturn >= 0 ? '+' : ''}${totalReturn.toFixed(2)}%`} icon={totalReturn >= 0 ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />} color={totalReturn >= 0 ? "green" : "red"} />
            </div>

            {viewMode === 'holdings' && (
                <>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div className="card">
                            <h2 className="text-xl font-bold mb-4">資產配置 (Treemap)</h2>
                            <ResponsiveContainer width="100%" height={300}>
                                <Treemap data={holdings.map((h, idx) => ({ name: `${h.code}\\n${h.name}`, size: h.value, weight: h.weight, fill: COLORS[idx % COLORS.length] }))} dataKey="size"
                                    content={(props) => {
                                        if (!props || !props.name) return null
                                        const { x, y, width, height, name, weight, fill } = props
                                        return (
                                            <g>
                                                <rect x={x} y={y} width={width} height={height} style={{ fill, stroke: '#fff', strokeWidth: 2 }} />
                                                {width > 60 && height > 40 && (
                                                    <>
                                                        <text x={x + width / 2} y={y + height / 2 - 5} textAnchor="middle" fill="#fff" fontSize={12} fontWeight="bold">{name.split('\\n')[0]}</text>
                                                        <text x={x + width / 2} y={y + height / 2 + 10} textAnchor="middle" fill="#fff" fontSize={11}>{weight?.toFixed(1)}%</text>
                                                    </>
                                                )}
                                            </g>
                                        )
                                    }} />
                            </ResponsiveContainer>
                        </div>

                        <div className="card">
                            <h2 className="text-xl font-bold mb-4">產業配置</h2>
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={sectorAllocation}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="sector" />
                                    <YAxis />
                                    <Tooltip />
                                    <Bar dataKey="percent" fill="#3b82f6" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    <div className="card">
                        <h2 className="text-xl font-bold mb-4">持股明細</h2>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead className="bg-gray-50 dark:bg-gray-800"><tr><th className="px-4 py-3 text-left">代碼</th><th className="px-4 py-3 text-left">名稱</th><th className="px-4 py-3 text-right">股數</th><th className="px-4 py-3 text-right">成本</th><th className="px-4 py-3 text-right">現價</th><th className="px-4 py-3 text-right">市值</th><th className="px-4 py-3 text-right">權重</th><th className="px-4 py-3 text-right">損益</th><th className="px-4 py-3 text-right">報酬率</th></tr></thead>
                                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">{holdings.map((holding) => {
                                    const pnl = (holding.currentPrice - holding.avgCost) * holding.shares
                                    const returnPct = ((holding.currentPrice - holding.avgCost) / holding.avgCost) * 100
                                    return <HoldingRow key={holding.code} holding={holding} pnl={pnl} returnPct={returnPct} />
                                })}</tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}

            {viewMode === 'performance' && (
                <>
                    <div className="card">
                        <h2 className="text-2xl font-bold mb-4">績效走勢圖</h2>
                        <ResponsiveContainer width="100%" height={350}>
                            <LineChart data={performanceHistory}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="month" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} name="投資組合" />
                                <Line type="monotone" dataKey="benchmark" stroke="#94a3b8" strokeWidth={2} name="基準指數" strokeDasharray="5 5" />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <RiskMetricCard label="Beta" value="0.95" description="低於大盤波動" />
                        <RiskMetricCard label="Sharpe Ratio" value="1.25" description="風險調整後報酬佳" />
                        <RiskMetricCard label="Max Drawdown" value="-12.3%" description="最大回撤" alert />
                    </div>
                </>
            )}

            {viewMode === 'attribution' && (
                <div className="card">
                    <h2 className="text-2xl font-bold mb-4">績效歸因分析</h2>
                    <div className="space-y-4">
                        <AttributionRow category="選股效應" contribution={3.2} />
                        <AttributionRow category="產業配置" contribution={1.8} />
                        <AttributionRow category="市場時機" contribution={-0.5} negative />
                        <AttributionRow category="其他因素" contribution={0.3} />
                    </div>
                    <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <p className="text-sm">💡 您的投資組合主要受益於<strong>選股效應</strong>（+3.2%）和<strong>產業配置</strong>（+1.8%），建議持續關注半導體產業動態。</p>
                    </div>
                </div>
            )}
        </div>
    )
}

function SummaryCard({ label, value, icon, color }) {
    const colorClasses = { blue: 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400', green: 'bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400', red: 'bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400', gray: 'bg-gray-50 dark:bg-gray-900/30 text-gray-600 dark:text-gray-400' }
    return <div className={`card ${colorClasses[color]}`}><div className="flex items-center gap-2 mb-2">{icon}<span className="text-sm font-medium">{label}</span></div><div className="text-2xl font-bold">{value}</div></div>
}

function HoldingRow({ holding, pnl, returnPct }) {
    const isProfitable = pnl >= 0
    if (holding.code === '現金') return (<tr className="hover:bg-gray-50 dark:hover:bg-gray-800/50"><td className="px-4 py-3 font-medium">{holding.code}</td><td className="px-4 py-3">{holding.name}</td><td className="px-4 py-3 text-right">-</td><td className="px-4 py-3 text-right">-</td><td className="px-4 py-3 text-right">-</td><td className="px-4 py-3 text-right">${holding.value.toLocaleString()}</td><td className="px-4 py-3 text-right">{holding.weight.toFixed(1)}%</td><td className="px-4 py-3 text-right">-</td><td className="px-4 py-3 text-right">-</td></tr>)
    return (<tr className="hover:bg-gray-50 dark:hover:bg-gray-800/50"><td className="px-4 py-3 font-medium">{holding.code}</td><td className="px-4 py-3">{holding.name}</td><td className="px-4 py-3 text-right">{holding.shares.toLocaleString()}</td><td className="px-4 py-3 text-right">${holding.avgCost}</td><td className="px-4 py-3 text-right">${holding.currentPrice}</td><td className="px-4 py-3 text-right">${holding.value.toLocaleString()}</td><td className="px-4 py-3 text-right">{holding.weight.toFixed(1)}%</td><td className={`px-4 py-3 text-right font-medium ${isProfitable ? 'text-green-600' : 'text-red-600'}`}>{isProfitable ? '+' : ''}{pnl.toLocaleString()}</td><td className={`px-4 py-3 text-right font-medium ${isProfitable ? 'text-green-600' : 'text-red-600'}`}>{isProfitable ? '+' : ''}{returnPct.toFixed(2)}%</td></tr>)
}

function RiskMetricCard({ label, value, description, alert = false }) {
    return (
        <div className={`card ${alert ? 'border-orange-200 dark:border-orange-700' : ''}`}>
            <div className="flex items-center gap-2 mb-2">{alert && <AlertCircle className="w-5 h-5 text-orange-600" />}<h3 className="font-bold">{label}</h3></div>
            <div className="text-3xl font-bold mb-1">{value}</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
        </div>
    )
}

function AttributionRow({ category, contribution, negative = false }) {
    const width = Math.abs(contribution) * 20
    return (
        <div>
            <div className="flex items-center justify-between mb-2"><span className="font-medium">{category}</span><span className={`font-bold ${negative ? 'text-red-600' : 'text-green-600'}`}>{contribution >= 0 ? '+' : ''}{contribution.toFixed(1)}%</span></div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2"><div className={`h-2 rounded-full ${negative ? 'bg-red-500' : 'bg-green-500'}`} style={{ width: `${width}%` }} /></div>
        </div>
    )
}
