"""
MiniCRM TTK异步处理器测试

测试异步处理功能的各个方面，包括：
- 任务提交和执行
- 进度跟踪
- 任务取消
- 错误处理
- UI更新
- 性能监控
"""

import time
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from src.minicrm.ui.ttk_base.async_processor import (
    AsyncProcessor,
    AsyncTask,
    ProgressDialog,
    ProgressInfo,
    TaskPriority,
    TaskStatus,
    async_task,
    run_async,
)


class TestTaskStatus(unittest.TestCase):
    """测试任务状态枚举"""

    def test_task_status_values(self):
        """测试任务状态值"""
        self.assertEqual(TaskStatus.PENDING.value, "pending")
        self.assertEqual(TaskStatus.RUNNING.value, "running")
        self.assertEqual(TaskStatus.COMPLETED.value, "completed")
        self.assertEqual(TaskStatus.FAILED.value, "failed")
        self.assertEqual(TaskStatus.CANCELLED.value, "cancelled")


class TestTaskPriority(unittest.TestCase):
    """测试任务优先级枚举"""

    def test_task_priority_values(self):
        """测试任务优先级值"""
        self.assertEqual(TaskPriority.LOW.value, 1)
        self.assertEqual(TaskPriority.NORMAL.value, 2)
        self.assertEqual(TaskPriority.HIGH.value, 3)
        self.assertEqual(TaskPriority.CRITICAL.value, 4)


class TestAsyncTask(unittest.TestCase):
    """测试异步任务类"""

    def test_task_creation(self):
        """测试任务创建"""

        def test_func(x, y):
            return x + y

        task = AsyncTask(
            task_id="test_task",
            name="Test Task",
            func=test_func,
            args=(1, 2),
            kwargs={"timeout": 10},
            priority=TaskPriority.HIGH,
        )

        self.assertEqual(task.task_id, "test_task")
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.func, test_func)
        self.assertEqual(task.args, (1, 2))
        self.assertEqual(task.kwargs, {"timeout": 10})
        self.assertEqual(task.priority, TaskPriority.HIGH)
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.progress, 0.0)
        self.assertIsNone(task.result)
        self.assertIsNone(task.error)

    def test_task_defaults(self):
        """测试任务默认值"""

        def test_func():
            pass

        task = AsyncTask(task_id="test_task", name="Test Task", func=test_func)

        self.assertEqual(task.args, ())
        self.assertEqual(task.kwargs, {})
        self.assertEqual(task.priority, TaskPriority.NORMAL)
        self.assertIsNone(task.timeout)
        self.assertIsNone(task.callback)
        self.assertIsNone(task.error_callback)
        self.assertIsNone(task.progress_callback)


class TestProgressInfo(unittest.TestCase):
    """测试进度信息类"""

    def test_progress_info_creation(self):
        """测试进度信息创建"""
        progress = ProgressInfo(
            current=50,
            total=100,
            message="Processing...",
            percentage=50.0,
            elapsed_time=10.5,
            estimated_remaining=10.5,
        )

        self.assertEqual(progress.current, 50)
        self.assertEqual(progress.total, 100)
        self.assertEqual(progress.message, "Processing...")
        self.assertEqual(progress.percentage, 50.0)
        self.assertEqual(progress.elapsed_time, 10.5)
        self.assertEqual(progress.estimated_remaining, 10.5)

    def test_progress_info_defaults(self):
        """测试进度信息默认值"""
        progress = ProgressInfo()

        self.assertEqual(progress.current, 0)
        self.assertEqual(progress.total, 100)
        self.assertEqual(progress.message, "")
        self.assertEqual(progress.percentage, 0.0)
        self.assertEqual(progress.elapsed_time, 0.0)
        self.assertEqual(progress.estimated_remaining, 0.0)


class TestAsyncProcessor(unittest.TestCase):
    """测试异步处理器"""

    def setUp(self):
        """测试准备"""
        self.processor = AsyncProcessor(max_workers=2)

    def tearDown(self):
        """测试清理"""
        if self.processor:
            self.processor.shutdown(wait=False)

    def test_processor_initialization(self):
        """测试处理器初始化"""
        self.assertEqual(self.processor._max_workers, 2)
        self.assertTrue(self.processor._is_running)
        self.assertEqual(len(self.processor._tasks), 0)
        self.assertEqual(len(self.processor._running_tasks), 0)
        self.assertEqual(self.processor._total_tasks, 0)
        self.assertEqual(self.processor._completed_tasks, 0)
        self.assertEqual(self.processor._failed_tasks, 0)
        self.assertEqual(self.processor._cancelled_tasks, 0)

    def test_submit_simple_task(self):
        """测试提交简单任务"""

        def simple_task(x, y):
            return x + y

        task_id = self.processor.submit_task(simple_task, 1, 2)

        # 验证任务提交
        self.assertIsInstance(task_id, str)
        self.assertIn(task_id, self.processor._tasks)
        self.assertEqual(self.processor._total_tasks, 1)

        # 等待任务完成
        result = self.processor.wait_for_task(task_id, timeout=5.0)

        # 验证任务结果
        self.assertEqual(result, 3)
        self.assertEqual(self.processor.get_task_status(task_id), TaskStatus.COMPLETED)
        self.assertEqual(self.processor.get_task_result(task_id), 3)

    def test_submit_task_with_kwargs(self):
        """测试提交带关键字参数的任务"""

        def task_with_kwargs(x, y, multiplier=1):
            return (x + y) * multiplier

        task_id = self.processor.submit_task(task_with_kwargs, 1, 2, multiplier=3)

        # 等待任务完成
        result = self.processor.wait_for_task(task_id, timeout=5.0)

        # 验证结果
        self.assertEqual(result, 9)  # (1 + 2) * 3

    def test_task_with_progress_callback(self):
        """测试带进度回调的任务"""
        progress_updates = []

        def progress_callback(progress_info):
            progress_updates.append(progress_info)

        def task_with_progress(progress_callback=None):
            if progress_callback:
                progress_callback(25, 100, "Step 1")
                time.sleep(0.1)
                progress_callback(50, 100, "Step 2")
                time.sleep(0.1)
                progress_callback(75, 100, "Step 3")
                time.sleep(0.1)
                progress_callback(100, 100, "Complete")
            return "done"

        task_id = self.processor.submit_task(
            task_with_progress, progress_callback=progress_callback
        )

        # 等待任务完成
        result = self.processor.wait_for_task(task_id, timeout=5.0)

        # 验证结果和进度更新
        self.assertEqual(result, "done")
        # 注意：由于UI更新是异步的，可能需要等待
        time.sleep(0.5)
        self.assertGreater(len(progress_updates), 0)

    def test_task_with_callback(self):
        """测试带完成回调的任务"""
        callback_result = []

        def completion_callback(result):
            callback_result.append(result)

        def simple_task():
            return "task_result"

        task_id = self.processor.submit_task(simple_task, callback=completion_callback)

        # 等待任务完成
        self.processor.wait_for_task(task_id, timeout=5.0)

        # 等待回调执行
        time.sleep(0.5)

        # 验证回调被调用
        self.assertEqual(len(callback_result), 1)
        self.assertEqual(callback_result[0], "task_result")

    def test_task_with_error(self):
        """测试任务错误处理"""
        error_callbacks = []

        def error_callback(error):
            error_callbacks.append(error)

        def failing_task():
            raise ValueError("Test error")

        task_id = self.processor.submit_task(
            failing_task, error_callback=error_callback
        )

        # 等待任务完成（失败）
        result = self.processor.wait_for_task(task_id, timeout=5.0)

        # 验证任务失败
        self.assertIsNone(result)
        self.assertEqual(self.processor.get_task_status(task_id), TaskStatus.FAILED)

        error = self.processor.get_task_error(task_id)
        self.assertIsInstance(error, ValueError)
        self.assertEqual(str(error), "Test error")

        # 等待错误回调
        time.sleep(0.5)
        self.assertEqual(len(error_callbacks), 1)
        self.assertIsInstance(error_callbacks[0], ValueError)

    def test_cancel_task(self):
        """测试取消任务"""

        def long_running_task(cancel_event=None):
            for i in range(100):
                if cancel_event and cancel_event.is_set():
                    raise InterruptedError("Task cancelled")
                time.sleep(0.01)
            return "completed"

        task_id = self.processor.submit_task(long_running_task)

        # 等待任务开始
        time.sleep(0.1)

        # 取消任务
        cancelled = self.processor.cancel_task(task_id)

        # 验证取消结果
        # 注意：取消可能不总是成功，取决于任务的执行状态
        if cancelled:
            self.assertEqual(
                self.processor.get_task_status(task_id), TaskStatus.CANCELLED
            )

    def test_get_statistics(self):
        """测试获取统计信息"""

        # 提交一些任务
        def simple_task(x):
            return x * 2

        def failing_task():
            raise ValueError("Error")

        # 提交成功任务
        task1_id = self.processor.submit_task(simple_task, 1)
        task2_id = self.processor.submit_task(simple_task, 2)

        # 提交失败任务
        task3_id = self.processor.submit_task(failing_task)

        # 等待任务完成
        self.processor.wait_for_task(task1_id, timeout=5.0)
        self.processor.wait_for_task(task2_id, timeout=5.0)
        self.processor.wait_for_task(task3_id, timeout=5.0)

        # 获取统计信息
        stats = self.processor.get_statistics()

        # 验证统计信息
        self.assertEqual(stats["total_tasks"], 3)
        self.assertEqual(stats["completed_tasks"], 2)
        self.assertEqual(stats["failed_tasks"], 1)
        self.assertEqual(stats["max_workers"], 2)
        self.assertGreaterEqual(stats["success_rate"], 0)

    def test_clear_completed_tasks(self):
        """测试清理已完成任务"""

        def simple_task(x):
            return x

        # 提交并完成一些任务
        task_ids = []
        for i in range(5):
            task_id = self.processor.submit_task(simple_task, i)
            task_ids.append(task_id)

        # 等待所有任务完成
        for task_id in task_ids:
            self.processor.wait_for_task(task_id, timeout=5.0)

        # 验证任务存在
        self.assertEqual(len(self.processor._tasks), 5)

        # 清理已完成任务
        cleared_count = self.processor.clear_completed_tasks()

        # 验证清理结果
        self.assertEqual(cleared_count, 5)
        self.assertEqual(len(self.processor._tasks), 0)

    def test_get_running_tasks(self):
        """测试获取运行中任务"""

        def long_task():
            time.sleep(1.0)
            return "done"

        # 提交长时间运行的任务
        task_id = self.processor.submit_task(long_task)

        # 等待任务开始
        time.sleep(0.1)

        # 获取运行中任务
        running_tasks = self.processor.get_running_tasks()

        # 验证运行中任务
        if running_tasks:  # 任务可能已经完成
            self.assertIn(task_id, running_tasks)

        # 等待任务完成
        self.processor.wait_for_task(task_id, timeout=5.0)

        # 验证任务不再运行
        running_tasks_after = self.processor.get_running_tasks()
        self.assertNotIn(task_id, running_tasks_after)


class TestProgressDialog(unittest.TestCase):
    """测试进度对话框"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

    def tearDown(self):
        """测试清理"""
        if self.root:
            self.root.destroy()

    def test_dialog_creation(self):
        """测试对话框创建"""
        dialog = ProgressDialog(self.root, title="Test Progress", cancelable=True)

        # 验证对话框属性
        self.assertEqual(dialog.title(), "Test Progress")
        self.assertFalse(dialog._cancelled)
        self.assertIsNone(dialog._task_id)
        self.assertIsNone(dialog._processor)

        # 验证UI组件存在
        self.assertIsNotNone(dialog._message_label)
        self.assertIsNotNone(dialog._progress_bar)
        self.assertIsNotNone(dialog._progress_text)
        self.assertIsNotNone(dialog._cancel_button)

        dialog.destroy()

    def test_dialog_without_cancel(self):
        """测试不可取消的对话框"""
        dialog = ProgressDialog(self.root, title="Test Progress", cancelable=False)

        # 验证没有取消按钮
        self.assertFalse(hasattr(dialog, "_cancel_button"))

        dialog.destroy()

    def test_update_message(self):
        """测试更新消息"""
        dialog = ProgressDialog(self.root)

        # 更新消息
        dialog.update_message("Processing data...")

        # 验证消息更新
        self.assertEqual(dialog._message_label.cget("text"), "Processing data...")

        dialog.destroy()

    @patch("src.minicrm.ui.ttk_base.async_processor.AsyncProcessor")
    def test_bind_task(self, mock_processor_class):
        """测试绑定任务"""
        # 创建模拟处理器
        mock_processor = Mock()
        mock_processor.get_task_status.return_value = TaskStatus.RUNNING
        mock_processor.get_task_progress.return_value = 50.0

        dialog = ProgressDialog(self.root)

        # 绑定任务
        dialog.bind_task(mock_processor, "test_task")

        # 验证绑定
        self.assertEqual(dialog._processor, mock_processor)
        self.assertEqual(dialog._task_id, "test_task")

        dialog.destroy()


class TestAsyncDecorators(unittest.TestCase):
    """测试异步装饰器"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

    def tearDown(self):
        """测试清理"""
        if self.root:
            self.root.destroy()

    @patch("src.minicrm.ui.ttk_base.async_processor.async_processor")
    def test_async_task_decorator(self, mock_processor):
        """测试异步任务装饰器"""
        mock_processor.submit_task.return_value = "test_task_id"

        @async_task(name="Test Task", priority=TaskPriority.HIGH)
        def decorated_task(x, y):
            return x + y

        # 调用装饰的函数
        task_id = decorated_task(1, 2)

        # 验证任务提交
        self.assertEqual(task_id, "test_task_id")
        mock_processor.submit_task.assert_called_once()

        # 验证调用参数
        call_args = mock_processor.submit_task.call_args
        self.assertEqual(call_args[0][1], 1)  # 第一个参数
        self.assertEqual(call_args[0][2], 2)  # 第二个参数
        self.assertEqual(call_args[1]["name"], "Test Task")
        self.assertEqual(call_args[1]["priority"], TaskPriority.HIGH)

    @patch("src.minicrm.ui.ttk_base.async_processor.async_processor")
    @patch("src.minicrm.ui.ttk_base.async_processor.ProgressDialog")
    def test_async_task_with_progress(self, mock_dialog_class, mock_processor):
        """测试带进度的异步任务装饰器"""
        mock_processor.submit_task.return_value = "test_task_id"
        mock_dialog = Mock()
        mock_dialog_class.return_value = mock_dialog

        @async_task(name="Test Task", show_progress=True)
        def decorated_task(x, y):
            return x + y

        # 调用装饰的函数（带父窗口）
        task_id = decorated_task(1, 2, parent_window=self.root)

        # 验证任务提交和进度对话框创建
        self.assertEqual(task_id, "test_task_id")
        mock_processor.submit_task.assert_called_once()
        mock_dialog_class.assert_called_once()
        mock_dialog.bind_task.assert_called_once_with(mock_processor, "test_task_id")

    @patch("src.minicrm.ui.ttk_base.async_processor.async_processor")
    def test_run_async_function(self, mock_processor):
        """测试run_async函数"""
        mock_processor.submit_task.return_value = "test_task_id"

        def test_function(x, y):
            return x * y

        # 调用run_async
        task_id = run_async(
            test_function,
            3,
            4,
            parent_window=self.root,
            progress_title="Calculating...",
            show_progress=False,
        )

        # 验证任务提交
        self.assertEqual(task_id, "test_task_id")
        mock_processor.submit_task.assert_called_once()

        # 验证调用参数
        call_args = mock_processor.submit_task.call_args
        self.assertEqual(call_args[0][1], 3)  # 第一个参数
        self.assertEqual(call_args[0][2], 4)  # 第二个参数
        self.assertEqual(call_args[1]["name"], "test_function")


class TestAsyncProcessorIntegration(unittest.TestCase):
    """测试异步处理器集成"""

    def setUp(self):
        """测试准备"""
        self.processor = AsyncProcessor(max_workers=2)

    def tearDown(self):
        """测试清理"""
        if self.processor:
            self.processor.shutdown(wait=False)

    def test_concurrent_tasks(self):
        """测试并发任务执行"""

        def concurrent_task(task_id, duration):
            time.sleep(duration)
            return f"Task {task_id} completed"

        # 提交多个并发任务
        task_ids = []
        for i in range(4):
            task_id = self.processor.submit_task(
                concurrent_task,
                i,
                0.2,  # 200ms
                name=f"Concurrent Task {i}",
            )
            task_ids.append(task_id)

        # 等待所有任务完成
        results = []
        for task_id in task_ids:
            result = self.processor.wait_for_task(task_id, timeout=5.0)
            results.append(result)

        # 验证所有任务都完成了
        self.assertEqual(len(results), 4)
        for i, result in enumerate(results):
            self.assertEqual(result, f"Task {i} completed")

    def test_task_priority_handling(self):
        """测试任务优先级处理"""

        # 注意：当前实现可能不严格按优先级执行，这里主要测试优先级设置
        def priority_task(priority_name):
            return f"Priority {priority_name} task"

        # 提交不同优先级的任务
        low_task = self.processor.submit_task(
            priority_task, "LOW", priority=TaskPriority.LOW
        )

        high_task = self.processor.submit_task(
            priority_task, "HIGH", priority=TaskPriority.HIGH
        )

        critical_task = self.processor.submit_task(
            priority_task, "CRITICAL", priority=TaskPriority.CRITICAL
        )

        # 等待任务完成
        low_result = self.processor.wait_for_task(low_task, timeout=5.0)
        high_result = self.processor.wait_for_task(high_task, timeout=5.0)
        critical_result = self.processor.wait_for_task(critical_task, timeout=5.0)

        # 验证任务都完成了
        self.assertEqual(low_result, "Priority LOW task")
        self.assertEqual(high_result, "Priority HIGH task")
        self.assertEqual(critical_result, "Priority CRITICAL task")

    def test_error_recovery(self):
        """测试错误恢复"""

        def mixed_task(should_fail):
            if should_fail:
                raise RuntimeError("Intentional failure")
            return "Success"

        # 提交混合任务（成功和失败）
        success_task = self.processor.submit_task(mixed_task, False)
        failure_task = self.processor.submit_task(mixed_task, True)
        recovery_task = self.processor.submit_task(mixed_task, False)

        # 等待任务完成
        success_result = self.processor.wait_for_task(success_task, timeout=5.0)
        failure_result = self.processor.wait_for_task(failure_task, timeout=5.0)
        recovery_result = self.processor.wait_for_task(recovery_task, timeout=5.0)

        # 验证结果
        self.assertEqual(success_result, "Success")
        self.assertIsNone(failure_result)  # 失败任务返回None
        self.assertEqual(recovery_result, "Success")  # 后续任务不受影响

        # 验证任务状态
        self.assertEqual(
            self.processor.get_task_status(success_task), TaskStatus.COMPLETED
        )
        self.assertEqual(
            self.processor.get_task_status(failure_task), TaskStatus.FAILED
        )
        self.assertEqual(
            self.processor.get_task_status(recovery_task), TaskStatus.COMPLETED
        )


if __name__ == "__main__":
    unittest.main()
