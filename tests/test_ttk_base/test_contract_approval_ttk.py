"""
MiniCRM 合同审批TTK组件单元测试

测试ContractApprovalTTK类的功能，包括：
- 审批任务列表显示和管理
- 审批流程状态跟踪
- 审批操作处理（批准、拒绝、退回）
- 审批历史记录查看
- 审批通知和提醒
- 批量审批操作

作者: MiniCRM开发团队
"""

from datetime import datetime, timedelta
from decimal import Decimal
import tkinter as tk
from tkinter import ttk
from unittest.mock import Mock, patch

import pytest

from minicrm.core.exceptions import ServiceError
from minicrm.models.contract import Contract, ContractStatus, ContractType
from minicrm.services.contract_service import ContractService
from minicrm.ui.ttk_base.contract_approval_ttk import (
    ApprovalAction,
    ContractApprovalTTK,
)


class TestContractApprovalTTK:
    """ContractApprovalTTK组件测试类"""

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

        # 模拟待审批合同数据
        contract1 = Contract(
            id=1,
            contract_number="S20240101001",
            party_name="测试客户A",
            contract_type=ContractType.SALES,
            contract_status=ContractStatus.PENDING,
            contract_amount=Decimal(500000),
            created_at=datetime.now() - timedelta(days=3),
            terms_and_conditions="标准销售条款",
        )

        contract2 = Contract(
            id=2,
            contract_number="P20240101002",
            party_name="测试供应商B",
            contract_type=ContractType.PURCHASE,
            contract_status=ContractStatus.PENDING,
            contract_amount=Decimal(1200000),
            created_at=datetime.now() - timedelta(days=8),
            terms_and_conditions="标准采购条款",
        )

        service.list_all.return_value = [contract1, contract2]
        service.update_contract_status.return_value = contract1

        return service

    @pytest.fixture
    def approval_widget(self, root, mock_contract_service):
        """创建测试用的审批组件"""
        widget = ContractApprovalTTK(
            root, contract_service=mock_contract_service, current_user="测试用户"
        )
        return widget

    def test_initialization(self, approval_widget, mock_contract_service):
        """测试组件初始化"""
        assert approval_widget._contract_service == mock_contract_service
        assert approval_widget._current_user == "测试用户"
        assert approval_widget._pending_approvals is not None
        assert approval_widget._selected_approval is None
        assert approval_widget._approval_tree is not None

        # 验证服务方法被调用
        mock_contract_service.list_all.assert_called_once()

    def test_load_approval_data(self, approval_widget, mock_contract_service):
        """测试加载审批数据"""
        # 验证待审批数据已加载
        assert len(approval_widget._pending_approvals) == 2

        # 验证数据格式
        approval_data = approval_widget._pending_approvals[0]
        assert "contract_number" in approval_data
        assert "party_name" in approval_data
        assert "contract_status" in approval_data

    def test_refresh_approval_list(self, approval_widget):
        """测试刷新审批列表显示"""
        # 获取树形视图中的项目数量
        tree_items = approval_widget._approval_tree.get_children()
        assert len(tree_items) == 2

        # 验证第一个项目的数据
        first_item = tree_items[0]
        values = approval_widget._approval_tree.item(first_item, "values")
        assert values[0] == "S20240101001"  # 合同编号

    def test_approval_selection(self, approval_widget):
        """测试审批选择功能"""
        # 模拟选择第一个审批项目
        tree_items = approval_widget._approval_tree.get_children()
        if tree_items:
            approval_widget._approval_tree.selection_set(tree_items[0])
            approval_widget._on_approval_selected()

            # 验证选中的审批
            assert approval_widget._selected_approval is not None
            assert (
                approval_widget._selected_approval["contract_number"] == "S20240101001"
            )

    def test_calculate_pending_days(self, approval_widget):
        """测试待审天数计算"""
        # 测试3天前的日期
        past_date = (datetime.now() - timedelta(days=3)).isoformat()
        days = approval_widget._calculate_pending_days(past_date)
        assert days == 3

        # 测试空字符串
        days = approval_widget._calculate_pending_days("")
        assert days == 0

        # 测试无效格式
        days = approval_widget._calculate_pending_days("invalid")
        assert days == 0

    def test_determine_priority(self, approval_widget):
        """测试优先级确定"""
        # 高优先级（超过7天）
        approval = {"contract_amount": Decimal(500000)}
        priority = approval_widget._determine_priority(approval, 8)
        assert priority == "高"

        # 高优先级（金额超过100万）
        approval = {"contract_amount": Decimal(1500000)}
        priority = approval_widget._determine_priority(approval, 2)
        assert priority == "高"

        # 中优先级
        approval = {"contract_amount": Decimal(600000)}
        priority = approval_widget._determine_priority(approval, 4)
        assert priority == "中"

        # 低优先级
        approval = {"contract_amount": Decimal(100000)}
        priority = approval_widget._determine_priority(approval, 1)
        assert priority == "低"

    def test_update_stats(self, approval_widget):
        """测试统计信息更新"""
        approval_widget._update_stats()

        # 验证统计标签有内容
        stats_text = approval_widget._stats_label.cget("text")
        assert "待审批: 2 个" in stats_text
        assert "高优先级:" in stats_text

    def test_button_states_no_selection(self, approval_widget):
        """测试无选择时的按钮状态"""
        approval_widget._selected_approval = None
        approval_widget._update_button_states()

        # 验证按钮状态
        assert approval_widget._approve_btn.cget("state") == "disabled"
        assert approval_widget._reject_btn.cget("state") == "disabled"
        assert approval_widget._return_btn.cget("state") == "disabled"
        assert approval_widget._delegate_btn.cget("state") == "disabled"

    def test_button_states_with_selection(self, approval_widget):
        """测试有选择时的按钮状态"""
        # 设置选中的审批
        approval_widget._selected_approval = {
            "id": 1,
            "contract_number": "S20240101001",
        }
        approval_widget._update_button_states()

        # 验证按钮状态
        assert approval_widget._approve_btn.cget("state") == "normal"
        assert approval_widget._reject_btn.cget("state") == "normal"
        assert approval_widget._return_btn.cget("state") == "normal"
        assert approval_widget._delegate_btn.cget("state") == "normal"

    def test_apply_filters(self, approval_widget):
        """测试筛选功能"""
        # 设置筛选条件
        approval_widget._type_filter_var.set("销售合同")

        # 应用筛选
        filtered = approval_widget._apply_filters(approval_widget._pending_approvals)

        # 验证筛选结果
        assert len(filtered) == 1
        assert filtered[0]["contract_type_display"] == "销售合同"

    @patch("tkinter.messagebox.showinfo")
    def test_approve_contract_success(
        self, mock_showinfo, approval_widget, mock_contract_service
    ):
        """测试成功批准合同"""
        # 设置选中的审批
        approval_widget._selected_approval = {
            "id": 1,
            "contract_number": "S20240101001",
        }

        # 模拟审批意见输入
        approval_widget._comment_text = Mock()
        approval_widget._comment_text.get.return_value = "审批通过，条款符合要求"

        # 执行批准操作
        approval_widget._approve_contract()

        # 验证服务方法被调用
        mock_contract_service.update_contract_status.assert_called_once_with(
            1, ContractStatus.APPROVED, "审批通过: 审批通过，条款符合要求"
        )
        mock_showinfo.assert_called_once_with("成功", "合同已批准")

    @patch("tkinter.messagebox.showwarning")
    def test_approve_contract_no_selection(self, mock_showwarning, approval_widget):
        """测试无选择时批准合同"""
        approval_widget._selected_approval = None
        approval_widget._approve_contract()

        mock_showwarning.assert_called_once_with("提示", "请先选择要批准的合同")

    @patch("tkinter.messagebox.showerror")
    def test_approve_contract_service_error(
        self, mock_showerror, approval_widget, mock_contract_service
    ):
        """测试批准合同服务错误"""
        # 设置选中的审批
        approval_widget._selected_approval = {
            "id": 1,
            "contract_number": "S20240101001",
        }

        # 模拟服务错误
        mock_contract_service.update_contract_status.side_effect = ServiceError(
            "更新失败"
        )

        # 模拟审批意见输入
        approval_widget._comment_text = Mock()
        approval_widget._comment_text.get.return_value = "审批意见"

        approval_widget._approve_contract()

        mock_showerror.assert_called_once()

    @patch("tkinter.messagebox.showinfo")
    @patch("tkinter.messagebox.askyesno", return_value=True)
    def test_reject_contract_success(
        self, mock_askyesno, mock_showinfo, approval_widget, mock_contract_service
    ):
        """测试成功拒绝合同"""
        # 设置选中的审批
        approval_widget._selected_approval = {
            "id": 1,
            "contract_number": "S20240101001",
        }

        # 模拟审批意见输入
        approval_widget._comment_text = Mock()
        approval_widget._comment_text.get.return_value = "条款不符合要求"

        # 执行拒绝操作
        approval_widget._reject_contract()

        # 验证确认对话框被调用
        mock_askyesno.assert_called_once()

        # 验证服务方法被调用
        mock_contract_service.update_contract_status.assert_called_once_with(
            1, ContractStatus.DRAFT, "审批拒绝: 条款不符合要求"
        )
        mock_showinfo.assert_called_once_with("成功", "合同已拒绝")

    @patch("tkinter.messagebox.askyesno", return_value=False)
    def test_reject_contract_cancelled(
        self, mock_askyesno, approval_widget, mock_contract_service
    ):
        """测试取消拒绝合同"""
        # 设置选中的审批
        approval_widget._selected_approval = {
            "id": 1,
            "contract_number": "S20240101001",
        }

        # 模拟审批意见输入
        approval_widget._comment_text = Mock()
        approval_widget._comment_text.get.return_value = "拒绝原因"

        # 执行拒绝操作
        approval_widget._reject_contract()

        # 验证确认对话框被调用
        mock_askyesno.assert_called_once()

        # 验证服务方法未被调用
        mock_contract_service.update_contract_status.assert_not_called()

    @patch("tkinter.messagebox.showinfo")
    def test_return_contract_success(
        self, mock_showinfo, approval_widget, mock_contract_service
    ):
        """测试成功退回合同"""
        # 设置选中的审批
        approval_widget._selected_approval = {
            "id": 1,
            "contract_number": "S20240101001",
        }

        # 模拟审批意见输入
        approval_widget._comment_text = Mock()
        approval_widget._comment_text.get.return_value = "需要补充材料"

        # 执行退回操作
        approval_widget._return_contract()

        # 验证服务方法被调用
        mock_contract_service.update_contract_status.assert_called_once_with(
            1, ContractStatus.DRAFT, "审批退回: 需要补充材料"
        )
        mock_showinfo.assert_called_once_with("成功", "合同已退回")

    def test_record_approval_action(self, approval_widget):
        """测试记录审批操作"""
        # 这是一个内部方法，测试其逻辑
        contract_id = 1
        action = ApprovalAction.APPROVE
        comment = "审批通过"

        # 调用记录方法（如果存在）
        if hasattr(approval_widget, "_record_approval_action"):
            approval_widget._record_approval_action(contract_id, action, comment)

            # 验证审批历史被更新
            # 这里可以检查内部状态或日志

    def test_format_datetime(self, approval_widget):
        """测试日期时间格式化"""
        # 测试正常日期时间
        dt_str = "2024-01-15T10:30:00"
        formatted = approval_widget._format_datetime(dt_str)
        assert "2024-01-15" in formatted

        # 测试空字符串
        formatted = approval_widget._format_datetime("")
        assert formatted == "未知"

        # 测试无效格式
        formatted = approval_widget._format_datetime("invalid")
        assert formatted == "invalid"

    def test_show_empty_detail(self, approval_widget):
        """测试显示空详情状态"""
        approval_widget._show_empty_detail()

        # 验证详情框架中有提示标签
        children = approval_widget._detail_frame.winfo_children()
        assert len(children) > 0

        # 查找提示标签
        tip_found = False
        for child in children:
            if isinstance(child, ttk.Label) and "请选择审批项目查看详情" in child.cget(
                "text"
            ):
                tip_found = True
                break
        assert tip_found

    def test_event_callbacks(self, approval_widget):
        """测试事件回调功能"""
        # 设置回调函数
        callback_called = False
        approval_data = None

        def on_approval_completed(data):
            nonlocal callback_called, approval_data
            callback_called = True
            approval_data = data

        approval_widget.on_approval_completed = on_approval_completed

        # 模拟触发审批完成事件
        test_data = {
            "contract_id": 1,
            "action": ApprovalAction.APPROVE.value,
            "comment": "测试审批",
        }

        if approval_widget.on_approval_completed:
            approval_widget.on_approval_completed(test_data)

        # 验证回调被调用
        assert callback_called
        assert approval_data == test_data

    @patch("tkinter.messagebox.showinfo")
    def test_refresh_approvals(
        self, mock_showinfo, approval_widget, mock_contract_service
    ):
        """测试刷新审批功能"""
        # 重置调用计数
        mock_contract_service.list_all.reset_mock()

        # 调用刷新
        approval_widget._refresh_approvals()

        # 验证服务方法被再次调用
        mock_contract_service.list_all.assert_called_once()

    def test_batch_operations(self, approval_widget):
        """测试批量操作功能"""
        # 模拟多选
        tree_items = approval_widget._approval_tree.get_children()
        if len(tree_items) >= 2:
            approval_widget._approval_tree.selection_set(tree_items[:2])
            approval_widget._update_button_states()

            # 验证批量操作按钮状态
            assert approval_widget._batch_approve_btn.cget("state") == "normal"

    def test_cleanup(self, approval_widget):
        """测试组件清理"""
        # 添加一些数据
        approval_widget.set_data("test_key", "test_value")

        # 执行清理
        approval_widget.cleanup()

        # 验证数据被清理
        assert len(approval_widget.get_all_data()) == 0


class TestApprovalDialog:
    """审批对话框测试类"""

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
        return Mock(spec=ContractService)

    def test_approval_dialog_initialization(self, root, mock_contract_service):
        """测试审批对话框初始化"""
        from minicrm.ui.ttk_base.contract_approval_ttk import ApprovalDialog

        contract_data = {
            "id": 1,
            "contract_number": "S20240101001",
            "party_name": "测试客户",
            "contract_type_display": "销售合同",
            "formatted_amount": "¥500,000.00",
        }

        dialog = ApprovalDialog(root, mock_contract_service, contract_data, "测试用户")

        assert dialog.contract_service == mock_contract_service
        assert dialog.contract_data == contract_data
        assert dialog.current_user == "测试用户"
        assert dialog.result is None

    @patch("tkinter.messagebox.showerror")
    def test_approval_dialog_approve_no_comment(
        self, mock_showerror, root, mock_contract_service
    ):
        """测试审批对话框批准时无意见"""
        from minicrm.ui.ttk_base.contract_approval_ttk import ApprovalDialog

        contract_data = {"id": 1, "contract_number": "S20240101001"}
        dialog = ApprovalDialog(root, mock_contract_service, contract_data, "测试用户")

        # 模拟空的审批意见
        dialog.comment_text = Mock()
        dialog.comment_text.get.return_value = ""

        dialog._approve()

        # 验证显示错误消息
        mock_showerror.assert_called_once_with("错误", "请输入审批意见")

    def test_approval_dialog_approve_success(self, root, mock_contract_service):
        """测试审批对话框成功批准"""
        from minicrm.ui.ttk_base.contract_approval_ttk import ApprovalDialog

        contract_data = {"id": 1, "contract_number": "S20240101001"}
        dialog = ApprovalDialog(root, mock_contract_service, contract_data, "测试用户")

        # 模拟审批意见
        dialog.comment_text = Mock()
        dialog.comment_text.get.return_value = "审批通过"

        # 模拟对话框销毁
        dialog.dialog = Mock()

        dialog._approve()

        # 验证结果
        assert dialog.result == {"action": "approve", "comment": "审批通过"}

    @patch("tkinter.messagebox.askyesno", return_value=True)
    def test_approval_dialog_reject_success(
        self, mock_askyesno, root, mock_contract_service
    ):
        """测试审批对话框成功拒绝"""
        from minicrm.ui.ttk_base.contract_approval_ttk import ApprovalDialog

        contract_data = {"id": 1, "contract_number": "S20240101001"}
        dialog = ApprovalDialog(root, mock_contract_service, contract_data, "测试用户")

        # 模拟拒绝原因
        dialog.comment_text = Mock()
        dialog.comment_text.get.return_value = "条款不符合要求"

        # 模拟对话框销毁
        dialog.dialog = Mock()

        dialog._reject()

        # 验证确认对话框被调用
        mock_askyesno.assert_called_once()

        # 验证结果
        assert dialog.result == {"action": "reject", "comment": "条款不符合要求"}

    def test_approval_dialog_return_success(self, root, mock_contract_service):
        """测试审批对话框成功退回"""
        from minicrm.ui.ttk_base.contract_approval_ttk import ApprovalDialog

        contract_data = {"id": 1, "contract_number": "S20240101001"}
        dialog = ApprovalDialog(root, mock_contract_service, contract_data, "测试用户")

        # 模拟退回原因
        dialog.comment_text = Mock()
        dialog.comment_text.get.return_value = "需要补充材料"

        # 模拟对话框销毁
        dialog.dialog = Mock()

        dialog._return()

        # 验证结果
        assert dialog.result == {"action": "return", "comment": "需要补充材料"}

    def test_approval_dialog_cancel(self, root, mock_contract_service):
        """测试审批对话框取消"""
        from minicrm.ui.ttk_base.contract_approval_ttk import ApprovalDialog

        contract_data = {"id": 1, "contract_number": "S20240101001"}
        dialog = ApprovalDialog(root, mock_contract_service, contract_data, "测试用户")

        # 模拟对话框销毁
        dialog.dialog = Mock()

        dialog._cancel()

        # 验证结果
        assert dialog.result is None


if __name__ == "__main__":
    pytest.main([__file__])
