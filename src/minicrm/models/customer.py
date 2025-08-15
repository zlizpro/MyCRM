"""
MiniCRM 客户数据模型

定义客户相关的数据结构和业务逻辑，包括：
- 客户基本信息模型
- 客户等级和分类管理
- 客户价值评估
- 数据验证和格式化
- 与transfunctions的集成

设计原则：
- 使用dataclass简化模型定义
- 集成transfunctions进行数据验证和格式化
- 支持客户等级和分类管理
- 提供完整的序列化功能
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from transfunctions import (
    CustomerValueMetrics,
    ValidationError,
    calculate_customer_value_score,
    format_currency,
    format_phone,
    validate_customer_data,
)

from .base import ContactModel, register_model


class CustomerLevel(Enum):
    """客户等级枚举"""

    VIP = "vip"  # VIP客户
    IMPORTANT = "important"  # 重要客户
    NORMAL = "normal"  # 普通客户
    POTENTIAL = "potential"  # 潜在客户


class CustomerType(Enum):
    """客户类型枚举"""

    ENTERPRISE = "enterprise"  # 企业客户
    INDIVIDUAL = "individual"  # 个人客户
    GOVERNMENT = "government"  # 政府客户
    NONPROFIT = "nonprofit"  # 非营利组织


class IndustryType(Enum):
    """行业类型枚举"""

    FURNITURE = "furniture"  # 家具制造
    CONSTRUCTION = "construction"  # 建筑装修
    INTERIOR_DESIGN = "interior_design"  # 室内设计
    WHOLESALE = "wholesale"  # 批发贸易
    RETAIL = "retail"  # 零售
    OTHER = "other"  # 其他


@register_model
@dataclass
class Customer(ContactModel):
    """
    客户数据模型

    继承自ContactModel，包含客户的完整信息，包括基本信息、
    业务信息、统计数据等。集成transfunctions进行数据验证和格式化。
    """

    # 客户分类信息
    customer_level: CustomerLevel = CustomerLevel.NORMAL
    customer_type: CustomerType = CustomerType.ENTERPRISE
    industry_type: IndustryType = IndustryType.OTHER

    # 业务信息
    company_name: str = ""
    tax_id: str = ""  # 税号
    credit_limit: Decimal = Decimal("0.00")  # 授信额度
    payment_terms: int = 30  # 付款期限（天）

    # 统计信息
    total_orders: int = 0
    total_amount: Decimal = Decimal("0.00")
    last_order_date: datetime | None = None
    last_contact_date: datetime | None = None

    # 客户价值评分
    value_score: float = 0.0
    loyalty_score: float = 0.0

    # 标签和备注
    tags: list[str] | None = None
    source: str = ""  # 客户来源

    def __post_init__(self):
        """初始化后处理"""
        # 初始化标签列表
        if self.tags is None:
            self.tags = []

        # 清理字符串字段
        self.company_name = self.company_name.strip()
        self.tax_id = self.tax_id.strip()
        self.source = self.source.strip()

        # 如果没有设置公司名称，使用客户姓名
        if not self.company_name and self.name:
            self.company_name = self.name

        super().__post_init__()

    def validate(self) -> None:
        """验证客户数据"""
        super().validate()

        # 使用transfunctions验证客户数据
        # 映射客户类型到验证函数期望的格式
        customer_type_map = {
            CustomerType.ENTERPRISE.value: "其他",  # 企业客户映射为其他
            CustomerType.INDIVIDUAL.value: "其他",  # 个人客户映射为其他
            CustomerType.GOVERNMENT.value: "其他",  # 政府客户映射为其他
            CustomerType.NONPROFIT.value: "其他",  # 非营利组织映射为其他
        }

        customer_data = {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "company_name": self.company_name,
            "customer_type": customer_type_map.get(self.customer_type.value, "其他"),
            "credit_limit": float(self.credit_limit),
        }

        validation_result = validate_customer_data(customer_data)
        if not validation_result.is_valid:
            error_messages = "; ".join(validation_result.errors)
            raise ValidationError(f"客户数据验证失败: {error_messages}") from None

        # 验证授信额度
        if self.credit_limit < 0:
            raise ValidationError("授信额度不能为负数")

        # 验证付款期限
        if self.payment_terms < 0 or self.payment_terms > 365:
            raise ValidationError("付款期限必须在0-365天之间")

    def calculate_value_score(self) -> CustomerValueMetrics:
        """
        计算客户价值评分

        使用transfunctions中的客户价值计算函数

        Returns:
            CustomerValueMetrics: 客户价值指标
        """
        # 准备计算数据
        customer_data = {
            "customer_id": self.id or 0,
            "total_amount": float(self.total_amount),
            "total_orders": self.total_orders,
            "last_order_date": self.last_order_date,
            "customer_level": self.customer_level.value,
            "cooperation_months": self._calculate_cooperation_months(),
        }

        # 使用transfunctions计算客户价值
        # 提供空的历史数据作为默认值
        transaction_history: list[dict[str, Any]] = []
        interaction_history: list[dict[str, Any]] = []

        metrics = calculate_customer_value_score(
            customer_data, transaction_history, interaction_history
        )

        # 更新模型中的评分
        self.value_score = metrics.total_score
        self.loyalty_score = metrics.loyalty_score

        return metrics

    def _calculate_cooperation_months(self) -> int:
        """计算合作月数"""
        if not self.created_at:
            return 0

        now = datetime.now()
        delta = now - self.created_at
        return max(1, delta.days // 30)

    def add_tag(self, tag: str) -> None:
        """添加标签"""
        tag = tag.strip()
        if tag and self.tags is not None and tag not in self.tags:
            self.tags.append(tag)
            self.update_timestamp()

    def remove_tag(self, tag: str) -> None:
        """移除标签"""
        if self.tags is not None and tag in self.tags:
            self.tags.remove(tag)
            self.update_timestamp()

    def has_tag(self, tag: str) -> bool:
        """检查是否有指定标签"""
        return self.tags is not None and tag in self.tags

    def update_contact_date(self) -> None:
        """更新最后联系日期"""
        self.last_contact_date = datetime.now()
        self.update_timestamp()

    def update_order_stats(
        self, order_amount: Decimal, order_date: datetime | None = None
    ) -> None:
        """
        更新订单统计信息

        Args:
            order_amount: 订单金额
            order_date: 订单日期，默认为当前时间
        """
        if order_date is None:
            order_date = datetime.now()

        self.total_orders += 1
        self.total_amount += order_amount
        self.last_order_date = order_date
        self.update_timestamp()

    def is_vip(self) -> bool:
        """检查是否为VIP客户"""
        return self.customer_level == CustomerLevel.VIP

    def is_active_customer(self, days_threshold: int = 90) -> bool:
        """
        检查是否为活跃客户

        Args:
            days_threshold: 活跃度阈值（天）

        Returns:
            bool: 是否为活跃客户
        """
        if not self.last_contact_date and not self.last_order_date:
            return False

        last_activity = max(
            self.last_contact_date or datetime.min, self.last_order_date or datetime.min
        )

        days_since_activity = (datetime.now() - last_activity).days
        return days_since_activity <= days_threshold

    def get_formatted_phone(self) -> str:
        """获取格式化的电话号码"""
        if not self.phone:
            return ""
        return format_phone(self.phone)

    def get_formatted_credit_limit(self) -> str:
        """获取格式化的授信额度"""
        return format_currency(float(self.credit_limit))

    def get_formatted_total_amount(self) -> str:
        """获取格式化的总交易金额"""
        return format_currency(float(self.total_amount))

    def to_dict(self, include_private: bool = False) -> dict[str, Any]:
        """转换为字典，包含格式化的字段"""
        data = super().to_dict(include_private)

        # 添加格式化字段
        data.update(
            {
                "formatted_phone": self.get_formatted_phone(),
                "formatted_credit_limit": self.get_formatted_credit_limit(),
                "formatted_total_amount": self.get_formatted_total_amount(),
                "customer_level_display": self.customer_level.value,
                "customer_type_display": self.customer_type.value,
                "industry_type_display": self.industry_type.value,
                "is_vip": self.is_vip(),
                "is_active": self.is_active_customer(),
                "cooperation_months": self._calculate_cooperation_months(),
            }
        )

        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Customer":
        """从字典创建客户实例"""
        # 过滤掉计算字段和格式化字段
        computed_fields = {
            "formatted_phone",
            "formatted_credit_limit",
            "formatted_total_amount",
            "customer_level_display",
            "customer_type_display",
            "industry_type_display",
            "is_vip",
            "is_active",
            "cooperation_months",
        }
        data = {k: v for k, v in data.items() if k not in computed_fields}

        # 处理枚举字段
        if "customer_level" in data and isinstance(data["customer_level"], str):
            try:
                data["customer_level"] = CustomerLevel(data["customer_level"])
            except ValueError:
                data["customer_level"] = CustomerLevel.NORMAL

        if "customer_type" in data and isinstance(data["customer_type"], str):
            try:
                data["customer_type"] = CustomerType(data["customer_type"])
            except ValueError:
                data["customer_type"] = CustomerType.ENTERPRISE

        if "industry_type" in data and isinstance(data["industry_type"], str):
            try:
                data["industry_type"] = IndustryType(data["industry_type"])
            except ValueError:
                data["industry_type"] = IndustryType.OTHER

        # 处理Decimal字段
        for field in ["credit_limit", "total_amount"]:
            if field in data and not isinstance(data[field], Decimal):
                try:
                    data[field] = Decimal(str(data[field]))
                except (ValueError, TypeError):
                    data[field] = Decimal("0.00")

        # 处理日期字段
        for field in ["last_order_date", "last_contact_date"]:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field])
                except ValueError:
                    data[field] = None

        # 处理标签列表
        if "tags" in data and not isinstance(data["tags"], list):
            data["tags"] = []

        return super().from_dict(data)

    def __str__(self) -> str:
        """返回客户的字符串表示"""
        company_info = (
            f" ({self.company_name})" if self.company_name != self.name else ""
        )
        level_info = self.customer_level.value
        return (
            f"Customer(id={self.id}, name='{self.name}'{company_info}, "
            f"level={level_info})"
        )
