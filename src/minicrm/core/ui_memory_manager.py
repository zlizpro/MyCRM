"""MiniCRM UI内存管理器

专门负责UI组件的内存管理,包括:
- UI组件生命周期管理
- 内存泄漏检测和预防
- 组件缓存和回收
- 资源清理和释放
- 内存使用优化
"""

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import gc
import logging

# 纯Python替代Qt类
import threading
from typing import Any, Callable, Optional
from weakref import WeakKeyDictionary, WeakSet


class BaseObject:
    """基础对象类 - 替代QObject"""


class Timer:
    """定时器类 - 替代QTimer"""

    def __init__(self):
        self._timer: Optional[threading.Timer] = None
        self._interval = 1000  # 毫秒
        self._callback: Optional[Callable] = None
        self._running = False

    def timeout_connect(self, callback: Callable) -> None:
        """连接超时回调"""
        self._callback = callback

    def start(self, interval: int) -> None:
        """启动定时器"""
        self._interval = interval / 1000.0  # 转换为秒
        self._running = True
        self._schedule_next()

    def stop(self) -> None:
        """停止定时器"""
        self._running = False
        if self._timer:
            self._timer.cancel()

    def _schedule_next(self) -> None:
        """调度下一次执行"""
        if self._running and self._callback:
            self._timer = threading.Timer(self._interval, self._execute)
            self._timer.start()

    def _execute(self) -> None:
        """执行回调"""
        if self._callback:
            self._callback()
        if self._running:
            self._schedule_next()


class Widget:
    """组件类 - 替代QWidget"""

    def __init__(self):
        self._destroyed = False

    def is_destroyed(self) -> bool:
        """检查是否已销毁"""
        return self._destroyed

    def destroy(self) -> None:
        """销毁组件"""
        self._destroyed = True


class Pixmap:
    """图像类 - 替代QPixmap"""

    def __init__(self, data: Any = None):
        self._data = data
        self._size = (0, 0)

    def size(self) -> tuple[int, int]:
        """获取图像大小"""
        return self._size


@dataclass
class ComponentInfo:
    """组件信息"""

    component_id: str
    component_type: str
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    memory_estimate_kb: float = 0.0
    is_cached: bool = False
    cleanup_callbacks: list[Callable] = field(default_factory=list)


@dataclass
class MemoryLeakInfo:
    """内存泄漏信息"""

    component_type: str
    leak_count: int
    first_detected: datetime
    last_detected: datetime
    estimated_leak_size_kb: float


class UIMemoryManager:
    """UI内存管理器

    提供全面的UI组件内存管理功能,包括生命周期管理、泄漏检测、缓存优化等.
    """

    def __init__(self):
        """初始化UI内存管理器"""
        self._logger = logging.getLogger(__name__)

        # 组件跟踪
        self._tracked_components: WeakKeyDictionary = WeakKeyDictionary()
        self._component_info: dict[str, ComponentInfo] = {}
        self._component_refs: WeakSet = WeakSet()

        # 缓存管理
        self._component_cache: dict[str, Any] = {}
        self._pixmap_cache: dict[str, Pixmap] = {}
        self._cache_access_times: dict[str, datetime] = {}
        self._cache_max_size = 100
        self._cache_ttl = timedelta(minutes=30)

        # 内存泄漏检测
        self._leak_detection_enabled = True
        self._component_counts: dict[str, int] = defaultdict(int)
        self._previous_counts: dict[str, int] = defaultdict(int)
        self._detected_leaks: dict[str, MemoryLeakInfo] = {}

        # 清理配置
        self._auto_cleanup_enabled = True
        self._cleanup_interval_minutes = 10
        self._max_idle_time = timedelta(minutes=30)

        # 定时器
        self._cleanup_timer = Timer()
        self._cleanup_timer.timeout_connect(self._perform_cleanup)

        self._leak_detection_timer = Timer()
        self._leak_detection_timer.timeout_connect(self._detect_memory_leaks)

        self._enabled = True

        self._logger.debug("UI内存管理器初始化完成")

    def enable(self) -> None:
        """启用UI内存管理器"""
        self._enabled = True

        if self._auto_cleanup_enabled:
            self._cleanup_timer.start(self._cleanup_interval_minutes * 60 * 1000)

        if self._leak_detection_enabled:
            self._leak_detection_timer.start(60000)  # 每分钟检测一次

        self._logger.info("UI内存管理器已启用")

    def disable(self) -> None:
        """禁用UI内存管理器"""
        self._enabled = False
        self._cleanup_timer.stop()
        self._leak_detection_timer.stop()
        self._logger.info("UI内存管理器已禁用")

    def register_component(
        self,
        component: Any,
        component_type: str = None,
        cleanup_callback: Callable = None,
    ) -> str:
        """注册UI组件

        Args:
            component: UI组件对象
            component_type: 组件类型
            cleanup_callback: 清理回调函数

        Returns:
            str: 组件ID
        """
        if not self._enabled:
            return ""

        try:
            # 生成组件ID
            component_id = self._generate_component_id(component)

            # 确定组件类型
            if not component_type:
                component_type = component.__class__.__name__

            # 创建组件信息
            info = ComponentInfo(
                component_id=component_id,
                component_type=component_type,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                memory_estimate_kb=self._estimate_component_memory(component),
            )

            if cleanup_callback:
                info.cleanup_callbacks.append(cleanup_callback)

            # 注册组件
            self._tracked_components[component] = component_id
            self._component_info[component_id] = info
            self._component_refs.add(component)

            # 更新组件计数
            self._component_counts[component_type] += 1

            self._logger.debug(f"注册UI组件: {component_type} ({component_id})")
            return component_id

        except Exception as e:
            self._logger.error(f"注册UI组件失败: {e}")
            return ""

    def unregister_component(self, component: Any) -> bool:
        """注销UI组件

        Args:
            component: UI组件对象

        Returns:
            bool: 是否成功注销
        """
        if not self._enabled:
            return False

        try:
            # 获取组件ID
            component_id = self._tracked_components.get(component)
            if not component_id:
                return False

            # 获取组件信息
            info = self._component_info.get(component_id)
            if info:
                # 执行清理回调
                for callback in info.cleanup_callbacks:
                    try:
                        callback()
                    except Exception as e:
                        self._logger.error(f"执行清理回调失败: {e}")

                # 更新组件计数
                self._component_counts[info.component_type] -= 1

                # 移除组件信息
                del self._component_info[component_id]

            # 从跟踪中移除
            if component in self._tracked_components:
                del self._tracked_components[component]

            self._logger.debug(f"注销UI组件: {component_id}")
            return True

        except Exception as e:
            self._logger.error(f"注销UI组件失败: {e}")
            return False

    def access_component(self, component: Any) -> None:
        """记录组件访问

        Args:
            component: UI组件对象
        """
        if not self._enabled:
            return

        try:
            component_id = self._tracked_components.get(component)
            if component_id and component_id in self._component_info:
                info = self._component_info[component_id]
                info.last_accessed = datetime.now()
                info.access_count += 1

        except Exception as e:
            self._logger.error(f"记录组件访问失败: {e}")

    def cache_component(self, key: str, component: Any, ttl: timedelta = None) -> bool:
        """缓存UI组件

        Args:
            key: 缓存键
            component: 组件对象
            ttl: 生存时间

        Returns:
            bool: 是否成功缓存
        """
        if not self._enabled:
            return False

        try:
            # 检查缓存大小限制
            if len(self._component_cache) >= self._cache_max_size:
                self._evict_oldest_cache_item()

            # 缓存组件
            self._component_cache[key] = component
            self._cache_access_times[key] = datetime.now()

            # 标记组件为已缓存
            component_id = self._tracked_components.get(component)
            if component_id and component_id in self._component_info:
                self._component_info[component_id].is_cached = True

            self._logger.debug(f"缓存UI组件: {key}")
            return True

        except Exception as e:
            self._logger.error(f"缓存UI组件失败: {e}")
            return False

    def get_cached_component(self, key: str) -> Any | None:
        """获取缓存的组件

        Args:
            key: 缓存键

        Returns:
            Optional[Any]: 缓存的组件,如果不存在或过期则返回None
        """
        if not self._enabled:
            return None

        try:
            if key not in self._component_cache:
                return None

            # 检查是否过期
            access_time = self._cache_access_times.get(key)
            if access_time and datetime.now() - access_time > self._cache_ttl:
                # 过期,删除缓存
                del self._component_cache[key]
                del self._cache_access_times[key]
                return None

            # 更新访问时间
            self._cache_access_times[key] = datetime.now()

            return self._component_cache[key]

        except Exception as e:
            self._logger.error(f"获取缓存组件失败: {e}")
            return None

    def cleanup_idle_components(self) -> dict[str, Any]:
        """清理空闲组件

        Returns:
            Dict[str, Any]: 清理结果
        """
        if not self._enabled:
            return {"error": "内存管理器已禁用"}

        try:
            cleanup_results = {
                "cleaned_components": 0,
                "cleaned_cache_items": 0,
                "memory_freed_kb": 0.0,
                "cleaned_component_types": [],
            }

            current_time = datetime.now()
            components_to_clean = []

            # 找出空闲组件
            for component_id, info in self._component_info.items():
                if current_time - info.last_accessed > self._max_idle_time:
                    components_to_clean.append(component_id)

            # 清理空闲组件
            for component_id in components_to_clean:
                info = self._component_info[component_id]

                # 执行清理回调
                for callback in info.cleanup_callbacks:
                    try:
                        callback()
                    except Exception as e:
                        self._logger.error(f"执行清理回调失败: {e}")

                # 更新统计
                cleanup_results["cleaned_components"] += 1
                cleanup_results["memory_freed_kb"] += info.memory_estimate_kb

                if (
                    info.component_type
                    not in cleanup_results["cleaned_component_types"]
                ):
                    cleanup_results["cleaned_component_types"].append(
                        info.component_type
                    )

                # 移除组件信息
                del self._component_info[component_id]

            # 清理过期缓存
            cache_keys_to_remove = []
            for key, access_time in self._cache_access_times.items():
                if current_time - access_time > self._cache_ttl:
                    cache_keys_to_remove.append(key)

            for key in cache_keys_to_remove:
                if key in self._component_cache:
                    del self._component_cache[key]
                del self._cache_access_times[key]
                cleanup_results["cleaned_cache_items"] += 1

            self._logger.info(f"空闲组件清理完成: {cleanup_results}")
            return cleanup_results

        except Exception as e:
            self._logger.error(f"清理空闲组件失败: {e}")
            return {"error": str(e)}

    def detect_memory_leaks(self) -> list[MemoryLeakInfo]:
        """检测内存泄漏

        Returns:
            List[MemoryLeakInfo]: 检测到的内存泄漏列表
        """
        if not self._enabled or not self._leak_detection_enabled:
            return []

        try:
            current_time = datetime.now()
            detected_leaks = []

            # 比较组件计数变化
            for component_type, current_count in self._component_counts.items():
                previous_count = self._previous_counts.get(component_type, 0)

                # 如果组件数量持续增长且没有相应的减少,可能存在泄漏
                if current_count > previous_count + 10:  # 阈值:增长超过10个
                    leak_count = current_count - previous_count

                    if component_type in self._detected_leaks:
                        # 更新现有泄漏信息
                        leak_info = self._detected_leaks[component_type]
                        leak_info.leak_count += leak_count
                        leak_info.last_detected = current_time
                    else:
                        # 创建新的泄漏信息
                        leak_info = MemoryLeakInfo(
                            component_type=component_type,
                            leak_count=leak_count,
                            first_detected=current_time,
                            last_detected=current_time,
                            estimated_leak_size_kb=leak_count
                            * 50.0,  # 估算每个组件50KB
                        )
                        self._detected_leaks[component_type] = leak_info

                    detected_leaks.append(leak_info)

            # 更新前一次的计数
            self._previous_counts = self._component_counts.copy()

            if detected_leaks:
                self._logger.warning(f"检测到 {len(detected_leaks)} 个可能的内存泄漏")

            return detected_leaks

        except Exception as e:
            self._logger.error(f"内存泄漏检测失败: {e}")
            return []

    def force_garbage_collection(self) -> dict[str, Any]:
        """强制垃圾回收

        Returns:
            Dict[str, Any]: 垃圾回收结果
        """
        try:
            # 记录回收前状态
            components_before = len(self._component_info)
            cache_before = len(self._component_cache)

            # 清理已销毁的组件引用
            self._cleanup_destroyed_components()

            # 执行垃圾回收
            collected_objects = gc.collect()

            # 记录回收后状态
            components_after = len(self._component_info)
            cache_after = len(self._component_cache)

            results = {
                "collected_objects": collected_objects,
                "components_cleaned": components_before - components_after,
                "cache_items_cleaned": cache_before - cache_after,
                "gc_stats": {
                    "generation_0": gc.get_count()[0],
                    "generation_1": gc.get_count()[1],
                    "generation_2": gc.get_count()[2],
                },
            }

            self._logger.info(f"强制垃圾回收完成: {results}")
            return results

        except Exception as e:
            self._logger.error(f"强制垃圾回收失败: {e}")
            return {"error": str(e)}

    def get_memory_statistics(self) -> dict[str, Any]:
        """获取内存统计信息

        Returns:
            Dict[str, Any]: 内存统计信息
        """
        try:
            # 组件统计
            component_stats = {}
            total_memory_kb = 0.0

            for component_type, count in self._component_counts.items():
                type_memory = sum(
                    info.memory_estimate_kb
                    for info in self._component_info.values()
                    if info.component_type == component_type
                )

                component_stats[component_type] = {
                    "count": count,
                    "memory_kb": type_memory,
                    "avg_memory_per_component_kb": type_memory / count
                    if count > 0
                    else 0.0,
                }

                total_memory_kb += type_memory

            # 缓存统计
            cache_stats = {
                "component_cache_size": len(self._component_cache),
                "pixmap_cache_size": len(self._pixmap_cache),
                "cache_hit_rate": self._calculate_cache_hit_rate(),
                "avg_cache_age_minutes": self._calculate_avg_cache_age(),
            }

            # 泄漏统计
            leak_stats = {
                "detected_leaks_count": len(self._detected_leaks),
                "total_leaked_components": sum(
                    leak.leak_count for leak in self._detected_leaks.values()
                ),
                "estimated_leak_memory_kb": sum(
                    leak.estimated_leak_size_kb
                    for leak in self._detected_leaks.values()
                ),
            }

            return {
                "timestamp": datetime.now().isoformat(),
                "total_tracked_components": len(self._component_info),
                "total_memory_estimate_kb": total_memory_kb,
                "component_statistics": component_stats,
                "cache_statistics": cache_stats,
                "leak_statistics": leak_stats,
                "configuration": {
                    "auto_cleanup_enabled": self._auto_cleanup_enabled,
                    "leak_detection_enabled": self._leak_detection_enabled,
                    "cache_max_size": self._cache_max_size,
                    "cache_ttl_minutes": self._cache_ttl.total_seconds() / 60,
                    "max_idle_time_minutes": self._max_idle_time.total_seconds() / 60,
                },
            }

        except Exception as e:
            self._logger.error(f"获取内存统计失败: {e}")
            return {"error": str(e)}

    def _generate_component_id(self, component: Any) -> str:
        """生成组件ID"""
        import hashlib

        content = f"{component.__class__.__name__}_{id(component)}_{datetime.now().timestamp()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _estimate_component_memory(self, component: Any) -> float:
        """估算组件内存使用(KB)"""
        try:
            # 简化的内存估算
            base_size = 10.0  # 基础大小10KB

            # 根据组件类型调整
            if hasattr(component, "__dict__"):
                # 根据属性数量估算
                attr_count = len(component.__dict__)
                base_size += attr_count * 0.5

            # 如果是Qt组件,根据类型调整
            if hasattr(component, "children"):
                children_count = (
                    len(component.children()) if callable(component.children) else 0
                )
                base_size += children_count * 2.0

            return base_size

        except Exception:
            return 10.0  # 默认估算值

    def _evict_oldest_cache_item(self) -> None:
        """驱逐最旧的缓存项"""
        if not self._cache_access_times:
            return

        oldest_key = min(
            self._cache_access_times.keys(), key=lambda k: self._cache_access_times[k]
        )

        if oldest_key in self._component_cache:
            del self._component_cache[oldest_key]
        del self._cache_access_times[oldest_key]

    def _cleanup_destroyed_components(self) -> None:
        """清理已销毁的组件"""
        try:
            # WeakKeyDictionary和WeakSet会自动清理已销毁的对象
            # 但我们需要清理对应的信息

            valid_component_ids = set(self._tracked_components.values())
            invalid_component_ids = (
                set(self._component_info.keys()) - valid_component_ids
            )

            for component_id in invalid_component_ids:
                if component_id in self._component_info:
                    info = self._component_info[component_id]
                    self._component_counts[info.component_type] -= 1
                    del self._component_info[component_id]

        except Exception as e:
            self._logger.error(f"清理已销毁组件失败: {e}")

    def _perform_cleanup(self) -> None:
        """执行定期清理"""
        if not self._enabled or not self._auto_cleanup_enabled:
            return

        try:
            # 清理空闲组件
            self.cleanup_idle_components()

            # 清理已销毁的组件
            self._cleanup_destroyed_components()

            # 执行轻量级垃圾回收
            gc.collect(0)  # 只回收第0代

        except Exception as e:
            self._logger.error(f"定期清理失败: {e}")

    def _detect_memory_leaks(self) -> None:
        """定期检测内存泄漏"""
        if not self._enabled or not self._leak_detection_enabled:
            return

        try:
            leaks = self.detect_memory_leaks()
            if leaks:
                for leak in leaks:
                    self._logger.warning(
                        f"检测到内存泄漏: {leak.component_type}, "
                        f"泄漏数量: {leak.leak_count}, "
                        f"估算大小: {leak.estimated_leak_size_kb:.1f}KB"
                    )

        except Exception as e:
            self._logger.error(f"内存泄漏检测失败: {e}")

    def _calculate_cache_hit_rate(self) -> float:
        """计算缓存命中率"""
        # 简化实现,实际应该跟踪命中和未命中次数
        return 0.0

    def _calculate_avg_cache_age(self) -> float:
        """计算平均缓存年龄(分钟)"""
        if not self._cache_access_times:
            return 0.0

        current_time = datetime.now()
        total_age = sum(
            (current_time - access_time).total_seconds() / 60
            for access_time in self._cache_access_times.values()
        )

        return total_age / len(self._cache_access_times)

    def clear_all_caches(self) -> None:
        """清空所有缓存"""
        self._component_cache.clear()
        self._pixmap_cache.clear()
        self._cache_access_times.clear()
        self._logger.info("所有缓存已清空")

    def set_cache_size(self, max_size: int) -> None:
        """设置缓存大小限制"""
        self._cache_max_size = max_size
        self._logger.info(f"缓存大小限制已设置为: {max_size}")

    def set_cache_ttl(self, ttl_minutes: int) -> None:
        """设置缓存生存时间"""
        self._cache_ttl = timedelta(minutes=ttl_minutes)
        self._logger.info(f"缓存生存时间已设置为: {ttl_minutes}分钟")


# 全局UI内存管理器实例
ui_memory_manager = UIMemoryManager()
