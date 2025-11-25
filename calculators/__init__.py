"""
量化因子計算器模組

提供六大因子計算功能：
- 價值 (Value)
- 品質 (Quality)
- 動能 (Momentum)
- 規模 (Size)
- 波動率 (Volatility)
- 成長 (Growth)
"""

from .factor_engine import FactorEngine
from .value_factor import ValueFactorCalculator
from .quality_factor import QualityFactorCalculator
from .momentum_factor import MomentumFactorCalculator
from .other_factors import SizeFactorCalculator, VolatilityFactorCalculator, GrowthFactorCalculator

__all__ = [
    'FactorEngine',
    'ValueFactorCalculator',
    'QualityFactorCalculator',
    'MomentumFactorCalculator',
    'SizeFactorCalculator',
    'VolatilityFactorCalculator',
    'GrowthFactorCalculator'
]

__version__ = '1.0.0'
