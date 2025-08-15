"""
MiniCRM 基础数据访问对象

重构后的基础DAO，使用模块化设计。
为了保持向后兼容性，这里重新导出新的模块化组件。
"""

# 重新导出新的模块化组件
from .dao.base_dao import BaseDAO
from .dao.database_executor import DatabaseExecutor
from .dao.model_converter import ModelConverter
from .dao.sql_builder import SQLBuilder


# 保持向后兼容性
__all__ = [
    "BaseDAO",
    "SQLBuilder",
    "DatabaseExecutor",
    "ModelConverter",
]
