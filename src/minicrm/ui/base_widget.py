"""
MiniCRM 基础UI组件

定义了所有UI组件的基础类和通用功能，包括：
- 基础组件类
- 事件处理机制
- 样式管理
- 数据绑定
- 国际化支持
"""

import contextlib
from abc import abstractmethod
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import QWidget

from ..core import MiniCRMLogger, get_logger


class BaseWidget(QWidget):
    """
    基础UI组件类

    所有UI组件都应该继承自这个基础类。
    提供通用的UI功能、事件处理和样式管理。
    """

    # 信号定义
    data_changed = Signal(object)  # 数据变化信号
    error_occurred = Signal(str)  # 错误发生信号
    loading_started = Signal()  # 开始加载信号
    loading_finished = Signal()  # 加载完成信号

    def __init__(self, parent: QWidget | None = None):
        """
        初始化基础组件

        Args:
            parent: 父组件
        """
        super().__init__(parent)

        self._logger = get_logger(self.__class__.__name__)
        self._is_loading = False
        self._data = None
        self._event_handlers: dict[str, list[Callable]] = {}

        # 初始化UI
        self._setup_ui()
        self._setup_signals()
        self._apply_styles()

    @property
    def logger(self) -> MiniCRMLogger:
        """获取日志记录器"""
        return self._logger

    @property
    def is_loading(self) -> bool:
        """获取加载状态"""
        return self._is_loading

    @property
    def data(self) -> Any:
        """获取组件数据"""
        return self._data

    @data.setter
    def data(self, value: Any) -> None:
        """设置组件数据"""
        if self._data != value:
            self._data = value
            self._on_data_changed(value)
            self.data_changed.emit(value)

    @abstractmethod
    def _setup_ui(self) -> None:
        """
        设置UI布局

        子类必须实现此方法来创建具体的UI元素。
        """
        pass

    def _setup_signals(self) -> None:
        """
        设置信号连接

        子类可以重写此方法来设置特定的信号连接。
        """
        pass

    def _apply_styles(self) -> None:
        """
        应用样式

        子类可以重写此方法来应用特定的样式。
        """
        pass

    def _on_data_changed(self, data: Any) -> None:
        """
        数据变化处理

        Args:
            data: 新数据
        """
        # 子类可以重写此方法来处理数据变化
        pass

    def set_loading(self, loading: bool) -> None:
        """
        设置加载状态

        Args:
            loading: 是否正在加载
        """
        if self._is_loading != loading:
            self._is_loading = loading

            if loading:
                self.loading_started.emit()
                self._on_loading_started()
            else:
                self.loading_finished.emit()
                self._on_loading_finished()

    def _on_loading_started(self) -> None:
        """加载开始处理"""
        # 子类可以重写此方法来处理加载开始
        self.setEnabled(False)

    def _on_loading_finished(self) -> None:
        """加载完成处理"""
        # 子类可以重写此方法来处理加载完成
        self.setEnabled(True)

    def show_error(self, message: str) -> None:
        """
        显示错误信息

        Args:
            message: 错误消息
        """
        self._logger.error(f"UI错误: {message}")
        self.error_occurred.emit(message)
        self._on_error_occurred(message)

    def _on_error_occurred(self, message: str) -> None:
        """
        错误发生处理

        Args:
            message: 错误消息
        """
        # 子类可以重写此方法来处理错误显示
        pass

    def add_event_handler(self, event_name: str, handler: Callable) -> None:
        """
        添加事件处理器

        Args:
            event_name: 事件名称
            handler: 处理函数
        """
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)

    def remove_event_handler(self, event_name: str, handler: Callable) -> None:
        """
        移除事件处理器

        Args:
            event_name: 事件名称
            handler: 处理函数
        """
        if event_name in self._event_handlers:
            with contextlib.suppress(ValueError):
                self._event_handlers[event_name].remove(handler)

    def trigger_event(self, event_name: str, *args, **kwargs) -> None:
        """
        触发事件

        Args:
            event_name: 事件名称
            *args: 位置参数
            **kwargs: 关键字参数
        """
        if event_name in self._event_handlers:
            for handler in self._event_handlers[event_name]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    self._logger.error(f"事件处理器执行失败: {e}")

    def refresh(self) -> None:
        """
        刷新组件

        子类可以重写此方法来实现特定的刷新逻辑。
        """
        self._logger.debug(f"刷新组件: {self.__class__.__name__}")

    def cleanup(self) -> None:
        """
        清理资源

        子类可以重写此方法来清理特定的资源。
        """
        self._logger.debug(f"清理组件: {self.__class__.__name__}")
        self._event_handlers.clear()

    def get_component_info(self) -> dict[str, Any]:
        """
        获取组件信息

        Returns:
            Dict[str, Any]: 组件信息
        """
        return {
            "class_name": self.__class__.__name__,
            "is_loading": self._is_loading,
            "has_data": self._data is not None,
            "event_handlers": len(self._event_handlers),
            "is_visible": self.isVisible(),
            "is_enabled": self.isEnabled(),
        }


class BaseDialog(BaseWidget):
    """
    基础对话框类

    为对话框组件提供通用功能。
    """

    # 对话框结果信号
    accepted = Signal()
    rejected = Signal()

    def __init__(self, parent: QWidget | None = None):
        """
        初始化基础对话框

        Args:
            parent: 父组件
        """
        super().__init__(parent)
        self._result = None

    @property
    def result(self) -> Any:
        """获取对话框结果"""
        return self._result

    def accept(self, result: Any = None) -> None:
        """
        接受对话框

        Args:
            result: 对话框结果
        """
        self._result = result
        self.accepted.emit()
        self.close()

    def reject(self) -> None:
        """拒绝对话框"""
        self._result = None
        self.rejected.emit()
        self.close()


class BasePanel(BaseWidget):
    """
    基础面板类

    为面板组件提供通用功能。
    """

    def __init__(self, parent: QWidget | None = None):
        """
        初始化基础面板

        Args:
            parent: 父组件
        """
        super().__init__(parent)
        self._title = ""
        self._collapsible = False
        self._collapsed = False

    @property
    def title(self) -> str:
        """获取面板标题"""
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        """设置面板标题"""
        self._title = value
        self._update_title_display()

    @property
    def collapsible(self) -> bool:
        """获取是否可折叠"""
        return self._collapsible

    @collapsible.setter
    def collapsible(self, value: bool) -> None:
        """设置是否可折叠"""
        self._collapsible = value
        self._update_collapse_button()

    @property
    def collapsed(self) -> bool:
        """获取是否已折叠"""
        return self._collapsed

    def collapse(self) -> None:
        """折叠面板"""
        if self._collapsible and not self._collapsed:
            self._collapsed = True
            self._update_collapsed_state()

    def expand(self) -> None:
        """展开面板"""
        if self._collapsible and self._collapsed:
            self._collapsed = False
            self._update_collapsed_state()

    def toggle_collapse(self) -> None:
        """切换折叠状态"""
        if self._collapsed:
            self.expand()
        else:
            self.collapse()

    def _update_title_display(self) -> None:
        """更新标题显示"""
        # 子类可以重写此方法来更新标题显示
        pass

    def _update_collapse_button(self) -> None:
        """更新折叠按钮"""
        # 子类可以重写此方法来更新折叠按钮
        pass

    def _update_collapsed_state(self) -> None:
        """更新折叠状态"""
        # 子类可以重写此方法来更新折叠状态
        pass


class AsyncWorker(QObject):
    """
    异步工作器

    用于在后台线程中执行耗时操作，避免阻塞UI。
    """

    # 信号定义
    started = Signal()
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, task: Callable, *args, **kwargs):
        """
        初始化异步工作器

        Args:
            task: 要执行的任务函数
            *args: 任务参数
            **kwargs: 任务关键字参数
        """
        super().__init__()
        self._task = task
        self._args = args
        self._kwargs = kwargs
        self._logger = get_logger(self.__class__.__name__)

    def run(self) -> None:
        """执行任务"""
        try:
            self.started.emit()
            result = self._task(*self._args, **self._kwargs)
            self.finished.emit(result)
        except Exception as e:
            self._logger.error(f"异步任务执行失败: {e}")
            self.error.emit(str(e))


def run_async(widget: BaseWidget, task: Callable, *args, **kwargs) -> None:
    """
    在后台线程中运行任务

    Args:
        widget: UI组件
        task: 要执行的任务
        *args: 任务参数
        **kwargs: 任务关键字参数
    """

    def on_started():
        widget.set_loading(True)

    def on_finished(result):
        widget.set_loading(False)
        if hasattr(widget, "_on_async_finished"):
            widget._on_async_finished(result)

    def on_error(error_msg):
        widget.set_loading(False)
        widget.show_error(f"操作失败: {error_msg}")

    worker = AsyncWorker(task, *args, **kwargs)
    worker.started.connect(on_started)
    worker.finished.connect(on_finished)
    worker.error.connect(on_error)

    # 使用定时器在主线程中执行
    QTimer.singleShot(0, worker.run)
