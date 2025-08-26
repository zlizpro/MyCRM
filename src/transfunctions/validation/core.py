"""
Transfunctions - 核心验证函数

提供基础的数据验证功能,包括邮箱、电话等通用验证.
"""

import logging
import re
from datetime import datetime


# 配置日志
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """数据验证异常类"""

    def __init__(self, message: str, field: str | None = None):
        """初始化验证异常

        Args:
            message: 错误消息
            field: 出错的字段名(可选)
        """
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_email(email: str, raise_exception: bool = False) -> bool:
    """验证邮箱地址格式

    Args:
        email: 邮箱地址字符串
        raise_exception: 是否在验证失败时抛出异常

    Returns:
        bool: 邮箱格式是否有效

    Raises:
        ValidationError: 当邮箱格式无效且raise_exception=True时

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    if not email or not isinstance(email, str):
        if raise_exception:
            raise ValidationError("邮箱地址不能为空", "email")
        return False

    email = email.strip().lower()

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    is_valid = bool(re.match(pattern, email))

    if not is_valid and raise_exception:
        raise ValidationError("邮箱地址格式不正确", "email")

    # 检查邮箱长度
    if is_valid and len(email) > 254:
        if raise_exception:
            raise ValidationError("邮箱地址过长", "email")
        return False

    if is_valid:
        logger.debug(f"邮箱验证通过: {email}")

    return is_valid


def validate_phone(
    phone: str, phone_type: str = "mobile", raise_exception: bool = False
) -> bool:
    """验证电话号码格式

    Args:
        phone: 电话号码字符串
        phone_type: 电话类型,"mobile"(手机)或"landline"(固话)
        raise_exception: 是否在验证失败时抛出异常

    Returns:
        bool: 电话号码格式是否有效

    Raises:
        ValidationError: 当电话号码格式无效且raise_exception=True时

    Example:
        >>> validate_phone("13812345678")
        True
        >>> validate_phone("021-12345678", "landline")
        True
    """
    if not phone or not isinstance(phone, str):
        if raise_exception:
            raise ValidationError("电话号码不能为空", "phone")
        return False

    # 清理电话号码(移除空格、横线等)
    clean_phone = re.sub(r"[\s\-\(\)]", "", phone)

    # 常用正则表达式模式
    patterns = {
        "mobile_phone": r"^1[3-9]\d{9}$",
        "landline_phone": r"^0\d{2,3}-?\d{7,8}$",
    }

    is_valid = False

    if phone_type == "mobile":
        is_valid = bool(re.match(patterns["mobile_phone"], clean_phone))
        if not is_valid and raise_exception:
            raise ValidationError("手机号码格式不正确,应为11位数字且以1开头", "phone")
    elif phone_type == "landline":
        is_valid = bool(re.match(patterns["landline_phone"], phone))
        if not is_valid and raise_exception:
            raise ValidationError("固定电话格式不正确,应为区号-号码格式", "phone")
    else:
        # 尝试匹配手机或固话
        is_valid = bool(re.match(patterns["mobile_phone"], clean_phone)) or bool(
            re.match(patterns["landline_phone"], phone)
        )
        if not is_valid and raise_exception:
            raise ValidationError("电话号码格式不正确", "phone")

    if is_valid:
        logger.debug(f"电话验证通过: {phone}")

    return is_valid


def validate_required_fields(data: dict, required_fields: list[str]) -> list[str]:
    """验证必填字段

    Args:
        data: 数据字典
        required_fields: 必填字段列表

    Returns:
        List[str]: 缺失字段的错误信息列表
    """
    errors = []

    for field in required_fields:
        if not data.get(field):
            field_name = _get_field_display_name(field)
            errors.append(f"{field_name}字段不能为空")

    return errors


def validate_string_length(
    value: str, min_length: int = 0, max_length: int = 255, field_name: str = "字段"
) -> str | None:
    """验证字符串长度"""
    if not isinstance(value, str):
        return f"{field_name}必须是字符串类型"

    length = len(value.strip())

    if length < min_length:
        return f"{field_name}长度不能少于{min_length}个字符"

    if length > max_length:
        return f"{field_name}长度不能超过{max_length}个字符"

    return None


def validate_numeric_range(
    value: int | float,
    min_value: float | None = None,
    max_value: float | None = None,
    field_name: str = "数值",
) -> str | None:
    """验证数值范围"""
    if not isinstance(value, int | float):
        return f"{field_name}必须是数值类型"

    if min_value is not None and value < min_value:
        return f"{field_name}不能小于{min_value}"

    if max_value is not None and value > max_value:
        return f"{field_name}不能超过{max_value}"

    return None


def validate_date_format(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
    """验证日期格式"""
    if not date_str or not isinstance(date_str, str):
        return False

    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False


def _get_field_display_name(field: str) -> str:
    """获取字段显示名称"""
    field_names = {
        "name": "名称",
        "phone": "电话",
        "email": "邮箱",
        "address": "地址",
        "contact_person": "联系人",
    }
    return field_names.get(field, field)
