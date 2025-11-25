// Dashboard 頁面 - AI 投資分析儀主儀表板
import { useState } from 'react'
import { TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react'

export default function Dashboard() {
    const [marketData] = useState({
        taiex: { value: 17850, change: +125.5, changePercent: +0.71 },
        dow: { value: 38521, change: +189.3, changePercent: +0.49 },
        sp500: { value: 4912, change: +24.8, changePercent: +0.51 },
        nasdaq: { value: 15632, change: -45.2, changePercent: -0.29 },
        gold: { value: 2045.80, change: +15.30, changePercent: +0.75 },
        usdtwd: { value: 31.25, change: -0.15, changePercent: -0.48 },
        btc: { value: 95000, change: +2300, changePercent: +2.48 },
        vix: { value: 15.2, change: -0.5, changePercent: -3.18 }
    })

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                    AI 投資分析儀
                </h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                    Gemini Quant - 您的智慧投資決策夥伴
                </p>
            </div>

            {/* 市場關鍵指數 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <MarketCard
                    title="台股加權"
                    value={marketData.taiex.value}
                    change={marketData.taiex.change}
                    changePercent={marketData.taiex.changePercent}
                    icon={<TrendingUp className="w-6 h-6" />}
                />
                <MarketCard
                    title="道瓊工業"
                    value={marketData.dow.value}
                    change={marketData.dow.change}
                    changePercent={marketData.dow.changePercent}
                    icon={<Activity className="w-6 h-6" />}
                />
                <MarketCard
                    title="S&P 500"
                    value={marketData.sp500.value}
                    change={marketData.sp500.change}
                    changePercent={marketData.sp500.changePercent}
                    icon={<Activity className="w-6 h-6" />}
                />
                <MarketCard
                    title="NASDAQ"
                    value={marketData.nasdaq.value}
                    change={marketData.nasdaq.change}
                    changePercent={marketData.nasdaq.changePercent}
                    icon={<Activity className="w-6 h-6" />}
                />
                <MarketCard
                    title="黃金 (USD/oz)"
                    value={marketData.gold.value}
                    change={marketData.gold.change}
                    changePercent={marketData.gold.changePercent}
                    icon={<DollarSign className="w-6 h-6" />}
                    decimals={2}
                />
                <MarketCard
                    title="USD/TWD 匯率"
                    value={marketData.usdtwd.value}
                    change={marketData.usdtwd.change}
                    changePercent={marketData.usdtwd.changePercent}
                    icon={<DollarSign className="w-6 h-6" />}
                    decimals={2}
                />
                <MarketCard
                    title="BTC/USD"
                    value={marketData.btc.value}
                    change={marketData.btc.change}
                    changePercent={marketData.btc.changePercent}
                    icon={<DollarSign className="w-6 h-6" />}
                />
                <MarketCard
                    title="VIX 恐慌指數"
                    value={marketData.vix.value}
                    change={marketData.vix.change}
                    changePercent={marketData.vix.changePercent}
                    icon={<Activity className="w-6 h-6" />}
                    decimals={1}
                />
            </div>

            {/* AI 每日戰略觀點 */}
            <div className="card">
                <h2 className="text-2xl font-bold mb-4">AI 每日戰略觀點</h2>
                <div className="text-gray-500 dark:text-gray-400">
                    <p className="text-sm mb-4">展示模式運行中</p>
                    <p>連接後端API後，將顯示Gemini AI生成的每日投資策略分析與建議。</p>
                </div>
            </div>

            {/* 快速操作 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <ActionCard title="查看因子分析" description="深入了解六大因子表現" />
                <ActionCard title="大戶同步率" description="追蹤聰明錢流向（TDCC）" />
                <ActionCard title="技術分析" description="查看 K 線圖與技術指標" />
            </div>
        </div>
    )
}

// 市場數據卡片
function MarketCard({ title, value, change, changePercent, icon, decimals = 0 }) {
    const isPositive = change >= 0

    return (
        <div className="card">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</h3>
                {icon}
            </div>
            <div className="space-y-2">
                <div className="text-2xl font-bold">
                    {decimals > 0 ? value.toFixed(decimals) : value.toLocaleString()}
                </div>
                <div className={`flex items-center text-sm ${isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                    {isPositive ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
                    <span>{isPositive ? '+' : ''}{change.toFixed(2)}</span>
                    <span className="ml-2">({isPositive ? '+' : ''}{changePercent.toFixed(2)}%)</span>
                </div>
            </div>
        </div>
    )
}

// 快速操作卡片
function ActionCard({ title, description }) {
    return (
        <div className="card hover:shadow-lg transition-shadow duration-200 cursor-pointer">
            <h3 className="text-lg font-bold mb-2">{title}</h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">{description}</p>
        </div>
    )
}
