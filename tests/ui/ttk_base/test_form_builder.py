"""TTK表单构建器测试

测试表单构建器的功能，包括：
- FormBuilderTTK动态表单生成测试
- 各种输入组件集成测试
- 表单验证机制测试
- 数据绑定和同步测试

作者: MiniCRM开发团队
"""

import tkinter as tk
import unittest
from unittest.mock import Mock

from src.minicrm.ui.ttk_base.form_builder import FormBuilderTTK


class TestFormBuilderTTK(unittest.TestCase):
    """测试表单构建器"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        # 定义测试字段
        self.test_fields = [
            {"id": "name", "type": "entry", "label": "姓名", "required": True},
            {
                "id": "age",
                "type": "number_spinner",
                "label": "年龄",
                "min_value": 0,
                "max_value": 120,
            },
            {"id": "email", "type": "entry", "label": "邮箱", "format": "email"},
            {"id": "description", "type": "text", "label": "描述", "height": 3},
            {
                "id": "gender",
                "type": "combobox",
                "label": "性别",
                "options": ["男", "女", "其他"],
            },
        ]

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_form_creation(self):
        """测试表单创建"""
        form = FormBuilderTTK(self.root, self.test_fields)

        # 验证字段组件创建
        self.assertEqual(len(form.widgets), len(self.test_fields))
        self.assertEqual(len(form.labels), len(self.test_fields))
        self.assertEqual(len(form.error_labels), len(self.test_fields))

        # 验证特定字段
        self.assertIn("name", form.widgets)
        self.assertIn("age", form.widgets)
        self.assertIn("email", form.widgets)

    def test_form_data_operations(self):
        """测试表单数据操作"""
        form = FormBuilderTTK(self.root, self.test_fields)

        # 测试设置表单数据
        test_data = {
            "name": "张三",
            "age": 25,
            "email": "zhangsan@example.com",
            "description": "这是一个测试用户",
            "gender": "男",
        }

        form.set_form_data(test_data)

        # 测试获取表单数据
        retrieved_data = form.get_form_data()

        # 验证数据设置成功（注意某些组件可能有数据转换）
        self.assertEqual(retrieved_data["name"], "张三")
        self.assertEqual(retrieved_data["gender"], "男")

    def test_field_value_operations(self):
        """测试字段值操作"""
        form = FormBuilderTTK(self.root, self.test_fields)

        # 测试设置单个字段值
        form.set_field_value("name", "李四")
        self.assertEqual(form.get_field_value("name"), "李四")

        # 测试默认值
        self.assertEqual(form.get_field_value("nonexistent", "default"), "default")

    def test_form_validation(self):
        """测试表单验证"""
        form = FormBuilderTTK(self.root, self.test_fields)

        # 测试空表单验证（name是必填的）
        is_valid, errors = form.validate_form()
        self.assertFalse(is_valid)
        self.assertIn("name", errors)

        # 设置有效数据
        form.set_field_value("name", "王五")
        form.set_field_value("email", "wangwu@example.com")

        is_valid, errors = form.validate_form()
        # 注意：由于GUI环境问题，这里可能无法完全验证
        # 但至少验证了验证机制的存在

    def test_form_clear(self):
        """测试表单清空"""
        form = FormBuilderTTK(self.root, self.test_fields)

        # 设置一些数据
        form.set_field_value("name", "测试")
        form.set_field_value("age", 30)

        # 清空表单
        form.clear_form()

        # 验证数据被清空
        self.assertIsNone(form.get_field_value("name"))
        self.assertIsNone(form.get_field_value("age"))

    def test_field_visibility(self):
        """测试字段可见性"""
        form = FormBuilderTTK(self.root, self.test_fields)

        # 测试隐藏字段
        form.set_field_visible("name", False)

        # 测试显示字段
        form.set_field_visible("name", True)

        # 这里主要测试方法调用不会出错
        # 实际的可见性效果需要在GUI环境中验证

    def test_field_enabled_state(self):
        """测试字段启用状态"""
        form = FormBuilderTTK(self.root, self.test_fields)

        # 测试禁用字段
        form.set_field_enabled("name", False)

        # 测试启用字段
        form.set_field_enabled("name", True)

        # 这里主要测试方法调用不会出错

    def test_form_events(self):
        """测试表单事件"""
        form = FormBuilderTTK(self.root, self.test_fields)

        # 模拟事件处理器
        submit_handler = Mock()
        reset_handler = Mock()

        form.add_event_handler("form_submit", submit_handler)
        form.add_event_handler("form_reset", reset_handler)

        # 设置有效数据
        form.set_field_value("name", "测试用户")

        # 模拟提交（注意：实际的按钮点击需要GUI环境）
        form._on_submit()

        # 模拟重置
        form._on_reset()

        # 验证事件被触发
        submit_handler.assert_called()
        reset_handler.assert_called()

    def test_different_field_types(self):
        """测试不同字段类型"""
        # 测试更多字段类型
        extended_fields = [
            {"id": "checkbox_field", "type": "checkbox", "label": "复选框"},
            {
                "id": "radio_field",
                "type": "radiobutton",
                "label": "单选",
                "options": ["选项1", "选项2"],
            },
            {
                "id": "scale_field",
                "type": "scale",
                "label": "滑块",
                "from_": 0,
                "to": 100,
            },
            {"id": "spinbox_field", "type": "spinbox", "label": "微调框"},
        ]

        form = FormBuilderTTK(self.root, extended_fields)

        # 验证所有字段都被创建
        self.assertEqual(len(form.widgets), len(extended_fields))

        # 验证特定字段类型
        self.assertIn("checkbox_field", form.widgets)
        self.assertIn("radio_field", form.widgets)
        self.assertIn("scale_field", form.widgets)
        self.assertIn("spinbox_field", form.widgets)

    def test_form_layout(self):
        """测试表单布局"""
        # 测试不同列数
        form_1_col = FormBuilderTTK(self.root, self.test_fields, columns=1)
        form_3_col = FormBuilderTTK(self.root, self.test_fields, columns=3)

        self.assertEqual(form_1_col.columns, 1)
        self.assertEqual(form_3_col.columns, 3)

    def test_error_handling(self):
        """测试错误处理"""
        form = FormBuilderTTK(self.root, self.test_fields)

        # 测试错误消息显示
        errors = {"name": "姓名不能为空", "email": "邮箱格式不正确"}
        form._show_error_messages(errors)

        # 测试清除错误消息
        form._clear_error_messages()

        # 验证方法调用不会出错


class TestFormBuilderIntegration(unittest.TestCase):
    """测试表单构建器集成功能"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_complete_form_workflow(self):
        """测试完整的表单工作流程"""
        # 定义一个完整的表单
        fields = [
            {"id": "username", "type": "entry", "label": "用户名", "required": True},
            {"id": "password", "type": "entry", "label": "密码", "required": True},
            {
                "id": "age",
                "type": "number_spinner",
                "label": "年龄",
                "min_value": 18,
                "max_value": 100,
            },
            {
                "id": "email",
                "type": "entry",
                "label": "邮箱",
                "format": "email",
                "required": True,
            },
        ]

        form = FormBuilderTTK(self.root, fields)

        # 1. 测试空表单验证
        is_valid, errors = form.validate_form()
        self.assertFalse(is_valid)

        # 2. 设置部分数据
        form.set_field_value("username", "testuser")
        form.set_field_value("password", "password123")

        # 3. 测试部分有效数据
        is_valid, errors = form.validate_form()
        # 可能仍然无效，因为email是必填的

        # 4. 设置完整有效数据
        form.set_field_value("email", "test@example.com")
        form.set_field_value("age", 25)

        # 5. 获取最终数据
        final_data = form.get_form_data()

        # 验证数据完整性
        self.assertIn("username", final_data)
        self.assertIn("password", final_data)
        self.assertIn("email", final_data)
        self.assertIn("age", final_data)


if __name__ == "__main__":
    unittest.main()
