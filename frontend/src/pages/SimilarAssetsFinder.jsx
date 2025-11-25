// 相似因子資產發現器 (Similar Assets Finder)
// 因子DNA比對、相似標的推薦
import { useState } from 'react'
import {
    RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    ResponsiveContainer, Tooltip, Legend
} from 'recharts'
import { Search, Target, TrendingUp } from 'lucide-react'

export default function SimilarAssetsFinder() {
    const [seedStock, setSeedStock] = useState('2330')
    const [loading, setLoading] = useState(false)
    const [similarStocks, setSimilarStocks] = useState([
        {
            stock_code: '2454',
            stock_name: '聯發科',
            similarity: 92.5,
            scores: {
                value: 72.1,
                quality: 86.2,
                momentum: 68.5,
                size: 88.3,
                volatility: 65.9,
                growth: 81.7
            }
        },
        {
            stock_code: '2317',
            stock_name: '鴻海',
            similarity: 87.3,
            scores: {
                value: 78.3,
                quality: 82.1,
                momentum: 62.8,
                size: 95.2,
                volatility: 71.3,
                growth: 69.4
            }
        },
        {
            stock_code: '2303',
            stock_name: '聯電',
            similarity: 85.1,
            scores: {
                value: 76.8,
                quality: 79.5,
                momentum: 71.2,
                size: 82.6,
                volatility: 68.7,
                growth: 74.9
            }
        }
    ])

    // 種子股票因子
    const seedFactors = {
        value: 75.2,
        quality: 88.5,
        momentum: 65.8,
        size: 92.1,
        volatility: 68.3,
        growth: 79.6
    }

    const findSimilarAssets = () => {
        setLoading(true)
        setTimeout(() => setLoading(false), 1500)
    }

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">相似因子資產發現器</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        因子 DNA 比對 | 相似標的推薦 | 投資組合擴充
                    </p>
                </div>
            </div>

            {/* 種子股票輸入 */}
            <div className="card">
                <h2 className="text-xl font-bold mb-4">種子股票設定</h2>
                <div className="flex items-center gap-4">
                    <div className="flex-1">
                        <label className="block text-sm font-medium mb-2">股票代碼</label>
                        <input
                            type="text"
                            value={seedStock}
                            onChange={(e) => setSeedStock(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                            placeholder="2330"
                        />
                    </div>
                    <div className="flex-1">
                        <label className="block text-sm font-medium mb-2">相似度閾值</label>
                        <select className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                            <option>70% 以上</option>
                            <option>80% 以上</option>
                            <option>90% 以上</option>
                        </select>
                    </div>
                    <div className="flex-1">
                        <label className="block text-sm font-medium mb-2">結果數量</label>
                        <select className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                            <option>Top 5</option>
                            <option>Top 10</option>
                            <option>Top 20</option>
                        </select>
                    </div>
                    <div className="self-end">
                        <button
                            onClick={findSimilarAssets}
                            disabled={loading}
                            className="btn btn-primary flex items-center gap-2"
                        >
                            <Search className="w-5 h-5" />
                            {loading ? '搜尋中...' : '尋找相似資產'}
                        </button>
                    </div>
                </div>
            </div>

            {/* 種子股票因子DNA */}
            <div className="card">
                <h2 className="text-2xl font-bold mb-4">種子股票因子 DNA：{seedStock} (台積電)</h2>
                <ResponsiveContainer width="100%" height={350}>
                    <RadarChart data={[
                        { factor: '價值', score: seedFactors.value, fullMark: 100 },
                        { factor: '品質', score: seedFactors.quality, fullMark: 100 },
                        { factor: '動能', score: seedFactors.momentum, fullMark: 100 },
                        { factor: '規模', score: seedFactors.size, fullMark: 100 },
                        { factor: '波動率', score: seedFactors.volatility, fullMark: 100 },
                        { factor: '成長', score: seedFactors.growth, fullMark: 100 },
                    ]}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="factor" />
                        <PolarRadiusAxis angle={90} domain={[0, 100]} />
                        <Radar
                            name="種子股票"
                            dataKey="score"
                            stroke="#3b82f6"
                            fill="#3b82f6"
                            fillOpacity={0.6}
                        />
                        <Tooltip />
                        <Legend />
                    </RadarChart>
                </ResponsiveContainer>
            </div>

            {/* 相似資產列表 */}
            <div className="space-y-4">
                <h2 className="text-2xl font-bold">發現 {similarStocks.length} 檔相似資產</h2>

                {similarStocks.map((stock, index) => (
                    <SimilarStockCard
                        key={stock.stock_code}
                        stock={stock}
                        seedFactors={seedFactors}
                        rank={index + 1}
                    />
                ))}
            </div>

            {/* 應用場景說明 */}
            <div className="card bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700">
                <h3 className="font-bold text-lg mb-3">應用場景</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                        <h4 className="font-medium mb-2">🎯 投資組合擴充</h4>
                        <p className="text-gray-600 dark:text-gray-400">
                            找到與核心持股相似的資產，擴大投資範圍同時保持策略一致性
                        </p>
                    </div>
                    <div>
                        <h4 className="font-medium mb-2">🔄 對沖與分散</h4>
                        <p className="text-gray-600 dark:text-gray-400">
                            尋找因子特徵互補的資產，建立平衡的投資組合
                        </p>
                    </div>
                    <div>
                        <h4 className="font-medium mb-2">💡 替代標的</h4>
                        <p className="text-gray-600 dark:text-gray-400">
                            當目標股票估值過高時，找到相似但更便宜的替代選擇
                        </p>
                    </div>
                    <div>
                        <h4 className="font-medium mb-2">📊 同類比較</h4>
                        <p className="text-gray-600 dark:text-gray-400">
                            與同行業相似公司比較，找出相對優勢與投資機會
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}

// 相似股票卡片
function SimilarStockCard({ stock, seedFactors, rank }) {
    // 準備雷達圖資料
    const radarData = [
        { factor: '價值', seed: seedFactors.value, similar: stock.scores.value },
        { factor: '品質', seed: seedFactors.quality, similar: stock.scores.quality },
        { factor: '動能', seed: seedFactors.momentum, similar: stock.scores.momentum },
        { factor: '規模', seed: seedFactors.size, similar: stock.scores.size },
        { factor: '波動率', seed: seedFactors.volatility, similar: stock.scores.volatility },
        { factor: '成長', seed: seedFactors.growth, similar: stock.scores.growth },
    ]

    return (
        <div className="card">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                    <div className="text-3xl font-bold text-gray-400">#{rank}</div>
                    <div>
                        <h3 className="text-xl font-bold">{stock.stock_code} - {stock.stock_name}</h3>
                        <div className="flex items-center gap-2 mt-1">
                            <Target className="w-4 h-4 text-blue-600" />
                            <span className="text-sm text-gray-600 dark:text-gray-400">
                                相似度：<span className="font-bold text-blue-600">{stock.similarity}%</span>
                            </span>
                        </div>
                    </div>
                </div>

                <button className="btn btn-secondary text-sm">
                    查看詳情
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 雷達圖比較 */}
                <ResponsiveContainer width="100%" height={250}>
                    <RadarChart data={radarData}>
                        <PolarGrid />
                        <PolarAngleAxis dataKey="factor" tick={{ fontSize: 11 }} />
                        <PolarRadiusAxis angle={90} domain={[0, 100]} />
                        <Radar
                            name="種子股票"
                            dataKey="seed"
                            stroke="#3b82f6"
                            fill="#3b82f6"
                            fillOpacity={0.3}
                        />
                        <Radar
                            name={stock.stock_name}
                            dataKey="similar"
                            stroke="#10b981"
                            fill="#10b981"
                            fillOpacity={0.3}
                        />
                        <Tooltip />
                        <Legend />
                    </RadarChart>
                </ResponsiveContainer>

                {/* 因子差異 */}
                <div className="space-y-2">
                    <h4 className="font-medium mb-3">因子差異分析</h4>
                    {radarData.map(item => (
                        <FactorDiff
                            key={item.factor}
                            factor={item.factor}
                            seed={item.seed}
                            similar={item.similar}
                        />
                    ))}
                </div>
            </div>
        </div>
    )
}

// 因子差異元件
function FactorDiff({ factor, seed, similar }) {
    const diff = similar - seed
    const diffAbs = Math.abs(diff)

    return (
        <div className="flex items-center gap-3">
            <div className="w-16 text-sm font-medium">{factor}</div>
            <div className="flex-1 flex items-center gap-2">
                <div className="w-12 text-right text-sm text-gray-600">{seed.toFixed(1)}</div>
                <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2 relative">
                    <div
                        className="absolute h-2 rounded-full bg-blue-500"
                        style={{ width: `${seed}%` }}
                    />
                    <div
                        className="absolute h-2 rounded-full bg-green-500 opacity-50"
                        style={{ width: `${similar}%` }}
                    />
                </div>
                <div className="w-12 text-sm text-gray-600">{similar.toFixed(1)}</div>
            </div>
            <div className={`w-16 text-right text-sm font-medium ${diff > 0 ? 'text-green-600' : diff < 0 ? 'text-red-600' : 'text-gray-600'
                }`}>
                {diff > 0 ? '+' : ''}{diff.toFixed(1)}
            </div>
        </div>
    )
}
