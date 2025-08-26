"""TTK进度对话框

提供进度显示和取消功能,包括:
- 确定进度和不确定进度模式
- 进度文本显示和更新
- 取消操作支持
- 异步进度更新
- 线程安全的进度更新机制

设计目标:
1. 提供用户友好的进度显示界面
2. 支持长时间运行的操作
3. 允许用户取消正在进行的操作
4. 确保线程安全的进度更新

作者: MiniCRM开发团队
"""

import logging
import threading
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Optional, Union

from .base_dialog import BaseDialogTTK, DialogResult


class ProgressDialogTTK(BaseDialogTTK):
    """TTK进度对话框

    显示操作进度,支持确定和不确定进度模式,
    提供取消功能和异步进度更新.
    """

    def __init__(
        self,
        parent: Optional[tk.Widget] = None,
        title: str = "操作进行中",
        message: str = "请稍候...",
        determinate: bool = True,
        cancelable: bool = True,
        auto_close: bool = True,
        **kwargs,
    ):
        """初始化进度对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            message: 进度消息
            determinate: 是否为确定进度模式
            cancelable: 是否可取消
            auto_close: 是否自动关闭
            **kwargs: 其他参数
        """
        # 进度对话框特定属性
        self.message = message
        self.determinate = determinate
        self.cancelable = cancelable
        self.auto_close = auto_close

        # 进度状态
        self.progress_value = 0
        self.progress_max = 100
        self.is_cancelled = False
        self.is_completed = False

        # 进度组件
        self.message_label: Optional[ttk.Label] = None
        self.progress_bar: Optional[ttk.Progressbar] = None
        self.detail_label: Optional[ttk.Label] = None

        # 进度变量
        self.progress_var = tk.DoubleVar()
        self.message_var = tk.StringVar(value=message)
        self.detail_var = tk.StringVar()

        # 线程安全更新
        self._update_lock = threading.Lock()
        self._pending_updates = []

        # 取消回调
        self.cancel_callback: Optional[Callable] = None

        # 设置对话框大小
        kwargs.setdefault("size", (400, 150))
        kwargs.setdefault("resizable", (False, False))

        super().__init__(parent, title, **kwargs)

        # 启动进度更新检查
        self._start_update_checker()

    def _setup_content(self) -> None:
        """设置对话框内容"""
        # 创建消息标签
        self.message_label = ttk.Label(
            self.content_frame,
            textvariable=self.message_var,
            font=("Microsoft YaHei UI", 9),
        )
        self.message_label.pack(pady=(0, 10))

        # 创建进度条
        mode = "determinate" if self.determinate else "indeterminate"
        self.progress_bar = ttk.Progressbar(
            self.content_frame, mode=mode, variable=self.progress_var, length=350
        )
        self.progress_bar.pack(pady=(0, 10), padx=20, fill=tk.X)

        # 设置进度条范围
        if self.determinate:
            self.progress_bar.configure(maximum=self.progress_max)
        else:
            # 启动不确定进度动画
            self.progress_bar.start(10)

        # 创建详细信息标签
        self.detail_label = ttk.Label(
            self.content_frame,
            textvariable=self.detail_var,
            font=("Microsoft YaHei UI", 8),
            foreground="gray",
        )
        self.detail_label.pack()

    def _setup_buttons(self) -> None:
        """设置对话框按钮"""
        if self.cancelable:
            self.add_button("取消", self._on_cancel_progress, DialogResult.CANCEL)

    def _on_cancel_progress(self) -> None:
        """取消进度处理"""
        if self.is_completed:
            self._close_dialog()
            return

        # 确认取消
        if self.confirm("确定要取消当前操作吗?", "确认取消"):
            self.is_cancelled = True

            # 调用取消回调
            if self.cancel_callback:
                try:
                    self.cancel_callback()
                except Exception as e:
                    self.logger.error(f"取消回调执行失败: {e}")

            # 更新界面
            self.set_message("正在取消...")
            self.set_button_enabled("取消", False)

            # 触发取消事件
            self.trigger_event("cancelled")

    def _start_update_checker(self) -> None:
        """启动更新检查器"""

        def check_updates():
            try:
                with self._update_lock:
                    if self._pending_updates:
                        # 处理所有待更新的内容
                        for update_func in self._pending_updates:
                            update_func()
                        self._pending_updates.clear()

                # 检查是否完成
                if self.is_completed and self.auto_close:
                    self.after(1000, self._close_dialog)  # 1秒后自动关闭
                elif not self.is_completed and not self.is_cancelled:
                    # 继续检查更新
                    self.after(100, check_updates)

            except Exception as e:
                self.logger.error(f"更新检查失败: {e}")

        # 启动检查
        self.after(100, check_updates)

    def set_progress(
        self, value: float, maximum: Optional[Union[int, float]] = None
    ) -> None:
        """设置进度值

        Args:
            value: 进度值
            maximum: 最大值(可选)
        """
        if not self.determinate:
            self.logger.warning("不确定进度模式下无法设置进度值")
            return

        def update():
            if maximum is not None:
                self.progress_max = maximum
                self.progress_bar.configure(maximum=maximum)

            self.progress_value = value
            self.progress_var.set(value)

        # 线程安全更新
        with self._update_lock:
            self._pending_updates.append(update)

    def set_progress_percentage(self, percentage: float) -> None:
        """设置进度百分比

        Args:
            percentage: 进度百分比 (0-100)
        """
        if not self.determinate:
            self.logger.warning("不确定进度模式下无法设置进度百分比")
            return

        value = max(0, min(100, percentage))
        self.set_progress(value, 100)

    def set_message(self, message: str) -> None:
        """设置进度消息

        Args:
            message: 进度消息
        """

        def update():
            self.message_var.set(message)

        # 线程安全更新
        with self._update_lock:
            self._pending_updates.append(update)

    def set_detail(self, detail: str) -> None:
        """设置详细信息

        Args:
            detail: 详细信息
        """

        def update():
            self.detail_var.set(detail)

        # 线程安全更新
        with self._update_lock:
            self._pending_updates.append(update)

    def increment_progress(self, increment: float = 1) -> None:
        """增加进度值

        Args:
            increment: 增加量
        """
        if not self.determinate:
            self.logger.warning("不确定进度模式下无法增加进度值")
            return

        new_value = min(self.progress_value + increment, self.progress_max)
        self.set_progress(new_value)

    def complete_progress(self, message: str = "操作完成") -> None:
        """完成进度

        Args:
            message: 完成消息
        """
        self.is_completed = True

        def update():
            if self.determinate:
                self.progress_var.set(self.progress_max)
            else:
                # 停止不确定进度动画
                self.progress_bar.stop()
                self.progress_bar.configure(mode="determinate", maximum=100)
                self.progress_var.set(100)

            self.message_var.set(message)

            # 更新按钮
            if self.cancelable:
                self.set_button_text("取消", "关闭")

        # 线程安全更新
        with self._update_lock:
            self._pending_updates.append(update)

        # 触发完成事件
        self.trigger_event("completed")

    def set_cancel_callback(self, callback: Callable) -> None:
        """设置取消回调函数

        Args:
            callback: 取消时调用的函数
        """
        self.cancel_callback = callback

    def is_progress_cancelled(self) -> bool:
        """检查进度是否被取消

        Returns:
            是否被取消
        """
        return self.is_cancelled

    def is_progress_completed(self) -> bool:
        """检查进度是否完成

        Returns:
            是否完成
        """
        return self.is_completed

    def get_progress_value(self) -> Union[int, float]:
        """获取当前进度值

        Returns:
            当前进度值
        """
        return self.progress_value

    def get_progress_percentage(self) -> float:
        """获取当前进度百分比

        Returns:
            当前进度百分比 (0-100)
        """
        if self.progress_max == 0:
            return 0
        return (self.progress_value / self.progress_max) * 100

    def reset_progress(self) -> None:
        """重置进度"""
        self.progress_value = 0
        self.is_cancelled = False
        self.is_completed = False

        def update():
            self.progress_var.set(0)
            if not self.determinate:
                self.progress_bar.start(10)

            # 重置按钮
            if self.cancelable:
                self.set_button_text("关闭", "取消")
                self.set_button_enabled("取消", True)

        # 线程安全更新
        with self._update_lock:
            self._pending_updates.append(update)

        # 重新启动更新检查
        self._start_update_checker()

    def _validate_input(self) -> bool:
        """验证输入(进度对话框不需要验证)"""
        return True

    def _get_result_data(self) -> Any:
        """获取结果数据"""
        return {
            "cancelled": self.is_cancelled,
            "completed": self.is_completed,
            "progress_value": self.progress_value,
            "progress_percentage": self.get_progress_percentage(),
        }

    def _cleanup(self) -> None:
        """清理资源"""
        try:
            # 停止不确定进度动画
            if self.progress_bar and not self.determinate:
                self.progress_bar.stop()

            # 清理更新队列
            with self._update_lock:
                self._pending_updates.clear()

            super()._cleanup()

        except Exception as e:
            self.logger.error(f"进度对话框清理失败: {e}")


class ProgressTask:
    """进度任务类

    用于封装需要显示进度的任务,提供进度更新接口.
    """

    def __init__(
        self, task_func: Callable, progress_dialog: ProgressDialogTTK, *args, **kwargs
    ):
        """初始化进度任务

        Args:
            task_func: 任务函数
            progress_dialog: 进度对话框
            *args: 任务函数参数
            **kwargs: 任务函数关键字参数
        """
        self.task_func = task_func
        self.progress_dialog = progress_dialog
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self.exception = None
        self.thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """启动任务"""
        self.thread = threading.Thread(target=self._run_task)
        self.thread.daemon = True
        self.thread.start()

    def _run_task(self) -> None:
        """运行任务"""
        try:
            # 创建进度更新器
            progress_updater = ProgressUpdater(self.progress_dialog)

            # 执行任务
            self.result = self.task_func(progress_updater, *self.args, **self.kwargs)

            # 完成进度
            if not self.progress_dialog.is_cancelled:
                self.progress_dialog.complete_progress("操作完成")

        except Exception as e:
            self.exception = e
            self.progress_dialog.set_message(f"操作失败: {e}")
            self.progress_dialog.complete_progress("操作失败")

    def wait(self) -> Any:
        """等待任务完成

        Returns:
            任务结果
        """
        if self.thread:
            self.thread.join()

        if self.exception:
            raise self.exception

        return self.result


class ProgressUpdater:
    """进度更新器

    提供给任务函数使用的进度更新接口.
    """

    def __init__(self, progress_dialog: ProgressDialogTTK):
        """初始化进度更新器

        Args:
            progress_dialog: 进度对话框
        """
        self.progress_dialog = progress_dialog

    def update_progress(
        self, value: float, maximum: Optional[Union[int, float]] = None
    ) -> None:
        """更新进度

        Args:
            value: 进度值
            maximum: 最大值
        """
        self.progress_dialog.set_progress(value, maximum)

    def update_percentage(self, percentage: float) -> None:
        """更新进度百分比

        Args:
            percentage: 进度百分比
        """
        self.progress_dialog.set_progress_percentage(percentage)

    def update_message(self, message: str) -> None:
        """更新进度消息

        Args:
            message: 进度消息
        """
        self.progress_dialog.set_message(message)

    def update_detail(self, detail: str) -> None:
        """更新详细信息

        Args:
            detail: 详细信息
        """
        self.progress_dialog.set_detail(detail)

    def increment(self, increment: float = 1) -> None:
        """增加进度

        Args:
            increment: 增加量
        """
        self.progress_dialog.increment_progress(increment)

    def is_cancelled(self) -> bool:
        """检查是否被取消

        Returns:
            是否被取消
        """
        return self.progress_dialog.is_cancelled

    def check_cancelled(self) -> None:
        """检查取消状态,如果被取消则抛出异常"""
        if self.is_cancelled():
            raise InterruptedError("操作被用户取消")


# 便利函数
def show_progress_dialog(
    parent: Optional[tk.Widget],
    task_func: Callable,
    title: str = "操作进行中",
    message: str = "请稍候...",
    determinate: bool = True,
    cancelable: bool = True,
    *args,
    **kwargs,
) -> Any:
    """显示进度对话框并执行任务

    Args:
        parent: 父窗口
        task_func: 任务函数(第一个参数必须是ProgressUpdater)
        title: 对话框标题
        message: 进度消息
        determinate: 是否为确定进度模式
        cancelable: 是否可取消
        *args: 任务函数参数
        **kwargs: 任务函数关键字参数

    Returns:
        任务执行结果
    """
    # 创建进度对话框
    dialog = ProgressDialogTTK(
        parent=parent,
        title=title,
        message=message,
        determinate=determinate,
        cancelable=cancelable,
    )

    # 创建并启动任务
    task = ProgressTask(task_func, dialog, *args, **kwargs)
    task.start()

    # 显示对话框
    dialog.show_dialog()

    # 等待任务完成
    try:
        return task.wait()
    except Exception as e:
        logging.getLogger(__name__).error(f"任务执行失败: {e}")
        raise
