"""
Transfunctions - 计算模块

提供统一的业务计算功能.
"""

from .customer import CustomerValueMetrics, calculate_customer_value_score
from .financial import calculate_compound_interest, calculate_quote_total
from .statistics import (
    PaginationResult,
    calculate_average,
    calculate_growth_rate,
    calculate_pagination,
    calculate_weighted_average,
)


__all__ = [
    # 数据类
    "CustomerValueMetrics",
    "PaginationResult",
    # 客户相关计算
    "calculate_customer_value_score",
    # 财务计算
    "calculate_quote_total",
    "calculate_compound_interest",
    # 统计计算
    "calculate_pagination",
    "calculate_growth_rate",
    "calculate_average",
    "calculate_weighted_average",
]
