// 股票詳情頁面 - 整合價格圖表
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { api, fetchAPI } from '../services/api';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';

const StockDetailDemo = () => {
    const { code } = useParams();
    const [stock, setStock] = useState(null);
    const [prices, setPrices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [days, setDays] = useState(30);

    useEffect(() => {
        loadData();
    }, [code, days]);

    const loadData = async () => {
        try {
            setLoading(true);

            // 載入股票資訊
            const stockData = await fetchAPI(api.stocks.detail(code, 'tw'));
            setStock(stockData);

            // 載入價格歷史
            const priceData = await fetchAPI(api.prices.history(code, 'tw', days));

            // 轉換數據格式供圖表使用
            const chartData = priceData.data.map(p => ({
                date: new Date(p.trade_date).toLocaleDateString('zh-TW', { month: '2-digit', day: '2-digit' }),
                price: parseFloat(p.close_price),
                volume: parseInt(p.volume)
            }));

            setPrices(chartData);

        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="p-6">
            {/* 股票資訊卡片 */}
            {stock && (
                <div className="bg-white dark:bg-gray-800 rounded-lg p-6 mb-6 shadow">
                    <div className="flex justify-between items-start">
                        <div>
                            <h1 className="text-3xl font-bold mb-2">{stock.stock_code}</h1>
                            <p className="text-xl text-gray-600 dark:text-gray-400">{stock.stock_name}</p>
                            <p className="text-sm text-gray-500 mt-2">{stock.industry} · {stock.market}</p>
                        </div>
                        {prices.length > 0 && (
                            <div className="text-right">
                                <p className="text-sm text-gray-500">最新收盤價</p>
                                <p className="text-3xl font-bold text-blue-600">
                                    ${prices[prices.length - 1].price.toFixed(2)}
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* 時間範圍選擇 */}
            <div className="mb-4 flex gap-2">
                {[7, 30, 90].map(d => (
                    <button
                        key={d}
                        onClick={() => setDays(d)}
                        className={`px-4 py-2 rounded ${days === d
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-200 dark:bg-gray-700'
                            }`}
                    >
                        {d}天
                    </button>
                ))}
            </div>

            {/* 價格圖表 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
                <h2 className="text-xl font-bold mb-4">價格走勢</h2>
                <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={prices}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line
                            type="monotone"
                            dataKey="price"
                            stroke="#2563eb"
                            strokeWidth={2}
                            name="收盤價"
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* 成交量圖表 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow mt-6">
                <h2 className="text-xl font-bold mb-4">成交量</h2>
                <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={prices}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Line
                            type="monotone"
                            dataKey="volume"
                            stroke="#10b981"
                            name="成交量"
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default StockDetailDemo;
