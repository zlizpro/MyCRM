"""
MiniCRM 缓存管理器

负责分析服务的缓存管理:
- 内存缓存
- TTL过期管理
- 缓存统计
- 缓存清理
"""

import logging
import time
from typing import Any


class CacheManager:
    """
    缓存管理器

    提供简单的内存缓存功能,支持TTL过期机制.
    """

    def __init__(self, cache_ttl: int = 300):
        """
        初始化缓存管理器

        Args:
            cache_ttl: 缓存生存时间(秒),默认5分钟
        """
        self._cache: dict[str, dict[str, Any]] = {}
        self._cache_ttl = cache_ttl
        self._logger = logging.getLogger(__name__)

        self._logger.debug(f"缓存管理器初始化完成,TTL: {cache_ttl}秒")

    def get(self, key: str) -> Any | None:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值,如果不存在或已过期则返回None
        """
        if key not in self._cache:
            return None

        cache_entry = self._cache[key]
        current_time = time.time()

        # 检查是否过期
        if current_time - cache_entry["timestamp"] > self._cache_ttl:
            del self._cache[key]
            self._logger.debug(f"缓存过期并删除: {key}")
            return None

        self._logger.debug(f"缓存命中: {key}")
        return cache_entry["value"]

    def set(self, key: str, value: Any) -> None:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
        """
        self._cache[key] = {"value": value, "timestamp": time.time()}
        self._logger.debug(f"缓存设置: {key}")

    def clear(self, pattern: str | None = None) -> None:
        """
        清除缓存

        Args:
            pattern: 缓存键模式,如果为None则清除所有缓存
        """
        if pattern is None:
            self._cache.clear()
            self._logger.info("清除所有缓存")
        else:
            keys_to_remove = [key for key in self._cache if pattern in key]
            for key in keys_to_remove:
                del self._cache[key]
            self._logger.info(
                f"清除匹配模式 '{pattern}' 的缓存,共{len(keys_to_remove)}项"
            )

    def get_statistics(self) -> dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            Dict[str, Any]: 缓存统计数据
        """
        current_time = time.time()
        valid_entries = 0
        expired_entries = 0

        for cache_entry in self._cache.values():
            if current_time - cache_entry["timestamp"] > self._cache_ttl:
                expired_entries += 1
            else:
                valid_entries += 1

        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_ttl": self._cache_ttl,
        }
