                                <XAxis dataKey="date" stroke="#9CA3AF" />
                                <YAxis stroke="#9CA3AF" />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1F2937',
                                        border: 'none',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="price"
                                    stroke="#F59E0B"
                                    strokeWidth={2}
                                    name="黃金價格"
                                />
                            </LineChart >
                        </ResponsiveContainer >
                    ) : (
    <div className="text-center py-16 text-gray-500">
        <p>暫無黃金數據</p>
        <p className="text-sm mt-2">請執行數據同步腳本</p>
    </div>
)}
                </div >

    {/* 匯率走勢 */ }
    < div className = "bg-white dark:bg-gray-800 rounded-lg p-6 shadow-lg" >
        <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">
            美元台幣30日走勢
        </h2>
{
    forexRates.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
            <LineChart data={forexRates}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip
                    contentStyle={{
                        backgroundColor: '#1F2937',
                        border: 'none',
                        borderRadius: '8px'
                    }}
                />
                <Line
                    type="monotone"
                    dataKey="rate"
                    stroke="#10B981"
                    strokeWidth={2}
                    name="匯率"
                />
            </LineChart>
        </ResponsiveContainer>
    ) : (
    <div className="text-center py-16 text-gray-500">
        <p>暫無匯率數據</p>
        <p className="text-sm mt-2">請執行數據同步腳本</p>
    </div>
)
}
                </div >
            </div >
        </div >
    );
};

export default MarketOverview;
