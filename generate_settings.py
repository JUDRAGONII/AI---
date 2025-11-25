# 生成正確的Settings.jsx檔案
import os

settings_content = '''// 系統設定頁面 (Settings)
// 通知設定、主題切換、技術指標參數調整、API金鑰配置
import { useState, useEffect } from 'react'
import { Bell, Moon, Sun, TrendingUp, Key } from 'lucide-react'

export default function Settings() {
    const [darkMode, setDarkMode] = useState(() => {
        return document.documentElement.classList.contains('dark')
    })

    const [notifications, setNotifications] = useState({
        priceAlert: true,
        reportReady: true,
        portfolioUpdate: false,
        newsAlert: true
    })

    const [technicalParams, setTechnicalParams] = useState({
        ma5: 5,
        ma20: 20,
        ma60: 60,
        rsiPeriod: 14,
        macdFast: 12,
        macdSlow: 26,
        macdSignal: 9
    })

    const [apiKeys, setApiKeys] = useState({
        gemini: '',
        supabaseUrl: '',
        supabaseKey: '',
        n8nWebhook: '',
        fred: '',
        alphaVantage: '',
        tiingo: ''
    })

    const [syncStatus, setSyncStatus] = useState({ syncing: false, message: '', type: '' })

    useEffect(() => {
        const handleDarkModeChange = (e) => {
            setDarkMode(e.detail)
        }
        window.addEventListener('darkModeChange', handleDarkModeChange)
        return () => window.removeEventListener('darkModeChange', handleDarkModeChange)
    }, [])

    useEffect(() => {
        const saved = localStorage.getItem('apiKeys')
        if (saved) {
            try {
                setApiKeys(prev => ({ ...prev, ...JSON.parse(saved) }))
            } catch (e) {
                console.error('載入API金鑰失敗:', e)
            }
        }
    }, [])

    const handleNotificationToggle = (key) => {
        setNotifications(prev => ({ ...prev, [key]: !prev[key] }))
    }

    const handleParamChange = (key, value) => {
        setTechnicalParams(prev => ({ ...prev, [key]: parseInt(value) || 0 }))
    }

    const handleApiKeyChange = (key, value) => {
        setApiKeys(prev => ({ ...prev, [key]: value }))
    }

    const saveApiKeys = async () => {
        localStorage.setItem('apiKeys', JSON.stringify(apiKeys))
        setSyncStatus({ syncing: true, message: '正在儲存...', type: 'info' })
        
        setTimeout(() => {
            setSyncStatus({ syncing: false, message: '✅ API金鑰已儲存', type: 'success' })
            setTimeout(() => setSyncStatus({ syncing: false, message: '', type: '' }), 3000)
        }, 500)
    }

    const clearApiKeys = () => {
        if (confirm('確定要清除所有API金鑰嗎？')) {
            setApiKeys({
                gemini: '',
                supabaseUrl: '',
                supabaseKey: '',
                n8nWebhook: '',
                fred: '',
                alphaVantage: '',
                tiingo: ''
            })
            localStorage.removeItem('apiKeys')
            setSyncStatus({ syncing: false, message: '✅ 已清除所有API金鑰', type: 'success' })
            setTimeout(() => setSyncStatus({ syncing: false, message: '', type: '' }), 3000)
        }
    }

    return (
        <div className="p-8 space-y-8 max-w-4xl">
            <div>
                <h1 className="text-3xl font-bold">系統設定</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                    個人化您的 AI 投資分析儀體驗
                </p>
            </div>

            <div className="card">
                <div className="flex items-center gap-3 mb-4">
                    <Key className="w-6 h-6" />
                    <h2 className="text-2xl font-bold">API 金鑰配置</h2>
                </div>

                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-4 mb-6">
                    <div className="flex items-start gap-2">
                        <Bell className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                        <div className="text-sm">
                            <p className="font-medium text-blue-900 dark:text-blue-100 mb-1">重要提醒</p>
                            <p className="text-blue-800 dark:text-blue-200">
                                ✨ 台灣證交所（TWSE）OpenAPI 完全免費，無需申請API Token！API金鑰儲存在瀏覽器中。
                            </p>
                        </div>
                    </div>
                </div>

                {syncStatus.message && (
                    <div className={`mb-4 p-4 rounded-lg ${
                        syncStatus.type === 'success' ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200' :
                        syncStatus.type === 'warning' ? 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-200' :
                        'bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200'
                    }`}>
                        {syncStatus.message}
                    </div>
                )}

                <div className="space-y-6">
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <label className="block text-sm font-medium">
                                Google Gemini API Key
                                <span className="text-red-500 ml-1">*必填</span>
                            </label>
                            <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                                獲取API金鑰 →
                            </a>
                        </div>
                        <input
                            type="password"
                            value={apiKeys.gemini}
                            onChange={(e) => handleApiKeyChange('gemini', e.target.value)}
                            placeholder="輸入您的 Gemini API Key..."
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 font-mono text-sm"
                        />
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            用於 AI 報告生成、智慧分析等功能
                        </p>
                    </div>
                </div>

                <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700 flex gap-3">
                    <button onClick={saveApiKeys} disabled={syncStatus.syncing} className="btn btn-primary disabled:opacity-50">
                        {syncStatus.syncing ? '儲存中...' : '儲存 API 配置'}
                    </button>
                    <button onClick={clearApiKeys} className="btn btn-secondary">
                        清除所有金鑰
                    </button>
                </div>
            </div>

            <div className="card">
                <div className="flex items-center gap-3 mb-4">
                    {darkMode ? <Moon className="w-6 h-6" /> : <Sun className="w-6 h-6" />}
                    <h2 className="text-2xl font-bold">主題設定</h2>
                </div>
                <div className="space-y-4">
                    <SettingRow label="深色模式" description="啟用深色主題以減少眼睛疲勞">
                        <button
                            onClick={() => {
                                const newDarkMode = !darkMode
                                setDarkMode(newDarkMode)
                                document.documentElement.classList.toggle('dark')
                                localStorage.setItem('darkMode', newDarkMode ? 'true' : 'false')
                                window.dispatchEvent(new CustomEvent('darkModeChange', { detail: newDarkMode }))
                            }}
                            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${darkMode ? 'bg-blue-600' : 'bg-gray-300'}`}
                        >
                            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${darkMode ? 'translate-x-6' : 'translate-x-1'}`} />
                        </button>
                    </SettingRow>
                </div>
            </div>
        </div>
    )
}

function SettingRow({ label, description, children }) {
    return (
        <div className="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700 last:border-0">
            <div>
                <div className="font-medium">{label}</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">{description}</div>
            </div>
            {children}
        </div>
    )
}
'''

# 寫入檔案
target_path = r'c:\Users\GV72\Desktop\私人事務\APP\台股美股金融資料庫\frontend\src\pages\Settings.jsx'
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(settings_content)

print(f"✅ Settings.jsx已成功生成到: {target_path}")
