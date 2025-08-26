"""
MiniCRM 查询分析器

专门负责SQL查询分析和执行计划解析,包括:
- 查询执行计划分析
- 查询优化建议生成
- SQL语句解析和优化
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class QueryPlan:
    """查询执行计划"""

    query_id: str
    sql: str
    plan_steps: list[dict[str, Any]] = field(default_factory=list)
    estimated_cost: float = 0.0
    uses_index: bool = False
    table_scans: list[str] = field(default_factory=list)
    index_usage: list[str] = field(default_factory=list)
    optimization_suggestions: list[str] = field(default_factory=list)


@dataclass
class QueryOptimization:
    """查询优化建议"""

    original_sql: str
    optimized_sql: str
    optimization_type: str
    description: str
    estimated_improvement: float = 0.0


class QueryAnalyzer:
    """
    查询分析器

    专门负责SQL查询的分析和优化建议生成.
    """

    def __init__(self, database_manager):
        """
        初始化查询分析器

        Args:
            database_manager: 数据库管理器实例
        """
        self._db = database_manager
        self._logger = logging.getLogger(__name__)

    def analyze_query_plan(self, sql: str) -> QueryPlan:
        """
        分析查询执行计划

        Args:
            sql: SQL查询语句

        Returns:
            QueryPlan: 查询执行计划分析结果
        """
        try:
            # 生成查询ID
            query_id = self._generate_query_id(sql)

            # 获取查询执行计划
            explain_sql = f"EXPLAIN QUERY PLAN {sql}"
            plan_rows = self._db.execute_query(explain_sql)

            plan = QueryPlan(query_id=query_id, sql=sql)

            # 解析执行计划
            for row in plan_rows:
                step = {
                    "id": row.get("id", 0),
                    "parent": row.get("parent", 0),
                    "detail": row.get("detail", ""),
                }
                plan.plan_steps.append(step)

                # 分析执行计划细节
                detail = step["detail"].upper()

                # 检查是否使用索引
                if "USING INDEX" in detail:
                    plan.uses_index = True
                    # 提取索引名称
                    index_match = re.search(r"USING INDEX (\w+)", detail)
                    if index_match:
                        plan.index_usage.append(index_match.group(1))

                # 检查是否进行表扫描
                if "SCAN TABLE" in detail:
                    table_match = re.search(r"SCAN TABLE (\w+)", detail)
                    if table_match:
                        plan.table_scans.append(table_match.group(1))

            # 生成优化建议
            plan.optimization_suggestions = self._generate_optimization_suggestions(
                plan
            )

            return plan

        except Exception as e:
            self._logger.error(f"分析查询执行计划失败: {e}")
            return QueryPlan(query_id="", sql=sql)

    def optimize_query(self, sql: str) -> QueryOptimization:
        """
        优化查询语句

        Args:
            sql: 原始SQL语句

        Returns:
            QueryOptimization: 查询优化建议
        """
        try:
            optimized_sql = sql
            optimization_type = "none"
            description = "无需优化"

            # 移除不必要的空格和换行
            optimized_sql = re.sub(r"\s+", " ", optimized_sql.strip())

            # 优化SELECT语句
            if sql.strip().upper().startswith("SELECT"):
                optimized_sql, opt_type, desc = self._optimize_select_query(
                    optimized_sql
                )
                if opt_type != "none":
                    optimization_type = opt_type
                    description = desc

            # 优化WHERE子句
            if "WHERE" in optimized_sql.upper():
                optimized_sql, opt_type, desc = self._optimize_where_clause(
                    optimized_sql
                )
                if opt_type != "none":
                    optimization_type = (
                        f"{optimization_type}, {opt_type}"
                        if optimization_type != "none"
                        else opt_type
                    )
                    description = (
                        f"{description}; {desc}" if description != "无需优化" else desc
                    )

            # 优化ORDER BY子句
            if "ORDER BY" in optimized_sql.upper():
                optimized_sql, opt_type, desc = self._optimize_order_by(optimized_sql)
                if opt_type != "none":
                    optimization_type = (
                        f"{optimization_type}, {opt_type}"
                        if optimization_type != "none"
                        else opt_type
                    )
                    description = (
                        f"{description}; {desc}" if description != "无需优化" else desc
                    )

            return QueryOptimization(
                original_sql=sql,
                optimized_sql=optimized_sql,
                optimization_type=optimization_type,
                description=description,
            )

        except Exception as e:
            self._logger.error(f"查询优化失败: {e}")
            return QueryOptimization(sql, sql, "error", f"优化失败: {e}")

    def _generate_query_id(self, sql: str) -> str:
        """生成查询ID"""
        import hashlib

        return hashlib.md5(sql.encode()).hexdigest()[:12]

    def _generate_optimization_suggestions(self, plan: QueryPlan) -> list[str]:
        """生成查询优化建议"""
        suggestions = []

        # 检查表扫描
        if plan.table_scans:
            for table in plan.table_scans:
                suggestions.append(f"表 {table} 进行了全表扫描,考虑添加适当的索引")

        # 检查索引使用
        if not plan.uses_index and plan.table_scans:
            suggestions.append("查询未使用索引,性能可能较差")

        # 检查复杂的执行计划
        if len(plan.plan_steps) > 5:
            suggestions.append("查询执行计划较复杂,考虑简化查询逻辑")

        return suggestions

    def _optimize_select_query(self, sql: str) -> tuple[str, str, str]:
        """优化SELECT查询"""
        optimized_sql = sql
        optimization_type = "none"
        description = "无需优化"

        # 检查SELECT *
        if re.search(r"SELECT\s+\*", sql, re.IGNORECASE):
            optimization_type = "select_columns"
            description = "建议指定具体列名而不是使用SELECT *"

        # 检查DISTINCT的使用
        if "DISTINCT" in sql.upper():
            optimization_type = "distinct_usage"
            description = "检查是否可以通过改进查询逻辑避免使用DISTINCT"

        return optimized_sql, optimization_type, description

    def _optimize_where_clause(self, sql: str) -> tuple[str, str, str]:
        """优化WHERE子句"""
        optimized_sql = sql
        optimization_type = "none"
        description = "无需优化"

        # 检查函数在WHERE子句中的使用
        if re.search(r"WHERE.*\w+\([^)]*\w+[^)]*\)", sql, re.IGNORECASE):
            optimization_type = "where_functions"
            description = "WHERE子句中使用了函数,可能影响索引使用"

        # 检查LIKE的使用
        if re.search(r"LIKE\s+'%.*%'", sql, re.IGNORECASE):
            optimization_type = "like_pattern"
            description = "使用了前导通配符的LIKE模式,无法使用索引"

        return optimized_sql, optimization_type, description

    def _optimize_order_by(self, sql: str) -> tuple[str, str, str]:
        """优化ORDER BY子句"""
        optimized_sql = sql
        optimization_type = "none"
        description = "无需优化"

        # 检查ORDER BY是否可以使用索引
        order_match = re.search(r"ORDER BY\s+(\w+)", sql, re.IGNORECASE)
        if order_match:
            column = order_match.group(1)
            optimization_type = "order_by_index"
            description = f"为ORDER BY列 {column} 创建索引可以提高排序性能"

        return optimized_sql, optimization_type, description
