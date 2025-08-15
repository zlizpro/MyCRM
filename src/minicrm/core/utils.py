"""
MiniCRM 核心工具函数

提供整个应用程序中使用的通用工具函数，包括：
- 数据验证工具
- 字符串处理工具
- 日期时间工具
- 文件操作工具
- 数据转换工具
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any
from transfunctions.formatting import format_phone
from transfunctions.formatting import format_currency
from transfunctions.formatting import format_date


def is_valid_email(email: str) -> bool:
    """
    验证邮箱地址格式是否正确

    Args:
        email: 邮箱地址字符串

    Returns:
        bool: 邮箱格式是否正确

    Example:
        >>> is_valid_email("user@example.com")
        True
        >>> is_valid_email("invalid-email")
        False
    """
    if not email or not isinstance(email, str):
        return False

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def is_valid_phone(phone: str) -> bool:
    """
    验证中国大陆手机号码格式是否正确

    Args:
        phone: 手机号码字符串

    Returns:
        bool: 手机号码格式是否正确

    Example:
        >>> is_valid_phone("13812345678")
        True
        >>> is_valid_phone("12345678901")
        False
    """
    if not phone or not isinstance(phone, str):
        return False

    # 移除所有非数字字符
    clean_phone = re.sub(r"\D", "", phone)

    # 中国大陆手机号码格式：1[3-9]xxxxxxxxx
    pattern = r"^1[3-9]\d{9}$"
    return bool(re.match(pattern, clean_phone))


# format_phone 函数已移除，请使用 transfunctions.formatting.format_phone

# format_currency 函数已移除，请使用 transfunctions.formatting.format_currency

# format_date 函数已移除，请使用 transfunctions.formatting.format_date

def safe_get(data: dict[str, Any], key: str, default: Any = None) -> Any:
    """
    安全地从字典中获取值

    Args:
        data: 数据字典
        key: 键名，支持点号分隔的嵌套键
        default: 默认值

    Returns:
        Any: 获取到的值或默认值

    Example:
        >>> data = {"user": {"name": "张三", "age": 30}}
        >>> safe_get(data, "user.name")
        "张三"
        >>> safe_get(data, "user.email", "未设置")
        "未设置"
    """
    if not isinstance(data, dict):
        return default

    keys = key.split(".")
    current = data

    try:
        for k in keys:
            current = current[k]
        return current
    except (KeyError, TypeError):
        return default


def clean_string(text: str) -> str:
    """
    清理字符串，移除多余的空白字符

    Args:
        text: 原始字符串

    Returns:
        str: 清理后的字符串

    Example:
        >>> clean_string("  hello   world  ")
        "hello world"
    """
    if not text or not isinstance(text, str):
        return ""

    # 移除首尾空白，并将多个连续空白字符替换为单个空格
    return re.sub(r"\s+", " ", text.strip())


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串到指定长度

    Args:
        text: 原始字符串
        max_length: 最大长度
        suffix: 截断后的后缀

    Returns:
        str: 截断后的字符串

    Example:
        >>> truncate_string("这是一个很长的字符串", 8)
        "这是一个很长..."
    """
    if not text or not isinstance(text, str):
        return ""

    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def ensure_directory(path: str | Path) -> Path:
    """
    确保目录存在，如果不存在则创建

    Args:
        path: 目录路径

    Returns:
        Path: 目录路径对象

    Example:
        >>> ensure_directory("data/backups")
        PosixPath('data/backups')
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def get_file_size_mb(file_path: str | Path) -> float:
    """
    获取文件大小（MB）

    Args:
        file_path: 文件路径

    Returns:
        float: 文件大小（MB）

    Example:
        >>> get_file_size_mb("data.db")
        2.5
    """
    try:
        path_obj = Path(file_path)
        if path_obj.exists() and path_obj.is_file():
            size_bytes = path_obj.stat().st_size
            return size_bytes / (1024 * 1024)  # 转换为MB
        return 0.0
    except (OSError, ValueError):
        return 0.0


def dict_to_flat(data: dict[str, Any], separator: str = ".") -> dict[str, Any]:
    """
    将嵌套字典扁平化

    Args:
        data: 嵌套字典
        separator: 键名分隔符

    Returns:
        Dict[str, Any]: 扁平化后的字典

    Example:
        >>> dict_to_flat({"user": {"name": "张三", "age": 30}})
        {"user.name": "张三", "user.age": 30}
    """

    def _flatten(obj: Any, parent_key: str = "") -> dict[str, Any]:
        items = []

        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else key
                items.extend(_flatten(value, new_key).items())
        else:
            return {parent_key: obj}

        return dict(items)

    return _flatten(data)


def batch_process(items: list[Any], batch_size: int = 100) -> list[list[Any]]:
    """
    将列表分批处理

    Args:
        items: 要分批的列表
        batch_size: 每批的大小

    Returns:
        List[List[Any]]: 分批后的列表

    Example:
        >>> batch_process([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    if not items:
        return []

    batches = []
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        batches.append(batch)

    return batches


def generate_unique_filename(
    base_name: str, extension: str, directory: str | Path
) -> str:
    """
    生成唯一的文件名（如果文件已存在，则添加数字后缀）

    Args:
        base_name: 基础文件名
        extension: 文件扩展名
        directory: 目录路径

    Returns:
        str: 唯一的文件名

    Example:
        >>> generate_unique_filename("backup", "db", "/data")
        "backup_001.db"  # 如果backup.db已存在
    """
    directory = Path(directory)
    counter = 0

    while True:
        if counter == 0:
            filename = f"{base_name}.{extension}"
        else:
            filename = f"{base_name}_{counter:03d}.{extension}"

        if not (directory / filename).exists():
            return filename

        counter += 1

        # 防止无限循环
        if counter > 999:
            # 使用时间戳作为后缀
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{base_name}_{timestamp}.{extension}"
