import { useState } from 'react'
import { api, fetchAPI } from '../services/api'
import { Calculator, DollarSign, Percent, TrendingUp, TrendingDown, ArrowRight } from 'lucide-react'

export default function TaxCalculator() {
    const [activeTab, setActiveTab] = useState('transaction') // 'transaction' or 'dividend'

    return (
        <div className="p-6 space-y-6">
            <header>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <Calculator className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                    稅務與財務試算工具
                </h1>
                <p className="text-gray-500 dark:text-gray-400 mt-1">
                    提供台美股交易成本與股利稅務的精確試算，協助您優化投資回報。
                </p>
            </header>

            {/* Tabs */}
            <div className="border-b border-gray-200 dark:border-gray-700">
                <nav className="-mb-px flex space-x-8">
                    <button
                        onClick={() => setActiveTab('transaction')}
                        className={`
                            whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm
                            ${activeTab === 'transaction'
                                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                            }
                        `}
                    >
                        交易成本試算
                    </button>
                    <button
                        onClick={() => setActiveTab('dividend')}
                        className={`
                            whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm
                            ${activeTab === 'dividend'
                                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                            }
                        `}
                    >
                        股利稅務試算
                    </button>
                </nav>
            </div>

            {/* Content */}
            <div className="mt-6">
                {activeTab === 'transaction' ? <TransactionCostCalculator /> : <DividendTaxCalculator />}
            </div>
        </div>
    )
}

function TransactionCostCalculator() {
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [formData, setFormData] = useState({
        market: 'tw',
        price: '',
        qty: '1000',
        is_sell: false,
        stock_type: 'stock',
        discount: '0.6',
        commission: '0' // for US
    })

    const handleCalculate = async (e) => {
        e.preventDefault()
        setLoading(true)
        try {
            const payload = {
                market: formData.market,
                price: Number(formData.price),
                qty: Number(formData.qty),
                is_sell: formData.is_sell === 'true' || formData.is_sell === true,
                stock_type: formData.stock_type,
                discount: Number(formData.discount),
                commission: Number(formData.commission)
            }

            const response = await fetchAPI(api.tax.calculateTransaction(), {
                method: 'POST',
                body: JSON.stringify(payload)
            })
            setResult(response.data)
        } catch (error) {
            console.error(error)
            alert('計算失敗: ' + error.message)
        } finally {
            setLoading(false)
        }
    }

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }))
    }

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Input Form */}
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 h-fit">
                <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                    <DollarSign className="w-5 h-5 text-green-500" />
                    參數設定
                </h2>
                <form onSubmit={handleCalculate} className="space-y-4">
                    {/* Market Switch */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">市場</label>
                        <div className="flex rounded-md shadow-sm">
                            <button
                                type="button"
                                onClick={() => {
                                    setFormData({ ...formData, market: 'tw' })
                                    setResult(null)
                                }}
                                className={`flex-1 px-4 py-2 text-sm font-medium rounded-l-md border ${formData.market === 'tw'
                                    ? 'bg-blue-600 text-white border-blue-600'
                                    : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 border-gray-300 dark:border-gray-600 hover:bg-gray-50'
                                    }`}
                            >
                                🇹🇼 台股 (TW)
                            </button>
                            <button
                                type="button"
                                onClick={() => {
                                    setFormData({ ...formData, market: 'us' })
                                    setResult(null)
                                }}
                                className={`flex-1 px-4 py-2 text-sm font-medium rounded-r-md border ${formData.market === 'us'
                                    ? 'bg-blue-600 text-white border-blue-600'
                                    : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 border-gray-300 dark:border-gray-600 hover:bg-gray-50'
                                    }`}
                            >
                                🇺🇸 美股 (US)
                            </button>
                        </div>
                    </div>

                    {/* Buy/Sell */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">交易方向</label>
                        <select
                            name="is_sell"
                            value={formData.is_sell}
                            onChange={handleChange}
                            className="w-full rounded-lg border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                        >
                            <option value={false}>買入 (Buy)</option>
                            <option value={true}>賣出 (Sell)</option>
                        </select>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">成交價格</label>
                            <input
                                type="number"
                                name="price"
                                value={formData.price}
                                onChange={handleChange}
                                placeholder="如: 1000"
                                className="w-full rounded-lg border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">股數</label>
                            <input
                                type="number"
                                name="qty"
                                value={formData.qty}
                                onChange={handleChange}
                                className="w-full rounded-lg border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                                required
                            />
                        </div>
                    </div>

                    {formData.market === 'tw' ? (
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">標的類型</label>
                                <select
                                    name="stock_type"
                                    value={formData.stock_type}
                                    onChange={handleChange}
                                    className="w-full rounded-lg border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                                >
                                    <option value="stock">股票 (0.3% 稅)</option>
                                    <option value="etf">ETF (0.1% 稅)</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">券商折數 (6折=0.6)</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    name="discount"
                                    value={formData.discount}
                                    onChange={handleChange}
                                    className="w-full rounded-lg border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                                />
                            </div>
                        </div>
                    ) : (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">手續費 (USD)</label>
                            <input
                                type="number"
                                step="0.01"
                                name="commission"
                                value={formData.commission}
                                onChange={handleChange}
                                className="w-full rounded-lg border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                        {loading ? '計算中...' : '開始試算'}
                        <ArrowRight className="w-4 h-4" />
                    </button>
                </form>
            </div>

            {/* Results */}
            <div className="space-y-6">
                {result && (
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 animate-fade-in">
                        <h2 className="text-lg font-semibold mb-6 text-gray-900 dark:text-white border-b pb-2 border-gray-100 dark:border-gray-700">
                            試算結果 ({formData.market === 'tw' ? 'TWD' : 'USD'})
                        </h2>

                        <div className="space-y-4">
                            <div className="flex justify-between items-center py-2 border-b border-dashed border-gray-200 dark:border-gray-700">
                                <span className="text-gray-600 dark:text-gray-400">成交金額</span>
                                <span className="font-mono text-lg font-medium text-gray-900 dark:text-white">
                                    {result?.amount?.toLocaleString()}
                                </span>
                            </div>

                            <div className="flex justify-between items-center py-2 border-b border-dashed border-gray-200 dark:border-gray-700">
                                <span className="text-gray-600 dark:text-gray-400">手續費</span>
                                <span className="font-mono text-red-500">
                                    -{result?.fee?.toLocaleString()}
                                </span>
                            </div>

                            {formData.market === 'tw' && (formData.is_sell === 'true' || formData.is_sell === true) && (
                                <div className="flex justify-between items-center py-2 border-b border-dashed border-gray-200 dark:border-gray-700">
                                    <span className="text-gray-600 dark:text-gray-400">證券交易稅</span>
                                    <span className="font-mono text-red-500">
                                        -{result.tax.toLocaleString()}
                                    </span>
                                </div>
                            )}

                            <div className="flex justify-between items-center py-3">
                                <span className="text-gray-800 dark:text-gray-200 font-medium">總交易成本</span>
                                <span className="font-mono font-bold text-red-600">
                                    {result?.total_cost?.toLocaleString()}
                                </span>
                            </div>

                            <div className={`mt-4 p-4 rounded-lg flex justify-between items-center ${(formData.is_sell === 'true' || formData.is_sell === true)
                                ? 'bg-green-50 dark:bg-green-900/20'
                                : 'bg-red-50 dark:bg-red-900/20'
                                }`}>
                                <span className="font-semibold text-gray-700 dark:text-gray-300">
                                    {(formData.is_sell === 'true' || formData.is_sell === true) ? '預估淨收入' : '預估總支出'}
                                </span>
                                <span className={`font-mono text-2xl font-bold ${(formData.is_sell === 'true' || formData.is_sell === true)
                                    ? 'text-green-600 dark:text-green-400'
                                    : 'text-red-600 dark:text-red-400'
                                    }`}>
                                    {result?.net_amount?.toLocaleString()}
                                </span>
                            </div>
                        </div>

                        {formData.market === 'tw' && (
                            <div className="mt-4 text-xs text-gray-500 dark:text-gray-500">
                                * 手續費以 0.1425% 計算，最低 20 元。
                                <br />
                                * 證交稅：股票 0.3%，ETF 0.1% (僅賣出收取)。
                            </div>
                        )}
                    </div>
                )}

                {/* Info Card */}
                {!result && (
                    <div className="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-xl border border-blue-100 dark:border-blue-800 flex flex-col items-center justify-center text-center h-full min-h-[300px]">
                        <TrendingUp className="w-12 h-12 text-blue-400 mb-4 opacity-50" />
                        <h3 className="text-blue-900 dark:text-blue-300 font-medium mb-2">準備開始試算</h3>
                        <p className="text-sm text-blue-700 dark:text-blue-400">
                            輸入左側交易參數，即可獲得精確的交易成本分析。
                        </p>
                    </div>
                )}
            </div>
        </div>
    )
}

function DividendTaxCalculator() {
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [formData, setFormData] = useState({
        market: 'tw',
        amount: '',
        tax_rate: '0.05'
    })

    const handleCalculate = async (e) => {
        e.preventDefault()
        setLoading(true)
        try {
            const payload = {
                market: formData.market,
                amount: Number(formData.amount),
                tax_rate: Number(formData.tax_rate)
            }
            const response = await fetchAPI(api.tax.simulateDividend(), {
                method: 'POST',
                body: JSON.stringify(payload)
            })
            setResult(response.data)
        } catch (error) {
            console.error(error)
            alert('計算失敗: ' + error.message)
        } finally {
            setLoading(false)
        }
    }

    const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value })

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Input */}
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 h-fit">
                <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white flex items-center gap-2">
                    <Percent className="w-5 h-5 text-purple-500" />
                    股利設定
                </h2>
                <form onSubmit={handleCalculate} className="space-y-4">
                    {/* Market Switch */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">市場</label>
                        <div className="flex rounded-md shadow-sm">
                            <button
                                type="button"
                                onClick={() => {
                                    setFormData({ ...formData, market: 'tw' })
                                    setResult(null)
                                }}
                                className={`flex-1 px-4 py-2 text-sm font-medium rounded-l-md border ${formData.market === 'tw'
                                    ? 'bg-purple-600 text-white border-purple-600'
                                    : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 border-gray-300 dark:border-gray-600 hover:bg-gray-50'
                                    }`}
                            >
                                🇹🇼 台股 (TW)
                            </button>
                            <button
                                type="button"
                                onClick={() => {
                                    setFormData({ ...formData, market: 'us' })
                                    setResult(null)
                                }}
                                className={`flex-1 px-4 py-2 text-sm font-medium rounded-r-md border ${formData.market === 'us'
                                    ? 'bg-purple-600 text-white border-purple-600'
                                    : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 border-gray-300 dark:border-gray-600 hover:bg-gray-50'
                                    }`}
                            >
                                🇺🇸 美股 (US)
                            </button>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">獲配股利總額 ({formData.market === 'tw' ? 'TWD' : 'USD'})</label>
                        <input
                            type="number"
                            name="amount"
                            value={formData.amount}
                            onChange={handleChange}
                            className="w-full rounded-lg border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:ring-purple-500 focus:border-purple-500"
                            required
                        />
                    </div>

                    {formData.market === 'tw' && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">個人綜合所得稅率</label>
                            <select
                                name="tax_rate"
                                value={formData.tax_rate}
                                onChange={handleChange}
                                className="w-full rounded-lg border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:ring-purple-500 focus:border-purple-500"
                            >
                                <option value="0.05">5%</option>
                                <option value="0.12">12%</option>
                                <option value="0.20">20%</option>
                                <option value="0.30">30%</option>
                                <option value="0.40">40%</option>
                            </select>
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full py-2.5 px-4 rounded-lg bg-purple-600 hover:bg-purple-700 text-white font-medium transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                        {loading ? '計算中...' : '開始分析'}
                        <ArrowRight className="w-4 h-4" />
                    </button>
                </form>
            </div>

            {/* Results */}
            <div className="space-y-6">
                {result && formData.market === 'tw' && (
                    <div className="grid grid-cols-1 gap-4">
                        {/* 兩案比較卡片 */}
                        <div className={`p-4 rounded-xl border-2 ${result.best_option === 'A'
                            ? 'border-green-500 bg-green-50 dark:bg-green-900/10'
                            : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800'
                            }`}>
                            <div className="flex justify-between items-start mb-2">
                                <h3 className="font-bold text-gray-900 dark:text-white">方案 A: 合併課稅</h3>
                                {result.best_option === 'A' && <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">建議使用</span>}
                            </div>
                            <div className="text-sm space-y-1 text-gray-600 dark:text-gray-300">
                                <div className="flex justify-between">
                                    <span>增加應納稅額:</span>
                                    <span>${(result?.option_a?.tax_increase + result?.option_a?.deductible || 0).toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between text-green-600">
                                    <span>可抵減稅額 (8.5%):</span>
                                    <span>-${result?.option_a?.deductible?.toLocaleString()}</span>
                                </div>
                                <div className="border-t pt-1 flex justify-between font-medium text-gray-900 dark:text-white">
                                    <span>實際增加負擔:</span>
                                    <span>${result?.option_a?.tax_increase?.toLocaleString()}</span>
                                </div>
                            </div>
                        </div>

                        <div className={`p-4 rounded-xl border-2 ${result.best_option === 'B'
                            ? 'border-green-500 bg-green-50 dark:bg-green-900/10'
                            : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800'
                            }`}>
                            <div className="flex justify-between items-start mb-2">
                                <h3 className="font-bold text-gray-900 dark:text-white">方案 B: 分離課稅 (28%)</h3>
                                {result.best_option === 'B' && <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">建議使用</span>}
                            </div>
                            <div className="text-sm space-y-1 text-gray-600 dark:text-gray-300">
                                <div className="flex justify-between">
                                    <span>應納稅額:</span>
                                    <span>${result?.option_b?.tax_increase?.toLocaleString()}</span>
                                </div>
                            </div>
                        </div>

                        {/* 補充保費 */}
                        <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700">
                            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">其他稅費</h3>
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600 dark:text-gray-400">二代健保補充保費 (2.11%)</span>
                                <span className="font-mono font-medium text-red-600">
                                    ${result?.supplementary_premium?.toLocaleString()}
                                </span>
                            </div>
                            <div className="mt-2 text-xs text-gray-400">
                                * 單筆股利達 20,000 元即需扣繳。
                            </div>
                        </div>

                        {/* 結論 */}
                        <div className="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200 text-center">
                            若選擇方案 {result.best_option}，您將可節省
                            <span className="font-bold text-lg mx-1">${result?.savings?.toLocaleString()}</span>
                            稅金。
                        </div>
                    </div>
                )}

                {result && formData.market === 'us' && (
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
                        <h2 className="text-lg font-semibold mb-6 text-gray-900 dark:text-white border-b pb-2 border-gray-100 dark:border-gray-700">
                            美股稅務分析 (USD)
                        </h2>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center py-2">
                                <span className="text-gray-600 dark:text-gray-400">股息總額</span>
                                <span className="font-mono text-lg font-medium text-gray-900 dark:text-white">
                                    {result?.gross_dividend?.toLocaleString()}
                                </span>
                            </div>

                            <div className="flex justify-between items-center py-2 border-b border-dashed border-gray-200 dark:border-gray-700">
                                <span className="text-gray-600 dark:text-gray-400">預扣稅 (30%)</span>
                                <span className="font-mono text-red-500">
                                    -{result?.withholding_tax?.toLocaleString()}
                                </span>
                            </div>

                            <div className="flex justify-between items-center py-3 bg-green-50 dark:bg-green-900/20 px-4 rounded-lg">
                                <span className="text-gray-800 dark:text-gray-200 font-medium">實際入帳金額</span>
                                <span className="font-mono text-xl font-bold text-green-600 dark:text-green-400">
                                    {result?.net_dividend?.toLocaleString()}
                                </span>
                            </div>
                        </div>
                    </div>
                )}

                {!result && (
                    <div className="bg-purple-50 dark:bg-purple-900/20 p-6 rounded-xl border border-purple-100 dark:border-purple-800 flex flex-col items-center justify-center text-center h-full min-h-[300px]">
                        <Percent className="w-12 h-12 text-purple-400 mb-4 opacity-50" />
                        <h3 className="text-purple-900 dark:text-purple-300 font-medium mb-2">股利稅務規劃</h3>
                        <p className="text-sm text-purple-700 dark:text-purple-400">
                            比較不同課稅方式，找出最適合您的報稅方案。
                        </p>
                    </div>
                )}
            </div>
        </div>
    )
}
