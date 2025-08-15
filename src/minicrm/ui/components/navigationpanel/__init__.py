"""
MiniCRM 导航面板模块

提供完整的导航面板功能，包括导航项管理、样式配置等
"""

from .navigation_panel import NavigationPanel
from .navigation_types import NavigationItem


__all__ = [
    "NavigationPanel",
    "NavigationItem",
]
