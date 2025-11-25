// 交易日誌頁面 - 含券商資訊
import { useState } from 'react'
import { Plus, Filter, Download, Edit, Trash2, Building2 } from 'lucide-react'

export default function TransactionLog() {
    const [filterType, setFilterType] = useState('all')

    const transactions = [
        { id: 1, date: '2024-11-20', type: 'buy', code: '2330', name: '台積電', broker: '元大證券', shares: 100, price: 580, amount: 58000, fee: 145, reason: '因子分數突破80，技術面MA20支撐明確，TDCC大戶增持', notes: '預計持有3-6個月，目標價650', status: 'holding' },
        { id: 2, date: '2024-11-15', type: 'sell', code: '2454', name: '聯發科', broker: '富邦證券', shares: 50, price: 880, amount: 44000, fee: 110, reason: '達到目標價，技術面RSI超買', notes: '獲利約12%，符合預期', status: 'closed', buyPrice: 785, pnl: 4750, returnPct: 10.8 },
        { id: 3, date: '2024-11-10', type: 'buy', code: '0050', name: '元大台灣50', broker: '元大證券', shares: 100, price: 135, amount: 13500, fee: 34, reason: '定期定額投資，分散風險', notes: '長期持有標的', status: 'holding' },
        { id: 4, date: '2024-11-05', type: 'sell', code: '2317', name: '鴻海', broker: '富邦證券', shares: 500, price: 110, amount: 55000, fee: 138, reason: '產業前景不明，獲利了結', notes: '持有期間6個月，報酬率5%', status: 'closed', buyPrice: 105, pnl: 2362, returnPct: 4.5 },
        { id: 5, date: '2024-10-28', type: 'buy', code: 'AAPL', name: 'Apple Inc.', broker: 'Charles Schwab', shares: 10, price: 195, amount: 1950, fee: 0, reason: '美股科技股長期看好，蘋果財報優於預期', notes: 'USD帳戶交易', status: 'holding' },
    ]

    const filteredTransactions = filterType === 'all' ? transactions : transactions.filter(t => t.type === filterType)
    const stats = {
        totalTrades: transactions.length,
        buyCount: transactions.filter(t => t.type === 'buy').length,
        sellCount: transactions.filter(t => t.type === 'sell').length,
        totalPnl: transactions.filter(t => t.status === 'closed').reduce((sum, t) => sum + (t.pnl || 0), 0)
    }

    return (
        <div className="p-8 space-y-8">
            <div className="flex items-center justify-between">
                <div><h1 className="text-3xl font-bold">交易日誌</h1><p className="text-gray-600 dark:text-gray-400 mt-2">完整記錄每筆交易的決策過程與結果</p></div>
                <div className="flex gap-2">
                    <button className="btn btn-secondary flex items-center gap-2"><Filter className="w-5 h-5" />篩選</button>
                    <button className="btn btn-secondary flex items-center gap-2"><Download className="w-5 h-5" />匯出</button>
                    <button className="btn btn-primary flex items-center gap-2"><Plus className="w-5 h-5" />新增交易</button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <StatCard label="總交易數" value={stats.totalTrades} />
                <StatCard label="買入" value={stats.buyCount} color="green" />
                <StatCard label="賣出" value={stats.sellCount} color="red" />
                <StatCard label="已實現損益" value={`$${stats.totalPnl.toLocaleString()}`} color={stats.totalPnl >= 0 ? 'green' : 'red'} />
            </div>

            <div className="flex gap-2">
                <button onClick={() => setFilterType('all')} className={`px-4 py-2 rounded-lg ${filterType === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}>全部</button>
                <button onClick={() => setFilterType('buy')} className={`px-4 py-2 rounded-lg ${filterType === 'buy' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}>買入</button>
                <button onClick={() => setFilterType('sell')} className={`px-4 py-2 rounded-lg ${filterType === 'sell' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}>賣出</button>
            </div>

            <div className="space-y-4">
                {filteredTransactions.map(transaction => (
                    <TransactionCard key={transaction.id} transaction={transaction} />
                ))}
            </div>
        </div>
    )
}

function StatCard({ label, value, color = 'blue' }) {
    const colorClasses = { blue: 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400', green: 'bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400', red: 'bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400' }
    return <div className={`card ${colorClasses[color]}`}><div className="text-sm font-medium mb-2">{label}</div><div className="text-2xl font-bold">{value}</div></div>
}

function TransactionCard({ transaction }) {
    const isBuy = transaction.type === 'buy'
    const typeColor = isBuy ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'
    const typeBg = isBuy ? 'bg-red-100 dark:bg-red-900/30' : 'bg-green-100 dark:bg-green-900/30'

    return (
        <div className="card">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${typeBg} ${typeColor}`}>{isBuy ? '買入' : '賣出'}</span>
                    <div>
                        <h3 className="text-xl font-bold">{transaction.code} - {transaction.name}</h3>
                        <div className="flex items-center gap-2 mt-1">
                            <p className="text-sm text-gray-600 dark:text-gray-400">{transaction.date}</p>
                            <span className="text-gray-400">|</span>
                            <div className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400">
                                <Building2 className="w-3 h-3" />
                                <span>{transaction.broker}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex gap-2">
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"><Edit className="w-4 h-4" /></button>
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg text-red-600"><Trash2 className="w-4 h-4" /></button>
                </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
                <InfoItem label="券商" value={transaction.broker} />
                <InfoItem label="股數" value={`${transaction.shares} 股`} />
                <InfoItem label="價格" value={`$${transaction.price}`} />
                <InfoItem label="金額" value={`$${transaction.amount.toLocaleString()}`} />
                <InfoItem label="手續費" value={`$${transaction.fee}`} />
            </div>

            {transaction.status === 'closed' && (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg mb-4">
                    <InfoItem label="買入價" value={`$${transaction.buyPrice}`} />
                    <InfoItem label="損益" value={`${transaction.pnl >= 0 ? '+' : ''}$${transaction.pnl.toLocaleString()}`} valueColor={transaction.pnl >= 0 ? 'text-green-600' : 'text-red-600'} />
                    <InfoItem label="報酬率" value={`${transaction.returnPct >= 0 ? '+' : ''}${transaction.returnPct.toFixed(2)}%`} valueColor={transaction.returnPct >= 0 ? 'text-green-600' : 'text-red-600'} />
                </div>
            )}

            <div className="space-y-2">
                <div><span className="font-medium text-sm text-gray-600 dark:text-gray-400">買賣理由：</span><p className="text-sm mt-1">{transaction.reason}</p></div>
                {transaction.notes && (<div><span className="font-medium text-sm text-gray-600 dark:text-gray-400">備註：</span><p className="text-sm mt-1 text-gray-600 dark:text-gray-400">{transaction.notes}</p></div>)}
            </div>

            {transaction.status === 'holding' && (
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400">持有中</span>
                </div>
            )}
        </div>
    )
}

function InfoItem({ label, value, valueColor = '' }) {
    return <div><div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{label}</div><div className={`font-medium ${valueColor}`}>{value}</div></div>
}
