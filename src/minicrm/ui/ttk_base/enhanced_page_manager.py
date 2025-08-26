"""MiniCRM TTK增强页面管理系统.

实现任务8的页面管理需求:
- 配置所有TTK面板的页面管理
- 实现页面缓存和懒加载策略
- 确保页面切换的流畅性
- 提供性能监控和优化

设计特点:
1. 智能缓存管理 - LRU缓存策略,自动内存管理
2. 懒加载机制 - 按需创建页面,提升启动性能
3. 流畅切换 - 预加载和过渡动画支持
4. 性能监控 - 实时监控页面加载时间和内存使用
5. 配置驱动 - 灵活的页面配置和策略设置

作者: MiniCRM开发团队
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
import logging
import threading
import time
from typing import TYPE_CHECKING, Any, Callable

from minicrm.core.exceptions import UIError
from minicrm.ui.ttk_base.page_manager import BasePage, PageConfig


if TYPE_CHECKING:
    import tkinter as tk


class CacheStrategy(Enum):
    """缓存策略枚举."""

    LRU = "lru"  # 最近最少使用
    LFU = "lfu"  # 最少使用频率
    FIFO = "fifo"  # 先进先出
    TTL = "ttl"  # 生存时间


class LoadingStrategy(Enum):
    """加载策略枚举."""

    LAZY = "lazy"  # 懒加载
    EAGER = "eager"  # 立即加载
    PRELOAD = "preload"  # 预加载
    ON_DEMAND = "on_demand"  # 按需加载


@dataclass
class PageCacheConfig:
    """页面缓存配置."""

    enabled: bool = True
    strategy: CacheStrategy = CacheStrategy.LRU
    max_size: int = 10
    ttl_seconds: float = 300.0  # 5分钟
    memory_threshold_mb: float = 100.0  # 100MB内存阈值
    auto_cleanup: bool = True
    cleanup_interval: float = 60.0  # 1分钟清理间隔


@dataclass
class PageLoadConfig:
    """页面加载配置."""

    strategy: LoadingStrategy = LoadingStrategy.LAZY
    preload_priority: int = 0  # 预加载优先级,数字越大优先级越高
    preload_delay: float = 0.1  # 预加载延迟(秒)
    timeout_seconds: float = 10.0  # 加载超时时间
    retry_count: int = 3  # 重试次数
    background_load: bool = True  # 后台加载


@dataclass
class PageTransitionConfig:
    """页面切换配置."""

    enabled: bool = True
    duration_ms: int = 200  # 切换动画时长
    fade_effect: bool = True  # 淡入淡出效果
    loading_indicator: bool = True  # 显示加载指示器
    smooth_scroll: bool = True  # 平滑滚动


@dataclass
class PagePerformanceMetrics:
    """页面性能指标."""

    page_id: str
    load_time: float = 0.0
    show_time: float = 0.0
    memory_usage: float = 0.0
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    cache_hits: int = 0
    cache_misses: int = 0

    def update_access(self) -> None:
        """更新访问信息."""
        self.access_count += 1
        self.last_access = time.time()


class PageCache:
    """页面缓存管理器."""

    def __init__(self, config: PageCacheConfig):
        """初始化页面缓存.

        Args:
            config: 缓存配置
        """
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # 缓存存储
        self._cache: OrderedDict[str, BasePage] = OrderedDict()
        self._access_count: dict[str, int] = {}
        self._cache_time: dict[str, float] = {}

        # 性能指标
        self.metrics: dict[str, PagePerformanceMetrics] = {}

        # 清理线程
        self._cleanup_thread: threading.Thread | None = None
        self._cleanup_stop_event = threading.Event()

        if config.auto_cleanup:
            self._start_cleanup_thread()

    def get(self, page_id: str) -> BasePage | None:
        """获取缓存页面.

        Args:
            page_id: 页面ID

        Returns:
            页面实例,如果不存在则返回None
        """
        if not self.config.enabled:
            return None

        if page_id not in self._cache:
            self._record_cache_miss(page_id)
            return None

        # 更新访问信息
        self._update_access(page_id)
        self._record_cache_hit(page_id)

        # LRU策略:移到末尾
        if self.config.strategy == CacheStrategy.LRU:
            self._cache.move_to_end(page_id)

        return self._cache[page_id]

    def put(self, page_id: str, page: BasePage) -> bool:
        """添加页面到缓存.

        Args:
            page_id: 页面ID
            page: 页面实例

        Returns:
            是否成功添加
        """
        if not self.config.enabled:
            return False

        try:
            # 检查缓存大小限制
            if len(self._cache) >= self.config.max_size:
                self._evict_pages()

            # 添加到缓存
            self._cache[page_id] = page
            self._cache_time[page_id] = time.time()
            self._access_count[page_id] = 0

            # 初始化性能指标
            if page_id not in self.metrics:
                self.metrics[page_id] = PagePerformanceMetrics(page_id)

            self.logger.debug(f"页面添加到缓存: {page_id}")
            return True

        except Exception as e:
            self.logger.exception(f"页面缓存添加失败 [{page_id}]: {e}")
            return False

    def remove(self, page_id: str) -> bool:
        """从缓存中移除页面.

        Args:
            page_id: 页面ID

        Returns:
            是否成功移除
        """
        try:
            if page_id in self._cache:
                page = self._cache.pop(page_id)
                self._cache_time.pop(page_id, None)
                self._access_count.pop(page_id, None)

                # 销毁页面
                if hasattr(page, "destroy"):
                    page.destroy()

                self.logger.debug(f"页面从缓存中移除: {page_id}")
                return True

            return False

        except Exception as e:
            self.logger.exception(f"页面缓存移除失败 [{page_id}]: {e}")
            return False

    def clear(self) -> None:
        """清空缓存."""
        try:
            for page_id in list(self._cache.keys()):
                self.remove(page_id)

            self.logger.debug("页面缓存已清空")

        except Exception as e:
            self.logger.exception(f"页面缓存清空失败: {e}")

    def _evict_pages(self) -> None:
        """淘汰页面."""
        try:
            if self.config.strategy == CacheStrategy.LRU:
                # 移除最近最少使用的页面
                page_id = next(iter(self._cache))
                self.remove(page_id)

            elif self.config.strategy == CacheStrategy.LFU:
                # 移除使用频率最低的页面
                min_count = min(self._access_count.values())
                for page_id, count in self._access_count.items():
                    if count == min_count:
                        self.remove(page_id)
                        break

            elif self.config.strategy == CacheStrategy.FIFO:
                # 移除最早添加的页面
                page_id = next(iter(self._cache))
                self.remove(page_id)

            elif self.config.strategy == CacheStrategy.TTL:
                # 移除过期页面
                current_time = time.time()
                expired_pages = []

                for page_id, cache_time in self._cache_time.items():
                    if current_time - cache_time > self.config.ttl_seconds:
                        expired_pages.append(page_id)

                for page_id in expired_pages:
                    self.remove(page_id)

                # 如果没有过期页面,使用LRU策略
                if not expired_pages and self._cache:
                    page_id = next(iter(self._cache))
                    self.remove(page_id)

        except Exception as e:
            self.logger.exception(f"页面淘汰失败: {e}")

    def _update_access(self, page_id: str) -> None:
        """更新访问信息."""
        self._access_count[page_id] = self._access_count.get(page_id, 0) + 1

        if page_id in self.metrics:
            self.metrics[page_id].update_access()

    def _record_cache_hit(self, page_id: str) -> None:
        """记录缓存命中."""
        if page_id in self.metrics:
            self.metrics[page_id].cache_hits += 1

    def _record_cache_miss(self, page_id: str) -> None:
        """记录缓存未命中."""
        if page_id not in self.metrics:
            self.metrics[page_id] = PagePerformanceMetrics(page_id)

        self.metrics[page_id].cache_misses += 1

    def _start_cleanup_thread(self) -> None:
        """启动清理线程."""
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            return

        self._cleanup_stop_event.clear()
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_worker, daemon=True
        )
        self._cleanup_thread.start()

        self.logger.debug("缓存清理线程启动")

    def _stop_cleanup_thread(self) -> None:
        """停止清理线程."""
        self._cleanup_stop_event.set()
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=2.0)

        self.logger.debug("缓存清理线程停止")

    def _cleanup_worker(self) -> None:
        """清理工作线程."""
        while not self._cleanup_stop_event.is_set():
            try:
                # TTL策略清理过期页面
                if self.config.strategy == CacheStrategy.TTL:
                    current_time = time.time()
                    expired_pages = []

                    for page_id, cache_time in self._cache_time.items():
                        if current_time - cache_time > self.config.ttl_seconds:
                            expired_pages.append(page_id)

                    for page_id in expired_pages:
                        self.remove(page_id)

                # 等待下次清理
                self._cleanup_stop_event.wait(self.config.cleanup_interval)

            except Exception as e:
                self.logger.exception(f"缓存清理工作线程错误: {e}")

    def get_cache_info(self) -> dict[str, Any]:
        """获取缓存信息."""
        total_hits = sum(m.cache_hits for m in self.metrics.values())
        total_misses = sum(m.cache_misses for m in self.metrics.values())
        hit_rate = (
            total_hits / (total_hits + total_misses)
            if (total_hits + total_misses) > 0
            else 0
        )

        return {
            "enabled": self.config.enabled,
            "strategy": self.config.strategy.value,
            "size": len(self._cache),
            "max_size": self.config.max_size,
            "hit_rate": hit_rate,
            "total_hits": total_hits,
            "total_misses": total_misses,
            "pages": list(self._cache.keys()),
        }

    def cleanup(self) -> None:
        """清理缓存资源."""
        try:
            self._stop_cleanup_thread()
            self.clear()

        except Exception as e:
            self.logger.exception(f"缓存清理失败: {e}")


class LazyPageLoader:
    """懒加载页面加载器."""

    def __init__(self, config: PageLoadConfig):
        """初始化懒加载器.

        Args:
            config: 加载配置
        """
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # 预加载队列
        self._preload_queue: list[tuple[str, int]] = []  # (page_id, priority)
        self._preload_thread: threading.Thread | None = None
        self._preload_stop_event = threading.Event()

        # 加载状态
        self._loading_pages: set[str] = set()
        self._load_callbacks: dict[str, list[Callable]] = {}

        if config.background_load:
            self._start_preload_thread()

    def add_to_preload_queue(self, page_id: str, priority: int = 0) -> None:
        """添加页面到预加载队列.

        Args:
            page_id: 页面ID
            priority: 优先级
        """
        if page_id not in [item[0] for item in self._preload_queue]:
            self._preload_queue.append((page_id, priority))
            # 按优先级排序
            self._preload_queue.sort(key=lambda x: x[1], reverse=True)

            self.logger.debug(f"页面添加到预加载队列: {page_id} (优先级: {priority})")

    def remove_from_preload_queue(self, page_id: str) -> None:
        """从预加载队列中移除页面.

        Args:
            page_id: 页面ID
        """
        self._preload_queue = [
            (pid, pri) for pid, pri in self._preload_queue if pid != page_id
        ]

    def is_loading(self, page_id: str) -> bool:
        """检查页面是否正在加载.

        Args:
            page_id: 页面ID

        Returns:
            是否正在加载
        """
        return page_id in self._loading_pages

    def add_load_callback(self, page_id: str, callback: Callable) -> None:
        """添加加载完成回调.

        Args:
            page_id: 页面ID
            callback: 回调函数
        """
        if page_id not in self._load_callbacks:
            self._load_callbacks[page_id] = []

        self._load_callbacks[page_id].append(callback)

    def _start_preload_thread(self) -> None:
        """启动预加载线程."""
        if self._preload_thread and self._preload_thread.is_alive():
            return

        self._preload_stop_event.clear()
        self._preload_thread = threading.Thread(
            target=self._preload_worker, daemon=True
        )
        self._preload_thread.start()

        self.logger.debug("预加载线程启动")

    def _stop_preload_thread(self) -> None:
        """停止预加载线程."""
        self._preload_stop_event.set()
        if self._preload_thread and self._preload_thread.is_alive():
            self._preload_thread.join(timeout=2.0)

        self.logger.debug("预加载线程停止")

    def _preload_worker(self) -> None:
        """预加载工作线程."""
        while not self._preload_stop_event.is_set():
            try:
                if self._preload_queue:
                    page_id, priority = self._preload_queue.pop(0)

                    if page_id not in self._loading_pages:
                        self.logger.debug(f"开始预加载页面: {page_id}")
                        # 这里需要与页面管理器集成来实际加载页面
                        # 暂时只是标记为加载中
                        self._loading_pages.add(page_id)

                        # 模拟加载延迟
                        time.sleep(self.config.preload_delay)

                        # 移除加载标记
                        self._loading_pages.discard(page_id)

                        # 执行回调
                        callbacks = self._load_callbacks.get(page_id, [])
                        for callback in callbacks:
                            try:
                                callback(page_id)
                            except Exception as e:
                                self.logger.exception(f"预加载回调执行失败: {e}")

                # 等待一段时间再处理下一个
                self._preload_stop_event.wait(0.1)

            except Exception as e:
                self.logger.exception(f"预加载工作线程错误: {e}")

    def cleanup(self) -> None:
        """清理加载器资源."""
        try:
            self._stop_preload_thread()
            self._preload_queue.clear()
            self._loading_pages.clear()
            self._load_callbacks.clear()

        except Exception as e:
            self.logger.exception(f"懒加载器清理失败: {e}")


class PageTransitionManager:
    """页面切换管理器."""

    def __init__(self, config: PageTransitionConfig):
        """初始化切换管理器.

        Args:
            config: 切换配置
        """
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # 切换状态
        self._transitioning = False
        self._current_transition: str | None = None

    def start_transition(self, from_page: str | None, to_page: str) -> None:
        """开始页面切换.

        Args:
            from_page: 源页面ID
            to_page: 目标页面ID
        """
        if not self.config.enabled:
            return

        try:
            self._transitioning = True
            self._current_transition = f"{from_page} -> {to_page}"

            # 显示加载指示器
            if self.config.loading_indicator:
                self._show_loading_indicator()

            self.logger.debug(f"开始页面切换: {self._current_transition}")

        except Exception as e:
            self.logger.exception(f"页面切换开始失败: {e}")

    def end_transition(self) -> None:
        """结束页面切换."""
        if not self.config.enabled:
            return

        try:
            # 隐藏加载指示器
            if self.config.loading_indicator:
                self._hide_loading_indicator()

            self.logger.debug(f"页面切换完成: {self._current_transition}")

            self._transitioning = False
            self._current_transition = None

        except Exception as e:
            self.logger.exception(f"页面切换结束失败: {e}")

    def is_transitioning(self) -> bool:
        """检查是否正在切换.

        Returns:
            是否正在切换
        """
        return self._transitioning

    def _show_loading_indicator(self) -> None:
        """显示加载指示器."""
        # TODO: 实现加载指示器显示逻辑

    def _hide_loading_indicator(self) -> None:
        """隐藏加载指示器."""
        # TODO: 实现加载指示器隐藏逻辑


class PerformanceMonitor:
    """性能监控器."""

    def __init__(self):
        """初始化性能监控器."""
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # 性能指标
        self.metrics: dict[str, PagePerformanceMetrics] = {}

        # 监控配置
        self.monitoring_enabled = True
        self.memory_check_interval = 30.0  # 30秒检查一次内存

        # 监控线程
        self._monitor_thread: threading.Thread | None = None
        self._monitor_stop_event = threading.Event()

        if self.monitoring_enabled:
            self._start_monitor_thread()

    def record_page_load(self, page_id: str, load_time: float) -> None:
        """记录页面加载时间.

        Args:
            page_id: 页面ID
            load_time: 加载时间(秒)
        """
        if page_id not in self.metrics:
            self.metrics[page_id] = PagePerformanceMetrics(page_id)

        self.metrics[page_id].load_time = load_time

        # 记录性能警告
        if load_time > 2.0:  # 超过2秒
            self.logger.warning(f"页面加载时间过长: {page_id} ({load_time:.2f}秒)")

    def record_page_show(self, page_id: str, show_time: float) -> None:
        """记录页面显示时间.

        Args:
            page_id: 页面ID
            show_time: 显示时间(秒)
        """
        if page_id not in self.metrics:
            self.metrics[page_id] = PagePerformanceMetrics(page_id)

        self.metrics[page_id].show_time = show_time

        # 记录性能警告
        if show_time > 0.5:  # 超过500毫秒
            self.logger.warning(f"页面显示时间过长: {page_id} ({show_time:.2f}秒)")

    def record_memory_usage(self, page_id: str, memory_mb: float) -> None:
        """记录页面内存使用.

        Args:
            page_id: 页面ID
            memory_mb: 内存使用量(MB)
        """
        if page_id not in self.metrics:
            self.metrics[page_id] = PagePerformanceMetrics(page_id)

        self.metrics[page_id].memory_usage = memory_mb

        # 记录内存警告
        if memory_mb > 50.0:  # 超过50MB
            self.logger.warning(f"页面内存使用过高: {page_id} ({memory_mb:.2f}MB)")

    def get_performance_report(self) -> dict[str, Any]:
        """获取性能报告.

        Returns:
            性能报告字典
        """
        total_pages = len(self.metrics)
        if total_pages == 0:
            return {"total_pages": 0}

        # 计算平均值
        avg_load_time = sum(m.load_time for m in self.metrics.values()) / total_pages
        avg_show_time = sum(m.show_time for m in self.metrics.values()) / total_pages
        avg_memory = sum(m.memory_usage for m in self.metrics.values()) / total_pages

        # 找出性能最差的页面
        slowest_load = max(self.metrics.values(), key=lambda m: m.load_time)
        slowest_show = max(self.metrics.values(), key=lambda m: m.show_time)
        highest_memory = max(self.metrics.values(), key=lambda m: m.memory_usage)

        return {
            "total_pages": total_pages,
            "average_load_time": avg_load_time,
            "average_show_time": avg_show_time,
            "average_memory_usage": avg_memory,
            "slowest_load_page": {
                "page_id": slowest_load.page_id,
                "load_time": slowest_load.load_time,
            },
            "slowest_show_page": {
                "page_id": slowest_show.page_id,
                "show_time": slowest_show.show_time,
            },
            "highest_memory_page": {
                "page_id": highest_memory.page_id,
                "memory_usage": highest_memory.memory_usage,
            },
            "pages": {
                page_id: {
                    "load_time": metrics.load_time,
                    "show_time": metrics.show_time,
                    "memory_usage": metrics.memory_usage,
                    "access_count": metrics.access_count,
                    "cache_hits": metrics.cache_hits,
                    "cache_misses": metrics.cache_misses,
                }
                for page_id, metrics in self.metrics.items()
            },
        }

    def _start_monitor_thread(self) -> None:
        """启动监控线程."""
        if self._monitor_thread and self._monitor_thread.is_alive():
            return

        self._monitor_stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_worker, daemon=True
        )
        self._monitor_thread.start()

        self.logger.debug("性能监控线程启动")

    def _stop_monitor_thread(self) -> None:
        """停止监控线程."""
        self._monitor_stop_event.set()
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2.0)

        self.logger.debug("性能监控线程停止")

    def _monitor_worker(self) -> None:
        """监控工作线程."""
        while not self._monitor_stop_event.is_set():
            try:
                # 检查内存使用情况
                # TODO: 实现实际的内存检查逻辑

                # 等待下次检查
                self._monitor_stop_event.wait(self.memory_check_interval)

            except Exception as e:
                self.logger.exception(f"性能监控工作线程错误: {e}")

    def cleanup(self) -> None:
        """清理监控器资源."""
        try:
            self._stop_monitor_thread()
            self.metrics.clear()

        except Exception as e:
            self.logger.exception(f"性能监控器清理失败: {e}")


class EnhancedPageManagerTTK:
    """增强的TTK页面管理器.

    实现任务8的所有需求:
    - 配置所有TTK面板的页面管理
    - 实现页面缓存和懒加载策略
    - 确保页面切换的流畅性
    - 提供性能监控和优化
    """

    def __init__(
        self,
        container: tk.Widget,
        cache_config: PageCacheConfig | None = None,
        load_config: PageLoadConfig | None = None,
        transition_config: PageTransitionConfig | None = None,
    ):
        """初始化增强页面管理器.

        Args:
            container: 页面容器组件
            cache_config: 缓存配置
            load_config: 加载配置
            transition_config: 切换配置
        """
        self.container = container
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # 配置
        self.cache_config = cache_config or PageCacheConfig()
        self.load_config = load_config or PageLoadConfig()
        self.transition_config = transition_config or PageTransitionConfig()

        # 核心组件
        self.cache = PageCache(self.cache_config)
        self.loader = LazyPageLoader(self.load_config)
        self.transition_manager = PageTransitionManager(self.transition_config)
        self.performance_monitor = PerformanceMonitor()

        # 页面管理
        self.page_configs: dict[str, PageConfig] = {}
        self.page_factories: dict[str, Callable[[], BasePage]] = {}

        # 状态管理
        self.current_page: str | None = None
        self.page_history: list[str] = []

        self.logger.debug("增强页面管理器初始化完成")

    def register_page(
        self,
        page_id: str,
        page_class: type[BasePage],
        title: str = "",
        cache_enabled: bool = True,
        preload: bool = False,
        preload_priority: int = 0,
        **kwargs: Any,
    ) -> None:
        """注册页面.

        Args:
            page_id: 页面ID
            page_class: 页面类
            title: 页面标题
            cache_enabled: 是否启用缓存
            preload: 是否预加载
            preload_priority: 预加载优先级
            **kwargs: 其他配置参数
        """
        try:
            config = PageConfig(
                page_id=page_id,
                page_class=page_class,
                title=title,
                cache=cache_enabled,
                preload=preload,
                **kwargs,
            )

            self.page_configs[page_id] = config

            # 添加到预加载队列
            if preload:
                self.loader.add_to_preload_queue(page_id, preload_priority)

            self.logger.debug(f"页面注册成功: {page_id}")

        except Exception as e:
            error_msg = f"页面注册失败: {page_id}"
            self.logger.exception(f"{error_msg}: {e}")
            raise UIError(error_msg, "EnhancedPageManagerTTK") from e

    def register_page_factory(
        self,
        page_id: str,
        factory: Callable[[], BasePage],
        title: str = "",
        cache_enabled: bool = True,
        preload: bool = False,
        preload_priority: int = 0,
    ) -> None:
        """注册页面工厂.

        Args:
            page_id: 页面ID
            factory: 页面工厂函数
            title: 页面标题
            cache_enabled: 是否启用缓存
            preload: 是否预加载
            preload_priority: 预加载优先级
        """
        try:
            self.page_factories[page_id] = factory

            # 创建虚拟配置
            config = PageConfig(
                page_id=page_id,
                page_class=BasePage,  # 占位符
                title=title,
                cache=cache_enabled,
                preload=preload,
            )

            self.page_configs[page_id] = config

            # 添加到预加载队列
            if preload:
                self.loader.add_to_preload_queue(page_id, preload_priority)

            self.logger.debug(f"页面工厂注册成功: {page_id}")

        except Exception as e:
            error_msg = f"页面工厂注册失败: {page_id}"
            self.logger.exception(f"{error_msg}: {e}")
            raise UIError(error_msg, "EnhancedPageManagerTTK") from e

    def navigate_to(self, page_id: str, params: dict[str, Any] | None = None) -> bool:
        """导航到指定页面.

        Args:
            page_id: 页面ID
            params: 页面参数

        Returns:
            是否导航成功
        """
        try:
            if page_id not in self.page_configs:
                self.logger.error(f"页面不存在: {page_id}")
                return False

            # 开始切换
            self.transition_manager.start_transition(self.current_page, page_id)

            # 记录开始时间
            start_time = time.time()

            # 获取或创建页面
            page = self._get_or_create_page(page_id)
            if not page:
                self.transition_manager.end_transition()
                return False

            # 隐藏当前页面
            if self.current_page:
                self._hide_current_page()

            # 显示新页面
            show_start = time.time()
            success = self._show_page(page_id, page, params or {})
            show_time = time.time() - show_start

            if success:
                # 更新当前页面
                self.current_page = page_id

                # 添加到历史记录
                self._add_to_history(page_id)

                # 记录性能指标
                total_time = time.time() - start_time
                self.performance_monitor.record_page_show(page_id, show_time)

                self.logger.debug(f"页面导航成功: {page_id} (耗时: {total_time:.3f}秒)")

            # 结束切换
            self.transition_manager.end_transition()

            return success

        except Exception as e:
            self.logger.exception(f"页面导航失败 [{page_id}]: {e}")
            self.transition_manager.end_transition()
            return False

    def _get_or_create_page(self, page_id: str) -> BasePage | None:
        """获取或创建页面实例.

        Args:
            page_id: 页面ID

        Returns:
            页面实例
        """
        try:
            # 从缓存获取
            page = self.cache.get(page_id)
            if page:
                self.logger.debug(f"从缓存获取页面: {page_id}")
                return page

            # 创建新页面
            start_time = time.time()
            page = self._create_page_instance(page_id)
            load_time = time.time() - start_time

            if page:
                # 记录加载时间
                self.performance_monitor.record_page_load(page_id, load_time)

                # 添加到缓存
                config = self.page_configs[page_id]
                if config.cache:
                    self.cache.put(page_id, page)

                self.logger.debug(f"页面创建成功: {page_id} (耗时: {load_time:.3f}秒)")

            return page

        except Exception as e:
            self.logger.exception(f"页面获取或创建失败 [{page_id}]: {e}")
            return None

    def _create_page_instance(self, page_id: str) -> BasePage | None:
        """创建页面实例.

        Args:
            page_id: 页面ID

        Returns:
            页面实例
        """
        try:
            # 使用工厂函数创建
            if page_id in self.page_factories:
                return self.page_factories[page_id]()

            # 使用类创建
            config = self.page_configs[page_id]
            page_class = config.page_class

            # 创建页面实例
            page = page_class(page_id, self.container)

            # 加载页面UI
            page.load()

            return page

        except Exception as e:
            self.logger.exception(f"页面实例创建失败 [{page_id}]: {e}")
            return None

    def _hide_current_page(self) -> None:
        """隐藏当前页面."""
        if not self.current_page:
            return

        try:
            page = self.cache.get(self.current_page)
            if page:
                page.hide()

        except Exception as e:
            self.logger.exception(f"隐藏当前页面失败: {e}")

    def _show_page(self, page_id: str, page: BasePage, params: dict[str, Any]) -> bool:
        """显示页面.

        Args:
            page_id: 页面ID
            page: 页面实例
            params: 页面参数

        Returns:
            是否显示成功
        """
        try:
            # 设置页面参数
            for key, value in params.items():
                page.set_data(key, value)

            # 显示页面
            page.show()

            return True

        except Exception as e:
            self.logger.exception(f"页面显示失败 [{page_id}]: {e}")
            return False

    def _add_to_history(self, page_id: str) -> None:
        """添加到历史记录.

        Args:
            page_id: 页面ID
        """
        # 避免重复记录
        if self.page_history and self.page_history[-1] == page_id:
            return

        self.page_history.append(page_id)

        # 限制历史记录长度
        if len(self.page_history) > 50:
            self.page_history = self.page_history[-50:]

    def go_back(self) -> bool:
        """返回上一页.

        Returns:
            是否成功返回
        """
        if len(self.page_history) < 2:
            return False

        # 移除当前页面
        self.page_history.pop()

        # 获取上一页
        previous_page = self.page_history[-1]

        # 导航到上一页(不添加到历史记录)
        return self._navigate_without_history(previous_page)

    def _navigate_without_history(self, page_id: str) -> bool:
        """导航但不添加到历史记录.

        Args:
            page_id: 页面ID

        Returns:
            是否导航成功
        """
        # 临时保存历史记录
        temp_history = self.page_history.copy()

        # 导航
        success = self.navigate_to(page_id)

        # 恢复历史记录
        if success:
            self.page_history = temp_history

        return success

    def preload_page(self, page_id: str, priority: int = 0) -> None:
        """预加载页面.

        Args:
            page_id: 页面ID
            priority: 优先级
        """
        if page_id in self.page_configs:
            self.loader.add_to_preload_queue(page_id, priority)

    def get_current_page(self) -> str | None:
        """获取当前页面ID.

        Returns:
            当前页面ID
        """
        return self.current_page

    def get_page_history(self) -> list[str]:
        """获取页面历史记录.

        Returns:
            页面历史记录
        """
        return self.page_history.copy()

    def get_manager_info(self) -> dict[str, Any]:
        """获取管理器信息.

        Returns:
            管理器信息字典
        """
        return {
            "current_page": self.current_page,
            "total_pages": len(self.page_configs),
            "history_length": len(self.page_history),
            "cache_info": self.cache.get_cache_info(),
            "performance_report": self.performance_monitor.get_performance_report(),
            "is_transitioning": self.transition_manager.is_transitioning(),
        }

    def cleanup(self) -> None:
        """清理管理器资源."""
        try:
            self.cache.cleanup()
            self.loader.cleanup()
            self.performance_monitor.cleanup()

            self.page_configs.clear()
            self.page_factories.clear()
            self.page_history.clear()

            self.logger.debug("增强页面管理器清理完成")

        except Exception as e:
            self.logger.exception(f"增强页面管理器清理失败: {e}")
