"""
MiniCRM 页面管理器 - 兼容性导入模块

为了保持向后兼容性，此文件重新导出新的模块化页面管理组件。
实际实现已迁移到 page_management 模块中。

⚠️ 注意：此文件仅用于兼容性，新代码请直接使用 page_management 模块。

文件拆分说明：
- 原文件 1201行 → 拆分为8个文件，每个≤400行
- 符合MiniCRM模块化开发标准
- 保持完整的向后兼容性
"""

# 重新导出所有类以保持向后兼容性
from .page_management import (
    BasePage,
    BreadcrumbWidget,
    NavigationHistory,
    NavigationHistoryWidget,
    NavigationToolbar,
    PageInfo,
    PageManager,
    PageManagerWidget,
    PageRouter,
    PageTransition,
)


# 保持原有的导入方式可用
__all__ = [
    "PageInfo",
    "NavigationHistory",
    "PageManager",
    "PageRouter",
    "PageTransition",
    "BreadcrumbWidget",
    "BasePage",
    "NavigationHistoryWidget",
    "NavigationToolbar",
    "PageManagerWidget",
]
