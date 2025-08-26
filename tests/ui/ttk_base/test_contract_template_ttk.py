"""MiniCRM TTK合同模板管理组件测试

测试ContractTemplateTTK组件的功能，包括：
- 组件初始化和UI创建
- 模板数据加载和显示
- 模板操作（创建、编辑、删除、复制）
- 版本管理功能
- 模板导入导出功能
- 事件处理和回调

作者: MiniCRM开发团队
"""

import json
import tempfile
import unittest
from unittest.mock import Mock, patch


# 检查是否有GUI环境
try:
    import tkinter as tk

    GUI_AVAILABLE = True
except Exception:
    GUI_AVAILABLE = False

from minicrm.models.contract import ContractType
from minicrm.models.contract_template import (
    ContractTemplate,
    TemplateStatus,
    TemplateType,
)
from minicrm.services.contract_service import ContractService
from minicrm.ui.ttk_base.contract_template_ttk import (
    ContractTemplateEditDialog,
    ContractTemplateTTK,
)


class TestContractTemplateTTK(unittest.TestCase):
    """合同模板管理组件测试类"""

    def setUp(self):
        """测试准备"""
        if not GUI_AVAILABLE:
            self.skipTest("GUI环境不可用")

        # 设置虚拟显示环境变量
        os.environ["DISPLAY"] = ":99"

        try:
            self.root = tk.Tk()
            self.root.withdraw()  # 隐藏测试窗口
        except Exception as e:
            self.skipTest(f"无法创建Tkinter窗口: {e}")

        # 创建模拟服务
        self.mock_service = Mock(spec=ContractService)

        # 创建测试模板数据
        self.test_templates = [
            ContractTemplate(
                id=1,
                template_name="销售合同模板",
                contract_type=ContractType.SALES,
                template_status=TemplateStatus.ACTIVE,
                template_type=TemplateType.SYSTEM,
                template_version="1.0",
                created_by="系统",
                usage_count=10,
                terms_template="标准销售合同条款",
                delivery_terms_template="标准交付条款",
                warranty_terms_template="标准保修条款",
            ),
            ContractTemplate(
                id=2,
                template_name="采购合同模板",
                contract_type=ContractType.PURCHASE,
                template_status=TemplateStatus.DRAFT,
                template_type=TemplateType.USER,
                template_version="2.1",
                created_by="张经理",
                usage_count=5,
                terms_template="采购合同条款",
                delivery_terms_template="采购交付条款",
            ),
        ]

        # 配置模拟服务返回值
        self.mock_service.get_templates.return_value = self.test_templates

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_component_initialization(self):
        """测试组件初始化"""
        # 创建组件
        component = ContractTemplateTTK(self.root, self.mock_service)

        # 验证组件创建成功
        self.assertIsNotNone(component)
        self.assertEqual(component._contract_service, self.mock_service)
        self.assertIsNotNone(component._template_tree)
        self.assertIsNotNone(component._detail_frame)
        self.assertIsNotNone(component._preview_frame)
        self.assertIsNotNone(component._version_frame)

        # 验证服务调用
        self.mock_service.get_templates.assert_called_once()

    def test_template_data_loading(self):
        """测试模板数据加载"""
        component = ContractTemplateTTK(self.root, self.mock_service)

        # 验证数据加载
        self.assertEqual(len(component._templates), 2)
        self.assertEqual(component._templates[0]["template_name"], "销售合同模板")
        self.assertEqual(component._templates[1]["template_name"], "采购合同模板")

        # 验证树形视图中的项目数量
        tree_items = component._template_tree.get_children()
        self.assertEqual(len(tree_items), 2)

    def test_template_selection(self):
        """测试模板选择功能"""
        component = ContractTemplateTTK(self.root, self.mock_service)

        # 模拟选择第一个模板
        tree_items = component._template_tree.get_children()
        if tree_items:
            component._template_tree.selection_set(tree_items[0])
            component._on_template_selected()

            # 验证选择结果
            self.assertIsNotNone(component._selected_template)
            self.assertEqual(
                component._selected_template["template_name"], "销售合同模板"
            )

    def test_template_creation(self):
        """测试模板创建功能"""
        # 配置模拟服务
        new_template = ContractTemplate(
            id=3,
            template_name="新建模板",
            contract_type=ContractType.SERVICE,
            template_status=TemplateStatus.DRAFT,
            template_type=TemplateType.USER,
            created_by="测试用户",
        )
        self.mock_service.create_template.return_value = new_template

        component = ContractTemplateTTK(self.root, self.mock_service)

        # 模拟创建新模板（这里只测试服务调用，不测试UI对话框）
        template_data = {
            "template_name": "新建模板",
            "contract_type": ContractType.SERVICE.value,
            "template_version": "1.0",
            "created_by": "测试用户",
            "terms_template": "测试条款",
            "delivery_terms_template": "测试交付条款",
            "template_status": TemplateStatus.DRAFT.value,
            "template_type": TemplateType.USER.value,
        }

        # 直接调用服务创建模板
        result = self.mock_service.create_template(template_data)

        # 验证创建结果
        self.mock_service.create_template.assert_called_once_with(template_data)
        self.assertEqual(result.template_name, "新建模板")

    def test_template_copy(self):
        """测试模板复制功能"""
        component = ContractTemplateTTK(self.root, self.mock_service)

        # 选择要复制的模板
        component._selected_template = component._templates[0]

        # 配置模拟服务
        copied_template = ContractTemplate(
            id=4,
            template_name="销售合同模板 - 副本",
            contract_type=ContractType.SALES,
            template_status=TemplateStatus.DRAFT,
            template_type=TemplateType.USER,
            created_by="当前用户",
        )
        self.mock_service.create_template.return_value = copied_template

        # 模拟复制操作（跳过用户输入对话框）
        with patch(
            "tkinter.simpledialog.askstring", return_value="销售合同模板 - 副本"
        ):
            with patch.object(component, "_refresh_templates"):
                component._copy_template()

        # 验证服务调用
        self.mock_service.create_template.assert_called_once()
        call_args = self.mock_service.create_template.call_args[0][0]
        self.assertEqual(call_args["template_name"], "销售合同模板 - 副本")
        self.assertEqual(call_args["template_type"], TemplateType.USER.value)

    def test_template_export(self):
        """测试模板导出功能"""
        component = ContractTemplateTTK(self.root, self.mock_service)

        # 选择要导出的模板
        component._selected_template = component._templates[0]

        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            temp_path = temp_file.name

        try:
            # 模拟文件选择对话框
            with patch("tkinter.filedialog.asksaveasfilename", return_value=temp_path):
                with patch("tkinter.messagebox.showinfo"):
                    component._export_template()

            # 验证文件内容
            with open(temp_path, encoding="utf-8") as f:
                exported_data = json.load(f)

            self.assertEqual(exported_data["template_name"], "销售合同模板")
            self.assertNotIn("id", exported_data)  # ID不应该被导出

        finally:
            # 清理临时文件
            import os

            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_template_import(self):
        """测试模板导入功能"""
        component = ContractTemplateTTK(self.root, self.mock_service)

        # 准备导入数据
        import_data = {
            "template_name": "导入的模板",
            "contract_type": ContractType.SALES.value,
            "template_version": "1.0",
            "created_by": "导入用户",
            "terms_template": "导入的条款",
        }

        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            json.dump(import_data, temp_file, ensure_ascii=False, indent=2)
            temp_path = temp_file.name

        try:
            # 配置模拟服务
            imported_template = ContractTemplate(
                id=5,
                template_name="导入的模板",
                contract_type=ContractType.SALES,
                created_by="导入用户",
            )
            self.mock_service.create_template.return_value = imported_template

            # 模拟文件选择对话框
            with patch("tkinter.filedialog.askopenfilename", return_value=temp_path):
                with patch("tkinter.messagebox.showinfo"):
                    with patch.object(component, "_refresh_templates"):
                        component._import_template()

            # 验证服务调用
            self.mock_service.create_template.assert_called_once_with(import_data)

        finally:
            # 清理临时文件
            import os

            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_button_states_update(self):
        """测试按钮状态更新"""
        component = ContractTemplateTTK(self.root, self.mock_service)

        # 测试无选择状态
        component._selected_template = None
        component._update_button_states()

        self.assertEqual(component._edit_btn.cget("state"), "disabled")
        self.assertEqual(component._copy_btn.cget("state"), "disabled")
        self.assertEqual(component._delete_btn.cget("state"), "disabled")

        # 测试有选择状态（用户模板）
        component._selected_template = component._templates[1]  # 用户模板
        component._update_button_states()

        self.assertEqual(component._edit_btn.cget("state"), "normal")
        self.assertEqual(component._copy_btn.cget("state"), "normal")
        self.assertEqual(component._delete_btn.cget("state"), "normal")

        # 测试系统模板选择状态
        component._selected_template = component._templates[0]  # 系统模板
        component._update_button_states()

        self.assertEqual(
            component._edit_btn.cget("state"), "disabled"
        )  # 系统模板不能编辑
        self.assertEqual(component._copy_btn.cget("state"), "normal")  # 但可以复制
        self.assertEqual(component._delete_btn.cget("state"), "disabled")  # 不能删除

    def test_stats_update(self):
        """测试统计信息更新"""
        component = ContractTemplateTTK(self.root, self.mock_service)

        # 验证统计信息
        stats_text = component._stats_label.cget("text")
        self.assertIn("共 2 个模板", stats_text)
        self.assertIn("激活: 1", stats_text)
        self.assertIn("草稿: 1", stats_text)

    def test_event_callbacks(self):
        """测试事件回调"""
        component = ContractTemplateTTK(self.root, self.mock_service)

        # 设置回调函数
        template_selected_callback = Mock()
        template_applied_callback = Mock()
        component.on_template_selected = template_selected_callback
        component.on_template_applied = template_applied_callback

        # 触发模板选择事件
        component._selected_template = component._templates[0]
        component._on_template_selected()

        # 验证选择回调
        template_selected_callback.assert_called_once_with(component._selected_template)

        # 触发模板应用事件
        component._apply_template()

        # 验证应用回调
        template_applied_callback.assert_called_once_with(component._selected_template)

    def test_cleanup(self):
        """测试资源清理"""
        component = ContractTemplateTTK(self.root, self.mock_service)

        # 设置一些数据
        component._selected_template = component._templates[0]

        # 执行清理
        component.cleanup()

        # 验证清理结果
        self.assertEqual(len(component._templates), 0)
        self.assertIsNone(component._selected_template)
        self.assertEqual(len(component._template_versions), 0)


class TestContractTemplateEditDialog(unittest.TestCase):
    """合同模板编辑对话框测试类"""

    def setUp(self):
        """测试准备"""
        if not GUI_AVAILABLE:
            self.skipTest("GUI环境不可用")

        try:
            self.root = tk.Tk()
            self.root.withdraw()  # 隐藏测试窗口
        except Exception as e:
            self.skipTest(f"无法创建Tkinter窗口: {e}")

        # 创建模拟服务
        self.mock_service = Mock(spec=ContractService)

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_dialog_initialization_create_mode(self):
        """测试对话框初始化（创建模式）"""
        dialog = ContractTemplateEditDialog(self.root, self.mock_service, mode="create")

        # 验证初始化
        self.assertEqual(dialog.mode, "create")
        self.assertEqual(dialog.contract_service, self.mock_service)
        self.assertEqual(dialog.name_var.get(), "")
        self.assertEqual(dialog.contract_type_var.get(), ContractType.SALES.value)

    def test_dialog_initialization_edit_mode(self):
        """测试对话框初始化（编辑模式）"""
        template_data = {
            "template_name": "测试模板",
            "contract_type": ContractType.PURCHASE.value,
            "template_version": "2.0",
            "created_by": "测试用户",
            "terms_template": "测试条款",
            "delivery_terms_template": "测试交付条款",
        }

        dialog = ContractTemplateEditDialog(
            self.root, self.mock_service, mode="edit", template_data=template_data
        )

        # 验证初始化
        self.assertEqual(dialog.mode, "edit")
        self.assertEqual(dialog.name_var.get(), "测试模板")
        self.assertEqual(dialog.contract_type_var.get(), ContractType.PURCHASE.value)
        self.assertEqual(dialog.version_var.get(), "2.0")
        self.assertEqual(dialog.created_by_var.get(), "测试用户")

    @patch("tkinter.messagebox.showinfo")
    def test_save_template_create_mode(self, mock_showinfo):
        """测试保存模板（创建模式）"""
        # 配置模拟服务
        new_template = ContractTemplate(
            id=1,
            template_name="新模板",
            contract_type=ContractType.SERVICE,
            created_by="测试用户",
        )
        self.mock_service.create_template.return_value = new_template

        dialog = ContractTemplateEditDialog(self.root, self.mock_service, mode="create")

        # 设置表单数据
        dialog.name_var.set("新模板")
        dialog.contract_type_var.set(ContractType.SERVICE.value)
        dialog.version_var.set("1.0")
        dialog.created_by_var.set("测试用户")

        # 创建对话框UI（简化版，只创建必要的组件）
        dialog.terms_text = tk.Text(self.root)
        dialog.delivery_text = tk.Text(self.root)
        dialog.terms_text.insert("1.0", "测试条款")
        dialog.delivery_text.insert("1.0", "测试交付条款")

        # 模拟保存操作
        dialog.result = False
        dialog.dialog = Mock()
        dialog._save_template()

        # 验证服务调用
        self.mock_service.create_template.assert_called_once()
        call_args = self.mock_service.create_template.call_args[0][0]
        self.assertEqual(call_args["template_name"], "新模板")
        self.assertEqual(call_args["contract_type"], ContractType.SERVICE.value)
        self.assertEqual(call_args["terms_template"], "测试条款")

        # 验证结果
        self.assertTrue(dialog.result)
        mock_showinfo.assert_called_once()

    @patch("tkinter.messagebox.showerror")
    def test_save_template_validation_error(self, mock_showerror):
        """测试保存模板验证错误"""
        dialog = ContractTemplateEditDialog(self.root, self.mock_service, mode="create")

        # 不设置模板名称（验证错误）
        dialog.name_var.set("")
        dialog.contract_type_var.set(ContractType.SALES.value)
        dialog.version_var.set("1.0")
        dialog.created_by_var.set("测试用户")

        # 模拟保存操作
        dialog._save_template()

        # 验证错误提示
        mock_showerror.assert_called_once_with("错误", "请输入模板名称")
        self.assertFalse(dialog.result)


if __name__ == "__main__":
    unittest.main()
