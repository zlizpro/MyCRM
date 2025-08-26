"""MiniCRM主入口点启动测试.

测试main.py的启动流程，确保：
- 主函数能够正确导入TTK应用程序
- 配置系统正常工作
- 基本的启动流程能够执行
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


class TestMainStartup(unittest.TestCase):
    """主入口点启动测试类."""

    def setUp(self):
        """测试准备."""
        # 设置测试日志
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    def test_import_main_module(self):
        """测试主模块导入."""
        try:
            # 测试导入main模块
            import minicrm.main

            # 验证main函数存在
            self.assertTrue(hasattr(minicrm.main, "main"))
            self.assertTrue(callable(minicrm.main.main))

            # 验证其他必要函数存在
            self.assertTrue(hasattr(minicrm.main, "setup_application"))
            self.assertTrue(hasattr(minicrm.main, "cleanup_application"))

            self.logger.info("✅ 主模块导入测试通过")

        except ImportError as e:
            self.fail(f"主模块导入失败: {e}")

    def test_import_ttk_application(self):
        """测试TTK应用程序导入."""
        try:
            # 测试导入TTK应用程序
            from minicrm.application_ttk import MiniCRMApplicationTTK

            # 验证类存在
            self.assertTrue(callable(MiniCRMApplicationTTK))

            self.logger.info("✅ TTK应用程序导入测试通过")

        except ImportError as e:
            self.fail(f"TTK应用程序导入失败: {e}")

    def test_import_config_system(self):
        """测试配置系统导入."""
        try:
            # 测试导入配置系统
            from minicrm.config.settings import ConfigManager, get_config

            # 验证类和函数存在
            self.assertTrue(callable(ConfigManager))
            self.assertTrue(callable(get_config))

            self.logger.info("✅ 配置系统导入测试通过")

        except ImportError as e:
            self.fail(f"配置系统导入失败: {e}")

    @patch("minicrm.main.MiniCRMApplicationTTK")
    @patch("minicrm.application_ttk.MiniCRMApplicationTTK")
    @patch("minicrm.main.get_config")
    def test_main_function_with_mocks(self, mock_get_config, mock_app_class):
        """测试main函数执行（使用模拟对象）."""
        try:
            # 设置模拟配置
            mock_config = MagicMock()
            mock_config.database.path = "test.db"
            mock_config.logging.level = "INFO"
            mock_config.ui.theme = "light"
            mock_get_config.return_value = mock_config

            # 设置模拟应用程序
            mock_app = MagicMock()
            mock_app.run.side_effect = KeyboardInterrupt()  # 模拟用户中断
            mock_app_class.return_value = mock_app

            # 导入并执行main函数
            from minicrm.main import main

            exit_code = main()

            # 验证退出代码（KeyboardInterrupt应该返回130）
            self.assertEqual(exit_code, 130)

            # 验证配置被获取
            mock_get_config.assert_called_once()

            # 验证应用程序被创建
            mock_app_class.assert_called_once_with(mock_config)

            # 验证应用程序被运行
            mock_app.run.assert_called_once()

            # 验证应用程序被关闭
            mock_app.shutdown.assert_called_once()

            self.logger.info("✅ main函数执行测试通过")

        except Exception as e:
            self.fail(f"main函数执行测试失败: {e}")

    def test_configuration_loading(self):
        """测试配置加载."""
        try:
            # 导入配置系统
            from minicrm.config.settings import ConfigManager

            # 创建配置管理器
            config = ConfigManager()
            config.load()

            # 验证配置结构
            self.assertIsNotNone(config.app)
            self.assertIsNotNone(config.database)
            self.assertIsNotNone(config.ui)
            self.assertIsNotNone(config.logging)

            # 验证配置值
            self.assertEqual(config.app.name, "MiniCRM")
            self.assertIn(config.ui.theme, ["light", "dark"])

            self.logger.info("✅ 配置加载测试通过")

        except Exception as e:
            self.fail(f"配置加载测试失败: {e}")

    def test_setup_application_function(self):
        """测试应用程序设置函数."""
        try:
            # 导入设置函数
            from minicrm.main import setup_application

            # 执行设置（这应该不会抛出异常）
            setup_application()

            self.logger.info("✅ 应用程序设置测试通过")

        except Exception as e:
            self.fail(f"应用程序设置测试失败: {e}")

    def test_cleanup_application_function(self):
        """测试应用程序清理函数."""
        try:
            # 导入清理函数
            from minicrm.main import cleanup_application

            # 执行清理（这应该不会抛出异常）
            cleanup_application()

            self.logger.info("✅ 应用程序清理测试通过")

        except Exception as e:
            self.fail(f"应用程序清理测试失败: {e}")

    def test_constants_import(self):
        """测试常量导入."""
        try:
            # 导入常量
            from minicrm.core.constants import APP_NAME, APP_VERSION

            # 验证常量存在且有值
            self.assertIsNotNone(APP_NAME)
            self.assertIsNotNone(APP_VERSION)
            self.assertIsInstance(APP_NAME, str)
            self.assertIsInstance(APP_VERSION, str)

            self.logger.info("✅ 常量导入测试通过")

        except ImportError as e:
            self.fail(f"常量导入失败: {e}")

    def test_logging_system_import(self):
        """测试日志系统导入."""
        try:
            # 导入日志系统
            from minicrm.core.logging import (
                get_logger,
                initialize_logging,
                shutdown_logging,
            )

            # 验证函数存在
            self.assertTrue(callable(get_logger))
            self.assertTrue(callable(initialize_logging))
            self.assertTrue(callable(shutdown_logging))

            self.logger.info("✅ 日志系统导入测试通过")

        except ImportError as e:
            self.fail(f"日志系统导入失败: {e}")

    def test_exception_classes_import(self):
        """测试异常类导入."""
        try:
            # 导入异常类
            from minicrm.core.exceptions import ConfigurationError, MiniCRMError

            # 验证异常类存在
            self.assertTrue(issubclass(MiniCRMError, Exception))
            self.assertTrue(issubclass(ConfigurationError, Exception))

            self.logger.info("✅ 异常类导入测试通过")

        except ImportError as e:
            self.fail(f"异常类导入失败: {e}")


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
