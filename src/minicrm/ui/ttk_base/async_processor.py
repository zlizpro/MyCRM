"""MiniCRM TTK异步处理器

提供TTK界面的异步数据加载和处理功能,包括:
- 异步任务管理
- UI响应优化
- 进度指示
- 后台任务取消
- 错误处理
- 任务队列管理
"""

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from queue import Empty, Queue
import threading
import time
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional


class TaskStatus(Enum):
    """任务状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级枚举"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AsyncTask:
    """异步任务定义"""

    task_id: str
    name: str
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: Optional[float] = None
    callback: Optional[Callable] = None
    error_callback: Optional[Callable] = None
    progress_callback: Optional[Callable] = None

    # 运行时状态
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[Exception] = None
    progress: float = 0.0

    # 内部使用
    future: Optional[Future] = None
    cancel_event: Optional[threading.Event] = None


@dataclass
class ProgressInfo:
    """进度信息"""

    current: int = 0
    total: int = 100
    message: str = ""
    percentage: float = 0.0
    elapsed_time: float = 0.0
    estimated_remaining: float = 0.0


class AsyncProcessor:
    """TTK异步处理器

    管理异步任务的执行、进度跟踪和UI更新.
    """

    def __init__(self, max_workers: int = 4):
        """初始化异步处理器

        Args:
            max_workers: 最大工作线程数
        """
        self._logger = logging.getLogger(__name__)

        # 线程池
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._max_workers = max_workers

        # 任务管理
        self._tasks: Dict[str, AsyncTask] = {}
        self._task_queue = Queue()
        self._running_tasks: Dict[str, AsyncTask] = {}

        # UI更新队列
        self._ui_update_queue = Queue()
        self._ui_update_interval = 100  # 毫秒

        # 状态管理
        self._is_running = True
        self._task_counter = 0

        # 统计信息
        self._total_tasks = 0
        self._completed_tasks = 0
        self._failed_tasks = 0
        self._cancelled_tasks = 0

        # 启动UI更新循环
        self._start_ui_update_loop()

        self._logger.debug(f"异步处理器初始化完成,最大工作线程: {max_workers}")

    def submit_task(
        self,
        func: Callable,
        *args,
        name: Optional[str] = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[float] = None,
        callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None,
        **kwargs,
    ) -> str:
        """提交异步任务

        Args:
            func: 要执行的函数
            *args: 函数参数
            name: 任务名称
            priority: 任务优先级
            timeout: 超时时间(秒)
            callback: 完成回调函数
            error_callback: 错误回调函数
            progress_callback: 进度回调函数
            **kwargs: 函数关键字参数

        Returns:
            str: 任务ID
        """
        try:
            # 生成任务ID
            self._task_counter += 1
            task_id = f"task_{self._task_counter}_{int(time.time())}"

            # 创建取消事件
            cancel_event = threading.Event()

            # 创建任务
            task = AsyncTask(
                task_id=task_id,
                name=name or f"Task {self._task_counter}",
                func=func,
                args=args,
                kwargs=kwargs,
                priority=priority,
                timeout=timeout,
                callback=callback,
                error_callback=error_callback,
                progress_callback=progress_callback,
                cancel_event=cancel_event,
            )

            # 存储任务
            self._tasks[task_id] = task
            self._total_tasks += 1

            # 提交到线程池
            future = self._executor.submit(self._execute_task, task)
            task.future = future

            # 添加到运行任务列表
            self._running_tasks[task_id] = task

            self._logger.debug(f"提交任务: {task_id} - {task.name}")
            return task_id

        except Exception as e:
            self._logger.error(f"提交任务失败: {e}")
            raise

    def _execute_task(self, task: AsyncTask) -> Any:
        """执行任务

        Args:
            task: 要执行的任务

        Returns:
            Any: 任务结果
        """
        try:
            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()

            # 创建进度更新函数
            def update_progress(current: int, total: int = 100, message: str = ""):
                if task.cancel_event and task.cancel_event.is_set():
                    raise InterruptedError("任务已取消")

                progress_info = ProgressInfo(
                    current=current,
                    total=total,
                    message=message,
                    percentage=current / total * 100 if total > 0 else 0,
                    elapsed_time=time.time() - task.started_at.timestamp(),
                )

                task.progress = progress_info.percentage

                # 调用进度回调
                if task.progress_callback:
                    self._schedule_ui_update(task.progress_callback, progress_info)

            # 准备函数参数
            func_kwargs = task.kwargs.copy()

            # 如果函数支持进度回调,添加进度更新函数
            import inspect

            sig = inspect.signature(task.func)
            if "progress_callback" in sig.parameters:
                func_kwargs["progress_callback"] = update_progress
            elif "update_progress" in sig.parameters:
                func_kwargs["update_progress"] = update_progress

            # 如果函数支持取消事件,添加取消事件
            if "cancel_event" in sig.parameters:
                func_kwargs["cancel_event"] = task.cancel_event

            # 执行任务
            start_time = time.time()

            if task.timeout:
                # 带超时的执行
                result = self._execute_with_timeout(task, func_kwargs)
            else:
                # 正常执行
                result = task.func(*task.args, **func_kwargs)

            # 检查是否被取消
            if task.cancel_event and task.cancel_event.is_set():
                task.status = TaskStatus.CANCELLED
                self._cancelled_tasks += 1
                return None

            # 任务完成
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            task.progress = 100.0
            self._completed_tasks += 1

            # 调用完成回调
            if task.callback:
                self._schedule_ui_update(task.callback, result)

            self._logger.debug(
                f"任务完成: {task.task_id} - {task.name}, "
                f"耗时: {time.time() - start_time:.2f}s"
            )

            return result

        except Exception as e:
            # 任务失败
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
            task.error = e
            self._failed_tasks += 1

            # 调用错误回调
            if task.error_callback:
                self._schedule_ui_update(task.error_callback, e)

            self._logger.error(f"任务失败: {task.task_id} - {task.name}, 错误: {e}")
            raise

        finally:
            # 从运行任务列表中移除
            self._running_tasks.pop(task.task_id, None)

    def _execute_with_timeout(self, task: AsyncTask, func_kwargs: dict) -> Any:
        """带超时的任务执行

        Args:
            task: 任务对象
            func_kwargs: 函数参数

        Returns:
            Any: 任务结果
        """
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError(f"任务超时: {task.timeout}秒")

        # 设置超时信号(仅在Unix系统上可用)
        try:
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(task.timeout))

            try:
                result = task.func(*task.args, **func_kwargs)
                return result
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

        except AttributeError:
            # Windows系统不支持SIGALRM,使用线程超时
            import concurrent.futures

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(task.func, *task.args, **func_kwargs)
                try:
                    return future.result(timeout=task.timeout)
                except concurrent.futures.TimeoutError:
                    raise TimeoutError(f"任务超时: {task.timeout}秒")

    def _schedule_ui_update(self, callback: Callable, *args) -> None:
        """调度UI更新

        Args:
            callback: 回调函数
            *args: 回调参数
        """
        try:
            self._ui_update_queue.put((callback, args))
        except Exception as e:
            self._logger.error(f"调度UI更新失败: {e}")

    def _start_ui_update_loop(self) -> None:
        """启动UI更新循环"""

        def update_ui():
            try:
                # 处理所有待更新的UI回调
                while True:
                    try:
                        callback, args = self._ui_update_queue.get_nowait()
                        callback(*args)
                    except Empty:
                        break
                    except Exception as e:
                        self._logger.error(f"UI更新回调失败: {e}")

            except Exception as e:
                self._logger.error(f"UI更新循环失败: {e}")

            # 如果处理器仍在运行,继续调度
            if self._is_running:
                # 使用tkinter的after方法调度下次更新
                try:
                    # 获取主窗口
                    root = tk._default_root
                    if root:
                        root.after(self._ui_update_interval, update_ui)
                except:
                    # 如果无法获取主窗口,使用线程定时器
                    timer = threading.Timer(self._ui_update_interval / 1000, update_ui)
                    timer.daemon = True
                    timer.start()

        # 启动UI更新循环
        update_ui()

    def cancel_task(self, task_id: str) -> bool:
        """取消任务

        Args:
            task_id: 任务ID

        Returns:
            bool: 是否成功取消
        """
        try:
            task = self._tasks.get(task_id)
            if not task:
                return False

            # 设置取消事件
            if task.cancel_event:
                task.cancel_event.set()

            # 尝试取消Future
            if task.future and not task.future.done():
                cancelled = task.future.cancel()
                if cancelled:
                    task.status = TaskStatus.CANCELLED
                    self._cancelled_tasks += 1
                    self._logger.debug(f"任务已取消: {task_id}")
                return cancelled

            return False

        except Exception as e:
            self._logger.error(f"取消任务失败: {task_id}, 错误: {e}")
            return False

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态

        Args:
            task_id: 任务ID

        Returns:
            Optional[TaskStatus]: 任务状态
        """
        task = self._tasks.get(task_id)
        return task.status if task else None

    def get_task_progress(self, task_id: str) -> float:
        """获取任务进度

        Args:
            task_id: 任务ID

        Returns:
            float: 进度百分比 (0-100)
        """
        task = self._tasks.get(task_id)
        return task.progress if task else 0.0

    def get_task_result(self, task_id: str) -> Any:
        """获取任务结果

        Args:
            task_id: 任务ID

        Returns:
            Any: 任务结果
        """
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.COMPLETED:
            return task.result
        return None

    def get_task_error(self, task_id: str) -> Optional[Exception]:
        """获取任务错误

        Args:
            task_id: 任务ID

        Returns:
            Optional[Exception]: 任务错误
        """
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.FAILED:
            return task.error
        return None

    def get_running_tasks(self) -> List[str]:
        """获取正在运行的任务列表

        Returns:
            List[str]: 任务ID列表
        """
        return list(self._running_tasks.keys())

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        return {
            "total_tasks": self._total_tasks,
            "completed_tasks": self._completed_tasks,
            "failed_tasks": self._failed_tasks,
            "cancelled_tasks": self._cancelled_tasks,
            "running_tasks": len(self._running_tasks),
            "pending_tasks": self._total_tasks
            - self._completed_tasks
            - self._failed_tasks
            - self._cancelled_tasks
            - len(self._running_tasks),
            "success_rate": (self._completed_tasks / self._total_tasks * 100)
            if self._total_tasks > 0
            else 0,
            "max_workers": self._max_workers,
        }

    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """等待任务完成

        Args:
            task_id: 任务ID
            timeout: 超时时间(秒)

        Returns:
            Any: 任务结果
        """
        task = self._tasks.get(task_id)
        if not task or not task.future:
            return None

        try:
            return task.future.result(timeout=timeout)
        except Exception as e:
            self._logger.error(f"等待任务失败: {task_id}, 错误: {e}")
            return None

    def clear_completed_tasks(self) -> int:
        """清理已完成的任务

        Returns:
            int: 清理的任务数量
        """
        cleared_count = 0

        tasks_to_remove = []
        for task_id, task in self._tasks.items():
            if task.status in (
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
                TaskStatus.CANCELLED,
            ):
                tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self._tasks[task_id]
            cleared_count += 1

        self._logger.debug(f"清理已完成任务: {cleared_count} 个")
        return cleared_count

    def shutdown(self, wait: bool = True) -> None:
        """关闭异步处理器

        Args:
            wait: 是否等待所有任务完成
        """
        try:
            self._is_running = False

            # 取消所有运行中的任务
            for task_id in list(self._running_tasks.keys()):
                self.cancel_task(task_id)

            # 关闭线程池
            self._executor.shutdown(wait=wait)

            self._logger.info("异步处理器已关闭")

        except Exception as e:
            self._logger.error(f"关闭异步处理器失败: {e}")


class ProgressDialog(tk.Toplevel):
    """进度对话框

    显示异步任务的执行进度.
    """

    def __init__(self, parent, title: str = "处理中...", cancelable: bool = True):
        """初始化进度对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            cancelable: 是否可取消
        """
        super().__init__(parent)

        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)

        # 设置为模态对话框
        self.transient(parent)
        self.grab_set()

        # 居中显示
        self.center_window()

        # 状态变量
        self._cancelled = False
        self._task_id: Optional[str] = None
        self._processor: Optional[AsyncProcessor] = None

        # 创建UI
        self._create_ui(cancelable)

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def center_window(self) -> None:
        """居中显示窗口"""
        self.update_idletasks()

        # 获取窗口大小
        width = self.winfo_width()
        height = self.winfo_height()

        # 获取屏幕大小
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # 计算居中位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_ui(self, cancelable: bool) -> None:
        """创建UI组件"""
        # 主框架
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 消息标签
        self._message_label = ttk.Label(
            main_frame, text="正在处理,请稍候...", font=("Microsoft YaHei UI", 10)
        )
        self._message_label.pack(pady=(0, 10))

        # 进度条
        self._progress_var = tk.DoubleVar()
        self._progress_bar = ttk.Progressbar(
            main_frame,
            variable=self._progress_var,
            maximum=100,
            length=300,
            mode="determinate",
        )
        self._progress_bar.pack(pady=(0, 10))

        # 进度文本
        self._progress_text = ttk.Label(
            main_frame, text="0%", font=("Microsoft YaHei UI", 9)
        )
        self._progress_text.pack(pady=(0, 10))

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        if cancelable:
            # 取消按钮
            self._cancel_button = ttk.Button(
                button_frame, text="取消", command=self._on_cancel
            )
            self._cancel_button.pack(side=tk.RIGHT)

    def bind_task(self, processor: AsyncProcessor, task_id: str) -> None:
        """绑定任务

        Args:
            processor: 异步处理器
            task_id: 任务ID
        """
        self._processor = processor
        self._task_id = task_id

        # 开始监控任务进度
        self._monitor_progress()

    def _monitor_progress(self) -> None:
        """监控任务进度"""
        if not self._processor or not self._task_id or self._cancelled:
            return

        try:
            # 获取任务状态和进度
            status = self._processor.get_task_status(self._task_id)
            progress = self._processor.get_task_progress(self._task_id)

            # 更新进度显示
            self._progress_var.set(progress)
            self._progress_text.config(text=f"{progress:.1f}%")

            # 检查任务状态
            if status == TaskStatus.COMPLETED:
                self._on_task_completed()
            elif status == TaskStatus.FAILED:
                self._on_task_failed()
            elif status == TaskStatus.CANCELLED:
                self._on_task_cancelled()
            else:
                # 继续监控
                self.after(100, self._monitor_progress)

        except Exception as e:
            logging.getLogger(__name__).error(f"监控任务进度失败: {e}")
            self._on_task_failed()

    def _on_task_completed(self) -> None:
        """任务完成处理"""
        self._progress_var.set(100)
        self._progress_text.config(text="100%")
        self._message_label.config(text="处理完成")

        # 延迟关闭对话框
        self.after(500, self.destroy)

    def _on_task_failed(self) -> None:
        """任务失败处理"""
        self._message_label.config(text="处理失败")

        # 显示错误信息
        if self._processor and self._task_id:
            error = self._processor.get_task_error(self._task_id)
            if error:
                tk.messagebox.showerror("错误", f"处理失败:{error!s}")

        self.destroy()

    def _on_task_cancelled(self) -> None:
        """任务取消处理"""
        self._message_label.config(text="已取消")
        self.destroy()

    def _on_cancel(self) -> None:
        """取消按钮处理"""
        if self._processor and self._task_id:
            self._processor.cancel_task(self._task_id)

        self._cancelled = True
        self.destroy()

    def _on_close(self) -> None:
        """关闭事件处理"""
        self._on_cancel()

    def update_message(self, message: str) -> None:
        """更新消息

        Args:
            message: 新消息
        """
        self._message_label.config(text=message)


# 全局异步处理器实例
async_processor = AsyncProcessor()


# 装饰器函数


def async_task(
    name: Optional[str] = None,
    priority: TaskPriority = TaskPriority.NORMAL,
    timeout: Optional[float] = None,
    show_progress: bool = False,
):
    """异步任务装饰器

    Args:
        name: 任务名称
        priority: 任务优先级
        timeout: 超时时间
        show_progress: 是否显示进度对话框
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # 提取UI相关参数
            parent_window = kwargs.pop("parent_window", None)
            progress_title = kwargs.pop("progress_title", name or "处理中...")

            # 提交任务
            task_id = async_processor.submit_task(
                func,
                *args,
                name=name or func.__name__,
                priority=priority,
                timeout=timeout,
                **kwargs,
            )

            # 如果需要显示进度对话框
            if show_progress and parent_window:
                dialog = ProgressDialog(parent_window, progress_title)
                dialog.bind_task(async_processor, task_id)

            return task_id

        return wrapper

    return decorator


def run_async(
    func: Callable,
    *args,
    parent_window: Optional[tk.Widget] = None,
    progress_title: str = "处理中...",
    show_progress: bool = True,
    **kwargs,
) -> str:
    """运行异步函数的便捷方法

    Args:
        func: 要执行的函数
        *args: 函数参数
        parent_window: 父窗口(用于显示进度对话框)
        progress_title: 进度对话框标题
        show_progress: 是否显示进度对话框
        **kwargs: 函数关键字参数

    Returns:
        str: 任务ID
    """
    # 提交任务
    task_id = async_processor.submit_task(func, *args, name=func.__name__, **kwargs)

    # 如果需要显示进度对话框
    if show_progress and parent_window:
        dialog = ProgressDialog(parent_window, progress_title)
        dialog.bind_task(async_processor, task_id)

    return task_id
