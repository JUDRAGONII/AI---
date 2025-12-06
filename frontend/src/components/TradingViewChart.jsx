import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

/**
 * TradingView Lightweight Charts 組件
 * 支援 K 線圖、成交量與技術指標疊加
 */
const TradingViewChart = ({ data, indicators = {}, signals = [], height = 500 }) => {
    const chartContainerRef = useRef(null);
    const chartRef = useRef(null);
    const candleSeriesRef = useRef(null);
    const volumeSeriesRef = useRef(null);
    const indicatorSeriesRef = useRef({});

    useEffect(() => {
        if (!chartContainerRef.current || !data || data.length === 0) return;

        // 創建圖表
        const chart = createChart(chartContainerRef.current, {
            width: chartContainerRef.current.clientWidth,
            height: height,
            layout: {
                background: { color: 'transparent' },
                textColor: '#d1d5db',
            },
            grid: {
                vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
                horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
            },
            crosshair: {
                mode: 1, // Normal mode
            },
            rightPriceScale: {
                borderColor: 'rgba(197, 203, 206, 0.4)',
            },
            timeScale: {
                borderColor: 'rgba(197, 203, 206, 0.4)',
                timeVisible: true,
                secondsVisible: false,
            },
        });

        chartRef.current = chart;

        // 創建 K 線圖序列
        const candleSeries = chart.addCandlestickSeries({
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderVisible: false,
            wickUpColor: '#26a69a',
            wickDownColor: '#ef5350',
        });

        candleSeriesRef.current = candleSeries;

        // 設定 K 線數據
        const candleData = data.map(d => ({
            time: d.time || d.date,
            open: parseFloat(d.open),
            high: parseFloat(d.high),
            low: parseFloat(d.low),
            close: parseFloat(d.close),
        }));

        candleSeries.setData(candleData);

        // 創建成交量序列（如果有數據）
        if (data[0]?.volume !== undefined) {
            const volumeSeries = chart.addHistogramSeries({
                color: '#26a69a',
                priceFormat: {
                    type: 'volume',
                },
                priceScaleId: 'volume',
                scaleMargins: {
                    top: 0.8,
                    bottom: 0,
                },
            });

            volumeSeriesRef.current = volumeSeries;

            const volumeData = data.map((d, index) => {
                const previousClose = index > 0 ? parseFloat(data[index - 1].close) : parseFloat(d.open);
                const currentClose = parseFloat(d.close);

                return {
                    time: d.time || d.date,
                    value: parseFloat(d.volume),
                    color: currentClose >= previousClose ? 'rgba(38, 166, 154, 0.5)' : 'rgba(239, 83, 80, 0.5)',
                };
            });

            volumeSeries.setData(volumeData);
        }

        // 添加技術指標
        if (indicators.ma) {
            const maSeries = chart.addLineSeries({
                color: '#2962FF',
                lineWidth: 2,
                title: `MA${indicators.ma.period || ''}`,
            });
            indicatorSeriesRef.current.ma = maSeries;

            if (Array.isArray(indicators.ma.data) && indicators.ma.data.length > 0) {
                maSeries.setData(indicators.ma.data.map(d => ({
                    time: d.time || d.date,
                    value: parseFloat(d.value),
                })));
            }
        }

        if (indicators.rsi) {
            // RSI 需要獨立的價格軸
            const rsiSeries = chart.addLineSeries({
                color: '#FF6D00',
                lineWidth: 2,
                title: 'RSI',
                priceScaleId: 'rsi',
                scaleMargins: {
                    top: 0.8,
                    bottom: 0,
                },
            });
            indicatorSeriesRef.current.rsi = rsiSeries;

            if (Array.isArray(indicators.rsi.data) && indicators.rsi.data.length > 0) {
                rsiSeries.setData(indicators.rsi.data.map(d => ({
                    time: d.time || d.date,
                    value: parseFloat(d.value),
                })));
            }
        }

        if (indicators.macd) {
            // MACD 需要獨立的價格軸
            const macdSeries = chart.addHistogramSeries({
                color: '#2962FF',
                title: 'MACD',
                priceScaleId: 'macd',
                scaleMargins: {
                    top: 0.8,
                    bottom: 0,
                },
            });
            indicatorSeriesRef.current.macd = macdSeries;

            if (Array.isArray(indicators.macd.data) && indicators.macd.data.length > 0) {
                macdSeries.setData(indicators.macd.data.map(d => ({
                    time: d.time || d.date,
                    value: parseFloat(d.value), // Histogram value
                    color: parseFloat(d.value) >= 0 ? '#26a69a' : '#ef5350',
                })));
            }
        }

        if (indicators.bollinger) {
            // 布林通道疊加在主圖
            const upperSeries = chart.addLineSeries({
                color: 'rgba(4, 111, 232, 0.5)',
                lineWidth: 1,
                title: 'BB Upper',
            });
            const lowerSeries = chart.addLineSeries({
                color: 'rgba(4, 111, 232, 0.5)',
                lineWidth: 1,
                title: 'BB Lower',
            });

            indicatorSeriesRef.current.bollingerUpper = upperSeries;
            indicatorSeriesRef.current.bollingerLower = lowerSeries;

            if (Array.isArray(indicators.bollinger.data) && indicators.bollinger.data.length > 0) {
                upperSeries.setData(indicators.bollinger.data.map(d => ({
                    time: d.time || d.date,
                    value: parseFloat(d.upper),
                })));
                lowerSeries.setData(indicators.bollinger.data.map(d => ({
                    time: d.time || d.date,
                    value: parseFloat(d.lower),
                })));
            }
        }

        // 渲染訊號標記 (Markers)
        if (signals && signals.length > 0) {
            const markers = signals.map(signal => ({
                time: signal.date,
                position: signal.position || (signal.action === 'buy' ? 'belowBar' : 'aboveBar'),
                color: signal.action === 'buy' ? '#26a69a' : '#ef5350',
                shape: signal.action === 'buy' ? 'arrowUp' : 'arrowDown',
                text: signal.description,
                size: 1, // default size
            }));
            candleSeries.setMarkers(markers);
        } else {
            candleSeries.setMarkers([]);
        }

        // 響應式調整
        const handleResize = () => {
            if (chartContainerRef.current && chartRef.current) {
                chartRef.current.applyOptions({
                    width: chartContainerRef.current.clientWidth,
                });
            }
        };

        window.addEventListener('resize', handleResize);

        // 自動縮放到適合的範圍
        chart.timeScale().fitContent();

        // 清理函數
        return () => {
            window.removeEventListener('resize', handleResize);
            if (chartRef.current) {
                chartRef.current.remove();
                chartRef.current = null;
            }
        };
    }, [data, indicators, signals, height]);

    return (
        <div
            ref={chartContainerRef}
            className="w-full rounded-lg bg-gray-800/50"
            style={{ height: `${height}px` }}
        />
    );
};

export default TradingViewChart;
