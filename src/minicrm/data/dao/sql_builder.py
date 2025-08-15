"""
MiniCRM SQL构建器

负责构建各种SQL语句
"""

import logging
from typing import Any


class SQLBuilder:
    """SQL语句构建器"""

    def __init__(self):
        """初始化SQL构建器"""
        self._logger = logging.getLogger(__name__)

    def build_insert_sql(
        self, table_name: str, data: dict[str, Any]
    ) -> tuple[str, tuple]:
        """
        构建INSERT SQL语句

        Args:
            table_name: 表名
            data: 数据字典

        Returns:
            tuple: (SQL语句, 参数元组)
        """
        try:
            if not data:
                raise ValueError("数据不能为空")

            columns = list(data.keys())
            placeholders = ["?" for _ in columns]
            values = tuple(data.values())

            sql = f"""
            INSERT INTO {table_name} ({", ".join(columns)})
            VALUES ({", ".join(placeholders)})
            """

            return sql.strip(), values

        except Exception as e:
            self._logger.error(f"构建INSERT SQL失败: {e}")
            raise

    def build_update_sql(
        self, table_name: str, record_id: int, data: dict[str, Any]
    ) -> tuple[str, tuple]:
        """
        构建UPDATE SQL语句

        Args:
            table_name: 表名
            record_id: 记录ID
            data: 更新数据

        Returns:
            tuple: (SQL语句, 参数元组)
        """
        try:
            if not data:
                raise ValueError("更新数据不能为空")

            # 构建SET子句
            set_clauses = []
            values = []

            for column, value in data.items():
                if column != "id":  # 不更新ID字段
                    set_clauses.append(f"{column} = ?")
                    values.append(value)

            if not set_clauses:
                raise ValueError("没有可更新的字段")

            values.append(record_id)

            sql = f"""
            UPDATE {table_name}
            SET {", ".join(set_clauses)}
            WHERE id = ?
            """

            return sql.strip(), tuple(values)

        except Exception as e:
            self._logger.error(f"构建UPDATE SQL失败: {e}")
            raise

    def build_select_sql(
        self,
        table_name: str,
        where_clause: str = None,
        order_by: str = None,
        limit: int = None,
        offset: int = None,
        columns: list[str] = None,
    ) -> str:
        """
        构建SELECT SQL语句

        Args:
            table_name: 表名
            where_clause: WHERE子句
            order_by: 排序字段
            limit: 限制数量
            offset: 偏移量
            columns: 查询列，默认为*

        Returns:
            str: SQL语句
        """
        try:
            # 构建SELECT子句
            select_clause = ", ".join(columns) if columns else "*"

            sql = f"SELECT {select_clause} FROM {table_name}"

            # 添加WHERE子句
            if where_clause:
                sql += f" WHERE {where_clause}"

            # 添加ORDER BY子句
            if order_by:
                sql += f" ORDER BY {order_by}"

            # 添加LIMIT子句
            if limit is not None:
                sql += f" LIMIT {limit}"

            # 添加OFFSET子句
            if offset is not None:
                sql += f" OFFSET {offset}"

            return sql

        except Exception as e:
            self._logger.error(f"构建SELECT SQL失败: {e}")
            raise

    def build_delete_sql(self, table_name: str, record_id: int) -> tuple[str, tuple]:
        """
        构建DELETE SQL语句

        Args:
            table_name: 表名
            record_id: 记录ID

        Returns:
            tuple: (SQL语句, 参数元组)
        """
        try:
            sql = f"DELETE FROM {table_name} WHERE id = ?"
            return sql, (record_id,)

        except Exception as e:
            self._logger.error(f"构建DELETE SQL失败: {e}")
            raise

    def build_count_sql(self, table_name: str, where_clause: str = None) -> str:
        """
        构建COUNT SQL语句

        Args:
            table_name: 表名
            where_clause: WHERE子句

        Returns:
            str: SQL语句
        """
        try:
            sql = f"SELECT COUNT(*) FROM {table_name}"

            if where_clause:
                sql += f" WHERE {where_clause}"

            return sql

        except Exception as e:
            self._logger.error(f"构建COUNT SQL失败: {e}")
            raise

    def build_where_clause(self, filters: dict[str, Any]) -> tuple[str, list]:
        """
        构建WHERE子句

        Args:
            filters: 过滤条件字典

        Returns:
            tuple: (WHERE子句, 参数列表)
        """
        try:
            if not filters:
                return "", []

            conditions = []
            params = []

            for column, value in filters.items():
                if value is None:
                    conditions.append(f"{column} IS NULL")
                elif isinstance(value, list | tuple):
                    # IN条件
                    placeholders = ", ".join(["?" for _ in value])
                    conditions.append(f"{column} IN ({placeholders})")
                    params.extend(value)
                elif (
                    isinstance(value, str)
                    and value.startswith("%")
                    and value.endswith("%")
                ):
                    # LIKE条件
                    conditions.append(f"{column} LIKE ?")
                    params.append(value)
                else:
                    # 等值条件
                    conditions.append(f"{column} = ?")
                    params.append(value)

            where_clause = " AND ".join(conditions)
            return where_clause, params

        except Exception as e:
            self._logger.error(f"构建WHERE子句失败: {e}")
            raise
