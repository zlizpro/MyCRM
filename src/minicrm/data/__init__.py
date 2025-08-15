"""
MiniCRM 数据访问层模块

包含所有数据访问相关的功能：
- 数据库管理
- 数据访问对象(DAO)
- 基础DAO类
- CRUD操作混入
- 数据迁移

这个模块负责所有与数据存储相关的操作，为上层服务提供数据访问接口。
数据层不应该包含业务逻辑，只负责数据的存储和检索。
"""

# 版本信息
__version__ = "1.0.0"

# 导入核心组件
from .base_dao import BaseDAO
from .dao.business_dao import BusinessDAO

# 导入具体DAO类
from .dao.customer_dao import CustomerDAO
from .dao.supplier_dao import SupplierDAO
from .database import DatabaseManager


# 导出的公共接口
__all__ = [
    # 数据库管理
    "DatabaseManager",
    # 基础DAO
    "BaseDAO",
    # 具体DAO
    "CustomerDAO",
    "SupplierDAO",
    "BusinessDAO",
]
