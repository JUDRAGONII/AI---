// 對話式 AI 分析師 (AI Chat Analyst)
// 自然語言查詢介面、上下文理解、圖表生成
import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, TrendingUp, BarChart3, Lightbulb } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function AIChatAnalyst() {
    const [messages, setMessages] = useState([
        {
            id: 1,
            role: 'assistant',
            content: '您好！我是您的 AI 投資分析助手。您可以詢問我關於股票分析、投資組合建議、市場趨勢等問題。請問有什麼可以幫助您的？',
            timestamp: new Date()
        }
    ])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const messagesEndRef = useRef(null)

    // 自動滾動到底部
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    const handleSend = async () => {
        if (!input.trim()) return

        const userMessage = {
            id: messages.length + 1,
            role: 'user',
            content: input,
            timestamp: new Date()
        }

        setMessages(prev => [...prev, userMessage])
        setInput('')
        setLoading(true)

        // 模擬 AI 思考時間
        setTimeout(async () => {
            const aiResponse = await getAIResponse(input)
            const assistantMessage = {
                id: messages.length + 2,
                role: 'assistant',
                content: aiResponse.content,
                type: aiResponse.type,
                chart: aiResponse.chart,
                timestamp: new Date()
            }
            setMessages(prev => [...prev, assistantMessage])
            setLoading(false)
        }, 1500)
    }

    // 快速問題範本
    const quickQuestions = [
        '分析台積電（2330）',
        '我的投資組合如何？',
        '今天市場表現怎麼樣？',
        '推薦適合長期投資的股票',
    ]

    return (
        <div className="flex flex-col h-[calc(100vh-4rem)]">
            {/* Header */}
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/30">
                        <Bot className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold">AI 投資分析師</h1>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            自然語言查詢 | 即時分析 | 智慧建議
                        </p>
                    </div>
                </div>
            </div>

            {/* 快速問題 */}
            {messages.length <= 1 && (
                <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                    <div className="flex items-center gap-2 mb-3">
                        <Lightbulb className="w-5 h-5 text-yellow-600" />
                        <span className="font-medium">快速開始</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {quickQuestions.map((q, i) => (
                            <button
                                key={i}
                                onClick={() => setInput(q)}
                                className="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-sm transition-colors"
                            >
                                {q}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* 訊息區域 */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.map((message) => (
                    <MessageBubble key={message.id} message={message} />
                ))}

                {loading && (
                    <div className="flex items-start gap-3">
                        <div className="p-2 rounded-full bg-blue-100 dark:bg-blue-900/30">
                            <Bot className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div className="flex-1 max-w-3xl">
                            <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
                                <div className="flex gap-2">
                                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* 輸入區域 */}
            <div className="p-6 border-t border-gray-200 dark:border-gray-700">
                <div className="flex gap-3">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="輸入您的問題..."
                        className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || loading}
                        className="btn btn-primary flex items-center gap-2 px-6"
                    >
                        <Send className="w-5 h-5" />
                        發送
                    </button>
                </div>
                <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                    💡 提示：您可以詢問股票分析、投資建議、市場趨勢等問題
                </div>
            </div>
        </div>
    )
}

// 訊息氣泡元件
function MessageBubble({ message }) {
    const isUser = message.role === 'user'

    return (
        <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
            {/* 頭像 */}
            <div className={`p-2 rounded-full ${isUser
                ? 'bg-green-100 dark:bg-green-900/30'
                : 'bg-blue-100 dark:bg-blue-900/30'
                }`}>
                {isUser ? (
                    <User className="w-5 h-5 text-green-600 dark:text-green-400" />
                ) : (
                    <Bot className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                )}
            </div>

            {/* 訊息內容 */}
            <div className={`flex-1 max-w-3xl ${isUser ? 'flex flex-col items-end' : ''}`}>
                <div className={`rounded-lg p-4 ${isUser
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-800'
                    }`}>
                    <div className="whitespace-pre-wrap">{message.content}</div>

                    {/* 圖表生成 */}
                    {message.chart && message.chart.length > 0 && (
                        <div className="mt-4 p-3 bg-white dark:bg-gray-900 rounded-lg">
                            <div className="flex items-center gap-2 mb-2 text-gray-700 dark:text-gray-300">
                                <BarChart3 className="w-4 h-4" />
                                <span className="text-sm font-medium">價格走勢圖</span>
                            </div>
                            <ResponsiveContainer width="100%" height={200}>
                                <LineChart data={message.chart}>
                                    <CartesianGrid strokeDasharray="3 3" className="dark:stroke-gray-700" />
                                    <XAxis
                                        dataKey="date"
                                        className="text-xs"
                                        stroke="currentColor"
                                    />
                                    <YAxis
                                        className="text-xs"
                                        stroke="currentColor"
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'var(--color-bg)',
                                            border: '1px solid var(--color-border)'
                                        }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="price"
                                        stroke="#3b82f6"
                                        strokeWidth={2}
                                        dot={false}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    )}
                </div>

                {/* 時間戳記 */}
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {message.timestamp.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })}
                </div>
            </div>
        </div>
    )
}
