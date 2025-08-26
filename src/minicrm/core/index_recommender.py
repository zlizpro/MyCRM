"""
MiniCRM 索引推荐器

专门负责数据库索引分析和推荐,包括:
- 索引使用情况分析
- 索引推荐生成
- 索引创建和管理
- 慢查询索引优化
"""

import logging
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class IndexRecommendation:
    """索引推荐"""

    table_name: str
    columns: list[str]
    index_type: str = "btree"  # btree, unique, partial
    reason: str = ""
    estimated_benefit: float = 0.0
    creation_sql: str = ""


class IndexRecommender:
    """
    索引推荐器

    专门负责分析查询模式并推荐合适的索引.
    """

    def __init__(self, database_manager):
        """
        初始化索引推荐器

        Args:
            database_manager: 数据库管理器实例
        """
        self._db = database_manager
        self._logger = logging.getLogger(__name__)
        self._existing_indexes: set[str] = set()
        self._recommended_indexes: list[IndexRecommendation] = []

    def recommend_indexes(
        self, analysis_period_days: int = 7
    ) -> list[IndexRecommendation]:
        """
        基于查询模式推荐索引

        Args:
            analysis_period_days: 分析周期(天)

        Returns:
            List[IndexRecommendation]: 索引推荐列表
        """
        try:
            recommendations = []

            # 获取现有索引
            self._load_existing_indexes()

            # 分析查询模式
            query_patterns = self._analyze_query_patterns(analysis_period_days)

            # 为频繁查询的列推荐索引
            for pattern in query_patterns:
                table_name = pattern.get("table_name")
                columns = pattern.get("columns", [])
                frequency = pattern.get("frequency", 0)

                if table_name and columns and frequency > 10:  # 频率阈值
                    # 检查是否已存在相关索引
                    if not self._has_covering_index(table_name, columns):
                        recommendation = self._create_index_recommendation(
                            table_name, columns, frequency
                        )
                        if recommendation:
                            recommendations.append(recommendation)

            # 分析慢查询并推荐索引
            slow_query_recommendations = self._analyze_slow_queries_for_indexes()
            recommendations.extend(slow_query_recommendations)

            # 去重和排序
            recommendations = self._deduplicate_recommendations(recommendations)
            recommendations.sort(key=lambda x: x.estimated_benefit, reverse=True)

            self._recommended_indexes = recommendations
            return recommendations

        except Exception as e:
            self._logger.error(f"推荐索引失败: {e}")
            return []

    def create_recommended_indexes(self, max_indexes: int = 5) -> list[str]:
        """
        创建推荐的索引

        Args:
            max_indexes: 最大创建索引数量

        Returns:
            List[str]: 成功创建的索引名称列表
        """
        created_indexes = []

        try:
            recommendations = self._recommended_indexes[:max_indexes]

            for recommendation in recommendations:
                try:
                    # 执行索引创建SQL
                    self._db.execute_update(recommendation.creation_sql)

                    index_name = self._extract_index_name(recommendation.creation_sql)
                    created_indexes.append(index_name)

                    self._logger.info(
                        f"成功创建索引: {index_name} "
                        f"表: {recommendation.table_name} "
                        f"列: {', '.join(recommendation.columns)}"
                    )

                except Exception as e:
                    self._logger.error(
                        f"创建索引失败: {recommendation.creation_sql}, 错误: {e}"
                    )

            # 更新现有索引列表
            self._load_existing_indexes()

            return created_indexes

        except Exception as e:
            self._logger.error(f"批量创建索引失败: {e}")
            return created_indexes

    def analyze_index_usage(self) -> dict[str, Any]:
        """分析索引使用情况"""
        try:
            # 获取所有表的统计信息
            tables_sql = (
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%'"
            )
            tables = self._db.execute_query(tables_sql)

            index_usage = {}

            for table in tables:
                table_name = table["name"]

                # 获取表的索引
                indexes_sql = f"PRAGMA index_list({table_name})"
                indexes = self._db.execute_query(indexes_sql)

                table_indexes = []
                for index in indexes:
                    index_info = {
                        "name": index["name"],
                        "unique": bool(index["unique"]),
                        "partial": bool(index["partial"]),
                    }
                    table_indexes.append(index_info)

                index_usage[table_name] = {
                    "index_count": len(table_indexes),
                    "indexes": table_indexes,
                }

            return index_usage

        except Exception as e:
            self._logger.error(f"分析索引使用失败: {e}")
            return {}

    def _load_existing_indexes(self) -> None:
        """加载现有索引信息"""
        try:
            # 获取所有索引信息
            sql = """
                SELECT name, tbl_name, sql
                FROM sqlite_master
                WHERE type = 'index' AND name NOT LIKE 'sqlite_%'
            """
            indexes = self._db.execute_query(sql)

            self._existing_indexes = {idx["name"] for idx in indexes}

        except Exception as e:
            self._logger.error(f"加载索引信息失败: {e}")

    def _analyze_query_patterns(self, days: int) -> list[dict[str, Any]]:
        """分析查询模式"""
        # 这里应该从性能分析器获取历史查询数据
        # 简化实现,返回一些常见的查询模式
        return [
            {
                "table_name": "customers",
                "columns": ["name"],
                "frequency": 50,
                "avg_time": 15.5,
            },
            {
                "table_name": "quotes",
                "columns": ["customer_id", "quote_date"],
                "frequency": 30,
                "avg_time": 25.2,
            },
            {
                "table_name": "financial_records",
                "columns": ["customer_id", "status"],
                "frequency": 25,
                "avg_time": 18.7,
            },
        ]

    def _has_covering_index(self, table_name: str, columns: list[str]) -> bool:
        """检查是否已存在覆盖指定列的索引"""
        try:
            # 获取表的索引信息
            sql = f"PRAGMA index_list({table_name})"
            indexes = self._db.execute_query(sql)

            for index in indexes:
                index_name = index["name"]
                # 获取索引的列信息
                sql = f"PRAGMA index_info({index_name})"
                index_columns = self._db.execute_query(sql)

                indexed_columns = [col["name"] for col in index_columns]

                # 检查是否覆盖所需的列
                if all(col in indexed_columns for col in columns):
                    return True

            return False

        except Exception as e:
            self._logger.error(f"检查索引覆盖失败: {e}")
            return False

    def _create_index_recommendation(
        self, table_name: str, columns: list[str], frequency: int
    ) -> IndexRecommendation | None:
        """创建索引推荐"""
        try:
            # 生成索引名称
            index_name = f"idx_{table_name}_{'_'.join(columns)}"

            # 生成创建SQL
            columns_str = ", ".join(columns)
            creation_sql = f"CREATE INDEX {index_name} ON {table_name}({columns_str})"

            # 估算收益
            estimated_benefit = min(frequency * 0.1, 10.0)  # 简化的收益估算

            # 生成推荐理由
            reason = (
                f"基于查询频率({frequency}次)为表{table_name}的列{columns_str}推荐索引"
            )

            return IndexRecommendation(
                table_name=table_name,
                columns=columns,
                reason=reason,
                estimated_benefit=estimated_benefit,
                creation_sql=creation_sql,
            )

        except Exception as e:
            self._logger.error(f"创建索引推荐失败: {e}")
            return None

    def _analyze_slow_queries_for_indexes(self) -> list[IndexRecommendation]:
        """分析慢查询并推荐索引"""
        recommendations = []

        try:
            # 这里应该从数据库性能分析器获取慢查询
            # 简化实现
            slow_queries = [
                {
                    "sql": "SELECT * FROM customers WHERE name LIKE '%test%'",
                    "execution_time": 150.0,
                },
                {
                    "sql": "SELECT * FROM quotes WHERE customer_id = ? AND status = ?",
                    "execution_time": 200.0,
                },
            ]

            for query_info in slow_queries:
                # 分析SQL语句,提取可能需要索引的列
                table_columns = self._extract_indexable_columns(query_info["sql"])

                for table_name, columns in table_columns.items():
                    if not self._has_covering_index(table_name, columns):
                        recommendation = IndexRecommendation(
                            table_name=table_name,
                            columns=columns,
                            reason=f"慢查询优化: 执行时间{query_info['execution_time']:.2f}ms",
                            estimated_benefit=query_info["execution_time"] / 100,
                            creation_sql=f"CREATE INDEX idx_{table_name}_{'_'.join(columns)} ON {table_name}({', '.join(columns)})",
                        )
                        recommendations.append(recommendation)

        except Exception as e:
            self._logger.error(f"分析慢查询索引失败: {e}")

        return recommendations

    def _extract_indexable_columns(self, sql: str) -> dict[str, list[str]]:
        """从SQL语句中提取可能需要索引的列"""
        table_columns: dict[str, list[str]] = {}

        try:
            # 简化的SQL解析,提取WHERE子句中的列
            where_match = re.search(
                r"WHERE\s+(.+?)(?:\s+ORDER\s+BY|\s+GROUP\s+BY|\s+LIMIT|$)",
                sql,
                re.IGNORECASE | re.DOTALL,
            )
            if where_match:
                where_clause = where_match.group(1)

                # 提取表名.列名或列名
                column_matches = re.findall(r"(\w+)\.(\w+)|(\w+)\s*[=<>]", where_clause)

                for match in column_matches:
                    if match[0] and match[1]:  # table.column
                        table_name = match[0]
                        column_name = match[1]
                    elif match[2]:  # column
                        # 需要从FROM子句推断表名
                        table_name = self._extract_table_from_sql(sql)
                        column_name = match[2]
                    else:
                        continue

                    if table_name:
                        if table_name not in table_columns:
                            table_columns[table_name] = []
                        if column_name not in table_columns[table_name]:
                            table_columns[table_name].append(column_name)

        except Exception as e:
            self._logger.error(f"提取索引列失败: {e}")

        return table_columns

    def _extract_table_from_sql(self, sql: str) -> str | None:
        """从SQL语句中提取主表名"""
        try:
            from_match = re.search(r"FROM\s+(\w+)", sql, re.IGNORECASE)
            if from_match:
                return from_match.group(1)
        except Exception:
            pass
        return None

    def _deduplicate_recommendations(
        self, recommendations: list[IndexRecommendation]
    ) -> list[IndexRecommendation]:
        """去重索引推荐"""
        seen = set()
        unique_recommendations = []

        for rec in recommendations:
            key = (rec.table_name, tuple(sorted(rec.columns)))
            if key not in seen:
                seen.add(key)
                unique_recommendations.append(rec)

        return unique_recommendations

    def _extract_index_name(self, creation_sql: str) -> str:
        """从创建SQL中提取索引名称"""
        match = re.search(r"CREATE INDEX\s+(\w+)", creation_sql, re.IGNORECASE)
        return match.group(1) if match else "unknown"
