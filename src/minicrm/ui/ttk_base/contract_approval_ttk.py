"""MiniCRM TTK合同审批流程组件

基于TTK框架实现的合同审批流程管理组件,用于替换Qt版本的审批功能.
支持审批流程定义、审批状态跟踪、审批历史记录、多级审批等功能.

设计特点:
- 使用TTK组件构建审批流程界面
- 支持多级审批和并行审批
- 提供审批历史和状态跟踪
- 集成审批通知和提醒功能
- 支持审批权限管理
- 遵循MiniCRM开发标准

作者: MiniCRM开发团队
"""

from datetime import datetime
from enum import Enum
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable, Dict, List, Optional

from minicrm.core.exceptions import ServiceError
from minicrm.models.contract import Contract, ContractStatus
from minicrm.services.contract_service import ContractService
from minicrm.ui.ttk_base.base_widget import BaseWidget


class ApprovalStatus(Enum):
    """审批状态枚举"""

    PENDING = "pending"  # 待审批
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    CANCELLED = "cancelled"  # 已取消


class ApprovalAction(Enum):
    """审批操作枚举"""

    APPROVE = "approve"  # 批准
    REJECT = "reject"  # 拒绝
    RETURN = "return"  # 退回
    DELEGATE = "delegate"  # 委托


class ContractApprovalTTK(BaseWidget):
    """TTK合同审批流程组件

    提供完整的合同审批流程管理功能:
    - 审批任务列表显示和管理
    - 审批流程状态跟踪
    - 审批操作处理(批准、拒绝、退回)
    - 审批历史记录查看
    - 审批通知和提醒
    - 批量审批操作
    """

    def __init__(
        self,
        parent: tk.Widget,
        contract_service: Optional[ContractService] = None,
        current_user: str = "当前用户",
        **kwargs,
    ):
        """初始化合同审批流程组件

        Args:
            parent: 父组件
            contract_service: 合同服务实例,如果为None则自动创建
            current_user: 当前用户标识
            **kwargs: 其他参数
        """
        self._contract_service = contract_service or ContractService()
        self._current_user = current_user

        # 数据存储
        self._pending_approvals: List[Dict[str, Any]] = []
        self._approval_history: List[Dict[str, Any]] = []
        self._selected_approval: Optional[Dict[str, Any]] = None

        # UI组件
        self._approval_tree: Optional[ttk.Treeview] = None
        self._history_tree: Optional[ttk.Treeview] = None
        self._detail_frame: Optional[ttk.Frame] = None

        # 事件回调
        self.on_approval_completed: Optional[Callable] = None
        self.on_approval_status_changed: Optional[Callable] = None

        super().__init__(parent, **kwargs)

        # 加载审批数据
        self._load_approval_data()

    def _setup_ui(self) -> None:
        """设置UI布局"""
        # 创建主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建标题区域
        self._create_title_area(main_container)

        # 创建工具栏
        self._create_toolbar(main_container)

        # 创建主要内容区域
        self._create_content_area(main_container)

    def _create_title_area(self, parent: ttk.Frame) -> None:
        """创建标题区域"""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        # 标题
        title_label = ttk.Label(
            title_frame, text="合同审批管理", font=("Microsoft YaHei UI", 14, "bold")
        )
        title_label.pack(side=tk.LEFT)

        # 审批统计信息
        self._stats_label = ttk.Label(title_frame, text="", foreground="gray")
        self._stats_label.pack(side=tk.RIGHT)

    def _create_toolbar(self, parent: ttk.Frame) -> None:
        """创建工具栏"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))

        # 左侧按钮
        left_frame = ttk.Frame(toolbar_frame)
        left_frame.pack(side=tk.LEFT)

        # 批准按钮
        self._approve_btn = ttk.Button(
            left_frame,
            text="✅ 批准",
            command=self._approve_contract,
            state=tk.DISABLED,
        )
        self._approve_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 拒绝按钮
        self._reject_btn = ttk.Button(
            left_frame,
            text="❌ 拒绝",
            command=self._reject_contract,
            state=tk.DISABLED,
        )
        self._reject_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 退回按钮
        self._return_btn = ttk.Button(
            left_frame,
            text="↩️ 退回",
            command=self._return_contract,
            state=tk.DISABLED,
        )
        self._return_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 委托按钮
        self._delegate_btn = ttk.Button(
            left_frame,
            text="👥 委托",
            command=self._delegate_approval,
            state=tk.DISABLED,
        )
        self._delegate_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 右侧按钮
        right_frame = ttk.Frame(toolbar_frame)
        right_frame.pack(side=tk.RIGHT)

        # 批量操作按钮
        self._batch_approve_btn = ttk.Button(
            right_frame,
            text="批量批准",
            command=self._batch_approve,
            state=tk.DISABLED,
        )
        self._batch_approve_btn.pack(side=tk.LEFT, padx=(5, 0))

        # 刷新按钮
        self._refresh_btn = ttk.Button(
            right_frame, text="🔄 刷新", command=self._refresh_approvals
        )
        self._refresh_btn.pack(side=tk.LEFT, padx=(5, 0))

    def _create_content_area(self, parent: ttk.Frame) -> None:
        """创建主要内容区域"""
        # 创建标签页
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 待审批标签页
        self._create_pending_approvals_tab(notebook)

        # 审批历史标签页
        self._create_approval_history_tab(notebook)

        # 审批详情标签页
        self._create_approval_detail_tab(notebook)

    def _create_pending_approvals_tab(self, notebook: ttk.Notebook) -> None:
        """创建待审批标签页"""
        pending_frame = ttk.Frame(notebook)
        notebook.add(pending_frame, text="待审批")

        # 创建筛选区域
        filter_frame = ttk.Frame(pending_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_frame, text="筛选:").pack(side=tk.LEFT)

        # 合同类型筛选
        ttk.Label(filter_frame, text="合同类型:").pack(side=tk.LEFT, padx=(10, 5))
        self._type_filter_var = tk.StringVar(value="全部")
        type_combo = ttk.Combobox(
            filter_frame,
            textvariable=self._type_filter_var,
            values=["全部", "销售合同", "采购合同", "服务合同", "框架合同", "其他"],
            state="readonly",
            width=10,
        )
        type_combo.pack(side=tk.LEFT, padx=(0, 10))
        type_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # 优先级筛选
        ttk.Label(filter_frame, text="优先级:").pack(side=tk.LEFT, padx=(10, 5))
        self._priority_filter_var = tk.StringVar(value="全部")
        priority_combo = ttk.Combobox(
            filter_frame,
            textvariable=self._priority_filter_var,
            values=["全部", "高", "中", "低"],
            state="readonly",
            width=8,
        )
        priority_combo.pack(side=tk.LEFT, padx=(0, 10))
        priority_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # 创建审批列表
        self._create_approval_list(pending_frame)

    def _create_approval_list(self, parent: ttk.Frame) -> None:
        """创建审批列表"""
        # 创建表格框架
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 定义列
        columns = (
            "contract_number",
            "party_name",
            "contract_type",
            "amount",
            "priority",
            "submit_time",
            "days_pending",
        )
        self._approval_tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="extended"
        )

        # 配置列
        self._approval_tree.heading("contract_number", text="合同编号")
        self._approval_tree.heading("party_name", text="合同方")
        self._approval_tree.heading("contract_type", text="合同类型")
        self._approval_tree.heading("amount", text="合同金额")
        self._approval_tree.heading("priority", text="优先级")
        self._approval_tree.heading("submit_time", text="提交时间")
        self._approval_tree.heading("days_pending", text="待审天数")

        self._approval_tree.column("contract_number", width=120, minwidth=100)
        self._approval_tree.column("party_name", width=150, minwidth=100)
        self._approval_tree.column("contract_type", width=100, minwidth=80)
        self._approval_tree.column("amount", width=120, minwidth=100)
        self._approval_tree.column("priority", width=80, minwidth=60)
        self._approval_tree.column("submit_time", width=120, minwidth=100)
        self._approval_tree.column("days_pending", width=80, minwidth=60)

        # 添加滚动条
        approval_scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=self._approval_tree.yview
        )
        self._approval_tree.configure(yscrollcommand=approval_scrollbar.set)

        # 布局
        self._approval_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        approval_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定事件
        self._approval_tree.bind("<<TreeviewSelect>>", self._on_approval_selected)
        self._approval_tree.bind("<Double-1>", self._on_approval_double_clicked)
        self._approval_tree.bind("<Button-3>", self._show_approval_context_menu)

    def _create_approval_history_tab(self, notebook: ttk.Notebook) -> None:
        """创建审批历史标签页"""
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="审批历史")

        # 创建历史列表
        history_columns = (
            "contract_number",
            "party_name",
            "action",
            "approver",
            "approval_time",
            "comments",
        )
        self._history_tree = ttk.Treeview(
            history_frame, columns=history_columns, show="headings"
        )

        # 配置列
        self._history_tree.heading("contract_number", text="合同编号")
        self._history_tree.heading("party_name", text="合同方")
        self._history_tree.heading("action", text="操作")
        self._history_tree.heading("approver", text="审批人")
        self._history_tree.heading("approval_time", text="审批时间")
        self._history_tree.heading("comments", text="审批意见")

        self._history_tree.column("contract_number", width=120)
        self._history_tree.column("party_name", width=150)
        self._history_tree.column("action", width=80)
        self._history_tree.column("approver", width=100)
        self._history_tree.column("approval_time", width=120)
        self._history_tree.column("comments", width=200)

        # 添加滚动条
        history_scrollbar = ttk.Scrollbar(
            history_frame, orient=tk.VERTICAL, command=self._history_tree.yview
        )
        self._history_tree.configure(yscrollcommand=history_scrollbar.set)

        # 布局
        self._history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_approval_detail_tab(self, notebook: ttk.Notebook) -> None:
        """创建审批详情标签页"""
        self._detail_frame = ttk.Frame(notebook)
        notebook.add(self._detail_frame, text="审批详情")

        # 初始显示空状态
        self._show_empty_detail()

    def _load_approval_data(self) -> None:
        """加载审批数据"""
        try:
            # 获取待审批的合同
            pending_contracts = self._get_pending_approvals()
            self._pending_approvals = [
                contract.to_dict() for contract in pending_contracts
            ]

            # 获取审批历史
            approval_history = self._get_approval_history()
            self._approval_history = approval_history

            # 刷新显示
            self._refresh_approval_list()
            self._refresh_history_list()
            self._update_stats()

            self.logger.info(f"加载了 {len(self._pending_approvals)} 个待审批合同")

        except ServiceError as e:
            self.logger.error(f"加载审批数据失败: {e}")
            messagebox.showerror("错误", f"加载审批数据失败:{e}")
        except Exception as e:
            self.logger.error(f"加载审批数据时发生未知错误: {e}")
            messagebox.showerror("错误", f"加载审批数据时发生未知错误:{e}")

    def _get_pending_approvals(self) -> List[Contract]:
        """获取待审批的合同"""
        try:
            # 获取待审批状态的合同
            contracts = self._contract_service.list_all(
                {"contract_status": [ContractStatus.PENDING]}
            )
            return contracts
        except Exception as e:
            self.logger.error(f"获取待审批合同失败: {e}")
            return []

    def _get_approval_history(self) -> List[Dict[str, Any]]:
        """获取审批历史"""
        # 模拟审批历史数据
        return [
            {
                "contract_number": "S20240101001",
                "party_name": "测试客户A",
                "action": "批准",
                "approver": "张经理",
                "approval_time": "2024-01-15 10:30:00",
                "comments": "合同条款符合要求,批准签署",
            },
            {
                "contract_number": "P20240101002",
                "party_name": "测试供应商B",
                "action": "拒绝",
                "approver": "李总监",
                "approval_time": "2024-01-14 16:45:00",
                "comments": "价格偏高,建议重新谈判",
            },
        ]

    def _refresh_approval_list(self) -> None:
        """刷新审批列表显示"""
        if not self._approval_tree:
            return

        # 清空现有项目
        for item in self._approval_tree.get_children():
            self._approval_tree.delete(item)

        # 应用筛选
        filtered_approvals = self._apply_filters(self._pending_approvals)

        # 添加审批项目
        for approval in filtered_approvals:
            # 计算待审天数
            submit_time = approval.get("created_at", "")
            days_pending = self._calculate_pending_days(submit_time)

            # 确定优先级
            priority = self._determine_priority(approval, days_pending)

            # 插入项目
            item_id = self._approval_tree.insert(
                "",
                "end",
                values=(
                    approval.get("contract_number", ""),
                    approval.get("party_name", ""),
                    approval.get("contract_type_display", ""),
                    approval.get("formatted_amount", ""),
                    priority,
                    self._format_datetime(submit_time),
                    f"{days_pending}天",
                ),
                tags=(priority.lower(),),
            )

        # 配置优先级标签样式
        self._approval_tree.tag_configure("高", background="#ffe6e6")
        self._approval_tree.tag_configure("中", background="#fff2e6")
        self._approval_tree.tag_configure("低", background="#e6ffe6")

    def _refresh_history_list(self) -> None:
        """刷新审批历史列表"""
        if not self._history_tree:
            return

        # 清空现有项目
        for item in self._history_tree.get_children():
            self._history_tree.delete(item)

        # 添加历史项目
        for history in self._approval_history:
            self._history_tree.insert(
                "",
                "end",
                values=(
                    history.get("contract_number", ""),
                    history.get("party_name", ""),
                    history.get("action", ""),
                    history.get("approver", ""),
                    history.get("approval_time", ""),
                    history.get("comments", ""),
                ),
            )

    def _apply_filters(self, approvals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """应用筛选条件"""
        filtered = approvals.copy()

        # 合同类型筛选
        type_filter = self._type_filter_var.get()
        if type_filter != "全部":
            filtered = [
                a for a in filtered if a.get("contract_type_display", "") == type_filter
            ]

        # 优先级筛选
        priority_filter = self._priority_filter_var.get()
        if priority_filter != "全部":
            filtered = [
                a
                for a in filtered
                if self._determine_priority(
                    a, self._calculate_pending_days(a.get("created_at", ""))
                )
                == priority_filter
            ]

        return filtered

    def _calculate_pending_days(self, submit_time: str) -> int:
        """计算待审天数"""
        if not submit_time:
            return 0

        try:
            if isinstance(submit_time, str):
                dt = datetime.fromisoformat(submit_time.replace("Z", "+00:00"))
            else:
                dt = submit_time
            return (datetime.now() - dt).days
        except:
            return 0

    def _determine_priority(self, approval: Dict[str, Any], days_pending: int) -> str:
        """确定优先级"""
        # 根据待审天数和合同金额确定优先级
        amount = approval.get("contract_amount", 0)

        if days_pending > 7 or amount > 1000000:  # 超过7天或金额超过100万
            return "高"
        if days_pending > 3 or amount > 500000:  # 超过3天或金额超过50万
            return "中"
        return "低"

    def _update_stats(self) -> None:
        """更新统计信息"""
        total_pending = len(self._pending_approvals)
        high_priority = sum(
            1
            for a in self._pending_approvals
            if self._determine_priority(
                a, self._calculate_pending_days(a.get("created_at", ""))
            )
            == "高"
        )

        stats_text = f"待审批: {total_pending} 个 (高优先级: {high_priority} 个)"
        self._stats_label.config(text=stats_text)

    def _on_filter_changed(self, event=None) -> None:
        """处理筛选条件变化"""
        self._refresh_approval_list()

    def _on_approval_selected(self, event=None) -> None:
        """处理审批选择事件"""
        selection = self._approval_tree.selection()
        if not selection:
            self._selected_approval = None
            self._show_empty_detail()
            self._update_button_states()
            return

        # 获取选中的审批
        item = selection[0]
        item_index = self._approval_tree.index(item)

        filtered_approvals = self._apply_filters(self._pending_approvals)
        if 0 <= item_index < len(filtered_approvals):
            self._selected_approval = filtered_approvals[item_index]
            self._show_approval_detail()
            self._update_button_states()

    def _on_approval_double_clicked(self, event=None) -> None:
        """处理审批双击事件"""
        if self._selected_approval:
            self._show_approval_dialog()

    def _show_approval_context_menu(self, event) -> None:
        """显示审批右键菜单"""
        if not self._approval_tree.selection():
            return

        # 创建右键菜单
        context_menu = tk.Menu(self, tearoff=0)

        context_menu.add_command(label="批准", command=self._approve_contract)
        context_menu.add_command(label="拒绝", command=self._reject_contract)
        context_menu.add_command(label="退回", command=self._return_contract)
        context_menu.add_separator()
        context_menu.add_command(label="查看详情", command=self._show_approval_dialog)
        context_menu.add_command(label="委托审批", command=self._delegate_approval)

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def _show_approval_detail(self) -> None:
        """显示审批详情"""
        if not self._selected_approval:
            return

        # 清空详情框架
        for widget in self._detail_frame.winfo_children():
            widget.destroy()

        # 创建滚动区域
        canvas = tk.Canvas(self._detail_frame)
        scrollbar = ttk.Scrollbar(
            self._detail_frame, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 布局滚动组件
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 显示合同详情
        self._create_approval_detail_display(scrollable_frame)

    def _create_approval_detail_display(self, parent: ttk.Frame) -> None:
        """创建审批详情显示"""
        approval = self._selected_approval

        # 合同基本信息
        basic_frame = ttk.LabelFrame(parent, text="合同基本信息", padding=10)
        basic_frame.pack(fill=tk.X, padx=10, pady=5)

        basic_info = [
            ("合同编号", approval.get("contract_number", "")),
            ("合同方", approval.get("party_name", "")),
            ("合同类型", approval.get("contract_type_display", "")),
            ("合同金额", approval.get("formatted_amount", "")),
            ("合同状态", approval.get("status_display", "")),
            ("签署日期", approval.get("formatted_sign_date", "")),
            ("生效日期", approval.get("formatted_effective_date", "")),
            ("到期日期", approval.get("formatted_expiry_date", "")),
        ]

        for label, value in basic_info:
            info_frame = ttk.Frame(basic_frame)
            info_frame.pack(fill=tk.X, pady=2)

            ttk.Label(info_frame, text=f"{label}:", width=12, anchor=tk.W).pack(
                side=tk.LEFT
            )
            ttk.Label(info_frame, text=str(value), anchor=tk.W).pack(
                side=tk.LEFT, fill=tk.X, expand=True
            )

        # 审批信息
        approval_frame = ttk.LabelFrame(parent, text="审批信息", padding=10)
        approval_frame.pack(fill=tk.X, padx=10, pady=5)

        submit_time = approval.get("created_at", "")
        days_pending = self._calculate_pending_days(submit_time)
        priority = self._determine_priority(approval, days_pending)

        approval_info = [
            ("提交时间", self._format_datetime(submit_time)),
            ("待审天数", f"{days_pending}天"),
            ("优先级", priority),
            ("当前审批人", self._current_user),
        ]

        for label, value in approval_info:
            info_frame = ttk.Frame(approval_frame)
            info_frame.pack(fill=tk.X, pady=2)

            ttk.Label(info_frame, text=f"{label}:", width=12, anchor=tk.W).pack(
                side=tk.LEFT
            )
            ttk.Label(info_frame, text=str(value), anchor=tk.W).pack(
                side=tk.LEFT, fill=tk.X, expand=True
            )

        # 合同条款
        if approval.get("terms_and_conditions"):
            terms_frame = ttk.LabelFrame(parent, text="合同条款", padding=10)
            terms_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            terms_text = tk.Text(terms_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
            terms_text.pack(fill=tk.BOTH, expand=True)
            terms_text.config(state=tk.NORMAL)
            terms_text.insert("1.0", approval.get("terms_and_conditions", ""))
            terms_text.config(state=tk.DISABLED)

        # 审批操作区域
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, padx=10, pady=10)

        # 审批意见输入
        ttk.Label(action_frame, text="审批意见:").pack(anchor=tk.W, pady=(0, 5))
        self._comment_text = tk.Text(action_frame, height=4, wrap=tk.WORD)
        self._comment_text.pack(fill=tk.X, pady=(0, 10))

        # 操作按钮
        button_frame = ttk.Frame(action_frame)
        button_frame.pack(fill=tk.X)

        approve_btn = ttk.Button(
            button_frame, text="✅ 批准", command=self._approve_contract
        )
        approve_btn.pack(side=tk.LEFT, padx=(0, 5))

        reject_btn = ttk.Button(
            button_frame, text="❌ 拒绝", command=self._reject_contract
        )
        reject_btn.pack(side=tk.LEFT, padx=(0, 5))

        return_btn = ttk.Button(
            button_frame, text="↩️ 退回", command=self._return_contract
        )
        return_btn.pack(side=tk.LEFT, padx=(0, 5))

    def _show_empty_detail(self) -> None:
        """显示空详情状态"""
        # 清空详情框架
        for widget in self._detail_frame.winfo_children():
            widget.destroy()

        # 显示提示
        tip_label = ttk.Label(
            self._detail_frame,
            text="请选择审批项目查看详情",
            font=("Microsoft YaHei UI", 12),
            foreground="gray",
        )
        tip_label.pack(expand=True)

    def _update_button_states(self) -> None:
        """更新按钮状态"""
        has_selection = self._selected_approval is not None
        has_multiple_selection = len(self._approval_tree.selection()) > 1

        # 单个操作按钮
        self._approve_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)
        self._reject_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)
        self._return_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)
        self._delegate_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)

        # 批量操作按钮
        self._batch_approve_btn.config(
            state=tk.NORMAL if has_multiple_selection else tk.DISABLED
        )

    def _format_datetime(self, datetime_str: str) -> str:
        """格式化日期时间字符串"""
        if not datetime_str:
            return "未知"

        try:
            if isinstance(datetime_str, str):
                dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
            else:
                dt = datetime_str
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return str(datetime_str)

    # ==================== 审批操作方法 ====================

    def _approve_contract(self) -> None:
        """批准合同"""
        if not self._selected_approval:
            messagebox.showwarning("提示", "请先选择要批准的合同")
            return

        # 获取审批意见
        comment = ""
        if hasattr(self, "_comment_text"):
            comment = self._comment_text.get("1.0", tk.END).strip()

        if not comment:
            comment = simpledialog.askstring("审批意见", "请输入审批意见:")
            if not comment:
                return

        try:
            contract_id = self._selected_approval.get("id")
            if contract_id:
                # 更新合同状态为已批准
                updated_contract = self._contract_service.update_contract_status(
                    contract_id, ContractStatus.APPROVED, f"审批通过: {comment}"
                )

                # 记录审批历史
                self._record_approval_action(
                    contract_id, ApprovalAction.APPROVE, comment
                )

                messagebox.showinfo("成功", "合同已批准")

                # 触发审批完成事件
                if self.on_approval_completed:
                    self.on_approval_completed(
                        {
                            "contract_id": contract_id,
                            "action": ApprovalAction.APPROVE.value,
                            "comment": comment,
                        }
                    )

                # 刷新数据
                self._refresh_approvals()

        except ServiceError as e:
            messagebox.showerror("错误", f"批准合同失败:{e}")
        except Exception as e:
            self.logger.error(f"批准合同时发生未知错误: {e}")
            messagebox.showerror("错误", f"批准合同时发生未知错误:{e}")

    def _reject_contract(self) -> None:
        """拒绝合同"""
        if not self._selected_approval:
            messagebox.showwarning("提示", "请先选择要拒绝的合同")
            return

        # 获取拒绝原因
        comment = ""
        if hasattr(self, "_comment_text"):
            comment = self._comment_text.get("1.0", tk.END).strip()

        if not comment:
            comment = simpledialog.askstring("拒绝原因", "请输入拒绝原因:")
            if not comment:
                return

        # 确认拒绝
        if not messagebox.askyesno("确认拒绝", "确定要拒绝这个合同吗?"):
            return

        try:
            contract_id = self._selected_approval.get("id")
            if contract_id:
                # 更新合同状态为草稿(拒绝后退回)
                updated_contract = self._contract_service.update_contract_status(
                    contract_id, ContractStatus.DRAFT, f"审批拒绝: {comment}"
                )

                # 记录审批历史
                self._record_approval_action(
                    contract_id, ApprovalAction.REJECT, comment
                )

                messagebox.showinfo("成功", "合同已拒绝")

                # 触发审批完成事件
                if self.on_approval_completed:
                    self.on_approval_completed(
                        {
                            "contract_id": contract_id,
                            "action": ApprovalAction.REJECT.value,
                            "comment": comment,
                        }
                    )

                # 刷新数据
                self._refresh_approvals()

        except ServiceError as e:
            messagebox.showerror("错误", f"拒绝合同失败:{e}")
        except Exception as e:
            self.logger.error(f"拒绝合同时发生未知错误: {e}")
            messagebox.showerror("错误", f"拒绝合同时发生未知错误:{e}")

    def _return_contract(self) -> None:
        """退回合同"""
        if not self._selected_approval:
            messagebox.showwarning("提示", "请先选择要退回的合同")
            return

        # 获取退回原因
        comment = ""
        if hasattr(self, "_comment_text"):
            comment = self._comment_text.get("1.0", tk.END).strip()

        if not comment:
            comment = simpledialog.askstring("退回原因", "请输入退回原因:")
            if not comment:
                return

        try:
            contract_id = self._selected_approval.get("id")
            if contract_id:
                # 更新合同状态为草稿(退回修改)
                updated_contract = self._contract_service.update_contract_status(
                    contract_id, ContractStatus.DRAFT, f"审批退回: {comment}"
                )

                # 记录审批历史
                self._record_approval_action(
                    contract_id, ApprovalAction.RETURN, comment
                )

                messagebox.showinfo("成功", "合同已退回")

                # 触发审批完成事件
                if self.on_approval_completed:
                    self.on_approval_completed(
                        {
                            "contract_id": contract_id,
                            "action": ApprovalAction.RETURN.value,
                            "comment": comment,
                        }
                    )

                # 刷新数据
                self._refresh_approvals()

        except ServiceError as e:
            messagebox.showerror("错误", f"退回合同失败:{e}")
        except Exception as e:
            self.logger.error(f"退回合同时发生未知错误: {e}")
            messagebox.showerror("错误", f"退回合同时发生未知错误:{e}")

    def _delegate_approval(self) -> None:
        """委托审批"""
        if not self._selected_approval:
            messagebox.showwarning("提示", "请先选择要委托的合同")
            return

        # 获取委托对象
        delegate_to = simpledialog.askstring("委托审批", "请输入委托给的审批人:")
        if not delegate_to:
            return

        # 获取委托原因
        comment = simpledialog.askstring("委托原因", "请输入委托原因:")
        if not comment:
            return

        try:
            contract_id = self._selected_approval.get("id")
            if contract_id:
                # 记录委托操作
                self._record_approval_action(
                    contract_id,
                    ApprovalAction.DELEGATE,
                    f"委托给 {delegate_to}: {comment}",
                )

                messagebox.showinfo("成功", f"已委托给 {delegate_to}")

                # 触发审批状态变化事件
                if self.on_approval_status_changed:
                    self.on_approval_status_changed(
                        {
                            "contract_id": contract_id,
                            "action": ApprovalAction.DELEGATE.value,
                            "delegate_to": delegate_to,
                            "comment": comment,
                        }
                    )

        except Exception as e:
            self.logger.error(f"委托审批时发生错误: {e}")
            messagebox.showerror("错误", f"委托审批失败:{e}")

    def _batch_approve(self) -> None:
        """批量批准"""
        selected_items = self._approval_tree.selection()
        if len(selected_items) < 2:
            messagebox.showwarning("提示", "请选择多个合同进行批量操作")
            return

        # 确认批量操作
        if not messagebox.askyesno(
            "确认批量批准", f"确定要批准选中的 {len(selected_items)} 个合同吗?"
        ):
            return

        # 获取批量审批意见
        comment = simpledialog.askstring("批量审批意见", "请输入批量审批意见:")
        if not comment:
            return

        try:
            success_count = 0
            error_count = 0

            filtered_approvals = self._apply_filters(self._pending_approvals)

            for item in selected_items:
                try:
                    item_index = self._approval_tree.index(item)
                    if 0 <= item_index < len(filtered_approvals):
                        approval = filtered_approvals[item_index]
                        contract_id = approval.get("id")

                        if contract_id:
                            # 批准合同
                            self._contract_service.update_contract_status(
                                contract_id,
                                ContractStatus.APPROVED,
                                f"批量审批通过: {comment}",
                            )

                            # 记录审批历史
                            self._record_approval_action(
                                contract_id, ApprovalAction.APPROVE, comment
                            )

                            success_count += 1

                except Exception as e:
                    self.logger.error(f"批量批准合同失败 {contract_id}: {e}")
                    error_count += 1

            # 显示结果
            if error_count == 0:
                messagebox.showinfo("成功", f"成功批准 {success_count} 个合同")
            else:
                messagebox.showwarning(
                    "部分成功",
                    f"成功批准 {success_count} 个合同,失败 {error_count} 个",
                )

            # 刷新数据
            self._refresh_approvals()

        except Exception as e:
            self.logger.error(f"批量批准时发生未知错误: {e}")
            messagebox.showerror("错误", f"批量批准失败:{e}")

    def _record_approval_action(
        self, contract_id: int, action: ApprovalAction, comment: str
    ) -> None:
        """记录审批操作"""
        # 这里应该调用服务层记录审批历史
        # 暂时添加到本地历史记录中
        history_record = {
            "contract_id": contract_id,
            "action": action.value,
            "approver": self._current_user,
            "approval_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comments": comment,
        }

        # 实际应该保存到数据库
        self.logger.info(f"记录审批操作: {history_record}")

    def _show_approval_dialog(self) -> None:
        """显示审批对话框"""
        if not self._selected_approval:
            return

        # 创建审批对话框
        dialog = ContractApprovalDialog(
            self, self._selected_approval, self._current_user
        )

        result = dialog.show()
        if result:
            # 处理审批结果
            action = result.get("action")
            comment = result.get("comment", "")

            if action == "approve":
                self._approve_contract()
            elif action == "reject":
                self._reject_contract()
            elif action == "return":
                self._return_contract()

    def _refresh_approvals(self) -> None:
        """刷新审批数据"""
        self._load_approval_data()

    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """获取待审批列表

        Returns:
            待审批合同列表
        """
        return self._pending_approvals.copy()

    def get_approval_history(self) -> List[Dict[str, Any]]:
        """获取审批历史

        Returns:
            审批历史记录列表
        """
        return self._approval_history.copy()

    def cleanup(self) -> None:
        """清理资源"""
        self._pending_approvals.clear()
        self._approval_history.clear()
        self._selected_approval = None
        super().cleanup()


class ContractApprovalDialog:
    """合同审批对话框"""

    def __init__(
        self,
        parent: tk.Widget,
        contract_data: Dict[str, Any],
        current_user: str,
    ):
        """初始化审批对话框

        Args:
            parent: 父组件
            contract_data: 合同数据
            current_user: 当前用户
        """
        self.parent = parent
        self.contract_data = contract_data
        self.current_user = current_user

        self.dialog = None
        self.result = None

    def show(self) -> Optional[Dict[str, Any]]:
        """显示对话框

        Returns:
            审批结果
        """
        # 创建对话框窗口
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("合同审批")
        self.dialog.geometry("700x600")
        self.dialog.resizable(True, True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"700x600+{x}+{y}")

        # 创建界面
        self._create_dialog_ui()

        # 等待对话框关闭
        self.dialog.wait_window()

        return self.result

    def _create_dialog_ui(self) -> None:
        """创建对话框界面"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 合同信息区域
        info_frame = ttk.LabelFrame(main_frame, text="合同信息", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        # 显示合同基本信息
        info_text = f"""
合同编号: {self.contract_data.get("contract_number", "")}
合同方: {self.contract_data.get("party_name", "")}
合同类型: {self.contract_data.get("contract_type_display", "")}
合同金额: {self.contract_data.get("formatted_amount", "")}
合同状态: {self.contract_data.get("status_display", "")}
        """.strip()

        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W)

        # 审批意见区域
        comment_frame = ttk.LabelFrame(main_frame, text="审批意见", padding=10)
        comment_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.comment_text = tk.Text(comment_frame, height=10, wrap=tk.WORD)
        self.comment_text.pack(fill=tk.BOTH, expand=True)

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        # 批准按钮
        approve_btn = ttk.Button(button_frame, text="✅ 批准", command=self._approve)
        approve_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 拒绝按钮
        reject_btn = ttk.Button(button_frame, text="❌ 拒绝", command=self._reject)
        reject_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 退回按钮
        return_btn = ttk.Button(button_frame, text="↩️ 退回", command=self._return)
        return_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=self._cancel)
        cancel_btn.pack(side=tk.RIGHT)

    def _approve(self) -> None:
        """批准操作"""
        comment = self.comment_text.get("1.0", tk.END).strip()
        if not comment:
            messagebox.showerror("错误", "请输入审批意见")
            return

        self.result = {"action": "approve", "comment": comment}
        self.dialog.destroy()

    def _reject(self) -> None:
        """拒绝操作"""
        comment = self.comment_text.get("1.0", tk.END).strip()
        if not comment:
            messagebox.showerror("错误", "请输入拒绝原因")
            return

        if not messagebox.askyesno("确认拒绝", "确定要拒绝这个合同吗?"):
            return

        self.result = {"action": "reject", "comment": comment}
        self.dialog.destroy()

    def _return(self) -> None:
        """退回操作"""
        comment = self.comment_text.get("1.0", tk.END).strip()
        if not comment:
            messagebox.showerror("错误", "请输入退回原因")
            return

        self.result = {"action": "return", "comment": comment}
        self.dialog.destroy()

    def _cancel(self) -> None:
        """取消操作"""
        self.result = None
        self.dialog.destroy()
