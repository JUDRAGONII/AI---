// App.jsx - 主應用程式入口
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ShareholderAnalysis from './pages/ShareholderAnalysis'
import FactorDashboard from './pages/FactorDashboard'
import AIInsights from './pages/AIInsights'
import TechnicalAnalysis from './pages/TechnicalAnalysis'
import Portfolio from './pages/Portfolio'  // 新的投資組合頁面
import PortfolioManagement from './pages/PortfolioManagement'
import NewsManagement from './pages/NewsManagement'
import Settings from './pages/Settings'
import PortfolioOptimization from './pages/PortfolioOptimization'
import StrategyBacktesting from './pages/StrategyBacktesting'
import PortfolioStressTesting from './pages/PortfolioStressTesting'
import InvestmentGoals from './pages/InvestmentGoals'
import AIChatAnalyst from './pages/AIChatAnalyst'
import SimilarAssetsFinder from './pages/SimilarAssetsFinder'
import SmartAlertSystem from './pages/SmartAlertSystem'
import PortfolioDetails from './pages/PortfolioDetails'
import TransactionLog from './pages/TransactionLog'  // 交易日誌
import AccountManagement from './pages/AccountManagement'
import APIManagement from './pages/APIManagement'
import ReportCenter from './pages/ReportCenter'
import DynamicIntelligence from './pages/DynamicIntelligence'
import AIPortfolioStrategy from './pages/AIPortfolioStrategy'
import WhatIfSimulator from './pages/WhatIfSimulator'
import BehavioralCoach from './pages/BehavioralCoach'
import SmartEnhancer from './pages/SmartEnhancer'
import CatalystRanker from './pages/CatalystRanker'
import StrategyTracker from './pages/StrategyTracker'
import DeviationHeatmap from './pages/DeviationHeatmap'
import GoalCalibrator from './pages/GoalCalibrator'
import TacticalPlanner from './pages/TacticalPlanner'
import ScenarioHedging from './pages/ScenarioHedging'
import AIHouseView from './pages/AIHouseView'
import StockListTW from './pages/StockListTW'
import StockListUS from './pages/StockListUS'
import StockDetailDemo from './pages/StockDetailDemo'
import MarketOverview from './pages/MarketOverview'
import DepthAnalysis from './pages/DepthAnalysis'  // 股價深度分析
import ChipsAnalysis from './pages/ChipsAnalysis'  // 籌碼分析
import MacroEconomyView from './pages/MacroEconomyView'  // 宏觀經濟
import MarketPulse from './pages/MarketPulse'  // 市場脈搏
import TaxCalculator from './pages/TaxCalculator'

// 佔位符頁面（未來實作）
const ComingSoon = ({ title }) => (
  <div className="flex items-center justify-center h-full">
    <div className="text-center">
      <h2 className="text-2xl font-bold mb-2">{title}</h2>
      <p className="text-gray-500 dark:text-gray-400">功能開發中，敬請期待...</p>
    </div>
  </div>
)

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="ai-insights" element={<AIInsights />} />
            <Route path="factors" element={<FactorDashboard />} />
            <Route path="shareholder" element={<ShareholderAnalysis />} />
            <Route path="technical" element={<TechnicalAnalysis />} />
            <Route path="portfolio" element={<PortfolioManagement />} />
            <Route path="news" element={<NewsManagement />} />
            <Route path="settings" element={<Settings />} />

            {/* 進階功能 */}
            <Route path="optimization" element={<PortfolioOptimization />} />
            <Route path="backtesting" element={<StrategyBacktesting />} />
            <Route path="stress-testing" element={<PortfolioStressTesting />} />
            <Route path="goals" element={<InvestmentGoals />} />
            <Route path="ai-chat" element={<AIChatAnalyst />} />
            <Route path="similar-assets" element={<SimilarAssetsFinder />} />
            <Route path="alerts" element={<SmartAlertSystem />} />
            <Route path="portfolio-detail" element={<Portfolio />} />  {/* 投資組合明細 */}
            <Route path="portfolio-details" element={<PortfolioDetails />} />
            <Route path="transactions" element={<TransactionLog />} />
            <Route path="account" element={<AccountManagement />} />
            <Route path="api-management" element={<APIManagement />} />
            <Route path="reports" element={<ReportCenter />} />
            <Route path="intelligence" element={<DynamicIntelligence />} />
            <Route path="ai-strategy" element={<AIPortfolioStrategy />} />
            <Route path="what-if" element={<WhatIfSimulator />} />
            <Route path="behavioral-coach" element={<BehavioralCoach />} />
            <Route path="smart-enhancer" element={<SmartEnhancer />} />
            <Route path="catalyst-ranker" element={<CatalystRanker />} />
            <Route path="strategy-tracker" element={<StrategyTracker />} />
            <Route path="deviation-heatmap" element={<DeviationHeatmap />} />
            <Route path="goal-calibrator" element={<GoalCalibrator />} />
            <Route path="tactical-planner" element={<TacticalPlanner />} />
            <Route path="scenario-hedging" element={<ScenarioHedging />} />
            <Route path="ai-house-view" element={<AIHouseView />} />
            <Route path="stock-list-tw" element={<StockListTW />} />
            <Route path="stock-list-us" element={<StockListUS />} />
            <Route path="stock/:code" element={<StockDetailDemo />} />
            <Route path="tax-calculator" element={<TaxCalculator />} />
            <Route path="market-overview" element={<MarketOverview />} />
            <Route path="depth-analysis" element={<DepthAnalysis />} />
            <Route path="chips-analysis" element={<ChipsAnalysis />} />
            <Route path="macro-economy" element={<MacroEconomyView />} />
            <Route path="market-pulse" element={<MarketPulse />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
