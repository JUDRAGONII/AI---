import React, { useState, useEffect } from 'react';
import { Activity, BarChart3 } from 'lucide-react';
import TradingViewChart from '../components/TradingViewChart';

const TechnicalAnalysis = () => {
    const [stockCode, setStockCode] = useState('2330');
    const [market, setMarket] = useState('tw');
    const [selectedIndicators, setSelectedIndicators] = useState({ ma: true });
    const [priceData, setPriceData] = useState([]);
    const [indicatorsData, setIndicatorsData] = useState({});
    const [signals, setSignals] = useState([]);
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState(null);
    const [showIndicatorPanel, setShowIndicatorPanel] = useState(true);

    useEffect(() => {
        fetchChartData();
    }, [stockCode, market]);

    useEffect(() => {
        if (priceData.length > 0) {
            fetchIndicators();
            fetchSignals();
        }
    }, [selectedIndicators, priceData]);

    const fetchChartData = async () => {
        if (!stockCode) return;

        setLoading(true);
        try {
            const priceResponse = await fetch(`http://localhost:5000/api/prices/${stockCode}?market=${market}&days=100`);
            const priceResult = await priceResponse.json();

            if (priceResult.data && priceResult.data.length > 0) {
                const chartData = priceResult.data.map(item => ({
                    time: new Date(item.trade_date).toISOString().split('T')[0],
                    open: parseFloat(item.open_price),
                    high: parseFloat(item.high_price),
                    low: parseFloat(item.low_price),
                    close: parseFloat(item.close_price),
                    volume: parseFloat(item.volume || 0),
                }));

                setPriceData(chartData);

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
            if (selectedIndicators.ma) {
                const maResponse = await fetch(`http://localhost:5000/api/indicators/${stockCode}/ma?market=${market}&period=20`);
                const maResult = await maResponse.json();

                if (maResult.data && maResult.data.length > 0) {
                    indicators.ma = {
                        period: 20,
                        data: maResult.data.map(item => ({
                            time: new Date(item.trade_date).toISOString().split('T')[0],
                            value: parseFloat(item.ma),
                        }))
                    };
                }
            }

            if (selectedIndicators.rsi) {
                const rsiResponse = await fetch(`http://localhost:5000/api/indicators/${stockCode}/rsi?market=${market}`);
                const rsiResult = await rsiResponse.json();

                if (rsiResult.data && rsiResult.data.length > 0) {
                    indicators.rsi = {
                        data: rsiResult.data.map(item => ({
                            time: new Date(item.trade_date).toISOString().split('T')[0],
                            value: parseFloat(item.rsi),
                        }))
                    };
                }
            }

            if (selectedIndicators.macd) {
                const macdResponse = await fetch(`http://localhost:5000/api/indicators/${stockCode}/macd?market=${market}`);
                const macdResult = await macdResponse.json();

                if (macdResult.data && macdResult.data.length > 0) {
                    indicators.macd = {
                        data: macdResult.data.map(item => ({
                            time: new Date(item.trade_date).toISOString().split('T')[0],
                            value: parseFloat(item.macd),
                            signal: parseFloat(item.signal),
                            histogram: parseFloat(item.histogram)
                        }))
                    };
                }
            }

            if (selectedIndicators.bollinger) {
                const bbResponse = await fetch(`http://localhost:5000/api/indicators/${stockCode}/bollinger?market=${market}&period=20`);
                const bbResult = await bbResponse.json();

                if (bbResult.data && bbResult.data.length > 0) {
                    indicators.bollinger = {
                        data: bbResult.data.map(item => ({
                            time: new Date(item.trade_date).toISOString().split('T')[0],
                            upper: parseFloat(item.upper),
                            middle: parseFloat(item.middle),
                            lower: parseFloat(item.lower)
                        }))
                    };
                }
            }

            setIndicatorsData(indicators);
        } catch (error) {
            console.error('獲取技術指標失敗:', error);
        }
    };

    const fetchSignals = async () => {
        try {
            const response = await fetch(`http://localhost:5000/api/signals/${stockCode}?market=${market}&days=100`);
            const data = await response.json();
            setSignals(data.signals || []);
        } catch (error) {
            console.error('獲取訊號失敗:', error);
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
                                onClick={() => toggleIndicator('macd')}
                                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${selectedIndicators.macd
                                    ? 'bg-purple-600 text-white'
                                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                                    }`}
                            >
                                MACD
                            </button>
                            <button
                                onClick={() => toggleIndicator('bollinger')}
                                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${selectedIndicators.bollinger
                                    ? 'bg-cyan-600 text-white'
                                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                                    }`}
                            >
                                布林通道
                            </button>
                            <button
                                onClick={fetchChartData}
                                disabled={loading}
                                className="ml-auto px-4 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
                            >
                                <Activity className="w-4 h-4" />
                                <span>{loading ? '載入中...' : '查詢'}</span>
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

            {/* 技術指標面板 & 訊號總覽 */}
            {stats && showIndicatorPanel && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                    {/* 指標面板 */}
                    <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">📊 技術指標總覽</h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            {indicatorsData.ma && indicatorsData.ma.length > 0 && (
                                <div className="border border-blue-200 dark:border-blue-700 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3">
                                    <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">MA20</div>
                                    <div className="text-lg font-bold text-blue-600">
                                        ${indicatorsData.ma[indicatorsData.ma.length - 1]?.value?.toFixed(2) || '-'}
                                    </div>
                                </div>
                            )}
                            {indicatorsData.rsi && indicatorsData.rsi.length > 0 && (
                                <div className={`border rounded-lg p-3 ${indicatorsData.rsi[indicatorsData.rsi.length - 1]?.value >= 70
                                    ? 'border-red-200 bg-red-50 dark:border-red-700 dark:bg-red-900/20'
                                    : indicatorsData.rsi[indicatorsData.rsi.length - 1]?.value <= 30
                                        ? 'border-green-200 bg-green-50 dark:border-green-700 dark:bg-green-900/20'
                                        : 'border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800'
                                    }`}>
                                    <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">RSI</div>
                                    <div className={`text-lg font-bold ${indicatorsData.rsi[indicatorsData.rsi.length - 1]?.value >= 70 ? 'text-red-600' :
                                        indicatorsData.rsi[indicatorsData.rsi.length - 1]?.value <= 30 ? 'text-green-600' :
                                            'text-gray-900 dark:text-white'
                                        }`}>
                                        {indicatorsData.rsi[indicatorsData.rsi.length - 1]?.value?.toFixed(1) || '-'}
                                        {indicatorsData.rsi[indicatorsData.rsi.length - 1]?.value >= 70 && <span className="text-xs ml-1">(超買)</span>}
                                        {indicatorsData.rsi[indicatorsData.rsi.length - 1]?.value <= 30 && <span className="text-xs ml-1">(超賣)</span>}
                                    </div>
                                </div>
                            )}
                            {indicatorsData.macd && indicatorsData.macd.length > 0 && (
                                <div className="border border-purple-200 dark:border-purple-700 bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3">
                                    <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">MACD</div>
                                    <div className={`text-lg font-bold ${indicatorsData.macd[indicatorsData.macd.length - 1]?.value >= 0
                                        ? 'text-green-600'
                                        : 'text-red-600'
                                        }`}>
                                        {indicatorsData.macd[indicatorsData.macd.length - 1]?.value?.toFixed(2) || '-'}
                                    </div>
                                </div>
                            )}
                            {indicatorsData.bollinger && indicatorsData.bollinger.length > 0 && (
                                <div className="border border-cyan-200 dark:border-cyan-700 bg-cyan-50 dark:bg-cyan-900/20 rounded-lg p-3">
                                    <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">布林寬度</div>
                                    <div className="text-lg font-bold text-cyan-600">
                                        {((indicatorsData.bollinger[indicatorsData.bollinger.length - 1]?.upper -
                                            indicatorsData.bollinger[indicatorsData.bollinger.length - 1]?.lower) || 0).toFixed(2)}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* 訊號總覽 */}
                    <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700 rounded-lg shadow p-6 border-2 border-blue-200 dark:border-blue-700">
                        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                            <Activity className="w-5 h-5 text-blue-600" />
                            交易訊號
                        </h3>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between p-2 bg-white/50 dark:bg-gray-700/50 rounded">
                                <span className="text-sm text-gray-600 dark:text-gray-400">總訊號數</span>
                                <span className="text-xl font-bold text-gray-900 dark:text-white">{signals.length}</span>
                            </div>
                            <div className="flex items-center justify-between p-2 bg-green-50 dark:bg-green-900/20 rounded">
                                <span className="text-sm text-gray-600 dark:text-gray-400">買入訊號</span>
                                <span className="text-xl font-bold text-green-600">
                                    {signals.filter(s => s.action === 'buy').length}
                                </span>
                            </div>
                            <div className="flex items-center justify-between p-2 bg-red-50 dark:bg-red-900/20 rounded">
                                <span className="text-sm text-gray-600 dark:text-gray-400">賣出訊號</span>
                                <span className="text-xl font-bold text-red-600">
                                    {signals.filter(s => s.action === 'sell').length}
                                </span>
                            </div>
                            {signals.length > 0 && (
                                <div className="mt-4 pt-4 border-t border-gray-300 dark:border-gray-600">
                                    <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">🔔 最新訊號</div>
                                    <div className={`px-3 py-2 rounded-lg ${signals[signals.length - 1]?.action === 'buy'
                                        ? 'bg-green-100 dark:bg-green-900/30'
                                        : 'bg-red-100 dark:bg-red-900/30'
                                        }`}>
                                        <div className={`text-sm font-bold ${signals[signals.length - 1]?.action === 'buy'
                                            ? 'text-green-700 dark:text-green-400'
                                            : 'text-red-700 dark:text-red-400'
                                            }`}>
                                            {signals[signals.length - 1]?.description}
                                        </div>
                                        <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                                            📅 {signals[signals.length - 1]?.date}
                                        </div>
                                    </div>
                                </div>
                            )}
                            {signals.length === 0 && (
                                <div className="text-center py-4 text-gray-500 dark:text-gray-400 text-sm">
                                    暫無訊號
                                </div>
                            )}
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
                        signals={signals}
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
