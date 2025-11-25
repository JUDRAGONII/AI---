// 帳戶管理頁面 (Account Management)
// 個人資料、密碼修改、兩步驟驗證
import { useState } from 'react'
import { User, Lock, Shield, Mail, Phone, Save } from 'lucide-react'

export default function AccountManagement() {
    const [activeTab, setActiveTab] = useState('profile') // profile, security, preferences
    const [profile, setProfile] = useState({
        name: '投資者',
        email: 'investor@example.com',
        phone: '+886 912-345-678',
        avatar: ''
    })

    const [twoFactorEnabled, setTwoFactorEnabled] = useState(false)

    return (
        <div className="p-8 space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">帳戶管理</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                    管理您的個人資料與安全設定
                </p>
            </div>

            {/* 標籤頁 */}
            <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
                <TabButton
                    label="個人資料"
                    icon={<User className="w-4 h-4" />}
                    active={activeTab === 'profile'}
                    onClick={() => setActiveTab('profile')}
                />
                <TabButton
                    label="安全設定"
                    icon={<Lock className="w-4 h-4" />}
                    active={activeTab === 'security'}
                    onClick={() => setActiveTab('security')}
                />
                <TabButton
                    label="偏好設定"
                    icon={<Shield className="w-4 h-4" />}
                    active={activeTab === 'preferences'}
                    onClick={() => setActiveTab('preferences')}
                />
            </div>

            {/* 個人資料標籤 */}
            {activeTab === 'profile' && (
                <div className="max-w-2xl">
                    <div className="card">
                        <h2 className="text-xl font-bold mb-6">個人資料</h2>

                        <div className="space-y-6">
                            {/* 頭像 */}
                            <div className="flex items-center gap-4">
                                <div className="w-20 h-20 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                                    <User className="w-10 h-10 text-blue-600 dark:text-blue-400" />
                                </div>
                                <button className="btn btn-secondary text-sm">上傳頭像</button>
                            </div>

                            {/* 姓名 */}
                            <div>
                                <label className="block text-sm font-medium mb-2">姓名</label>
                                <input
                                    type="text"
                                    value={profile.name}
                                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                                />
                            </div>

                            {/* Email */}
                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    <div className="flex items-center gap-2">
                                        <Mail className="w-4 h-4" />
                                        Email
                                    </div>
                                </label>
                                <input
                                    type="email"
                                    value={profile.email}
                                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                                />
                            </div>

                            {/* 電話 */}
                            <div>
                                <label className="block text-sm font-medium mb-2">
                                    <div className="flex items-center gap-2">
                                        <Phone className="w-4 h-4" />
                                        電話
                                    </div>
                                </label>
                                <input
                                    type="tel"
                                    value={profile.phone}
                                    onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                                />
                            </div>

                            {/* 儲存按鈕 */}
                            <div className="flex justify-end">
                                <button className="btn btn-primary flex items-center gap-2">
                                    <Save className="w-4 h-4" />
                                    儲存變更
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* 安全設定標籤 */}
            {activeTab === 'security' && (
                <div className="max-w-2xl space-y-6">
                    {/* 密碼修改 */}
                    <div className="card">
                        <h2 className="text-xl font-bold mb-6">變更密碼</h2>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-2">目前密碼</label>
                                <input
                                    type="password"
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">新密碼</label>
                                <input
                                    type="password"
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">確認新密碼</label>
                                <input
                                    type="password"
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
                                />
                            </div>

                            <div className="flex justify-end">
                                <button className="btn btn-primary">更新密碼</button>
                            </div>
                        </div>
                    </div>

                    {/* 兩步驟驗證 */}
                    <div className="card">
                        <div className="flex items-start justify-between mb-4">
                            <div>
                                <h2 className="text-xl font-bold mb-2">兩步驟驗證 (2FA)</h2>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                    增加額外的安全層級保護您的帳戶
                                </p>
                            </div>
                            <button
                                onClick={() => setTwoFactorEnabled(!twoFactorEnabled)}
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${twoFactorEnabled ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                                    }`}
                            >
                                <span
                                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${twoFactorEnabled ? 'translate-x-6' : 'translate-x-1'
                                        }`}
                                />
                            </button>
                        </div>

                        {twoFactorEnabled && (
                            <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                <p className="text-sm mb-3">使用驗證器應用程式掃描此 QR Code：</p>
                                <div className="w-48 h-48 bg-white p-4 rounded-lg mx-auto">
                                    <div className="w-full h-full bg-gray-200 rounded flex items-center justify-center">
                                        QR Code
                                    </div>
                                </div>
                                <p className="text-xs text-gray-600 dark:text-gray-400 mt-3 text-center">
                                    或手動輸入金鑰：ABCD-EFGH-IJKL-MNOP
                                </p>
                            </div>
                        )}
                    </div>

                    {/* 登入歷史 */}
                    <div class="card">
                        <h2 className="text-xl font-bold mb-4">最近登入紀錄</h2>
                        <div className="space-y-3">
                            <LoginHistoryItem
                                device="Windows PC"
                                location="台北, 台灣"
                                time="2024-11-23 15:30"
                                current
                            />
                            <LoginHistoryItem
                                device="iPhone 15"
                                location="台北, 台灣"
                                time="2024-11-22 09:15"
                            />
                            <LoginHistoryItem
                                device="iPad Pro"
                                location="台北, 台灣"
                                time="2024-11-21 18:45"
                            />
                        </div>
                    </div>
                </div>
            )}

            {/* 偏好設定標籤 */}
            {activeTab === 'preferences' && (
                <div className="max-w-2xl space-y-6">
                    <div className="card">
                        <h2 className="text-xl font-bold mb-6">通知設定</h2>

                        <div className="space-y-4">
                            <PreferenceItem
                                label="Email 通知"
                                description="接收重要更新與警報"
                                enabled={true}
                            />
                            <PreferenceItem
                                label="LINE 推播"
                                description="即時價格警報"
                                enabled={true}
                            />
                            <PreferenceItem
                                label="每日報告"
                                description="每天早上接收 AI 分析報告"
                                enabled={false}
                            />
                        </div>
                    </div>

                    <div className="card">
                        <h2 className="text-xl font-bold mb-6">介面設定</h2>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-2">語言</label>
                                <select className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                                    <option>繁體中文</option>
                                    <option>English</option>
                                    <option>简体中文</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">時區</label>
                                <select className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800">
                                    <option>Asia/Taipei (GMT+8)</option>
                                    <option>America/New_York (GMT-5)</option>
                                    <option>Europe/London (GMT+0)</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

// 標籤按鈕
function TabButton({ label, icon, active, onClick }) {
    return (
        <button
            onClick={onClick}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${active
                    ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                }`}
        >
            {icon}
            {label}
        </button>
    )
}

// 登入歷史項目
function LoginHistoryItem({ device, location, time, current = false }) {
    return (
        <div className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
            <div>
                <div className="font-medium">{device}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">{location}</div>
            </div>
            <div className="text-right">
                <div className="text-sm">{time}</div>
                {current && (
                    <span className="text-xs px-2 py-1 rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400">
                        目前
                    </span>
                )}
            </div>
        </div>
    )
}

// 偏好設定項目
function PreferenceItem({ label, description, enabled }) {
    const [isEnabled, setIsEnabled] = useState(enabled)

    return (
        <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
            <div>
                <div className="font-medium">{label}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">{description}</div>
            </div>
            <button
                onClick={() => setIsEnabled(!isEnabled)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${isEnabled ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                    }`}
            >
                <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${isEnabled ? 'translate-x-6' : 'translate-x-1'
                        }`}
                />
            </button>
        </div>
    )
}
