"""
MiniCRM 合同模板TTK组件单元测试

测试ContractTemplateTTK类的功能, 包括:
- 模板列表显示和管理
- 模板创建、编辑、删除
- 模板版本控制和历史管理
- 模板预览和应用
- 模板导入导出
- 使用统计和分析

作者: MiniCRM开发团队
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import tkinter as tk
from tkinter import ttk
from unittest.mock import Mock, patch

import pytest

from minicrm.core.exceptions import ServiceError
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


class TestContractTemplateTTK:
    """ContractTemplateTTK组件测试类"""

    @pytest.fixture
    def root(self):
        """创建测试用的根窗口"""
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        yield root
        root.destroy()

    @pytest.fixture
    def mock_contract_service(self):
        """创建模拟的合同服务"""
        service = Mock(spec=ContractService)

        # 模拟模板数据
        template1 = ContractTemplate(
            id=1,
            template_name="销售合同模板",
            contract_type=ContractType.SALES,
            template_status=TemplateStatus.ACTIVE,
            template_type=TemplateType.SYSTEM,
            template_version="1.0",
            created_by="系统",
            usage_count=10,
            terms_template="标准销售条款",
            delivery_terms_template="标准交付条款",
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )

        template2 = ContractTemplate(
            id=2,
            template_name="采购合同模板",
            contract_type=ContractType.PURCHASE,
            template_status=TemplateStatus.DRAFT,
            template_type=TemplateType.USER,
            template_version="1.1",
            created_by="用户A",
            usage_count=5,
            terms_template="标准采购条款",
            delivery_terms_template="标准交付条款",
            created_at=datetime(2024, 1, 15, tzinfo=timezone.utc),
        )

        service.get_templates.return_value = [template1, template2]
        service.create_template.return_value = template1

        return service

    @pytest.fixture
    def template_widget(self, root, mock_contract_service):
        """创建测试用的模板组件"""
        return ContractTemplateTTK(root, contract_service=mock_contract_service)

    def test_initialization(self, template_widget, mock_contract_service):
        """测试组件初始化"""
        assert template_widget._contract_service == mock_contract_service
        assert template_widget._templates is not None
        assert template_widget._selected_template is None
        assert template_widget._template_tree is not None

        # 验证服务方法被调用
        mock_contract_service.get_templates.assert_called_once()

    def test_load_templates(self, template_widget):
        """测试加载模板数据"""
        # 验证模板数据已加载
        assert len(template_widget._templates) == 2

        # 验证模板数据格式
        template_data = template_widget._templates[0]
        assert "template_name" in template_data
        assert "contract_type" in template_data
        assert "template_status" in template_data

    def test_refresh_template_list(self, template_widget):
        """测试刷新模板列表显示"""
        # 获取树形视图中的项目数量
        tree_items = template_widget._template_tree.get_children()
        assert len(tree_items) == 2

        # 验证第一个项目的数据
        first_item = tree_items[0]
        values = template_widget._template_tree.item(first_item, "values")
        assert values[0] == "销售合同模板"  # 模板名称

    def test_template_selection(self, template_widget):
        """测试模板选择功能"""
        # 模拟选择第一个模板
        tree_items = template_widget._template_tree.get_children()
        if tree_items:
            template_widget._template_tree.selection_set(tree_items[0])
            template_widget._on_template_selected()

            # 验证选中的模板
            assert template_widget._selected_template is not None
            assert template_widget._selected_template["template_name"] == "销售合同模板"

    def test_update_stats(self, template_widget):
        """测试统计信息更新"""
        template_widget._update_stats()

        # 验证统计标签有内容
        stats_text = template_widget._stats_label.cget("text")
        assert "共 2 个模板" in stats_text
        assert "激活: 1" in stats_text

    def test_button_states_no_selection(self, template_widget):
        """测试无选择时的按钮状态"""
        template_widget._selected_template = None
        template_widget._update_button_states()

        # 验证按钮状态
        assert template_widget._edit_btn.cget("state") == "disabled"
        assert template_widget._copy_btn.cget("state") == "disabled"
        assert template_widget._delete_btn.cget("state") == "disabled"

    def test_button_states_with_selection(self, template_widget):
        """测试有选择时的按钮状态"""
        # 设置选中的模板(用户模板)
        template_widget._selected_template = {
            "id": 2,
            "template_type": TemplateType.USER.value,
            "is_editable": True,
        }
        template_widget._update_button_states()

        # 验证按钮状态
        assert template_widget._edit_btn.cget("state") == "normal"
        assert template_widget._copy_btn.cget("state") == "normal"
        assert template_widget._delete_btn.cget("state") == "normal"

    def test_button_states_system_template(self, template_widget):
        """测试系统模板的按钮状态"""
        # 设置选中的模板(系统模板)
        template_widget._selected_template = {
            "id": 1,
            "template_type": TemplateType.SYSTEM.value,
            "is_editable": False,
        }
        template_widget._update_button_states()

        # 验证按钮状态(系统模板不能编辑和删除)
        assert template_widget._edit_btn.cget("state") == "disabled"
        assert template_widget._copy_btn.cget("state") == "normal"  # 可以复制
        assert template_widget._delete_btn.cget("state") == "disabled"

    @patch("tkinter.messagebox.showinfo")
    def test_copy_template_success(
        self, mock_showinfo, template_widget, mock_contract_service
    ):
        """测试复制模板成功"""
        # 设置选中的模板
        template_widget._selected_template = {
            "id": 1,
            "template_name": "原模板",
            "template_status": TemplateStatus.ACTIVE.value,
            "template_type": TemplateType.SYSTEM.value,
            "template_version": "1.0",
            "usage_count": 10,
            "created_by": "系统",
            "terms_template": "条款内容",
        }

        # 模拟用户输入新名称
        with patch("tkinter.simpledialog.askstring", return_value="复制的模板"):
            template_widget._copy_template()

        # 验证服务方法被调用
        mock_contract_service.create_template.assert_called_once()
        mock_showinfo.assert_called_once()

    @patch("tkinter.messagebox.showwarning")
    def test_copy_template_no_selection(self, mock_showwarning, template_widget):
        """测试无选择时复制模板"""
        template_widget._selected_template = None
        template_widget._copy_template()

        mock_showwarning.assert_called_once_with("提示", "请先选择要复制的模板")

    @patch("tkinter.messagebox.showerror")
    def test_copy_template_service_error(
        self, mock_showerror, template_widget, mock_contract_service
    ):
        """测试复制模板服务错误"""
        # 设置选中的模板
        template_widget._selected_template = {
            "id": 1,
            "template_name": "原模板",
            "template_status": TemplateStatus.ACTIVE.value,
        }

        # 模拟服务错误
        mock_contract_service.create_template.side_effect = ServiceError("创建失败")

        with patch("tkinter.simpledialog.askstring", return_value="复制的模板"):
            template_widget._copy_template()

        mock_showerror.assert_called_once()

    def test_format_datetime(self, template_widget):
        """测试日期时间格式化"""
        # 测试正常日期时间
        dt_str = "2024-01-15T10:30:00"
        formatted = template_widget._format_datetime(dt_str)
        assert "2024-01-15" in formatted

        # 测试空字符串
        formatted = template_widget._format_datetime("")
        assert formatted == "未知"

        # 测试无效格式
        formatted = template_widget._format_datetime("invalid")
        assert formatted == "invalid"

    def test_determine_priority(self, template_widget):
        """测试优先级确定"""
        # 高优先级(超过7天)
        approval = {"contract_amount": Decimal(500000)}
        priority = template_widget._determine_priority(approval, 8)
        assert priority == "高"

        # 高优先级(金额超过100万)
        approval = {"contract_amount": Decimal(1500000)}
        priority = template_widget._determine_priority(approval, 2)
        assert priority == "高"

        # 中优先级
        approval = {"contract_amount": Decimal(600000)}
        priority = template_widget._determine_priority(approval, 4)
        assert priority == "中"

        # 低优先级
        approval = {"contract_amount": Decimal(100000)}
        priority = template_widget._determine_priority(approval, 1)
        assert priority == "低"

    def test_calculate_pending_days(self, template_widget):
        """测试待审天数计算"""
        # 测试正常日期
        past_date = (datetime.now(tz=timezone.utc) - timedelta(days=5)).isoformat()
        days = template_widget._calculate_pending_days(past_date)
        assert days == 5

        # 测试空字符串
        days = template_widget._calculate_pending_days("")
        assert days == 0

        # 测试无效格式
        days = template_widget._calculate_pending_days("invalid")
        assert days == 0

    @patch("tkinter.messagebox.showinfo")
    def test_refresh_templates(self, template_widget, mock_contract_service):
        """测试刷新模板功能"""
        # 重置调用计数
        mock_contract_service.get_templates.reset_mock()

        # 调用刷新
        template_widget._refresh_templates()

        # 验证服务方法被再次调用
        mock_contract_service.get_templates.assert_called_once()

    def test_show_empty_detail(self, template_widget):
        """测试显示空详情状态"""
        template_widget._show_empty_detail()

        # 验证详情框架中有提示标签
        children = template_widget._detail_frame.winfo_children()
        assert len(children) > 0

        # 查找提示标签
        tip_found = False
        for child in children:
            if isinstance(child, ttk.Label) and "请选择模板查看详情" in child.cget(
                "text"
            ):
                tip_found = True
                break
        assert tip_found

    def test_event_callbacks(self, template_widget):
        """测试事件回调功能"""
        # 设置回调函数
        callback_called = False
        selected_template = None

        def on_template_selected(template):
            nonlocal callback_called, selected_template
            callback_called = True
            selected_template = template

        template_widget.on_template_selected = on_template_selected

        # 设置选中模板并触发事件
        template_widget._selected_template = {"id": 1, "name": "测试模板"}
        template_widget._on_template_selected()

        # 验证回调被调用
        assert callback_called
        assert selected_template == template_widget._selected_template

    def test_cleanup(self, template_widget):
        """测试组件清理"""
        # 添加一些数据
        template_widget.set_data("test_key", "test_value")

        # 执行清理
        template_widget.cleanup()

        # 验证数据被清理
        assert len(template_widget.get_all_data()) == 0


class TestContractTemplateEditDialog:
    """合同模板编辑对话框测试类"""

    @pytest.fixture
    def root(self):
        """创建测试用的根窗口"""
        root = tk.Tk()
        root.withdraw()
        yield root
        root.destroy()

    @pytest.fixture
    def mock_contract_service(self):
        """创建模拟的合同服务"""
        service = Mock(spec=ContractService)
        template = ContractTemplate(
            id=1,
            template_name="测试模板",
            contract_type=ContractType.SALES,
            template_version="1.0",
            created_by="测试用户",
        )
        service.create_template.return_value = template
        return service

    def test_dialog_initialization_create_mode(self, root, mock_contract_service):
        """测试创建模式的对话框初始化"""

        dialog = ContractTemplateEditDialog(root, mock_contract_service, mode="create")

        assert dialog.mode == "create"
        assert dialog.contract_service == mock_contract_service
        assert dialog.template_data == {}
        assert dialog.result is False

    def test_dialog_initialization_edit_mode(self, root, mock_contract_service):
        """测试编辑模式的对话框初始化"""

        template_data = {
            "template_name": "现有模板",
            "contract_type": ContractType.SALES.value,
            "template_version": "1.0",
            "created_by": "用户",
        }

        dialog = ContractTemplateEditDialog(
            root, mock_contract_service, mode="edit", template_data=template_data
        )

        assert dialog.mode == "edit"
        assert dialog.template_data == template_data

    @patch("tkinter.messagebox.showerror")
    def test_save_template_validation_error(
        self, mock_showerror, root, mock_contract_service
    ):
        """测试保存模板时的验证错误"""

        dialog = ContractTemplateEditDialog(root, mock_contract_service, mode="create")

        # 不设置任何值, 直接保存
        dialog._save_template()

        # 验证显示错误消息
        mock_showerror.assert_called_once()

    @patch("tkinter.messagebox.showinfo")
    def test_save_template_success(self, mock_showinfo, root, mock_contract_service):
        """测试成功保存模板"""

        dialog = ContractTemplateEditDialog(root, mock_contract_service, mode="create")

        # 设置有效的输入值
        dialog.name_var.set("新模板")
        dialog.contract_type_var.set("销售合同")
        dialog.version_var.set("1.0")
        dialog.created_by_var.set("测试用户")

        # 模拟文本框内容
        dialog.terms_text = Mock()
        dialog.terms_text.get.return_value = "条款内容"
        dialog.delivery_text = Mock()
        dialog.delivery_text.get.return_value = "交付条款"

        # 模拟对话框销毁
        dialog.dialog = Mock()

        dialog._save_template()

        # 验证服务方法被调用
        mock_contract_service.create_template.assert_called_once()
        mock_showinfo.assert_called_once()
        assert dialog.result is True


if __name__ == "__main__":
    pytest.main([__file__])
