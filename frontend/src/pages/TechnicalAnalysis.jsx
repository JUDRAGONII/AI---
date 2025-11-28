import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Activity } from 'lucide-react';

const TechnicalAnalysis = () => {
    const [stockCode, setStockCode] = useState('2330');
    const [market, setMarket] = useState('tw');
    const [indicator, setIndicator] = useState('rsi');
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState(null);

    useEffect(() => {
        fetchIndicatorData();
    }, [stockCode, market, indicator]);

    const fetchIndicatorData = async () => {
        if (!stockCode) return;

        setLoading(true);
        try {
            const response = await fetch(`http://localhost:5000/api/indicators/${stockCode}/${indicator}?market=${market}`);
            const result = await response.json();

            if (result.data) {
                const chartData = result.data.reverse().map(item => ({
                    date: new Date(item.trade_date).toLocaleDateString('zh-TW', { month: '2-digit', day: '2-digit' }),
                    value: indicator === 'rsi' ? item.rsi :
                        indicator === 'ma' ? item.ma :
                            item.close_price,
                    close: parseFloat(item.close_price),
                    ...(indicator === 'macd' && {
                        macd: item.macd,
                        signal: item.signal,
                        histogram: item.histogram
                    }),
                    ...(indicator === 'bollinger' && {
                        upper: item.upper,
                        middle: item.middle,
                        lower: item.lower
                    })
                }));

                setData(chartData);

                if (chartData.length > 0) {
                    const values = chartData.map(d => d.value).filter(v => v != null);
                    setStats({
                        current: values[values.length - 1],
                        max: Math.max(...values),
                        min: Math.min(...values),
                        avg: values.reduce((a, b) => a + b, 0) / values.length
                    });
                }
            }
        } catch (error) {
            console.error('獲取技術指標失敗:', error);
        } finally {
            setLoading(false);
        }
    };

    const getIndicatorName = () => {
        const names = {
            rsi: 'RSI (相對強弱指標)',
            ma: 'MA (移動平均線)',
            macd: 'MACD',
            bollinger: 'Bollinger Bands (布林通道)'
        };
        return names[indicator] || indicator;
    };

    const getIndicatorColor = (value) => {
        if (indicator === 'rsi') {
            if (value > 70) return 'text-red-600';
            if (value < 30) return 'text-green-600';
            return 'text-gray-900 dark:text-white';
        }
        return 'text-gray-900 dark:text-white';
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">技術分析中心</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-1">即時技術指標計算與圖表展示</p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            股票代碼
                        </label>
                        <input
                            type="text"
                            value={stockCode}
                            onChange={(e) => setStockCode(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                            placeholder="輸入代碼"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            市場
                        </label>
                        <select
                            value={market}
                            onChange={(e) => setMarket(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                            <option value="tw">台股</option>
                            <option value="us">美股</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            技術指標
                        </label>
                        <select
                            value={indicator}
                            onChange={(e) => setIndicator(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                            <option value="rsi">RSI</option>
                            <option value="ma">移動平均線</option>
                            <option value="macd">MACD</option>
                            <option value="bollinger">布林通道</option>
                        </select>
                    </div>

                    <div className="flex items-end">
                        <button
                            onClick={fetchIndicatorData}
                            disabled={loading}
                            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center space-x-2"
                        >
                            <Activity className="w-4 h-4" />
                            <span>{loading ? '載入中...' : '查詢'}</span>
                        </button>
                    </div>
                </div>
            </div>

            {stats && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">當前值</div>
                        <div className={`text-2xl font-bold ${getIndicatorColor(stats.current)}`}>
                            {stats.current?.toFixed(2)}
                        </div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">最高</div>
                        <div className="text-2xl font-bold text-green-600">
                            {stats.max?.toFixed(2)}
                        </div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">最低</div>
                        <div className="text-2xl font-bold text-red-600">
                            {stats.min?.toFixed(2)}
                        </div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">平均</div>
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                            {stats.avg?.toFixed(2)}
                        </div>
                    </div>
                </div>
            )}

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                    {stockCode} - {getIndicatorName()}
                </h2>

                {loading ? (
                    <div className="flex items-center justify-center h-96">
                        <div className="text-gray-400">載入中...</div>
                    </div>
                ) : data.length > 0 ? (
                    <ResponsiveContainer width="100%" height={400}>
                        {indicator === 'rsi' ? (
                            <LineChart data={data}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis dataKey="date" stroke="#9CA3AF" />
                                <YAxis stroke="#9CA3AF" domain={[0, 100]} />
                                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px', color: '#fff' }} />
                                <Legend />
                                <Line type="monotone" dataKey="value" stroke="#3B82F6" strokeWidth={2} name="RSI" dot={false} />
                                <Line type="monotone" dataKey={() => 70} stroke="#EF4444" strokeWidth={1} strokeDasharray="5 5" name="超買區" />
                                <Line type="monotone" dataKey={() => 30} stroke="#10B981" strokeWidth={1} strokeDasharray="5 5" name="超賣區" />
                            </LineChart>
                        ) : indicator === 'bollinger' ? (
                            <LineChart data={data}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis dataKey="date" stroke="#9CA3AF" />
                                <YAxis stroke="#9CA3AF" />
                                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px', color: '#fff' }} />
                                <Legend />
                                <Line type="monotone" dataKey="upper" stroke="#EF4444" strokeWidth={1} name="上軌" dot={false} />
                                <Line type="monotone" dataKey="middle" stroke="#3B82F6" strokeWidth={2} name="中軌" dot={false} />
                                <Line type="monotone" dataKey="lower" stroke="#10B981" strokeWidth={1} name="下軌" dot={false} />
                                <Line type="monotone" dataKey="close" stroke="#F59E0B" strokeWidth={2} name="收盤價" dot={false} />
                            </LineChart>
                        ) : (
                            <LineChart data={data}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis dataKey="date" stroke="#9CA3AF" />
                                <YAxis stroke="#9CA3AF" />
                                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px', color: '#fff' }} />
                                <Legend />
                                <Line type="monotone" dataKey="value" stroke="#3B82F6" strokeWidth={2} name={getIndicatorName()} dot={false} />
                                <Line type="monotone" dataKey="close" stroke="#9CA3AF" strokeWidth={1} name="收盤價" dot={false} />
                            </LineChart>
                        )}
                    </ResponsiveContainer>
                ) : (
                    <div className="flex items-center justify-center h-96">
                        <div className="text-center text-gray-500">
                            <Activity className="w-16 h-16 mx-auto mb-4 opacity-50" />
                            <p>請輸入股票代碼並選擇指標</p>
                        </div>
                    </div>
                )}
            </div>

            {indicator === 'rsi' && data.length > 0 && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                    <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">RSI 指標說明</h3>
                    <ul className="text-sm text-blue-800 dark:text-blue-400 space-y-1">
                        <li>• RSI {'>'} 70：超買區域，可能面臨回調壓力</li>
                        <li>• RSI {'<'} 30：超賣區域，可能出現反彈機會</li>
                        <li>• RSI 50 附近：多空平衡區域</li>
                    </ul>
                </div>
            )}
        </div>
    );
};

export default TechnicalAnalysis;
