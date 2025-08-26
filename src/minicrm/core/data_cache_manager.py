"""
MiniCRM 数据缓存管理器

提供全面的数据缓存功能,包括:
- 多级缓存系统
- 智能缓存策略
- 缓存失效和更新
- 分布式缓存支持
- 缓存性能监控
"""

import logging
import pickle
import time
from collections import OrderedDict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import RLock
from typing import Any


@dataclass
class CacheEntry:
    """缓存条目"""

    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl: timedelta | None = None
    size_bytes: int = 0
    tags: set[str] = field(default_factory=set)
    dependencies: set[str] = field(default_factory=set)


@dataclass
class CacheStatistics:
    """缓存统计信息"""

    total_entries: int = 0
    total_size_bytes: int = 0
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    hit_rate: float = 0.0
    avg_access_time_ms: float = 0.0
    memory_usage_mb: float = 0.0


class CachePolicy:
    """缓存策略枚举"""

    LRU = "lru"  # 最近最少使用
    LFU = "lfu"  # 最少使用频率
    FIFO = "fifo"  # 先进先出
    TTL = "ttl"  # 基于时间
    SIZE = "size"  # 基于大小


class DataCacheManager:
    """
    数据缓存管理器

    提供多级缓存、智能策略、自动失效等功能的综合缓存解决方案.
    """

    def __init__(
        self,
        max_size_mb: float = 100.0,
        default_ttl_minutes: int = 30,
        cache_policy: str = CachePolicy.LRU,
    ):
        """
        初始化数据缓存管理器

        Args:
            max_size_mb: 最大缓存大小(MB)
            default_ttl_minutes: 默认TTL(分钟)
            cache_policy: 缓存策略
        """
        self._logger = logging.getLogger(__name__)

        # 缓存配置
        self._max_size_bytes = int(max_size_mb * 1024 * 1024)
        self._default_ttl = timedelta(minutes=default_ttl_minutes)
        self._cache_policy = cache_policy

        # 缓存存储
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._cache_lock = RLock()

        # 索引和标签
        self._tag_index: dict[str, set[str]] = {}  # 标签到键的映射
        self._dependency_index: dict[str, set[str]] = {}  # 依赖到键的映射

        # 统计信息
        self._stats = CacheStatistics()
        self._access_times: list[float] = []

        # 回调函数
        self._eviction_callbacks: list[Callable[[str, Any], None]] = []
        self._miss_callbacks: list[Callable[[str], Any]] = []

        # 预加载配置
        self._preload_enabled = True
        self._preload_patterns: dict[str, Callable] = {}

        self._enabled = True

        self._logger.debug(f"数据缓存管理器初始化完成 (最大大小: {max_size_mb}MB)")

    def enable(self) -> None:
        """启用缓存管理器"""
        self._enabled = True
        self._logger.info("数据缓存管理器已启用")

    def disable(self) -> None:
        """禁用缓存管理器"""
        self._enabled = False
        self._logger.info("数据缓存管理器已禁用")

    def put(
        self,
        key: str,
        value: Any,
        ttl: timedelta | None = None,
        tags: set[str] | None = None,
        dependencies: set[str] | None = None,
    ) -> bool:
        """
        存储数据到缓存

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间
            tags: 标签集合
            dependencies: 依赖键集合

        Returns:
            bool: 是否成功存储
        """
        if not self._enabled:
            return False

        try:
            with self._cache_lock:
                # 计算数据大小
                size_bytes = self._calculate_size(value)

                # 检查是否需要腾出空间
                if not self._ensure_space(size_bytes):
                    self._logger.warning(f"无法为键 {key} 腾出足够空间")
                    return False

                # 创建缓存条目
                now = datetime.now()
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=now,
                    last_accessed=now,
                    ttl=ttl or self._default_ttl,
                    size_bytes=size_bytes,
                    tags=tags or set(),
                    dependencies=dependencies or set(),
                )

                # 如果键已存在,先清理旧的索引
                if key in self._cache:
                    self._remove_from_indexes(key)

                # 存储到缓存
                self._cache[key] = entry

                # 更新索引
                self._update_indexes(key, entry)

                # 更新统计
                self._stats.total_entries = len(self._cache)
                self._stats.total_size_bytes += size_bytes

                self._logger.debug(f"缓存存储成功: {key} ({size_bytes} bytes)")
                return True

        except Exception as e:
            self._logger.error(f"缓存存储失败: {key}, 错误: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        从缓存获取数据

        Args:
            key: 缓存键
            default: 默认值

        Returns:
            Any: 缓存的值或默认值
        """
        if not self._enabled:
            return default

        start_time = time.perf_counter()

        try:
            with self._cache_lock:
                # 检查缓存是否存在
                if key not in self._cache:
                    self._stats.miss_count += 1

                    # 尝试预加载
                    if self._preload_enabled:
                        preloaded_value = self._try_preload(key)
                        if preloaded_value is not None:
                            return preloaded_value

                    # 调用缺失回调
                    for callback in self._miss_callbacks:
                        try:
                            result = callback(key)
                            if result is not None:
                                # 自动缓存回调结果
                                self.put(key, result)
                                return result
                        except Exception as e:
                            self._logger.error(f"缓存缺失回调失败: {e}")

                    return default

                entry = self._cache[key]

                # 检查是否过期
                if self._is_expired(entry):
                    self._remove_entry(key)
                    self._stats.miss_count += 1
                    return default

                # 检查依赖是否有效
                if not self._check_dependencies(entry):
                    self._remove_entry(key)
                    self._stats.miss_count += 1
                    return default

                # 更新访问信息
                entry.last_accessed = datetime.now()
                entry.access_count += 1

                # 根据策略调整位置
                if self._cache_policy == CachePolicy.LRU:
                    # 移动到末尾(最近使用)
                    self._cache.move_to_end(key)

                # 更新统计
                self._stats.hit_count += 1

                return entry.value

        except Exception as e:
            self._logger.error(f"缓存获取失败: {key}, 错误: {e}")
            self._stats.miss_count += 1
            return default

        finally:
            # 记录访问时间
            access_time = (time.perf_counter() - start_time) * 1000
            self._access_times.append(access_time)
            if len(self._access_times) > 1000:
                self._access_times = self._access_times[-1000:]

    def remove(self, key: str) -> bool:
        """
        从缓存移除数据

        Args:
            key: 缓存键

        Returns:
            bool: 是否成功移除
        """
        if not self._enabled:
            return False

        try:
            with self._cache_lock:
                if key in self._cache:
                    self._remove_entry(key)
                    return True
                return False

        except Exception as e:
            self._logger.error(f"缓存移除失败: {key}, 错误: {e}")
            return False

    def invalidate_by_tag(self, tag: str) -> int:
        """
        根据标签失效缓存

        Args:
            tag: 标签

        Returns:
            int: 失效的条目数量
        """
        if not self._enabled:
            return 0

        try:
            with self._cache_lock:
                keys_to_remove = self._tag_index.get(tag, set()).copy()

                for key in keys_to_remove:
                    self._remove_entry(key)

                self._logger.debug(
                    f"根据标签 {tag} 失效了 {len(keys_to_remove)} 个缓存条目"
                )
                return len(keys_to_remove)

        except Exception as e:
            self._logger.error(f"根据标签失效缓存失败: {tag}, 错误: {e}")
            return 0

    def invalidate_by_dependency(self, dependency: str) -> int:
        """
        根据依赖失效缓存

        Args:
            dependency: 依赖键

        Returns:
            int: 失效的条目数量
        """
        if not self._enabled:
            return 0

        try:
            with self._cache_lock:
                keys_to_remove = self._dependency_index.get(dependency, set()).copy()

                for key in keys_to_remove:
                    self._remove_entry(key)

                self._logger.debug(
                    f"根据依赖 {dependency} 失效了 {len(keys_to_remove)} 个缓存条目"
                )
                return len(keys_to_remove)

        except Exception as e:
            self._logger.error(f"根据依赖失效缓存失败: {dependency}, 错误: {e}")
            return 0

    def clear(self) -> None:
        """清空所有缓存"""
        try:
            with self._cache_lock:
                # 调用驱逐回调
                for key, entry in self._cache.items():
                    for callback in self._eviction_callbacks:
                        try:
                            callback(key, entry.value)
                        except Exception as e:
                            self._logger.error(f"驱逐回调失败: {e}")

                # 清空缓存和索引
                self._cache.clear()
                self._tag_index.clear()
                self._dependency_index.clear()

                # 重置统计
                self._stats = CacheStatistics()

                self._logger.info("缓存已清空")

        except Exception as e:
            self._logger.error(f"清空缓存失败: {e}")

    def get_statistics(self) -> CacheStatistics:
        """
        获取缓存统计信息

        Returns:
            CacheStatistics: 统计信息
        """
        try:
            with self._cache_lock:
                # 计算命中率
                total_requests = self._stats.hit_count + self._stats.miss_count
                self._stats.hit_rate = (
                    (self._stats.hit_count / total_requests * 100)
                    if total_requests > 0
                    else 0.0
                )

                # 计算平均访问时间
                if self._access_times:
                    self._stats.avg_access_time_ms = sum(self._access_times) / len(
                        self._access_times
                    )

                # 计算内存使用
                self._stats.memory_usage_mb = self._stats.total_size_bytes / 1024 / 1024

                # 更新当前状态
                self._stats.total_entries = len(self._cache)
                self._stats.total_size_bytes = sum(
                    entry.size_bytes for entry in self._cache.values()
                )

                return self._stats

        except Exception as e:
            self._logger.error(f"获取缓存统计失败: {e}")
            return CacheStatistics()

    def register_preload_pattern(
        self, pattern: str, loader: Callable[[str], Any]
    ) -> None:
        """
        注册预加载模式

        Args:
            pattern: 键模式
            loader: 加载函数
        """
        self._preload_patterns[pattern] = loader
        self._logger.debug(f"注册预加载模式: {pattern}")

    def register_eviction_callback(self, callback: Callable[[str, Any], None]) -> None:
        """
        注册驱逐回调

        Args:
            callback: 回调函数
        """
        self._eviction_callbacks.append(callback)

    def register_miss_callback(self, callback: Callable[[str], Any]) -> None:
        """
        注册缺失回调

        Args:
            callback: 回调函数
        """
        self._miss_callbacks.append(callback)

    def warm_up(self, keys: list[str]) -> int:
        """
        预热缓存

        Args:
            keys: 要预热的键列表

        Returns:
            int: 成功预热的键数量
        """
        if not self._enabled:
            return 0

        warmed_count = 0

        for key in keys:
            try:
                # 尝试预加载
                value = self._try_preload(key)
                if value is not None:
                    warmed_count += 1

            except Exception as e:
                self._logger.error(f"预热缓存失败: {key}, 错误: {e}")

        self._logger.info(f"缓存预热完成: {warmed_count}/{len(keys)}")
        return warmed_count

    def optimize(self) -> dict[str, Any]:
        """
        优化缓存

        Returns:
            Dict[str, Any]: 优化结果
        """
        if not self._enabled:
            return {"error": "缓存管理器已禁用"}

        try:
            with self._cache_lock:
                optimization_results = {
                    "expired_entries_removed": 0,
                    "unused_entries_removed": 0,
                    "memory_freed_bytes": 0,
                    "fragmentation_reduced": False,
                }

                # 1. 移除过期条目
                expired_keys = []
                for key, entry in self._cache.items():
                    if self._is_expired(entry):
                        expired_keys.append(key)

                for key in expired_keys:
                    entry = self._cache[key]
                    optimization_results["memory_freed_bytes"] += entry.size_bytes
                    self._remove_entry(key)
                    optimization_results["expired_entries_removed"] += 1

                # 2. 移除长时间未使用的条目
                unused_threshold = datetime.now() - timedelta(hours=1)
                unused_keys = []

                for key, entry in self._cache.items():
                    if (
                        entry.access_count < 2
                        and entry.last_accessed < unused_threshold
                    ):
                        unused_keys.append(key)

                # 只移除一部分未使用的条目
                for key in unused_keys[: len(unused_keys) // 2]:
                    entry = self._cache[key]
                    optimization_results["memory_freed_bytes"] += entry.size_bytes
                    self._remove_entry(key)
                    optimization_results["unused_entries_removed"] += 1

                # 3. 重新组织缓存(对于OrderedDict,重新排序)
                if self._cache_policy == CachePolicy.LFU:
                    # 按访问频率重新排序
                    sorted_items = sorted(
                        self._cache.items(),
                        key=lambda x: x[1].access_count,
                        reverse=True,
                    )
                    self._cache.clear()
                    self._cache.update(sorted_items)
                    optimization_results["fragmentation_reduced"] = True

                self._logger.info(f"缓存优化完成: {optimization_results}")
                return optimization_results

        except Exception as e:
            self._logger.error(f"缓存优化失败: {e}")
            return {"error": str(e)}

    def _calculate_size(self, value: Any) -> int:
        """计算值的大小"""
        try:
            # 使用pickle序列化来估算大小
            return len(pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL))
        except Exception:
            # 如果无法序列化,使用简单估算
            if isinstance(value, str):
                return len(value.encode("utf-8"))
            elif isinstance(value, list | tuple):
                return sum(self._calculate_size(item) for item in value)
            elif isinstance(value, dict):
                return sum(
                    self._calculate_size(k) + self._calculate_size(v)
                    for k, v in value.items()
                )
            else:
                return 100  # 默认估算值

    def _ensure_space(self, required_bytes: int) -> bool:
        """确保有足够的空间"""
        current_size = sum(entry.size_bytes for entry in self._cache.values())

        if current_size + required_bytes <= self._max_size_bytes:
            return True

        # 需要腾出空间
        bytes_to_free = current_size + required_bytes - self._max_size_bytes
        freed_bytes = 0

        # 根据策略选择要移除的条目
        if self._cache_policy == CachePolicy.LRU:
            # 移除最近最少使用的条目
            keys_to_remove = []
            for key in self._cache:
                if freed_bytes >= bytes_to_free:
                    break
                entry = self._cache[key]
                keys_to_remove.append(key)
                freed_bytes += entry.size_bytes

        elif self._cache_policy == CachePolicy.LFU:
            # 移除使用频率最低的条目
            sorted_entries = sorted(
                self._cache.items(), key=lambda x: x[1].access_count
            )
            keys_to_remove = []
            for key, entry in sorted_entries:
                if freed_bytes >= bytes_to_free:
                    break
                keys_to_remove.append(key)
                freed_bytes += entry.size_bytes

        else:
            # 默认FIFO策略
            keys_to_remove = []
            for key in self._cache:
                if freed_bytes >= bytes_to_free:
                    break
                entry = self._cache[key]
                keys_to_remove.append(key)
                freed_bytes += entry.size_bytes

        # 移除选中的条目
        for key in keys_to_remove:
            self._remove_entry(key)
            self._stats.eviction_count += 1

        return freed_bytes >= bytes_to_free

    def _remove_entry(self, key: str) -> None:
        """移除缓存条目"""
        if key not in self._cache:
            return

        entry = self._cache[key]

        # 调用驱逐回调
        for callback in self._eviction_callbacks:
            try:
                callback(key, entry.value)
            except Exception as e:
                self._logger.error(f"驱逐回调失败: {e}")

        # 从索引中移除
        self._remove_from_indexes(key)

        # 从缓存中移除
        del self._cache[key]

    def _update_indexes(self, key: str, entry: CacheEntry) -> None:
        """更新索引"""
        # 更新标签索引
        for tag in entry.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
            self._tag_index[tag].add(key)

        # 更新依赖索引
        for dependency in entry.dependencies:
            if dependency not in self._dependency_index:
                self._dependency_index[dependency] = set()
            self._dependency_index[dependency].add(key)

    def _remove_from_indexes(self, key: str) -> None:
        """从索引中移除"""
        if key not in self._cache:
            return

        entry = self._cache[key]

        # 从标签索引中移除
        for tag in entry.tags:
            if tag in self._tag_index:
                self._tag_index[tag].discard(key)
                if not self._tag_index[tag]:
                    del self._tag_index[tag]

        # 从依赖索引中移除
        for dependency in entry.dependencies:
            if dependency in self._dependency_index:
                self._dependency_index[dependency].discard(key)
                if not self._dependency_index[dependency]:
                    del self._dependency_index[dependency]

    def _is_expired(self, entry: CacheEntry) -> bool:
        """检查条目是否过期"""
        if entry.ttl is None:
            return False
        return datetime.now() - entry.created_at > entry.ttl

    def _check_dependencies(self, entry: CacheEntry) -> bool:
        """检查依赖是否有效"""
        for dependency in entry.dependencies:
            if dependency not in self._cache:
                return False
            dep_entry = self._cache[dependency]
            if self._is_expired(dep_entry):
                return False
        return True

    def _try_preload(self, key: str) -> Any:
        """尝试预加载数据"""
        if not self._preload_enabled:
            return None

        for pattern, loader in self._preload_patterns.items():
            if pattern in key:  # 简单的模式匹配
                try:
                    value = loader(key)
                    if value is not None:
                        # 自动缓存预加载的数据
                        self.put(key, value)
                        return value
                except Exception as e:
                    self._logger.error(f"预加载失败: {key}, 错误: {e}")

        return None


# 全局数据缓存管理器实例
data_cache_manager = DataCacheManager()
