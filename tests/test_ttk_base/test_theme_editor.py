"""TTK主题编辑器测试

测试TTK主题编辑器的各项功能，包括：
- 主题编辑器界面创建
- 颜色选择器功能
- 字体配置功能
- 主题预览功能
- 主题导入导出功能

作者: MiniCRM开发团队
"""

import json
import os
from pathlib import Path

# 添加src路径以便导入模块
import sys
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock, patch


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from minicrm.ui.ttk_base.style_manager import ThemeType
from minicrm.ui.ttk_base.theme_editor import (
    ColorPickerFrame,
    FontConfigFrame,
    ThemeEditorTTK,
    ThemePreviewFrame,
    show_theme_editor,
)
from minicrm.ui.ttk_base.theme_manager import TTKThemeManager


class TestColorPickerFrame(unittest.TestCase):
    """颜色选择器框架测试类"""

    def setUp(self):
        """测试前准备"""
        self.root = tk.Tk()
        self.root.withdraw()

        self.color_changed = False
        self.changed_color = None

        def on_color_change(color):
            self.color_changed = True
            self.changed_color = color

        self.color_picker = ColorPickerFrame(
            self.root, "测试颜色", "#FF0000", on_color_change
        )

    def tearDown(self):
        """测试后清理"""
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.color_picker)
        self.assertEqual(self.color_picker.get_color(), "#FF0000")
        self.assertIsNotNone(self.color_picker.label)
        self.assertIsNotNone(self.color_picker.color_button)
        self.assertIsNotNone(self.color_picker.color_label)

    def test_set_color(self):
        """测试设置颜色"""
        new_color = "#00FF00"
        self.color_picker.set_color(new_color)

        self.assertEqual(self.color_picker.get_color(), new_color)
        self.assertEqual(self.color_picker.color_label.cget("text"), new_color)
        self.assertTrue(self.color_changed)
        self.assertEqual(self.changed_color, new_color)

    def test_get_color(self):
        """测试获取颜色"""
        color = self.color_picker.get_color()
        self.assertEqual(color, "#FF0000")

    @patch("tkinter.colorchooser.askcolor")
    def test_choose_color(self, mock_askcolor):
        """测试选择颜色"""
        # 模拟用户选择颜色
        mock_askcolor.return_value = ((0, 255, 0), "#00FF00")

        # 触发颜色选择
        self.color_picker._choose_color()

        # 验证颜色已更新
        self.assertEqual(self.color_picker.get_color(), "#00FF00")
        self.assertTrue(self.color_changed)

    @patch("tkinter.colorchooser.askcolor")
    def test_choose_color_cancel(self, mock_askcolor):
        """测试取消颜色选择"""
        # 模拟用户取消选择
        mock_askcolor.return_value = (None, None)

        original_color = self.color_picker.get_color()

        # 触发颜色选择
        self.color_picker._choose_color()

        # 验证颜色未改变
        self.assertEqual(self.color_picker.get_color(), original_color)


class TestFontConfigFrame(unittest.TestCase):
    """字体配置框架测试类"""

    def setUp(self):
        """测试前准备"""
        self.root = tk.Tk()
        self.root.withdraw()

        self.font_changed = False
        self.changed_font = None

        def on_font_change(font_config):
            self.font_changed = True
            self.changed_font = font_config

        initial_config = {
            "family": "Arial",
            "size": 12,
            "weight": "bold",
            "slant": "roman",
        }

        self.font_config = FontConfigFrame(
            self.root, "测试字体", initial_config, on_font_change
        )

    def tearDown(self):
        """测试后清理"""
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.font_config)
        config = self.font_config.get_font_config()
        self.assertEqual(config["family"], "Arial")
        self.assertEqual(config["size"], 12)
        self.assertEqual(config["weight"], "bold")

    def test_get_font_config(self):
        """测试获取字体配置"""
        config = self.font_config.get_font_config()

        self.assertIsInstance(config, dict)
        self.assertIn("family", config)
        self.assertIn("size", config)
        self.assertIn("weight", config)
        self.assertIn("slant", config)

    def test_set_font_config(self):
        """测试设置字体配置"""
        new_config = {
            "family": "Times New Roman",
            "size": 14,
            "weight": "normal",
            "slant": "roman",
        }

        self.font_config.set_font_config(new_config)

        config = self.font_config.get_font_config()
        self.assertEqual(config["family"], "Times New Roman")
        self.assertEqual(config["size"], 14)
        self.assertEqual(config["weight"], "normal")

    def test_font_change_callback(self):
        """测试字体变化回调"""
        # 模拟字体族变化
        self.font_config.family_var.set("Courier New")
        self.font_config._on_font_change()

        self.assertTrue(self.font_changed)
        self.assertEqual(self.changed_font["family"], "Courier New")


class TestThemePreviewFrame(unittest.TestCase):
    """主题预览框架测试类"""

    def setUp(self):
        """测试前准备"""
        self.root = tk.Tk()
        self.root.withdraw()

        self.preview_frame = ThemePreviewFrame(self.root)

    def tearDown(self):
        """测试后清理"""
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.preview_frame)

        # 验证预览组件存在
        children = self.preview_frame.winfo_children()
        self.assertGreater(len(children), 0)


class TestThemeEditorTTK(unittest.TestCase):
    """TTK主题编辑器测试类"""

    def setUp(self):
        """测试前准备"""
        self.root = tk.Tk()
        self.root.withdraw()

        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()

        # 创建主题管理器
        self.theme_manager = TTKThemeManager(self.root)
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
        editor = ThemeEditorTTK(self.root, self.theme_manager)

        self.assertIsNotNone(editor)
        self.assertEqual(editor.theme_manager, self.theme_manager)
        self.assertIsInstance(editor.current_theme_config, dict)
        self.assertIsInstance(editor.color_pickers, dict)
        self.assertIsInstance(editor.font_configs, dict)

        # 不显示对话框，直接销毁
        editor.destroy()

    def test_load_theme_config(self):
        """测试加载主题配置"""
        editor = ThemeEditorTTK(self.root, self.theme_manager)

        # 加载默认主题配置
        editor._load_theme_config(ThemeType.DEFAULT.value)

        self.assertIn("colors", editor.current_theme_config)
        self.assertIn("fonts", editor.current_theme_config)
        self.assertEqual(editor.current_theme_id, ThemeType.DEFAULT.value)

        editor.destroy()

    def test_color_change_handling(self):
        """测试颜色变化处理"""
        editor = ThemeEditorTTK(self.root, self.theme_manager)

        # 模拟颜色变化
        editor._on_color_change("primary", "#FF5722")

        self.assertEqual(editor.current_theme_config["colors"]["primary"], "#FF5722")

        editor.destroy()

    def test_font_change_handling(self):
        """测试字体变化处理"""
        editor = ThemeEditorTTK(self.root, self.theme_manager)

        # 模拟字体变化
        font_config = {"family": "Helvetica", "size": 11, "weight": "bold"}
        editor._on_font_change("default", font_config)

        self.assertEqual(editor.current_theme_config["fonts"]["default"], font_config)

        editor.destroy()

    def test_spacing_change_handling(self):
        """测试间距变化处理"""
        editor = ThemeEditorTTK(self.root, self.theme_manager)

        # 设置间距变量
        editor.spacing_vars = {
            "padding_small": tk.StringVar(value="8"),
            "padding_medium": tk.StringVar(value="12"),
        }

        # 模拟间距变化
        editor._on_spacing_change()

        self.assertEqual(editor.current_theme_config["spacing"]["padding_small"], 8)
        self.assertEqual(editor.current_theme_config["spacing"]["padding_medium"], 12)

        editor.destroy()

    @patch("tkinter.filedialog.askopenfilename")
    def test_import_theme(self, mock_filedialog):
        """测试导入主题"""
        editor = ThemeEditorTTK(self.root, self.theme_manager)

        # 创建测试主题文件
        theme_config = {
            "name": "导入测试主题",
            "colors": {"primary": "#E91E63"},
            "fonts": {"default": {"family": "Georgia", "size": 10}},
            "spacing": {"padding_small": 5},
        }

        import_file = os.path.join(self.temp_dir, "import_test.json")
        with open(import_file, "w", encoding="utf-8") as f:
            json.dump(theme_config, f)

        # 模拟文件选择
        mock_filedialog.return_value = import_file

        with patch("tkinter.messagebox.showinfo") as mock_info:
            editor._import_theme()
            mock_info.assert_called_once()

        editor.destroy()

    @patch("tkinter.filedialog.asksaveasfilename")
    def test_export_theme(self, mock_filedialog):
        """测试导出主题"""
        editor = ThemeEditorTTK(self.root, self.theme_manager)

        # 设置主题配置
        editor.current_theme_config = {
            "colors": {"primary": "#3F51B5"},
            "fonts": {"default": {"family": "Verdana", "size": 9}},
            "spacing": {"padding_small": 4},
        }
        editor.theme_name_var.set("导出测试主题")

        export_file = os.path.join(self.temp_dir, "export_test.json")
        mock_filedialog.return_value = export_file

        with patch("tkinter.messagebox.showinfo") as mock_info:
            editor._export_theme()
            mock_info.assert_called_once()

        # 验证文件已创建
        self.assertTrue(os.path.exists(export_file))

        editor.destroy()

    def test_reset_theme(self):
        """测试重置主题"""
        editor = ThemeEditorTTK(self.root, self.theme_manager)

        # 修改配置
        editor.current_theme_config["colors"] = {"primary": "#CHANGED"}

        # 重置主题
        editor._reset_theme()

        # 验证配置已重置
        self.assertNotEqual(
            editor.current_theme_config["colors"]["primary"], "#CHANGED"
        )

        editor.destroy()

    @patch("tkinter.messagebox.showinfo")
    def test_apply_theme(self, mock_info):
        """测试应用主题"""
        editor = ThemeEditorTTK(self.root, self.theme_manager)

        # 设置主题名称
        editor.theme_name_var.set("测试应用主题")

        # 设置主题配置
        editor.current_theme_config = {
            "colors": {"primary": "#607D8B"},
            "fonts": {"default": {"family": "Tahoma", "size": 9}},
            "spacing": {"padding_small": 3},
        }

        # 应用主题
        editor._apply_theme()

        # 验证成功消息
        mock_info.assert_called_once()

        editor.destroy()

    @patch("tkinter.messagebox.showinfo")
    def test_save_theme(self, mock_info):
        """测试保存主题"""
        editor = ThemeEditorTTK(self.root, self.theme_manager)

        # 设置主题名称
        editor.theme_name_var.set("测试保存主题")

        # 设置主题配置
        editor.current_theme_config = {
            "colors": {"primary": "#795548"},
            "fonts": {"default": {"family": "Calibri", "size": 10}},
            "spacing": {"padding_small": 6},
        }

        # 保存主题
        with patch.object(editor, "destroy") as mock_destroy:
            editor._save_theme()
            mock_destroy.assert_called_once()

        # 验证成功消息
        mock_info.assert_called_once()

    @patch("tkinter.messagebox.showerror")
    def test_save_theme_without_name(self, mock_error):
        """测试保存主题时没有名称"""
        editor = ThemeEditorTTK(self.root, self.theme_manager)

        # 不设置主题名称
        editor.theme_name_var.set("")

        # 尝试保存主题
        editor._save_theme()

        # 验证错误消息
        mock_error.assert_called_once()

        editor.destroy()


class TestThemeEditorIntegration(unittest.TestCase):
    """主题编辑器集成测试类"""

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

    def test_theme_editing_workflow(self):
        """测试主题编辑工作流程"""
        editor = ThemeEditorTTK(self.root, self.theme_manager)

        # 1. 加载基础主题
        editor._load_theme_config(ThemeType.LIGHT.value)
        self.assertEqual(editor.current_theme_id, ThemeType.LIGHT.value)

        # 2. 修改颜色
        editor._on_color_change("primary", "#FF9800")
        self.assertEqual(editor.current_theme_config["colors"]["primary"], "#FF9800")

        # 3. 修改字体
        font_config = {"family": "Comic Sans MS", "size": 13, "weight": "normal"}
        editor._on_font_change("default", font_config)
        self.assertEqual(editor.current_theme_config["fonts"]["default"], font_config)

        # 4. 设置主题名称并保存
        editor.theme_name_var.set("集成测试主题")

        with patch("tkinter.messagebox.showinfo"):
            with patch.object(editor, "destroy"):
                editor._save_theme()

        # 5. 验证主题已创建
        themes = self.theme_manager.get_available_themes()
        self.assertIn(editor.current_theme_id, themes)

        editor.destroy()

    def test_color_picker_integration(self):
        """测试颜色选择器集成"""
        editor = ThemeEditorTTK(self.root, self.theme_manager)

        # 创建颜色选择器
        color_picker = ColorPickerFrame(
            editor.content_frame,
            "集成测试颜色",
            "#4CAF50",
            lambda color: editor._on_color_change("test_color", color),
        )

        # 模拟颜色变化
        color_picker.set_color("#8BC34A")

        # 验证主题配置已更新
        self.assertEqual(editor.current_theme_config["colors"]["test_color"], "#8BC34A")

        editor.destroy()

    def test_font_config_integration(self):
        """测试字体配置集成"""
        editor = ThemeEditorTTK(self.root, self.theme_manager)

        # 创建字体配置器
        font_config = FontConfigFrame(
            editor.content_frame,
            "集成测试字体",
            {"family": "Impact", "size": 15, "weight": "bold"},
            lambda config: editor._on_font_change("test_font", config),
        )

        # 模拟字体变化
        new_config = {"family": "Trebuchet MS", "size": 11, "weight": "normal"}
        font_config.set_font_config(new_config)
        font_config._on_font_change()

        # 验证主题配置已更新
        self.assertEqual(
            editor.current_theme_config["fonts"]["test_font"]["family"], "Trebuchet MS"
        )

        editor.destroy()


class TestShowThemeEditor(unittest.TestCase):
    """显示主题编辑器函数测试类"""

    def setUp(self):
        """测试前准备"""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """测试后清理"""
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    @patch("minicrm.ui.ttk_base.theme_editor.ThemeEditorTTK")
    def test_show_theme_editor(self, mock_editor_class):
        """测试显示主题编辑器函数"""
        mock_editor = Mock()
        mock_editor_class.return_value = mock_editor

        # 调用函数
        show_theme_editor(self.root)

        # 验证编辑器被创建和显示
        mock_editor_class.assert_called_once_with(self.root, None)
        mock_editor.show_modal.assert_called_once()

    @patch("minicrm.ui.ttk_base.theme_editor.ThemeEditorTTK")
    def test_show_theme_editor_with_manager(self, mock_editor_class):
        """测试使用指定主题管理器显示编辑器"""
        mock_editor = Mock()
        mock_editor_class.return_value = mock_editor

        theme_manager = TTKThemeManager(self.root)

        # 调用函数
        show_theme_editor(self.root, theme_manager)

        # 验证编辑器被创建和显示
        mock_editor_class.assert_called_once_with(self.root, theme_manager)
        mock_editor.show_modal.assert_called_once()


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
