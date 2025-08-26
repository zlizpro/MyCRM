"""
客户数据访问对象实现

严格遵循数据访问层职责:
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

    严格遵循单一职责原则:
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
                name, phone, email, address, customer_type_id,
                contact_person, notes, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                data.get("name"),
                data.get("phone"),
                data.get("email"),
                data.get("address"),
                data.get("customer_type_id"),
                data.get("contact_person"),
                data.get("notes"),
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
            Optional[Dict[str, Any]]: 客户数据,不存在时返回None
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

    def get_by_type(self, customer_type_id: int) -> list[dict[str, Any]]:
        """
        根据客户类型获取客户列表

        Args:
            customer_type_id: 客户类型ID

        Returns:
            List[Dict[str, Any]]: 客户列表
        """
        try:
            sql = "SELECT * FROM customers WHERE customer_type_id = ? ORDER BY name"
            results = self._db.execute_query(sql, (customer_type_id,))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"按类型获取客户失败: {e}")
            raise DatabaseError(f"按类型获取客户失败: {e}") from e

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

            # 按类型统计
            type_sql = """
            SELECT ct.name, COUNT(c.id)
            FROM customers c
            LEFT JOIN customer_types ct ON c.customer_type_id = ct.id
            GROUP BY c.customer_type_id, ct.name
            """
            type_results = self._db.execute_query(type_sql)
            stats["by_type"] = {row[0] or "未分类": row[1] for row in type_results}

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

    def execute_complex_query(
        self, sql: str, params: tuple[Any, ...] | None = None
    ) -> list[dict[str, Any]]:
        """
        执行复杂查询

        Args:
            sql: SQL查询语句
            params: 查询参数

        Returns:
            List[Dict[str, Any]]: 查询结果

        Raises:
            DatabaseError: 数据库操作失败
        """
        try:
            results = self._db.execute_query(sql, params or ())
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"执行复杂查询失败: {e}")
            raise DatabaseError(f"执行复杂查询失败: {e}") from e

    def search_with_conditions(
        self,
        conditions: dict[str, Any],
        joins: list[str] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        根据复杂条件搜索客户

        Args:
            conditions: 搜索条件字典
            joins: 表连接列表
            order_by: 排序字段
            limit: 限制数量
            offset: 偏移量

        Returns:
            List[Dict[str, Any]]: 搜索结果

        Raises:
            DatabaseError: 数据库操作失败
        """
        try:
            # 构建基础查询
            sql_parts = ["SELECT customers.*"]
            params = []

            # 添加统计字段(如果有订单关联)
            if joins and any("orders" in join for join in joins):
                sql_parts[0] += """,
                    COUNT(orders.id) as total_orders,
                    COALESCE(SUM(orders.amount), 0) as total_amount,
                    MAX(orders.order_date) as last_order_date"""

            sql_parts.append("FROM customers")

            # 添加表连接
            if joins:
                sql_parts.extend(joins)

            # 构建WHERE条件
            if conditions:
                where_clauses = []
                for field, value in conditions.items():
                    if isinstance(value, list):
                        # IN条件
                        placeholders = ", ".join(["?" for _ in value])
                        where_clauses.append(f"{field} IN ({placeholders})")
                        params.extend(value)
                    elif isinstance(value, dict):
                        # 范围条件
                        if "min" in value and "max" in value:
                            where_clauses.append(f"{field} BETWEEN ? AND ?")
                            params.extend([value["min"], value["max"]])
                        elif "min" in value:
                            where_clauses.append(f"{field} >= ?")
                            params.append(value["min"])
                        elif "max" in value:
                            where_clauses.append(f"{field} <= ?")
                            params.append(value["max"])
                    elif isinstance(value, str) and "%" in value:
                        # LIKE条件
                        where_clauses.append(f"{field} LIKE ?")
                        params.append(value)
                    else:
                        # 等值条件
                        where_clauses.append(f"{field} = ?")
                        params.append(value)

                if where_clauses:
                    sql_parts.append("WHERE " + " AND ".join(where_clauses))

            # 添加GROUP BY(如果有聚合字段)
            if joins and any("orders" in join for join in joins):
                sql_parts.append("GROUP BY customers.id")

            # 添加排序
            if order_by:
                sql_parts.append(f"ORDER BY {order_by}")

            # 添加限制和偏移
            if limit:
                sql_parts.append(f"LIMIT {limit}")
                if offset:
                    sql_parts.append(f"OFFSET {offset}")

            sql = " ".join(sql_parts)
            results = self._db.execute_query(sql, tuple(params))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"复杂条件搜索失败: {e}")
            raise DatabaseError(f"复杂条件搜索失败: {e}") from e

    # ==================== 财务相关方法 ====================

    def insert_receivable(self, receivable_data: dict[str, Any]) -> int:
        """
        插入应收账款记录

        Args:
            receivable_data: 应收账款数据

        Returns:
            int: 应收账款记录ID
        """
        try:
            sql = """
            INSERT INTO financial_records (
                customer_id, record_type, amount, due_date, status, notes, created_at
            ) VALUES (?, 'receivable', ?, ?, ?, ?, ?)
            """

            params = (
                receivable_data.get("customer_id"),
                receivable_data.get("amount"),
                receivable_data.get("due_date"),
                receivable_data.get("status", "pending"),
                receivable_data.get("notes", ""),
                receivable_data.get("created_at"),
            )

            return self._db.execute_insert(sql, params)

        except Exception as e:
            self._logger.error(f"插入应收账款记录失败: {e}")
            raise DatabaseError(f"插入应收账款记录失败: {e}") from e

    def insert_payment(self, payment_data: dict[str, Any]) -> int:
        """
        插入收款记录

        Args:
            payment_data: 收款数据

        Returns:
            int: 收款记录ID
        """
        try:
            sql = """
            INSERT INTO financial_records (
                customer_id, record_type, amount, paid_date, status, notes, created_at
            ) VALUES (?, 'payment', ?, ?, 'paid', ?, ?)
            """

            params = (
                payment_data.get("customer_id"),
                payment_data.get("amount"),
                payment_data.get("payment_date"),
                payment_data.get("notes", ""),
                payment_data.get("created_at"),
            )

            return self._db.execute_insert(sql, params)

        except Exception as e:
            self._logger.error(f"插入收款记录失败: {e}")
            raise DatabaseError(f"插入收款记录失败: {e}") from e

    def get_receivables(self, customer_id: int = None) -> list[dict[str, Any]]:
        """
        获取应收账款记录

        Args:
            customer_id: 客户ID,为None时获取所有应收账款

        Returns:
            List[Dict[str, Any]]: 应收账款记录列表
        """
        try:
            if customer_id:
                sql = """
                SELECT fr.*, c.name as customer_name
                FROM financial_records fr
                JOIN customers c ON fr.customer_id = c.id
                WHERE fr.customer_id = ? AND fr.record_type = 'receivable'
                ORDER BY fr.due_date
                """
                params = (customer_id,)
            else:
                sql = """
                SELECT fr.*, c.name as customer_name
                FROM financial_records fr
                JOIN customers c ON fr.customer_id = c.id
                WHERE fr.record_type = 'receivable'
                ORDER BY fr.due_date
                """
                params = ()

            results = self._db.execute_query(sql, params)
            return [self._financial_row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"获取应收账款记录失败: {e}")
            raise DatabaseError(f"获取应收账款记录失败: {e}") from e

    def get_payments(self, customer_id: int = None) -> list[dict[str, Any]]:
        """
        获取收款记录

        Args:
            customer_id: 客户ID,为None时获取所有收款记录

        Returns:
            List[Dict[str, Any]]: 收款记录列表
        """
        try:
            if customer_id:
                sql = """
                SELECT fr.*, c.name as customer_name
                FROM financial_records fr
                JOIN customers c ON fr.customer_id = c.id
                WHERE fr.customer_id = ? AND fr.record_type = 'payment'
                ORDER BY fr.paid_date DESC
                """
                params = (customer_id,)
            else:
                sql = """
                SELECT fr.*, c.name as customer_name
                FROM financial_records fr
                JOIN customers c ON fr.customer_id = c.id
                WHERE fr.record_type = 'payment'
                ORDER BY fr.paid_date DESC
                """
                params = ()

            results = self._db.execute_query(sql, params)
            return [self._financial_row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"获取收款记录失败: {e}")
            raise DatabaseError(f"获取收款记录失败: {e}") from e

    def get_receivables_summary(self) -> dict[str, Any]:
        """
        获取应收账款汇总信息

        Returns:
            Dict[str, Any]: 应收账款汇总数据
        """
        try:
            # 总应收账款
            total_sql = """
            SELECT COALESCE(SUM(amount), 0) as total_amount
            FROM financial_records
            WHERE record_type = 'receivable' AND status = 'pending'
            """
            total_result = self._db.execute_query(total_sql)
            total_amount = total_result[0][0] if total_result else 0

            # 逾期应收账款
            overdue_sql = """
            SELECT COALESCE(SUM(amount), 0) as overdue_amount
            FROM financial_records
            WHERE record_type = 'receivable' AND status = 'pending'
            AND due_date < date('now')
            """
            overdue_result = self._db.execute_query(overdue_sql)
            overdue_amount = overdue_result[0][0] if overdue_result else 0

            return {
                "total_amount": float(total_amount),
                "overdue_amount": float(overdue_amount),
            }

        except Exception as e:
            self._logger.error(f"获取应收账款汇总失败: {e}")
            raise DatabaseError(f"获取应收账款汇总失败: {e}") from e

    def get_pending_receivables(self, customer_id: int) -> list[dict[str, Any]]:
        """
        获取待收款的应收账款

        Args:
            customer_id: 客户ID

        Returns:
            List[Dict[str, Any]]: 待收款应收账款列表
        """
        try:
            sql = """
            SELECT * FROM financial_records
            WHERE customer_id = ? AND record_type = 'receivable' AND status = 'pending'
            ORDER BY due_date
            """

            results = self._db.execute_query(sql, (customer_id,))
            return [self._financial_row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"获取待收款应收账款失败: {e}")
            raise DatabaseError(f"获取待收款应收账款失败: {e}") from e

    def update_receivable_status(self, receivable_id: int, status: str) -> bool:
        """
        更新应收账款状态

        Args:
            receivable_id: 应收账款ID
            status: 新状态

        Returns:
            bool: 更新是否成功
        """
        try:
            sql = """
            UPDATE financial_records
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND record_type = 'receivable'
            """

            return self._db.execute_update(sql, (status, receivable_id))

        except Exception as e:
            self._logger.error(f"更新应收账款状态失败: {e}")
            raise DatabaseError(f"更新应收账款状态失败: {e}") from e

    def update_receivable_amount(self, receivable_id: int, new_amount: float) -> bool:
        """
        更新应收账款金额

        Args:
            receivable_id: 应收账款ID
            new_amount: 新金额

        Returns:
            bool: 更新是否成功
        """
        try:
            sql = """
            UPDATE financial_records
            SET amount = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND record_type = 'receivable'
            """

            return self._db.execute_update(sql, (new_amount, receivable_id))

        except Exception as e:
            self._logger.error(f"更新应收账款金额失败: {e}")
            raise DatabaseError(f"更新应收账款金额失败: {e}") from e

    def get_receivables_total(self, customer_id: int) -> float:
        """
        获取客户应收账款总额

        Args:
            customer_id: 客户ID

        Returns:
            float: 应收账款总额
        """
        try:
            sql = """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM financial_records
            WHERE customer_id = ? AND record_type = 'receivable' AND status = 'pending'
            """

            result = self._db.execute_query(sql, (customer_id,))
            return float(result[0][0]) if result else 0.0

        except Exception as e:
            self._logger.error(f"获取应收账款总额失败: {e}")
            raise DatabaseError(f"获取应收账款总额失败: {e}") from e

    def get_credit_info(self, customer_id: int) -> dict[str, Any] | None:
        """
        获取客户授信信息

        Args:
            customer_id: 客户ID

        Returns:
            Optional[Dict[str, Any]]: 授信信息,不存在时返回None
        """
        try:
            # 这里假设有一个credit_records表,如果没有则返回None
            # 实际实现中可能需要创建这个表
            return None

        except Exception as e:
            self._logger.error(f"获取客户授信信息失败: {e}")
            raise DatabaseError(f"获取客户授信信息失败: {e}") from e

    def insert_credit_record(self, credit_data: dict[str, Any]) -> int:
        """
        插入授信记录

        Args:
            credit_data: 授信数据

        Returns:
            int: 授信记录ID
        """
        try:
            # 这里需要创建credit_records表的实现
            # 暂时返回一个模拟ID
            return 1

        except Exception as e:
            self._logger.error(f"插入授信记录失败: {e}")
            raise DatabaseError(f"插入授信记录失败: {e}") from e

    def get_transaction_history(self, customer_id: int) -> list[dict[str, Any]]:
        """
        获取客户交易历史

        Args:
            customer_id: 客户ID

        Returns:
            List[Dict[str, Any]]: 交易历史记录
        """
        try:
            # 这里可以从合同表或其他相关表获取交易历史
            # 暂时返回空列表
            return []

        except Exception as e:
            self._logger.error(f"获取客户交易历史失败: {e}")
            raise DatabaseError(f"获取客户交易历史失败: {e}") from e

    def _financial_row_to_dict(self, row: Any) -> dict[str, Any]:
        """
        将财务记录行转换为字典

        Args:
            row: 数据库行

        Returns:
            Dict[str, Any]: 字典格式的数据
        """
        if hasattr(row, "keys"):
            return dict(row)
        else:
            # 财务记录表的字段映射
            columns = [
                "id",
                "customer_id",
                "supplier_id",
                "contract_id",
                "record_type",
                "amount",
                "due_date",
                "paid_date",
                "status",
                "notes",
                "created_at",
                "updated_at",
                "customer_name",  # 来自JOIN的字段
            ]
            return dict(zip(columns, row, strict=False))

    def _row_to_dict(self, row: Any) -> dict[str, Any]:
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
            # 如果是元组,需要手动映射字段名
            columns = [
                "id",
                "name",
                "phone",
                "email",
                "address",
                "customer_type_id",
                "contact_person",
                "notes",
                "created_at",
                "updated_at",
            ]
            return dict(zip(columns, row, strict=False))
