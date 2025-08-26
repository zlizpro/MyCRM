"""
样式管理器单元测试

测试StyleManager及其相关类的功能，包括：
- 主题创建和应用测试
- 样式配置和管理测试
- 自定义样式和模板测试
- 主题文件保存和加载测试
- 颜色方案和字体配置测试

作者: MiniCRM开发团队
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch


# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from src.minicrm.ui.ttk_base.style_manager import (
    ColorScheme,
    CustomTheme,
    DarkTheme,
    DefaultTheme,
    FontConfig,
    HighContrastTheme,
    LightTheme,
    SpacingConfig,
    StyleManager,
    ThemeType,
    apply_global_theme,
    get_global_style_manager,
)


class TestColorScheme(unittest.TestCase):
    """颜色方案测试类"""

    def test_color_scheme_creation(self):
        """测试颜色方案创建"""
        colors = ColorScheme()

        # 测试默认颜色
        self.assertEqual(colors.primary, "#007BFF")
        self.assertEqual(colors.bg_primary, "#FFFFFF")
        self.assertEqual(colors.text_primary, "#212529")
        self.assertEqual(colors.border_primary, "#DEE2E6")

    def test_color_scheme_customization(self):
        """测试颜色方案自定义"""
        colors = ColorScheme(
            primary="#FF0000", bg_primary="#000000", text_primary="#FFFFFF"
        )

        self.assertEqual(colors.primary, "#FF0000")
        self.assertEqual(colors.bg_primary, "#000000")
        self.assertEqual(colors.text_primary, "#FFFFFF")


class TestFontConfig(unittest.TestCase):
    """字体配置测试类"""

    def test_font_config_creation(self):
        """测试字体配置创建"""
        font = FontConfig()

        self.assertEqual(font.family, "Microsoft YaHei UI")
        self.assertEqual(font.size, 9)
        self.assertEqual(font.weight, "normal")
        self.assertEqual(font.slant, "roman")

    def test_font_config_to_tuple(self):
        """测试字体配置转换为元组"""
        font = FontConfig(family="Arial", size=12, weight="bold")
        font_tuple = font.to_tuple()

        self.assertEqual(font_tuple, ("Arial", 12, "bold", "roman"))

    def test_font_config_customization(self):
        """测试字体配置自定义"""
        font = FontConfig(
            family="Times New Roman", size=14, weight="bold", slant="italic"
        )

        self.assertEqual(font.family, "Times New Roman")
        self.assertEqual(font.size, 14)
        self.assertEqual(font.weight, "bold")
        self.assertEqual(font.slant, "italic")


class TestSpacingConfig(unittest.TestCase):
    """间距配置测试类"""

    def test_spacing_config_creation(self):
        """测试间距配置创建"""
        spacing = SpacingConfig()

        self.assertEqual(spacing.padding_small, 2)
        self.assertEqual(spacing.padding_medium, 5)
        self.assertEqual(spacing.padding_large, 10)
        self.assertEqual(spacing.border_width, 1)

    def test_spacing_config_customization(self):
        """测试间距配置自定义"""
        spacing = SpacingConfig(
            padding_small=1, padding_medium=3, padding_large=8, border_width=2
        )

        self.assertEqual(spacing.padding_small, 1)
        self.assertEqual(spacing.padding_medium, 3)
        self.assertEqual(spacing.padding_large, 8)
        self.assertEqual(spacing.border_width, 2)


class TestBaseTheme(unittest.TestCase):
    """基础主题测试类"""

    def test_default_theme_creation(self):
        """测试默认主题创建"""
        theme = DefaultTheme()

        self.assertEqual(theme.name, "default")
        self.assertIsInstance(theme.colors, ColorScheme)
        self.assertIn("default", theme.fonts)
        self.assertIn("heading", theme.fonts)
        self.assertIsInstance(theme.spacing, SpacingConfig)

    def test_dark_theme_colors(self):
        """测试深色主题颜色配置"""
        theme = DarkTheme()
        theme.configure_colors()

        self.assertEqual(theme.colors.bg_primary, "#2B2B2B")
        self.assertEqual(theme.colors.text_primary, "#FFFFFF")
        self.assertEqual(theme.colors.border_primary, "#555555")

    def test_light_theme_colors(self):
        """测试浅色主题颜色配置"""
        theme = LightTheme()
        theme.configure_colors()

        self.assertEqual(theme.colors.bg_primary, "#FAFAFA")
        self.assertEqual(theme.colors.text_primary, "#333333")
        self.assertEqual(theme.colors.border_primary, "#DDDDDD")

    def test_high_contrast_theme_colors(self):
        """测试高对比度主题颜色配置"""
        theme = HighContrastTheme()
        theme.configure_colors()

        self.assertEqual(theme.colors.bg_primary, "#FFFFFF")
        self.assertEqual(theme.colors.text_primary, "#000000")
        self.assertEqual(theme.colors.primary, "#0000FF")
        self.assertEqual(theme.colors.border_primary, "#000000")

    def test_theme_style_config(self):
        """测试主题样式配置"""
        theme = DefaultTheme()
        config = theme.get_style_config()

        self.assertIn("colors", config)
        self.assertIn("fonts", config)
        self.assertIn("spacing", config)
        self.assertIn("custom_styles", config)

        # 检查颜色配置
        colors = config["colors"]
        self.assertIn("primary", colors)
        self.assertIn("bg_primary", colors)

        # 检查字体配置
        fonts = config["fonts"]
        self.assertIn("default", fonts)
        self.assertIn("heading", fonts)


class TestStyleManagerLogic(unittest.TestCase):
    """样式管理器逻辑测试类（无需GUI）"""

    def setUp(self):
        """测试准备"""
        # 使用Mock对象模拟ttk.Style
        with patch(
            "src.minicrm.ui.ttk_base.style_manager.ttk.Style"
        ) as mock_style_class:
            self.mock_style = Mock()
            mock_style_class.return_value = self.mock_style
            self.style_manager = StyleManager()

    def test_style_manager_creation(self):
        """测试样式管理器创建"""
        self.assertIsNotNone(self.style_manager)
        self.assertIsNotNone(self.style_manager.themes)
        self.assertIn(ThemeType.DEFAULT.value, self.style_manager.themes)
        self.assertIn(ThemeType.DARK.value, self.style_manager.themes)
        self.assertIn(ThemeType.LIGHT.value, self.style_manager.themes)
        self.assertIn(ThemeType.HIGH_CONTRAST.value, self.style_manager.themes)

    def test_register_custom_theme(self):
        """测试注册自定义主题"""
        custom_theme = DefaultTheme()
        custom_theme.name = "custom_test"

        self.style_manager.register_theme(custom_theme)

        self.assertIn("custom_test", self.style_manager.themes)
        self.assertEqual(self.style_manager.themes["custom_test"], custom_theme)

    def test_apply_theme(self):
        """测试应用主题"""
        # 测试应用存在的主题
        result = self.style_manager.apply_theme(ThemeType.DARK.value)
        self.assertTrue(result)
        self.assertEqual(self.style_manager.current_theme.name, ThemeType.DARK.value)

        # 测试应用不存在的主题
        result = self.style_manager.apply_theme("nonexistent")
        self.assertFalse(result)

    def test_get_available_themes(self):
        """测试获取可用主题列表"""
        themes = self.style_manager.get_available_themes()

        self.assertIn(ThemeType.DEFAULT.value, themes)
        self.assertIn(ThemeType.DARK.value, themes)
        self.assertIn(ThemeType.LIGHT.value, themes)
        self.assertIn(ThemeType.HIGH_CONTRAST.value, themes)

    def test_create_custom_style(self):
        """测试创建自定义样式"""
        self.style_manager.create_custom_style(
            "CustomButton.TButton", background="#FF0000", foreground="#FFFFFF"
        )

        # 验证样式配置被调用
        self.mock_style.configure.assert_called_with(
            "CustomButton.TButton", background="#FF0000", foreground="#FFFFFF"
        )

    def test_create_style_template(self):
        """测试创建样式模板"""
        template_config = {
            "background": "#FF0000",
            "foreground": "#FFFFFF",
            "padding": 5,
        }

        self.style_manager.create_style_template("red_button", template_config)

        self.assertIn("red_button", self.style_manager.style_templates)
        self.assertEqual(
            self.style_manager.style_templates["red_button"], template_config
        )

    def test_apply_style_template(self):
        """测试应用样式模板"""
        # 先创建模板
        template_config = {"background": "#FF0000", "foreground": "#FFFFFF"}
        self.style_manager.create_style_template("test_template", template_config)

        # 应用模板
        self.style_manager.apply_style_template(
            "TestButton.TButton",
            "test_template",
            padding=10,  # 覆盖选项
        )

        # 验证样式配置被调用
        expected_config = template_config.copy()
        expected_config["padding"] = 10
        self.mock_style.configure.assert_called_with(
            "TestButton.TButton", **expected_config
        )

    def test_theme_change_callbacks(self):
        """测试主题变化回调"""
        callback1 = Mock()
        callback2 = Mock()

        # 添加回调
        self.style_manager.add_theme_change_callback(callback1)
        self.style_manager.add_theme_change_callback(callback2)

        # 应用主题
        self.style_manager.apply_theme(ThemeType.DARK.value)

        # 验证回调被调用
        callback1.assert_called_once_with(ThemeType.DARK.value)
        callback2.assert_called_once_with(ThemeType.DARK.value)

        # 移除回调
        self.style_manager.remove_theme_change_callback(callback1)

        # 再次应用主题
        self.style_manager.apply_theme(ThemeType.LIGHT.value)

        # 验证只有callback2被调用
        callback2.assert_called_with(ThemeType.LIGHT.value)
        self.assertEqual(callback1.call_count, 1)  # 仍然是1次


class TestCustomTheme(unittest.TestCase):
    """自定义主题测试类"""

    def test_custom_theme_creation(self):
        """测试自定义主题创建"""
        config = {
            "colors": {"primary": "#FF0000", "bg_primary": "#000000"},
            "fonts": {
                "default": {
                    "family": "Arial",
                    "size": 10,
                    "weight": "normal",
                    "slant": "roman",
                }
            },
            "spacing": {"padding_small": 3, "border_width": 2},
            "custom_styles": {"CustomButton.TButton": {"background": "#00FF00"}},
        }

        theme = CustomTheme("test_custom", config)

        self.assertEqual(theme.name, "test_custom")
        self.assertEqual(theme.colors.primary, "#FF0000")
        self.assertEqual(theme.colors.bg_primary, "#000000")
        self.assertEqual(theme.fonts["default"].family, "Arial")
        self.assertEqual(theme.fonts["default"].size, 10)
        self.assertEqual(theme.spacing.padding_small, 3)
        self.assertEqual(theme.spacing.border_width, 2)
        self.assertIn("CustomButton.TButton", theme.custom_styles)


class TestThemeFileOperations(unittest.TestCase):
    """主题文件操作测试类"""

    def setUp(self):
        """测试准备"""
        with patch(
            "src.minicrm.ui.ttk_base.style_manager.ttk.Style"
        ) as mock_style_class:
            self.mock_style = Mock()
            mock_style_class.return_value = self.mock_style
            self.style_manager = StyleManager()

        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """测试清理"""
        # 清理临时文件
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_theme_to_file(self):
        """测试保存主题到文件"""
        theme_file = os.path.join(self.temp_dir, "test_theme.json")

        result = self.style_manager.save_theme_to_file(
            ThemeType.DEFAULT.value, theme_file
        )

        self.assertTrue(result)
        self.assertTrue(os.path.exists(theme_file))

        # 验证文件内容
        with open(theme_file, encoding="utf-8") as f:
            saved_config = json.load(f)

        self.assertIn("colors", saved_config)
        self.assertIn("fonts", saved_config)
        self.assertIn("spacing", saved_config)

    def test_load_theme_from_file(self):
        """测试从文件加载主题"""
        # 创建测试主题文件
        theme_config = {
            "colors": {"primary": "#FF0000", "bg_primary": "#000000"},
            "fonts": {
                "default": {
                    "family": "Arial",
                    "size": 12,
                    "weight": "bold",
                    "slant": "roman",
                }
            },
            "spacing": {"padding_small": 4},
            "custom_styles": {},
        }

        theme_file = os.path.join(self.temp_dir, "custom_theme.json")
        with open(theme_file, "w", encoding="utf-8") as f:
            json.dump(theme_config, f)

        # 加载主题
        result = self.style_manager.load_theme_from_file(theme_file, "loaded_theme")

        self.assertTrue(result)
        self.assertIn("loaded_theme", self.style_manager.themes)

        # 验证主题配置
        loaded_theme = self.style_manager.themes["loaded_theme"]
        self.assertEqual(loaded_theme.colors.primary, "#FF0000")
        self.assertEqual(loaded_theme.colors.bg_primary, "#000000")
        self.assertEqual(loaded_theme.fonts["default"].family, "Arial")
        self.assertEqual(loaded_theme.fonts["default"].size, 12)

    def test_save_nonexistent_theme(self):
        """测试保存不存在的主题"""
        theme_file = os.path.join(self.temp_dir, "nonexistent.json")

        result = self.style_manager.save_theme_to_file("nonexistent", theme_file)

        self.assertFalse(result)
        self.assertFalse(os.path.exists(theme_file))

    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.json")

        result = self.style_manager.load_theme_from_file(nonexistent_file)

        self.assertFalse(result)


class TestGlobalStyleManager(unittest.TestCase):
    """全局样式管理器测试类"""

    def test_get_global_style_manager(self):
        """测试获取全局样式管理器"""
        with patch("src.minicrm.ui.ttk_base.style_manager.ttk.Style"):
            manager1 = get_global_style_manager()
            manager2 = get_global_style_manager()

            # 应该返回同一个实例
            self.assertIs(manager1, manager2)
            self.assertIsInstance(manager1, StyleManager)

    def test_apply_global_theme(self):
        """测试应用全局主题"""
        with patch("src.minicrm.ui.ttk_base.style_manager.ttk.Style"):
            result = apply_global_theme(ThemeType.DARK.value)
            self.assertTrue(result)


class TestThemeTypes(unittest.TestCase):
    """主题类型测试类"""

    def test_theme_type_enum(self):
        """测试主题类型枚举"""
        self.assertEqual(ThemeType.DEFAULT.value, "default")
        self.assertEqual(ThemeType.DARK.value, "dark")
        self.assertEqual(ThemeType.LIGHT.value, "light")
        self.assertEqual(ThemeType.HIGH_CONTRAST.value, "high_contrast")
        self.assertEqual(ThemeType.CUSTOM.value, "custom")


if __name__ == "__main__":
    # 运行所有测试
    unittest.main(verbosity=2)
