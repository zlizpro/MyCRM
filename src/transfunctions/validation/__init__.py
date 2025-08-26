"""
Transfunctions - 验证模块

提供统一的数据验证功能.
"""

from .business import (
    ValidationError,
    ValidationResult,
    validate_business_rules,
    validate_contract_data,
    validate_customer_data,
    validate_quote_data,
    validate_service_ticket_data,
    validate_supplier_data,
)
from .core import (
    validate_date_format,
    validate_email,
    validate_numeric_range,
    validate_phone,
    validate_required_fields,
    validate_string_length,
)


__all__ = [
    # 验证类和异常
    "ValidationError",
    "ValidationResult",
    # 核心验证函数
    "validate_email",
    "validate_phone",
    "validate_required_fields",
    "validate_string_length",
    "validate_numeric_range",
    "validate_date_format",
    # 业务验证函数
    "validate_customer_data",
    "validate_supplier_data",
    "validate_contract_data",
    "validate_quote_data",
    "validate_service_ticket_data",
    "validate_business_rules",
]
