// 智慧事件警報系統 (Smart Alert System)
// 價格監控、財報監控、量化指標監控
import { useState } from 'react'
import { Bell, Plus, TrendingUp, TrendingDown, Activity, Check } from 'lucide-react'

export default function SmartAlertSystem() {
    const [alerts] = useState([
        {
            id: 1,
            type: 'price',
            stock_code: '2330',
            stock_name: '台積電',
            condition: '價格跌破 MA20',
            current_value: 575,
            trigger_value: 580,
            status: 'triggered',
            created_at: '2024-11-22 14:30',
            triggered_at: '2024-11-23 09:15'
        },
        {
            id: 2,
            type: 'volume',
            stock_code: '2317',
            stock_name: '鴻海',
            condition: '成交量暴增 > 150%',
            current_value: 250000,
            trigger_value: 100000,
            status: 'triggered',
            created_at: '2024-11-20 10:00',
            triggered_at: '2024-11-23 10:30'
        },
        {
            id: 3,
            type: 'factor',
            stock_code: '0050',
            stock_name: '元大台灣50',
            condition: '總分跌破 70',
            current_value: 75.2,
            trigger_value: 70,
            status: 'active',
            created_at: '2024-11-15 16:00',
            triggered_at: null
        },
        {
            id: 4,
            type: 'price',
            stock_code: '2454',
            stock_name: '聯發科',
            condition: '價格突破 900',
            current_value: 850,
            trigger_value: 900,
            status: 'active',
            created_at: '2024-11-10 11:20',
            triggered_at: null
        }
    ])

    const triggeredAlerts = alerts.filter(a => a.status === 'triggered')
    const activeAlerts = alerts.filter(a => a.status === 'active')

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">智慧事件警報系統</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        價格監控 | 財報監控 | 量化指標監控 | AI 噪音過濾
                    </p>
                </div>

                <button className="btn btn-primary flex items-center gap-2">
                    <Plus className="w-5 h-5" />
                    新增警報
                </button>
            </div>

            {/* 統計卡片 */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="card bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/30 dark:to-red-800/30">
                    <div className="flex items-center gap-2 mb-2">
                        <Bell className="w-5 h-5 text-red-600" />
                        <h3 className="font-medium">觸發警報</h3>
                    </div>
                    <div className="text-3xl font-bold text-red-600 dark:text-red-400">
                        {triggeredAlerts.length}
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30">
                    <div className="flex items-center gap-2 mb-2">
                        <Activity className="w-5 h-5 text-blue-600" />
                        <h3 className="font-medium">監控中</h3>
                    </div>
                    <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                        {activeAlerts.length}
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/30 dark:to-green-800/30">
                    <div className="flex items-center gap-2 mb-2">
                        <Check className="w-5 h-5 text-green-600" />
                        <h3 className="font-medium">已確認</h3>
                    </div>
                    <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                        0
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/30 dark:to-purple-800/30">
                    <div className="flex items-center gap-2 mb-2">
                        <Bell className="w-5 h-5 text-purple-600" />
                        <h3 className="font-medium">總警報數</h3>
                    </div>
                    <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">
                        {alerts.length}
                    </div>
                </div>
            </div>

            {/* 觸發的警報 */}
            {triggeredAlerts.length > 0 && (
                <div className="space-y-4">
                    <h2 className="text-2xl font-bold text-red-600 dark:text-red-400">
                        ⚠️ {triggeredAlerts.length} 個警報已觸發
                    </h2>
                    {triggeredAlerts.map(alert => (
                        <AlertCard key={alert.id} alert={alert} />
                    ))}
                </div>
            )}

            {/* 監控中的警報 */}
            {activeAlerts.length > 0 && (
                <div className="space-y-4">
                    <h2 className="text-2xl font-bold">監控中的警報</h2>
                    {activeAlerts.map(alert => (
                        <AlertCard key={alert.id} alert={alert} />
                    ))}
                </div>
            )}

            {/* 警報類型說明 */}
            <div className="card bg-gray-50 dark:bg-gray-800/50">
                <h3 className="font-bold text-lg mb-4">支援的警報類型</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <AlertTypeCard
                        icon={<TrendingUp className="w-5 h-5" />}
                        title="價格警報"
                        description="突破/跌破特定價格、均線、支撐/壓力位"
                    />
                    <AlertTypeCard
                        icon={<Activity className="w-5 h-5" />}
                        title="成交量警報"
                        description="成交量暴增/暴減、異常交易偵測"
                    />
                    <AlertTypeCard
                        icon={<TrendingDown className="w-5 h-5" />}
                        title="因子警報"
                        description="因子分數變化、評級升降級"
                    />
                    <AlertTypeCard
                        icon={<Bell className="w-5 h-5" />}
                        title="財報警報"
                        description="財報公告、EPS 超預期、股息宣告"
                    />
                    <AlertTypeCard
                        icon={<Activity className="w-5 h-5" />}
                        title="技術指標警報"
                        description="RSI 超買/超賣、MACD 交叉、KD 黃金/死亡交叉"
                    />
                    <AlertTypeCard
                        icon={<Bell className="w-5 h-5" />}
                        title="新聞警報"
                        description="關鍵字匹配新聞、AI 重要度評分"
                    />
                </div>
            </div>
        </div>
    )
}

// 警報卡片
function AlertCard({ alert }) {
    const isTriggered = alert.status === 'triggered'

    const typeIcons = {
        price: <TrendingUp className="w-5 h-5" />,
        volume: <Activity className="w-5 h-5" />,
        factor: <TrendingDown className="w-5 h-5" />
    }

    const typeColors = {
        price: 'blue',
        volume: 'purple',
        factor: 'orange'
    }

    const color = typeColors[alert.type] || 'gray'

    return (
        <div className={`card ${isTriggered ? 'border-2 border-red-500 bg-red-50 dark:bg-red-900/10' : ''}`}>
            <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                    <div className={`p-2 rounded-lg bg-${color}-100 dark:bg-${color}-900/30`}>
                        {typeIcons[alert.type]}
                    </div>

                    <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-bold">{alert.stock_code} - {alert.stock_name}</h3>
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${isTriggered
                                    ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                                    : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                                }`}>
                                {isTriggered ? '已觸發' : '監控中'}
                            </span>
                        </div>

                        <div className="space-y-1 text-sm">
                            <p className="font-medium">{alert.condition}</p>
                            <div className="flex items-center gap-4 text-gray-600 dark:text-gray-400">
                                <span>當前值：<span className="font-medium">{alert.current_value}</span></span>
                                <span>觸發值：<span className="font-medium">{alert.trigger_value}</span></span>
                                <span>建立時間：{alert.created_at}</span>
                                {isTriggered && <span className="text-red-600 dark:text-red-400">觸發時間：{alert.triggered_at}</span>}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex gap-2">
                    {isTriggered && (
                        <button className="btn btn-primary text-sm">
                            確認
                        </button>
                    )}
                    <button className="btn btn-secondary text-sm">
                        詳情
                    </button>
                    <button className="btn btn-secondary text-sm">
                        刪除
                    </button>
                </div>
            </div>
        </div>
    )
}

// 警報類型卡片
function AlertTypeCard({ icon, title, description }) {
    return (
        <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
                {icon}
                <h4 className="font-medium">{title}</h4>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
        </div>
    )
}
