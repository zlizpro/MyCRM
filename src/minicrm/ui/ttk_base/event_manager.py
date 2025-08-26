"""TTK事件管理系统

提供统一的事件绑定和处理机制,包括:
- 统一的事件绑定和解绑接口
- 事件委托和事件传播机制
- 事件调试和性能监控功能
- 自定义事件支持
- 异步事件处理

设计目标:
1. 简化事件处理的复杂性
2. 提供统一的事件管理接口
3. 支持事件调试和性能分析
4. 减少内存使用和提高性能

作者: MiniCRM开发团队
"""

from collections import defaultdict
from enum import Enum
from functools import wraps
import logging
import queue
import threading
import time
import tkinter as tk
from typing import Any, Callable, Dict, List, Optional
import weakref


class EventType(Enum):
    """事件类型枚举"""

    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    FOCUS_IN = "focus_in"
    FOCUS_OUT = "focus_out"
    MOUSE_ENTER = "mouse_enter"
    MOUSE_LEAVE = "mouse_leave"
    MOUSE_MOVE = "mouse_move"
    WINDOW_RESIZE = "window_resize"
    CUSTOM = "custom"


class EventPriority(Enum):
    """事件优先级枚举"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class Event:
    """事件对象

    封装事件的基本信息,包括事件类型、源组件、
    数据等信息.
    """

    def __init__(
        self,
        event_type: str,
        source: Any = None,
        data: Optional[Dict[str, Any]] = None,
        priority: EventPriority = EventPriority.NORMAL,
        timestamp: Optional[float] = None,
    ):
        """初始化事件对象

        Args:
            event_type: 事件类型
            source: 事件源对象
            data: 事件数据
            priority: 事件优先级
            timestamp: 事件时间戳
        """
        self.event_type = event_type
        self.source = source
        self.data = data or {}
        self.priority = priority
        self.timestamp = timestamp or time.time()
        self.handled = False
        self.cancelled = False

    def cancel(self) -> None:
        """取消事件"""
        self.cancelled = True

    def mark_handled(self) -> None:
        """标记事件已处理"""
        self.handled = True

    def is_cancelled(self) -> bool:
        """检查事件是否被取消"""
        return self.cancelled

    def is_handled(self) -> bool:
        """检查事件是否已处理"""
        return self.handled


class EventHandler:
    """事件处理器包装类

    包装事件处理函数,提供额外的元数据和功能.
    """

    def __init__(
        self,
        handler: Callable,
        priority: EventPriority = EventPriority.NORMAL,
        once: bool = False,
        condition: Optional[Callable[[Event], bool]] = None,
    ):
        """初始化事件处理器

        Args:
            handler: 处理函数
            priority: 优先级
            once: 是否只执行一次
            condition: 执行条件函数
        """
        self.handler = handler
        self.priority = priority
        self.once = once
        self.condition = condition
        self.call_count = 0
        self.last_call_time = None
        self.total_execution_time = 0.0

    def can_handle(self, event: Event) -> bool:
        """检查是否可以处理事件

        Args:
            event: 事件对象

        Returns:
            是否可以处理
        """
        if self.condition:
            return self.condition(event)
        return True

    def handle(self, event: Event) -> Any:
        """处理事件

        Args:
            event: 事件对象

        Returns:
            处理结果
        """
        if not self.can_handle(event):
            return None

        start_time = time.time()
        try:
            result = self.handler(event)
            self.call_count += 1
            self.last_call_time = start_time
            self.total_execution_time += time.time() - start_time
            return result
        except Exception as e:
            logging.getLogger(__name__).error(f"事件处理器执行失败: {e}")
            raise

    def should_remove(self) -> bool:
        """检查是否应该移除处理器

        Returns:
            是否应该移除
        """
        return self.once and self.call_count > 0


class EventManager:
    """TTK事件管理器

    提供统一的事件管理功能,包括事件绑定、解绑、
    触发、委托等功能.
    """

    def __init__(self, enable_debug: bool = False):
        """初始化事件管理器

        Args:
            enable_debug: 是否启用调试模式
        """
        self.logger = logging.getLogger(__name__)
        self.enable_debug = enable_debug

        # 事件处理器存储 {event_type: [EventHandler]}
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)

        # 组件事件绑定存储 {widget: {event_type: [EventHandler]}}
        self._widget_handlers: Dict[Any, Dict[str, List[EventHandler]]] = defaultdict(
            lambda: defaultdict(list)
        )

        # 事件委托存储 {parent: {event_type: [EventHandler]}}
        self._delegated_handlers: Dict[Any, Dict[str, List[EventHandler]]] = (
            defaultdict(lambda: defaultdict(list))
        )

        # 异步事件队列
        self._event_queue: queue.Queue = queue.Queue()
        self._async_thread: Optional[threading.Thread] = None
        self._stop_async = threading.Event()

        # 事件统计
        self._event_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "count": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "last_triggered": None,
            }
        )

        # 弱引用存储,避免内存泄漏
        self._weak_refs: Dict[Any, weakref.ref] = {}

        # 启动异步事件处理线程
        self._start_async_processing()

    def _start_async_processing(self) -> None:
        """启动异步事件处理线程"""
        if self._async_thread is None or not self._async_thread.is_alive():
            self._async_thread = threading.Thread(
                target=self._async_event_processor, daemon=True
            )
            self._async_thread.start()

    def _async_event_processor(self) -> None:
        """异步事件处理器"""
        while not self._stop_async.is_set():
            try:
                # 从队列获取事件,超时1秒
                event = self._event_queue.get(timeout=1.0)
                self._process_event_sync(event)
                self._event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"异步事件处理失败: {e}")

    def bind_event(
        self,
        widget: tk.Widget,
        event_type: str,
        handler: Callable,
        priority: EventPriority = EventPriority.NORMAL,
        once: bool = False,
        condition: Optional[Callable[[Event], bool]] = None,
    ) -> None:
        """绑定事件到组件

        Args:
            widget: 目标组件
            event_type: 事件类型
            handler: 事件处理函数
            priority: 优先级
            once: 是否只执行一次
            condition: 执行条件
        """
        event_handler = EventHandler(handler, priority, once, condition)

        # 添加到组件事件存储
        self._widget_handlers[widget][event_type].append(event_handler)

        # 按优先级排序
        self._widget_handlers[widget][event_type].sort(
            key=lambda h: h.priority.value, reverse=True
        )

        # 绑定到tkinter事件系统
        tkinter_event = self._get_tkinter_event(event_type)
        if tkinter_event:
            widget.bind(
                tkinter_event,
                lambda e: self._handle_widget_event(widget, event_type, e),
            )

        # 创建弱引用
        if widget not in self._weak_refs:
            self._weak_refs[widget] = weakref.ref(
                widget, lambda ref: self._cleanup_widget_handlers(widget)
            )

        if self.enable_debug:
            self.logger.debug(f"绑定事件: {widget} -> {event_type}")

    def unbind_event(
        self, widget: tk.Widget, event_type: str, handler: Optional[Callable] = None
    ) -> None:
        """解绑事件

        Args:
            widget: 目标组件
            event_type: 事件类型
            handler: 特定的处理函数,None表示解绑所有
        """
        if widget not in self._widget_handlers:
            return

        if event_type not in self._widget_handlers[widget]:
            return

        if handler is None:
            # 解绑所有处理器
            self._widget_handlers[widget][event_type].clear()
        else:
            # 解绑特定处理器
            self._widget_handlers[widget][event_type] = [
                h
                for h in self._widget_handlers[widget][event_type]
                if h.handler != handler
            ]

        # 如果没有处理器了,从tkinter解绑
        if not self._widget_handlers[widget][event_type]:
            tkinter_event = self._get_tkinter_event(event_type)
            if tkinter_event:
                widget.unbind(tkinter_event)

        if self.enable_debug:
            self.logger.debug(f"解绑事件: {widget} -> {event_type}")

    def bind_global_event(
        self,
        event_type: str,
        handler: Callable,
        priority: EventPriority = EventPriority.NORMAL,
        once: bool = False,
        condition: Optional[Callable[[Event], bool]] = None,
    ) -> None:
        """绑定全局事件

        Args:
            event_type: 事件类型
            handler: 事件处理函数
            priority: 优先级
            once: 是否只执行一次
            condition: 执行条件
        """
        event_handler = EventHandler(handler, priority, once, condition)
        self._handlers[event_type].append(event_handler)

        # 按优先级排序
        self._handlers[event_type].sort(key=lambda h: h.priority.value, reverse=True)

        if self.enable_debug:
            self.logger.debug(f"绑定全局事件: {event_type}")

    def unbind_global_event(
        self, event_type: str, handler: Optional[Callable] = None
    ) -> None:
        """解绑全局事件

        Args:
            event_type: 事件类型
            handler: 特定的处理函数,None表示解绑所有
        """
        if event_type not in self._handlers:
            return

        if handler is None:
            self._handlers[event_type].clear()
        else:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h.handler != handler
            ]

        if self.enable_debug:
            self.logger.debug(f"解绑全局事件: {event_type}")

    def delegate_event(
        self,
        parent: tk.Widget,
        event_type: str,
        handler: Callable,
        selector: Optional[Callable[[tk.Widget], bool]] = None,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> None:
        """委托事件处理

        Args:
            parent: 父组件
            event_type: 事件类型
            handler: 事件处理函数
            selector: 子组件选择器函数
            priority: 优先级
        """

        def delegated_handler(event: Event) -> Any:
            # 检查事件源是否匹配选择器
            if selector and not selector(event.source):
                return None
            return handler(event)

        event_handler = EventHandler(delegated_handler, priority)
        self._delegated_handlers[parent][event_type].append(event_handler)

        if self.enable_debug:
            self.logger.debug(f"委托事件: {parent} -> {event_type}")

    def trigger_event(
        self,
        event_type: str,
        source: Any = None,
        data: Optional[Dict[str, Any]] = None,
        async_mode: bool = False,
    ) -> None:
        """触发事件

        Args:
            event_type: 事件类型
            source: 事件源
            data: 事件数据
            async_mode: 是否异步处理
        """
        event = Event(event_type, source, data)

        if async_mode:
            self._event_queue.put(event)
        else:
            self._process_event_sync(event)

    def _process_event_sync(self, event: Event) -> None:
        """同步处理事件

        Args:
            event: 事件对象
        """
        start_time = time.time()

        try:
            # 处理全局事件处理器
            self._execute_handlers(self._handlers.get(event.event_type, []), event)

            # 处理组件特定事件处理器
            if event.source in self._widget_handlers:
                handlers = self._widget_handlers[event.source].get(event.event_type, [])
                self._execute_handlers(handlers, event)

            # 处理委托事件
            self._process_delegated_events(event)

            # 更新统计信息
            self._update_event_stats(event.event_type, time.time() - start_time)

        except Exception as e:
            self.logger.error(f"事件处理失败 [{event.event_type}]: {e}")

    def _execute_handlers(self, handlers: List[EventHandler], event: Event) -> None:
        """执行事件处理器列表

        Args:
            handlers: 处理器列表
            event: 事件对象
        """
        handlers_to_remove = []

        for handler in handlers:
            if event.is_cancelled():
                break

            try:
                handler.handle(event)

                # 检查是否需要移除处理器
                if handler.should_remove():
                    handlers_to_remove.append(handler)

            except Exception as e:
                self.logger.error(f"事件处理器执行失败: {e}")

        # 移除一次性处理器
        for handler in handlers_to_remove:
            if handler in handlers:
                handlers.remove(handler)

    def _process_delegated_events(self, event: Event) -> None:
        """处理委托事件

        Args:
            event: 事件对象
        """
        for parent, event_handlers in self._delegated_handlers.items():
            if event.event_type in event_handlers:
                # 检查事件源是否是父组件的子组件
                if self._is_child_of(event.source, parent):
                    self._execute_handlers(event_handlers[event.event_type], event)

    def _is_child_of(self, child: Any, parent: Any) -> bool:
        """检查是否是子组件

        Args:
            child: 子组件
            parent: 父组件

        Returns:
            是否是子组件
        """
        if not hasattr(child, "master"):
            return False

        current = child
        while current and hasattr(current, "master"):
            if current.master == parent:
                return True
            current = current.master

        return False

    def _handle_widget_event(
        self, widget: tk.Widget, event_type: str, tk_event
    ) -> None:
        """处理组件事件

        Args:
            widget: 组件
            event_type: 事件类型
            tk_event: tkinter事件对象
        """
        # 转换tkinter事件数据
        event_data = self._convert_tk_event_data(tk_event)

        # 触发自定义事件
        self.trigger_event(event_type, widget, event_data)

    def _convert_tk_event_data(self, tk_event) -> Dict[str, Any]:
        """转换tkinter事件数据

        Args:
            tk_event: tkinter事件对象

        Returns:
            事件数据字典
        """
        data = {}

        # 鼠标事件数据
        if hasattr(tk_event, "x") and hasattr(tk_event, "y"):
            data["x"] = tk_event.x
            data["y"] = tk_event.y

        if hasattr(tk_event, "x_root") and hasattr(tk_event, "y_root"):
            data["x_root"] = tk_event.x_root
            data["y_root"] = tk_event.y_root

        # 键盘事件数据
        if hasattr(tk_event, "keysym"):
            data["key"] = tk_event.keysym

        if hasattr(tk_event, "char"):
            data["char"] = tk_event.char

        # 修饰键状态
        if hasattr(tk_event, "state"):
            data["state"] = tk_event.state

        return data

    def _get_tkinter_event(self, event_type: str) -> Optional[str]:
        """获取对应的tkinter事件名称

        Args:
            event_type: 自定义事件类型

        Returns:
            tkinter事件名称
        """
        event_mapping = {
            EventType.CLICK.value: "<Button-1>",
            EventType.DOUBLE_CLICK.value: "<Double-Button-1>",
            EventType.RIGHT_CLICK.value: "<Button-3>",
            EventType.KEY_PRESS.value: "<KeyPress>",
            EventType.KEY_RELEASE.value: "<KeyRelease>",
            EventType.FOCUS_IN.value: "<FocusIn>",
            EventType.FOCUS_OUT.value: "<FocusOut>",
            EventType.MOUSE_ENTER.value: "<Enter>",
            EventType.MOUSE_LEAVE.value: "<Leave>",
            EventType.MOUSE_MOVE.value: "<Motion>",
            EventType.WINDOW_RESIZE.value: "<Configure>",
        }

        return event_mapping.get(event_type)

    def _update_event_stats(self, event_type: str, execution_time: float) -> None:
        """更新事件统计信息

        Args:
            event_type: 事件类型
            execution_time: 执行时间
        """
        stats = self._event_stats[event_type]
        stats["count"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["count"]
        stats["last_triggered"] = time.time()

    def _cleanup_widget_handlers(self, widget: Any) -> None:
        """清理组件事件处理器

        Args:
            widget: 组件
        """
        if widget in self._widget_handlers:
            del self._widget_handlers[widget]

        if widget in self._weak_refs:
            del self._weak_refs[widget]

        if self.enable_debug:
            self.logger.debug(f"清理组件事件处理器: {widget}")

    def get_event_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取事件统计信息

        Returns:
            事件统计信息字典
        """
        return dict(self._event_stats)

    def clear_event_stats(self) -> None:
        """清空事件统计信息"""
        self._event_stats.clear()

    def enable_event_debugging(self, enabled: bool = True) -> None:
        """启用/禁用事件调试

        Args:
            enabled: 是否启用
        """
        self.enable_debug = enabled

    def cleanup(self) -> None:
        """清理事件管理器资源"""
        # 停止异步处理线程
        self._stop_async.set()
        if self._async_thread and self._async_thread.is_alive():
            self._async_thread.join(timeout=1.0)

        # 清理所有处理器
        self._handlers.clear()
        self._widget_handlers.clear()
        self._delegated_handlers.clear()
        self._weak_refs.clear()

        # 清理队列
        while not self._event_queue.empty():
            try:
                self._event_queue.get_nowait()
            except queue.Empty:
                break

        self.logger.debug("事件管理器清理完成")


# 装饰器支持
def event_handler(
    event_type: str,
    priority: EventPriority = EventPriority.NORMAL,
    once: bool = False,
    condition: Optional[Callable[[Event], bool]] = None,
):
    """事件处理器装饰器

    Args:
        event_type: 事件类型
        priority: 优先级
        once: 是否只执行一次
        condition: 执行条件
    """

    def decorator(func: Callable) -> Callable:
        func._event_type = event_type
        func._event_priority = priority
        func._event_once = once
        func._event_condition = condition
        return func

    return decorator


def throttle(interval: float):
    """事件节流装饰器

    Args:
        interval: 节流间隔(秒)
    """

    def decorator(func: Callable) -> Callable:
        last_call_time = [0.0]

        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            if current_time - last_call_time[0] >= interval:
                last_call_time[0] = current_time
                return func(*args, **kwargs)

        return wrapper

    return decorator


def debounce(delay: float):
    """事件防抖装饰器

    Args:
        delay: 防抖延迟(秒)
    """

    def decorator(func: Callable) -> Callable:
        timer = [None]

        @wraps(func)
        def wrapper(*args, **kwargs):
            def delayed_call():
                func(*args, **kwargs)

            if timer[0]:
                timer[0].cancel()

            timer[0] = threading.Timer(delay, delayed_call)
            timer[0].start()

        return wrapper

    return decorator


# 全局事件管理器实例
_global_event_manager: Optional[EventManager] = None


def get_global_event_manager() -> EventManager:
    """获取全局事件管理器实例

    Returns:
        全局事件管理器
    """
    global _global_event_manager
    if _global_event_manager is None:
        _global_event_manager = EventManager()
    return _global_event_manager


def cleanup_global_event_manager() -> None:
    """清理全局事件管理器"""
    global _global_event_manager
    if _global_event_manager:
        _global_event_manager.cleanup()
        _global_event_manager = None
