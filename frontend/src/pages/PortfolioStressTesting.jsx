// 投資組合壓力測試 (Portfolio Stress Testing)
// 歷史情境模擬、最大回撤計算、虧損預估、蒙地卡羅模擬
import { useState, useEffect } from 'react'
import {
    LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    AreaChart, Area
} from 'recharts'
import { AlertTriangle, TrendingDown, Shield, Zap, Activity, History } from 'lucide-react'

export default function PortfolioStressTesting() {
    const [selectedScenario, setSelectedScenario] = useState('2008crisis')
    const [running, setRunning] = useState(false)
    const [mcResults, setMcResults] = useState(null)
    const [simulationPaths, setSimulationPaths] = useState([])
    const [holdings, setHoldings] = useState([])

    // 歷史情境資料 (靜態)
    const scenarios = [
        { id: '2008crisis', name: '2008 金融海嘯', impact: -42.5, duration: '18個月', description: '全球信貸緊縮，雷曼兄弟倒閉' },
        { id: '2020covid', name: '2020 COVID-19', impact: -35.8, duration: '3個月', description: '全球疫情爆發，流動性危機' },
        { id: '2022inflation', name: '2022 通膨恐慌', impact: -22.3, duration: '9個月', description: '高通膨與聯準會激進升息' },
        { id: 'dotcom', name: '2000 網路泡沫', impact: -48.2, duration: '30個月', description: '科技股過度估值修正' },
    ]

    // 預設範例持倉
    const defaultHoldings = [
        { code: '2330', market: 'TW', weight: 0.25 },
        { code: '2317', market: 'TW', weight: 0.15 },
        { code: '2454', market: 'TW', weight: 0.10 },
        { code: '0050', market: 'TW', weight: 0.50 }
    ]

    useEffect(() => {
        fetchPortfolio()
    }, [])

    const fetchPortfolio = async () => {
        try {
            const res = await fetch('http://localhost:5000/api/portfolio')
            const data = await res.json()
            if (data.success && data.data && data.data.length > 0) {
                const formatted = data.data.map(h => ({
                    code: h.stock_code,
                    market: h.market || 'TW',
                    weight: parseFloat(h.percentage) / 100 || 0
                }))
                setHoldings(formatted)
            } else {
                setHoldings(defaultHoldings)
            }
        } catch (e) {
            setHoldings(defaultHoldings)
        }
    }

    const runStressTest = async () => {
        setRunning(true)
        try {
            // 執行蒙地卡羅模擬
            const res = await fetch('http://localhost:5000/api/quant/monte-carlo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    holdings: holdings,
                    simulations: 1000,
                    days: 252,
                    initial_capital: 1000000 // 假設 100 萬本金
                })
            })
            const result = await res.json()

            if (result.success) {
                setMcResults(result.data)

                // 整理路徑數據供圖表顯示 (只顯示前 20 條)
                if (result.data.paths) {
                    // 轉換格式: [{day: 1, path1: 100, path2: 102...}, ...]
                    const paths = result.data.paths
                    const days = paths[0].data.length
                    const chartData = []

                    for (let i = 0; i < days; i += 5) { // 降採樣
                        const point = { day: i }
                        paths.forEach((p, idx) => {
                            point[`path${idx}`] = p.data[i]
                        })
                        chartData.push(point)
                    }
                    setSimulationPaths(chartData)
                }
            }
        } catch (e) {
            console.error("Stress test failed:", e)
        } finally {
            setRunning(false)
        }
    }

    const scenario = scenarios.find(s => s.id === selectedScenario)

    return (
        <div className="p-8 space-y-8 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">投資組合壓力測試</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        歷史情境模擬 | 蒙地卡羅預測 | 極端風險分析
                    </p>
                </div>

                <button
                    onClick={runStressTest}
                    disabled={running}
                    className="btn btn-primary flex items-center gap-2 shadow-lg shadow-red-500/30 bg-red-600 hover:bg-red-700 text-white"
                >
                    <Zap className={`w-5 h-5 ${running ? 'animate-pulse' : ''}`} />
                    {running ? '正在模擬中...' : '執行全方位壓力測試'}
                </button>
            </div>

            {/* 結果展示區 (有結果才顯示) */}
            {mcResults && (
                <div className="animate-fade-in space-y-8">
                    {/* 風險指標 */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="card border-t-4 border-red-500">
                            <div className="flex items-center gap-2 mb-3">
                                <Shield className="w-5 h-5 text-red-600" />
                                <h3 className="font-bold text-gray-900 dark:text-white">95% VaR (風險值)</h3>
                            </div>
                            <div className="text-3xl font-bold text-red-600 dark:text-red-400 mb-2">
                                ${mcResults.risk_metrics.var_95_amount.toLocaleString()}
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                有 95% 的機率，未來一年最大虧損不會超過此金額
                            </p>
                        </div>

                        <div className="card border-t-4 border-orange-500">
                            <div className="flex items-center gap-2 mb-3">
                                <AlertTriangle className="w-5 h-5 text-orange-600" />
                                <h3 className="font-bold text-gray-900 dark:text-white">95% CVaR (尾部風險)</h3>
                            </div>
                            <div className="text-3xl font-bold text-orange-600 dark:text-orange-400 mb-2">
                                ${mcResults.risk_metrics.cvar_95_amount.toLocaleString()}
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                若發生極端狀況 (最差 5%)，平均預期虧損金額
                            </p>
                        </div>

                        <div className="card border-t-4 border-blue-500">
                            <div className="flex items-center gap-2 mb-3">
                                <Activity className="w-5 h-5 text-blue-600" />
                                <h3 className="font-bold text-gray-900 dark:text-white">中位數預估價值</h3>
                            </div>
                            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                                ${Math.round(mcResults.percentiles.p50).toLocaleString()}
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                                蒙地卡羅模擬 1000 次後的中位數資產價值
                            </p>
                        </div>
                    </div>

                    {/* 蒙地卡羅模擬圖 */}
                    <div className="card">
                        <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">蒙地卡羅路徑模擬 (未來 252 天)</h2>
                        <div className="h-[400px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={simulationPaths}>
                                    <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                                    <XAxis dataKey="day" label={{ value: '天數', position: 'insideBottom', offset: -5 }} />
                                    <YAxis domain={['auto', 'auto']} />
                                    <Tooltip contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#F3F4F6' }} />
                                    {/* 繪製多條路徑 */}
                                    {mcResults.paths && mcResults.paths.map((path, idx) => (
                                        <Line
                                            key={idx}
                                            type="monotone"
                                            dataKey={`path${idx}`}
                                            stroke={idx === 0 ? '#ef4444' : '#3b82f6'}
                                            strokeOpacity={0.3}
                                            strokeWidth={1}
                                            dot={false}
                                        />
                                    ))}
                                    <ReferenceLine y={1000000} stroke="#10b981" strokeDasharray="3 3" label="初始本金" />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                        <p className="text-center text-sm text-gray-500 mt-2">顯示隨機抽樣的 20 條模擬路徑，紅色為其中一條範例</p>
                    </div>
                </div>
            )}

            {/* 歷史情境模擬 */}
            <div className="card">
                <div className="flex items-center gap-3 mb-6">
                    <History className="w-6 h-6 text-purple-600" />
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">歷史情境重演</h2>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    {scenarios.map(s => (
                        <button
                            key={s.id}
                            onClick={() => setSelectedScenario(s.id)}
                            className={`p-4 rounded-lg border-2 text-left transition-all ${selectedScenario === s.id
                                ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20 shadow-md'
                                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                                }`}
                        >
                            <div className="font-bold text-gray-900 dark:text-white mb-1">{s.name}</div>
                            <div className="text-sm text-red-600 dark:text-red-400 font-bold">{s.impact}% 衝擊</div>
                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">{s.duration}</div>
                        </button>
                    ))}
                </div>

                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
                    <h3 className="font-bold text-lg mb-2 text-gray-900 dark:text-white">{scenario?.name} 情境說明</h3>
                    <p className="text-gray-600 dark:text-gray-300 mb-4">{scenario?.description}</p>

                    <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                        <span className="px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-full font-medium">
                            假設持倉下跌 {Math.abs(scenario?.impact)}%
                        </span>
                        <span>若您的投資組合遭遇相同情況，預計市值將縮水至：</span>
                        <span className="font-bold text-gray-900 dark:text-white text-lg">
                            ${Math.round(1000000 * (1 + scenario?.impact / 100)).toLocaleString()}
                        </span>
                        <span>(以 100 萬本金計算)</span>
                    </div>
                </div>
            </div>

            {!mcResults && (
                <div className="flex flex-col items-center justify-center p-12 text-center text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800/30 rounded-lg border-2 border-dashed border-gray-200 dark:border-gray-700">
                    <Shield className="w-16 h-16 mb-4 text-gray-300 dark:text-gray-600" />
                    <p className="text-lg">點擊上方「執行全方位壓力測試」以開始蒙地卡羅模擬</p>
                    <p className="text-sm mt-2">系統將進行 1,000 次隨機路徑模擬，預測未來資產分佈與風險值</p>
                </div>
            )}
        </div>
    )
}
