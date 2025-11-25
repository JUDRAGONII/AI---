// 技術分析中心 (Technical Analysis Center)
// 展示 K 線圖、技術指標、多圖比較
import { useState, useEffect } from 'react'
import {
    LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    ComposedChart
} from 'recharts'
import { TrendingUp, TrendingDown, BarChart3, Activity } from 'lucide-react'
import { db } from '../supabase'

export default function TechnicalAnalysis() {
    const [stockCode, setStockCode] = useState('2330')
    const [market, setMarket] = useState('tw')
    const [loading, setLoading] = useState(false)
    const [priceData] = useState([]) // 使用模擬數據
    const [selectedIndicators, setSelectedIndicators] = useState(['MA20', 'MA60'])

    // 切換指標選擇
    const toggleIndicator = (indicator) => {
        setSelectedIndicators(prev =>
            prev.includes(indicator)
                ? prev.filter(i => i !== indicator)
                : [...prev, indicator]
        )
    }

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">技術分析中心</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        K 線圖、技術指標、趨勢分析
                    </p>
                </div>

                {/* 控制面板 */}
                <div className="flex items-center gap-3">
                    <select
                        value={market}
                        onChange={(e) => setMarket(e.target.value)}
                        className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-sm"
                    >
                        <option value="tw">台股</option>
                        <option value="us">美股</option>
                    </select>

                    <input
                        type="text"
                        value={stockCode}
                        onChange={(e) => setStockCode(e.target.value)}
                        className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                        placeholder="股票代碼"
                    />

                    <button className="btn btn-primary">
                        查詢
                    </button>
                </div>
            </div>

            {/* 提示訊息 */}
            <div className="card bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700">
                <div className="flex items-start gap-3">
                    <Activity className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div>
                        <p className="font-medium text-blue-900 dark:text-blue-100 mb-1">技術分析功能</p>
                        <p className="text-sm text-blue-800 dark:text-blue-200">
                            目前使用展示模式。連接後端API後，可查看實際股票的完整技術分析、K線圖、技術指標等功能。
                        </p>
                    </div>
                </div>
            </div>

            {/* 指標選擇器 */}
            <div className="card">
                <h3 className="font-bold mb-3">技術指標</h3>
                <div className="flex flex-wrap gap-2">
                    {['MA5', 'MA20', 'MA60'].map(indicator => (
                        <button
                            key={indicator}
                            onClick={() => toggleIndicator(indicator)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${selectedIndicators.includes(indicator)
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                                }`}
                        >
                            {indicator}
                        </button>
                    ))}
                </div>
            </div>

            {/* 技術分析說明 */}
            <div className="card bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-purple-200 dark:border-purple-800">
                <h3 className="font-bold text-lg mb-3">技術分析指引</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                        <h4 className="font-medium mb-2">均線系統 (MA)</h4>
                        <ul className="space-y-1 text-gray-600 dark:text-gray-400">
                            <li>• MA5 &gt; MA20 &gt; MA60：多頭排列，趨勢向上</li>
                            <li>• MA5 &lt; MA20 &lt; MA60：空頭排列，趨勢向下</li>
                            <li>• 價格突破均線：可能是轉折訊號</li>
                        </ul>
                    </div>
                    <div>
                        <h4 className="font-medium mb-2">成交量分析</h4>
                        <ul className="space-y-1 text-gray-600 dark:text-gray-400">
                            <li>• 量增價漲：多頭強勢</li>
                            <li>• 量縮價漲：可能是假突破</li>
                            <li>• 量增價跌：空頭強勢</li>
                        </ul>
                    </div>
                </div>
            </div>

            {/* 功能說明卡片 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <FeatureCard
                    title="價格走勢圖"
                    description="K線圖與移動平均線，完整呈現價格趨勢"
                    icon={<TrendingUp className="w-8 h-8" />}
                />
                <FeatureCard
                    title="技術指標"
                    description="MA、MACD、RSI、KD等20+種專業指標"
                    icon={<Activity className="w-8 h-8" />}
                />
                <FeatureCard
                    title="成交量分析"
                    description="量價配合分析，掌握市場動能"
                    icon={<BarChart3 className="w-8 h-8" />}
                />
            </div>
        </div>
    )
}

// 功能卡片
function FeatureCard({ title, description, icon }) {
    return (
        <div className="card text-center">
            <div className="flex justify-center mb-3 text-blue-600">
                {icon}
            </div>
            <h4 className="font-bold mb-2">{title}</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
        </div>
    )
}
