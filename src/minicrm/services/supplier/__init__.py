"""
MiniCRM 供应商服务包

提供模块化的供应商管理服务：
- 核心CRUD操作
- 质量评估服务
- 交流事件管理
- 统计分析服务
- 任务管理服务
"""

from .supplier_core_service import SupplierCoreService
from .supplier_enums import CommunicationEventType, EventPriority, EventStatus
from .supplier_event_service import SupplierEventService
from .supplier_quality_service import SupplierQualityService
from .supplier_statistics_service import SupplierStatisticsService
from .supplier_task_service import SupplierTaskService


__all__ = [
    "SupplierCoreService",
    "SupplierQualityService",
    "SupplierEventService",
    "SupplierStatisticsService",
    "SupplierTaskService",
    "CommunicationEventType",
    "EventStatus",
    "EventPriority",
]
