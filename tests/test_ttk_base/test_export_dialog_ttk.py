"""TTK导出对话框测试

测试ExportDialogTTK类的功能，包括：
- 对话框创建和初始化
- 数据类型选择
- 筛选条件设置
- 字段选择
- 导出配置收集
- 导出执行

作者: MiniCRM开发团队
"""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from src.minicrm.services.import_export_service import ImportExportService
from src.minicrm.ui.ttk_base.base_dialog import DialogResult
from src.minicrm.ui.ttk_base.export_dialog_ttk import (
    ExportDialogTTK,
    show_export_dialog,
)


class TestExportDialogTTK(unittest.TestCase):
    """ExportDialogTTK测试类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        # 创建模拟的导入导出服务
        self.mock_import_export_service = Mock(spec=ImportExportService)
        self.mock_import_export_service.export_data.return_value = "/test/export.xlsx"

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_dialog_creation(self):
        """测试对话框创建"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 验证对话框属性
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.title(), "数据导出")
        self.assertIsNotNone(dialog.notebook)
        self.assertEqual(len(dialog.notebook.tabs()), 4)  # 4个标签页

    def test_dialog_creation_without_service(self):
        """测试没有服务时的对话框创建"""
        with patch.object(ExportDialogTTK, "show_error") as mock_show_error:
            with patch.object(ExportDialogTTK, "_on_cancel") as mock_cancel:
                dialog = ExportDialogTTK(parent=self.root, import_export_service=None)

                # 验证显示错误并取消
                mock_show_error.assert_called_once_with("导入导出服务不可用", "错误")
                mock_cancel.assert_called_once()

    def test_data_types_initialization(self):
        """测试数据类型初始化"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 验证数据类型定义
        expected_types = [
            "customers",
            "suppliers",
            "quotes",
            "contracts",
            "interactions",
            "tasks",
        ]
        for data_type in expected_types:
            self.assertIn(data_type, dialog.data_types)

    def test_export_formats_initialization(self):
        """测试导出格式初始化"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 验证导出格式定义
        expected_formats = ["excel", "csv", "pdf"]
        for format_type in expected_formats:
            self.assertIn(format_type, dialog.export_formats)

    def test_field_definitions_initialization(self):
        """测试字段定义初始化"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 验证字段定义
        self.assertIn("customers", dialog.field_definitions)
        self.assertIn("suppliers", dialog.field_definitions)

        # 验证客户字段
        customer_fields = dialog.field_definitions["customers"]
        field_ids = [field[0] for field in customer_fields]
        self.assertIn("id", field_ids)
        self.assertIn("name", field_ids)
        self.assertIn("phone", field_ids)

    def test_data_type_selection(self):
        """测试数据类型选择"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 默认选择
        self.assertEqual(dialog.data_type_var.get(), "customers")

        # 修改选择
        dialog.data_type_var.set("suppliers")
        self.assertEqual(dialog.data_type_var.get(), "suppliers")

    def test_data_type_changed_handler(self):
        """测试数据类型变化处理"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        with patch.object(dialog, "_load_data_statistics") as mock_load_stats:
            with patch.object(dialog, "_update_field_selection") as mock_update_fields:
                # 触发数据类型变化
                dialog._on_data_type_changed()

                # 验证处理函数被调用
                mock_load_stats.assert_called_once()
                mock_update_fields.assert_called_once()

    def test_load_data_statistics(self):
        """测试加载数据统计"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 加载统计信息
        dialog._load_data_statistics()

        # 验证统计标签被更新
        self.assertIsNotNone(dialog.stats_label.cget("text"))
        self.assertNotEqual(dialog.stats_label.cget("text"), "")

    def test_field_selection_update(self):
        """测试字段选择更新"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 更新字段选择
        dialog._update_field_selection()

        # 验证字段变量被创建
        self.assertIsInstance(dialog.field_vars, dict)
        self.assertTrue(len(dialog.field_vars) > 0)

    def test_select_all_fields(self):
        """测试全选字段"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 全选字段
        dialog._select_all_fields()

        # 验证所有字段被选中
        for var in dialog.field_vars.values():
            self.assertTrue(var.get())

    def test_deselect_all_fields(self):
        """测试取消全选字段"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 先全选
        dialog._select_all_fields()

        # 取消全选
        dialog._deselect_all_fields()

        # 验证必选字段仍被选中，可选字段被取消
        data_type = dialog.data_type_var.get()
        fields = dialog.field_definitions.get(data_type, [])

        for field_key, _, is_required in fields:
            if field_key in dialog.field_vars:
                expected = is_required
                actual = dialog.field_vars[field_key].get()
                self.assertEqual(actual, expected)

    def test_reset_field_selection(self):
        """测试重置字段选择"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 修改字段选择
        dialog._select_all_fields()

        # 重置字段选择
        dialog._reset_field_selection()

        # 验证字段选择被重置为默认值
        data_type = dialog.data_type_var.get()
        fields = dialog.field_definitions.get(data_type, [])

        for field_key, _, is_required in fields:
            if field_key in dialog.field_vars:
                expected = is_required
                actual = dialog.field_vars[field_key].get()
                self.assertEqual(actual, expected)

    def test_date_filter_toggle(self):
        """测试日期筛选切换"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 初始状态：日期筛选禁用
        self.assertFalse(dialog.use_date_filter_var.get())

        # 启用日期筛选
        dialog.use_date_filter_var.set(True)
        dialog._toggle_date_filter()

        # 验证日期输入框被启用
        # 这里只验证函数执行没有错误
        self.assertTrue(True)

    def test_browse_save_path(self):
        """测试浏览保存路径"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        with patch(
            "src.minicrm.ui.ttk_base.export_dialog_ttk.save_file_dialog",
            return_value="/test/export.xlsx",
        ):
            # 浏览保存路径
            dialog._browse_save_path()

            # 验证路径被设置
            self.assertEqual(dialog.save_path_var.get(), "/test/export.xlsx")

    def test_browse_save_path_cancelled(self):
        """测试取消浏览保存路径"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        original_path = dialog.save_path_var.get()

        with patch(
            "src.minicrm.ui.ttk_base.export_dialog_ttk.save_file_dialog",
            return_value=None,
        ):
            # 取消浏览
            dialog._browse_save_path()

            # 验证路径未改变
            self.assertEqual(dialog.save_path_var.get(), original_path)

    def test_collect_export_config(self):
        """测试收集导出配置"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 设置一些配置
        dialog.data_type_var.set("customers")
        dialog.format_var.set("excel")
        dialog.include_headers_var.set(True)
        dialog.use_date_filter_var.set(True)
        dialog.start_date_var.set("2024-01-01")
        dialog.end_date_var.set("2024-12-31")

        # 选择一些字段
        dialog._update_field_selection()
        for var in list(dialog.field_vars.values())[:2]:  # 选择前两个字段
            var.set(True)

        # 收集配置
        config = dialog._collect_export_config()

        # 验证配置
        self.assertEqual(config["data_type"], "customers")
        self.assertEqual(config["format"], "excel")
        self.assertTrue(config["include_headers"])
        self.assertIn("date_range", config["filters"])
        self.assertTrue(len(config["fields"]) >= 2)

    def test_validate_export_config_valid(self):
        """测试验证有效的导出配置"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 创建有效配置
        config = {
            "fields": ["id", "name"],
            "file_path": "/test/export.xlsx",
            "filters": {},
        }

        # 验证配置
        result = dialog._validate_export_config(config)
        self.assertTrue(result)

    def test_validate_export_config_no_fields(self):
        """测试验证无字段的导出配置"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 创建无字段配置
        config = {"fields": [], "file_path": "/test/export.xlsx", "filters": {}}

        with patch.object(dialog, "show_error") as mock_show_error:
            # 验证配置
            result = dialog._validate_export_config(config)

            # 验证结果和错误消息
            self.assertFalse(result)
            mock_show_error.assert_called_with("请至少选择一个要导出的字段")

    def test_validate_export_config_no_file_path(self):
        """测试验证无文件路径的导出配置"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 创建无文件路径配置
        config = {"fields": ["id", "name"], "file_path": "", "filters": {}}

        with patch.object(dialog, "show_error") as mock_show_error:
            # 验证配置
            result = dialog._validate_export_config(config)

            # 验证结果和错误消息
            self.assertFalse(result)
            mock_show_error.assert_called_with("请指定保存文件路径")

    def test_validate_export_config_invalid_date(self):
        """测试验证无效日期的导出配置"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 创建无效日期配置
        config = {
            "fields": ["id", "name"],
            "file_path": "/test/export.xlsx",
            "filters": {"date_range": {"start": "invalid-date", "end": "2024-12-31"}},
        }

        with patch.object(dialog, "show_error") as mock_show_error:
            # 验证配置
            result = dialog._validate_export_config(config)

            # 验证结果和错误消息
            self.assertFalse(result)
            mock_show_error.assert_called_with("日期格式不正确，请使用 YYYY-MM-DD 格式")

    def test_start_export(self):
        """测试开始导出"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 设置有效配置
        dialog._update_field_selection()
        for var in list(dialog.field_vars.values())[:2]:
            var.set(True)
        dialog.save_path_var.set("/test/export.xlsx")

        with patch.object(dialog, "confirm", return_value=True):
            with patch.object(dialog, "_execute_export") as mock_execute:
                # 开始导出
                dialog._start_export()

                # 验证执行导出被调用
                mock_execute.assert_called_once()

    def test_start_export_cancelled(self):
        """测试取消开始导出"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 设置有效配置
        dialog._update_field_selection()
        for var in list(dialog.field_vars.values())[:2]:
            var.set(True)
        dialog.save_path_var.set("/test/export.xlsx")

        with patch.object(dialog, "confirm", return_value=False):
            with patch.object(dialog, "_execute_export") as mock_execute:
                # 取消导出
                dialog._start_export()

                # 验证执行导出未被调用
                mock_execute.assert_not_called()

    def test_execute_export(self):
        """测试执行导出"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        config = {
            "data_type": "customers",
            "format": "excel",
            "filters": {},
            "open_after_export": False,
        }

        with patch(
            "src.minicrm.ui.ttk_base.export_dialog_ttk.ProgressDialogTTK"
        ) as mock_progress_class:
            mock_progress = Mock()
            mock_progress_class.return_value = mock_progress

            # 执行导出
            dialog._execute_export(config)

            # 验证进度对话框被创建
            mock_progress_class.assert_called_once()

    def test_on_export_success(self):
        """测试导出成功处理"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        config = {"open_after_export": False}

        with patch.object(dialog, "show_info") as mock_show_info:
            with patch.object(dialog, "_close_dialog") as mock_close:
                # 导出成功
                dialog._on_export_success("/test/export.xlsx", config)

                # 验证成功消息和对话框关闭
                mock_show_info.assert_called()
                mock_close.assert_called_once()
                self.assertEqual(dialog.result, DialogResult.OK)

    def test_validate_input(self):
        """测试输入验证"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 设置有效配置
        dialog._update_field_selection()
        for var in list(dialog.field_vars.values())[:2]:
            var.set(True)
        dialog.save_path_var.set("/test/export.xlsx")

        # 验证输入
        result = dialog._validate_input()
        self.assertTrue(result)

    def test_get_export_config(self):
        """测试获取导出配置"""
        dialog = ExportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 获取配置
        config = dialog.get_export_config()

        # 验证配置结构
        self.assertIn("data_type", config)
        self.assertIn("format", config)
        self.assertIn("filters", config)
        self.assertIn("fields", config)


class TestExportDialogConvenienceFunction(unittest.TestCase):
    """导出对话框便利函数测试"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.mock_import_export_service = Mock(spec=ImportExportService)

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_show_export_dialog(self):
        """测试显示导出对话框便利函数"""
        with patch(
            "src.minicrm.ui.ttk_base.export_dialog_ttk.ExportDialogTTK"
        ) as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.show_dialog.return_value = (DialogResult.OK, {"test": "data"})
            mock_dialog_class.return_value = mock_dialog

            # 调用便利函数
            result, data = show_export_dialog(
                parent=self.root, import_export_service=self.mock_import_export_service
            )

            # 验证对话框被创建和显示
            mock_dialog_class.assert_called_once_with(
                parent=self.root, import_export_service=self.mock_import_export_service
            )
            mock_dialog.show_dialog.assert_called_once()

            # 验证返回值
            self.assertEqual(result, DialogResult.OK)
            self.assertEqual(data, {"test": "data"})


if __name__ == "__main__":
    unittest.main()
