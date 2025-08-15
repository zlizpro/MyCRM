"""
MiniCRM 供应商管理服务协调器

提供统一的供应商管理接口，协调各个子服务：
- 核心CRUD操作
- 质量评估服务
- 交流事件管理
- 统计分析服务
- 任务管理服务

保持向后兼容性，同时实现模块化架构。
"""

from typing import Any

from minicrm.data.dao.supplier_dao import SupplierDAO
from minicrm.services.base_service import BaseService
from minicrm.services.supplier import (
    CommunicationEventType,
    EventPriority,
    EventStatus,
    SupplierCoreService,
    SupplierEventService,
    SupplierQualityService,
    SupplierStatisticsService,
    SupplierTaskService,
)


class SupplierService(BaseService):
    """
    供应商管理服务协调器

    统一管理所有供应商相关的业务逻辑，通过组合模式
    协调各个专门的子服务，保持接口的一致性和向后兼容性。

    架构优势：
    - 模块化设计，职责清晰
    - 易于测试和维护
    - 符合单一职责原则
    - 保持向后兼容
    """

    def __init__(self, supplier_dao: SupplierDAO):
        """
        初始化供应商服务协调器

        Args:
            supplier_dao: 供应商数据访问对象
        """
        super().__init__(supplier_dao)
        self._supplier_dao = supplier_dao

        # 初始化各个子服务
        self.core = SupplierCoreService(supplier_dao)
        self.quality = SupplierQualityService(supplier_dao)
        self.events = SupplierEventService(supplier_dao)
        self.statistics = SupplierStatisticsService(supplier_dao)
        self.tasks = SupplierTaskService(supplier_dao)

        self._logger.info("供应商服务协调器初始化完成")

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "SupplierService"

    # ==================== 核心CRUD操作 ====================
    # 委托给SupplierCoreService

    def create_supplier(self, supplier_data: dict[str, Any]) -> int:
        """创建新供应商"""
        return self.core.create_supplier(supplier_data)

    def update_supplier(self, supplier_id: int, data: dict[str, Any]) -> bool:
        """更新供应商信息"""
        return self.core.update_supplier(supplier_id, data)

    def delete_supplier(self, supplier_id: int) -> bool:
        """删除供应商"""
        return self.core.delete_supplier(supplier_id)

    def search_suppliers(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """搜索供应商"""
        return self.core.search_suppliers(query, filters, page, page_size)

    # ==================== 质量评估功能 ====================
    # 委托给SupplierQualityService

    def evaluate_supplier_quality(self, supplier_id: int) -> dict[str, Any]:
        """供应商质量评估和分级算法"""
        return self.quality.evaluate_supplier_quality(supplier_id)

    # ==================== 交流事件处理功能 ====================
    # 委托给SupplierEventService

    def create_communication_event(
        self, supplier_id: int, event_data: dict[str, Any]
    ) -> int:
        """创建供应商交流事件"""
        return self.events.create_communication_event(supplier_id, event_data)

    def update_event_status(
        self,
        event_id: int,
        status: str,
        progress_notes: str = "",
        updated_by: str = "system",
    ) -> bool:
        """更新事件处理状态"""
        return self.events.update_event_status(
            event_id, status, progress_notes, updated_by
        )

    def process_event(
        self, event_id: int, processing_data: dict[str, Any]
    ) -> dict[str, Any]:
        """处理交流事件"""
        result = self.events.process_event(event_id, processing_data)

        # 处理完成后更新质量评分
        event = self._supplier_dao.get_communication_event(event_id)
        if event:
            self.quality.update_supplier_quality_from_event(event)

        return result

    def get_overdue_events(self) -> list[dict[str, Any]]:
        """获取超时的交流事件"""
        return self.events.get_overdue_events()

    # ==================== 统计分析功能 ====================
    # 委托给SupplierStatisticsService

    def get_event_statistics(
        self, supplier_id: int | None = None, time_period: int = 30
    ) -> dict[str, Any]:
        """获取交流事件统计信息"""
        return self.statistics.get_event_statistics(supplier_id, time_period)

    def get_supplier_performance_metrics(
        self, supplier_id: int, time_period: int = 90
    ) -> dict[str, Any]:
        """获取供应商绩效指标"""
        return self.statistics.get_supplier_performance_metrics(
            supplier_id, time_period
        )

    def generate_supplier_report(
        self, supplier_id: int, report_type: str = "comprehensive"
    ) -> dict[str, Any]:
        """生成供应商报告"""
        return self.statistics.generate_supplier_report(supplier_id, report_type)

    # ==================== 任务管理功能 ====================
    # 委托给SupplierTaskService

    def manage_supplier_interaction(
        self, supplier_id: int, interaction_data: dict[str, Any]
    ) -> int:
        """管理供应商互动记录"""
        return self.tasks.manage_supplier_interaction(supplier_id, interaction_data)

    def create_follow_up_task(self, supplier_id: int, task_data: dict[str, Any]) -> int:
        """创建跟进任务"""
        return self.tasks.create_follow_up_task(supplier_id, task_data)

    def get_pending_tasks(self, supplier_id: int | None = None) -> list[dict[str, Any]]:
        """获取待处理任务"""
        return self.tasks.get_pending_tasks(supplier_id)

    def complete_task(self, task_id: int, completion_notes: str = "") -> bool:
        """完成任务"""
        return self.tasks.complete_task(task_id, completion_notes)

    # ==================== 便捷方法 ====================
    # 提供一些常用的组合操作

    def get_supplier_overview(self, supplier_id: int) -> dict[str, Any]:
        """
        获取供应商概览信息

        组合多个服务的数据，提供供应商的全面概览

        Args:
            supplier_id: 供应商ID

        Returns:
            Dict[str, Any]: 供应商概览数据
        """
        try:
            # 获取基本信息
            supplier = self._supplier_dao.get_by_id(supplier_id)
            if not supplier:
                return {}

            # 组合各种数据
            overview = {
                "basic_info": supplier,
                "quality_assessment": self.quality.evaluate_supplier_quality(
                    supplier_id
                ),
                "performance_metrics": self.statistics.get_supplier_performance_metrics(
                    supplier_id
                ),
                "recent_events": self.statistics.get_event_statistics(supplier_id, 7),
                "pending_tasks": self.tasks.get_pending_tasks(supplier_id),
            }

            return overview

        except Exception as e:
            self._logger.error(f"获取供应商概览失败: {e}")
            return {}

    def handle_quality_issue(
        self, supplier_id: int, issue_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        处理质量问题的完整流程

        Args:
            supplier_id: 供应商ID
            issue_data: 质量问题数据

        Returns:
            Dict[str, Any]: 处理结果
        """
        try:
            # 1. 创建质量问题事件
            event_data = {
                "event_type": CommunicationEventType.QUALITY_ISSUE.value,
                "title": issue_data.get("title", "质量问题"),
                "content": issue_data.get("description", ""),
                "urgency_level": issue_data.get("urgency", "high"),
                "created_by": issue_data.get("reporter", "system"),
            }

            event_id = self.events.create_communication_event(supplier_id, event_data)

            # 2. 创建跟进任务
            task_data = {
                "title": f"处理质量问题: {issue_data.get('title', '')}",
                "description": f"跟进质量问题事件 #{event_id}",
                "priority": "high",
                "task_type": "quality_issue",
                "related_event_id": event_id,
            }

            task_id = self.tasks.create_follow_up_task(supplier_id, task_data)

            # 3. 重新评估供应商质量
            quality_result = self.quality.evaluate_supplier_quality(supplier_id)

            result = {
                "event_id": event_id,
                "task_id": task_id,
                "quality_assessment": quality_result,
                "status": "created",
                "message": "质量问题已记录，已创建跟进任务",
            }

            self._logger.info(f"成功处理质量问题: 供应商{supplier_id}, 事件{event_id}")
            return result

        except Exception as e:
            self._logger.error(f"处理质量问题失败: {e}")
            return {"status": "error", "message": str(e)}


# 导出枚举类型，保持向后兼容
__all__ = [
    "SupplierService",
    "CommunicationEventType",
    "EventStatus",
    "EventPriority",
]
