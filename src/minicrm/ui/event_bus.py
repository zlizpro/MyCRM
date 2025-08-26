"""MiniCRM 全局事件总线

提供应用程序级别的事件通信机制,包括:
- 事件发布和订阅
- 事件过滤和路由
- 异步事件处理
- 事件历史记录
- 事件优先级管理

设计原则:
- 松耦合:组件间通过事件通信,不直接依赖
- 高性能:支持异步处理和批量事件
- 可扩展:支持自定义事件类型和处理器
- 可调试:完整的事件历史和日志记录
"""

from collections import defaultdict, deque
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
import logging
import threading
import time
from typing import Any, Callable, Optional


class BaseObject:
    """基础对象类 - 替代QObject"""


class Signal:
    """信号类 - 替代Qt Signal"""

    def __init__(self, *args):
        self._callbacks: list[Callable] = []

    def connect(self, callback: Callable) -> None:
        """连接回调函数"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def emit(self, *args, **kwargs) -> None:
        """发射信号"""
        for callback in self._callbacks:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Signal callback error: {e}")


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


from minicrm.core.exceptions import UIError


class EventPriority(Enum):
    """事件优先级"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """事件基类"""

    type: str
    data: Any = None
    source: str | None = None
    target: str | None = None
    priority: EventPriority = EventPriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    event_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.event_id is None:
            self.event_id = f"{self.type}_{int(self.timestamp * 1000000)}"


class EventFilter:
    """事件过滤器基类"""

    def should_process(self, event: Event) -> bool:
        """判断是否应该处理该事件

        Args:
            event: 事件对象

        Returns:
            bool: 是否应该处理
        """
        return True


class TypeEventFilter(EventFilter):
    """按事件类型过滤"""

    def __init__(self, event_types: str | list[str]):
        if isinstance(event_types, str):
            self.event_types = {event_types}
        else:
            self.event_types = set(event_types)

    def should_process(self, event: Event) -> bool:
        return event.type in self.event_types


class SourceEventFilter(EventFilter):
    """按事件源过滤"""

    def __init__(self, sources: str | list[str]):
        if isinstance(sources, str):
            self.sources = {sources}
        else:
            self.sources = set(sources)

    def should_process(self, event: Event) -> bool:
        return event.source in self.sources


class PriorityEventFilter(EventFilter):
    """按优先级过滤"""

    def __init__(self, min_priority: EventPriority):
        self.min_priority = min_priority

    def should_process(self, event: Event) -> bool:
        return event.priority.value >= self.min_priority.value


@dataclass
class EventSubscription:
    """事件订阅信息"""

    callback: Callable[[Event], None]
    event_filter: EventFilter | None = None
    async_processing: bool = False
    weak_ref: bool = True
    subscription_id: str | None = None

    def __post_init__(self):
        if self.subscription_id is None:
            self.subscription_id = f"sub_{id(self.callback)}"


class EventBus(BaseObject):
    """全局事件总线

    提供应用程序级别的事件通信功能:
    - 事件发布和订阅管理
    - 事件过滤和路由
    - 异步事件处理
    - 事件历史记录
    - 性能监控和调试

    Signals:
        event_published: 事件发布信号 (event: Event)
        event_processed: 事件处理完成信号 (event: Event, processing_time: float)
        event_error: 事件处理错误信号 (event: Event, error: str)
    """

    # Qt信号定义
    event_published = Signal(Event)
    event_processed = Signal(Event, float)
    event_error = Signal(Event, str)

    def __init__(self, parent: BaseObject | None = None):
        """初始化事件总线

        Args:
            parent: 父对象
        """
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)

        # 事件订阅者
        self._subscribers: dict[str, list[EventSubscription]] = defaultdict(list)

        # 全局订阅者(监听所有事件)
        self._global_subscribers: list[EventSubscription] = []

        # 事件队列(按优先级排序)
        self._event_queue: deque = deque()

        # 事件历史记录
        self._event_history: deque = deque(maxlen=10000)

        # 异步处理线程池
        self._thread_pool = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="EventBus"
        )

        # 事件处理统计
        self._processing_stats: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"count": 0, "total_time": 0.0, "avg_time": 0.0, "errors": 0}
        )

        # 线程锁
        self._lock = threading.RLock()

        # 事件处理定时器
        self._processing_timer = Timer()
        self._processing_timer.timeout_connect(self._process_event_queue)
        self._processing_timer.start(10)  # 每10ms处理一次事件队列

        # 是否启用事件历史记录
        self._enable_history = True

        # 是否启用性能统计
        self._enable_stats = True

        self._logger.debug("事件总线初始化完成")

    def publish(
        self,
        event_type: str,
        data: Any = None,
        source: str | None = None,
        target: str | None = None,
        priority: EventPriority = EventPriority.NORMAL,
        metadata: dict[str, Any] | None = None,
        sync: bool = False,
    ) -> str:
        """发布事件

        Args:
            event_type: 事件类型
            data: 事件数据
            source: 事件源
            target: 事件目标
            priority: 事件优先级
            metadata: 事件元数据
            sync: 是否同步处理

        Returns:
            str: 事件ID
        """
        try:
            # 创建事件对象
            event = Event(
                type=event_type,
                data=data,
                source=source,
                target=target,
                priority=priority,
                metadata=metadata or {},
            )

            # 添加到历史记录
            if self._enable_history:
                self._event_history.append(event)

            # 发送Qt信号
            self.event_published.emit(event)

            if sync:
                # 同步处理
                self._process_event(event)
            else:
                # 添加到队列异步处理
                with self._lock:
                    self._add_to_queue(event)

            self._logger.debug(f"事件发布: {event_type} (ID: {event.event_id})")
            return event.event_id

        except Exception as e:
            self._logger.error(f"事件发布失败 [{event_type}]: {e}")
            raise UIError(f"事件发布失败: {e}", "EventBus") from e

    def subscribe(
        self,
        event_type: str,
        callback: Callable[[Event], None],
        event_filter: EventFilter | None = None,
        async_processing: bool = False,
        weak_ref: bool = True,
    ) -> str:
        """订阅事件

        Args:
            event_type: 事件类型
            callback: 回调函数
            event_filter: 事件过滤器
            async_processing: 是否异步处理
            weak_ref: 是否使用弱引用

        Returns:
            str: 订阅ID
        """
        try:
            subscription = EventSubscription(
                callback=callback,
                event_filter=event_filter,
                async_processing=async_processing,
                weak_ref=weak_ref,
            )

            with self._lock:
                self._subscribers[event_type].append(subscription)

            self._logger.debug(
                f"订阅事件: {event_type} (ID: {subscription.subscription_id})"
            )
            return subscription.subscription_id

        except Exception as e:
            self._logger.error(f"事件订阅失败 [{event_type}]: {e}")
            raise UIError(f"事件订阅失败: {e}", "EventBus") from e

    def subscribe_global(
        self,
        callback: Callable[[Event], None],
        event_filter: EventFilter | None = None,
        async_processing: bool = False,
        weak_ref: bool = True,
    ) -> str:
        """订阅所有事件

        Args:
            callback: 回调函数
            event_filter: 事件过滤器
            async_processing: 是否异步处理
            weak_ref: 是否使用弱引用

        Returns:
            str: 订阅ID
        """
        try:
            subscription = EventSubscription(
                callback=callback,
                event_filter=event_filter,
                async_processing=async_processing,
                weak_ref=weak_ref,
            )

            with self._lock:
                self._global_subscribers.append(subscription)

            self._logger.debug(f"订阅全局事件 (ID: {subscription.subscription_id})")
            return subscription.subscription_id

        except Exception as e:
            self._logger.error(f"全局事件订阅失败: {e}")
            raise UIError(f"全局事件订阅失败: {e}", "EventBus") from e

    def unsubscribe(self, subscription_id: str) -> bool:
        """取消订阅

        Args:
            subscription_id: 订阅ID

        Returns:
            bool: 是否成功取消订阅
        """
        try:
            with self._lock:
                # 在特定事件类型订阅中查找
                for event_type, subscriptions in self._subscribers.items():
                    for i, subscription in enumerate(subscriptions):
                        if subscription.subscription_id == subscription_id:
                            del subscriptions[i]
                            self._logger.debug(
                                f"取消事件订阅: {event_type} (ID: {subscription_id})"
                            )
                            return True

                # 在全局订阅中查找
                for i, subscription in enumerate(self._global_subscribers):
                    if subscription.subscription_id == subscription_id:
                        del self._global_subscribers[i]
                        self._logger.debug(f"取消全局事件订阅 (ID: {subscription_id})")
                        return True

                return False

        except Exception as e:
            self._logger.error(f"取消订阅失败 [{subscription_id}]: {e}")
            return False

    def unsubscribe_all(self, event_type: str | None = None) -> int:
        """取消所有订阅

        Args:
            event_type: 事件类型,如果为None则取消所有订阅

        Returns:
            int: 取消的订阅数量
        """
        try:
            count = 0

            with self._lock:
                if event_type:
                    # 取消特定事件类型的订阅
                    if event_type in self._subscribers:
                        count = len(self._subscribers[event_type])
                        del self._subscribers[event_type]
                else:
                    # 取消所有订阅
                    for subscriptions in self._subscribers.values():
                        count += len(subscriptions)
                    self._subscribers.clear()

                    count += len(self._global_subscribers)
                    self._global_subscribers.clear()

            self._logger.debug(f"取消订阅数量: {count}")
            return count

        except Exception as e:
            self._logger.error(f"取消所有订阅失败: {e}")
            return 0

    def _add_to_queue(self, event: Event) -> None:
        """添加事件到队列(按优先级排序)"""
        # 简单的优先级队列实现
        inserted = False
        for i, queued_event in enumerate(self._event_queue):
            if event.priority.value > queued_event.priority.value:
                self._event_queue.insert(i, event)
                inserted = True
                break

        if not inserted:
            self._event_queue.append(event)

    def _process_event_queue(self) -> None:
        """处理事件队列"""
        try:
            with self._lock:
                if not self._event_queue:
                    return

                # 批量处理事件(最多10个)
                batch_size = min(10, len(self._event_queue))
                events_to_process = []

                for _ in range(batch_size):
                    if self._event_queue:
                        events_to_process.append(self._event_queue.popleft())

            # 处理事件
            for event in events_to_process:
                self._process_event(event)

        except Exception as e:
            self._logger.error(f"事件队列处理失败: {e}")

    def _process_event(self, event: Event) -> None:
        """处理单个事件"""
        try:
            start_time = time.time()

            # 获取订阅者
            subscribers = []

            with self._lock:
                # 特定事件类型的订阅者
                if event.type in self._subscribers:
                    subscribers.extend(self._subscribers[event.type])

                # 全局订阅者
                subscribers.extend(self._global_subscribers)

            # 处理订阅者
            for subscription in subscribers:
                try:
                    # 检查过滤器
                    if (
                        subscription.event_filter
                        and not subscription.event_filter.should_process(event)
                    ):
                        continue

                    # 检查目标
                    if event.target and hasattr(subscription.callback, "__self__"):
                        callback_source = getattr(
                            subscription.callback.__self__, "__class__", {}
                        ).get("__name__", "")
                        if callback_source != event.target:
                            continue

                    # 执行回调
                    if subscription.async_processing:
                        # 异步处理
                        self._thread_pool.submit(
                            self._safe_callback, subscription.callback, event
                        )
                    else:
                        # 同步处理
                        self._safe_callback(subscription.callback, event)

                except Exception as e:
                    self._logger.error(f"订阅者处理失败 [{event.type}]: {e}")
                    self.event_error.emit(event, str(e))

            # 更新统计信息
            processing_time = time.time() - start_time
            if self._enable_stats:
                self._update_stats(event.type, processing_time, success=True)

            # 发送处理完成信号
            self.event_processed.emit(event, processing_time)

        except Exception as e:
            self._logger.error(f"事件处理失败 [{event.type}]: {e}")
            if self._enable_stats:
                self._update_stats(event.type, 0.0, success=False)
            self.event_error.emit(event, str(e))

    def _safe_callback(self, callback: Callable[[Event], None], event: Event) -> None:
        """安全执行回调函数"""
        try:
            callback(event)
        except Exception as e:
            self._logger.error(f"回调函数执行失败 [{event.type}]: {e}")
            raise

    def _update_stats(
        self, event_type: str, processing_time: float, success: bool
    ) -> None:
        """更新处理统计信息"""
        try:
            stats = self._processing_stats[event_type]
            stats["count"] += 1

            if success:
                stats["total_time"] += processing_time
                stats["avg_time"] = stats["total_time"] / stats["count"]
            else:
                stats["errors"] += 1

        except Exception as e:
            self._logger.error(f"统计信息更新失败: {e}")

    def get_event_history(
        self, event_type: str | None = None, limit: int = 100
    ) -> list[Event]:
        """获取事件历史记录

        Args:
            event_type: 事件类型过滤
            limit: 返回数量限制

        Returns:
            List[Event]: 事件历史列表
        """
        try:
            with self._lock:
                if event_type:
                    filtered_events = [
                        e for e in self._event_history if e.type == event_type
                    ]
                else:
                    filtered_events = list(self._event_history)

                # 返回最新的事件
                return filtered_events[-limit:] if limit > 0 else filtered_events

        except Exception as e:
            self._logger.error(f"获取事件历史失败: {e}")
            return []

    def get_processing_stats(self) -> dict[str, dict[str, Any]]:
        """获取处理统计信息"""
        with self._lock:
            return dict(self._processing_stats)

    def clear_history(self) -> None:
        """清空事件历史"""
        with self._lock:
            self._event_history.clear()
            self._logger.debug("事件历史已清空")

    def clear_stats(self) -> None:
        """清空统计信息"""
        with self._lock:
            self._processing_stats.clear()
            self._logger.debug("统计信息已清空")

    def set_enable_history(self, enabled: bool) -> None:
        """设置是否启用历史记录"""
        self._enable_history = enabled
        self._logger.debug(f"事件历史记录: {'启用' if enabled else '禁用'}")

    def set_enable_stats(self, enabled: bool) -> None:
        """设置是否启用统计信息"""
        self._enable_stats = enabled
        self._logger.debug(f"统计信息: {'启用' if enabled else '禁用'}")

    def get_queue_size(self) -> int:
        """获取事件队列大小"""
        with self._lock:
            return len(self._event_queue)

    def get_subscriber_count(self, event_type: str | None = None) -> int:
        """获取订阅者数量"""
        with self._lock:
            if event_type:
                return len(self._subscribers.get(event_type, []))
            total = sum(len(subs) for subs in self._subscribers.values())
            total += len(self._global_subscribers)
            return total

    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 停止定时器
            self._processing_timer.stop()

            # 关闭线程池
            self._thread_pool.shutdown(wait=True)

            # 清空订阅者
            with self._lock:
                self._subscribers.clear()
                self._global_subscribers.clear()
                self._event_queue.clear()
                self._event_history.clear()
                self._processing_stats.clear()

            self._logger.debug("事件总线清理完成")

        except Exception as e:
            self._logger.error(f"事件总线清理失败: {e}")


# 全局事件总线实例
_global_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """获取全局事件总线实例"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def set_global_event_bus(event_bus: EventBus) -> None:
    """设置全局事件总线实例"""
    global _global_event_bus
    _global_event_bus = event_bus


# 便捷函数
def publish_event(
    event_type: str,
    data: Any = None,
    source: str | None = None,
    priority: EventPriority = EventPriority.NORMAL,
) -> str:
    """发布事件"""
    return get_event_bus().publish(
        event_type, data=data, source=source, priority=priority
    )


def subscribe_event(
    event_type: str,
    callback: Callable[[Event], None],
    event_filter: EventFilter | None = None,
) -> str:
    """订阅事件"""
    return get_event_bus().subscribe(event_type, callback, event_filter=event_filter)


def unsubscribe_event(subscription_id: str) -> bool:
    """取消订阅事件"""
    return get_event_bus().unsubscribe(subscription_id)
