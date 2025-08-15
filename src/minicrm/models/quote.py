"""
MiniCRM 报价数据模型

定义报价相关的数据结构和业务逻辑，包括：
- 报价基本信息模型
- 报价项目和产品清单
- 报价状态和历史管理
- 数据验证和格式化
- 与transfunctions的集成

设计原则：
- 使用dataclass简化模型定义
- 支持多产品报价和历史比对
- 提供报价计算和格式化功能
- 集成transfunctions进行数据验证和计算
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any

from transfunctions import (
    ValidationError,
    calculate_quote_total,
    format_currency,
    format_date,
)

from .base import NamedModel, register_model


class QuoteStatus(Enum):
    """报价状态枚举"""

    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待发送
    SENT = "sent"  # 已发送
    VIEWED = "viewed"  # 已查看
    ACCEPTED = "accepted"  # 已接受
    REJECTED = "rejected"  # 已拒绝
    EXPIRED = "expired"  # 已过期
    CONVERTED = "converted"  # 已转换为订单


class QuoteType(Enum):
    """报价类型枚举"""

    STANDARD = "standard"  # 标准报价
    CUSTOM = "custom"  # 定制报价
    BULK = "bulk"  # 批量报价
    FRAMEWORK = "framework"  # 框架报价
    REVISION = "revision"  # 修订报价


@dataclass
class QuoteItem:
    """
    报价项目数据类

    表示报价中的单个产品或服务项目
    """

    product_name: str = ""  # 产品名称
    product_code: str = ""  # 产品编码
    specification: str = ""  # 规格说明
    unit: str = "件"  # 单位
    quantity: Decimal = Decimal("1")  # 数量
    unit_price: Decimal = Decimal("0.00")  # 单价
    discount_rate: float = 0.0  # 折扣率 (0-1)
    tax_rate: float = 0.13  # 税率 (默认13%)
    notes: str = ""  # 备注

    def __post_init__(self):
        """初始化后处理"""
        # 清理字符串字段
        self.product_name = self.product_name.strip()
        self.product_code = self.product_code.strip()
        self.specification = self.specification.strip()
        self.unit = self.unit.strip()
        self.notes = self.notes.strip()

    def validate(self) -> None:
        """验证报价项目数据"""
        if not self.product_name:
            raise ValidationError("产品名称不能为空")

        if self.quantity <= 0:
            raise ValidationError("数量必须大于0")

        if self.unit_price < 0:
            raise ValidationError("单价不能为负数")

        if not (0 <= self.discount_rate <= 1):
            raise ValidationError("折扣率必须在0-1之间")

        if not (0 <= self.tax_rate <= 1):
            raise ValidationError("税率必须在0-1之间")

    def get_subtotal(self) -> Decimal:
        """计算小计金额（不含税）"""
        return self.quantity * self.unit_price * Decimal(str(1 - self.discount_rate))

    def get_tax_amount(self) -> Decimal:
        """计算税额"""
        return self.get_subtotal() * Decimal(str(self.tax_rate))

    def get_total(self) -> Decimal:
        """计算总金额（含税）"""
        return self.get_subtotal() + self.get_tax_amount()

    def get_formatted_unit_price(self) -> str:
        """获取格式化的单价"""
        return format_currency(float(self.unit_price))

    def get_formatted_subtotal(self) -> str:
        """获取格式化的小计"""
        return format_currency(float(self.get_subtotal()))

    def get_formatted_total(self) -> str:
        """获取格式化的总金额"""
        return format_currency(float(self.get_total()))

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "product_name": self.product_name,
            "product_code": self.product_code,
            "specification": self.specification,
            "unit": self.unit,
            "quantity": float(self.quantity),
            "unit_price": float(self.unit_price),
            "discount_rate": self.discount_rate,
            "tax_rate": self.tax_rate,
            "notes": self.notes,
            "subtotal": float(self.get_subtotal()),
            "tax_amount": float(self.get_tax_amount()),
            "total": float(self.get_total()),
            "formatted_unit_price": self.get_formatted_unit_price(),
            "formatted_subtotal": self.get_formatted_subtotal(),
            "formatted_total": self.get_formatted_total(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QuoteItem":
        """从字典创建报价项目实例"""
        # 处理Decimal字段
        for field in ["quantity", "unit_price"]:
            if field in data and not isinstance(data[field], Decimal):
                try:
                    data[field] = Decimal(str(data[field]))
                except (ValueError, TypeError):
                    data[field] = Decimal("0" if field == "unit_price" else "1")

        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@register_model
@dataclass
class Quote(NamedModel):
    """
    报价数据模型

    继承自NamedModel，包含报价的完整信息，包括基本信息、
    报价项目、状态管理、历史记录等。
    """

    # 报价基本信息
    quote_number: str = ""  # 报价编号
    quote_type: QuoteType = QuoteType.STANDARD
    quote_status: QuoteStatus = QuoteStatus.DRAFT

    # 关联信息
    customer_id: int | None = None  # 客户ID
    customer_name: str = ""  # 客户名称
    contact_person: str = ""  # 联系人

    # 报价项目
    items: list[QuoteItem] | None = None  # 报价项目列表

    # 金额信息
    subtotal_amount: Decimal = Decimal("0.00")  # 小计金额
    tax_amount: Decimal = Decimal("0.00")  # 税额
    total_amount: Decimal = Decimal("0.00")  # 总金额

    # 时间信息
    quote_date: datetime | None = None  # 报价日期
    valid_until: datetime | None = None  # 有效期至
    sent_date: datetime | None = None  # 发送日期
    response_date: datetime | None = None  # 客户响应日期

    # 报价条款
    payment_terms: str = ""  # 付款条款
    delivery_terms: str = ""  # 交付条款
    validity_days: int = 30  # 有效期天数

    # 历史和版本
    parent_quote_id: int | None = None  # 父报价ID（用于修订版本）
    version: int = 1  # 版本号
    revision_reason: str = ""  # 修订原因

    # 转换信息
    converted_to_order: bool = False  # 是否已转换为订单
    order_id: int | None = None  # 关联订单ID

    def __post_init__(self):
        """初始化后处理"""
        # 初始化报价项目列表
        if self.items is None:
            self.items = []

        # 清理字符串字段
        self.quote_number = self.quote_number.strip()
        self.customer_name = self.customer_name.strip()
        self.contact_person = self.contact_person.strip()
        self.payment_terms = self.payment_terms.strip()
        self.delivery_terms = self.delivery_terms.strip()
        self.revision_reason = self.revision_reason.strip()

        # 生成报价编号（如果未提供）
        if not self.quote_number:
            self.quote_number = self._generate_quote_number()

        # 设置报价日期（如果未提供）
        if not self.quote_date:
            self.quote_date = datetime.now()

        # 设置有效期（如果未提供）
        if not self.valid_until and self.quote_date:
            self.valid_until = self.quote_date + timedelta(days=self.validity_days)

        super().__post_init__()

    def validate(self) -> None:
        """验证报价数据"""
        super().validate()

        # 验证报价编号
        if not self.quote_number:
            raise ValidationError("报价编号不能为空")

        # 验证客户信息
        if not self.customer_name:
            raise ValidationError("客户名称不能为空")

        # 验证有效期
        if self.validity_days < 1 or self.validity_days > 365:
            raise ValidationError("有效期天数必须在1-365之间")

        # 验证日期逻辑
        if self.quote_date and self.valid_until and self.quote_date >= self.valid_until:
            raise ValidationError("报价日期必须早于有效期")

        # 验证报价项目
        if not self.items:
            raise ValidationError("报价必须包含至少一个项目")

        for i, item in enumerate(self.items):
            try:
                item.validate()
            except ValidationError as e:
                raise ValidationError(f"报价项目{i + 1}验证失败: {e}") from e

    def _generate_quote_number(self) -> str:
        """生成报价编号"""
        now = datetime.now()
        type_prefix = {
            QuoteType.STANDARD: "Q",
            QuoteType.CUSTOM: "CQ",
            QuoteType.BULK: "BQ",
            QuoteType.FRAMEWORK: "FQ",
            QuoteType.REVISION: "RQ",
        }.get(self.quote_type, "Q")

        return f"{type_prefix}{now.strftime('%Y%m%d')}{now.strftime('%H%M%S')}"

    def add_item(self, item: QuoteItem) -> None:
        """添加报价项目"""
        item.validate()
        if self.items is not None:
            self.items.append(item)
        self.calculate_totals()
        self.update_timestamp()

    def remove_item(self, index: int) -> None:
        """移除报价项目"""
        if self.items is not None and 0 <= index < len(self.items):
            self.items.pop(index)
            self.calculate_totals()
            self.update_timestamp()

    def update_item(self, index: int, item: QuoteItem) -> None:
        """更新报价项目"""
        if self.items is not None and 0 <= index < len(self.items):
            item.validate()
            self.items[index] = item
            self.calculate_totals()
            self.update_timestamp()

    def calculate_totals(self) -> None:
        """计算报价总金额"""
        if not self.items:
            self.subtotal_amount = Decimal("0.00")
            self.tax_amount = Decimal("0.00")
            self.total_amount = Decimal("0.00")
            return

        # 使用transfunctions计算报价总额
        items_data = [item.to_dict() for item in self.items]

        try:
            totals = calculate_quote_total(items_data)

            self.subtotal_amount = totals["subtotal_after_discounts"]
            self.tax_amount = totals["tax_amount"]
            self.total_amount = totals["total_amount"]
        except Exception:
            # 如果transfunctions计算失败，使用本地计算
            self.subtotal_amount = sum(
                (item.get_subtotal() for item in self.items), Decimal("0")
            )
            self.tax_amount = sum(
                (item.get_tax_amount() for item in self.items), Decimal("0")
            )
            self.total_amount = sum(
                (item.get_total() for item in self.items), Decimal("0")
            )

    def is_expired(self) -> bool:
        """检查报价是否已过期"""
        if not self.valid_until:
            return False
        return datetime.now() > self.valid_until

    def is_expiring_soon(self, days_threshold: int = 3) -> bool:
        """
        检查报价是否即将过期

        Args:
            days_threshold: 过期预警阈值（天）

        Returns:
            bool: 是否即将过期
        """
        if not self.valid_until:
            return False

        warning_date = self.valid_until - timedelta(days=days_threshold)
        return datetime.now() >= warning_date and not self.is_expired()

    def get_remaining_days(self) -> int:
        """获取报价剩余有效天数"""
        if not self.valid_until:
            return -1

        remaining = (self.valid_until - datetime.now()).days
        return max(0, remaining)

    def send_quote(self, send_date: datetime | None = None) -> None:
        """
        发送报价

        Args:
            send_date: 发送日期，默认为当前时间
        """
        if self.quote_status != QuoteStatus.PENDING:
            self.quote_status = QuoteStatus.PENDING

        self.sent_date = send_date or datetime.now()
        self.quote_status = QuoteStatus.SENT
        self.update_timestamp()

    def mark_as_viewed(self, view_date: datetime | None = None) -> None:
        """
        标记为已查看

        Args:
            view_date: 查看日期，默认为当前时间
        """
        if self.quote_status == QuoteStatus.SENT:
            self.quote_status = QuoteStatus.VIEWED
            if not self.response_date:
                self.response_date = view_date or datetime.now()
            self.update_timestamp()

    def accept_quote(self, response_date: datetime | None = None) -> None:
        """
        接受报价

        Args:
            response_date: 响应日期，默认为当前时间
        """
        if self.quote_status in [QuoteStatus.SENT, QuoteStatus.VIEWED]:
            self.quote_status = QuoteStatus.ACCEPTED
            self.response_date = response_date or datetime.now()
            self.update_timestamp()

    def reject_quote(
        self, response_date: datetime | None = None, reason: str = ""
    ) -> None:
        """
        拒绝报价

        Args:
            response_date: 响应日期，默认为当前时间
            reason: 拒绝原因
        """
        if self.quote_status in [QuoteStatus.SENT, QuoteStatus.VIEWED]:
            self.quote_status = QuoteStatus.REJECTED
            self.response_date = response_date or datetime.now()
            if reason:
                self.notes = f"{self.notes}\n拒绝原因: {reason}".strip()
            self.update_timestamp()

    def convert_to_order(self, order_id: int) -> None:
        """
        转换为订单

        Args:
            order_id: 订单ID
        """
        if self.quote_status != QuoteStatus.ACCEPTED:
            raise ValidationError("只有已接受的报价才能转换为订单")

        self.quote_status = QuoteStatus.CONVERTED
        self.converted_to_order = True
        self.order_id = order_id
        self.update_timestamp()

    def create_revision(self, reason: str = "") -> "Quote":
        """
        创建修订版本

        Args:
            reason: 修订原因

        Returns:
            Quote: 新的修订版本报价
        """
        revision = self.copy()
        revision.quote_type = QuoteType.REVISION
        revision.parent_quote_id = self.id
        revision.version = self.version + 1
        revision.revision_reason = reason
        revision.quote_status = QuoteStatus.DRAFT
        revision.sent_date = None
        revision.response_date = None

        return revision

    def get_formatted_subtotal(self) -> str:
        """获取格式化的小计金额"""
        return format_currency(float(self.subtotal_amount))

    def get_formatted_tax_amount(self) -> str:
        """获取格式化的税额"""
        return format_currency(float(self.tax_amount))

    def get_formatted_total(self) -> str:
        """获取格式化的总金额"""
        return format_currency(float(self.total_amount))

    def get_formatted_quote_date(self) -> str:
        """获取格式化的报价日期"""
        if not self.quote_date:
            return ""
        return format_date(self.quote_date, "%Y-%m-%d")

    def get_formatted_valid_until(self) -> str:
        """获取格式化的有效期"""
        if not self.valid_until:
            return ""
        return format_date(self.valid_until, "%Y-%m-%d")

    def get_status_display(self) -> str:
        """获取状态显示文本"""
        status_map = {
            QuoteStatus.DRAFT: "草稿",
            QuoteStatus.PENDING: "待发送",
            QuoteStatus.SENT: "已发送",
            QuoteStatus.VIEWED: "已查看",
            QuoteStatus.ACCEPTED: "已接受",
            QuoteStatus.REJECTED: "已拒绝",
            QuoteStatus.EXPIRED: "已过期",
            QuoteStatus.CONVERTED: "已转换",
        }
        return status_map.get(self.quote_status, "未知")

    def to_dict(self, include_private: bool = False) -> dict[str, Any]:
        """转换为字典，包含格式化的字段"""
        data = super().to_dict(include_private)

        # 添加报价项目
        data["items"] = [item.to_dict() for item in self.items] if self.items else []

        # 添加格式化字段
        data.update(
            {
                "formatted_subtotal": self.get_formatted_subtotal(),
                "formatted_tax_amount": self.get_formatted_tax_amount(),
                "formatted_total": self.get_formatted_total(),
                "formatted_quote_date": self.get_formatted_quote_date(),
                "formatted_valid_until": self.get_formatted_valid_until(),
                "status_display": self.get_status_display(),
                "quote_type_display": self.quote_type.value,
                "is_expired": self.is_expired(),
                "is_expiring_soon": self.is_expiring_soon(),
                "remaining_days": self.get_remaining_days(),
                "item_count": len(self.items) if self.items else 0,
            }
        )

        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Quote":
        """从字典创建报价实例"""
        # 处理枚举字段
        enum_fields = {
            "quote_type": (QuoteType, QuoteType.STANDARD),
            "quote_status": (QuoteStatus, QuoteStatus.DRAFT),
        }

        for field, (enum_class, default_value) in enum_fields.items():
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = enum_class(data[field])
                except ValueError:
                    data[field] = default_value

        # 处理Decimal字段
        for field in ["subtotal_amount", "tax_amount", "total_amount"]:
            if field in data and not isinstance(data[field], Decimal):
                try:
                    data[field] = Decimal(str(data[field]))
                except (ValueError, TypeError):
                    data[field] = Decimal("0.00")

        # 处理日期字段
        date_fields = ["quote_date", "valid_until", "sent_date", "response_date"]
        for field in date_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field])
                except ValueError:
                    data[field] = None

        # 处理报价项目列表
        if "items" in data:
            if isinstance(data["items"], list):
                data["items"] = [
                    QuoteItem.from_dict(item) if isinstance(item, dict) else item
                    for item in data["items"]
                ]
            else:
                data["items"] = []

        return super().from_dict(data)

    def __str__(self) -> str:
        """返回报价的字符串表示"""
        status_info = self.quote_status.value
        return (
            f"Quote(id={self.id}, number='{self.quote_number}', "
            f"customer='{self.customer_name}', status={status_info})"
        )
