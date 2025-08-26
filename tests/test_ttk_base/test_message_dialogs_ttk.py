"""测试TTK消息对话框

测试消息对话框类的功能，包括：
- MessageBoxTTK消息对话框
- ConfirmDialogTTK确认对话框
- InputDialogTTK输入对话框
- 各种便利函数
- 不同消息类型和样式

作者: MiniCRM开发团队
"""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from src.minicrm.ui.ttk_base.base_dialog import DialogResult
from src.minicrm.ui.ttk_base.message_dialogs_ttk import (
    ConfirmDialogTTK,
    InputDialogTTK,
    MessageBoxTTK,
    MessageType,
    confirm,
    get_input,
    get_multiline_input,
    get_password,
    show_error,
    show_info,
    show_message,
    show_success,
    show_warning,
)


class TestMessageBoxTTK(unittest.TestCase):
    """测试MessageBoxTTK类"""

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

    def test_info_message_box_creation(self):
        """测试信息消息框创建"""
        dialog = MessageBoxTTK(
            parent=self.root,
            title="信息",
            message="这是一条信息消息",
            message_type=MessageType.INFO,
        )

        # 验证基本属性
        self.assertEqual(dialog.message, "这是一条信息消息")
        self.assertEqual(dialog.message_type, MessageType.INFO)
        self.assertEqual(dialog.dialog_title, "信息")

        # 验证UI组件
        self.assertIsNotNone(dialog.icon_label)
        self.assertIsNotNone(dialog.message_label)

        # 验证按钮
        self.assertIn("确定", dialog.buttons)

        dialog.destroy()

    def test_warning_message_box_creation(self):
        """测试警告消息框创建"""
        dialog = MessageBoxTTK(
            parent=self.root,
            message="这是一条警告消息",
            message_type=MessageType.WARNING,
        )

        # 验证默认标题
        self.assertEqual(dialog.dialog_title, "警告")
        self.assertEqual(dialog.message_type, MessageType.WARNING)

        dialog.destroy()

    def test_error_message_box_creation(self):
        """测试错误消息框创建"""
        dialog = MessageBoxTTK(
            parent=self.root, message="这是一条错误消息", message_type=MessageType.ERROR
        )

        # 验证默认标题
        self.assertEqual(dialog.dialog_title, "错误")
        self.assertEqual(dialog.message_type, MessageType.ERROR)

        dialog.destroy()

    def test_question_message_box_creation(self):
        """测试问题消息框创建"""
        dialog = MessageBoxTTK(
            parent=self.root, message="这是一个问题", message_type=MessageType.QUESTION
        )

        # 验证默认标题
        self.assertEqual(dialog.dialog_title, "确认")
        self.assertEqual(dialog.message_type, MessageType.QUESTION)

        # 验证问题类型有是/否按钮
        self.assertIn("是", dialog.buttons)
        self.assertIn("否", dialog.buttons)

        dialog.destroy()

    def test_success_message_box_creation(self):
        """测试成功消息框创建"""
        dialog = MessageBoxTTK(
            parent=self.root, message="操作成功", message_type=MessageType.SUCCESS
        )

        # 验证默认标题
        self.assertEqual(dialog.dialog_title, "成功")
        self.assertEqual(dialog.message_type, MessageType.SUCCESS)

        dialog.destroy()

    def test_message_box_with_detail(self):
        """测试带详细信息的消息框"""
        detail_text = "这是详细的错误信息\n包含多行内容\n用于调试"

        dialog = MessageBoxTTK(
            parent=self.root,
            message="发生错误",
            message_type=MessageType.ERROR,
            detail=detail_text,
        )

        # 验证详细信息组件
        self.assertIsNotNone(dialog.detail_text)
        self.assertEqual(dialog.detail, detail_text)

        dialog.destroy()

    def test_custom_buttons_message_box(self):
        """测试自定义按钮消息框"""
        custom_buttons = ["重试", "忽略", "取消"]

        dialog = MessageBoxTTK(
            parent=self.root,
            message="操作失败",
            buttons=custom_buttons,
            default_button="重试",
        )

        # 验证自定义按钮
        for button_text in custom_buttons:
            self.assertIn(button_text, dialog.buttons)

        dialog.destroy()

    def test_message_box_button_clicks(self):
        """测试消息框按钮点击"""
        dialog = MessageBoxTTK(
            parent=self.root, message="测试消息", message_type=MessageType.QUESTION
        )

        # 测试点击"是"按钮
        dialog._on_button_click(DialogResult.YES)
        self.assertEqual(dialog.result, DialogResult.YES)

        dialog.destroy()


class TestConfirmDialogTTK(unittest.TestCase):
    """测试ConfirmDialogTTK类"""

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

    def test_confirm_dialog_creation(self):
        """测试确认对话框创建"""
        dialog = ConfirmDialogTTK(
            parent=self.root,
            title="确认操作",
            message="确定要删除这个文件吗？",
            confirm_text="删除",
            cancel_text="保留",
        )

        # 验证基本属性
        self.assertEqual(dialog.message, "确定要删除这个文件吗？")
        self.assertEqual(dialog.confirm_text, "删除")
        self.assertEqual(dialog.cancel_text, "保留")

        # 验证UI组件
        self.assertIsNotNone(dialog.icon_label)
        self.assertIsNotNone(dialog.message_label)

        # 验证按钮
        self.assertIn("删除", dialog.buttons)
        self.assertIn("保留", dialog.buttons)

        dialog.destroy()

    def test_confirm_dialog_default_values(self):
        """测试确认对话框默认值"""
        dialog = ConfirmDialogTTK(parent=self.root, message="确认操作？")

        # 验证默认值
        self.assertEqual(dialog.confirm_text, "确定")
        self.assertEqual(dialog.cancel_text, "取消")
        self.assertEqual(dialog.icon_type, MessageType.QUESTION)

        dialog.destroy()

    def test_confirm_dialog_confirm_action(self):
        """测试确认对话框确认操作"""
        dialog = ConfirmDialogTTK(parent=self.root)

        # 测试确认
        dialog._on_confirm()
        self.assertEqual(dialog.result, DialogResult.OK)
        self.assertTrue(dialog.return_value)

        dialog.destroy()

    def test_confirm_dialog_cancel_action(self):
        """测试确认对话框取消操作"""
        dialog = ConfirmDialogTTK(parent=self.root)

        # 测试取消
        dialog._on_cancel_confirm()
        self.assertEqual(dialog.result, DialogResult.CANCEL)
        self.assertFalse(dialog.return_value)

        dialog.destroy()


class TestInputDialogTTK(unittest.TestCase):
    """测试InputDialogTTK类"""

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

    def test_single_line_input_dialog_creation(self):
        """测试单行输入对话框创建"""
        dialog = InputDialogTTK(
            parent=self.root,
            title="输入姓名",
            message="请输入您的姓名:",
            initial_value="张三",
            multiline=False,
        )

        # 验证基本属性
        self.assertEqual(dialog.message, "请输入您的姓名:")
        self.assertEqual(dialog.initial_value, "张三")
        self.assertFalse(dialog.multiline)
        self.assertFalse(dialog.password)

        # 验证UI组件
        self.assertIsNotNone(dialog.message_label)
        self.assertIsNotNone(dialog.input_widget)

        # 验证初始值
        self.assertEqual(dialog.input_var.get(), "张三")

        dialog.destroy()

    def test_multiline_input_dialog_creation(self):
        """测试多行输入对话框创建"""
        initial_text = "第一行\n第二行\n第三行"

        dialog = InputDialogTTK(
            parent=self.root,
            title="输入描述",
            message="请输入详细描述:",
            initial_value=initial_text,
            multiline=True,
        )

        # 验证属性
        self.assertTrue(dialog.multiline)

        # 验证多行文本框
        self.assertIsInstance(dialog.input_widget, tk.Text)

        # 验证初始值
        content = dialog.get_input_value()
        self.assertEqual(content, initial_text)

        dialog.destroy()

    def test_password_input_dialog_creation(self):
        """测试密码输入对话框创建"""
        dialog = InputDialogTTK(
            parent=self.root, title="输入密码", message="请输入密码:", password=True
        )

        # 验证密码属性
        self.assertTrue(dialog.password)

        # 验证密码输入框（应该显示*）
        self.assertEqual(dialog.input_widget.cget("show"), "*")

        dialog.destroy()

    def test_input_dialog_validation(self):
        """测试输入对话框验证"""
        # 测试无验证函数的情况
        dialog = InputDialogTTK(parent=self.root)
        dialog.set_input_value("test input")

        result = dialog._validate_input()
        self.assertTrue(result)

        dialog.destroy()

        # 测试空输入
        dialog = InputDialogTTK(parent=self.root)
        dialog.set_input_value("")

        with patch.object(dialog, "show_error") as mock_error:
            result = dialog._validate_input()
            self.assertFalse(result)
            mock_error.assert_called()

        dialog.destroy()

        # 测试自定义验证函数
        def validate_email(value):
            return "@" in value and "." in value

        dialog = InputDialogTTK(parent=self.root, validation_func=validate_email)

        # 测试无效邮箱
        dialog.set_input_value("invalid_email")
        with patch.object(dialog, "show_error") as mock_error:
            result = dialog._validate_input()
            self.assertFalse(result)
            mock_error.assert_called()

        # 测试有效邮箱
        dialog.set_input_value("test@example.com")
        result = dialog._validate_input()
        self.assertTrue(result)

        dialog.destroy()

    def test_input_dialog_validation_exception(self):
        """测试输入对话框验证异常"""

        def failing_validator(value):
            raise ValueError("验证器异常")

        dialog = InputDialogTTK(parent=self.root, validation_func=failing_validator)
        dialog.set_input_value("test")

        with patch.object(dialog, "show_error") as mock_error:
            result = dialog._validate_input()
            self.assertFalse(result)
            mock_error.assert_called()

        dialog.destroy()

    def test_input_value_operations(self):
        """测试输入值操作"""
        # 测试单行输入
        dialog = InputDialogTTK(parent=self.root, multiline=False)

        dialog.set_input_value("测试文本")
        self.assertEqual(dialog.get_input_value(), "测试文本")

        dialog.destroy()

        # 测试多行输入
        dialog = InputDialogTTK(parent=self.root, multiline=True)

        multiline_text = "第一行\n第二行\n第三行"
        dialog.set_input_value(multiline_text)
        self.assertEqual(dialog.get_input_value(), multiline_text)

        dialog.destroy()

    def test_input_dialog_result_data(self):
        """测试输入对话框结果数据"""
        dialog = InputDialogTTK(parent=self.root)
        dialog.set_input_value("用户输入的内容")

        result_data = dialog._get_result_data()
        self.assertEqual(result_data, "用户输入的内容")

        dialog.destroy()


class TestMessageDialogConvenienceFunctions(unittest.TestCase):
    """测试消息对话框便利函数"""

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

    def test_show_message_function(self):
        """测试show_message函数"""
        with patch(
            "src.minicrm.ui.ttk_base.message_dialogs_ttk.MessageBoxTTK"
        ) as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.show_dialog.return_value = ("ok", "ok")
            mock_dialog_class.return_value = mock_dialog

            result = show_message(
                parent=self.root,
                title="测试消息",
                message="这是测试消息",
                message_type=MessageType.INFO,
            )

            # 验证对话框被创建
            mock_dialog_class.assert_called_once()

            # 验证返回结果
            self.assertEqual(result, "ok")

    def test_show_info_function(self):
        """测试show_info函数"""
        with patch(
            "src.minicrm.ui.ttk_base.message_dialogs_ttk.show_message"
        ) as mock_show_message:
            mock_show_message.return_value = "ok"

            result = show_info(self.root, "信息消息", "信息标题")

            mock_show_message.assert_called_once_with(
                self.root, "信息标题", "信息消息", MessageType.INFO
            )
            self.assertEqual(result, "ok")

    def test_show_warning_function(self):
        """测试show_warning函数"""
        with patch(
            "src.minicrm.ui.ttk_base.message_dialogs_ttk.show_message"
        ) as mock_show_message:
            mock_show_message.return_value = "ok"

            result = show_warning(self.root, "警告消息", "警告标题")

            mock_show_message.assert_called_once_with(
                self.root, "警告标题", "警告消息", MessageType.WARNING
            )
            self.assertEqual(result, "ok")

    def test_show_error_function(self):
        """测试show_error函数"""
        with patch(
            "src.minicrm.ui.ttk_base.message_dialogs_ttk.show_message"
        ) as mock_show_message:
            mock_show_message.return_value = "ok"

            result = show_error(self.root, "错误消息", "错误标题")

            mock_show_message.assert_called_once_with(
                self.root, "错误标题", "错误消息", MessageType.ERROR
            )
            self.assertEqual(result, "ok")

    def test_show_success_function(self):
        """测试show_success函数"""
        with patch(
            "src.minicrm.ui.ttk_base.message_dialogs_ttk.show_message"
        ) as mock_show_message:
            mock_show_message.return_value = "ok"

            result = show_success(self.root, "成功消息", "成功标题")

            mock_show_message.assert_called_once_with(
                self.root, "成功标题", "成功消息", MessageType.SUCCESS
            )
            self.assertEqual(result, "ok")

    def test_confirm_function(self):
        """测试confirm函数"""
        with patch(
            "src.minicrm.ui.ttk_base.message_dialogs_ttk.ConfirmDialogTTK"
        ) as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.show_dialog.return_value = ("ok", True)
            mock_dialog_class.return_value = mock_dialog

            result = confirm(
                parent=self.root,
                message="确认操作？",
                title="确认",
                confirm_text="是",
                cancel_text="否",
            )

            # 验证对话框被创建
            mock_dialog_class.assert_called_once()

            # 验证返回结果
            self.assertTrue(result)

    def test_confirm_function_cancelled(self):
        """测试confirm函数取消情况"""
        with patch(
            "src.minicrm.ui.ttk_base.message_dialogs_ttk.ConfirmDialogTTK"
        ) as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.show_dialog.return_value = ("cancel", False)
            mock_dialog_class.return_value = mock_dialog

            result = confirm(self.root, "确认操作？")

            # 验证返回结果
            self.assertFalse(result)

    def test_get_input_function(self):
        """测试get_input函数"""
        with patch(
            "src.minicrm.ui.ttk_base.message_dialogs_ttk.InputDialogTTK"
        ) as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.show_dialog.return_value = ("ok", "用户输入")
            mock_dialog_class.return_value = mock_dialog

            result = get_input(
                parent=self.root,
                title="输入",
                message="请输入:",
                initial_value="默认值",
            )

            # 验证对话框被创建
            mock_dialog_class.assert_called_once()

            # 验证返回结果
            self.assertEqual(result, "用户输入")

    def test_get_input_function_cancelled(self):
        """测试get_input函数取消情况"""
        with patch(
            "src.minicrm.ui.ttk_base.message_dialogs_ttk.InputDialogTTK"
        ) as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.show_dialog.return_value = ("cancel", None)
            mock_dialog_class.return_value = mock_dialog

            result = get_input(self.root, "输入", "请输入:")

            # 验证返回结果
            self.assertIsNone(result)

    def test_get_password_function(self):
        """测试get_password函数"""
        with patch(
            "src.minicrm.ui.ttk_base.message_dialogs_ttk.get_input"
        ) as mock_get_input:
            mock_get_input.return_value = "secret_password"

            result = get_password(
                parent=self.root, title="输入密码", message="请输入密码:"
            )

            # 验证调用参数
            mock_get_input.assert_called_once_with(
                parent=self.root,
                title="输入密码",
                message="请输入密码:",
                password=True,
                validation_func=None,
            )

            # 验证返回结果
            self.assertEqual(result, "secret_password")

    def test_get_multiline_input_function(self):
        """测试get_multiline_input函数"""
        with patch(
            "src.minicrm.ui.ttk_base.message_dialogs_ttk.get_input"
        ) as mock_get_input:
            mock_get_input.return_value = "多行\n输入\n内容"

            result = get_multiline_input(
                parent=self.root,
                title="多行输入",
                message="请输入:",
                initial_value="初始内容",
            )

            # 验证调用参数
            mock_get_input.assert_called_once_with(
                parent=self.root,
                title="多行输入",
                message="请输入:",
                initial_value="初始内容",
                multiline=True,
                validation_func=None,
            )

            # 验证返回结果
            self.assertEqual(result, "多行\n输入\n内容")


if __name__ == "__main__":
    unittest.main()
