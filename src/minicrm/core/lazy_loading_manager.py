"""
MiniCRM 懒加载管理器

提供全面的懒加载功能,包括:
- 数据懒加载策略
- 分页和虚拟化支持
- 异步加载管理
- 加载状态跟踪
- 智能预加载
"""

import logging
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from .data_cache_manager import data_cache_manager


@dataclass
class LoadingTask:
    """加载任务"""

    task_id: str
    loader_func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # 优先级,数字越大优先级越高
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: str = "pending"  # pending, loading, completed, failed
    result: Any = None
    error: Exception | None = None
    cache_key: str | None = None
    dependencies: set[str] = field(default_factory=set)


@dataclass
class LazyLoadConfig:
    """懒加载配置"""

    enabled: bool = True
    batch_size: int = 50
    max_concurrent_loads: int = 5
    cache_enabled: bool = True
    preload_enabled: bool = True
    preload_threshold: int = 10  # 距离边界多少项时开始预加载
    timeout_seconds: int = 30


@dataclass
class LoadingStatistics:
    """加载统计信息"""

    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    cached_hits: int = 0
    avg_load_time_ms: float = 0.0
    max_load_time_ms: float = 0.0
    concurrent_loads: int = 0
    queue_size: int = 0


class LazyLoadingManager:
    """
    懒加载管理器

    提供智能的数据懒加载功能,支持分页、缓存、异步加载等特性.
    """

    def __init__(self, config: LazyLoadConfig | None = None):
        """
        初始化懒加载管理器

        Args:
            config: 懒加载配置
        """
        self._logger = logging.getLogger(__name__)

        # 配置
        self._config = config or LazyLoadConfig()

        # 任务管理
        self._task_queue: deque[LoadingTask] = deque()
        self._active_tasks: dict[str, LoadingTask] = {}
        self._completed_tasks: dict[str, LoadingTask] = {}
        self._task_lock = threading.RLock()

        # 线程池
        self._executor = ThreadPoolExecutor(
            max_workers=self._config.max_concurrent_loads,
            thread_name_prefix="LazyLoader",
        )

        # 加载器注册
        self._loaders: dict[str, Callable] = {}
        self._loader_configs: dict[str, dict[str, Any]] = {}

        # 分页管理
        self._page_cache: dict[str, dict[int, Any]] = {}
        self._page_sizes: dict[str, int] = {}
        self._total_counts: dict[str, int] = {}

        # 预加载管理
        self._preload_patterns: dict[str, Callable] = {}
        self._access_patterns: dict[str, list[int]] = defaultdict(list)

        # 统计信息
        self._stats = LoadingStatistics()
        self._load_times: list[float] = []

        # 监听器
        self._load_listeners: list[Callable] = []
        self._error_listeners: list[Callable] = []

        # 工作线程
        self._worker_thread = None
        self._stop_event = threading.Event()

        self._enabled = True

        self._logger.debug("懒加载管理器初始化完成")

    def enable(self) -> None:
        """启用懒加载管理器"""
        self._enabled = True
        self._start_worker()
        self._logger.info("懒加载管理器已启用")

    def disable(self) -> None:
        """禁用懒加载管理器"""
        self._enabled = False
        self._stop_worker()
        self._logger.info("懒加载管理器已禁用")

    def register_loader(
        self,
        loader_name: str,
        loader_func: Callable,
        batch_size: int | None = None,
        cache_ttl_minutes: int | None = None,
    ) -> None:
        """
        注册数据加载器

        Args:
            loader_name: 加载器名称
            loader_func: 加载函数
            batch_size: 批次大小
            cache_ttl_minutes: 缓存TTL(分钟)
        """
        self._loaders[loader_name] = loader_func
        self._loader_configs[loader_name] = {
            "batch_size": batch_size or self._config.batch_size,
            "cache_ttl_minutes": cache_ttl_minutes or 30,
        }

        self._logger.debug(f"注册数据加载器: {loader_name}")

    def load_data(
        self,
        loader_name: str,
        *args,
        priority: int = 0,
        cache_key: str | None = None,
        force_reload: bool = False,
        **kwargs,
    ) -> Future:
        """
        懒加载数据

        Args:
            loader_name: 加载器名称
            *args: 加载器参数
            priority: 优先级
            cache_key: 缓存键
            force_reload: 是否强制重新加载
            **kwargs: 加载器关键字参数

        Returns:
            Future: 加载任务的Future对象
        """
        if not self._enabled:
            future = Future()
            future.set_exception(RuntimeError("懒加载管理器已禁用"))
            return future

        try:
            # 检查缓存
            if not force_reload and cache_key and self._config.cache_enabled:
                cached_result = data_cache_manager.get(cache_key)
                if cached_result is not None:
                    self._stats.cached_hits += 1
                    future = Future()
                    future.set_result(cached_result)
                    return future

            # 检查加载器是否存在
            if loader_name not in self._loaders:
                future = Future()
                future.set_exception(ValueError(f"未找到加载器: {loader_name}"))
                return future

            # 创建加载任务
            task_id = self._generate_task_id(loader_name, args, kwargs)
            task = LoadingTask(
                task_id=task_id,
                loader_func=self._loaders[loader_name],
                args=args,
                kwargs=kwargs,
                priority=priority,
                cache_key=cache_key,
            )

            # 提交任务
            future = self._submit_task(task)

            return future

        except Exception as e:
            self._logger.error(f"提交懒加载任务失败: {e}")
            future = Future()
            future.set_exception(e)
            return future

    def load_page(
        self, loader_name: str, page: int, page_size: int | None = None, *args, **kwargs
    ) -> Future:
        """
        分页加载数据

        Args:
            loader_name: 加载器名称
            page: 页码(从0开始)
            page_size: 页面大小
            *args: 加载器参数
            **kwargs: 加载器关键字参数

        Returns:
            Future: 加载任务的Future对象
        """
        if not self._enabled:
            future = Future()
            future.set_exception(RuntimeError("懒加载管理器已禁用"))
            return future

        try:
            # 确定页面大小
            if page_size is None:
                page_size = self._loader_configs.get(loader_name, {}).get(
                    "batch_size", self._config.batch_size
                )

            # 生成缓存键
            cache_key = (
                f"{loader_name}_page_{page}_{page_size}_{hash(str(args) + str(kwargs))}"
            )

            # 检查页面缓存
            if (
                loader_name in self._page_cache
                and page in self._page_cache[loader_name]
            ):
                future = Future()
                future.set_result(self._page_cache[loader_name][page])
                return future

            # 计算偏移量
            offset = page * page_size

            # 添加分页参数
            kwargs.update(
                {
                    "limit": page_size,
                    "offset": offset,
                    "page": page,
                    "page_size": page_size,
                }
            )

            # 记录访问模式
            self._record_access_pattern(loader_name, page)

            # 加载数据
            future = self.load_data(loader_name, *args, cache_key=cache_key, **kwargs)

            # 添加页面缓存回调
            def cache_page_result(fut):
                try:
                    result = fut.result()
                    if loader_name not in self._page_cache:
                        self._page_cache[loader_name] = {}
                    self._page_cache[loader_name][page] = result

                    # 触发预加载
                    if self._config.preload_enabled:
                        self._trigger_preload(loader_name, page, args, kwargs)

                except Exception as e:
                    self._logger.error(f"缓存页面结果失败: {e}")

            future.add_done_callback(cache_page_result)

            return future

        except Exception as e:
            self._logger.error(f"分页加载失败: {e}")
            future = Future()
            future.set_exception(e)
            return future

    def preload_data(
        self,
        loader_name: str,
        keys: list[str],
        priority: int = -1,  # 预加载优先级较低
    ) -> list[Future]:
        """
        预加载数据

        Args:
            loader_name: 加载器名称
            keys: 要预加载的键列表
            priority: 优先级

        Returns:
            List[Future]: 预加载任务的Future列表
        """
        if not self._enabled or not self._config.preload_enabled:
            return []

        futures = []

        for key in keys:
            try:
                # 检查是否已缓存
                if data_cache_manager.get(key) is not None:
                    continue

                # 创建预加载任务
                future = self.load_data(
                    loader_name, key, priority=priority, cache_key=key
                )
                futures.append(future)

            except Exception as e:
                self._logger.error(f"创建预加载任务失败: {key}, 错误: {e}")

        self._logger.debug(f"创建了 {len(futures)} 个预加载任务")
        return futures

    def get_loading_status(self, task_id: str) -> str | None:
        """
        获取加载状态

        Args:
            task_id: 任务ID

        Returns:
            Optional[str]: 加载状态
        """
        with self._task_lock:
            if task_id in self._active_tasks:
                return self._active_tasks[task_id].status
            elif task_id in self._completed_tasks:
                return self._completed_tasks[task_id].status
            else:
                return None

    def cancel_task(self, task_id: str) -> bool:
        """
        取消加载任务

        Args:
            task_id: 任务ID

        Returns:
            bool: 是否成功取消
        """
        try:
            with self._task_lock:
                # 从队列中移除
                for i, task in enumerate(self._task_queue):
                    if task.task_id == task_id:
                        del self._task_queue[i]
                        return True

                # 如果任务正在执行,标记为取消
                if task_id in self._active_tasks:
                    task = self._active_tasks[task_id]
                    task.status = "cancelled"
                    return True

                return False

        except Exception as e:
            self._logger.error(f"取消任务失败: {task_id}, 错误: {e}")
            return False

    def clear_cache(self, loader_name: str | None = None) -> None:
        """
        清空缓存

        Args:
            loader_name: 加载器名称,如果为None则清空所有缓存
        """
        try:
            if loader_name:
                # 清空特定加载器的页面缓存
                if loader_name in self._page_cache:
                    del self._page_cache[loader_name]

                # 清空相关的数据缓存
                # 这里需要根据实际情况实现缓存键的匹配

            else:
                # 清空所有缓存
                self._page_cache.clear()
                data_cache_manager.clear()

            self._logger.info(f"缓存已清空: {loader_name or '全部'}")

        except Exception as e:
            self._logger.error(f"清空缓存失败: {e}")

    def get_statistics(self) -> LoadingStatistics:
        """
        获取加载统计信息

        Returns:
            LoadingStatistics: 统计信息
        """
        try:
            with self._task_lock:
                # 更新统计信息
                self._stats.queue_size = len(self._task_queue)
                self._stats.concurrent_loads = len(self._active_tasks)

                # 计算平均加载时间
                if self._load_times:
                    self._stats.avg_load_time_ms = sum(self._load_times) / len(
                        self._load_times
                    )
                    self._stats.max_load_time_ms = max(self._load_times)

                return self._stats

        except Exception as e:
            self._logger.error(f"获取统计信息失败: {e}")
            return LoadingStatistics()

    def add_load_listener(self, listener: Callable[[str, Any], None]) -> None:
        """
        添加加载完成监听器

        Args:
            listener: 监听器函数
        """
        self._load_listeners.append(listener)

    def add_error_listener(self, listener: Callable[[str, Exception], None]) -> None:
        """
        添加错误监听器

        Args:
            listener: 监听器函数
        """
        self._error_listeners.append(listener)

    def _submit_task(self, task: LoadingTask) -> Future:
        """提交加载任务"""
        with self._task_lock:
            # 检查是否有相同的任务正在执行
            for active_task in self._active_tasks.values():
                if (
                    active_task.loader_func == task.loader_func
                    and active_task.args == task.args
                    and active_task.kwargs == task.kwargs
                ):
                    # 返回现有任务的Future
                    return self._executor.submit(
                        self._wait_for_task, active_task.task_id
                    )

            # 添加到队列
            self._task_queue.append(task)
            self._stats.total_tasks += 1

            # 按优先级排序
            self._task_queue = deque(
                sorted(self._task_queue, key=lambda t: t.priority, reverse=True)
            )

            # 提交到线程池
            future = self._executor.submit(self._execute_task, task.task_id)

            return future

    def _execute_task(self, task_id: str) -> Any:
        """执行加载任务"""
        task = None

        try:
            # 从队列中获取任务
            with self._task_lock:
                for i, t in enumerate(self._task_queue):
                    if t.task_id == task_id:
                        task = self._task_queue[i]
                        del self._task_queue[i]
                        break

                if not task:
                    raise ValueError(f"任务不存在: {task_id}")

                # 移动到活动任务
                self._active_tasks[task_id] = task
                task.status = "loading"
                task.started_at = datetime.now()

            # 执行加载
            start_time = time.perf_counter()

            try:
                result = task.loader_func(*task.args, **task.kwargs)
                task.result = result
                task.status = "completed"

                # 缓存结果
                if task.cache_key and self._config.cache_enabled:
                    cache_ttl = timedelta(
                        minutes=self._loader_configs.get(
                            task.loader_func.__name__, {}
                        ).get("cache_ttl_minutes", 30)
                    )
                    data_cache_manager.put(task.cache_key, result, ttl=cache_ttl)

                # 更新统计
                load_time = (time.perf_counter() - start_time) * 1000
                self._load_times.append(load_time)
                if len(self._load_times) > 1000:
                    self._load_times = self._load_times[-1000:]

                self._stats.completed_tasks += 1

                # 通知监听器
                for listener in self._load_listeners:
                    try:
                        listener(task_id, result)
                    except Exception as e:
                        self._logger.error(f"加载监听器失败: {e}")

                return result

            except Exception as e:
                task.error = e
                task.status = "failed"
                self._stats.failed_tasks += 1

                # 通知错误监听器
                for listener in self._error_listeners:
                    try:
                        listener(task_id, e)
                    except Exception as listener_error:
                        self._logger.error(f"错误监听器失败: {listener_error}")

                raise e

        except Exception as e:
            self._logger.error(f"执行加载任务失败: {task_id}, 错误: {e}")
            raise e

        finally:
            # 清理任务
            with self._task_lock:
                if task_id in self._active_tasks:
                    task = self._active_tasks[task_id]
                    task.completed_at = datetime.now()

                    # 移动到完成任务
                    self._completed_tasks[task_id] = task
                    del self._active_tasks[task_id]

                    # 限制完成任务的数量
                    if len(self._completed_tasks) > 1000:
                        # 移除最旧的任务
                        oldest_task_id = min(
                            self._completed_tasks.keys(),
                            key=lambda k: self._completed_tasks[k].completed_at
                            or datetime.min,
                        )
                        del self._completed_tasks[oldest_task_id]

    def _wait_for_task(self, task_id: str) -> Any:
        """等待任务完成"""
        timeout = self._config.timeout_seconds
        start_time = time.time()

        while time.time() - start_time < timeout:
            with self._task_lock:
                if task_id in self._completed_tasks:
                    task = self._completed_tasks[task_id]
                    if task.status == "completed":
                        return task.result
                    elif task.status == "failed":
                        raise task.error

                if task_id in self._active_tasks:
                    task = self._active_tasks[task_id]
                    if task.status == "cancelled":
                        raise RuntimeError("任务已取消")

            time.sleep(0.1)

        raise TimeoutError(f"任务超时: {task_id}")

    def _generate_task_id(self, loader_name: str, args: tuple, kwargs: dict) -> str:
        """生成任务ID"""
        import hashlib

        content = f"{loader_name}_{args}_{kwargs}_{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _record_access_pattern(self, loader_name: str, page: int) -> None:
        """记录访问模式"""
        self._access_patterns[loader_name].append(page)

        # 限制历史记录长度
        if len(self._access_patterns[loader_name]) > 100:
            self._access_patterns[loader_name] = self._access_patterns[loader_name][
                -100:
            ]

    def _trigger_preload(
        self, loader_name: str, current_page: int, args: tuple, kwargs: dict
    ) -> None:
        """触发预加载"""
        try:
            # 分析访问模式,预测下一页
            access_history = self._access_patterns.get(loader_name, [])

            if len(access_history) < 2:
                # 历史不足,预加载下一页
                next_pages = [current_page + 1]
            else:
                # 基于历史模式预测
                if access_history[-1] > access_history[-2]:
                    # 向前访问,预加载后续页面
                    next_pages = [current_page + 1, current_page + 2]
                else:
                    # 向后访问,预加载前面页面
                    next_pages = [max(0, current_page - 1)]

            # 创建预加载任务
            for page in next_pages:
                if (
                    loader_name in self._page_cache
                    and page in self._page_cache[loader_name]
                ):
                    continue  # 已缓存,跳过

                # 创建预加载任务
                preload_kwargs = kwargs.copy()
                page_size = preload_kwargs.get("page_size", self._config.batch_size)
                preload_kwargs.update(
                    {
                        "limit": page_size,
                        "offset": page * page_size,
                        "page": page,
                        "page_size": page_size,
                    }
                )

                cache_key = f"{loader_name}_page_{page}_{page_size}_{hash(str(args) + str(preload_kwargs))}"

                self.load_data(
                    loader_name,
                    *args,
                    priority=-1,  # 低优先级
                    cache_key=cache_key,
                    **preload_kwargs,
                )

        except Exception as e:
            self._logger.error(f"触发预加载失败: {e}")

    def _start_worker(self) -> None:
        """启动工作线程"""
        if self._worker_thread and self._worker_thread.is_alive():
            return

        self._stop_event.clear()
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()

    def _stop_worker(self) -> None:
        """停止工作线程"""
        self._stop_event.set()
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)

    def _worker_loop(self) -> None:
        """工作线程循环"""
        while not self._stop_event.is_set():
            try:
                # 这里可以添加定期维护任务
                # 比如清理过期的完成任务、优化缓存等

                time.sleep(1.0)

            except Exception as e:
                self._logger.error(f"工作线程错误: {e}")

    def __del__(self):
        """析构函数"""
        try:
            self._stop_worker()
            self._executor.shutdown(wait=False)
        except Exception:
            pass


# 全局懒加载管理器实例
lazy_loading_manager = LazyLoadingManager()
