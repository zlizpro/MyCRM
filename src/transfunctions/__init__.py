"""
transfunctions - MiniCRM 可复用函数库

这个模块提供了MiniCRM系统中所有可复用的核心函数，包括：
- 数据验证函数 (validation)
- 数据格式化函数 (formatting)
- 业务计算函数 (calculations)

设计原则：
1. 每个函数都是纯函数，无副作用
2. 完整的类型注解和文档字符串
3. 统一的错误处理机制
4. 高度可复用和可测试

使用示例：
    from transfunctions import validate_customer_data, format_currency

    # 验证客户数据
    is_valid = validate_customer_data(customer_info)

    # 格式化货币
    formatted_price = format_currency(12500.50)
"""

import logging
from typing import Any


# 版本信息
__version__ = "1.0.0"
__author__ = "MiniCRM Development Team"

# 配置日志
logger = logging.getLogger(__name__)

# 从各个模块导入核心函数
try:
    # 数据验证函数和类
    # 业务计算函数和类
    from .calculations import (
        CustomerValueMetrics,
        PaginationResult,
        calculate_customer_value_score,
        calculate_pagination,
        calculate_quote_total,
    )

    # 数据操作函数和类
    from .data_operations import (
        CRUDTemplate,
        QueryBuilder,
        batch_operation_template,
        build_search_query,
        convert_dict_to_model,
        convert_row_to_dict,
        create_crud_template,
        paginated_search_template,
    )

    # 数据格式化函数
    from .formatting import (
        format_address,
        format_currency,
        format_date,
        format_phone,
    )
    from .validation import (
        ValidationError,
        ValidationResult,
        validate_customer_data,
        validate_email,
        validate_phone,
        validate_supplier_data,
    )

    logger.info("transfunctions模块加载成功")

except ImportError as e:
    logger.warning(f"部分transfunctions模块导入失败: {e}")
    # 在开发阶段，某些模块可能还未实现，这是正常的

# 导出的公共接口
__all__ = [
    # 验证类和异常
    "ValidationError",
    "ValidationResult",
    # 验证函数
    "validate_customer_data",
    "validate_supplier_data",
    "validate_email",
    "validate_phone",
    # 格式化函数
    "format_currency",
    "format_phone",
    "format_date",
    "format_address",
    # 计算类
    "CustomerValueMetrics",
    "PaginationResult",
    # 计算函数
    "calculate_customer_value_score",
    "calculate_quote_total",
    "calculate_pagination",
    # 数据操作类和函数
    "CRUDTemplate",
    "QueryBuilder",
    "create_crud_template",
    "paginated_search_template",
    "batch_operation_template",
    "build_search_query",
    "convert_row_to_dict",
    "convert_dict_to_model",
]

# 模块级别的配置常量
DEFAULT_CONFIG = {
    "currency_symbol": "¥",
    "date_format": "%Y-%m-%d",
    "phone_format": "xxx-xxxx-xxxx",
    "decimal_places": 2,
}


def get_version() -> str:
    """获取transfunctions版本号

    Returns:
        str: 版本号字符串
    """
    return __version__


def get_available_functions() -> list[str]:
    """获取所有可用函数列表

    Returns:
        list[str]: 可用函数名称列表
    """
    return __all__


def validate_config(config: dict[str, Any]) -> bool:
    """验证配置参数

    Args:
        config: 配置字典

    Returns:
        bool: 配置是否有效
    """
    required_keys = ["currency_symbol", "date_format", "phone_format", "decimal_places"]
    return all(key in config for key in required_keys)
