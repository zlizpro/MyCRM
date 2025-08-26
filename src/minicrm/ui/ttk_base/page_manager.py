"""TTK页面管理系统

提供TTK应用程序的页面管理功能,包括:
- 页面生命周期管理
- 页面路由和切换
- 页面缓存和预加载
- 懒加载和内存管理
- 页面状态保存和恢复

设计目标:
1. 提供高效的页面管理机制
2. 支持复杂的页面切换逻辑
3. 优化内存使用和性能
4. 提供良好的用户体验

作者: MiniCRM开发团队
"""

from abc import ABC, abstractmethod
from enum import Enum
import logging
import threading
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Type


class PageState(Enum):
    """页面状态枚举"""

    UNLOADED = "unloaded"  # 未加载
    LOADING = "loading"  # 加载中
    LOADED = "loaded"  # 已加载
    ACTIVE = "active"  # 活动状态
    INACTIVE = "inactive"  # 非活动状态
    CACHED = "cached"  # 已缓存
    DESTROYED = "destroyed"  # 已销毁


class PageLifecycleEvent(Enum):
    """页面生命周期事件枚举"""

    BEFORE_LOAD = "before_load"
    AFTER_LOAD = "after_load"
    BEFORE_SHOW = "before_show"
    AFTER_SHOW = "after_show"
    BEFORE_HIDE = "before_hide"
    AFTER_HIDE = "after_hide"
    BEFORE_DESTROY = "before_destroy"
    AFTER_DESTROY = "after_destroy"


class BasePage(ABC):
    """页面基类

    所有页面都应该继承此基类,实现必要的生命周期方法.
    """

    def __init__(self, page_id: str, parent: tk.Widget):
        """初始化页面

        Args:
            page_id: 页面唯一标识
            parent: 父组件
        """
        self.page_id = page_id
        self.parent = parent
        self.state = PageState.UNLOADED
        self.frame: Optional[ttk.Frame] = None
        self.data: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}[{page_id}]")

    @abstractmethod
    def create_ui(self) -> ttk.Frame:
        """创建页面UI

        Returns:
            页面主框架
        """

    def load(self) -> None:
        """加载页面"""
        if self.state != PageState.UNLOADED:
            return

        self.state = PageState.LOADING
        try:
            self.frame = self.create_ui()
            self.state = PageState.LOADED
            self.logger.debug(f"页面加载完成: {self.page_id}")
        except Exception as e:
            self.state = PageState.UNLOADED
            self.logger.error(f"页面加载失败: {e}")
            raise

    def show(self) -> None:
        """显示页面"""
        if self.state not in [PageState.LOADED, PageState.INACTIVE, PageState.CACHED]:
            return

        if self.frame:
            self.frame.pack(fill=tk.BOTH, expand=True)
            self.state = PageState.ACTIVE
            self.on_show()
            self.logger.debug(f"页面显示: {self.page_id}")

    def hide(self) -> None:
        """隐藏页面"""
        if self.state != PageState.ACTIVE:
            return

        if self.frame:
            self.frame.pack_forget()
            self.state = PageState.INACTIVE
            self.on_hide()
            self.logger.debug(f"页面隐藏: {self.page_id}")

    def destroy(self) -> None:
        """销毁页面"""
        if self.state == PageState.DESTROYED:
            return

        self.on_destroy()
        if self.frame:
            self.frame.destroy()
            self.frame = None

        self.state = PageState.DESTROYED
        self.logger.debug(f"页面销毁: {self.page_id}")

    def cache(self) -> None:
        """缓存页面"""
        if self.state == PageState.INACTIVE:
            self.state = PageState.CACHED
            self.on_cache()
            self.logger.debug(f"页面缓存: {self.page_id}")

    def restore_from_cache(self) -> None:
        """从缓存恢复页面"""
        if self.state == PageState.CACHED:
            self.state = PageState.INACTIVE
            self.on_restore_from_cache()
            self.logger.debug(f"页面从缓存恢复: {self.page_id}")

    def get_frame(self) -> Optional[ttk.Frame]:
        """获取页面框架

        Returns:
            页面框架,如果未加载则返回None
        """
        return self.frame

    def set_data(self, key: str, value: Any) -> None:
        """设置页面数据

        Args:
            key: 数据键
            value: 数据值
        """
        self.data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        """获取页面数据

        Args:
            key: 数据键
            default: 默认值

        Returns:
            数据值
        """
        return self.data.get(key, default)

    # 生命周期钩子方法(子类可以重写)
    def on_show(self) -> None:
        """页面显示时调用"""

    def on_hide(self) -> None:
        """页面隐藏时调用"""

    def on_destroy(self) -> None:
        """页面销毁时调用"""

    def on_cache(self) -> None:
        """页面缓存时调用"""

    def on_restore_from_cache(self) -> None:
        """页面从缓存恢复时调用"""


class PageConfig:
    """页面配置类"""

    def __init__(
        self,
        page_id: str,
        page_class: Type[BasePage],
        title: str = "",
        preload: bool = False,
        cache: bool = True,
        cache_timeout: Optional[float] = None,
        lazy_load: bool = True,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """初始化页面配置

        Args:
            page_id: 页面唯一标识
            page_class: 页面类
            title: 页面标题
            preload: 是否预加载
            cache: 是否缓存
            cache_timeout: 缓存超时时间(秒)
            lazy_load: 是否懒加载
            dependencies: 依赖的页面ID列表
            metadata: 页面元数据
        """
        self.page_id = page_id
        self.page_class = page_class
        self.title = title
        self.preload = preload
        self.cache = cache
        self.cache_timeout = cache_timeout
        self.lazy_load = lazy_load
        self.dependencies = dependencies or []
        self.metadata = metadata or {}


class PageManagerTTK:
    """TTK页面管理器

    负责管理页面的生命周期、缓存、预加载等功能.
    """

    def __init__(
        self,
        container: tk.Widget,
        max_cache_size: int = 10,
        default_cache_timeout: float = 300.0,  # 5分钟
        preload_enabled: bool = True,
        lazy_load_enabled: bool = True,
    ):
        """初始化页面管理器

        Args:
            container: 页面容器组件
            max_cache_size: 最大缓存页面数
            default_cache_timeout: 默认缓存超时时间(秒)
            preload_enabled: 是否启用预加载
            lazy_load_enabled: 是否启用懒加载
        """
        self.container = container
        self.max_cache_size = max_cache_size
        self.default_cache_timeout = default_cache_timeout
        self.preload_enabled = preload_enabled
        self.lazy_load_enabled = lazy_load_enabled

        # 日志记录器
        self.logger = logging.getLogger(self.__class__.__name__)

        # 页面管理
        self.page_configs: Dict[str, PageConfig] = {}
        self.pages: Dict[str, BasePage] = {}
        self.page_instances: Dict[str, weakref.ReferenceType] = {}

        # 状态管理
        self.current_page: Optional[str] = None
        self.page_history: List[str] = []
        self.cached_pages: Dict[str, float] = {}  # page_id -> cache_time

        # 生命周期回调
        self.lifecycle_callbacks: Dict[PageLifecycleEvent, List[Callable]] = {
            event: [] for event in PageLifecycleEvent
        }

        # 预加载管理
        self.preload_queue: Set[str] = set()
        self.preload_thread: Optional[threading.Thread] = None
        self.preload_stop_event = threading.Event()

        # 启动预加载线程
        if self.preload_enabled:
            self._start_preload_thread()

    def register_page(self, config: PageConfig) -> None:
        """注册页面

        Args:
            config: 页面配置
        """
        try:
            self.page_configs[config.page_id] = config

            # 添加到预加载队列
            if config.preload and self.preload_enabled:
                self.preload_queue.add(config.page_id)

            self.logger.debug(f"页面注册完成: {config.page_id}")

        except Exception as e:
            self.logger.error(f"页面注册失败: {e}")
            raise

    def unregister_page(self, page_id: str) -> None:
        """注销页面

        Args:
            page_id: 页面ID
        """
        try:
            # 销毁页面实例
            if page_id in self.pages:
                self.pages[page_id].destroy()
                del self.pages[page_id]

            # 清理配置
            if page_id in self.page_configs:
                del self.page_configs[page_id]

            # 清理缓存
            if page_id in self.cached_pages:
                del self.cached_pages[page_id]

            # 从预加载队列移除
            self.preload_queue.discard(page_id)

            # 清理实例引用
            if page_id in self.page_instances:
                del self.page_instances[page_id]

            self.logger.debug(f"页面注销完成: {page_id}")

        except Exception as e:
            self.logger.error(f"页面注销失败: {e}")

    def get_page(self, page_id: str) -> Optional[BasePage]:
        """获取页面实例

        Args:
            page_id: 页面ID

        Returns:
            页面实例,如果不存在则返回None
        """
        try:
            # 检查是否已存在实例
            if page_id in self.pages:
                return self.pages[page_id]

            # 检查是否已注册
            if page_id not in self.page_configs:
                self.logger.warning(f"页面未注册: {page_id}")
                return None

            # 创建页面实例
            config = self.page_configs[page_id]
            page = config.page_class(page_id, self.container)
            self.pages[page_id] = page

            # 创建弱引用
            self.page_instances[page_id] = weakref.ref(
                page, lambda ref: self._on_page_destroyed(page_id)
            )

            # 触发生命周期事件
            self._trigger_lifecycle_event(PageLifecycleEvent.AFTER_LOAD, page_id, page)

            self.logger.debug(f"页面实例创建: {page_id}")
            return page

        except Exception as e:
            self.logger.error(f"页面实例创建失败: {e}")
            return None

    def load_page(self, page_id: str, force_reload: bool = False) -> bool:
        """加载页面

        Args:
            page_id: 页面ID
            force_reload: 是否强制重新加载

        Returns:
            是否加载成功
        """
        try:
            page = self.get_page(page_id)
            if not page:
                return False

            # 检查是否需要重新加载
            if page.state == PageState.LOADED and not force_reload:
                return True

            # 触发加载前事件
            self._trigger_lifecycle_event(PageLifecycleEvent.BEFORE_LOAD, page_id, page)

            # 加载页面
            page.load()

            # 触发加载后事件
            self._trigger_lifecycle_event(PageLifecycleEvent.AFTER_LOAD, page_id, page)

            return True

        except Exception as e:
            self.logger.error(f"页面加载失败 [{page_id}]: {e}")
            return False

    def show_page(self, page_id: str, add_to_history: bool = True) -> bool:
        """显示页面

        Args:
            page_id: 页面ID
            add_to_history: 是否添加到历史记录

        Returns:
            是否显示成功
        """
        try:
            # 隐藏当前页面
            if self.current_page:
                self.hide_page(self.current_page)

            # 加载页面
            if not self.load_page(page_id):
                return False

            page = self.pages[page_id]

            # 从缓存恢复
            if page.state == PageState.CACHED:
                page.restore_from_cache()

            # 触发显示前事件
            self._trigger_lifecycle_event(PageLifecycleEvent.BEFORE_SHOW, page_id, page)

            # 显示页面
            page.show()

            # 更新当前页面
            self.current_page = page_id

            # 添加到历史记录
            if add_to_history:
                if page_id in self.page_history:
                    self.page_history.remove(page_id)
                self.page_history.append(page_id)

                # 限制历史记录长度
                if len(self.page_history) > 50:
                    self.page_history = self.page_history[-50:]

            # 触发显示后事件
            self._trigger_lifecycle_event(PageLifecycleEvent.AFTER_SHOW, page_id, page)

            self.logger.debug(f"页面显示: {page_id}")
            return True

        except Exception as e:
            self.logger.error(f"页面显示失败 [{page_id}]: {e}")
            return False

    def hide_page(self, page_id: str) -> bool:
        """隐藏页面

        Args:
            page_id: 页面ID

        Returns:
            是否隐藏成功
        """
        try:
            if page_id not in self.pages:
                return False

            page = self.pages[page_id]
            if page.state != PageState.ACTIVE:
                return True

            # 触发隐藏前事件
            self._trigger_lifecycle_event(PageLifecycleEvent.BEFORE_HIDE, page_id, page)

            # 隐藏页面
            page.hide()

            # 缓存页面
            config = self.page_configs.get(page_id)
            if config and config.cache:
                self._cache_page(page_id)

            # 触发隐藏后事件
            self._trigger_lifecycle_event(PageLifecycleEvent.AFTER_HIDE, page_id, page)

            self.logger.debug(f"页面隐藏: {page_id}")
            return True

        except Exception as e:
            self.logger.error(f"页面隐藏失败 [{page_id}]: {e}")
            return False

    def destroy_page(self, page_id: str) -> bool:
        """销毁页面

        Args:
            page_id: 页面ID

        Returns:
            是否销毁成功
        """
        try:
            if page_id not in self.pages:
                return False

            page = self.pages[page_id]

            # 触发销毁前事件
            self._trigger_lifecycle_event(
                PageLifecycleEvent.BEFORE_DESTROY, page_id, page
            )

            # 销毁页面
            page.destroy()

            # 清理引用
            del self.pages[page_id]

            # 清理缓存
            if page_id in self.cached_pages:
                del self.cached_pages[page_id]

            # 更新当前页面
            if self.current_page == page_id:
                self.current_page = None

            # 从历史记录移除
            while page_id in self.page_history:
                self.page_history.remove(page_id)

            # 触发销毁后事件
            self._trigger_lifecycle_event(
                PageLifecycleEvent.AFTER_DESTROY, page_id, page
            )

            self.logger.debug(f"页面销毁: {page_id}")
            return True

        except Exception as e:
            self.logger.error(f"页面销毁失败 [{page_id}]: {e}")
            return False

    def _cache_page(self, page_id: str) -> None:
        """缓存页面

        Args:
            page_id: 页面ID
        """
        try:
            if page_id not in self.pages:
                return

            page = self.pages[page_id]
            config = self.page_configs.get(page_id)

            if not config or not config.cache:
                return

            # 检查缓存大小限制
            if len(self.cached_pages) >= self.max_cache_size:
                self._cleanup_cache()

            # 缓存页面
            page.cache()
            self.cached_pages[page_id] = time.time()

            self.logger.debug(f"页面缓存: {page_id}")

        except Exception as e:
            self.logger.error(f"页面缓存失败: {e}")

    def _cleanup_cache(self) -> None:
        """清理缓存"""
        try:
            current_time = time.time()
            expired_pages = []

            # 查找过期页面
            for page_id, cache_time in self.cached_pages.items():
                config = self.page_configs.get(page_id)
                timeout = (
                    config.cache_timeout
                    if config and config.cache_timeout
                    else self.default_cache_timeout
                )

                if current_time - cache_time > timeout:
                    expired_pages.append(page_id)

            # 移除过期页面
            for page_id in expired_pages:
                self.destroy_page(page_id)

            # 如果还是超过限制,移除最旧的页面
            while len(self.cached_pages) >= self.max_cache_size:
                oldest_page = min(self.cached_pages.items(), key=lambda x: x[1])[0]
                self.destroy_page(oldest_page)

            self.logger.debug(f"缓存清理完成,移除 {len(expired_pages)} 个过期页面")

        except Exception as e:
            self.logger.error(f"缓存清理失败: {e}")

    def _start_preload_thread(self) -> None:
        """启动预加载线程"""
        if self.preload_thread and self.preload_thread.is_alive():
            return

        self.preload_stop_event.clear()
        self.preload_thread = threading.Thread(target=self._preload_worker, daemon=True)
        self.preload_thread.start()

        self.logger.debug("预加载线程启动")

    def _stop_preload_thread(self) -> None:
        """停止预加载线程"""
        self.preload_stop_event.set()
        if self.preload_thread and self.preload_thread.is_alive():
            self.preload_thread.join(timeout=2.0)

        self.logger.debug("预加载线程停止")

    def _preload_worker(self) -> None:
        """预加载工作线程"""
        while not self.preload_stop_event.is_set():
            try:
                if self.preload_queue:
                    page_id = self.preload_queue.pop()

                    # 检查页面是否已加载
                    if page_id not in self.pages:
                        self.logger.debug(f"预加载页面: {page_id}")
                        self.load_page(page_id)

                # 等待一段时间再处理下一个
                self.preload_stop_event.wait(1.0)

            except Exception as e:
                self.logger.error(f"预加载工作线程错误: {e}")

    def _on_page_destroyed(self, page_id: str) -> None:
        """页面销毁回调

        Args:
            page_id: 页面ID
        """
        # 清理实例引用
        if page_id in self.page_instances:
            del self.page_instances[page_id]

    def _trigger_lifecycle_event(
        self, event: PageLifecycleEvent, page_id: str, page: BasePage
    ) -> None:
        """触发生命周期事件

        Args:
            event: 生命周期事件
            page_id: 页面ID
            page: 页面实例
        """
        try:
            callbacks = self.lifecycle_callbacks.get(event, [])
            for callback in callbacks:
                try:
                    callback(page_id, page)
                except Exception as e:
                    self.logger.error(f"生命周期回调执行失败 [{event.value}]: {e}")

        except Exception as e:
            self.logger.error(f"生命周期事件触发失败: {e}")

    def add_lifecycle_callback(
        self, event: PageLifecycleEvent, callback: Callable
    ) -> None:
        """添加生命周期回调

        Args:
            event: 生命周期事件
            callback: 回调函数
        """
        self.lifecycle_callbacks[event].append(callback)

    def remove_lifecycle_callback(
        self, event: PageLifecycleEvent, callback: Callable
    ) -> None:
        """移除生命周期回调

        Args:
            event: 生命周期事件
            callback: 回调函数
        """
        try:
            self.lifecycle_callbacks[event].remove(callback)
        except ValueError:
            self.logger.warning(f"生命周期回调不存在: {event.value}")

    def get_current_page(self) -> Optional[str]:
        """获取当前页面ID

        Returns:
            当前页面ID,如果没有则返回None
        """
        return self.current_page

    def get_page_history(self) -> List[str]:
        """获取页面历史记录

        Returns:
            页面历史记录列表
        """
        return self.page_history.copy()

    def go_back(self) -> bool:
        """返回上一页

        Returns:
            是否成功返回
        """
        if len(self.page_history) < 2:
            return False

        # 移除当前页面
        self.page_history.pop()

        # 获取上一页
        previous_page = self.page_history[-1]

        # 显示上一页(不添加到历史记录)
        return self.show_page(previous_page, add_to_history=False)

    def clear_history(self) -> None:
        """清空页面历史记录"""
        self.page_history.clear()

    def preload_page(self, page_id: str) -> None:
        """预加载页面

        Args:
            page_id: 页面ID
        """
        if self.preload_enabled and page_id in self.page_configs:
            self.preload_queue.add(page_id)

    def get_page_info(self) -> Dict[str, Any]:
        """获取页面管理器信息

        Returns:
            页面管理器信息字典
        """
        return {
            "current_page": self.current_page,
            "total_pages": len(self.page_configs),
            "loaded_pages": len(self.pages),
            "cached_pages": len(self.cached_pages),
            "preload_queue_size": len(self.preload_queue),
            "history_length": len(self.page_history),
            "max_cache_size": self.max_cache_size,
            "preload_enabled": self.preload_enabled,
            "lazy_load_enabled": self.lazy_load_enabled,
            "pages": {
                page_id: {
                    "state": page.state.value,
                    "title": config.title,
                    "cached": page_id in self.cached_pages,
                    "cache_time": self.cached_pages.get(page_id),
                }
                for page_id, page in self.pages.items()
                if (config := self.page_configs.get(page_id))
            },
        }

    def cleanup(self) -> None:
        """清理页面管理器资源"""
        try:
            # 停止预加载线程
            self._stop_preload_thread()

            # 销毁所有页面
            for page_id in list(self.pages.keys()):
                self.destroy_page(page_id)

            # 清理所有引用
            self.page_configs.clear()
            self.pages.clear()
            self.page_instances.clear()
            self.cached_pages.clear()
            self.preload_queue.clear()
            self.page_history.clear()

            # 清理回调
            for callbacks in self.lifecycle_callbacks.values():
                callbacks.clear()

            self.logger.debug("页面管理器资源清理完成")

        except Exception as e:
            self.logger.error(f"页面管理器资源清理失败: {e}")


class PageRouterTTK:
    """TTK页面路由器

    负责处理页面路由、导航和切换逻辑.
    """

    def __init__(self, page_manager: PageManagerTTK):
        """初始化页面路由器

        Args:
            page_manager: 页面管理器实例
        """
        self.page_manager = page_manager
        self.logger = logging.getLogger(self.__class__.__name__)

        # 路由表
        self.routes: Dict[str, str] = {}  # route_path -> page_id
        self.route_params: Dict[str, Dict[str, Any]] = {}  # route_path -> params

        # 导航守卫
        self.before_navigate_guards: List[Callable] = []
        self.after_navigate_guards: List[Callable] = []

        # 当前路由
        self.current_route: Optional[str] = None

    def register_route(
        self, route_path: str, page_id: str, params: Optional[Dict[str, Any]] = None
    ) -> None:
        """注册路由

        Args:
            route_path: 路由路径
            page_id: 页面ID
            params: 路由参数
        """
        try:
            self.routes[route_path] = page_id
            if params:
                self.route_params[route_path] = params

            self.logger.debug(f"路由注册: {route_path} -> {page_id}")

        except Exception as e:
            self.logger.error(f"路由注册失败: {e}")
            raise

    def unregister_route(self, route_path: str) -> None:
        """注销路由

        Args:
            route_path: 路由路径
        """
        try:
            if route_path in self.routes:
                del self.routes[route_path]

            if route_path in self.route_params:
                del self.route_params[route_path]

            self.logger.debug(f"路由注销: {route_path}")

        except Exception as e:
            self.logger.error(f"路由注销失败: {e}")

    def navigate_to(
        self, route_path: str, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """导航到指定路由

        Args:
            route_path: 路由路径
            params: 导航参数

        Returns:
            是否导航成功
        """
        try:
            # 检查路由是否存在
            if route_path not in self.routes:
                self.logger.warning(f"路由不存在: {route_path}")
                return False

            page_id = self.routes[route_path]

            # 执行导航前守卫
            for guard in self.before_navigate_guards:
                try:
                    if not guard(route_path, page_id, params):
                        self.logger.debug(f"导航被守卫阻止: {route_path}")
                        return False
                except Exception as e:
                    self.logger.error(f"导航前守卫执行失败: {e}")
                    return False

            # 设置页面参数
            if params:
                page = self.page_manager.get_page(page_id)
                if page:
                    for key, value in params.items():
                        page.set_data(key, value)

            # 显示页面
            success = self.page_manager.show_page(page_id)

            if success:
                self.current_route = route_path

                # 执行导航后守卫
                for guard in self.after_navigate_guards:
                    try:
                        guard(route_path, page_id, params)
                    except Exception as e:
                        self.logger.error(f"导航后守卫执行失败: {e}")

                self.logger.debug(f"导航成功: {route_path} -> {page_id}")

            return success

        except Exception as e:
            self.logger.error(f"导航失败 [{route_path}]: {e}")
            return False

    def navigate_to_page(
        self, page_id: str, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """直接导航到页面

        Args:
            page_id: 页面ID
            params: 导航参数

        Returns:
            是否导航成功
        """
        try:
            # 查找对应的路由
            route_path = None
            for path, pid in self.routes.items():
                if pid == page_id:
                    route_path = path
                    break

            if route_path:
                return self.navigate_to(route_path, params)
            # 直接显示页面
            if params:
                page = self.page_manager.get_page(page_id)
                if page:
                    for key, value in params.items():
                        page.set_data(key, value)

            return self.page_manager.show_page(page_id)

        except Exception as e:
            self.logger.error(f"页面导航失败 [{page_id}]: {e}")
            return False

    def go_back(self) -> bool:
        """返回上一页

        Returns:
            是否成功返回
        """
        return self.page_manager.go_back()

    def add_before_navigate_guard(self, guard: Callable) -> None:
        """添加导航前守卫

        Args:
            guard: 守卫函数,接收(route_path, page_id, params)参数,返回bool
        """
        self.before_navigate_guards.append(guard)

    def remove_before_navigate_guard(self, guard: Callable) -> None:
        """移除导航前守卫

        Args:
            guard: 守卫函数
        """
        try:
            self.before_navigate_guards.remove(guard)
        except ValueError:
            self.logger.warning("导航前守卫不存在")

    def add_after_navigate_guard(self, guard: Callable) -> None:
        """添加导航后守卫

        Args:
            guard: 守卫函数,接收(route_path, page_id, params)参数
        """
        self.after_navigate_guards.append(guard)

    def remove_after_navigate_guard(self, guard: Callable) -> None:
        """移除导航后守卫

        Args:
            guard: 守卫函数
        """
        try:
            self.after_navigate_guards.remove(guard)
        except ValueError:
            self.logger.warning("导航后守卫不存在")

    def get_current_route(self) -> Optional[str]:
        """获取当前路由

        Returns:
            当前路由路径,如果没有则返回None
        """
        return self.current_route

    def get_routes(self) -> Dict[str, str]:
        """获取所有路由

        Returns:
            路由映射字典
        """
        return self.routes.copy()

    def get_router_info(self) -> Dict[str, Any]:
        """获取路由器信息

        Returns:
            路由器信息字典
        """
        return {
            "current_route": self.current_route,
            "total_routes": len(self.routes),
            "before_guards": len(self.before_navigate_guards),
            "after_guards": len(self.after_navigate_guards),
            "routes": self.routes.copy(),
        }
