"""
MiniCRM 客户编辑TTK组件测试

测试客户详情和编辑对话框的功能，包括：
- CustomerDetailTTK组件测试
- CustomerEditDialogTTK组件测试
- 数据加载和显示测试
- 表单验证和保存测试
- 用户交互测试

测试原则：
- 使用Mock模拟外部依赖
- 测试UI组件的核心功能
- 验证数据绑定和事件处理
- 确保错误处理的正确性
"""

from datetime import datetime
from decimal import Decimal
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from minicrm.core.exceptions import ServiceError
from minicrm.models.customer import CustomerLevel, CustomerType, IndustryType
from minicrm.ui.panels.customer_detail_ttk import CustomerDetailTTK
from minicrm.ui.panels.customer_edit_dialog_ttk import CustomerEditDialogTTK


class TestCustomerDetailTTK(unittest.TestCase):
    """客户详情TTK组件测试"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        # 创建模拟的客户服务
        self.mock_customer_service = Mock()

        # 创建测试用的客户数据
        self.test_customer_data = {
            "id": 1,
            "name": "测试客户",
            "phone": "13800138000",
            "email": "test@example.com",
            "company_name": "测试公司",
            "customer_level": CustomerLevel.VIP.value,
            "customer_type": CustomerType.ENTERPRISE.value,
            "industry_type": IndustryType.FURNITURE.value,
            "credit_limit": Decimal("100000.00"),
            "payment_terms": 30,
            "address": "测试地址",
            "notes": "测试备注",
            "total_orders": 5,
            "total_amount": Decimal("50000.00"),
            "last_order_date": datetime(2024, 1, 15),
            "value_score": 85.5,
            "loyalty_score": 90.0,
            "formatted_phone": "138-0013-8000",
            "formatted_credit_limit": "¥100,000.00",
            "formatted_total_amount": "¥50,000.00",
            "cooperation_months": 12,
        }

        # 创建编辑回调函数
        self.edit_callback = Mock()

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "detail_widget"):
            self.detail_widget.destroy()
        self.root.destroy()

    def test_customer_detail_creation(self):
        """测试客户详情组件创建"""
        # 创建客户详情组件
        self.detail_widget = CustomerDetailTTK(
            self.root, self.mock_customer_service, self.edit_callback
        )

        # 验证组件创建成功
        self.assertIsNotNone(self.detail_widget)
        self.assertIsInstance(self.detail_widget, CustomerDetailTTK)

        # 验证UI组件存在
        self.assertIsNotNone(self.detail_widget._notebook)
        self.assertIsNotNone(self.detail_widget._basic_info_form)
        self.assertIsNotNone(self.detail_widget._interaction_table)
        self.assertIsNotNone(self.detail_widget._finance_info_form)

    def test_load_customer_success(self):
        """测试成功加载客户数据"""
        # 设置模拟服务返回数据
        self.mock_customer_service.get_customer_by_id.return_value = (
            self.test_customer_data
        )

        # 创建客户详情组件
        self.detail_widget = CustomerDetailTTK(
            self.root, self.mock_customer_service, self.edit_callback
        )

        # 加载客户数据
        self.detail_widget.load_customer(1)

        # 验证服务调用
        self.mock_customer_service.get_customer_by_id.assert_called_once_with(1)

        # 验证数据加载
        self.assertEqual(self.detail_widget.get_current_customer_id(), 1)
        self.assertEqual(
            self.detail_widget.get_current_customer_data(), self.test_customer_data
        )

    def test_load_customer_not_found(self):
        """测试加载不存在的客户"""
        # 设置模拟服务返回None
        self.mock_customer_service.get_customer_by_id.return_value = None

        # 创建客户详情组件
        self.detail_widget = CustomerDetailTTK(
            self.root, self.mock_customer_service, self.edit_callback
        )

        # 模拟messagebox
        with patch("tkinter.messagebox.showerror") as mock_error:
            self.detail_widget.load_customer(999)

            # 验证错误提示
            mock_error.assert_called_once()
            args = mock_error.call_args[0]
            self.assertEqual(args[0], "错误")
            self.assertIn("未找到客户ID: 999", args[1])

    def test_load_customer_service_error(self):
        """测试加载客户时服务错误"""
        # 设置模拟服务抛出异常
        self.mock_customer_service.get_customer_by_id.side_effect = ServiceError(
            "数据库连接失败"
        )

        # 创建客户详情组件
        self.detail_widget = CustomerDetailTTK(
            self.root, self.mock_customer_service, self.edit_callback
        )

        # 模拟messagebox
        with patch("tkinter.messagebox.showerror") as mock_error:
            self.detail_widget.load_customer(1)

            # 验证错误提示
            mock_error.assert_called_once()
            args = mock_error.call_args[0]
            self.assertEqual(args[0], "错误")
            self.assertIn("数据库连接失败", args[1])

    def test_edit_callback(self):
        """测试编辑回调功能"""
        # 设置模拟服务返回数据
        self.mock_customer_service.get_customer_by_id.return_value = (
            self.test_customer_data
        )

        # 创建客户详情组件
        self.detail_widget = CustomerDetailTTK(
            self.root, self.mock_customer_service, self.edit_callback
        )

        # 加载客户数据
        self.detail_widget.load_customer(1)

        # 触发编辑操作
        self.detail_widget._on_edit_customer()

        # 验证回调函数被调用
        self.edit_callback.assert_called_once_with(1)

    def test_calculate_value_score(self):
        """测试计算客户价值评分"""
        # 设置模拟服务返回数据
        self.mock_customer_service.get_customer_by_id.return_value = (
            self.test_customer_data
        )
        self.mock_customer_service.calculate_customer_value_score.return_value = {
            "total_score": 85.5,
            "loyalty_score": 90.0,
            "transaction_score": 80.0,
            "interaction_score": 85.0,
        }

        # 创建客户详情组件
        self.detail_widget = CustomerDetailTTK(
            self.root, self.mock_customer_service, self.edit_callback
        )

        # 加载客户数据
        self.detail_widget.load_customer(1)

        # 模拟messagebox
        with patch("tkinter.messagebox.showinfo") as mock_info:
            self.detail_widget._calculate_value_score()

            # 验证服务调用
            self.mock_customer_service.calculate_customer_value_score.assert_called_once_with(
                1
            )

            # 验证信息提示
            mock_info.assert_called_once()
            args = mock_info.call_args[0]
            self.assertEqual(args[0], "价值评分")
            self.assertIn("85.5", args[1])


class TestCustomerEditDialogTTK(unittest.TestCase):
    """客户编辑对话框TTK组件测试"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        # 创建模拟的客户服务
        self.mock_customer_service = Mock()

        # 创建测试用的客户数据
        self.test_customer_data = {
            "id": 1,
            "name": "测试客户",
            "phone": "13800138000",
            "email": "test@example.com",
            "company_name": "测试公司",
            "customer_level": CustomerLevel.VIP.value,
            "customer_type": CustomerType.ENTERPRISE.value,
            "industry_type": IndustryType.FURNITURE.value,
            "tax_id": "123456789",
            "credit_limit": Decimal("100000.00"),
            "payment_terms": 30,
            "address": "测试地址",
            "source": "网络推广",
            "notes": "测试备注",
        }

        # 创建保存回调函数
        self.save_callback = Mock()

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "edit_dialog"):
            try:
                self.edit_dialog.destroy()
            except:
                pass
        self.root.destroy()

    def test_new_customer_dialog_creation(self):
        """测试新增客户对话框创建"""
        # 创建新增客户对话框
        self.edit_dialog = CustomerEditDialogTTK(
            self.root,
            self.mock_customer_service,
            customer_id=None,
            on_save_callback=self.save_callback,
        )

        # 验证对话框创建成功
        self.assertIsNotNone(self.edit_dialog)
        self.assertTrue(self.edit_dialog._is_new_customer)
        self.assertIsNone(self.edit_dialog._customer_id)
        self.assertEqual(self.edit_dialog.title(), "新增客户")

    def test_edit_customer_dialog_creation(self):
        """测试编辑客户对话框创建"""
        # 设置模拟服务返回数据
        self.mock_customer_service.get_customer_by_id.return_value = (
            self.test_customer_data
        )

        # 创建编辑客户对话框
        self.edit_dialog = CustomerEditDialogTTK(
            self.root,
            self.mock_customer_service,
            customer_id=1,
            on_save_callback=self.save_callback,
        )

        # 验证对话框创建成功
        self.assertIsNotNone(self.edit_dialog)
        self.assertFalse(self.edit_dialog._is_new_customer)
        self.assertEqual(self.edit_dialog._customer_id, 1)
        self.assertEqual(self.edit_dialog.title(), "编辑客户")

        # 验证数据加载
        self.mock_customer_service.get_customer_by_id.assert_called_once_with(1)

    def test_form_validation_success(self):
        """测试表单验证成功"""
        # 创建新增客户对话框
        self.edit_dialog = CustomerEditDialogTTK(
            self.root,
            self.mock_customer_service,
            customer_id=None,
            on_save_callback=self.save_callback,
        )

        # 设置有效的表单数据
        if self.edit_dialog._form_builder:
            valid_data = {
                "name": "测试客户",
                "phone": "13800138000",
                "email": "test@example.com",
                "company_name": "测试公司",
                "customer_level": CustomerLevel.NORMAL.value,
                "customer_type": CustomerType.ENTERPRISE.value,
                "industry_type": IndustryType.OTHER.value,
                "credit_limit": "10000.00",
                "payment_terms": "30",
            }
            self.edit_dialog._form_builder.set_form_data(valid_data)

        # 模拟messagebox
        with patch("tkinter.messagebox.showinfo") as mock_info:
            result = self.edit_dialog._validate_form()

            # 验证验证成功
            self.assertTrue(result)
            mock_info.assert_called_once_with("验证成功", "所有数据验证通过！")

    def test_form_validation_failure(self):
        """测试表单验证失败"""
        # 创建新增客户对话框
        self.edit_dialog = CustomerEditDialogTTK(
            self.root,
            self.mock_customer_service,
            customer_id=None,
            on_save_callback=self.save_callback,
        )

        # 设置无效的表单数据（缺少必填字段）
        if self.edit_dialog._form_builder:
            invalid_data = {
                "name": "",  # 必填字段为空
                "phone": "invalid_phone",  # 无效电话
                "email": "invalid_email",  # 无效邮箱
                "credit_limit": "invalid_number",  # 无效数字
            }
            self.edit_dialog._form_builder.set_form_data(invalid_data)

        # 模拟messagebox
        with patch("tkinter.messagebox.showerror") as mock_error:
            result = self.edit_dialog._validate_form()

            # 验证验证失败
            self.assertFalse(result)
            mock_error.assert_called_once()

    def test_save_new_customer_success(self):
        """测试成功保存新客户"""
        # 设置模拟服务返回新客户ID
        self.mock_customer_service.create_customer.return_value = 123

        # 创建新增客户对话框
        self.edit_dialog = CustomerEditDialogTTK(
            self.root,
            self.mock_customer_service,
            customer_id=None,
            on_save_callback=self.save_callback,
        )

        # 设置有效的表单数据
        if self.edit_dialog._form_builder:
            valid_data = {
                "name": "新客户",
                "phone": "13900139000",
                "email": "new@example.com",
                "company_name": "新公司",
                "customer_level": CustomerLevel.NORMAL.value,
                "customer_type": CustomerType.ENTERPRISE.value,
                "industry_type": IndustryType.OTHER.value,
                "credit_limit": "5000.00",
                "payment_terms": "15",
            }
            self.edit_dialog._form_builder.set_values(valid_data)

        # 模拟messagebox和destroy
        with (
            patch("tkinter.messagebox.showinfo") as mock_info,
            patch.object(self.edit_dialog, "destroy") as mock_destroy,
        ):
            self.edit_dialog._on_save()

            # 验证服务调用
            self.mock_customer_service.create_customer.assert_called_once()

            # 验证成功提示
            mock_info.assert_called_once()
            args = mock_info.call_args[0]
            self.assertEqual(args[0], "成功")
            self.assertIn("客户创建成功", args[1])

            # 验证回调函数调用
            self.save_callback.assert_called_once_with(123, True)

            # 验证对话框关闭
            mock_destroy.assert_called_once()

    def test_save_edit_customer_success(self):
        """测试成功保存编辑客户"""
        # 设置模拟服务返回数据
        self.mock_customer_service.get_customer_by_id.return_value = (
            self.test_customer_data
        )
        self.mock_customer_service.update_customer.return_value = True

        # 创建编辑客户对话框
        self.edit_dialog = CustomerEditDialogTTK(
            self.root,
            self.mock_customer_service,
            customer_id=1,
            on_save_callback=self.save_callback,
        )

        # 修改表单数据
        if self.edit_dialog._form_builder:
            updated_data = {
                "name": "更新客户",
                "phone": "13800138000",
                "email": "updated@example.com",
                "company_name": "更新公司",
                "customer_level": CustomerLevel.VIP.value,
                "customer_type": CustomerType.ENTERPRISE.value,
                "industry_type": IndustryType.FURNITURE.value,
                "credit_limit": "200000.00",
                "payment_terms": "45",
            }
            self.edit_dialog._form_builder.set_values(updated_data)

        # 模拟messagebox和destroy
        with (
            patch("tkinter.messagebox.showinfo") as mock_info,
            patch.object(self.edit_dialog, "destroy") as mock_destroy,
        ):
            self.edit_dialog._on_save()

            # 验证服务调用
            self.mock_customer_service.update_customer.assert_called_once_with(
                1, unittest.mock.ANY
            )

            # 验证成功提示
            mock_info.assert_called_once()
            args = mock_info.call_args[0]
            self.assertEqual(args[0], "成功")
            self.assertIn("客户信息更新成功", args[1])

            # 验证回调函数调用
            self.save_callback.assert_called_once_with(1, False)

            # 验证对话框关闭
            mock_destroy.assert_called_once()

    def test_save_customer_service_error(self):
        """测试保存客户时服务错误"""
        # 设置模拟服务抛出异常
        self.mock_customer_service.create_customer.side_effect = ServiceError(
            "数据库连接失败"
        )

        # 创建新增客户对话框
        self.edit_dialog = CustomerEditDialogTTK(
            self.root,
            self.mock_customer_service,
            customer_id=None,
            on_save_callback=self.save_callback,
        )

        # 设置有效的表单数据
        if self.edit_dialog._form_builder:
            valid_data = {
                "name": "测试客户",
                "phone": "13800138000",
                "email": "test@example.com",
            }
            self.edit_dialog._form_builder.set_values(valid_data)

        # 模拟messagebox
        with patch("tkinter.messagebox.showerror") as mock_error:
            self.edit_dialog._on_save()

            # 验证错误提示
            mock_error.assert_called_once()
            args = mock_error.call_args[0]
            self.assertEqual(args[0], "错误")
            self.assertIn("数据库连接失败", args[1])

    def test_field_validators(self):
        """测试字段验证器"""
        # 创建对话框
        self.edit_dialog = CustomerEditDialogTTK(
            self.root,
            self.mock_customer_service,
            customer_id=None,
            on_save_callback=self.save_callback,
        )

        # 测试姓名验证
        valid, msg = self.edit_dialog._validate_name("张三")
        self.assertTrue(valid)
        self.assertEqual(msg, "")

        valid, msg = self.edit_dialog._validate_name("")
        self.assertFalse(valid)
        self.assertIn("不能为空", msg)

        valid, msg = self.edit_dialog._validate_name("a")
        self.assertFalse(valid)
        self.assertIn("至少需要2个字符", msg)

        # 测试电话验证
        valid, msg = self.edit_dialog._validate_phone("13800138000")
        self.assertTrue(valid)

        valid, msg = self.edit_dialog._validate_phone("")
        self.assertFalse(valid)
        self.assertIn("不能为空", msg)

        # 测试邮箱验证
        valid, msg = self.edit_dialog._validate_email("test@example.com")
        self.assertTrue(valid)

        valid, msg = self.edit_dialog._validate_email("")
        self.assertTrue(valid)  # 邮箱不是必填项

        # 测试授信额度验证
        valid, msg = self.edit_dialog._validate_credit_limit("10000.00")
        self.assertTrue(valid)

        valid, msg = self.edit_dialog._validate_credit_limit("-1000")
        self.assertFalse(valid)
        self.assertIn("不能为负数", msg)

        valid, msg = self.edit_dialog._validate_credit_limit("invalid")
        self.assertFalse(valid)
        self.assertIn("有效的数字", msg)

        # 测试付款期限验证
        valid, msg = self.edit_dialog._validate_payment_terms("30")
        self.assertTrue(valid)

        valid, msg = self.edit_dialog._validate_payment_terms("-10")
        self.assertFalse(valid)
        self.assertIn("不能为负数", msg)

        valid, msg = self.edit_dialog._validate_payment_terms("400")
        self.assertFalse(valid)
        self.assertIn("不能超过365天", msg)

    def test_static_methods(self):
        """测试静态方法"""
        # 测试显示新增客户对话框
        with (
            patch.object(
                CustomerEditDialogTTK, "__init__", return_value=None
            ) as mock_init,
            patch.object(
                CustomerEditDialogTTK, "get_result", return_value=123
            ) as mock_result,
            patch("tkinter.Tk.wait_window") as mock_wait,
        ):
            result = CustomerEditDialogTTK.show_new_customer_dialog(
                self.root, self.mock_customer_service, self.save_callback
            )

            # 验证返回结果
            self.assertEqual(result, 123)

        # 测试显示编辑客户对话框
        with (
            patch.object(
                CustomerEditDialogTTK, "__init__", return_value=None
            ) as mock_init,
            patch.object(
                CustomerEditDialogTTK, "get_result", return_value=1
            ) as mock_result,
            patch("tkinter.Tk.wait_window") as mock_wait,
        ):
            result = CustomerEditDialogTTK.show_edit_customer_dialog(
                self.root, self.mock_customer_service, 1, self.save_callback
            )

            # 验证返回结果
            self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
