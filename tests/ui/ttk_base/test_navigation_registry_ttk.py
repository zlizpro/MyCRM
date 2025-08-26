"""TTK导航注册系统集成测试

测试NavigationRegistryTTK类的各项功能，包括：
- 导航项注册和管理
- 页面路由和切换
- 服务依赖检查
- 导航面板集成
- 页面管理器集成

作者: MiniCRM开发团队
"""

import tkinter as tk
from tkinter import ttk
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
from minicrm.core.exceptions import UIError
from minicrm.ui.ttk_base.navigation_panel import NavigationPanelTTK
from minicrm.ui.ttk_base.navigation_registry_ttk import (
    NavigationItemTTK,
    NavigationRegistryTTK,
    register_all_ttk_pages,
)
from minicrm.ui.ttk_base.page_manager import PageManagerTTK, PageRouterTTK


@unittest.skipUnless(TKINTER_AVAILABLE, "tkinter not available in this environment")
class TestNavigationItemTTK(unittest.TestCase):
    """NavigationItemTTK类测试"""

    def test_navigation_item_creation(self):
        """测试导航项创建"""
        item = NavigationItemTTK(
            name="test_page",
            title="测试页面",
            icon="🧪",
            order=1,
            description="测试页面描述",
        )

        self.assertEqual(item.name, "test_page")
        self.assertEqual(item.title, "测试页面")
        self.assertEqual(item.icon, "🧪")
        self.assertEqual(item.order, 1)
        self.assertEqual(item.description, "测试页面描述")
        self.assertEqual(item.route_path, "/test_page")
        self.assertTrue(item.visible)
        self.assertTrue(item.cache_enabled)
        self.assertFalse(item.preload)

    def test_navigation_item_with_custom_route(self):
        """测试自定义路由的导航项"""
        item = NavigationItemTTK(
            name="custom_page",
            title="自定义页面",
            icon="⚙️",
            route_path="/custom/path",
        )

        self.assertEqual(item.route_path, "/custom/path")

    def test_navigation_item_with_service_requirement(self):
        """测试需要服务的导航项"""
        item = NavigationItemTTK(
            name="service_page",
            title="服务页面",
            icon="🔧",
            requires_service="test_service",
        )

        self.assertEqual(item.requires_service, "test_service")


@unittest.skipUnless(TKINTER_AVAILABLE, "tkinter not available in this environment")
class TestNavigationRegistryTTK(unittest.TestCase):
    """NavigationRegistryTTK类测试"""

    def setUp(self):
        """测试准备"""
        # 创建测试根窗口
        self.root = tk.Tk()
        self.root.withdraw()

        # 创建模拟应用程序
        self.mock_app = Mock(spec=MiniCRMApplication)
        self.mock_app.get_service.return_value = Mock()

        # 创建TTK组件
        self.page_manager = PageManagerTTK(container=self.root)
        self.page_router = PageRouterTTK(self.page_manager)
        self.navigation_panel = NavigationPanelTTK(parent=self.root)

        # 创建导航注册系统
        self.registry = NavigationRegistryTTK(
            app=self.mock_app,
            page_manager=self.page_manager,
            page_router=self.page_router,
            navigation_panel=self.navigation_panel,
        )

    def tearDown(self):
        """测试清理"""
        if self.root:
            self.root.destroy()

    def test_registry_initialization(self):
        """测试注册系统初始化"""
        self.assertIsNotNone(self.registry)
        self.assertEqual(self.registry._app, self.mock_app)
        self.assertEqual(self.registry._page_manager, self.page_manager)
        self.assertEqual(self.registry._page_router, self.page_router)
        self.assertEqual(self.registry._navigation_panel, self.navigation_panel)
        self.assertEqual(len(self.registry._navigation_items), 0)

    def test_register_navigation_item_success(self):
        """测试成功注册导航项"""

        # 创建测试页面类
        class TestPage(ttk.Frame):
            def __init__(self, parent):
                super().__init__(parent)

        item = NavigationItemTTK(
            name="test_page",
            title="测试页面",
            icon="🧪",
            widget_class=TestPage,
        )

        # 注册导航项
        self.registry.register_navigation_item(item)

        # 验证注册成功
        self.assertTrue(self.registry.is_page_registered("test_page"))
        self.assertIn("test_page", self.registry.get_registered_pages())

    def test_register_navigation_item_with_service_dependency(self):
        """测试注册需要服务的导航项"""
        # 模拟服务可用
        self.mock_app.get_service.return_value = Mock()

        class TestServicePage(ttk.Frame):
            def __init__(self, parent, service):
                super().__init__(parent)
                self.service = service

        item = NavigationItemTTK(
            name="service_page",
            title="服务页面",
            icon="🔧",
            widget_class=TestServicePage,
            requires_service="test_service",
        )

        # 注册导航项
        self.registry.register_navigation_item(item)

        # 验证注册成功
        self.assertTrue(self.registry.is_page_registered("service_page"))

    def test_register_navigation_item_service_unavailable(self):
        """测试服务不可用时的注册"""
        # 模拟服务不可用
        self.mock_app.get_service.return_value = None

        item = NavigationItemTTK(
            name="unavailable_service_page",
            title="不可用服务页面",
            icon="❌",
            requires_service="unavailable_service",
        )

        # 注册导航项（应该被跳过）
        self.registry.register_navigation_item(item)

        # 验证未注册
        self.assertFalse(self.registry.is_page_registered("unavailable_service_page"))

    def test_navigate_to_existing_page(self):
        """测试导航到存在的页面"""

        # 注册测试页面
        class TestPage(ttk.Frame):
            def __init__(self, parent):
                super().__init__(parent)

        item = NavigationItemTTK(
            name="test_page",
            title="测试页面",
            icon="🧪",
            widget_class=TestPage,
        )
        self.registry.register_navigation_item(item)

        # 模拟页面管理器的navigate_to方法
        with patch.object(
            self.page_manager, "navigate_to", return_value=True
        ) as mock_navigate:
            result = self.registry.navigate_to("test_page")

            self.assertTrue(result)
            mock_navigate.assert_called_once_with("test_page", None)

    def test_navigate_to_nonexistent_page(self):
        """测试导航到不存在的页面"""
        result = self.registry.navigate_to("nonexistent_page")
        self.assertFalse(result)

    def test_get_navigation_structure(self):
        """测试获取导航结构"""
        # 注册多个导航项
        items = [
            NavigationItemTTK(
                name="page1",
                title="页面1",
                icon="1️⃣",
                order=1,
            ),
            NavigationItemTTK(
                name="page2",
                title="页面2",
                icon="2️⃣",
                order=2,
            ),
            NavigationItemTTK(
                name="child_page",
                title="子页面",
                icon="👶",
                parent="page1",
                order=1,
            ),
        ]

        for item in items:
            self.registry.register_navigation_item(item)

        # 获取导航结构
        structure = self.registry.get_navigation_structure()

        # 验证结构
        self.assertEqual(len(structure), 2)  # 两个根级页面
        self.assertEqual(structure[0]["name"], "page1")
        self.assertEqual(structure[1]["name"], "page2")
        self.assertEqual(len(structure[0]["children"]), 1)  # page1有一个子页面
        self.assertEqual(structure[0]["children"][0]["name"], "child_page")

    def test_unregister_page(self):
        """测试注销页面"""

        # 注册测试页面
        class TestPage(ttk.Frame):
            def __init__(self, parent):
                super().__init__(parent)

        item = NavigationItemTTK(
            name="test_page",
            title="测试页面",
            icon="🧪",
            widget_class=TestPage,
        )
        self.registry.register_navigation_item(item)

        # 验证页面已注册
        self.assertTrue(self.registry.is_page_registered("test_page"))

        # 注销页面
        self.registry.unregister_page("test_page")

        # 验证页面已注销
        self.assertFalse(self.registry.is_page_registered("test_page"))

    def test_create_widget_instance_with_special_pages(self):
        """测试特殊页面的组件实例创建"""

        # 测试客户管理页面
        class MockCustomerPanel(ttk.Frame):
            def __init__(self, parent, service):
                super().__init__(parent)
                self.service = service

        # 模拟客户服务
        mock_customer_service = Mock()
        self.mock_app.get_service.side_effect = lambda name: {
            "customer": mock_customer_service
        }.get(name)

        item = NavigationItemTTK(
            name="customers",
            title="客户管理",
            icon="👥",
            widget_class=MockCustomerPanel,
        )

        # 创建组件实例
        widget = self.registry._create_widget_instance(item)

        # 验证实例创建成功
        self.assertIsInstance(widget, MockCustomerPanel)
        self.assertEqual(widget.service, mock_customer_service)

    def test_create_widget_instance_service_unavailable(self):
        """测试服务不可用时的组件创建"""

        class MockServicePanel(ttk.Frame):
            def __init__(self, parent, service):
                super().__init__(parent)

        # 模拟服务不可用
        self.mock_app.get_service.return_value = None

        item = NavigationItemTTK(
            name="customers",
            title="客户管理",
            icon="👥",
            widget_class=MockServicePanel,
        )

        # 创建组件实例应该抛出异常
        with self.assertRaises(UIError):
            self.registry._create_widget_instance(item)

    def test_refresh_navigation_panel(self):
        """测试刷新导航面板"""

        # 注册测试页面
        class TestPage(ttk.Frame):
            def __init__(self, parent):
                super().__init__(parent)

        item = NavigationItemTTK(
            name="test_page",
            title="测试页面",
            icon="🧪",
            widget_class=TestPage,
        )
        self.registry.register_navigation_item(item)

        # 模拟导航面板方法
        with patch.object(self.navigation_panel, "clear_all_items") as mock_clear:
            with patch.object(self.navigation_panel, "add_navigation_item") as mock_add:
                self.registry.refresh_navigation_panel()

                mock_clear.assert_called_once()
                mock_add.assert_called_once()

    def test_update_navigation_item_state(self):
        """测试更新导航项状态"""

        # 注册测试页面
        class TestPage(ttk.Frame):
            def __init__(self, parent):
                super().__init__(parent)

        item = NavigationItemTTK(
            name="test_page",
            title="测试页面",
            icon="🧪",
            widget_class=TestPage,
        )
        self.registry.register_navigation_item(item)

        # 模拟导航面板的update_item_state方法
        with patch.object(self.navigation_panel, "update_item_state") as mock_update:
            self.registry.update_navigation_item_state("test_page", "active")

            mock_update.assert_called_once_with("test_page", "active")


@unittest.skipUnless(TKINTER_AVAILABLE, "tkinter not available in this environment")
class TestRegisterAllTTKPages(unittest.TestCase):
    """测试注册所有TTK页面功能"""

    def setUp(self):
        """测试准备"""
        # 创建测试根窗口
        self.root = tk.Tk()
        self.root.withdraw()

        # 创建模拟应用程序
        self.mock_app = Mock(spec=MiniCRMApplication)

        # 模拟所有服务都可用
        self.mock_app.get_service.return_value = Mock()

        # 创建TTK组件
        self.page_manager = PageManagerTTK(container=self.root)
        self.page_router = PageRouterTTK(self.page_manager)
        self.navigation_panel = NavigationPanelTTK(parent=self.root)

        # 创建导航注册系统
        self.registry = NavigationRegistryTTK(
            app=self.mock_app,
            page_manager=self.page_manager,
            page_router=self.page_router,
            navigation_panel=self.navigation_panel,
        )

    def tearDown(self):
        """测试清理"""
        if self.root:
            self.root.destroy()

    @patch("minicrm.ui.ttk_base.navigation_registry_ttk.DashboardRefactored")
    @patch("minicrm.ui.ttk_base.navigation_registry_ttk.CustomerPanelTTK")
    @patch("minicrm.ui.ttk_base.navigation_registry_ttk.SupplierPanelTTK")
    @patch("minicrm.ui.ttk_base.navigation_registry_ttk.FinancePanelTTK")
    @patch("minicrm.ui.ttk_base.navigation_registry_ttk.ContractPanelTTK")
    @patch("minicrm.ui.ttk_base.navigation_registry_ttk.QuotePanelTTK")
    @patch("minicrm.ui.ttk_base.navigation_registry_ttk.TaskPanelTTK")
    @patch("minicrm.ui.ttk_base.navigation_registry_ttk.ImportExportPanelTTK")
    @patch("minicrm.ui.ttk_base.navigation_registry_ttk.SettingsPanel")
    def test_register_all_ttk_pages_success(self, *mock_classes):
        """测试成功注册所有TTK页面"""
        # 模拟所有页面类
        for mock_class in mock_classes:
            mock_class.return_value = Mock()

        # 注册所有页面
        register_all_ttk_pages(self.registry)

        # 验证所有页面都已注册
        expected_pages = [
            "dashboard",
            "customers",
            "suppliers",
            "finance",
            "contracts",
            "quotes",
            "tasks",
            "import_export",
            "settings",
        ]

        registered_pages = self.registry.get_registered_pages()
        for page in expected_pages:
            self.assertIn(page, registered_pages)

    @patch("minicrm.ui.ttk_base.navigation_registry_ttk.CustomerPanelTTK")
    def test_register_all_ttk_pages_with_service_failure(self, mock_customer_panel):
        """测试服务不可用时的页面注册"""

        # 模拟客户服务不可用
        def mock_get_service(service_name):
            if service_name == "customer":
                return None
            return Mock()

        self.mock_app.get_service.side_effect = mock_get_service

        # 注册页面（客户页面应该被跳过）
        with patch("minicrm.ui.ttk_base.navigation_registry_ttk.DashboardRefactored"):
            with patch("minicrm.ui.ttk_base.navigation_registry_ttk.SupplierPanelTTK"):
                register_all_ttk_pages(self.registry)

        # 验证客户页面未注册
        self.assertFalse(self.registry.is_page_registered("customers"))


if __name__ == "__main__":
    unittest.main()
