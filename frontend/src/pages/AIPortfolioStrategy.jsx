import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, DollarSign, PieChart as PieIcon } from 'lucide-react';

const AIPortfolioStrategy = () => {
    const [strategy, setStrategy] = useState(null);
    const [loading, setLoading] = useState(false);
    const [riskProfile, setRiskProfile] = useState('moderate');

    const fetchStrategy = async () => {
        setLoading(true);
        // 模擬AI策略（未來連接Gemini API）
        setTimeout(() => {
            setStrategy({
                asset_allocation: [
                    { asset: '台股', current: 45, target: 40, action: '減持' },
                    { asset: '美股', current: 30, target: 35, action: '增持' },
                    { asset: '債券', current: 15, target: 15, action: '維持' },
                    { asset: '現金', current: 10, target: 10, action: '維持' }
                ],
                recommendations: [
                    { symbol: '2330', action: '減持', reason: '估值偏高，建議減碼20%', priority: 'high' },
                    { symbol: 'AAPL', action: '增持', reason: 'AI產品線強勁，建議加碼10%', priority: 'medium' },
                    { symbol: 'MSFT', action: '持有', reason: '雲端業務穩健成長', priority: 'low' }
                ]
            });
            setLoading(false);
        }, 1500);
    };

    useEffect(() => {
        fetchStrategy();
    }, [riskProfile]);

    const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#6b7280'];

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AI投資組合策略</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-1">基於風險屬性的智能資產配置建議</p>
            </div>

            {/* 風險屬性選擇 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                    風險屬性
                </label>
                <div className="flex gap-3">
                    {['conservative', 'moderate', 'aggressive'].map(profile => (
                        <button
                            key={profile}
                            onClick={() => setRiskProfile(profile)}
                            className={`px-4 py-2 rounded-lg ${riskProfile === profile
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                                }`}
                        >
                            {profile === 'conservative' ? '保守' : profile === 'moderate' ? '穩健' : '積極'}
                        </button>
                    ))}
                </div>
            </div>

            {loading ? (
                <div className="flex items-center justify-center h-64">
                    <div className="text-gray-400">AI分析中...</div>
                </div>
            ) : strategy && (
                <>
                    {/* 資產配置建議 */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                                <PieIcon className="w-5 h-5" />
                                資產配置調整建議
                            </h2>
                            <div className="space-y-3">
                                {strategy.asset_allocation.map(item => (
                                    <div key={item.asset} className="flex items-center justify-between">
                                        <span className="text-sm font-medium">{item.asset}</span>
                                        <div className="flex items-center gap-3">
                                            <span className="text-sm text-gray-600 dark:text-gray-400">
                                                {item.current}% → {item.target}%
                                            </span>
                                            <span className={`px-2 py-1 rounded text-xs font-medium ${item.action === '增持' ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300' :
                                                    item.action === '減持' ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300' :
                                                        'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                                                }`}>
                                                {item.action}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">目標配置圖</h2>
                            <ResponsiveContainer width="100%" height={250}>
                                <PieChart>
                                    <Pie
                                        data={strategy.asset_allocation}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={false}
                                        label={({ asset, target }) => `${asset} ${target}%`}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        dataKey="target"
                                    >
                                        {strategy.asset_allocation.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* 個股建議 */}
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                            <TrendingUp className="w-5 h-5" />
                            個股操作建議
                        </h2>
                        <div className="space-y-4">
                            {strategy.recommendations.map((rec, idx) => (
                                <div key={idx} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center gap-3">
                                            <span className="text-lg font-bold">{rec.symbol}</span>
                                            <span className={`px-2 py-1 rounded text-xs font-medium ${rec.action === '增持' ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300' :
                                                    rec.action === '減持' ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300' :
                                                        'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                                                }`}>
                                                {rec.action}
                                            </span>
                                        </div>
                                        <span className={`text-xs px-2 py-1 rounded ${rec.priority === 'high' ? 'bg-red-100 text-red-700' :
                                                rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                                    'bg-gray-100 text-gray-700'
                                            }`}>
                                            {rec.priority === 'high' ? '高優先' : rec.priority === 'medium' ? '中優先' : '低優先'}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">{rec.reason}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* AI說明 */}
                    <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                        <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">💡 AI策略說明</h3>
                        <p className="text-sm text-blue-800 dark:text-blue-400">
                            此策略基於您的<strong>{riskProfile === 'conservative' ? '保守' : riskProfile === 'moderate' ? '穩健' : '積極'}</strong>風險屬性，
                            結合當前市場環境、技術指標和估值分析生成。建議定期（每月）重新評估並調整策略。
                        </p>
                    </div>
                </>
            )}
        </div>
    );
};

export default AIPortfolioStrategy;
