"""
MiniCRM TTK应用程序基本功能测试

测试TTK应用程序的基本结构和功能，使用模拟服务避免依赖注入问题。

作者: MiniCRM开发团队
"""

import unittest
from unittest.mock import Mock, patch

from minicrm.core.config import AppConfig


class TestMiniCRMApplicationTTKBasic(unittest.TestCase):
    """MiniCRM TTK应用程序基本功能测试"""

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

    @patch("minicrm.application_ttk.configure_application_dependencies")
    @patch("minicrm.application_ttk.get_service")
    @patch("minicrm.application_ttk.get_global_event_manager")
    @patch("minicrm.application_ttk.TTKThemeManager")
    @patch("minicrm.application_ttk.TTKErrorHandler")
    def test_application_creation_with_mocked_services(
        self,
        mock_error_handler,
        mock_theme_manager,
        mock_event_manager,
        mock_get_service,
        mock_configure,
    ):
        """测试使用模拟服务创建应用程序"""
        # 模拟依赖注入配置
        mock_configure.return_value = None

        # 模拟TTK组件
        mock_event_manager.return_value = Mock()
        mock_theme_manager_instance = Mock()
        mock_theme_manager_instance.set_theme = Mock()
        mock_theme_manager.return_value = mock_theme_manager_instance
        mock_error_handler.return_value = Mock()

        # 创建模拟服务
        mock_database_manager = Mock()
        mock_database_manager.initialize_database.return_value = None

        mock_customer_service = Mock()
        mock_supplier_service = Mock()
        mock_analytics_service = Mock()
        mock_settings_service = Mock()
        mock_task_service = Mock()

        # 配置get_service返回值
        def get_service_side_effect(service_type):
            from minicrm.core.interfaces.service_interfaces import (
                IAnalyticsService,
                ICustomerService,
                ISettingsService,
                ISupplierService,
                ITaskService,
            )
            from minicrm.data.database import DatabaseManager

            if service_type == DatabaseManager:
                return mock_database_manager
            if service_type == ICustomerService:
                return mock_customer_service
            if service_type == ISupplierService:
                return mock_supplier_service
            if service_type == IAnalyticsService:
                return mock_analytics_service
            if service_type == ISettingsService:
                return mock_settings_service
            if service_type == ITaskService:
                return mock_task_service
            return Mock()

        mock_get_service.side_effect = get_service_side_effect

        # 模拟TTK组件
        with patch("minicrm.application_ttk.MainWindowTTK") as mock_main_window:
            mock_window_instance = Mock()
            mock_main_window.return_value = mock_window_instance

            # 模拟主窗口方法
            mock_window_instance.add_event_handler = Mock()
            mock_window_instance.register_page = Mock()
            mock_window_instance.add_navigation_item = Mock()
            mock_window_instance.register_route = Mock()
            mock_window_instance.navigate_to = Mock(return_value=True)
            mock_window_instance.set_status_text = Mock()

            # 创建应用程序
            from minicrm.application_ttk import MiniCRMApplicationTTK

            self.app = MiniCRMApplicationTTK(self.config)

            # 验证应用程序创建成功
            self.assertTrue(self.app.is_initialized)
            self.assertFalse(self.app.is_running)
            self.assertFalse(self.app.is_shutting_down)

            # 验证服务已设置
            self.assertEqual(self.app.customer_service, mock_customer_service)
            self.assertEqual(self.app.supplier_service, mock_supplier_service)
            self.assertEqual(self.app.analytics_service, mock_analytics_service)
            self.assertEqual(self.app.settings_service, mock_settings_service)
            self.assertEqual(self.app.task_service, mock_task_service)

            # 验证主窗口已创建
            self.assertIsNotNone(self.app.main_window)

            # 验证页面注册被调用
            self.assertTrue(mock_window_instance.register_page.called)

            # 验证导航项添加被调用
            self.assertTrue(mock_window_instance.add_navigation_item.called)

            # 验证路由注册被调用
            self.assertTrue(mock_window_instance.register_route.called)

    @patch("minicrm.application_ttk.configure_application_dependencies")
    @patch("minicrm.application_ttk.get_service")
    def test_service_status_reporting(self, mock_get_service, mock_configure):
        """测试服务状态报告"""
        # 设置模拟
        mock_configure.return_value = None
        mock_get_service.return_value = Mock()

        with patch("minicrm.application_ttk.MainWindowTTK"):
            from minicrm.application_ttk import MiniCRMApplicationTTK

            self.app = MiniCRMApplicationTTK(self.config)

            # 获取服务状态
            status = self.app.get_service_status()

            # 验证状态结构
            self.assertIsInstance(status, dict)
            self.assertIn("customer_service", status)
            self.assertIn("supplier_service", status)
            self.assertIn("analytics_service", status)
            self.assertIn("settings_service", status)
            self.assertIn("task_service", status)

            # 验证所有服务都已初始化
            for service_name, service_status in status.items():
                self.assertTrue(service_status, f"服务 {service_name} 未初始化")

    @patch("minicrm.application_ttk.configure_application_dependencies")
    @patch("minicrm.application_ttk.get_service")
    def test_application_info(self, mock_get_service, mock_configure):
        """测试应用程序信息获取"""
        # 设置模拟
        mock_configure.return_value = None
        mock_get_service.return_value = Mock()

        with patch("minicrm.application_ttk.MainWindowTTK") as mock_main_window:
            mock_window_instance = Mock()
            mock_main_window.return_value = mock_window_instance
            mock_window_instance.get_main_window_info.return_value = {"test": "info"}

            from minicrm.application_ttk import MiniCRMApplicationTTK

            self.app = MiniCRMApplicationTTK(self.config)

            # 获取应用程序信息
            info = self.app.get_application_info()

            # 验证信息结构
            self.assertIsInstance(info, dict)
            self.assertEqual(info["application_type"], "TTK")
            self.assertTrue(info["is_initialized"])
            self.assertFalse(info["is_running"])
            self.assertFalse(info["is_shutting_down"])
            self.assertIsInstance(info["services"], dict)
            self.assertIsNotNone(info["main_window"])

    @patch("minicrm.application_ttk.configure_application_dependencies")
    @patch("minicrm.application_ttk.get_service")
    def test_shutdown_functionality(self, mock_get_service, mock_configure):
        """测试关闭功能"""
        # 设置模拟
        mock_configure.return_value = None
        mock_get_service.return_value = Mock()

        with patch("minicrm.application_ttk.MainWindowTTK") as mock_main_window:
            mock_window_instance = Mock()
            mock_main_window.return_value = mock_window_instance
            mock_window_instance.cleanup = Mock()

            from minicrm.application_ttk import MiniCRMApplicationTTK

            self.app = MiniCRMApplicationTTK(self.config)

            # 验证初始状态
            self.assertTrue(self.app.is_initialized)
            self.assertFalse(self.app.is_shutting_down)

            # 执行关闭
            self.app.shutdown()

            # 验证关闭状态
            self.assertTrue(self.app.is_shutting_down)

            # 验证清理方法被调用
            mock_window_instance.cleanup.assert_called_once()

    @patch("minicrm.application_ttk.configure_application_dependencies")
    @patch("minicrm.application_ttk.get_service")
    def test_get_service_by_name(self, mock_get_service, mock_configure):
        """测试通过名称获取服务"""
        # 设置模拟
        mock_configure.return_value = None

        # 创建模拟服务
        mock_customer_service = Mock()
        mock_finance_service = Mock()

        def get_service_side_effect(service_type):
            from minicrm.core.interfaces.service_interfaces import ICustomerService
            from minicrm.services.finance_service import FinanceService

            if service_type == ICustomerService:
                return mock_customer_service
            if service_type == FinanceService:
                return mock_finance_service
            return Mock()

        mock_get_service.side_effect = get_service_side_effect

        with patch("minicrm.application_ttk.MainWindowTTK"):
            from minicrm.application_ttk import MiniCRMApplicationTTK

            self.app = MiniCRMApplicationTTK(self.config)

            # 测试获取核心服务
            customer_service = self.app.get_service("customer")
            self.assertEqual(customer_service, mock_customer_service)

            # 测试获取其他服务
            finance_service = self.app.get_service("finance")
            self.assertEqual(finance_service, mock_finance_service)

    @patch("minicrm.application_ttk.configure_application_dependencies")
    @patch("minicrm.application_ttk.get_service")
    def test_error_handling_during_initialization(
        self, mock_get_service, mock_configure
    ):
        """测试初始化过程中的错误处理"""
        # 模拟配置失败
        mock_configure.side_effect = Exception("配置失败")

        from minicrm.application_ttk import MiniCRMApplicationTTK
        from minicrm.core.exceptions import MiniCRMError

        # 验证异常被正确处理
        with self.assertRaises(MiniCRMError) as context:
            self.app = MiniCRMApplicationTTK(self.config)

        self.assertIn("TTK应用程序初始化失败", str(context.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
