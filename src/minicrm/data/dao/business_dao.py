"""
业务数据访问对象实现

负责处理业务相关的数据访问操作，包括：
- 报价管理
- 合同管理
- 订单管理
- 付款记录
- 售后服务记录
- 任务管理
- 客户互动记录

严格遵循数据访问层职责，不包含业务逻辑。
"""

import logging
from datetime import datetime
from typing import Any

from minicrm.core.exceptions import DatabaseError
from minicrm.data.dao.base_dao import BaseDAO
from minicrm.data.database import DatabaseManager


class QuoteDAO(BaseDAO):
    """
    报价数据访问对象

    负责报价和报价明细的数据库操作
    """

    def __init__(self, database_manager: DatabaseManager):
        """初始化报价DAO"""
        super().__init__(database_manager, "quotes")
        self._logger = logging.getLogger(__name__)

    def create_quote_with_items(
        self, quote_data: dict[str, Any], quote_items: list[dict[str, Any]]
    ) -> int:
        """
        创建报价及其明细项

        Args:
            quote_data: 报价主数据
            quote_items: 报价明细项列表

        Returns:
            int: 新创建的报价ID
        """
        try:
            with self._db.transaction() as conn:
                # 插入报价主记录
                quote_sql = """
                INSERT INTO quotes (
                    quote_number, customer_id, total_amount, status,
                    valid_until, notes, created_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                quote_params = (
                    quote_data.get("quote_number"),
                    quote_data.get("customer_id"),
                    quote_data.get("total_amount"),
                    quote_data.get("status", "draft"),
                    quote_data.get("valid_until"),
                    quote_data.get("notes"),
                    quote_data.get("created_by"),
                    quote_data.get("created_at", datetime.now()),
                    quote_data.get("updated_at", datetime.now()),
                )

                cursor = conn.execute(quote_sql, quote_params)
                quote_id = cursor.lastrowid

                # 插入报价明细
                if quote_items:
                    item_sql = """
                    INSERT INTO quote_items (
                        quote_id, product_id, product_name, specification,
                        quantity, unit_price, total_price, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """

                    for item in quote_items:
                        item_params = (
                            quote_id,
                            item.get("product_id"),
                            item.get("product_name"),
                            item.get("specification"),
                            item.get("quantity"),
                            item.get("unit_price"),
                            item.get("total_price"),
                            item.get("notes"),
                        )
                        conn.execute(item_sql, item_params)

                self._logger.info(f"成功创建报价，ID: {quote_id}")
                return quote_id

        except Exception as e:
            self._logger.error(f"创建报价失败: {e}")
            raise DatabaseError(f"创建报价失败: {e}") from e

    def get_quote_with_items(self, quote_id: int) -> dict[str, Any] | None:
        """
        获取报价及其明细项

        Args:
            quote_id: 报价ID

        Returns:
            Optional[Dict[str, Any]]: 包含明细项的报价数据
        """
        try:
            # 获取报价主记录
            quote = self.get_by_id(quote_id)
            if not quote:
                return None

            # 获取报价明细
            items_sql = "SELECT * FROM quote_items WHERE quote_id = ? ORDER BY id"
            items_result = self._db.execute_query(items_sql, (quote_id,))
            quote["items"] = [self._row_to_dict(row) for row in items_result]

            return quote

        except Exception as e:
            self._logger.error(f"获取报价详情失败: {e}")
            raise DatabaseError(f"获取报价详情失败: {e}") from e

    def get_quotes_by_customer(self, customer_id: int) -> list[dict[str, Any]]:
        """获取客户的所有报价"""
        return self.search({"customer_id": customer_id}, "created_at DESC")

    def get_quotes_by_status(self, status: str) -> list[dict[str, Any]]:
        """根据状态获取报价列表"""
        return self.search({"status": status}, "created_at DESC")


class ContractDAO(BaseDAO):
    """
    合同数据访问对象

    负责合同相关的数据库操作
    """

    def __init__(self, database_manager: DatabaseManager):
        """初始化合同DAO"""
        super().__init__(database_manager, "contracts")
        self._logger = logging.getLogger(__name__)

    def get_contracts_by_customer(self, customer_id: int) -> list[dict[str, Any]]:
        """获取客户的所有合同"""
        return self.search({"customer_id": customer_id}, "signed_date DESC")

    def get_contracts_by_supplier(self, supplier_id: int) -> list[dict[str, Any]]:
        """获取供应商的所有合同"""
        return self.search({"supplier_id": supplier_id}, "signed_date DESC")

    def get_contracts_by_status(self, status: str) -> list[dict[str, Any]]:
        """根据状态获取合同列表"""
        return self.search({"status": status}, "signed_date DESC")

    def get_expiring_contracts(self, days: int = 30) -> list[dict[str, Any]]:
        """
        获取即将到期的合同

        Args:
            days: 提前天数

        Returns:
            List[Dict[str, Any]]: 即将到期的合同列表
        """
        try:
            sql = f"""
            SELECT * FROM contracts
            WHERE end_date IS NOT NULL
            AND end_date <= date('now', '+{days} days')
            AND status = 'active'
            ORDER BY end_date ASC
            """

            results = self._db.execute_query(sql)
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"获取即将到期合同失败: {e}")
            raise DatabaseError(f"获取即将到期合同失败: {e}") from e


class OrderDAO(BaseDAO):
    """
    订单数据访问对象

    负责订单和订单明细的数据库操作
    """

    def __init__(self, database_manager: DatabaseManager):
        """初始化订单DAO"""
        super().__init__(database_manager, "orders")
        self._logger = logging.getLogger(__name__)

    def create_order_with_items(
        self, order_data: dict[str, Any], order_items: list[dict[str, Any]]
    ) -> int:
        """
        创建订单及其明细项

        Args:
            order_data: 订单主数据
            order_items: 订单明细项列表

        Returns:
            int: 新创建的订单ID
        """
        try:
            with self._db.transaction() as conn:
                # 插入订单主记录
                order_sql = """
                INSERT INTO orders (
                    order_number, customer_id, supplier_id, order_type,
                    total_amount, status, order_date, delivery_date,
                    notes, created_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                order_params = (
                    order_data.get("order_number"),
                    order_data.get("customer_id"),
                    order_data.get("supplier_id"),
                    order_data.get("order_type", "sales"),
                    order_data.get("total_amount"),
                    order_data.get("status", "pending"),
                    order_data.get("order_date", datetime.now()),
                    order_data.get("delivery_date"),
                    order_data.get("notes"),
                    order_data.get("created_by"),
                    order_data.get("created_at", datetime.now()),
                    order_data.get("updated_at", datetime.now()),
                )

                cursor = conn.execute(order_sql, order_params)
                order_id = cursor.lastrowid

                # 插入订单明细
                if order_items:
                    item_sql = """
                    INSERT INTO order_items (
                        order_id, product_id, product_name, specification,
                        quantity, unit_price, total_price, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """

                    for item in order_items:
                        item_params = (
                            order_id,
                            item.get("product_id"),
                            item.get("product_name"),
                            item.get("specification"),
                            item.get("quantity"),
                            item.get("unit_price"),
                            item.get("total_price"),
                            item.get("notes"),
                        )
                        conn.execute(item_sql, item_params)

                self._logger.info(f"成功创建订单，ID: {order_id}")
                return order_id

        except Exception as e:
            self._logger.error(f"创建订单失败: {e}")
            raise DatabaseError(f"创建订单失败: {e}") from e

    def get_order_with_items(self, order_id: int) -> dict[str, Any] | None:
        """
        获取订单及其明细项

        Args:
            order_id: 订单ID

        Returns:
            Optional[Dict[str, Any]]: 包含明细项的订单数据
        """
        try:
            # 获取订单主记录
            order = self.get_by_id(order_id)
            if not order:
                return None

            # 获取订单明细
            items_sql = "SELECT * FROM order_items WHERE order_id = ? ORDER BY id"
            items_result = self._db.execute_query(items_sql, (order_id,))
            order["items"] = [self._row_to_dict(row) for row in items_result]

            return order

        except Exception as e:
            self._logger.error(f"获取订单详情失败: {e}")
            raise DatabaseError(f"获取订单详情失败: {e}") from e

    def get_orders_by_customer(self, customer_id: int) -> list[dict[str, Any]]:
        """获取客户的所有订单"""
        return self.search({"customer_id": customer_id}, "order_date DESC")

    def get_orders_by_supplier(self, supplier_id: int) -> list[dict[str, Any]]:
        """获取供应商的所有订单"""
        return self.search({"supplier_id": supplier_id}, "order_date DESC")

    def get_orders_by_status(self, status: str) -> list[dict[str, Any]]:
        """根据状态获取订单列表"""
        return self.search({"status": status}, "order_date DESC")


class PaymentDAO(BaseDAO):
    """
    付款记录数据访问对象

    负责付款记录的数据库操作
    """

    def __init__(self, database_manager: DatabaseManager):
        """初始化付款DAO"""
        super().__init__(database_manager, "payments")
        self._logger = logging.getLogger(__name__)

    def get_payments_by_customer(self, customer_id: int) -> list[dict[str, Any]]:
        """获取客户的所有付款记录"""
        return self.search({"customer_id": customer_id}, "payment_date DESC")

    def get_payments_by_supplier(self, supplier_id: int) -> list[dict[str, Any]]:
        """获取供应商的所有付款记录"""
        return self.search({"supplier_id": supplier_id}, "payment_date DESC")

    def get_payments_by_order(self, order_id: int) -> list[dict[str, Any]]:
        """获取订单的所有付款记录"""
        return self.search({"order_id": order_id}, "payment_date DESC")

    def get_payment_statistics(self, start_date: str, end_date: str) -> dict[str, Any]:
        """
        获取付款统计信息

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            Dict[str, Any]: 付款统计数据
        """
        try:
            stats = {}

            # 总付款金额
            total_sql = """
            SELECT SUM(amount) FROM payments
            WHERE payment_date BETWEEN ? AND ?
            """
            result = self._db.execute_query(total_sql, (start_date, end_date))
            stats["total_amount"] = result[0][0] if result and result[0][0] else 0

            # 按付款类型统计
            type_sql = """
            SELECT payment_type, SUM(amount)
            FROM payments
            WHERE payment_date BETWEEN ? AND ?
            GROUP BY payment_type
            """
            type_results = self._db.execute_query(type_sql, (start_date, end_date))
            stats["by_type"] = {row[0]: row[1] for row in type_results}

            # 按付款方式统计
            method_sql = """
            SELECT payment_method, SUM(amount)
            FROM payments
            WHERE payment_date BETWEEN ? AND ?
            GROUP BY payment_method
            """
            method_results = self._db.execute_query(method_sql, (start_date, end_date))
            stats["by_method"] = {row[0]: row[1] for row in method_results}

            return stats

        except Exception as e:
            self._logger.error(f"获取付款统计失败: {e}")
            raise DatabaseError(f"获取付款统计失败: {e}") from e


class TaskDAO(BaseDAO):
    """
    任务数据访问对象

    负责任务管理的数据库操作
    """

    def __init__(self, database_manager: DatabaseManager):
        """初始化任务DAO"""
        super().__init__(database_manager, "tasks")
        self._logger = logging.getLogger(__name__)

    def get_tasks_by_customer(self, customer_id: int) -> list[dict[str, Any]]:
        """获取客户相关的所有任务"""
        return self.search({"customer_id": customer_id}, "created_at DESC")

    def get_tasks_by_supplier(self, supplier_id: int) -> list[dict[str, Any]]:
        """获取供应商相关的所有任务"""
        return self.search({"supplier_id": supplier_id}, "created_at DESC")

    def get_tasks_by_status(self, status: str) -> list[dict[str, Any]]:
        """根据状态获取任务列表"""
        return self.search({"status": status}, "due_date ASC")

    def get_overdue_tasks(self) -> list[dict[str, Any]]:
        """获取逾期任务"""
        try:
            sql = """
            SELECT * FROM tasks
            WHERE due_date < date('now')
            AND status != 'completed'
            ORDER BY due_date ASC
            """

            results = self._db.execute_query(sql)
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"获取逾期任务失败: {e}")
            raise DatabaseError(f"获取逾期任务失败: {e}") from e

    def get_upcoming_tasks(self, days: int = 7) -> list[dict[str, Any]]:
        """
        获取即将到期的任务

        Args:
            days: 提前天数

        Returns:
            List[Dict[str, Any]]: 即将到期的任务列表
        """
        try:
            sql = f"""
            SELECT * FROM tasks
            WHERE due_date BETWEEN date('now') AND date('now', '+{days} days')
            AND status != 'completed'
            ORDER BY due_date ASC
            """

            results = self._db.execute_query(sql)
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"获取即将到期任务失败: {e}")
            raise DatabaseError(f"获取即将到期任务失败: {e}") from e


class InteractionDAO(BaseDAO):
    """
    客户互动记录数据访问对象

    负责客户互动记录的数据库操作
    """

    def __init__(self, database_manager: DatabaseManager):
        """初始化互动记录DAO"""
        super().__init__(database_manager, "customer_interactions")
        self._logger = logging.getLogger(__name__)

    def get_interactions_by_customer(self, customer_id: int) -> list[dict[str, Any]]:
        """获取客户的所有互动记录"""
        return self.search({"customer_id": customer_id}, "interaction_date DESC")

    def get_interactions_by_type(self, interaction_type: str) -> list[dict[str, Any]]:
        """根据类型获取互动记录"""
        return self.search(
            {"interaction_type": interaction_type}, "interaction_date DESC"
        )

    def get_recent_interactions(self, limit: int = 50) -> list[dict[str, Any]]:
        """获取最近的互动记录"""
        return self.search(order_by="interaction_date DESC", limit=limit)

    def get_follow_up_required(self) -> list[dict[str, Any]]:
        """获取需要跟进的互动记录"""
        try:
            sql = """
            SELECT * FROM customer_interactions
            WHERE follow_up_required = 1
            AND (follow_up_date IS NULL OR follow_up_date <= date('now'))
            ORDER BY interaction_date ASC
            """

            results = self._db.execute_query(sql)
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self._logger.error(f"获取需要跟进的互动记录失败: {e}")
            raise DatabaseError(f"获取需要跟进的互动记录失败: {e}") from e


class AfterSalesDAO(BaseDAO):
    """
    售后服务记录数据访问对象

    负责售后服务记录的数据库操作
    """

    def __init__(self, database_manager: DatabaseManager):
        """初始化售后服务DAO"""
        super().__init__(database_manager, "after_sales_records")
        self._logger = logging.getLogger(__name__)

    def get_records_by_customer(self, customer_id: int) -> list[dict[str, Any]]:
        """获取客户的所有售后记录"""
        return self.search({"customer_id": customer_id}, "reported_date DESC")

    def get_records_by_product(self, product_id: int) -> list[dict[str, Any]]:
        """获取产品的所有售后记录"""
        return self.search({"product_id": product_id}, "reported_date DESC")

    def get_records_by_status(self, status: str) -> list[dict[str, Any]]:
        """根据状态获取售后记录"""
        return self.search({"status": status}, "reported_date DESC")

    def get_records_by_issue_type(self, issue_type: str) -> list[dict[str, Any]]:
        """根据问题类型获取售后记录"""
        return self.search({"issue_type": issue_type}, "reported_date DESC")

    def get_after_sales_statistics(self) -> dict[str, Any]:
        """
        获取售后服务统计信息

        Returns:
            Dict[str, Any]: 售后统计数据
        """
        try:
            stats = {}

            # 总售后记录数
            total_sql = "SELECT COUNT(*) FROM after_sales_records"
            result = self._db.execute_query(total_sql)
            stats["total_records"] = result[0][0] if result else 0

            # 按问题类型统计
            type_sql = """
            SELECT issue_type, COUNT(*)
            FROM after_sales_records
            GROUP BY issue_type
            """
            type_results = self._db.execute_query(type_sql)
            stats["by_issue_type"] = {row[0]: row[1] for row in type_results}

            # 按状态统计
            status_sql = """
            SELECT status, COUNT(*)
            FROM after_sales_records
            GROUP BY status
            """
            status_results = self._db.execute_query(status_sql)
            stats["by_status"] = {row[0]: row[1] for row in status_results}

            # 按优先级统计
            priority_sql = """
            SELECT priority, COUNT(*)
            FROM after_sales_records
            GROUP BY priority
            """
            priority_results = self._db.execute_query(priority_sql)
            stats["by_priority"] = {row[0]: row[1] for row in priority_results}

            # 平均满意度评分
            rating_sql = """
            SELECT AVG(satisfaction_rating)
            FROM after_sales_records
            WHERE satisfaction_rating IS NOT NULL
            """
            rating_result = self._db.execute_query(rating_sql)
            stats["avg_satisfaction"] = (
                rating_result[0][0] if rating_result and rating_result[0][0] else 0
            )

            return stats

        except Exception as e:
            self._logger.error(f"获取售后统计失败: {e}")
            raise DatabaseError(f"获取售后统计失败: {e}") from e


class BusinessDAO:
    """
    业务数据访问对象聚合类

    提供统一的业务数据访问接口，聚合所有业务相关的DAO
    """

    def __init__(self, database_manager: DatabaseManager):
        """
        初始化业务DAO

        Args:
            database_manager: 数据库管理器
        """
        self.quotes = QuoteDAO(database_manager)
        self.contracts = ContractDAO(database_manager)
        self.orders = OrderDAO(database_manager)
        self.payments = PaymentDAO(database_manager)
        self.tasks = TaskDAO(database_manager)
        self.interactions = InteractionDAO(database_manager)
        self.after_sales = AfterSalesDAO(database_manager)

        self._logger = logging.getLogger(__name__)

    def get_customer_business_summary(self, customer_id: int) -> dict[str, Any]:
        """
        获取客户业务摘要

        Args:
            customer_id: 客户ID

        Returns:
            Dict[str, Any]: 客户业务摘要数据
        """
        try:
            summary = {
                "customer_id": customer_id,
                "quotes": self.quotes.get_quotes_by_customer(customer_id),
                "contracts": self.contracts.get_contracts_by_customer(customer_id),
                "orders": self.orders.get_orders_by_customer(customer_id),
                "payments": self.payments.get_payments_by_customer(customer_id),
                "tasks": self.tasks.get_tasks_by_customer(customer_id),
                "interactions": self.interactions.get_interactions_by_customer(
                    customer_id
                ),
                "after_sales": self.after_sales.get_records_by_customer(customer_id),
            }

            # 计算统计数据
            summary["statistics"] = {
                "total_quotes": len(summary["quotes"]),
                "total_contracts": len(summary["contracts"]),
                "total_orders": len(summary["orders"]),
                "total_payments": sum(p.get("amount", 0) for p in summary["payments"]),
                "pending_tasks": len(
                    [t for t in summary["tasks"] if t.get("status") != "completed"]
                ),
                "recent_interactions": len(summary["interactions"][:10]),
                "open_after_sales": len(
                    [a for a in summary["after_sales"] if a.get("status") == "open"]
                ),
            }

            return summary

        except Exception as e:
            self._logger.error(f"获取客户业务摘要失败: {e}")
            raise DatabaseError(f"获取客户业务摘要失败: {e}") from e

    def get_supplier_business_summary(self, supplier_id: int) -> dict[str, Any]:
        """
        获取供应商业务摘要

        Args:
            supplier_id: 供应商ID

        Returns:
            Dict[str, Any]: 供应商业务摘要数据
        """
        try:
            summary = {
                "supplier_id": supplier_id,
                "contracts": self.contracts.get_contracts_by_supplier(supplier_id),
                "orders": self.orders.get_orders_by_supplier(supplier_id),
                "payments": self.payments.get_payments_by_supplier(supplier_id),
                "tasks": self.tasks.get_tasks_by_supplier(supplier_id),
            }

            # 计算统计数据
            summary["statistics"] = {
                "total_contracts": len(summary["contracts"]),
                "total_orders": len(summary["orders"]),
                "total_payments": sum(p.get("amount", 0) for p in summary["payments"]),
                "pending_tasks": len(
                    [t for t in summary["tasks"] if t.get("status") != "completed"]
                ),
            }

            return summary

        except Exception as e:
            self._logger.error(f"获取供应商业务摘要失败: {e}")
            raise DatabaseError(f"获取供应商业务摘要失败: {e}") from e
