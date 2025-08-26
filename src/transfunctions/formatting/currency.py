"""
Transfunctions - 货币和数值格式化

提供货币、百分比等数值格式化功能.
"""

import logging
import re
from decimal import ROUND_HALF_UP, Decimal


# 配置日志
logger = logging.getLogger(__name__)


class FormattingError(Exception):
    """格式化异常类"""

    def __init__(self, message: str, value=None):
        """初始化格式化异常

        Args:
            message: 错误消息
            value: 导致错误的值
        """
        self.message = message
        self.value = value
        super().__init__(self.message)


def format_currency(
    amount: int | float | Decimal | str,
    symbol: str = "¥",
    decimal_places: int = 2,
    show_symbol: bool = True,
    thousand_separator: bool = True,
) -> str:
    """格式化货币金额

    Args:
        amount: 金额数值
        symbol: 货币符号,默认为人民币符号
        decimal_places: 小数位数,默认2位
        show_symbol: 是否显示货币符号
        thousand_separator: 是否使用千位分隔符

    Returns:
        str: 格式化后的货币字符串

    Raises:
        FormattingError: 当金额格式无效时

    Example:
        >>> format_currency(12345.67)
        '¥12,345.67'
        >>> format_currency(12345.67, show_symbol=False)
        '12,345.67'
        >>> format_currency(12345, decimal_places=0)
        '¥12,345'
    """
    try:
        # 转换为Decimal以确保精度
        if isinstance(amount, str):
            # 清理字符串中的非数字字符(除了小数点和负号)
            clean_amount = re.sub(r"[^\d\.\-]", "", amount)
            decimal_amount = Decimal(clean_amount)
        else:
            decimal_amount = Decimal(str(amount))

        # 四舍五入到指定小数位
        rounded_amount = decimal_amount.quantize(
            Decimal("0." + "0" * decimal_places), rounding=ROUND_HALF_UP
        )

        # 格式化数字
        if thousand_separator:
            # 分离整数和小数部分
            integer_part = int(abs(rounded_amount))
            decimal_part = rounded_amount % 1

            # 添加千位分隔符
            integer_str = f"{integer_part:,}"

            # 处理小数部分
            if decimal_places > 0:
                decimal_str = f"{decimal_part:.{decimal_places}f}"[1:]  # 去掉"0."
                formatted_number = integer_str + decimal_str
            else:
                formatted_number = integer_str
        else:
            formatted_number = f"{rounded_amount:.{decimal_places}f}"

        # 处理负数
        if rounded_amount < 0:
            formatted_number = "-" + formatted_number.lstrip("-")

        # 添加货币符号
        if show_symbol:
            result = symbol + formatted_number
        else:
            result = formatted_number

        logger.debug(f"货币格式化: {amount} -> {result}")
        return result

    except (ValueError, TypeError, ArithmeticError) as e:
        raise FormattingError(f"无法格式化金额: {amount}", amount) from e


def format_percentage(value: int | float, decimal_places: int = 1) -> str:
    """格式化百分比

    Args:
        value: 数值(0-1之间或0-100之间)
        decimal_places: 小数位数

    Returns:
        str: 格式化后的百分比字符串
    """
    if value is None:
        return "0.0%"

    try:
        # 如果值在0-1之间,转换为百分比
        if 0 <= value <= 1:
            percentage = value * 100
        else:
            percentage = value

        format_str = f"{{:.{decimal_places}f}}%"
        return format_str.format(percentage)

    except (ValueError, TypeError):
        return "0.0%"


def format_number_with_unit(
    value: int | float,
    unit: str = "",
    decimal_places: int = 0,
    thousands_sep: bool = True,
) -> str:
    """格式化带单位的数字

    Args:
        value: 数值
        unit: 单位
        decimal_places: 小数位数
        thousands_sep: 是否使用千分位分隔符

    Returns:
        str: 格式化后的数字字符串
    """
    if value is None:
        return f"0{unit}"

    try:
        if thousands_sep:
            format_str = f"{{:,.{decimal_places}f}}"
        else:
            format_str = f"{{:.{decimal_places}f}}"

        formatted_value = format_str.format(float(value))
        return f"{formatted_value}{unit}"

    except (ValueError, TypeError):
        return f"0{unit}"
