"""
Transfunctions - 查询构建器

提供动态SQL查询构建功能，支持复杂的搜索条件和查询优化。
"""

from enum import Enum
from typing import Any


class ComparisonOperator(Enum):
    """比较操作符枚举"""

    EQUAL = "="
    NOT_EQUAL = "!="
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="
    LESS_THAN = "<"
    LESS_EQUAL = "<="
    LIKE = "LIKE"
    NOT_LIKE = "NOT LIKE"
    IN = "IN"
    NOT_IN = "NOT IN"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"
    BETWEEN = "BETWEEN"


class LogicalOperator(Enum):
    """逻辑操作符枚举"""

    AND = "AND"
    OR = "OR"


class QueryBuilder:
    """
    SQL查询构建器

    支持动态构建复杂的SQL查询语句，包括：
    - 多表连接
    - 复杂WHERE条件
    - 排序和分页
    - 聚合查询
    """

    def __init__(self, table_name: str):
        """
        初始化查询构建器

        Args:
            table_name: 主表名
        """
        self.table_name = table_name
        self.select_fields: list[str] = ["*"]
        self.joins: list[str] = []
        self.where_conditions: list[str] = []
        self.where_params: list[Any] = []
        self.group_by_fields: list[str] = []
        self.having_conditions: list[str] = []
        self.having_params: list[Any] = []
        self.order_by_fields: list[str] = []
        self.limit_value: int | None = None
        self.offset_value: int | None = None

    def select(self, *fields: str) -> "QueryBuilder":
        """
        设置SELECT字段

        Args:
            *fields: 字段名列表

        Returns:
            QueryBuilder: 查询构建器实例（支持链式调用）
        """
        if fields:
            self.select_fields = list(fields)
        return self

    def join(
        self, table: str, on_condition: str, join_type: str = "INNER"
    ) -> "QueryBuilder":
        """
        添加表连接

        Args:
            table: 要连接的表名
            on_condition: 连接条件
            join_type: 连接类型（INNER, LEFT, RIGHT, FULL）

        Returns:
            QueryBuilder: 查询构建器实例
        """
        self.joins.append(f"{join_type} JOIN {table} ON {on_condition}")
        return self

    def where(
        self,
        field: str,
        operator: ComparisonOperator | str,
        value: Any = None,
        logical_op: LogicalOperator = LogicalOperator.AND,
    ) -> "QueryBuilder":
        """
        添加WHERE条件

        Args:
            field: 字段名
            operator: 比较操作符
            value: 比较值
            logical_op: 逻辑操作符（与前一个条件的关系）

        Returns:
            QueryBuilder: 查询构建器实例
        """
        if isinstance(operator, str):
            operator = ComparisonOperator(operator)

        # 构建条件字符串
        if operator in [ComparisonOperator.IS_NULL, ComparisonOperator.IS_NOT_NULL]:
            condition = f"{field} {operator.value}"
        elif operator == ComparisonOperator.BETWEEN:
            if not isinstance(value, list | tuple) or len(value) != 2:
                raise ValueError("BETWEEN操作符需要包含两个值的列表或元组")
            condition = f"{field} BETWEEN ? AND ?"
            self.where_params.extend(value)
        elif operator in [ComparisonOperator.IN, ComparisonOperator.NOT_IN]:
            if not isinstance(value, list | tuple):
                raise ValueError(f"{operator.value}操作符需要列表或元组值")
            placeholders = ", ".join(["?" for _ in value])
            condition = f"{field} {operator.value} ({placeholders})"
            self.where_params.extend(value)
        else:
            condition = f"{field} {operator.value} ?"
            self.where_params.append(value)

        # 添加逻辑操作符
        if self.where_conditions:
            condition = f"{logical_op.value} {condition}"

        self.where_conditions.append(condition)
        return self

    def where_like(
        self,
        field: str,
        pattern: str,
        logical_op: LogicalOperator = LogicalOperator.AND,
    ) -> "QueryBuilder":
        """
        添加LIKE条件的便捷方法

        Args:
            field: 字段名
            pattern: 匹配模式
            logical_op: 逻辑操作符

        Returns:
            QueryBuilder: 查询构建器实例
        """
        return self.where(field, ComparisonOperator.LIKE, pattern, logical_op)

    def where_in(
        self,
        field: str,
        values: list[Any],
        logical_op: LogicalOperator = LogicalOperator.AND,
    ) -> "QueryBuilder":
        """
        添加IN条件的便捷方法

        Args:
            field: 字段名
            values: 值列表
            logical_op: 逻辑操作符

        Returns:
            QueryBuilder: 查询构建器实例
        """
        return self.where(field, ComparisonOperator.IN, values, logical_op)

    def group_by(self, *fields: str) -> "QueryBuilder":
        """
        设置GROUP BY字段

        Args:
            *fields: 分组字段列表

        Returns:
            QueryBuilder: 查询构建器实例
        """
        self.group_by_fields.extend(fields)
        return self

    def having(
        self,
        condition: str,
        *params: Any,
        logical_op: LogicalOperator = LogicalOperator.AND,
    ) -> "QueryBuilder":
        """
        添加HAVING条件

        Args:
            condition: HAVING条件字符串
            *params: 条件参数
            logical_op: 逻辑操作符

        Returns:
            QueryBuilder: 查询构建器实例
        """
        if self.having_conditions:
            condition = f"{logical_op.value} {condition}"

        self.having_conditions.append(condition)
        self.having_params.extend(params)
        return self

    def order_by(self, field: str, direction: str = "ASC") -> "QueryBuilder":
        """
        添加排序字段

        Args:
            field: 排序字段
            direction: 排序方向（ASC或DESC）

        Returns:
            QueryBuilder: 查询构建器实例
        """
        direction = direction.upper()
        if direction not in ["ASC", "DESC"]:
            raise ValueError("排序方向必须是ASC或DESC")

        self.order_by_fields.append(f"{field} {direction}")
        return self

    def limit(self, count: int) -> "QueryBuilder":
        """
        设置LIMIT

        Args:
            count: 限制数量

        Returns:
            QueryBuilder: 查询构建器实例
        """
        self.limit_value = count
        return self

    def offset(self, count: int) -> "QueryBuilder":
        """
        设置OFFSET

        Args:
            count: 偏移量

        Returns:
            QueryBuilder: 查询构建器实例
        """
        self.offset_value = count
        return self

    def paginate(self, page: int, page_size: int) -> "QueryBuilder":
        """
        设置分页

        Args:
            page: 页码（从1开始）
            page_size: 每页大小

        Returns:
            QueryBuilder: 查询构建器实例
        """
        offset = (page - 1) * page_size
        return self.limit(page_size).offset(offset)

    def build(self) -> tuple[str, list[Any]]:
        """
        构建SQL查询语句

        Returns:
            Tuple[str, List[Any]]: (SQL语句, 参数列表)
        """
        # 构建SELECT部分
        sql_parts = [f"SELECT {', '.join(self.select_fields)}"]
        sql_parts.append(f"FROM {self.table_name}")

        # 添加JOIN
        if self.joins:
            sql_parts.extend(self.joins)

        # 添加WHERE
        params = []
        if self.where_conditions:
            sql_parts.append(f"WHERE {' '.join(self.where_conditions)}")
            params.extend(self.where_params)

        # 添加GROUP BY
        if self.group_by_fields:
            sql_parts.append(f"GROUP BY {', '.join(self.group_by_fields)}")

        # 添加HAVING
        if self.having_conditions:
            sql_parts.append(f"HAVING {' '.join(self.having_conditions)}")
            params.extend(self.having_params)

        # 添加ORDER BY
        if self.order_by_fields:
            sql_parts.append(f"ORDER BY {', '.join(self.order_by_fields)}")

        # 添加LIMIT和OFFSET
        if self.limit_value is not None:
            sql_parts.append(f"LIMIT {self.limit_value}")
            if self.offset_value is not None:
                sql_parts.append(f"OFFSET {self.offset_value}")

        sql = " ".join(sql_parts)
        return sql, params

    def build_count(self) -> tuple[str, list[Any]]:
        """
        构建COUNT查询语句

        Returns:
            Tuple[str, List[Any]]: (COUNT SQL语句, 参数列表)
        """
        # 构建COUNT查询（不包含ORDER BY, LIMIT, OFFSET）
        sql_parts = ["SELECT COUNT(*)"]
        sql_parts.append(f"FROM {self.table_name}")

        # 添加JOIN
        if self.joins:
            sql_parts.extend(self.joins)

        # 添加WHERE
        params = []
        if self.where_conditions:
            sql_parts.append(f"WHERE {' '.join(self.where_conditions)}")
            params.extend(self.where_params)

        # 添加GROUP BY
        if self.group_by_fields:
            sql_parts.append(f"GROUP BY {', '.join(self.group_by_fields)}")

        # 添加HAVING
        if self.having_conditions:
            sql_parts.append(f"HAVING {' '.join(self.having_conditions)}")
            params.extend(self.having_params)

        sql = " ".join(sql_parts)
        return sql, params


def build_search_query(
    table_name: str,
    search_fields: list[str],
    search_term: str,
    additional_conditions: dict[str, Any] | None = None,
    order_by: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
) -> tuple[str, list[Any]]:
    """
    构建搜索查询的便捷函数

    Args:
        table_name: 表名
        search_fields: 搜索字段列表
        search_term: 搜索关键词
        additional_conditions: 额外的搜索条件
        order_by: 排序字段
        page: 页码
        page_size: 每页大小

    Returns:
        Tuple[str, List[Any]]: (SQL语句, 参数列表)
    """
    builder = QueryBuilder(table_name)

    # 添加搜索条件
    if search_term and search_fields:
        search_pattern = f"%{search_term}%"
        for i, field in enumerate(search_fields):
            logical_op = LogicalOperator.OR if i > 0 else LogicalOperator.AND
            builder.where_like(field, search_pattern, logical_op)

    # 添加额外条件
    if additional_conditions:
        for field, value in additional_conditions.items():
            if isinstance(value, list | tuple):
                builder.where_in(field, value)
            else:
                builder.where(field, ComparisonOperator.EQUAL, value)

    # 添加排序
    if order_by:
        if " " in order_by:
            field, direction = order_by.split(" ", 1)
            builder.order_by(field, direction)
        else:
            builder.order_by(order_by)

    # 添加分页
    if page is not None and page_size is not None:
        builder.paginate(page, page_size)

    return builder.build()
