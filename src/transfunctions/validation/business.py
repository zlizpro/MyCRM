"""
Transfunctions - 业务验证函数

提供MiniCRM业务相关的验证功能,包括客户、供应商等业务实体验证.
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
            field: 出错的字段名(可选)
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
    # 中国大陆手机号码(11位,1开头)
    "mobile_phone": r"^1[3-9]\d{9}$",
    # 固定电话(区号-号码格式)
    "landline_phone": r"^0\d{2,3}-?\d{7,8}$",
    # 邮箱地址
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    # 中文姓名(2-10个中文字符)
    "chinese_name": r"^[\u4e00-\u9fa5]{2,10}$",
    # 公司名称(中文、英文、数字、常用符号)
    "company_name": r"^[\u4e00-\u9fa5a-zA-Z0-9\(\)\(\)\&\-\s]{2,50}$",
    # 统一社会信用代码(18位)
    "credit_code": r"^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$",
    # 邮政编码(6位数字)
    "postal_code": r"^\d{6}$",
}


def validate_customer_data(customer_data: dict[str, Any]) -> ValidationResult:
    """验证客户数据完整性和格式

    Args:
        customer_data: 客户数据字典,包含姓名、电话、邮箱等信息

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

    # 邮箱验证(可选字段)
    email = customer_data.get("email", "").strip()
    if email:
        if not validate_email(email):
            result.add_error("邮箱地址格式不正确")

    # 公司名称验证(可选字段)
    company = customer_data.get("company", "").strip()
    if company:
        if len(company) > 100:
            result.add_error("公司名称不能超过100个字符")
        elif not re.match(PATTERNS["company_name"], company):
            result.add_warning("公司名称包含特殊字符,请确认是否正确")

    # 客户等级验证
    level = customer_data.get("level")
    if level and level not in ["VIP", "重要", "普通", "潜在"]:
        result.add_error("客户等级必须是:VIP、重要、普通、潜在之一")

    # 地址验证(可选字段)
    address = customer_data.get("address", "").strip()
    if address and len(address) > 200:
        result.add_error("地址不能超过200个字符")

    # 客户类型检查(板材行业特定)
    valid_types = ["生态板客户", "家具板客户", "阻燃板客户", "其他"]
    if (
        customer_data.get("customer_type")
        and customer_data["customer_type"] not in valid_types
    ):
        result.add_error(f"客户类型必须是以下之一: {', '.join(valid_types)}")

    logger.info(f"客户数据验证完成,有效性: {result.is_valid}")
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

    # 邮箱验证(可选)
    email = supplier_data.get("email", "").strip()
    if email:
        if not validate_email(email):
            result.add_error("邮箱地址格式不正确")

    # 统一社会信用代码验证(可选)
    credit_code = supplier_data.get("credit_code", "").strip()
    if credit_code:
        if not re.match(PATTERNS["credit_code"], credit_code):
            result.add_error("统一社会信用代码格式不正确")

    # 供应商等级验证
    level = supplier_data.get("level")
    if level and level not in ["战略", "重要", "普通", "备选"]:
        result.add_error("供应商等级必须是:战略、重要、普通、备选之一")

    # 兼容旧的等级系统
    valid_grades = ["A级", "B级", "C级", "D级"]
    if supplier_data.get("grade") and supplier_data["grade"] not in valid_grades:
        result.add_warning("建议使用新的等级系统:战略、重要、普通、备选")

    logger.info(f"供应商数据验证完成,有效性: {result.is_valid}")
    return result


def validate_contract_data(contract_data: dict[str, Any]) -> ValidationResult:
    """验证合同数据完整性和格式

    Args:
        contract_data: 合同数据字典,包含合同编号、合同方、金额等信息

    Returns:
        ValidationResult: 验证结果对象

    Example:
        >>> data = {"contract_number": "C2025001", "party_name": "ABC公司", "contract_amount": 100000}
        >>> result = validate_contract_data(data)
        >>> print(result.is_valid)
        True
    """
    result = ValidationResult(is_valid=True, errors=[], warnings=[])

    # 必填字段检查
    required_fields = ["contract_number", "party_name", "contract_type", "contract_amount"]
    for field in required_fields:
        if not contract_data.get(field):
            result.add_error(f"合同{field}不能为空")

    # 合同编号验证
    contract_number = contract_data.get("contract_number", "").strip()
    if contract_number:
        if len(contract_number) < 3:
            result.add_error("合同编号至少需要3个字符")
        elif len(contract_number) > 50:
            result.add_error("合同编号不能超过50个字符")
        # 检查编号格式(建议格式: C+年份+序号)
        if not re.match(r"^[A-Z]\d{4}\d{3,}$", contract_number):
            result.add_warning("建议使用标准格式: C+年份+序号 (如C2025001)")

    # 合同方名称验证
    party_name = contract_data.get("party_name", "").strip()
    if party_name:
        if len(party_name) < 2:
            result.add_error("合同方名称至少需要2个字符")
        elif len(party_name) > 100:
            result.add_error("合同方名称不能超过100个字符")

    # 合同类型验证
    contract_type = contract_data.get("contract_type")
    valid_types = ["sales", "purchase", "service", "framework", "other"]
    if contract_type and contract_type not in valid_types:
        result.add_error(f"合同类型必须是以下之一: {', '.join(valid_types)}")

    # 合同状态验证
    contract_status = contract_data.get("contract_status")
    valid_statuses = ["draft", "pending", "approved", "signed", "active", "completed", "terminated", "expired"]
    if contract_status and contract_status not in valid_statuses:
        result.add_error(f"合同状态必须是以下之一: {', '.join(valid_statuses)}")

    # 合同金额验证
    contract_amount = contract_data.get("contract_amount")
    if contract_amount is not None:
        try:
            amount = float(contract_amount)
            if amount < 0:
                result.add_error("合同金额不能为负数")
            elif amount == 0:
                result.add_warning("合同金额为0，请确认是否正确")
            elif amount > 10000000:  # 1000万
                result.add_warning("合同金额较大，请确认是否正确")
        except (ValueError, TypeError):
            result.add_error("合同金额必须是有效的数字")

    # 日期验证
    from datetime import datetime
    
    # 签署日期验证
    sign_date = contract_data.get("sign_date")
    if sign_date:
        try:
            if isinstance(sign_date, str):
                datetime.strptime(sign_date, "%Y-%m-%d")
        except ValueError:
            result.add_error("签署日期格式不正确，应为YYYY-MM-DD")

    # 生效日期验证
    effective_date = contract_data.get("effective_date")
    if effective_date:
        try:
            if isinstance(effective_date, str):
                datetime.strptime(effective_date, "%Y-%m-%d")
        except ValueError:
            result.add_error("生效日期格式不正确，应为YYYY-MM-DD")

    # 到期日期验证
    expiry_date = contract_data.get("expiry_date")
    if expiry_date:
        try:
            if isinstance(expiry_date, str):
                expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
                # 检查是否已过期
                if expiry < datetime.now():
                    result.add_warning("合同已过期")
        except ValueError:
            result.add_error("到期日期格式不正确，应为YYYY-MM-DD")

    # 日期逻辑验证
    if sign_date and effective_date:
        try:
            sign_dt = datetime.strptime(sign_date, "%Y-%m-%d") if isinstance(sign_date, str) else sign_date
            effective_dt = datetime.strptime(effective_date, "%Y-%m-%d") if isinstance(effective_date, str) else effective_date
            if effective_dt < sign_dt:
                result.add_error("生效日期不能早于签署日期")
        except:
            pass

    if effective_date and expiry_date:
        try:
            effective_dt = datetime.strptime(effective_date, "%Y-%m-%d") if isinstance(effective_date, str) else effective_date
            expiry_dt = datetime.strptime(expiry_date, "%Y-%m-%d") if isinstance(expiry_date, str) else expiry_date
            if expiry_dt <= effective_dt:
                result.add_error("到期日期必须晚于生效日期")
        except:
            pass

    # 付款方式验证
    payment_method = contract_data.get("payment_method")
    valid_payment_methods = ["现金", "银行转账", "支票", "承兑汇票", "信用证", "其他"]
    if payment_method and payment_method not in valid_payment_methods:
        result.add_warning(f"建议使用标准付款方式: {', '.join(valid_payment_methods)}")

    # 进度验证
    progress = contract_data.get("progress_percentage")
    if progress is not None:
        try:
            progress_val = float(progress)
            if progress_val < 0 or progress_val > 100:
                result.add_error("合同进度必须在0-100之间")
        except (ValueError, TypeError):
            result.add_error("合同进度必须是有效的数字")

    logger.info(f"合同数据验证完成,有效性: {result.is_valid}")
    return result


def validate_service_ticket_data(ticket_data: dict[str, Any]) -> ValidationResult:
    """验证售后工单数据完整性和格式

    Args:
        ticket_data: 售后工单数据字典

    Returns:
        ValidationResult: 验证结果对象

    Example:
        >>> data = {"ticket_number": "T2025001", "customer_id": 1, "issue_type": "质量问题"}
        >>> result = validate_service_ticket_data(data)
        >>> print(result.is_valid)
        True
    """
    result = ValidationResult(is_valid=True, errors=[], warnings=[])

    # 必填字段检查
    required_fields = ["ticket_number", "customer_id", "issue_type", "description"]
    for field in required_fields:
        if not ticket_data.get(field):
            result.add_error(f"工单{field}不能为空")

    # 工单编号验证
    ticket_number = ticket_data.get("ticket_number", "").strip()
    if ticket_number:
        if len(ticket_number) < 3:
            result.add_error("工单编号至少需要3个字符")
        elif len(ticket_number) > 50:
            result.add_error("工单编号不能超过50个字符")
        # 检查编号格式(建议格式: T+年份+序号)
        if not re.match(r"^[A-Z]\d{4}\d{3,}$", ticket_number):
            result.add_warning("建议使用标准格式: T+年份+序号 (如T2025001)")

    # 客户ID验证
    customer_id = ticket_data.get("customer_id")
    if customer_id is not None:
        try:
            cid = int(customer_id)
            if cid <= 0:
                result.add_error("客户ID必须是正整数")
        except (ValueError, TypeError):
            result.add_error("客户ID必须是有效的整数")

    # 问题类型验证
    issue_type = ticket_data.get("issue_type")
    valid_issue_types = ["质量问题", "使用问题", "安装问题", "配件更换", "功能咨询", "投诉建议", "其他"]
    if issue_type and issue_type not in valid_issue_types:
        result.add_error(f"问题类型必须是以下之一: {', '.join(valid_issue_types)}")

    # 优先级验证
    priority = ticket_data.get("priority")
    valid_priorities = ["低", "中", "高", "紧急"]
    if priority and priority not in valid_priorities:
        result.add_error(f"优先级必须是以下之一: {', '.join(valid_priorities)}")

    # 状态验证
    status = ticket_data.get("status")
    valid_statuses = ["待处理", "处理中", "待客户确认", "已解决", "已关闭", "已取消"]
    if status and status not in valid_statuses:
        result.add_error(f"工单状态必须是以下之一: {', '.join(valid_statuses)}")

    # 描述验证
    description = ticket_data.get("description", "").strip()
    if description:
        if len(description) < 10:
            result.add_warning("问题描述建议至少10个字符，以便更好地理解问题")
        elif len(description) > 1000:
            result.add_error("问题描述不能超过1000个字符")

    # 解决方案验证
    solution = ticket_data.get("solution", "").strip()
    if solution and len(solution) > 1000:
        result.add_error("解决方案不能超过1000个字符")

    # 满意度验证
    satisfaction = ticket_data.get("satisfaction")
    if satisfaction is not None:
        try:
            sat_val = int(satisfaction)
            if sat_val < 1 or sat_val > 5:
                result.add_error("满意度评分必须在1-5之间")
        except (ValueError, TypeError):
            result.add_error("满意度评分必须是有效的整数")

    # 日期验证
    from datetime import datetime
    
    created_date = ticket_data.get("created_date")
    if created_date:
        try:
            if isinstance(created_date, str):
                datetime.strptime(created_date, "%Y-%m-%d")
        except ValueError:
            result.add_error("创建日期格式不正确，应为YYYY-MM-DD")

    resolved_date = ticket_data.get("resolved_date")
    if resolved_date:
        try:
            if isinstance(resolved_date, str):
                datetime.strptime(resolved_date, "%Y-%m-%d")
        except ValueError:
            result.add_error("解决日期格式不正确，应为YYYY-MM-DD")

    logger.info(f"售后工单数据验证完成,有效性: {result.is_valid}")
    return result


def validate_quote_data(quote_data: dict[str, Any]) -> ValidationResult:
    """验证报价数据完整性和格式

    Args:
        quote_data: 报价数据字典

    Returns:
        ValidationResult: 验证结果对象

    Example:
        >>> data = {"quote_number": "Q2025001", "customer_id": 1, "total_amount": 50000}
        >>> result = validate_quote_data(data)
        >>> print(result.is_valid)
        True
    """
    result = ValidationResult(is_valid=True, errors=[], warnings=[])

    # 必填字段检查
    required_fields = ["quote_number", "customer_id", "total_amount"]
    for field in required_fields:
        if not quote_data.get(field):
            result.add_error(f"报价{field}不能为空")

    # 报价编号验证
    quote_number = quote_data.get("quote_number", "").strip()
    if quote_number:
        if len(quote_number) < 3:
            result.add_error("报价编号至少需要3个字符")
        elif len(quote_number) > 50:
            result.add_error("报价编号不能超过50个字符")
        # 检查编号格式(建议格式: Q+年份+序号)
        if not re.match(r"^[A-Z]\d{4}\d{3,}$", quote_number):
            result.add_warning("建议使用标准格式: Q+年份+序号 (如Q2025001)")

    # 客户ID验证
    customer_id = quote_data.get("customer_id")
    if customer_id is not None:
        try:
            cid = int(customer_id)
            if cid <= 0:
                result.add_error("客户ID必须是正整数")
        except (ValueError, TypeError):
            result.add_error("客户ID必须是有效的整数")

    # 报价总额验证
    total_amount = quote_data.get("total_amount")
    if total_amount is not None:
        try:
            amount = float(total_amount)
            if amount < 0:
                result.add_error("报价总额不能为负数")
            elif amount == 0:
                result.add_warning("报价总额为0，请确认是否正确")
            elif amount > 10000000:  # 1000万
                result.add_warning("报价总额较大，请确认是否正确")
        except (ValueError, TypeError):
            result.add_error("报价总额必须是有效的数字")

    # 报价状态验证
    status = quote_data.get("status")
    valid_statuses = ["草稿", "已发送", "客户确认", "已接受", "已拒绝", "已过期"]
    if status and status not in valid_statuses:
        result.add_error(f"报价状态必须是以下之一: {', '.join(valid_statuses)}")

    # 有效期验证
    valid_days = quote_data.get("valid_days")
    if valid_days is not None:
        try:
            days = int(valid_days)
            if days <= 0:
                result.add_error("报价有效期必须是正整数")
            elif days > 365:
                result.add_warning("报价有效期超过一年，请确认是否正确")
        except (ValueError, TypeError):
            result.add_error("报价有效期必须是有效的整数")

    # 日期验证
    from datetime import datetime
    
    quote_date = quote_data.get("quote_date")
    if quote_date:
        try:
            if isinstance(quote_date, str):
                datetime.strptime(quote_date, "%Y-%m-%d")
        except ValueError:
            result.add_error("报价日期格式不正确，应为YYYY-MM-DD")

    expiry_date = quote_data.get("expiry_date")
    if expiry_date:
        try:
            if isinstance(expiry_date, str):
                expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
                # 检查是否已过期
                if expiry < datetime.now():
                    result.add_warning("报价已过期")
        except ValueError:
            result.add_error("过期日期格式不正确，应为YYYY-MM-DD")

    # 报价项目验证
    items = quote_data.get("items", [])
    if items:
        for i, item in enumerate(items):
            if not item.get("product_name"):
                result.add_error(f"第{i+1}项产品名称不能为空")
            
            quantity = item.get("quantity")
            if quantity is not None:
                try:
                    qty = float(quantity)
                    if qty <= 0:
                        result.add_error(f"第{i+1}项产品数量必须大于0")
                except (ValueError, TypeError):
                    result.add_error(f"第{i+1}项产品数量必须是有效的数字")
            
            unit_price = item.get("unit_price")
            if unit_price is not None:
                try:
                    price = float(unit_price)
                    if price < 0:
                        result.add_error(f"第{i+1}项产品单价不能为负数")
                except (ValueError, TypeError):
                    result.add_error(f"第{i+1}项产品单价必须是有效的数字")

    logger.info(f"报价数据验证完成,有效性: {result.is_valid}")
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
