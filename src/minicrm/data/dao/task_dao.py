"""
任务数据访问对象

提供任务相关的数据访问功能,包括:
- 基本CRUD操作
- 任务状态管理
- 任务查询和搜索
- 任务统计功能

严格遵循DAO模式和数据访问层职责:
- 只处理数据访问逻辑,不包含业务逻辑
- 使用transfunctions的CRUD模板
- 提供高效的查询接口
"""

import logging
from datetime import datetime
from typing import Any

from minicrm.data.database import DatabaseManager

from .base_dao import BaseDAO


class TaskDAO(BaseDAO):
    """
    任务数据访问对象

    继承自BaseDAO,提供任务特有的数据访问功能.
    专注于数据访问层的职责,不包含业务逻辑.
    """

    def __init__(self, database_manager: DatabaseManager):
        """
        初始化任务DAO

        Args:
            database_manager: 数据库管理器
        """
        super().__init__(database_manager, "tasks")
        self._logger = logging.getLogger(__name__)

    def get_by_status(
        self,
        status: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        根据状态获取任务列表

        Args:
            status: 任务状态
            limit: 限制数量
            offset: 偏移量

        Returns:
            list[dict[str, Any]]: 任务列表
        """
        try:
            conditions = {"status": status}
            return self.search(
                conditions=conditions,
                order_by="created_at DESC",
                limit=limit,
                offset=offset,
            )

        except Exception as e:
            self._logger.error(f"根据状态获取任务失败: {e}")
            raise

    def get_pending_tasks(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        获取待办任务

        Args:
            limit: 限制数量
            offset: 偏移量

        Returns:
            list[dict[str, Any]]: 待办任务列表
        """
        return self.get_by_status("pending", limit, offset)

    def get_by_party(
        self,
        party_id: int,
        party_type: str = "customer",
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        根据关联方获取任务列表

        Args:
            party_id: 关联方ID
            party_type: 关联方类型 ('customer' 或 'supplier')
            limit: 限制数量
            offset: 偏移量

        Returns:
            list[dict[str, Any]]: 任务列表
        """
        try:
            if party_type == "customer":
                conditions = {"customer_id": party_id}
            elif party_type == "supplier":
                conditions = {"supplier_id": party_id}
            else:
                raise ValueError(f"不支持的关联方类型: {party_type}")

            return self.search(
                conditions=conditions,
                order_by="created_at DESC",
                limit=limit,
                offset=offset,
            )

        except Exception as e:
            self._logger.error(f"根据关联方获取任务失败: {e}")
            raise

    def get_overdue_tasks(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        获取逾期任务

        Args:
            limit: 限制数量
            offset: 偏移量

        Returns:
            list[dict[str, Any]]: 逾期任务列表
        """
        try:
            # 查询状态为pending且due_date小于当前日期的任务
            current_date = datetime.now().date().isoformat()

            # 使用原生SQL查询逾期任务
            sql = """
                SELECT * FROM tasks
                WHERE status = 'pending'
                AND due_date < ?
                ORDER BY due_date ASC
                LIMIT ? OFFSET ?
            """

            results = self.db_manager.execute_query(sql, (current_date, limit, offset))

            return results

        except Exception as e:
            self._logger.error(f"获取逾期任务失败: {e}")
            raise

    def get_tasks_by_priority(
        self,
        priority: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        根据优先级获取任务

        Args:
            priority: 任务优先级 ('low', 'medium', 'high', 'urgent')
            limit: 限制数量
            offset: 偏移量

        Returns:
            list[dict[str, Any]]: 任务列表
        """
        try:
            conditions = {"priority": priority}
            return self.search(
                conditions=conditions,
                order_by="created_at DESC",
                limit=limit,
                offset=offset,
            )

        except Exception as e:
            self._logger.error(f"根据优先级获取任务失败: {e}")
            raise

    def update_status(
        self, task_id: int, status: str, completed_at: datetime | None = None
    ) -> bool:
        """
        更新任务状态

        Args:
            task_id: 任务ID
            status: 新状态
            completed_at: 完成时间(当状态为completed时)

        Returns:
            bool: 是否更新成功
        """
        try:
            update_data = {"status": status, "updated_at": datetime.now()}

            if status == "completed" and completed_at:
                update_data["completed_at"] = completed_at

            return self.update(task_id, update_data)

        except Exception as e:
            self._logger.error(f"更新任务状态失败: {e}")
            raise

    def get_task_statistics(self) -> dict[str, int]:
        """
        获取任务统计信息

        Returns:
            dict[str, int]: 任务统计数据
        """
        try:
            stats = {}

            # 统计各状态的任务数量
            statuses = ["pending", "in_progress", "completed", "cancelled"]

            for status in statuses:
                count_sql = "SELECT COUNT(*) as count FROM tasks WHERE status = ?"
                result = self.db_manager.execute_query(count_sql, (status,))
                stats[f"{status}_count"] = result[0]["count"] if result else 0

            # 统计逾期任务数量
            current_date = datetime.now().date().isoformat()
            overdue_sql = """
                SELECT COUNT(*) as count FROM tasks
                WHERE status = 'pending' AND due_date < ?
            """
            result = self.db_manager.execute_query(overdue_sql, (current_date,))
            stats["overdue_count"] = result[0]["count"] if result else 0

            # 统计今日到期任务数量
            today_sql = """
                SELECT COUNT(*) as count FROM tasks
                WHERE status = 'pending' AND due_date = ?
            """
            result = self.db_manager.execute_query(today_sql, (current_date,))
            stats["due_today_count"] = result[0]["count"] if result else 0

            return stats

        except Exception as e:
            self._logger.error(f"获取任务统计失败: {e}")
            raise

    def search_tasks(
        self,
        keyword: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        assigned_to: str | None = None,
        customer_id: int | None = None,
        supplier_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        搜索任务

        Args:
            keyword: 关键词(搜索标题和描述)
            status: 任务状态
            priority: 任务优先级
            assigned_to: 分配给
            customer_id: 客户ID
            supplier_id: 供应商ID
            limit: 限制数量
            offset: 偏移量

        Returns:
            list[dict[str, Any]]: 搜索结果
        """
        try:
            conditions = {}

            if status:
                conditions["status"] = status
            if priority:
                conditions["priority"] = priority
            if assigned_to:
                conditions["assigned_to"] = assigned_to
            if customer_id:
                conditions["customer_id"] = customer_id
            if supplier_id:
                conditions["supplier_id"] = supplier_id

            # 如果有关键词,使用原生SQL进行模糊搜索
            if keyword:
                sql_parts = ["SELECT * FROM tasks WHERE 1=1"]
                params = []

                # 添加关键词搜索条件
                sql_parts.append("AND (title LIKE ? OR description LIKE ?)")
                keyword_param = f"%{keyword}%"
                params.extend([keyword_param, keyword_param])

                # 添加其他条件
                for field, value in conditions.items():
                    sql_parts.append(f"AND {field} = ?")
                    params.append(value)

                sql_parts.append("ORDER BY created_at DESC LIMIT ? OFFSET ?")
                params.extend([limit, offset])

                sql = " ".join(sql_parts)
                return self.db_manager.execute_query(sql, tuple(params))
            else:
                # 没有关键词,使用普通搜索
                return self.search(
                    conditions=conditions,
                    order_by="created_at DESC",
                    limit=limit,
                    offset=offset,
                )

        except Exception as e:
            self._logger.error(f"搜索任务失败: {e}")
            raise


# 导出的公共接口
__all__ = [
    "TaskDAO",
]
