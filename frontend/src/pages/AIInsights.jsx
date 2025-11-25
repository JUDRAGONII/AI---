// AI 統一觀點頁面 (AI Insights / House View)
// 展示每日戰略報告、歷史觀點追蹤
import { useState, useEffect } from 'react'
import { Calendar, TrendingUp, Target, Clock, CheckCircle, XCircle } from 'lucide-react'
import { db } from '../supabase'
import ReactMarkdown from 'react-markdown'

export default function AIInsights() {
    const [loading, setLoading] = useState(true)
    const [dailyReports, setDailyReports] = useState([])
    const [selectedReport, setSelectedReport] = useState(null)
    const [reportType, setReportType] = useState('daily_strategy')

    useEffect(() => {
        loadReports()
    }, [reportType])

    const loadReports = async () => {
        setLoading(true)
        try {
            // 從資料庫獲取 AI 報告
            const reports = await db.queryAIReports(reportType, 30)

            if (reports && reports.length > 0) {
                setDailyReports(reports)
                setSelectedReport(reports[0])  // 預設選擇最新一篇
            }
        } catch (error) {
            console.error('載入 AI 報告失敗:', error)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-xl">載入中...</div>
            </div>
        )
    }

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">AI 統一觀點</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        Gemini AI 每日市場戰略分析 | 數據驅動決策依據
                    </p>
                </div>

                {/* 報告類型選擇 */}
                <div className="flex items-center gap-3">
                    <select
                        value={reportType}
                        onChange={(e) => setReportType(e.target.value)}
                        className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                    >
                        <option value="daily_strategy">每日戰略報告</option>
                        <option value="decision_template">決策模板</option>
                        <option value="portfolio_strategy">投資組合策略</option>
                    </select>
                </div>
            </div>

            {dailyReports.length > 0 ? (
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    {/* 左側：報告列表 */}
                    <div className="lg:col-span-1 space-y-3">
                        <h2 className="text-lg font-bold mb-4">歷史報告</h2>
                        <div className="space-y-2 max-h-[600px] overflow-y-auto">
                            {dailyReports.map((report) => (
                                <ReportCard
                                    key={report.id}
                                    report={report}
                                    isSelected={selectedReport?.id === report.id}
                                    onClick={() => setSelectedReport(report)}
                                />
                            ))}
                        </div>
                    </div>

                    {/* 右側：報告內容 */}
                    <div className="lg:col-span-3">
                        {selectedReport && (
                            <div className="card">
                                {/* 報告標題資訊 */}
                                <div className="mb-6 pb-6 border-b border-gray-200 dark:border-gray-700">
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <h2 className="text-2xl font-bold mb-2">
                                                {getReportTitle(selectedReport.report_type)}
                                            </h2>
                                            <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                                                <div className="flex items-center gap-1">
                                                    <Calendar className="w-4 h-4" />
                                                    <span>
                                                        {new Date(selectedReport.report_date || selectedReport.created_at).toLocaleDateString('zh-TW', {
                                                            year: 'numeric',
                                                            month: 'long',
                                                            day: 'numeric'
                                                        })}
                                                    </span>
                                                </div>
                                                <div className="flex items-center gap-1">
                                                    <Clock className="w-4 h-4" />
                                                    <span>
                                                        {new Date(selectedReport.created_at).toLocaleTimeString('zh-TW', {
                                                            hour: '2-digit',
                                                            minute: '2-digit'
                                                        })}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>

                                        {/* 情緒指標（如果有）*/}
                                        {selectedReport.sentiment && (
                                            <div className="px-4 py-2 rounded-lg bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700">
                                                <div className="text-xs text-gray-600 dark:text-gray-400">市場情緒</div>
                                                <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                                                    {selectedReport.sentiment}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* 報告內容 (Markdown 渲染) */}
                                <div className="prose dark:prose-invert max-w-none">
                                    <ReactMarkdown>
                                        {selectedReport.content || '本報告尚未生成內容'}
                                    </ReactMarkdown>
                                </div>

                                {/* 報告標籤/關鍵詞（如果有）*/}
                                {selectedReport.tags && selectedReport.tags.length > 0 && (
                                    <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                                        <div className="flex items-center gap-2 flex-wrap">
                                            <span className="text-sm font-medium">標籤：</span>
                                            {selectedReport.tags.map((tag, index) => (
                                                <span
                                                    key={index}
                                                    className="px-3 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                                                >
                                                    {tag}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            ) : (
                <div className="card text-center py-12">
                    <TrendingUp className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                    <p className="text-gray-500 dark:text-gray-400 text-lg">
                        暫無 AI 報告
                    </p>
                    <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
                        請稍後再試，或確認資料庫中是否有生成報告
                    </p>
                </div>
            )}

            {/* 觀點準確度追蹤區（未來功能）*/}
            {dailyReports.length > 0 && (
                <div className="card bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-blue-200 dark:border-blue-800">
                    <div className="flex items-start gap-3">
                        <Target className="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-1" />
                        <div>
                            <h3 className="font-bold text-lg mb-2">歷史觀點準確度追蹤</h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                                此功能將追蹤 AI 觀點的準確度，比對預測與實際市場表現
                            </p>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <AccuracyCard label="預測準確率" value="--%" icon={<CheckCircle className="w-5 h-5" />} />
                                <AccuracyCard label="錯誤預測" value="--次" icon={<XCircle className="w-5 h-5" />} />
                                <AccuracyCard label="平均偏差" value="--%" icon={<TrendingUp className="w-5 h-5" />} />
                            </div>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">
                                * 功能開發中，未來將自動追蹤並評估 AI 預測表現
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

// 報告卡片元件
function ReportCard({ report, isSelected, onClick }) {
    return (
        <div
            onClick={onClick}
            className={`
        p-4 rounded-lg border cursor-pointer transition-all duration-200
        ${isSelected
                    ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-500 dark:border-blue-600 shadow-md'
                    : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700'
                }
      `}
        >
            <div className="flex items-start justify-between mb-2">
                <div className="text-sm font-medium">
                    {new Date(report.report_date || report.created_at).toLocaleDateString('zh-TW', {
                        month: 'short',
                        day: 'numeric'
                    })}
                </div>
                {isSelected && (
                    <CheckCircle className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                )}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
                {report.content ? report.content.substring(0, 60) + '...' : '查看報告內容'}
            </div>
        </div>
    )
}

// 準確度卡片元件
function AccuracyCard({ label, value, icon }) {
    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
                {icon}
            </div>
            <div className="text-2xl font-bold">{value}</div>
        </div>
    )
}

// 獲取報告標題
function getReportTitle(reportType) {
    const titles = {
        'daily_strategy': '每日戰略投資分析報告',
        'decision_template': '統合究極版決策模板',
        'portfolio_strategy': 'AI 投資組合策略建議'
    }
    return titles[reportType] || '投資分析報告'
}
