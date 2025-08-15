"""
客户数据访问对象实现

严格遵循数据访问层职责：
- 只负责数据的CRUD操作
- 不包含业务逻辑
- 实现ICustomerDAO接口
"""

import logging
from typing import Any

from minicrm.core.exceptions import DatabaseError
from minicrm.core.interfaces.dao_interfaces import ICustomerDAO
from minicrm.data.database import DatabaseManager


class CustomerDAO(ICustomerDAO):
    """
    客户数据访问对象实现

    严格遵循单一职责原则：
    - 只负责客户数据的数据库操作
    - 不包含业务逻辑
    - 实现标准的CRUD接口
    """

    def __init__(self, database_manager: DatabaseManager):
        """
        初始化客户DAO

        Args:
            database_manager: 数据库管理器
        """
        self._db = database_manager
        self._logger = logging.getLogger(__name__)
        self._table_name = "customers"

    def insert(self, data: dict[str, Any]) -> int:
        """
        插入客户数据

        Args:
            data: 客户数据字典

        Returns:
            int: 新插入记录的ID

        Raises:
            DatabaseError: 数据库操作失败
        """
        try:
            sql = """
            INSERT INTO customers (
                name, phone, email, company, address,
                level, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                data.get("name"),
                data.get("phone"),
                data.get("email"),
                data.get("company"),
                data.get("address"),
                data.get("level", "normal"),
                data.get("status", "active"),
                data.get("created_at"),
                data.get("updated_at"),
            )

            return self._db.execute_insert(sql, params)

        except Exception as e:
            self._logger.error(f"插入客户数据失败: {e}")
            raise DatabaseError(f"插入客户数据失败: {e}") from e

    def get_by_id(self, record_id: int) -> dict[str, Any] | None:
        """
        根据ID获取客户记录

        Args:
            record_id: 客户ID

        Returns:
            Optional[Dict[str, Any]]: 客户数据，不存在时返回None
        """
        try:
            sql = "SELECT * FROM customers WHERE id = ?"
            result = self._db.execute_query(sql, (record_id,))

            if result:
                return self._row_to_dict(result[0])
            return None

        except Exception as e:
            self._logger.error(f"获取客户记录失败: {e}")
            raise DatabaseError(f"获取客户记录失败: {e}") from e

    def update(self, record_id: int, data: dict[str, Any]) -> bool:
        """
        更新客户记录

        Args:
            record_id: 客户ID
            data: 更新数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 构建动态更新SQL
            set_clauses = []
            params = []

            for key, value in data.items():
                if key != "id":  # 不更新ID字段
                    set_clauses.append(f"{key} = ?")
                    params.append(value)

            if not set_clauses:
                return False

            sql = f"UPDATE customers SET {', '.join(set_clauses)} WHERE id = ?"
            params.append(record_id)

            rows_affected = self._db.execute_update(sql, tuple(params))
            return rows_affected > 0

        except Exception as e:
            self._logger.error(f"更新客户记录失败: {e}")
            raise DatabaseError(f"更新客户记录失败: {e}") from e

    def delete(self, record_id: int) -> bool:
        """
        删除客户记录

        Args:
            record_id: 客户ID

        Returns:
            bool: 删除是否成功
        """
        try:
            sql = "DELETE FROM customers WHERE id = ?"
            rows_affected = self._db.execute_update(sql, (record_id,))
            return rows_affected > 0

        except Exception as e:
            self._logger.error(f"删除客户记录失败: {e}")
            raise DatabaseError(f"删除客户记录失败: {e}") from e

    def search(
        self,
        conditions: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        搜索客户记录

        Args:
            conditions: 搜索条件
            order_by: 排序字段
            limit: 限制数量
            offset: 偏移量

        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        try:
            sql = "SELECT * FROM customers"
            params = []

            # 构建WHERE子句
            if conditions:
                where_clauses = []
                for key, value in conditions.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)

                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)

            # 添加排序
            if order_by:
                sql += f" ORDER BY {order_by}"
            else:
                sql += " ORDER BY created_at DESC"

            # 添加分页
            if limit:
                sql += f" LIMIT {limit}"
                if offset:
                    sql += f" OFFSET {offset}"

            results = self._db.execute_query(sql, tuple(params))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"搜索客户记录失败: {e}")
            raise DatabaseError(f"搜索客户记录失败: {e}") from e

    def count(self, conditions: dict[str, Any] | None = None) -> int:
        """
        统计客户记录数量

        Args:
            conditions: 统计条件

        Returns:
            int: 记录数量
        """
        try:
            sql = "SELECT COUNT(*) FROM customers"
            params = []

            if conditions:
                where_clauses = []
                for key, value in conditions.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)

                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)

            result = self._db.execute_query(sql, tuple(params))
            return result[0][0] if result else 0

        except Exception as e:
            self._logger.error(f"统计客户记录失败: {e}")
            raise DatabaseError(f"统计客户记录失败: {e}") from e

    def search_by_name_or_phone(self, query: str) -> list[dict[str, Any]]:
        """
        根据姓名或电话搜索客户

        Args:
            query: 搜索关键词

        Returns:
            List[Dict[str, Any]]: 匹配的客户列表
        """
        try:
            sql = """
            SELECT * FROM customers
            WHERE name LIKE ? OR phone LIKE ?
            ORDER BY name
            """

            search_pattern = f"%{query}%"
            results = self._db.execute_query(sql, (search_pattern, search_pattern))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"按姓名或电话搜索失败: {e}")
            raise DatabaseError(f"按姓名或电话搜索失败: {e}") from e

    def get_by_level(self, level: str) -> list[dict[str, Any]]:
        """
        根据客户等级获取客户列表

        Args:
            level: 客户等级

        Returns:
            List[Dict[str, Any]]: 客户列表
        """
        try:
            sql = "SELECT * FROM customers WHERE level = ? ORDER BY name"
            results = self._db.execute_query(sql, (level,))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"按等级获取客户失败: {e}")
            raise DatabaseError(f"按等级获取客户失败: {e}") from e

    def get_statistics(self) -> dict[str, Any]:
        """
        获取客户统计信息

        Returns:
            Dict[str, Any]: 统计数据
        """
        try:
            stats = {}

            # 总客户数
            total_sql = "SELECT COUNT(*) FROM customers"
            result = self._db.execute_query(total_sql)
            stats["total_customers"] = result[0][0] if result else 0

            # 按等级统计
            level_sql = """
            SELECT level, COUNT(*)
            FROM customers
            GROUP BY level
            """
            level_results = self._db.execute_query(level_sql)
            stats["by_level"] = {row[0]: row[1] for row in level_results}

            # 按状态统计
            status_sql = """
            SELECT status, COUNT(*)
            FROM customers
            GROUP BY status
            """
            status_results = self._db.execute_query(status_sql)
            stats["by_status"] = {row[0]: row[1] for row in status_results}

            # 本月新增客户
            monthly_sql = """
            SELECT COUNT(*) FROM customers
            WHERE created_at >= date('now', 'start of month')
            """
            monthly_result = self._db.execute_query(monthly_sql)
            stats["new_this_month"] = monthly_result[0][0] if monthly_result else 0

            return stats

        except Exception as e:
            self._logger.error(f"获取客户统计失败: {e}")
            raise DatabaseError(f"获取客户统计失败: {e}") from e

    def get_recent_interactions(
        self, customer_id: int, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        获取客户最近互动记录

        Args:
            customer_id: 客户ID
            limit: 限制数量

        Returns:
            List[Dict[str, Any]]: 互动记录列表
        """
        try:
            sql = """
            SELECT * FROM customer_interactions
            WHERE customer_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """

            results = self._db.execute_query(sql, (customer_id, limit))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"获取客户互动记录失败: {e}")
            raise DatabaseError(f"获取客户互动记录失败: {e}") from e

    def _row_to_dict(self, row) -> dict[str, Any]:
        """
        将数据库行转换为字典

        Args:
            row: 数据库行

        Returns:
            Dict[str, Any]: 字典格式的数据
        """
        # 这里需要根据实际的数据库实现来调整
        # 假设使用sqlite3.Row或类似的对象
        if hasattr(row, "keys"):
            return dict(row)
        else:
            # 如果是元组，需要手动映射字段名
            columns = [
                "id",
                "name",
                "phone",
                "email",
                "company",
                "address",
                "level",
                "status",
                "created_at",
                "updated_at",
            ]
            return dict(zip(columns, row, strict=False))
