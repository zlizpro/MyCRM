"""测试应用程序服务集成

测试MiniCRM TTK应用程序中的服务集成功能，确保：
- 应用程序正确初始化服务集成
- 事件处理器正确注册和工作
- 面板与服务集成器正确连接
- 全局事件处理正常工作
"""

import unittest
from unittest.mock import Mock, patch

from minicrm.application_ttk import MiniCRMApplicationTTK
from minicrm.config.settings import ConfigManager


class TestApplicationServiceIntegration(unittest.TestCase):
    """测试应用程序服务集成"""

    def setUp(self):
        """测试准备"""
        self.config = ConfigManager()

    @patch("minicrm.application_ttk.configure_application_dependencies")
    @patch("minicrm.application_ttk.get_service")
    @patch("minicrm.application_ttk.MainWindowTTK")
    @patch("minicrm.application_ttk.get_global_event_manager")
    @patch("minicrm.application_ttk.TTKThemeManager")
    @patch("minicrm.application_ttk.TTKErrorHandler")
    def test_service_integration_initialization(
        self,
        mock_error_handler,
        mock_theme_manager,
        mock_event_manager,
        mock_main_window,
        mock_get_service,
        mock_configure_deps,
    ):
        """测试服务集成初始化"""
        # 准备模拟服务
        mock_customer_service = Mock()
        mock_supplier_service = Mock()
        mock_analytics_service = Mock()
        mock_settings_service = Mock()
        mock_task_service = Mock()
        mock_finance_service = Mock()
        mock_contract_service = Mock()
        mock_database_manager = Mock()

        # 配置get_service返回值
        def get_service_side_effect(service_type):
            service_map = {
                "ICustomerService": mock_customer_service,
                "ISupplierService": mock_supplier_service,
                "IAnalyticsService": mock_analytics_service,
                "ISettingsService": mock_settings_service,
                "ITaskService": mock_task_service,
                "finance": mock_finance_service,
                "contract": mock_contract_service,
                "DatabaseManager": mock_database_manager,
            }
            return service_map.get(str(service_type), Mock())

        mock_get_service.side_effect = get_service_side_effect

        # 模拟数据库初始化
        mock_database_manager.initialize_database.return_value = None

        # 创建应用程序实例
        app = MiniCRMApplicationTTK(self.config)

        # 验证服务集成初始化
        self.assertIsNotNone(app.integration_manager)
        self.assertIsNotNone(app.service_integrations)

        # 验证服务集成器存在
        self.assertIn("customer", app.service_integrations)
        self.assertIn("supplier", app.service_integrations)
        self.assertIn("finance", app.service_integrations)
        self.assertIn("task", app.service_integrations)
        self.assertIn("contract", app.service_integrations)

    @patch("minicrm.application_ttk.configure_application_dependencies")
    @patch("minicrm.application_ttk.get_service")
    @patch("minicrm.application_ttk.MainWindowTTK")
    @patch("minicrm.application_ttk.get_global_event_manager")
    @patch("minicrm.application_ttk.TTKThemeManager")
    @patch("minicrm.application_ttk.TTKErrorHandler")
    def test_event_handlers_registration(
        self,
        mock_error_handler,
        mock_theme_manager,
        mock_event_manager,
        mock_main_window,
        mock_get_service,
        mock_configure_deps,
    ):
        """测试事件处理器注册"""
        # 准备模拟服务
        mock_services = {
            "ICustomerService": Mock(),
            "ISupplierService": Mock(),
            "IAnalyticsService": Mock(),
            "ISettingsService": Mock(),
            "ITaskService": Mock(),
            "finance": Mock(),
            "contract": Mock(),
            "DatabaseManager": Mock(),
        }

        mock_get_service.side_effect = lambda service_type: mock_services.get(
            str(service_type), Mock()
        )
        mock_services["DatabaseManager"].initialize_database.return_value = None

        # 创建应用程序实例
        app = MiniCRMApplicationTTK(self.config)

        # 验证事件处理器方法存在
        self.assertTrue(hasattr(app, "_on_customer_created"))
        self.assertTrue(hasattr(app, "_on_customer_updated"))
        self.assertTrue(hasattr(app, "_on_customer_deleted"))
        self.assertTrue(hasattr(app, "_on_supplier_created"))
        self.assertTrue(hasattr(app, "_on_supplier_updated"))
        self.assertTrue(hasattr(app, "_on_supplier_deleted"))
        self.assertTrue(hasattr(app, "_on_task_created"))
        self.assertTrue(hasattr(app, "_on_task_updated"))
        self.assertTrue(hasattr(app, "_on_task_completed"))
        self.assertTrue(hasattr(app, "_on_contract_created"))
        self.assertTrue(hasattr(app, "_on_contract_updated"))
        self.assertTrue(hasattr(app, "_on_payment_recorded"))

    @patch("minicrm.application_ttk.configure_application_dependencies")
    @patch("minicrm.application_ttk.get_service")
    @patch("minicrm.application_ttk.MainWindowTTK")
    @patch("minicrm.application_ttk.get_global_event_manager")
    @patch("minicrm.application_ttk.TTKThemeManager")
    @patch("minicrm.application_ttk.TTKErrorHandler")
    def test_event_handling(
        self,
        mock_error_handler,
        mock_theme_manager,
        mock_event_manager,
        mock_main_window,
        mock_get_service,
        mock_configure_deps,
    ):
        """测试事件处理"""
        # 准备模拟服务
        mock_services = {
            "ICustomerService": Mock(),
            "ISupplierService": Mock(),
            "IAnalyticsService": Mock(),
            "ISettingsService": Mock(),
            "ITaskService": Mock(),
            "finance": Mock(),
            "contract": Mock(),
            "DatabaseManager": Mock(),
        }

        mock_get_service.side_effect = lambda service_type: mock_services.get(
            str(service_type), Mock()
        )
        mock_services["DatabaseManager"].initialize_database.return_value = None

        # 创建应用程序实例
        app = MiniCRMApplicationTTK(self.config)

        # 测试客户事件处理
        with patch.object(app, "_logger") as mock_logger:
            app._on_customer_created(123, {"name": "测试客户"})
            mock_logger.info.assert_called()

            app._on_customer_updated(123, {"name": "更新客户"})
            mock_logger.info.assert_called()

            app._on_customer_deleted(123)
            mock_logger.info.assert_called()

        # 测试供应商事件处理
        with patch.object(app, "_logger") as mock_logger:
            app._on_supplier_created(456, {"name": "测试供应商"})
            mock_logger.info.assert_called()

            app._on_supplier_updated(456, {"name": "更新供应商"})
            mock_logger.info.assert_called()

            app._on_supplier_deleted(456)
            mock_logger.info.assert_called()

        # 测试任务事件处理
        with patch.object(app, "_logger") as mock_logger:
            app._on_task_created(789, {"title": "测试任务"})
            mock_logger.info.assert_called()

            app._on_task_updated(789, {"title": "更新任务"})
            mock_logger.info.assert_called()

            app._on_task_completed(789)
            mock_logger.info.assert_called()

    @patch("minicrm.application_ttk.configure_application_dependencies")
    @patch("minicrm.application_ttk.get_service")
    @patch("minicrm.application_ttk.MainWindowTTK")
    @patch("minicrm.application_ttk.get_global_event_manager")
    @patch("minicrm.application_ttk.TTKThemeManager")
    @patch("minicrm.application_ttk.TTKErrorHandler")
    def test_get_service_integration(
        self,
        mock_error_handler,
        mock_theme_manager,
        mock_event_manager,
        mock_main_window,
        mock_get_service,
        mock_configure_deps,
    ):
        """测试获取服务集成器"""
        # 准备模拟服务
        mock_services = {
            "ICustomerService": Mock(),
            "ISupplierService": Mock(),
            "IAnalyticsService": Mock(),
            "ISettingsService": Mock(),
            "ITaskService": Mock(),
            "finance": Mock(),
            "contract": Mock(),
            "DatabaseManager": Mock(),
        }

        mock_get_service.side_effect = lambda service_type: mock_services.get(
            str(service_type), Mock()
        )
        mock_services["DatabaseManager"].initialize_database.return_value = None

        # 创建应用程序实例
        app = MiniCRMApplicationTTK(self.config)

        # 测试获取服务集成器
        customer_integration = app.get_service_integration("customer")
        self.assertIsNotNone(customer_integration)

        supplier_integration = app.get_service_integration("supplier")
        self.assertIsNotNone(supplier_integration)

        finance_integration = app.get_service_integration("finance")
        self.assertIsNotNone(finance_integration)

        task_integration = app.get_service_integration("task")
        self.assertIsNotNone(task_integration)

        contract_integration = app.get_service_integration("contract")
        self.assertIsNotNone(contract_integration)

        # 测试获取不存在的服务集成器
        unknown_integration = app.get_service_integration("unknown")
        self.assertIsNone(unknown_integration)

    @patch("minicrm.application_ttk.configure_application_dependencies")
    @patch("minicrm.application_ttk.get_service")
    @patch("minicrm.application_ttk.MainWindowTTK")
    @patch("minicrm.application_ttk.get_global_event_manager")
    @patch("minicrm.application_ttk.TTKThemeManager")
    @patch("minicrm.application_ttk.TTKErrorHandler")
    def test_service_integration_properties(
        self,
        mock_error_handler,
        mock_theme_manager,
        mock_event_manager,
        mock_main_window,
        mock_get_service,
        mock_configure_deps,
    ):
        """测试服务集成属性访问"""
        # 准备模拟服务
        mock_services = {
            "ICustomerService": Mock(),
            "ISupplierService": Mock(),
            "IAnalyticsService": Mock(),
            "ISettingsService": Mock(),
            "ITaskService": Mock(),
            "finance": Mock(),
            "contract": Mock(),
            "DatabaseManager": Mock(),
        }

        mock_get_service.side_effect = lambda service_type: mock_services.get(
            str(service_type), Mock()
        )
        mock_services["DatabaseManager"].initialize_database.return_value = None

        # 创建应用程序实例
        app = MiniCRMApplicationTTK(self.config)

        # 测试属性访问
        self.assertIsNotNone(app.service_integrations)
        self.assertIsInstance(app.service_integrations, dict)

        self.assertIsNotNone(app.integration_manager)

        # 验证服务集成字典包含预期的键
        expected_keys = [
            "customer",
            "supplier",
            "finance",
            "task",
            "contract",
            "manager",
        ]
        for key in expected_keys:
            self.assertIn(key, app.service_integrations)


class TestServiceIntegrationErrorHandling(unittest.TestCase):
    """测试服务集成错误处理"""

    def setUp(self):
        """测试准备"""
        self.config = ConfigManager()

    @patch("minicrm.application_ttk.configure_application_dependencies")
    @patch("minicrm.application_ttk.get_service")
    @patch("minicrm.application_ttk.MainWindowTTK")
    @patch("minicrm.application_ttk.get_global_event_manager")
    @patch("minicrm.application_ttk.TTKThemeManager")
    @patch("minicrm.application_ttk.TTKErrorHandler")
    def test_service_integration_initialization_error(
        self,
        mock_error_handler,
        mock_theme_manager,
        mock_event_manager,
        mock_main_window,
        mock_get_service,
        mock_configure_deps,
    ):
        """测试服务集成初始化错误"""
        # 模拟服务获取失败
        mock_get_service.side_effect = Exception("服务获取失败")

        # 验证初始化失败时抛出异常
        with self.assertRaises(Exception):
            MiniCRMApplicationTTK(self.config)

    @patch("minicrm.application_ttk.configure_application_dependencies")
    @patch("minicrm.application_ttk.get_service")
    @patch("minicrm.application_ttk.MainWindowTTK")
    @patch("minicrm.application_ttk.get_global_event_manager")
    @patch("minicrm.application_ttk.TTKThemeManager")
    @patch("minicrm.application_ttk.TTKErrorHandler")
    def test_event_handler_error_handling(
        self,
        mock_error_handler,
        mock_theme_manager,
        mock_event_manager,
        mock_main_window,
        mock_get_service,
        mock_configure_deps,
    ):
        """测试事件处理器错误处理"""
        # 准备模拟服务
        mock_services = {
            "ICustomerService": Mock(),
            "ISupplierService": Mock(),
            "IAnalyticsService": Mock(),
            "ISettingsService": Mock(),
            "ITaskService": Mock(),
            "finance": Mock(),
            "contract": Mock(),
            "DatabaseManager": Mock(),
        }

        mock_get_service.side_effect = lambda service_type: mock_services.get(
            str(service_type), Mock()
        )
        mock_services["DatabaseManager"].initialize_database.return_value = None

        # 创建应用程序实例
        app = MiniCRMApplicationTTK(self.config)

        # 测试事件处理器在异常情况下不会崩溃
        with patch.object(app, "_logger") as mock_logger:
            # 模拟logger抛出异常
            mock_logger.info.side_effect = Exception("日志记录失败")

            # 事件处理器应该能够处理异常而不崩溃
            try:
                app._on_customer_created(123, {"name": "测试客户"})
                app._on_supplier_created(456, {"name": "测试供应商"})
                app._on_task_created(789, {"title": "测试任务"})
            except Exception:
                self.fail("事件处理器不应该因为日志异常而崩溃")


if __name__ == "__main__":
    unittest.main()
