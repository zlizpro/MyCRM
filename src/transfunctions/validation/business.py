"""
Transfunctions - 业务验证函数

提供MiniCRM业务相关的验证功能，包括客户、供应商等业务实体验证。
"""

import logging
import re
from dataclasses import dataclass
from typing import Any

from .core import validate_email, validate_phone

# 配置日志
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """数据验证异常类"""

    def __init__(self, message: str, field: str | None = None):
        """初始化验证异常

        Args:
            message: 错误消息
            field: 出错的字段名（可选）
        """
        self.message = message
        self.field = field
        super().__init__(self.message)


@dataclass
class ValidationResult:
    """验证结果数据类"""

    is_valid: bool
    errors: list[str]
    warnings: list[str]

    def add_error(self, error: str) -> None:
        """添加错误信息"""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """添加警告信息"""
        self.warnings.append(warning)


# 常用正则表达式模式
PATTERNS = {
    # 中国大陆手机号码（11位，1开头）
    "mobile_phone": r"^1[3-9]\d{9}$",
    # 固定电话（区号-号码格式）
    "landline_phone": r"^0\d{2,3}-?\d{7,8}$",
    # 邮箱地址
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    # 中文姓名（2-10个中文字符）
    "chinese_name": r"^[\u4e00-\u9fa5]{2,10}$",
    # 公司名称（中文、英文、数字、常用符号）
    "company_name": r"^[\u4e00-\u9fa5a-zA-Z0-9\(\)\（\）\&\-\s]{2,50}$",
    # 统一社会信用代码（18位）
    "credit_code": r"^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$",
    # 邮政编码（6位数字）
    "postal_code": r"^\d{6}$",
}


def validate_customer_data(customer_data: dict[str, Any]) -> ValidationResult:
    """验证客户数据完整性和格式

    Args:
        customer_data: 客户数据字典，包含姓名、电话、邮箱等信息

    Returns:
        ValidationResult: 验证结果对象

    Example:
        >>> data = {"name": "张三", "phone": "13812345678", "email": "zhang@example.com"}
        >>> result = validate_customer_data(data)
        >>> print(result.is_valid)
        True
    """
    result = ValidationResult(is_valid=True, errors=[], warnings=[])

    # 必填字段检查
    required_fields = ["name", "phone"]
    for field in required_fields:
        if not customer_data.get(field):
            result.add_error(f"客户{field}不能为空")

    # 客户名称验证
    name = customer_data.get("name", "").strip()
    if name:
        if len(name) < 2:
            result.add_error("客户名称至少需要2个字符")
        elif len(name) > 50:
            result.add_error("客户名称不能超过50个字符")

    # 电话号码验证
    phone = customer_data.get("phone", "").strip()
    if phone:
        if not validate_phone(phone):
            result.add_error("电话号码格式不正确")

    # 邮箱验证（可选字段）
    email = customer_data.get("email", "").strip()
    if email:
        if not validate_email(email):
            result.add_error("邮箱地址格式不正确")

    # 公司名称验证（可选字段）
    company = customer_data.get("company", "").strip()
    if company:
        if len(company) > 100:
            result.add_error("公司名称不能超过100个字符")
        elif not re.match(PATTERNS["company_name"], company):
            result.add_warning("公司名称包含特殊字符，请确认是否正确")

    # 客户等级验证
    level = customer_data.get("level")
    if level and level not in ["VIP", "重要", "普通", "潜在"]:
        result.add_error("客户等级必须是：VIP、重要、普通、潜在之一")

    # 地址验证（可选字段）
    address = customer_data.get("address", "").strip()
    if address and len(address) > 200:
        result.add_error("地址不能超过200个字符")

    # 客户类型检查（板材行业特定）
    valid_types = ["生态板客户", "家具板客户", "阻燃板客户", "其他"]
    if (
        customer_data.get("customer_type")
        and customer_data["customer_type"] not in valid_types
    ):
        result.add_error(f"客户类型必须是以下之一: {', '.join(valid_types)}")

    logger.info(f"客户数据验证完成，有效性: {result.is_valid}")
    return result


def validate_supplier_data(supplier_data: dict[str, Any]) -> ValidationResult:
    """验证供应商数据完整性和格式

    Args:
        supplier_data: 供应商数据字典

    Returns:
        ValidationResult: 验证结果对象
    """
    result = ValidationResult(is_valid=True, errors=[], warnings=[])

    # 必填字段检查
    required_fields = ["name", "contact_person", "phone"]
    for field in required_fields:
        if not supplier_data.get(field):
            result.add_error(f"供应商{field}不能为空")

    # 供应商名称验证
    name = supplier_data.get("name", "").strip()
    if name:
        if len(name) < 2:
            result.add_error("供应商名称至少需要2个字符")
        elif len(name) > 100:
            result.add_error("供应商名称不能超过100个字符")

    # 联系人验证
    contact_person = supplier_data.get("contact_person", "").strip()
    if contact_person:
        if len(contact_person) < 2:
            result.add_error("联系人姓名至少需要2个字符")
        elif len(contact_person) > 20:
            result.add_error("联系人姓名不能超过20个字符")

    # 电话号码验证
    phone = supplier_data.get("phone", "").strip()
    if phone:
        if not validate_phone(phone):
            result.add_error("电话号码格式不正确")

    # 邮箱验证（可选）
    email = supplier_data.get("email", "").strip()
    if email:
        if not validate_email(email):
            result.add_error("邮箱地址格式不正确")

    # 统一社会信用代码验证（可选）
    credit_code = supplier_data.get("credit_code", "").strip()
    if credit_code:
        if not re.match(PATTERNS["credit_code"], credit_code):
            result.add_error("统一社会信用代码格式不正确")

    # 供应商等级验证
    level = supplier_data.get("level")
    if level and level not in ["战略", "重要", "普通", "备选"]:
        result.add_error("供应商等级必须是：战略、重要、普通、备选之一")

    # 兼容旧的等级系统
    valid_grades = ["A级", "B级", "C级", "D级"]
    if supplier_data.get("grade") and supplier_data["grade"] not in valid_grades:
        result.add_warning("建议使用新的等级系统：战略、重要、普通、备选")

    logger.info(f"供应商数据验证完成，有效性: {result.is_valid}")
    return result


def validate_business_rules(data: dict[str, Any], rules: dict[str, Any]) -> list[str]:
    """验证业务规则

    Args:
        data: 数据字典
        rules: 业务规则字典

    Returns:
        List[str]: 业务规则违规信息列表
    """
    errors = []

    # 示例业务规则验证
    if "max_amount_for_regular" in rules:
        if (
            data.get("customer_level") != "VIP"
            and data.get("amount", 0) > rules["max_amount_for_regular"]
        ):
            errors.append(
                f"普通客户单笔金额不能超过{rules['max_amount_for_regular']}元"
            )

    return errors
