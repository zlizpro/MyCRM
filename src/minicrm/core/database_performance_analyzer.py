"""
MiniCRM 数据库性能分析器

专门用于数据库查询性能监控和分析,包括:
- 慢查询检测和记录
- 查询执行统计分析
- 数据库连接性能监控
- 查询频率和趋势分析
- 数据库性能报告生成
"""

import logging
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


@dataclass
class DatabaseQueryMetric:
    """数据库查询性能指标"""

    query_id: str
    sql: str
    params: tuple | None = None
    execution_time: float = 0.0  # 毫秒
    rows_affected: int = 0
    rows_returned: int = 0
    connection_time: float = 0.0  # 毫秒
    timestamp: datetime = field(default_factory=datetime.now)
    operation_type: str = "unknown"  # SELECT, INSERT, UPDATE, DELETE
    table_name: str | None = None
    is_slow_query: bool = False
    error_message: str | None = None


@dataclass
class DatabaseConnectionMetric:
    """数据库连接性能指标"""

    connection_id: str
    connect_time: float = 0.0  # 毫秒
    close_time: float = 0.0  # 毫秒
    total_queries: int = 0
    total_execution_time: float = 0.0  # 毫秒
    created_at: datetime = field(default_factory=datetime.now)
    closed_at: datetime | None = None
    is_active: bool = True


class DatabasePerformanceAnalyzer:
    """
    数据库性能分析器

    提供全面的数据库性能监控和分析功能,包括慢查询检测、
    查询统计分析、连接性能监控等.
    """

    def __init__(self, slow_query_threshold: float = 1000.0):
        """
        初始化数据库性能分析器

        Args:
            slow_query_threshold: 慢查询阈值(毫秒),默认1000ms
        """
        self._logger = logging.getLogger(__name__)
        self._slow_query_threshold = slow_query_threshold
        self._query_metrics: list[DatabaseQueryMetric] = []
        self._connection_metrics: dict[str, DatabaseConnectionMetric] = {}
        self._query_patterns: dict[str, list[DatabaseQueryMetric]] = defaultdict(list)
        self._enabled = True
        self._max_metrics = 5000  # 最大保存的查询指标数量

        self._logger.debug("数据库性能分析器初始化完成")

    def enable(self) -> None:
        """启用数据库性能分析"""
        self._enabled = True
        self._logger.info("数据库性能分析已启用")

    def disable(self) -> None:
        """禁用数据库性能分析"""
        self._enabled = False
        self._logger.info("数据库性能分析已禁用")

    def is_enabled(self) -> bool:
        """检查是否启用了数据库性能分析"""
        return self._enabled

    def record_query(
        self,
        sql: str,
        params: tuple | None = None,
        execution_time: float = 0.0,
        rows_affected: int = 0,
        rows_returned: int = 0,
        connection_time: float = 0.0,
        error_message: str | None = None,
    ) -> str:
        """
        记录数据库查询性能指标

        Args:
            sql: SQL查询语句
            params: 查询参数
            execution_time: 执行时间(毫秒)
            rows_affected: 影响的行数
            rows_returned: 返回的行数
            connection_time: 连接时间(毫秒)
            error_message: 错误信息

        Returns:
            str: 查询ID
        """
        if not self._enabled:
            return ""

        try:
            # 生成查询ID
            query_id = self._generate_query_id(sql, params)

            # 分析查询类型和表名
            operation_type, table_name = self._analyze_query(sql)

            # 检查是否为慢查询
            is_slow_query = execution_time >= self._slow_query_threshold

            # 创建查询指标
            metric = DatabaseQueryMetric(
                query_id=query_id,
                sql=sql,
                params=params,
                execution_time=execution_time,
                rows_affected=rows_affected,
                rows_returned=rows_returned,
                connection_time=connection_time,
                operation_type=operation_type,
                table_name=table_name,
                is_slow_query=is_slow_query,
                error_message=error_message,
            )

            # 保存指标
            self._add_query_metric(metric)

            # 记录慢查询日志
            if is_slow_query:
                self._logger.warning(
                    f"慢查询检测 [{query_id}]: {execution_time:.2f}ms - {sql[:100]}"
                )

            return query_id

        except Exception as e:
            self._logger.error(f"记录数据库查询指标失败: {e}")
            return ""

    def record_connection(self, connection_id: str, connect_time: float = 0.0) -> None:
        """
        记录数据库连接性能指标

        Args:
            connection_id: 连接ID
            connect_time: 连接时间(毫秒)
        """
        if not self._enabled:
            return

        try:
            metric = DatabaseConnectionMetric(
                connection_id=connection_id, connect_time=connect_time
            )

            self._connection_metrics[connection_id] = metric

            self._logger.debug(f"记录数据库连接: {connection_id}")

        except Exception as e:
            self._logger.error(f"记录数据库连接指标失败: {e}")

    def close_connection(self, connection_id: str, close_time: float = 0.0) -> None:
        """
        记录数据库连接关闭

        Args:
            connection_id: 连接ID
            close_time: 关闭时间(毫秒)
        """
        if not self._enabled or connection_id not in self._connection_metrics:
            return

        try:
            metric = self._connection_metrics[connection_id]
            metric.close_time = close_time
            metric.closed_at = datetime.now()
            metric.is_active = False

            self._logger.debug(f"关闭数据库连接: {connection_id}")

        except Exception as e:
            self._logger.error(f"记录数据库连接关闭失败: {e}")

    def get_slow_queries(
        self, limit: int = 50, time_range: timedelta | None = None
    ) -> list[DatabaseQueryMetric]:
        """
        获取慢查询列表

        Args:
            limit: 返回数量限制
            time_range: 时间范围过滤

        Returns:
            List[DatabaseQueryMetric]: 慢查询列表
        """
        slow_queries = [m for m in self._query_metrics if m.is_slow_query]

        # 时间范围过滤
        if time_range:
            cutoff_time = datetime.now() - time_range
            slow_queries = [q for q in slow_queries if q.timestamp >= cutoff_time]

        # 按执行时间倒序排列
        slow_queries.sort(key=lambda q: q.execution_time, reverse=True)

        return slow_queries[:limit]

    def get_query_statistics(
        self, table_name: str | None = None, operation_type: str | None = None
    ) -> dict[str, Any]:
        """
        获取查询统计信息

        Args:
            table_name: 表名过滤
            operation_type: 操作类型过滤

        Returns:
            Dict[str, Any]: 查询统计信息
        """
        metrics = self._query_metrics

        # 应用过滤条件
        if table_name:
            metrics = [m for m in metrics if m.table_name == table_name]
        if operation_type:
            metrics = [m for m in metrics if m.operation_type == operation_type]

        if not metrics:
            return {
                "total_queries": 0,
                "avg_execution_time_ms": 0.0,
                "min_execution_time_ms": 0.0,
                "max_execution_time_ms": 0.0,
                "slow_queries_count": 0,
                "error_queries_count": 0,
            }

        execution_times = [m.execution_time for m in metrics]
        slow_queries = [m for m in metrics if m.is_slow_query]
        error_queries = [m for m in metrics if m.error_message]

        return {
            "total_queries": len(metrics),
            "avg_execution_time_ms": sum(execution_times) / len(execution_times),
            "min_execution_time_ms": min(execution_times),
            "max_execution_time_ms": max(execution_times),
            "total_execution_time_ms": sum(execution_times),
            "slow_queries_count": len(slow_queries),
            "error_queries_count": len(error_queries),
            "slow_query_percentage": (len(slow_queries) / len(metrics)) * 100,
        }

    def get_table_statistics(self) -> dict[str, dict[str, Any]]:
        """
        获取按表分组的查询统计

        Returns:
            Dict[str, Dict[str, Any]]: 按表分组的统计信息
        """
        table_stats = {}
        tables = {m.table_name for m in self._query_metrics if m.table_name}

        for table in tables:
            table_stats[table] = self.get_query_statistics(table_name=table)

        return table_stats

    def get_operation_statistics(self) -> dict[str, dict[str, Any]]:
        """
        获取按操作类型分组的查询统计

        Returns:
            Dict[str, Dict[str, Any]]: 按操作类型分组的统计信息
        """
        operation_stats = {}
        operations = {m.operation_type for m in self._query_metrics}

        for operation in operations:
            operation_stats[operation] = self.get_query_statistics(
                operation_type=operation
            )

        return operation_stats

    def get_connection_statistics(self) -> dict[str, Any]:
        """
        获取数据库连接统计信息

        Returns:
            Dict[str, Any]: 连接统计信息
        """
        if not self._connection_metrics:
            return {
                "total_connections": 0,
                "active_connections": 0,
                "avg_connect_time_ms": 0.0,
                "avg_close_time_ms": 0.0,
            }

        connections = list(self._connection_metrics.values())
        active_connections = [c for c in connections if c.is_active]
        closed_connections = [c for c in connections if not c.is_active]

        connect_times = [c.connect_time for c in connections if c.connect_time > 0]
        close_times = [c.close_time for c in closed_connections if c.close_time > 0]

        return {
            "total_connections": len(connections),
            "active_connections": len(active_connections),
            "closed_connections": len(closed_connections),
            "avg_connect_time_ms": (
                sum(connect_times) / len(connect_times) if connect_times else 0.0
            ),
            "avg_close_time_ms": (
                sum(close_times) / len(close_times) if close_times else 0.0
            ),
        }

    def generate_performance_report(self) -> dict[str, Any]:
        """
        生成数据库性能报告

        Returns:
            Dict[str, Any]: 完整的数据库性能报告
        """
        try:
            # 基础统计
            overall_stats = self.get_query_statistics()
            table_stats = self.get_table_statistics()
            operation_stats = self.get_operation_statistics()
            connection_stats = self.get_connection_statistics()

            # 慢查询分析
            slow_queries = self.get_slow_queries(limit=10)
            slow_query_summary = [
                {
                    "query_id": q.query_id,
                    "sql": q.sql[:100] + "..." if len(q.sql) > 100 else q.sql,
                    "execution_time_ms": q.execution_time,
                    "table_name": q.table_name,
                    "operation_type": q.operation_type,
                    "timestamp": q.timestamp.isoformat(),
                }
                for q in slow_queries
            ]

            # 性能建议
            recommendations = self._generate_performance_recommendations(overall_stats)

            return {
                "report_timestamp": datetime.now().isoformat(),
                "overall_statistics": overall_stats,
                "table_statistics": table_stats,
                "operation_statistics": operation_stats,
                "connection_statistics": connection_stats,
                "slow_queries": slow_query_summary,
                "recommendations": recommendations,
                "analyzer_config": {
                    "slow_query_threshold_ms": self._slow_query_threshold,
                    "max_metrics": self._max_metrics,
                    "enabled": self._enabled,
                },
            }

        except Exception as e:
            self._logger.error(f"生成数据库性能报告失败: {e}")
            return {"error": str(e)}

    def _add_query_metric(self, metric: DatabaseQueryMetric) -> None:
        """添加查询指标"""
        self._query_metrics.append(metric)

        # 按查询模式分组
        pattern = self._extract_query_pattern(metric.sql)
        self._query_patterns[pattern].append(metric)

        # 限制指标数量
        if len(self._query_metrics) > self._max_metrics:
            # 删除最旧的指标
            self._query_metrics = sorted(
                self._query_metrics, key=lambda m: m.timestamp, reverse=True
            )[: self._max_metrics]

    def _generate_query_id(self, sql: str, params: tuple | None) -> str:
        """生成查询ID"""
        import hashlib

        content = f"{sql}_{params}_{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _analyze_query(self, sql: str) -> tuple[str, str | None]:
        """
        分析查询类型和表名

        Args:
            sql: SQL查询语句

        Returns:
            Tuple[str, Optional[str]]: (操作类型, 表名)
        """
        sql_upper = sql.strip().upper()

        # 确定操作类型
        if sql_upper.startswith("SELECT"):
            operation_type = "SELECT"
        elif sql_upper.startswith("INSERT"):
            operation_type = "INSERT"
        elif sql_upper.startswith("UPDATE"):
            operation_type = "UPDATE"
        elif sql_upper.startswith("DELETE"):
            operation_type = "DELETE"
        elif sql_upper.startswith("CREATE"):
            operation_type = "CREATE"
        elif sql_upper.startswith("DROP"):
            operation_type = "DROP"
        elif sql_upper.startswith("ALTER"):
            operation_type = "ALTER"
        else:
            operation_type = "OTHER"

        # 提取表名
        table_name = self._extract_table_name(sql, operation_type)

        return operation_type, table_name

    def _extract_table_name(self, sql: str, operation_type: str) -> str | None:
        """提取SQL语句中的表名"""
        try:
            sql_upper = sql.strip().upper()

            if operation_type == "SELECT":
                # SELECT ... FROM table_name
                match = re.search(r"FROM\s+(\w+)", sql_upper)
            elif operation_type == "INSERT":
                # INSERT INTO table_name
                match = re.search(r"INSERT\s+INTO\s+(\w+)", sql_upper)
            elif operation_type == "UPDATE":
                # UPDATE table_name SET
                match = re.search(r"UPDATE\s+(\w+)\s+SET", sql_upper)
            elif operation_type == "DELETE":
                # DELETE FROM table_name
                match = re.search(r"DELETE\s+FROM\s+(\w+)", sql_upper)
            else:
                match = None

            return match.group(1) if match else None

        except Exception:
            return None

    def _extract_query_pattern(self, sql: str) -> str:
        """提取查询模式(去除具体参数值)"""
        # 简单的模式提取,将数字和字符串替换为占位符
        pattern = re.sub(r"'[^']*'", "'?'", sql)  # 字符串参数
        pattern = re.sub(r"\b\d+\b", "?", pattern)  # 数字参数
        return pattern.strip()

    def _generate_performance_recommendations(self, stats: dict[str, Any]) -> list[str]:
        """生成性能优化建议"""
        recommendations = []

        try:
            # 慢查询建议
            if stats.get("slow_query_percentage", 0) > 10:
                recommendations.append(
                    f"慢查询比例较高({stats['slow_query_percentage']:.1f}%),"
                    "建议优化查询语句或添加索引"
                )

            # 平均执行时间建议
            avg_time = stats.get("avg_execution_time_ms", 0)
            if avg_time > 500:
                recommendations.append(
                    f"平均查询时间较长({avg_time:.1f}ms),建议优化数据库结构"
                )

            # 错误查询建议
            error_count = stats.get("error_queries_count", 0)
            if error_count > 0:
                recommendations.append(f"发现{error_count}个查询错误,建议检查SQL语句")

            if not recommendations:
                recommendations.append("数据库性能表现良好")

        except Exception as e:
            self._logger.warning(f"生成性能建议时出错: {e}")
            recommendations.append("性能分析出现异常,建议检查监控数据")

        return recommendations

    def clear_metrics(self) -> None:
        """清空所有性能指标"""
        self._query_metrics.clear()
        self._connection_metrics.clear()
        self._query_patterns.clear()
        self._logger.info("数据库性能指标已清空")


# 全局数据库性能分析器实例
database_performance_analyzer = DatabasePerformanceAnalyzer()
