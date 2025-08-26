"""MiniCRM TTK报价模板管理组件测试

测试TTK报价模板管理组件的功能，包括：
- 组件初始化和UI创建
- 模板列表加载和显示
- 模板CRUD操作
- 模板选择和应用
- 事件处理

遵循MiniCRM开发标准和测试规范。
"""

import tkinter as tk
import unittest
from unittest.mock import Mock

from src.minicrm.services.quote_template_service import QuoteTemplateService
from src.minicrm.ui.ttk_base.quote_template_ttk import (
    QuoteTemplateTTK,
)


class TestQuoteTemplateTTK(unittest.TestCase):
    """TTK报价模板管理组件测试类"""

    def setUp(self):
        """测试准备"""
        # 创建测试窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        # 创建模拟服务
        self.mock_template_service = Mock(spec=QuoteTemplateService)

        # 模拟模板数据
        self.mock_templates = [
            {
                "id": "standard",
                "name": "标准模板",
                "description": "标准报价模板",
                "version": "1.0",
                "is_default": True,
                "is_system": True,
                "created_at": "2024-01-01T00:00:00",
            },
            {
                "id": "custom1",
                "name": "自定义模板1",
                "description": "自定义报价模板",
                "version": "1.0",
                "is_default": False,
                "is_system": False,
                "created_at": "2024-01-02T00:00:00",
            },
        ]

        self.mock_template_service.get_all_templates.return_value = self.mock_templates

        # 创建测试组件
        self.template_widget = QuoteTemplateTTK(self.root, self.mock_template_service)

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "template_widget"):
            self.template_widget.cleanup()
        if hasattr(self, "root"):
            self.root.destroy()

    def test_initialization(self):
        """测试组件初始化"""
        # 验证基本属性
        self.assertIsNotNone(self.template_widget._template_service)

        # 验证数据加载
        self.mock_template_service.get_all_templates.assert_called_once()
        self.assertEqual(len(self.template_widget._templates), 2)

        # 验证UI组件创建
        self.assertIsNotNone(self.template_widget._template_tree)
        self.assertIsNotNone(self.template_widget._detail_frame)
        self.assertIsNotNone(self.template_widget._preview_frame)

    def test_load_templates_success(self):
        """测试成功加载模板"""
        # 验证模板加载
        self.assertEqual(len(self.template_widget._templates), 2)
        self.assertEqual(self.template_widget._templates[0]["name"], "标准模板")
        self.assertEqual(self.template_widget._templates[1]["name"], "自定义模板1")

    def test_load_templates_service_error(self):
        """测试模板加载服务错误"""
        # 创建新的组件，模拟服务错误
        mock_service = Mock(spec=QuoteTemplateService)
        mock_service.get_all_templates.side_effect = ServiceError("加载失败")

        with patch("tkinter.messagebox.showerror") as mock_error:
            widget = QuoteTemplateTTK(self.root, mock_service)

            # 验证错误处理
            mock_error.assert_called_once()
            self.assertEqual(len(widget._templates), 0)
            widget.cleanup()

    def test_template_selection(self):
        """测试模板选择"""
        # 模拟选择第一个模板
        tree = self.template_widget._template_tree
        items = tree.get_children()

        if items:
            # 选择第一个项目
            tree.selection_set(items[0])
            self.template_widget._on_template_selected()

            # 验证选择结果
            self.assertIsNotNone(self.template_widget._selected_template)
            self.assertEqual(
                self.template_widget._selected_template["name"], "标准模板"
            )

    def test_create_new_template(self):
        """测试创建新模板"""
        with patch.object(self.template_widget, "_refresh_templates") as mock_refresh:
            with patch(
                "src.minicrm.ui.ttk_base.quote_template_ttk.TemplateEditDialog"
            ) as mock_dialog:
                # 模拟对话框返回成功
                mock_dialog_instance = Mock()
                mock_dialog_instance.show.return_value = True
                mock_dialog.return_value = mock_dialog_instance

                # 执行创建操作
                self.template_widget._create_new_template()

                # 验证对话框创建和刷新调用
                mock_dialog.assert_called_once()
                mock_refresh.assert_called_once()

    def test_edit_template_success(self):
        """测试成功编辑模板"""
        # 选择一个非系统模板
        self.template_widget._selected_template = self.mock_templates[1]  # 自定义模板

        with patch.object(self.template_widget, "_refresh_templates") as mock_refresh:
            with patch(
                "src.minicrm.ui.ttk_base.quote_template_ttk.TemplateEditDialog"
            ) as mock_dialog:
                # 模拟对话框返回成功
                mock_dialog_instance = Mock()
                mock_dialog_instance.show.return_value = True
                mock_dialog.return_value = mock_dialog_instance

                # 执行编辑操作
                self.template_widget._edit_template()

                # 验证对话框创建和刷新调用
                mock_dialog.assert_called_once()
                mock_refresh.assert_called_once()

    def test_edit_template_system_template(self):
        """测试编辑系统模板"""
        # 选择系统模板
        self.template_widget._selected_template = self.mock_templates[0]  # 系统模板

        with patch("tkinter.messagebox.showwarning") as mock_warning:
            self.template_widget._edit_template()

            # 验证警告显示
            mock_warning.assert_called_once()

    def test_edit_template_no_selection(self):
        """测试没有选择模板时的编辑"""
        self.template_widget._selected_template = None

        with patch("tkinter.messagebox.showwarning") as mock_warning:
            self.template_widget._edit_template()

            # 验证警告显示
            mock_warning.assert_called_once()

    def test_copy_template_success(self):
        """测试成功复制模板"""
        # 选择模板
        self.template_widget._selected_template = self.mock_templates[0]

        # 模拟用户输入新名称
        with patch("tkinter.simpledialog.askstring", return_value="复制的模板"):
            # 模拟服务成功
            self.mock_template_service.duplicate_template.return_value = (
                "new_template_id"
            )

            with patch("tkinter.messagebox.showinfo") as mock_info:
                with patch.object(
                    self.template_widget, "_refresh_templates"
                ) as mock_refresh:
                    self.template_widget._copy_template()

                    # 验证服务调用
                    self.mock_template_service.duplicate_template.assert_called_once()
                    mock_info.assert_called_once()
                    mock_refresh.assert_called_once()

    def test_copy_template_cancelled(self):
        """测试取消复制模板"""
        # 选择模板
        self.template_widget._selected_template = self.mock_templates[0]

        # 模拟用户取消输入
        with patch("tkinter.simpledialog.askstring", return_value=None):
            self.template_widget._copy_template()

            # 验证服务未被调用
            self.mock_template_service.duplicate_template.assert_not_called()

    def test_delete_template_success(self):
        """测试成功删除模板"""
        # 选择非系统、非默认模板
        custom_template = {
            "id": "custom2",
            "name": "可删除模板",
            "is_system": False,
            "is_default": False,
        }
        self.template_widget._selected_template = custom_template

        # 模拟用户确认删除
        with patch("tkinter.messagebox.askyesno", return_value=True):
            # 模拟服务成功
            self.mock_template_service.delete_template.return_value = True

            with patch("tkinter.messagebox.showinfo") as mock_info:
                with patch.object(
                    self.template_widget, "_refresh_templates"
                ) as mock_refresh:
                    self.template_widget._delete_template()

                    # 验证服务调用
                    self.mock_template_service.delete_template.assert_called_once_with(
                        "custom2"
                    )
                    mock_info.assert_called_once()
                    mock_refresh.assert_called_once()

    def test_delete_template_system_template(self):
        """测试删除系统模板"""
        # 选择系统模板
        self.template_widget._selected_template = self.mock_templates[0]

        with patch("tkinter.messagebox.showwarning") as mock_warning:
            self.template_widget._delete_template()

            # 验证警告显示
            mock_warning.assert_called_once()

    def test_set_as_default_success(self):
        """测试成功设置默认模板"""
        # 选择非默认模板
        self.template_widget._selected_template = self.mock_templates[1]

        # 模拟服务成功
        self.mock_template_service.set_default_template.return_value = True

        with patch("tkinter.messagebox.showinfo") as mock_info:
            with patch.object(
                self.template_widget, "_refresh_templates"
            ) as mock_refresh:
                self.template_widget._set_as_default()

                # 验证服务调用
                self.mock_template_service.set_default_template.assert_called_once()
                mock_info.assert_called_once()
                mock_refresh.assert_called_once()

    def test_apply_template(self):
        """测试应用模板"""
        # 设置回调函数
        mock_callback = Mock()
        self.template_widget.on_template_applied = mock_callback

        # 选择模板
        self.template_widget._selected_template = self.mock_templates[0]

        # 执行应用操作
        self.template_widget._apply_template()

        # 验证回调调用
        mock_callback.assert_called_once_with(self.mock_templates[0])

    def test_import_template_success(self):
        """测试成功导入模板"""
        mock_file_path = "/test/template.json"
        mock_template_data = {"name": "导入的模板", "description": "从文件导入的模板"}

        with patch("tkinter.filedialog.askopenfilename", return_value=mock_file_path):
            with patch("builtins.open", create=True) as mock_open:
                with patch("json.load", return_value=mock_template_data):
                    # 模拟服务成功
                    self.mock_template_service.create_template.return_value = (
                        "imported_id"
                    )

                    with patch("tkinter.messagebox.showinfo") as mock_info:
                        with patch.object(
                            self.template_widget, "_refresh_templates"
                        ) as mock_refresh:
                            self.template_widget._import_template()

                            # 验证服务调用
                            self.mock_template_service.create_template.assert_called_once()
                            mock_info.assert_called_once()
                            mock_refresh.assert_called_once()

    def test_export_template_success(self):
        """测试成功导出模板"""
        # 选择模板
        self.template_widget._selected_template = self.mock_templates[0]

        # 模拟获取完整模板数据
        full_template = {**self.mock_templates[0], "config": {"test": "config"}}
        self.mock_template_service.get_template.return_value = full_template

        mock_file_path = "/test/export.json"

        with patch("tkinter.filedialog.asksaveasfilename", return_value=mock_file_path):
            with patch("builtins.open", create=True) as mock_open:
                with patch("json.dump") as mock_json_dump:
                    with patch("tkinter.messagebox.showinfo") as mock_info:
                        self.template_widget._export_template()

                        # 验证文件操作
                        mock_open.assert_called_once()
                        mock_json_dump.assert_called_once()
                        mock_info.assert_called_once()

    def test_get_selected_template(self):
        """测试获取选中模板"""
        # 初始状态
        self.assertIsNone(self.template_widget.get_selected_template())

        # 设置选中模板
        self.template_widget._selected_template = self.mock_templates[0]

        # 验证获取结果
        selected = self.template_widget.get_selected_template()
        self.assertEqual(selected, self.mock_templates[0])

    def test_get_all_templates(self):
        """测试获取所有模板"""
        all_templates = self.template_widget.get_all_templates()

        # 验证返回副本
        self.assertEqual(len(all_templates), 2)
        self.assertIsNot(all_templates, self.template_widget._templates)

    def test_cleanup(self):
        """测试资源清理"""
        # 设置一些数据
        self.template_widget._selected_template = self.mock_templates[0]

        # 执行清理
        self.template_widget.cleanup()

        # 验证清理结果
        self.assertEqual(len(self.template_widget._templates), 0)
        self.assertIsNone(self.template_widget._selected_template)

    def test_button_states_update(self):
        """测试按钮状态更新"""
        # 初始状态 - 没有选择
        self.template_widget._selected_template = None
        self.template_widget._update_button_states()

        # 验证按钮状态
        self.assertEqual(self.template_widget._edit_btn.cget("state"), "disabled")
        self.assertEqual(self.template_widget._copy_btn.cget("state"), "disabled")
        self.assertEqual(self.template_widget._delete_btn.cget("state"), "disabled")
        self.assertEqual(self.template_widget._export_btn.cget("state"), "disabled")

        # 选择非系统模板
        self.template_widget._selected_template = self.mock_templates[1]
        self.template_widget._update_button_states()

        # 验证按钮状态
        self.assertEqual(self.template_widget._edit_btn.cget("state"), "normal")
        self.assertEqual(self.template_widget._copy_btn.cget("state"), "normal")
        self.assertEqual(self.template_widget._export_btn.cget("state"), "normal")


class TestTemplateEditDialog(unittest.TestCase):
    """模板编辑对话框测试类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()

        self.mock_template_service = Mock(spec=QuoteTemplateService)

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "root"):
            self.root.destroy()

    def test_create_mode_initialization(self):
        """测试创建模式初始化"""
        dialog = TemplateEditDialog(
            self.root, self.mock_template_service, mode="create"
        )

        # 验证初始化
        self.assertEqual(dialog.mode, "create")
        self.assertEqual(dialog.name_var.get(), "")
        self.assertEqual(dialog.description_var.get(), "")
        self.assertEqual(dialog.version_var.get(), "1.0")

    def test_edit_mode_initialization(self):
        """测试编辑模式初始化"""
        template_data = {
            "name": "测试模板",
            "description": "测试描述",
            "version": "2.0",
        }

        dialog = TemplateEditDialog(
            self.root,
            self.mock_template_service,
            mode="edit",
            template_data=template_data,
        )

        # 验证初始化
        self.assertEqual(dialog.mode, "edit")
        self.assertEqual(dialog.name_var.get(), "测试模板")
        self.assertEqual(dialog.description_var.get(), "测试描述")
        self.assertEqual(dialog.version_var.get(), "2.0")


if __name__ == "__main__":
    unittest.main()
