"""
MiniCRM 导入导出UI模块

提供模块化的数据导入导出界面组件.

模块结构:
- workers/: 后台工作线程
- panels/: UI面板组件
- main_panel.py: 主协调面板

使用示例:
    from minicrm.ui.import_export import ImportExportPanel

    panel = ImportExportPanel(import_service)
"""

from .main_panel import ImportExportPanel


__all__ = ["ImportExportPanel"]
