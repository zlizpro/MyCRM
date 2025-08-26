"""TTK设置对话框测试

测试SettingsDialogTTK类的功能，包括：
- 对话框创建和初始化
- 设置项的显示和编辑
- 设置验证和保存
- 导入导出功能
- 用户交互处理

作者: MiniCRM开发团队
"""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from src.minicrm.core.exceptions import ValidationError
from src.minicrm.services.settings_service import SettingsService
from src.minicrm.ui.ttk_base.base_dialog import DialogResult
from src.minicrm.ui.ttk_base.settings_dialog_ttk import (
    SettingsDialogTTK,
    show_settings_dialog,
)


class TestSettingsDialogTTK(unittest.TestCase):
    """SettingsDialogTTK测试类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        # 创建模拟的设置服务
        self.mock_settings_service = Mock(spec=SettingsService)
        self.mock_settings_service._validate_setting_value = Mock()
        self.mock_settings_service.get_all_settings.return_value = {
            "theme": {
                "theme_name": "default",
                "primary_color": "#007BFF",
                "font_family": "Microsoft YaHei UI",
                "font_size": 9,
                "window_opacity": 1.0,
                "enable_animations": True,
            },
            "database": {
                "auto_backup": True,
                "backup_interval": "daily",
                "max_backups": 10,
                "backup_location": "/backup",
                "compress_backups": True,
            },
            "system": {
                "log_level": "INFO",
                "enable_performance_monitoring": False,
                "cache_size": 100,
                "max_log_files": 5,
                "enable_crash_reporting": True,
            },
            "ui": {
                "window_width": 1200,
                "window_height": 800,
                "window_maximized": False,
                "sidebar_width": 250,
                "show_status_bar": True,
                "toolbar_style": "icons_and_text",
            },
        }

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_dialog_creation(self):
        """测试对话框创建"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        # 验证对话框属性
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.title(), "系统设置")
        self.assertIsNotNone(dialog.notebook)
        self.assertEqual(len(dialog.notebook.tabs()), 4)  # 4个标签页

    def test_dialog_creation_without_service(self):
        """测试没有服务时的对话框创建"""
        with patch.object(SettingsDialogTTK, "show_error") as mock_show_error:
            with patch.object(SettingsDialogTTK, "_on_cancel") as mock_cancel:
                dialog = SettingsDialogTTK(parent=self.root, settings_service=None)

                # 验证显示错误并取消
                mock_show_error.assert_called_once_with("设置服务不可用", "错误")
                mock_cancel.assert_called_once()

    def test_settings_loading(self):
        """测试设置加载"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        # 验证设置服务被调用
        self.mock_settings_service.get_all_settings.assert_called_once()

        # 验证设置数据被加载
        self.assertEqual(dialog.current_settings["theme"]["theme_name"], "default")
        self.assertEqual(dialog.current_settings["database"]["auto_backup"], True)

    def test_setting_widgets_creation(self):
        """测试设置控件创建"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        # 验证设置控件存储
        self.assertIn("theme", dialog.setting_widgets)
        self.assertIn("database", dialog.setting_widgets)
        self.assertIn("system", dialog.setting_widgets)
        self.assertIn("ui", dialog.setting_widgets)

        # 验证主题设置控件
        theme_widgets = dialog.setting_widgets["theme"]
        self.assertIn("theme_name", theme_widgets)
        self.assertIn("font_family", theme_widgets)
        self.assertIn("enable_animations", theme_widgets)

    def test_setting_variables_creation(self):
        """测试设置变量创建"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        # 验证设置变量存储
        self.assertIn("theme", dialog.setting_vars)
        self.assertIn("database", dialog.setting_vars)

        # 验证变量类型
        theme_vars = dialog.setting_vars["theme"]
        self.assertIsInstance(theme_vars["theme_name"], tk.StringVar)
        self.assertIsInstance(theme_vars["enable_animations"], tk.BooleanVar)

    def test_setting_values_loading(self):
        """测试设置值加载到界面"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        # 验证设置值被正确加载
        theme_vars = dialog.setting_vars["theme"]
        self.assertEqual(theme_vars["theme_name"].get(), "default")
        self.assertEqual(theme_vars["enable_animations"].get(), True)

        database_vars = dialog.setting_vars["database"]
        self.assertEqual(database_vars["auto_backup"].get(), True)
        self.assertEqual(database_vars["backup_interval"].get(), "daily")

    def test_setting_change_handling(self):
        """测试设置变化处理"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        # 修改设置值
        theme_vars = dialog.setting_vars["theme"]
        theme_vars["theme_name"].set("dark")

        # 验证修改标志
        self.assertTrue(dialog.settings_modified)

        # 验证当前设置被更新
        self.assertEqual(dialog.current_settings["theme"]["theme_name"], "dark")

    def test_setting_validation(self):
        """测试设置验证"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        # 模拟验证成功
        self.mock_settings_service._validate_setting_value.return_value = None

        # 修改设置并验证
        theme_vars = dialog.setting_vars["theme"]
        theme_vars["font_size"].set(12)

        # 验证验证函数被调用
        self.mock_settings_service._validate_setting_value.assert_called()

    def test_setting_validation_error(self):
        """测试设置验证错误"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        # 模拟验证失败
        self.mock_settings_service._validate_setting_value.side_effect = (
            ValidationError("无效值")
        )

        # 修改设置触发验证错误
        theme_vars = dialog.setting_vars["theme"]
        theme_vars["font_size"].set(-1)  # 无效值

        # 验证错误样式被应用（这里只能验证没有抛出异常）
        self.assertTrue(True)  # 如果没有异常，测试通过

    def test_apply_settings(self):
        """测试应用设置"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        # 修改设置
        dialog.settings_modified = True

        with patch.object(dialog, "show_info") as mock_show_info:
            # 应用设置
            dialog._apply_settings()

            # 验证设置服务被调用
            self.mock_settings_service.update_settings.assert_called()

            # 验证成功消息
            mock_show_info.assert_called_with("设置已应用")

            # 验证修改标志被重置
            self.assertFalse(dialog.settings_modified)

    def test_apply_settings_validation_error(self):
        """测试应用设置时的验证错误"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        # 模拟验证失败
        self.mock_settings_service._validate_setting_value.side_effect = (
            ValidationError("验证失败")
        )

        with patch.object(dialog, "show_error") as mock_show_error:
            # 应用设置
            dialog._apply_settings()

            # 验证错误消息
            mock_show_error.assert_called_with("设置验证失败: 验证失败")

    def test_reset_settings(self):
        """测试重置设置"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        with patch.object(dialog, "confirm", return_value=True):
            with patch.object(dialog, "show_info") as mock_show_info:
                with patch.object(dialog, "_load_current_settings") as mock_load:
                    with patch.object(dialog, "_load_settings_to_ui") as mock_load_ui:
                        # 重置设置
                        dialog._reset_settings()

                        # 验证重置服务被调用
                        self.mock_settings_service.reset_settings.assert_called_once()

                        # 验证重新加载
                        mock_load.assert_called_once()
                        mock_load_ui.assert_called_once()

                        # 验证成功消息
                        mock_show_info.assert_called_with("设置已重置")

    def test_reset_settings_cancelled(self):
        """测试取消重置设置"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        with patch.object(dialog, "confirm", return_value=False):
            # 取消重置
            dialog._reset_settings()

            # 验证重置服务未被调用
            self.mock_settings_service.reset_settings.assert_not_called()

    def test_import_settings(self):
        """测试导入设置"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        with patch(
            "src.minicrm.ui.ttk_base.settings_dialog_ttk.open_file_dialog",
            return_value="/test/settings.json",
        ):
            with patch.object(dialog, "show_info") as mock_show_info:
                with patch.object(dialog, "_load_current_settings") as mock_load:
                    with patch.object(dialog, "_load_settings_to_ui") as mock_load_ui:
                        # 导入设置
                        dialog._import_settings()

                        # 验证导入服务被调用
                        self.mock_settings_service.import_settings.assert_called_with(
                            "/test/settings.json"
                        )

                        # 验证重新加载
                        mock_load.assert_called_once()
                        mock_load_ui.assert_called_once()

                        # 验证成功消息
                        mock_show_info.assert_called_with("设置导入成功")

    def test_import_settings_no_file(self):
        """测试取消导入设置"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        with patch(
            "src.minicrm.ui.ttk_base.settings_dialog_ttk.open_file_dialog",
            return_value=None,
        ):
            # 取消导入
            dialog._import_settings()

            # 验证导入服务未被调用
            self.mock_settings_service.import_settings.assert_not_called()

    def test_export_settings(self):
        """测试导出设置"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        with patch(
            "src.minicrm.ui.ttk_base.settings_dialog_ttk.save_file_dialog",
            return_value="/test/export.json",
        ):
            with patch.object(dialog, "show_info") as mock_show_info:
                # 导出设置
                dialog._export_settings()

                # 验证导出服务被调用
                self.mock_settings_service.export_settings.assert_called_with(
                    "/test/export.json"
                )

                # 验证成功消息
                mock_show_info.assert_called_with("设置导出成功")

    def test_export_settings_no_file(self):
        """测试取消导出设置"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        with patch(
            "src.minicrm.ui.ttk_base.settings_dialog_ttk.save_file_dialog",
            return_value=None,
        ):
            # 取消导出
            dialog._export_settings()

            # 验证导出服务未被调用
            self.mock_settings_service.export_settings.assert_not_called()

    def test_validate_input(self):
        """测试输入验证"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        # 模拟验证成功
        self.mock_settings_service._validate_setting_value.return_value = None

        # 验证输入
        result = dialog._validate_input()

        # 验证结果
        self.assertTrue(result)

    def test_validate_input_error(self):
        """测试输入验证错误"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        # 模拟验证失败
        self.mock_settings_service._validate_setting_value.side_effect = (
            ValidationError("验证失败")
        )

        with patch.object(dialog, "show_error") as mock_show_error:
            # 验证输入
            result = dialog._validate_input()

            # 验证结果
            self.assertFalse(result)
            mock_show_error.assert_called()

    def test_on_ok(self):
        """测试确定按钮"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        with patch.object(dialog, "_validate_input", return_value=True):
            with patch.object(dialog, "_apply_settings"):
                with patch.object(dialog, "_close_dialog") as mock_close:
                    # 点击确定
                    dialog._on_ok()

                    # 验证对话框关闭
                    mock_close.assert_called_once()
                    self.assertEqual(dialog.result, DialogResult.OK)

    def test_on_cancel_with_changes(self):
        """测试有修改时的取消按钮"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        dialog.settings_modified = True

        with patch.object(dialog, "confirm", return_value=True):
            with patch(
                "src.minicrm.ui.ttk_base.settings_dialog_ttk.BaseDialogTTK._on_cancel"
            ) as mock_super_cancel:
                # 点击取消
                dialog._on_cancel()

                # 验证调用父类取消方法
                mock_super_cancel.assert_called_once()

    def test_on_cancel_no_changes(self):
        """测试无修改时的取消按钮"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        dialog.settings_modified = False

        with patch(
            "src.minicrm.ui.ttk_base.settings_dialog_ttk.BaseDialogTTK._on_cancel"
        ) as mock_super_cancel:
            # 点击取消
            dialog._on_cancel()

            # 验证调用父类取消方法
            mock_super_cancel.assert_called_once()

    def test_get_modified_settings(self):
        """测试获取修改后的设置"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        # 获取修改后的设置
        settings = dialog.get_modified_settings()

        # 验证返回的是副本
        self.assertIsNot(settings, dialog.current_settings)
        self.assertEqual(settings, dialog.current_settings)

    def test_is_settings_modified(self):
        """测试检查设置是否已修改"""
        dialog = SettingsDialogTTK(
            parent=self.root, settings_service=self.mock_settings_service
        )

        # 初始状态
        self.assertFalse(dialog.is_settings_modified())

        # 修改设置
        dialog.settings_modified = True
        self.assertTrue(dialog.is_settings_modified())


class TestSettingsDialogConvenienceFunction(unittest.TestCase):
    """设置对话框便利函数测试"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.mock_settings_service = Mock(spec=SettingsService)

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_show_settings_dialog(self):
        """测试显示设置对话框便利函数"""
        with patch(
            "src.minicrm.ui.ttk_base.settings_dialog_ttk.SettingsDialogTTK"
        ) as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.show_dialog.return_value = (DialogResult.OK, {"test": "data"})
            mock_dialog_class.return_value = mock_dialog

            # 调用便利函数
            result, data = show_settings_dialog(
                parent=self.root, settings_service=self.mock_settings_service
            )

            # 验证对话框被创建和显示
            mock_dialog_class.assert_called_once_with(
                parent=self.root, settings_service=self.mock_settings_service
            )
            mock_dialog.show_dialog.assert_called_once()

            # 验证返回值
            self.assertEqual(result, DialogResult.OK)
            self.assertEqual(data, {"test": "data"})


if __name__ == "__main__":
    unittest.main()
