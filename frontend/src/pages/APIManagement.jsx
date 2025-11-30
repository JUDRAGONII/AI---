// API 與數據源管理頁面
// API 連線狀態監控、錯誤率顯示、數據延遲監控
import { useState, useEffect } from 'react'
import { Activity, CheckCircle, XCircle, Clock, AlertTriangle, RefreshCw } from 'lucide-react'

export default function APIManagement() {
    const [refreshing, setRefreshing] = useState(false)
    const [apiStatus, setApiStatus] = useState([])
    const [loading, setLoading] = useState(true)
    const [lastUpdated, setLastUpdated] = useState(null)

    useEffect(() => {
        fetchApiStatus()

        // 設置定時刷新 (每30秒)
        const interval = setInterval(fetchApiStatus, 30000)
        return () => clearInterval(interval)
    }, [])

    const fetchApiStatus = async () => {
        try {
            setRefreshing(true)
            const response = await fetch('http://localhost:5000/api/system/api-status')
            if (!response.ok) throw new Error('API request failed')

            const data = await response.json()
            setApiStatus(data.apis)
            setLastUpdated(new Date().toLocaleTimeString())
        } catch (error) {
            console.error('Failed to fetch API status:', error)
        } finally {
            setRefreshing(false)
            setLoading(false)
        }
    }

    const handleRefresh = () => {
        fetchApiStatus()
    }

    // 整體狀態統計
    const stats = {
        total: apiStatus.length,
        healthy: apiStatus.filter(api => api.status === 'healthy').length,
        warning: apiStatus.filter(api => api.status === 'warning').length,
        error: apiStatus.filter(api => api.status === 'error').length,
        avgUptime: apiStatus.length > 0
            ? (apiStatus.reduce((sum, api) => sum + api.uptime, 0) / apiStatus.length).toFixed(1)
            : 0
    }

    if (loading) {
        return (
            <div className="p-8 flex items-center justify-center h-screen">
                <div className="text-center">
                    <RefreshCw className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
                    <p className="text-gray-600 dark:text-gray-400">載入 API 狀態中...</p>
                </div>
            </div>
        )
    }

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">API 與數據源管理</h1>
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                        即時監控所有 API 連線狀態與效能指標 {lastUpdated && `(最後更新: ${lastUpdated})`}
                    </p>
                </div>

                <button
                    onClick={handleRefresh}
                    disabled={refreshing}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center gap-2 transition-colors"
                >
                    <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
                    重新整理
                </button>
            </div>

            {/* 整體狀態卡片 */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
                <StatusCard
                    label="API 總數"
                    value={stats.total}
                    icon={<Activity className="w-5 h-5" />}
                    color="blue"
                />
                <StatusCard
                    label="正常運作"
                    value={stats.healthy}
                    icon={<CheckCircle className="w-5 h-5" />}
                    color="green"
                />
                <StatusCard
                    label="警告"
                    value={stats.warning}
                    icon={<AlertTriangle className="w-5 h-5" />}
                    color="orange"
                />
                <StatusCard
                    label="錯誤"
                    value={stats.error}
                    icon={<XCircle className="w-5 h-5" />}
                    color="red"
                />
                <StatusCard
                    label="平均可用率"
                    value={`${stats.avgUptime}%`}
                    icon={<Activity className="w-5 h-5" />}
                    color="blue"
                />
            </div>

            {/* API 列表 */}
            <div className="space-y-4">
                {apiStatus.map((api, index) => (
                    <APICard key={index} api={api} />
                ))}
            </div>

            {/* 使用建議 */}
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-6">
                <h3 className="font-bold text-lg mb-3 text-blue-900 dark:text-blue-100">💡 API 使用建議</h3>
                <div className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
                    <p>✅ 定期檢查 API 狀態，確保資料來源穩定</p>
                    <p>✅ 注意速率限制，避免超出配額</p>
                    <p>✅ Gemini API (AI服務) 延遲較高（約2.5秒）屬正常現象</p>
                    <p>💡 資料庫狀態直接影響所有數據查詢速度</p>
                    <p>💡 黃金與匯率數據每日自動同步</p>
                </div>
            </div>
        </div>
    )
}

// 狀態卡片
function StatusCard({ label, value, icon, color }) {
    const colorClasses = {
        blue: 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
        green: 'bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400',
        orange: 'bg-orange-50 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400',
        red: 'bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400'
    }

    return (
        <div className={`p-6 rounded-lg shadow-sm ${colorClasses[color]}`}>
            <div className="flex items-center gap-2 mb-2">
                {icon}
                <span className="text-sm font-medium">{label}</span>
            </div>
            <div className="text-2xl font-bold">{value}</div>
        </div>
    )
}

// API 卡片
function APICard({ api }) {
    const statusConfig = {
        healthy: {
            icon: <CheckCircle className="w-5 h-5" />,
            color: 'text-green-600 dark:text-green-400',
            bg: 'bg-green-50 dark:bg-green-900/30',
            text: '正常'
        },
        warning: {
            icon: <AlertTriangle className="w-5 h-5" />,
            color: 'text-orange-600 dark:text-orange-400',
            bg: 'bg-orange-50 dark:bg-orange-900/30',
            text: '警告'
        },
        error: {
            icon: <XCircle className="w-5 h-5" />,
            color: 'text-red-600 dark:text-red-400',
            bg: 'bg-red-50 dark:bg-red-900/30',
            text: '錯誤'
        },
        unknown: {
            icon: <Activity className="w-5 h-5" />,
            color: 'text-gray-600 dark:text-gray-400',
            bg: 'bg-gray-50 dark:bg-gray-800',
            text: '未知'
        }
    }

    const status = statusConfig[api.status] || statusConfig.unknown

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${status.bg}`}>
                        {status.icon}
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white">{api.name}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{api.category}</p>
                    </div>
                </div>

                <span className={`px-3 py-1 rounded-full text-sm font-medium ${status.bg} ${status.color}`}>
                    {status.text}
                </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <MetricItem
                    label="可用率"
                    value={`${api.uptime}%`}
                    good={api.uptime >= 99}
                />
                <MetricItem
                    label="延遲"
                    value={api.status === 'error' ? 'N/A' : `${api.latency}ms`}
                    good={api.latency < 500}
                />
                <MetricItem
                    label="數據筆數/請求"
                    value={api.requestsToday}
                />
                <MetricItem
                    label="錯誤率"
                    value={`${api.errorRate}%`}
                    good={api.errorRate < 5}
                />
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                    <Clock className="w-4 h-4" />
                    <span>最後更新：{api.lastUpdate}</span>
                </div>
                <div className="text-right text-gray-600 dark:text-gray-400">
                    速率限制：{api.rateLimit}
                </div>
            </div>
        </div>
    )
}

// 指標項目
function MetricItem({ label, value, good }) {
    const colorClass = good === undefined
        ? 'text-gray-900 dark:text-white'
        : good
            ? 'text-green-600 dark:text-green-400'
            : 'text-orange-600 dark:text-orange-400'

    return (
        <div>
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{label}</div>
            <div className={`font-bold ${colorClass}`}>{value}</div>
        </div>
    )
}
