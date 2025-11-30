import React, { useState, useEffect } from 'react';
import { Brain, TrendingUp, AlertTriangle, Clock, Download, RefreshCw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const AIHouseView = () => {
    const [reports, setReports] = useState([]);
    const [currentReport, setCurrentReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        loadReports();
    }, []);

    const loadReports = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:5000/api/ai/reports?type=market&limit=10');

            if (!response.ok) {
                throw new Error('獲取報告失敗');
            }

            const data = await response.json();

            if (data.reports && data.reports.length > 0) {
                const formattedReports = data.reports.map(report => ({
                    id: report.id,
                    date: new Date(report.created_at).toLocaleDateString('zh-TW'),
                    title: report.title,
                    type: report.report_type,
                    sentiment: report.sentiment || 'neutral',
                    content: report.content,
                    accuracy: parseFloat(report.accuracy) || 0,
                    lastUpdated: new Date(report.created_at).toLocaleString('zh-TW')
                }));
                setReports(formattedReports);
                setCurrentReport(formattedReports[0]);
            } else {
                // 如果沒有報告，設置為空
                setReports([]);
                setCurrentReport(null);
            }
            setLoading(false);
        } catch (error) {
            console.error('載入報告失敗:', error);
            setReports([]);
            setCurrentReport(null);
            setLoading(false);
        }
    };

    const generateNewReport = async () => {
        try {
            setGenerating(true);
            const response = await fetch('http://localhost:5000/api/ai/market-report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    market_data: {
                        taiex: 17450,
                        sp500: 4560,
                        nasdaq: 14200,
                        vix: 15.8,
                        gold: 2040.50,
                        usdtwd: 31.4
                    }
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '報告生成失敗');
            }

            const result = await response.json();

            // 重新載入報告列表
            await loadReports();

            setGenerating(false);
            alert('AI報告生成成功！');
        } catch (error) {
            console.error('生成報告失敗:', error);
            setGenerating(false);
            alert(`AI報告生成失敗：${error.message}`);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <Brain className="w-16 h-16 mx-auto mb-4 text-blue-600 animate-pulse" />
                    <p className="text-gray-600 dark:text-gray-400">載入AI報告中...</p>
                </div>
            </div>
        );
    }

    // 如果沒有報告，顯示空狀態
    if (reports.length === 0) {
        return (
            <div className="p-6 max-w-7xl mx-auto">
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">AI 統一觀點</h1>
                        <p className="text-gray-600 dark:text-gray-400 mt-2">每日市場覆盤 | AI 核心觀點 | 歷史準確度追蹤</p>
                    </div>
                    <button
                        onClick={generateNewReport}
                        disabled={generating}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center gap-2"
                    >
                        {generating ? (
                            <>
                                <RefreshCw className="w-4 h-4 animate-spin" />
                                生成中...
                            </>
                        ) : (
                            <>
                                <Brain className="w-4 h-4" />
                                生成新報告
                            </>
                        )}
                    </button>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
                    <Brain className="w-24 h-24 mx-auto mb-6 text-gray-400" />
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">尚無AI報告</h2>
                    <p className="text-gray-600 dark:text-gray-400 mb-6">點擊上方「生成新報告」按鈕，使用AI生成第一份市場分析報告</p>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* 標題與操作 */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">AI 統一觀點</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">每日市場覆盤 | AI 核心觀點 | 歷史準確度追蹤</p>
                </div>
                <button
                    onClick={generateNewReport}
                    disabled={generating}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center gap-2"
                >
                    {generating ? (
                        <>
                            <RefreshCw className="w-4 h-4 animate-spin" />
                            生成中...
                        </>
                    ) : (
                        <>
                            <Brain className="w-4 h-4" />
                            生成新報告
                        </>
                    )}
                </button>
            </div>

            {/* 報告概覽卡片 */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <div className="flex items-center gap-3 mb-2">
                        <Brain className="w-5 h-5 text-blue-600" />
                        <span className="text-sm text-gray-600 dark:text-gray-400">總報告數</span>
                    </div>
                    <div className="text-3xl font-bold">{reports.length}</div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <div className="flex items-center gap-3 mb-2">
                        <TrendingUp className="w-5 h-5 text-green-600" />
                        <span className="text-sm text-gray-600 dark:text-gray-400">平均準確度</span>
                    </div>
                    <div className="text-3xl font-bold text-green-600">
                        {reports.length > 0
                            ? `${(reports.reduce((sum, r) => sum + r.accuracy, 0) / reports.length).toFixed(1)}%`
                            : 'N/A'}
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <div className="flex items-center gap-3 mb-2">
                        <AlertTriangle className="w-5 h-5 text-yellow-600" />
                        <span className="text-sm text-gray-600 dark:text-gray-400">市場情緒</span>
                    </div>
                    <div className="text-lg font-semibold">
                        <span className="inline-block px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">
                            {currentReport?.sentiment === 'bullish' ? '看多' :
                                currentReport?.sentiment === 'bearish' ? '看空' : '中性'}
                        </span>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <div className="flex items-center gap-3 mb-2">
                        <Clock className="w-5 h-5 text-gray-600" />
                        <span className="text-sm text-gray-600 dark:text-gray-400">最後更新</span>
                    </div>
                    <div className="text-sm font-semibold">{currentReport?.lastUpdated || 'N/A'}</div>
                </div>
            </div>

            {/* 報告內容 */}
            {currentReport && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
                    <div className="border-b border-gray-200 dark:border-gray-700 p-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{currentReport.title}</h2>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">生成時間：{currentReport.lastUpdated}</p>
                            </div>
                            <button className="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2">
                                <Download className="w-4 h-4" />
                                匯出PDF
                            </button>
                        </div>
                    </div>

                    <div className="p-6">
                        <div className="prose dark:prose-invert max-w-none">
                            <ReactMarkdown>{currentReport.content}</ReactMarkdown>
                        </div>
                    </div>
                </div>
            )}

            {/* 歷史報告列表 */}
            {reports.length > 1 && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">歷史報告</h3>
                    <div className="space-y-3">
                        {reports.slice(1).map((report) => (
                            <div
                                key={report.id}
                                onClick={() => setCurrentReport(report)}
                                className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                            >
                                <div className="flex items-center justify-between">
                                    <div>
                                        <div className="font-semibold">{report.title}</div>
                                        <div className="text-sm text-gray-600 dark:text-gray-400">{report.date}</div>
                                    </div>
                                    <div className="text-sm text-gray-600 dark:text-gray-400">
                                        準確度: {report.accuracy}%
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default AIHouseView;
