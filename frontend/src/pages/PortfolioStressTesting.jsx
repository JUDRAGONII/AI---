// 投資組合壓力測試 (Portfolio Stress Testing)
// 歷史情境模擬、最大回撤計算、虧損預估
import { useState } from 'react'
import {
    LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { AlertTriangle, TrendingDown, Shield, Zap } from 'lucide-react'

export default function PortfolioStressTesting() {
    const [selectedScenario, setSelectedScenario] = useState('2008crisis')
    const [running, setRunning] = useState(false)

    // 歷史情境
    const scenarios = [
        { id: '2008crisis', name: '2008 金融海嘯', impact: -42.5, duration: '18個月' },
        { id: '2020covid', name: '2020 COVID-19', impact: -35.8, duration: '3個月' },
        { id: '2022inflation', name: '2022 通膨恐慌', impact: -22.3, duration: '9個月' },
        { id: 'dotcom', name: '2000 網路泡沫', impact: -48.2, duration: '30個月' },
    ]

    // 模擬當前投資組合在情境下的表現
    const stressTestResults = {
        currentValue: 5850000,
        scenarioValue: 3575000,
        loss: -2275000,
        lossPercent: -38.9,
        maxDrawdown: -42.5,
        recoveryTime: '14個月',
        varAt95: -18.5, // 95% VaR
        cvarAt95: -25.3 // 95% CVaR
    }

    // 回撤曲線
    const drawdownCurve = Array.from({ length: 18 }, (_, i) => ({
        month: `M${i + 1}`,
        portfolio: 100 - (i < 6 ? i * 7 : i < 12 ? 42 - (i - 6) * 1.5 : 33 + (i - 12) * 3),
        benchmark: 100 - (i < 6 ? i * 8 : i < 12 ? 48 - (i - 6) * 2 : 36 + (i - 12) * 4)
    }))

    // 損失分布
    const lossDistribution = Array.from({ length: 20 }, (_, i) => ({
        range: `${-50 + i * 5}~${-45 + i * 5}%`,
        frequency: Math.exp(-Math.pow((i - 10), 2) / 8) * 100
    }))

    const runStressTest = () => {
        setRunning(true)
        setTimeout(() => setRunning(false), 2000)
    }

    const scenario = scenarios.find(s => s.id === selectedScenario)

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">投資組合壓力測試</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        歷史情境模擬 | 最大回撤分析 | 風險量化
                    </p>
                </div>

                <button
                    onClick={runStressTest}
                    disabled={running}
                    className="btn btn-primary flex items-center gap-2"
                >
                    <Zap className="w-5 h-5" />
                    {running ? '測試中...' : '執行壓力測試'}
                </button>
            </div>

            {/* 情境選擇 */}
            <div className="card">
                <h2 className="text-xl font-bold mb-4">選擇歷史情境</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {scenarios.map(s => (
                        <button
                            key={s.id}
                            onClick={() => setSelectedScenario(s.id)}
                            className={`p-4 rounded-lg border-2 transition-all ${selectedScenario === s.id
                                    ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                                }`}
                        >
                            <div className="font-bold mb-1">{s.name}</div>
                            <div className="text-sm text-red-600 dark:text-red-400 font-medium">{s.impact}%</div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{s.duration}</div>
                        </button>
                    ))}
                </div>
            </div>

            {/* 壓力測試結果 */}
            <div className="card bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 border-red-200 dark:border-red-800">
                <div className="flex items-start gap-3 mb-6">
                    <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-1" />
                    <div>
                        <h3 className="font-bold text-lg mb-2">
                            {scenario?.name} 情境測試結果
                        </h3>
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                            假設您的投資組合經歷與 {scenario?.name} 相同的市場環境
                        </p>
                    </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                    <ResultMetric
                        label="當前市值"
                        value={`$${stressTestResults.currentValue.toLocaleString()}`}
                    />
                    <ResultMetric
                        label="情境後市值"
                        value={`$${stressTestResults.scenarioValue.toLocaleString()}`}
                        negative
                    />
                    <ResultMetric
                        label="預估虧損"
                        value={`${stressTestResults.lossPercent.toFixed(1)}%`}
                        negative
                    />
                    <ResultMetric
                        label="恢復時間"
                        value={stressTestResults.recoveryTime}
                    />
                </div>
            </div>

            {/* 風險指標 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="card">
                    <div className="flex items-center gap-2 mb-3">
                        <TrendingDown className="w-5 h-5 text-red-600" />
                        <h3 className="font-bold">最大回撤</h3>
                    </div>
                    <div className="text-3xl font-bold text-red-600 dark:text-red-400 mb-2">
                        {stressTestResults.maxDrawdown}%
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                        歷史最大單日跌幅
                    </p>
                </div>

                <div className="card">
                    <div className="flex items-center gap-2 mb-3">
                        <Shield className="w-5 h-5 text-orange-600" />
                        <h3 className="font-bold">VaR (95%)</h3>
                    </div>
                    <div className="text-3xl font-bold text-orange-600 dark:text-orange-400 mb-2">
                        {stressTestResults.varAt95}%
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                        95%信心水準下的風險值
                    </p>
                </div>

                <div className="card">
                    <div className="flex items-center gap-2 mb-3">
                        <AlertTriangle className="w-5 h-5 text-red-600" />
                        <h3 className="font-bold">CVaR (95%)</h3>
                    </div>
                    <div className="text-3xl font-bold text-red-600 dark:text-red-400 mb-2">
                        {stressTestResults.cvarAt95}%
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                        條件風險值（尾部風險）
                    </p>
                </div>
            </div>

            {/* 回撤曲線 */}
            <div className="card">
                <h2 className="text-2xl font-bold mb-4">情境回撤曲線</h2>
                <ResponsiveContainer width="100%" height={350}>
                    <LineChart data={drawdownCurve}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis domain={[0, 100]} unit="%" />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="portfolio" stroke="#3b82f6" strokeWidth={2} name="您的投資組合" />
                        <Line type="monotone" dataKey="benchmark" stroke="#94a3b8" strokeWidth={2} name="大盤" strokeDasharray="5 5" />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* 損失分布 */}
            <div className="card">
                <h2 className="text-2xl font-bold mb-4">蒙地卡羅損失分布</h2>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={lossDistribution}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="range" tick={{ fontSize: 10 }} />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="frequency" fill="#ef4444" />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            {/* 對沖建議 */}
            <div className="card bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700">
                <h3 className="font-bold text-lg mb-3">風險對沖建議</h3>
                <div className="space-y-2 text-sm">
                    <p>✅ 考慮增加防禦型資產（公用事業、必需消費品）至 15-20%</p>
                    <p>✅ 納入債券型 ETF 以降低整體波動（建議 10-15%）</p>
                    <p>✅ 設定停損點：單一持股跌幅超過 15% 時考慮減碼</p>
                    <p>✅ 分散投資至不同產業，降低系統性風險</p>
                    <p>✅ 保留 10-15% 現金部位以應對突發狀況</p>
                </div>
            </div>
        </div>
    )
}

// 結果指標元件
function ResultMetric({ label, value, negative = false }) {
    return (
        <div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">{label}</div>
            <div className={`text-2xl font-bold ${negative ? 'text-red-600 dark:text-red-400' : ''}`}>
                {value}
            </div>
        </div>
    )
}
