"""
MiniCRM 用户界面模块

包含所有用户界面相关的组件和功能：
- 基础UI组件类
- 主窗口和布局管理
- 通用UI组件
- 主题和样式管理
- 图表和可视化组件
- 异步操作支持

这个模块实现了MiniCRM的完整用户界面，基于PySide6(Qt)框架构建。
所有UI组件都继承自基础组件类，提供统一的接口和行为。
"""

# 版本信息
__version__ = "1.0.0"

# 导入基础UI组件
from .base_widget import AsyncWorker, BaseDialog, BasePanel, BaseWidget, run_async


# 导入主要UI组件（将在后续任务中实现）
# from .main_window import MainWindow
# from .components import *
# from .themes import *

# 导出的公共接口
__all__ = [
    # 基础组件
    "BaseWidget",
    "BaseDialog",
    "BasePanel",
    "AsyncWorker",
    "run_async",
    # 主要组件（将在后续任务中添加）
    # "MainWindow",
]
