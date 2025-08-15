"""
MiniCRM 合同数据模型

定义合同相关的数据结构和业务逻辑，包括：
- 合同基本信息模型
- 合同状态和生命周期管理
- 合同条款和条件
- 数据验证和格式化
- 与transfunctions的集成

设计原则：
- 使用dataclass简化模型定义
- 支持客户合同和供应商合同
- 提供合同状态管理和到期提醒
- 集成transfunctions进行数据验证和格式化
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any

from transfunctions import ValidationError, format_currency, format_date

from .base import NamedModel, register_model


class ContractType(Enum):
    """合同类型枚举"""

    SALES = "sales"  # 销售合同
    PURCHASE = "purchase"  # 采购合同
    SERVICE = "service"  # 服务合同
    FRAMEWORK = "framework"  # 框架合同
    OTHER = "other"  # 其他


class ContractStatus(Enum):
    """合同状态枚举"""

    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待审批
    APPROVED = "approved"  # 已审批
    SIGNED = "signed"  # 已签署
    ACTIVE = "active"  # 执行中
    COMPLETED = "completed"  # 已完成
    TERMINATED = "terminated"  # 已终止
    EXPIRED = "expired"  # 已过期


class PaymentMethod(Enum):
    """付款方式枚举"""

    CASH = "cash"  # 现金
    BANK_TRANSFER = "bank_transfer"  # 银行转账
    CHECK = "check"  # 支票
    CREDIT_CARD = "credit_card"  # 信用卡
    INSTALLMENT = "installment"  # 分期付款
    OTHER = "other"  # 其他


@register_model
@dataclass
class Contract(NamedModel):
    """
    合同数据模型

    继承自NamedModel，包含合同的完整信息，包括基本信息、
    合同条款、状态管理、财务信息等。
    """

    # 合同基本信息
    contract_number: str = ""  # 合同编号
    contract_type: ContractType = ContractType.SALES
    contract_status: ContractStatus = ContractStatus.DRAFT

    # 关联方信息
    customer_id: int | None = None  # 客户ID（销售合同）
    supplier_id: int | None = None  # 供应商ID（采购合同）
    party_name: str = ""  # 合同方名称

    # 合同金额和条款
    contract_amount: Decimal = Decimal("0.00")  # 合同总金额
    currency: str = "CNY"  # 货币类型
    payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER
    payment_terms: int = 30  # 付款期限（天）

    # 合同时间
    sign_date: datetime | None = None  # 签署日期
    effective_date: datetime | None = None  # 生效日期
    expiry_date: datetime | None = None  # 到期日期

    # 合同条款
    terms_and_conditions: str = ""  # 条款和条件
    delivery_terms: str = ""  # 交付条款
    warranty_terms: str = ""  # 保修条款

    # 附件和文档
    attachments: list[str] | None = None  # 附件文件路径列表
    template_id: int | None = None  # 合同模板ID

    # 执行信息
    progress_percentage: float = 0.0  # 执行进度百分比
    actual_amount: Decimal = Decimal("0.00")  # 实际执行金额

    # 提醒设置
    reminder_days: int = 30  # 到期提醒天数
    auto_renewal: bool = False  # 是否自动续约

    def __post_init__(self):
        """初始化后处理"""
        # 初始化附件列表
        if self.attachments is None:
            self.attachments = []

        # 清理字符串字段
        self.contract_number = self.contract_number.strip()
        self.party_name = self.party_name.strip()
        self.terms_and_conditions = self.terms_and_conditions.strip()
        self.delivery_terms = self.delivery_terms.strip()
        self.warranty_terms = self.warranty_terms.strip()

        # 生成合同编号（如果未提供）
        if not self.contract_number:
            self.contract_number = self._generate_contract_number()

        super().__post_init__()

    def validate(self) -> None:
        """验证合同数据"""
        super().validate()

        # 验证合同编号
        if not self.contract_number:
            raise ValidationError("合同编号不能为空")

        # 验证合同方
        if not self.party_name:
            raise ValidationError("合同方名称不能为空")

        # 验证关联方ID（在有party_name的情况下可以暂时不要求ID）
        if (
            self.contract_type == ContractType.SALES
            and not self.customer_id
            and not self.party_name
        ):
            raise ValidationError("销售合同必须关联客户或提供客户名称")
        elif (
            self.contract_type == ContractType.PURCHASE
            and not self.supplier_id
            and not self.party_name
        ):
            raise ValidationError("采购合同必须关联供应商或提供供应商名称")

        # 验证合同金额
        if self.contract_amount < 0:
            raise ValidationError("合同金额不能为负数")

        # 验证付款期限
        if self.payment_terms < 0 or self.payment_terms > 365:
            raise ValidationError("付款期限必须在0-365天之间")

        # 验证日期逻辑
        if (
            self.effective_date
            and self.expiry_date
            and self.effective_date >= self.expiry_date
        ):
            raise ValidationError("生效日期必须早于到期日期")

        if (
            self.sign_date
            and self.effective_date
            and self.sign_date > self.effective_date
        ):
            raise ValidationError("签署日期不能晚于生效日期")

        # 验证执行进度
        if not (0 <= self.progress_percentage <= 100):
            raise ValidationError("执行进度必须在0-100之间")

        # 验证实际金额
        if self.actual_amount < 0:
            raise ValidationError("实际执行金额不能为负数")
        if self.actual_amount > self.contract_amount:
            raise ValidationError("实际执行金额不能超过合同总金额")

    def _generate_contract_number(self) -> str:
        """生成合同编号"""
        now = datetime.now()
        type_prefix = {
            ContractType.SALES: "S",
            ContractType.PURCHASE: "P",
            ContractType.SERVICE: "V",
            ContractType.FRAMEWORK: "F",
            ContractType.OTHER: "O",
        }.get(self.contract_type, "C")

        return f"{type_prefix}{now.strftime('%Y%m%d')}{now.strftime('%H%M%S')}"

    def is_active(self) -> bool:
        """检查合同是否处于活跃状态"""
        return self.contract_status in [ContractStatus.SIGNED, ContractStatus.ACTIVE]

    def is_expired(self) -> bool:
        """检查合同是否已过期"""
        if not self.expiry_date:
            return False
        return datetime.now() > self.expiry_date

    def is_expiring_soon(self, days_threshold: int | None = None) -> bool:
        """
        检查合同是否即将到期

        Args:
            days_threshold: 到期预警阈值（天），默认使用合同设置的提醒天数

        Returns:
            bool: 是否即将到期
        """
        if not self.expiry_date:
            return False

        threshold = days_threshold or self.reminder_days
        warning_date = self.expiry_date - timedelta(days=threshold)
        return datetime.now() >= warning_date and not self.is_expired()

    def get_remaining_days(self) -> int:
        """获取合同剩余天数"""
        if not self.expiry_date:
            return -1

        remaining = (self.expiry_date - datetime.now()).days
        return max(0, remaining)

    def get_contract_duration_days(self) -> int:
        """获取合同总期限（天）"""
        if not self.effective_date or not self.expiry_date:
            return 0
        return (self.expiry_date - self.effective_date).days

    def update_progress(
        self, percentage: float, actual_amount: Decimal | None = None
    ) -> None:
        """
        更新合同执行进度

        Args:
            percentage: 执行进度百分比
            actual_amount: 实际执行金额
        """
        if not (0 <= percentage <= 100):
            raise ValidationError("执行进度必须在0-100之间")

        self.progress_percentage = percentage

        if actual_amount is not None:
            if actual_amount < 0:
                raise ValidationError("实际执行金额不能为负数")
            if actual_amount > self.contract_amount:
                raise ValidationError("实际执行金额不能超过合同总金额")
            self.actual_amount = actual_amount

        # 根据进度自动更新状态
        if percentage == 100:
            self.contract_status = ContractStatus.COMPLETED
        elif percentage > 0 and self.contract_status == ContractStatus.SIGNED:
            self.contract_status = ContractStatus.ACTIVE

        self.update_timestamp()

    def sign_contract(self, sign_date: datetime | None = None) -> None:
        """
        签署合同

        Args:
            sign_date: 签署日期，默认为当前时间
        """
        if self.contract_status not in [
            ContractStatus.DRAFT,
            ContractStatus.PENDING,
            ContractStatus.APPROVED,
        ]:
            raise ValidationError(f"合同状态为{self.contract_status.value}，无法签署")

        self.sign_date = sign_date or datetime.now()
        self.contract_status = ContractStatus.SIGNED

        # 如果没有设置生效日期，默认为签署日期
        if not self.effective_date:
            self.effective_date = self.sign_date

        self.update_timestamp()

    def terminate_contract(self, reason: str = "") -> None:
        """
        终止合同

        Args:
            reason: 终止原因
        """
        if self.contract_status in [
            ContractStatus.COMPLETED,
            ContractStatus.TERMINATED,
            ContractStatus.EXPIRED,
        ]:
            raise ValidationError(f"合同状态为{self.contract_status.value}，无法终止")

        self.contract_status = ContractStatus.TERMINATED
        if reason:
            self.notes = f"{self.notes}\n终止原因: {reason}".strip()

        self.update_timestamp()

    def add_attachment(self, file_path: str) -> None:
        """添加附件"""
        file_path = file_path.strip()
        if (
            file_path
            and self.attachments is not None
            and file_path not in self.attachments
        ):
            self.attachments.append(file_path)
            self.update_timestamp()

    def remove_attachment(self, file_path: str) -> None:
        """移除附件"""
        if self.attachments is not None and file_path in self.attachments:
            self.attachments.remove(file_path)
            self.update_timestamp()

    def get_formatted_amount(self) -> str:
        """获取格式化的合同金额"""
        return format_currency(float(self.contract_amount))

    def get_formatted_actual_amount(self) -> str:
        """获取格式化的实际执行金额"""
        return format_currency(float(self.actual_amount))

    def get_formatted_sign_date(self) -> str:
        """获取格式化的签署日期"""
        if not self.sign_date:
            return ""
        return format_date(self.sign_date, "%Y-%m-%d")

    def get_formatted_effective_date(self) -> str:
        """获取格式化的生效日期"""
        if not self.effective_date:
            return ""
        return format_date(self.effective_date, "%Y-%m-%d")

    def get_formatted_expiry_date(self) -> str:
        """获取格式化的到期日期"""
        if not self.expiry_date:
            return ""
        return format_date(self.expiry_date, "%Y-%m-%d")

    def get_status_display(self) -> str:
        """获取状态显示文本"""
        status_map = {
            ContractStatus.DRAFT: "草稿",
            ContractStatus.PENDING: "待审批",
            ContractStatus.APPROVED: "已审批",
            ContractStatus.SIGNED: "已签署",
            ContractStatus.ACTIVE: "执行中",
            ContractStatus.COMPLETED: "已完成",
            ContractStatus.TERMINATED: "已终止",
            ContractStatus.EXPIRED: "已过期",
        }
        return status_map.get(self.contract_status, "未知")

    def to_dict(self, include_private: bool = False) -> dict[str, Any]:
        """转换为字典，包含格式化的字段"""
        data = super().to_dict(include_private)

        # 添加格式化字段
        data.update(
            {
                "formatted_amount": self.get_formatted_amount(),
                "formatted_actual_amount": self.get_formatted_actual_amount(),
                "formatted_sign_date": self.get_formatted_sign_date(),
                "formatted_effective_date": self.get_formatted_effective_date(),
                "formatted_expiry_date": self.get_formatted_expiry_date(),
                "status_display": self.get_status_display(),
                "contract_type_display": self.contract_type.value,
                "payment_method_display": self.payment_method.value,
                "is_active": self.is_active(),
                "is_expired": self.is_expired(),
                "is_expiring_soon": self.is_expiring_soon(),
                "remaining_days": self.get_remaining_days(),
                "duration_days": self.get_contract_duration_days(),
            }
        )

        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Contract":
        """从字典创建合同实例"""
        # 处理枚举字段
        enum_fields = {
            "contract_type": (ContractType, ContractType.SALES),
            "contract_status": (ContractStatus, ContractStatus.DRAFT),
            "payment_method": (PaymentMethod, PaymentMethod.BANK_TRANSFER),
        }

        for field, (enum_class, default_value) in enum_fields.items():
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = enum_class(data[field])
                except ValueError:
                    data[field] = default_value

        # 处理Decimal字段
        for field in ["contract_amount", "actual_amount"]:
            if field in data and not isinstance(data[field], Decimal):
                try:
                    data[field] = Decimal(str(data[field]))
                except (ValueError, TypeError):
                    data[field] = Decimal("0.00")

        # 处理日期字段
        date_fields = ["sign_date", "effective_date", "expiry_date"]
        for field in date_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field])
                except ValueError:
                    data[field] = None

        # 处理附件列表
        if "attachments" in data and not isinstance(data["attachments"], list):
            data["attachments"] = []

        return super().from_dict(data)

    def __str__(self) -> str:
        """返回合同的字符串表示"""
        status_info = self.contract_status.value
        return (
            f"Contract(id={self.id}, number='{self.contract_number}', "
            f"party='{self.party_name}', status={status_info})"
        )
