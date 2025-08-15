"""
MiniCRM 客户互动和任务管理服务

提供客户互动记录、任务管理和提醒功能的业务逻辑处理，包括：
- 互动记录管理（电话、邮件、会议等）
- 任务和提醒管理功能
- 交流事件跟踪和处理逻辑
- 自动提醒和通知机制

严格遵循分层架构和模块化原则：
- 只处理业务逻辑，不包含UI逻辑
- 通过DAO接口访问数据
- 强制使用transfunctions进行验证和计算
- 文件大小控制在推荐范围内（目标300行以内）
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from minicrm.core.exceptions import BusinessLogicError, ServiceError
from minicrm.models.interaction import (
    Interaction,
    InteractionStatus,
    InteractionType,
    Priority,
)
from transfunctions.validation import (
    ValidationError,
    validate_date_format,
    validate_numeric_range,
    validate_required_fields,
)

from .base_service import BaseService


class InteractionService(BaseService):
    """
    互动和任务管理服务实现

    负责客户互动记录和任务管理的核心业务逻辑：
    - 互动记录的CRUD操作和业务规则
    - 任务创建、更新和状态管理
    - 提醒机制和通知功能
    - 交流事件跟踪和处理

    严格遵循单一职责原则和模块化标准。
    """

    def __init__(self, interaction_dao=None):
        """
        初始化互动服务

        Args:
            interaction_dao: 互动记录数据访问对象
        """
        super().__init__(interaction_dao)
        self._logger = logging.getLogger(__name__)  # type: ignore
        self._logger.info("互动服务初始化完成")

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "InteractionService"

    def create_interaction(self, interaction_data: dict[str, Any]) -> int:
        """
        创建新的互动记录

        实现完整的互动记录创建业务规则：
        1. 使用transfunctions验证数据
        2. 应用业务规则和默认值
        3. 检查时间冲突
        4. 保存到数据库

        Args:
            interaction_data: 互动记录数据字典

        Returns:
            int: 新创建的互动记录ID

        Raises:
            ValidationError: 当数据验证失败时
            BusinessLogicError: 当业务规则检查失败时
            ServiceError: 当数据库操作失败时
        """
        try:
            self._log_operation("创建互动记录", {"service": self.get_service_name()})

            # 1. 强制使用transfunctions验证数据
            self._validate_interaction_data(interaction_data)

            # 2. 应用业务规则设置默认值
            self._apply_interaction_defaults(interaction_data)

            # 3. 检查时间冲突（如果是重要互动）
            if interaction_data.get("priority") in ["high", "urgent"]:
                self._check_time_conflicts(interaction_data)

            # 4. 创建互动记录模型实例进行验证
            interaction = Interaction.from_dict(interaction_data)
            interaction.validate()

            # 5. 保存到数据库
            interaction_id = self._dao.insert(interaction.to_dict())

            # 6. 如果启用提醒，设置提醒
            if interaction_data.get("reminder_enabled", False):
                self._schedule_reminder(interaction_id, interaction)

            self._log_operation("互动记录创建成功", {"id": interaction_id})
            return interaction_id

        except (ValidationError, BusinessLogicError) as e:
            self._logger.warning(f"互动记录创建业务异常: {e}")
            raise
        except Exception as e:
            self._logger.error(f"互动记录创建系统异常: {e}")
            raise ServiceError(f"创建互动记录失败: {e}") from e

    def update_interaction(self, interaction_id: int, data: dict[str, Any]) -> bool:
        """
        更新互动记录

        Args:
            interaction_id: 互动记录ID
            data: 更新数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 验证数据
            self._validate_interaction_data(data, is_update=True)

            # 检查互动记录是否存在
            existing_interaction = self._dao.get_by_id(interaction_id)
            if not existing_interaction:
                raise BusinessLogicError(f"互动记录不存在: {interaction_id}")

            # 更新时间戳
            data["updated_at"] = datetime.now().isoformat()

            # 更新数据库
            result = self._dao.update(interaction_id, data)

            if result:
                self._log_operation("互动记录更新成功", {"id": interaction_id})

            return result

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"更新互动记录失败: {e}")
            raise ServiceError(f"更新互动记录失败: {e}") from e

    def complete_interaction(
        self, interaction_id: int, outcome: str = "", follow_up_required: bool = False
    ) -> bool:
        """
        完成互动记录

        Args:
            interaction_id: 互动记录ID
            outcome: 互动结果
            follow_up_required: 是否需要跟进

        Returns:
            bool: 操作是否成功
        """
        try:
            # 获取现有记录
            existing_data = self._dao.get_by_id(interaction_id)
            if not existing_data:
                raise BusinessLogicError(f"互动记录不存在: {interaction_id}")

            # 创建模型实例并完成互动
            interaction = Interaction.from_dict(existing_data)
            interaction.complete_interaction(outcome=outcome)

            # 设置跟进
            if follow_up_required:
                follow_up_date = datetime.now() + timedelta(days=7)  # 默认7天后跟进
                interaction.set_follow_up(follow_up_date, "需要跟进")

            # 更新数据库
            result = self._dao.update(interaction_id, interaction.to_dict())

            if result:
                self._log_operation("互动记录完成", {"id": interaction_id})

            return result

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"完成互动记录失败: {e}")
            raise ServiceError(f"完成互动记录失败: {e}") from e

    def get_pending_reminders(self) -> list[dict[str, Any]]:
        """
        获取待处理的提醒

        Returns:
            List[Dict[str, Any]]: 需要提醒的互动记录列表
        """
        try:
            # 查询启用提醒且状态为计划中的记录
            conditions = {
                "reminder_enabled": True,
                "interaction_status": InteractionStatus.PLANNED.value,
            }

            interactions = self._dao.search(conditions)
            pending_reminders = []

            for interaction_data in interactions:
                interaction = Interaction.from_dict(interaction_data)
                if interaction.should_remind_now():
                    pending_reminders.append(interaction.to_dict())

            return pending_reminders

        except Exception as e:
            self._logger.error(f"获取待处理提醒失败: {e}")
            raise ServiceError(f"获取待处理提醒失败: {e}") from e

    def get_overdue_interactions(self) -> list[dict[str, Any]]:
        """
        获取逾期的互动记录

        Returns:
            List[Dict[str, Any]]: 逾期的互动记录列表
        """
        try:
            # 查询计划中且计划时间早于当前时间的记录
            current_time = datetime.now().isoformat()
            conditions = {
                "interaction_status": InteractionStatus.PLANNED.value,
                "scheduled_date__lt": current_time,
            }

            interactions = self._dao.search(conditions)
            overdue_interactions = []

            for interaction_data in interactions:
                interaction = Interaction.from_dict(interaction_data)
                if interaction.is_overdue():
                    overdue_interactions.append(interaction.to_dict())

            return overdue_interactions

        except Exception as e:
            self._logger.error(f"获取逾期互动记录失败: {e}")
            raise ServiceError(f"获取逾期互动记录失败: {e}") from e

    def get_customer_interactions(
        self, customer_id: int, limit: int = 50
    ) -> list[dict[str, Any]]:
        """
        获取客户的互动记录

        Args:
            customer_id: 客户ID
            limit: 限制数量

        Returns:
            List[Dict[str, Any]]: 客户的互动记录列表
        """
        try:
            conditions = {"party_type": "customer", "party_id": customer_id}

            interactions = self._dao.search(
                conditions=conditions,
                order_by="scheduled_date DESC",
                limit=limit,
            )

            return interactions

        except Exception as e:
            self._logger.error(f"获取客户互动记录失败: {e}")
            raise ServiceError(f"获取客户互动记录失败: {e}") from e

    def create_task(self, task_data: dict[str, Any]) -> int:
        """
        创建任务

        Args:
            task_data: 任务数据

        Returns:
            int: 任务ID
        """
        try:
            # 任务实际上是一种特殊的互动记录
            task_data.update(
                {
                    "interaction_type": InteractionType.FOLLOW_UP.value,
                    "subject": task_data.get("title", "任务"),
                    "content": task_data.get("description", ""),
                    "follow_up_required": True,
                    "follow_up_date": task_data.get("due_date"),
                }
            )

            return self._dao.insert(task_data)

        except Exception as e:
            self._handle_service_error("创建任务", e)
            return -1  # 不会执行到这里，但满足类型检查

    def get_pending_tasks(self, party_id: int | None = None) -> list[dict[str, Any]]:
        """
        获取待办任务

        Args:
            party_id: 关联方ID（可选）

        Returns:
            List[Dict[str, Any]]: 待办任务列表
        """
        try:
            conditions = {
                "interaction_type": InteractionType.FOLLOW_UP.value,
                "follow_up_required": True,
                "interaction_status__in": [
                    InteractionStatus.PLANNED.value,
                    InteractionStatus.IN_PROGRESS.value,
                ],
            }

            if party_id:
                conditions["party_id"] = party_id

            return self._dao.search(
                conditions=conditions,
                order_by="follow_up_date ASC",
            )

        except Exception as e:
            self._handle_service_error("获取待办任务", e)
            return []  # 不会执行到这里，但满足类型检查

    def complete_task(self, task_id: int, completion_notes: str = "") -> bool:
        """
        完成任务

        Args:
            task_id: 任务ID
            completion_notes: 完成备注

        Returns:
            bool: 操作是否成功
        """
        try:
            task_data = self._dao.get_by_id(task_id)
            if not task_data:
                raise BusinessLogicError(f"任务不存在: {task_id}")

            task = Interaction.from_dict(task_data)
            task.complete_interaction(outcome=completion_notes)
            task.complete_follow_up()

            return self._dao.update(task_id, task.to_dict())

        except Exception as e:
            self._handle_service_error("完成任务", e)
            return False  # 不会执行到这里，但满足类型检查

    def _validate_interaction_data(
        self, data: dict[str, Any], is_update: bool = False
    ) -> None:
        """
        验证互动记录数据 - 使用transfunctions统一验证

        Args:
            data: 互动记录数据
            is_update: 是否为更新操作
        """
        # 必填字段验证（创建时）- 使用transfunctions
        if not is_update:
            required_fields = ["party_name", "subject", "interaction_type"]
            errors = validate_required_fields(data, required_fields)
            if errors:
                raise ValidationError("; ".join(errors))

        # 数据类型验证
        type_mapping = {
            "party_id": int,
            "duration_minutes": int,
            "reminder_minutes": int,
            "reminder_enabled": bool,
            "follow_up_required": bool,
        }
        self._validate_data_types(data, type_mapping)

        # 日期格式验证 - 使用transfunctions
        if "scheduled_date" in data and data["scheduled_date"]:
            if not validate_date_format(data["scheduled_date"]):
                raise ValidationError("计划时间格式不正确")

            scheduled_date = datetime.fromisoformat(data["scheduled_date"])
            # 计划时间不能是过去时间（允许1小时误差）
            if scheduled_date < datetime.now() - timedelta(hours=1):
                raise ValidationError("计划时间不能早于当前时间")

        # 持续时间验证 - 使用transfunctions
        if "duration_minutes" in data:
            error = validate_numeric_range(
                data["duration_minutes"],
                min_value=0,
                max_value=24 * 60,
                field_name="持续时间",
            )
            if error:
                raise ValidationError(error)

    def _apply_interaction_defaults(self, data: dict[str, Any]) -> None:
        """
        应用互动记录默认值的业务规则

        Args:
            data: 互动记录数据字典（会被修改）
        """
        # 设置默认状态
        data.setdefault("interaction_status", InteractionStatus.PLANNED.value)

        # 设置默认优先级
        data.setdefault("priority", Priority.NORMAL.value)

        # 设置默认互动类型
        data.setdefault("interaction_type", InteractionType.PHONE_CALL.value)

        # 设置默认关联方类型
        data.setdefault("party_type", "customer")

        # 设置创建时间
        data.setdefault("created_at", datetime.now().isoformat())

        # 设置默认提醒时间（30分钟）
        data.setdefault("reminder_minutes", 30)

        # 如果没有设置计划时间，设置为当前时间
        if not data.get("scheduled_date"):
            data["scheduled_date"] = datetime.now().isoformat()

    def _check_time_conflicts(self, data: dict[str, Any]) -> None:
        """
        检查时间冲突

        Args:
            data: 互动记录数据

        Raises:
            BusinessLogicError: 当存在时间冲突时
        """
        if not data.get("scheduled_date"):
            return

        scheduled_date = datetime.fromisoformat(data["scheduled_date"])

        # 检查前后1小时内是否有其他重要互动
        start_time = scheduled_date - timedelta(hours=1)
        end_time = scheduled_date + timedelta(hours=1)

        conditions = {
            "priority__in": [Priority.HIGH.value, Priority.URGENT.value],
            "interaction_status": InteractionStatus.PLANNED.value,
            "scheduled_date__gte": start_time.isoformat(),
            "scheduled_date__lte": end_time.isoformat(),
        }

        conflicting_interactions = self._dao.search(conditions)

        if conflicting_interactions:
            raise BusinessLogicError(
                f"时间冲突：{scheduled_date.strftime('%Y-%m-%d %H:%M')} "
                f"前后1小时内已有其他重要互动安排"
            )

    def _schedule_reminder(self, interaction_id: int, interaction: Interaction) -> None:
        """
        安排提醒

        Args:
            interaction_id: 互动记录ID
            interaction: 互动记录实例
        """
        # 这里可以集成外部提醒系统
        # 目前只记录日志
        reminder_time = interaction.get_reminder_time()
        if reminder_time:
            self._logger.info(
                f"已安排提醒: 互动ID={interaction_id}, "
                f"提醒时间={reminder_time.strftime('%Y-%m-%d %H:%M')}"
            )
