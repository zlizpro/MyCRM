"""TTK表单数据绑定系统测试

测试表单数据绑定系统的功能，包括：
- DataBinding双向数据绑定测试
- 数据格式化和解析测试
- 数据验证测试
- 变化监听测试

作者: MiniCRM开发团队
"""

from datetime import date, datetime
import tkinter as tk
from tkinter import ttk
import unittest

from src.minicrm.ui.ttk_base.form_data_binding import (
    CommonFormatters,
    CommonParsers,
    CommonValidators,
    DataBinding,
)


class TestDataBinding(unittest.TestCase):
    """测试数据绑定类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口
        self.binding = DataBinding()

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_basic_data_operations(self):
        """测试基本数据操作"""
        # 测试设置和获取数据
        self.binding.set_data("name", "张三")
        self.assertEqual(self.binding.get_data("name"), "张三")

        # 测试默认值
        self.assertEqual(self.binding.get_data("age", 0), 0)

        # 测试获取所有数据
        self.binding.set_data("age", 25)
        all_data = self.binding.get_all_data()
        self.assertEqual(all_data["name"], "张三")
        self.assertEqual(all_data["age"], 25)

    def test_set_all_data(self):
        """测试批量设置数据"""
        data = {"name": "李四", "age": 30, "email": "lisi@example.com"}
        self.binding.set_all_data(data)

        self.assertEqual(self.binding.get_data("name"), "李四")
        self.assertEqual(self.binding.get_data("age"), 30)
        self.assertEqual(self.binding.get_data("email"), "lisi@example.com")

    def test_clear_data(self):
        """测试清空数据"""
        self.binding.set_data("name", "王五")
        self.binding.set_data("age", 35)

        self.binding.clear_data()

        self.assertIsNone(self.binding.get_data("name"))
        self.assertIsNone(self.binding.get_data("age"))

    def test_entry_binding(self):
        """测试Entry组件绑定"""
        entry = ttk.Entry(self.root)

        # 绑定数据
        self.binding.bind("username", entry)

        # 测试数据到组件同步
        self.binding.set_data("username", "testuser")
        self.assertEqual(entry.get(), "testuser")

        # 测试组件到数据同步
        entry.delete(0, tk.END)
        entry.insert(0, "newuser")
        self.binding.sync_widget_to_data("username")
        self.assertEqual(self.binding.get_data("username"), "newuser")

    def test_text_binding(self):
        """测试Text组件绑定"""
        text = tk.Text(self.root)

        # 绑定数据
        self.binding.bind("description", text)

        # 测试数据到组件同步
        self.binding.set_data("description", "这是一段描述")
        self.assertEqual(text.get("1.0", tk.END).strip(), "这是一段描述")

        # 测试组件到数据同步
        text.delete("1.0", tk.END)
        text.insert("1.0", "新的描述")
        self.binding.sync_widget_to_data("description")
        self.assertEqual(self.binding.get_data("description"), "新的描述")

    def test_combobox_binding(self):
        """测试Combobox组件绑定"""
        combobox = ttk.Combobox(self.root, values=["选项1", "选项2", "选项3"])

        # 绑定数据
        self.binding.bind("choice", combobox)

        # 测试数据到组件同步
        self.binding.set_data("choice", "选项2")
        self.assertEqual(combobox.get(), "选项2")

        # 测试组件到数据同步
        combobox.set("选项3")
        self.binding.sync_widget_to_data("choice")
        self.assertEqual(self.binding.get_data("choice"), "选项3")

    def test_data_listeners(self):
        """测试数据变化监听器"""
        listener_calls = []

        def test_listener(key, old_value, new_value):
            listener_calls.append((key, old_value, new_value))

        # 添加监听器
        self.binding.add_listener("test_key", test_listener)

        # 设置数据，应该触发监听器
        self.binding.set_data("test_key", "value1")
        self.assertEqual(len(listener_calls), 1)
        self.assertEqual(listener_calls[0], ("test_key", None, "value1"))

        # 修改数据，应该再次触发监听器
        self.binding.set_data("test_key", "value2")
        self.assertEqual(len(listener_calls), 2)
        self.assertEqual(listener_calls[1], ("test_key", "value1", "value2"))

        # 移除监听器
        self.binding.remove_listener("test_key", test_listener)
        self.binding.set_data("test_key", "value3")
        self.assertEqual(len(listener_calls), 2)  # 不应该再触发

    def test_data_validation(self):
        """测试数据验证"""
        # 设置验证器
        self.binding.set_validator("age", lambda x: isinstance(x, int) and x >= 0)

        # 有效数据应该通过
        self.binding.set_data("age", 25)
        self.assertEqual(self.binding.get_data("age"), 25)

        # 无效数据应该抛出异常
        with self.assertRaises(ValueError):
            self.binding.set_data("age", -5)

        with self.assertRaises(ValueError):
            self.binding.set_data("age", "invalid")

    def test_validate_all(self):
        """测试批量验证"""
        # 设置验证器
        self.binding.set_validator("name", lambda x: x and len(x) > 0)
        self.binding.set_validator("age", lambda x: isinstance(x, int) and x >= 0)

        # 设置有效数据
        self.binding._data = {"name": "张三", "age": 25}
        is_valid, errors = self.binding.validate_all()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # 设置无效数据
        self.binding._data = {"name": "", "age": -5}
        is_valid, errors = self.binding.validate_all()
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 2)


class TestCommonFormatters(unittest.TestCase):
    """测试常用格式化器"""

    def test_date_formatter(self):
        """测试日期格式化器"""
        formatter = CommonFormatters.date_formatter("%Y-%m-%d")

        test_date = date(2023, 12, 25)
        self.assertEqual(formatter(test_date), "2023-12-25")

        test_datetime = datetime(2023, 12, 25, 10, 30, 0)
        self.assertEqual(formatter(test_datetime), "2023-12-25")

        self.assertEqual(formatter(None), "")

    def test_number_formatter(self):
        """测试数字格式化器"""
        formatter = CommonFormatters.number_formatter(2)

        self.assertEqual(formatter(123.456), "123.46")
        self.assertEqual(formatter(100), "100.00")
        self.assertEqual(formatter(None), "")
        self.assertEqual(formatter("invalid"), "invalid")

    def test_currency_formatter(self):
        """测试货币格式化器"""
        formatter = CommonFormatters.currency_formatter("¥")

        self.assertEqual(formatter(123.45), "¥123.45")
        self.assertEqual(formatter(100), "¥100.00")
        self.assertEqual(formatter(None), "")

    def test_percentage_formatter(self):
        """测试百分比格式化器"""
        formatter = CommonFormatters.percentage_formatter()

        self.assertEqual(formatter(0.1234), "12.3%")
        self.assertEqual(formatter(1), "100.0%")
        self.assertEqual(formatter(None), "")


class TestCommonParsers(unittest.TestCase):
    """测试常用解析器"""

    def test_date_parser(self):
        """测试日期解析器"""
        parser = CommonParsers.date_parser("%Y-%m-%d")

        result = parser("2023-12-25")
        self.assertEqual(result, date(2023, 12, 25))

        self.assertIsNone(parser(""))
        self.assertIsNone(parser("invalid"))
        self.assertIsNone(parser(None))

    def test_number_parser(self):
        """测试数字解析器"""
        parser = CommonParsers.number_parser()

        self.assertEqual(parser("123"), 123)
        self.assertEqual(parser("123.45"), 123.45)
        self.assertIsNone(parser(""))
        self.assertIsNone(parser("invalid"))
        self.assertIsNone(parser(None))

    def test_currency_parser(self):
        """测试货币解析器"""
        parser = CommonParsers.currency_parser()

        self.assertEqual(parser("¥123.45"), 123.45)
        self.assertEqual(parser("$100.00"), 100.00)
        self.assertEqual(parser("123.45"), 123.45)
        self.assertIsNone(parser(""))
        self.assertIsNone(parser("invalid"))

    def test_percentage_parser(self):
        """测试百分比解析器"""
        parser = CommonParsers.percentage_parser()

        self.assertEqual(parser("12.3%"), 0.123)
        self.assertEqual(parser("100%"), 1.0)
        self.assertEqual(parser("50"), 0.5)
        self.assertIsNone(parser(""))
        self.assertIsNone(parser("invalid"))


class TestCommonValidators(unittest.TestCase):
    """测试常用验证器"""

    def test_required_validator(self):
        """测试必填验证器"""
        validator = CommonValidators.required_validator()

        self.assertTrue(validator("test"))
        self.assertTrue(validator(123))
        self.assertFalse(validator(""))
        self.assertFalse(validator("   "))
        self.assertFalse(validator(None))

    def test_email_validator(self):
        """测试邮箱验证器"""
        validator = CommonValidators.email_validator()

        self.assertTrue(validator("test@example.com"))
        self.assertTrue(validator("user.name@domain.co.uk"))
        self.assertTrue(validator(""))  # 空值通过验证
        self.assertFalse(validator("invalid-email"))
        self.assertFalse(validator("@example.com"))
        self.assertFalse(validator("test@"))

    def test_phone_validator(self):
        """测试电话号码验证器"""
        validator = CommonValidators.phone_validator()

        self.assertTrue(validator("13812345678"))
        self.assertTrue(validator("15987654321"))
        self.assertTrue(validator(""))  # 空值通过验证
        self.assertFalse(validator("12812345678"))  # 不是1开头的有效号码
        self.assertFalse(validator("138123456789"))  # 长度不对
        self.assertFalse(validator("1381234567"))  # 长度不对

    def test_range_validator(self):
        """测试范围验证器"""
        validator = CommonValidators.range_validator(0, 100)

        self.assertTrue(validator(50))
        self.assertTrue(validator(0))
        self.assertTrue(validator(100))
        self.assertTrue(validator(None))  # 空值通过验证
        self.assertFalse(validator(-1))
        self.assertFalse(validator(101))
        self.assertFalse(validator("invalid"))


if __name__ == "__main__":
    unittest.main()
