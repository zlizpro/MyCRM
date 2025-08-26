"""Qt到TTK适配器模块

提供Qt到TTK的适配器层,包括:
- QtToTtkAdapter: Qt到TTK适配器基类
- EventAdapter: 事件适配器
- StyleAdapter: 样式适配器
- 组件映射和转换工具

作者: MiniCRM开发团队
"""

from .event_adapter import EventAdapter
from .qt_to_ttk_adapter import QtToTtkAdapter
from .style_adapter import StyleAdapter


__all__ = ["EventAdapter", "QtToTtkAdapter", "StyleAdapter"]
