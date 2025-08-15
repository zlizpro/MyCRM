"""
MiniCRM 单元格格式化器

专门负责表格单元格数据的格式化处理，支持多种数据类型。
使用transfunctions标准格式化函数确保一致性。
"""

import logging
from typing import Any


# 导入transfunctions格式化函数
try:
    from transfunctions.formatting import format_currency, format_date, format_phone

    _TRANSFUNCTIONS_AVAILABLE = True
except ImportError:
    _TRANSFUNCTIONS_AVAILABLE = False


class CellFormatter:
    """
    单元格格式化器类

    负责根据列配置对单元格数据进行格式化处理。
    支持货币、日期、电话、百分比等多种数据类型。
    """

    def __init__(self):
        """初始化格式化器"""
        self._logger = logging.getLogger(f"{__name__}.CellFormatter")

        # 格式化函数映射
        self._formatters = {
            "currency": self._format_currency,
            "percentage": self._format_percentage,
            "date": self._format_date,
            "datetime": self._format_datetime,
            "phone": self._format_phone,
            "boolean": self._format_boolean,
            "text": self._format_text,
        }

    def format_value(self, value: Any, column: dict[str, Any]) -> str:
        """
        格式化单元格值

        Args:
            value: 原始值
            column: 列配置

        Returns:
            str: 格式化后的字符串
        """
        try:
            if value is None:
                return ""

            column_type = column.get("type", "text")
            formatter = self._formatters.get(column_type, self._format_text)

            return formatter(value, column)

        except Exception as e:
            self._logger.error(f"格式化单元格值失败: {e}")
            return str(value) if value is not None else ""

    def _format_currency(self, value: Any, column: dict[str, Any]) -> str:
        """格式化货币值"""
        if _TRANSFUNCTIONS_AVAILABLE:
            try:
                num_value = float(value)
                return format_currency(num_value)
            except (ValueError, TypeError):
                return f"¥{value}"
        else:
            try:
                return f"¥{float(value):,.2f}"
            except (ValueError, TypeError):
                return f"¥{value}"

    def _format_percentage(self, value: Any, column: dict[str, Any]) -> str:
        """格式化百分比值"""
        try:
            return f"{float(value):.1f}%"
        except (ValueError, TypeError):
            return f"{value}%"

    def _format_date(self, value: Any, column: dict[str, Any]) -> str:
        """格式化日期值"""
        if _TRANSFUNCTIONS_AVAILABLE:
            return format_date(str(value))
        else:
            if hasattr(value, "strftime"):
                return value.strftime("%Y-%m-%d")
            return str(value)

    def _format_datetime(self, value: Any, column: dict[str, Any]) -> str:
        """格式化日期时间值"""
        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d %H:%M")
        return str(value)

    def _format_phone(self, value: Any, column: dict[str, Any]) -> str:
        """格式化电话号码"""
        if _TRANSFUNCTIONS_AVAILABLE:
            return format_phone(str(value))
        else:
            return str(value)

    def _format_boolean(self, value: Any, column: dict[str, Any]) -> str:
        """格式化布尔值"""
        return "是" if value else "否"

    def _format_text(self, value: Any, column: dict[str, Any]) -> str:
        """格式化文本值"""
        return str(value)


# 全局格式化器实例
_cell_formatter = CellFormatter()


def format_cell_value(value: Any, column: dict[str, Any]) -> str:
    """
    格式化单元格值的便捷函数

    Args:
        value: 原始值
        column: 列配置

    Returns:
        str: 格式化后的字符串
    """
    return _cell_formatter.format_value(value, column)
