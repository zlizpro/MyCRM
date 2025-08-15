"""MiniCRM - 现代化模块化CRM系统

这是一个基于PySide6的现代化CRM系统，专为板材行业设计。
系统采用模块化架构，集成了transfunctions可复用函数库。

主要功能：
- 客户信息管理
- 供应商管理
- 报价比对
- 合同管理
- 售后跟踪
- 数据分析和报表

技术栈：
- GUI: PySide6
- 数据库: SQLite
- 文档处理: docxtpl, reportlab
- 图表: matplotlib
"""

__version__ = "0.1.0"
__author__ = "MiniCRM Team"
__email__ = "team@minicrm.com"

# 导出主要组件
__all__ = [
    "__version__",
    "__author__",
    "__email__",
]
