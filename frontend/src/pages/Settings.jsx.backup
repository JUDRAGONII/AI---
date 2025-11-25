// 系統設定頁面 (Settings)
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
            < div >
                <h1 className="text-3xl font-bold">系統設定</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                    個人化您的 AI 投資分析儀體驗
                </p>
            </div >

        {/* API 金鑰配置 */ }
        < div className = "card" >
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
                                API金鑰將儲存在瀏覽器本地儲存（localStorage）中，請勿在公用電腦上儲存敏感資訊。
                            </p>
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    {/* Gemini API */}
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <label className="block text-sm font-medium">
                                Google Gemini API Key
                                <span className="text-red-500 ml-1">*必填</span>
                            </label>
                            <a
                                href="https://aistudio.google.com/apikey"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                            >
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

                    {/* Supabase */}
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

                    {/* TWSE Token */}
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <label className="block text-sm font-medium">
                                TWSE API Token (台灣證交所)
                                <span className="text-orange-500 ml-1">選填</span>
                            </label>
                            <a
                                href="https://openapi.twse.com.tw"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                            >
                                獲取Token →
                            </a>
                        </div>
                        <input
                            type="password"
                            value={apiKeys.twseToken}
                            onChange={(e) => handleApiKeyChange('twseToken', e.target.value)}
                            placeholder="輸入您的 TWSE Token..."
                            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 font-mono text-sm"
                        />
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            用於台股即時行情、三大法人等資料
                        </p>
                    </div>

                    {/* N8N Webhook */}
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
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            用於自動化新聞抓取、通知推送等
                        </p>
                    </div>

                    {/* FRED API */}
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <label className="block text-sm font-medium">
                                FRED API Key (美國經濟資料)
                                <span className="text-orange-500 ml-1">選填</span>
                            </label>
                            <a
                                href="https://fred.stlouisfed.org/docs/api/api_key.html"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                            >
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
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            用於美國經濟指標、利率、GDP等資料
                        </p>
                    </div>

                    {/* Alpha Vantage */}
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <label className="block text-sm font-medium">
                                Alpha Vantage API Key
                                <span className="text-orange-500 ml-1">選填</span>
                            </label>
                            <a
                                href="https://www.alphavantage.co/support/#api-key"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                            >
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
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            用於金融新聞、即時報價等功能
                        </p>
                    </div>

                    {/* Tiingo */}
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <label className="block text-sm font-medium">
                                Tiingo API Key (美股資料)
                                <span className="text-orange-500 ml-1">選填</span>
                            </label>
                            <a
                                href="https://www.tiingo.com/account/api/token"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                            >
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
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                            用於美股歷史價格、技術指標等資料
                        </p>
                    </div>
                </div>

                <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700 flex gap-3">
                    <button onClick={saveApiKeys} className="btn btn-primary">
                        儲存 API 配置
                    </button>
                    <button onClick={clearApiKeys} className="btn btn-secondary">
                        清除所有金鑰
                    </button>
                </div>
            </div >

        {/* 主題設定 */ }
        < div className = "card" >
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
            </div >

        {/* 通知設定 */ }
        < div className = "card" >
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
            </div >

        {/* 技術指標參數 */ }
        < div className = "card" >
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
            </div >
        </div >
    )
}

// 設定行元件
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

// 切換開關元件
function ToggleSwitch({ checked, onChange }) {
    return (
        <button onClick={onChange} className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${checked ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'}`}>
            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${checked ? 'translate-x-6' : 'translate-x-1'}`} />
        </button>
    )
}

// 參數輸入元件
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