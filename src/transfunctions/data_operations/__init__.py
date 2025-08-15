"""
Transfunctions - 数据操作模块

提供可复用的数据访问和操作功能：
- CRUD操作模板
- 数据查询构建器
- 分页处理
- 数据转换工具
"""

from .crud_templates import (
    CRUDTemplate,
    batch_operation_template,
    create_crud_template,
    paginated_search_template,
)
from .data_converter import convert_dict_to_model, convert_row_to_dict
from .query_builder import QueryBuilder, build_search_query


__all__ = [
    # CRUD模板
    "CRUDTemplate",
    "create_crud_template",
    "paginated_search_template",
    "batch_operation_template",
    # 查询构建器
    "QueryBuilder",
    "build_search_query",
    # 数据转换
    "convert_row_to_dict",
    "convert_dict_to_model",
]
