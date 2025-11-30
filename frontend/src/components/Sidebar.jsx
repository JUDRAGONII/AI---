// Sidebar 側邊欄元件 - 完整31個頁面選單
import { Link, useLocation } from 'react-router-dom'
import {
    LayoutDashboard, TrendingUp, BarChart3, Users, Newspaper, Settings,
    Target, BrainCircuit, ChevronLeft, Database, Sparkles, Activity,
    Shield, Goal, MessageSquare, Search, Bell, FileText, Calendar,
    Zap, TrendingDown, Brain, Gauge, HelpCircle, Map, Crosshair,
    Compass, Swords, NotebookPen, UserCog, Key
} from 'lucide-react'

const menuItems = [
    // 核心功能
    { icon: LayoutDashboard, label: '儀表板', path: '/', category: '核心' },
    { icon: BrainCircuit, label: 'AI 洞察', path: '/ai-insights', category: '核心' },
    { icon: BarChart3, label: '因子分析', path: '/factors', category: '核心' },
    { icon: Users, label: '大戶同步率', path: '/shareholder', category: '核心' },
    { icon: TrendingUp, label: '技術分析', path: '/technical', category: '核心' },
    { icon: Target, label: '投資組合', path: '/portfolio', category: '核心' },
    { icon: Newspaper, label: '新聞中心', path: '/news', category: '核心' },

    // 投資組合進階
    { icon: Sparkles, label: '組合優化', path: '/optimization', category: '投資組合' },
    { icon: Activity, label: '組合詳情', path: '/portfolio-details', category: '投資組合' },
    { icon: Calendar, label: '交易記錄', path: '/transactions', category: '投資組合' },

    // 策略與測試
    { icon: TrendingDown, label: '策略回測', path: '/backtesting', category: '策略' },
    { icon: Shield, label: '壓力測試', path: '/stress-testing', category: '策略' },

    // AI進階功能
    { icon: Goal, label: '投資目標', path: '/goals', category: 'AI進階' },
    { icon: MessageSquare, label: 'AI 對話', path: '/ai-chat', category: 'AI進階' },
    { icon: Search, label: '相似資產', path: '/similar-assets', category: 'AI進階' },
    { icon: Bell, label: '智慧警報', path: '/alerts', category: 'AI進階' },
    { icon: Brain, label: 'AI 策略', path: '/ai-strategy', category: 'AI進階' },

    // 智慧工具
    { icon: Zap, label: '動態情報', path: '/intelligence', category: '智慧工具' },
    { icon: HelpCircle, label: '情境模擬', path: '/what-if', category: '智慧工具' },
    { icon: Gauge, label: '行為教練', path: '/behavioral-coach', category: '智慧工具' },
    { icon: Sparkles, label: '智慧增強', path: '/smart-enhancer', category: '智慧工具' },
    { icon: TrendingUp, label: '催化劑評分', path: '/catalyst-ranker', category: '智慧工具' },
    { icon: Map, label: '策略追蹤', path: '/strategy-tracker', category: '智慧工具' },
    { icon: Activity, label: '偏離熱力圖', path: '/deviation-heatmap', category: '智慧工具' },

    // 進階規劃
    { icon: Crosshair, label: '目標校準', path: '/goal-calibrator', category: '規劃' },
    { icon: Compass, label: '戰術規劃', path: '/tactical-planner', category: '規劃' },
    { icon: Swords, label: '情境對沖', path: '/scenario-hedging', category: '規劃' },
    { icon: FileText, label: '報告中心', path: '/reports', category: '規劃' },

    // 系統管理
    { icon: UserCog, label: '帳戶管理', path: '/account', category: '系統' },
    { icon: Key, label: 'API 管理', path: '/api-management', category: '系統' },
    { icon: Settings, label: '系統設定', path: '/settings', category: '系統' },
]

import { useState, useEffect } from 'react'
import { api } from '../services/api'

export default function Sidebar({ isOpen, onToggle }) {
    const location = useLocation()
    const [dbStatus, setDbStatus] = useState({
        tw: 0,
        us: 0,
        gold: 0,
        forex: 0,
        loading: true
    })

    // 分組顯示選單
    const categories = ['核心', '投資組合', '策略', 'AI進階', '智慧工具', '規劃', '系統']

    useEffect(() => {
        const fetchDbStatus = async () => {
            try {
                const response = await fetch(api.market.summary())
                const data = await response.json()
                setDbStatus({
                    tw: data.stocks?.tw_prices || 0,
                    us: data.stocks?.us_prices || 0,
                    gold: data.gold?.count || 0,
                    forex: data.forex?.count || 0,
                    loading: false
                })
            } catch (error) {
                console.error('獲取資料庫狀態失敗:', error)
                setDbStatus(prev => ({ ...prev, loading: false }))
            }
        }

        if (isOpen) {
            fetchDbStatus()
            // 每30秒更新一次
            const interval = setInterval(fetchDbStatus, 30000)
            return () => clearInterval(interval)
        }
    }, [isOpen])

    const formatCount = (count) => {
        if (count >= 1000) {
            return `${(count / 1000).toFixed(1)}K`
        }
        return count
    }

    return (
        <aside className={`
      bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700
      transition-all duration-300 ease-in-out
      ${isOpen ? 'w-64' : 'w-20'}
    `}>
            <div className="flex flex-col h-full">
                {/* Logo */}
                <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                    {isOpen && (
                        <div>
                            <h1 className="text-xl font-bold text-blue-600 dark:text-blue-400">
                                Gemini Quant
                            </h1>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                                AI 投資分析儀
                            </p>
                        </div>
                    )}
                    <button
                        onClick={onToggle}
                        className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                        <ChevronLeft className={`w-5 h-5 transition-transform ${!isOpen ? 'rotate-180' : ''}`} />
                    </button>
                </div>

                {/* Menu Items */}
                <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
                    {isOpen ? (
                        // 展開時：分類顯示
                        categories.map(category => {
                            const items = menuItems.filter(item => item.category === category)
                            return (
                                <div key={category} className="mb-4">
                                    <div className="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                        {category}
                                    </div>
                                    {items.map(item => {
                                        const Icon = item.icon
                                        const isActive = location.pathname === item.path
                                        return (
                                            <Link
                                                key={item.path}
                                                to={item.path}
                                                className={`
                          flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-sm
                          ${isActive
                                                        ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 font-medium'
                                                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                                                    }
                        `}
                                            >
                                                <Icon className="w-4 h-4 flex-shrink-0" />
                                                <span>{item.label}</span>
                                            </Link>
                                        )
                                    })}
                                </div>
                            )
                        })
                    ) : (
                        // 收起時：只顯示圖標
                        menuItems.map(item => {
                            const Icon = item.icon
                            const isActive = location.pathname === item.path
                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className={`
                      flex items-center justify-center p-3 rounded-lg transition-colors mb-1
                      ${isActive
                                            ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400'
                                            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                                        }
                    `}
                                    title={item.label}
                                >
                                    <Icon className="w-5 h-5" />
                                </Link>
                            )
                        })
                    )}
                </nav>

                {/* Footer - Database Status */}
                {isOpen && (
                    <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                        <div className="flex items-center gap-2 mb-2">
                            <Database className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                            <div className="text-xs font-medium text-gray-700 dark:text-gray-300">資料庫狀態</div>
                        </div>
                        <div className="space-y-1 text-xs text-gray-600 dark:text-gray-400">
                            <div className="flex justify-between">
                                <span>台股</span>
                                <span className="font-medium text-green-600 dark:text-green-400">
                                    {formatCount(dbStatus.tw)}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span>美股</span>
                                <span className="font-medium text-green-600 dark:text-green-400">
                                    {formatCount(dbStatus.us)}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span>黃金</span>
                                <span className="font-medium text-green-600 dark:text-green-400">
                                    {formatCount(dbStatus.gold)}
                                </span>
                            </div>
                            <div className="flex justify-between">
                                <span>匯率</span>
                                <span className="font-medium text-green-600 dark:text-green-400">
                                    {formatCount(dbStatus.forex)}
                                </span>
                            </div>
                        </div>
                        <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                            <div className="flex items-center gap-1">
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                <span className="text-xs text-gray-500 dark:text-gray-400">
                                    {dbStatus.loading ? '更新中...' : '同步進行中'}
                                </span>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </aside>
    )
}
