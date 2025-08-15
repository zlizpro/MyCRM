"""
MiniCRM 页面管理模块

提供完整的页面管理功能，包括页面注册、路由、导航等
"""

# 导出主要类
from .history_widget import NavigationHistoryWidget
from .navigation_widgets import BreadcrumbWidget, NavigationToolbar
from .page_base import BasePage, NavigationHistory, PageInfo
from .page_manager import PageManager
from .page_manager_widget import PageManagerWidget
from .page_router import PageRouter
from .page_transitions import PageTransition


# 版本信息
__version__ = "1.0.0"

# 导出列表
__all__ = [
    # 基础类
    "PageInfo",
    "NavigationHistory",
    "BasePage",
    # 核心管理器
    "PageManager",
    "PageRouter",
    # UI组件
    "BreadcrumbWidget",
    "NavigationToolbar",
    "NavigationHistoryWidget",
    "PageManagerWidget",
    # 动画效果
    "PageTransition",
]
