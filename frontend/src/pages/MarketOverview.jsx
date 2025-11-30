import React, { useState, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const MarketOverview = () => {
    const [goldPrices, setGoldPrices] = useState([]);
    const [forexRates, setForexRates] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchMarketData();
    }, []);

    const fetchMarketData = async () => {
        try {
            setLoading(true);

            // 獲取黃金價格
            const goldResponse = await fetch('http://localhost:5000/api/commodity/GOLD?days=30');
            const goldData = await goldResponse.json();
            if (goldData.prices) {
                setGoldPrices(goldData.prices.map(p => ({
                    date: p.trade_date.split('T')[0],
                    price: parseFloat(p.close_price)
                })));
            }

            // 獲取USD/TWD匯率
            const forexResponse = await fetch('http://localhost:5000/api/forex/USDTWD?days=30');
            const forexData = await forexResponse.json();
            if (forexData.rates) {
                setForexRates(forexData.rates.map(r => ({
                    date: r.trade_date.split('T')[0],
                    rate: parseFloat(r.rate)
                })));
            }

            setLoading(false);
        } catch (error) {
            console.error('獲取市場數據失敗:', error);
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <RefreshCw className="w-16 h-16 mx-auto mb-4 text-blue-600 animate-spin" />
                    <p className="text-gray-600 dark:text-gray-400">載入市場數據中...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-6">
            {/* 頁面標題 */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">市場總覽</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">黃金價格與匯率走勢</p>
                </div>
                <button
                    onClick={fetchMarketData}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                    <RefreshCw className="w-4 h-4" />
                    刷新數據
                </button>
            </div>

            {/* 黃金價格走勢 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
                <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
                    黃金價格30日走勢
                </h2>
                {goldPrices.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={goldPrices}>
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
                                stroke="#F59E0B"
                                strokeWidth={2}
                                name="黃金價格"
                            />
                        </LineChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="text-center py-16 text-gray-500">
                        <p>暫無黃金數據</p>
                        <p className="text-sm mt-2">請執行數據同步腳本</p>
                    </div>
                )}
            </div>

            {/* 匯率走勢 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg">
                <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
                    美元台幣30日走勢
                </h2>
                {forexRates.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={forexRates}>
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
                                dataKey="rate"
                                stroke="#10B981"
                                strokeWidth={2}
                                name="匯率"
                            />
                        </LineChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="text-center py-16 text-gray-500">
                        <p>暫無匯率數據</p>
                        <p className="text-sm mt-2">請執行數據同步腳本</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MarketOverview;
