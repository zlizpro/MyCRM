"""
MiniCRM 数据表格组件

重构后的数据表格，使用模块化设计。
为了保持向后兼容性，这里重新导出新的模块化组件。
"""

# 重新导出新的模块化组件
from .table.data_table import DataTable
from .table.table_data_manager import SortOrder, TableDataManager
from .table.table_export_manager import TableExportManager
from .table.table_filter_manager import TableFilterManager
from .table.table_pagination_manager import TablePaginationManager


# 保持向后兼容性
__all__ = [
    "DataTable",
    "SortOrder",
    "TableDataManager",
    "TableExportManager",
    "TableFilterManager",
    "TablePaginationManager",
]
