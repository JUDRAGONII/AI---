// 動態情報儀表板 (Dynamic Intelligence Dashboard)
// 持股相關情報過濾、AI影響分析、模擬應對建議
import { useState, useEffect } from 'react'
import { Newspaper, TrendingUp, AlertCircle, Lightbulb, Filter } from 'lucide-react'

export default function DynamicIntelligence() {
    const [selectedStock, setSelectedStock] = useState('2330')
    const [filterCategory, setFilterCategory] = useState('all')

    // 模擬持股相關情報
    const intelligenceItems = [
        {
            id: 1,
            type: 'news',
            stock: '2330',
            stockName: '台積電',
            title: '台積電宣布3奈米製程量產進度超前',
            source: '經濟日報',
            time: '2小時前',
            sentiment: 'positive',
            aiImpact: 'high',
            impactScore: 8.5,
            analysis: '預期將提升市場信心，短期股價可能上漲3-5%',
            suggestedAction: '持續持有，若突破600元可考慮加碼'
        },
        {
            id: 2,
            type: 'earnings',
            stock: '2330',
            stockName: '台積電',
            title: '法人預估Q4營收將創新高',
            source: 'Bloomberg',
            time: '5小時前',
            sentiment: 'positive',
            aiImpact: 'medium',
            impactScore: 7.2,
            analysis: '受惠於AI晶片需求強勁，營收展望樂觀',
            suggestedAction: '維持持有，注意法說會訊息'
        },
        {
            id: 3,
            type: 'technical',
            stock: '2330',
            stockName: '台積電',
            title: '技術分析：突破20日均線壓力',
            source: '系統分析',
            time: '1小時前',
            sentiment: 'positive',
            aiImpact: 'medium',
            impactScore: 6.8,
            analysis: '技術面轉強，短期趨勢向上',
            suggestedAction: '短線交易者可考慮進場'
        },
        {
            id: 4,
            type: 'institutional',
            stock: '2330',
            stockName: '台積電',
            title: '外資連續5日買超',
            source: 'TDCC',
            time: '昨日',
            sentiment: 'positive',
            aiImpact: 'high',
            impactScore: 8.0,
            analysis: '籌碼面穩定，主力積極布局',
            suggestedAction: '跟隨主力，維持多頭思維'
        },
        {
            id: 5,
            type: 'risk',
            stock: '2330',
            stockName: '台積電',
            title: '地緣政治風險升溫',
            source: 'Reuters',
            time: '3小時前',
            sentiment: 'negative',
            aiImpact: 'medium',
            impactScore: -5.5,
            analysis: '短期可能面臨波動，但長期基本面不變',
            suggestedAction: '設定停損點於550元，長期投資者無需過度擔憂'
        }
    ]

    const filteredItems = filterCategory === 'all'
        ? intelligenceItems.filter(item => item.stock === selectedStock)
        : intelligenceItems.filter(item => item.stock === selectedStock && item.type === filterCategory)

    // 整體影響評分
    const overallImpact = filteredItems.reduce((sum, item) => sum + item.impactScore, 0) / filteredItems.length

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">動態情報儀表板</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        持股相關情報即時追蹤 | AI 影響分析 | 智慧應對建議
                    </p>
                </div>

                <div className="flex items-center gap-4">
                    <select
                        value={selectedStock}
                        onChange={(e) => setSelectedStock(e.target.value)}
                        className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                    >
                        <option value="2330">2330 台積電</option>
                        <option value="2317">2317 鴻海</option>
                        <option value="2454">2454 聯發科</option>
                    </select>
                </div>
            </div>

            {/* 整體影響評估 */}
            <div className="card bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="text-lg font-bold mb-2">整體影響評估</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            基於 {filteredItems.length} 則情報的 AI 綜合分析
                        </p>
                    </div>
                    <div className="text-center">
                        <div className={`text-4xl font-bold ${overallImpact > 5 ? 'text-green-600' :
                                overallImpact > 0 ? 'text-blue-600' :
                                    'text-red-600'
                            }`}>
                            {overallImpact >= 0 ? '+' : ''}{overallImpact.toFixed(1)}
                        </div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">影響分數</div>
                    </div>
                </div>

                {overallImpact > 5 && (
                    <div className="mt-4 p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
                        <p className="text-sm font-medium text-green-800 dark:text-green-400">
                            ✅ 整體情報偏正面，建議維持或增加持股
                        </p>
                    </div>
                )}
                {overallImpact <= 0 && (
                    <div className="mt-4 p-3 bg-red-100 dark:bg-red-900/30 rounded-lg">
                        <p className="text-sm font-medium text-red-800 dark:text-red-400">
                            ⚠️ 負面情報較多，建議謹慎評估風險
                        </p>
                    </div>
                )}
            </div>

            {/* 篩選器 */}
            <div className="flex gap-2">
                <button
                    onClick={() => setFilterCategory('all')}
                    className={`px-4 py-2 rounded-lg ${filterCategory === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                >
                    全部
                </button>
                <button
                    onClick={() => setFilterCategory('news')}
                    className={`px-4 py-2 rounded-lg ${filterCategory === 'news' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                >
                    新聞
                </button>
                <button
                    onClick={() => setFilterCategory('earnings')}
                    className={`px-4 py-2 rounded-lg ${filterCategory === 'earnings' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                >
                    財報
                </button>
                <button
                    onClick={() => setFilterCategory('technical')}
                    className={`px-4 py-2 rounded-lg ${filterCategory === 'technical' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                >
                    技術面
                </button>
                <button
                    onClick={() => setFilterCategory('institutional')}
                    className={`px-4 py-2 rounded-lg ${filterCategory === 'institutional' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                >
                    法人
                </button>
            </div>

            {/* 情報列表 */}
            <div className="space-y-4">
                {filteredItems.map(item => (
                    <IntelligenceCard key={item.id} item={item} />
                ))}
            </div>
        </div>
    )
}

// 情報卡片
function IntelligenceCard({ item }) {
    const typeConfig = {
        news: { icon: <Newspaper className="w-5 h-5" />, label: '新聞', color: 'blue' },
        earnings: { icon: <TrendingUp className="w-5 h-5" />, label: '財報', color: 'green' },
        technical: { icon: <TrendingUp className="w-5 h-5" />, label: '技術', color: 'purple' },
        institutional: { icon: <TrendingUp className="w-5 h-5" />, label: '法人', color: 'orange' },
        risk: { icon: <AlertCircle className="w-5 h-5" />, label: '風險', color: 'red' }
    }

    const sentimentConfig = {
        positive: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-400', label: '正面' },
        negative: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-400', label: '負面' },
        neutral: { bg: 'bg-gray-100 dark:bg-gray-700', text: 'text-gray-600 dark:text-gray-400', label: '中性' }
    }

    const type = typeConfig[item.type]
    const sentiment = sentimentConfig[item.sentiment]
    const impactLevel = Math.abs(item.impactScore) > 7 ? 'high' : Math.abs(item.impactScore) > 4 ? 'medium' : 'low'

    return (
        <div className="card">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-start gap-3 flex-1">
                    <div className={`p-2 rounded-lg bg-${type.color}-50 dark:bg-${type.color}-900/30`}>
                        {type.icon}
                    </div>
                    <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                            <h3 className="text-lg font-bold">{item.title}</h3>
                            <span className={`px-2 py-1 rounded text-xs font-medium ${sentiment.bg} ${sentiment.text}`}>
                                {sentiment.label}
                            </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                            <span>{item.source}</span>
                            <span>•</span>
                            <span>{item.time}</span>
                            <span>•</span>
                            <span className={`px-2 py-0.5 rounded text-xs ${type.color === 'blue' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400' :
                                    type.color === 'green' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' :
                                        type.color === 'purple' ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400' :
                                            type.color === 'orange' ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400' :
                                                'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                                }`}>
                                {type.label}
                            </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                <div className="flex items-center gap-2 mb-2">
                                    <AlertCircle className="w-4 h-4 text-blue-600" />
                                    <span className="text-sm font-medium">AI 影響分析</span>
                                </div>
                                <p className="text-sm text-gray-700 dark:text-gray-300">{item.analysis}</p>
                                <div className="mt-2">
                                    <span className={`text-xs font-medium ${item.impactScore > 0 ? 'text-green-600' : 'text-red-600'
                                        }`}>
                                        影響分數: {item.impactScore >= 0 ? '+' : ''}{item.impactScore.toFixed(1)}
                                    </span>
                                </div>
                            </div>

                            <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                <div className="flex items-center gap-2 mb-2">
                                    <Lightbulb className="w-4 h-4 text-green-600" />
                                    <span className="text-sm font-medium">建議應對策略</span>
                                </div>
                                <p className="text-sm text-gray-700 dark:text-gray-300">{item.suggestedAction}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
