// Dashboard 完整API整合
import React, { useState, useEffect } from 'react';
import { api, fetchAPI } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
    const [stats, setStats] = useState({
        totalStocks: 0,
        totalPrices: 0,
        apiHealth: 'checking...',
    });
    const [topStocks, setTopStocks] = useState([]);
    const [recentPrices, setRecentPrices] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadDashboard();
    }, []);

    const loadDashboard = async () => {
        try {
            setLoading(true);

            // 健康檢查
            const health = await fetchAPI(api.health());
            setStats(prev => ({ ...prev, apiHealth: health.status }));

            // 載入台股列表
            const stocksData = await fetchAPI(api.stocks.list('tw', 10));
            setTopStocks(stocksData.stocks || []);
            setStats(prev => ({ ...prev, totalStocks: stocksData.count }));

            // 載入台積電價格作為示範
            if (stocksData.stocks.length > 0) {
                const priceData = await fetchAPI(api.prices.history('2330', 'tw', 7));
                const chartData = priceData.data.slice(0, 7).map(p => ({
                    date: new Date(p.trade_date).toLocaleDateString('zh-TW', { month: '2-digit', day: '2-digit' }),
                    price: parseFloat(p.close_price),
                }));
                setRecentPrices(chartData);
                setStats(prev => ({ ...prev, totalPrices: priceData.count }));
            }

        } catch (err) {
            console.error('Dashboard load error:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <h1 className="text-4xl font-bold mb-8 text-gray-900 dark:text-white">
                儀表板
            </h1>

            {/* 統計卡片 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                        API狀態
                    </h3>
                    <p className={`text-3xl font-bold ${stats.apiHealth === 'healthy' ? 'text-green-600' : 'text-red-600'
                        }`}>
                        {stats.apiHealth === 'healthy' ? '正常' : '檢查中'}
                    </p>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                        股票總數
                    </h3>
                    <p className="text-3xl font-bold text-blue-600">
                        {stats.totalStocks}
                    </p>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                        價格記錄
                    </h3>
                    <p className="text-3xl font-bold text-purple-600">
                        {stats.totalPrices}
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* 熱門股票 */}
                <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
                    <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
                        熱門台股
                    </h2>
                    <div className="space-y-3">
                        {topStocks.map((stock, idx) => (
                            <div
                                key={stock.stock_code}
                                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                            >
                                <div className="flex items-center gap-3">
                                    <span className="text-lg font-bold text-gray-400">
                                        {idx + 1}
                                    </span>
                                    <div>
                                        <p className="font-bold text-gray-900 dark:text-white">
                                            {stock.stock_code}
                                        </p>
                                        <p className="text-sm text-gray-600 dark:text-gray-400">
                                            {stock.stock_name}
                                        </p>
                                    </div>
                                </div>
                                <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded">
                                    {stock.industry}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* 價格走勢（台積電） */}
                <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
                    <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
                        台積電近7日走勢
                    </h2>
                    {recentPrices.length > 0 ? (
                        <ResponsiveContainer width="100%" height={250}>
                            <LineChart data={recentPrices}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis dataKey="date" stroke="#9CA3AF" />
                                <YAxis stroke="#9CA3AF" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1F2937',
                                        border: 'none',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="price"
                                    stroke="#3B82F6"
                                    strokeWidth={3}
                                    dot={{ fill: '#3B82F6', r: 4 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    ) : (
                        <p className="text-gray-500 text-center py-8">暫無數據</p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
