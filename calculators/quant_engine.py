"""
進階量化分析引擎
包含蒙地卡羅模擬、效率前緣優化、風險因子分析
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from loguru import logger
from scipy.optimize import minimize
from datetime import datetime

class MonteCarloSimulator:
    """蒙地卡羅模擬器"""
    
    def __init__(self, returns_data: pd.DataFrame):
        """
        初始化模擬器
        :param returns_data: 歷史日收益率 DataFrame (每列為一資產)
        """
        self.returns = returns_data
        self.mean_returns = returns_data.mean()
        self.cov_matrix = returns_data.cov()
        
    def simulate(self, weights: List[float], num_simulations: int = 1000, 
                 time_horizon: int = 252, initial_capital: float = 1000000) -> Dict:
        """
        執行模擬
        """
        logger.info(f"執行蒙地卡羅模擬: {num_simulations} 次, {time_horizon} 天")
        
        try:
            # 轉換權重為 array
            weights = np.array(weights)
            
            # 確保權重和為 1 (簡單處理)
            weights = weights / np.sum(weights)
            
            # 使用 Cholesky 分解生成相關聯的隨機亂數
            # 矩陣分解: L * L.T = Covariance
            L = np.linalg.cholesky(self.cov_matrix)
            
            # 模擬結果容器
            simulation_paths = np.zeros((num_simulations, time_horizon))
            final_values = np.zeros(num_simulations)
            
            # 預期日收益與波動度 (Portfolio level)
            port_mean_daily = np.sum(self.mean_returns * weights)
            # port_daily_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights))) # 簡化假設
            
            for i in range(num_simulations):
                # 簡單幾何布朗運動 (GBM) 多資產模擬較複雜，這裡採用相關聯的隨機收益率疊加方法
                # 生成不相關的隨機數
                uncorrelated_randoms = np.random.normal(0, 1, size=(self.returns.shape[1], time_horizon))
                
                # 轉換為相關聯的隨機數
                correlated_randoms = np.dot(L, uncorrelated_randoms)
                
                # 計算各資產每日模擬收益率
                # Return = Mean + Random * Volatility ??? 
                # 更準確的方法: Sim_Ret = Mean + Correlated_Random
                # 這裡直接用多元常態分佈抽樣的收益率
                
                simulated_returns = self.mean_returns.values.reshape(-1, 1) + correlated_randoms
                
                # 組合每日收益率 (加權)
                portfolio_sim_daily_returns = np.dot(weights, simulated_returns)
                
                # 計算路徑 (累積收益)
                cumulative_returns = np.cumprod(1 + portfolio_sim_daily_returns)
                path = initial_capital * cumulative_returns
                
                simulation_paths[i, :] = path
                final_values[i] = path[-1]
            
            # 計算統計數據
            percentiles = np.percentile(final_values, [5, 50, 95])
            
            # VaR & CVaR (95%)
            # Loss distribution (Profit/Loss)
            pnl = final_values - initial_capital
            var_95 = -np.percentile(pnl, 5) # 5% 最差情況的損失（正數表示損失金額）
            cvar_95 = -np.mean(pnl[pnl <= -var_95]) # 尾部平均損失
            
            # 隨機抽取 20 條路徑供前端繪圖
            indices = np.random.choice(num_simulations, 20, replace=False)
            display_paths = []
            for idx in indices:
                # 降採樣以減少傳輸量 (每 5 天一點)
                # path = simulation_paths[idx][::5]
                # 完整路徑
                path = simulation_paths[idx]
                display_paths.append({
                    "id": int(idx),
                    "data": path.tolist()
                })
            
            return {
                "initial_capital": initial_capital,
                "percentiles": {
                    "p05": float(percentiles[0]),
                    "p50": float(percentiles[1]),
                    "p95": float(percentiles[2])
                },
                "risk_metrics": {
                    "var_95_amount": float(var_95 if var_95 > 0 else 0),
                    "var_95_percent": float(var_95 / initial_capital * 100),
                    "cvar_95_amount": float(cvar_95 if cvar_95 > 0 else 0),
                    "max_drawdown": 0.0 # TODO: 計算模擬路徑的平均最大回撤
                },
                "paths": display_paths
            }
            
        except Exception as e:
            logger.error(f"蒙地卡羅模擬失敗: {e}")
            return {"error": str(e)}


class EfficientFrontierOptimizer:
    """效率前緣優化器"""
    
    def __init__(self, returns_data: pd.DataFrame, risk_free_rate: float = 0.02):
        self.returns = returns_data
        self.mean_returns = returns_data.mean() * 252 # 年化
        self.cov_matrix = returns_data.cov() * 252   # 年化
        self.risk_free_rate = risk_free_rate
        self.num_assets = len(returns_data.columns)
        self.asset_names = returns_data.columns.tolist()
        
    def portfolio_performance(self, weights):
        """計算組合年化收益與波動率"""
        weights = np.array(weights)
        returns = np.sum(self.mean_returns * weights)
        std = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        return returns, std
        
    def negative_sharpe(self, weights):
        """最小化負夏普比率 (即最大化夏普)"""
        p_ret, p_std = self.portfolio_performance(weights)
        return -(p_ret - self.risk_free_rate) / p_std
        
    def minimize_volatility(self, weights):
        """最小化波動率"""
        return self.portfolio_performance(weights)[1]
        
    def optimize(self, points: int = 50) -> Dict:
        """計算效率前緣曲線與關鍵點"""
        logger.info("計算效率前緣...")
        
        args = ()
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(self.num_assets))
        initial_guess = self.num_assets * [1. / self.num_assets,]
        
        # 1. 最小變異組合 (Min Vol)
        min_vol_result = minimize(self.minimize_volatility, initial_guess, method='SLSQP', 
                                 bounds=bounds, constraints=constraints)
        min_vol_ret, min_vol_std = self.portfolio_performance(min_vol_result.x)
        
        # 2. 最大夏普組合 (Max Sharpe)
        max_sharpe_result = minimize(self.negative_sharpe, initial_guess, method='SLSQP', 
                                    bounds=bounds, constraints=constraints)
        max_sharpe_ret, max_sharpe_std = self.portfolio_performance(max_sharpe_result.x)
        
        # 3. 生成前緣曲線 (在 Min Vol Return 和 Max Possible Return 之間插值)
        # 尋找個別資產最高預期收益作為上限
        max_ret_possible = self.mean_returns.max()
        target_returns = np.linspace(min_vol_ret, max_ret_possible, points)
        
        frontier_points = []
        for target in target_returns:
            # 針對每個目標收益，最小化波動率
            cons = (
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: self.portfolio_performance(x)[0] - target}
            )
            res = minimize(self.minimize_volatility, initial_guess, method='SLSQP', 
                          bounds=bounds, constraints=cons)
            if res.success:
                frontier_points.append({
                    "return": float(target),
                    "std": float(res.fun),
                    "sharpe": float((target - self.risk_free_rate) / res.fun)
                })
        
        return {
            "frontier": frontier_points,
            "min_vol_portfolio": {
                "return": float(min_vol_ret),
                "std": float(min_vol_std),
                "weights": dict(zip(self.asset_names, min_vol_result.x.tolist()))
            },
            "max_sharpe_portfolio": {
                "return": float(max_sharpe_ret),
                "std": float(max_sharpe_std),
                "weights": dict(zip(self.asset_names, max_sharpe_result.x.tolist()))
            }
        }


class RiskFactorAnalyzer:
    """風險因子分析器"""
    # 簡化版：實際應使用多因子回歸 (Fama-French)
    # 這裡將計算相對於 Benchmark 的 Alpha, Beta
    
    def __init__(self, portfolio_returns: pd.Series, benchmark_returns: pd.Series, risk_free_rate: float = 0.02):
        # 對齊日期
        df = pd.concat([portfolio_returns, benchmark_returns], axis=1).dropna()
        self.port_ret = df.iloc[:, 0]
        self.bench_ret = df.iloc[:, 1]
        self.rf = risk_free_rate / 252 # 日化
        
    def analyze(self) -> Dict:
        try:
            # 1. Beta 計算 (Cov/Var)
            covariance = np.cov(self.port_ret, self.bench_ret)[0][1]
            variance = np.var(self.bench_ret)
            beta = covariance / variance if variance != 0 else 0
            
            # 2. Alpha 計算 (CAPM)
            # Rp - Rf = Beta * (Rm - Rf) + Alpha
            # Alpha = (Rp - Rf) - Beta * (Rm - Rf)
            # 年化處理
            ann_port_ret = self.port_ret.mean() * 252
            ann_bench_ret = self.bench_ret.mean() * 252
            rf_ann = self.rf * 252
            
            alpha = (ann_port_ret - rf_ann) - beta * (ann_bench_ret - rf_ann)
            
            # 3. Sharpe Ratio
            port_std = self.port_ret.std() * np.sqrt(252)
            sharpe = (ann_port_ret - rf_ann) / port_std if port_std != 0 else 0
            
            # 4. Sortino Ratio (只考慮下行波動)
            downside_returns = self.port_ret[self.port_ret < 0]
            downside_std = downside_returns.std() * np.sqrt(252)
            sortino = (ann_port_ret - rf_ann) / downside_std if downside_std != 0 and not np.isnan(downside_std) else 0
            
            # 5. Max Drawdown
            cumulative = (1 + self.port_ret).cumprod()
            peak = cumulative.expanding(min_periods=1).max()
            drawdown = (cumulative - peak) / peak
            max_drawdown = drawdown.min()
            
            return {
                "alpha": float(alpha),
                "beta": float(beta),
                "sharpe_ratio": float(sharpe),
                "sortino_ratio": float(sortino),
                "max_drawdown": float(max_drawdown),
                "volatility": float(port_std),
                "benchmark_return": float(ann_bench_ret),
                "portfolio_return": float(ann_port_ret)
            }
            
        except Exception as e:
            logger.error(f"風險因子分析失敗: {e}")
            return {}

if __name__ == "__main__":
    # 測試代碼
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=100)
    data = {
        'A': np.random.normal(0.001, 0.02, 100),
        'B': np.random.normal(0.0005, 0.01, 100),
        'C': np.random.normal(0.0015, 0.03, 100)
    }
    df = pd.DataFrame(data, index=dates)
    
    # 測試蒙地卡羅
    sim = MonteCarloSimulator(df)
    res_mc = sim.simulate([0.4, 0.3, 0.3])
    print("MC 95% Value:", res_mc['percentiles']['p95'])
    
    # 測試效率前緣
    opt = EfficientFrontierOptimizer(df)
    res_ef = opt.optimize()
    print("Max Sharpe Ret:", res_ef['max_sharpe_portfolio']['return'])
    
    # 測試風險分析
    analyzer = RiskFactorAnalyzer(df['A'], df['B']) # 假設 B 是大盤
    res_risk = analyzer.analyze()
    print("Alpha:", res_risk['alpha'])
