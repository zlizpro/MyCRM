"""测试合同编辑TTK对话框

测试ContractEditDialogTTK的功能，包括：
- 对话框初始化和UI创建
- 表单数据加载和验证
- 创建和编辑模式
- 数据收集和保存

作者: MiniCRM开发团队
"""

from datetime import datetime
from decimal import Decimal
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from minicrm.core.exceptions import ValidationError
from minicrm.models.contract import (
    Contract,
    ContractStatus,
    ContractType,
    PaymentMethod,
)
from minicrm.services.contract_service import ContractService
from minicrm.ui.ttk_base.contract_edit_dialog_ttk import ContractEditDialogTTK


class TestContractEditDialogTTK(unittest.TestCase):
    """合同编辑TTK对话框测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建根窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏窗口

        # 创建模拟的合同服务
        self.mock_contract_service = Mock(spec=ContractService)

        # 创建测试合同数据
        self.test_contract = Contract(
            id=1,
            contract_number="S20240101001",
            party_name="测试客户A",
            contract_type=ContractType.SALES,
            contract_status=ContractStatus.DRAFT,
            contract_amount=Decimal("100000.00"),
            currency="CNY",
            payment_method=PaymentMethod.BANK_TRANSFER,
            payment_terms=30,
            sign_date=datetime(2024, 1, 1),
            effective_date=datetime(2024, 1, 1),
            expiry_date=datetime(2024, 12, 31),
            terms_and_conditions="测试条款",
            delivery_terms="测试交付条款",
            warranty_terms="测试保修条款",
            reminder_days=30,
            auto_renewal=False,
            progress_percentage=0.0,
            notes="测试备注",
        )

    def tearDown(self):
        """测试后清理"""
        if hasattr(self, "dialog"):
            try:
                self.dialog.destroy()
            except:
                pass
        self.root.destroy()

    def test_dialog_initialization_create_mode(self):
        """测试对话框初始化 - 创建模式"""
        # 创建对话框（创建模式）
        self.dialog = ContractEditDialogTTK(
            self.root, self.mock_contract_service, contract=None
        )

        # 验证对话框创建成功
        self.assertIsNotNone(self.dialog)
        self.assertEqual(self.dialog.contract_service, self.mock_contract_service)
        self.assertIsNone(self.dialog.contract)
        self.assertFalse(self.dialog.is_edit_mode)
        self.assertEqual(self.dialog.title(), "新建合同")

        # 验证UI组件创建
        self.assertIsNotNone(self.dialog.notebook)
        self.assertIsNotNone(self.dialog.basic_form)
        self.assertIsNotNone(self.dialog.financial_form)
        self.assertIsNotNone(self.dialog.settings_form)

    def test_dialog_initialization_edit_mode(self):
        """测试对话框初始化 - 编辑模式"""
        # 创建对话框（编辑模式）
        self.dialog = ContractEditDialogTTK(
            self.root, self.mock_contract_service, contract=self.test_contract
        )

        # 验证对话框创建成功
        self.assertIsNotNone(self.dialog)
        self.assertEqual(self.dialog.contract, self.test_contract)
        self.assertTrue(self.dialog.is_edit_mode)
        self.assertEqual(self.dialog.title(), "编辑合同")

    def test_form_data_loading(self):
        """测试表单数据加载"""
        # 创建对话框（编辑模式）
        self.dialog = ContractEditDialogTTK(
            self.root, self.mock_contract_service, contract=self.test_contract
        )

        # 验证基本信息加载
        basic_data = self.dialog.basic_form.get_form_data()
        self.assertEqual(basic_data["contract_number"], "S20240101001")
        self.assertEqual(basic_data["party_name"], "测试客户A")
        self.assertEqual(basic_data["contract_type"], "sales")
        self.assertEqual(basic_data["contract_status"], "draft")

        # 验证财务信息加载
        financial_data = self.dialog.financial_form.get_form_data()
        self.assertEqual(financial_data["contract_amount"], 100000.00)
        self.assertEqual(financial_data["currency"], "CNY")
        self.assertEqual(financial_data["payment_method"], "bank_transfer")
        self.assertEqual(financial_data["payment_terms"], 30)

        # 验证条款信息加载
        terms_content = self.dialog.terms_text.get("1.0", tk.END).strip()
        self.assertEqual(terms_content, "测试条款")

        delivery_content = self.dialog.delivery_text.get("1.0", tk.END).strip()
        self.assertEqual(delivery_content, "测试交付条款")

        warranty_content = self.dialog.warranty_text.get("1.0", tk.END).strip()
        self.assertEqual(warranty_content, "测试保修条款")

        # 验证设置信息加载
        settings_data = self.dialog.settings_form.get_form_data()
        self.assertEqual(settings_data["reminder_days"], 30)
        self.assertEqual(settings_data["auto_renewal"], False)
        self.assertEqual(settings_data["progress_percentage"], 0.0)
        self.assertEqual(settings_data["notes"], "测试备注")

    def test_collect_form_data(self):
        """测试表单数据收集"""
        # 创建对话框
        self.dialog = ContractEditDialogTTK(
            self.root, self.mock_contract_service, contract=None
        )

        # 设置表单数据
        self.dialog.basic_form.set_form_data(
            {
                "contract_number": "TEST001",
                "party_name": "测试客户",
                "contract_type": "sales",
                "contract_status": "draft",
            }
        )

        self.dialog.financial_form.set_form_data(
            {
                "contract_amount": 50000.00,
                "currency": "CNY",
                "payment_method": "bank_transfer",
                "payment_terms": 15,
            }
        )

        self.dialog.terms_text.insert("1.0", "测试条款内容")
        self.dialog.delivery_text.insert("1.0", "测试交付条款")
        self.dialog.warranty_text.insert("1.0", "测试保修条款")

        self.dialog.settings_form.set_form_data(
            {
                "reminder_days": 15,
                "auto_renewal": True,
                "progress_percentage": 25.0,
                "notes": "测试备注信息",
            }
        )

        # 收集数据
        collected_data = self.dialog._collect_form_data()

        # 验证收集的数据
        self.assertEqual(collected_data["contract_number"], "TEST001")
        self.assertEqual(collected_data["party_name"], "测试客户")
        self.assertEqual(collected_data["contract_type"], "sales")
        self.assertEqual(collected_data["contract_amount"], 50000.00)
        self.assertEqual(collected_data["terms_and_conditions"], "测试条款内容")
        self.assertEqual(collected_data["delivery_terms"], "测试交付条款")
        self.assertEqual(collected_data["warranty_terms"], "测试保修条款")
        self.assertEqual(collected_data["reminder_days"], 15)
        self.assertEqual(collected_data["auto_renewal"], True)

    def test_data_validation_success(self):
        """测试数据验证 - 成功情况"""
        # 创建对话框
        self.dialog = ContractEditDialogTTK(
            self.root, self.mock_contract_service, contract=None
        )

        # 准备有效数据
        valid_data = {
            "party_name": "有效客户名称",
            "contract_type": "sales",
            "contract_status": "draft",
            "contract_amount": 100000.00,
            "payment_terms": 30,
            "sign_date": "2024-01-01",
            "effective_date": "2024-01-01",
            "expiry_date": "2024-12-31",
            "progress_percentage": 50.0,
        }

        # 验证数据（应该不抛出异常）
        try:
            self.dialog._validate_contract_data(valid_data)
        except ValidationError:
            self.fail("有效数据验证失败")

    def test_data_validation_failures(self):
        """测试数据验证 - 失败情况"""
        # 创建对话框
        self.dialog = ContractEditDialogTTK(
            self.root, self.mock_contract_service, contract=None
        )

        # 测试空的合同方名称
        invalid_data = {
            "party_name": "",
            "contract_type": "sales",
            "contract_amount": 100000.00,
        }

        with self.assertRaises(ValidationError) as context:
            self.dialog._validate_contract_data(invalid_data)
        self.assertIn("合同方名称不能为空", str(context.exception))

        # 测试负数金额
        invalid_data = {
            "party_name": "测试客户",
            "contract_type": "sales",
            "contract_amount": -1000.00,
        }

        with self.assertRaises(ValidationError) as context:
            self.dialog._validate_contract_data(invalid_data)
        self.assertIn("合同金额不能为负数", str(context.exception))

        # 测试无效的付款期限
        invalid_data = {
            "party_name": "测试客户",
            "contract_type": "sales",
            "contract_amount": 100000.00,
            "payment_terms": 400,  # 超过365天
        }

        with self.assertRaises(ValidationError) as context:
            self.dialog._validate_contract_data(invalid_data)
        self.assertIn("付款期限必须在0-365天之间", str(context.exception))

        # 测试日期逻辑错误
        invalid_data = {
            "party_name": "测试客户",
            "contract_type": "sales",
            "contract_amount": 100000.00,
            "effective_date": "2024-12-31",
            "expiry_date": "2024-01-01",  # 到期日期早于生效日期
        }

        with self.assertRaises(ValidationError) as context:
            self.dialog._validate_contract_data(invalid_data)
        self.assertIn("生效日期必须早于到期日期", str(context.exception))

    def test_save_operation(self):
        """测试保存操作"""
        # 创建对话框
        self.dialog = ContractEditDialogTTK(
            self.root, self.mock_contract_service, contract=None
        )

        # 设置有效的表单数据
        self.dialog.basic_form.set_form_data(
            {
                "party_name": "测试客户",
                "contract_type": "sales",
                "contract_status": "draft",
            }
        )

        self.dialog.financial_form.set_form_data(
            {
                "contract_amount": 100000.00,
                "currency": "CNY",
                "payment_method": "bank_transfer",
                "payment_terms": 30,
            }
        )

        # 模拟保存操作
        with patch.object(self.dialog, "destroy") as mock_destroy:
            self.dialog._on_save()

            # 验证结果设置
            self.assertTrue(self.dialog.result)

            # 验证对话框关闭
            mock_destroy.assert_called_once()

    def test_cancel_operation(self):
        """测试取消操作"""
        # 创建对话框
        self.dialog = ContractEditDialogTTK(
            self.root, self.mock_contract_service, contract=None
        )

        # 模拟取消操作
        with patch.object(self.dialog, "destroy") as mock_destroy:
            self.dialog._on_cancel()

            # 验证结果设置
            self.assertFalse(self.dialog.result)

            # 验证对话框关闭
            mock_destroy.assert_called_once()

    def test_validate_operation(self):
        """测试验证操作"""
        # 创建对话框
        self.dialog = ContractEditDialogTTK(
            self.root, self.mock_contract_service, contract=None
        )

        # 设置有效数据
        self.dialog.basic_form.set_form_data(
            {
                "party_name": "测试客户",
                "contract_type": "sales",
                "contract_status": "draft",
            }
        )

        self.dialog.financial_form.set_form_data(
            {"contract_amount": 100000.00, "payment_terms": 30}
        )

        # 模拟验证操作（应该显示成功消息）
        with patch(
            "minicrm.ui.ttk_base.message_dialogs_ttk.show_info"
        ) as mock_show_info:
            self.dialog._on_validate()
            mock_show_info.assert_called_with(self.dialog, "合同数据验证通过！")

    def test_reset_operation(self):
        """测试重置操作"""
        # 创建对话框
        self.dialog = ContractEditDialogTTK(
            self.root, self.mock_contract_service, contract=None
        )

        # 设置一些数据
        self.dialog.basic_form.set_form_data(
            {"party_name": "测试客户", "contract_type": "sales"}
        )

        self.dialog.terms_text.insert("1.0", "测试条款")

        # 模拟重置操作
        with patch("minicrm.ui.ttk_base.message_dialogs_ttk.confirm") as mock_confirm:
            mock_confirm.return_value = True

            self.dialog._on_reset()

            # 验证确认对话框调用
            mock_confirm.assert_called_once()

            # 验证数据清空
            basic_data = self.dialog.basic_form.get_form_data()
            self.assertEqual(basic_data.get("party_name", ""), "")

            terms_content = self.dialog.terms_text.get("1.0", tk.END).strip()
            self.assertEqual(terms_content, "")

    def test_enum_value_extraction(self):
        """测试枚举值提取"""
        # 创建对话框
        self.dialog = ContractEditDialogTTK(
            self.root, self.mock_contract_service, contract=None
        )

        # 测试枚举对象
        self.assertEqual(self.dialog._get_enum_value(ContractType.SALES), "sales")
        self.assertEqual(self.dialog._get_enum_value(ContractStatus.DRAFT), "draft")

        # 测试字符串
        self.assertEqual(self.dialog._get_enum_value("test_string"), "test_string")

        # 测试None
        self.assertEqual(self.dialog._get_enum_value(None), "")

    def test_get_contract_data(self):
        """测试获取合同数据"""
        # 创建对话框
        self.dialog = ContractEditDialogTTK(
            self.root, self.mock_contract_service, contract=None
        )

        # 设置合同数据
        test_data = {"party_name": "测试客户", "contract_amount": 100000.00}
        self.dialog.contract_data = test_data

        # 获取数据
        retrieved_data = self.dialog.get_contract_data()

        # 验证数据
        self.assertEqual(retrieved_data, test_data)

        # 验证返回的是副本
        self.assertIsNot(retrieved_data, self.dialog.contract_data)

    @patch("minicrm.ui.ttk_base.contract_edit_dialog_ttk.BaseDialog.center_on_parent")
    def test_show_modal(self, mock_center):
        """测试模态显示"""
        # 创建对话框
        self.dialog = ContractEditDialogTTK(
            self.root, self.mock_contract_service, contract=None
        )

        # 设置结果
        self.dialog.result = True

        # 模拟wait_window（立即返回）
        with patch.object(self.dialog, "wait_window"):
            result = self.dialog.show_modal()

            # 验证返回结果
            self.assertTrue(result)

            # 验证居中调用
            mock_center.assert_called_once()


class TestContractEditDialogTTKIntegration(unittest.TestCase):
    """合同编辑TTK对话框集成测试类"""

    def setUp(self):
        """测试前准备"""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """测试后清理"""
        self.root.destroy()

    def test_full_create_workflow(self):
        """测试完整的创建工作流程"""
        # 创建模拟服务
        mock_service = Mock()

        # 创建对话框
        dialog = ContractEditDialogTTK(self.root, mock_service, contract=None)

        # 验证初始化
        self.assertIsNotNone(dialog)
        self.assertFalse(dialog.is_edit_mode)

        # 设置表单数据
        dialog.basic_form.set_form_data(
            {
                "party_name": "集成测试客户",
                "contract_type": "sales",
                "contract_status": "draft",
            }
        )

        dialog.financial_form.set_form_data(
            {"contract_amount": 200000.00, "currency": "CNY", "payment_terms": 45}
        )

        # 收集数据
        contract_data = dialog._collect_form_data()

        # 验证数据
        self.assertEqual(contract_data["party_name"], "集成测试客户")
        self.assertEqual(contract_data["contract_amount"], 200000.00)

        # 清理
        dialog.destroy()

    def test_full_edit_workflow(self):
        """测试完整的编辑工作流程"""
        # 创建模拟服务
        mock_service = Mock()

        # 创建测试合同
        test_contract = Contract(
            id=1,
            contract_number="EDIT001",
            party_name="编辑测试客户",
            contract_type=ContractType.PURCHASE,
            contract_status=ContractStatus.SIGNED,
            contract_amount=Decimal("150000.00"),
        )

        # 创建对话框
        dialog = ContractEditDialogTTK(self.root, mock_service, contract=test_contract)

        # 验证初始化
        self.assertIsNotNone(dialog)
        self.assertTrue(dialog.is_edit_mode)

        # 验证数据加载
        basic_data = dialog.basic_form.get_form_data()
        self.assertEqual(basic_data["party_name"], "编辑测试客户")
        self.assertEqual(basic_data["contract_type"], "purchase")

        # 清理
        dialog.destroy()


if __name__ == "__main__":
    unittest.main()
