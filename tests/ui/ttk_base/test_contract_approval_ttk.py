"""MiniCRM TTK合同审批流程组件测试

测试ContractApprovalTTK组件的功能，包括：
- 组件初始化和UI创建
- 审批数据加载和显示
- 审批操作（批准、拒绝、退回、委托）
- 批量审批功能
- 审批历史记录
- 事件处理和回调

作者: MiniCRM开发团队
"""

from datetime import datetime, timedelta
import unittest
from unittest.mock import Mock, patch


# 检查是否有GUI环境
try:
    import tkinter as tk

    GUI_AVAILABLE = True
except Exception:
    GUI_AVAILABLE = False

from minicrm.models.contract import Contract, ContractStatus, ContractType
from minicrm.services.contract_service import ContractService
from minicrm.ui.ttk_base.contract_approval_ttk import (
    ApprovalAction,
    ContractApprovalDialog,
    ContractApprovalTTK,
)


class TestContractApprovalTTK(unittest.TestCase):
    """合同审批流程组件测试类"""

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

        # 创建测试合同数据
        self.test_contracts = [
            Contract(
                id=1,
                contract_number="S20240101001",
                party_name="测试客户A",
                contract_type=ContractType.SALES,
                contract_status=ContractStatus.PENDING,
                contract_amount=500000,
                created_at=datetime.now() - timedelta(days=2),
                terms_and_conditions="标准销售合同条款",
            ),
            Contract(
                id=2,
                contract_number="P20240101002",
                party_name="测试供应商B",
                contract_type=ContractType.PURCHASE,
                contract_status=ContractStatus.PENDING,
                contract_amount=1200000,
                created_at=datetime.now() - timedelta(days=8),
                terms_and_conditions="采购合同条款",
            ),
        ]

        # 配置模拟服务返回值
        self.mock_service.list_all.return_value = self.test_contracts

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_component_initialization(self):
        """测试组件初始化"""
        # 创建组件
        component = ContractApprovalTTK(
            self.root, self.mock_service, current_user="测试用户"
        )

        # 验证组件创建成功
        self.assertIsNotNone(component)
        self.assertEqual(component._contract_service, self.mock_service)
        self.assertEqual(component._current_user, "测试用户")
        self.assertIsNotNone(component._approval_tree)
        self.assertIsNotNone(component._history_tree)
        self.assertIsNotNone(component._detail_frame)

        # 验证服务调用
        self.mock_service.list_all.assert_called_once()

    def test_approval_data_loading(self):
        """测试审批数据加载"""
        component = ContractApprovalTTK(self.root, self.mock_service)

        # 验证数据加载
        self.assertEqual(len(component._pending_approvals), 2)
        self.assertEqual(
            component._pending_approvals[0]["contract_number"], "S20240101001"
        )
        self.assertEqual(
            component._pending_approvals[1]["contract_number"], "P20240101002"
        )

        # 验证树形视图中的项目数量
        tree_items = component._approval_tree.get_children()
        self.assertEqual(len(tree_items), 2)

    def test_priority_calculation(self):
        """测试优先级计算"""
        component = ContractApprovalTTK(self.root, self.mock_service)

        # 测试高优先级（超过7天或金额超过100万）
        approval_data = component._pending_approvals[1]  # 8天前，120万
        days_pending = component._calculate_pending_days(
            approval_data.get("created_at", "")
        )
        priority = component._determine_priority(approval_data, days_pending)
        self.assertEqual(priority, "高")

        # 测试中优先级
        approval_data = component._pending_approvals[0]  # 2天前，50万
        days_pending = component._calculate_pending_days(
            approval_data.get("created_at", "")
        )
        priority = component._determine_priority(approval_data, days_pending)
        self.assertEqual(priority, "中")

    def test_approval_selection(self):
        """测试审批选择功能"""
        component = ContractApprovalTTK(self.root, self.mock_service)

        # 模拟选择第一个审批项目
        tree_items = component._approval_tree.get_children()
        if tree_items:
            component._approval_tree.selection_set(tree_items[0])
            component._on_approval_selected()

            # 验证选择结果
            self.assertIsNotNone(component._selected_approval)
            self.assertEqual(
                component._selected_approval["contract_number"], "S20240101001"
            )

    def test_approve_contract(self):
        """测试批准合同功能"""
        component = ContractApprovalTTK(self.root, self.mock_service)

        # 选择要批准的合同
        component._selected_approval = component._pending_approvals[0]

        # 配置模拟服务
        updated_contract = Contract(
            id=1,
            contract_number="S20240101001",
            contract_status=ContractStatus.APPROVED,
        )
        self.mock_service.update_contract_status.return_value = updated_contract

        # 模拟审批意见输入
        with patch("tkinter.simpledialog.askstring", return_value="审批通过"):
            with patch("tkinter.messagebox.showinfo"):
                with patch.object(component, "_refresh_approvals"):
                    with patch.object(component, "_record_approval_action"):
                        component._approve_contract()

        # 验证服务调用
        self.mock_service.update_contract_status.assert_called_once_with(
            1, ContractStatus.APPROVED, "审批通过: 审批通过"
        )

    def test_reject_contract(self):
        """测试拒绝合同功能"""
        component = ContractApprovalTTK(self.root, self.mock_service)

        # 选择要拒绝的合同
        component._selected_approval = component._pending_approvals[0]

        # 配置模拟服务
        updated_contract = Contract(
            id=1, contract_number="S20240101001", contract_status=ContractStatus.DRAFT
        )
        self.mock_service.update_contract_status.return_value = updated_contract

        # 模拟拒绝操作
        with patch("tkinter.simpledialog.askstring", return_value="条款不符合要求"):
            with patch("tkinter.messagebox.askyesno", return_value=True):
                with patch("tkinter.messagebox.showinfo"):
                    with patch.object(component, "_refresh_approvals"):
                        with patch.object(component, "_record_approval_action"):
                            component._reject_contract()

        # 验证服务调用
        self.mock_service.update_contract_status.assert_called_once_with(
            1, ContractStatus.DRAFT, "审批拒绝: 条款不符合要求"
        )

    def test_return_contract(self):
        """测试退回合同功能"""
        component = ContractApprovalTTK(self.root, self.mock_service)

        # 选择要退回的合同
        component._selected_approval = component._pending_approvals[0]

        # 配置模拟服务
        updated_contract = Contract(
            id=1, contract_number="S20240101001", contract_status=ContractStatus.DRAFT
        )
        self.mock_service.update_contract_status.return_value = updated_contract

        # 模拟退回操作
        with patch("tkinter.simpledialog.askstring", return_value="需要补充材料"):
            with patch("tkinter.messagebox.showinfo"):
                with patch.object(component, "_refresh_approvals"):
                    with patch.object(component, "_record_approval_action"):
                        component._return_contract()

        # 验证服务调用
        self.mock_service.update_contract_status.assert_called_once_with(
            1, ContractStatus.DRAFT, "审批退回: 需要补充材料"
        )

    def test_delegate_approval(self):
        """测试委托审批功能"""
        component = ContractApprovalTTK(self.root, self.mock_service)

        # 选择要委托的合同
        component._selected_approval = component._pending_approvals[0]

        # 设置回调函数
        status_changed_callback = Mock()
        component.on_approval_status_changed = status_changed_callback

        # 模拟委托操作
        with patch(
            "tkinter.simpledialog.askstring", side_effect=["李经理", "出差委托"]
        ):
            with patch("tkinter.messagebox.showinfo"):
                with patch.object(component, "_record_approval_action"):
                    component._delegate_approval()

        # 验证回调调用
        status_changed_callback.assert_called_once()
        call_args = status_changed_callback.call_args[0][0]
        self.assertEqual(call_args["action"], ApprovalAction.DELEGATE.value)
        self.assertEqual(call_args["delegate_to"], "李经理")

    def test_batch_approve(self):
        """测试批量批准功能"""
        component = ContractApprovalTTK(self.root, self.mock_service)

        # 模拟选择多个项目
        tree_items = component._approval_tree.get_children()
        component._approval_tree.selection_set(tree_items)

        # 配置模拟服务
        updated_contract = Contract(id=1, contract_status=ContractStatus.APPROVED)
        self.mock_service.update_contract_status.return_value = updated_contract

        # 模拟批量批准操作
        with patch("tkinter.messagebox.askyesno", return_value=True):
            with patch("tkinter.simpledialog.askstring", return_value="批量审批通过"):
                with patch("tkinter.messagebox.showinfo"):
                    with patch.object(component, "_refresh_approvals"):
                        with patch.object(component, "_record_approval_action"):
                            component._batch_approve()

        # 验证服务调用次数（应该调用2次，每个合同一次）
        self.assertEqual(self.mock_service.update_contract_status.call_count, 2)

    def test_filter_functionality(self):
        """测试筛选功能"""
        component = ContractApprovalTTK(self.root, self.mock_service)

        # 测试合同类型筛选
        component._type_filter_var.set("销售合同")
        filtered = component._apply_filters(component._pending_approvals)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["contract_type_display"], "销售合同")

        # 测试优先级筛选
        component._type_filter_var.set("全部")
        component._priority_filter_var.set("高")
        filtered = component._apply_filters(component._pending_approvals)
        # 应该只有一个高优先级的合同（8天前，120万）
        self.assertEqual(len(filtered), 1)

    def test_stats_update(self):
        """测试统计信息更新"""
        component = ContractApprovalTTK(self.root, self.mock_service)

        # 验证统计信息
        stats_text = component._stats_label.cget("text")
        self.assertIn("待审批: 2 个", stats_text)
        self.assertIn("高优先级: 1 个", stats_text)

    def test_button_states_update(self):
        """测试按钮状态更新"""
        component = ContractApprovalTTK(self.root, self.mock_service)

        # 测试无选择状态
        component._selected_approval = None
        component._approval_tree.selection_set([])
        component._update_button_states()

        self.assertEqual(component._approve_btn.cget("state"), "disabled")
        self.assertEqual(component._reject_btn.cget("state"), "disabled")
        self.assertEqual(component._return_btn.cget("state"), "disabled")
        self.assertEqual(component._batch_approve_btn.cget("state"), "disabled")

        # 测试单选状态
        tree_items = component._approval_tree.get_children()
        if tree_items:
            component._approval_tree.selection_set([tree_items[0]])
            component._selected_approval = component._pending_approvals[0]
            component._update_button_states()

            self.assertEqual(component._approve_btn.cget("state"), "normal")
            self.assertEqual(component._reject_btn.cget("state"), "normal")
            self.assertEqual(component._return_btn.cget("state"), "normal")
            self.assertEqual(component._batch_approve_btn.cget("state"), "disabled")

        # 测试多选状态
        if len(tree_items) > 1:
            component._approval_tree.selection_set(tree_items)
            component._update_button_states()

            self.assertEqual(component._batch_approve_btn.cget("state"), "normal")

    def test_event_callbacks(self):
        """测试事件回调"""
        component = ContractApprovalTTK(self.root, self.mock_service)

        # 设置回调函数
        approval_completed_callback = Mock()
        component.on_approval_completed = approval_completed_callback

        # 选择合同并批准
        component._selected_approval = component._pending_approvals[0]

        # 配置模拟服务
        updated_contract = Contract(id=1, contract_status=ContractStatus.APPROVED)
        self.mock_service.update_contract_status.return_value = updated_contract

        # 模拟批准操作
        with patch("tkinter.simpledialog.askstring", return_value="测试批准"):
            with patch("tkinter.messagebox.showinfo"):
                with patch.object(component, "_refresh_approvals"):
                    with patch.object(component, "_record_approval_action"):
                        component._approve_contract()

        # 验证回调调用
        approval_completed_callback.assert_called_once()
        call_args = approval_completed_callback.call_args[0][0]
        self.assertEqual(call_args["action"], ApprovalAction.APPROVE.value)
        self.assertEqual(call_args["comment"], "测试批准")

    def test_cleanup(self):
        """测试资源清理"""
        component = ContractApprovalTTK(self.root, self.mock_service)

        # 设置一些数据
        component._selected_approval = component._pending_approvals[0]

        # 执行清理
        component.cleanup()

        # 验证清理结果
        self.assertEqual(len(component._pending_approvals), 0)
        self.assertEqual(len(component._approval_history), 0)
        self.assertIsNone(component._selected_approval)


class TestContractApprovalDialog(unittest.TestCase):
    """合同审批对话框测试类"""

    def setUp(self):
        """测试准备"""
        if not GUI_AVAILABLE:
            self.skipTest("GUI环境不可用")

        try:
            self.root = tk.Tk()
            self.root.withdraw()  # 隐藏测试窗口
        except Exception as e:
            self.skipTest(f"无法创建Tkinter窗口: {e}")

        # 创建测试合同数据
        self.contract_data = {
            "id": 1,
            "contract_number": "S20240101001",
            "party_name": "测试客户",
            "contract_type_display": "销售合同",
            "formatted_amount": "¥500,000.00",
            "status_display": "待审批",
        }

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_dialog_initialization(self):
        """测试对话框初始化"""
        dialog = ContractApprovalDialog(self.root, self.contract_data, "测试用户")

        # 验证初始化
        self.assertEqual(dialog.contract_data, self.contract_data)
        self.assertEqual(dialog.current_user, "测试用户")
        self.assertIsNone(dialog.result)

    def test_approve_action(self):
        """测试批准操作"""
        dialog = ContractApprovalDialog(self.root, self.contract_data, "测试用户")

        # 创建对话框UI组件（简化版）
        dialog.comment_text = tk.Text(self.root)
        dialog.comment_text.insert("1.0", "审批通过")
        dialog.dialog = Mock()

        # 执行批准操作
        dialog._approve()

        # 验证结果
        self.assertIsNotNone(dialog.result)
        self.assertEqual(dialog.result["action"], "approve")
        self.assertEqual(dialog.result["comment"], "审批通过")

    def test_reject_action(self):
        """测试拒绝操作"""
        dialog = ContractApprovalDialog(self.root, self.contract_data, "测试用户")

        # 创建对话框UI组件（简化版）
        dialog.comment_text = tk.Text(self.root)
        dialog.comment_text.insert("1.0", "条款不符合要求")
        dialog.dialog = Mock()

        # 模拟确认对话框
        with patch("tkinter.messagebox.askyesno", return_value=True):
            dialog._reject()

        # 验证结果
        self.assertIsNotNone(dialog.result)
        self.assertEqual(dialog.result["action"], "reject")
        self.assertEqual(dialog.result["comment"], "条款不符合要求")

    def test_return_action(self):
        """测试退回操作"""
        dialog = ContractApprovalDialog(self.root, self.contract_data, "测试用户")

        # 创建对话框UI组件（简化版）
        dialog.comment_text = tk.Text(self.root)
        dialog.comment_text.insert("1.0", "需要补充材料")
        dialog.dialog = Mock()

        # 执行退回操作
        dialog._return()

        # 验证结果
        self.assertIsNotNone(dialog.result)
        self.assertEqual(dialog.result["action"], "return")
        self.assertEqual(dialog.result["comment"], "需要补充材料")

    @patch("tkinter.messagebox.showerror")
    def test_validation_error(self, mock_showerror):
        """测试验证错误"""
        dialog = ContractApprovalDialog(self.root, self.contract_data, "测试用户")

        # 创建对话框UI组件（简化版）
        dialog.comment_text = tk.Text(self.root)
        # 不输入审批意见

        # 尝试批准（应该失败）
        dialog._approve()

        # 验证错误提示
        mock_showerror.assert_called_once_with("错误", "请输入审批意见")
        self.assertIsNone(dialog.result)

    def test_cancel_action(self):
        """测试取消操作"""
        dialog = ContractApprovalDialog(self.root, self.contract_data, "测试用户")

        dialog.dialog = Mock()

        # 执行取消操作
        dialog._cancel()

        # 验证结果
        self.assertIsNone(dialog.result)


if __name__ == "__main__":
    unittest.main()
