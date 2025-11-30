import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, Activity, AlertCircle, Brain, Eye } from 'lucide-react';

const Dashboard = () => {
    const [marketData, setMarketData] = useState(null);
    const [aiInsights] = useState({
        sentiment: 'neutral',
        marketView: '當前市場處於盤整階段，台股受半導體產業影響，美股科技股表現強勁。建議觀望為主。',
        keyPoints: [
            '台積電(2330)技術指標RSI=43.75，處於中性區間',
            '美股科技股持續強勢，AAPL突破新高',
            '黃金價格波動加劇，建議關注避險需求',
            '美元台幣匯率穩定，外資動向值得觀察'
        ],
        recommendations: [
            { type: 'buy', symbol: 'MSFT', reason: '雲端業務成長強勁' },
            { type: 'hold', symbol: '2330', reason: 'AI晶片需求持續' },
            { type: 'watch', symbol: 'GOLD', reason: '關注地緣政治風險' }
        ],
        lastUpdated: new Date().toLocaleString('zh-TW')
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const marketResponse = await fetch('http://localhost:5000/api/market/summary');
            const marketResult = await marketResponse.json();
            setMarketData(marketResult);
            setLoading(false);
        } catch (error) {
            console.error('獲取儀表板數據失敗:', error);
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <Activity className="w-16 h-16 mx-auto mb-4 text-blue-600 animate-pulse" />
                    <p className="text-gray-600 dark:text-gray-400">載入市場數據中...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* 頁面標題 */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">投資指揮中心</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">市場總覽 + AI 智能觀點 + 持股追蹤</p>
                </div>
                <button
                    onClick={fetchDashboardData}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                >
                    <Activity className="w-4 h-4" />
                    刷新數據
                </button>
            </div>

            {/* AI 智能觀點區塊 */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
                <div className="flex items-center gap-3 mb-4">
                    <Brain className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">AI 戰略觀點摘要</h2>
                    <span className={`ml-auto px-3 py-1 rounded-full text-sm font-medium ${aiInsights?.sentiment === 'bullish' ? 'bg-green-100 text-green-700' :
                        aiInsights?.sentiment === 'bearish' ? 'bg-red-100 text-red-700' :
                            'bg-gray-100 text-gray-700'
                        }`}>
                        {aiInsights?.sentiment === 'bullish' ? '看多' : aiInsights?.sentiment === 'bearish' ? '看空' : '中性'}
                    </span>
                </div>

                <p className="text-gray-700 dark:text-gray-300 mb-4 text-lg">💡 {aiInsights?.marketView}</p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-3">關鍵洞察</h3>
                        <ul className="space-y-2">
                            {aiInsights?.keyPoints.map((point, idx) => (
                                <li key={idx} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400">
                                    <span className="text-blue-600 mt-1">•</span>
                                    <span>{point}</span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-3">AI 操作建議</h3>
                        <div className="space-y-2">
                            {aiInsights?.recommendations.map((rec, idx) => (
                                <div key={idx} className="flex items-center justify-between p-2 bg-white dark:bg-gray-800 rounded-lg">
                                    <div className="flex items-center gap-2">
                                        <span className={`px-2 py-1 rounded text-xs font-medium ${rec.type === 'buy' ? 'bg-green-100 text-green-700' :
                                            rec.type === 'sell' ? 'bg-red-100 text-red-700' :
                                                'bg-yellow-100 text-yellow-700'
                                            }`}>
                                            {rec.type === 'buy' ? '買入' : rec.type === 'sell' ? '賣出' : '觀察'}
                                        </span>
                                        <span className="font-semibold text-sm">{rec.symbol}</span>
                                    </div>
                                    <span className="text-xs text-gray-600 dark:text-gray-400">{rec.reason}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="mt-4 text-xs text-gray-500 dark:text-gray-400 text-right">
                    最後更新：{aiInsights?.lastUpdated}
                </div>
            </div>

            {/* 市場關鍵指數 (包含美股四大指數) */}
            <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">市場關鍵指數</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
                    <MarketCard title="台股加權" value="17,234" change="+0.45%" trend="up" icon={<TrendingUp className="w-4 h-4" />} />
                    <MarketCard title="S&P 500" value="4,567" change="+0.32%" trend="up" icon={<TrendingUp className="w-4 h-4" />} />
                    <MarketCard title="Dow Jones" value="35,428" change="+0.18%" trend="up" icon={<TrendingUp className="w-4 h-4" />} />
                    <MarketCard title="NASDAQ" value="14,123" change="+0.56%" trend="up" icon={<TrendingUp className="w-4 h-4" />} />
                    <MarketCard title="Russell 2000" value="1,789" change="-0.12%" trend="down" icon={<TrendingDown className="w-4 h-4" />} />
                    <MarketCard title="黃金" value={marketData?.gold_price ? `$${marketData.gold_price.toFixed(2)}` : 'N/A'} change="+1.2%" trend="up" icon={<DollarSign className="w-4 h-4" />} />
                    <MarketCard title="USD/TWD" value={marketData?.latest_forex_rate ? marketData.latest_forex_rate.toFixed(2) : 'N/A'} change="-0.1%" trend="down" icon={<Activity className="w-4 h-4" />} />
                    <MarketCard title="VIX" value="15.8" change="-2.3%" trend="down" icon={<AlertCircle className="w-4 h-4" />} />
                </div>
            </div>

            {/* 投資組合總覽 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">投資組合總覽</h3>
                    <Eye className="w-5 h-5 text-gray-400" />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">總資產</div>
                        <div className="text-2xl font-bold">$1,650,000</div>
                    </div>
                    <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">總成本</div>
                        <div className="text-2xl font-bold">$1,580,000</div>
                    </div>
                    <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">總損益</div>
                        <div className="text-2xl font-bold text-green-600">+$70,000</div>
                    </div>
                    <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">報酬率</div>
                        <div className="text-2xl font-bold text-green-600">+4.43%</div>
                    </div>
                </div>
            </div>

            {/* 持股觀察清單 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">持股觀察清單</h3>
                <div className="space-y-3">
                    {[
                        { code: '2330', name: '台積電', price: 580, change: +1.2, value: 580000, weight: 35.2 },
                        { code: 'AAPL', name: 'Apple Inc.', price: 189.5, change: +0.8, value: 378000, weight: 22.9 },
                        { code: '2454', name: '聯發科', price: 880, change: -0.3, value: 264000, weight: 16.0 }
                    ].map((stock) => (
                        <div key={stock.code} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors">
                            <div>
                                <div className="font-bold">{stock.code}</div>
                                <div className="text-sm text-gray-600 dark:text-gray-400">{stock.name}</div>
                            </div>
                            <div className="flex items-center gap-6">
                                <div className="text-right">
                                    <div className="font-semibold">${stock.price}</div>
                                    <div className={`text-sm ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {stock.change >= 0 ? '+' : ''}{stock.change}%
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-sm text-gray-600 dark:text-gray-400">市值</div>
                                    <div className="font-semibold">${stock.value.toLocaleString()}</div>
                                </div>
                                <div className="text-sm text-gray-600 dark:text-gray-400">{stock.weight}%</div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 市場數據統計 - 含黃金與匯率 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* 台股數據統計 */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">台股數據統計</h3>
                    <div className="space-y-3">
                        <StatItem label="追蹤股票數" value={marketData?.stocks?.tw || 138} />
                        <StatItem label="價格數據筆數" value={marketData?.stocks?.tw_prices || 30544} />
                        <StatItem label="最新更新" value="2025-11-30" />
                    </div>
                </div>

                {/* 美股數據統計 */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">美股數據統計</h3>
                    <div className="space-y-3">
                        <StatItem label="追蹤股票數" value={marketData?.stocks?.us || 100} />
                        <StatItem label="價格數據筆數" value={marketData?.stocks?.us_prices || 25001} />
                        <StatItem label="最新更新" value="2025-11-30" />
                    </div>
                </div>

                {/* 黃金數據統計 */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border-l-4 border-yellow-500">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                        <DollarSign className="w-5 h-5 text-yellow-500" />
                        黃金數據統計
                    </h3>
                    <div className="space-y-3">
                        <StatItem
                            label="當前價格"
                            value={marketData?.gold?.price ? `$${marketData.gold.price.toFixed(2)}` : 'N/A'}
                        />
                        <StatItem label="數據筆數" value={marketData?.gold?.count || 251} />
                        <StatItem label="數據來源" value="yfinance" />
                    </div>
                </div>

                {/* 匯率數據統計 */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border-l-4 border-blue-500">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-blue-500" />
                        匯率數據統計
                    </h3>
                    <div className="space-y-3">
                        <StatItem
                            label="USD/TWD"
                            value={marketData?.forex?.usd_twd ? marketData.forex.usd_twd.toFixed(2) : 'N/A'}
                        />
                        <StatItem label="追蹤貨幣對" value={marketData?.forex?.pairs || '5對'} />
                        <StatItem label="數據筆數" value={marketData?.forex?.count || 665} />
                    </div>
                </div>
            </div>
        </div>
    );
};

function MarketCard({ title, value, change, trend, icon }) {
    return (
        <div className={`rounded-lg shadow p-3 ${trend === 'up' ? 'bg-green-50 dark:bg-green-900/20 border border-green-200' :
            trend === 'down' ? 'bg-red-50 dark:bg-red-900/20 border border-red-200' :
                'bg-gray-50 dark:bg-gray-800 border border-gray-200'
            }`}>
            <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-medium text-gray-600 dark:text-gray-400">{title}</span>
                <span className={trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'}>
                    {icon}
                </span>
            </div>
            <div className="text-lg font-bold mb-1">{value}</div>
            <div className={`text-xs font-medium ${trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'}`}>
                {change}
            </div>
        </div>
    );
}

function StatItem({ label, value }) {
    return (
        <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
            <span className="text-lg font-semibold">{value}</span>
        </div>
    );
}

export default Dashboard;
