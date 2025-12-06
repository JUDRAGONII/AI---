import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, PlusCircle, Trash2, RefreshCw, PieChart, BarChart3 } from 'lucide-react';

const Portfolio = () => {
    const [portfolioData, setPortfolioData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);

    useEffect(() => {
        fetchPortfolio();
    }, []);

    const fetchPortfolio = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:5000/api/portfolio');
            const data = await response.json();
            setPortfolioData(data);
        } catch (error) {
            console.error('獲取投資組合失敗:', error);
        } finally {
            setLoading(false);
        }
    };

    const deleteHolding = async (holdingId) => {
        if (!window.confirm('確定要刪除此持倉嗎？')) return;

        try {
            await fetch(`http://localhost:5000/api/portfolio/holdings/${holdingId}`, {
                method: 'DELETE'
            });
            fetchPortfolio();
        } catch (error) {
            console.error('刪除持倉失敗:', error);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <RefreshCw className="w-16 h-16 mx-auto mb-4 text-blue-600 animate-spin" />
                    <p className="text-gray-600 dark:text-gray-400">載入投資組合中...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* 頁面標題 */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                        投資組合明細
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">持倉管理 + 績效分析 + 風險指標</p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={fetchPortfolio}
                        className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center gap-2"
                    >
                        <RefreshCw className="w-4 h-4" />
                        刷新
                    </button>
                    <button
                        onClick={() => setShowAddForm(!showAddForm)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                    >
                        <PlusCircle className="w-4 h-4" />
                        新增持倉
                    </button>
                </div>
            </div>

            {/* 總覽卡片 */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600 dark:text-gray-400">總資產</span>
                        <DollarSign className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        ${portfolioData?.total_value?.toLocaleString() || 0}
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600 dark:text-gray-400">總成本</span>
                        <BarChart3 className="w-5 h-5 text-gray-600" />
                    </div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        ${portfolioData?.total_cost?.toLocaleString() || 0}
                    </div>
                </div>

                <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 ${portfolioData?.total_profit >= 0 ? 'border-l-4 border-green-500' : 'border-l-4 border-red-500'
                    }`}>
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600 dark:text-gray-400">總損益</span>
                        {portfolioData?.total_profit >= 0 ? (
                            <TrendingUp className="w-5 h-5 text-green-600" />
                        ) : (
                            <TrendingDown className="w-5 h-5 text-red-600" />
                        )}
                    </div>
                    <div className={`text-2xl font-bold ${portfolioData?.total_profit >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                        {portfolioData?.total_profit >= 0 ? '+' : ''}
                        ${portfolioData?.total_profit?.toLocaleString() || 0}
                    </div>
                </div>

                <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 ${portfolioData?.return_rate >= 0 ? 'border-l-4 border-green-500' : 'border-l-4 border-red-500'
                    }`}>
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600 dark:text-gray-400">報酬率</span>
                        <PieChart className="w-5 h-5 text-purple-600" />
                    </div>
                    <div className={`text-2xl font-bold ${portfolioData?.return_rate >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                        {portfolioData?.return_rate >= 0 ? '+' : ''}
                        {portfolioData?.return_rate?.toFixed(2) || 0}%
                    </div>
                </div>
            </div>

            {/* 持倉列表 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
                <div className="p-6">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">持倉明細</h2>

                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50 dark:bg-gray-700">
                                <tr>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                        代碼
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                        市場
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                        數量
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                        平均成本
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                        現價
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                        市值
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                        損益
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                        比重
                                    </th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                        操作
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                {portfolioData?.holdings?.map((holding) => (
                                    <tr key={holding.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                        <td className="px-4 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <div>
                                                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                                                        {holding.stock_code}
                                                    </div>
                                                    <div className="text-xs text-gray-500 dark:text-gray-400">
                                                        {holding.notes || '-'}
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap">
                                            <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${holding.market === 'tw'
                                                    ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
                                                    : 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300'
                                                }`}>
                                                {holding.market.toUpperCase()}
                                            </span>
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-gray-900 dark:text-white">
                                            {holding.quantity.toLocaleString()}
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-gray-900 dark:text-white">
                                            ${holding.avg_cost}
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-gray-900 dark:text-white">
                                            ${holding.current_price}
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900 dark:text-white">
                                            ${holding.market_value?.toLocaleString()}
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm">
                                            <div className={holding.profit >= 0 ? 'text-green-600' : 'text-red-600'}>
                                                <div className="font-medium">
                                                    {holding.profit >= 0 ? '+' : ''}${Math.abs(holding.profit).toLocaleString()}
                                                </div>
                                                <div className="text-xs">
                                                    ({holding.profit_rate >= 0 ? '+' : ''}{holding.profit_rate}%)
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-gray-900 dark:text-white">
                                            {holding.weight}%
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <button
                                                onClick={() => deleteHolding(holding.id)}
                                                className="text-red-600 hover:text-red-900 dark:hover:text-red-400"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* 提示訊息 */}
            {(!portfolioData?.holdings || portfolioData.holdings.length === 0) && (
                <div className="text-center py-12">
                    <PieChart className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                    <p className="text-gray-600 dark:text-gray-400">尚無持倉數據</p>
                    <button
                        onClick={() => setShowAddForm(true)}
                        className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        新增第一筆持倉
                    </button>
                </div>
            )}
        </div>
    );
};

export default Portfolio;
