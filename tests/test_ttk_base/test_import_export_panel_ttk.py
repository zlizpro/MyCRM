"""TTK导入导出面板测试

测试ImportExportPanelTTK类的功能，包括：
- 面板初始化和UI创建
- 导入功能集成
- 导出功能集成
- 文档生成功能
- 统计信息显示
- 错误处理和用户交互

作者: MiniCRM开发团队
"""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from src.minicrm.services.import_export_service import ImportExportService
from src.minicrm.ui.ttk_base.import_export_panel_ttk import (
    ImportExportPanelTTK,
    create_import_export_panel,
)


class TestImportExportPanelTTK(unittest.TestCase):
    """ImportExportPanelTTK测试类."""

    def setUp(self):
        """测试前准备."""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        # 创建模拟的导入导出服务
        self.mock_import_export_service = Mock(spec=ImportExportService)
        self.mock_import_export_service.get_supported_formats.return_value = {
            "import": [".csv", ".xlsx"],
            "export": [".csv", ".xlsx", ".pdf"],
        }

        # 创建面板实例
        self.panel = ImportExportPanelTTK(
            parent=self.root,
            import_export_service=self.mock_import_export_service,
        )

    def tearDown(self):
        """测试后清理."""
        if self.panel:
            self.panel.cleanup()
        self.root.destroy()

    def test_panel_initialization(self):
        """测试面板初始化."""
        # 验证面板创建成功
        self.assertIsNotNone(self.panel)
        self.assertEqual(
            self.panel.import_export_service, self.mock_import_export_service
        )

        # 验证UI组件创建
        self.assertIsNotNone(self.panel.notebook)
        self.assertEqual(self.panel.notebook.index("end"), 4)  # 4个标签页

        # 验证标签页标题
        tab_texts = []
        for i in range(self.panel.notebook.index("end")):
            tab_texts.append(self.panel.notebook.tab(i, "text"))

        expected_tabs = ["数据导入", "数据导出", "文档生成", "统计信息"]
        self.assertEqual(tab_texts, expected_tabs)

    def test_import_tab_creation(self):
        """测试导入标签页创建."""
        # 验证导入相关组件存在
        self.assertIsNotNone(self.panel.import_data_type_var)
        self.assertIsNotNone(self.panel.import_history_tree)

        # 验证默认数据类型
        self.assertEqual(self.panel.import_data_type_var.get(), "customers")

        # 验证导入历史表格列
        columns = self.panel.import_history_tree["columns"]
        expected_columns = ("time", "type", "file", "status", "count")
        self.assertEqual(columns, expected_columns)

    def test_export_tab_creation(self):
        """测试导出标签页创建."""
        # 验证导出相关组件存在
        self.assertIsNotNone(self.panel.export_data_type_var)
        self.assertIsNotNone(self.panel.export_format_var)
        self.assertIsNotNone(self.panel.export_history_tree)
        self.assertIsNotNone(self.panel.export_stats_label)

        # 验证默认值
        self.assertEqual(self.panel.export_data_type_var.get(), "customers")
        self.assertEqual(self.panel.export_format_var.get(), "excel")

        # 验证导出历史表格列
        columns = self.panel.export_history_tree["columns"]
        expected_columns = ("time", "type", "format", "file", "count")
        self.assertEqual(columns, expected_columns)

    def test_document_tab_creation(self):
        """测试文档生成标签页创建."""
        # 验证文档生成相关组件存在
        self.assertIsNotNone(self.panel.document_type_var)
        self.assertIsNotNone(self.panel.document_format_var)
        self.assertIsNotNone(self.panel.document_status_label)

        # 验证默认值
        self.assertEqual(self.panel.document_type_var.get(), "contract")
        self.assertEqual(self.panel.document_format_var.get(), "pdf")

    def test_statistics_tab_creation(self):
        """测试统计信息标签页创建."""
        # 验证统计相关组件存在
        self.assertIsNotNone(self.panel.stats_cards)
        self.assertIsNotNone(self.panel.history_tree)

        # 验证统计卡片
        expected_keys = ["customers", "suppliers", "contracts", "quotes"]
        for key in expected_keys:
            self.assertIn(key, self.panel.stats_cards)
            self.assertIn("count", self.panel.stats_cards[key])
            self.assertIn("time", self.panel.stats_cards[key])

    @patch("src.minicrm.ui.ttk_base.import_export_panel_ttk.ImportDialogTTK")
    def test_open_import_dialog(self, mock_dialog_class):
        """测试打开导入对话框."""
        # 设置模拟对话框
        mock_dialog = Mock()
        mock_dialog.show_dialog.return_value = ("ok", {"success_count": 10})
        mock_dialog_class.return_value = mock_dialog

        # 调用打开导入对话框
        self.panel._open_import_dialog()

        # 验证对话框创建和显示
        mock_dialog_class.assert_called_once_with(
            parent=self.panel,
            import_export_service=self.mock_import_export_service,
        )
        mock_dialog.show_dialog.assert_called_once()

    @patch("src.minicrm.ui.ttk_base.import_export_panel_ttk.ExportDialogTTK")
    def test_open_export_dialog(self, mock_dialog_class):
        """测试打开导出对话框."""
        # 设置模拟对话框
        mock_dialog = Mock()
        mock_dialog.show_dialog.return_value = (
            "ok",
            {"file_path": "/test/export.xlsx"},
        )
        mock_dialog_class.return_value = mock_dialog

        # 调用打开导出对话框
        self.panel._open_export_dialog()

        # 验证对话框创建和显示
        mock_dialog_class.assert_called_once_with(
            parent=self.panel,
            import_export_service=self.mock_import_export_service,
        )
        mock_dialog.show_dialog.assert_called_once()

    @patch("tkinter.filedialog.asksaveasfilename")
    def test_download_template(self, mock_filedialog):
        """测试下载模板功能."""
        # 设置文件对话框返回值
        mock_filedialog.return_value = "/test/template.xlsx"

        # 模拟生成模板文件方法
        with patch.object(self.panel, "_generate_template_file") as mock_generate:
            self.panel._download_template()

            # 验证文件对话框调用
            mock_filedialog.assert_called_once()

            # 验证模板生成调用
            mock_generate.assert_called_once_with("customers", "/test/template.xlsx")

    @patch("pandas.DataFrame")
    def test_generate_template_file_excel(self, mock_dataframe):
        """测试生成Excel模板文件."""
        # 设置模拟DataFrame
        mock_df = Mock()
        mock_dataframe.return_value = mock_df

        # 调用生成模板文件
        self.panel._generate_template_file("customers", "/test/template.xlsx")

        # 验证DataFrame创建和保存
        mock_dataframe.assert_called_once()
        mock_df.to_excel.assert_called_once_with("/test/template.xlsx", index=False)

    @patch("csv.writer")
    @patch("builtins.open", create=True)
    def test_generate_template_file_csv(self, mock_open, mock_csv_writer):
        """测试生成CSV模板文件."""
        # 设置模拟writer
        mock_writer = Mock()
        mock_csv_writer.return_value = mock_writer

        # 调用生成模板文件
        self.panel._generate_template_file("customers", "/test/template.csv")

        # 验证文件打开和写入
        mock_open.assert_called_once_with(
            "/test/template.csv", "w", newline="", encoding="utf-8-sig"
        )
        mock_writer.writerow.assert_called_once()

    @patch("tkinter.filedialog.asksaveasfilename")
    @patch("threading.Thread")
    def test_generate_document(self, mock_thread, mock_filedialog):
        """测试生成文档功能."""
        # 设置文件对话框返回值
        mock_filedialog.return_value = "/test/document.pdf"

        # 设置模拟线程
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        # 调用生成文档
        self.panel._generate_document()

        # 验证文件对话框调用
        mock_filedialog.assert_called_once()

        # 验证线程创建和启动
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    def test_update_export_statistics(self):
        """测试更新导出统计信息."""
        # 设置统计数据
        self.panel.statistics = {
            "customers": {"total": 1234, "last_updated": "2024-01-15 10:30"},
            "suppliers": {"total": 567, "last_updated": "2024-01-14 16:45"},
        }

        # 更新导出统计
        self.panel._update_export_statistics()

        # 验证统计标签更新
        expected_text = "1234 条记录可导出"
        self.assertEqual(self.panel.export_stats_label.cget("text"), expected_text)

    def test_load_import_history(self):
        """测试加载导入历史."""
        # 调用加载导入历史
        self.panel._load_import_history()

        # 验证历史记录加载
        children = self.panel.import_history_tree.get_children()
        self.assertGreater(len(children), 0)

        # 验证第一条记录的数据
        first_item = children[0]
        values = self.panel.import_history_tree.item(first_item, "values")
        self.assertEqual(len(values), 5)  # 5列数据

    def test_load_export_history(self):
        """测试加载导出历史."""
        # 调用加载导出历史
        self.panel._load_export_history()

        # 验证历史记录加载
        children = self.panel.export_history_tree.get_children()
        self.assertGreater(len(children), 0)

        # 验证第一条记录的数据
        first_item = children[0]
        values = self.panel.export_history_tree.item(first_item, "values")
        self.assertEqual(len(values), 5)  # 5列数据

    def test_load_operation_history(self):
        """测试加载操作历史."""
        # 调用加载操作历史
        self.panel._load_operation_history()

        # 验证历史记录加载
        children = self.panel.history_tree.get_children()
        self.assertGreater(len(children), 0)

        # 验证第一条记录的数据
        first_item = children[0]
        values = self.panel.history_tree.item(first_item, "values")
        self.assertEqual(len(values), 5)  # 5列数据

    def test_update_statistics_display(self):
        """测试更新统计信息显示."""
        # 设置统计数据
        self.panel.statistics = {
            "customers": {"total": 1234, "last_updated": "2024-01-15 10:30"},
            "suppliers": {"total": 567, "last_updated": "2024-01-14 16:45"},
        }

        # 更新统计显示
        self.panel._update_statistics_display()

        # 验证统计卡片更新
        customers_card = self.panel.stats_cards["customers"]
        self.assertEqual(customers_card["count"].cget("text"), "1234")
        self.assertEqual(customers_card["time"].cget("text"), "更新: 2024-01-15 10:30")

        suppliers_card = self.panel.stats_cards["suppliers"]
        self.assertEqual(suppliers_card["count"].cget("text"), "567")
        self.assertEqual(suppliers_card["time"].cget("text"), "更新: 2024-01-14 16:45")

    def test_refresh_statistics(self):
        """测试刷新统计信息."""
        # 模拟加载统计信息方法
        with (
            patch.object(self.panel, "_load_statistics") as mock_load_stats,
            patch.object(
                self.panel, "_update_statistics_display"
            ) as mock_update_display,
            patch.object(self.panel, "_update_export_statistics") as mock_update_export,
        ):
            # 调用刷新统计
            self.panel._refresh_statistics()

            # 验证方法调用
            mock_load_stats.assert_called_once()
            mock_update_display.assert_called_once()
            mock_update_export.assert_called_once()

    @patch("tkinter.messagebox.askyesno")
    def test_clear_history(self, mock_messagebox):
        """测试清理历史记录."""
        # 设置确认对话框返回True
        mock_messagebox.return_value = True

        # 先加载一些历史记录
        self.panel._load_import_history()
        self.panel._load_export_history()
        self.panel._load_operation_history()

        # 验证有历史记录
        self.assertGreater(len(self.panel.import_history_tree.get_children()), 0)
        self.assertGreater(len(self.panel.export_history_tree.get_children()), 0)
        self.assertGreater(len(self.panel.history_tree.get_children()), 0)

        # 调用清理历史
        self.panel._clear_history()

        # 验证确认对话框调用
        mock_messagebox.assert_called_once()

        # 验证历史记录被清空
        self.assertEqual(len(self.panel.import_history_tree.get_children()), 0)
        self.assertEqual(len(self.panel.export_history_tree.get_children()), 0)
        self.assertEqual(len(self.panel.history_tree.get_children()), 0)

    def test_get_current_statistics(self):
        """测试获取当前统计信息."""
        # 设置统计数据
        test_stats = {
            "customers": {"total": 1234, "last_updated": "2024-01-15 10:30"},
            "suppliers": {"total": 567, "last_updated": "2024-01-14 16:45"},
        }
        self.panel.statistics = test_stats

        # 获取统计信息
        result = self.panel.get_current_statistics()

        # 验证返回的统计信息
        self.assertEqual(result, test_stats)
        self.assertIsNot(result, test_stats)  # 应该是副本，不是原对象

    def test_refresh_data(self):
        """测试刷新面板数据."""
        # 模拟各个加载方法
        with (
            patch.object(self.panel, "_load_statistics") as mock_load_stats,
            patch.object(self.panel, "_load_import_history") as mock_load_import,
            patch.object(self.panel, "_load_export_history") as mock_load_export,
            patch.object(self.panel, "_load_operation_history") as mock_load_operation,
            patch.object(
                self.panel, "_update_statistics_display"
            ) as mock_update_display,
            patch.object(self.panel, "_update_export_statistics") as mock_update_export,
        ):
            # 调用刷新数据
            self.panel.refresh_data()

            # 验证所有方法都被调用
            mock_load_stats.assert_called_once()
            mock_load_import.assert_called_once()
            mock_load_export.assert_called_once()
            mock_load_operation.assert_called_once()
            mock_update_display.assert_called_once()
            mock_update_export.assert_called_once()

    def test_cleanup(self):
        """测试资源清理."""
        # 设置一些需要清理的资源
        self.panel.progress_dialog = Mock()
        self.panel.operation_thread = Mock()
        self.panel.operation_thread.is_alive.return_value = False

        # 调用清理
        self.panel.cleanup()

        # 验证进度对话框被关闭
        self.panel.progress_dialog.close_dialog.assert_called_once()
        self.assertIsNone(self.panel.progress_dialog)

    def test_error_handling_no_service(self):
        """测试没有服务时的错误处理."""
        # 创建没有服务的面板
        panel_no_service = ImportExportPanelTTK(parent=self.root)

        # 模拟错误显示方法
        with patch.object(panel_no_service, "_show_error") as mock_show_error:
            # 尝试打开导入对话框
            panel_no_service._open_import_dialog()

            # 验证错误消息显示
            mock_show_error.assert_called_once_with("导入导出服务不可用")

        panel_no_service.cleanup()

    @patch("tkinter.messagebox.showinfo")
    def test_show_success(self, mock_messagebox):
        """测试显示成功消息."""
        message = "操作成功"
        self.panel._show_success(message)
        mock_messagebox.assert_called_once_with("成功", message)

    @patch("tkinter.messagebox.showerror")
    def test_show_error(self, mock_messagebox):
        """测试显示错误消息."""
        message = "操作失败"
        self.panel._show_error(message)
        mock_messagebox.assert_called_once_with("错误", message)

    @patch("tkinter.messagebox.showinfo")
    def test_show_info(self, mock_messagebox):
        """测试显示信息消息."""
        message = "信息内容"
        self.panel._show_info(message)
        mock_messagebox.assert_called_once_with("信息", message)


class TestImportExportPanelTTKIntegration(unittest.TestCase):
    """ImportExportPanelTTK集成测试类."""

    def setUp(self):
        """测试前准备."""
        self.root = tk.Tk()
        self.root.withdraw()

        # 创建真实的服务实例（用于集成测试）
        self.mock_service = Mock(spec=ImportExportService)

    def tearDown(self):
        """测试后清理."""
        self.root.destroy()

    def test_create_import_export_panel_function(self):
        """测试便利函数创建面板."""
        panel = create_import_export_panel(
            parent=self.root,
            import_export_service=self.mock_service,
        )

        # 验证面板创建成功
        self.assertIsInstance(panel, ImportExportPanelTTK)
        self.assertEqual(panel.import_export_service, self.mock_service)

        panel.cleanup()

    def test_panel_with_real_service_interface(self):
        """测试面板与真实服务接口的集成."""
        # 设置服务方法返回值
        self.mock_service.get_supported_formats.return_value = {
            "import": [".csv", ".xlsx"],
            "export": [".csv", ".xlsx", ".pdf"],
        }

        panel = ImportExportPanelTTK(
            parent=self.root,
            import_export_service=self.mock_service,
        )

        # 验证面板正常初始化
        self.assertIsNotNone(panel.notebook)
        self.assertEqual(panel.notebook.index("end"), 4)

        panel.cleanup()

    def test_panel_tab_switching(self):
        """测试标签页切换功能."""
        panel = ImportExportPanelTTK(
            parent=self.root,
            import_export_service=self.mock_service,
        )

        # 测试切换到不同标签页
        for i in range(panel.notebook.index("end")):
            panel.notebook.select(i)
            current_tab = panel.notebook.select()
            self.assertIsNotNone(current_tab)

        panel.cleanup()

    def test_panel_data_type_selection(self):
        """测试数据类型选择功能."""
        panel = ImportExportPanelTTK(
            parent=self.root,
            import_export_service=self.mock_service,
        )

        # 测试导入数据类型选择
        original_value = panel.import_data_type_var.get()
        panel.import_data_type_var.set("suppliers")
        self.assertEqual(panel.import_data_type_var.get(), "suppliers")

        # 测试导出数据类型选择
        panel.export_data_type_var.set("contracts")
        self.assertEqual(panel.export_data_type_var.get(), "contracts")

        panel.cleanup()


if __name__ == "__main__":
    unittest.main()
