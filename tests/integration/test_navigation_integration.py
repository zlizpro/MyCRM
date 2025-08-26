"""TTK导航系统集成测试

测试NavigationRegistryTTK与其他TTK组件的集成，包括：
- 导航注册系统与主窗口的集成
- 页面管理器与导航面板的集成
- 路由系统的完整工作流程

作者: MiniCRM开发团队
"""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch


# 检查tkinter可用性
try:
    root = tk.Tk()
    root.withdraw()
    root.destroy()
    TKINTER_AVAILABLE = True
except Exception:
    TKINTER_AVAILABLE = False

from minicrm.application import MiniCRMApplication
from minicrm.ui.ttk_base.main_window_ttk import MainWindowTTK
from minicrm.ui.ttk_base.navigation_registry_ttk import NavigationRegistryTTK


@unittest.skipUnless(TKINTER_AVAILABLE, "tkinter not available in this environment")
class TestNavigationIntegration(unittest.TestCase):
    """导航系统集成测试"""

    def setUp(self):
        """测试准备"""
        # 创建测试根窗口
        self.root = tk.Tk()
        self.root.withdraw()

        # 创建模拟应用程序
        self.mock_app = Mock(spec=MiniCRMApplication)
        self.mock_app.get_service.return_value = Mock()

    def tearDown(self):
        """测试清理"""
        if self.root:
            self.root.destroy()

    @patch("minicrm.ui.ttk_base.navigation_registry_ttk.DashboardRefactored")
    @patch("minicrm.ui.ttk_base.navigation_registry_ttk.CustomerPanelTTK")
    @patch("minicrm.ui.ttk_base.navigation_registry_ttk.SupplierPanelTTK")
    def test_main_window_navigation_setup(
        self, mock_supplier, mock_customer, mock_dashboard
    ):
        """测试主窗口导航设置"""
        # 模拟页面类
        for mock_class in [mock_supplier, mock_customer, mock_dashboard]:
            mock_class.return_value = Mock()

        # 创建主窗口
        main_window = MainWindowTTK(title="测试窗口")

        # 设置导航注册系统
        main_window.setup_navigation_registry(self.mock_app)

        # 验证导航注册系统已创建
        self.assertIsNotNone(main_window.navigation_registry_ttk)
        self.assertIsInstance(
            main_window.navigation_registry_ttk, NavigationRegistryTTK
        )

    @patch("minicrm.ui.ttk_base.navigation_registry_ttk.register_all_ttk_pages")
    def test_navigation_registry_initialization(self, mock_register_all):
        """测试导航注册系统初始化"""
        # 创建主窗口
        main_window = MainWindowTTK(title="测试窗口")

        # 设置导航注册系统
        main_window.setup_navigation_registry(self.mock_app)

        # 验证register_all_ttk_pages被调用
        mock_register_all.assert_called_once()

        # 验证传递的参数类型正确
        args = mock_register_all.call_args[0]
        self.assertIsInstance(args[0], NavigationRegistryTTK)

    def test_navigation_components_integration(self):
        """测试导航组件集成"""
        # 创建主窗口
        main_window = MainWindowTTK(title="测试窗口")

        # 验证所有必要的TTK组件都已创建
        self.assertIsNotNone(main_window.navigation_panel_ttk)
        self.assertIsNotNone(main_window.page_manager_ttk)
        self.assertIsNotNone(main_window.page_router_ttk)

        # 设置导航注册系统
        main_window.setup_navigation_registry(self.mock_app)

        # 验证导航注册系统与组件正确关联
        registry = main_window.navigation_registry_ttk
        self.assertEqual(registry._page_manager, main_window.page_manager_ttk)
        self.assertEqual(registry._page_router, main_window.page_router_ttk)
        self.assertEqual(registry._navigation_panel, main_window.navigation_panel_ttk)

    def test_navigation_setup_error_handling(self):
        """测试导航设置错误处理"""
        # 创建主窗口但不初始化组件
        main_window = MainWindowTTK(title="测试窗口")

        # 清空必要组件以模拟错误状态
        main_window.page_manager_ttk = None

        # 验证错误处理
        with self.assertRaises(ValueError):
            main_window.setup_navigation_registry(self.mock_app)


if __name__ == "__main__":
    unittest.main()
