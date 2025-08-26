"""SQL安全验证器.

提供SQL注入防护功能, 包括表名、列名验证和安全的SQL语句构建.
确保所有数据库操作都符合安全标准.

主要功能:
- 表名和列名白名单验证
- 安全的WHERE子句构建
- SQL注入攻击防护
- 参数化查询支持
"""

from __future__ import annotations

import re
from typing import Any, ClassVar

from minicrm.core.exceptions import ValidationError


class SQLSafetyValidator:
    """SQL安全验证器.

    提供完整的SQL安全验证功能, 防止SQL注入攻击.
    """

    # 允许的表名白名单
    ALLOWED_TABLES: ClassVar[set[str]] = {
        "customers",
        "customer_types",
        "suppliers",
        "supplier_types",
        "quotes",
        "contracts",
        "service_tickets",
        "interactions",
        "tasks",
        "quote_items",
        "contract_items",
        "payments",
        "documents",
    }

    # 通用列名 - 所有表都有的字段
    COMMON_COLUMNS: ClassVar[set[str]] = {
        "id",
        "created_at",
        "updated_at",
        "deleted_at",
    }

    # 各表特定的允许列名
    TABLE_SPECIFIC_COLUMNS: ClassVar[dict[str, set[str]]] = {
        "customers": {
            "name",
            "phone",
            "email",
            "company",
            "address",
            "customer_type_id",
            "level",
            "credit_limit",
        },
        "customer_types": {"name", "description", "color_code"},
        "suppliers": {
            "name",
            "contact_person",
            "phone",
            "email",
            "company",
            "address",
            "supplier_type_id",
            "level",
            "business_license",
        },
        "supplier_types": {"name", "description", "color_code"},
        "quotes": {
            "customer_id",
            "supplier_id",
            "quote_number",
            "quote_date",
            "valid_until",
            "total_amount",
            "status",
            "notes",
        },
        "contracts": {
            "customer_id",
            "supplier_id",
            "contract_number",
            "contract_date",
            "start_date",
            "end_date",
            "contract_amount",
            "status",
            "terms",
        },
        "service_tickets": {
            "customer_id",
            "supplier_id",
            "ticket_number",
            "issue_type",
            "description",
            "priority",
            "status",
            "assigned_to",
            "resolution",
        },
    }

    @classmethod
    def validate_table_name(cls, table_name: str) -> str:
        """验证表名安全性.

        Args:
            table_name: 要验证的表名

        Returns:
            str: 验证通过的表名

        Raises:
            ValidationError: 表名不在允许列表中
        """
        if not table_name or not isinstance(table_name, str):
            msg = "表名不能为空"
            raise ValidationError(msg)

        # 检查表名格式 - 只允许字母、数字、下划线
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
            msg = f"无效的表名格式: {table_name}"
            raise ValidationError(msg)

        # 检查表名是否在白名单中
        if table_name not in cls.ALLOWED_TABLES:
            msg = f"不允许的表名: {table_name}"
            raise ValidationError(msg)

        return table_name

    @classmethod
    def validate_column_name(
        cls, column_name: str, table_name: str | None = None
    ) -> str:
        """验证列名安全性.

        Args:
            column_name: 要验证的列名
            table_name: 表名(可选, 用于特定表的列名验证)

        Returns:
            str: 验证通过的列名

        Raises:
            ValidationError: 列名不安全或不允许
        """
        if not column_name or not isinstance(column_name, str):
            msg = "列名不能为空"
            raise ValidationError(msg)

        # 检查列名格式 - 只允许字母数字下划线
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", column_name):
            msg = f"无效的列名格式: {column_name}"
            raise ValidationError(msg)

        # 检查是否为通用列名
        if column_name in cls.COMMON_COLUMNS:
            return column_name

        # 如果指定了表名 检查表特定的列名
        if table_name:
            cls.validate_table_name(table_name)  # 先验证表名
            allowed_columns = cls.TABLE_SPECIFIC_COLUMNS.get(table_name, set())
            if column_name not in allowed_columns:
                msg = f"表 {table_name} 不允许的列名: {column_name}"
                raise ValidationError(msg)

        return column_name

    @classmethod
    def get_allowed_columns(cls, table_name: str) -> set[str]:
        """获取指定表的所有允许列名.

        Args:
            table_name: 表名

        Returns:
            set[str]: 允许的列名集合
        """
        cls.validate_table_name(table_name)

        # 合并通用列名和表特定列名
        allowed_columns = cls.COMMON_COLUMNS.copy()
        table_columns = cls.TABLE_SPECIFIC_COLUMNS.get(table_name, set())
        allowed_columns.update(table_columns)

        return allowed_columns

    @classmethod
    def build_safe_where_clause(
        cls, conditions: dict[str, Any], table_name: str | None = None
    ) -> tuple[str, list[Any]]:
        """安全构建WHERE子句.

        Args:
            conditions: 查询条件字典
            table_name: 表名(用于列名验证)

        Returns:
            tuple[str, list[Any]]: WHERE子句和参数列表

        Raises:
            ValidationError: 条件中包含不安全的列名
        """
        if not conditions:
            return "", []

        where_parts: list[str] = []
        params: list[Any] = []

        for column, value in conditions.items():
            # 验证列名安全性
            cls.validate_column_name(column, table_name)

            # 处理不同类型的条件值
            if value is None:
                where_parts.append(f"{column} IS NULL")
            elif isinstance(value, (list, tuple)):
                # IN 查询
                placeholders = ",".join(["?" for _ in value])
                where_parts.append(f"{column} IN ({placeholders})")
                params.extend(value)
            else:
                # 等值查询
                where_parts.append(f"{column} = ?")
                params.append(value)

        where_clause = " AND ".join(where_parts)
        return where_clause, params

    @classmethod
    def build_safe_like_conditions(
        cls, search_columns: list[str], search_value: str, table_name: str | None = None
    ) -> tuple[str, list[str]]:
        """安全构建LIKE查询条件.

        Args:
            search_columns: 要搜索的列名列表
            search_value: 搜索值
            table_name: 表名(用于列名验证)

        Returns:
            tuple[str, list[str]]: LIKE条件子句和参数列表

        Raises:
            ValidationError: 搜索列名不安全
        """
        if not search_columns or not search_value:
            return "", []

        # 验证所有搜索列名
        for column in search_columns:
            cls.validate_column_name(column, table_name)

        # 转义搜索值中的特殊字符
        escaped_value = cls._escape_like_value(search_value)
        like_value = f"%{escaped_value}%"

        # 构建LIKE条件
        like_conditions = [f"{column} LIKE ?" for column in search_columns]
        like_clause = f"({' OR '.join(like_conditions)})"

        # 每个LIKE条件都需要相同的参数
        params = [like_value for _ in search_columns]

        return like_clause, params

    @classmethod
    def _escape_like_value(cls, value: str) -> str:
        """转义LIKE查询中的特殊字符.

        Args:
            value: 要转义的值

        Returns:
            str: 转义后的值
        """
        # 转义LIKE查询中的特殊字符
        value = value.replace("\\", "\\\\")  # 先转义反斜杠
        value = value.replace("%", "\\%")  # 转义百分号
        return value.replace("_", "\\_")  # 转义下划线

    @classmethod
    def build_safe_order_by(cls, order_by: str, table_name: str | None = None) -> str:
        """安全构建ORDER BY子句.

        Args:
            order_by: 排序字段和方向, 如 "name ASC" 或 "created_at DESC"
            table_name: 表名(用于列名验证)

        Returns:
            str: 安全的ORDER BY子句

        Raises:
            ValidationError: 排序字段不安全
        """
        if not order_by:
            return ""

        # 解析排序字段和方向
        parts = order_by.strip().split()
        if len(parts) == 1:
            column = parts[0]
            direction = "ASC"
        elif len(parts) == 2:
            column, direction = parts
        else:
            msg = f"无效的ORDER BY格式: {order_by}"
            raise ValidationError(msg)

        # 验证列名
        cls.validate_column_name(column, table_name)

        # 验证排序方向
        direction = direction.upper()
        if direction not in ("ASC", "DESC"):
            msg = f"无效的排序方向: {direction}"
            raise ValidationError(msg)

        return f"{column} {direction}"

    @classmethod
    def validate_limit_offset(
        cls, limit: int | None = None, offset: int | None = None
    ) -> tuple[int, int]:
        """验证LIMIT和OFFSET参数.

        Args:
            limit: 限制数量
            offset: 偏移量

        Returns:
            验证后的limit和offset元组

        Raises:
            ValidationError: 参数值无效
        """
        if limit is not None and (not isinstance(limit, int) or limit < 0):
            msg = "LIMIT必须是非负整数"
            raise ValidationError(msg)

        if limit is not None and limit > 10000:  # 防止过大的查询
            msg = "LIMIT不能超过10000"
            raise ValidationError(msg)

        if offset is not None and (not isinstance(offset, int) or offset < 0):
            msg = "OFFSET必须是非负整数"
            raise ValidationError(msg)

        return limit or 0, offset or 0


class SafeSQLBuilder:
    """安全SQL构建器.

    提供安全的SQL语句构建功能, 确保所有构建的SQL都经过安全验证.
    """

    def __init__(self, table_name: str):
        """初始化SQL构建器.

        Args:
            table_name: 目标表名
        """
        self.table_name = SQLSafetyValidator.validate_table_name(table_name)
        self.validator = SQLSafetyValidator

    def build_select(
        self,
        columns: list[str] | None = None,
        conditions: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        include_deleted: bool = False,
    ) -> tuple[str, list[Any]]:
        """构建安全的SELECT语句.

        Args:
            columns: 要查询的列名列表, None表示查询所有列
            conditions: 查询条件
            order_by: 排序字段
            limit: 限制数量
            offset: 偏移量
            include_deleted: 是否包含已删除记录

        Returns:
            SQL语句和参数列表的元组
        """
        # 构建SELECT子句
        if columns:
            # 验证所有列名
            for col in columns:
                self.validator.validate_column_name(col, self.table_name)
            select_clause = ", ".join(columns)
        else:
            select_clause = "*"

        # 使用已验证的表名构建SQL - table_name已通过SQLSafetyValidator.validate_table_name验证
        sql = f"SELECT {select_clause} FROM {self.table_name}"  # noqa: S608
        params = []

        # 构建WHERE子句
        where_parts = []

        # 添加删除状态过滤
        if not include_deleted:
            where_parts.append("deleted_at IS NULL")

        # 添加其他条件
        if conditions:
            where_clause, where_params = self.validator.build_safe_where_clause(
                conditions, self.table_name
            )
            if where_clause:
                where_parts.append(where_clause)
                params.extend(where_params)

        if where_parts:
            sql += " WHERE " + " AND ".join(where_parts)

        # 添加ORDER BY
        if order_by:
            safe_order_by = self.validator.build_safe_order_by(
                order_by, self.table_name
            )
            sql += f" ORDER BY {safe_order_by}"

        # 添加LIMIT和OFFSET
        if limit is not None or offset is not None:
            validated_limit, validated_offset = self.validator.validate_limit_offset(
                limit, offset
            )
            if validated_limit > 0:
                sql += f" LIMIT {validated_limit}"
                if validated_offset > 0:
                    sql += f" OFFSET {validated_offset}"

        return sql, params

    def build_count(
        self, conditions: dict[str, Any] | None = None, include_deleted: bool = False
    ) -> tuple[str, list[Any]]:
        """构建安全的COUNT语句.

        Args:
            conditions: 查询条件
            include_deleted: 是否包含已删除记录

        Returns:
            SQL语句和参数列表的元组
        """
        # 使用已验证的表名构建SQL - table_name已通过SQLSafetyValidator.validate_table_name验证
        sql = f"SELECT COUNT(*) as count FROM {self.table_name}"  # noqa: S608
        params = []

        # 构建WHERE子句
        where_parts = []

        # 添加删除状态过滤
        if not include_deleted:
            where_parts.append("deleted_at IS NULL")

        # 添加其他条件
        if conditions:
            where_clause, where_params = self.validator.build_safe_where_clause(
                conditions, self.table_name
            )
            if where_clause:
                where_parts.append(where_clause)
                params.extend(where_params)

        if where_parts:
            sql += " WHERE " + " AND ".join(where_parts)

        return sql, params

    def build_search_with_like(
        self,
        search_columns: list[str],
        search_value: str,
        additional_conditions: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        include_deleted: bool = False,
    ) -> tuple[str, list[Any]]:
        """构建带LIKE搜索的安全SELECT语句.

        Args:
            search_columns: 要搜索的列名列表
            search_value: 搜索值
            additional_conditions: 额外的查询条件
            order_by: 排序字段
            limit: 限制数量
            offset: 偏移量
            include_deleted: 是否包含已删除记录

        Returns:
            SQL语句和参数列表的元组
        """
        # 使用已验证的表名构建SQL - table_name已通过SQLSafetyValidator.validate_table_name验证
        sql = f"SELECT * FROM {self.table_name}"  # noqa: S608
        params = []

        # 构建WHERE子句
        where_parts = []

        # 添加删除状态过滤
        if not include_deleted:
            where_parts.append("deleted_at IS NULL")

        # 添加LIKE搜索条件
        if search_columns and search_value:
            like_clause, like_params = self.validator.build_safe_like_conditions(
                search_columns, search_value, self.table_name
            )
            if like_clause:
                where_parts.append(like_clause)
                params.extend(like_params)

        # 添加其他条件
        if additional_conditions:
            where_clause, where_params = self.validator.build_safe_where_clause(
                additional_conditions, self.table_name
            )
            if where_clause:
                where_parts.append(where_clause)
                params.extend(where_params)

        if where_parts:
            sql += " WHERE " + " AND ".join(where_parts)

        # 添加ORDER BY
        if order_by:
            safe_order_by = self.validator.build_safe_order_by(
                order_by, self.table_name
            )
            sql += f" ORDER BY {safe_order_by}"

        # 添加LIMIT和OFFSET
        if limit is not None or offset is not None:
            validated_limit, validated_offset = self.validator.validate_limit_offset(
                limit, offset
            )
            if validated_limit > 0:
                sql += f" LIMIT {validated_limit}"
                if validated_offset > 0:
                    sql += f" OFFSET {validated_offset}"

        return sql, params
