"""
MiniCRM 查询缓存管理器

专门负责查询结果缓存管理,包括:
- 查询结果缓存
- 缓存策略管理
- 缓存统计和监控
- 缓存清理和过期处理
"""

import logging
from datetime import datetime, timedelta
from typing import Any


class QueryCacheManager:
    """
    查询缓存管理器

    专门负责管理查询结果的缓存,提高查询性能.
    """

    def __init__(self, database_manager):
        """
        初始化查询缓存管理器

        Args:
            database_manager: 数据库管理器实例
        """
        self._db = database_manager
        self._logger = logging.getLogger(__name__)

        # 查询缓存
        self._query_cache: dict[str, Any] = {}
        self._cache_stats = {"hits": 0, "misses": 0}
        self._cache_max_size = 1000
        self._cache_ttl = timedelta(minutes=30)

        self._enabled = True

    def enable(self) -> None:
        """启用查询缓存"""
        self._enabled = True
        self._logger.info("查询缓存已启用")

    def disable(self) -> None:
        """禁用查询缓存"""
        self._enabled = False
        self._logger.info("查询缓存已禁用")

    def is_enabled(self) -> bool:
        """检查缓存是否启用"""
        return self._enabled

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

        # 生成缓存键
        cache_key = self._generate_cache_key(sql, params)

        # 检查缓存
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            self._cache_stats["hits"] += 1
            return cached_result

        # 执行查询
        self._cache_stats["misses"] += 1
        result = self._db.execute_query(sql, params)

        # 存入缓存
        self._put_to_cache(cache_key, result)

        return result

    def get_cache_statistics(self) -> dict[str, Any]:
        """
        获取查询缓存统计信息

        Returns:
            Dict[str, Any]: 缓存统计信息
        """
        total_requests = self._cache_stats["hits"] + self._cache_stats["misses"]
        hit_rate = (
            (self._cache_stats["hits"] / total_requests * 100)
            if total_requests > 0
            else 0.0
        )

        return {
            "cache_size": len(self._query_cache),
            "max_cache_size": self._cache_max_size,
            "cache_hits": self._cache_stats["hits"],
            "cache_misses": self._cache_stats["misses"],
            "hit_rate_percent": hit_rate,
            "cache_ttl_minutes": self._cache_ttl.total_seconds() / 60,
        }

    def clear_cache(self) -> None:
        """清空查询缓存"""
        self._query_cache.clear()
        self._cache_stats = {"hits": 0, "misses": 0}
        self._logger.info("查询缓存已清空")

    def set_cache_config(
        self, max_size: int | None = None, ttl_minutes: int | None = None
    ) -> None:
        """
        设置缓存配置

        Args:
            max_size: 最大缓存大小
            ttl_minutes: 缓存生存时间(分钟)
        """
        if max_size is not None:
            self._cache_max_size = max_size
            self._logger.info(f"缓存最大大小设置为: {max_size}")

        if ttl_minutes is not None:
            self._cache_ttl = timedelta(minutes=ttl_minutes)
            self._logger.info(f"缓存TTL设置为: {ttl_minutes}分钟")

        # 如果缓存大小超过新的限制,清理多余的项
        if len(self._query_cache) > self._cache_max_size:
            self._cleanup_excess_cache()

    def cleanup_expired_cache(self) -> int:
        """
        清理过期的缓存项

        Returns:
            int: 清理的缓存项数量
        """
        if not self._enabled:
            return 0

        expired_keys = []
        current_time = datetime.now()

        for cache_key, cached_item in self._query_cache.items():
            if current_time - cached_item["timestamp"] >= self._cache_ttl:
                expired_keys.append(cache_key)

        # 删除过期项
        for key in expired_keys:
            del self._query_cache[key]

        if expired_keys:
            self._logger.info(f"清理了 {len(expired_keys)} 个过期缓存项")

        return len(expired_keys)

    def invalidate_cache_by_pattern(self, pattern: str) -> int:
        """
        根据模式失效缓存

        Args:
            pattern: 匹配模式(简单的字符串包含匹配)

        Returns:
            int: 失效的缓存项数量
        """
        invalidated_keys = []

        for cache_key in self._query_cache.keys():
            if pattern in cache_key:
                invalidated_keys.append(cache_key)

        # 删除匹配的项
        for key in invalidated_keys:
            del self._query_cache[key]

        if invalidated_keys:
            self._logger.info(
                f"根据模式 '{pattern}' 失效了 {len(invalidated_keys)} 个缓存项"
            )

        return len(invalidated_keys)

    def _generate_cache_key(self, sql: str, params: tuple) -> str:
        """生成缓存键"""
        import hashlib

        content = f"{sql}_{params}"
        return hashlib.md5(content.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Any | None:
        """从缓存获取数据"""
        if cache_key in self._query_cache:
            cached_item = self._query_cache[cache_key]
            # 检查是否过期
            if datetime.now() - cached_item["timestamp"] < self._cache_ttl:
                return cached_item["data"]
            else:
                # 删除过期项
                del self._query_cache[cache_key]
        return None

    def _put_to_cache(self, cache_key: str, data: Any) -> None:
        """将数据存入缓存"""
        # 检查缓存大小限制
        if len(self._query_cache) >= self._cache_max_size:
            # 删除最旧的项
            self._cleanup_excess_cache()

        self._query_cache[cache_key] = {
            "data": data,
            "timestamp": datetime.now(),
        }

    def _cleanup_excess_cache(self) -> None:
        """清理多余的缓存项"""
        if len(self._query_cache) <= self._cache_max_size:
            return

        # 按时间戳排序,删除最旧的项
        sorted_items = sorted(
            self._query_cache.items(), key=lambda x: x[1]["timestamp"]
        )

        # 计算需要删除的项数
        items_to_remove = len(self._query_cache) - self._cache_max_size + 1

        # 删除最旧的项
        for i in range(items_to_remove):
            key_to_remove = sorted_items[i][0]
            del self._query_cache[key_to_remove]

        self._logger.debug(f"清理了 {items_to_remove} 个缓存项以释放空间")

    def get_cache_keys(self) -> list[str]:
        """获取所有缓存键"""
        return list(self._query_cache.keys())

    def get_cache_info(self, cache_key: str) -> dict[str, Any] | None:
        """
        获取特定缓存项的信息

        Args:
            cache_key: 缓存键

        Returns:
            Dict[str, Any]: 缓存项信息,如果不存在则返回None
        """
        if cache_key in self._query_cache:
            cached_item = self._query_cache[cache_key]
            return {
                "key": cache_key,
                "timestamp": cached_item["timestamp"],
                "age_seconds": (
                    datetime.now() - cached_item["timestamp"]
                ).total_seconds(),
                "data_size": len(str(cached_item["data"])),
                "expired": datetime.now() - cached_item["timestamp"] >= self._cache_ttl,
            }
        return None
