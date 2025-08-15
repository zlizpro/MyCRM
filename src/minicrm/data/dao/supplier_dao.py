"""
供应商数据访问对象实现

严格遵循数据访问层职责：
- 只负责数据的CRUD操作
- 不包含业务逻辑
- 实现ISupplierDAO接口
"""

import logging
from datetime import datetime
from typing import Any

from minicrm.core.exceptions import DatabaseError
from minicrm.core.interfaces.dao_interfaces import ISupplierDAO
from minicrm.data.database import DatabaseManager


class SupplierDAO(ISupplierDAO):
    """
    供应商数据访问对象实现

    严格遵循单一职责原则：
    - 只负责供应商数据的数据库操作
    - 不包含业务逻辑
    - 实现标准的CRUD接口
    """

    def __init__(self, database_manager: DatabaseManager):
        """
        初始化供应商DAO

        Args:
            database_manager: 数据库管理器
        """
        self._db = database_manager
        self._logger = logging.getLogger(__name__)
        self._table_name = "suppliers"

    def insert(self, data: dict[str, Any]) -> int:
        """插入供应商数据"""
        try:
            sql = """
            INSERT INTO suppliers (
                name, contact_person, phone, email, address,
                business_license, supplier_type_id, level, status,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                data.get("name"),
                data.get("contact_person"),
                data.get("phone"),
                data.get("email"),
                data.get("address"),
                data.get("business_license"),
                data.get("supplier_type_id"),
                data.get("level", "normal"),
                data.get("status", "active"),
                data.get("created_at"),
                data.get("updated_at"),
            )

            return self._db.execute_insert(sql, params)

        except Exception as e:
            self._logger.error(f"插入供应商数据失败: {e}")
            raise DatabaseError(f"插入供应商数据失败: {e}") from e

    def get_by_id(self, record_id: int) -> dict[str, Any] | None:
        """根据ID获取供应商记录"""
        try:
            sql = "SELECT * FROM suppliers WHERE id = ?"
            result = self._db.execute_query(sql, (record_id,))

            if result:
                return self._row_to_dict(result[0])
            return None

        except Exception as e:
            self._logger.error(f"获取供应商记录失败: {e}")
            raise DatabaseError(f"获取供应商记录失败: {e}") from e

    def update(self, record_id: int, data: dict[str, Any]) -> bool:
        """更新供应商记录"""
        try:
            set_clauses = []
            params = []

            for key, value in data.items():
                if key != "id":
                    set_clauses.append(f"{key} = ?")
                    params.append(value)

            if not set_clauses:
                return False

            sql = f"UPDATE suppliers SET {', '.join(set_clauses)} WHERE id = ?"
            params.append(record_id)

            rows_affected = self._db.execute_update(sql, tuple(params))
            return rows_affected > 0

        except Exception as e:
            self._logger.error(f"更新供应商记录失败: {e}")
            raise DatabaseError(f"更新供应商记录失败: {e}") from e

    def delete(self, record_id: int) -> bool:
        """删除供应商记录"""
        try:
            sql = "DELETE FROM suppliers WHERE id = ?"
            rows_affected = self._db.execute_update(sql, (record_id,))
            return rows_affected > 0

        except Exception as e:
            self._logger.error(f"删除供应商记录失败: {e}")
            raise DatabaseError(f"删除供应商记录失败: {e}") from e

    def search(
        self,
        conditions: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """搜索供应商记录"""
        try:
            sql = "SELECT * FROM suppliers"
            params = []

            if conditions:
                where_clauses = []
                for key, value in conditions.items():
                    where_clauses.append(f"{key} = ?")
                    params.append(value)

                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)

            if order_by:
                sql += f" ORDER BY {order_by}"
            else:
                sql += " ORDER BY created_at DESC"

            if limit:
                sql += f" LIMIT {limit}"
                if offset:
                    sql += f" OFFSET {offset}"

            results = self._db.execute_query(sql, tuple(params))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"搜索供应商记录失败: {e}")
            raise DatabaseError(f"搜索供应商记录失败: {e}") from e

    def count(self, conditions: dict[str, Any] | None = None) -> int:
        """统计供应商记录数量"""
        try:
            sql = "SELECT COUNT(*) FROM suppliers"
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
            self._logger.error(f"统计供应商记录失败: {e}")
            raise DatabaseError(f"统计供应商记录失败: {e}") from e

    def search_by_name_or_contact(self, query: str) -> list[dict[str, Any]]:
        """根据名称或联系方式搜索供应商"""
        try:
            sql = """
            SELECT * FROM suppliers
            WHERE name LIKE ? OR contact_person LIKE ? OR phone LIKE ?
            ORDER BY name
            """

            search_pattern = f"%{query}%"
            results = self._db.execute_query(
                sql, (search_pattern, search_pattern, search_pattern)
            )
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"按名称或联系方式搜索失败: {e}")
            raise DatabaseError(f"按名称或联系方式搜索失败: {e}") from e

    def get_by_type(self, supplier_type_id: int) -> list[dict[str, Any]]:
        """根据供应商类型获取供应商列表"""
        try:
            sql = "SELECT * FROM suppliers WHERE supplier_type_id = ? ORDER BY name"
            results = self._db.execute_query(sql, (supplier_type_id,))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"按类型获取供应商失败: {e}")
            raise DatabaseError(f"按类型获取供应商失败: {e}") from e

    def get_statistics(self) -> dict[str, Any]:
        """获取供应商统计信息"""
        try:
            stats = {}

            # 总供应商数
            total_sql = "SELECT COUNT(*) FROM suppliers"
            result = self._db.execute_query(total_sql)
            stats["total_suppliers"] = result[0][0] if result else 0

            # 按类型统计
            type_sql = """
            SELECT st.name, COUNT(s.id)
            FROM suppliers s
            LEFT JOIN supplier_types st ON s.supplier_type_id = st.id
            GROUP BY s.supplier_type_id, st.name
            """
            type_results = self._db.execute_query(type_sql)
            stats["by_type"] = {row[0] or "未分类": row[1] for row in type_results}

            # 按状态统计
            status_sql = """
            SELECT status, COUNT(*)
            FROM suppliers
            GROUP BY status
            """
            status_results = self._db.execute_query(status_sql)
            stats["by_status"] = {row[0]: row[1] for row in status_results}

            return stats

        except Exception as e:
            self._logger.error(f"获取供应商统计失败: {e}")
            raise DatabaseError(f"获取供应商统计失败: {e}") from e

    def get_quality_ratings(self, supplier_id: int) -> list[dict[str, Any]]:
        """获取供应商质量评级记录"""
        try:
            sql = """
            SELECT * FROM supplier_quality_ratings
            WHERE supplier_id = ?
            ORDER BY created_at DESC
            """

            results = self._db.execute_query(sql, (supplier_id,))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"获取供应商质量评级失败: {e}")
            raise DatabaseError(f"获取供应商质量评级失败: {e}") from e

    def get_transaction_history(self, supplier_id: int) -> list[dict[str, Any]]:
        """获取供应商交易历史记录"""
        try:
            sql = """
            SELECT * FROM supplier_transactions
            WHERE supplier_id = ?
            ORDER BY transaction_date DESC
            """

            results = self._db.execute_query(sql, (supplier_id,))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"获取供应商交易历史失败: {e}")
            raise DatabaseError(f"获取供应商交易历史失败: {e}") from e

    def get_interaction_history(self, supplier_id: int) -> list[dict[str, Any]]:
        """获取供应商互动历史记录"""
        try:
            sql = """
            SELECT * FROM supplier_interactions
            WHERE supplier_id = ?
            ORDER BY created_at DESC
            """

            results = self._db.execute_query(sql, (supplier_id,))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"获取供应商互动历史失败: {e}")
            raise DatabaseError(f"获取供应商互动历史失败: {e}") from e

    def insert_interaction(self, interaction_data: dict[str, Any]) -> int:
        """插入供应商互动记录"""
        try:
            sql = """
            INSERT INTO supplier_interactions (
                supplier_id, interaction_type, content,
                created_at, created_by
            ) VALUES (?, ?, ?, ?, ?)
            """

            params = (
                interaction_data.get("supplier_id"),
                interaction_data.get("interaction_type"),
                interaction_data.get("content"),
                interaction_data.get("created_at"),
                interaction_data.get("created_by"),
            )

            return self._db.execute_insert(sql, params)

        except Exception as e:
            self._logger.error(f"插入供应商互动记录失败: {e}")
            raise DatabaseError(f"插入供应商互动记录失败: {e}") from e

    def insert_communication_event(self, event_data: dict[str, Any]) -> int:
        """插入供应商交流事件记录"""
        try:
            sql = """
            INSERT INTO supplier_communication_events (
                supplier_id, event_number, event_type, title, content,
                priority, status, created_at, due_time, created_by, urgency_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                event_data.get("supplier_id"),
                event_data.get("event_number"),
                event_data.get("event_type"),
                event_data.get("title"),
                event_data.get("content"),
                event_data.get("priority"),
                event_data.get("status"),
                event_data.get("created_at"),
                event_data.get("due_time"),
                event_data.get("created_by"),
                event_data.get("urgency_level"),
            )

            return self._db.execute_insert(sql, params)

        except Exception as e:
            self._logger.error(f"插入供应商交流事件失败: {e}")
            raise DatabaseError(f"插入供应商交流事件失败: {e}") from e

    def get_communication_event(self, event_id: int) -> dict[str, Any] | None:
        """获取交流事件记录"""
        try:
            sql = "SELECT * FROM supplier_communication_events WHERE id = ?"
            result = self._db.execute_query(sql, (event_id,))

            if result:
                return self._row_to_dict(result[0])
            return None

        except Exception as e:
            self._logger.error(f"获取交流事件失败: {e}")
            raise DatabaseError(f"获取交流事件失败: {e}") from e

    def update_communication_event(self, event_id: int, data: dict[str, Any]) -> bool:
        """更新交流事件记录"""
        try:
            set_clauses = []
            params = []

            for key, value in data.items():
                if key != "id":
                    set_clauses.append(f"{key} = ?")
                    params.append(value)

            if not set_clauses:
                return False

            sql = (
                f"UPDATE supplier_communication_events SET "
                f"{', '.join(set_clauses)} WHERE id = ?"
            )
            params.append(event_id)

            rows_affected = self._db.execute_update(sql, tuple(params))
            return rows_affected > 0

        except Exception as e:
            self._logger.error(f"更新交流事件失败: {e}")
            raise DatabaseError(f"更新交流事件失败: {e}") from e

    def get_communication_events(
        self,
        supplier_id: int | None = None,
        start_date: datetime | None = None,
        status_filter: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """获取交流事件列表"""
        try:
            sql = "SELECT * FROM supplier_communication_events WHERE 1=1"
            params: list[str | int] = []

            if supplier_id:
                sql += " AND supplier_id = ?"
                params.append(supplier_id)

            if start_date:
                sql += " AND created_at >= ?"
                params.append(start_date.isoformat())

            if status_filter:
                placeholders = ",".join(["?"] * len(status_filter))
                sql += f" AND status IN ({placeholders})"
                params.extend(status_filter)

            sql += " ORDER BY created_at DESC"

            results = self._db.execute_query(sql, tuple(params))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"获取交流事件列表失败: {e}")
            raise DatabaseError(f"获取交流事件列表失败: {e}") from e

    def get_daily_event_count(self, supplier_id: int, date_str: str) -> int:
        """获取指定日期的事件数量"""
        try:
            sql = """
            SELECT COUNT(*) FROM supplier_communication_events
            WHERE supplier_id = ? AND DATE(created_at) = ?
            """
            result = self._db.execute_query(sql, (supplier_id, date_str))
            return result[0][0] if result else 0

        except Exception as e:
            self._logger.error(f"获取日事件数量失败: {e}")
            raise DatabaseError(f"获取日事件数量失败: {e}") from e

    def insert_event_processing_result(self, result_data: dict[str, Any]) -> int:
        """插入事件处理结果"""
        try:
            sql = """
            INSERT INTO event_processing_results (
                event_id, solution, result, satisfaction_rating,
                processing_time, processed_by, follow_up_required
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                result_data.get("event_id"),
                result_data.get("solution"),
                result_data.get("result"),
                result_data.get("satisfaction_rating"),
                result_data.get("processing_time"),
                result_data.get("processed_by"),
                result_data.get("follow_up_required"),
            )

            return self._db.execute_insert(sql, params)

        except Exception as e:
            self._logger.error(f"插入事件处理结果失败: {e}")
            raise DatabaseError(f"插入事件处理结果失败: {e}") from e

    def insert_payable(self, payable_data: dict[str, Any]) -> int:
        """插入应付账款记录"""
        try:
            sql = """
            INSERT INTO supplier_payables (
                supplier_id, amount, due_date, description,
                status, created_at, purchase_order_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                payable_data.get("supplier_id"),
                payable_data.get("amount"),
                payable_data.get("due_date"),
                payable_data.get("description"),
                payable_data.get("status", "pending"),
                payable_data.get("created_at"),
                payable_data.get("purchase_order_id"),
            )

            return self._db.execute_insert(sql, params)

        except Exception as e:
            self._logger.error(f"插入应付账款记录失败: {e}")
            raise DatabaseError(f"插入应付账款记录失败: {e}") from e

    def insert_supplier_payment(self, payment_data: dict[str, Any]) -> int:
        """插入供应商付款记录"""
        try:
            sql = """
            INSERT INTO supplier_payments (
                supplier_id, amount, payment_method, payment_date,
                description, created_at, reference_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                payment_data.get("supplier_id"),
                payment_data.get("amount"),
                payment_data.get("payment_method"),
                payment_data.get("payment_date"),
                payment_data.get("description"),
                payment_data.get("created_at"),
                payment_data.get("reference_number"),
            )

            return self._db.execute_insert(sql, params)

        except Exception as e:
            self._logger.error(f"插入供应商付款记录失败: {e}")
            raise DatabaseError(f"插入供应商付款记录失败: {e}") from e

    def get_payables(self, supplier_id: int) -> list[dict[str, Any]]:
        """获取供应商应付账款列表"""
        try:
            sql = """
            SELECT * FROM supplier_payables
            WHERE supplier_id = ?
            ORDER BY due_date ASC
            """

            results = self._db.execute_query(sql, (supplier_id,))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"获取应付账款列表失败: {e}")
            raise DatabaseError(f"获取应付账款列表失败: {e}") from e

    def get_supplier_payments(self, supplier_id: int) -> list[dict[str, Any]]:
        """获取供应商付款记录"""
        try:
            sql = """
            SELECT * FROM supplier_payments
            WHERE supplier_id = ?
            ORDER BY payment_date DESC
            """

            results = self._db.execute_query(sql, (supplier_id,))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"获取供应商付款记录失败: {e}")
            raise DatabaseError(f"获取供应商付款记录失败: {e}") from e

    def get_payables_summary(self) -> dict[str, Any]:
        """获取应付账款汇总信息"""
        try:
            # 总应付账款
            total_sql = """
            SELECT COALESCE(SUM(amount), 0) FROM supplier_payables
            WHERE status = 'pending'
            """
            total_result = self._db.execute_query(total_sql)
            total_amount = total_result[0][0] if total_result else 0

            # 逾期应付账款
            overdue_sql = """
            SELECT COALESCE(SUM(amount), 0) FROM supplier_payables
            WHERE status = 'pending' AND due_date < date('now')
            """
            overdue_result = self._db.execute_query(overdue_sql)
            overdue_amount = overdue_result[0][0] if overdue_result else 0

            # 即将到期的应付账款（7天内）
            upcoming_sql = """
            SELECT COALESCE(SUM(amount), 0) FROM supplier_payables
            WHERE status = 'pending'
            AND due_date BETWEEN date('now') AND date('now', '+7 days')
            """
            upcoming_result = self._db.execute_query(upcoming_sql)
            upcoming_amount = upcoming_result[0][0] if upcoming_result else 0

            return {
                "total_amount": float(total_amount),
                "overdue_amount": float(overdue_amount),
                "upcoming_amount": float(upcoming_amount),
                "overdue_count": self._count_overdue_payables(),
                "upcoming_count": self._count_upcoming_payables(),
            }

        except Exception as e:
            self._logger.error(f"获取应付账款汇总失败: {e}")
            raise DatabaseError(f"获取应付账款汇总失败: {e}") from e

    def update_payable_status(self, payable_id: int, status: str) -> bool:
        """更新应付账款状态"""
        try:
            sql = "UPDATE supplier_payables SET status = ? WHERE id = ?"
            rows_affected = self._db.execute_update(sql, (status, payable_id))
            return rows_affected > 0

        except Exception as e:
            self._logger.error(f"更新应付账款状态失败: {e}")
            raise DatabaseError(f"更新应付账款状态失败: {e}") from e

    def get_pending_payables(self, supplier_id: int) -> list[dict[str, Any]]:
        """获取待付款的应付账款"""
        try:
            sql = """
            SELECT * FROM supplier_payables
            WHERE supplier_id = ? AND status = 'pending'
            ORDER BY due_date ASC
            """

            results = self._db.execute_query(sql, (supplier_id,))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"获取待付款应付账款失败: {e}")
            raise DatabaseError(f"获取待付款应付账款失败: {e}") from e

    def get_payment_terms(self, supplier_id: int) -> dict[str, Any] | None:
        """获取供应商账期设置"""
        try:
            sql = """
            SELECT * FROM supplier_payment_terms
            WHERE supplier_id = ?
            ORDER BY created_at DESC
            LIMIT 1
            """

            result = self._db.execute_query(sql, (supplier_id,))
            if result:
                return self._row_to_dict(result[0])
            return None

        except Exception as e:
            self._logger.error(f"获取供应商账期设置失败: {e}")
            raise DatabaseError(f"获取供应商账期设置失败: {e}") from e

    def insert_payment_terms(self, terms_data: dict[str, Any]) -> int:
        """插入供应商账期设置"""
        try:
            sql = """
            INSERT INTO supplier_payment_terms (
                supplier_id, payment_days, payment_method,
                discount_rate, discount_days, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """

            params = (
                terms_data.get("supplier_id"),
                terms_data.get("payment_days"),
                terms_data.get("payment_method"),
                terms_data.get("discount_rate", 0),
                terms_data.get("discount_days", 0),
                terms_data.get("created_at"),
            )

            return self._db.execute_insert(sql, params)

        except Exception as e:
            self._logger.error(f"插入供应商账期设置失败: {e}")
            raise DatabaseError(f"插入供应商账期设置失败: {e}") from e

    def _count_overdue_payables(self) -> int:
        """统计逾期应付账款数量"""
        try:
            sql = """
            SELECT COUNT(*) FROM supplier_payables
            WHERE status = 'pending' AND due_date < date('now')
            """
            result = self._db.execute_query(sql)
            return result[0][0] if result else 0

        except Exception as e:
            self._logger.error(f"统计逾期应付账款失败: {e}")
            return 0

    def _count_upcoming_payables(self) -> int:
        """统计即将到期应付账款数量"""
        try:
            sql = """
            SELECT COUNT(*) FROM supplier_payables
            WHERE status = 'pending'
            AND due_date BETWEEN date('now') AND date('now', '+7 days')
            """
            result = self._db.execute_query(sql)
            return result[0][0] if result else 0

        except Exception as e:
            self._logger.error(f"统计即将到期应付账款失败: {e}")
            return 0

    def _row_to_dict(self, row: Any) -> dict[str, Any]:
        """将数据库行转换为字典"""
        if hasattr(row, "keys"):
            return dict(row)
        else:
            columns = [
                "id",
                "name",
                "contact_person",
                "phone",
                "email",
                "address",
                "business_license",
                "supplier_type_id",
                "level",
                "status",
                "created_at",
                "updated_at",
            ]
            return dict(zip(columns, row, strict=False))
