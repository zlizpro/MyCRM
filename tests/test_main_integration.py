"""MiniCRM主入口点集成测试.

测试TTK应用程序的启动和初始化流程，确保：
- 应用程序能够正确启动
- 所有服务正确连接到TTK界面
- 配置系统正常工作
- 资源清理正确执行
"""

import logging
from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch


# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from minicrm.application_ttk import MiniCRMApplicationTTK
from minicrm.config.settings import ConfigManager
from minicrm.core.exceptions import MiniCRMError


class TestMainIntegration(unittest.TestCase):
    """主入口点集成测试类."""

    def setUp(self):
        """测试准备."""
        # 设置测试日志
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        # 创建测试配置
        self.config = ConfigManager()
        self.config.load()

        # 测试应用程序实例
        self.app = None

    def tearDown(self):
        """测试清理."""
        if self.app:
            try:
                self.app.shutdown()
            except Exception as e:
                self.logger.warning(f"应用程序清理失败: {e}")

    def test_application_creation(self):
        """测试TTK应用程序创建."""
        try:
            # 创建应用程序实例
            self.app = MiniCRMApplicationTTK(self.config)

            # 验证应用程序已初始化
            self.assertTrue(self.app.is_initialized)
            self.assertFalse(self.app.is_running)
            self.assertFalse(self.app.is_shutting_down)

            # 验证配置正确设置
            self.assertEqual(self.app.config, self.config)

            # 验证主窗口已创建
            self.assertIsNotNone(self.app.main_window)

            self.logger.info("✅ TTK应用程序创建测试通过")

        except Exception as e:
            self.fail(f"TTK应用程序创建失败: {e}")

    def test_services_initialization(self):
        """测试服务层初始化."""
        try:
            # 创建应用程序实例
            self.app = MiniCRMApplicationTTK(self.config)

            # 验证服务状态
            service_status = self.app.get_service_status()

            # 检查核心服务是否已初始化
            expected_services = [
                "customer_service",
                "supplier_service",
                "analytics_service",
                "settings_service",
                "task_service",
            ]

            for service_name in expected_services:
                self.assertTrue(
                    service_status.get(service_name, False),
                    f"服务 {service_name} 未正确初始化",
                )

            # 验证可以获取服务实例
            customer_service = self.app.customer_service
            self.assertIsNotNone(customer_service)

            supplier_service = self.app.supplier_service
            self.assertIsNotNone(supplier_service)

            self.logger.info("✅ 服务层初始化测试通过")

        except Exception as e:
            self.fail(f"服务层初始化测试失败: {e}")

    def test_database_connection(self):
        """测试数据库连接."""
        try:
            # 创建应用程序实例
            self.app = MiniCRMApplicationTTK(self.config)

            # 验证数据库管理器已初始化
            db_manager = self.app.database_manager
            self.assertIsNotNone(db_manager)

            # 验证数据库连接
            # 注意：这里只测试连接是否可用，不执行实际的数据库操作
            self.assertTrue(hasattr(db_manager, "get_connection"))

            self.logger.info("✅ 数据库连接测试通过")

        except Exception as e:
            self.fail(f"数据库连接测试失败: {e}")

    def test_ttk_components_initialization(self):
        """测试TTK组件初始化."""
        try:
            # 创建应用程序实例
            self.app = MiniCRMApplicationTTK(self.config)

            # 验证主窗口
            main_window = self.app.main_window
            self.assertIsNotNone(main_window)

            # 验证主窗口信息
            window_info = main_window.get_main_window_info()
            self.assertIsInstance(window_info, dict)
            self.assertIn("title", window_info)
            self.assertIn("size", window_info)

            self.logger.info("✅ TTK组件初始化测试通过")

        except Exception as e:
            self.fail(f"TTK组件初始化测试失败: {e}")

    def test_application_info(self):
        """测试应用程序信息获取."""
        try:
            # 创建应用程序实例
            self.app = MiniCRMApplicationTTK(self.config)

            # 获取应用程序信息
            app_info = self.app.get_application_info()

            # 验证信息结构
            self.assertIsInstance(app_info, dict)
            self.assertEqual(app_info["application_type"], "TTK")
            self.assertTrue(app_info["is_initialized"])
            self.assertFalse(app_info["is_running"])
            self.assertFalse(app_info["is_shutting_down"])

            # 验证服务状态
            self.assertIn("services", app_info)
            self.assertIsInstance(app_info["services"], dict)

            # 验证主窗口信息
            self.assertIn("main_window", app_info)

            self.logger.info("✅ 应用程序信息测试通过")

        except Exception as e:
            self.fail(f"应用程序信息测试失败: {e}")

    def test_service_retrieval(self):
        """测试服务获取功能."""
        try:
            # 创建应用程序实例
            self.app = MiniCRMApplicationTTK(self.config)

            # 测试通过字符串获取服务
            customer_service = self.app.get_service("customer")
            self.assertIsNotNone(customer_service)

            supplier_service = self.app.get_service("supplier")
            self.assertIsNotNone(supplier_service)

            analytics_service = self.app.get_service("analytics")
            self.assertIsNotNone(analytics_service)

            # 测试获取不存在的服务
            with self.assertRaises(MiniCRMError):
                self.app.get_service("nonexistent_service")

            self.logger.info("✅ 服务获取测试通过")

        except Exception as e:
            self.fail(f"服务获取测试失败: {e}")

    def test_application_shutdown(self):
        """测试应用程序关闭流程."""
        try:
            # 创建应用程序实例
            self.app = MiniCRMApplicationTTK(self.config)

            # 验证初始状态
            self.assertTrue(self.app.is_initialized)
            self.assertFalse(self.app.is_shutting_down)

            # 执行关闭
            self.app.shutdown()

            # 验证关闭状态
            self.assertTrue(self.app.is_shutting_down)

            self.logger.info("✅ 应用程序关闭测试通过")

        except Exception as e:
            self.fail(f"应用程序关闭测试失败: {e}")

    @patch("minicrm.main.MiniCRMApplicationTTK")
    def test_main_function_success(self, mock_app_class):
        """测试main函数成功执行."""
        # 创建模拟应用程序实例
        mock_app = MagicMock()
        mock_app.run.return_value = None
        mock_app.shutdown.return_value = None
        mock_app_class.return_value = mock_app

        # 导入并执行main函数
        from minicrm.main import main

        # 在单独的线程中运行main函数，避免阻塞测试
        result = [None]
        exception = [None]

        def run_main():
            try:
                result[0] = main()
            except Exception as e:
                exception[0] = e

        # 由于main函数会启动GUI，我们需要模拟快速退出
        with patch("minicrm.main.get_config") as mock_get_config:
            mock_config = MagicMock()
            mock_config.database.path = "test.db"
            mock_config.logging.level = "INFO"
            mock_config.ui.theme = "light"
            mock_get_config.return_value = mock_config

            # 模拟应用程序快速退出
            mock_app.run.side_effect = KeyboardInterrupt()

            exit_code = main()

            # 验证退出代码
            self.assertEqual(exit_code, 130)  # KeyboardInterrupt的退出代码

            # 验证应用程序被创建和关闭
            mock_app_class.assert_called_once()
            mock_app.shutdown.assert_called_once()

        self.logger.info("✅ main函数测试通过")

    def test_configuration_loading(self):
        """测试配置加载."""
        try:
            # 创建应用程序实例
            self.app = MiniCRMApplicationTTK(self.config)

            # 验证配置已正确加载
            app_config = self.app.config
            self.assertIsNotNone(app_config)

            # 验证配置属性
            self.assertIsNotNone(app_config.app)
            self.assertIsNotNone(app_config.database)
            self.assertIsNotNone(app_config.ui)
            self.assertIsNotNone(app_config.logging)

            # 验证配置值
            self.assertEqual(app_config.app.name, "MiniCRM")
            self.assertIn(app_config.ui.theme, ["light", "dark"])

            self.logger.info("✅ 配置加载测试通过")

        except Exception as e:
            self.fail(f"配置加载测试失败: {e}")


class TestStartupProcess(unittest.TestCase):
    """启动流程测试类."""

    def setUp(self):
        """测试准备."""
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    def test_import_dependencies(self):
        """测试依赖导入."""
        try:
            # 测试核心模块导入
            from minicrm.application_ttk import MiniCRMApplicationTTK
            from minicrm.config.settings import ConfigManager
            from minicrm.core.exceptions import MiniCRMError

            # 测试服务模块导入
            from minicrm.services.customer_service import CustomerService
            from minicrm.services.supplier_service import SupplierService

            # 测试UI模块导入
            from minicrm.ui.ttk_base.main_window_ttk import MainWindowTTK

            self.logger.info("✅ 依赖导入测试通过")

        except ImportError as e:
            self.fail(f"依赖导入失败: {e}")

    def test_configuration_system(self):
        """测试配置系统."""
        try:
            # 创建配置管理器
            config = ConfigManager()
            config.load()

            # 验证配置结构
            self.assertIsNotNone(config.app)
            self.assertIsNotNone(config.database)
            self.assertIsNotNone(config.ui)
            self.assertIsNotNone(config.logging)

            # 验证配置验证
            config.validate()

            self.logger.info("✅ 配置系统测试通过")

        except Exception as e:
            self.fail(f"配置系统测试失败: {e}")


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
