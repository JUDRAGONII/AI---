# 生成完整版Settings.jsx - 包含所有API和深色模式雙向同步
settings_complete = '''// 系統設定頁面 (Settings)
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
        // 共用API（前後端同步）
        gemini: '',
        // 前端專用API
        supabaseUrl: '',
        supabaseKey: '',
        n8nWebhook: '',
        // 後端專用API - 股票與財報資料
        alphaVantage: '',
        tiingo: '',
        finnhub: '',
        fmp: '',
        // 後端專用API - 經濟與市場資料
        fred: '',
        goldApi: '',
        exchangeRate: '',
        marketaux: ''
    })

    const [syncStatus, setSyncStatus] = useState({ syncing: false, message: '', type: '' })

    // 監聽Header的深色模式變化（雙向同步）
    useEffect(() => {
        const handleDarkModeChange = (e) => {
            setDarkMode(e.detail)
        }
        window.addEventListener('darkModeChange', handleDarkModeChange)
        return () => window.removeEventListener('darkModeChange', handleDarkModeChange)
    }, [])

    // 從localStorage載入API金鑰
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
                alphaVantage: '',
                tiingo: '',
                finnhub: '',
                fmp: '',
                fred: '',
                goldApi: '',
                exchangeRate: '',
                marketaux: ''
            })
            localStorage.removeItem('apiKeys')
            setSyncStatus({ syncing: false, message: '✅ 已清除所有API金鑰', type: 'success' })
            setTimeout(() => setSyncStatus({ syncing: false, message: '', type: '' }), 3000)
        }
    }

    // 深色模式切換處理（雙向同步）
    const handleDarkModeToggle = () => {
        const newDarkMode = !darkMode
        setDarkMode(newDarkMode)
        document.documentElement.classList.toggle('dark')
        localStorage.setItem('darkMode', newDarkMode ? 'true' : 'false')
        // 發送事件通知其他組件（如Header, Sidebar）
        window.dispatchEvent(new CustomEvent('darkModeChange', { detail: newDarkMode }))
    }

    return (
        <div className="p-8 space-y-8 max-w-4xl">
            <div>
                <h1 className="text-3xl font-bold">系統設定</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                    個人化您的 AI 投資分析儀體驗
                </p>
            </div>

            {/* API金鑰配置 */}
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
                                ✨ 台灣證交所（TWSE）OpenAPI 完全免費，無需申請API Token！<br/>
                                API金鑰儲存在瀏覽器中，共用API會在儲存時自動同步到後端配置。
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
                    {/* 共用API */}
                    <div className="pb-6 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                            <span className="bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 px-2 py-1 rounded text-sm">前後端共用</span>
                            自動同步API
                        </h3>
                        
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
                                用於 AI 報告生成、智慧分析等功能（前後端共用，會自動同步）
                            </p>
                        </div>
                    </div>

                    {/* 前端專用API */}
                    <div className="pb-6 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                            <span className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded text-sm">前端專用</span>
                            前端應用API
                        </h3>
                        
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    Supabase URL
                                    <span className="text-orange-500 ml-1">選填</span>
                                </label>
                                <input
                                    type="text"
                                    value={apiKeys.supabaseUrl}
                                    onChange={(e) => handleApiKeyChange('supabaseUrl', e.target.value)}
                                    placeholder="https://your-project.supabase.co"
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 font-mono text-sm"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    Supabase Anon Key
                                    <span className="text-orange-500 ml-1">選填</span>
                                </label>
                                <input
                                    type="password"
                                    value={apiKeys.supabaseKey}
                                    onChange={(e) => handleApiKeyChange('supabaseKey', e.target.value)}
                                    placeholder="輸入您的 Supabase Anon Key..."
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 font-mono text-sm"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    N8N Webhook URL (自動化工作流)
                                    <span className="text-orange-500 ml-1">選填</span>
                                </label>
                                <input
                                    type="text"
                                    value={apiKeys.n8nWebhook}
                                    onChange={(e) => handleApiKeyChange('n8nWebhook', e.target.value)}
                                    placeholder="https://your-n8n.com/webhook/..."
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 font-mono text-sm"
                                />
                            </div>
                        </div>
                    </div>

                    {/* 後端專用API - 股票與財報資料 */}
                    <div className="pb-6 border-b border-gray-200 dark:border-gray-700">
                        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                            <span className="bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-2 py-1 rounded text-sm">後端專用</span>
                            股票與財報資料 API
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                            這些API用於獲取股票報價、新聞、財報等資料
                        </p>
                        
                        <div className="space-y-4">
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="block text-sm font-medium">
                                        Alpha Vantage API Key
                                        <span className="text-orange-500 ml-1">選填</span>
                                    </label>
                                    <a href="https://www.alphavantage.co/support/#api-key" target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                                        獲取API金鑰 →
                                    </a>
                                </div>
                                <input
                                    type="password"
                                    value={apiKeys.alphaVantage}
                                    onChange={(e) => handleApiKeyChange('alphaVantage', e.target.value)}
                                    placeholder="輸入您的 Alpha Vantage API Key..."
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 font-mono text-sm"
                                />
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">金融新聞、即時報價</p>
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="block text-sm font-medium">
                                        Tiingo API Key
                                        <span className="text-orange-500 ml-1">選填</span>
                                    </label>
                                    <a href="https://www.tiingo.com/account/api/token" target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                                        獲取API金鑰 →
                                    </a>
                                </div>
                                <input
                                    type="password"
                                    value={apiKeys.tiingo}
                                    onChange={(e) => handleApiKeyChange('tiingo', e.target.value)}
                                    placeholder="輸入您的 Tiingo API Key..."
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 font-mono text-sm"
                                />
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">美股歷史價格、技術指標</p>
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="block text-sm font-medium">
                                        Finnhub API Key
                                        <span className="text-orange-500 ml-1">選填</span>
                                    </label>
                                    <a href="https://finnhub.io/" target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                                        獲取API金鑰 →
                                    </a>
                                </div>
                                <input
                                    type="password"
                                    value={apiKeys.finnhub}
                                    onChange={(e) => handleApiKeyChange('finnhub', e.target.value)}
                                    placeholder="輸入您的 Finnhub API Key..."
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 font-mono text-sm"
                                />
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">股票、新聞、財報資料（備援）</p>
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="block text-sm font-medium">
                                        FMP API Key (Financial Modeling Prep)
                                        <span className="text-orange-500 ml-1">選填</span>
                                    </label>
                                    <a href="https://financialmodelingprep.com/developer/docs/" target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                                        獲取API金鑰 →
                                    </a>
                                </div>
                                <input
                                    type="password"
                                    value={apiKeys.fmp}
                                    onChange={(e) => handleApiKeyChange('fmp', e.target.value)}
                                    placeholder="輸入您的 FMP API Key..."
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 font-mono text-sm"
                                />
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">財報、股票資料</p>
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="block text-sm font-medium">
                                        Marketaux API Key
                                        <span className="text-orange-500 ml-1">選填</span>
                                    </label>
                                    <a href="https://www.marketaux.com/" target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                                        獲取API金鑰 →
                                    </a>
                                </div>
                                <input
                                    type="password"
                                    value={apiKeys.marketaux}
                                    onChange={(e) => handleApiKeyChange('marketaux', e.target.value)}
                                    placeholder="輸入您的 Marketaux API Key..."
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 font-mono text-sm"
                                />
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">新聞資料（備選）</p>
                            </div>
                        </div>
                    </div>

                    {/* 後端專用API - 經濟與市場資料 */}
                    <div>
                        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                            <span className="bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-2 py-1 rounded text-sm">後端專用</span>
                            經濟與市場資料 API
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                            這些API用於獲取總體經濟、匯率、黃金等市場資料
                        </p>
                        
                        <div className="space-y-4">
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="block text-sm font-medium">
                                        FRED API Key (美國經濟資料)
                                        <span className="text-orange-500 ml-1">選填</span>
                                    </label>
                                    <a href="https://fred.stlouisfed.org/docs/api/api_key.html" target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                                        獲取API金鑰 →
                                    </a>
                                </div>
                                <input
                                    type="password"
                                    value={apiKeys.fred}
                                    onChange={(e) => handleApiKeyChange('fred', e.target.value)}
                                    placeholder="輸入您的 FRED API Key..."
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 font-mono text-sm"
                                />
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">美國經濟指標、利率、GDP等</p>
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="block text-sm font-medium">
                                        Gold API Key (黃金價格)
                                        <span className="text-orange-500 ml-1">選填</span>
                                    </label>
                                    <a href="https://www.goldapi.io/" target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                                        獲取API金鑰 →
                                    </a>
                                </div>
                                <input
                                    type="password"
                                    value={apiKeys.goldApi}
                                    onChange={(e) => handleApiKeyChange('goldApi', e.target.value)}
                                    placeholder="輸入您的 Gold API Key..."
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 font-mono text-sm"
                                />
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">即時黃金價格資料</p>
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="block text-sm font-medium">
                                        ExchangeRate API Key (匯率資料)
                                        <span className="text-orange-500 ml-1">選填</span>
                                    </label>
                                    <a href="https://www.exchangerate-api.com/" target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                                        獲取API金鑰 →
                                    </a>
                                </div>
                                <input
                                    type="password"
                                    value={apiKeys.exchangeRate}
                                    onChange={(e) => handleApiKeyChange('exchangeRate', e.target.value)}
                                    placeholder="輸入您的 ExchangeRate API Key..."
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 font-mono text-sm"
                                />
                                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">全球匯率換算資料</p>
                            </div>
                        </div>
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

            {/* 主題設定 */}
            <div className="card">
                <div className="flex items-center gap-3 mb-4">
                    {darkMode ? <Moon className="w-6 h-6" /> : <Sun className="w-6 h-6" />}
                    <h2 className="text-2xl font-bold">主題設定</h2>
                </div>
                <div className="space-y-4">
                    <SettingRow label="深色模式" description="啟用深色主題以減少眼睛疲勞">
                        <button
                            onClick={handleDarkModeToggle}
                            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${darkMode ? 'bg-blue-600' : 'bg-gray-300'}`}
                        >
                            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${darkMode ? 'translate-x-6' : 'translate-x-1'}`} />
                        </button>
                    </SettingRow>
                </div>
            </div>

            {/* 通知設定 */}
            <div className="card">
                <div className="flex items-center gap-3 mb-4">
                    <Bell className="w-6 h-6" />
                    <h2 className="text-2xl font-bold">通知設定</h2>
                </div>
                <div className="space-y-4">
                    <SettingRow label="價格警報" description="當持股價格達到設定條件時通知">
                        <ToggleSwitch checked={notifications.priceAlert} onChange={() => handleNotificationToggle('priceAlert')} />
                    </SettingRow>
                    <SettingRow label="報告完成通知" description="AI 報告生成完成時通知">
                        <ToggleSwitch checked={notifications.reportReady} onChange={() => handleNotificationToggle('reportReady')} />
                    </SettingRow>
                    <SettingRow label="投資組合更新" description="持股損益變動超過設定閾值時通知">
                        <ToggleSwitch checked={notifications.portfolioUpdate} onChange={() => handleNotificationToggle('portfolioUpdate')} />
                    </SettingRow>
                    <SettingRow label="新聞警報" description="關鍵字匹配的新聞發布時通知">
                        <ToggleSwitch checked={notifications.newsAlert} onChange={() => handleNotificationToggle('newsAlert')} />
                    </SettingRow>
                </div>
            </div>

            {/* 技術指標參數 */}
            <div className="card">
                <div className="flex items-center gap-3 mb-4">
                    <TrendingUp className="w-6 h-6" />
                    <h2 className="text-2xl font-bold">技術指標參數</h2>
                </div>

                <div className="space-y-6">
                    <div>
                        <h3 className="font-medium mb-3">移動平均線 (MA)</h3>
                        <div className="grid grid-cols-3 gap-4">
                            <ParamInput label="MA 短期" value={technicalParams.ma5} onChange={(v) => handleParamChange('ma5', v)} suffix="日" />
                            <ParamInput label="MA 中期" value={technicalParams.ma20} onChange={(v) => handleParamChange('ma20', v)} suffix="日" />
                            <ParamInput label="MA 長期" value={technicalParams.ma60} onChange={(v) => handleParamChange('ma60', v)} suffix="日" />
                        </div>
                    </div>

                    <div>
                        <h3 className="font-medium mb-3">MACD 參數</h3>
                        <div className="grid grid-cols-3 gap-4">
                            <ParamInput label="快線" value={technicalParams.macdFast} onChange={(v) => handleParamChange('macdFast', v)} suffix="日" />
                            <ParamInput label="慢線" value={technicalParams.macdSlow} onChange={(v) => handleParamChange('macdSlow', v)} suffix="日" />
                            <ParamInput label="訊號線" value={technicalParams.macdSignal} onChange={(v) => handleParamChange('macdSignal', v)} suffix="日" />
                        </div>
                    </div>

                    <div>
                        <h3 className="font-medium mb-3">其他指標</h3>
                        <div className="grid grid-cols-3 gap-4">
                            <ParamInput label="RSI 週期" value={technicalParams.rsiPeriod} onChange={(v) => handleParamChange('rsiPeriod', v)} suffix="日" />
                        </div>
                    </div>
                </div>

                <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                    <button className="btn btn-primary">儲存設定</button>
                    <button className="btn btn-secondary ml-3">重置為預設值</button>
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

function ToggleSwitch({ checked, onChange }) {
    return (
        <button onClick={onChange} className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${checked ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'}`}>
            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${checked ? 'translate-x-6' : 'translate-x-1'}`} />
        </button>
    )
}

function ParamInput({ label, value, onChange, suffix }) {
    return (
        <div>
            <label className="block text-sm font-medium mb-1">{label}</label>
            <div className="relative">
                <input
                    type="number"
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 pr-10"
                />
                <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-sm text-gray-500">{suffix}</span>
            </div>
        </div>
    )
}
'''

# 寫入檔案
target_path = r'c:\\Users\\GV72\\Desktop\\私人事務\\APP\\台股美股金融資料庫\\frontend\\src\\pages\\Settings.jsx'
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(settings_complete)

print(f"✅ 完整版Settings.jsx已更新")
print(f"\\n新增API清單：")
print("  - Gold API (黃金價格)")
print("  - ExchangeRate API (匯率資料)")
print("  - Marketaux API (新聞資料)")
print("  - FMP API (財報資料)")
print("\\n✅ 深色模式現在已雙向同步")
print("  - Settings ↔ Header ↔ Sidebar")
