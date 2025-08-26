"""
配置管理系统测试模块

测试配置管理器的各种功能，包括加载、保存、验证和更新配置。
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.minicrm.config.settings import (
    ApplicationConfig,
    ConfigManager,
    DatabaseConfig,
    UIConfig,
    get_config,
    load_config,
    reset_config,
    save_config,
)
from src.minicrm.core.exceptions import ConfigurationError, ValidationError


class TestApplicationConfig(unittest.TestCase):
    """测试应用程序配置"""

    def test_default_values(self):
        """测试默认配置值"""
        config = ApplicationConfig()

        self.assertEqual(config.name, "MiniCRM")
        self.assertEqual(config.version, "1.0.0")
        self.assertEqual(config.description, "跨平台客户关系管理系统")
        self.assertEqual(config.author, "MiniCRM开发团队")
        self.assertFalse(config.debug)
        self.assertTrue(config.auto_save)
        self.assertTrue(config.auto_backup)
        self.assertEqual(config.language, "zh_CN")

    def test_validation_success(self):
        """测试配置验证成功"""
        config = ApplicationConfig()

        # 不应该抛出异常
        config.validate()

    def test_validation_empty_name(self):
        """测试空应用名称验证"""
        config = ApplicationConfig()
        config.name = ""

        with self.assertRaises(ValidationError):
            config.validate()

    def test_validation_empty_version(self):
        """测试空版本号验证"""
        config = ApplicationConfig()
        config.version = ""

        with self.assertRaises(ValidationError):
            config.validate()


class TestDatabaseConfig(unittest.TestCase):
    """测试数据库配置"""

    def test_default_values(self):
        """测试默认配置值"""
        config = DatabaseConfig()

        self.assertEqual(config.name, "minicrm.db")
        self.assertTrue(config.path.endswith("minicrm.db"))
        self.assertEqual(config.backup_interval, 24)
        self.assertEqual(config.max_backups, 30)
        self.assertEqual(config.connection_timeout, 30)
        self.assertTrue(config.enable_wal)
        self.assertEqual(config.cache_size, 64000)
        self.assertTrue(config.auto_vacuum)

    def test_validation_success(self):
        """测试配置验证成功"""
        config = DatabaseConfig()

        # 不应该抛出异常
        config.validate()

    def test_validation_invalid_backup_interval(self):
        """测试无效备份间隔验证"""
        config = DatabaseConfig()
        config.backup_interval = 0

        with self.assertRaises(ValidationError):
            config.validate()

    def test_validation_invalid_max_backups(self):
        """测试无效最大备份数验证"""
        config = DatabaseConfig()
        config.max_backups = -1

        with self.assertRaises(ValidationError):
            config.validate()

    def test_get_full_path(self):
        """测试获取完整路径"""
        config = DatabaseConfig()
        config.path = "/test/path/db.sqlite"

        result = config.get_full_path()

        self.assertIsInstance(result, Path)
        self.assertEqual(str(result), "/test/path/db.sqlite")

    @patch("src.minicrm.config.settings.ensure_directory_exists")
    def test_ensure_directory(self, mock_ensure_dir):
        """测试确保目录存在"""
        config = DatabaseConfig()
        config.path = "/test/path/db.sqlite"

        config.ensure_directory()

        # 验证调用了ensure_directory_exists
        mock_ensure_dir.assert_called_once()


class TestUIConfig(unittest.TestCase):
    """测试UI配置"""

    def test_default_values(self):
        """测试默认配置值"""
        config = UIConfig()

        self.assertEqual(config.min_width, 1024)
        self.assertEqual(config.min_height, 768)
        self.assertEqual(config.default_width, 1280)
        self.assertEqual(config.default_height, 800)
        self.assertTrue(config.remember_window_state)
        self.assertEqual(config.theme, "light")
        self.assertIn("light", config.available_themes)
        self.assertIn("dark", config.available_themes)

    def test_validation_success(self):
        """测试配置验证成功"""
        config = UIConfig()

        # 不应该抛出异常
        config.validate()

    def test_validation_invalid_window_size(self):
        """测试无效窗口尺寸验证"""
        config = UIConfig()
        config.min_width = 0

        with self.assertRaises(ValidationError):
            config.validate()

    def test_validation_default_smaller_than_min(self):
        """测试默认尺寸小于最小尺寸验证"""
        config = UIConfig()
        config.default_width = 800  # 小于min_width(1024)

        with self.assertRaises(ValidationError):
            config.validate()

    def test_validation_invalid_theme(self):
        """测试无效主题验证"""
        config = UIConfig()
        config.theme = "invalid_theme"

        with self.assertRaises(ValidationError):
            config.validate()

    def test_validation_invalid_page_size(self):
        """测试无效分页大小验证"""
        config = UIConfig()
        config.default_page_size = 999  # 不在page_size_options中

        with self.assertRaises(ValidationError):
            config.validate()


class TestConfigManager(unittest.TestCase):
    """测试配置管理器"""

    def setUp(self):
        """测试准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"
        self.config_manager = ConfigManager(str(self.config_file))

    def tearDown(self):
        """测试清理"""
        # 清理临时文件
        if self.config_file.exists():
            self.config_file.unlink()
        os.rmdir(self.temp_dir)

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.config_manager.config_file, self.config_file)
        self.assertFalse(self.config_manager._is_loaded)
        self.assertIsInstance(self.config_manager.app, ApplicationConfig)
        self.assertIsInstance(self.config_manager.database, DatabaseConfig)
        self.assertIsInstance(self.config_manager.ui, UIConfig)

    def test_load_default_config(self):
        """测试加载默认配置"""
        # 配置文件不存在时应该使用默认配置
        self.config_manager.load()

        self.assertTrue(self.config_manager._is_loaded)
        self.assertEqual(self.config_manager.app.name, "MiniCRM")
        self.assertTrue(self.config_file.exists())  # 应该创建配置文件

    def test_load_user_config(self):
        """测试加载用户配置"""
        # 创建用户配置文件
        user_config = {
            "app": {"name": "Custom MiniCRM", "debug": True},
            "ui": {"theme": {"default": "dark"}},
        }

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(user_config, f)

        self.config_manager.load()

        self.assertTrue(self.config_manager._is_loaded)
        self.assertEqual(self.config_manager.app.name, "Custom MiniCRM")
        self.assertTrue(self.config_manager.app.debug)
        self.assertEqual(self.config_manager.ui.theme, "dark")

    def test_load_invalid_json(self):
        """测试加载无效JSON配置"""
        # 创建无效的JSON文件
        with open(self.config_file, "w", encoding="utf-8") as f:
            f.write("invalid json content")

        with self.assertRaises(ConfigurationError) as context:
            self.config_manager.load()

        self.assertIn("配置文件格式错误", str(context.exception))

    def test_save_config(self):
        """测试保存配置"""
        self.config_manager.load()

        # 修改配置
        self.config_manager.app.name = "Modified MiniCRM"
        self.config_manager.app.debug = True

        # 保存配置
        self.config_manager.save()

        # 验证文件存在
        self.assertTrue(self.config_file.exists())

        # 验证文件内容
        with open(self.config_file, encoding="utf-8") as f:
            saved_config = json.load(f)

        self.assertEqual(saved_config["app"]["name"], "Modified MiniCRM")
        self.assertTrue(saved_config["app"]["debug"])

    def test_validate_config(self):
        """测试配置验证"""
        self.config_manager.load()

        # 正常情况下不应该抛出异常
        self.config_manager.validate()

        # 设置无效配置
        self.config_manager.app.name = ""

        with self.assertRaises(ValidationError):
            self.config_manager.validate()

    def test_reset_to_default(self):
        """测试重置为默认配置"""
        self.config_manager.load()

        # 修改配置
        self.config_manager.app.name = "Modified MiniCRM"

        # 重置配置
        self.config_manager.reset_to_default()

        # 验证配置已重置
        self.assertEqual(self.config_manager.app.name, "MiniCRM")

    def test_update_config(self):
        """测试更新配置"""
        self.config_manager.load()

        # 更新配置
        self.config_manager.update_config("app", "name", "Updated MiniCRM")

        # 验证配置已更新
        self.assertEqual(self.config_manager.app.name, "Updated MiniCRM")

    def test_update_config_invalid_section(self):
        """测试更新无效配置节"""
        self.config_manager.load()

        with self.assertRaises(ConfigurationError) as context:
            self.config_manager.update_config("invalid_section", "key", "value")

        self.assertIn("配置节不存在", str(context.exception))

    def test_update_config_invalid_key(self):
        """测试更新无效配置键"""
        self.config_manager.load()

        with self.assertRaises(ConfigurationError) as context:
            self.config_manager.update_config("app", "invalid_key", "value")

        self.assertIn("配置键不存在", str(context.exception))

    def test_get_config(self):
        """测试获取配置值"""
        self.config_manager.load()

        # 获取存在的配置
        result = self.config_manager.get_config("app", "name")
        self.assertEqual(result, "MiniCRM")

        # 获取不存在的配置，使用默认值
        result = self.config_manager.get_config("app", "nonexistent", "default_value")
        self.assertEqual(result, "default_value")

        # 获取不存在的配置节
        result = self.config_manager.get_config("invalid_section", "key", "default")
        self.assertEqual(result, "default")

    def test_get_all_config(self):
        """测试获取所有配置"""
        self.config_manager.load()

        all_config = self.config_manager.get_all_config()

        self.assertIsInstance(all_config, dict)
        self.assertIn("app", all_config)
        self.assertIn("database", all_config)
        self.assertIn("ui", all_config)
        self.assertEqual(all_config["app"]["name"], "MiniCRM")


class TestGlobalFunctions(unittest.TestCase):
    """测试全局配置函数"""

    def setUp(self):
        """测试准备"""
        # 重置全局配置管理器
        import src.minicrm.config.settings as settings_module

        settings_module.config_manager = ConfigManager()

    @patch("src.minicrm.config.settings.config_manager")
    def test_get_config(self, mock_config_manager):
        """测试获取全局配置"""
        mock_config_manager._is_loaded = False

        result = get_config()

        # 验证加载被调用
        mock_config_manager.load.assert_called_once()
        self.assertEqual(result, mock_config_manager)

    @patch("src.minicrm.config.settings.ConfigManager")
    def test_load_config_with_file(self, mock_config_manager_class):
        """测试加载指定配置文件"""
        mock_instance = MagicMock()
        mock_config_manager_class.return_value = mock_instance

        result = load_config("/path/to/config.json")

        # 验证创建了新的配置管理器实例
        mock_config_manager_class.assert_called_once_with("/path/to/config.json")
        mock_instance.load.assert_called_once()
        self.assertEqual(result, mock_instance)

    @patch("src.minicrm.config.settings.config_manager")
    def test_save_config(self, mock_config_manager):
        """测试保存全局配置"""
        save_config()

        mock_config_manager.save.assert_called_once()

    @patch("src.minicrm.config.settings.config_manager")
    def test_reset_config(self, mock_config_manager):
        """测试重置全局配置"""
        reset_config()

        mock_config_manager.reset_to_default.assert_called_once()
        mock_config_manager.save.assert_called_once()


if __name__ == "__main__":
    unittest.main()
