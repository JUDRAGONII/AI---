import React, { useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Play, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';

const StrategyBacktesting = () => {
    const [strategy, setStrategy] = useState({
        entry: 'rsi_oversold',
        exit: 'take_profit_10',
        period: '1y'
    });
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);

    const runBacktest = async () => {
        setLoading(true);
        // 模擬回測結果
        setTimeout(() => {
            setResults({
                total_return: 15.3,
                sharpe_ratio: 1.45,
                max_drawdown: -8.2,
                win_rate: 62.5,
                total_trades: 24,
                profitable_trades: 15,
                losing_trades: 9,
                equity_curve: Array.from({ length: 12 }, (_, i) => ({
                    month: `${i + 1}月`,
                    value: 100000 * (1 + (0.15 * i / 12) + (Math.random() - 0.5) * 0.02)
                })),
                monthly_returns: Array.from({ length: 12 }, (_, i) => ({
                    month: `${i + 1}月`,
                    return: (Math.random() - 0.3) * 5
                }))
            });
            setLoading(false);
        }, 2000);
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">策略回測實驗室</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-1">驗證交易策略的歷史績效</p>
            </div>

            {/* 策略設定 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">策略參數</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            進場條件
                        </label>
                        <select
                            value={strategy.entry}
                            onChange={(e) => setStrategy({ ...strategy, entry: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                            <option value="rsi_oversold">RSI超賣（<30）</option>
                            <option value="ma_cross">均線金叉</option>
                            <option value="breakout">突破新高</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            出場條件
                        </label>
                        <select
                            value={strategy.exit}
                            onChange={(e) => setStrategy({ ...strategy, exit: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                            <option value="take_profit_10">獲利10%出場</option>
                            <option value="stop_loss_5">停損5%出場</option>
                            <option value="rsi_overbought">RSI超買（>70）</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            回測期間
                        </label>
                        <select
                            value={strategy.period}
                            onChange={(e) => setStrategy({ ...strategy, period: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                            <option value="3m">3個月</option>
                            <option value="6m">6個月</option>
                            <option value="1y">1年</option>
                            <option value="3y">3年</option>
                        </select>
                    </div>
                </div>

                <button
                    onClick={runBacktest}
                    disabled={loading}
                    className="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                >
                    <Play className="w-4 h-4" />
                    {loading ? '回測中...' : '執行回測'}
                </button>
            </div>

            {/* 回測結果 */}
            {results && (
                <>
                    {/* 績效指標 */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <MetricCard
                            label="總報酬率"
                            value={`${results.total_return > 0 ? '+' : ''}${results.total_return.toFixed(2)}%`}
                            icon={<TrendingUp className="w-5 h-5" />}
                            color={results.total_return > 0 ? 'green' : 'red'}
                        />
                        <MetricCard
                            label="Sharpe Ratio"
                            value={results.sharpe_ratio.toFixed(2)}
                            icon={<DollarSign className="w-5 h-5" />}
                            color="blue"
                        />
                        <MetricCard
                            label="最大回撤"
                            value={`${results.max_drawdown.toFixed(2)}%`}
                            icon={<TrendingDown className="w-5 h-5" />}
                            color="red"
                        />
                        <MetricCard
                            label="勝率"
                            value={`${results.win_rate.toFixed(1)}%`}
                            icon={<TrendingUp className="w-5 h-5" />}
                            color={results.win_rate > 50 ? 'green' : 'orange'}
                        />
                    </div>

                    {/* 資金曲線 */}
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">資金曲線</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={results.equity_curve}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis dataKey="month" stroke="#9CA3AF" />
                                <YAxis stroke="#9CA3AF" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1F2937',
                                        border: 'none',
                                        borderRadius: '8px',
                                        color: '#fff'
                                    }}
                                />
                                <Legend />
                                <Line type="monotone" dataKey="value" stroke="#3B82F6" strokeWidth={2} name="資金" />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    {/* 月報酬分布 */}
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">月報酬分布</h2>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={results.monthly_returns}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis dataKey="month" stroke="#9CA3AF" />
                                <YAxis stroke="#9CA3AF" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1F2937',
                                        border: 'none',
                                        borderRadius: '8px',
                                        color: '#fff'
                                    }}
                                />
                                <Legend />
                                <Bar dataKey="return" fill="#3B82F6" name="報酬率%" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* 交易統計 */}
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">交易統計</h2>
                        <div className="grid grid-cols-3 gap-4 text-center">
                            <div>
                                <div className="text-2xl font-bold text-gray-900 dark:text-white">{results.total_trades}</div>
                                <div className="text-sm text-gray-600 dark:text-gray-400">總交易次數</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-green-600">{results.profitable_trades}</div>
                                <div className="text-sm text-gray-600 dark:text-gray-400">獲利交易</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-red-600">{results.losing_trades}</div>
                                <div className="text-sm text-gray-600 dark:text-gray-400">虧損交易</div>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

function MetricCard({ label, value, icon, color }) {
    const colorClasses = {
        green: 'bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400',
        red: 'bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400',
        blue: 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
        orange: 'bg-orange-50 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400'
    };

    return (
        <div className={`rounded-lg shadow p-4 ${colorClasses[color]}`}>
            <div className="flex items-center gap-2 mb-2">
                {icon}
                <span className="text-sm font-medium">{label}</span>
            </div>
            <div className="text-2xl font-bold">{value}</div>
        </div>
    );
}

export default StrategyBacktesting;
