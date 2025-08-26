"""MiniCRM 合同管理TTK面板

基于tkinter/ttk实现的合同管理面板,替换Qt版本的ContractPanel.
提供完整的合同管理功能,包括:
- 合同列表显示和操作
- 合同状态管理和审批流程
- 合同模板应用和编辑器
- 附件管理和文档生成
- 到期提醒和续约管理

设计原则:
- 继承BaseWidget提供统一的组件基础
- 使用DataTableTTK显示合同列表
- 集成FormBuilderTTK进行合同编辑
- 模块化设计,保持代码清晰
- 遵循MiniCRM开发标准

作者: MiniCRM开发团队
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional

from minicrm.services.contract_service import ContractService
from minicrm.ui.ttk_base.base_widget import BaseWidget
from minicrm.ui.ttk_base.data_table_ttk import DataTableTTK


class ContractPanelTTK(BaseWidget):
    """合同管理TTK面板

    提供完整的合同管理界面,包括合同列表、搜索筛选、
    状态管理、编辑操作等功能.
    """

    def __init__(self, parent: tk.Widget, contract_service: ContractService, **kwargs):
        """初始化合同管理面板

        Args:
            parent: 父容器组件
            contract_service: 合同服务实例
            **kwargs: 其他参数
        """
        self.contract_service = contract_service

        # 数据存储
        self.contracts: List[Dict[str, Any]] = []
        self.selected_contract_id: Optional[int] = None

        # UI组件
        self.search_frame: Optional[ttk.Frame] = None
        self.search_entry: Optional[ttk.Entry] = None
        self.status_filter: Optional[ttk.Combobox] = None
        self.type_filter: Optional[ttk.Combobox] = None
        self.contract_table: Optional[DataTableTTK] = None
        self.detail_frame: Optional[ttk.Frame] = None
        self.button_frame: Optional[ttk.Frame] = None

        # 事件回调
        self.on_contract_selected: Optional[Callable] = None
        self.on_contract_created: Optional[Callable] = None
        self.on_contract_updated: Optional[Callable] = None
        self.on_contract_deleted: Optional[Callable] = None
        self.on_status_changed: Optional[Callable] = None

        # 初始化基础组件
        super().__init__(parent, **kwargs)

        # 加载初始数据
        self._load_contracts()

    def _setup_ui(self) -> None:
        """设置UI布局"""
        # 创建主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建搜索筛选区域
        self._create_search_area(main_container)

        # 创建操作按钮区域
        self._create_button_area(main_container)

        # 创建分割面板
        self._create_split_panel(main_container)

    def _create_search_area(self, parent: ttk.Frame) -> None:
        """创建搜索筛选区域"""
        self.search_frame = ttk.LabelFrame(parent, text="搜索筛选", padding=10)
        self.search_frame.pack(fill=tk.X, pady=(0, 10))

        # 第一行:搜索框
        search_row = ttk.Frame(self.search_frame)
        search_row.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(search_row, text="搜索:").pack(side=tk.LEFT, padx=(0, 5))

        self.search_entry = ttk.Entry(search_row, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))

        search_btn = ttk.Button(
            search_row, text="🔍 搜索", command=self._perform_search
        )
        search_btn.pack(side=tk.LEFT, padx=(0, 5))

        clear_btn = ttk.Button(search_row, text="清除", command=self._clear_search)
        clear_btn.pack(side=tk.LEFT)

        # 第二行:筛选器
        filter_row = ttk.Frame(self.search_frame)
        filter_row.pack(fill=tk.X)

        # 状态筛选
        ttk.Label(filter_row, text="状态:").pack(side=tk.LEFT, padx=(0, 5))

        self.status_filter = ttk.Combobox(filter_row, width=15, state="readonly")
        self.status_filter["values"] = [
            "全部",
            "草稿",
            "待审批",
            "已审批",
            "已签署",
            "执行中",
            "已完成",
            "已终止",
            "已过期",
        ]
        self.status_filter.set("全部")
        self.status_filter.pack(side=tk.LEFT, padx=(0, 15))

        # 类型筛选
        ttk.Label(filter_row, text="类型:").pack(side=tk.LEFT, padx=(0, 5))

        self.type_filter = ttk.Combobox(filter_row, width=15, state="readonly")
        self.type_filter["values"] = [
            "全部",
            "销售合同",
            "采购合同",
            "服务合同",
            "框架合同",
            "其他",
        ]
        self.type_filter.set("全部")
        self.type_filter.pack(side=tk.LEFT, padx=(0, 15))

        # 刷新按钮
        refresh_btn = ttk.Button(
            filter_row, text="🔄 刷新", command=self._load_contracts
        )
        refresh_btn.pack(side=tk.RIGHT)

    def _create_button_area(self, parent: ttk.Frame) -> None:
        """创建操作按钮区域"""
        self.button_frame = ttk.Frame(parent)
        self.button_frame.pack(fill=tk.X, pady=(0, 10))

        # 左侧按钮组
        left_buttons = ttk.Frame(self.button_frame)
        left_buttons.pack(side=tk.LEFT)

        # 新建合同
        new_btn = ttk.Button(
            left_buttons, text="➕ 新建合同", command=self._create_contract
        )
        new_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 编辑合同
        edit_btn = ttk.Button(left_buttons, text="✏️ 编辑", command=self._edit_contract)
        edit_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 删除合同
        delete_btn = ttk.Button(
            left_buttons, text="🗑️ 删除", command=self._delete_contract
        )
        delete_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 右侧按钮组
        right_buttons = ttk.Frame(self.button_frame)
        right_buttons.pack(side=tk.RIGHT)

        # 导出合同
        export_btn = ttk.Button(
            right_buttons, text="📤 导出", command=self._export_contract
        )
        export_btn.pack(side=tk.LEFT, padx=(5, 0))

        # 打印合同
        print_btn = ttk.Button(
            right_buttons, text="🖨️ 打印", command=self._print_contract
        )
        print_btn.pack(side=tk.LEFT, padx=(5, 0))

    def _create_split_panel(self, parent: ttk.Frame) -> None:
        """创建分割面板"""
        # 创建PanedWindow
        paned_window = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # 左侧:合同列表
        self._create_contract_table(paned_window)

        # 右侧:详情面板
        self._create_detail_panel(paned_window)

    def _create_contract_table(self, parent: ttk.PanedWindow) -> None:
        """创建合同表格"""
        # 定义表格列
        columns = [
            {"id": "contract_number", "text": "合同编号", "width": 120},
            {"id": "party_name", "text": "合同方", "width": 150},
            {"id": "contract_type", "text": "类型", "width": 100},
            {"id": "contract_amount", "text": "金额", "width": 120, "anchor": "e"},
            {"id": "sign_date", "text": "签署日期", "width": 100},
            {"id": "expiry_date", "text": "到期日期", "width": 100},
            {"id": "contract_status", "text": "状态", "width": 80},
            {"id": "progress", "text": "进度", "width": 80, "anchor": "e"},
        ]

        # 创建表格组件
        self.contract_table = DataTableTTK(
            parent,
            columns=columns,
            multi_select=True,
            show_pagination=True,
            page_size=50,
        )

        # 设置事件回调
        self.contract_table.on_row_selected = self._on_contract_selected
        self.contract_table.on_row_double_clicked = self._on_contract_double_clicked
        self.contract_table.on_selection_changed = self._on_selection_changed

        # 添加到分割面板
        parent.add(self.contract_table, weight=3)

    def _create_detail_panel(self, parent: ttk.PanedWindow) -> None:
        """创建详情面板"""
        self.detail_frame = ttk.LabelFrame(parent, text="合同详情", padding=10)

        # 创建滚动区域
        canvas = tk.Canvas(self.detail_frame)
        scrollbar = ttk.Scrollbar(
            self.detail_frame, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 布局滚动区域
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 创建详情内容
        self._create_detail_content(scrollable_frame)

        # 添加到分割面板
        parent.add(self.detail_frame, weight=1)

    def _create_detail_content(self, parent: ttk.Frame) -> None:
        """创建详情内容"""
        # 基本信息区域
        basic_frame = ttk.LabelFrame(parent, text="基本信息", padding=5)
        basic_frame.pack(fill=tk.X, pady=(0, 10))

        self.detail_labels = {}

        # 创建详情标签
        detail_fields = [
            ("contract_number", "合同编号"),
            ("party_name", "合同方"),
            ("contract_type", "合同类型"),
            ("contract_status", "合同状态"),
            ("contract_amount", "合同金额"),
            ("currency", "货币类型"),
            ("payment_method", "付款方式"),
            ("payment_terms", "付款期限"),
        ]

        for i, (field_id, label_text) in enumerate(detail_fields):
            row = i // 2
            col = (i % 2) * 2

            ttk.Label(basic_frame, text=f"{label_text}:").grid(
                row=row, column=col, sticky="w", padx=(0, 5), pady=2
            )

            value_label = ttk.Label(basic_frame, text="", foreground="blue")
            value_label.grid(row=row, column=col + 1, sticky="w", padx=(0, 15), pady=2)

            self.detail_labels[field_id] = value_label

        # 时间信息区域
        time_frame = ttk.LabelFrame(parent, text="时间信息", padding=5)
        time_frame.pack(fill=tk.X, pady=(0, 10))

        time_fields = [
            ("sign_date", "签署日期"),
            ("effective_date", "生效日期"),
            ("expiry_date", "到期日期"),
            ("remaining_days", "剩余天数"),
        ]

        for i, (field_id, label_text) in enumerate(time_fields):
            row = i // 2
            col = (i % 2) * 2

            ttk.Label(time_frame, text=f"{label_text}:").grid(
                row=row, column=col, sticky="w", padx=(0, 5), pady=2
            )

            value_label = ttk.Label(time_frame, text="")
            value_label.grid(row=row, column=col + 1, sticky="w", padx=(0, 15), pady=2)

            self.detail_labels[field_id] = value_label

        # 进度信息区域
        progress_frame = ttk.LabelFrame(parent, text="执行进度", padding=5)
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))

        # 进度标签
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.pack()

        # 操作按钮区域
        action_frame = ttk.LabelFrame(parent, text="快速操作", padding=5)
        action_frame.pack(fill=tk.X)

        # 状态操作按钮
        status_btn_frame = ttk.Frame(action_frame)
        status_btn_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(status_btn_frame, text="签署合同", command=self._sign_contract).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        ttk.Button(
            status_btn_frame, text="终止合同", command=self._terminate_contract
        ).pack(side=tk.LEFT, padx=(0, 5))

        # 进度操作按钮
        progress_btn_frame = ttk.Frame(action_frame)
        progress_btn_frame.pack(fill=tk.X)

        ttk.Button(
            progress_btn_frame, text="更新进度", command=self._update_progress
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            progress_btn_frame, text="查看附件", command=self._view_attachments
        ).pack(side=tk.LEFT)

    def _bind_events(self) -> None:
        """绑定事件"""
        # 搜索框回车事件
        if self.search_entry:
            self.search_entry.bind("<Return>", lambda e: self._perform_search())

        # 筛选器变化事件
        if self.status_filter:
            self.status_filter.bind("<<ComboboxSelected>>", self._on_filter_changed)

        if self.type_filter:
            self.type_filter.bind("<<ComboboxSelected>>", self._on_filter_changed)

    def _load_contracts(self) -> None:
        """加载合同数据"""
        try:
            # 获取合同列表
            contracts = self.contract_service.list_all()

            # 转换为显示格式
            self.contracts = []
            for contract in contracts:
                contract_dict = (
                    contract.to_dict() if hasattr(contract, "to_dict") else contract
                )
                display_data = self._format_contract_for_display(contract_dict)
                self.contracts.append(display_data)

            # 更新表格数据
            if self.contract_table:
                self.contract_table.load_data(self.contracts)

            self.logger.info(f"加载了 {len(self.contracts)} 个合同")

        except Exception as e:
            self.logger.error(f"加载合同数据失败: {e}")
            message_dialogs_ttk.show_error(self, f"加载合同数据失败: {e}")

    def _format_contract_for_display(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """格式化合同数据用于显示"""
        # 格式化合同类型
        contract_type = contract.get("contract_type", "")
        type_map = {
            "sales": "销售合同",
            "purchase": "采购合同",
            "service": "服务合同",
            "framework": "框架合同",
            "other": "其他",
        }
        contract["contract_type"] = type_map.get(contract_type, contract_type)

        # 格式化合同状态
        contract_status = contract.get("contract_status", "")
        status_map = {
            "draft": "草稿",
            "pending": "待审批",
            "approved": "已审批",
            "signed": "已签署",
            "active": "执行中",
            "completed": "已完成",
            "terminated": "已终止",
            "expired": "已过期",
        }
        contract["contract_status"] = status_map.get(contract_status, contract_status)

        # 格式化金额
        amount = contract.get("contract_amount", 0)
        try:
            contract["contract_amount"] = f"¥{float(amount):,.2f}"
        except (ValueError, TypeError):
            contract["contract_amount"] = "¥0.00"

        # 格式化进度
        progress = contract.get("progress_percentage", 0)
        try:
            contract["progress"] = f"{float(progress):.1f}%"
        except (ValueError, TypeError):
            contract["progress"] = "0.0%"

        # 格式化日期
        for date_field in ["sign_date", "effective_date", "expiry_date"]:
            date_value = contract.get(date_field)
            if date_value:
                try:
                    if hasattr(date_value, "strftime"):
                        contract[date_field] = date_value.strftime("%Y-%m-%d")
                    else:
                        contract[date_field] = str(date_value)[:10]
                except:
                    contract[date_field] = ""
            else:
                contract[date_field] = ""

        return contract

    def _perform_search(self) -> None:
        """执行搜索"""
        if not self.search_entry:
            return

        search_text = self.search_entry.get().strip().lower()

        if not search_text:
            # 如果搜索框为空,显示所有数据
            filtered_data = self.contracts
        else:
            # 搜索合同编号、合同方名称
            filtered_data = []
            for contract in self.contracts:
                if (
                    search_text in contract.get("contract_number", "").lower()
                    or search_text in contract.get("party_name", "").lower()
                ):
                    filtered_data.append(contract)

        # 应用筛选器
        filtered_data = self._apply_filters(filtered_data)

        # 更新表格
        if self.contract_table:
            self.contract_table.load_data(filtered_data)

    def _clear_search(self) -> None:
        """清除搜索"""
        if self.search_entry:
            self.search_entry.delete(0, tk.END)

        if self.status_filter:
            self.status_filter.set("全部")

        if self.type_filter:
            self.type_filter.set("全部")

        # 重新加载数据
        self._load_contracts()

    def _on_filter_changed(self, event=None) -> None:
        """处理筛选器变化"""
        # 应用筛选
        filtered_data = self._apply_filters(self.contracts)

        # 更新表格
        if self.contract_table:
            self.contract_table.load_data(filtered_data)

    def _apply_filters(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """应用筛选条件"""
        filtered_data = data.copy()

        # 状态筛选
        if self.status_filter:
            status_filter = self.status_filter.get()
            if status_filter != "全部":
                filtered_data = [
                    contract
                    for contract in filtered_data
                    if contract.get("contract_status") == status_filter
                ]

        # 类型筛选
        if self.type_filter:
            type_filter = self.type_filter.get()
            if type_filter != "全部":
                filtered_data = [
                    contract
                    for contract in filtered_data
                    if contract.get("contract_type") == type_filter
                ]

        return filtered_data

    def _on_contract_selected(self, contract_data: Dict[str, Any]) -> None:
        """处理合同选择事件"""
        self.selected_contract_id = contract_data.get("id")
        self._update_detail_panel(contract_data)

        # 触发外部回调
        if self.on_contract_selected:
            self.on_contract_selected(contract_data)

    def _on_contract_double_clicked(self, contract_data: Dict[str, Any]) -> None:
        """处理合同双击事件"""
        self._edit_contract()

    def _on_selection_changed(self, selected_data: List[Dict[str, Any]]) -> None:
        """处理选择变化事件"""
        if selected_data:
            self._on_contract_selected(selected_data[0])

    def _update_detail_panel(self, contract_data: Dict[str, Any]) -> None:
        """更新详情面板"""
        if not hasattr(self, "detail_labels"):
            return

        # 更新基本信息
        for field_id, label in self.detail_labels.items():
            value = contract_data.get(field_id, "")
            label.config(text=str(value))

        # 更新进度条
        progress = contract_data.get("progress_percentage", 0)
        try:
            progress_value = float(str(progress).rstrip("%"))
            self.progress_var.set(progress_value)
            self.progress_label.config(text=f"{progress_value:.1f}%")
        except (ValueError, TypeError):
            self.progress_var.set(0)
            self.progress_label.config(text="0%")

        # 计算剩余天数
        expiry_date = contract_data.get("expiry_date")
        if expiry_date and "remaining_days" in self.detail_labels:
            try:
                from datetime import datetime

                if isinstance(expiry_date, str):
                    expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
                else:
                    expiry = expiry_date

                remaining = (expiry - datetime.now()).days
                if remaining > 0:
                    self.detail_labels["remaining_days"].config(
                        text=f"{remaining} 天", foreground="green"
                    )
                elif remaining == 0:
                    self.detail_labels["remaining_days"].config(
                        text="今天到期", foreground="orange"
                    )
                else:
                    self.detail_labels["remaining_days"].config(
                        text=f"已过期 {abs(remaining)} 天", foreground="red"
                    )
            except:
                self.detail_labels["remaining_days"].config(text="", foreground="black")

    def _create_contract(self) -> None:
        """创建新合同"""
        try:
            from minicrm.ui.ttk_base.contract_edit_dialog_ttk import (
                ContractEditDialogTTK,
            )

            dialog = ContractEditDialogTTK(self, self.contract_service, contract=None)

            if dialog.show_modal():
                contract_data = dialog.get_contract_data()

                # 创建合同
                new_contract = self.contract_service.create_contract(contract_data)

                # 刷新列表
                self._load_contracts()

                # 触发回调
                if self.on_contract_created:
                    self.on_contract_created(new_contract.id)

                message_dialogs_ttk.show_info(self, "合同创建成功!")

        except Exception as e:
            self.logger.error(f"创建合同失败: {e}")
            message_dialogs_ttk.show_error(self, f"创建合同失败: {e}")

    def _edit_contract(self) -> None:
        """编辑选中的合同"""
        if not self.selected_contract_id:
            message_dialogs_ttk.show_warning(self, "请先选择要编辑的合同")
            return

        try:
            # 获取合同详情
            contract = self.contract_service.get_by_id(self.selected_contract_id)
            if not contract:
                message_dialogs_ttk.show_error(self, "合同不存在")
                return

            from minicrm.ui.ttk_base.contract_edit_dialog_ttk import (
                ContractEditDialogTTK,
            )

            dialog = ContractEditDialogTTK(
                self, self.contract_service, contract=contract
            )

            if dialog.show_modal():
                contract_data = dialog.get_contract_data()

                # 更新合同
                updated_contract = self.contract_service.update(
                    self.selected_contract_id, contract_data
                )

                # 刷新列表
                self._load_contracts()

                # 触发回调
                if self.on_contract_updated:
                    self.on_contract_updated(updated_contract.id)

                message_dialogs_ttk.show_info(self, "合同更新成功!")

        except Exception as e:
            self.logger.error(f"编辑合同失败: {e}")
            message_dialogs_ttk.show_error(self, f"编辑合同失败: {e}")

    def _delete_contract(self) -> None:
        """删除选中的合同"""
        if not self.selected_contract_id:
            message_dialogs_ttk.show_warning(self, "请先选择要删除的合同")
            return

        # 确认删除
        if not message_dialogs_ttk.confirm(
            self, "确定要删除选中的合同吗?此操作不可撤销.", "确认删除"
        ):
            return

        try:
            # 删除合同
            self.contract_service.delete(self.selected_contract_id)

            # 清除选择
            self.selected_contract_id = None

            # 刷新列表
            self._load_contracts()

            # 触发回调
            if self.on_contract_deleted:
                self.on_contract_deleted(self.selected_contract_id)

            message_dialogs_ttk.show_info(self, "合同删除成功!")

        except Exception as e:
            self.logger.error(f"删除合同失败: {e}")
            message_dialogs_ttk.show_error(self, f"删除合同失败: {e}")

    def _export_contract(self) -> None:
        """导出合同"""
        if not self.selected_contract_id:
            message_dialogs_ttk.show_warning(self, "请先选择要导出的合同")
            return

        # TODO: 实现合同导出功能
        message_dialogs_ttk.show_info(self, "导出功能正在开发中...")

    def _print_contract(self) -> None:
        """打印合同"""
        if not self.selected_contract_id:
            message_dialogs_ttk.show_warning(self, "请先选择要打印的合同")
            return

        # TODO: 实现合同打印功能
        message_dialogs_ttk.show_info(self, "打印功能正在开发中...")

    def _sign_contract(self) -> None:
        """签署合同"""
        if not self.selected_contract_id:
            message_dialogs_ttk.show_warning(self, "请先选择要签署的合同")
            return

        try:
            # 签署合同
            self.contract_service.sign_contract(self.selected_contract_id)

            # 刷新列表
            self._load_contracts()

            # 触发回调
            if self.on_status_changed:
                self.on_status_changed(self.selected_contract_id, "signed")

            message_dialogs_ttk.show_info(self, "合同签署成功!")

        except Exception as e:
            self.logger.error(f"签署合同失败: {e}")
            message_dialogs_ttk.show_error(self, f"签署合同失败: {e}")

    def _terminate_contract(self) -> None:
        """终止合同"""
        if not self.selected_contract_id:
            message_dialogs_ttk.show_warning(self, "请先选择要终止的合同")
            return

        # 获取终止原因
        reason = tk.simpledialog.askstring("终止合同", "请输入终止原因:", parent=self)

        if not reason:
            return

        try:
            # 终止合同
            self.contract_service.terminate_contract(self.selected_contract_id, reason)

            # 刷新列表
            self._load_contracts()

            # 触发回调
            if self.on_status_changed:
                self.on_status_changed(self.selected_contract_id, "terminated")

            message_dialogs_ttk.show_info(self, "合同终止成功!")

        except Exception as e:
            self.logger.error(f"终止合同失败: {e}")
            message_dialogs_ttk.show_error(self, f"终止合同失败: {e}")

    def _update_progress(self) -> None:
        """更新合同进度"""
        if not self.selected_contract_id:
            message_dialogs_ttk.show_warning(self, "请先选择要更新进度的合同")
            return

        # TODO: 实现进度更新对话框
        message_dialogs_ttk.show_info(self, "进度更新功能正在开发中...")

    def _view_attachments(self) -> None:
        """查看合同附件"""
        if not self.selected_contract_id:
            message_dialogs_ttk.show_warning(self, "请先选择要查看附件的合同")
            return

        # TODO: 实现附件查看功能
        message_dialogs_ttk.show_info(self, "附件查看功能正在开发中...")

    def get_selected_contract_id(self) -> Optional[int]:
        """获取选中的合同ID"""
        return self.selected_contract_id

    def refresh_data(self) -> None:
        """刷新数据"""
        self._load_contracts()

    def cleanup(self) -> None:
        """清理资源"""
        self.contracts.clear()
        self.selected_contract_id = None

        if self.contract_table:
            self.contract_table.cleanup()

        super().cleanup()


# 导出类
__all__ = ["ContractPanelTTK"]
