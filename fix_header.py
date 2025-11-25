# 重新生成正確的Header.jsx with darkModeChange listener
header_code = '''// Header 頂部欄元件
import { Moon, Sun, Bell, User, X } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'

export default function Header({ onMenuClick }) {
    const [darkMode, setDarkMode] = useState(() => {
        return document.documentElement.classList.contains('dark')
    })
    const [showNotifications, setShowNotifications] = useState(false)
    const [showUserMenu, setShowUserMenu] = useState(false)

    // Refs for detecting outside clicks
    const notificationsRef = useRef(null)
    const userMenuRef = useRef(null)

    // 檢測初始深色模式狀態
    useEffect(() => {
        const isDark = document.documentElement.classList.contains('dark') ||
            window.matchMedia('(prefers-color-scheme: dark)').matches
        if (isDark && !document.documentElement.classList.contains('dark')) {
            document.documentElement.classList.add('dark')
            setDarkMode(true)
        }
    }, [])

    // 監聽來自其他組件（Settings）的深色模式變化事件
    useEffect(() => {
        const handleDarkModeChange = (e) => {
            setDarkMode(e.detail)
        }
        window.addEventListener('darkModeChange', handleDarkModeChange)
        return () => window.removeEventListener('darkModeChange', handleDarkModeChange)
    }, [])

    // 點擊外部區域關閉下拉選單
    useEffect(() => {
        const handleClickOutside = (event) => {
            // 檢查通知下拉選單
            if (notificationsRef.current && !notificationsRef.current.contains(event.target)) {
                setShowNotifications(false)
            }
            // 檢查使用者選單
            if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
                setShowUserMenu(false)
            }
        }

        // 只在下拉選單開啟時添加監聽器
        if (showNotifications || showUserMenu) {
            document.addEventListener('mousedown', handleClickOutside)
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside)
        }
    }, [showNotifications, showUserMenu])

    // 切換深色模式
    const toggleDarkMode = () => {
        const newDarkMode = !darkMode
        setDarkMode(newDarkMode)
        document.documentElement.classList.toggle('dark')
        // 同步到localStorage
        localStorage.setItem('darkMode', newDarkMode ? 'true' : 'false')
        // 觸發自訂事件讓Settings頁面同步
        window.dispatchEvent(new CustomEvent('darkModeChange', { detail: newDarkMode }))
    }

    // 模擬通知數據
    const notifications = [
        { id: 1, title: '價格警報', message: '台積電突破590元', time: '5分鐘前' },
        { id: 2, title: 'AI建議', message: '新的投資機會出現', time: '1小時前' },
        { id: 3, title: '系統更新', message: '資料庫同步完成', time: '2小時前' }
    ]

    return (
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
            <div className="flex items-center justify-between">
                {/* Left */}
                <div className="flex items-center gap-4">
                    <time className="text-sm text-gray-600 dark:text-gray-400">
                        {new Date().toLocaleDateString('zh-TW', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            weekday: 'long'
                        })}
                    </time>
                </div>

                {/* Right */}
                <div className="flex items-center gap-3">
                    {/* 深色模式切換 */}
                    <button
                        onClick={toggleDarkMode}
                        className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        title={darkMode ? '切換至淺色模式' : '切換至深色模式'}
                    >
                        {darkMode ? (
                            <Sun className="w-5 h-5 text-yellow-500" />
                        ) : (
                            <Moon className="w-5 h-5 text-gray-600" />
                        )}
                    </button>

                    {/* 通知 */}
                    <div className="relative" ref={notificationsRef}>
                        <button
                            onClick={() => setShowNotifications(!showNotifications)}
                            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors relative"
                        >
                            <Bell className="w-5 h-5" />
                            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                        </button>

                        {/* 通知下拉選單 */}
                        {showNotifications && (
                            <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50">
                                <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                                    <h3 className="font-bold">通知</h3>
                                    <button onClick={() => setShowNotifications(false)}>
                                        <X className="w-4 h-4" />
                                    </button>
                                </div>
                                <div className="max-h-96 overflow-y-auto">
                                    {notifications.map(notif => (
                                        <div key={notif.id} className="p-4 border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer">
                                            <div className="font-medium text-sm">{notif.title}</div>
                                            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">{notif.message}</div>
                                            <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">{notif.time}</div>
                                        </div>
                                    ))}
                                </div>
                                <div className="p-3 text-center border-t border-gray-200 dark:border-gray-700">
                                    <button className="text-sm text-blue-600 dark:text-blue-400 hover:underline">
                                        查看全部通知
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* 使用者 */}
                    <div className="relative" ref={userMenuRef}>
                        <button
                            onClick={() => setShowUserMenu(!showUserMenu)}
                            className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        >
                            <User className="w-5 h-5" />
                            <span className="text-sm font-medium hidden md:block">使用者</span>
                        </button>

                        {/* 使用者下拉選單 */}
                        {showUserMenu && (
                            <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50">
                                <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                                    <div className="font-medium">訪客使用者</div>
                                    <div className="text-sm text-gray-500 dark:text-gray-400">guest@example.com</div>
                                </div>
                                <div className="py-2">
                                    <button className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700">
                                        個人設定
                                    </button>
                                    <button className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700">
                                        帳戶管理
                                    </button>
                                    <button className="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700">
                                        系統偏好
                                    </button>
                                </div>
                                <div className="border-t border-gray-200 dark:border-gray-700 py-2">
                                    <button className="w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700">
                                        登出
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </header>
    )
}
'''

# 寫入檔案
target_path = r'c:\\Users\\GV72\\Desktop\\私人事務\\APP\\台股美股金融資料庫\\frontend\\src\\components\\Header.jsx'
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(header_code)

print("✅ Header.jsx已修復")
print("✅ 深色模式雙向同步功能已添加")
print("   - Header監聽darkModeChange事件")
print("   - Settings切換深色模式時Header圖示會同步更新")
