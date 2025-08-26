"""增强版业务流程数据访问对象.

实现业务流程相关的数据访问操作,包括报价、合同、售后工单等.
集成transfunctions进行数据验证和格式化.

主要功能:
- 报价管理CRUD操作
- 合同管理CRUD操作
- 售后工单管理CRUD操作
- 业务数据验证和格式化
- 业务流程统计分析
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import TYPE_CHECKING, Any

from minicrm.core.exceptions import DatabaseError
from minicrm.core.sql_safety import SafeSQLBuilder
from minicrm.data.dao.enhanced_base_dao import EnhancedBaseDAO
from transfunctions import (
    format_currency,
)


if TYPE_CHECKING:
    from minicrm.data.database_manager_enhanced import EnhancedDatabaseManager


class EnhancedQuoteDAO(EnhancedBaseDAO):
    """增强版报价数据访问对象.

    提供完整的报价数据访问功能,包括CRUD操作、报价计算、历史比对等.
    """

    def __init__(self, db_manager: EnhancedDatabaseManager):
        """初始化报价DAO.

        Args:
            db_manager: 增强版数据库管理器
        """
        super().__init__(db_manager, "quotes")
        self._logger = logging.getLogger(__name__)
        self._sql_builder = SafeSQLBuilder("quotes")

    def _get_validation_config(self) -> dict[str, Any]:
        """获取报价数据验证配置."""
        return {
            "required_fields": [
                "customer_id",
                "quote_number",
                "quote_date",
                "valid_until",
            ],
            "optional_fields": ["supplier_id", "total_amount", "status", "notes"],
            "field_types": {
                "customer_id": int,
                "supplier_id": int,
                "quote_number": str,
                "quote_date": str,
                "valid_until": str,
                "total_amount": float,
                "status": str,
                "notes": str,
            },
            "field_constraints": {
                "quote_number": {"max_length": 50},
                "status": {
                    "choices": ["draft", "sent", "accepted", "rejected", "expired"]
                },
                "total_amount": {"min_value": 0},
            },
        }

    def _get_table_schema(self) -> dict[str, str]:
        """获取报价表结构定义."""
        return {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "customer_id": "INTEGER",
            "supplier_id": "INTEGER",
            "quote_number": "TEXT NOT NULL UNIQUE",
            "quote_date": "TEXT NOT NULL",
            "valid_until": "TEXT NOT NULL",
            "total_amount": "REAL DEFAULT 0",
            "status": 'TEXT DEFAULT "draft"',
            "notes": "TEXT",
            "created_at": "TEXT NOT NULL",
            "updated_at": "TEXT NOT NULL",
            "deleted_at": "TEXT",
        }

    def create_quote(self, quote_data: dict[str, Any]) -> int:
        """创建新报价.

        Args:
            quote_data: 报价数据

        Returns:
            int: 新报价ID
        """
        try:
            if not quote_data.get("quote_number"):
                quote_data["quote_number"] = self._generate_quote_number()

            quote_id = self.create(quote_data)
        except Exception as e:
            error_msg = f"创建报价失败: {e}"
            raise DatabaseError(error_msg) from e
        else:
            self._logger.info(
                "成功创建报价: %s, ID: %s", quote_data.get("quote_number"), quote_id
            )
            return quote_id

    def _generate_quote_number(self) -> str:
        """生成报价编号.

        格式: Q + YYYYMMDD + 3位序号 (例: Q20241219001)

        Returns:
            str: 生成的报价编号
        """
        today = datetime.now(timezone.utc).strftime("%Y%m%d")

        # 使用SafeSQLBuilder构建安全的COUNT查询
        # 由于需要LIKE查询, 使用基础方法构建
        sql, params = self._sql_builder.build_count(include_deleted=False)

        # 手动添加LIKE条件, 但使用参数化查询确保安全
        sql = sql.replace(
            "WHERE deleted_at IS NULL",
            "WHERE quote_number LIKE ? AND deleted_at IS NULL",
        )
        params = [f"Q{today}%", *params]

        results = self._db_manager.execute_query(sql, tuple(params))
        count = results[0]["count"] if results else 0

        return f"Q{today}{count + 1:03d}"

    def get_customer_quotes(self, customer_id: int) -> list[dict[str, Any]]:
        """获取客户的所有报价.

        Args:
            customer_id: 客户ID

        Returns:
            list[dict[str, Any]]: 客户报价列表, 按报价日期倒序排列
        """
        return self.search(
            conditions={"customer_id": customer_id}, order_by="quote_date DESC"
        )

    def get_quote_statistics(self) -> dict[str, Any]:
        """获取报价统计信息."""
        try:
            # 总报价数
            total_quotes = self.count()

            # 按状态统计
            status_stats = {}
            for status in ["draft", "sent", "accepted", "rejected", "expired"]:
                status_stats[status] = self.count({"status": status})

            # 本月报价总额
            current_month = datetime.now(timezone.utc).strftime("%Y-%m")

            # 构建安全的SUM查询 - 使用基础查询方法
            # 由于需要特殊的聚合查询, 暂时使用验证过的表名
            # 注意: validated_table已通过SafeSQLBuilder验证, 参数使用?占位符
            validated_table = self._sql_builder.table_name
            sql = f"""
            SELECT SUM(total_amount) as total_amount
            FROM {validated_table}
            WHERE deleted_at IS NULL AND quote_date LIKE ?
            """  # noqa: S608
            amount_result = self._db_manager.execute_query(sql, (f"{current_month}%",))

            monthly_amount = 0
            if amount_result and amount_result[0]["total_amount"]:
                monthly_amount = amount_result[0]["total_amount"]

            return {
                "total_quotes": total_quotes,
                "status_statistics": status_stats,
                "monthly_quote_amount": format_currency(monthly_amount),
            }

        except Exception as e:
            error_msg = f"获取报价统计信息失败: {e}"
            raise DatabaseError(error_msg) from e


class EnhancedContractDAO(EnhancedBaseDAO):
    """增强版合同数据访问对象."""

    def __init__(self, db_manager: EnhancedDatabaseManager):
        """初始化合同DAO."""
        super().__init__(db_manager, "contracts")
        self._logger = logging.getLogger(__name__)
        self._sql_builder = SafeSQLBuilder("contracts")

    def _get_validation_config(self) -> dict[str, Any]:
        """获取合同数据验证配置."""
        return {
            "required_fields": [
                "customer_id",
                "contract_number",
                "contract_date",
                "contract_amount",
            ],
            "optional_fields": [
                "supplier_id",
                "start_date",
                "end_date",
                "status",
                "terms",
            ],
            "field_types": {
                "customer_id": int,
                "supplier_id": int,
                "contract_number": str,
                "contract_date": str,
                "start_date": str,
                "end_date": str,
                "contract_amount": float,
                "status": str,
                "terms": str,
            },
        }

    def _get_table_schema(self) -> dict[str, str]:
        """获取合同表结构定义."""
        return {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "customer_id": "INTEGER",
            "supplier_id": "INTEGER",
            "contract_number": "TEXT NOT NULL UNIQUE",
            "contract_date": "TEXT NOT NULL",
            "start_date": "TEXT",
            "end_date": "TEXT",
            "contract_amount": "REAL NOT NULL",
            "status": 'TEXT DEFAULT "draft"',
            "terms": "TEXT",
            "created_at": "TEXT NOT NULL",
            "updated_at": "TEXT NOT NULL",
            "deleted_at": "TEXT",
        }


class EnhancedServiceTicketDAO(EnhancedBaseDAO):
    """增强版售后工单数据访问对象."""

    def __init__(self, db_manager: EnhancedDatabaseManager):
        """初始化售后工单DAO."""
        super().__init__(db_manager, "service_tickets")
        self._logger = logging.getLogger(__name__)
        self._sql_builder = SafeSQLBuilder("service_tickets")

    def _get_validation_config(self) -> dict[str, Any]:
        """获取售后工单数据验证配置."""
        return {
            "required_fields": [
                "customer_id",
                "ticket_number",
                "issue_type",
                "description",
            ],
            "optional_fields": [
                "supplier_id",
                "priority",
                "status",
                "assigned_to",
                "resolution",
            ],
            "field_types": {
                "customer_id": int,
                "supplier_id": int,
                "ticket_number": str,
                "issue_type": str,
                "description": str,
                "priority": str,
                "status": str,
                "assigned_to": str,
                "resolution": str,
            },
        }

    def _get_table_schema(self) -> dict[str, str]:
        """获取售后工单表结构定义."""
        return {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "customer_id": "INTEGER",
            "supplier_id": "INTEGER",
            "ticket_number": "TEXT NOT NULL UNIQUE",
            "issue_type": "TEXT NOT NULL",
            "description": "TEXT NOT NULL",
            "priority": 'TEXT DEFAULT "medium"',
            "status": 'TEXT DEFAULT "open"',
            "assigned_to": "TEXT",
            "resolution": "TEXT",
            "created_at": "TEXT NOT NULL",
            "updated_at": "TEXT NOT NULL",
            "deleted_at": "TEXT",
        }
