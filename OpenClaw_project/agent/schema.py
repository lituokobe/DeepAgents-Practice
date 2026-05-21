"""
自定义数据结构定义
包含运行时上下文、用户偏好等类型定义。
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProcurementContext:
    """
    运行时上下文，由调用方在 invoke 时传入。
    用于传递当前用户身份等基础信息。
    """
    user_id: str                # 必填，用户唯一标识
    username: str               # 必填，用户姓名/登录名


@dataclass
class UserPreferences:
    """
    用户偏好数据结构，存储在长期记忆文件中。
    对应 /memories/{user_id}/preferences.md 的内容。
    """
    preferred_output: Optional[str] = None         # 'table' 或 'chart'
    preferred_chart_type: Optional[str] = None      # 'bar', 'line', 'pie' 等
    preferred_currency: Optional[str] = None        # 'CNY', 'USD' 等
    preferred_language: Optional[str] = None        # 'zh', 'en' 等
    recent_suppliers: list[str] = None              # 近期使用的供应商列表
    recent_queries: list[str] = None                # 近期分析需求摘要列表

    def __post_init__(self):
        if self.recent_suppliers is None:
            self.recent_suppliers = []
        if self.recent_queries is None:
            self.recent_queries = []