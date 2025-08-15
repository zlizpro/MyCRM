"""
MiniCRM 互动记录数据模型

定义互动记录相关的数据结构和业务逻辑，包括：
- 客户和供应商互动记录
- 交流事件跟踪和处理
- 任务和提醒管理
- 数据验证和格式化
- 与transfunctions的集成

设计原则：
- 使用dataclass简化模型定义
- 支持多种互动类型和状态管理
- 提供任务跟进和提醒功能
- 集成transfunctions进行数据验证和格式化
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from transfunctions import ValidationError, format_date

from .base import BaseModel, register_model


class InteractionType(Enum):
    """互动类型枚举"""

    PHONE_CALL = "phone_call"  # 电话沟通
    EMAIL = "email"  # 邮件沟通
    MEETING = "meeting"  # 会议
    VISIT = "visit"  # 拜访
    AFTER_SALES = "after_sales"  # 售后服务
    COMPLAINT = "complaint"  # 投诉处理
    CONSULTATION = "consultation"  # 咨询
    NEGOTIATION = "negotiation"  # 商务谈判
    FOLLOW_UP = "follow_up"  # 跟进
    OTHER = "other"  # 其他


class InteractionStatus(Enum):
    """互动状态枚举"""

    PLANNED = "planned"  # 计划中
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消
    POSTPONED = "postponed"  # 已延期


class Priority(Enum):
    """优先级枚举"""

    LOW = "low"  # 低
    NORMAL = "normal"  # 普通
    HIGH = "high"  # 高
    URGENT = "urgent"  # 紧急


class PartyType(Enum):
    """关联方类型枚举"""

    CUSTOMER = "customer"  # 客户
    SUPPLIER = "supplier"  # 供应商


@register_model
@dataclass
class Interaction(BaseModel):
    """
    互动记录数据模型

    继承自NamedModel，包含互动记录的完整信息，包括基本信息、
    互动内容、状态管理、跟进计划等。
    """

    # 互动基本信息
    interaction_type: InteractionType = InteractionType.PHONE_CALL
    interaction_status: InteractionStatus = InteractionStatus.PLANNED
    priority: Priority = Priority.NORMAL

    # 关联方信息
    party_type: PartyType = PartyType.CUSTOMER
    party_id: int | None = None  # 关联方ID（客户或供应商）
    party_name: str = ""  # 关联方名称
    contact_person: str = ""  # 联系人

    # 时间信息
    scheduled_date: datetime | None = None  # 计划时间
    actual_date: datetime | None = None  # 实际时间
    duration_minutes: int = 0  # 持续时间（分钟）

    # 互动内容
    subject: str = ""  # 主题
    content: str = ""  # 详细内容
    outcome: str = ""  # 结果

    # 跟进信息
    follow_up_required: bool = False  # 是否需要跟进
    follow_up_date: datetime | None = None  # 跟进日期
    follow_up_notes: str = ""  # 跟进备注

    # 关联信息
    related_quote_id: int | None = None  # 关联报价ID
    related_contract_id: int | None = None  # 关联合同ID
    related_order_id: int | None = None  # 关联订单ID

    # 附件和标签
    attachments: list[str] | None = None  # 附件文件路径列表
    tags: list[str] | None = None  # 标签列表

    # 提醒设置
    reminder_enabled: bool = False  # 是否启用提醒
    reminder_minutes: int = 30  # 提醒提前时间（分钟）

    def __post_init__(self):
        """初始化后处理"""
        # 初始化列表字段
        if self.attachments is None:
            self.attachments = []
        if self.tags is None:
            self.tags = []

        # 清理字符串字段
        self.party_name = self.party_name.strip()
        self.contact_person = self.contact_person.strip()
        self.subject = self.subject.strip()
        self.content = self.content.strip()
        self.outcome = self.outcome.strip()
        self.follow_up_notes = self.follow_up_notes.strip()

        # 如果没有设置主题，使用互动类型作为默认主题
        if not self.subject:
            self.subject = self._get_default_subject()

        super().__post_init__()

    def validate(self) -> None:
        """验证互动记录数据"""
        super().validate()

        # 验证关联方信息
        if not self.party_name:
            raise ValidationError("关联方名称不能为空")

        # 验证主题
        if not self.subject:
            raise ValidationError("互动主题不能为空")

        # 验证时间逻辑
        if self.scheduled_date and self.actual_date:
            # 实际时间不应该早于计划时间太多（允许1小时的误差）
            time_diff = self.scheduled_date - self.actual_date
            if time_diff > timedelta(hours=1):
                raise ValidationError("实际时间不应该早于计划时间")

        # 验证持续时间
        if self.duration_minutes < 0:
            raise ValidationError("持续时间不能为负数")
        if self.duration_minutes > 24 * 60:  # 不超过24小时
            raise ValidationError("持续时间不能超过24小时")

        # 验证跟进逻辑
        if self.follow_up_required and not self.follow_up_date:
            raise ValidationError("需要跟进时必须设置跟进日期")

        # 验证提醒设置
        if self.reminder_minutes < 0:
            raise ValidationError("提醒时间不能为负数")

    def _get_default_subject(self) -> str:
        """获取默认主题"""
        type_map = {
            InteractionType.PHONE_CALL: "电话沟通",
            InteractionType.EMAIL: "邮件沟通",
            InteractionType.MEETING: "会议",
            InteractionType.VISIT: "客户拜访",
            InteractionType.AFTER_SALES: "售后服务",
            InteractionType.COMPLAINT: "投诉处理",
            InteractionType.CONSULTATION: "业务咨询",
            InteractionType.NEGOTIATION: "商务谈判",
            InteractionType.FOLLOW_UP: "跟进沟通",
            InteractionType.OTHER: "其他沟通",
        }
        return type_map.get(self.interaction_type, "互动记录")

    def is_overdue(self) -> bool:
        """检查是否已逾期"""
        if not self.scheduled_date:
            return False
        if self.interaction_status in [
            InteractionStatus.COMPLETED,
            InteractionStatus.CANCELLED,
        ]:
            return False
        return datetime.now() > self.scheduled_date

    def is_due_soon(self, hours_threshold: int = 24) -> bool:
        """
        检查是否即将到期

        Args:
            hours_threshold: 到期预警阈值（小时）

        Returns:
            bool: 是否即将到期
        """
        if not self.scheduled_date:
            return False
        if self.interaction_status in [
            InteractionStatus.COMPLETED,
            InteractionStatus.CANCELLED,
        ]:
            return False

        warning_time = self.scheduled_date - timedelta(hours=hours_threshold)
        return datetime.now() >= warning_time and not self.is_overdue()

    def get_reminder_time(self) -> datetime | None:
        """获取提醒时间"""
        if not self.reminder_enabled or not self.scheduled_date:
            return None
        return self.scheduled_date - timedelta(minutes=self.reminder_minutes)

    def should_remind_now(self) -> bool:
        """检查是否应该现在提醒"""
        reminder_time = self.get_reminder_time()
        if not reminder_time:
            return False
        return (
            datetime.now() >= reminder_time
            and self.interaction_status == InteractionStatus.PLANNED
        )

    def start_interaction(self, start_time: datetime | None = None) -> None:
        """
        开始互动

        Args:
            start_time: 开始时间，默认为当前时间
        """
        if self.interaction_status != InteractionStatus.PLANNED:
            raise ValidationError(
                f"互动状态为{self.interaction_status.value}，无法开始"
            )

        self.interaction_status = InteractionStatus.IN_PROGRESS
        self.actual_date = start_time or datetime.now()
        self.update_timestamp()

    def complete_interaction(
        self, end_time: datetime | None = None, outcome: str = ""
    ) -> None:
        """
        完成互动

        Args:
            end_time: 结束时间，默认为当前时间
            outcome: 互动结果
        """
        if self.interaction_status not in [
            InteractionStatus.PLANNED,
            InteractionStatus.IN_PROGRESS,
        ]:
            raise ValidationError(
                f"互动状态为{self.interaction_status.value}，无法完成"
            )

        end_time = end_time or datetime.now()

        # 如果还没有开始，设置开始时间
        if not self.actual_date:
            self.actual_date = end_time

        # 计算持续时间
        if self.actual_date:
            duration = end_time - self.actual_date
            self.duration_minutes = max(0, int(duration.total_seconds() / 60))

        self.interaction_status = InteractionStatus.COMPLETED
        if outcome:
            self.outcome = outcome

        self.update_timestamp()

    def cancel_interaction(self, reason: str = "") -> None:
        """
        取消互动

        Args:
            reason: 取消原因
        """
        if self.interaction_status in [
            InteractionStatus.COMPLETED,
            InteractionStatus.CANCELLED,
        ]:
            raise ValidationError(
                f"互动状态为{self.interaction_status.value}，无法取消"
            )

        self.interaction_status = InteractionStatus.CANCELLED
        if reason:
            self.notes = f"{self.notes}\n取消原因: {reason}".strip()

        self.update_timestamp()

    def postpone_interaction(self, new_date: datetime, reason: str = "") -> None:
        """
        延期互动

        Args:
            new_date: 新的计划时间
            reason: 延期原因
        """
        if self.interaction_status in [
            InteractionStatus.COMPLETED,
            InteractionStatus.CANCELLED,
        ]:
            raise ValidationError(
                f"互动状态为{self.interaction_status.value}，无法延期"
            )

        if new_date <= datetime.now():
            raise ValidationError("新的计划时间必须晚于当前时间")

        self.scheduled_date = new_date
        self.interaction_status = InteractionStatus.POSTPONED
        if reason:
            self.notes = f"{self.notes}\n延期原因: {reason}".strip()

        self.update_timestamp()

    def set_follow_up(self, follow_up_date: datetime, notes: str = "") -> None:
        """
        设置跟进

        Args:
            follow_up_date: 跟进日期
            notes: 跟进备注
        """
        if follow_up_date <= datetime.now():
            raise ValidationError("跟进日期必须晚于当前时间")

        self.follow_up_required = True
        self.follow_up_date = follow_up_date
        self.follow_up_notes = notes
        self.update_timestamp()

    def complete_follow_up(self) -> None:
        """完成跟进"""
        self.follow_up_required = False
        self.follow_up_date = None
        self.follow_up_notes = ""
        self.update_timestamp()

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

    def get_formatted_scheduled_date(self) -> str:
        """获取格式化的计划时间"""
        if not self.scheduled_date:
            return ""
        return format_date(self.scheduled_date, "%Y-%m-%d %H:%M")

    def get_formatted_actual_date(self) -> str:
        """获取格式化的实际时间"""
        if not self.actual_date:
            return ""
        return format_date(self.actual_date, "%Y-%m-%d %H:%M")

    def get_formatted_follow_up_date(self) -> str:
        """获取格式化的跟进日期"""
        if not self.follow_up_date:
            return ""
        return format_date(self.follow_up_date, "%Y-%m-%d")

    def get_duration_display(self) -> str:
        """获取持续时间显示文本"""
        if self.duration_minutes == 0:
            return ""

        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60

        if hours > 0:
            return f"{hours}小时{minutes}分钟" if minutes > 0 else f"{hours}小时"
        else:
            return f"{minutes}分钟"

    def get_status_display(self) -> str:
        """获取状态显示文本"""
        status_map = {
            InteractionStatus.PLANNED: "计划中",
            InteractionStatus.IN_PROGRESS: "进行中",
            InteractionStatus.COMPLETED: "已完成",
            InteractionStatus.CANCELLED: "已取消",
            InteractionStatus.POSTPONED: "已延期",
        }
        return status_map.get(self.interaction_status, "未知")

    def get_priority_display(self) -> str:
        """获取优先级显示文本"""
        priority_map = {
            Priority.LOW: "低",
            Priority.NORMAL: "普通",
            Priority.HIGH: "高",
            Priority.URGENT: "紧急",
        }
        return priority_map.get(self.priority, "未知")

    def get_type_display(self) -> str:
        """获取类型显示文本"""
        type_map = {
            InteractionType.PHONE_CALL: "电话沟通",
            InteractionType.EMAIL: "邮件沟通",
            InteractionType.MEETING: "会议",
            InteractionType.VISIT: "拜访",
            InteractionType.AFTER_SALES: "售后服务",
            InteractionType.COMPLAINT: "投诉处理",
            InteractionType.CONSULTATION: "咨询",
            InteractionType.NEGOTIATION: "商务谈判",
            InteractionType.FOLLOW_UP: "跟进",
            InteractionType.OTHER: "其他",
        }
        return type_map.get(self.interaction_type, "未知")

    def to_dict(self, include_private: bool = False) -> dict[str, Any]:
        """转换为字典，包含格式化的字段"""
        data = super().to_dict(include_private)

        # 添加格式化字段
        data.update(
            {
                "formatted_scheduled_date": self.get_formatted_scheduled_date(),
                "formatted_actual_date": self.get_formatted_actual_date(),
                "formatted_follow_up_date": self.get_formatted_follow_up_date(),
                "duration_display": self.get_duration_display(),
                "status_display": self.get_status_display(),
                "priority_display": self.get_priority_display(),
                "type_display": self.get_type_display(),
                "party_type_display": self.party_type.value,
                "is_overdue": self.is_overdue(),
                "is_due_soon": self.is_due_soon(),
                "should_remind_now": self.should_remind_now(),
                "reminder_time": (
                    reminder_time.isoformat()
                    if (reminder_time := self.get_reminder_time()) is not None
                    else None
                ),
            }
        )

        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Interaction":
        """从字典创建互动记录实例"""
        # 处理枚举字段
        enum_fields = {
            "interaction_type": (InteractionType, InteractionType.PHONE_CALL),
            "interaction_status": (InteractionStatus, InteractionStatus.PLANNED),
            "priority": (Priority, Priority.NORMAL),
            "party_type": (PartyType, PartyType.CUSTOMER),
        }

        for field, (enum_class, default_value) in enum_fields.items():
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = enum_class(data[field])
                except ValueError:
                    data[field] = default_value

        # 处理日期字段
        date_fields = ["scheduled_date", "actual_date", "follow_up_date"]
        for field in date_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field])
                except ValueError:
                    data[field] = None

        # 处理列表字段
        for field in ["attachments", "tags"]:
            if field in data and not isinstance(data[field], list):
                data[field] = []

        return super().from_dict(data)

    def __str__(self) -> str:
        """返回互动记录的字符串表示"""
        status_info = self.interaction_status.value
        return (
            f"Interaction(id={self.id}, subject='{self.subject}', "
            f"party='{self.party_name}', status={status_info})"
        )
