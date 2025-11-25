// 新聞管理中心 (News Management)
// RSS 訂閱、新聞過濾、AI 摘要
import { useState } from 'react'
import { Newspaper, Rss, Search, Filter, Sparkles } from 'lucide-react'

export default function NewsManagement() {
    const [selectedCategory, setSelectedCategory] = useState('all')
    const [searchQuery, setSearchQuery] = useState('')

    // 模擬新聞資料
    const newsData = [
        {
            id: 1,
            title: '台積電宣布3奈米新製程量產',
            source: 'MoneyDJ',
            category: 'tech',
            date: '2024-11-23',
            summary: 'AI 摘要：台積電今日宣布3奈米製程正式量產，預計將為Apple、NVIDIA等客戶提供更先進的晶片製造服務...',
            url: 'https://example.com/news/1'
        },
        {
            id: 2,
            title: '聯準會暗示明年可能降息',
            source: 'Reuters',
            category: 'macro',
            date: '2024-11-22',
            summary: 'AI 摘要：聯準會官員表示，若通膨持續緩和，2025年可能考慮調降利率，市場反應積極...',
            url: 'https://example.com/news/2'
        },
        {
            id: 3,
            title: '特斯拉電動車銷量創新高',
            source: 'Bloomberg',
            category: 'company',
            date: '2024-11-22',
            summary: 'AI 摘要：Tesla Q3交付量超過預期，全球電動車需求強勁，股價盤後上漲5%...',
            url: 'https://example.com/news/3'
        },
        {
            id: 4,
            title: '加密貨幣市場波動加劇',
            source: 'CoinDesk',
            category: 'crypto',
            date: '2024-11-21',
            summary: 'AI 摘要：比特幣價格突破$95000，市場情緒樂觀，但分析師警告波動風險...',
            url: 'https://example.com/news/4'
        },
    ]

    const categories = [
        { id: 'all', name: '全部', count: newsData.length },
        { id: 'tech', name: '科技', count: 1 },
        { id: 'macro', name: '宏觀', count: 1 },
        { id: 'company', name: '個股', count: 1 },
        { id: 'crypto', name: '加密貨幣', count: 1 },
    ]

    const filteredNews = newsData.filter(news =>
        (selectedCategory === 'all' || news.category === selectedCategory) &&
        (searchQuery === '' || news.title.toLowerCase().includes(searchQuery.toLowerCase()))
    )

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">新聞管理中心</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        RSS 訂閱、智慧過濾、AI 自動摘要
                    </p>
                </div>

                <button className="btn btn-primary flex items-center gap-2">
                    <Rss className="w-5 h-5" />
                    新增 RSS 源
                </button>
            </div>

            {/* 搜尋與過濾 */}
            <div className="card">
                <div className="flex items-center gap-4">
                    <div className="flex-1 relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="搜尋新聞標題..."
                            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                        />
                    </div>
                    <button className="btn btn-secondary flex items-center gap-2">
                        <Filter className="w-5 h-5" />
                        進階過濾
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* 分類側邊欄 */}
                <div className="space-y-2">
                    <h3 className="font-bold mb-3">分類</h3>
                    {categories.map(cat => (
                        <button
                            key={cat.id}
                            onClick={() => setSelectedCategory(cat.id)}
                            className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${selectedCategory === cat.id
                                    ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-medium'
                                    : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                                }`}
                        >
                            <div className="flex items-center justify-between">
                                <span>{cat.name}</span>
                                <span className="text-sm text-gray-500">{cat.count}</span>
                            </div>
                        </button>
                    ))}
                </div>

                {/* 新聞列表 */}
                <div className="lg:col-span-3 space-y-4">
                    <h3 className="font-bold">{filteredNews.length} 篇新聞</h3>

                    {filteredNews.map(news => (
                        <NewsCard key={news.id} news={news} />
                    ))}

                    {filteredNews.length === 0 && (
                        <div className="card text-center py-12">
                            <Newspaper className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                            <p className="text-gray-500 dark:text-gray-400">
                                無符合條件的新聞
                            </p>
                        </div>
                    )}
                </div>
            </div>

            {/* RSS 源管理 */}
            <div className="card">
                <h2 className="text-2xl font-bold mb-4">RSS 訂閱源</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <RSSSourceCard name="MoneyDJ" url="https://www.moneydj.com/rss/" status="active" />
                    <RSSSourceCard name="Bloomberg" url="https://www.bloomberg.com/feed/" status="active" />
                    <RSSSourceCard name="Reuters" url="https://www.reuters.com/rssfeed/" status="inactive" />
                </div>
            </div>
        </div>
    )
}

// 新聞卡片元件
function NewsCard({ news }) {
    const categoryColors = {
        tech: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
        macro: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400',
        company: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
        crypto: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400',
    }

    return (
        <div className="card hover:shadow-lg transition-shadow duration-200">
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${categoryColors[news.category]}`}>
                        {news.category}
                    </span>
                    <span className="text-sm text-gray-500">{news.source}</span>
                </div>
                <span className="text-sm text-gray-400">{news.date}</span>
            </div>

            <h3 className="text-lg font-bold mb-2 hover:text-blue-600 dark:hover:text-blue-400 cursor-pointer">
                {news.title}
            </h3>

            <div className="flex items-start gap-2 mb-3">
                <Sparkles className="w-4 h-4 text-blue-500 flex-shrink-0 mt-1" />
                <p className="text-sm text-gray-600 dark:text-gray-400">{news.summary}</p>
            </div>

            <a
                href={news.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
                閱讀完整報導 →
            </a>
        </div>
    )
}

// RSS 源卡片元件
function RSSSourceCard({ name, url, status }) {
    return (
        <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
            <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium">{name}</h4>
                <span className={`px-2 py-1 rounded text-xs font-medium ${status === 'active'
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                    }`}>
                    {status === 'active' ? '啟用' : '停用'}
                </span>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{url}</p>
        </div>
    )
}
