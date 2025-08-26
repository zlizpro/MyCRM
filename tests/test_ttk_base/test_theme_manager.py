"""TTK主题管理器测试

测试TTK主题管理器的各项功能，包括：
- 主题切换功能
- 自定义主题创建
- 主题配置保存和加载
- 主题导入导出
- 主题变化回调

作者: MiniCRM开发团队
"""

import json
import os
from pathlib import Path

# 添加src路径以便导入模块
import sys
import tempfile
import tkinter as tk
from tkinter import ttk
import unittest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from minicrm.ui.ttk_base.style_manager import ThemeType
from minicrm.ui.ttk_base.theme_manager import (
    TTKThemeManager,
    apply_global_ttk_theme,
    get_global_ttk_theme_manager,
)


class TestTTKThemeManager(unittest.TestCase):
    """TTK主题管理器测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建测试用的根窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏窗口

        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()

        # 创建主题管理器实例
        self.theme_manager = TTKThemeManager(self.root)

        # 模拟配置目录
        self.theme_manager.config_dir = Path(self.temp_dir)
        self.theme_manager.config_file = (
            self.theme_manager.config_dir / "theme_config.json"
        )

    def tearDown(self):
        """测试后清理"""
        try:
            self.root.destroy()
        except tk.TclError:
            pass

        # 清理临时文件
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.theme_manager)
        self.assertIsNotNone(self.theme_manager.style_manager)
        self.assertEqual(len(self.theme_manager.theme_change_callbacks), 0)

    def test_get_available_themes(self):
        """测试获取可用主题列表"""
        themes = self.theme_manager.get_available_themes()

        self.assertIsInstance(themes, dict)
        self.assertIn(ThemeType.DEFAULT.value, themes)
        self.assertIn(ThemeType.DARK.value, themes)
        self.assertIn(ThemeType.LIGHT.value, themes)
        self.assertIn(ThemeType.HIGH_CONTRAST.value, themes)

    def test_get_current_theme(self):
        """测试获取当前主题"""
        current_theme = self.theme_manager.get_current_theme()
        self.assertIsInstance(current_theme, str)
        self.assertIn(current_theme, self.theme_manager.get_available_themes())

    def test_set_theme(self):
        """测试设置主题"""
        # 测试设置有效主题
        success = self.theme_manager.set_theme(ThemeType.DARK.value)
        self.assertTrue(success)
        self.assertEqual(self.theme_manager.get_current_theme(), ThemeType.DARK.value)

        # 测试设置无效主题
        success = self.theme_manager.set_theme("invalid_theme")
        self.assertFalse(success)

    def test_get_theme_config(self):
        """测试获取主题配置"""
        # 测试获取默认主题配置
        config = self.theme_manager.get_theme_config(ThemeType.DEFAULT.value)
        self.assertIsInstance(config, dict)
        self.assertIn("colors", config)
        self.assertIn("fonts", config)
        self.assertIn("spacing", config)

        # 测试获取不存在的主题配置
        config = self.theme_manager.get_theme_config("nonexistent")
        self.assertEqual(config, {})

    def test_create_custom_theme(self):
        """测试创建自定义主题"""
        theme_id = "test_custom"
        theme_name = "测试自定义主题"

        # 自定义颜色
        custom_colors = {"primary": "#FF0000", "bg_primary": "#F0F0F0"}

        # 自定义字体
        custom_fonts = {"default": {"family": "Arial", "size": 10, "weight": "bold"}}

        # 自定义间距
        custom_spacing = {"padding_small": 3, "padding_medium": 6}

        success = self.theme_manager.create_custom_theme(
            theme_id,
            theme_name,
            colors=custom_colors,
            fonts=custom_fonts,
            spacing=custom_spacing,
        )

        self.assertTrue(success)

        # 验证主题已创建
        themes = self.theme_manager.get_available_themes()
        self.assertIn(theme_id, themes)
        self.assertEqual(themes[theme_id], theme_name)

        # 验证主题配置
        config = self.theme_manager.get_theme_config(theme_id)
        self.assertEqual(config["colors"]["primary"], "#FF0000")
        self.assertEqual(config["fonts"]["default"]["family"], "Arial")
        self.assertEqual(config["spacing"]["padding_small"], 3)

    def test_delete_custom_theme(self):
        """测试删除自定义主题"""
        # 创建自定义主题
        theme_id = "test_delete"
        self.theme_manager.create_custom_theme(theme_id, "测试删除主题")

        # 验证主题存在
        self.assertIn(theme_id, self.theme_manager.get_available_themes())

        # 删除主题
        success = self.theme_manager.delete_custom_theme(theme_id)
        self.assertTrue(success)

        # 验证主题已删除
        self.assertNotIn(theme_id, self.theme_manager.get_available_themes())

        # 测试删除内置主题（应该失败）
        success = self.theme_manager.delete_custom_theme(ThemeType.DEFAULT.value)
        self.assertFalse(success)

    def test_export_theme(self):
        """测试导出主题"""
        # 创建自定义主题
        theme_id = "test_export"
        self.theme_manager.create_custom_theme(theme_id, "测试导出主题")

        # 导出主题
        export_file = os.path.join(self.temp_dir, "exported_theme.json")
        success = self.theme_manager.export_theme(theme_id, export_file)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(export_file))

        # 验证导出的文件内容
        with open(export_file, encoding="utf-8") as f:
            exported_config = json.load(f)

        self.assertIn("colors", exported_config)
        self.assertIn("fonts", exported_config)
        self.assertEqual(exported_config["name"], "测试导出主题")

    def test_import_theme(self):
        """测试导入主题"""
        # 创建测试主题文件
        theme_config = {
            "name": "导入测试主题",
            "colors": {"primary": "#00FF00", "bg_primary": "#FFFFFF"},
            "fonts": {
                "default": {"family": "Times New Roman", "size": 12, "weight": "normal"}
            },
            "spacing": {"padding_small": 4},
        }

        import_file = os.path.join(self.temp_dir, "import_theme.json")
        with open(import_file, "w", encoding="utf-8") as f:
            json.dump(theme_config, f, indent=2, ensure_ascii=False)

        # 导入主题
        success = self.theme_manager.import_theme(import_file, "imported_theme")
        self.assertTrue(success)

        # 验证主题已导入
        themes = self.theme_manager.get_available_themes()
        self.assertIn("imported_theme", themes)

        # 验证主题配置
        config = self.theme_manager.get_theme_config("imported_theme")
        self.assertEqual(config["colors"]["primary"], "#00FF00")
        self.assertEqual(config["fonts"]["default"]["family"], "Times New Roman")

    def test_theme_change_callbacks(self):
        """测试主题变化回调"""
        callback_called = False
        callback_theme = None

        def test_callback(theme_id):
            nonlocal callback_called, callback_theme
            callback_called = True
            callback_theme = theme_id

        # 添加回调
        self.theme_manager.add_theme_change_callback(test_callback)

        # 切换主题
        self.theme_manager.set_theme(ThemeType.DARK.value)

        # 验证回调被调用
        self.assertTrue(callback_called)
        self.assertEqual(callback_theme, ThemeType.DARK.value)

        # 移除回调
        self.theme_manager.remove_theme_change_callback(test_callback)

        # 重置标志
        callback_called = False
        callback_theme = None

        # 再次切换主题
        self.theme_manager.set_theme(ThemeType.LIGHT.value)

        # 验证回调未被调用
        self.assertFalse(callback_called)
        self.assertIsNone(callback_theme)

    def test_get_theme_colors(self):
        """测试获取主题颜色"""
        colors = self.theme_manager.get_theme_colors(ThemeType.DEFAULT.value)

        self.assertIsInstance(colors, dict)
        self.assertIn("primary", colors)
        self.assertIn("bg_primary", colors)
        self.assertIn("text_primary", colors)

    def test_get_theme_fonts(self):
        """测试获取主题字体"""
        fonts = self.theme_manager.get_theme_fonts(ThemeType.DEFAULT.value)

        self.assertIsInstance(fonts, dict)
        self.assertIn("default", fonts)

        default_font = fonts["default"]
        self.assertIn("family", default_font)
        self.assertIn("size", default_font)
        self.assertIn("weight", default_font)

    def test_get_theme_spacing(self):
        """测试获取主题间距"""
        spacing = self.theme_manager.get_theme_spacing(ThemeType.DEFAULT.value)

        self.assertIsInstance(spacing, dict)
        self.assertIn("padding_small", spacing)
        self.assertIn("padding_medium", spacing)
        self.assertIn("padding_large", spacing)

    def test_apply_theme_to_widget(self):
        """测试将主题应用到组件"""
        # 创建测试组件
        frame = ttk.Frame(self.root)

        # 应用主题到组件
        self.theme_manager.apply_theme_to_widget(frame, ThemeType.DARK.value)

        # 这里主要测试不会抛出异常
        # 实际的样式应用效果在GUI环境中才能验证

    def test_reset_to_default(self):
        """测试重置为默认主题"""
        # 先切换到其他主题
        self.theme_manager.set_theme(ThemeType.DARK.value)
        self.assertEqual(self.theme_manager.get_current_theme(), ThemeType.DARK.value)

        # 重置为默认主题
        self.theme_manager.reset_to_default()
        self.assertEqual(
            self.theme_manager.get_current_theme(), ThemeType.DEFAULT.value
        )

    def test_config_persistence(self):
        """测试配置持久化"""
        # 创建自定义主题
        theme_id = "test_persistence"
        self.theme_manager.create_custom_theme(theme_id, "持久化测试主题")

        # 切换到自定义主题
        self.theme_manager.set_theme(theme_id)

        # 验证配置文件存在
        self.assertTrue(self.theme_manager.config_file.exists())

        # 读取配置文件
        with open(self.theme_manager.config_file, encoding="utf-8") as f:
            config = json.load(f)

        self.assertEqual(config["current_theme"], theme_id)
        self.assertIn(theme_id, config["custom_themes"])

    def test_error_handling(self):
        """测试错误处理"""
        # 测试导出不存在的主题
        success = self.theme_manager.export_theme("nonexistent", "/tmp/test.json")
        self.assertFalse(success)

        # 测试导入不存在的文件
        success = self.theme_manager.import_theme("/nonexistent/file.json")
        self.assertFalse(success)

        # 测试删除不存在的主题
        success = self.theme_manager.delete_custom_theme("nonexistent")
        self.assertFalse(success)


class TestGlobalTTKThemeManager(unittest.TestCase):
    """全局TTK主题管理器测试类"""

    def setUp(self):
        """测试前准备"""
        # 重置全局实例
        import minicrm.ui.ttk_base.theme_manager as theme_module

        theme_module._global_ttk_theme_manager = None

    def test_get_global_instance(self):
        """测试获取全局实例"""
        manager1 = get_global_ttk_theme_manager()
        manager2 = get_global_ttk_theme_manager()

        # 验证单例模式
        self.assertIs(manager1, manager2)
        self.assertIsInstance(manager1, TTKThemeManager)

    def test_apply_global_theme(self):
        """测试应用全局主题"""
        success = apply_global_ttk_theme(ThemeType.DARK.value)
        self.assertTrue(success)

        manager = get_global_ttk_theme_manager()
        self.assertEqual(manager.get_current_theme(), ThemeType.DARK.value)


class TestThemeManagerIntegration(unittest.TestCase):
    """主题管理器集成测试类"""

    def setUp(self):
        """测试前准备"""
        self.root = tk.Tk()
        self.root.withdraw()

        self.theme_manager = TTKThemeManager(self.root)

    def tearDown(self):
        """测试后清理"""
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def test_theme_switching_workflow(self):
        """测试主题切换工作流程"""
        # 1. 获取初始主题
        initial_theme = self.theme_manager.get_current_theme()

        # 2. 切换到深色主题
        success = self.theme_manager.set_theme(ThemeType.DARK.value)
        self.assertTrue(success)
        self.assertEqual(self.theme_manager.get_current_theme(), ThemeType.DARK.value)

        # 3. 创建自定义主题
        custom_theme_id = "workflow_test"
        success = self.theme_manager.create_custom_theme(
            custom_theme_id, "工作流程测试主题", colors={"primary": "#FF5722"}
        )
        self.assertTrue(success)

        # 4. 切换到自定义主题
        success = self.theme_manager.set_theme(custom_theme_id)
        self.assertTrue(success)
        self.assertEqual(self.theme_manager.get_current_theme(), custom_theme_id)

        # 5. 验证自定义主题配置
        config = self.theme_manager.get_theme_config(custom_theme_id)
        self.assertEqual(config["colors"]["primary"], "#FF5722")

        # 6. 重置为默认主题
        self.theme_manager.reset_to_default()
        self.assertEqual(
            self.theme_manager.get_current_theme(), ThemeType.DEFAULT.value
        )

    def test_custom_theme_lifecycle(self):
        """测试自定义主题生命周期"""
        theme_id = "lifecycle_test"
        theme_name = "生命周期测试主题"

        # 1. 创建自定义主题
        success = self.theme_manager.create_custom_theme(
            theme_id,
            theme_name,
            colors={"primary": "#9C27B0", "bg_primary": "#F3E5F5"},
            fonts={"default": {"family": "Courier New", "size": 11}},
            spacing={"padding_small": 6},
        )
        self.assertTrue(success)

        # 2. 验证主题存在
        themes = self.theme_manager.get_available_themes()
        self.assertIn(theme_id, themes)
        self.assertEqual(themes[theme_id], theme_name)

        # 3. 应用主题
        success = self.theme_manager.set_theme(theme_id)
        self.assertTrue(success)

        # 4. 验证主题配置
        colors = self.theme_manager.get_theme_colors(theme_id)
        fonts = self.theme_manager.get_theme_fonts(theme_id)
        spacing = self.theme_manager.get_theme_spacing(theme_id)

        self.assertEqual(colors["primary"], "#9C27B0")
        self.assertEqual(colors["bg_primary"], "#F3E5F5")
        self.assertEqual(fonts["default"]["family"], "Courier New")
        self.assertEqual(fonts["default"]["size"], 11)
        self.assertEqual(spacing["padding_small"], 6)

        # 5. 删除主题
        success = self.theme_manager.delete_custom_theme(theme_id)
        self.assertTrue(success)

        # 6. 验证主题已删除
        themes = self.theme_manager.get_available_themes()
        self.assertNotIn(theme_id, themes)


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
