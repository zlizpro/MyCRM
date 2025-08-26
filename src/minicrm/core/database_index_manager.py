"""
MiniCRM 数据库索引管理器

专门负责数据库索引的创建、维护和优化,包括:
- 自动索引创建和删除
- 索引使用情况监控
- 索引维护和重建
- 索引性能分析
- 智能索引推荐
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .database_performance_analyzer import database_performance_analyzer


@dataclass
class IndexInfo:
    """索引信息"""

    name: str
    table_name: str
    columns: list[str]
    is_unique: bool = False
    is_partial: bool = False
    creation_sql: str = ""
    size_kb: float = 0.0
    usage_count: int = 0
    last_used: datetime | None = None
    created_at: datetime | None = None


@dataclass
class IndexStatistics:
    """索引统计信息"""

    total_indexes: int = 0
    used_indexes: int = 0
    unused_indexes: int = 0
    total_size_kb: float = 0.0
    avg_usage_count: float = 0.0
    most_used_indexes: list[str] = field(default_factory=list)
    least_used_indexes: list[str] = field(default_factory=list)


class DatabaseIndexManager:
    """
    数据库索引管理器

    提供全面的索引管理功能,包括创建、监控、维护和优化.
    """

    def __init__(self, database_manager):
        """
        初始化索引管理器

        Args:
            database_manager: 数据库管理器实例
        """
        self._db = database_manager
        self._logger = logging.getLogger(__name__)

        # 索引信息缓存
        self._indexes: dict[str, IndexInfo] = {}
        self._index_usage_stats: dict[str, int] = {}

        # 配置参数
        self._auto_create_indexes = True
        self._auto_drop_unused_indexes = False
        self._unused_threshold_days = 30
        self._min_usage_count = 10

        self._enabled = True

        self._logger.debug("数据库索引管理器初始化完成")

    def enable(self) -> None:
        """启用索引管理器"""
        self._enabled = True
        self._logger.info("数据库索引管理器已启用")

    def disable(self) -> None:
        """禁用索引管理器"""
        self._enabled = False
        self._logger.info("数据库索引管理器已禁用")

    def scan_existing_indexes(self) -> dict[str, IndexInfo]:
        """
        扫描现有索引

        Returns:
            Dict[str, IndexInfo]: 索引信息字典
        """
        if not self._enabled:
            return {}

        try:
            self._indexes.clear()

            # 获取所有用户创建的索引
            sql = """
                SELECT name, tbl_name, sql
                FROM sqlite_master
                WHERE type = 'index'
                AND name NOT LIKE 'sqlite_%'
                AND sql IS NOT NULL
            """

            index_rows = self._db.execute_query(sql)

            for row in index_rows:
                index_name = row["name"]
                table_name = row["tbl_name"]
                creation_sql = row["sql"] or ""

                # 获取索引详细信息
                index_info = self._get_index_details(
                    index_name, table_name, creation_sql
                )
                if index_info:
                    self._indexes[index_name] = index_info

            self._logger.info(f"扫描到 {len(self._indexes)} 个索引")
            return self._indexes

        except Exception as e:
            self._logger.error(f"扫描索引失败: {e}")
            return {}

    def create_index(
        self,
        table_name: str,
        columns: list[str],
        index_name: str | None = None,
        unique: bool = False,
        where_clause: str | None = None,
    ) -> bool:
        """
        创建索引

        Args:
            table_name: 表名
            columns: 列名列表
            index_name: 索引名称(可选)
            unique: 是否唯一索引
            where_clause: 部分索引的WHERE子句

        Returns:
            bool: 创建是否成功
        """
        if not self._enabled:
            return False

        try:
            # 生成索引名称
            if not index_name:
                index_name = f"idx_{table_name}_{'_'.join(columns)}"

            # 检查索引是否已存在
            if self._index_exists(index_name):
                self._logger.warning(f"索引 {index_name} 已存在")
                return False

            # 构建创建SQL
            columns_str = ", ".join(columns)
            unique_str = "UNIQUE " if unique else ""
            where_str = f" WHERE {where_clause}" if where_clause else ""

            creation_sql = f"CREATE {unique_str}INDEX {index_name} ON {table_name}({columns_str}){where_str}"

            # 执行创建
            self._db.execute_update(creation_sql)

            # 创建索引信息对象
            index_info = IndexInfo(
                name=index_name,
                table_name=table_name,
                columns=columns,
                is_unique=unique,
                is_partial=bool(where_clause),
                creation_sql=creation_sql,
                created_at=datetime.now(),
            )

            # 更新缓存
            self._indexes[index_name] = index_info

            self._logger.info(f"成功创建索引: {index_name}")
            return True

        except Exception as e:
            self._logger.error(f"创建索引失败: {creation_sql}, 错误: {e}")
            return False

    def drop_index(self, index_name: str) -> bool:
        """
        删除索引

        Args:
            index_name: 索引名称

        Returns:
            bool: 删除是否成功
        """
        if not self._enabled:
            return False

        try:
            # 检查索引是否存在
            if not self._index_exists(index_name):
                self._logger.warning(f"索引 {index_name} 不存在")
                return False

            # 执行删除
            drop_sql = f"DROP INDEX {index_name}"
            self._db.execute_update(drop_sql)

            # 从缓存中移除
            if index_name in self._indexes:
                del self._indexes[index_name]

            self._logger.info(f"成功删除索引: {index_name}")
            return True

        except Exception as e:
            self._logger.error(f"删除索引失败: {index_name}, 错误: {e}")
            return False

    def analyze_index_usage(self) -> IndexStatistics:
        """
        分析索引使用情况

        Returns:
            IndexStatistics: 索引统计信息
        """
        if not self._enabled:
            return IndexStatistics()

        try:
            # 确保索引信息是最新的
            self.scan_existing_indexes()

            # 从性能分析器获取查询统计
            self._update_index_usage_from_queries()

            # 计算统计信息
            total_indexes = len(self._indexes)
            used_indexes = sum(
                1 for idx in self._indexes.values() if idx.usage_count > 0
            )
            unused_indexes = total_indexes - used_indexes

            total_size = sum(idx.size_kb for idx in self._indexes.values())
            avg_usage = (
                sum(idx.usage_count for idx in self._indexes.values()) / total_indexes
                if total_indexes > 0
                else 0.0
            )

            # 找出使用最多和最少的索引
            sorted_by_usage = sorted(
                self._indexes.values(), key=lambda x: x.usage_count, reverse=True
            )

            most_used = [idx.name for idx in sorted_by_usage[:5] if idx.usage_count > 0]
            least_used = [
                idx.name for idx in sorted_by_usage[-5:] if idx.usage_count == 0
            ]

            return IndexStatistics(
                total_indexes=total_indexes,
                used_indexes=used_indexes,
                unused_indexes=unused_indexes,
                total_size_kb=total_size,
                avg_usage_count=avg_usage,
                most_used_indexes=most_used,
                least_used_indexes=least_used,
            )

        except Exception as e:
            self._logger.error(f"分析索引使用情况失败: {e}")
            return IndexStatistics()

    def optimize_indexes(self) -> dict[str, Any]:
        """
        优化索引

        Returns:
            Dict[str, Any]: 优化结果
        """
        if not self._enabled:
            return {"error": "索引管理器已禁用"}

        try:
            optimization_results = {
                "created_indexes": [],
                "dropped_indexes": [],
                "rebuilt_indexes": [],
                "recommendations": [],
            }

            # 1. 分析当前索引使用情况
            stats = self.analyze_index_usage()

            # 2. 删除未使用的索引(如果启用)
            if self._auto_drop_unused_indexes:
                dropped = self._drop_unused_indexes()
                optimization_results["dropped_indexes"] = dropped

            # 3. 基于查询模式创建推荐索引
            if self._auto_create_indexes:
                created = self._create_recommended_indexes()
                optimization_results["created_indexes"] = created

            # 4. 重建碎片化的索引
            rebuilt = self._rebuild_fragmented_indexes()
            optimization_results["rebuilt_indexes"] = rebuilt

            # 5. 生成优化建议
            recommendations = self._generate_optimization_recommendations(stats)
            optimization_results["recommendations"] = recommendations

            self._logger.info(f"索引优化完成: {optimization_results}")
            return optimization_results

        except Exception as e:
            self._logger.error(f"索引优化失败: {e}")
            return {"error": str(e)}

    def get_index_recommendations(self) -> list[dict[str, Any]]:
        """
        获取索引推荐

        Returns:
            List[Dict[str, Any]]: 索引推荐列表
        """
        if not self._enabled:
            return []

        try:
            recommendations = []

            # 分析慢查询
            slow_queries = database_performance_analyzer.get_slow_queries(limit=20)

            for query_metric in slow_queries:
                # 分析查询,提取可能需要索引的表和列
                table_columns = self._analyze_query_for_indexes(query_metric.sql)

                for table_name, columns in table_columns.items():
                    # 检查是否已有合适的索引
                    if not self._has_suitable_index(table_name, columns):
                        recommendation = {
                            "table_name": table_name,
                            "columns": columns,
                            "reason": f"慢查询优化 (执行时间: {query_metric.execution_time:.2f}ms)",
                            "query_sample": query_metric.sql[:100] + "...",
                            "estimated_benefit": self._estimate_index_benefit(
                                query_metric
                            ),
                            "creation_sql": self._generate_index_sql(
                                table_name, columns
                            ),
                        }
                        recommendations.append(recommendation)

            # 按预期收益排序
            recommendations.sort(key=lambda x: x["estimated_benefit"], reverse=True)

            return recommendations

        except Exception as e:
            self._logger.error(f"获取索引推荐失败: {e}")
            return []

    def maintain_indexes(self) -> dict[str, Any]:
        """
        维护索引

        Returns:
            Dict[str, Any]: 维护结果
        """
        if not self._enabled:
            return {"error": "索引管理器已禁用"}

        try:
            maintenance_results = {
                "analyzed_indexes": 0,
                "reindexed_count": 0,
                "errors": [],
            }

            # 扫描所有索引
            indexes = self.scan_existing_indexes()
            maintenance_results["analyzed_indexes"] = len(indexes)

            # 对每个索引执行REINDEX(SQLite中的索引维护)
            for index_name in indexes.keys():
                try:
                    reindex_sql = f"REINDEX {index_name}"
                    self._db.execute_update(reindex_sql)
                    maintenance_results["reindexed_count"] += 1

                except Exception as e:
                    error_msg = f"重建索引 {index_name} 失败: {e}"
                    maintenance_results["errors"].append(error_msg)
                    self._logger.error(error_msg)

            self._logger.info(f"索引维护完成: {maintenance_results}")
            return maintenance_results

        except Exception as e:
            self._logger.error(f"索引维护失败: {e}")
            return {"error": str(e)}

    def generate_index_report(self) -> dict[str, Any]:
        """
        生成索引报告

        Returns:
            Dict[str, Any]: 索引报告
        """
        try:
            # 获取索引统计
            stats = self.analyze_index_usage()

            # 获取索引推荐
            recommendations = self.get_index_recommendations()

            # 获取索引详细信息
            index_details = []
            for index_info in self._indexes.values():
                detail = {
                    "name": index_info.name,
                    "table": index_info.table_name,
                    "columns": index_info.columns,
                    "unique": index_info.is_unique,
                    "partial": index_info.is_partial,
                    "size_kb": index_info.size_kb,
                    "usage_count": index_info.usage_count,
                    "last_used": index_info.last_used.isoformat()
                    if index_info.last_used
                    else None,
                    "created_at": index_info.created_at.isoformat()
                    if index_info.created_at
                    else None,
                }
                index_details.append(detail)

            return {
                "report_timestamp": datetime.now().isoformat(),
                "statistics": {
                    "total_indexes": stats.total_indexes,
                    "used_indexes": stats.used_indexes,
                    "unused_indexes": stats.unused_indexes,
                    "total_size_kb": stats.total_size_kb,
                    "avg_usage_count": stats.avg_usage_count,
                    "most_used_indexes": stats.most_used_indexes,
                    "least_used_indexes": stats.least_used_indexes,
                },
                "index_details": index_details,
                "recommendations": recommendations,
                "configuration": {
                    "auto_create_indexes": self._auto_create_indexes,
                    "auto_drop_unused_indexes": self._auto_drop_unused_indexes,
                    "unused_threshold_days": self._unused_threshold_days,
                    "min_usage_count": self._min_usage_count,
                },
            }

        except Exception as e:
            self._logger.error(f"生成索引报告失败: {e}")
            return {"error": str(e)}

    def _get_index_details(
        self, index_name: str, table_name: str, creation_sql: str
    ) -> IndexInfo | None:
        """获取索引详细信息"""
        try:
            # 获取索引列信息
            pragma_sql = f"PRAGMA index_info({index_name})"
            columns_info = self._db.execute_query(pragma_sql)

            columns = [col["name"] for col in columns_info]

            # 检查是否为唯一索引
            is_unique = "UNIQUE" in creation_sql.upper()

            # 检查是否为部分索引
            is_partial = "WHERE" in creation_sql.upper()

            return IndexInfo(
                name=index_name,
                table_name=table_name,
                columns=columns,
                is_unique=is_unique,
                is_partial=is_partial,
                creation_sql=creation_sql,
                usage_count=self._index_usage_stats.get(index_name, 0),
            )

        except Exception as e:
            self._logger.error(f"获取索引详细信息失败: {index_name}, 错误: {e}")
            return None

    def _index_exists(self, index_name: str) -> bool:
        """检查索引是否存在"""
        try:
            sql = "SELECT name FROM sqlite_master WHERE type='index' AND name=?"
            result = self._db.execute_query(sql, (index_name,))
            return len(result) > 0
        except Exception:
            return False

    def _update_index_usage_from_queries(self) -> None:
        """从查询统计更新索引使用情况"""
        try:
            # 从性能分析器获取查询指标
            query_metrics = database_performance_analyzer.get_metrics()

            # 重置使用统计
            self._index_usage_stats.clear()

            for metric in query_metrics:
                # 分析查询可能使用的索引
                used_indexes = self._identify_used_indexes(
                    metric.operation, metric.metadata
                )

                for index_name in used_indexes:
                    self._index_usage_stats[index_name] = (
                        self._index_usage_stats.get(index_name, 0) + 1
                    )

            # 更新索引对象的使用统计
            for index_name, usage_count in self._index_usage_stats.items():
                if index_name in self._indexes:
                    self._indexes[index_name].usage_count = usage_count
                    self._indexes[index_name].last_used = datetime.now()

        except Exception as e:
            self._logger.error(f"更新索引使用统计失败: {e}")

    def _identify_used_indexes(
        self, operation: str, metadata: dict[str, Any]
    ) -> list[str]:
        """识别查询可能使用的索引"""
        used_indexes = []

        try:
            # 从SQL中提取可能使用的索引
            sql = metadata.get("sql", "")
            if sql:
                # 简化的索引使用分析
                # 实际应该通过EXPLAIN QUERY PLAN来准确识别
                for index_name, index_info in self._indexes.items():
                    # 检查查询是否涉及索引的表和列
                    if index_info.table_name.lower() in sql.lower() and any(
                        col.lower() in sql.lower() for col in index_info.columns
                    ):
                        used_indexes.append(index_name)

        except Exception as e:
            self._logger.error(f"识别使用索引失败: {e}")

        return used_indexes

    def _drop_unused_indexes(self) -> list[str]:
        """删除未使用的索引"""
        dropped_indexes = []

        try:
            for index_name, index_info in list(self._indexes.items()):
                # 检查是否为未使用的索引
                if (
                    index_info.usage_count < self._min_usage_count
                    and index_info.last_used
                    and (datetime.now() - index_info.last_used).days
                    > self._unused_threshold_days
                ):
                    if self.drop_index(index_name):
                        dropped_indexes.append(index_name)

        except Exception as e:
            self._logger.error(f"删除未使用索引失败: {e}")

        return dropped_indexes

    def _create_recommended_indexes(self) -> list[str]:
        """创建推荐的索引"""
        created_indexes = []

        try:
            recommendations = self.get_index_recommendations()

            # 限制一次创建的索引数量
            max_create = 3

            for i, rec in enumerate(recommendations[:max_create]):
                index_name = f"idx_{rec['table_name']}_{'_'.join(rec['columns'])}"

                if self.create_index(
                    table_name=rec["table_name"],
                    columns=rec["columns"],
                    index_name=index_name,
                ):
                    created_indexes.append(index_name)

        except Exception as e:
            self._logger.error(f"创建推荐索引失败: {e}")

        return created_indexes

    def _rebuild_fragmented_indexes(self) -> list[str]:
        """重建碎片化的索引"""
        rebuilt_indexes = []

        try:
            # SQLite中通过REINDEX重建索引
            for index_name in self._indexes.keys():
                try:
                    reindex_sql = f"REINDEX {index_name}"
                    self._db.execute_update(reindex_sql)
                    rebuilt_indexes.append(index_name)
                except Exception as e:
                    self._logger.error(f"重建索引 {index_name} 失败: {e}")

        except Exception as e:
            self._logger.error(f"重建索引失败: {e}")

        return rebuilt_indexes

    def _generate_optimization_recommendations(
        self, stats: IndexStatistics
    ) -> list[str]:
        """生成优化建议"""
        recommendations = []

        try:
            # 未使用索引建议
            if stats.unused_indexes > 0:
                recommendations.append(
                    f"发现 {stats.unused_indexes} 个未使用的索引,考虑删除以节省存储空间"
                )

            # 索引覆盖率建议
            if stats.used_indexes < stats.total_indexes * 0.7:
                recommendations.append("索引使用率较低,建议审查索引策略")

            # 大小建议
            if stats.total_size_kb > 10000:  # 10MB
                recommendations.append("索引总大小较大,考虑优化索引设计")

            # 使用频率建议
            if stats.avg_usage_count < 10:
                recommendations.append("索引平均使用频率较低,建议分析查询模式")

            if not recommendations:
                recommendations.append("索引配置良好,无需特别优化")

        except Exception as e:
            self._logger.warning(f"生成优化建议时出错: {e}")
            recommendations.append("优化分析出现异常,建议检查系统状态")

        return recommendations

    def _analyze_query_for_indexes(self, sql: str) -> dict[str, list[str]]:
        """分析查询需要的索引"""
        # 这里应该实现更复杂的SQL解析逻辑
        # 简化实现,返回基本的表列映射
        table_columns = {}

        try:
            # 提取WHERE子句中的列
            import re

            # 提取表名
            from_match = re.search(r"FROM\s+(\w+)", sql, re.IGNORECASE)
            if from_match:
                table_name = from_match.group(1)

                # 提取WHERE子句中的列
                where_match = re.search(
                    r"WHERE\s+(.+?)(?:\s+ORDER|\s+GROUP|\s+LIMIT|$)", sql, re.IGNORECASE
                )
                if where_match:
                    where_clause = where_match.group(1)

                    # 简单的列提取
                    column_matches = re.findall(r"(\w+)\s*[=<>]", where_clause)
                    if column_matches:
                        table_columns[table_name] = column_matches

        except Exception as e:
            self._logger.error(f"分析查询索引需求失败: {e}")

        return table_columns

    def _has_suitable_index(self, table_name: str, columns: list[str]) -> bool:
        """检查是否有合适的索引"""
        for index_info in self._indexes.values():
            if index_info.table_name == table_name and all(
                col in index_info.columns for col in columns
            ):
                return True
        return False

    def _estimate_index_benefit(self, query_metric) -> float:
        """估算索引收益"""
        # 简化的收益估算
        return min(query_metric.execution_time / 10, 100.0)

    def _generate_index_sql(self, table_name: str, columns: list[str]) -> str:
        """生成索引创建SQL"""
        index_name = f"idx_{table_name}_{'_'.join(columns)}"
        columns_str = ", ".join(columns)
        return f"CREATE INDEX {index_name} ON {table_name}({columns_str})"


# 全局数据库索引管理器实例
database_index_manager = None


def get_index_manager(database_manager=None):
    """获取索引管理器实例"""
    global database_index_manager
    if database_index_manager is None and database_manager:
        database_index_manager = DatabaseIndexManager(database_manager)
    return database_index_manager
