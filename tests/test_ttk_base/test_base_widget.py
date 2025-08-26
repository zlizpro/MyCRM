"""BaseWidget类单元测试

测试TTK基础组件类的功能，包括：
- 组件初始化和生命周期管理
- 事件处理机制
- 数据绑定功能
- 子组件管理
- 可见性和启用状态管理
- 数据验证和清理

作者: MiniCRM开发团队
"""

import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import Mock

from src.minicrm.ui.ttk_base.base_widget import (
    BaseWidget,
    DataBindingMixin,
    ResponsiveMixin,
    ValidationMixin,
)


class TestWidget(BaseWidget):
    """测试用的具体组件实现"""

    def _setup_ui(self):
        """设置测试UI"""
        self.test_label = ttk.Label(self, text="测试标签")
        self.test_label.pack()

        self.test_entry = ttk.Entry(self)
        self.test_entry.pack()

        self.add_child_widget(self.test_label)
        self.add_child_widget(self.test_entry)

    def _bind_events(self):
        """绑定测试事件"""
        self.test_entry.bind("<KeyRelease>", self._on_entry_change)

    def _on_entry_change(self, event):
        """入口变化事件处理"""
        self.trigger_event("entry_changed", self.test_entry.get())


class TestBaseWidget(unittest.TestCase):
    """BaseWidget类测试"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口

        self.widget = TestWidget(self.root)

    def tearDown(self):
        """测试清理"""
        try:
            if self.widget:
                self.widget.cleanup()
                self.widget.destroy()
        except tk.TclError:
            pass

        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def test_widget_initialization(self):
        """测试组件初始化"""
        # 验证初始化状态
        self.assertTrue(self.widget._initialized)
        self.assertTrue(self.widget._visible)
        self.assertTrue(self.widget._enabled)
        self.assertEqual(len(self.widget._data), 0)

        # 验证子组件创建
        self.assertIsNotNone(self.widget.test_label)
        self.assertIsNotNone(self.widget.test_entry)

        # 验证子组件管理
        child_widgets = self.widget.get_child_widgets()
        self.assertEqual(len(child_widgets), 2)
        self.assertIn(self.widget.test_label, child_widgets)
        self.assertIn(self.widget.test_entry, child_widgets)

    def test_event_handler_management(self):
        """测试事件处理器管理"""
        # 添加事件处理器
        handler1 = Mock()
        handler2 = Mock()

        self.widget.add_event_handler("test_event", handler1)
        self.widget.add_event_handler("test_event", handler2)

        # 触发事件
        self.widget.trigger_event("test_event", "arg1", key="value")

        # 验证处理器被调用
        handler1.assert_called_once_with("arg1", key="value")
        handler2.assert_called_once_with("arg1", key="value")

        # 移除事件处理器
        self.widget.remove_event_handler("test_event", handler1)

        # 再次触发事件
        handler1.reset_mock()
        handler2.reset_mock()
        self.widget.trigger_event("test_event", "arg2")

        # 验证只有handler2被调用
        handler1.assert_not_called()
        handler2.assert_called_once_with("arg2")

    def test_child_widget_management(self):
        """测试子组件管理"""
        # 创建新的子组件
        new_button = ttk.Button(self.widget, text="新按钮")

        # 添加子组件
        self.widget.add_child_widget(new_button)

        # 验证子组件添加
        child_widgets = self.widget.get_child_widgets()
        self.assertIn(new_button, child_widgets)
        self.assertEqual(len(child_widgets), 3)

        # 移除子组件
        self.widget.remove_child_widget(new_button)

        # 验证子组件移除
        child_widgets = self.widget.get_child_widgets()
        self.assertNotIn(new_button, child_widgets)
        self.assertEqual(len(child_widgets), 2)

    def test_data_management(self):
        """测试数据管理"""
        # 设置数据
        self.widget.set_data("name", "测试名称")
        self.widget.set_data("age", 25)

        # 验证数据获取
        self.assertEqual(self.widget.get_data("name"), "测试名称")
        self.assertEqual(self.widget.get_data("age"), 25)
        self.assertEqual(self.widget.get_data("nonexistent", "默认值"), "默认值")

        # 验证所有数据获取
        all_data = self.widget.get_all_data()
        self.assertEqual(all_data["name"], "测试名称")
        self.assertEqual(all_data["age"], 25)
        self.assertEqual(len(all_data), 2)

        # 清空数据
        self.widget.clear_data()
        self.assertEqual(len(self.widget.get_all_data()), 0)

    def test_data_change_event(self):
        """测试数据变化事件"""
        # 添加数据变化事件处理器
        data_changed_handler = Mock()
        self.widget.add_event_handler("data_changed", data_changed_handler)

        # 设置数据
        self.widget.set_data("test_key", "test_value")

        # 验证事件被触发
        data_changed_handler.assert_called_once_with("test_key", None, "test_value")

        # 更新数据
        data_changed_handler.reset_mock()
        self.widget.set_data("test_key", "new_value")

        # 验证事件再次被触发
        data_changed_handler.assert_called_once_with(
            "test_key", "test_value", "new_value"
        )

    def test_data_binding(self):
        """测试数据绑定"""
        # 绑定数据到Entry组件
        self.widget.bind_data("user_name", self.widget.test_entry)

        # 设置数据
        self.widget.set_data("user_name", "张三")

        # 同步数据到组件
        self.widget.sync_data_to_widgets()

        # 验证组件值更新
        self.assertEqual(self.widget.test_entry.get(), "张三")

        # 修改组件值
        self.widget.test_entry.delete(0, tk.END)
        self.widget.test_entry.insert(0, "李四")

        # 同步组件值到数据
        self.widget.sync_widgets_to_data()

        # 验证数据更新
        self.assertEqual(self.widget.get_data("user_name"), "李四")

    def test_custom_data_binding(self):
        """测试自定义数据绑定"""

        # 自定义getter和setter
        def custom_getter(widget):
            return f"前缀_{widget.get()}"

        def custom_setter(widget, value):
            widget.delete(0, tk.END)
            widget.insert(0, value.replace("前缀_", ""))

        # 绑定数据
        self.widget.bind_data(
            "custom_field",
            self.widget.test_entry,
            getter=custom_getter,
            setter=custom_setter,
        )

        # 设置数据
        self.widget.set_data("custom_field", "前缀_测试值")
        self.widget.sync_data_to_widgets()

        # 验证自定义setter工作
        self.assertEqual(self.widget.test_entry.get(), "测试值")

        # 同步回数据
        self.widget.sync_widgets_to_data()

        # 验证自定义getter工作
        self.assertEqual(self.widget.get_data("custom_field"), "前缀_测试值")

    def test_visibility_management(self):
        """测试可见性管理"""
        # 初始状态应该可见
        self.assertTrue(self.widget.is_visible())

        # 隐藏组件
        self.widget.set_visible(False)
        self.assertFalse(self.widget.is_visible())

        # 显示组件
        self.widget.set_visible(True)
        self.assertTrue(self.widget.is_visible())

    def test_enabled_state_management(self):
        """测试启用状态管理"""
        # 初始状态应该启用
        self.assertTrue(self.widget.is_enabled())

        # 禁用组件
        self.widget.set_enabled(False)
        self.assertFalse(self.widget.is_enabled())

        # 启用组件
        self.widget.set_enabled(True)
        self.assertTrue(self.widget.is_enabled())

    def test_visibility_change_event(self):
        """测试可见性变化事件"""
        # 添加可见性变化事件处理器
        visibility_handler = Mock()
        self.widget.add_event_handler("visibility_changed", visibility_handler)

        # 改变可见性
        self.widget.set_visible(False)
        visibility_handler.assert_called_once_with(False)

        visibility_handler.reset_mock()
        self.widget.set_visible(True)
        visibility_handler.assert_called_once_with(True)

    def test_enabled_change_event(self):
        """测试启用状态变化事件"""
        # 添加启用状态变化事件处理器
        enabled_handler = Mock()
        self.widget.add_event_handler("enabled_changed", enabled_handler)

        # 改变启用状态
        self.widget.set_enabled(False)
        enabled_handler.assert_called_once_with(False)

        enabled_handler.reset_mock()
        self.widget.set_enabled(True)
        enabled_handler.assert_called_once_with(True)

    def test_refresh_method(self):
        """测试刷新方法"""
        # 添加刷新事件处理器
        refresh_handler = Mock()
        self.widget.add_event_handler("refreshed", refresh_handler)

        # 设置数据并绑定
        self.widget.bind_data("test_field", self.widget.test_entry)
        self.widget.set_data("test_field", "刷新测试")

        # 执行刷新
        self.widget.refresh()

        # 验证数据同步和事件触发
        self.assertEqual(self.widget.test_entry.get(), "刷新测试")
        refresh_handler.assert_called_once()

    def test_validate_method(self):
        """测试验证方法"""
        # 基础组件的验证方法应该返回True
        is_valid, errors = self.widget.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_cleanup_method(self):
        """测试清理方法"""
        # 添加一些数据和事件处理器
        self.widget.set_data("test_key", "test_value")
        handler = Mock()
        self.widget.add_event_handler("test_event", handler)

        # 执行清理
        self.widget.cleanup()

        # 验证清理结果
        self.assertEqual(len(self.widget._event_handlers), 0)
        self.assertEqual(len(self.widget._child_widgets), 0)
        self.assertEqual(len(self.widget._data_bindings), 0)
        self.assertEqual(len(self.widget._data), 0)

    def test_default_getter_setter(self):
        """测试默认的getter和setter"""
        # 测试Entry组件
        entry = ttk.Entry(self.widget)
        entry.insert(0, "测试值")

        # 测试默认getter
        value = self.widget._default_getter(entry)
        self.assertEqual(value, "测试值")

        # 测试默认setter
        self.widget._default_setter(entry, "新值")
        self.assertEqual(entry.get(), "新值")

        # 测试Label组件
        label = ttk.Label(self.widget, text="标签文本")

        # 测试默认setter for Label
        self.widget._default_setter(label, "新标签文本")
        self.assertEqual(label.cget("text"), "新标签文本")


class TestDataBindingMixin(unittest.TestCase):
    """DataBindingMixin测试"""

    def setUp(self):
        """测试准备"""
        self.mixin = DataBindingMixin()

    def test_validator_management(self):
        """测试验证器管理"""
        # 设置验证器
        validator = lambda x: len(x) > 0
        self.mixin.set_binding_validator("name", validator)

        # 测试验证
        self.assertTrue(self.mixin.validate_binding_data("name", "有效值"))
        self.assertFalse(self.mixin.validate_binding_data("name", ""))

    def test_formatter_management(self):
        """测试格式化器管理"""
        # 设置格式化器
        formatter = lambda x: f"格式化_{x}"
        self.mixin.set_binding_formatter("display", formatter)

        # 测试格式化
        result = self.mixin.format_binding_data("display", "测试")
        self.assertEqual(result, "格式化_测试")

        # 测试无格式化器的情况
        result = self.mixin.format_binding_data("other", "测试")
        self.assertEqual(result, "测试")

    def test_auto_sync_setting(self):
        """测试自动同步设置"""
        # 默认应该是False
        self.assertFalse(self.mixin._auto_sync)

        # 启用自动同步
        self.mixin.enable_auto_sync(True)
        self.assertTrue(self.mixin._auto_sync)

        # 禁用自动同步
        self.mixin.enable_auto_sync(False)
        self.assertFalse(self.mixin._auto_sync)


class TestResponsiveMixin(unittest.TestCase):
    """ResponsiveMixin测试"""

    def setUp(self):
        """测试准备"""
        self.mixin = ResponsiveMixin()

    def test_breakpoint_management(self):
        """测试断点管理"""
        # 添加断点
        layout_func_1 = Mock()
        layout_func_2 = Mock()

        self.mixin.add_breakpoint(768, layout_func_1)
        self.mixin.add_breakpoint(1024, layout_func_2)

        # 测试小屏幕
        self.mixin.handle_resize(600, 400)
        layout_func_1.assert_not_called()
        layout_func_2.assert_not_called()

        # 测试中等屏幕
        self.mixin.handle_resize(800, 600)
        layout_func_1.assert_called_once_with(800, 600)
        layout_func_2.assert_not_called()

        # 测试大屏幕
        layout_func_1.reset_mock()
        self.mixin.handle_resize(1200, 800)
        layout_func_1.assert_not_called()
        layout_func_2.assert_called_once_with(1200, 800)

    def test_breakpoint_change_detection(self):
        """测试断点变化检测"""
        layout_func = Mock()
        self.mixin.add_breakpoint(768, layout_func)

        # 第一次调用应该触发布局
        self.mixin.handle_resize(800, 600)
        layout_func.assert_called_once_with(800, 600)

        # 相同断点的后续调用不应该触发布局
        layout_func.reset_mock()
        self.mixin.handle_resize(850, 650)
        layout_func.assert_not_called()


class TestValidationMixin(unittest.TestCase):
    """ValidationMixin测试"""

    def setUp(self):
        """测试准备"""
        self.mixin = ValidationMixin()

    def test_validator_addition(self):
        """测试验证器添加"""
        # 添加验证器
        validator1 = lambda x: len(x) > 0
        validator2 = lambda x: len(x) < 10

        self.mixin.add_validator("name", validator1, "名称不能为空")
        self.mixin.add_validator("name", validator2, "名称不能超过10个字符")

        # 验证器应该被添加
        self.assertIn("name", self.mixin._validators)
        self.assertEqual(len(self.mixin._validators["name"]), 2)

    def test_field_validation(self):
        """测试字段验证"""
        # 添加验证器
        self.mixin.add_validator("age", lambda x: x >= 0, "年龄不能为负数")
        self.mixin.add_validator("age", lambda x: x <= 120, "年龄不能超过120")

        # 测试有效值
        is_valid, errors = self.mixin.validate_field("age", 25)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # 测试无效值
        is_valid, errors = self.mixin.validate_field("age", -5)
        self.assertFalse(is_valid)
        self.assertIn("年龄不能为负数", errors)

        # 测试多个验证失败
        is_valid, errors = self.mixin.validate_field("age", 150)
        self.assertFalse(is_valid)
        self.assertIn("年龄不能超过120", errors)

    def test_all_fields_validation(self):
        """测试所有字段验证"""
        # 添加验证器
        self.mixin.add_validator("name", lambda x: len(x) > 0, "名称不能为空")
        self.mixin.add_validator("age", lambda x: x >= 0, "年龄不能为负数")

        # 测试有效数据
        data = {"name": "张三", "age": 25}
        is_valid, field_errors = self.mixin.validate_all_fields(data)
        self.assertTrue(is_valid)
        self.assertEqual(len(field_errors), 0)

        # 测试无效数据
        data = {"name": "", "age": -5}
        is_valid, field_errors = self.mixin.validate_all_fields(data)
        self.assertFalse(is_valid)
        self.assertIn("name", field_errors)
        self.assertIn("age", field_errors)

    def test_nonexistent_field_validation(self):
        """测试不存在字段的验证"""
        # 验证不存在的字段应该返回True
        is_valid, errors = self.mixin.validate_field("nonexistent", "value")
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)


class TestBaseWidgetIntegration(unittest.TestCase):
    """BaseWidget集成测试"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """测试清理"""
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def test_complete_widget_workflow(self):
        """测试完整的组件工作流程"""
        # 创建测试组件
        widget = TestWidget(self.root)

        try:
            # 验证初始化
            self.assertTrue(widget._initialized)

            # 设置数据
            widget.set_data("user_name", "测试用户")
            widget.set_data("user_age", 30)

            # 绑定数据
            widget.bind_data("user_name", widget.test_entry)

            # 同步数据
            widget.sync_data_to_widgets()
            self.assertEqual(widget.test_entry.get(), "测试用户")

            # 添加事件处理器
            entry_changed_handler = Mock()
            widget.add_event_handler("entry_changed", entry_changed_handler)

            # 模拟用户输入
            widget.test_entry.delete(0, tk.END)
            widget.test_entry.insert(0, "新用户名")
            widget.test_entry.event_generate("<KeyRelease>")

            # 验证事件触发
            entry_changed_handler.assert_called_with("新用户名")

            # 同步回数据
            widget.sync_widgets_to_data()
            self.assertEqual(widget.get_data("user_name"), "新用户名")

            # 测试可见性和启用状态
            widget.set_visible(False)
            self.assertFalse(widget.is_visible())

            widget.set_enabled(False)
            self.assertFalse(widget.is_enabled())

            # 刷新组件
            widget.refresh()

            # 验证数据
            is_valid, errors = widget.validate()
            self.assertTrue(is_valid)

        finally:
            widget.cleanup()
            widget.destroy()


if __name__ == "__main__":
    unittest.main()
