// 投資組合催化劑排名 (Portfolio Catalyst Ranker)
// Top 10 優化資產排名、推薦理由、戰術觸發點
import { useState } from 'react'
import { Trophy, TrendingUp, Target, Calendar, AlertCircle } from 'lucide-react'

export default function CatalystRanker() {
    const [timeHorizon, setTimeHorizon] = useState('short') // short, medium, long

    // Top 10 催化劑資產
    const catalysts = [
        {
            rank: 1,
            code: '2330',
            name: '台積電',
            catalystScore: 95,
            catalysts: [
                '3奈米製程量產加速',
                'AI晶片需求強勁',
                '美國補貼政策支持'
            ],
            expectedImpact: '+15-20%',
            triggerPrice: 600,
            currentPrice: 580,
            triggerCondition: '突破600元且成交量放大',
            timeline: '1-3個月',
            confidence: 85,
            riskFactors: ['地緣政治', '產能擴張成本']
        },
        {
            rank: 2,
            code: '2603',
            name: '長榮',
            catalystScore: 88,
            catalysts: [
                '運價觸底反彈',
                '新船交付增加運能',
                '紅海危機推升運費'
            ],
            expectedImpact: '+25-35%',
            triggerPrice: 150,
            currentPrice: 138,
            triggerCondition: '運價指數回升至2000點',
            timeline: '2-4個月',
            confidence: 75,
            riskFactors: ['全球貿易量', '油價波動']
        },
        {
            rank: 3,
            code: '2454',
            name: '聯發科',
            catalystScore: 85,
            catalysts: [
                '天璣9300獲小米採用',
                '車用晶片訂單成長',
                '毛利率改善'
            ],
            expectedImpact: '+18-25%',
            triggerPrice: 900,
            currentPrice: 880,
            triggerCondition: '法說會釋出正面展望',
            timeline: '1-2個月',
            confidence: 80,
            riskFactors: ['高通競爭', '智慧型手機需求']
        },
        {
            rank: 4,
            code: '2002',
            name: '中鋼',
            catalystScore: 82,
            catalysts: [
                '中國基建復甦',
                '鋼價築底反彈',
                '碳權交易利多'
            ],
            expectedImpact: '+12-18%',
            triggerPrice: 28,
            currentPrice: 26.5,
            triggerCondition: '鋼價回升至500美元/噸',
            timeline: '3-6個月',
            confidence: 70,
            riskFactors: ['原物料成本', '中國需求']
        },
        {
            rank: 5,
            code: '2408',
            name: '南亞科',
            catalystScore: 80,
            catalysts: [
                'DRAM價格回升',
                'AI伺服器需求增加',
                '產能利用率提升'
            ],
            expectedImpact: '+20-30%',
            triggerPrice: 75,
            currentPrice: 68,
            triggerCondition: 'DRAM合約價連續2季上漲',
            timeline: '2-4個月',
            confidence: 75,
            riskFactors: ['記憶體價格週期', '產能過剩']
        }
    ]

    const filteredCatalysts = catalysts.slice(0, timeHorizon === 'short' ? 5 : 10)

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <Trophy className="w-8 h-8 text-yellow-600" />
                        投資組合催化劑排名
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        AI 驅動的催化劑分析 | Top 10 優化資產 | 戰術觸發點
                    </p>
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={() => setTimeHorizon('short')}
                        className={`px-4 py-2 rounded-lg ${timeHorizon === 'short' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                    >
                        短期 (1-3月)
                    </button>
                    <button
                        onClick={() => setTimeHorizon('medium')}
                        className={`px-4 py-2 rounded-lg ${timeHorizon === 'medium' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                    >
                        中期 (3-6月)
                    </button>
                    <button
                        onClick={() => setTimeHorizon('long')}
                        className={`px-4 py-2 rounded-lg ${timeHorizon === 'long' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                    >
                        長期 (6月+)
                    </button>
                </div>
            </div>

            {/* 說明卡片 */}
            <div className="card bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20">
                <h3 className="font-bold text-lg mb-2">💡 什麼是催化劑？</h3>
                <p className="text-sm">
                    催化劑是指可能在短期內推動股價上漲的<strong>特定事件</strong>或<strong>基本面變化</strong>。
                    AI 分析了財報、產業趨勢、技術面等多個維度，為您找出最有潛力的投資標的及其觸發條件。
                </p>
            </div>

            {/* Top 催化劑列表 */}
            <div className="space-y-4">
                {filteredCatalysts.map((catalyst) => (
                    <CatalystCard key={catalyst.code} catalyst={catalyst} />
                ))}
            </div>

            {/* 使用建議 */}
            <div className="card">
                <h3 className="font-bold text-lg mb-3">📋 使用建議</h3>
                <div className="space-y-2 text-sm">
                    <p>✅ <strong>定期檢視</strong>：每週檢查催化劑進展，調整投資組合</p>
                    <p>✅ <strong>設定警報</strong>：對觸發條件設定價格警報，不錯過機會</p>
                    <p>✅ <strong>分散投資</strong>：不要只押注單一催化劑，建議配置 Top 3-5</p>
                    <p>⚠️ <strong>風險管理</strong>：催化劑可能不如預期，務必設定停損</p>
                    <p>💡 <strong>動態調整</strong>：催化劑實現後及時獲利了結，尋找下一個機會</p>
                </div>
            </div>
        </div>
    )
}

// 催化劑卡片
function CatalystCard({ catalyst }) {
    const confidenceColor = catalyst.confidence >= 80 ? 'text-green-600' :
        catalyst.confidence >= 70 ? 'text-blue-600' : 'text-orange-600'

    const distanceToTrigger = ((catalyst.triggerPrice - catalyst.currentPrice) / catalyst.currentPrice * 100).toFixed(1)

    return (
        <div className="card">
            <div className="flex items-start justify-between mb-4">
                {/* 排名徽章 */}
                <div className="flex items-start gap-4 flex-1">
                    <div className={`w-16 h-16 rounded-full flex items-center justify-center font-bold text-2xl ${catalyst.rank === 1 ? 'bg-yellow-400 text-yellow-900' :
                            catalyst.rank === 2 ? 'bg-gray-300 text-gray-700' :
                                catalyst.rank === 3 ? 'bg-orange-400 text-orange-900' :
                                    'bg-blue-100 dark:bg-blue-900/30 text-blue-600'
                        }`}>
                        #{catalyst.rank}
                    </div>

                    <div className="flex-1">
                        {/* 標題與分數 */}
                        <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-2xl font-bold">{catalyst.code} - {catalyst.name}</h3>
                            <span className="px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400">
                                催化劑分數 {catalyst.catalystScore}
                            </span>
                        </div>

                        {/* 催化劑列表 */}
                        <div className="mb-4">
                            <h4 className="text-sm font-bold text-gray-600 dark:text-gray-400 mb-2 flex items-center gap-2">
                                <TrendingUp className="w-4 h-4" />
                                關鍵催化劑
                            </h4>
                            <ul className="space-y-1">
                                {catalyst.catalysts.map((c, i) => (
                                    <li key={i} className="text-sm flex items-start gap-2">
                                        <span className="text-blue-600">•</span>
                                        <span>{c}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        {/* 關鍵數據網格 */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                            <DataBox label="預期影響" value={catalyst.expectedImpact} highlight />
                            <DataBox label="當前價格" value={`$${catalyst.currentPrice}`} />
                            <DataBox label="觸發價格" value={`$${catalyst.triggerPrice}`} />
                            <DataBox label="距觸發" value={`${distanceToTrigger > 0 ? '+' : ''}${distanceToTrigger}%`} />
                        </div>

                        {/* 觸發條件 */}
                        <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg mb-3">
                            <div className="flex items-start gap-2">
                                <Target className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                                <div>
                                    <div className="text-sm font-bold text-blue-900 dark:text-blue-300 mb-1">戰術觸發點</div>
                                    <div className="text-sm">{catalyst.triggerCondition}</div>
                                </div>
                            </div>
                        </div>

                        {/* 時間軸與信心度 */}
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4 text-sm">
                                <div className="flex items-center gap-2">
                                    <Calendar className="w-4 h-4 text-gray-600" />
                                    <span>預期時間：<strong>{catalyst.timeline}</strong></span>
                                </div>
                                <div className={`font-bold ${confidenceColor}`}>
                                    信心度：{catalyst.confidence}%
                                </div>
                            </div>
                        </div>

                        {/* 風險因素 */}
                        {catalyst.riskFactors.length > 0 && (
                            <div className="mt-3 p-2 bg-orange-50 dark:bg-orange-900/20 rounded">
                                <div className="flex items-start gap-2 text-sm">
                                    <AlertCircle className="w-4 h-4 text-orange-600 flex-shrink-0 mt-0.5" />
                                    <div>
                                        <span className="font-medium text-orange-900 dark:text-orange-300">風險因素：</span>
                                        <span className="ml-2">{catalyst.riskFactors.join('、')}</span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

// 數據盒
function DataBox({ label, value, highlight = false }) {
    return (
        <div className={`p-2 rounded ${highlight ? 'bg-green-50 dark:bg-green-900/20' : 'bg-gray-50 dark:bg-gray-800'}`}>
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{label}</div>
            <div className={`font-bold ${highlight ? 'text-green-600 text-lg' : ''}`}>{value}</div>
        </div>
    )
}
