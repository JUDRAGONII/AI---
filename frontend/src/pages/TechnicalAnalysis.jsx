import React, { useState, useEffect } from 'react';
import { TrendingUp, Activity, BarChart3 } from 'lucide-react';
import TradingViewChart from '../components/TradingViewChart';

const TechnicalAnalysis = () => {
    const [stockCode, setStockCode] = useState('2330');
    const [market, setMarket] = useState('tw');
    const [selectedIndicators, setSelectedIndicators] = useState({ ma: true });
    const [priceData, setPriceData] = useState([]);
    const [indicatorsData, setIndicatorsData] = useState({});
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState(null);

    useEffect(() => {
        fetchChartData();
    }, [stockCode, market]);

    useEffect(() => {
        if (priceData.length > 0) {
            fetchIndicators();
        }
    }, [selectedIndicators, priceData]);

    const fetchChartData = async () => {
        if (!stockCode) return;

        setLoading(true);
        try {
            // 獲取價格數據
            const priceResponse = await fetch(`http://localhost:5000/api/prices/${stockCode}?market=${market}&limit=100`);
            const priceResult = await priceResponse.json();

            if (priceResult.prices && priceResult.prices.length > 0) {
                const chartData = priceResult.prices.map(item => ({
                    time: item.trade_date,
                    open: parseFloat(item.open_price),
                    high: parseFloat(item.high_price),
                    low: parseFloat(item.low_price),
                    close: parseFloat(item.close_price),
                    volume: parseFloat(item.volume || 0),
                })).reverse();

                setPriceData(chartData);

                // 計算統計
                if (chartData.length > 0) {
                    const closes = chartData.map(d => d.close);
                    setStats({
                        current: closes[closes.length - 1],
                        max: Math.max(...closes),
                        min: Math.min(...closes),
                        avg: closes.reduce((a, b) => a + b, 0) / closes.length
                    });
                }
            }
        } catch (error) {
            console.error('獲取價格數據失敗:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchIndicators = async () => {
        const indicators = {};

        try {
            // 獲取 MA 數據
            if (selectedIndicators.ma) {
                const maResponse = await fetch(`http://localhost:5000/api/indicators/${stockCode}/ma?market=${market}&period=20`);
                const maResult = await maResponse.json();

                if (maResult.data && maResult.data.length > 0) {
                    indicators.ma = {
                        period: 20,
                        data: maResult.data.map(item => ({
                            time: item.trade_date,
                            value: parseFloat(item.ma),
                        })).reverse()
                    };
                }
            }

            // 獲取 RSI 數據
            if (selectedIndicators.rsi) {
                const rsiResponse = await fetch(`http://localhost:5000/api/indicators/${stockCode}/rsi?market=${market}`);
                const rsiResult = await rsiResponse.json();

                if (rsiResult.data && rsiResult.data.length > 0) {
                    indicators.rsi = {
                        data: rsiResult.data.map(item => ({
                            time: item.trade_date,
                            value: parseFloat(item.rsi),
                        })).reverse()
                    };
                }
            }

            setIndicatorsData(indicators);
        } catch (error) {
            console.error('獲取技術指標失敗:', error);
        }
    };

    const toggleIndicator = (indicator) => {
        setSelectedIndicators(prev => ({
            ...prev,
            [indicator]: !prev[indicator]
        }));
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">技術分析中心</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-1">專業級 K 線圖與技術指標分析</p>
            </div>

            {/* 控制面板 */}
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

                    <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            技術指標
                        </label>
                        <div className="flex gap-2 flex-wrap">
                            <button
                                onClick={() => toggleIndicator('ma')}
                                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${selectedIndicators.ma
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                                    }`}
                            >
                                MA(20)
                            </button>
                            <button
                                onClick={() => toggleIndicator('rsi')}
                                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${selectedIndicators.rsi
                                    ? 'bg-orange-600 text-white'
                                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                                    }`}
                            >
                                RSI
                            </button>
                            <button
                                onClick={fetchChartData}
                                disabled={loading}
                                className="ml-auto px-4 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                            >
                                <Activity className="w-4 h-4" />
                                <span>{loading ? '載入中...' : '刷新'}</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* 統計卡片 */}
            {stats && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">當前價格</div>
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                            ${stats.current.toFixed(2)}
                        </div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">最高價</div>
                        <div className="text-2xl font-bold text-red-600">
                            ${stats.max.toFixed(2)}
                        </div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">最低價</div>
                        <div className="text-2xl font-bold text-green-600">
                            ${stats.min.toFixed(2)}
                        </div>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">平均價</div>
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                            ${stats.avg.toFixed(2)}
                        </div>
                    </div>
                </div>
            )}

            {/* K 線圖表 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <BarChart3 className="w-6 h-6 text-blue-600" />
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                            {stockCode} K 線圖
                        </h2>
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                        近 100 個交易日
                    </div>
                </div>

                {loading ? (
                    <div className="flex items-center justify-center h-[500px]">
                        <div className="text-center">
                            <Activity className="w-16 h-16 mx-auto mb-4 text-blue-600 animate-pulse" />
                            <p className="text-gray-600 dark:text-gray-400">載入圖表數據中...</p>
                        </div>
                    </div>
                ) : priceData.length > 0 ? (
                    <TradingViewChart
                        data={priceData}
                        indicators={indicatorsData}
                        height={500}
                    />
                ) : (
                    <div className="flex items-center justify-center h-[500px] text-gray-500">
                        請輸入股票代碼並點擊查詢
                    </div>
                )}
            </div>

            {/* 使用說明 */}
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">💡 操作提示</h3>
                <ul className="space-y-1 text-sm text-blue-800 dark:text-blue-400">
                    <li>• 使用滑鼠滾輪縮放圖表</li>
                    <li>• 按住滑鼠左鍵拖動可平移圖表</li>
                    <li>• 點擊技術指標按鈕可切換顯示</li>
                    <li>• 游標移動到圖表上可查看詳細數值</li>
                </ul>
            </div>
        </div>
    );
};

export default TechnicalAnalysis;
