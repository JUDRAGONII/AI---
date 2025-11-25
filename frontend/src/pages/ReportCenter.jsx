// 報告中心頁面 (Report Center)
// PDF/CSV 匯出、報告歸檔、歷史報告查詢
import { useState } from 'react'
import { FileText, Download, Calendar, Filter, Search } from 'lucide-react'

export default function ReportCenter() {
    const [filterType, setFilterType] = useState('all')
    const [searchQuery, setSearchQuery] = useState('')

    // 報告列表
    const reports = [
        {
            id: 1,
            title: '2024年11月 投資組合績效報告',
            type: 'portfolio',
            date: '2024-11-22',
            format: 'PDF',
            size: '2.3 MB',
            description: '包含持股明細、績效分析、風險指標'
        },
        {
            id: 2,
            title: '台積電 (2330) AI 深度分析報告',
            type: 'stock',
            date: '2024-11-21',
            format: 'PDF',
            size: '1.8 MB',
            description: 'AI 生成的個股分析報告'
        },
        {
            id: 3,
            title: '每日戰略報告 - 2024-11-20',
            type: 'daily',
            date: '2024-11-20',
            format: 'PDF',
            size: '850 KB',
            description: '市場總覽、AI 觀點、投資建議'
        },
        {
            id: 4,
            title: '交易記錄明細 (2024 Q3)',
            type: 'transaction',
            date: '2024-10-01',
            format: 'CSV',
            size: '125 KB',
            description: '第三季度所有交易記錄'
        },
        {
            id: 5,
            title: '因子分析報告 - 半導體產業',
            type: 'factor',
            date: '2024-09-15',
            format: 'PDF',
            size: '3.1 MB',
            description: '半導體產業六大因子綜合分析'
        },
        {
            id: 6,
            title: '策略回測報告 - MA交叉策略',
            type: 'backtest',
            date: '2024-09-10',
            format: 'PDF',
            size: '1.5 MB',
            description: '回測期間 2020-2024，總報酬 +45%'
        }
    ]

    const filteredReports = reports.filter(report => {
        const matchType = filterType === 'all' || report.type === filterType
        const matchSearch = report.title.toLowerCase().includes(searchQuery.toLowerCase())
        return matchType && matchSearch
    })

    // 報告類型統計
    const stats = {
        total: reports.length,
        portfolio: reports.filter(r => r.type === 'portfolio').length,
        stock: reports.filter(r => r.type === 'stock').length,
        daily: reports.filter(r => r.type === 'daily').length,
        transaction: reports.filter(r => r.type === 'transaction').length
    }

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">報告中心</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        管理、匯出與歸檔所有分析報告
                    </p>
                </div>

                <button className="btn btn-primary flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    生成新報告
                </button>
            </div>

            {/* 統計卡片 */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
                <StatCard label="總報告數" value={stats.total} color="blue" />
                <StatCard label="投資組合" value={stats.portfolio} color="green" />
                <StatCard label="個股分析" value={stats.stock} color="purple" />
                <StatCard label="每日戰略" value={stats.daily} color="orange" />
                <StatCard label="交易記錄" value={stats.transaction} color="gray" />
            </div>

            {/* 搜尋與篩選 */}
            <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="搜尋報告..."
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                    />
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={() => setFilterType('all')}
                        className={`px-4 py-2 rounded-lg ${filterType === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                    >
                        全部
                    </button>
                    <button
                        onClick={() => setFilterType('portfolio')}
                        className={`px-4 py-2 rounded-lg ${filterType === 'portfolio' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                    >
                        投資組合
                    </button>
                    <button
                        onClick={() => setFilterType('stock')}
                        className={`px-4 py-2 rounded-lg ${filterType === 'stock' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                    >
                        個股
                    </button>
                    <button
                        onClick={() => setFilterType('daily')}
                        className={`px-4 py-2 rounded-lg ${filterType === 'daily' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}
                    >
                        每日
                    </button>
                </div>
            </div>

            {/* 報告列表 */}
            <div className="space-y-4">
                {filteredReports.map(report => (
                    <ReportCard key={report.id} report={report} />
                ))}
            </div>

            {filteredReports.length === 0 && (
                <div className="card text-center py-12">
                    <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 dark:text-gray-400">找不到符合的報告</p>
                </div>
            )}
        </div>
    )
}

// 統計卡片
function StatCard({ label, value, color }) {
    const colorClasses = {
        blue: 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
        green: 'bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400',
        purple: 'bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
        orange: 'bg-orange-50 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
        gray: 'bg-gray-50 dark:bg-gray-900/30 text-gray-600 dark:text-gray-400'
    }

    return (
        <div className={`card ${colorClasses[color]}`}>
            <div className="text-sm font-medium mb-2">{label}</div>
            <div className="text-2xl font-bold">{value}</div>
        </div>
    )
}

// 報告卡片
function ReportCard({ report }) {
    const typeLabels = {
        portfolio: '投資組合',
        stock: '個股分析',
        daily: '每日戰略',
        transaction: '交易記錄',
        factor: '因子分析',
        backtest: '策略回測'
    }

    const typeColors = {
        portfolio: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
        stock: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400',
        daily: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400',
        transaction: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400',
        factor: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
        backtest: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
    }

    return (
        <div className="card">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-start gap-3 flex-1">
                    <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/30">
                        <FileText className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-lg font-bold">{report.title}</h3>
                            <span className={`px-2 py-1 rounded text-xs font-medium ${typeColors[report.type]}`}>
                                {typeLabels[report.type]}
                            </span>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{report.description}</p>
                        <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                            <div className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {report.date}
                            </div>
                            <span>{report.format}</span>
                            <span>{report.size}</span>
                        </div>
                    </div>
                </div>

                <div className="flex gap-2">
                    <button className="btn btn-secondary text-sm flex items-center gap-1">
                        <Download className="w-4 h-4" />
                        下載
                    </button>
                </div>
            </div>
        </div>
    )
}
