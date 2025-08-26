"""
MiniCRM 任务管理服务

负责任务的创建、管理、跟踪和提醒功能,包括:
- 任务的增删改查
- 任务状态管理
- 任务提醒和通知
- 任务统计和报表
"""

from datetime import datetime
from typing import Any

from ..core.exceptions import BusinessLogicError, ValidationError
from ..core.interfaces.service_interfaces import ITaskService
from ..data.dao.task_dao import TaskDAO
from ..data.database import DatabaseManager
from .base_service import BaseService


class TaskService(BaseService, ITaskService):
    """
    任务管理服务

    提供完整的任务管理功能,包括任务创建、状态跟踪、提醒管理等.
    """

    def __init__(self, database_manager: DatabaseManager):
        """
        初始化任务服务

        Args:
            database_manager: 数据库管理器
        """
        super().__init__()
        self._db_manager = database_manager
        self._task_dao = TaskDAO(database_manager)

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "TaskService"

    def create_task(self, task_data: dict[str, Any]) -> int:
        """
        创建新任务

        Args:
            task_data: 任务数据字典

        Returns:
            int: 新创建的任务ID

        Raises:
            ValidationError: 数据验证失败
            BusinessLogicError: 业务逻辑错误
        """
        try:
            # 验证任务数据
            self._validate_task_data(task_data)

            # 准备任务数据
            task_record = {
                "title": task_data.get("title", ""),
                "description": task_data.get("description", ""),
                "customer_id": task_data.get("customer_id"),
                "supplier_id": task_data.get("supplier_id"),
                "due_date": task_data.get("due_date"),
                "priority": task_data.get("priority", "medium"),
                "status": "pending",
                "assigned_to": task_data.get("assigned_to"),
                "created_by": task_data.get("created_by"),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            # 使用TaskDAO存储任务
            task_id = self._task_dao.insert(task_record)

            self._logger.info(f"成功创建任务: {task_id}")
            return task_id

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"创建任务失败: {e}")
            raise BusinessLogicError(f"创建任务失败: {e}") from e

    def get_task(self, task_id: int) -> dict[str, Any] | None:
        """
        获取任务信息

        Args:
            task_id: 任务ID

        Returns:
            Optional[Dict[str, Any]]: 任务信息,不存在时返回None
        """
        try:
            task = self._task_dao.get_by_id(task_id)
            if task:
                return self._format_task_data(task)
            return None

        except Exception as e:
            self._logger.error(f"获取任务失败: {e}")
            return None

    def update_task(self, task_id: int, data: dict[str, Any]) -> bool:
        """
        更新任务信息

        Args:
            task_id: 任务ID
            data: 更新数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 验证任务存在
            existing_task = self.get_task(task_id)
            if not existing_task:
                raise BusinessLogicError(f"任务不存在: {task_id}")

            # 准备更新数据
            update_data = {
                "content": data.get("title", existing_task.get("title")),
                "notes": data.get("description", existing_task.get("description")),
                "interaction_date": data.get("due_date", existing_task.get("due_date")),
                "status": data.get("status", existing_task.get("status")),
                "updated_at": datetime.now().isoformat(),
            }

            # 更新任务
            success = self._task_dao.update(task_id, update_data)

            if success:
                self._logger.info(f"成功更新任务: {task_id}")
            else:
                self._logger.warning(f"任务更新失败: {task_id}")

            return success

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"更新任务失败: {e}")
            raise BusinessLogicError(f"更新任务失败: {e}") from e

    def delete_task(self, task_id: int) -> bool:
        """
        删除任务

        Args:
            task_id: 任务ID

        Returns:
            bool: 删除是否成功
        """
        try:
            # 验证任务存在
            existing_task = self.get_task(task_id)
            if not existing_task:
                raise BusinessLogicError(f"任务不存在: {task_id}")

            # 删除任务
            success = self._task_dao.delete(task_id)

            if success:
                self._logger.info(f"成功删除任务: {task_id}")
            else:
                self._logger.warning(f"任务删除失败: {task_id}")

            return success

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"删除任务失败: {e}")
            raise BusinessLogicError(f"删除任务失败: {e}") from e

    def search_tasks(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        搜索任务

        Args:
            query: 搜索关键词
            filters: 筛选条件
            page: 页码
            page_size: 每页大小

        Returns:
            Tuple[List[Dict[str, Any]], int]: (任务列表, 总数)
        """
        try:
            # 添加任务类型筛选
            if filters is None:
                filters = {}
            filters["interaction_type"] = "task"

            # 构建搜索条件
            conditions = filters.copy() if filters else {}

            # 搜索任务
            tasks_data = self._task_dao.search(
                conditions=conditions, limit=page_size, offset=(page - 1) * page_size
            )

            # 格式化任务数据
            tasks = [self._format_task_data(task) for task in tasks_data]

            # 获取总数(简化实现)
            total = len(tasks)

            return tasks, total

        except Exception as e:
            self._logger.error(f"搜索任务失败: {e}")
            return [], 0

    def get_pending_tasks(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        获取待办任务

        Args:
            limit: 返回任务数量限制

        Returns:
            List[Dict[str, Any]]: 待办任务列表
        """
        try:
            # 使用TaskDAO获取待办任务
            tasks = self._task_dao.get_pending_tasks(limit=limit)

            # 格式化任务数据
            formatted_tasks = [self._format_task_data(task) for task in tasks]

            return formatted_tasks

        except Exception as e:
            self._logger.error(f"获取待办任务失败: {e}")
            return []

    def mark_task_completed(self, task_id: int) -> bool:
        """
        标记任务为已完成

        Args:
            task_id: 任务ID

        Returns:
            bool: 操作是否成功
        """
        try:
            return self.update_task(task_id, {"status": "completed"})

        except Exception as e:
            self._logger.error(f"标记任务完成失败: {e}")
            return False

    def _validate_task_data(self, task_data: dict[str, Any]) -> None:
        """
        验证任务数据

        Args:
            task_data: 任务数据

        Raises:
            ValidationError: 数据验证失败
        """
        if not task_data.get("title"):
            raise ValidationError("任务标题不能为空")

        # 验证关联对象(客户或供应商)
        if not task_data.get("customer_id") and not task_data.get("supplier_id"):
            raise ValidationError("任务必须关联客户或供应商")

        # 验证截止日期格式
        due_date = task_data.get("due_date")
        if due_date:
            try:
                datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            except ValueError as e:
                raise ValidationError("截止日期格式不正确") from e

    def _format_task_data(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        格式化任务数据

        Args:
            task: 任务数据

        Returns:
            Dict[str, Any]: 格式化的任务数据
        """
        return {
            "id": task.get("id"),
            "title": task.get("title", ""),
            "description": task.get("description", ""),
            "due_date": task.get("due_date"),
            "priority": task.get("priority", "medium"),
            "status": task.get("status", "pending"),
            "assigned_to": task.get("assigned_to"),
            "customer_id": task.get("customer_id"),
            "supplier_id": task.get("supplier_id"),
            "created_by": task.get("created_by"),
            "created_at": task.get("created_at"),
            "updated_at": task.get("updated_at"),
            "completed_at": task.get("completed_at"),
        }

    def get_task_statistics(self) -> dict[str, Any]:
        """
        获取任务统计信息

        Returns:
            Dict[str, Any]: 任务统计数据
        """
        try:
            # 获取所有任务
            all_tasks, total_count = self.search_tasks(page_size=1000)

            # 统计各状态任务数量
            pending_count = len([t for t in all_tasks if t.get("status") == "pending"])
            completed_count = len(
                [t for t in all_tasks if t.get("status") == "completed"]
            )
            overdue_count = len(
                [
                    t
                    for t in all_tasks
                    if t.get("status") == "pending"
                    and t.get("due_date")
                    and datetime.fromisoformat(t["due_date"].replace("Z", "+00:00"))
                    < datetime.now()
                ]
            )

            return {
                "total_tasks": total_count,
                "pending_tasks": pending_count,
                "completed_tasks": completed_count,
                "overdue_tasks": overdue_count,
                "completion_rate": (
                    completed_count / total_count if total_count > 0 else 0
                ),
            }

        except Exception as e:
            self._logger.error(f"获取任务统计失败: {e}")
            return {
                "total_tasks": 0,
                "pending_tasks": 0,
                "completed_tasks": 0,
                "overdue_tasks": 0,
                "completion_rate": 0,
            }

    def get_pending_count(self) -> int:
        """
        获取待办任务数量

        用于仪表盘显示待办任务数量指标.

        Returns:
            int: 待办任务数量

        Raises:
            BusinessLogicError: 当获取失败时
        """
        try:
            # 直接使用TaskDAO获取待办任务数量
            tasks = self._task_dao.get_pending_tasks(limit=1000)
            pending_count = len(tasks)

            self._logger.debug(f"获取待办任务数量: {pending_count}")
            return pending_count

        except Exception as e:
            self._logger.error(f"获取待办任务数量失败: {e}")
            raise BusinessLogicError(f"获取待办任务数量失败: {e}") from e
