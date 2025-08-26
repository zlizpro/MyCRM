"""
TTK错误处理器测试

测试TTK错误处理器的各项功能，包括：
- 错误分类和处理
- 用户友好的错误提示
- 错误恢复机制
- 性能监控集成
"""

import threading
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from src.minicrm.core.error_handler import ErrorSeverity, ErrorType
from src.minicrm.core.exceptions import UIError
from src.minicrm.core.ttk_error_handler import (
    TTKErrorHandler,
    confirm_operation,
    get_ttk_error_handler,
    handle_ui_operation,
    show_business_error,
    show_validation_error,
)


class TestTTKErrorHandler(unittest.TestCase):
    """TTK错误处理器测试类"""

    def setUp(self):
        """测试准备"""
        # 创建错误处理器实例，不使用真实的Tk窗口
        self.error_handler = TTKErrorHandler(None)

        # 模拟日志记录器
        self.error_handler._logger = Mock()

    def tearDown(self):
        """测试清理"""

    def test_initialization(self):
        """测试初始化"""
        handler = TTKErrorHandler()

        self.assertIsNotNone(handler._logger)
        self.assertEqual(handler._ui_error_count, 0)
        self.assertEqual(handler._recovery_success_count, 0)
        self.assertIsInstance(handler._recovery_callbacks, dict)
        self.assertIsInstance(handler._ttk_error_strategies, dict)

    def test_set_parent_window(self):
        """测试设置父窗口"""
        new_root = tk.Tk()
        new_root.withdraw()

        try:
            self.error_handler.set_parent_window(new_root)
            self.assertEqual(self.error_handler._parent_window, new_root)
        finally:
            new_root.destroy()

    def test_register_recovery_callback(self):
        """测试注册恢复回调"""
        callback = Mock()

        self.error_handler.register_recovery_callback("test_error", callback)

        self.assertIn("test_error", self.error_handler._recovery_callbacks)
        self.assertEqual(self.error_handler._recovery_callbacks["test_error"], callback)

    def test_classify_ui_error_widget_error(self):
        """测试UI错误分类 - 组件错误"""
        exception = Exception("widget creation failed")

        error_info = self.error_handler.classify_ui_error(
            exception, "create_button", {"widget_type": "Button"}
        )

        self.assertEqual(error_info.error_type, ErrorType.SYSTEM_ERROR)
        self.assertEqual(error_info.context["ui_component"], "widget")
        self.assertEqual(error_info.context["operation"], "create_button")
        self.assertEqual(error_info.context["ui_framework"], "ttk")

    def test_classify_ui_error_layout_error(self):
        """测试UI错误分类 - 布局错误"""
        exception = Exception("geometry manager error")

        error_info = self.error_handler.classify_ui_error(exception, "setup_layout", {})

        self.assertEqual(error_info.error_type, ErrorType.VALIDATION_ERROR)
        self.assertEqual(error_info.context["ui_component"], "layout")

    def test_classify_ui_error_style_error(self):
        """测试UI错误分类 - 样式错误"""
        exception = Exception("style configuration error")

        error_info = self.error_handler.classify_ui_error(exception, "apply_theme", {})

        self.assertEqual(error_info.error_type, ErrorType.VALIDATION_ERROR)
        self.assertEqual(error_info.context["ui_component"], "style")

    def test_classify_ui_error_event_error(self):
        """测试UI错误分类 - 事件错误"""
        exception = Exception("event binding failed")

        error_info = self.error_handler.classify_ui_error(exception, "bind_events", {})

        self.assertEqual(error_info.error_type, ErrorType.SYSTEM_ERROR)
        self.assertEqual(error_info.context["ui_component"], "event")

    @patch("src.minicrm.core.ttk_error_handler.performance_monitor")
    def test_handle_ui_operation_success(self, mock_monitor):
        """测试UI操作处理 - 成功情况"""
        mock_monitor.monitor_operation.return_value.__enter__ = Mock()
        mock_monitor.monitor_operation.return_value.__exit__ = Mock(return_value=None)

        with self.error_handler.handle_ui_operation("test_operation"):
            # 模拟成功的操作
            pass

        # 验证性能监控被调用
        mock_monitor.monitor_operation.assert_called_once()

    @patch("src.minicrm.core.ttk_error_handler.performance_monitor")
    @patch("tkinter.messagebox.showerror")
    def test_handle_ui_operation_with_error(self, mock_messagebox, mock_monitor):
        """测试UI操作处理 - 错误情况"""
        mock_monitor.monitor_operation.return_value.__enter__ = Mock()
        mock_monitor.monitor_operation.return_value.__exit__ = Mock(return_value=None)

        # 模拟恢复失败
        self.error_handler._attempt_recovery = Mock(return_value=False)

        with self.assertRaises(UIError):
            with self.error_handler.handle_ui_operation("test_operation"):
                raise Exception("test error")

        # 验证错误计数增加
        self.assertEqual(self.error_handler._ui_error_count, 1)

    def test_attempt_recovery_with_callback(self):
        """测试错误恢复 - 使用回调"""
        # 注册恢复回调
        recovery_callback = Mock(return_value=True)
        self.error_handler.register_recovery_callback("widget", recovery_callback)

        # 创建错误信息
        error_info = Mock()
        error_info.context = {"ui_component": "widget"}

        # 尝试恢复
        result = self.error_handler._attempt_recovery(error_info)

        self.assertTrue(result)
        recovery_callback.assert_called_once_with(error_info)

    def test_attempt_recovery_validation_error(self):
        """测试错误恢复 - 验证错误"""
        error_info = Mock()
        error_info.error_type = ErrorType.VALIDATION_ERROR
        error_info.context = {"ui_component": "layout"}

        result = self.error_handler._attempt_recovery(error_info)

        self.assertTrue(result)

    def test_attempt_recovery_system_error(self):
        """测试错误恢复 - 系统错误"""
        error_info = Mock()
        error_info.error_type = ErrorType.SYSTEM_ERROR
        error_info.context = {"ui_component": "widget"}

        result = self.error_handler._attempt_recovery(error_info)

        self.assertTrue(result)

    def test_get_error_title(self):
        """测试获取错误标题"""
        titles = {
            ErrorSeverity.CRITICAL: "严重错误",
            ErrorSeverity.HIGH: "系统错误",
            ErrorSeverity.MEDIUM: "操作警告",
            ErrorSeverity.LOW: "提示信息",
        }

        for severity, expected_title in titles.items():
            title = self.error_handler._get_error_title(severity)
            self.assertEqual(title, expected_title)

    def test_format_user_message(self):
        """测试格式化用户消息"""
        error_info = Mock()
        error_info.error_type = ErrorType.VALIDATION_ERROR
        error_info.message = "测试错误消息"
        error_info.details = "详细错误信息"
        error_info.context = {"ui_component": "layout"}

        message = self.error_handler._format_user_message(error_info)

        self.assertIn("输入数据验证失败", message)
        self.assertIn("测试错误消息", message)
        self.assertIn("详细信息：测试错误消息", message)
        self.assertIn("请检查窗口大小或重新调整界面布局", message)

    def test_get_user_suggestions(self):
        """测试获取用户建议"""
        test_cases = [
            ({"ui_component": "layout"}, "请检查窗口大小或重新调整界面布局"),
            ({"ui_component": "style"}, "请尝试切换到默认主题或重启应用程序"),
            ({"ui_component": "widget"}, "请重试操作或重启应用程序"),
            ({"ui_component": "event"}, "请重试操作，如果问题持续请联系技术支持"),
        ]

        for context, expected_suggestion in test_cases:
            error_info = Mock()
            error_info.context = context
            error_info.error_type = ErrorType.SYSTEM_ERROR

            suggestion = self.error_handler._get_user_suggestions(error_info)
            self.assertEqual(suggestion, expected_suggestion)

    @patch("tkinter.messagebox.showwarning")
    def test_show_validation_error(self, mock_messagebox):
        """测试显示验证错误"""
        self.error_handler.show_validation_error("test_field", "测试错误消息")

        mock_messagebox.assert_called_once()
        args, kwargs = mock_messagebox.call_args
        self.assertEqual(args[0], "数据验证错误")
        self.assertIn("test_field", args[1])
        self.assertIn("测试错误消息", args[1])

    @patch("tkinter.messagebox.showwarning")
    def test_show_business_error(self, mock_messagebox):
        """测试显示业务错误"""
        self.error_handler.show_business_error("test_operation", "测试业务错误")

        mock_messagebox.assert_called_once()
        args, kwargs = mock_messagebox.call_args
        self.assertEqual(args[0], "业务规则错误")
        self.assertIn("test_operation", args[1])
        self.assertIn("测试业务错误", args[1])

    @patch("tkinter.messagebox.askyesno")
    def test_confirm_operation(self, mock_messagebox):
        """测试确认操作"""
        mock_messagebox.return_value = True

        result = self.error_handler.confirm_operation("删除", "确认删除此项目？")

        self.assertTrue(result)
        mock_messagebox.assert_called_once()
        args, kwargs = mock_messagebox.call_args
        self.assertEqual(args[0], "确认删除")
        self.assertEqual(args[1], "确认删除此项目？")

    def test_get_ui_error_statistics(self):
        """测试获取UI错误统计"""
        # 模拟一些错误
        self.error_handler._ui_error_count = 10
        self.error_handler._recovery_success_count = 7

        stats = self.error_handler.get_ui_error_statistics()

        self.assertEqual(stats["ui_errors"], 10)
        self.assertEqual(stats["recovery_success"], 7)
        self.assertEqual(stats["recovery_rate"], 70.0)
        self.assertIn("total_errors", stats)
        self.assertIn("registered_callbacks", stats)

    def test_create_error_report(self):
        """测试创建错误报告"""
        # 模拟一些错误数据
        self.error_handler._ui_error_count = 5
        self.error_handler._recovery_success_count = 3

        report = self.error_handler.create_error_report()

        self.assertIsInstance(report, str)
        self.assertIn("MiniCRM TTK错误处理报告", report)
        self.assertIn("错误统计", report)
        self.assertIn("错误分布", report)
        self.assertIn("最近错误", report)


class TestGlobalFunctions(unittest.TestCase):
    """测试全局函数"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """测试清理"""
        if self.root:
            self.root.destroy()

    def test_get_ttk_error_handler(self):
        """测试获取全局错误处理器"""
        handler1 = get_ttk_error_handler(self.root)
        handler2 = get_ttk_error_handler()

        # 应该返回同一个实例
        self.assertIs(handler1, handler2)
        self.assertIsInstance(handler1, TTKErrorHandler)

    @patch("src.minicrm.core.ttk_error_handler.get_ttk_error_handler")
    def test_handle_ui_operation_function(self, mock_get_handler):
        """测试UI操作处理函数"""
        mock_handler = Mock()
        mock_get_handler.return_value = mock_handler

        context_manager = handle_ui_operation("test_op", param1="value1")

        mock_handler.handle_ui_operation.assert_called_once_with(
            "test_op", param1="value1"
        )

    @patch("src.minicrm.core.ttk_error_handler.get_ttk_error_handler")
    def test_show_validation_error_function(self, mock_get_handler):
        """测试显示验证错误函数"""
        mock_handler = Mock()
        mock_get_handler.return_value = mock_handler

        show_validation_error("field", "message", self.root)

        mock_handler.show_validation_error.assert_called_once_with(
            "field", "message", self.root
        )

    @patch("src.minicrm.core.ttk_error_handler.get_ttk_error_handler")
    def test_show_business_error_function(self, mock_get_handler):
        """测试显示业务错误函数"""
        mock_handler = Mock()
        mock_get_handler.return_value = mock_handler

        show_business_error("operation", "message", self.root)

        mock_handler.show_business_error.assert_called_once_with(
            "operation", "message", self.root
        )

    @patch("src.minicrm.core.ttk_error_handler.get_ttk_error_handler")
    def test_confirm_operation_function(self, mock_get_handler):
        """测试确认操作函数"""
        mock_handler = Mock()
        mock_handler.confirm_operation.return_value = True
        mock_get_handler.return_value = mock_handler

        result = confirm_operation("operation", "message", self.root)

        self.assertTrue(result)
        mock_handler.confirm_operation.assert_called_once_with(
            "operation", "message", self.root
        )


class TestErrorRecovery(unittest.TestCase):
    """测试错误恢复机制"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.error_handler = TTKErrorHandler(self.root)

    def tearDown(self):
        """测试清理"""
        if self.root:
            self.root.destroy()

    def test_recovery_callback_success(self):
        """测试恢复回调成功"""

        # 创建成功的恢复回调
        def successful_recovery(error_info):
            return True

        self.error_handler.register_recovery_callback(
            "test_component", successful_recovery
        )

        error_info = Mock()
        error_info.context = {"ui_component": "test_component"}

        result = self.error_handler._attempt_recovery(error_info)
        self.assertTrue(result)

    def test_recovery_callback_failure(self):
        """测试恢复回调失败"""

        # 创建失败的恢复回调
        def failing_recovery(error_info):
            raise Exception("Recovery failed")

        self.error_handler.register_recovery_callback(
            "test_component", failing_recovery
        )

        error_info = Mock()
        error_info.context = {"ui_component": "test_component"}

        result = self.error_handler._attempt_recovery(error_info)
        self.assertFalse(result)

    def test_validation_error_recovery(self):
        """测试验证错误恢复"""
        test_cases = [
            ({"ui_component": "layout"}, True),
            ({"ui_component": "style"}, True),
            ({"ui_component": "unknown"}, False),
        ]

        for context, expected_result in test_cases:
            error_info = Mock()
            error_info.error_type = ErrorType.VALIDATION_ERROR
            error_info.context = context

            result = self.error_handler._recover_validation_error(error_info)
            self.assertEqual(result, expected_result)

    def test_system_error_recovery(self):
        """测试系统错误恢复"""
        test_cases = [
            ({"ui_component": "widget"}, True),
            ({"ui_component": "event"}, True),
            ({"ui_component": "unknown"}, False),
        ]

        for context, expected_result in test_cases:
            error_info = Mock()
            error_info.error_type = ErrorType.SYSTEM_ERROR
            error_info.context = context

            result = self.error_handler._recover_system_error(error_info)
            self.assertEqual(result, expected_result)


class TestThreadSafety(unittest.TestCase):
    """测试线程安全性"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.error_handler = TTKErrorHandler(self.root)

    def tearDown(self):
        """测试清理"""
        if self.root:
            self.root.destroy()

    @patch("tkinter.messagebox.showerror")
    def test_show_error_dialog_from_main_thread(self, mock_messagebox):
        """测试从主线程显示错误对话框"""
        error_info = Mock()
        error_info.severity = ErrorSeverity.HIGH
        error_info.error_type = ErrorType.SYSTEM_ERROR
        error_info.message = "测试错误"
        error_info.context = {}

        self.error_handler._show_user_error_dialog(error_info)

        # 应该直接调用messagebox
        mock_messagebox.assert_called_once()

    def test_show_error_dialog_from_background_thread(self):
        """测试从后台线程显示错误对话框"""
        error_info = Mock()
        error_info.severity = ErrorSeverity.HIGH
        error_info.error_type = ErrorType.SYSTEM_ERROR
        error_info.message = "测试错误"
        error_info.context = {}

        # 模拟after方法
        self.error_handler._parent_window.after = Mock()

        def background_task():
            self.error_handler._show_user_error_dialog(error_info)

        thread = threading.Thread(target=background_task)
        thread.start()
        thread.join()

        # 应该调用after方法调度到主线程
        self.error_handler._parent_window.after.assert_called_once()


if __name__ == "__main__":
    unittest.main()
