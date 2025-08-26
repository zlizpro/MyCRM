"""MiniCRM TTK基础框架

这个模块提供了TTK基础框架的核心组件,包括:
- BaseWindow: TTK基础窗口类
- BaseWidget: TTK基础组件类
- LayoutManager: 布局管理器
- EventManager: 事件管理器
- StyleManager: 样式管理器
- 适配器层: Qt到TTK的适配器

作者: MiniCRM开发团队
版本: 1.0.0
"""

from .base_widget import BaseWidget
from .base_window import BaseWindow
from .layout_manager import LayoutManager


# from .event_manager import EventManager  # 将在子任务1.2中实现
# from .style_manager import StyleManager  # 将在子任务1.3中实现


__all__ = [
    "BaseWidget",
    "BaseWindow",
    "LayoutManager",
]  # "EventManager", "StyleManager" 将在后续子任务中添加

__version__ = "1.0.0"
