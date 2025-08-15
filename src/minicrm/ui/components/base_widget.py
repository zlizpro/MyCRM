"""
MiniCRM 基础组件类

提供所有UI组件的基础功能，包括：
- 统一的初始化流程
- 日志记录和错误处理
- 配置管理接口
- 资源清理机制
- 样式管理支持
- 信号连接管理
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QMessageBox, QWidget

from minicrm.core.exceptions import UIError


class BaseWidget(QWidget, ABC):
    """
    基础组件类

    所有自定义UI组件的基类，提供：
    - 统一的初始化和清理流程
    - 日志记录功能
    - 配置管理接口
    - 错误处理机制
    - 样式管理支持
    - 生命周期管理

    Signals:
        initialized: 组件初始化完成信号
        error_occurred: 错误发生信号 (error_message: str)
        cleanup_completed: 清理完成信号
    """

    # Qt信号定义
    initialized = Signal()
    error_occurred = Signal(str)
    cleanup_completed = Signal()

    def __init__(self, parent: QWidget | None = None):
        """
        初始化基础组件

        Args:
            parent: 父组件
        """
        super().__init__(parent)

        # 组件标识
        self._component_name = self.__class__.__name__
        self._is_initialized = False
        self._is_cleaning_up = False

        # 日志记录器
        self._logger = logging.getLogger(f"{__name__}.{self._component_name}")

        # 配置和应用程序引用
        self._app_instance: QObject | None = None
        self._config: dict | None = None

        # 资源管理
        self._timers: list[QTimer] = []
        self._connections: list[QObject] = []

        try:
            # 执行初始化流程
            self._initialize_component()

        except Exception as e:
            self._handle_error(f"组件初始化失败: {e}", e)

    def _initialize_component(self) -> None:
        """执行组件初始化流程"""
        try:
            self._logger.debug(f"开始初始化组件: {self._component_name}")

            # 1. 设置基础属性
            self._setup_base_properties()

            # 2. 设置用户界面
            self.setup_ui()

            # 3. 设置信号连接
            self.setup_connections()

            # 4. 应用样式
            self.apply_styles()

            # 5. 执行后初始化处理
            self.post_init()

            # 标记为已初始化
            self._is_initialized = True

            # 发送初始化完成信号
            self.initialized.emit()

            self._logger.debug(f"组件初始化完成: {self._component_name}")

        except Exception as e:
            self._logger.error(f"组件初始化失败: {e}")
            raise UIError(f"组件初始化失败: {e}", self._component_name) from e

    def _setup_base_properties(self) -> None:
        """设置基础属性"""
        # 设置对象名称（用于样式表选择器）
        self.setObjectName(self._component_name)

        # 设置工具提示
        if hasattr(self, "_tooltip"):
            self.setToolTip(self._tooltip)

    @abstractmethod
    def setup_ui(self) -> None:
        """
        设置用户界面

        子类必须实现此方法来创建UI布局和组件。
        """
        pass

    def setup_connections(self) -> None:
        """
        设置信号连接

        子类可以重写此方法来设置信号和槽的连接。
        默认实现为空，子类根据需要进行连接。
        """
        pass

    def apply_styles(self) -> None:
        """
        应用样式

        子类可以重写此方法来应用自定义样式。
        默认实现为空，子类根据需要设置样式。
        """
        pass

    def post_init(self) -> None:
        """
        后初始化处理

        在UI设置、信号连接和样式应用完成后调用。
        子类可以重写此方法进行额外的初始化工作。
        """
        pass

    def set_app_instance(self, app_instance: QObject) -> None:
        """
        设置应用程序实例引用

        Args:
            app_instance: 应用程序实例
        """
        self._app_instance = app_instance
        self._logger.debug("应用程序实例引用已设置")

    def get_app_instance(self) -> QObject | None:
        """获取应用程序实例引用"""
        return self._app_instance

    def set_config(self, config: dict) -> None:
        """
        设置配置字典

        Args:
            config: 配置字典
        """
        self._config = config
        self._logger.debug("配置已设置")

    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键
            default: 默认值

        Returns:
            配置值或默认值
        """
        if self._config:
            return self._config.get(key, default)
        return default

    def add_timer(self, timer: QTimer) -> None:
        """
        添加定时器到管理列表

        Args:
            timer: 定时器对象
        """
        self._timers.append(timer)

    def add_connection(self, obj: QObject) -> None:
        """
        添加连接对象到管理列表

        Args:
            obj: 连接的对象
        """
        self._connections.append(obj)

    def show_info(self, title: str, message: str) -> None:
        """
        显示信息对话框

        Args:
            title: 对话框标题
            message: 信息内容
        """
        QMessageBox.information(self, title, message)

    def show_warning(self, title: str, message: str) -> None:
        """
        显示警告对话框

        Args:
            title: 对话框标题
            message: 警告内容
        """
        QMessageBox.warning(self, title, message)

    def show_error(self, title: str, message: str) -> None:
        """
        显示错误对话框

        Args:
            title: 对话框标题
            message: 错误内容
        """
        QMessageBox.critical(self, title, message)

    def ask_confirmation(self, title: str, message: str) -> bool:
        """
        显示确认对话框

        Args:
            title: 对话框标题
            message: 确认内容

        Returns:
            bool: 用户是否确认
        """
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def _handle_error(self, message: str, exception: Exception) -> None:
        """
        处理错误

        Args:
            message: 错误消息
            exception: 异常对象
        """
        self._logger.error(f"{message}: {exception}")
        self.error_occurred.emit(message)

    def cleanup(self) -> None:
        """
        清理资源

        清理组件使用的所有资源，包括定时器、连接等。
        子类可以重写此方法进行额外的清理工作。
        """
        if self._is_cleaning_up:
            return

        self._is_cleaning_up = True

        try:
            self._logger.debug(f"开始清理组件资源: {self._component_name}")

            # 停止所有定时器
            for timer in self._timers:
                if timer.isActive():
                    timer.stop()

            # 清理连接
            self._connections.clear()

            # 子类清理
            self.cleanup_resources()

            # 发送清理完成信号
            self.cleanup_completed.emit()

            self._logger.debug(f"组件资源清理完成: {self._component_name}")

        except Exception as e:
            self._logger.error(f"资源清理失败: {e}")

    def cleanup_resources(self) -> None:
        """
        清理子类资源

        子类可以重写此方法进行特定的资源清理。
        """
        pass

    @property
    def is_initialized(self) -> bool:
        """检查组件是否已初始化"""
        return self._is_initialized

    @property
    def component_name(self) -> str:
        """获取组件名称"""
        return self._component_name

    def closeEvent(self, event) -> None:  # noqa: N802
        """窗口关闭事件"""
        self.cleanup()
        super().closeEvent(event)

    def __str__(self) -> str:
        """返回组件的字符串表示"""
        return f"{self._component_name}(initialized={self._is_initialized})"
