// 前端範例頁面 - 股票列表整合真實API
import React, { useState, useEffect } from 'react';
import { api, fetchAPI } from '../services/api';

const StockListDemo = () => {
    const [stocks, setStocks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [market, setMarket] = useState('tw');

    useEffect(() => {
        loadStocks();
    }, [market]);

    const loadStocks = async () => {
        try {
            setLoading(true);
            const data = await fetchAPI(api.stocks.list(market, 20));
            setStocks(data.stocks || []);
            setError(null);
        } catch (err) {
            setError(err.message);
            setStocks([]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6">
            <div className="mb-6">
                <h1 className="text-3xl font-bold mb-4">股票列表</h1>

                <div className="flex gap-4 mb-4">
                    <button
                        onClick={() => setMarket('tw')}
                        className={`px-4 py-2 rounded ${market === 'tw'
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-200 dark:bg-gray-700'
                            }`}
                    >
                        台股
                    </button>
                    <button
                        onClick={() => setMarket('us')}
                        className={`px-4 py-2 rounded ${market === 'us'
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-200 dark:bg-gray-700'
                            }`}
                    >
                        美股
                    </button>
                </div>
            </div>

            {loading && (
                <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">載入中...</p>
                </div>
            )}

            {error && (
                <div className="bg-red-100 dark:bg-red-900/30 border border-red-400 text-red-700 dark:text-red-300 px-4 py-3 rounded">
                    錯誤: {error}
                </div>
            )}

            {!loading && !error && (
                <div className="grid gap-4">
                    {stocks.length === 0 ? (
                        <p className="text-gray-500 text-center py-8">暫無數據</p>
                    ) : (
                        stocks.map((stock) => (
                            <div
                                key={stock.stock_code}
                                className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow hover:shadow-lg transition-shadow"
                            >
                                <div className="flex justify-between items-center">
                                    <div>
                                        <h3 className="text-xl font-bold">{stock.stock_code}</h3>
                                        <p className="text-gray-600 dark:text-gray-400">
                                            {stock.stock_name}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-500">{stock.industry}</p>
                                        <p className="text-xs text-gray-400">{stock.market}</p>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
};

export default StockListDemo;
