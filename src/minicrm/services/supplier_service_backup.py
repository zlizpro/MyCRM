"""
MiniCRM 供应商管理服务

提供供应商相关的业务逻辑处理，包括：
- 供应商信息管理（CRUD操作）
- 供应商质量评估和分级算法
- 供应商互动和任务管理

严格遵循分层架构和模块化原则：
- 只处理业务逻辑，不包含UI逻辑
- 通过DAO接口访问数据
- 强制使用transfunctions进行验证和计算
- 文件大小控制在推荐范围内
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
from transfunctions import (
    ValidationError,
    calculate_customer_value_score,
    validate_supplier_data,
)


class SupplierService(BaseService):
    """
    供应商管理服务实现

    负责供应商相关的核心业务逻辑：
    - 供应商CRUD操作的业务规则
    - 供应商质量评估和分级算法
    - 供应商互动和任务管理
    - 供应商交流事件处理

    严格遵循单一职责原则和模块化标准。
    """

    def __init__(self, supplier_dao: SupplierDAO):
        """
        初始化供应商服务

        Args:
            supplier_dao: 供应商数据访问对象
        """
        super().__init__(supplier_dao)
        self._supplier_dao = supplier_dao
        # 使用BaseService提供的logger，无需重新赋值

        # 质量评估权重配置
        self._quality_weights = {
            "product_quality": 0.4,  # 产品质量权重40%
            "delivery_performance": 0.3,  # 交期表现权重30%
            "service_satisfaction": 0.2,  # 服务满意度权重20%
            "cooperation_stability": 0.1,  # 合作稳定性权重10%
        }

        # 事件处理时限配置（小时）
        self._event_time_limits = {
            EventPriority.URGENT: 2,
            EventPriority.HIGH: 8,
            EventPriority.MEDIUM: 24,
            EventPriority.LOW: 72,
        }

        self._logger.info("供应商服务初始化完成")

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "SupplierService"

    def create_supplier(self, supplier_data: dict[str, Any]) -> int:
        """
        创建新供应商

        实现完整的供应商创建业务规则：
        1. 使用transfunctions验证数据
        2. 检查重复供应商
        3. 应用业务规则和默认值
        4. 保存到数据库

        Args:
            supplier_data: 供应商数据字典，包含名称、联系方式等信息

        Returns:
            int: 新创建的供应商ID

        Raises:
            ValidationError: 当供应商数据验证失败时
            BusinessLogicError: 当业务规则检查失败时
            ServiceError: 当数据库操作失败时
        """
        try:
            # 1. 强制使用transfunctions验证数据
            validation_result = validate_supplier_data(supplier_data)
            if not validation_result.is_valid:
                raise ValidationError(
                    f"供应商数据验证失败: {', '.join(validation_result.errors)}"
                )

            # 2. 业务规则：检查供应商是否已存在
            if self._check_supplier_exists(supplier_data):
                raise BusinessLogicError("供应商已存在，无法重复创建")

            # 3. 应用业务规则设置默认值
            self._apply_supplier_defaults(supplier_data)

            # 4. 保存到数据库
            supplier_id = self._supplier_dao.insert(supplier_data)

            self._logger.info(f"成功创建供应商，ID: {supplier_id}")
            return supplier_id

        except (ValidationError, BusinessLogicError) as e:
            self._logger.warning(f"供应商创建业务异常: {e}")
            raise
        except Exception as e:
            self._logger.error(f"供应商创建系统异常: {e}")
            raise ServiceError(f"创建供应商失败: {e}") from e

    def update_supplier(self, supplier_id: int, data: dict[str, Any]) -> bool:
        """
        更新供应商信息

        Args:
            supplier_id: 供应商ID
            data: 更新数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 验证数据
            validation_result = validate_supplier_data(data)
            if not validation_result.is_valid:
                raise ValidationError(
                    f"供应商数据验证失败: {', '.join(validation_result.errors)}"
                )

            # 检查供应商是否存在
            if not self._supplier_dao.get_by_id(supplier_id):
                raise BusinessLogicError(f"供应商不存在: {supplier_id}")

            # 更新数据库
            data["updated_at"] = datetime.now().isoformat()
            result = self._supplier_dao.update(supplier_id, data)

            if result:
                self._logger.info(f"成功更新供应商: {supplier_id}")

            return result

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"更新供应商失败: {e}")
            raise ServiceError(f"更新供应商失败: {e}") from e

    def delete_supplier(self, supplier_id: int) -> bool:
        """
        删除供应商

        Args:
            supplier_id: 供应商ID

        Returns:
            bool: 删除是否成功
        """
        try:
            # 检查供应商是否存在
            supplier = self._supplier_dao.get_by_id(supplier_id)
            if not supplier:
                raise BusinessLogicError(f"供应商不存在: {supplier_id}")

            # 执行删除
            result = self._supplier_dao.delete(supplier_id)

            if result:
                self._logger.info(f"成功删除供应商: {supplier_id}")

            return result

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"删除供应商失败: {e}")
            raise ServiceError(f"删除供应商失败: {e}") from e

    def evaluate_supplier_quality(self, supplier_id: int) -> dict[str, Any]:
        """
        供应商质量评估和分级算法

        基于以下维度评估供应商质量：
        - 产品质量评分
        - 交期准确率
        - 服务满意度
        - 合作稳定性

        Args:
            supplier_id: 供应商ID

        Returns:
            Dict[str, Any]: 包含质量评估结果的字典

        Raises:
            BusinessLogicError: 当供应商不存在时
            ServiceError: 当评估失败时
        """
        try:
            # 获取供应商基本信息
            supplier_data = self._supplier_dao.get_by_id(supplier_id)
            if not supplier_data:
                raise BusinessLogicError(f"供应商不存在: {supplier_id}")

            # 获取供应商历史数据
            transaction_history = self._supplier_dao.get_transaction_history(
                supplier_id
            )
            interaction_history = self._supplier_dao.get_interaction_history(
                supplier_id
            )

            # 使用transfunctions计算供应商质量评分
            # 复用客户价值评分算法，适配供应商场景
            quality_metrics = calculate_customer_value_score(
                supplier_data, transaction_history, interaction_history
            )

            # 转换为供应商质量评估结果
            result = {
                "supplier_id": supplier_id,
                "supplier_name": supplier_data.get("name", ""),
                "quality_score": quality_metrics.total_score,
                "product_quality": quality_metrics.transaction_value,
                "delivery_performance": quality_metrics.interaction_score,
                "service_satisfaction": quality_metrics.loyalty_score,
                "cooperation_stability": quality_metrics.potential_score,
                "grade": self._determine_supplier_grade(quality_metrics.total_score),
                "evaluated_at": datetime.now().isoformat(),
                "transaction_count": len(transaction_history),
                "interaction_count": len(interaction_history),
            }

            self._logger.info(
                f"供应商质量评估完成: {supplier_id}, "
                f"评分: {quality_metrics.total_score:.1f}"
            )
            return result

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"供应商质量评估失败: {e}")
            raise ServiceError(f"供应商质量评估失败: {e}") from e

    def manage_supplier_interaction(
        self, supplier_id: int, interaction_data: dict[str, Any]
    ) -> int:
        """
        管理供应商互动记录

        Args:
            supplier_id: 供应商ID
            interaction_data: 互动数据

        Returns:
            int: 互动记录ID
        """
        try:
            # 验证供应商存在
            if not self._supplier_dao.get_by_id(supplier_id):
                raise BusinessLogicError(f"供应商不存在: {supplier_id}")

            # 设置默认值
            interaction_data.update(
                {"supplier_id": supplier_id, "created_at": datetime.now().isoformat()}
            )

            # 保存互动记录
            interaction_id = self._supplier_dao.insert_interaction(interaction_data)

            self._logger.info(
                f"成功记录供应商互动: {supplier_id}, 互动ID: {interaction_id}"
            )
            return interaction_id

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"记录供应商互动失败: {e}")
            raise ServiceError(f"记录供应商互动失败: {e}") from e

    def search_suppliers(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        搜索供应商

        Args:
            query: 搜索关键词
            filters: 筛选条件
            page: 页码
            page_size: 每页大小

        Returns:
            Tuple[List[Dict[str, Any]], int]: (供应商列表, 总数)
        """
        try:
            conditions = {}
            if query:
                suppliers = self._supplier_dao.search_by_name_or_contact(query)
            else:
                if filters:
                    conditions.update(filters)

                offset = (page - 1) * page_size
                suppliers = self._supplier_dao.search(
                    conditions=conditions, limit=page_size, offset=offset
                )

            total = self._supplier_dao.count(conditions)
            return suppliers, total

        except Exception as e:
            self._logger.error(f"搜索供应商失败: {e}")
            raise ServiceError(f"搜索供应商失败: {e}") from e

    def _check_supplier_exists(self, supplier_data: dict[str, Any]) -> bool:
        """
        检查供应商是否已存在

        Args:
            supplier_data: 供应商数据

        Returns:
            bool: 供应商是否已存在
        """
        name = supplier_data.get("name", "").strip()
        phone = supplier_data.get("phone", "").strip()

        if not name and not phone:
            return False

        existing_suppliers = self._supplier_dao.search_by_name_or_contact(
            f"{name} {phone}"
        )
        return len(existing_suppliers) > 0

    def _apply_supplier_defaults(self, supplier_data: dict[str, Any]) -> None:
        """
        应用供应商默认值的业务规则

        Args:
            supplier_data: 供应商数据字典（会被修改）
        """
        # 设置默认供应商等级
        supplier_data.setdefault("grade", "普通供应商")

        # 设置默认状态
        supplier_data.setdefault("status", "active")

        # 设置创建时间
        supplier_data.setdefault("created_at", datetime.now().isoformat())

        # 根据供应商类型设置默认等级（业务规则）
        supplier_type = supplier_data.get("supplier_type", "")
        if supplier_type in ["原材料供应商", "核心供应商"]:
            supplier_data["grade"] = "重要供应商"  # 强制设置，不使用setdefault
        elif supplier_type == "战略合作伙伴":
            supplier_data["grade"] = "战略供应商"

    def _determine_supplier_grade(self, quality_score: float) -> str:
        """
        根据质量评分确定供应商等级

        Args:
            quality_score: 质量评分

        Returns:
            str: 供应商等级
        """
        if quality_score >= 90:
            return "战略供应商"
        elif quality_score >= 80:
            return "重要供应商"
        elif quality_score >= 70:
            return "普通供应商"
        else:
            return "备选供应商"

    # ==================== 交流事件处理功能 ====================

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

                # 如果事件完成，更新供应商质量评分
                if event_status == EventStatus.COMPLETED:
                    self._update_supplier_quality_from_event(event)

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

    def get_event_statistics(
        self, supplier_id: int | None = None, time_period: int = 30
    ) -> dict[str, Any]:
        """
        获取交流事件统计信息

        Args:
            supplier_id: 供应商ID，如果为None则统计所有供应商
            time_period: 统计时间段（天）

        Returns:
            Dict[str, Any]: 统计结果

        Raises:
            ServiceError: 当统计失败时
        """
        try:
            start_date = datetime.now() - timedelta(days=time_period)

            # 获取事件数据
            if supplier_id is not None:
                events = self._supplier_dao.get_communication_events(
                    supplier_id=supplier_id, start_date=start_date
                )
            else:
                events = self._supplier_dao.get_communication_events(
                    start_date=start_date
                )

            # 统计分析
            stats: dict[str, Any] = {
                "total_events": len(events),
                "by_type": {},
                "by_status": {},
                "by_priority": {},
                "average_processing_time": 0.0,
                "satisfaction_rating": 0.0,
                "overdue_events": 0,
            }

            if not events:
                return stats

            # 按类型统计
            for event in events:
                event_type = event.get("event_type", "unknown")
                stats["by_type"][event_type] = stats["by_type"].get(event_type, 0) + 1

            # 按状态统计
            for event in events:
                status = event.get("status", "unknown")
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # 按优先级统计
            for event in events:
                priority = event.get("priority", "unknown")
                stats["by_priority"][priority] = (
                    stats["by_priority"].get(priority, 0) + 1
                )

            # 计算平均处理时间和满意度
            completed_events = [e for e in events if e.get("status") == "completed"]
            if completed_events:
                processing_times = []
                satisfaction_ratings = []

                for event in completed_events:
                    created_at = datetime.fromisoformat(event.get("created_at", ""))
                    completed_at = datetime.fromisoformat(event.get("completed_at", ""))
                    processing_time = (
                        completed_at - created_at
                    ).total_seconds() / 3600  # 小时
                    processing_times.append(processing_time)

                    # 获取满意度评分
                    satisfaction = event.get("satisfaction_rating", 0)
                    if satisfaction > 0:
                        satisfaction_ratings.append(satisfaction)

                stats["average_processing_time"] = sum(processing_times) / len(
                    processing_times
                )
                if satisfaction_ratings:
                    stats["satisfaction_rating"] = sum(satisfaction_ratings) / len(
                        satisfaction_ratings
                    )

            # 统计超时事件
            now = datetime.now()
            for event in events:
                if event.get("status") not in ["completed", "closed"]:
                    due_time = datetime.fromisoformat(event.get("due_time", ""))
                    if now > due_time:
                        stats["overdue_events"] += 1

            return stats

        except Exception as e:
            self._logger.error(f"获取事件统计失败: {e}")
            raise ServiceError(f"获取事件统计失败: {e}") from e

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

    # ==================== 私有辅助方法 ====================

    def _validate_event_data(self, event_data: dict[str, Any]) -> None:
        """
        验证事件数据

        Args:
            event_data: 事件数据

        Raises:
            ValidationError: 当数据验证失败时
        """
        # 验证必填字段
        required_fields = ["event_type", "content"]
        for field in required_fields:
            if not event_data.get(field):
                raise ValidationError(f"事件{field}不能为空")

        # 验证事件类型
        try:
            CommunicationEventType(event_data["event_type"])
        except ValueError:
            raise ValidationError(
                f"无效的事件类型: {event_data['event_type']}"
            ) from None

        # 验证紧急程度
        urgency = event_data.get("urgency_level", "medium")
        if urgency not in ["low", "medium", "high", "urgent"]:
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

    def _update_supplier_quality_from_event(self, event: dict[str, Any]) -> None:
        """
        根据事件处理结果更新供应商质量评分

        Args:
            event: 事件信息
        """
        try:
            supplier_id = event.get("supplier_id")
            if not isinstance(supplier_id, int):
                self._logger.warning(f"无效的供应商ID: {supplier_id}")
                return

            event_type = event.get("event_type")
            satisfaction_rating = event.get("satisfaction_rating", 0)

            # 根据事件类型和满意度调整质量评分
            if event_type == "quality_issue" and satisfaction_rating < 3:
                # 质量问题且满意度低，降低质量评分
                self._adjust_supplier_quality_score(supplier_id, -2)
            elif event_type == "complaint" and satisfaction_rating < 3:
                # 投诉且满意度低，降低服务评分
                self._adjust_supplier_service_score(supplier_id, -1)
            elif satisfaction_rating >= 4:
                # 满意度高，提升相应评分
                self._adjust_supplier_quality_score(supplier_id, 1)

        except Exception as e:
            self._logger.warning(f"更新供应商质量评分失败: {e}")

    def _adjust_supplier_quality_score(
        self, supplier_id: int, adjustment: float
    ) -> None:
        """调整供应商质量评分"""
        # 这里应该调用质量评估相关的方法
        # 由于篇幅限制，这里只记录日志
        self._logger.info(f"调整供应商{supplier_id}质量评分: {adjustment}")

    def _adjust_supplier_service_score(
        self, supplier_id: int, adjustment: float
    ) -> None:
        """调整供应商服务评分"""
        # 这里应该调用服务评估相关的方法
        # 由于篇幅限制，这里只记录日志
        self._logger.info(f"调整供应商{supplier_id}服务评分: {adjustment}")

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
