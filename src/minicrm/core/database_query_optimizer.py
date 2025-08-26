"""
MiniCRM 数据库查询优化器

提供数据库查询性能分析和优化的协调功能,包括:
- 协调查询分析、索引推荐和缓存管理
- 生成综合性能优化报告
- 提供统一的优化接口
"""

import logging
from datetime import datetime
from typing import Any

from .database_performance_analyzer import database_performance_analyzer
from .index_recommender import IndexRecommendation, IndexRecommender
from .query_analyzer import QueryAnalyzer, QueryOptimization, QueryPlan
from .query_cache_manager import QueryCacheManager


class DatabaseQueryOptimizer:
    """
    数据库查询优化器

    协调查询分析、索引推荐和缓存管理,提供统一的优化接口.
    """

    def __init__(self, database_manager):
        """
        初始化查询优化器

        Args:
            database_manager: 数据库管理器实例
        """
        self._db = database_manager
        self._logger = logging.getLogger(__name__)

        # 初始化子组件
        self._query_analyzer = QueryAnalyzer(database_manager)
        self._index_recommender = IndexRecommender(database_manager)
        self._cache_manager = QueryCacheManager(database_manager)

        self._enabled = True

        self._logger.debug("数据库查询优化器初始化完成")

    def enable(self) -> None:
        """启用查询优化器"""
        self._enabled = True
        self._logger.info("数据库查询优化器已启用")

    def disable(self) -> None:
        """禁用查询优化器"""
        self._enabled = False
        self._logger.info("数据库查询优化器已禁用")

    def analyze_query_plan(self, sql: str) -> QueryPlan:
        """
        分析查询执行计划

        Args:
            sql: SQL查询语句

        Returns:
            QueryPlan: 查询执行计划分析结果
        """
        if not self._enabled:
            return QueryPlan("", sql)

        return self._query_analyzer.analyze_query_plan(sql)

    def optimize_query(self, sql: str) -> QueryOptimization:
        """
        优化查询语句

        Args:
            sql: 原始SQL语句

        Returns:
            QueryOptimization: 查询优化建议
        """
        if not self._enabled:
            return QueryOptimization(sql, sql, "none", "优化器已禁用")

        return self._query_analyzer.optimize_query(sql)

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
        if not self._enabled:
            return []

        return self._index_recommender.recommend_indexes(analysis_period_days)

    def create_recommended_indexes(self, max_indexes: int = 5) -> list[str]:
        """
        创建推荐的索引

        Args:
            max_indexes: 最大创建索引数量

        Returns:
            List[str]: 成功创建的索引名称列表
        """
        if not self._enabled:
            return []

        return self._index_recommender.create_recommended_indexes(max_indexes)

    def get_cache_statistics(self) -> dict[str, Any]:
        """
        获取查询缓存统计信息

        Returns:
            Dict[str, Any]: 缓存统计信息
        """
        return self._cache_manager.get_cache_statistics()

    def clear_cache(self) -> None:
        """清空查询缓存"""
        self._cache_manager.clear_cache()

    def execute_cached_query(self, sql: str, params: tuple = ()) -> list[Any]:
        """
        执行带缓存的查询

        Args:
            sql: SQL查询语句
            params: 查询参数

        Returns:
            List[Any]: 查询结果
        """
        if not self._enabled:
            return self._db.execute_query(sql, params)

        return self._cache_manager.execute_cached_query(sql, params)

    def generate_optimization_report(self) -> dict[str, Any]:
        """
        生成查询优化报告

        Returns:
            Dict[str, Any]: 优化报告
        """
        try:
            # 获取数据库性能分析
            db_report = database_performance_analyzer.generate_performance_report()

            # 获取缓存统计
            cache_stats = self.get_cache_statistics()

            # 分析索引使用情况
            index_usage = self._index_recommender.analyze_index_usage()

            # 获取推荐索引
            recommended_indexes = self.recommend_indexes()

            # 生成优化建议
            optimization_suggestions = self._generate_global_optimization_suggestions(
                db_report, cache_stats, index_usage
            )

            return {
                "report_timestamp": datetime.now().isoformat(),
                "database_performance": db_report.get("overall_statistics", {}),
                "cache_statistics": cache_stats,
                "index_usage": index_usage,
                "recommended_indexes": [
                    {
                        "table": rec.table_name,
                        "columns": rec.columns,
                        "reason": rec.reason,
                        "benefit": rec.estimated_benefit,
                        "sql": rec.creation_sql,
                    }
                    for rec in recommended_indexes
                ],
                "optimization_suggestions": optimization_suggestions,
            }

        except Exception as e:
            self._logger.error(f"生成优化报告失败: {e}")
            return {"error": str(e)}

    def _generate_global_optimization_suggestions(
        self,
        db_report: dict[str, Any],
        cache_stats: dict[str, Any],
        index_usage: dict[str, Any],
    ) -> list[str]:
        """生成全局优化建议"""
        suggestions = []

        try:
            # 数据库性能建议
            if (
                db_report.get("overall_statistics", {}).get("slow_query_percentage", 0)
                > 10
            ):
                suggestions.append("慢查询比例较高,建议优化查询语句或添加索引")

            # 缓存建议
            if cache_stats.get("hit_rate_percent", 0) < 50:
                suggestions.append("查询缓存命中率较低,考虑调整缓存策略或增加缓存大小")

            # 索引建议
            tables_without_indexes = sum(
                1
                for table_info in index_usage.values()
                if table_info["index_count"] == 0
            )

            if tables_without_indexes > 0:
                suggestions.append(
                    f"有{tables_without_indexes}个表没有索引,考虑为常用查询列添加索引"
                )

            # 推荐索引建议
            recommended_indexes = self.recommend_indexes()
            if len(recommended_indexes) > 0:
                suggestions.append(
                    f"系统推荐创建{len(recommended_indexes)}个索引以提高查询性能"
                )

            if not suggestions:
                suggestions.append("数据库性能表现良好,无需特别优化")

        except Exception as e:
            self._logger.warning(f"生成优化建议时出错: {e}")
            suggestions.append("优化分析出现异常,建议检查系统状态")

        return suggestions


# 全局数据库查询优化器实例
database_query_optimizer = None


def get_query_optimizer(database_manager=None):
    """获取查询优化器实例"""
    global database_query_optimizer
    if database_query_optimizer is None and database_manager:
        database_query_optimizer = DatabaseQueryOptimizer(database_manager)
    return database_query_optimizer
