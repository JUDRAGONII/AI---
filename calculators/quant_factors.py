"""
量化因子計算模組
計算六大量化因子分數
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger


class QuantFactorCalculator:
    """量化因子計算器"""
    
    @staticmethod
    def normalize_score(values: pd.Series, ascending: bool = True) -> pd.Series:
        """
        將數值標準化至 0-100 分
        
        Args:
            values: 原始數值
            ascending: True 表示數值越大分數越高
        
        Returns:
            0-100 分數
        """
        # 移除 NaN
        clean_values = values.dropna()
        
        if len(clean_values) == 0:
            return pd.Series(50, index=values.index)  # 預設 50 分
        
        # 使用百分位排名
        rank_pct = clean_values.rank(pct=True)
        
        if not ascending:
            rank_pct = 1 - rank_pct
        
        # 轉換為 0-100
        scores = rank_pct * 100
        
        # 填補原始 NaN 位置
        result = pd.Series(index=values.index, dtype=float)
        result[clean_values.index] = scores
        result = result.fillna(50)  # NaN 給中間分數
        
        return result
    
    @classmethod
    def calculate_value_score(cls, df: pd.DataFrame) -> Tuple[pd.Series, Dict]:
        """
        計算價值因子分數
        
        Args:
            df: 包含價值相關指標的 DataFrame
            需要欄位：pe_ratio, pb_ratio, dividend_yield, ev_ebitda
        
        Returns:
            (綜合分數, 各指標分數)
        """
        scores = {}
        
        # P/E (本益比) - 越低越好
        if 'pe_ratio' in df.columns:
            scores['pe'] = cls.normalize_score(df['pe_ratio'], ascending=False)
        
        # P/B (股價淨值比) - 越低越好
        if 'pb_ratio' in df.columns:
            scores['pb'] = cls.normalize_score(df['pb_ratio'], ascending=False)
        
        # 股息殖利率 - 越高越好
        if 'dividend_yield' in df.columns:
            scores['div_yield'] = cls.normalize_score(df['dividend_yield'], ascending=True)
        
        # EV/EBITDA - 越低越好
        if 'ev_ebitda' in df.columns:
            scores['ev_ebitda'] = cls.normalize_score(df['ev_ebitda'], ascending=False)
        
        # 綜合分數（平均）
        if scores:
            value_score = pd.concat(scores.values(), axis=1).mean(axis=1)
        else:
            value_score = pd.Series(50, index=df.index)
        
        return value_score, scores
    
    @classmethod
    def calculate_quality_score(cls, df: pd.DataFrame) -> Tuple[pd.Series, Dict]:
        """
        計算品質因子分數
        
        Args:
            df: 包含品質相關指標的 DataFrame
            需要欄位：roe, roa, debt_to_equity, gross_margin
        
        Returns:
            (綜合分數, 各指標分數)
        """
        scores = {}
        
        # ROE (股東權益報酬率) - 越高越好
        if 'roe' in df.columns:
            scores['roe'] = cls.normalize_score(df['roe'], ascending=True)
        
        # ROA (資產報酬率) - 越高越好
        if 'roa' in df.columns:
            scores['roa'] = cls.normalize_score(df['roa'], ascending=True)
        
        # 負債比 - 越低越好
        if 'debt_to_equity' in df.columns:
            scores['debt'] = cls.normalize_score(df['debt_to_equity'], ascending=False)
        
        # 毛利率 - 越高越好
        if 'gross_margin' in df.columns:
            scores['margin'] = cls.normalize_score(df['gross_margin'], ascending=True)
        
        # 綜合分數
        if scores:
            quality_score = pd.concat(scores.values(), axis=1).mean(axis=1)
        else:
            quality_score = pd.Series(50, index=df.index)
        
        return quality_score, scores
    
    @classmethod
    def calculate_momentum_score(cls, df: pd.DataFrame) -> Tuple[pd.Series, Dict]:
        """
        計算動能因子分數
        
        Args:
            df: 包含動能相關指標的 DataFrame
            需要欄位：rsi_14, relative_return_1m, relative_return_3m, distance_from_52w_high
        
        Returns:
            (綜合分數, 各指標分數)
        """
        scores = {}
        
        # RSI - 50-70 區間較佳
        if 'rsi_14' in df.columns:
            rsi_optimal = 60
            rsi_distance = abs(df['rsi_14'] - rsi_optimal)
            scores['rsi'] = cls.normalize_score(rsi_distance, ascending=False)
        
        # 1個月相對報酬 - 越高越好
        if 'relative_return_1m' in df.columns:
            scores['ret_1m'] = cls.normalize_score(df['relative_return_1m'], ascending=True)
        
        # 3個月相對報酬 - 越高越好
        if 'relative_return_3m' in df.columns:
            scores['ret_3m'] = cls.normalize_score(df['relative_return_3m'], ascending=True)
        
        # 距52週高點距離 - 越接近越好
        if 'distance_from_52w_high' in df.columns:
            scores['high_dist'] = cls.normalize_score(df['distance_from_52w_high'], ascending=False)
        
        # 綜合分數
        if scores:
            momentum_score = pd.concat(scores.values(), axis=1).mean(axis=1)
        else:
            momentum_score = pd.Series(50, index=df.index)
        
        return momentum_score, scores
    
    @classmethod
    def calculate_size_score(cls, df: pd.DataFrame) -> pd.Series:
        """
        計算規模因子分數
        
        Args:
            df: 包含 market_cap 的 DataFrame
        
        Returns:
            規模分數
        """
        if 'market_cap' in df.columns:
            # 市值越大分數越高（大型股偏好）
            return cls.normalize_score(df['market_cap'], ascending=True)
        else:
            return pd.Series(50, index=df.index)
    
    @classmethod
    def calculate_volatility_score(cls, df: pd.DataFrame) -> Tuple[pd.Series, Dict]:
        """
        計算波動率因子分數
        
        Args:
            df: 包含波動率相關指標的 DataFrame
            需要欄位：volatility_1y, beta
        
        Returns:
            (綜合分數, 各指標分數)
        """
        scores = {}
        
        # 波動率 - 適中較好（過高過低都不好）
        if 'volatility_1y' in df.columns:
            optimal_vol = df['volatility_1y'].median()
            vol_distance = abs(df['volatility_1y'] - optimal_vol)
            scores['vol'] = cls.normalize_score(vol_distance, ascending=False)
        
        # Beta - 接近 1 較好
        if 'beta' in df.columns:
            beta_distance = abs(df['beta'] - 1.0)
            scores['beta'] = cls.normalize_score(beta_distance, ascending=False)
        
        # 綜合分數
        if scores:
            volatility_score = pd.concat(scores.values(), axis=1).mean(axis=1)
        else:
            volatility_score = pd.Series(50, index=df.index)
        
        return volatility_score, scores
    
    @classmethod
    def calculate_growth_score(cls, df: pd.DataFrame) -> Tuple[pd.Series, Dict]:
        """
        計算成長因子分數
        
        Args:
            df: 包含成長相關指標的 DataFrame
            需要欄位：revenue_cagr_3y, eps_cagr_3y
        
        Returns:
            (綜合分數, 各指標分數)
        """
        scores = {}
        
        # 營收成長率 - 越高越好
        if 'revenue_cagr_3y' in df.columns:
            scores['revenue'] = cls.normalize_score(df['revenue_cagr_3y'], ascending=True)
        
        # EPS 成長率 - 越高越好
        if 'eps_cagr_3y' in df.columns:
            scores['eps'] = cls.normalize_score(df['eps_cagr_3y'], ascending=True)
        
        # 綜合分數
        if scores:
            growth_score = pd.concat(scores.values(), axis=1).mean(axis=1)
        else:
            growth_score = pd.Series(50, index=df.index)
        
        return growth_score, scores
    
    @classmethod
    def calculate_total_score(cls, df: pd.DataFrame, weights: Dict[str, float] = None) -> pd.Series:
        """
        計算總分（加權平均）
        
        Args:
            df: 包含各因子分數的 DataFrame
            weights: 各因子權重字典，預設為均等權重
        
        Returns:
            總分序列
        """
        if weights is None:
            # 預設均等權重
            weights = {
                'value': 1.0,
                'quality': 1.0,
                'momentum': 1.0,
                'size': 0.5,      # 規模權重較低
                'volatility': 0.5,  # 波動率權重較低
                'growth': 1.0
            }
        
        factor_columns = {
            'value': 'value_score',
            'quality': 'quality_score',
            'momentum': 'momentum_score',
            'size': 'size_score',
            'volatility': 'volatility_score',
            'growth': 'growth_score'
        }
        
        total_weight = sum(weights.values())
        total_score = pd.Series(0.0, index=df.index)
        
        for factor, col_name in factor_columns.items():
            if col_name in df.columns:
                total_score += df[col_name] * weights[factor]
        
        # 正規化至 0-100
        total_score = (total_score / total_weight)
        
        return total_score


# 使用範例
if __name__ == '__main__':
    # 測試資料
    test_data = pd.DataFrame({
        'pe_ratio': [15.2, 22.5, 10.8, 30.1],
        'pb_ratio': [2.1, 3.5, 1.2, 4.8],
        'dividend_yield': [0.025, 0.015, 0.040, 0.010],
        'roe': [0.15, 0.10, 0.20, 0.08],
        'roa': [0.08, 0.05, 0.12, 0.04],
    })
    
    calc = QuantFactorCalculator()
    value_score, _ = calc.calculate_value_score(test_data)
    quality_score, _ = calc.calculate_quality_score(test_data)
    
    print("價值因子分數:")
    print(value_score)
    print("\n品質因子分數:")
    print(quality_score)
