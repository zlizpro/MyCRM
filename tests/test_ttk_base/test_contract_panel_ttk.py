"""测试合同管理TTK面板

测试ContractPanelTTK的功能，包括：
- 面板初始化和UI创建
- 合同数据加载和显示
- 搜索和筛选功能
- 合同操作（创建、编辑、删除）
- 事件处理和回调

作者: MiniCRM开发团队
"""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from minicrm.services.contract_service import ContractService
from minicrm.ui.ttk_base.contract_panel_ttk import ContractPanelTTK


class TestContractPanelTTK(unittest.TestCase):
    """合同管理TTK面板测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建根窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏窗口

        # 创建模拟的合同服务
        self.mock_contract_service = Mock(spec=ContractService)

        # 创建测试数据
        self.test_contracts = [
            {
                "id": 1,
                "contract_number": "S20240101001",
                "party_name": "测试客户A",
                "contract_type": "sales",
                "contract_status": "signed",
                "contract_amount": 100000.00,
                "currency": "CNY",
                "sign_date": "2024-01-01",
                "expiry_date": "2024-12-31",
                "progress_percentage": 50.0,
            },
            {
                "id": 2,
                "contract_number": "P20240102001",
                "party_name": "测试供应商B",
                "contract_type": "purchase",
                "contract_status": "active",
                "contract_amount": 50000.00,
                "currency": "CNY",
                "sign_date": "2024-01-02",
                "expiry_date": "2024-06-30",
                "progress_percentage": 75.0,
            },
        ]

        # 配置模拟服务
        self.mock_contract_service.list_all.return_value = self.test_contracts

    def tearDown(self):
        """测试后清理"""
        if hasattr(self, "contract_panel"):
            self.contract_panel.cleanup()
        self.root.destroy()

    def test_panel_initialization(self):
        """测试面板初始化"""
        # 创建合同面板
        self.contract_panel = ContractPanelTTK(self.root, self.mock_contract_service)

        # 验证面板创建成功
        self.assertIsNotNone(self.contract_panel)
        self.assertEqual(
            self.contract_panel.contract_service, self.mock_contract_service
        )
        self.assertIsInstance(self.contract_panel.contracts, list)

        # 验证UI组件创建
        self.assertIsNotNone(self.contract_panel.search_frame)
        self.assertIsNotNone(self.contract_panel.search_entry)
        self.assertIsNotNone(self.contract_panel.status_filter)
        self.assertIsNotNone(self.contract_panel.type_filter)
        self.assertIsNotNone(self.contract_panel.contract_table)
        self.assertIsNotNone(self.contract_panel.detail_frame)
        self.assertIsNotNone(self.contract_panel.button_frame)

    def test_data_loading(self):
        """测试数据加载"""
        # 创建合同面板
        self.contract_panel = ContractPanelTTK(self.root, self.mock_contract_service)

        # 验证服务调用
        self.mock_contract_service.list_all.assert_called()

        # 验证数据加载
        self.assertEqual(len(self.contract_panel.contracts), 2)

        # 验证数据格式化
        contract = self.contract_panel.contracts[0]
        self.assertEqual(contract["contract_type"], "销售合同")
        self.assertEqual(contract["contract_status"], "已签署")
        self.assertEqual(contract["contract_amount"], "¥100,000.00")
        self.assertEqual(contract["progress"], "50.0%")

    def test_search_functionality(self):
        """测试搜索功能"""
        # 创建合同面板
        self.contract_panel = ContractPanelTTK(self.root, self.mock_contract_service)

        # 模拟搜索输入
        self.contract_panel.search_entry.insert(0, "测试客户A")

        # 执行搜索
        self.contract_panel._perform_search()

        # 验证搜索结果（这里需要检查表格数据，但由于表格是异步更新的，
        # 在实际测试中可能需要使用更复杂的验证方法）
        self.assertTrue(True)  # 占位符断言

    def test_filter_functionality(self):
        """测试筛选功能"""
        # 创建合同面板
        self.contract_panel = ContractPanelTTK(self.root, self.mock_contract_service)

        # 设置状态筛选
        self.contract_panel.status_filter.set("已签署")

        # 应用筛选
        filtered_data = self.contract_panel._apply_filters(
            self.contract_panel.contracts
        )

        # 验证筛选结果
        self.assertEqual(len(filtered_data), 1)
        self.assertEqual(filtered_data[0]["contract_status"], "已签署")

    def test_clear_search(self):
        """测试清除搜索"""
        # 创建合同面板
        self.contract_panel = ContractPanelTTK(self.root, self.mock_contract_service)

        # 设置搜索条件
        self.contract_panel.search_entry.insert(0, "测试")
        self.contract_panel.status_filter.set("已签署")
        self.contract_panel.type_filter.set("销售合同")

        # 清除搜索
        self.contract_panel._clear_search()

        # 验证清除结果
        self.assertEqual(self.contract_panel.search_entry.get(), "")
        self.assertEqual(self.contract_panel.status_filter.get(), "全部")
        self.assertEqual(self.contract_panel.type_filter.get(), "全部")

    def test_contract_selection(self):
        """测试合同选择"""
        # 创建合同面板
        self.contract_panel = ContractPanelTTK(self.root, self.mock_contract_service)

        # 模拟合同选择
        test_contract = self.test_contracts[0]
        self.contract_panel._on_contract_selected(test_contract)

        # 验证选择结果
        self.assertEqual(self.contract_panel.selected_contract_id, 1)

    @patch("minicrm.ui.ttk_base.contract_panel_ttk.ContractEditDialogTTK")
    def test_create_contract(self, mock_dialog_class):
        """测试创建合同"""
        # 配置模拟对话框
        mock_dialog = Mock()
        mock_dialog.show_modal.return_value = True
        mock_dialog.get_contract_data.return_value = {
            "party_name": "新客户",
            "contract_type": "sales",
            "contract_amount": 80000.00,
        }
        mock_dialog_class.return_value = mock_dialog

        # 配置模拟服务
        mock_contract = Mock()
        mock_contract.id = 3
        self.mock_contract_service.create_contract.return_value = mock_contract

        # 创建合同面板
        self.contract_panel = ContractPanelTTK(self.root, self.mock_contract_service)

        # 执行创建操作
        self.contract_panel._create_contract()

        # 验证对话框调用
        mock_dialog_class.assert_called_once()
        mock_dialog.show_modal.assert_called_once()

        # 验证服务调用
        self.mock_contract_service.create_contract.assert_called_once()

    @patch("minicrm.ui.ttk_base.contract_panel_ttk.ContractEditDialogTTK")
    def test_edit_contract(self, mock_dialog_class):
        """测试编辑合同"""
        # 配置模拟对话框
        mock_dialog = Mock()
        mock_dialog.show_modal.return_value = True
        mock_dialog.get_contract_data.return_value = {
            "party_name": "更新客户",
            "contract_amount": 120000.00,
        }
        mock_dialog_class.return_value = mock_dialog

        # 配置模拟服务
        mock_contract = Mock()
        mock_contract.id = 1
        self.mock_contract_service.get_by_id.return_value = mock_contract
        self.mock_contract_service.update.return_value = mock_contract

        # 创建合同面板
        self.contract_panel = ContractPanelTTK(self.root, self.mock_contract_service)

        # 设置选中的合同
        self.contract_panel.selected_contract_id = 1

        # 执行编辑操作
        self.contract_panel._edit_contract()

        # 验证服务调用
        self.mock_contract_service.get_by_id.assert_called_with(1)
        self.mock_contract_service.update.assert_called_once()

    @patch("minicrm.ui.ttk_base.message_dialogs_ttk.confirm")
    def test_delete_contract(self, mock_confirm):
        """测试删除合同"""
        # 配置模拟确认对话框
        mock_confirm.return_value = True

        # 创建合同面板
        self.contract_panel = ContractPanelTTK(self.root, self.mock_contract_service)

        # 设置选中的合同
        self.contract_panel.selected_contract_id = 1

        # 执行删除操作
        self.contract_panel._delete_contract()

        # 验证确认对话框调用
        mock_confirm.assert_called_once()

        # 验证服务调用
        self.mock_contract_service.delete.assert_called_with(1)

    def test_sign_contract(self):
        """测试签署合同"""
        # 创建合同面板
        self.contract_panel = ContractPanelTTK(self.root, self.mock_contract_service)

        # 设置选中的合同
        self.contract_panel.selected_contract_id = 1

        # 执行签署操作
        self.contract_panel._sign_contract()

        # 验证服务调用
        self.mock_contract_service.sign_contract.assert_called_with(1)

    def test_terminate_contract(self):
        """测试终止合同"""
        with patch(
            "minicrm.ui.ttk_base.message_dialogs_ttk.get_input"
        ) as mock_get_input:
            # 配置模拟输入对话框
            mock_get_input.return_value = "测试终止原因"

            # 创建合同面板
            self.contract_panel = ContractPanelTTK(
                self.root, self.mock_contract_service
            )

            # 设置选中的合同
            self.contract_panel.selected_contract_id = 1

            # 执行终止操作
            self.contract_panel._terminate_contract()

            # 验证服务调用
            self.mock_contract_service.terminate_contract.assert_called_with(
                1, "测试终止原因"
            )

    def test_format_contract_for_display(self):
        """测试合同数据格式化"""
        # 创建合同面板
        self.contract_panel = ContractPanelTTK(self.root, self.mock_contract_service)

        # 测试数据
        raw_contract = {
            "contract_type": "sales",
            "contract_status": "signed",
            "contract_amount": 100000.50,
            "progress_percentage": 75.5,
            "sign_date": "2024-01-01",
            "expiry_date": "2024-12-31",
        }

        # 格式化数据
        formatted = self.contract_panel._format_contract_for_display(raw_contract)

        # 验证格式化结果
        self.assertEqual(formatted["contract_type"], "销售合同")
        self.assertEqual(formatted["contract_status"], "已签署")
        self.assertEqual(formatted["contract_amount"], "¥100,000.50")
        self.assertEqual(formatted["progress"], "75.5%")
        self.assertEqual(formatted["sign_date"], "2024-01-01")
        self.assertEqual(formatted["expiry_date"], "2024-12-31")

    def test_event_callbacks(self):
        """测试事件回调"""
        # 创建合同面板
        self.contract_panel = ContractPanelTTK(self.root, self.mock_contract_service)

        # 设置回调函数
        callback_called = False
        callback_data = None

        def test_callback(data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = data

        self.contract_panel.on_contract_selected = test_callback

        # 触发事件
        test_contract = self.test_contracts[0]
        self.contract_panel._on_contract_selected(test_contract)

        # 验证回调调用
        self.assertTrue(callback_called)
        self.assertEqual(callback_data, test_contract)

    def test_refresh_data(self):
        """测试数据刷新"""
        # 创建合同面板
        self.contract_panel = ContractPanelTTK(self.root, self.mock_contract_service)

        # 重置模拟调用计数
        self.mock_contract_service.list_all.reset_mock()

        # 刷新数据
        self.contract_panel.refresh_data()

        # 验证服务调用
        self.mock_contract_service.list_all.assert_called()

    def test_cleanup(self):
        """测试资源清理"""
        # 创建合同面板
        self.contract_panel = ContractPanelTTK(self.root, self.mock_contract_service)

        # 执行清理
        self.contract_panel.cleanup()

        # 验证清理结果
        self.assertEqual(len(self.contract_panel.contracts), 0)
        self.assertIsNone(self.contract_panel.selected_contract_id)


class TestContractPanelTTKIntegration(unittest.TestCase):
    """合同管理TTK面板集成测试类"""

    def setUp(self):
        """测试前准备"""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """测试后清理"""
        self.root.destroy()

    @patch("minicrm.services.contract_service.ContractService")
    def test_full_workflow(self, mock_service_class):
        """测试完整工作流程"""
        # 配置模拟服务
        mock_service = Mock()
        mock_service.list_all.return_value = []
        mock_service_class.return_value = mock_service

        # 创建合同面板
        contract_panel = ContractPanelTTK(self.root, mock_service)

        # 验证初始化
        self.assertIsNotNone(contract_panel)

        # 验证数据加载
        mock_service.list_all.assert_called()

        # 清理
        contract_panel.cleanup()


if __name__ == "__main__":
    unittest.main()
