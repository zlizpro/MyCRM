"""
MiniCRM 供应商交流事件服务

提供供应商交流事件处理功能：
- 创建和管理交流事件
- 事件状态更新
- 事件处理流程
- 超时事件管理
"""

from datetime import datetime, timedelta
from typing import Any

from minicrm.core.exceptions import BusinessLogicError, ServiceError
from minicrm.data.dao.supplier_dao import SupplierDAO
from minicrm.services.base_service import BaseService
from minicrm.services.supplier.supplier_enums import (
    CommunicationEventType,
    EventPriority,
    EventStatus,
)
from transfunctions.validation import ValidationError, validate_required_fields


class SupplierEventService(BaseService):
    """
    供应商交流事件服务实现

    负责供应商交流事件相关的业务逻辑：
    - 事件创建和管理
    - 事件状态更新
    - 事件处理流程
    - 超时事件监控

    严格遵循单一职责原则。
    """

    def __init__(self, supplier_dao: SupplierDAO):
        """
        初始化供应商交流事件服务

        Args:
            supplier_dao: 供应商数据访问对象
        """
        super().__init__(supplier_dao)
        self._supplier_dao = supplier_dao

        # 事件处理时限配置（小时）
        self._event_time_limits = {
            EventPriority.URGENT: 2,
            EventPriority.HIGH: 8,
            EventPriority.MEDIUM: 24,
            EventPriority.LOW: 72,
        }

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "SupplierEventService"

    def create_communication_event(
        self, supplier_id: int, event_data: dict[str, Any]
    ) -> int:
        """
        创建供应商交流事件

        实现完整的事件创建流程：
        1. 验证供应商存在
        2. 验证事件数据
        3. 确定事件优先级
        4. 设置处理时限
        5. 创建事件记录

        Args:
            supplier_id: 供应商ID
            event_data: 事件数据字典，包含类型、内容、紧急程度等

        Returns:
            int: 事件ID

        Raises:
            ValidationError: 当事件数据验证失败时
            BusinessLogicError: 当供应商不存在时
            ServiceError: 当创建失败时
        """
        try:
            # 1. 验证供应商存在
            supplier = self._supplier_dao.get_by_id(supplier_id)
            if not supplier:
                raise BusinessLogicError(f"供应商不存在: {supplier_id}")

            # 2. 验证事件数据
            self._validate_event_data(event_data)

            # 3. 确定事件优先级和处理时限
            priority = self._determine_event_priority(event_data)
            due_time = self._calculate_event_due_time(priority)

            # 4. 生成事件编号
            event_number = self._generate_event_number(supplier_id)

            # 5. 准备完整的事件数据
            complete_event_data = {
                "supplier_id": supplier_id,
                "event_number": event_number,
                "event_type": event_data["event_type"],
                "title": event_data.get("title", ""),
                "content": event_data.get("content", ""),
                "priority": priority.value,
                "status": EventStatus.PENDING.value,
                "created_at": datetime.now().isoformat(),
                "due_time": due_time.isoformat(),
                "created_by": event_data.get("created_by", "system"),
                "urgency_level": event_data.get("urgency_level", "medium"),
            }

            # 6. 保存事件记录
            event_id = self._supplier_dao.insert_communication_event(
                complete_event_data
            )

            self._logger.info(
                f"成功创建供应商交流事件: {supplier_id}, "
                f"事件ID: {event_id}, 编号: {event_number}, 优先级: {priority.value}"
            )

            return event_id

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"创建供应商交流事件失败: {e}")
            raise ServiceError(f"创建供应商交流事件失败: {e}") from e

    def update_event_status(
        self,
        event_id: int,
        status: str,
        progress_notes: str = "",
        updated_by: str = "system",
    ) -> bool:
        """
        更新事件处理状态

        Args:
            event_id: 事件ID
            status: 新状态
            progress_notes: 处理进度备注
            updated_by: 更新人

        Returns:
            bool: 更新是否成功

        Raises:
            ValidationError: 当状态值无效时
            BusinessLogicError: 当事件不存在时
            ServiceError: 当更新失败时
        """
        try:
            # 验证状态值
            try:
                event_status = EventStatus(status)
            except ValueError:
                raise ValidationError(f"无效的事件状态: {status}") from None

            # 获取事件信息
            event = self._supplier_dao.get_communication_event(event_id)
            if not event:
                raise BusinessLogicError(f"交流事件不存在: {event_id}")

            # 准备更新数据
            update_data = {
                "status": event_status.value,
                "updated_at": datetime.now().isoformat(),
                "updated_by": updated_by,
            }

            # 如果有处理备注，添加到进度记录中
            if progress_notes:
                update_data["progress_notes"] = progress_notes

            # 如果状态变为已完成，记录完成时间
            if event_status == EventStatus.COMPLETED:
                update_data["completed_at"] = datetime.now().isoformat()

            # 更新事件状态
            result = self._supplier_dao.update_communication_event(
                event_id, update_data
            )

            if result:
                self._logger.info(
                    f"成功更新事件状态: {event_id}, 状态: {event_status.value}"
                )

            return result

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"更新事件状态失败: {e}")
            raise ServiceError(f"更新事件状态失败: {e}") from e

    def process_event(
        self, event_id: int, processing_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        处理交流事件

        实现完整的事件处理流程：
        1. 获取事件信息
        2. 执行处理逻辑
        3. 更新处理状态
        4. 记录处理结果
        5. 影响供应商评分

        Args:
            event_id: 事件ID
            processing_data: 处理数据，包含解决方案、处理结果等

        Returns:
            Dict[str, Any]: 处理结果

        Raises:
            BusinessLogicError: 当事件不存在或状态不允许处理时
            ServiceError: 当处理失败时
        """
        try:
            # 1. 获取事件信息
            event = self._supplier_dao.get_communication_event(event_id)
            if not event:
                raise BusinessLogicError(f"交流事件不存在: {event_id}")

            # 检查事件状态是否允许处理
            current_status = EventStatus(event.get("status", "pending"))
            if current_status in [EventStatus.COMPLETED, EventStatus.CLOSED]:
                raise BusinessLogicError(f"事件已完成或关闭，无法继续处理: {event_id}")

            # 2. 准备处理结果数据
            processing_result = {
                "event_id": event_id,
                "solution": processing_data.get("solution", ""),
                "result": processing_data.get("result", ""),
                "satisfaction_rating": processing_data.get("satisfaction_rating", 0),
                "processing_time": datetime.now().isoformat(),
                "processed_by": processing_data.get("processed_by", "system"),
                "follow_up_required": processing_data.get("follow_up_required", False),
            }

            # 3. 更新事件状态为已完成
            self.update_event_status(
                event_id,
                EventStatus.COMPLETED.value,
                f"处理完成: {processing_result['solution']}",
                processing_result["processed_by"],
            )

            # 4. 保存处理结果
            self._supplier_dao.insert_event_processing_result(processing_result)

            # 5. 如果需要后续跟进，创建任务
            if processing_result["follow_up_required"]:
                self._create_follow_up_task(event, processing_result)

            self._logger.info(f"成功处理交流事件: {event_id}")

            return processing_result

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"处理交流事件失败: {e}")
            raise ServiceError(f"处理交流事件失败: {e}") from e

    def get_overdue_events(self) -> list[dict[str, Any]]:
        """
        获取超时的交流事件

        Returns:
            List[Dict[str, Any]]: 超时事件列表

        Raises:
            ServiceError: 当查询失败时
        """
        try:
            now = datetime.now()
            overdue_events = []

            # 获取所有未完成的事件
            pending_events = self._supplier_dao.get_communication_events(
                status_filter=["pending", "in_progress"]
            )

            for event in pending_events:
                due_time = datetime.fromisoformat(event.get("due_time", ""))
                if now > due_time:
                    # 计算超时时间
                    overdue_hours = (now - due_time).total_seconds() / 3600
                    event["overdue_hours"] = round(overdue_hours, 1)
                    overdue_events.append(event)

            # 按超时时间排序，最严重的在前面
            overdue_events.sort(key=lambda x: x["overdue_hours"], reverse=True)

            return overdue_events

        except Exception as e:
            self._logger.error(f"获取超时事件失败: {e}")
            raise ServiceError(f"获取超时事件失败: {e}") from e

    def _validate_event_data(self, event_data: dict[str, Any]) -> None:
        """
        验证事件数据

        Args:
            event_data: 事件数据

        Raises:
            ValidationError: 当数据验证失败时
        """
        # 使用transfunctions验证必填字段
        required_fields = ["event_type", "content"]
        errors = validate_required_fields(event_data, required_fields)
        if errors:
            raise ValidationError(f"事件数据验证失败: {'; '.join(errors)}")

        # 验证事件类型
        try:
            CommunicationEventType(event_data["event_type"])
        except ValueError:
            raise ValidationError(
                f"无效的事件类型: {event_data['event_type']}"
            ) from None

        # 验证紧急程度
        urgency = event_data.get("urgency_level", "medium")
        valid_urgency_levels = ["low", "medium", "high", "urgent"]
        if urgency not in valid_urgency_levels:
            raise ValidationError(f"无效的紧急程度: {urgency}")

    def _determine_event_priority(self, event_data: dict[str, Any]) -> EventPriority:
        """
        确定事件优先级

        基于事件类型和紧急程度确定处理优先级

        Args:
            event_data: 事件数据

        Returns:
            EventPriority: 事件优先级
        """
        event_type = CommunicationEventType(event_data["event_type"])
        urgency_level = event_data.get("urgency_level", "medium")

        # 质量问题和投诉优先级较高
        if event_type in [
            CommunicationEventType.QUALITY_ISSUE,
            CommunicationEventType.COMPLAINT,
        ]:
            if urgency_level == "urgent":
                return EventPriority.URGENT
            elif urgency_level == "high":
                return EventPriority.HIGH
            else:
                return EventPriority.MEDIUM

        # 其他事件根据紧急程度确定
        priority_mapping = {
            "urgent": EventPriority.URGENT,
            "high": EventPriority.HIGH,
            "medium": EventPriority.MEDIUM,
            "low": EventPriority.LOW,
        }

        return priority_mapping.get(urgency_level, EventPriority.MEDIUM)

    def _calculate_event_due_time(self, priority: EventPriority) -> datetime:
        """
        计算事件处理截止时间

        Args:
            priority: 事件优先级

        Returns:
            datetime: 截止时间
        """
        hours_limit = self._event_time_limits.get(priority, 24)
        return datetime.now() + timedelta(hours=hours_limit)

    def _generate_event_number(self, supplier_id: int) -> str:
        """
        生成事件编号

        Args:
            supplier_id: 供应商ID

        Returns:
            str: 事件编号
        """
        today = datetime.now().strftime("%Y%m%d")
        # 获取今天该供应商的事件数量
        event_count = self._supplier_dao.get_daily_event_count(supplier_id, today)
        return f"SE{supplier_id:04d}{today}{event_count + 1:03d}"

    def _create_follow_up_task(
        self, event: dict[str, Any], processing_result: dict[str, Any]
    ) -> None:
        """
        创建后续跟进任务

        Args:
            event: 原始事件信息
            processing_result: 处理结果
        """
        try:
            task_data = {
                "supplier_id": event.get("supplier_id"),
                "title": f"跟进事件: {event.get('title', '')}",
                "description": (
                    f"需要跟进处理结果: {processing_result.get('solution', '')}"
                ),
                "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
                "created_by": processing_result.get("processed_by", "system"),
                "task_type": "follow_up",
                "related_event_id": event.get("id"),
            }

            # 这里应该调用任务管理服务创建任务
            # 由于任务管理服务可能还未实现，这里只记录日志
            self._logger.info(f"创建跟进任务: {task_data}")

        except Exception as e:
            self._logger.warning(f"创建跟进任务失败: {e}")
