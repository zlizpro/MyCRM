"""
MiniCRM 响应式布局系统

提供完整的响应式布局解决方案，包括：
- 响应式布局管理
- 自动缩放组件
- 断点管理系统
- 高DPI适配

使用示例:
    from minicrm.ui.responsive import ResponsiveLayoutManager, ResponsiveWidget

    layout_manager = ResponsiveLayoutManager()
    widget = ResponsiveWidget()
    widget.set_layout_manager(layout_manager)
"""

from .layout_manager import ResponsiveLayoutManager
from .responsive_widgets import AutoScaleWidget, ResponsiveWidget
from .types import BreakPoint, LayoutConfig, ScreenSize


__all__ = [
    # 类型定义
    "BreakPoint",
    "LayoutConfig",
    "ScreenSize",
    # 核心组件
    "ResponsiveLayoutManager",
    "ResponsiveWidget",
    "AutoScaleWidget",
]
