"""MiniCRM核心模块

包含系统的基础组件:异常类、常量定义、工具函数等.
这些组件为整个应用程序提供基础支持.
"""

from .constants import (
    DATABASE_CONFIG,
    DEFAULT_CONFIG,
    UI_CONFIG,
    ContractStatus,
    CustomerLevel,
    InteractionType,
    QuoteStatus,
    ServiceTicketStatus,
    SupplierLevel,
)
from .exceptions import (
    BusinessLogicError,
    ConfigurationError,
    DatabaseError,
    MiniCRMError,
    ServiceError,
    UIError,
    ValidationError,
)
from .logger import MiniCRMLogger, get_logger
from .utils import (
    ensure_directory_exists,
    format_currency,
    format_phone_number,
    generate_id,
    parse_date,
    sanitize_filename,
    validate_email,
)


__all__ = [
    # 异常类
    "MiniCRMError",
    "ValidationError",
    "DatabaseError",
    "BusinessLogicError",
    "ConfigurationError",
    "ServiceError",
    "UIError",
    # 枚举和常量
    "CustomerLevel",
    "SupplierLevel",
    "InteractionType",
    "ContractStatus",
    "QuoteStatus",
    "ServiceTicketStatus",
    "DEFAULT_CONFIG",
    "DATABASE_CONFIG",
    "UI_CONFIG",
    # 日志系统
    "MiniCRMLogger",
    "get_logger",
    # 工具函数
    "format_phone_number",
    "validate_email",
    "format_currency",
    "parse_date",
    "generate_id",
    "sanitize_filename",
    "ensure_directory_exists",
]
