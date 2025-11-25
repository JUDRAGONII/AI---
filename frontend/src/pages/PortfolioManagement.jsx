// 投資組合管理頁面 - 支援多幣別與現金
import { useState } from 'react'
import { Treemap, ResponsiveContainer } from 'recharts'
import { Plus, TrendingUp, TrendingDown, DollarSign, Target, AlertCircle, Wallet, Building2 } from 'lucide-react'

const TREEMAP_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#ec4899']
const USD_TO_TWD = 31.5 // 美金對台幣匯率

export default function PortfolioManagement() {
    const [portfolioData] = useState({
        // 券商帳戶（含現金）
        accounts: [
            { id: 'tw1', broker: '元大證券', market: 'TW', cash: 150000, currency: 'TWD' },
            { id: 'tw2', broker: '富邦證券', market: 'TW', cash: 80000, currency: 'TWD' },
            { id: 'us1', broker: 'Charles Schwab', market: 'US', cash: 5000, currency: 'USD' }
        ],
        // 持股明細
        holdings: [
            { code: '2330', name: '台積電', shares: 1000, avgCost: 550, currentPrice: 580, value: 580000, profit: 30000, profitPercent: 5.45, currency: 'TWD', accountId: 'tw1' },
            { code: '2317', name: '鴻海', shares: 8000, avgCost: 105, currentPrice: 120, value: 960000, profit: 120000, profitPercent: 14.29, currency: 'TWD', accountId: 'tw1' },
            { code: '2454', name: '聯發科', shares: 500, avgCost: 800, currentPrice: 850, value: 425000, profit: 25000, profitPercent: 6.25, currency: 'TWD', accountId: 'tw2' },
            { code: '2882', name: '國泰金', shares: 10000, avgCost: 45, currentPrice: 52, value: 520000, profit: 70000, profitPercent: 15.56, currency: 'TWD', accountId: 'tw2' },
            { code: 'AAPL', name: 'Apple Inc.', shares: 50, avgCost: 180, currentPrice: 195, value: 9750, profit: 750, profitPercent: 8.33, currency: 'USD', accountId: 'us1' },
            { code: 'TSLA', name: 'Tesla Inc.', shares: 20, avgCost: 240, currentPrice: 260, value: 5200, profit: 400, profitPercent: 8.33, currency: 'USD', accountId: 'us1' },
        ]
    })

    // 計算總資產（全部轉為TWD）
    const calculateTotals = () => {
        const totalCashTWD = portfolioData.accounts.reduce((sum, acc) =>
            sum + (acc.currency === 'USD' ? acc.cash * USD_TO_TWD : acc.cash), 0)

        const totalStockTWD = portfolioData.holdings.reduce((sum, h) =>
            sum + (h.currency === 'USD' ? h.value * USD_TO_TWD : h.value), 0)

        const totalCostTWD = portfolioData.holdings.reduce((sum, h) =>
            sum + (h.currency === 'USD' ? h.avgCost * h.shares * USD_TO_TWD : h.avgCost * h.shares), 0)

        const totalProfitTWD = portfolioData.holdings.reduce((sum, h) =>
            sum + (h.currency === 'USD' ? h.profit * USD_TO_TWD : h.profit), 0)

        return {
            totalValue: totalCashTWD + totalStockTWD,
            totalCash: totalCashTWD,
            totalStock: totalStockTWD,
            totalCost: totalCashTWD + totalCostTWD,
            totalProfit: totalProfitTWD,
            profitPercent: ((totalProfitTWD / totalCostTWD) * 100 || 0)
        }
    }

    const totals = calculateTotals()

    // Treemap資料（包含現金）
    const treemapData = [
        ...portfolioData.holdings.map((h, idx) => ({
            name: `${h.code}\n${h.name}`,
            size: h.currency === 'USD' ? h.value * USD_TO_TWD : h.value,
            currency: h.currency,
            value: h.value,
            profit: h.profitPercent,
            fill: TREEMAP_COLORS[idx % TREEMAP_COLORS.length]
        })),
        // 現金作為一個方塊
        {
            name: '現金\nCash',
            size: calculateTotals().totalCash,
            currency: 'TWD',
            value: calculateTotals().totalCash,
            profit: 0,
            fill: '#94a3b8' // 灰色
        }
    ]

    const riskMetrics = { avgReturn: '10.70', volatility: '4.37', sharpeRatio: '2.45', maxDrawdown: 5.2 }

    const CustomContent = (props) => {
        if (!props || !props.name) return null
        const { x, y, width, height, name, currency, value, profit, fill } = props
        return (
            <g>
                <rect x={x} y={y} width={width} height={height} style={{ fill, stroke: '#fff', strokeWidth: 2 }} />
                {width > 60 && height > 40 && (
                    <>
                        <text x={x + width / 2} y={y + height / 2 - 15} textAnchor="middle" fill="#fff" fontSize={13} fontWeight="bold">{name.split('\n')[0]}</text>
                        <text x={x + width / 2} y={y + height / 2} textAnchor="middle" fill="#fff" fontSize={11}>{currency === 'USD' ? `$${value?.toFixed(0)}` : `NT$${(value / 1000)?.toFixed(0)}K`}</text>
                        <text x={x + width / 2} y={y + height / 2 + 15} textAnchor="middle" fill="#fff" fontSize={10}>{profit >= 0 ? '+' : ''}{profit?.toFixed(1)}%</text>
                    </>
                )}
            </g>
        )
    }

    return (
        <div className="p-8 space-y-8">
            <div className="flex items-center justify-between">
                <div><h1 className="text-3xl font-bold">投資組合管理</h1><p className="text-gray-600 dark:text-gray-400 mt-2">多幣別持股、現金與績效分析</p></div>
                <button className="btn btn-primary flex items-center gap-2"><Plus className="w-5 h-5" />新增持股</button>
            </div>

            {/* 總覽卡片（含現金） */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
                <SummaryCard title="總資產" value={totals.totalValue} icon={<DollarSign className="w-5 h-5" />} isCurrency />
                <SummaryCard title="股票市值" value={totals.totalStock} icon={<TrendingUp className="w-5 h-5" />} isCurrency />
                <SummaryCard title="帳戶現金" value={totals.totalCash} icon={<Wallet className="w-5 h-5" />} isCurrency />
                <SummaryCard title="總成本" value={totals.totalCost} icon={<Target className="w-5 h-5" />} isCurrency />
                <SummaryCard title="總損益" value={totals.totalProfit} change={totals.profitPercent} icon={totals.totalProfit >= 0 ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />} isCurrency showChange />
            </div>

            {/* Treemap與風險指標 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card">
                    <h2 className="text-2xl font-bold mb-4">資產配置 (含現金)</h2>
                    <ResponsiveContainer width="100%" height={350}>
                        <Treemap data={treemapData} dataKey="size" content={<CustomContent />} />
                    </ResponsiveContainer>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">*美元資產已按 USD/TWD = {USD_TO_TWD} 換算</p>
                </div>

                <div className="card">
                    <h2 className="text-2xl font-bold mb-4">風險指標</h2>
                    <div className="space-y-4">
                        <RiskRow label="平均報酬率" value={`${riskMetrics.avgReturn}%`} />
                        <RiskRow label="波動率" value={`${riskMetrics.volatility}%`} />
                        <RiskRow label="夏普比率" value={riskMetrics.sharpeRatio} />
                        <RiskRow label="最大回撤" value={`${riskMetrics.maxDrawdown}%`} />
                    </div>
                    <div className="mt-6 p-4 rounded-lg bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700">
                        <div className="flex items-start gap-2">
                            <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                            <div className="text-sm"><p className="font-medium text-blue-900 dark:text-blue-100 mb-1">風險評估</p><p className="text-blue-800 dark:text-blue-200">投資組合風險調整後報酬表現優異</p></div>
                        </div>
                    </div>
                </div>
            </div>

            {/* 券商帳戶現金餘額 */}
            <div className="card">
                <h2 className="text-2xl font-bold mb-4 flex items-center gap-2"><Building2 className="w-6 h-6" />券商帳戶現金</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {portfolioData.accounts.map(acc => (
                        <div key={acc.id} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{acc.broker}</div>
                            <div className="text-2xl font-bold">{acc.currency === 'USD' ? `$${acc.cash.toLocaleString()}` : `NT$${acc.cash.toLocaleString()}`}</div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{acc.currency} {acc.market === 'TW' ? '台股' : '美股'}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 持股明細表格 */}
            <div className="card overflow-x-auto">
                <h2 className="text-2xl font-bold mb-4">持股明細</h2>
                <table className="w-full text-sm">
                    <thead className="bg-gray-50 dark:bg-gray-800"><tr><th className="px-4 py-3 text-left font-medium">代碼/名稱</th><th className="px-4 py-3 text-right font-medium">券商</th><th className="px-4 py-3 text-right font-medium">幣別</th><th className="px-4 py-3 text-right font-medium">股數</th><th className="px-4 py-3 text-right font-medium">成本均價</th><th className="px-4 py-3 text-right font-medium">現價</th><th className="px-4 py-3 text-right font-medium">市值</th><th className="px-4 py-3 text-right font-medium">損益</th><th className="px-4 py-3 text-right font-medium">報酬率</th></tr></thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">{portfolioData.holdings.map(h => {
                        const account = portfolioData.accounts.find(a => a.id === h.accountId)
                        return (
                            <tr key={h.code + h.accountId} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                                <td className="px-4 py-3"><div><div className="font-medium">{h.code}</div><div className="text-xs text-gray-500 dark:text-gray-400">{h.name}</div></div></td>
                                <td className="px-4 py-3 text-right text-xs">{account?.broker || '-'}</td>
                                <td className="px-4 py-3 text-right"><span className={`px-2 py-1 rounded text-xs font-medium ${h.currency === 'USD' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400' : 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'}`}>{h.currency}</span></td>
                                <td className="px-4 py-3 text-right">{h.shares.toLocaleString()}</td>
                                <td className="px-4 py-3 text-right">{h.currency === 'USD' ? `$${h.avgCost}` : `NT$${h.avgCost}`}</td>
                                <td className="px-4 py-3 text-right font-medium">{h.currency === 'USD' ? `$${h.currentPrice}` : `NT$${h.currentPrice}`}</td>
                                <td className="px-4 py-3 text-right">{h.currency === 'USD' ? `$${h.value.toLocaleString()}` : `NT$${h.value.toLocaleString()}`}</td>
                                <td className={`px-4 py-3 text-right font-medium ${h.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>{h.profit >= 0 ? '+' : ''}{h.currency === 'USD' ? `$${h.profit.toLocaleString()}` : `NT$${h.profit.toLocaleString()}`}</td>
                                <td className={`px-4 py-3 text-right font-medium ${h.profitPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>{h.profitPercent >= 0 ? '+' : ''}{h.profitPercent.toFixed(2)}%</td>
                            </tr>
                        )
                    })}</tbody>
                </table>
            </div>
        </div>
    )
}

function SummaryCard({ title, value, change, icon, isCurrency, showChange }) {
    const fmt = (v) => isCurrency ? `NT$${(v / 1000).toFixed(0)}K` : v.toLocaleString()
    return (
        <div className="card">
            <div className="flex items-center justify-between mb-2"><h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</h3>{icon}</div>
            <div className="text-2xl font-bold">{fmt(value)}</div>
            {showChange && change && <div className={`text-sm mt-1 ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>{change >= 0 ? '+' : ''}{change.toFixed(2)}%</div>}
        </div>
    )
}

function RiskRow({ label, value }) {
    return <div className="flex items-center justify-between py-2 border-b border-gray-200 dark:border-gray-700 last:border-0"><span className="text-gray-600 dark:text-gray-400">{label}</span><span className="font-bold text-lg">{value}</span></div>
}