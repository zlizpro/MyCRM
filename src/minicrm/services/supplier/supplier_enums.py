"""
MiniCRM 供应商服务枚举定义

定义供应商管理相关的枚举类型：
- 交流事件类型
- 事件状态
- 事件优先级
"""

from enum import Enum


class CommunicationEventType(Enum):
    """交流事件类型枚举"""

    INQUIRY = "inquiry"  # 询价
    COMPLAINT = "complaint"  # 投诉
    SUGGESTION = "suggestion"  # 建议
    QUALITY_ISSUE = "quality_issue"  # 质量问题
    COOPERATION = "cooperation"  # 合作洽谈
    TECHNICAL_SUPPORT = "technical_support"  # 技术支持
    OTHER = "other"  # 其他


class EventStatus(Enum):
    """事件状态枚举"""

    PENDING = "pending"  # 待处理
    IN_PROGRESS = "in_progress"  # 处理中
    COMPLETED = "completed"  # 已完成
    CLOSED = "closed"  # 已关闭


class EventPriority(Enum):
    """事件优先级枚举"""

    LOW = "low"  # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"  # 高
    URGENT = "urgent"  # 紧急
