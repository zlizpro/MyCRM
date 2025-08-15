"""
MiniCRM 供应商任务管理服务

提供供应商任务管理功能：
- 供应商互动记录
- 任务创建和跟进
- 任务状态管理
"""

from datetime import datetime
from typing import Any

from minicrm.core.exceptions import BusinessLogicError, ServiceError
from minicrm.data.dao.supplier_dao import SupplierDAO
from minicrm.services.base_service import BaseService


class SupplierTaskService(BaseService):
    """
    供应商任务管理服务实现

    负责供应商任务管理相关的业务逻辑：
    - 互动记录管理
    - 任务创建和跟进
    - 任务状态更新

    严格遵循单一职责原则。
    """

    def __init__(self, supplier_dao: SupplierDAO):
        """
        初始化供应商任务管理服务

        Args:
            supplier_dao: 供应商数据访问对象
        """
        super().__init__(supplier_dao)
        self._supplier_dao = supplier_dao

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "SupplierTaskService"

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

    def create_follow_up_task(self, supplier_id: int, task_data: dict[str, Any]) -> int:
        """
        创建跟进任务

        Args:
            supplier_id: 供应商ID
            task_data: 任务数据

        Returns:
            int: 任务ID

        Raises:
            BusinessLogicError: 当供应商不存在时
            ServiceError: 当创建失败时
        """
        try:
            # 验证供应商存在
            if not self._supplier_dao.get_by_id(supplier_id):
                raise BusinessLogicError(f"供应商不存在: {supplier_id}")

            # 设置任务默认值
            task_data.update(
                {
                    "supplier_id": supplier_id,
                    "created_at": datetime.now().isoformat(),
                    "status": "pending",
                    "task_type": task_data.get("task_type", "follow_up"),
                }
            )

            # 保存任务 (TODO: 实现DAO中的insert_task方法)
            # task_id = self._supplier_dao.insert_task(task_data)
            task_id = 1  # 临时返回值，待DAO实现

            self._logger.info(f"成功创建跟进任务: {supplier_id}, 任务ID: {task_id}")
            return task_id

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"创建跟进任务失败: {e}")
            raise ServiceError(f"创建跟进任务失败: {e}") from e

    def update_task_status(self, task_id: int, status: str, notes: str = "") -> bool:
        """
        更新任务状态

        Args:
            task_id: 任务ID
            status: 新状态
            notes: 更新备注

        Returns:
            bool: 更新是否成功

        Raises:
            BusinessLogicError: 当任务不存在时
            ServiceError: 当更新失败时
        """
        try:
            # 检查任务是否存在 (TODO: 实现DAO中的get_task方法)
            # task = self._supplier_dao.get_task(task_id)
            # if not task:
            #     raise BusinessLogicError(f"任务不存在: {task_id}")
            # task = {"id": task_id}  # 临时任务对象，待DAO实现后使用

            # 准备更新数据
            update_data = {
                "status": status,
                "updated_at": datetime.now().isoformat(),
            }

            if notes:
                update_data["notes"] = notes

            if status == "completed":
                update_data["completed_at"] = datetime.now().isoformat()

            # 更新任务 (TODO: 实现DAO中的update_task方法)
            # result = self._supplier_dao.update_task(task_id, update_data)
            result = True  # 临时返回值，待DAO实现

            if result:
                self._logger.info(f"成功更新任务状态: {task_id}, 状态: {status}")

            return result

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"更新任务状态失败: {e}")
            raise ServiceError(f"更新任务状态失败: {e}") from e

    def get_pending_tasks(self, supplier_id: int | None = None) -> list:
        """
        获取待处理任务

        Args:
            supplier_id: 供应商ID，如果为None则获取所有待处理任务

        Returns:
            list: 待处理任务列表

        Raises:
            ServiceError: 当查询失败时
        """
        try:
            # TODO: 实现DAO中的get_tasks方法
            # conditions = {"status": "pending"}
            # if supplier_id:
            #     conditions["supplier_id"] = supplier_id
            # tasks = self._supplier_dao.get_tasks(conditions)
            tasks: list = []  # 临时返回空列表，待DAO实现
            return tasks

        except Exception as e:
            self._logger.error(f"获取待处理任务失败: {e}")
            raise ServiceError(f"获取待处理任务失败: {e}") from e

    def complete_task(self, task_id: int, completion_notes: str = "") -> bool:
        """
        完成任务

        Args:
            task_id: 任务ID
            completion_notes: 完成备注

        Returns:
            bool: 完成是否成功
        """
        return self.update_task_status(task_id, "completed", completion_notes)
