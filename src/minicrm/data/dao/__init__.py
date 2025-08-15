"""
数据访问对象模块

提供所有数据访问对象的实现，严格遵循：
- 单一职责原则
- 接口隔离原则
- 依赖倒置原则
"""

from .base_dao import BaseDAO
from .customer_dao import CustomerDAO
from .supplier_dao import SupplierDAO


__all__ = [
    "BaseDAO",
    "CustomerDAO",
    "SupplierDAO",
]
