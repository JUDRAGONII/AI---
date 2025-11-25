"""
AI 模組

提供 Gemini API 整合與報告生成功能
"""

from .gemini_client import GeminiClient
from .report_generator import DailyReportGenerator, DecisionTemplateGenerator

__all__ = [
    'GeminiClient',
    'DailyReportGenerator',
    'DecisionTemplateGenerator'
]

__version__ = '1.0.0'
