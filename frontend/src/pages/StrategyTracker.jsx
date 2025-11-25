// 策略績效追蹤 (Strategy Performance Tracker)
// 影子投資組合建立、Tracking Error 計算、績效對比分析
import { useState } from 'react'
import {
    LineChart, Line, BarChart, Bar,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { Target, TrendingUp, AlertCircle, Eye } from 'lucide-react'

export default function StrategyTracker() {
    const [selectedStrategy, setSelectedStrategy] = useState('value')

    // 影子投資組合（不同策略）
    const shadowPortfolios = {
        value: {
            name: '價值策略組合',
            description: '低P/E、高股息標的',
            holdings: ['2882', '2603', '2308', '1216', '2002']
        },
        growth: {
            name: '成長策略組合',
            description: '高營收成長、高EPS成長',
            holdings: ['2330', '2454', '3008', '6669', '2345']
        },
        momentum: {
            name: '動能策略組合',
            description: '技術面強勢、高RSI標的',
            holdings: ['2454', '2408', '3231', '6187', '2345']
        }
    }

    // 績效歷史資料
    const performanceHistory = Array.from({ length: 12 }, (_, i) => ({
        month: `${i + 1}月`,
        actualPortfolio: 100 + i * 2.5 + Math.random() * 3,
        shadowPortfolio: 100 + i * 2.8 + Math.random() * 2.5,
        benchmark: 100 + i * 2.0
    }))

    // Tracking Error 歷史
    const trackingErrorHistory = Array.from({ length: 12 }, (_, i) => ({
        month: `${i + 1}月`,
        trackingError: 0.5 + Math.random() * 1.5
    }))

    // 績效指標比較
    const performanceMetrics = {
        actualPortfolio: {
            totalReturn: 28.5,
            annualizedReturn: 10.2,
            volatility: 14.5,
            sharpe: 1.15,
            maxDrawdown: -12.3,
            winRate: 62
        },
        shadowPortfolio: {
            totalReturn: 32.0,
            annualizedReturn: 11.5,
            volatility: 15.2,
            sharpe: 1.25,
            maxDrawdown: -14.5,
            winRate: 65
        },
        benchmark: {
            totalReturn: 22.0,
            annualizedReturn: 8.5,
            volatility: 12.0,
            sharpe: 1.05,
            maxDrawdown: -10.2,
            winRate: 58
        }
    }

    // Tracking Error 分析
    const trackingAnalysis = {
        avgTrackingError: 1.2,
        maxTrackingError: 2.5,
        minTrackingError: 0.3,
        trend: 'increasing'
    }

    const currentShadow = shadowPortfolios[selectedStrategy]

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <Eye className="w-8 h-8 text-blue-600" />
                        策略績效追蹤
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        影子投資組合對比 | Tracking Error 分析 | 策略有效性驗證
                    </p>
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={() => setSelectedStrategy('value')}
                        className={`px-4 py-2 rounded-lg ${selectedStrategy === 'value' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                    >
                        價值策略
                    </button>
                    <button
                        onClick={() => setSelectedStrategy('growth')}
                        className={`px-4 py-2 rounded-lg ${selectedStrategy === 'growth' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                    >
                        成長策略
                    </button>
                    <button
                        onClick={() => setSelectedStrategy('momentum')}
                        className={`px-4 py-2 rounded-lg ${selectedStrategy === 'momentum' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                    >
                        動能策略
                    </button>
                </div>
            </div>

            {/* 影子組合說明 */}
            <div className="card bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
                <h3 className="font-bold text-lg mb-2 flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    {currentShadow.name}
                </h3>
                <p className="text-sm mb-3">{currentShadow.description}</p>
                <div className="flex flex-wrap gap-2">
                    {currentShadow.holdings.map(code => (
                        <span key={code} className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-full text-sm font-medium">
                            {code}
                        </span>
                    ))}
                </div>
            </div>

            {/* 績效對比圖 */}
            <div className="card">
                <h3 className="text-xl font-bold mb-4">累積報酬率對比</h3>
                <ResponsiveContainer width="100%" height={350}>
                    <LineChart data={performanceHistory}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="actualPortfolio" stroke="#3b82f6" strokeWidth={2} name="實際組合" />
                        <Line type="monotone" dataKey="shadowPortfolio" stroke="#10b981" strokeWidth={2} name="影子組合" strokeDasharray="5 5" />
                        <Line type="monotone" dataKey="benchmark" stroke="#94a3b8" strokeWidth={2} name="基準指數" />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* 績效指標比較 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <MetricsCard title="實際投資組合" metrics={performanceMetrics.actualPortfolio} color="blue" />
                <MetricsCard title="影子組合" metrics={performanceMetrics.shadowPortfolio} color="green" highlight />
                <MetricsCard title="基準指數" metrics={performanceMetrics.benchmark} color="gray" />
            </div>

            {/* Tracking Error 分析 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Tracking Error 趨勢 */}
                <div className="card">
                    <h3 className="text-xl font-bold mb-4">Tracking Error 趨勢</h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={trackingErrorHistory}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="month" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="trackingError" fill="#f59e0b" name="Tracking Error (%)" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>

                {/* Tracking Error 統計 */}
                <div className="card">
                    <h3 className="text-xl font-bold mb-4">Tracking Error 分析</h3>
                    <div className="space-y-4">
                        <StatBox label="平均 Tracking Error" value={`${trackingAnalysis.avgTrackingError}%`} />
                        <StatBox label="最大 Tracking Error" value={`${trackingAnalysis.maxTrackingError}%`} warning />
                        <StatBox label="最小 Tracking Error" value={`${trackingAnalysis.minTrackingError}%`} />
                        <StatBox
                            label="趨勢"
                            value={trackingAnalysis.trend === 'increasing' ? '上升' : '下降'}
                            warning={trackingAnalysis.trend === 'increasing'}
                        />
                    </div>

                    <div className="mt-4 p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                        <div className="flex items-start gap-2">
                            <AlertCircle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                            <p className="text-sm">
                                <strong>提醒</strong>：Tracking Error 呈上升趨勢，表示實際組合與影子組合偏離增加，
                                建議檢視是否需要調整持股以貼近策略目標。
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* 洞察與建議 */}
            <div className="card">
                <h3 className="text-xl font-bold mb-4">AI 洞察與建議</h3>
                <div className="space-y-3">
                    <InsightItem
                        type="positive"
                        title="策略有效性良好"
                        description="影子組合的夏普比率(1.25)優於實際組合(1.15)，證明策略方向正確"
                    />
                    <InsightItem
                        type="neutral"
                        title="Tracking Error 可接受"
                        description="平均 Tracking Error 1.2% 在合理範圍內，顯示策略執行基本符合目標"
                    />
                    <InsightItem
                        type="warning"
                        title="考慮部分調整"
                        description="影子組合領先3.5%，建議考慮增加成長股配置以縮小差距"
                    />
                </div>
            </div>
        </div>
    )
}

// 績效指標卡片
function MetricsCard({ title, metrics, color, highlight = false }) {
    const colorClasses = {
        blue: 'border-blue-200 dark:border-blue-700',
        green: 'border-green-200 dark:border-green-700',
        gray: 'border-gray-200 dark:border-gray-600'
    }

    return (
        <div className={`card border-2 ${colorClasses[color]} ${highlight ? 'ring-2 ring-green-400' : ''}`}>
            {highlight && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <span className="px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-full">最佳表現</span>
                </div>
            )}
            <h4 className="font-bold text-lg mb-4 text-center">{title}</h4>
            <div className="space-y-3">
                <MetricRow label="總報酬" value={`+${metrics.totalReturn}%`} highlight />
                <MetricRow label="年化報酬" value={`${metrics.annualizedReturn}%`} />
                <MetricRow label="波動率" value={`${metrics.volatility}%`} />
                <MetricRow label="夏普比率" value={metrics.sharpe.toFixed(2)} />
                <MetricRow label="最大回撤" value={`${metrics.maxDrawdown}%`} />
                <MetricRow label="勝率" value={`${metrics.winRate}%`} />
            </div>
        </div>
    )
}

// 指標行
function MetricRow({ label, value, highlight = false }) {
    return (
        <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
            <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
            <span className={`font-medium ${highlight ? 'text-green-600 text-lg' : ''}`}>{value}</span>
        </div>
    )
}

// 統計盒
function StatBox({ label, value, warning = false }) {
    return (
        <div className={`p-3 rounded ${warning ? 'bg-orange-50 dark:bg-orange-900/20' : 'bg-gray-50 dark:bg-gray-800'}`}>
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{label}</div>
            <div className={`text-2xl font-bold ${warning ? 'text-orange-600' : ''}`}>{value}</div>
        </div>
    )
}

// 洞察項目
function InsightItem({ type, title, description }) {
    const config = {
        positive: { icon: '✅', bg: 'bg-green-50 dark:bg-green-900/20', border: 'border-green-200 dark:border-green-700' },
        neutral: { icon: 'ℹ️', bg: 'bg-blue-50 dark:bg-blue-900/20', border: 'border-blue-200 dark:border-blue-700' },
        warning: { icon: '⚠️', bg: 'bg-orange-50 dark:bg-orange-900/20', border: 'border-orange-200 dark:border-orange-700' }
    }

    const style = config[type]

    return (
        <div className={`p-3 rounded-lg border ${style.bg} ${style.border}`}>
            <div className="flex items-start gap-2">
                <span className="text-xl">{style.icon}</span>
                <div>
                    <div className="font-bold mb-1">{title}</div>
                    <div className="text-sm">{description}</div>
                </div>
            </div>
        </div>
    )
}
