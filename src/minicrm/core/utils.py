"""
MiniCRM工具函数模块

提供系统中常用的工具函数,包括:
- 数据验证和格式化
- 日期时间处理
- 文件操作
- ID生成
- 字符串处理

这些函数被整个应用程序广泛使用,确保了处理逻辑的一致性.
"""

import hashlib
import logging
import re
import uuid
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .constants import (
    CURRENCY_FORMATS,
    DATE_FORMATS,
    FILE_SIZE_UNITS,
    VALIDATION_CONFIG,
)
from .exceptions import ValidationError


logger = logging.getLogger(__name__)


# ==================== 数据验证函数 ====================


def validate_email(email: str) -> bool:
    """
    验证邮箱地址格式

    Args:
        email: 邮箱地址字符串

    Returns:
        是否为有效邮箱格式

    Examples:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    if not email or not isinstance(email, str):
        return False

    pattern = VALIDATION_CONFIG["email_pattern"]
    return bool(re.match(pattern, email.strip()))


def validate_phone_number(phone: str) -> bool:
    """
    验证手机号码格式

    Args:
        phone: 手机号码字符串

    Returns:
        是否为有效手机号格式

    Examples:
        >>> validate_phone_number("13812345678")
        True
        >>> validate_phone_number("12345678901")
        False
    """
    if not phone or not isinstance(phone, str):
        return False

    # 移除所有非数字字符
    clean_phone = re.sub(r"\D", "", phone)
    pattern = VALIDATION_CONFIG["phone_pattern"]
    return bool(re.match(pattern, clean_phone))


def validate_required_fields(data: dict[str, Any], required_fields: list[str]) -> None:
    """
    验证必填字段

    Args:
        data: 要验证的数据字典
        required_fields: 必填字段列表

    Raises:
        ValidationError: 当必填字段缺失时

    Examples:
        >>> data = {"name": "张三", "phone": "13812345678"}
        >>> validate_required_fields(data, ["name", "phone"])  # 不会抛出异常
        >>> validate_required_fields(data, ["name", "email"])  # 抛出ValidationError
    """
    missing_fields = []

    for field in required_fields:
        if field not in data or not data[field] or str(data[field]).strip() == "":
            missing_fields.append(field)

    if missing_fields:
        raise ValidationError(
            f"必填字段缺失: {', '.join(missing_fields)}",
            error_code="REQUIRED_FIELDS_MISSING",
            details={"missing_fields": missing_fields},
        )


def validate_text_length(
    text: str, max_length: int | None = None, field_name: str = "字段"
) -> None:
    """
    验证文本长度

    Args:
        text: 要验证的文本
        max_length: 最大长度,默认使用配置中的值
        field_name: 字段名称,用于错误消息

    Raises:
        ValidationError: 当文本长度超限时
    """
    if not isinstance(text, str):
        text = str(text)

    max_len = max_length or VALIDATION_CONFIG["max_text_length"]

    if len(text) > max_len:
        raise ValidationError(
            f"{field_name}长度不能超过{max_len}个字符",
            error_code="TEXT_TOO_LONG",
            details={
                "field_name": field_name,
                "max_length": max_len,
                "actual_length": len(text),
            },
        )


# ==================== 格式化函数 ====================


def format_phone_number(phone: str) -> str:
    """
    格式化手机号码显示

    Args:
        phone: 原始手机号码

    Returns:
        格式化后的手机号码 (138-1234-5678)

    Examples:
        >>> format_phone_number("13812345678")
        "138-1234-5678"
        >>> format_phone_number("138 1234 5678")
        "138-1234-5678"
    """
    if not phone:
        return ""

    # 移除所有非数字字符
    clean_phone = re.sub(r"\D", "", phone)

    # 验证是否为有效手机号
    if not validate_phone_number(clean_phone):
        return phone  # 如果不是有效格式,返回原始值

    # 格式化为 138-1234-5678
    if len(clean_phone) == 11:
        return f"{clean_phone[:3]}-{clean_phone[3:7]}-{clean_phone[7:]}"

    return phone


def format_currency(
    amount: int | float | Decimal | str, symbol: str = None, decimal_places: int = None
) -> str:
    """
    格式化货币金额

    Args:
        amount: 金额数值
        symbol: 货币符号,默认使用配置中的符号
        decimal_places: 小数位数,默认使用配置中的位数

    Returns:
        格式化后的货币字符串

    Examples:
        >>> format_currency(1234.56)
        "¥1,234.56"
        >>> format_currency(1000000)
        "¥1,000,000.00"
    """
    if amount is None:
        return ""

    try:
        # 转换为Decimal以确保精度
        if isinstance(amount, str):
            decimal_amount = Decimal(amount)
        else:
            decimal_amount = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        logger.warning(f"无法格式化货币金额: {amount}")
        return str(amount)

    symbol = symbol or CURRENCY_FORMATS["symbol"]
    decimal_places = (
        decimal_places
        if decimal_places is not None
        else CURRENCY_FORMATS["decimal_places"]
    )

    # 格式化数字
    format_str = f"{{:,.{decimal_places}f}}"
    formatted_number = format_str.format(float(decimal_amount))

    return f"{symbol}{formatted_number}"


def format_date(date_obj: datetime | date | str, format_type: str = "default") -> str:
    """
    格式化日期显示

    Args:
        date_obj: 日期对象或字符串
        format_type: 格式类型 (default, display, datetime, datetime_display, time)

    Returns:
        格式化后的日期字符串

    Examples:
        >>> from datetime import datetime
        >>> dt = datetime(2025, 1, 15, 14, 30, 0)
        >>> format_date(dt, "default")
        "2025-01-15"
        >>> format_date(dt, "display")
        "2025年01月15日"
        >>> format_date(dt, "datetime_display")
        "2025年01月15日 14:30:00"
    """
    if not date_obj:
        return ""

    # 如果是字符串,尝试解析
    if isinstance(date_obj, str):
        date_obj = parse_date(date_obj)
        if not date_obj:
            return ""

    # 获取格式字符串
    format_str = DATE_FORMATS.get(format_type, DATE_FORMATS["default"])

    try:
        return date_obj.strftime(format_str)
    except (AttributeError, ValueError) as e:
        logger.warning(f"日期格式化失败: {date_obj}, 错误: {e}")
        return str(date_obj)


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小显示

    Args:
        size_bytes: 文件大小(字节)

    Returns:
        格式化后的文件大小字符串

    Examples:
        >>> format_file_size(1024)
        "1.00 KB"
        >>> format_file_size(1048576)
        "1.00 MB"
    """
    if size_bytes == 0:
        return "0 B"

    for i, unit in enumerate(FILE_SIZE_UNITS):
        if size_bytes < 1024.0 or i == len(FILE_SIZE_UNITS) - 1:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0

    return f"{size_bytes:.2f} {FILE_SIZE_UNITS[-1]}"


# ==================== 日期时间处理函数 ====================


def parse_date(date_str: str) -> datetime | None:
    """
    解析日期字符串

    Args:
        date_str: 日期字符串

    Returns:
        解析后的datetime对象,失败返回None

    Examples:
        >>> parse_date("2025-01-15")
        datetime.datetime(2025, 1, 15, 0, 0)
        >>> parse_date("2025年01月15日")
        datetime.datetime(2025, 1, 15, 0, 0)
    """
    if not date_str or not isinstance(date_str, str):
        return None

    # 常见的日期格式
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y年%m月%d日",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y年%m月%d日 %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue

    logger.warning(f"无法解析日期字符串: {date_str}")
    return None


def get_current_timestamp() -> str:
    """
    获取当前时间戳字符串

    Returns:
        格式化的时间戳字符串 (YYYYMMDD_HHMMSS)

    Examples:
        >>> get_current_timestamp()
        "20250115_143000"
    """
    return datetime.now().strftime(DATE_FORMATS["filename"])


def calculate_age_in_days(
    start_date: datetime | date, end_date: datetime | date | None = None
) -> int:
    """
    计算两个日期之间的天数差

    Args:
        start_date: 开始日期
        end_date: 结束日期,默认为当前日期

    Returns:
        天数差

    Examples:
        >>> from datetime import date
        >>> start = date(2025, 1, 1)
        >>> end = date(2025, 1, 15)
        >>> calculate_age_in_days(start, end)
        14
    """
    if end_date is None:
        end_date = datetime.now().date()

    # 确保都是date对象
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()

    return (end_date - start_date).days


# ==================== ID生成函数 ====================


def generate_id(prefix: str = "", length: int = 8) -> str:
    """
    生成唯一ID

    Args:
        prefix: ID前缀
        length: ID长度(不包括前缀)

    Returns:
        生成的唯一ID

    Examples:
        >>> generate_id("CUST", 6)
        "CUST123456"
        >>> generate_id()
        "A1B2C3D4"
    """
    # 使用UUID生成随机字符串
    random_str = str(uuid.uuid4()).replace("-", "").upper()[:length]
    return f"{prefix}{random_str}" if prefix else random_str


def generate_sequence_id(prefix: str, sequence_number: int, length: int = 6) -> str:
    """
    生成序列ID

    Args:
        prefix: ID前缀
        sequence_number: 序列号
        length: 序列号长度

    Returns:
        生成的序列ID

    Examples:
        >>> generate_sequence_id("Q", 1, 6)
        "Q000001"
        >>> generate_sequence_id("CUST", 123, 4)
        "CUST0123"
    """
    format_str = f"{{:0{length}d}}"
    sequence_str = format_str.format(sequence_number)
    return f"{prefix}{sequence_str}"


def generate_hash_id(data: str, length: int = 8) -> str:
    """
    基于数据生成哈希ID

    Args:
        data: 用于生成哈希的数据
        length: 哈希ID长度

    Returns:
        生成的哈希ID

    Examples:
        >>> generate_hash_id("customer_name_phone")
        "A1B2C3D4"
    """
    hash_obj = hashlib.md5(data.encode("utf-8"))
    return hash_obj.hexdigest()[:length].upper()


# ==================== 文件操作函数 ====================


def ensure_directory_exists(directory_path: str | Path) -> Path:
    """
    确保目录存在,如果不存在则创建

    Args:
        directory_path: 目录路径

    Returns:
        目录路径对象

    Examples:
        >>> ensure_directory_exists("/path/to/directory")
        PosixPath('/path/to/directory')
    """
    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def sanitize_filename(filename: str) -> str:
    """
    清理文件名,移除不安全字符

    Args:
        filename: 原始文件名

    Returns:
        清理后的安全文件名

    Examples:
        >>> sanitize_filename("客户报表<2025-01-15>.xlsx")
        "客户报表_2025-01-15_.xlsx"
    """
    if not filename:
        return "untitled"

    # 移除或替换不安全字符
    unsafe_chars = r'<>:"/\|?*'
    safe_filename = filename

    for char in unsafe_chars:
        safe_filename = safe_filename.replace(char, "_")

    # 移除连续的下划线
    safe_filename = re.sub(r"_+", "_", safe_filename)

    # 移除开头和结尾的下划线和空格
    safe_filename = safe_filename.strip("_ ")

    # 确保文件名不为空
    if not safe_filename:
        safe_filename = "untitled"

    return safe_filename


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名

    Args:
        filename: 文件名

    Returns:
        文件扩展名(包括点号)

    Examples:
        >>> get_file_extension("document.pdf")
        ".pdf"
        >>> get_file_extension("archive.tar.gz")
        ".gz"
    """
    return Path(filename).suffix.lower()


def is_valid_file_extension(filename: str, allowed_extensions: list[str]) -> bool:
    """
    检查文件扩展名是否有效

    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名列表

    Returns:
        是否为有效扩展名

    Examples:
        >>> is_valid_file_extension("doc.pdf", [".pdf", ".docx"])
        True
        >>> is_valid_file_extension("doc.txt", [".pdf", ".docx"])
        False
    """
    ext = get_file_extension(filename)
    return ext in [e.lower() for e in allowed_extensions]


# ==================== 字符串处理函数 ====================


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断文本到指定长度

    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀

    Returns:
        截断后的文本

    Examples:
        >>> truncate_text("这是一个很长的文本内容", 10)
        "这是一个很长的文..."
    """
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def normalize_whitespace(text: str) -> str:
    """
    标准化空白字符

    Args:
        text: 原始文本

    Returns:
        标准化后的文本

    Examples:
        >>> normalize_whitespace("  hello   world  \\n\\t  ")
        "hello world"
    """
    if not text:
        return ""

    # 将所有空白字符替换为单个空格,并去除首尾空白
    return re.sub(r"\s+", " ", text).strip()


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """
    遮蔽敏感数据

    Args:
        data: 敏感数据
        mask_char: 遮蔽字符
        visible_chars: 可见字符数量

    Returns:
        遮蔽后的数据

    Examples:
        >>> mask_sensitive_data("13812345678")
        "138****5678"
        >>> mask_sensitive_data("user@example.com", visible_chars=3)
        "use*****com"
    """
    if not data or len(data) <= visible_chars:
        return data

    if len(data) <= visible_chars * 2:
        # 如果数据太短,只显示前几位
        return data[:visible_chars] + mask_char * (len(data) - visible_chars)

    # 显示前后各几位
    half_visible = visible_chars // 2
    start = data[:half_visible]
    end = data[-half_visible:] if half_visible > 0 else ""
    middle_length = len(data) - len(start) - len(end)

    return start + mask_char * middle_length + end


# ==================== 数据转换函数 ====================


def safe_int(value: Any, default: int = 0) -> int:
    """
    安全转换为整数

    Args:
        value: 要转换的值
        default: 默认值

    Returns:
        转换后的整数

    Examples:
        >>> safe_int("123")
        123
        >>> safe_int("abc", 0)
        0
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    安全转换为浮点数

    Args:
        value: 要转换的值
        default: 默认值

    Returns:
        转换后的浮点数

    Examples:
        >>> safe_float("123.45")
        123.45
        >>> safe_float("abc", 0.0)
        0.0
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """
    安全转换为字符串

    Args:
        value: 要转换的值
        default: 默认值

    Returns:
        转换后的字符串

    Examples:
        >>> safe_str(123)
        "123"
        >>> safe_str(None, "N/A")
        "N/A"
    """
    if value is None:
        return default
    try:
        return str(value)
    except Exception:
        return default


def dict_get_nested(data: dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    获取嵌套字典中的值

    Args:
        data: 字典数据
        key_path: 键路径,用点号分隔 (如 "user.profile.name")
        default: 默认值

    Returns:
        获取到的值或默认值

    Examples:
        >>> data = {"user": {"profile": {"name": "张三"}}}
        >>> dict_get_nested(data, "user.profile.name")
        "张三"
        >>> dict_get_nested(data, "user.profile.age", 0)
        0
    """
    keys = key_path.split(".")
    current = data

    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default
