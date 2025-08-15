"""
MiniCRM 通知组件

实现各种通知组件，提供：
- 消息通知
- 成功/警告/错误提示
- 自动消失通知
- 操作按钮通知
- 通知队列管理
"""

import logging
from enum import Enum

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class NotificationType(Enum):
    """通知类型枚举"""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationWidget(QFrame):
    """
    单个通知组件

    显示一个通知消息，支持自动消失和用户交互。

    Signals:
        closed: 通知关闭信号
        action_clicked: 操作按钮点击信号 (action_name: str)
    """

    # Qt信号定义
    closed = Signal()
    action_clicked = Signal(str)

    def __init__(
        self,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        title: str = "",
        auto_close: bool = True,
        duration: int = 5000,
        show_close_button: bool = True,
        actions: list[dict] = None,
        parent: QWidget | None = None,
    ):
        """
        初始化通知组件

        Args:
            message: 通知消息
            notification_type: 通知类型
            title: 通知标题
            auto_close: 是否自动关闭
            duration: 自动关闭时间（毫秒）
            show_close_button: 是否显示关闭按钮
            actions: 操作按钮列表 [{'name': 'action1', 'text': '按钮文本'}]
            parent: 父组件
        """
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)

        # 通知配置
        self._message = message
        self._notification_type = notification_type
        self._title = title
        self._auto_close = auto_close
        self._duration = duration
        self._show_close_button = show_close_button
        self._actions = actions or []

        # UI组件
        self._icon_label: QLabel | None = None
        self._title_label: QLabel | None = None
        self._message_label: QLabel | None = None
        self._close_button: QPushButton | None = None
        self._action_buttons: list[QPushButton] = []

        # 动画和定时器
        self._opacity_effect: QGraphicsOpacityEffect | None = None
        self._fade_animation: QPropertyAnimation | None = None
        self._auto_close_timer: QTimer | None = None

        # 设置组件
        self._setup_ui()
        self._setup_animations()
        self._setup_auto_close()

        self._logger.debug(f"通知组件初始化完成: {notification_type.value}")

    def _setup_ui(self) -> None:
        """设置用户界面"""
        try:
            # 设置框架样式
            self.setFrameStyle(QFrame.Shape.Box)
            self.setObjectName(f"notification_{self._notification_type.value}")

            # 主布局
            main_layout = QHBoxLayout(self)
            main_layout.setContentsMargins(15, 10, 15, 10)
            main_layout.setSpacing(10)

            # 图标
            self._create_icon(main_layout)

            # 内容区域
            content_layout = QVBoxLayout()
            content_layout.setSpacing(5)

            # 标题
            if self._title:
                self._title_label = QLabel(self._title)
                self._title_label.setObjectName("notificationTitle")

                title_font = QFont()
                title_font.setBold(True)
                title_font.setPointSize(11)
                self._title_label.setFont(title_font)

                content_layout.addWidget(self._title_label)

            # 消息
            self._message_label = QLabel(self._message)
            self._message_label.setObjectName("notificationMessage")
            self._message_label.setWordWrap(True)

            message_font = QFont()
            message_font.setPointSize(10)
            self._message_label.setFont(message_font)

            content_layout.addWidget(self._message_label)

            # 操作按钮
            if self._actions:
                self._create_action_buttons(content_layout)

            main_layout.addLayout(content_layout, 1)

            # 关闭按钮
            if self._show_close_button:
                self._create_close_button(main_layout)

            # 应用样式
            self._apply_styles()

        except Exception as e:
            self._logger.error(f"通知组件UI设置失败: {e}")
            raise

    def _create_icon(self, layout: QHBoxLayout) -> None:
        """创建图标"""
        self._icon_label = QLabel()
        self._icon_label.setObjectName("notificationIcon")
        self._icon_label.setFixedSize(24, 24)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 根据类型设置图标
        icon_text = {
            NotificationType.INFO: "ℹ️",
            NotificationType.SUCCESS: "✅",
            NotificationType.WARNING: "⚠️",
            NotificationType.ERROR: "❌",
        }.get(self._notification_type, "ℹ️")

        self._icon_label.setText(icon_text)

        icon_font = QFont()
        icon_font.setPointSize(16)
        self._icon_label.setFont(icon_font)

        layout.addWidget(self._icon_label)

    def _create_action_buttons(self, layout: QVBoxLayout) -> None:
        """创建操作按钮"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        for action in self._actions:
            button = QPushButton(action["text"])
            button.setObjectName("notificationActionButton")
            button.clicked.connect(
                lambda checked, name=action["name"]: self._on_action_clicked(name)
            )

            self._action_buttons.append(button)
            button_layout.addWidget(button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _create_close_button(self, layout: QHBoxLayout) -> None:
        """创建关闭按钮"""
        self._close_button = QPushButton("✖️")
        self._close_button.setObjectName("notificationCloseButton")
        self._close_button.setFixedSize(24, 24)
        self._close_button.clicked.connect(self.close_notification)

        layout.addWidget(self._close_button)

    def _apply_styles(self) -> None:
        """应用样式"""
        # 基础样式
        base_style = """
            QFrame {
                border-radius: 6px;
                border: 1px solid;
                background-color: white;
            }

            QLabel#notificationTitle {
                color: #212529;
                background-color: transparent;
            }

            QLabel#notificationMessage {
                color: #495057;
                background-color: transparent;
            }

            QLabel#notificationIcon {
                background-color: transparent;
            }

            QPushButton#notificationCloseButton {
                border: none;
                background-color: transparent;
                color: #6c757d;
                font-size: 12px;
                border-radius: 12px;
            }

            QPushButton#notificationCloseButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }

            QPushButton#notificationActionButton {
                border: 1px solid #ced4da;
                background-color: white;
                color: #495057;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 10px;
            }

            QPushButton#notificationActionButton:hover {
                background-color: #e9ecef;
            }
        """

        # 根据类型设置颜色
        type_styles = {
            NotificationType.INFO: """
                QFrame#notification_info {
                    border-color: #b8daff;
                    background-color: #d1ecf1;
                }
            """,
            NotificationType.SUCCESS: """
                QFrame#notification_success {
                    border-color: #c3e6cb;
                    background-color: #d4edda;
                }
            """,
            NotificationType.WARNING: """
                QFrame#notification_warning {
                    border-color: #ffeaa7;
                    background-color: #fff3cd;
                }
            """,
            NotificationType.ERROR: """
                QFrame#notification_error {
                    border-color: #f5c6cb;
                    background-color: #f8d7da;
                }
            """,
        }

        style = base_style + type_styles.get(self._notification_type, "")
        self.setStyleSheet(style)

    def _setup_animations(self) -> None:
        """设置动画"""
        try:
            # 透明度效果
            self._opacity_effect = QGraphicsOpacityEffect()
            self.setGraphicsEffect(self._opacity_effect)

            # 淡入淡出动画
            self._fade_animation = QPropertyAnimation(self._opacity_effect, b"opacity")
            self._fade_animation.setDuration(300)
            self._fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

            # 淡入
            self.fade_in()

        except Exception as e:
            self._logger.error(f"设置动画失败: {e}")

    def _setup_auto_close(self) -> None:
        """设置自动关闭"""
        if self._auto_close and self._duration > 0:
            self._auto_close_timer = QTimer()
            self._auto_close_timer.setSingleShot(True)
            self._auto_close_timer.timeout.connect(self.close_notification)
            self._auto_close_timer.start(self._duration)

    def fade_in(self) -> None:
        """淡入动画"""
        if self._fade_animation:
            self._fade_animation.setStartValue(0.0)
            self._fade_animation.setEndValue(1.0)
            self._fade_animation.start()

    def fade_out(self) -> None:
        """淡出动画"""
        if self._fade_animation:
            self._fade_animation.finished.connect(self._on_fade_out_finished)
            self._fade_animation.setStartValue(1.0)
            self._fade_animation.setEndValue(0.0)
            self._fade_animation.start()

    def _on_fade_out_finished(self) -> None:
        """淡出完成处理"""
        self.closed.emit()
        self.deleteLater()

    def _on_action_clicked(self, action_name: str) -> None:
        """处理操作按钮点击"""
        self.action_clicked.emit(action_name)

    def close_notification(self) -> None:
        """关闭通知"""
        try:
            # 停止自动关闭定时器
            if self._auto_close_timer:
                self._auto_close_timer.stop()

            # 开始淡出动画
            self.fade_out()

        except Exception as e:
            self._logger.error(f"关闭通知失败: {e}")

    def pause_auto_close(self) -> None:
        """暂停自动关闭"""
        if self._auto_close_timer and self._auto_close_timer.isActive():
            self._auto_close_timer.stop()

    def resume_auto_close(self) -> None:
        """恢复自动关闭"""
        if self._auto_close and self._auto_close_timer:
            remaining_time = max(1000, self._duration // 2)  # 至少1秒
            self._auto_close_timer.start(remaining_time)

    def enterEvent(self, event) -> None:  # noqa: N802
        """鼠标进入事件"""
        self.pause_auto_close()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        """鼠标离开事件"""
        self.resume_auto_close()
        super().leaveEvent(event)


class NotificationManager(QWidget):
    """
    通知管理器

    管理多个通知的显示、队列和位置。
    """

    def __init__(self, parent: QWidget | None = None):
        """
        初始化通知管理器

        Args:
            parent: 父组件
        """
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)

        # 通知列表
        self._notifications: list[NotificationWidget] = []
        self._max_notifications = 5

        # 设置组件
        self._setup_ui()

        self._logger.debug("通知管理器初始化完成")

    def _setup_ui(self) -> None:
        """设置用户界面"""
        try:
            # 设置为顶层窗口
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.Tool
            )
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

            # 主布局
            self._layout = QVBoxLayout(self)
            self._layout.setContentsMargins(10, 10, 10, 10)
            self._layout.setSpacing(10)
            self._layout.addStretch()

            # 初始隐藏
            self.hide()

        except Exception as e:
            self._logger.error(f"通知管理器UI设置失败: {e}")
            raise

    def show_notification(
        self,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        title: str = "",
        auto_close: bool = True,
        duration: int = 5000,
        actions: list[dict] = None,
    ) -> NotificationWidget:
        """
        显示通知

        Args:
            message: 通知消息
            notification_type: 通知类型
            title: 通知标题
            auto_close: 是否自动关闭
            duration: 自动关闭时间
            actions: 操作按钮列表

        Returns:
            NotificationWidget: 通知组件实例
        """
        try:
            # 如果通知过多，移除最旧的
            while len(self._notifications) >= self._max_notifications:
                oldest = self._notifications[0]
                self._remove_notification(oldest)

            # 创建新通知
            notification = NotificationWidget(
                message=message,
                notification_type=notification_type,
                title=title,
                auto_close=auto_close,
                duration=duration,
                actions=actions,
                parent=self,
            )

            # 连接信号
            notification.closed.connect(lambda: self._remove_notification(notification))

            # 添加到布局
            self._layout.insertWidget(self._layout.count() - 1, notification)
            self._notifications.append(notification)

            # 更新位置和显示
            self._update_position()
            self.show()

            self._logger.debug(f"显示通知: {notification_type.value} - {message}")

            return notification

        except Exception as e:
            self._logger.error(f"显示通知失败: {e}")
            return None

    def _remove_notification(self, notification: NotificationWidget) -> None:
        """移除通知"""
        try:
            if notification in self._notifications:
                self._notifications.remove(notification)
                notification.deleteLater()

            # 如果没有通知了，隐藏管理器
            if not self._notifications:
                self.hide()
            else:
                self._update_position()

        except Exception as e:
            self._logger.error(f"移除通知失败: {e}")

    def _update_position(self) -> None:
        """更新位置"""
        try:
            if not self.parent():
                return

            # 获取父组件的几何信息
            parent = self.parent()
            parent_rect = parent.rect() if hasattr(parent, "rect") else self.rect()

            # 计算所需大小
            self.adjustSize()

            # 定位到右上角
            x = parent_rect.right() - self.width() - 20
            y = parent_rect.top() + 20

            self.move(x, y)

        except Exception as e:
            self._logger.error(f"更新位置失败: {e}")

    def clear_all(self) -> None:
        """清除所有通知"""
        try:
            for notification in self._notifications[:]:
                notification.close_notification()

        except Exception as e:
            self._logger.error(f"清除所有通知失败: {e}")

    def set_max_notifications(self, max_count: int) -> None:
        """
        设置最大通知数量

        Args:
            max_count: 最大通知数量
        """
        self._max_notifications = max(1, max_count)


# 全局通知管理器实例
_global_notification_manager: NotificationManager | None = None


def get_notification_manager(parent: QWidget = None) -> NotificationManager:
    """
    获取全局通知管理器实例

    Args:
        parent: 父组件

    Returns:
        NotificationManager: 通知管理器实例
    """
    global _global_notification_manager

    if _global_notification_manager is None:
        _global_notification_manager = NotificationManager(parent)

    return _global_notification_manager


# 便捷函数
def show_info(
    message: str, title: str = "", parent: QWidget = None
) -> NotificationWidget:
    """显示信息通知"""
    manager = get_notification_manager(parent)
    return manager.show_notification(message, NotificationType.INFO, title)


def show_success(
    message: str, title: str = "", parent: QWidget = None
) -> NotificationWidget:
    """显示成功通知"""
    manager = get_notification_manager(parent)
    return manager.show_notification(message, NotificationType.SUCCESS, title)


def show_warning(
    message: str, title: str = "", parent: QWidget = None
) -> NotificationWidget:
    """显示警告通知"""
    manager = get_notification_manager(parent)
    return manager.show_notification(message, NotificationType.WARNING, title)


def show_error(
    message: str, title: str = "", parent: QWidget = None
) -> NotificationWidget:
    """显示错误通知"""
    manager = get_notification_manager(parent)
    return manager.show_notification(
        message, NotificationType.ERROR, title, auto_close=False
    )


def show_action_notification(
    message: str,
    actions: list[dict],
    notification_type: NotificationType = NotificationType.INFO,
    title: str = "",
    parent: QWidget = None,
) -> NotificationWidget:
    """显示带操作按钮的通知"""
    manager = get_notification_manager(parent)
    return manager.show_notification(
        message=message,
        notification_type=notification_type,
        title=title,
        actions=actions,
        auto_close=False,
    )
