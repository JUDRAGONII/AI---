// 智慧增強配置器 (Smart Portfolio Enhancer)
// 現有持股分析、增強型資產推薦、夏普比率優化
import { useState } from 'react'
import {
    RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    BarChart, Bar, ScatterChart, Scatter,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts'
import { Zap, TrendingUp, Shield, Award, ArrowRight } from 'lucide-react'

export default function SmartEnhancer() {
    // 當前投資組合
    const currentPortfolio = [
        { code: '2330', name: '台積電', weight: 35, factorScore: 82, sharpe: 1.2, sector: '半導體' },
        { code: '2317', name: '鴻海', weight: 20, factorScore: 65, sharpe: 0.8, sector: '電子' },
        { code: '2454', name: '聯發科', weight: 15, factorScore: 78, sharpe: 1.0, sector: '半導體' },
        { code: '2882', name: '國泰金', weight: 15, factorScore: 70, sharpe: 0.9, sector: '金融' },
        { code: '0050', name: '元大台灣50', weight: 15, factorScore: 75, sharpe: 1.1, sector: 'ETF' }
    ]

    // 當前組合分析
    const portfolioAnalysis = {
        currentSharpe: 1.08,
        targetSharpe: 1.35,
        improvement: 25.0,
        diversificationScore: 68,
        factorBalance: 72,
        riskLevel: 'moderate'
    }

    // AI推薦的增強資產
    const recommendations = [
        {
            code: '2408',
            name: '南亞科',
            score: 85,
            reason: '增強記憶體產業曝險，與現有半導體標的互補',
            expectedReturn: 12.5,
            sharpe: 1.4,
            correlationWithPortfolio: 0.65,
            suggestedWeight: 8,
            replaceTarget: '2317',
            impactOnSharpe: +0.12,
            sector: '半導體'
        },
        {
            code: '2603',
            name: '長榮',
            reason: '增加航運產業分散度，低相關性',
            score: 80,
            expectedReturn: 15.2,
            sharpe: 1.5,
            correlationWithPortfolio: 0.35,
            suggestedWeight: 10,
            replaceTarget: '部分現金',
            impactOnSharpe: +0.15,
            sector: '航運'
        },
        {
            code: '2912',
            name: '統一超',
            score: 78,
            reason: '增加防御性資產，穩定現金流',
            expectedReturn: 8.5,
            sharpe: 1.3,
            correlationWithPortfolio: 0.40,
            suggestedWeight: 7,
            replaceTarget: '2882',
            impactOnSharpe: +0.08,
            sector: '零售'
        }
    ]

    // 優化後組合比較
    const comparisonData = [
        { metric: '預期報酬', current: 10.5, enhanced: 12.8 },
        { metric: '夏普比率', current: 1.08, enhanced: 1.35 },
        { metric: '波動率', current: 15.2, enhanced: 14.5 },
        { metric: '分散度', current: 68, enhanced: 85 },
        { metric: '因子平衡', current: 72, enhanced: 88 }
    ]

    // 因子曝險雷達圖
    const factorExposure = [
        { factor: '價值', current: 65, enhanced: 75 },
        { factor: '品質', current: 80, enhanced: 85 },
        { factor: '動能', current: 70, enhanced: 80 },
        { factor: '規模', current: 75, enhanced: 72 },
        { factor: '波動', current: 60, enhanced: 68 },
        { factor: '成長', current: 78, enhanced: 82 }
    ]

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold flex items-center gap-3">
                    <Zap className="w-8 h-8 text-blue-600" />
                    智慧增強配置器
                </h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                    AI 驅動的投資組合優化 | 增強型資產推薦 | 夏普比率最大化
                </p>
            </div>

            {/* 優化潛力卡片 */}
            <div className="card bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="text-lg font-bold mb-2">優化潛力分析</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            基於 AI 分析，您的投資組合有顯著改善空間
                        </p>
                    </div>
                    <div className="text-center">
                        <div className="text-5xl font-bold text-green-600">+{portfolioAnalysis.improvement}%</div>
                        <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">夏普比率提升</div>
                    </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mt-4">
                    <div className="text-center p-3 bg-white dark:bg-gray-800 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">{portfolioAnalysis.currentSharpe}</div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">當前夏普比率</div>
                    </div>
                    <div className="flex items-center justify-center">
                        <ArrowRight className="w-8 h-8 text-green-600" />
                    </div>
                    <div className="text-center p-3 bg-white dark:bg-gray-800 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">{portfolioAnalysis.targetSharpe}</div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">優化後目標</div>
                    </div>
                </div>
            </div>

            {/* 當前組合分析 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 因子曝險分析 */}
                <div className="card">
                    <h3 className="text-xl font-bold mb-4">因子曝險比較</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <RadarChart data={factorExposure}>
                            <PolarGrid />
                            <PolarAngleAxis dataKey="factor" />
                            <PolarRadiusAxis angle={90} domain={[0, 100]} />
                            <Radar name="當前組合" dataKey="current" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                            <Radar name="優化組合" dataKey="enhanced" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                            <Legend />
                        </RadarChart>
                    </ResponsiveContainer>
                </div>

                {/* 績效指標比較 */}
                <div className="card">
                    <h3 className="text-xl font-bold mb-4">績效指標比較</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={comparisonData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="metric" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="current" fill="#94a3b8" name="當前" />
                            <Bar dataKey="enhanced" fill="#10b981" name="優化後" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* AI 推薦資產 */}
            <div className="space-y-4">
                <h3 className="text-xl font-bold flex items-center gap-2">
                    <Award className="w-6 h-6 text-blue-600" />
                    AI 推薦增強資產
                </h3>
                {recommendations.map((rec, index) => (
                    <RecommendationCard key={index} recommendation={rec} rank={index + 1} />
                ))}
            </div>

            {/* 執行計畫 */}
            <div className="card">
                <h3 className="text-xl font-bold mb-4">建議執行計畫</h3>
                <div className="space-y-3">
                    <ExecutionStep
                        step={1}
                        action="減持 2317 鴻海 10%"
                        reason="因子分數較低，拖累整體績效"
                        timing="本週"
                    />
                    <ExecutionStep
                        step={2}
                        action="新增 2408 南亞科 8%"
                        reason="增強半導體產業曝險，高夏普比率"
                        timing="下週"
                    />
                    <ExecutionStep
                        step={3}
                        action="新增 2603 長榮 10%"
                        reason="增加分散度，低相關性優質標的"
                        timing="下週"
                    />
                </div>

                <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <p className="text-sm">
                        ✅ <strong>預期效果</strong>：執行後夏普比率從 {portfolioAnalysis.currentSharpe} 提升至 {portfolioAnalysis.targetSharpe}，
                        年化報酬提升約 <strong>2.3%</strong>，同時降低波動率 <strong>0.7%</strong>
                    </p>
                </div>
            </div>
        </div>
    )
}

// 推薦卡片
function RecommendationCard({ recommendation, rank }) {
    return (
        <div className="card">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-start gap-4 flex-1">
                    <div className="w-12 h-12 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xl">
                        {rank}
                    </div>
                    <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                            <h4 className="text-xl font-bold">{recommendation.code} - {recommendation.name}</h4>
                            <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400">
                                分數 {recommendation.score}
                            </span>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                            💡 {recommendation.reason}
                        </p>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            <MetricBox label="預期報酬" value={`${recommendation.expectedReturn.toFixed(1)}%`} positive />
                            <MetricBox label="夏普比率" value={recommendation.sharpe.toFixed(2)} />
                            <MetricBox label="建議權重" value={`${recommendation.suggestedWeight}%`} />
                            <MetricBox label="夏普提升" value={`+${recommendation.impactOnSharpe.toFixed(2)}`} positive />
                        </div>

                        <div className="mt-3 p-2 bg-gray-50 dark:bg-gray-800 rounded text-sm">
                            <span className="text-gray-600 dark:text-gray-400">替代標的：</span>
                            <span className="font-medium ml-2">{recommendation.replaceTarget}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

// 指標盒
function MetricBox({ label, value, positive = false }) {
    return (
        <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded">
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{label}</div>
            <div className={`font-bold ${positive ? 'text-green-600' : ''}`}>{value}</div>
        </div>
    )
}

// 執行步驟
function ExecutionStep({ step, action, reason, timing }) {
    return (
        <div className="flex items-start gap-3 p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
            <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 flex items-center justify-center font-bold flex-shrink-0">
                {step}
            </div>
            <div className="flex-1">
                <div className="font-bold mb-1">{action}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">{reason}</div>
            </div>
            <div className="text-sm px-3 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 rounded-full">
                {timing}
            </div>
        </div>
    )
}
