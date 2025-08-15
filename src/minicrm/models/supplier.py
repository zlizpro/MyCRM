"""
MiniCRM 供应商数据模型

定义供应商相关的数据结构和业务逻辑，包括：
- 供应商基本信息模型
- 供应商等级和质量评估
- 供应产品类别管理
- 数据验证和格式化
- 与transfunctions的集成

设计原则：
- 使用dataclass简化模型定义
- 集成transfunctions进行数据验证和格式化
- 支持供应商质量评级管理
- 提供完整的序列化功能
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from transfunctions import (
    ValidationError,
    format_currency,
    format_phone,
    validate_supplier_data,
)

from .base import ContactModel, register_model


class SupplierLevel(Enum):
    """供应商等级枚举"""

    STRATEGIC = "strategic"  # 战略供应商
    IMPORTANT = "important"  # 重要供应商
    NORMAL = "normal"  # 普通供应商
    BACKUP = "backup"  # 备选供应商


class SupplierStatus(Enum):
    """供应商状态枚举"""

    ACTIVE = "active"  # 活跃
    INACTIVE = "inactive"  # 非活跃
    SUSPENDED = "suspended"  # 暂停合作
    BLACKLISTED = "blacklisted"  # 黑名单


class QualityRating(Enum):
    """质量评级枚举"""

    EXCELLENT = "excellent"  # 优秀 (A级)
    GOOD = "good"  # 良好 (B级)
    AVERAGE = "average"  # 一般 (C级)
    POOR = "poor"  # 较差 (D级)
    UNRATED = "unrated"  # 未评级


class SupplierType(Enum):
    """供应商类型枚举"""

    MANUFACTURER = "manufacturer"  # 制造商
    DISTRIBUTOR = "distributor"  # 经销商
    WHOLESALER = "wholesaler"  # 批发商
    SERVICE_PROVIDER = "service_provider"  # 服务提供商
    OTHER = "other"  # 其他


@register_model
@dataclass
class Supplier(ContactModel):
    """
    供应商数据模型

    继承自ContactModel，包含供应商的完整信息，包括基本信息、
    业务信息、质量评估、统计数据等。集成transfunctions进行数据验证和格式化。
    """

    # 供应商分类信息
    supplier_level: SupplierLevel = SupplierLevel.NORMAL
    supplier_type: SupplierType = SupplierType.MANUFACTURER
    supplier_status: SupplierStatus = SupplierStatus.ACTIVE

    # 质量评估
    quality_rating: QualityRating = QualityRating.UNRATED
    quality_score: float = 0.0  # 质量评分 (0-100)
    delivery_rating: float = 0.0  # 交期评分 (0-100)
    service_rating: float = 0.0  # 服务评分 (0-100)

    # 业务信息
    company_name: str = ""
    business_license: str = ""  # 营业执照号
    tax_id: str = ""  # 税号
    payment_terms: int = 30  # 付款期限（天）

    # 供应产品类别
    product_categories: list[str] | None = None
    main_products: str = ""  # 主要产品描述

    # 统计信息
    total_orders: int = 0
    total_amount: Decimal = Decimal("0.00")
    last_order_date: datetime | None = None
    last_contact_date: datetime | None = None

    # 合作信息
    cooperation_start_date: datetime | None = None
    contract_end_date: datetime | None = None

    # 标签和备注
    tags: list[str] | None = None
    certification: str = ""  # 认证信息

    def __post_init__(self):
        """初始化后处理"""
        # 初始化列表字段
        if self.product_categories is None:
            self.product_categories = []
        if self.tags is None:
            self.tags = []

        # 清理字符串字段
        self.company_name = self.company_name.strip()
        self.business_license = self.business_license.strip()
        self.tax_id = self.tax_id.strip()
        self.main_products = self.main_products.strip()
        self.certification = self.certification.strip()

        # 如果没有设置公司名称，使用供应商姓名
        if not self.company_name and self.name:
            self.company_name = self.name

        super().__post_init__()

    def validate(self) -> None:
        """验证供应商数据"""
        super().validate()

        # 使用transfunctions验证供应商数据
        supplier_data = {
            "name": self.name,
            "contact_person": self.contact_person
            or self.name,  # 如果没有联系人，使用供应商名称
            "phone": self.phone,
            "email": self.email,
            "company_name": self.company_name,
            "supplier_type": self.supplier_type.value,
            "business_license": self.business_license,
        }

        validation_result = validate_supplier_data(supplier_data)
        if not validation_result.is_valid:
            error_messages = "; ".join(validation_result.errors)
            raise ValidationError(f"供应商数据验证失败: {error_messages}") from None

        # 验证评分范围
        for score_field, score_value in [
            ("quality_score", self.quality_score),
            ("delivery_rating", self.delivery_rating),
            ("service_rating", self.service_rating),
        ]:
            if not (0 <= score_value <= 100):
                raise ValidationError(f"{score_field}必须在0-100之间")

        # 验证付款期限
        if self.payment_terms < 0 or self.payment_terms > 365:
            raise ValidationError("付款期限必须在0-365天之间")

    def calculate_overall_rating(self) -> float:
        """
        计算综合评级

        基于质量、交期、服务三个维度计算综合评分

        Returns:
            float: 综合评分 (0-100)
        """
        if all(
            score == 0
            for score in [self.quality_score, self.delivery_rating, self.service_rating]
        ):
            return 0.0

        # 权重分配：质量40%，交期30%，服务30%
        overall_score = (
            self.quality_score * 0.4
            + self.delivery_rating * 0.3
            + self.service_rating * 0.3
        )

        return round(overall_score, 2)

    def update_quality_rating(self) -> None:
        """根据评分更新质量等级"""
        overall_score = self.calculate_overall_rating()

        if overall_score >= 90:
            self.quality_rating = QualityRating.EXCELLENT
        elif overall_score >= 80:
            self.quality_rating = QualityRating.GOOD
        elif overall_score >= 60:
            self.quality_rating = QualityRating.AVERAGE
        elif overall_score > 0:
            self.quality_rating = QualityRating.POOR
        else:
            self.quality_rating = QualityRating.UNRATED

        self.update_timestamp()

    def add_product_category(self, category: str) -> None:
        """添加产品类别"""
        category = category.strip()
        if (
            category
            and self.product_categories is not None
            and category not in self.product_categories
        ):
            self.product_categories.append(category)
            self.update_timestamp()

    def remove_product_category(self, category: str) -> None:
        """移除产品类别"""
        if self.product_categories is not None and category in self.product_categories:
            self.product_categories.remove(category)
            self.update_timestamp()

    def has_product_category(self, category: str) -> bool:
        """检查是否有指定产品类别"""
        return (
            self.product_categories is not None and category in self.product_categories
        )

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

    def is_strategic(self) -> bool:
        """检查是否为战略供应商"""
        return self.supplier_level == SupplierLevel.STRATEGIC

    def is_active_supplier(self, days_threshold: int = 90) -> bool:
        """
        检查是否为活跃供应商

        Args:
            days_threshold: 活跃度阈值（天）

        Returns:
            bool: 是否为活跃供应商
        """
        if self.supplier_status != SupplierStatus.ACTIVE:
            return False

        if not self.last_contact_date and not self.last_order_date:
            return False

        last_activity = max(
            self.last_contact_date or datetime.min, self.last_order_date or datetime.min
        )

        days_since_activity = (datetime.now() - last_activity).days
        return days_since_activity <= days_threshold

    def is_contract_expiring(self, days_threshold: int = 30) -> bool:
        """
        检查合同是否即将到期

        Args:
            days_threshold: 到期预警阈值（天）

        Returns:
            bool: 合同是否即将到期
        """
        if not self.contract_end_date:
            return False

        days_to_expiry = (self.contract_end_date - datetime.now()).days
        return 0 <= days_to_expiry <= days_threshold

    def get_cooperation_months(self) -> int:
        """获取合作月数"""
        start_date = self.cooperation_start_date or self.created_at
        if not start_date:
            return 0

        now = datetime.now()
        delta = now - start_date
        return max(1, delta.days // 30)

    def get_formatted_phone(self) -> str:
        """获取格式化的电话号码"""
        if not self.phone:
            return ""
        return format_phone(self.phone)

    def get_formatted_total_amount(self) -> str:
        """获取格式化的总交易金额"""
        return format_currency(float(self.total_amount))

    def get_quality_rating_display(self) -> str:
        """获取质量评级显示文本"""
        rating_map = {
            QualityRating.EXCELLENT: "优秀 (A级)",
            QualityRating.GOOD: "良好 (B级)",
            QualityRating.AVERAGE: "一般 (C级)",
            QualityRating.POOR: "较差 (D级)",
            QualityRating.UNRATED: "未评级",
        }
        return rating_map.get(self.quality_rating, "未知")

    def to_dict(self, include_private: bool = False) -> dict[str, Any]:
        """转换为字典，包含格式化的字段"""
        data = super().to_dict(include_private)

        # 添加格式化字段
        data.update(
            {
                "formatted_phone": self.get_formatted_phone(),
                "formatted_total_amount": self.get_formatted_total_amount(),
                "supplier_level_display": self.supplier_level.value,
                "supplier_type_display": self.supplier_type.value,
                "supplier_status_display": self.supplier_status.value,
                "quality_rating_display": self.get_quality_rating_display(),
                "overall_rating": self.calculate_overall_rating(),
                "is_strategic": self.is_strategic(),
                "is_active": self.is_active_supplier(),
                "is_contract_expiring": self.is_contract_expiring(),
                "cooperation_months": self.get_cooperation_months(),
            }
        )

        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Supplier":
        """从字典创建供应商实例"""
        # 处理枚举字段
        enum_fields = {
            "supplier_level": (SupplierLevel, SupplierLevel.NORMAL),
            "supplier_type": (SupplierType, SupplierType.MANUFACTURER),
            "supplier_status": (SupplierStatus, SupplierStatus.ACTIVE),
            "quality_rating": (QualityRating, QualityRating.UNRATED),
        }

        for field, (enum_class, default_value) in enum_fields.items():
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = enum_class(data[field])
                except ValueError:
                    data[field] = default_value

        # 处理Decimal字段
        for field in ["total_amount"]:
            if field in data and not isinstance(data[field], Decimal):
                try:
                    data[field] = Decimal(str(data[field]))
                except (ValueError, TypeError):
                    data[field] = Decimal("0.00")

        # 处理日期字段
        date_fields = [
            "last_order_date",
            "last_contact_date",
            "cooperation_start_date",
            "contract_end_date",
        ]
        for field in date_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field])
                except ValueError:
                    data[field] = None

        # 处理列表字段
        for field in ["product_categories", "tags"]:
            if field in data and not isinstance(data[field], list):
                data[field] = []

        return super().from_dict(data)

    def __str__(self) -> str:
        """返回供应商的字符串表示"""
        company_info = (
            f" ({self.company_name})" if self.company_name != self.name else ""
        )
        level_info = self.supplier_level.value
        return (
            f"Supplier(id={self.id}, name='{self.name}'{company_info}, "
            f"level={level_info})"
        )
