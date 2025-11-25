// Error Boundary 組件 - 捕獲並優雅處理React組件錯誤
import React from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props)
        this.state = { hasError: false, error: null, errorInfo: null }
    }

    static getDerivedStateFromError(error) {
        // 更新狀態以顯示錯誤UI
        return { hasError: true }
    }

    componentDidCatch(error, errorInfo) {
        // 記錄錯誤到控制台（在生產環境可以發送到錯誤追蹤服務）
        console.error('Error Boundary 捕獲錯誤:', error, errorInfo)
        this.setState({
            error,
            errorInfo
        })
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null, errorInfo: null })
    }

    handleGoHome = () => {
        window.location.href = '/'
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
                    <div className="max-w-2xl w-full">
                        {/* 錯誤卡片 */}
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 border border-gray-200 dark:border-gray-700">
                            {/* 圖標與標題 */}
                            <div className="flex items-center gap-4 mb-6">
                                <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-full">
                                    <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400" />
                                </div>
                                <div>
                                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                                        糟糕！出現了一些問題
                                    </h1>
                                    <p className="text-gray-600 dark:text-gray-400 mt-1">
                                        我們的系統遇到了意外錯誤
                                    </p>
                                </div>
                            </div>

                            {/* 錯誤描述 */}
                            <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
                                <p className="text-sm text-gray-700 dark:text-gray-300 font-medium mb-2">
                                    錯誤訊息：
                                </p>
                                <p className="text-sm text-red-600 dark:text-red-400 font-mono">
                                    {this.state.error && this.state.error.toString()}
                                </p>
                            </div>

                            {/* 建議操作 */}
                            <div className="mb-6">
                                <h3 className="font-medium text-gray-900 dark:text-white mb-3">
                                    您可以嘗試：
                                </h3>
                                <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                                    <li className="flex items-start gap-2">
                                        <span className="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                                        <span>重新載入頁面以恢復正常</span>
                                    </li>
                                    <li className="flex items-start gap-2">
                                        <span className="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                                        <span>返回首頁重新開始</span>
                                    </li>
                                    <li className="flex items-start gap-2">
                                        <span className="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                                        <span>清除瀏覽器快取後重試</span>
                                    </li>
                                    <li className="flex items-start gap-2">
                                        <span className="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                                        <span>如果問題持續，請聯繫技術支援</span>
                                    </li>
                                </ul>
                            </div>

                            {/* 操作按鈕 */}
                            <div className="flex gap-3">
                                <button
                                    onClick={this.handleReset}
                                    className="btn btn-primary flex items-center gap-2"
                                >
                                    <RefreshCw className="w-4 h-4" />
                                    重新載入
                                </button>
                                <button
                                    onClick={this.handleGoHome}
                                    className="btn btn-secondary flex items-center gap-2"
                                >
                                    <Home className="w-4 h-4" />
                                    返回首頁
                                </button>
                            </div>

                            {/* 開發模式：顯示詳細錯誤堆疊 */}
                            {import.meta.env.DEV && this.state.errorInfo && (
                                <details className="mt-6">
                                    <summary className="cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400">
                                        顯示技術細節（開發模式）
                                    </summary>
                                    <div className="mt-3 p-4 bg-gray-900 dark:bg-black rounded-lg overflow-auto max-h-96">
                                        <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap">
                                            {this.state.errorInfo.componentStack}
                                        </pre>
                                    </div>
                                </details>
                            )}
                        </div>

                        {/* 底部提示 */}
                        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
                            錯誤已自動記錄，我們會盡快修復此問題
                        </p>
                    </div>
                </div>
            )
        }

        return this.props.children
    }
}

export default ErrorBoundary
