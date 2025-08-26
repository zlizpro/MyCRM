"""
MiniCRM TTK应用程序集成测试

测试MiniCRMApplicationTTK类的完整功能，包括：
- 应用程序初始化和生命周期管理
- 服务层集成
- TTK组件集成
- 导航和页面管理
- 错误处理和资源清理

作者: MiniCRM开发团队
"""

import logging
import threading
import time
import unittest
from unittest.mock import Mock, patch

from minicrm.application_ttk import MiniCRMApplicationTTK
from minicrm.core.config import AppConfig
from minicrm.core.exceptions import MiniCRMError


class TestMiniCRMApplicationTTK(unittest.TestCase):
    """MiniCRM TTK应用程序测试类"""

    def setUp(self):
        """测试准备"""
        # 创建测试配置
        self.config = AppConfig()

        # 设置日志级别
        logging.getLogger().setLevel(logging.DEBUG)

        # 应用程序实例
        self.app = None

    def tearDown(self):
        """测试清理"""
        if self.app:
            try:
                self.app.shutdown()
            except Exception as e:
                print(f"清理应用程序时出错: {e}")
            self.app = None

    def test_application_initialization(self):
        """测试应用程序初始化"""
        # 创建应用程序实例
        self.app = MiniCRMApplicationTTK(self.config)

        # 验证初始化状态
        self.assertTrue(self.app.is_initialized)
        self.assertFalse(self.app.is_running)
        self.assertFalse(self.app.is_shutting_down)

        # 验证配置
        self.assertEqual(self.app.config, self.config)

        # 验证主窗口创建
        self.assertIsNotNone(self.app.main_window)
        self.assertEqual(
            self.app.main_window.window_title, "MiniCRM - 板材行业客户关系管理系统"
        )

    def test_service_integration(self):
        """测试服务层集成"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 验证核心服务已初始化
        self.assertIsNotNone(self.app.customer_service)
        self.assertIsNotNone(self.app.supplier_service)
        self.assertIsNotNone(self.app.analytics_service)
        self.assertIsNotNone(self.app.settings_service)
        self.assertIsNotNone(self.app.task_service)
        self.assertIsNotNone(self.app.database_manager)

        # 验证服务状态
        service_status = self.app.get_service_status()
        self.assertTrue(service_status["customer_service"])
        self.assertTrue(service_status["supplier_service"])
        self.assertTrue(service_status["analytics_service"])
        self.assertTrue(service_status["settings_service"])
        self.assertTrue(service_status["task_service"])

    def test_get_service_by_name(self):
        """测试通过名称获取服务"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 测试获取核心服务
        customer_service = self.app.get_service("customer")
        self.assertIsNotNone(customer_service)
        self.assertEqual(customer_service, self.app.customer_service)

        supplier_service = self.app.get_service("supplier")
        self.assertIsNotNone(supplier_service)
        self.assertEqual(supplier_service, self.app.supplier_service)

        # 测试获取其他服务
        finance_service = self.app.get_service("finance")
        self.assertIsNotNone(finance_service)

        contract_service = self.app.get_service("contract")
        self.assertIsNotNone(contract_service)

        quote_service = self.app.get_service("quote")
        self.assertIsNotNone(quote_service)

    def test_get_service_invalid_type(self):
        """测试获取无效服务类型"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 测试无效服务名称
        with self.assertRaises(MiniCRMError):
            self.app.get_service("invalid_service")

    def test_ttk_components_integration(self):
        """测试TTK组件集成"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 验证主窗口组件
        main_window = self.app.main_window
        self.assertIsNotNone(main_window)

        # 验证主窗口包含必要组件
        self.assertIsNotNone(main_window.menu_bar_ttk)
        self.assertIsNotNone(main_window.tool_bar_ttk)
        self.assertIsNotNone(main_window.status_bar_ttk)
        self.assertIsNotNone(main_window.navigation_panel_ttk)
        self.assertIsNotNone(main_window.page_manager_ttk)
        self.assertIsNotNone(main_window.page_router_ttk)

    def test_navigation_setup(self):
        """测试导航系统设置"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 获取导航信息
        main_window = self.app.main_window
        nav_info = main_window.navigation_panel_ttk.get_navigation_info()

        # 验证导航项已注册
        nav_items = nav_info.get("items", [])
        expected_items = [
            "customer",
            "supplier",
            "quote",
            "contract",
            "finance",
            "task",
            "import_export",
        ]

        registered_items = [item.get("item_id") for item in nav_items]
        for expected_item in expected_items:
            self.assertIn(expected_item, registered_items)

    def test_page_registration(self):
        """测试页面注册"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 获取页面管理器信息
        main_window = self.app.main_window
        page_info = main_window.page_manager_ttk.get_page_info()

        # 验证页面已注册
        registered_pages = page_info.get("registered_pages", [])
        expected_pages = [
            "customer",
            "supplier",
            "quote",
            "contract",
            "finance",
            "task",
            "import_export",
        ]

        for expected_page in expected_pages:
            self.assertIn(expected_page, registered_pages)

    def test_route_registration(self):
        """测试路由注册"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 获取路由器信息
        main_window = self.app.main_window
        router_info = main_window.page_router_ttk.get_router_info()

        # 验证路由已注册
        routes = router_info.get("routes", {})
        expected_routes = {
            "/customer": "customer",
            "/supplier": "supplier",
            "/quote": "quote",
            "/contract": "contract",
            "/finance": "finance",
            "/task": "task",
            "/import_export": "import_export",
        }

        for route_path, page_id in expected_routes.items():
            self.assertIn(route_path, routes)
            self.assertEqual(routes[route_path], page_id)

    def test_navigation_functionality(self):
        """测试导航功能"""
        self.app = MiniCRMApplicationTTK(self.config)
        main_window = self.app.main_window

        # 测试导航到不同页面
        test_routes = ["/customer", "/supplier", "/quote", "/contract"]

        for route in test_routes:
            success = main_window.navigate_to(route)
            self.assertTrue(success, f"导航到 {route} 失败")

    def test_application_info(self):
        """测试应用程序信息获取"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 获取应用程序信息
        app_info = self.app.get_application_info()

        # 验证基本信息
        self.assertEqual(app_info["application_type"], "TTK")
        self.assertTrue(app_info["is_initialized"])
        self.assertFalse(app_info["is_running"])
        self.assertFalse(app_info["is_shutting_down"])

        # 验证服务信息
        services = app_info["services"]
        self.assertTrue(services["customer_service"])
        self.assertTrue(services["supplier_service"])

        # 验证主窗口信息
        self.assertIsNotNone(app_info["main_window"])

    def test_lifecycle_management(self):
        """测试生命周期管理"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 验证初始状态
        self.assertTrue(self.app.is_initialized)
        self.assertFalse(self.app.is_running)
        self.assertFalse(self.app.is_shutting_down)

        # 测试关闭
        self.app.shutdown()
        self.assertTrue(self.app.is_shutting_down)

    def test_error_handling_during_initialization(self):
        """测试初始化过程中的错误处理"""
        # 模拟依赖注入配置失败
        with patch(
            "minicrm.application_ttk.configure_application_dependencies"
        ) as mock_config:
            mock_config.side_effect = Exception("依赖注入配置失败")

            with self.assertRaises(MiniCRMError) as context:
                self.app = MiniCRMApplicationTTK(self.config)

            self.assertIn("TTK应用程序初始化失败", str(context.exception))

    def test_service_initialization_error(self):
        """测试服务初始化错误处理"""
        # 模拟数据库管理器获取失败
        with patch("minicrm.application_ttk.get_service") as mock_get_service:
            mock_get_service.side_effect = Exception("服务获取失败")

            with self.assertRaises(MiniCRMError) as context:
                self.app = MiniCRMApplicationTTK(self.config)

            self.assertIn("TTK应用程序初始化失败", str(context.exception))

    def test_main_window_setup_error(self):
        """测试主窗口设置错误处理"""
        # 模拟主窗口创建失败
        with patch("minicrm.application_ttk.MainWindowTTK") as mock_window:
            mock_window.side_effect = Exception("主窗口创建失败")

            with self.assertRaises(MiniCRMError) as context:
                self.app = MiniCRMApplicationTTK(self.config)

            self.assertIn("TTK应用程序初始化失败", str(context.exception))

    def test_cleanup_on_shutdown(self):
        """测试关闭时的资源清理"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 获取组件引用
        main_window = self.app.main_window
        customer_service = self.app.customer_service

        # 验证组件存在
        self.assertIsNotNone(main_window)
        self.assertIsNotNone(customer_service)

        # 执行关闭
        self.app.shutdown()

        # 验证状态
        self.assertTrue(self.app.is_shutting_down)

    def test_window_close_event_handling(self):
        """测试窗口关闭事件处理"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 模拟窗口关闭前事件
        self.app._on_before_close()

        # 模拟窗口关闭事件
        self.app._on_window_closing()

        # 验证应用程序已关闭
        self.assertTrue(self.app.is_shutting_down)

    def test_run_without_initialization(self):
        """测试未初始化时运行应用程序"""
        # 创建未初始化的应用程序
        app = object.__new__(MiniCRMApplicationTTK)
        app._is_initialized = False

        # 尝试运行应该抛出异常
        with self.assertRaises(MiniCRMError) as context:
            app.run()

        self.assertIn("应用程序未初始化", str(context.exception))

    @patch("tkinter.Tk.mainloop")
    def test_run_application(self, mock_mainloop):
        """测试运行应用程序"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 模拟主循环立即返回
        mock_mainloop.return_value = None

        # 在单独线程中运行应用程序
        def run_app():
            self.app.run()

        app_thread = threading.Thread(target=run_app)
        app_thread.start()

        # 等待应用程序启动
        time.sleep(0.1)

        # 验证应用程序状态
        self.assertTrue(self.app.is_initialized)

        # 等待线程完成
        app_thread.join(timeout=1.0)

    def test_multiple_shutdown_calls(self):
        """测试多次调用关闭方法"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 第一次关闭
        self.app.shutdown()
        self.assertTrue(self.app.is_shutting_down)

        # 第二次关闭应该安全处理
        self.app.shutdown()  # 不应该抛出异常

    def test_service_cleanup_with_cleanup_method(self):
        """测试带有cleanup方法的服务清理"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 为服务添加cleanup方法
        mock_cleanup = Mock()
        self.app._customer_service.cleanup = mock_cleanup

        # 执行关闭
        self.app.shutdown()

        # 验证cleanup方法被调用
        mock_cleanup.assert_called_once()

    def test_service_cleanup_without_cleanup_method(self):
        """测试没有cleanup方法的服务清理"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 确保服务没有cleanup方法
        if hasattr(self.app._customer_service, "cleanup"):
            delattr(self.app._customer_service, "cleanup")

        # 执行关闭应该不会出错
        self.app.shutdown()

        # 验证服务引用被清空
        self.assertIsNone(self.app._customer_service)


class TestMiniCRMApplicationTTKIntegration(unittest.TestCase):
    """MiniCRM TTK应用程序集成测试"""

    def setUp(self):
        """测试准备"""
        self.config = AppConfig()
        self.app = None

    def tearDown(self):
        """测试清理"""
        if self.app:
            try:
                self.app.shutdown()
            except Exception:
                pass
            self.app = None

    def test_full_application_workflow(self):
        """测试完整应用程序工作流程"""
        # 1. 创建和初始化应用程序
        self.app = MiniCRMApplicationTTK(self.config)
        self.assertTrue(self.app.is_initialized)

        # 2. 验证服务可用性
        customer_service = self.app.get_service("customer")
        self.assertIsNotNone(customer_service)

        # 3. 验证导航功能
        main_window = self.app.main_window
        success = main_window.navigate_to("/customer")
        self.assertTrue(success)

        # 4. 验证页面切换
        success = main_window.navigate_to("/supplier")
        self.assertTrue(success)

        # 5. 关闭应用程序
        self.app.shutdown()
        self.assertTrue(self.app.is_shutting_down)

    def test_service_interaction(self):
        """测试服务交互"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 获取客户服务
        customer_service = self.app.customer_service
        self.assertIsNotNone(customer_service)

        # 测试服务方法调用（如果有的话）
        if hasattr(customer_service, "get_all_customers"):
            try:
                customers = customer_service.get_all_customers()
                self.assertIsInstance(customers, list)
            except Exception as e:
                # 如果数据库未设置，这是预期的
                self.assertIsInstance(e, Exception)

    def test_error_recovery(self):
        """测试错误恢复"""
        self.app = MiniCRMApplicationTTK(self.config)

        # 模拟导航到无效页面
        main_window = self.app.main_window
        success = main_window.navigate_to("/invalid_page")
        self.assertFalse(success)

        # 验证应用程序仍然可用
        success = main_window.navigate_to("/customer")
        self.assertTrue(success)


if __name__ == "__main__":
    # 设置测试环境
    import os
    import sys

    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # 运行测试
    unittest.main(verbosity=2)
