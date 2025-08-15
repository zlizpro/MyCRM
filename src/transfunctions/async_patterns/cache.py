"""
Transfunctions - 缓存异步操作

提供统一的缓存操作接口。
"""

from typing import Any

from .base import AsyncPatternMixin


class UnifiedCacheOperations(AsyncPatternMixin):
    """统一的缓存操作接口

    提供同步和异步缓存操作的统一接口。
    """

    def __init__(self):
        super().__init__()
        self._sync_cache: dict[str, Any] = {}

    def get(self, key: str) -> Any | None:
        """统一的缓存获取接口"""

        def sync_get():
            return self._sync_cache.get(key)

        async def async_get():
            # 在实际项目中，这里可能是Redis异步操作
            return await self._wrap_sync_to_async(sync_get)()

        return self.sync_or_async(sync_get, async_get)()

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """统一的缓存设置接口"""

        def sync_set():
            self._sync_cache[key] = value
            # 在实际项目中，这里可能需要处理TTL

        async def async_set():
            await self._wrap_sync_to_async(sync_set)()

        return self.sync_or_async(sync_set, async_set)()


def create_unified_cache():
    """创建统一缓存操作实例"""
    return UnifiedCacheOperations()
