"""MiniCRM - 客户关系管理系统

一个基于Python和tkinter/ttk的跨平台客户关系管理应用程序,
专为板材行业设计,支持客户管理、供应商管理、报价比对等功能.

版本: 1.0.0
作者: MiniCRM开发团队
"""

__version__ = "1.0.0"
__author__ = "MiniCRM开发团队"
__description__ = "跨平台客户关系管理系统"

# 导出核心模块
from .core.constants import (
    ContractStatus,
    CustomerLevel,
    InteractionType,
    QuoteStatus,
    ServiceTicketStatus,
    SupplierLevel,
)
from .core.exceptions import (
    BusinessLogicError,
    ConfigurationError,
    DatabaseError,
    MiniCRMError,
    UIError,
    ValidationError,
)


__all__ = [
    # 异常类
    "MiniCRMError",
    "ValidationError",
    "DatabaseError",
    "BusinessLogicError",
    "ConfigurationError",
    "UIError",
    # 枚举常量
    "CustomerLevel",
    "SupplierLevel",
    "InteractionType",
    "ContractStatus",
    "QuoteStatus",
    "ServiceTicketStatus",
]
