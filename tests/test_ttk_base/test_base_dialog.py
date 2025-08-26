"""测试TTK基础对话框

测试BaseDialogTTK类的基础功能，包括：
- 对话框创建和初始化
- 事件处理机制
- 数据管理功能
- 按钮管理
- 模态显示功能

作者: MiniCRM开发团队
"""

import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import Mock, patch

from src.minicrm.ui.ttk_base.base_dialog import BaseDialogTTK, DialogResult


class TestDialogTTK(BaseDialogTTK):
    """测试用的对话框类"""

    def _setup_content(self):
        """设置测试内容"""
        self.test_label = ttk.Label(self.content_frame, text="测试对话框")
        self.test_label.pack()


class TestBaseDialogTTK(unittest.TestCase):
    """测试BaseDialogTTK类"""

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

    def test_dialog_creation(self):
        """测试对话框创建"""
        dialog = TestDialogTTK(parent=self.root, title="测试对话框", size=(300, 200))

        # 验证基本属性
        self.assertEqual(dialog.dialog_title, "测试对话框")
        self.assertEqual(dialog.dialog_size, (300, 200))
        self.assertTrue(dialog.is_modal)
        self.assertIsNotNone(dialog.main_frame)
        self.assertIsNotNone(dialog.content_frame)
        self.assertIsNotNone(dialog.button_frame)

        dialog.destroy()

    def test_dialog_properties(self):
        """测试对话框属性设置"""
        dialog = TestDialogTTK(
            parent=self.root,
            title="属性测试",
            size=(400, 300),
            min_size=(200, 150),
            resizable=(False, True),
            modal=False,
        )

        # 验证属性
        self.assertEqual(dialog.dialog_title, "属性测试")
        self.assertEqual(dialog.dialog_size, (400, 300))
        self.assertEqual(dialog.min_size, (200, 150))
        self.assertEqual(dialog.resizable_config, (False, True))
        self.assertFalse(dialog.is_modal)

        dialog.destroy()

    def test_button_management(self):
        """测试按钮管理"""
        dialog = TestDialogTTK(parent=self.root)

        # 测试添加按钮
        callback = Mock()
        button = dialog.add_button("测试按钮", callback, "test_result")

        self.assertIn("测试按钮", dialog.buttons)
        self.assertEqual(dialog.buttons["测试按钮"], button)

        # 测试按钮点击
        button.invoke()
        callback.assert_called_once()

        # 测试移除按钮
        dialog.remove_button("测试按钮")
        self.assertNotIn("测试按钮", dialog.buttons)

        dialog.destroy()

    def test_button_state_management(self):
        """测试按钮状态管理"""
        dialog = TestDialogTTK(parent=self.root)

        # 添加按钮
        dialog.add_button("状态测试", lambda: None)

        # 测试启用/禁用
        dialog.set_button_enabled("状态测试", False)
        button = dialog.get_button("状态测试")
        self.assertEqual(str(button.cget("state")), "disabled")

        dialog.set_button_enabled("状态测试", True)
        self.assertEqual(str(button.cget("state")), "normal")

        # 测试文本更改
        dialog.set_button_text("状态测试", "新文本")
        self.assertIn("新文本", dialog.buttons)
        self.assertNotIn("状态测试", dialog.buttons)

        dialog.destroy()

    def test_data_management(self):
        """测试数据管理"""
        dialog = TestDialogTTK(parent=self.root)

        # 测试设置和获取数据
        dialog.set_data("key1", "value1")
        dialog.set_data("key2", 123)

        self.assertEqual(dialog.get_data("key1"), "value1")
        self.assertEqual(dialog.get_data("key2"), 123)
        self.assertIsNone(dialog.get_data("nonexistent"))
        self.assertEqual(dialog.get_data("nonexistent", "default"), "default")

        # 测试获取所有数据
        all_data = dialog.get_all_data()
        self.assertEqual(all_data["key1"], "value1")
        self.assertEqual(all_data["key2"], 123)

        # 测试清空数据
        dialog.clear_data()
        self.assertEqual(len(dialog.get_all_data()), 0)

        dialog.destroy()

    def test_event_handling(self):
        """测试事件处理"""
        dialog = TestDialogTTK(parent=self.root)

        # 测试添加事件处理器
        handler1 = Mock()
        handler2 = Mock()

        dialog.add_event_handler("test_event", handler1)
        dialog.add_event_handler("test_event", handler2)

        # 测试触发事件
        dialog.trigger_event("test_event", "arg1", key="value")

        handler1.assert_called_once_with("arg1", key="value")
        handler2.assert_called_once_with("arg1", key="value")

        # 测试移除事件处理器
        dialog.remove_event_handler("test_event", handler1)
        dialog.trigger_event("test_event")

        # handler1不应该被再次调用
        self.assertEqual(handler1.call_count, 1)
        self.assertEqual(handler2.call_count, 2)

        dialog.destroy()

    def test_data_change_events(self):
        """测试数据变化事件"""
        dialog = TestDialogTTK(parent=self.root)

        # 添加数据变化事件处理器
        change_handler = Mock()
        dialog.add_event_handler("data_changed", change_handler)

        # 设置数据应该触发事件
        dialog.set_data("test_key", "test_value")

        change_handler.assert_called_once_with("test_key", None, "test_value")

        # 更新数据应该触发事件
        change_handler.reset_mock()
        dialog.set_data("test_key", "new_value")

        change_handler.assert_called_once_with("test_key", "test_value", "new_value")

        dialog.destroy()

    def test_dialog_result_handling(self):
        """测试对话框结果处理"""
        dialog = TestDialogTTK(parent=self.root)

        # 测试确定结果
        dialog._on_ok()
        self.assertEqual(dialog.result, DialogResult.OK)

        # 重新创建对话框测试取消结果
        dialog = TestDialogTTK(parent=self.root)
        dialog._on_cancel()
        self.assertEqual(dialog.result, DialogResult.CANCEL)

        dialog.destroy()

    def test_validation(self):
        """测试输入验证"""

        class ValidatingDialog(BaseDialogTTK):
            def _setup_content(self):
                pass

            def _validate_input(self):
                return self.get_data("valid", True)

        dialog = ValidatingDialog(parent=self.root)

        # 测试验证通过
        dialog.set_data("valid", True)
        self.assertTrue(dialog._validate_input())

        # 测试验证失败
        dialog.set_data("valid", False)
        self.assertFalse(dialog._validate_input())

        dialog.destroy()

    def test_close_dialog(self):
        """测试对话框关闭"""
        dialog = TestDialogTTK(parent=self.root)

        # 测试关闭前事件
        before_close_handler = Mock()
        dialog.add_event_handler("before_close", before_close_handler)

        # 测试关闭事件
        closing_handler = Mock()
        dialog.add_event_handler("closing", closing_handler)

        # 关闭对话框
        dialog.close_dialog(DialogResult.OK, "test_result")

        # 验证事件被触发
        before_close_handler.assert_called_once()
        closing_handler.assert_called_once()

        # 验证结果
        self.assertEqual(dialog.result, DialogResult.OK)
        self.assertEqual(dialog.return_value, "test_result")

    def test_error_handling_in_events(self):
        """测试事件处理中的错误处理"""
        dialog = TestDialogTTK(parent=self.root)

        # 添加会抛出异常的事件处理器
        def error_handler():
            raise ValueError("测试异常")

        normal_handler = Mock()

        dialog.add_event_handler("test_event", error_handler)
        dialog.add_event_handler("test_event", normal_handler)

        # 触发事件，应该不会因为异常而中断
        with patch.object(dialog.logger, "error") as mock_logger:
            dialog.trigger_event("test_event")

            # 验证异常被记录
            mock_logger.assert_called()

            # 验证正常处理器仍然被调用
            normal_handler.assert_called_once()

        dialog.destroy()

    def test_dialog_cleanup(self):
        """测试对话框清理"""
        dialog = TestDialogTTK(parent=self.root)

        # 添加一些数据和事件处理器
        dialog.set_data("test", "value")
        dialog.add_event_handler("test", Mock())
        dialog.add_button("test", Mock())

        # 执行清理
        dialog._cleanup()

        # 验证清理结果
        self.assertEqual(len(dialog._event_handlers), 0)
        self.assertEqual(len(dialog._data), 0)

        dialog.destroy()


if __name__ == "__main__":
    unittest.main()
