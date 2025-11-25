// Layout 元件 - 主版面架構
import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

export default function Layout() {
    const [sidebarOpen, setSidebarOpen] = useState(true)

    return (
        <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
            {/* Sidebar */}
            <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

            {/* Main Content */}
            <div className="flex flex-col flex-1 overflow-hidden">
                <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

                <main className="flex-1 overflow-x-hidden overflow-y-auto">
                    <Outlet />
                </main>
            </div>
        </div>
    )
}
