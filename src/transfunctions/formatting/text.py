"""
Transfunctions - 文本格式化

提供文本、电话、地址等格式化功能.
"""

import logging
import re


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


def format_phone(phone: str, format_type: str = "standard") -> str:
    """格式化电话号码

    Args:
        phone: 原始电话号码
        format_type: 格式类型,"standard"(标准格式)、"compact"(紧凑格式)、"display"(显示格式)

    Returns:
        str: 格式化后的电话号码

    Raises:
        FormattingError: 当电话号码格式无效时

    Example:
        >>> format_phone("13812345678")
        '138-1234-5678'
        >>> format_phone("13812345678", "compact")
        '13812345678'
        >>> format_phone("13812345678", "display")
        '138****5678'
    """
    if not phone or not isinstance(phone, str):
        return ""

    # 清理电话号码,只保留数字
    clean_phone = re.sub(r"\D", "", phone)

    if not clean_phone:
        return phone

    # 手机号码格式化(11位)
    if len(clean_phone) == 11 and clean_phone.startswith("1"):
        if format_type == "standard":
            return f"{clean_phone[:3]}-{clean_phone[3:7]}-{clean_phone[7:]}"
        elif format_type == "compact":
            return clean_phone
        elif format_type == "display":
            return f"{clean_phone[:3]}****{clean_phone[7:]}"
        elif format_type == "dashed":
            return f"{clean_phone[:3]}-{clean_phone[3:7]}-{clean_phone[7:]}"
        elif format_type == "spaced":
            return f"{clean_phone[:3]} {clean_phone[3:7]} {clean_phone[7:]}"
        else:
            return f"{clean_phone[:3]}-{clean_phone[3:7]}-{clean_phone[7:]}"

    # 固定电话格式化
    elif len(clean_phone) >= 10:
        if format_type == "standard":
            # 假设前3-4位是区号
            if len(clean_phone) == 10:
                return f"{clean_phone[:3]}-{clean_phone[3:]}"
            else:
                return f"{clean_phone[:4]}-{clean_phone[4:]}"
        elif format_type == "compact":
            return clean_phone
        elif format_type == "display":
            return f"{clean_phone[:4]}****{clean_phone[-4:]}"

    # 无法识别格式时返回原始值
    return phone


def format_address(
    address_data: str | dict[str, str],
    format_type: str = "full",
    separator: str = " ",
) -> str:
    """格式化地址信息

    Args:
        address_data: 地址数据(字符串或字典)
        format_type: 格式类型,"full"(完整)、"short"(简短)、"postal"(邮寄格式)
        separator: 分隔符

    Returns:
        str: 格式化后的地址字符串

    Raises:
        FormattingError: 当地址格式无效时

    Example:
        >>> address = {"province": "上海市", "city": "上海市", "district": "浦东新区", "detail": "张江路123号"}
        >>> format_address(address)
        '上海市 上海市 浦东新区 张江路123号'
        >>> format_address(address, "short")
        '浦东新区 张江路123号'
    """
    try:
        if isinstance(address_data, str):
            # 字符串地址直接返回清理后的版本
            cleaned_address = address_data.strip()
            if not cleaned_address:
                return ""
            return cleaned_address

        elif isinstance(address_data, dict):
            # 字典格式的地址数据
            parts = []

            if format_type == "full":
                # 完整地址格式
                fields = ["province", "city", "district", "street", "detail"]
            elif format_type == "short":
                # 简短地址格式
                fields = ["district", "street", "detail"]
            elif format_type == "postal":
                # 邮寄地址格式
                fields = ["province", "city", "district", "detail"]
            else:
                # 默认使用完整格式
                fields = ["province", "city", "district", "detail"]

            # 组装地址部分
            for field in fields:
                value = address_data.get(field, "").strip()
                if value:
                    parts.append(value)

            if not parts:
                return ""

            formatted_address = separator.join(parts)

            # 邮政编码处理
            postal_code = address_data.get("postal_code", "").strip()
            if postal_code and format_type == "postal":
                formatted_address = f"{formatted_address} {postal_code}"

            logger.debug(f"地址格式化: {address_data} -> {formatted_address}")
            return formatted_address

        else:
            return str(address_data) if address_data else ""

    except Exception as e:
        logger.warning(f"地址格式化失败: {e}")
        return str(address_data) if address_data else ""


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """截断文本

    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀

    Returns:
        str: 截断后的文本
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小

    Args:
        size_bytes: 文件大小(字节)

    Returns:
        str: 格式化后的文件大小字符串
    """
    if size_bytes == 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def _format_mobile_phone(clean_phone: str, format_type: str) -> str:
    """格式化手机号"""
    if format_type == "dashed":
        return f"{clean_phone[:3]}-{clean_phone[3:7]}-{clean_phone[7:]}"
    elif format_type == "spaced":
        return f"{clean_phone[:3]} {clean_phone[3:7]} {clean_phone[7:]}"
    else:  # standard
        return f"{clean_phone[:3]}-{clean_phone[3:7]}-{clean_phone[7:]}"


def _format_landline_phone(clean_phone: str) -> str:
    """格式化固定电话"""
    if len(clean_phone) == 7:
        return f"{clean_phone[:3]}-{clean_phone[3:]}"
    elif len(clean_phone) == 8:
        return f"{clean_phone[:4]}-{clean_phone[4:]}"
    elif len(clean_phone) >= 10:
        # 假设前3-4位是区号
        area_codes = ["010", "021", "022", "023", "024", "025", "027", "028", "029"]
        area_code_len = 3 if clean_phone[:3] in area_codes else 4
        return f"{clean_phone[:area_code_len]}-{clean_phone[area_code_len:]}"

    return clean_phone
