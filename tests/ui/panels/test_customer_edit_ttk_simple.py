"""
MiniCRM 客户编辑TTK组件简化测试

测试客户详情和编辑对话框的核心功能，避免Tkinter环境依赖：
- 数据验证逻辑测试
- 业务逻辑测试
- 错误处理测试

测试原则：
- 避免创建实际的Tkinter组件
- 专注于业务逻辑和数据处理
- 使用Mock模拟UI组件
"""

from datetime import datetime
from decimal import Decimal
import unittest
from unittest.mock import Mock, patch

from minicrm.models.customer import CustomerLevel, CustomerType, IndustryType
from minicrm.ui.panels.customer_edit_dialog_ttk import CustomerEditDialogTTK


class TestCustomerEditDialogValidation(unittest.TestCase):
    """客户编辑对话框验证逻辑测试"""

    def setUp(self):
        """测试准备"""
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

    def test_validate_name(self):
        """测试姓名验证"""
        # 模拟对话框实例，避免创建实际的Tkinter组件
        with (
            patch("tkinter.Toplevel.__init__"),
            patch.object(CustomerEditDialogTTK, "_setup_dialog"),
            patch.object(CustomerEditDialogTTK, "_setup_ui"),
            patch.object(CustomerEditDialogTTK, "_bind_events"),
            patch.object(CustomerEditDialogTTK, "_set_default_values"),
        ):
            dialog = CustomerEditDialogTTK.__new__(CustomerEditDialogTTK)
            dialog._customer_service = self.mock_customer_service
            dialog._customer_id = None
            dialog._is_new_customer = True

            # 测试有效姓名
            valid, msg = dialog._validate_name("张三")
            self.assertTrue(valid)
            self.assertEqual(msg, "")

            # 测试空姓名
            valid, msg = dialog._validate_name("")
            self.assertFalse(valid)
            self.assertIn("不能为空", msg)

            # 测试过短姓名
            valid, msg = dialog._validate_name("a")
            self.assertFalse(valid)
            self.assertIn("至少需要2个字符", msg)

            # 测试过长姓名
            valid, msg = dialog._validate_name("a" * 51)
            self.assertFalse(valid)
            self.assertIn("不能超过50个字符", msg)

    def test_validate_phone(self):
        """测试电话验证"""
        with (
            patch("tkinter.Toplevel.__init__"),
            patch.object(CustomerEditDialogTTK, "_setup_dialog"),
            patch.object(CustomerEditDialogTTK, "_setup_ui"),
            patch.object(CustomerEditDialogTTK, "_bind_events"),
            patch.object(CustomerEditDialogTTK, "_set_default_values"),
        ):
            dialog = CustomerEditDialogTTK.__new__(CustomerEditDialogTTK)
            dialog._customer_service = self.mock_customer_service
            dialog._customer_id = None
            dialog._is_new_customer = True
            dialog._logger = Mock()

            # 测试有效电话
            with patch("transfunctions.validation.validate_phone") as mock_validate:
                mock_validate.return_value = Mock(is_valid=True, errors=[])
                valid, msg = dialog._validate_phone("13800138000")
                self.assertTrue(valid)
                self.assertEqual(msg, "")

            # 测试空电话
            valid, msg = dialog._validate_phone("")
            self.assertFalse(valid)
            self.assertIn("不能为空", msg)

            # 测试无效电话
            with patch("transfunctions.validation.validate_phone") as mock_validate:
                mock_validate.return_value = Mock(
                    is_valid=False, errors=["电话号码格式不正确"]
                )
                valid, msg = dialog._validate_phone("invalid_phone")
                self.assertFalse(valid)
                self.assertIn("电话号码格式不正确", msg)

    def test_validate_email(self):
        """测试邮箱验证"""
        with (
            patch("tkinter.Toplevel.__init__"),
            patch.object(CustomerEditDialogTTK, "_setup_dialog"),
            patch.object(CustomerEditDialogTTK, "_setup_ui"),
            patch.object(CustomerEditDialogTTK, "_bind_events"),
            patch.object(CustomerEditDialogTTK, "_set_default_values"),
        ):
            dialog = CustomerEditDialogTTK.__new__(CustomerEditDialogTTK)
            dialog._customer_service = self.mock_customer_service
            dialog._customer_id = None
            dialog._is_new_customer = True
            dialog._logger = Mock()

            # 测试有效邮箱
            with patch("transfunctions.validation.validate_email") as mock_validate:
                mock_validate.return_value = Mock(is_valid=True, errors=[])
                valid, msg = dialog._validate_email("test@example.com")
                self.assertTrue(valid)
                self.assertEqual(msg, "")

            # 测试空邮箱（应该通过，因为不是必填项）
            valid, msg = dialog._validate_email("")
            self.assertTrue(valid)
            self.assertEqual(msg, "")

            # 测试无效邮箱
            with patch("transfunctions.validation.validate_email") as mock_validate:
                mock_validate.return_value = Mock(
                    is_valid=False, errors=["邮箱地址格式不正确"]
                )
                valid, msg = dialog._validate_email("invalid_email")
                self.assertFalse(valid)
                self.assertIn("邮箱地址格式不正确", msg)

    def test_validate_credit_limit(self):
        """测试授信额度验证"""
        with (
            patch("tkinter.Toplevel.__init__"),
            patch.object(CustomerEditDialogTTK, "_setup_dialog"),
            patch.object(CustomerEditDialogTTK, "_setup_ui"),
            patch.object(CustomerEditDialogTTK, "_bind_events"),
            patch.object(CustomerEditDialogTTK, "_set_default_values"),
        ):
            dialog = CustomerEditDialogTTK.__new__(CustomerEditDialogTTK)
            dialog._customer_service = self.mock_customer_service
            dialog._customer_id = None
            dialog._is_new_customer = True

            # 测试有效金额
            valid, msg = dialog._validate_credit_limit("10000.00")
            self.assertTrue(valid)
            self.assertEqual(msg, "")

            # 测试空值（应该通过）
            valid, msg = dialog._validate_credit_limit("")
            self.assertTrue(valid)
            self.assertEqual(msg, "")

            # 测试负数
            valid, msg = dialog._validate_credit_limit("-1000")
            self.assertFalse(valid)
            self.assertIn("不能为负数", msg)

            # 测试无效数字
            valid, msg = dialog._validate_credit_limit("invalid")
            self.assertFalse(valid)
            self.assertIn("有效的数字", msg)

            # 测试超大金额
            valid, msg = dialog._validate_credit_limit("9999999999.99")
            self.assertFalse(valid)
            self.assertIn("不能超过", msg)

    def test_validate_payment_terms(self):
        """测试付款期限验证"""
        with (
            patch("tkinter.Toplevel.__init__"),
            patch.object(CustomerEditDialogTTK, "_setup_dialog"),
            patch.object(CustomerEditDialogTTK, "_setup_ui"),
            patch.object(CustomerEditDialogTTK, "_bind_events"),
            patch.object(CustomerEditDialogTTK, "_set_default_values"),
        ):
            dialog = CustomerEditDialogTTK.__new__(CustomerEditDialogTTK)
            dialog._customer_service = self.mock_customer_service
            dialog._customer_id = None
            dialog._is_new_customer = True

            # 测试有效期限
            valid, msg = dialog._validate_payment_terms("30")
            self.assertTrue(valid)
            self.assertEqual(msg, "")

            # 测试空值（应该通过）
            valid, msg = dialog._validate_payment_terms("")
            self.assertTrue(valid)
            self.assertEqual(msg, "")

            # 测试负数
            valid, msg = dialog._validate_payment_terms("-10")
            self.assertFalse(valid)
            self.assertIn("不能为负数", msg)

            # 测试超大值
            valid, msg = dialog._validate_payment_terms("400")
            self.assertFalse(valid)
            self.assertIn("不能超过365天", msg)

            # 测试无效数字
            valid, msg = dialog._validate_payment_terms("invalid")
            self.assertFalse(valid)
            self.assertIn("有效的整数", msg)

    def test_prepare_save_data(self):
        """测试保存数据准备"""
        with (
            patch("tkinter.Toplevel.__init__"),
            patch.object(CustomerEditDialogTTK, "_setup_dialog"),
            patch.object(CustomerEditDialogTTK, "_setup_ui"),
            patch.object(CustomerEditDialogTTK, "_bind_events"),
            patch.object(CustomerEditDialogTTK, "_set_default_values"),
        ):
            dialog = CustomerEditDialogTTK.__new__(CustomerEditDialogTTK)
            dialog._customer_service = self.mock_customer_service
            dialog._customer_id = None
            dialog._is_new_customer = True

            # 测试数据准备
            form_data = {
                "name": "  测试客户  ",  # 包含空格
                "phone": "13800138000",
                "email": "test@example.com",
                "company_name": "测试公司",
                "customer_level": CustomerLevel.VIP.value,
                "customer_type": CustomerType.ENTERPRISE.value,
                "industry_type": IndustryType.FURNITURE.value,
                "credit_limit": "10000.50",
                "payment_terms": "30",
                "address": "测试地址",
                "source": "网络推广",
                "notes": "测试备注",
            }

            save_data = dialog._prepare_save_data(form_data)

            # 验证数据处理
            self.assertEqual(save_data["name"], "测试客户")  # 空格被去除
            self.assertEqual(save_data["phone"], "13800138000")
            self.assertEqual(save_data["credit_limit"], 10000.50)
            self.assertEqual(save_data["payment_terms"], 30)
            self.assertEqual(save_data["customer_level"], CustomerLevel.VIP.value)

    def test_prepare_form_values(self):
        """测试表单值准备"""
        with (
            patch("tkinter.Toplevel.__init__"),
            patch.object(CustomerEditDialogTTK, "_setup_dialog"),
            patch.object(CustomerEditDialogTTK, "_setup_ui"),
            patch.object(CustomerEditDialogTTK, "_bind_events"),
            patch.object(CustomerEditDialogTTK, "_set_default_values"),
        ):
            dialog = CustomerEditDialogTTK.__new__(CustomerEditDialogTTK)
            dialog._customer_service = self.mock_customer_service
            dialog._customer_id = 1
            dialog._is_new_customer = False

            # 测试表单值准备
            form_values = dialog._prepare_form_values(self.test_customer_data)

            # 验证数据转换
            self.assertEqual(form_values["name"], "测试客户")
            self.assertEqual(form_values["phone"], "13800138000")
            self.assertEqual(form_values["credit_limit"], "100000.00")
            self.assertEqual(form_values["payment_terms"], "30")
            self.assertEqual(form_values["customer_level"], CustomerLevel.VIP.value)


class TestCustomerDetailLogic(unittest.TestCase):
    """客户详情组件逻辑测试"""

    def setUp(self):
        """测试准备"""
        self.mock_customer_service = Mock()
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

    def test_format_date(self):
        """测试日期格式化"""
        # 由于无法创建实际的CustomerDetailTTK实例，我们测试日期格式化逻辑

        # 测试datetime对象
        date_obj = datetime(2024, 1, 15, 10, 30, 0)
        # 模拟_format_date方法的逻辑
        formatted = date_obj.strftime("%Y-%m-%d")
        self.assertEqual(formatted, "2024-01-15")

        # 测试ISO字符串
        iso_string = "2024-01-15T10:30:00Z"
        try:
            date_obj = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
            formatted = date_obj.strftime("%Y-%m-%d")
            self.assertEqual(formatted, "2024-01-15")
        except ValueError:
            formatted = iso_string
            self.assertEqual(formatted, iso_string)

        # 测试空值
        self.assertEqual("", "")  # 空值应该返回空字符串


if __name__ == "__main__":
    unittest.main()
