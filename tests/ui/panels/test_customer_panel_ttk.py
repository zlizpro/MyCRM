"""MiniCRM 客户管理面板TTK组件测试

测试CustomerPanelTTK组件的功能，包括：
- 组件初始化和UI创建
- 数据加载和显示
- 搜索和筛选功能
- 客户CRUD操作
- 批量操作功能
- 事件处理和回调

设计原则：
- 使用unittest框架进行单元测试
- 模拟CustomerServiceFacade避免数据库依赖
- 测试UI组件的创建和交互
- 验证业务逻辑的正确性
"""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from minicrm.models.customer import CustomerLevel, CustomerType, IndustryType
from minicrm.ui.panels.customer_panel_ttk import CustomerPanelTTK


class TestCustomerPanelTTK(unittest.TestCase):
    """客户管理面板TTK组件测试类"""

    def setUp(self):
        """测试准备"""
        # 创建根窗口（隐藏）
        self.root = tk.Tk()
        self.root.withdraw()

        # 创建模拟的客户服务
        self.mock_customer_service = Mock()

        # 模拟客户数据
        self.sample_customers = [
            {
                "id": 1,
                "name": "测试客户1",
                "phone": "13800138001",
                "company_name": "测试公司1",
                "customer_level": CustomerLevel.NORMAL.value,
                "customer_type": CustomerType.ENTERPRISE.value,
                "industry_type": IndustryType.FURNITURE.value,
                "created_at": "2024-01-01 10:00:00",
            },
            {
                "id": 2,
                "name": "测试客户2",
                "phone": "13800138002",
                "company_name": "测试公司2",
                "customer_level": CustomerLevel.VIP.value,
                "customer_type": CustomerType.INDIVIDUAL.value,
                "industry_type": IndustryType.RETAIL.value,
                "created_at": "2024-01-02 11:00:00",
            },
        ]

        # 配置模拟服务的返回值
        self.mock_customer_service.search_customers.return_value = (
            self.sample_customers,
            len(self.sample_customers),
        )

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "customer_panel"):
            self.customer_panel.cleanup()
        self.root.destroy()

    def test_panel_initialization(self):
        """测试面板初始化"""
        # 创建客户管理面板
        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 验证面板创建成功
        self.assertIsNotNone(self.customer_panel)
        self.assertEqual(
            self.customer_panel._customer_service, self.mock_customer_service
        )

        # 验证初始状态
        self.assertEqual(self.customer_panel._search_query, "")
        self.assertEqual(self.customer_panel._current_filters, {})
        self.assertIsNone(self.customer_panel._selected_customer_id)

    def test_ui_components_creation(self):
        """测试UI组件创建"""
        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 验证主要UI组件存在
        self.assertIsNotNone(self.customer_panel._search_entry)
        self.assertIsNotNone(self.customer_panel._filter_frame)
        self.assertIsNotNone(self.customer_panel._customer_table)
        self.assertIsNotNone(self.customer_panel._detail_panel)
        self.assertIsNotNone(self.customer_panel._splitter)

        # 验证按钮存在
        self.assertIsNotNone(self.customer_panel._add_button)
        self.assertIsNotNone(self.customer_panel._edit_button)
        self.assertIsNotNone(self.customer_panel._delete_button)
        self.assertIsNotNone(self.customer_panel._batch_delete_button)
        self.assertIsNotNone(self.customer_panel._export_button)
        self.assertIsNotNone(self.customer_panel._refresh_button)

        # 验证筛选器存在
        self.assertIsNotNone(self.customer_panel._level_filter)
        self.assertIsNotNone(self.customer_panel._type_filter)
        self.assertIsNotNone(self.customer_panel._industry_filter)

    def test_data_loading(self):
        """测试数据加载"""
        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 验证服务被调用
        self.mock_customer_service.search_customers.assert_called()

        # 验证数据被加载
        self.assertEqual(len(self.customer_panel._current_customers), 2)
        self.assertEqual(self.customer_panel._current_customers[0]["name"], "测试客户1")

    def test_search_functionality(self):
        """测试搜索功能"""
        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 模拟搜索输入
        self.customer_panel._search_entry.insert(0, "测试客户1")

        # 触发搜索事件
        event = Mock()
        self.customer_panel._on_search_changed(event)

        # 验证搜索查询被设置
        self.assertEqual(self.customer_panel._search_query, "测试客户1")

    def test_filter_functionality(self):
        """测试筛选功能"""
        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 设置筛选器值
        self.customer_panel._level_filter.set(CustomerLevel.VIP.value)
        self.customer_panel._type_filter.set(CustomerType.ENTERPRISE.value)

        # 触发筛选事件
        event = Mock()
        self.customer_panel._on_filter_changed(event)

        # 验证筛选条件被构建
        filters = self.customer_panel._build_filters()
        self.assertEqual(filters["customer_level"], CustomerLevel.VIP.value)
        self.assertEqual(filters["customer_type"], CustomerType.ENTERPRISE.value)

    def test_customer_selection(self):
        """测试客户选择"""
        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 模拟客户选择
        selected_data = [self.sample_customers[0]]
        self.customer_panel._on_customer_selected(selected_data)

        # 验证选择状态
        self.assertEqual(self.customer_panel._selected_customer_id, 1)

        # 验证按钮状态更新
        self.assertEqual(self.customer_panel._edit_button.cget("state"), "normal")
        self.assertEqual(self.customer_panel._delete_button.cget("state"), "normal")

    def test_button_states_update(self):
        """测试按钮状态更新"""
        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 测试无选择状态
        self.customer_panel._update_button_states(False, False)
        self.assertEqual(self.customer_panel._edit_button.cget("state"), "disabled")
        self.assertEqual(self.customer_panel._delete_button.cget("state"), "disabled")
        self.assertEqual(
            self.customer_panel._batch_delete_button.cget("state"), "disabled"
        )

        # 测试单选状态
        self.customer_panel._update_button_states(True, False)
        self.assertEqual(self.customer_panel._edit_button.cget("state"), "normal")
        self.assertEqual(self.customer_panel._delete_button.cget("state"), "normal")
        self.assertEqual(
            self.customer_panel._batch_delete_button.cget("state"), "disabled"
        )

        # 测试多选状态
        self.customer_panel._update_button_states(True, True)
        self.assertEqual(self.customer_panel._edit_button.cget("state"), "normal")
        self.assertEqual(self.customer_panel._delete_button.cget("state"), "normal")
        self.assertEqual(
            self.customer_panel._batch_delete_button.cget("state"), "normal"
        )

    @patch(
        "minicrm.ui.panels.customer_edit_dialog_ttk.CustomerEditDialogTTK.show_new_customer_dialog"
    )
    def test_add_customer_action(self, mock_dialog):
        """测试新增客户操作"""
        mock_dialog.return_value = 123  # 模拟返回新客户ID

        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 触发新增客户操作
        self.customer_panel._on_add_customer()

        # 验证对话框被调用
        mock_dialog.assert_called_once()

    @patch(
        "minicrm.ui.panels.customer_edit_dialog_ttk.CustomerEditDialogTTK.show_edit_customer_dialog"
    )
    def test_edit_customer_action(self, mock_dialog):
        """测试编辑客户操作"""
        mock_dialog.return_value = 1  # 模拟返回客户ID

        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 设置选中的客户
        self.customer_panel._selected_customer_id = 1

        # 触发编辑客户操作
        self.customer_panel._on_edit_customer()

        # 验证对话框被调用
        mock_dialog.assert_called_once()

    @patch("tkinter.messagebox.askyesno")
    def test_delete_customer_action(self, mock_messagebox):
        """测试删除客户操作"""
        mock_messagebox.return_value = True  # 用户确认删除
        self.mock_customer_service.delete_customer.return_value = True

        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 设置选中的客户
        self.customer_panel._selected_customer_id = 1

        # 触发删除客户操作
        self.customer_panel._on_delete_customer()

        # 验证确认对话框被调用
        mock_messagebox.assert_called_once()

        # 验证删除服务被调用
        self.mock_customer_service.delete_customer.assert_called_with(1)

    def test_refresh_action(self):
        """测试刷新操作"""
        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 重置模拟调用计数
        self.mock_customer_service.search_customers.reset_mock()

        # 触发刷新操作
        self.customer_panel._on_refresh()

        # 验证数据重新加载
        self.mock_customer_service.search_customers.assert_called()

    def test_status_bar_update(self):
        """测试状态栏更新"""
        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 测试状态栏更新
        self.customer_panel._update_status_bar(2, 2)
        self.assertEqual(self.customer_panel._status_label.cget("text"), "共 2 个客户")

        self.customer_panel._update_status_bar(1, 2)
        self.assertEqual(
            self.customer_panel._status_label.cget("text"), "显示 1 / 2 个客户"
        )

    def test_selection_status_update(self):
        """测试选择状态更新"""
        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 测试选择状态更新
        self.customer_panel._update_selection_status(0)
        self.assertEqual(self.customer_panel._selection_label.cget("text"), "")

        self.customer_panel._update_selection_status(1)
        self.assertEqual(
            self.customer_panel._selection_label.cget("text"), "已选择 1 个客户"
        )

        self.customer_panel._update_selection_status(3)
        self.assertEqual(
            self.customer_panel._selection_label.cget("text"), "已选择 3 个客户"
        )

    def test_public_interface_methods(self):
        """测试公共接口方法"""
        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 测试刷新数据方法
        self.mock_customer_service.search_customers.reset_mock()
        self.customer_panel.refresh_data()
        self.mock_customer_service.search_customers.assert_called()

        # 测试选中客户方法
        self.customer_panel.select_customer(1)
        self.assertEqual(self.customer_panel.get_selected_customer_id(), 1)

        # 测试获取选中客户ID方法
        self.customer_panel._selected_customer_id = 2
        self.assertEqual(self.customer_panel.get_selected_customer_id(), 2)

    def test_cleanup(self):
        """测试资源清理"""
        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 设置一些状态
        self.customer_panel._search_timer_id = "test_timer"
        self.customer_panel._selected_customer_id = 1

        # 执行清理
        self.customer_panel.cleanup()

        # 验证清理效果（这里主要是确保不抛出异常）
        self.assertIsNotNone(self.customer_panel)


class TestCustomerPanelTTKIntegration(unittest.TestCase):
    """客户管理面板TTK组件集成测试类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()

        # 创建更真实的模拟服务
        self.mock_customer_service = Mock()

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "customer_panel"):
            self.customer_panel.cleanup()
        self.root.destroy()

    def test_complete_workflow(self):
        """测试完整工作流程"""
        # 模拟服务返回
        customers = [
            {
                "id": 1,
                "name": "集成测试客户",
                "phone": "13800138000",
                "company_name": "集成测试公司",
                "customer_level": CustomerLevel.NORMAL.value,
                "customer_type": CustomerType.ENTERPRISE.value,
                "industry_type": IndustryType.FURNITURE.value,
                "created_at": "2024-01-01 10:00:00",
            }
        ]
        self.mock_customer_service.search_customers.return_value = (customers, 1)
        self.mock_customer_service.get_customer_by_id.return_value = customers[0]

        # 创建面板
        self.customer_panel = CustomerPanelTTK(
            parent=self.root,
            customer_service=self.mock_customer_service,
        )

        # 验证初始化
        self.assertIsNotNone(self.customer_panel)
        self.assertEqual(len(self.customer_panel._current_customers), 1)

        # 模拟选择客户
        self.customer_panel._on_customer_selected(customers)

        # 验证选择状态
        self.assertEqual(self.customer_panel._selected_customer_id, 1)

        # 验证UI状态
        self.assertEqual(self.customer_panel._edit_button.cget("state"), "normal")


if __name__ == "__main__":
    unittest.main()
