"""
Transfunctions - 日期时间格式化

提供日期时间格式化功能。
"""

import logging
from datetime import date, datetime

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


def format_date(
    date_value: datetime | date | str,
    format_string: str = "%Y-%m-%d",
    locale: str = "zh_CN",
) -> str:
    """格式化日期

    Args:
        date_value: 日期值（datetime、date对象或字符串）
        format_string: 格式字符串
        locale: 本地化设置

    Returns:
        str: 格式化后的日期字符串

    Raises:
        FormattingError: 当日期格式无效时

    Example:
        >>> format_date(datetime(2025, 1, 15))
        '2025-01-15'
        >>> format_date("2025-01-15", "%Y年%m月%d日")
        '2025年01月15日'
    """
    try:
        # 处理不同类型的输入
        if isinstance(date_value, str):
            # 尝试解析常见的日期格式
            date_formats = [
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%Y.%m.%d",
                "%Y-%m-%d %H:%M:%S",
                "%Y/%m/%d %H:%M:%S",
            ]

            parsed_date = None
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_value, fmt)
                    break
                except ValueError:
                    continue

            if parsed_date is None:
                raise ValueError(f"无法解析日期字符串: {date_value}")

            date_obj = parsed_date

        elif isinstance(date_value, datetime):
            date_obj = date_value
        elif isinstance(date_value, date):
            date_obj = datetime.combine(date_value, datetime.min.time())
        else:
            raise TypeError(f"不支持的日期类型: {type(date_value)}")

        # 格式化日期
        formatted_date = date_obj.strftime(format_string)

        # 中文本地化处理
        if locale == "zh_CN" and any(
            char in format_string for char in ["年", "月", "日"]
        ):
            # 替换中文数字（如果需要）
            pass

        logger.debug(f"日期格式化: {date_value} -> {formatted_date}")
        return formatted_date

    except (ValueError, TypeError) as e:
        raise FormattingError(f"无法格式化日期: {date_value}", date_value) from e


def format_datetime(
    datetime_obj: datetime | str, format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """格式化日期时间

    Args:
        datetime_obj: 日期时间对象或字符串
        format_str: 格式字符串

    Returns:
        str: 格式化后的日期时间字符串
    """
    return format_date(datetime_obj, format_str)


def format_duration(seconds: int) -> str:
    """格式化时长

    Args:
        seconds: 秒数

    Returns:
        str: 格式化后的时长字符串
    """
    if seconds < 0:
        return "0秒"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}小时")
    if minutes > 0:
        parts.append(f"{minutes}分钟")
    if secs > 0 or not parts:
        parts.append(f"{secs}秒")

    return "".join(parts)


def _parse_date_string(date_str: str) -> datetime | None:
    """解析日期字符串"""
    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"]:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None
