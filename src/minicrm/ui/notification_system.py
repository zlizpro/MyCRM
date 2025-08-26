"""MiniCRM 全局通知和消息系统

提供应用程序级别的通知和消息功能,包括:
- 多种类型的通知(信息、警告、错误、成功)
- 通知队列管理
- 通知持久化和历史记录
- 通知优先级和过期机制
- 自定义通知样式和行为

设计原则:
- 非侵入式:通知不阻塞用户操作
- 可配置:支持自定义通知样式和行为
- 高性能:支持批量通知和异步处理
- 可扩展:支持自定义通知类型和处理器
"""

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
import logging
import threading
import time
from typing import Any, Callable, Optional
from uuid import uuid4


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


class Widget:
    """组件类 - 替代QWidget"""

    def __init__(self):
        self._destroyed = False

    def is_destroyed(self) -> bool:
        """检查是否已销毁"""
        return self._destroyed


from minicrm.core.exceptions import UIError
from minicrm.ui.event_bus import EventPriority, get_event_bus


class NotificationType(Enum):
    """通知类型"""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    PROGRESS = "progress"
    CUSTOM = "custom"


class NotificationPriority(Enum):
    """通知优先级"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Notification:
    """通知对象"""

    id: str = field(default_factory=lambda: str(uuid4()))
    type: NotificationType = NotificationType.INFO
    title: str = ""
    message: str = ""
    priority: NotificationPriority = NotificationPriority.NORMAL
    duration: int | None = None  # 显示时长(毫秒),None表示不自动关闭
    timestamp: float = field(default_factory=time.time)
    source: str | None = None
    actions: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    persistent: bool = False  # 是否持久化到历史记录
    dismissible: bool = True  # 是否可以手动关闭

    def __post_init__(self):
        # 根据类型设置默认持续时间
        if self.duration is None:
            if self.type == NotificationType.ERROR:
                self.duration = 8000  # 错误通知显示8秒
            elif self.type == NotificationType.WARNING:
                self.duration = 6000  # 警告通知显示6秒
            elif self.type == NotificationType.SUCCESS:
                self.duration = 4000  # 成功通知显示4秒
            elif self.type == NotificationType.INFO:
                self.duration = 3000  # 信息通知显示3秒
            elif self.type == NotificationType.PROGRESS:
                self.duration = None  # 进度通知不自动关闭
            else:
                self.duration = 5000  # 自定义通知默认5秒


class NotificationFilter:
    """通知过滤器基类"""

    def should_show(self, notification: Notification) -> bool:
        """判断是否应该显示该通知

        Args:
            notification: 通知对象

        Returns:
            bool: 是否应该显示
        """
        return True


class TypeNotificationFilter(NotificationFilter):
    """按通知类型过滤"""

    def __init__(self, allowed_types: set[NotificationType]):
        self.allowed_types = allowed_types

    def should_show(self, notification: Notification) -> bool:
        return notification.type in self.allowed_types


class PriorityNotificationFilter(NotificationFilter):
    """按优先级过滤"""

    def __init__(self, min_priority: NotificationPriority):
        self.min_priority = min_priority

    def should_show(self, notification: Notification) -> bool:
        return notification.priority.value >= self.min_priority.value


class NotificationHandler:
    """通知处理器基类"""

    def handle_notification(self, notification: Notification) -> bool:
        """处理通知

        Args:
            notification: 通知对象

        Returns:
            bool: 是否处理成功
        """
        return True

    def can_handle(self, notification: Notification) -> bool:
        """判断是否可以处理该通知

        Args:
            notification: 通知对象

        Returns:
            bool: 是否可以处理
        """
        return True


class StatusBarNotificationHandler(NotificationHandler):
    """状态栏通知处理器"""

    def __init__(self, status_bar_widget: Widget | None = None):
        self.status_bar_widget = status_bar_widget

    def handle_notification(self, notification: Notification) -> bool:
        """在状态栏显示通知"""
        try:
            if self.status_bar_widget and hasattr(
                self.status_bar_widget, "showMessage"
            ):
                message = (
                    f"{notification.title}: {notification.message}"
                    if notification.title
                    else notification.message
                )
                duration = notification.duration or 3000
                self.status_bar_widget.showMessage(message, duration)
                return True
            return False
        except Exception:
            return False

    def can_handle(self, notification: Notification) -> bool:
        return self.status_bar_widget is not None


class LogNotificationHandler(NotificationHandler):
    """日志通知处理器"""

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger(__name__)

    def handle_notification(self, notification: Notification) -> bool:
        """将通知记录到日志"""
        try:
            message = (
                f"{notification.title}: {notification.message}"
                if notification.title
                else notification.message
            )

            if notification.type == NotificationType.ERROR:
                self.logger.error(message)
            elif notification.type == NotificationType.WARNING:
                self.logger.warning(message)
            elif notification.type == NotificationType.SUCCESS:
                self.logger.info(f"SUCCESS: {message}")
            else:
                self.logger.info(message)

            return True
        except Exception:
            return False


class NotificationSystem(BaseObject):
    """全局通知和消息系统

    提供应用程序级别的通知管理功能:
    - 通知创建和显示
    - 通知队列管理
    - 通知过滤和路由
    - 通知历史记录
    - 自定义通知处理器

    Signals:
        notification_added: 通知添加信号 (notification: Notification)
        notification_shown: 通知显示信号 (notification: Notification)
        notification_dismissed: 通知关闭信号 (notification: Notification)
        notification_expired: 通知过期信号 (notification: Notification)
    """

    # Qt信号定义
    notification_added = Signal(Notification)
    notification_shown = Signal(Notification)
    notification_dismissed = Signal(Notification)
    notification_expired = Signal(Notification)

    def __init__(self, parent: BaseObject | None = None):
        """初始化通知系统

        Args:
            parent: 父对象
        """
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)

        # 通知队列
        self._notification_queue: deque = deque()

        # 当前显示的通知
        self._active_notifications: dict[str, Notification] = {}

        # 通知历史记录
        self._notification_history: deque = deque(maxlen=1000)

        # 通知处理器
        self._handlers: list[NotificationHandler] = []

        # 通知过滤器
        self._filters: list[NotificationFilter] = []

        # 配置选项
        self._max_concurrent_notifications = 5
        self._enable_history = True
        self._enable_sound = False

        # 定时器(用于处理过期通知)
        self._cleanup_timer = Timer()
        self._cleanup_timer.timeout_connect(self._cleanup_expired_notifications)
        self._cleanup_timer.start(1000)  # 每秒检查一次过期通知

        # 事件总线
        self._event_bus = get_event_bus()

        # 设置默认处理器
        self._setup_default_handlers()

        # 设置事件监听
        self._setup_event_listeners()

        self._logger.debug("通知系统初始化完成")

    def add_handler(self, handler: NotificationHandler) -> None:
        """添加通知处理器

        Args:
            handler: 通知处理器
        """
        try:
            self._handlers.append(handler)
            self._logger.debug(f"添加通知处理器: {handler.__class__.__name__}")
        except Exception as e:
            self._logger.error(f"添加通知处理器失败: {e}")

    def remove_handler(self, handler: NotificationHandler) -> None:
        """移除通知处理器

        Args:
            handler: 通知处理器
        """
        try:
            if handler in self._handlers:
                self._handlers.remove(handler)
                self._logger.debug(f"移除通知处理器: {handler.__class__.__name__}")
        except Exception as e:
            self._logger.error(f"移除通知处理器失败: {e}")

    def add_filter(self, filter_obj: NotificationFilter) -> None:
        """添加通知过滤器

        Args:
            filter_obj: 通知过滤器
        """
        try:
            self._filters.append(filter_obj)
            self._logger.debug(f"添加通知过滤器: {filter_obj.__class__.__name__}")
        except Exception as e:
            self._logger.error(f"添加通知过滤器失败: {e}")

    def show_notification(
        self,
        message: str,
        title: str = "",
        notification_type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        duration: int | None = None,
        source: str | None = None,
        actions: list[dict[str, Any]] | None = None,
        persistent: bool = False,
    ) -> str:
        """显示通知

        Args:
            message: 通知消息
            title: 通知标题
            notification_type: 通知类型
            priority: 通知优先级
            duration: 显示时长(毫秒)
            source: 通知来源
            actions: 通知操作按钮
            persistent: 是否持久化

        Returns:
            str: 通知ID
        """
        try:
            # 创建通知对象
            notification = Notification(
                type=notification_type,
                title=title,
                message=message,
                priority=priority,
                duration=duration,
                source=source,
                actions=actions or [],
                persistent=persistent,
            )

            # 添加到队列
            self._add_notification(notification)

            return notification.id

        except Exception as e:
            self._logger.error(f"显示通知失败: {e}")
            raise UIError(f"显示通知失败: {e}", "NotificationSystem") from e

    def show_info(self, message: str, title: str = "信息", **kwargs) -> str:
        """显示信息通知"""
        return self.show_notification(message, title, NotificationType.INFO, **kwargs)

    def show_success(self, message: str, title: str = "成功", **kwargs) -> str:
        """显示成功通知"""
        return self.show_notification(
            message, title, NotificationType.SUCCESS, **kwargs
        )

    def show_warning(self, message: str, title: str = "警告", **kwargs) -> str:
        """显示警告通知"""
        return self.show_notification(
            message, title, NotificationType.WARNING, **kwargs
        )

    def show_error(self, message: str, title: str = "错误", **kwargs) -> str:
        """显示错误通知"""
        return self.show_notification(message, title, NotificationType.ERROR, **kwargs)

    def show_progress(self, message: str, title: str = "进度", **kwargs) -> str:
        """显示进度通知"""
        kwargs.setdefault("duration", None)  # 进度通知默认不自动关闭
        return self.show_notification(
            message, title, NotificationType.PROGRESS, **kwargs
        )

    def dismiss_notification(self, notification_id: str) -> bool:
        """关闭通知

        Args:
            notification_id: 通知ID

        Returns:
            bool: 是否成功关闭
        """
        try:
            if notification_id in self._active_notifications:
                notification = self._active_notifications[notification_id]

                if notification.dismissible:
                    del self._active_notifications[notification_id]

                    # 发送关闭信号
                    self.notification_dismissed.emit(notification)

                    # 发布事件
                    self._event_bus.publish(
                        "notification.dismissed",
                        data={"id": notification_id, "notification": notification},
                        source="NotificationSystem",
                    )

                    self._logger.debug(f"通知已关闭: {notification_id}")
                    return True
                self._logger.warning(f"通知不可关闭: {notification_id}")
                return False

            return False

        except Exception as e:
            self._logger.error(f"关闭通知失败 [{notification_id}]: {e}")
            return False

    def dismiss_all_notifications(self) -> int:
        """关闭所有通知

        Returns:
            int: 关闭的通知数量
        """
        try:
            dismissed_count = 0
            notification_ids = list(self._active_notifications.keys())

            for notification_id in notification_ids:
                if self.dismiss_notification(notification_id):
                    dismissed_count += 1

            self._logger.debug(f"关闭所有通知: {dismissed_count} 个")
            return dismissed_count

        except Exception as e:
            self._logger.error(f"关闭所有通知失败: {e}")
            return 0

    def update_notification(
        self,
        notification_id: str,
        message: str | None = None,
        title: str | None = None,
        progress: float | None = None,
    ) -> bool:
        """更新通知内容

        Args:
            notification_id: 通知ID
            message: 新消息
            title: 新标题
            progress: 进度值(0-100)

        Returns:
            bool: 是否更新成功
        """
        try:
            if notification_id in self._active_notifications:
                notification = self._active_notifications[notification_id]

                if message is not None:
                    notification.message = message

                if title is not None:
                    notification.title = title

                if progress is not None:
                    notification.metadata["progress"] = progress

                # 重新处理通知
                self._process_notification(notification)

                self._logger.debug(f"通知已更新: {notification_id}")
                return True

            return False

        except Exception as e:
            self._logger.error(f"更新通知失败 [{notification_id}]: {e}")
            return False

    def _add_notification(self, notification: Notification) -> None:
        """添加通知到队列"""
        try:
            # 检查过滤器
            for filter_obj in self._filters:
                if not filter_obj.should_show(notification):
                    self._logger.debug(f"通知被过滤器拒绝: {notification.id}")
                    return

            # 添加到历史记录
            if self._enable_history and notification.persistent:
                self._notification_history.append(notification)

            # 发送添加信号
            self.notification_added.emit(notification)

            # 如果当前活跃通知数量未达到上限,直接显示
            if len(self._active_notifications) < self._max_concurrent_notifications:
                self._show_notification(notification)
            else:
                # 否则添加到队列
                self._notification_queue.append(notification)
                self._logger.debug(f"通知添加到队列: {notification.id}")

        except Exception as e:
            self._logger.error(f"添加通知失败: {e}")

    def _show_notification(self, notification: Notification) -> None:
        """显示通知"""
        try:
            # 添加到活跃通知列表
            self._active_notifications[notification.id] = notification

            # 处理通知
            self._process_notification(notification)

            # 发送显示信号
            self.notification_shown.emit(notification)

            # 发布事件
            self._event_bus.publish(
                "notification.shown",
                data={"id": notification.id, "notification": notification},
                source="NotificationSystem",
                priority=EventPriority.HIGH
                if notification.priority == NotificationPriority.URGENT
                else EventPriority.NORMAL,
            )

            self._logger.debug(f"通知已显示: {notification.id}")

        except Exception as e:
            self._logger.error(f"显示通知失败: {e}")

    def _process_notification(self, notification: Notification) -> None:
        """处理通知"""
        try:
            # 使用所有可用的处理器处理通知
            for handler in self._handlers:
                if handler.can_handle(notification):
                    try:
                        handler.handle_notification(notification)
                    except Exception as e:
                        self._logger.error(
                            f"通知处理器失败 [{handler.__class__.__name__}]: {e}"
                        )

        except Exception as e:
            self._logger.error(f"处理通知失败: {e}")

    def _cleanup_expired_notifications(self) -> None:
        """清理过期通知"""
        try:
            current_time = time.time()
            expired_notifications = []

            for notification_id, notification in self._active_notifications.items():
                if notification.duration is not None:
                    elapsed_time = (current_time - notification.timestamp) * 1000
                    if elapsed_time >= notification.duration:
                        expired_notifications.append(notification_id)

            # 移除过期通知
            for notification_id in expired_notifications:
                notification = self._active_notifications[notification_id]
                del self._active_notifications[notification_id]

                # 发送过期信号
                self.notification_expired.emit(notification)

                # 发布事件
                self._event_bus.publish(
                    "notification.expired",
                    data={"id": notification_id, "notification": notification},
                    source="NotificationSystem",
                )

            # 从队列中显示新通知
            while (
                len(self._active_notifications) < self._max_concurrent_notifications
                and self._notification_queue
            ):
                next_notification = self._notification_queue.popleft()
                self._show_notification(next_notification)

        except Exception as e:
            self._logger.error(f"清理过期通知失败: {e}")

    def _setup_default_handlers(self) -> None:
        """设置默认通知处理器"""
        try:
            # 添加日志处理器
            log_handler = LogNotificationHandler()
            self.add_handler(log_handler)

        except Exception as e:
            self._logger.error(f"设置默认处理器失败: {e}")

    def _setup_event_listeners(self) -> None:
        """设置事件监听器"""
        try:
            # 监听应用关闭事件
            self._event_bus.subscribe("app.shutdown", self._on_app_shutdown_event)

            # 监听通知请求事件
            self._event_bus.subscribe(
                "notification.request", self._on_notification_request_event
            )

        except Exception as e:
            self._logger.error(f"事件监听器设置失败: {e}")

    def _on_app_shutdown_event(self, event) -> None:
        """处理应用关闭事件"""
        try:
            # 关闭所有通知
            self.dismiss_all_notifications()

        except Exception as e:
            self._logger.error(f"应用关闭事件处理失败: {e}")

    def _on_notification_request_event(self, event) -> None:
        """处理通知请求事件"""
        try:
            data = event.data
            if isinstance(data, dict):
                message = data.get("message", "")
                title = data.get("title", "")
                notification_type = data.get("type", "info")

                # 转换类型
                type_map = {
                    "info": NotificationType.INFO,
                    "success": NotificationType.SUCCESS,
                    "warning": NotificationType.WARNING,
                    "error": NotificationType.ERROR,
                    "progress": NotificationType.PROGRESS,
                }

                notification_type_enum = type_map.get(
                    notification_type, NotificationType.INFO
                )

                self.show_notification(
                    message=message,
                    title=title,
                    notification_type=notification_type_enum,
                    source=event.source,
                )

        except Exception as e:
            self._logger.error(f"通知请求事件处理失败: {e}")

    def get_active_notifications(self) -> list[Notification]:
        """获取当前活跃的通知"""
        return list(self._active_notifications.values())

    def get_notification_history(self, limit: int = 100) -> list[Notification]:
        """获取通知历史记录

        Args:
            limit: 返回数量限制

        Returns:
            List[Notification]: 通知历史列表
        """
        if limit > 0:
            return list(self._notification_history)[-limit:]
        return list(self._notification_history)

    def clear_history(self) -> None:
        """清空通知历史"""
        self._notification_history.clear()
        self._logger.debug("通知历史已清空")

    def set_max_concurrent_notifications(self, max_count: int) -> None:
        """设置最大并发通知数量"""
        self._max_concurrent_notifications = max(1, max_count)
        self._logger.debug(f"最大并发通知数量设置为: {max_count}")

    def set_enable_history(self, enabled: bool) -> None:
        """设置是否启用历史记录"""
        self._enable_history = enabled
        self._logger.debug(f"通知历史记录: {'启用' if enabled else '禁用'}")

    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 停止定时器
            self._cleanup_timer.stop()

            # 关闭所有通知
            self.dismiss_all_notifications()

            # 清空队列和历史
            self._notification_queue.clear()
            self._notification_history.clear()

            # 清空处理器和过滤器
            self._handlers.clear()
            self._filters.clear()

            self._logger.debug("通知系统清理完成")

        except Exception as e:
            self._logger.error(f"通知系统清理失败: {e}")


# 全局通知系统实例
_global_notification_system: NotificationSystem | None = None


def get_notification_system() -> NotificationSystem:
    """获取全局通知系统实例"""
    global _global_notification_system
    if _global_notification_system is None:
        _global_notification_system = NotificationSystem()
    return _global_notification_system


def set_global_notification_system(notification_system: NotificationSystem) -> None:
    """设置全局通知系统实例"""
    global _global_notification_system
    _global_notification_system = notification_system


# 便捷函数
def show_info(message: str, title: str = "信息", **kwargs) -> str:
    """显示信息通知"""
    return get_notification_system().show_info(message, title, **kwargs)


def show_success(message: str, title: str = "成功", **kwargs) -> str:
    """显示成功通知"""
    return get_notification_system().show_success(message, title, **kwargs)


def show_warning(message: str, title: str = "警告", **kwargs) -> str:
    """显示警告通知"""
    return get_notification_system().show_warning(message, title, **kwargs)


def show_error(message: str, title: str = "错误", **kwargs) -> str:
    """显示错误通知"""
    return get_notification_system().show_error(message, title, **kwargs)


def show_progress(message: str, title: str = "进度", **kwargs) -> str:
    """显示进度通知"""
    return get_notification_system().show_progress(message, title, **kwargs)
