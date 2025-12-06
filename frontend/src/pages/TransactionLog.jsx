import React, { useState, useEffect } from 'react';
import { Plus, Trash2, RefreshCw, Filter, DollarSign, TrendingUp, TrendingDown, Calendar } from 'lucide-react';

const TransactionLog = () => {
    const [transactions, setTransactions] = useState([]);
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);
    const [brokers, setBrokers] = useState([]);

    // 篩選器狀態
    const [filters, setFilters] = useState({
        market: '',
        type: '',
        stock_code: '',
        start_date: '',
        end_date: ''
    });

    // 新增表單狀態
    const [formData, setFormData] = useState({
        stock_code: '',
        market: 'tw',
        transaction_type: 'buy',
        quantity: '',
        price: '',
        transaction_date: new Date().toISOString().split('T')[0],
        broker: '元大證券',
        notes: ''
    });

    useEffect(() => {
        fetchTransactions();
        fetchBrokers();
    }, []);

    const fetchTransactions = async () => {
        try {
            setLoading(true);
            const params = new URLSearchParams();
            if (filters.market) params.append('market', filters.market);
            if (filters.type) params.append('type', filters.type);
            if (filters.stock_code) params.append('stock_code', filters.stock_code);
            if (filters.start_date) params.append('start_date', filters.start_date);
            if (filters.end_date) params.append('end_date', filters.end_date);

            const response = await fetch(`http://localhost:5000/api/transactions?${params}`);
            const data = await response.json();
            setTransactions(data.transactions || []);
            setSummary(data.summary || {});
        } catch (error) {
            console.error('獲取交易記錄失敗:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchBrokers = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/brokers?market=tw');
            const data = await response.json();
            setBrokers(data.brokers || []);
        } catch (error) {
            console.error('獲取券商列表失敗:', error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch('http://localhost:5000/api/transactions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                setShowAddForm(false);
                setFormData({
                    stock_code: '',
                    market: 'tw',
                    transaction_type: 'buy',
                    quantity: '',
                    price: '',
                    transaction_date: new Date().toISOString().split('T')[0],
                    broker: '元大證券',
                    notes: ''
                });
                fetchTransactions();
            }
        } catch (error) {
            console.error('新增交易失敗:', error);
        }
    };

    const deleteTransaction = async (id) => {
        if (!window.confirm('確定要刪除此交易記錄嗎？')) return;

        try {
            await fetch(`http://localhost:5000/api/transactions/${id}`, {
                method: 'DELETE'
            });
            fetchTransactions();
        } catch (error) {
            console.error('刪除交易失敗:', error);
        }
    };

    return (
        <div className="space-y-6">
            {/* 標題區 */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">交易日誌</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">記錄所有買賣交易 + 自動計算費用</p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={fetchTransactions}
                        className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center gap-2"
                    >
                        <RefreshCw className="w-4 h-4" />
                        刷新
                    </button>
                    <button
                        onClick={() => setShowAddForm(true)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                    >
                        <Plus className="w-4 h-4" />
                        新增交易
                    </button>
                </div>
            </div>

            {/* 統計卡片 */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600 dark:text-gray-400">買入筆數</span>
                        <TrendingUp className="w-5 h-5 text-green-600" />
                    </div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        {summary?.total_buy || 0}
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600 dark:text-gray-400">賣出筆數</span>
                        <TrendingDown className="w-5 h-5 text-red-600" />
                    </div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                        {summary?.total_sell || 0}
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border-l-4 border-orange-500">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600 dark:text-gray-400">總手續費</span>
                        <DollarSign className="w-5 h-5 text-orange-600" />
                    </div>
                    <div className="text-2xl font-bold text-orange-600">
                        ${summary?.total_fees?.toFixed(2) || 0}
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border-l-4 border-purple-500">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600 dark:text-gray-400">總稅金</span>
                        <DollarSign className="w-5 h-5 text-purple-600" />
                    </div>
                    <div className="text-2xl font-bold text-purple-600">
                        ${summary?.total_tax?.toFixed(2) || 0}
                    </div>
                </div>
            </div>

            {/* 交易記錄表格 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
                <div className="p-6">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">交易記錄</h2>

                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-50 dark:bg-gray-700">
                                <tr>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">日期</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">代碼</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">類型</th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">數量</th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">價格</th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">手續費</th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">稅金</th>
                                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">總金額</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">券商</th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">操作</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                                {transactions.map((t) => (
                                    <tr key={t.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                                            {t.transaction_date}
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap">
                                            <div className="flex items-center gap-2">
                                                <span className="text-sm font-medium text-gray-900 dark:text-white">{t.stock_code}</span>
                                                <span className={`px-2 py-1 text-xs rounded ${t.market === 'tw' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}`}>
                                                    {t.market.toUpperCase()}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap">
                                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${t.transaction_type === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                                {t.transaction_type === 'buy' ? '買入' : '賣出'}
                                            </span>
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-gray-900 dark:text-white">
                                            {t.quantity}
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-gray-900 dark:text-white">
                                            ${t.price}
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-orange-600">
                                            ${t.fees?.toFixed(2) || 0}
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm text-purple-600">
                                            ${t.tax?.toFixed(2) || 0}
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900 dark:text-white">
                                            ${t.total_amount?.toFixed(2) || 0}
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                                            {t.broker || '-'}
                                        </td>
                                        <td className="px-4 py-4 whitespace-nowrap text-sm">
                                            <button
                                                onClick={() => deleteTransaction(t.id)}
                                                className="text-red-600 hover:text-red-900"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    {transactions.length === 0 && !loading && (
                        <div className="text-center py-12">
                            <Calendar className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                            <p className="text-gray-600 dark:text-gray-400">尚無交易記錄</p>
                        </div>
                    )}
                </div>
            </div>

            {/* 新增交易表單 Modal */}
            {showAddForm && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">新增交易記錄</h3>

                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">市場</label>
                                    <select
                                        value={formData.market}
                                        onChange={(e) => setFormData({ ...formData, market: e.target.value })}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600"
                                    >
                                        <option value="tw">台股</option>
                                        <option value="us">美股</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">類型</label>
                                    <select
                                        value={formData.transaction_type}
                                        onChange={(e) => setFormData({ ...formData, transaction_type: e.target.value })}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600"
                                    >
                                        <option value="buy">買入</option>
                                        <option value="sell">賣出</option>
                                    </select>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">股票代碼</label>
                                <input
                                    type="text"
                                    value={formData.stock_code}
                                    onChange={(e) => setFormData({ ...formData, stock_code: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600"
                                    required
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">數量</label>
                                    <input
                                        type="number"
                                        value={formData.quantity}
                                        onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600"
                                        required
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">價格</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        value={formData.price}
                                        onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600"
                                        required
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">交易日期</label>
                                <input
                                    type="date"
                                    value={formData.transaction_date}
                                    onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">券商</label>
                                <select
                                    value={formData.broker}
                                    onChange={(e) => setFormData({ ...formData, broker: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600"
                                >
                                    {brokers.map((b) => (
                                        <option key={b.broker_name} value={b.broker_name}>
                                            {b.broker_name} (手續費{(b.fee_rate * b.discount * 100).toFixed(4)}%)
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">備註</label>
                                <textarea
                                    value={formData.notes}
                                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg dark:bg-gray-700 dark:border-gray-600"
                                    rows="2"
                                />
                            </div>

                            <div className="flex gap-3 pt-4">
                                <button
                                    type="submit"
                                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                >
                                    新增
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowAddForm(false)}
                                    className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                                >
                                    取消
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TransactionLog;
