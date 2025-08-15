"""
Transfunctions - 统计计算

提供分页、统计等通用计算功能。
"""

import logging
import math
from dataclasses import dataclass
from typing import Any

# 配置日志
logger = logging.getLogger(__name__)


class CalculationError(Exception):
    """计算异常类"""

    def __init__(self, message: str, context=None):
        """初始化计算异常

        Args:
            message: 错误消息
            context: 错误上下文信息
        """
        self.message = message
        self.context = context or {}
        super().__init__(self.message)


@dataclass
class PaginationResult:
    """分页结果数据类"""

    total_items: int  # 总记录数
    total_pages: int  # 总页数
    current_page: int  # 当前页码
    page_size: int  # 每页大小
    start_index: int  # 起始索引
    end_index: int  # 结束索引
    has_previous: bool  # 是否有上一页
    has_next: bool  # 是否有下一页

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "total_items": self.total_items,
            "total_pages": self.total_pages,
            "current_page": self.current_page,
            "page_size": self.page_size,
            "start_index": self.start_index,
            "end_index": self.end_index,
            "has_previous": self.has_previous,
            "has_next": self.has_next,
        }


def calculate_pagination(
    total_items: int, current_page: int = 1, page_size: int = 20
) -> PaginationResult:
    """计算分页信息

    Args:
        total_items: 总记录数
        current_page: 当前页码（从1开始）
        page_size: 每页大小

    Returns:
        PaginationResult: 分页结果对象

    Raises:
        CalculationError: 当分页参数无效时

    Example:
        >>> pagination = calculate_pagination(100, 3, 20)
        >>> print(f"第{pagination.current_page}页，共{pagination.total_pages}页")
    """
    try:
        # 参数验证
        if total_items < 0:
            raise CalculationError("总记录数不能为负数")

        if current_page < 1:
            raise CalculationError("当前页码必须大于0")

        if page_size < 1:
            raise CalculationError("每页大小必须大于0")

        # 计算总页数
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1

        # 确保当前页码在有效范围内
        current_page = min(current_page, total_pages)

        # 计算索引范围
        start_index = (current_page - 1) * page_size
        end_index = min(start_index + page_size, total_items)

        # 计算分页状态
        has_previous = current_page > 1
        has_next = current_page < total_pages

        result = PaginationResult(
            total_items=total_items,
            total_pages=total_pages,
            current_page=current_page,
            page_size=page_size,
            start_index=start_index,
            end_index=end_index,
            has_previous=has_previous,
            has_next=has_next,
        )

        logger.debug(f"分页计算完成: 第{current_page}页/共{total_pages}页")
        return result

    except Exception as e:
        raise CalculationError(
            f"分页计算失败: {str(e)}",
            {
                "total_items": total_items,
                "current_page": current_page,
                "page_size": page_size,
            },
        ) from e


def calculate_growth_rate(current_value: float, previous_value: float) -> float:
    """计算增长率

    Args:
        current_value: 当前值
        previous_value: 之前值

    Returns:
        float: 增长率（百分比，如15.5表示15.5%）
    """
    if previous_value == 0:
        return 100.0 if current_value > 0 else 0.0

    growth_rate = ((current_value - previous_value) / previous_value) * 100
    return round(growth_rate, 2)


def calculate_average(values: list[int | float]) -> float:
    """计算平均值

    Args:
        values: 数值列表

    Returns:
        float: 平均值
    """
    if not values:
        return 0.0

    return sum(values) / len(values)


def calculate_weighted_average(values: list[tuple[int | float, float]]) -> float:
    """计算加权平均值

    Args:
        values: (值, 权重) 元组列表

    Returns:
        float: 加权平均值
    """
    if not values:
        return 0.0

    total_weighted_value = sum(value * weight for value, weight in values)
    total_weight = sum(weight for _, weight in values)

    if total_weight == 0:
        return 0.0

    return total_weighted_value / total_weight


def _get_empty_pagination(page_size: int) -> dict[str, int]:
    """获取空的分页信息"""
    return {
        "total_count": 0,
        "page_size": page_size,
        "current_page": 1,
        "total_pages": 0,
        "start_index": 0,
        "end_index": 0,
        "has_previous": False,
        "has_next": False,
        "previous_page": None,
        "next_page": None,
    }
