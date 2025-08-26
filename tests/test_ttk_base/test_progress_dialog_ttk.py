"""测试TTK进度对话框

测试ProgressDialogTTK类的功能，包括：
- 进度对话框创建和显示
- 确定和不确定进度模式
- 进度更新和消息设置
- 取消功能
- 异步进度更新
- 进度任务执行

作者: MiniCRM开发团队
"""

import unittest
import tkinter as tk
import threading
import time
from unittest.mock import Mock, patch

from src.minicrm.ui.ttk_base.progress_dialog_ttk import (
    ProgressDialogTTK,
    ProgressTask,
    ProgressUpdater,
    show_progress_dialog
)


class TestProgressDialogTTK(unittest.TestCase):
    """测试ProgressDialogTTK类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口

    def tearDown(self):
        """测试清理"""
        try:
            self.root.destroy()
        except:
            pass

    def test_determinate_progress_dialog_creation(self):
        """测试确定进度对话框创建"""
        dialog = ProgressDialogTTK(
            parent=self.root,
            title="测试进度",
            message="正在处理...",
            determinate=True,
            cancelable=True
        )

        # 验证基本属性
        self.assertEqual(dialog.dialog_title, "测试进度")
        self.assertEqual(dialog.message, "正在处理...")
        self.assertTrue(dialog.determinate)
        self.assertTrue(dialog.cancelable)
        self.assertFalse(dialog.is_cancelled)
        self.assertFalse(dialog.is_completed)

        # 验证UI组件
        self.assertIsNotNone(dialog.message_label)
        self.assertIsNotNone(dialog.progress_bar)
        self.assertIsNotNone(dialog.detail_label)

        # 验证按钮
        self.assertIn("取消", dialog.buttons)

        dialog.destroy()

    def test_indeterminate_progress_dialog_creation(self):
        """测试不确定进度对话框创建"""
        dialog = ProgressDialogTTK(
            parent=self.root,
            title="不确定进度",
            message="请稍候...",
            determinate=False,
            cancelable=False
        )

        # 验证属性
        self.assertFalse(dialog.determinate)
        self.assertFalse(dialog.cancelable)

        # 验证进度条模式
        self.assertEqual(dialog.progress_bar.cget("mode"), "indeterminate")

        # 验证没有取消按钮
        self.assertNotIn("取消", dialog.buttons)

        dialog.destroy()

    def test_progress_value_setting(self):
        """测试进度值设置"""
        dialog = ProgressDialogTTK(
            parent=self.root,
            determinate=True
        )

        # 测试设置进度值
        dialog.set_progress(50, 100)

        # 等待更新
        self.root.update()

        self.assertEqual(dialog.progress_value, 50)
        self.assertEqual(dialog.progress_max, 100)

        # 测试进度百分比
        dialog.set_progress_percentage(75)
        self.root.update()

        self.assertEqual(dialog.get_progress_percentage(), 75)

        dialog.destroy()

    def test_progress_increment(self):
        """测试进度增量"""
        dialog = ProgressDialogTTK(
            parent=self.root,
            determinate=True
        )

        # 设置初始进度
        dialog.set_progress(10, 100)
        self.root.update()

        # 增加进度
        dialog.increment_progress(20)
        self.root.update()

        self.assertEqual(dialog.progress_value, 30)

        # 测试超出最大值的情况
        dialog.increment_progress(80)
        self.root.update()

        self.assertEqual(dialog.progress_value, 100)

        dialog.destroy()

    def test_message_and_detail_setting(self):
        """测试消息和详细信息设置"""
        dialog = ProgressDialogTTK(parent=self.root)

        # 测试设置消息
        dialog.set_message("新的进度消息")
        self.root.update()

        self.assertEqual(dialog.message_var.get(), "新的进度消息")

        # 测试设置详细信息
        dialog.set_detail("详细进度信息")
        self.root.update()

        self.assertEqual(dialog.detail_var.get(), "详细进度信息")

        dialog.destroy()

    def test_progress_completion(self):
        """测试进度完成"""
        dialog = ProgressDialogTTK(
            parent=self.root,
            determinate=True,
            cancelable=True
        )

        # 完成进度
        dialog.complete_progress("操作完成")
        self.root.update()

        # 验证状态
        self.assertTrue(dialog.is_completed)
        self.assertEqual(dialog.message_var.get(), "操作完成")

        # 验证按钮文本变化
        cancel_button = dialog.get_button("关闭")
        self.assertIsNotNone(cancel_button)

        dialog.destroy()

    def test_progress_cancellation(self):
        """测试进度取消"""
        dialog = ProgressDialogTTK(
            parent=self.root,
            cancelable=True
        )

        # 设置取消回调
        cancel_callback = Mock()
        dialog.set_cancel_callback(cancel_callback)

        # 模拟用户确认取消
        with patch.object(dialog, 'confirm', return_value=True):
            dialog._on_cancel_progress()

        # 验证取消状态
        self.assertTrue(dialog.is_cancelled)
        cancel_callback.assert_called_once()

        dialog.destroy()

    def test_progress_cancellation_declined(self):
        """测试用户拒绝取消"""
        dialog = ProgressDialogTTK(
            parent=self.root,
            cancelable=True
        )

        cancel_callback = Mock()
        dialog.set_cancel_callback(cancel_callback)

        # 模拟用户拒绝取消
        with patch.object(dialog, 'confirm', return_value=False):
            dialog._on_cancel_progress()

        # 验证未取消
        self.assertFalse(dialog.is_cancelled)
        cancel_callback.assert_not_called()

        dialog.destroy()

    def test_progress_reset(self):
        """测试进度重置"""
        dialog = ProgressDialogTTK(
            parent=self.root,
            determinate=True
        )

        # 设置一些进度
        dialog.set_progress(50)
        dialog.complete_progress()
        self.root.update()

        # 重置进度
        dialog.reset_progress()
        self.root.update()

        # 验证重置结果
        self.assertEqual(dialog.progress_value, 0)
        self.assertFalse(dialog.is_cancelled)
        self.assertFalse(dialog.is_completed)

        dialog.destroy()

    def test_indeterminate_progress_warnings(self):
        """测试不确定进度模式的警告"""
        dialog = ProgressDialogTTK(
            parent=self.root,
            determinate=False
        )

        # 测试在不确定模式下设置进度值应该产生警告
        with patch.object(dialog.logger, 'warning') as mock_warning:
            dialog.set_progress(50)
            mock_warning.assert_called()

        with patch.object(dialog.logger, 'warning') as mock_warning:
            dialog.set_progress_percentage(50)
            mock_warning.assert_called()

        with patch.object(dialog.logger, 'warning') as mock_warning:
            dialog.increment_progress(10)
            mock_warning.assert_called()

        dialog.destroy()


class TestProgressUpdater(unittest.TestCase):
    """测试ProgressUpdater类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.dialog = ProgressDialogTTK(parent=self.root)
        self.updater = ProgressUpdater(self.dialog)

    def tearDown(self):
        """测试清理"""
        try:
            self.dialog.destroy()
            self.root.destroy()
        except:
            pass

    def test_progress_updater_methods(self):
        """测试进度更新器方法"""
        # 测试更新进度
        self.updater.update_progress(30, 100)
        self.root.update()
        self.assertEqual(self.dialog.progress_value, 30)

        # 测试更新百分比
        self.updater.update_percentage(50)
        self.root.update()
        self.assertEqual(self.dialog.get_progress_percentage(), 50)

        # 测试更新消息
        self.updater.update_message("测试消息")
        self.root.update()
        self.assertEqual(self.dialog.message_var.get(), "测试消息")

        # 测试更新详细信息
        self.updater.update_detail("详细信息")
        self.root.update()
        self.assertEqual(self.dialog.detail_var.get(), "详细信息")

        # 测试增量更新
        self.updater.increment(10)
        self.root.update()
        self.assertEqual(self.dialog.get_progress_percentage(), 60)

    def test_cancellation_check(self):
        """测试取消检查"""
        # 测试未取消状态
        self.assertFalse(self.updater.is_cancelled())

        # 模拟取消
        self.dialog.is_cancelled = True
        self.assertTrue(self.updater.is_cancelled())

        # 测试取消异常
        with self.assertRaises(InterruptedError):
            self.updater.check_cancelled()


class TestProgressTask(unittest.TestCase):
    """测试ProgressTask类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.dialog = ProgressDialogTTK(parent=self.root)

    def tearDown(self):
        """测试清理"""
        try:
            self.dialog.destroy()
            self.root.destroy()
        except:
            pass

    def test_successful_task_execution(self):
        """测试成功的任务执行"""
        def test_task(updater, value):
            updater.update_message("开始任务")
            updater.update_progress(50)
            return value * 2

        task = ProgressTask(test_task, self.dialog, 21)
        task.start()
        result = task.wait()

        self.assertEqual(result, 42)
        self.assertIsNone(task.exception)

    def test_task_with_exception(self):
        """测试带异常的任务执行"""
        def failing_task(updater):
            raise ValueError("测试异常")

        task = ProgressTask(failing_task, self.dialog)
        task.start()

        with self.assertRaises(ValueError):
            task.wait()

        self.assertIsInstance(task.exception, ValueError)

    def test_task_cancellation(self):
        """测试任务取消"""
        def long_task(updater):
            for i in range(100):
                updater.check_cancelled()  # 检查取消状态
                updater.update_progress(i)
                time.sleep(0.01)
            return "completed"

        task = ProgressTask(long_task, self.dialog)
        task.start()

        # 模拟取消
        time.sleep(0.1)  # 让任务开始
        self.dialog.is_cancelled = True

        with self.assertRaises(InterruptedError):
            task.wait()


class TestProgressDialogConvenienceFunctions(unittest.TestCase):
    """测试进度对话框便利函数"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """测试清理"""
        try:
            self.root.destroy()
        except:
            pass

    def test_show_progress_dialog_function(self):
        """测试show_progress_dialog函数"""
        def quick_task(updater, result_value):
            updater.update_message("执行任务")
            updater.update_progress(100)
            return result_value

        # 由于show_progress_dialog会显示模态对话框，我们需要模拟
        with patch('src.minicrm.ui.ttk_base.progress_dialog_ttk.ProgressDialogTTK') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.show_dialog.return_value = ("ok", None)
            mock_dialog_class.return_value = mock_dialog

            with patch('src.minicrm.ui.ttk_base.progress_dialog_ttk.ProgressTask') as mock_task_class:
                mock_task = Mock()
                mock_task.wait.return_value = "test_result"
                mock_task_class.return_value = mock_task

                result = show_progress_dialog(
                    self.root,
                    quick_task,
                    title="测试进度",
                    message="测试消息",
                    "test_value"
                )

                # 验证对话框被创建
                mock_dialog_class.assert_called_once()

                # 验证任务被创建和启动
                mock_task_class.assert_called_once()
                mock_task.start.assert_called_once()
                mock_task.wait.assert_called_once()


if __name__ == "__main__":
    unittest.main()
