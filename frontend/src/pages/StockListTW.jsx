// StockListTW 完整API整合
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api, fetchAPI } from '../services/api';

const StockListTW = () => {
    const [stocks, setStocks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [limit, setLimit] = useState(50);

    useEffect(() => {
        loadStocks();
    }, [limit]);

    const loadStocks = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await fetchAPI(api.stocks.list('tw', limit));
            setStocks(data.stocks || []);
        } catch (err) {
            setError(err.message);
            setStocks([]);
        } finally {
            setLoading(false);
        }
    };

    const filteredStocks = stocks.filter(stock =>
        stock.stock_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        stock.stock_name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="mb-8">
                <h1 className="text-4xl font-bold mb-4 text-gray-900 dark:text-white">
                    台股清單
                </h1>
                <p className="text-gray-600 dark:text-gray-400">
                    共 {stocks.length} 支股票
                </p>
            </div>

            {/* 搜尋與篩選 */}
            <div className="mb-6 flex flex-col sm:flex-row gap-4">
                <input
                    type="text"
                    placeholder="搜尋股票代碼或名稱..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                />
                <select
                    value={limit}
                    onChange={(e) => setLimit(parseInt(e.target.value))}
                    className="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                >
                    <option value={20}>顯示 20 筆</option>
                    <option value={50}>顯示 50 筆</option>
                    <option value={100}>顯示 100 筆</option>
                </select>
            </div>

            {loading && (
                <div className="flex justify-center items-center py-16">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
            )}

            {error && (
                <div className="bg-red-100 dark:bg-red-900/30 border border-red-400 text-red-700 dark:text-red-300 px-4 py-3 rounded-lg mb-6">
                    錯誤: {error}
                </div>
            )}

            {!loading && !error && (
                <>
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
                        <table className="w-full">
                            <thead className="bg-gray-50 dark:bg-gray-700">
                                <tr>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 dark:text-white">
                                        股票代碼
                                    </th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 dark:text-white">
                                        股票名稱
                                    </th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 dark:text-white">
                                        產業
                                    </th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 dark:text-white">
                                        市場
                                    </th>
                                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 dark:text-white">
                                        操作
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                                {filteredStocks.map((stock) => (
                                    <tr
                                        key={stock.stock_code}
                                        className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                                    >
                                        <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">
                                            {stock.stock_code}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                                            {stock.stock_name}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                                            <span className="inline-block bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded text-xs">
                                                {stock.industry}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                                            {stock.market}
                                        </td>
                                        <td className="px-6 py-4 text-sm">
                                            <Link
                                                to={`/stock/${stock.stock_code}`}
                                                className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
                                            >
                                                查看詳情 →
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {filteredStocks.length === 0 && !loading && (
                        <div className="text-center py-16">
                            <p className="text-gray-500 dark:text-gray-400 text-lg">
                                找不到符合條件的股票
                            </p>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default StockListTW;
