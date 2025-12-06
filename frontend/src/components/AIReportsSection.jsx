import React, { useState, useEffect } from 'react';
import { FileText, Brain, TrendingUp, Calendar, RefreshCw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const AIReportsSection = () => {
    const [reports, setReports] = useState([]);
    const [selectedReport, setSelectedReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        fetchReports();
    }, [filter]);

    const fetchReports = async () => {
        try {
            setLoading(true);
            const url = filter === 'all'
                ? 'http://localhost:5000/api/ai/reports?limit=10'
                : `http://localhost:5000/api/ai/reports?type=${filter}&limit=5`;

            const response = await fetch(url);
            const data = await response.json();
            setReports(data.reports || []);

            // 預設選中第一份報告
            if (data.reports && data.reports.length > 0 && !selectedReport) {
                setSelectedReport(data.reports[0]);
            }
        } catch (error) {
            console.error('獲取 AI 報告失敗:', error);
        } finally {
            setLoading(false);
        }
    };

    const getReportIcon = (type) => {
        switch (type) {
            case 'daily_strategy':
                return <TrendingUp className="w-5 h-5 text-blue-600" />;
            case 'stock_decision':
                return <FileText className="w-5 h-5 text-green-600" />;
            case 'unified_decision':
                return <FileText className="w-5 h-5 text-green-600" />;
            case 'portfolio_strategy':
                return <Brain className="w-5 h-5 text-purple-600" />;
            default:
                return <FileText className="w-5 h-5 text-gray-600" />;
        }
    };

    const getReportTypeName = (type) => {
        const names = {
            'daily_strategy': '每日戰略',
            'stock_decision': '個股決策',
            'unified_decision': '統合決策',
            'portfolio_strategy': '投資組合策略'
        };
        return names[type] || type;
    };

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <Brain className="w-6 h-6 text-purple-600" />
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                        AI 分析報告中心
                    </h2>
                </div>
                <button
                    onClick={fetchReports}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    title="刷新報告"
                >
                    <RefreshCw className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                </button>
            </div>

            {/* 篩選器 */}
            <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
                {['all', 'daily_strategy', 'stock_decision', 'unified_decision', 'portfolio_strategy'].map(type => (
                    <button
                        key={type}
                        onClick={() => setFilter(type)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${filter === type
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                            }`}
                    >
                        {type === 'all' ? '全部報告' : getReportTypeName(type)}
                    </button>
                ))}
            </div>

            {loading ? (
                <div className="flex items-center justify-center py-12">
                    <div className="text-center">
                        <RefreshCw className="w-8 h-8 mx-auto mb-2 text-blue-600 animate-spin" />
                        <p className="text-gray-600 dark:text-gray-400">載入報告中...</p>
                    </div>
                </div>
            ) : reports.length === 0 ? (
                <div className="text-center py-12">
                    <Brain className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                    <p className="text-gray-600 dark:text-gray-400">尚無 AI 報告</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    {/* 左側：報告列表 */}
                    <div className="lg:col-span-1 space-y-2 max-h-96 overflow-y-auto">
                        {reports.map(report => (
                            <button
                                key={report.id}
                                onClick={() => setSelectedReport(report)}
                                className={`w-full text-left p-4 rounded-lg border transition-all ${selectedReport?.id === report.id
                                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                                    : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700'
                                    }`}
                            >
                                <div className="flex items-start gap-3">
                                    {getReportIcon(report.report_type)}
                                    <div className="flex-1 min-w-0">
                                        <p className="font-medium text-gray-900 dark:text-white text-sm truncate">
                                            {report.report_title}
                                        </p>
                                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center gap-1">
                                            <Calendar className="w-3 h-3" />
                                            {new Date(report.created_at).toLocaleString('zh-TW')}
                                        </p>
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>

                    {/* 右側：報告內容 */}
                    <div className="lg:col-span-2 border border-gray-200 dark:border-gray-700 rounded-lg p-6 max-h-96 overflow-y-auto">
                        {selectedReport ? (
                            <div>
                                <div className="flex items-center gap-2 mb-4">
                                    {getReportIcon(selectedReport.report_type)}
                                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                                        {selectedReport.report_title}
                                    </h3>
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-400 mb-4 flex items-center gap-4">
                                    <span className="flex items-center gap-1">
                                        <Calendar className="w-3 h-3" />
                                        {new Date(selectedReport.created_at).toLocaleString('zh-TW')}
                                    </span>
                                    <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded">
                                        {selectedReport.generated_by}
                                    </span>
                                </div>
                                <div className="prose dark:prose-invert max-w-none">
                                    <ReactMarkdown>{selectedReport.report_content}</ReactMarkdown>
                                </div>
                            </div>
                        ) : (
                            <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
                                請選擇一份報告查看
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default AIReportsSection;
