"""TTK导入对话框测试

测试ImportDialogTTK类的功能，包括：
- 对话框创建和初始化
- 向导步骤导航
- 文件选择和预览
- 数据类型选择
- 字段映射配置
- 导入选项设置
- 导入执行

作者: MiniCRM开发团队
"""

import tkinter as tk
import unittest
from unittest.mock import Mock, mock_open, patch

from src.minicrm.services.import_export_service import ImportExportService
from src.minicrm.ui.ttk_base.base_dialog import DialogResult
from src.minicrm.ui.ttk_base.import_dialog_ttk import (
    ImportDialogTTK,
    show_import_dialog,
)


class TestImportDialogTTK(unittest.TestCase):
    """ImportDialogTTK测试类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        # 创建模拟的导入导出服务
        self.mock_import_export_service = Mock(spec=ImportExportService)
        self.mock_import_export_service.import_data.return_value = {
            "success_count": 10,
            "error_count": 2,
            "errors": ["错误1", "错误2"],
        }

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_dialog_creation(self):
        """测试对话框创建"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 验证对话框属性
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog.title(), "数据导入向导")
        self.assertEqual(dialog.total_steps, 5)
        self.assertEqual(dialog.current_step, 0)

    def test_dialog_creation_without_service(self):
        """测试没有服务时的对话框创建"""
        with patch.object(ImportDialogTTK, "show_error") as mock_show_error:
            with patch.object(ImportDialogTTK, "_on_cancel") as mock_cancel:
                dialog = ImportDialogTTK(parent=self.root, import_export_service=None)

                # 验证显示错误并取消
                mock_show_error.assert_called_once_with("导入导出服务不可用", "错误")
                mock_cancel.assert_called_once()

    def test_wizard_steps_initialization(self):
        """测试向导步骤初始化"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 验证步骤名称
        expected_steps = ["文件选择", "数据类型", "字段映射", "导入选项", "执行导入"]
        self.assertEqual(dialog.step_names, expected_steps)

        # 验证步骤框架
        self.assertEqual(len(dialog.step_frames), 5)

    def test_data_types_initialization(self):
        """测试数据类型初始化"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 验证数据类型定义
        expected_types = ["customers", "suppliers"]
        for data_type in expected_types:
            self.assertIn(data_type, dialog.data_types)

    def test_target_fields_initialization(self):
        """测试目标字段初始化"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 验证目标字段定义
        self.assertIn("customers", dialog.target_fields)
        self.assertIn("suppliers", dialog.target_fields)

        # 验证客户字段
        customer_fields = dialog.target_fields["customers"]
        self.assertIn("name", customer_fields)
        self.assertIn("phone", customer_fields)
        self.assertTrue(customer_fields["name"]["required"])
        self.assertTrue(customer_fields["phone"]["required"])

    def test_show_step(self):
        """测试显示步骤"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 显示第二步
        dialog._show_step(1)

        # 验证当前步骤
        self.assertEqual(dialog.current_step, 1)

    def test_update_buttons(self):
        """测试更新按钮状态"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 第一步：上一步按钮应该禁用
        dialog._update_buttons()
        self.assertEqual(dialog.prev_button.cget("state"), "disabled")

        # 移动到第二步
        dialog._show_step(1)
        self.assertEqual(dialog.prev_button.cget("state"), "normal")

    def test_update_step_label(self):
        """测试更新步骤标签"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 验证初始标签
        expected_text = "步骤 1/5: 文件选择"
        self.assertEqual(dialog.step_label.cget("text"), expected_text)

        # 移动到第二步
        dialog._show_step(1)
        expected_text = "步骤 2/5: 数据类型"
        self.assertEqual(dialog.step_label.cget("text"), expected_text)

    def test_can_proceed_file_selection(self):
        """测试文件选择步骤是否可以继续"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 初始状态：无文件，不能继续
        self.assertFalse(dialog._can_proceed())

        # 设置文件路径和数据
        dialog.file_path_var.set("/test/file.csv")
        dialog.file_data = [{"name": "test"}]

        # 现在可以继续
        self.assertTrue(dialog._can_proceed())

    def test_can_proceed_data_type(self):
        """测试数据类型步骤是否可以继续"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 移动到数据类型步骤
        dialog._show_step(1)

        # 默认有选择，可以继续
        self.assertTrue(dialog._can_proceed())

    def test_can_proceed_field_mapping(self):
        """测试字段映射步骤是否可以继续"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 移动到字段映射步骤
        dialog._show_step(2)

        with patch.object(dialog, "_validate_field_mapping", return_value=True):
            # 映射有效，可以继续
            self.assertTrue(dialog._can_proceed())

    def test_next_step(self):
        """测试下一步"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 设置可以继续的条件
        dialog.file_path_var.set("/test/file.csv")
        dialog.file_data = [{"name": "test"}]

        # 下一步
        dialog._next_step()

        # 验证步骤增加
        self.assertEqual(dialog.current_step, 1)

    def test_prev_step(self):
        """测试上一步"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 移动到第二步
        dialog._show_step(1)

        # 上一步
        dialog._prev_step()

        # 验证步骤减少
        self.assertEqual(dialog.current_step, 0)

    def test_browse_file(self):
        """测试浏览文件"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        with patch(
            "src.minicrm.ui.ttk_base.import_dialog_ttk.open_file_dialog",
            return_value="/test/file.csv",
        ):
            with patch.object(dialog, "_load_file_preview") as mock_load_preview:
                # 浏览文件
                dialog._browse_file()

                # 验证文件路径被设置
                self.assertEqual(dialog.file_path_var.get(), "/test/file.csv")

                # 验证预览被加载
                mock_load_preview.assert_called_once()

    def test_browse_file_cancelled(self):
        """测试取消浏览文件"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        original_path = dialog.file_path_var.get()

        with patch(
            "src.minicrm.ui.ttk_base.import_dialog_ttk.open_file_dialog",
            return_value=None,
        ):
            with patch.object(dialog, "_load_file_preview") as mock_load_preview:
                # 取消浏览
                dialog._browse_file()

                # 验证文件路径未改变
                self.assertEqual(dialog.file_path_var.get(), original_path)

                # 验证预览未被加载
                mock_load_preview.assert_not_called()

    def test_load_csv_preview(self):
        """测试加载CSV文件预览"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 模拟CSV文件内容
        csv_content = (
            "name,phone,email\nJohn,123456,john@test.com\nJane,789012,jane@test.com"
        )

        with patch("builtins.open", mock_open(read_data=csv_content)):
            # 加载CSV预览
            dialog._load_csv_preview("/test/file.csv")

            # 验证文件头被设置
            self.assertEqual(dialog.file_headers, ["name", "phone", "email"])

            # 验证数据被加载
            self.assertEqual(len(dialog.file_data), 2)
            self.assertEqual(dialog.file_data[0]["name"], "John")

    def test_load_excel_preview(self):
        """测试加载Excel文件预览"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 模拟pandas DataFrame
        mock_df = Mock()
        mock_df.columns = ["name", "phone", "email"]
        mock_df.iterrows.return_value = [
            (0, {"name": "John", "phone": "123456", "email": "john@test.com"}),
            (1, {"name": "Jane", "phone": "789012", "email": "jane@test.com"}),
        ]
        mock_df.to_dict.return_value = [
            {"name": "John", "phone": "123456", "email": "john@test.com"},
            {"name": "Jane", "phone": "789012", "email": "jane@test.com"},
        ]

        with patch("pandas.read_excel", return_value=mock_df):
            with patch("pandas.notna", return_value=True):
                # 加载Excel预览
                dialog._load_excel_preview("/test/file.xlsx")

                # 验证文件头被设置
                self.assertEqual(dialog.file_headers, ["name", "phone", "email"])

                # 验证数据被加载
                self.assertEqual(len(dialog.file_data), 2)

    def test_load_excel_preview_no_pandas(self):
        """测试没有pandas时加载Excel文件"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        with patch(
            "pandas.read_excel", side_effect=ImportError("No module named 'pandas'")
        ):
            with patch.object(dialog, "show_error") as mock_show_error:
                # 尝试加载Excel
                dialog._load_excel_preview("/test/file.xlsx")

                # 验证错误消息
                mock_show_error.assert_called_with("需要安装pandas库来处理Excel文件")

    def test_on_data_type_changed(self):
        """测试数据类型变化处理"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        with patch.object(dialog, "_update_data_type_info") as mock_update_info:
            with patch.object(
                dialog, "_update_field_mapping_display"
            ) as mock_update_mapping:
                # 触发数据类型变化
                dialog._on_data_type_changed()

                # 验证处理函数被调用
                mock_update_info.assert_called_once()
                mock_update_mapping.assert_called_once()

    def test_update_data_type_info(self):
        """测试更新数据类型信息"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 更新数据类型信息
        dialog._update_data_type_info()

        # 验证信息文本被更新
        text_content = dialog.type_info_text.get("1.0", tk.END)
        self.assertIn("客户数据", text_content)
        self.assertIn("必填字段", text_content)

    def test_update_field_mapping_display(self):
        """测试更新字段映射显示"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 更新字段映射显示
        dialog._update_field_mapping_display()

        # 验证映射表格有内容
        children = dialog.mapping_tree.get_children()
        self.assertTrue(len(children) > 0)

    def test_auto_map_fields(self):
        """测试自动映射字段"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 设置文件头
        dialog.file_headers = ["name", "phone", "email", "address"]

        with patch.object(dialog, "show_info") as mock_show_info:
            with patch.object(
                dialog, "_update_field_mapping_display"
            ) as mock_update_display:
                # 自动映射
                dialog._auto_map_fields()

                # 验证映射被创建
                self.assertIn("name", dialog.import_config["field_mapping"])
                self.assertIn("phone", dialog.import_config["field_mapping"])

                # 验证显示被更新
                mock_update_display.assert_called_once()
                mock_show_info.assert_called_with("自动映射完成")

    def test_auto_map_fields_no_headers(self):
        """测试没有文件头时的自动映射"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 清空文件头
        dialog.file_headers = []

        with patch.object(dialog, "show_warning") as mock_show_warning:
            # 自动映射
            dialog._auto_map_fields()

            # 验证警告消息
            mock_show_warning.assert_called_with("请先选择文件")

    def test_clear_field_mapping(self):
        """测试清除字段映射"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 设置一些映射
        dialog.import_config["field_mapping"] = {"name": "客户名称", "phone": "电话"}

        with patch.object(
            dialog, "_update_field_mapping_display"
        ) as mock_update_display:
            # 清除映射
            dialog._clear_field_mapping()

            # 验证映射被清除
            self.assertEqual(len(dialog.import_config["field_mapping"]), 0)

            # 验证显示被更新
            mock_update_display.assert_called_once()

    def test_validate_field_mapping_valid(self):
        """测试验证有效的字段映射"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 设置有效映射（包含所有必填字段）
        dialog.import_config["field_mapping"] = {"name": "客户名称", "phone": "电话"}

        # 验证映射
        result = dialog._validate_field_mapping()
        self.assertTrue(result)

    def test_validate_field_mapping_invalid(self):
        """测试验证无效的字段映射"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 设置无效映射（缺少必填字段）
        dialog.import_config["field_mapping"] = {
            "name": "客户名称"
            # 缺少phone字段
        }

        # 验证映射
        result = dialog._validate_field_mapping()
        self.assertFalse(result)

    def test_update_import_summary(self):
        """测试更新导入摘要"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 设置一些配置
        dialog.file_path_var.set("/test/file.csv")
        dialog.file_data = [{"name": "test1"}, {"name": "test2"}]
        dialog.import_config["field_mapping"] = {"name": "客户名称"}

        # 更新摘要
        dialog._update_import_summary()

        # 验证摘要文本被更新
        text_content = dialog.summary_text.get("1.0", tk.END)
        self.assertIn("file.csv", text_content)
        self.assertIn("总记录数: 2", text_content)

    def test_start_import(self):
        """测试开始导入"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 设置导入配置
        dialog.file_path_var.set("/test/file.csv")
        dialog.file_data = [{"name": "test"}]
        dialog.import_config["field_mapping"] = {"name": "客户名称"}

        with patch.object(dialog, "confirm", return_value=True):
            with patch.object(dialog, "_execute_import") as mock_execute:
                # 开始导入
                dialog._start_import()

                # 验证执行导入被调用
                mock_execute.assert_called_once()

    def test_start_import_cancelled(self):
        """测试取消开始导入"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        with patch.object(dialog, "confirm", return_value=False):
            with patch.object(dialog, "_execute_import") as mock_execute:
                # 取消导入
                dialog._start_import()

                # 验证执行导入未被调用
                mock_execute.assert_not_called()

    def test_execute_import(self):
        """测试执行导入"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        config = {
            "file_path": "/test/file.csv",
            "data_type": "customers",
            "field_mapping": {"name": "客户名称"},
            "options": {},
        }

        # 执行导入
        dialog._execute_import(config)

        # 验证按钮状态被更新
        self.assertEqual(dialog.next_button.cget("state"), "disabled")
        self.assertEqual(dialog.prev_button.cget("state"), "disabled")

    def test_show_import_result(self):
        """测试显示导入结果"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        result = {"success_count": 10, "error_count": 2, "errors": ["错误1", "错误2"]}

        # 显示结果
        dialog._show_import_result(result)

        # 验证结果文本被更新
        text_content = dialog.result_text.get("1.0", tk.END)
        self.assertIn("成功导入: 10 条记录", text_content)
        self.assertIn("失败记录: 2 条", text_content)

        # 验证按钮状态
        self.assertEqual(dialog.next_button.cget("text"), "完成")
        self.assertEqual(dialog.next_button.cget("state"), "normal")

    def test_show_import_error(self):
        """测试显示导入错误"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        error_message = "导入失败：文件格式错误"

        # 显示错误
        dialog._show_import_error(error_message)

        # 验证错误文本被更新
        text_content = dialog.result_text.get("1.0", tk.END)
        self.assertIn("导入失败！", text_content)
        self.assertIn(error_message, text_content)

        # 验证按钮状态
        self.assertEqual(dialog.prev_button.cget("state"), "normal")
        self.assertEqual(dialog.next_button.cget("text"), "重试")

    def test_on_import_complete(self):
        """测试导入完成处理"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        with patch.object(dialog, "_close_dialog") as mock_close:
            # 导入完成
            dialog._on_import_complete()

            # 验证对话框关闭
            mock_close.assert_called_once()
            self.assertEqual(dialog.result, DialogResult.OK)

    def test_validate_input(self):
        """测试输入验证"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        with patch.object(dialog, "_can_proceed", return_value=True):
            # 验证输入
            result = dialog._validate_input()
            self.assertTrue(result)

    def test_get_import_config(self):
        """测试获取导入配置"""
        dialog = ImportDialogTTK(
            parent=self.root, import_export_service=self.mock_import_export_service
        )

        # 获取配置
        config = dialog.get_import_config()

        # 验证配置结构
        self.assertIn("file_path", config)
        self.assertIn("data_type", config)
        self.assertIn("field_mapping", config)
        self.assertIn("options", config)


class TestImportDialogConvenienceFunction(unittest.TestCase):
    """导入对话框便利函数测试"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.mock_import_export_service = Mock(spec=ImportExportService)

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_show_import_dialog(self):
        """测试显示导入对话框便利函数"""
        with patch(
            "src.minicrm.ui.ttk_base.import_dialog_ttk.ImportDialogTTK"
        ) as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.show_dialog.return_value = (DialogResult.OK, {"test": "data"})
            mock_dialog_class.return_value = mock_dialog

            # 调用便利函数
            result, data = show_import_dialog(
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
