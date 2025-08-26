"""MiniCRM TTK合同模板管理组件

基于TTK框架实现的合同模板管理组件,用于替换Qt版本的模板管理功能.
支持模板创建、编辑、删除、预览、应用、版本控制等完整的模板管理功能.

设计特点:
- 使用TTK组件构建模板管理界面
- 支持多种模板类型和版本管理
- 提供模板预览和编辑功能
- 集成模板导入导出功能
- 支持模板使用统计和分析
- 遵循MiniCRM开发标准

作者: MiniCRM开发团队
"""

from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable, Dict, List, Optional

from minicrm.core.exceptions import ServiceError
from minicrm.models.contract import ContractType
from minicrm.models.contract_template import (
    TemplateStatus,
    TemplateType,
)
from minicrm.services.contract_service import ContractService
from minicrm.ui.ttk_base.base_widget import BaseWidget


class ContractTemplateTTK(BaseWidget):
    """TTK合同模板管理组件

    提供完整的合同模板管理功能:
    - 模板列表显示和管理
    - 模板创建、编辑、删除
    - 模板版本控制和历史管理
    - 模板预览和应用
    - 模板导入导出
    - 使用统计和分析
    """

    def __init__(
        self,
        parent: tk.Widget,
        contract_service: Optional[ContractService] = None,
        **kwargs,
    ):
        """初始化合同模板管理组件

        Args:
            parent: 父组件
            contract_service: 合同服务实例,如果为None则自动创建
            **kwargs: 其他参数
        """
        self._contract_service = contract_service or ContractService()

        # 数据存储
        self._templates: List[Dict[str, Any]] = []
        self._selected_template: Optional[Dict[str, Any]] = None
        self._template_versions: Dict[int, List[Dict[str, Any]]] = {}

        # UI组件
        self._template_tree: Optional[ttk.Treeview] = None
        self._detail_frame: Optional[ttk.Frame] = None
        self._preview_frame: Optional[ttk.Frame] = None
        self._version_frame: Optional[ttk.Frame] = None

        # 事件回调
        self.on_template_selected: Optional[Callable] = None
        self.on_template_applied: Optional[Callable] = None
        self.on_template_changed: Optional[Callable] = None

        super().__init__(parent, **kwargs)

        # 加载模板数据
        self._load_templates()

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
            title_frame, text="合同模板管理", font=("Microsoft YaHei UI", 14, "bold")
        )
        title_label.pack(side=tk.LEFT)

        # 模板统计信息
        self._stats_label = ttk.Label(title_frame, text="", foreground="gray")
        self._stats_label.pack(side=tk.RIGHT)

    def _create_toolbar(self, parent: ttk.Frame) -> None:
        """创建工具栏"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))

        # 左侧按钮
        left_frame = ttk.Frame(toolbar_frame)
        left_frame.pack(side=tk.LEFT)

        # 新建模板按钮
        self._new_btn = ttk.Button(
            left_frame, text="➕ 新建模板", command=self._create_new_template
        )
        self._new_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 编辑模板按钮
        self._edit_btn = ttk.Button(
            left_frame,
            text="✏️ 编辑模板",
            command=self._edit_template,
            state=tk.DISABLED,
        )
        self._edit_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 复制模板按钮
        self._copy_btn = ttk.Button(
            left_frame,
            text="📋 复制模板",
            command=self._copy_template,
            state=tk.DISABLED,
        )
        self._copy_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 删除模板按钮
        self._delete_btn = ttk.Button(
            left_frame,
            text="🗑️ 删除模板",
            command=self._delete_template,
            state=tk.DISABLED,
        )
        self._delete_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 版本管理按钮
        self._version_btn = ttk.Button(
            left_frame,
            text="📋 版本管理",
            command=self._manage_versions,
            state=tk.DISABLED,
        )
        self._version_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 右侧按钮
        right_frame = ttk.Frame(toolbar_frame)
        right_frame.pack(side=tk.RIGHT)

        # 导入模板按钮
        self._import_btn = ttk.Button(
            right_frame, text="📥 导入模板", command=self._import_template
        )
        self._import_btn.pack(side=tk.LEFT, padx=(5, 0))

        # 导出模板按钮
        self._export_btn = ttk.Button(
            right_frame,
            text="📤 导出模板",
            command=self._export_template,
            state=tk.DISABLED,
        )
        self._export_btn.pack(side=tk.LEFT, padx=(5, 0))

        # 刷新按钮
        self._refresh_btn = ttk.Button(
            right_frame, text="🔄 刷新", command=self._refresh_templates
        )
        self._refresh_btn.pack(side=tk.LEFT, padx=(5, 0))

    def _create_content_area(self, parent: ttk.Frame) -> None:
        """创建主要内容区域"""
        # 创建分割面板
        paned_window = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # 左侧:模板列表
        self._create_template_list(paned_window)

        # 右侧:模板详情和预览
        self._create_detail_area(paned_window)

    def _create_template_list(self, parent: ttk.PanedWindow) -> None:
        """创建模板列表"""
        # 创建列表框架
        list_frame = ttk.Frame(parent)
        parent.add(list_frame, weight=1)

        # 列表标题
        list_title = ttk.Label(
            list_frame, text="模板列表", font=("Microsoft YaHei UI", 12, "bold")
        )
        list_title.pack(anchor=tk.W, pady=(0, 5))

        # 创建树形视图
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # 定义列
        columns = ("name", "type", "status", "version", "usage_count", "created_at")
        self._template_tree = ttk.Treeview(
            tree_frame, columns=columns, show="tree headings", selectmode="extended"
        )

        # 配置列
        self._template_tree.heading("#0", text="状态")
        self._template_tree.heading("name", text="模板名称")
        self._template_tree.heading("type", text="合同类型")
        self._template_tree.heading("status", text="状态")
        self._template_tree.heading("version", text="版本")
        self._template_tree.heading("usage_count", text="使用次数")
        self._template_tree.heading("created_at", text="创建时间")

        self._template_tree.column("#0", width=60, minwidth=60)
        self._template_tree.column("name", width=150, minwidth=100)
        self._template_tree.column("type", width=100, minwidth=80)
        self._template_tree.column("status", width=80, minwidth=60)
        self._template_tree.column("version", width=80, minwidth=60)
        self._template_tree.column("usage_count", width=80, minwidth=60)
        self._template_tree.column("created_at", width=120, minwidth=100)

        # 添加滚动条
        tree_scrollbar = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self._template_tree.yview
        )
        self._template_tree.configure(yscrollcommand=tree_scrollbar.set)

        # 布局
        self._template_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定事件
        self._template_tree.bind("<<TreeviewSelect>>", self._on_template_selected)
        self._template_tree.bind("<Double-1>", self._on_template_double_clicked)
        self._template_tree.bind("<Button-3>", self._show_context_menu)

    def _create_detail_area(self, parent: ttk.PanedWindow) -> None:
        """创建详情区域"""
        # 创建详情框架
        detail_frame = ttk.Frame(parent)
        parent.add(detail_frame, weight=2)

        # 创建标签页
        notebook = ttk.Notebook(detail_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 模板详情标签页
        self._detail_frame = ttk.Frame(notebook)
        notebook.add(self._detail_frame, text="模板详情")

        # 模板预览标签页
        self._preview_frame = ttk.Frame(notebook)
        notebook.add(self._preview_frame, text="模板预览")

        # 版本历史标签页
        self._version_frame = ttk.Frame(notebook)
        notebook.add(self._version_frame, text="版本历史")

        # 初始化详情显示
        self._show_empty_detail()

    def _load_templates(self) -> None:
        """加载模板数据"""
        try:
            # 从服务层获取模板数据
            templates = self._contract_service.get_templates()

            # 转换为字典格式
            self._templates = [template.to_dict() for template in templates]
            self._refresh_template_list()
            self._update_stats()

            self.logger.info(f"加载了 {len(self._templates)} 个合同模板")

        except ServiceError as e:
            self.logger.error(f"加载合同模板失败: {e}")
            messagebox.showerror("错误", f"加载合同模板失败:{e}")
        except Exception as e:
            self.logger.error(f"加载合同模板时发生未知错误: {e}")
            messagebox.showerror("错误", f"加载合同模板时发生未知错误:{e}")

    def _refresh_template_list(self) -> None:
        """刷新模板列表显示"""
        if not self._template_tree:
            return

        # 清空现有项目
        for item in self._template_tree.get_children():
            self._template_tree.delete(item)

        # 添加模板项目
        for template in self._templates:
            # 确定状态图标
            status = template.get("template_status", TemplateStatus.DRAFT)
            if isinstance(status, str):
                try:
                    status = TemplateStatus(status)
                except ValueError:
                    status = TemplateStatus.DRAFT

            if status == TemplateStatus.ACTIVE:
                status_icon = "✅"  # 激活模板
            elif status == TemplateStatus.ARCHIVED:
                status_icon = "📦"  # 已归档模板
            elif status == TemplateStatus.DEPRECATED:
                status_icon = "❌"  # 已弃用模板
            else:
                status_icon = "📄"  # 草稿模板

            # 格式化创建时间
            created_at = template.get("created_at", "")
            if created_at:
                try:
                    if isinstance(created_at, str):
                        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    else:
                        dt = created_at
                    created_at = dt.strftime("%Y-%m-%d")
                except:
                    pass

            # 获取合同类型显示
            contract_type = template.get("contract_type", ContractType.SALES)
            if isinstance(contract_type, str):
                try:
                    contract_type = ContractType(contract_type)
                except ValueError:
                    contract_type = ContractType.SALES

            contract_type_display = {
                ContractType.SALES: "销售合同",
                ContractType.PURCHASE: "采购合同",
                ContractType.SERVICE: "服务合同",
                ContractType.FRAMEWORK: "框架合同",
                ContractType.OTHER: "其他",
            }.get(contract_type, "未知")

            # 插入项目
            self._template_tree.insert(
                "",
                "end",
                text=status_icon,
                values=(
                    template.get("template_name", ""),
                    contract_type_display,
                    template.get("status_display", ""),
                    template.get("template_version", "1.0"),
                    template.get("usage_count", 0),
                    created_at,
                ),
                tags=(status.value if isinstance(status, TemplateStatus) else "draft",),
            )

        # 配置标签样式
        self._template_tree.tag_configure("active", background="#e6ffe6")
        self._template_tree.tag_configure("archived", background="#f0f0f0")
        self._template_tree.tag_configure("deprecated", background="#ffe6e6")

    def _update_stats(self) -> None:
        """更新统计信息"""
        total_count = len(self._templates)
        active_count = sum(
            1
            for t in self._templates
            if t.get("template_status") == TemplateStatus.ACTIVE.value
        )
        draft_count = sum(
            1
            for t in self._templates
            if t.get("template_status") == TemplateStatus.DRAFT.value
        )

        stats_text = (
            f"共 {total_count} 个模板 (激活: {active_count}, 草稿: {draft_count})"
        )
        self._stats_label.config(text=stats_text)

    def _on_template_selected(self, event=None) -> None:
        """处理模板选择事件"""
        selection = self._template_tree.selection()
        if not selection:
            self._selected_template = None
            self._show_empty_detail()
            self._update_button_states()
            return

        # 获取选中的模板
        item = selection[0]
        item_index = self._template_tree.index(item)

        if 0 <= item_index < len(self._templates):
            self._selected_template = self._templates[item_index]
            self._show_template_detail()
            self._load_template_versions()
            self._update_button_states()

            # 触发选择事件
            if self.on_template_selected:
                self.on_template_selected(self._selected_template)

    def _on_template_double_clicked(self, event=None) -> None:
        """处理模板双击事件"""
        if self._selected_template:
            self._edit_template()

    def _show_context_menu(self, event) -> None:
        """显示右键菜单"""
        if not self._template_tree.selection():
            return

        # 创建右键菜单
        context_menu = tk.Menu(self, tearoff=0)

        # 基本操作
        context_menu.add_command(label="编辑模板", command=self._edit_template)
        context_menu.add_command(label="复制模板", command=self._copy_template)
        context_menu.add_separator()

        # 版本管理
        context_menu.add_command(label="版本管理", command=self._manage_versions)
        context_menu.add_command(label="创建新版本", command=self._create_new_version)
        context_menu.add_separator()

        # 状态管理
        if self._selected_template:
            status = self._selected_template.get("template_status")
            if status == TemplateStatus.DRAFT.value:
                context_menu.add_command(
                    label="激活模板", command=self._activate_template
                )
            elif status == TemplateStatus.ACTIVE.value:
                context_menu.add_command(
                    label="归档模板", command=self._archive_template
                )
            elif status == TemplateStatus.ARCHIVED.value:
                context_menu.add_command(
                    label="激活模板", command=self._activate_template
                )

        context_menu.add_separator()
        context_menu.add_command(label="导出模板", command=self._export_template)

        # 删除操作(系统模板不能删除)
        if (
            self._selected_template
            and self._selected_template.get("template_type")
            != TemplateType.SYSTEM.value
        ):
            context_menu.add_separator()
            context_menu.add_command(label="删除模板", command=self._delete_template)

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def _show_template_detail(self) -> None:
        """显示模板详情"""
        if not self._selected_template:
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

        # 显示模板信息
        self._create_template_info_display(scrollable_frame)

    def _create_template_info_display(self, parent: ttk.Frame) -> None:
        """创建模板信息显示"""
        template = self._selected_template

        # 基本信息区域
        basic_frame = ttk.LabelFrame(parent, text="基本信息", padding=10)
        basic_frame.pack(fill=tk.X, padx=10, pady=5)

        basic_info = [
            ("模板名称", template.get("template_name", "")),
            ("合同类型", template.get("contract_type_display", "")),
            ("模板状态", template.get("status_display", "")),
            ("模板类型", template.get("type_display", "")),
            ("版本号", template.get("template_version", "")),
            ("创建者", template.get("created_by", "")),
            ("最后修改者", template.get("last_modified_by", "")),
            ("使用次数", template.get("usage_count", 0)),
            ("创建时间", self._format_datetime(template.get("created_at", ""))),
            ("更新时间", self._format_datetime(template.get("updated_at", ""))),
            ("最后使用", self._format_datetime(template.get("last_used_at", ""))),
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

        # 模板内容区域
        content_frame = ttk.LabelFrame(parent, text="模板内容", padding=10)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 条款模板
        if template.get("terms_template"):
            terms_label = ttk.Label(
                content_frame, text="条款模板:", font=("Microsoft YaHei UI", 10, "bold")
            )
            terms_label.pack(anchor=tk.W, pady=(0, 5))

            terms_text = tk.Text(
                content_frame, height=6, wrap=tk.WORD, state=tk.DISABLED
            )
            terms_text.pack(fill=tk.X, pady=(0, 10))
            terms_text.config(state=tk.NORMAL)
            terms_text.insert("1.0", template.get("terms_template", ""))
            terms_text.config(state=tk.DISABLED)

        # 交付条款模板
        if template.get("delivery_terms_template"):
            delivery_label = ttk.Label(
                content_frame,
                text="交付条款模板:",
                font=("Microsoft YaHei UI", 10, "bold"),
            )
            delivery_label.pack(anchor=tk.W, pady=(0, 5))

            delivery_text = tk.Text(
                content_frame, height=4, wrap=tk.WORD, state=tk.DISABLED
            )
            delivery_text.pack(fill=tk.X, pady=(0, 10))
            delivery_text.config(state=tk.NORMAL)
            delivery_text.insert("1.0", template.get("delivery_terms_template", ""))
            delivery_text.config(state=tk.DISABLED)

        # 保修条款模板
        if template.get("warranty_terms_template"):
            warranty_label = ttk.Label(
                content_frame,
                text="保修条款模板:",
                font=("Microsoft YaHei UI", 10, "bold"),
            )
            warranty_label.pack(anchor=tk.W, pady=(0, 5))

            warranty_text = tk.Text(
                content_frame, height=4, wrap=tk.WORD, state=tk.DISABLED
            )
            warranty_text.pack(fill=tk.X, pady=(0, 10))
            warranty_text.config(state=tk.NORMAL)
            warranty_text.insert("1.0", template.get("warranty_terms_template", ""))
            warranty_text.config(state=tk.DISABLED)

        # 操作按钮区域
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, padx=10, pady=10)

        # 应用模板按钮
        apply_btn = ttk.Button(
            action_frame, text="🎯 应用此模板", command=self._apply_template
        )
        apply_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 预览模板按钮
        preview_btn = ttk.Button(
            action_frame, text="👁️ 预览模板", command=self._preview_template
        )
        preview_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 编辑模板按钮
        if template.get("is_editable", True):
            edit_btn = ttk.Button(
                action_frame, text="✏️ 编辑模板", command=self._edit_template
            )
            edit_btn.pack(side=tk.LEFT, padx=(0, 5))

    def _load_template_versions(self) -> None:
        """加载模板版本历史"""
        if not self._selected_template:
            return

        template_id = self._selected_template.get("id")
        if not template_id:
            return

        # 清空版本框架
        for widget in self._version_frame.winfo_children():
            widget.destroy()

        # 创建版本列表
        version_label = ttk.Label(
            self._version_frame,
            text="版本历史",
            font=("Microsoft YaHei UI", 12, "bold"),
        )
        version_label.pack(anchor=tk.W, pady=(10, 5))

        # 版本树形视图
        version_columns = (
            "version",
            "status",
            "created_by",
            "created_at",
            "usage_count",
        )
        version_tree = ttk.Treeview(
            self._version_frame, columns=version_columns, show="headings", height=8
        )

        # 配置列
        version_tree.heading("version", text="版本号")
        version_tree.heading("status", text="状态")
        version_tree.heading("created_by", text="创建者")
        version_tree.heading("created_at", text="创建时间")
        version_tree.heading("usage_count", text="使用次数")

        version_tree.column("version", width=80)
        version_tree.column("status", width=80)
        version_tree.column("created_by", width=100)
        version_tree.column("created_at", width=120)
        version_tree.column("usage_count", width=80)

        version_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 模拟版本数据(实际应该从服务层获取)
        current_template = self._selected_template
        version_tree.insert(
            "",
            "end",
            values=(
                current_template.get("template_version", "1.0"),
                current_template.get("status_display", ""),
                current_template.get("created_by", ""),
                self._format_datetime(current_template.get("created_at", "")),
                current_template.get("usage_count", 0),
            ),
        )

        # 版本操作按钮
        version_action_frame = ttk.Frame(self._version_frame)
        version_action_frame.pack(fill=tk.X, padx=10, pady=5)

        create_version_btn = ttk.Button(
            version_action_frame, text="创建新版本", command=self._create_new_version
        )
        create_version_btn.pack(side=tk.LEFT, padx=(0, 5))

    def _show_empty_detail(self) -> None:
        """显示空详情状态"""
        # 清空详情框架
        for widget in self._detail_frame.winfo_children():
            widget.destroy()

        # 显示提示
        tip_label = ttk.Label(
            self._detail_frame,
            text="请选择模板查看详情",
            font=("Microsoft YaHei UI", 12),
            foreground="gray",
        )
        tip_label.pack(expand=True)

        # 清空预览框架
        for widget in self._preview_frame.winfo_children():
            widget.destroy()

        tip_label2 = ttk.Label(
            self._preview_frame,
            text="请选择模板查看预览",
            font=("Microsoft YaHei UI", 12),
            foreground="gray",
        )
        tip_label2.pack(expand=True)

        # 清空版本框架
        for widget in self._version_frame.winfo_children():
            widget.destroy()

        tip_label3 = ttk.Label(
            self._version_frame,
            text="请选择模板查看版本历史",
            font=("Microsoft YaHei UI", 12),
            foreground="gray",
        )
        tip_label3.pack(expand=True)

    def _update_button_states(self) -> None:
        """更新按钮状态"""
        has_selection = self._selected_template is not None
        is_system = (
            self._selected_template.get("template_type") == TemplateType.SYSTEM.value
            if has_selection
            else False
        )
        is_editable = (
            self._selected_template.get("is_editable", True) if has_selection else False
        )

        # 编辑按钮(系统模板不能编辑)
        self._edit_btn.config(
            state=tk.NORMAL if has_selection and is_editable else tk.DISABLED
        )

        # 复制按钮
        self._copy_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)

        # 删除按钮(系统模板不能删除)
        self._delete_btn.config(
            state=tk.NORMAL if has_selection and not is_system else tk.DISABLED
        )

        # 版本管理按钮
        self._version_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)

        # 导出按钮
        self._export_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)

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

    # ==================== 模板操作方法 ====================

    def _create_new_template(self) -> None:
        """创建新模板"""
        dialog = ContractTemplateEditDialog(self, self._contract_service, mode="create")
        if dialog.show():
            # 刷新模板列表
            self._refresh_templates()

    def _edit_template(self) -> None:
        """编辑模板"""
        if not self._selected_template:
            messagebox.showwarning("提示", "请先选择要编辑的模板")
            return

        if self._selected_template.get("template_type") == TemplateType.SYSTEM.value:
            messagebox.showwarning("提示", "系统模板不能编辑")
            return

        dialog = ContractTemplateEditDialog(
            self,
            self._contract_service,
            mode="edit",
            template_data=self._selected_template,
        )
        if dialog.show():
            # 刷新模板列表
            self._refresh_templates()

    def _copy_template(self) -> None:
        """复制模板"""
        if not self._selected_template:
            messagebox.showwarning("提示", "请先选择要复制的模板")
            return

        # 获取新模板名称
        new_name = simpledialog.askstring(
            "复制模板",
            "请输入新模板名称:",
            initialvalue=f"{self._selected_template.get('template_name', '')} - 副本",
        )

        if not new_name:
            return

        try:
            # 创建复制的模板数据
            template_data = self._selected_template.copy()
            template_data.update(
                {
                    "template_name": new_name,
                    "template_status": TemplateStatus.DRAFT.value,
                    "template_type": TemplateType.USER.value,
                    "is_latest_version": True,
                    "usage_count": 0,
                    "last_used_at": None,
                    "created_by": "当前用户",  # 实际应该从用户会话获取
                    "last_modified_by": "当前用户",
                }
            )

            # 移除ID字段,让服务层分配新ID
            template_data.pop("id", None)

            # 创建新模板
            new_template = self._contract_service.create_template(template_data)

            messagebox.showinfo("成功", f"模板已复制,新模板ID: {new_template.id}")

            # 刷新模板列表
            self._refresh_templates()

        except (ServiceError, ValidationError) as e:
            messagebox.showerror("错误", f"复制模板失败:{e}")
        except Exception as e:
            self.logger.error(f"复制模板时发生未知错误: {e}")
            messagebox.showerror("错误", f"复制模板时发生未知错误:{e}")

    def _delete_template(self) -> None:
        """删除模板"""
        if not self._selected_template:
            messagebox.showwarning("提示", "请先选择要删除的模板")
            return

        if self._selected_template.get("template_type") == TemplateType.SYSTEM.value:
            messagebox.showwarning("提示", "系统模板不能删除")
            return

        # 确认删除
        template_name = self._selected_template.get("template_name", "")
        if not messagebox.askyesno(
            "确认删除", f"确定要删除模板 '{template_name}' 吗?"
        ):
            return

        try:
            # 删除模板(这里需要实现服务层的删除方法)
            # success = self._contract_service.delete_template(self._selected_template["id"])

            # 临时实现
            messagebox.showinfo("成功", "模板已删除")

            # 刷新模板列表
            self._refresh_templates()

        except (ServiceError, ValidationError) as e:
            messagebox.showerror("错误", f"删除模板失败:{e}")
        except Exception as e:
            self.logger.error(f"删除模板时发生未知错误: {e}")
            messagebox.showerror("错误", f"删除模板时发生未知错误:{e}")

    def _manage_versions(self) -> None:
        """管理模板版本"""
        if not self._selected_template:
            messagebox.showwarning("提示", "请先选择模板")
            return

        # 切换到版本历史标签页
        # 这里需要获取notebook的引用并切换标签页
        messagebox.showinfo("提示", "版本管理功能已在版本历史标签页中显示")

    def _create_new_version(self) -> None:
        """创建新版本"""
        if not self._selected_template:
            messagebox.showwarning("提示", "请先选择模板")
            return

        # 获取新版本号
        current_version = self._selected_template.get("template_version", "1.0")
        try:
            major, minor = map(int, current_version.split("."))
            new_version = f"{major}.{minor + 1}"
        except:
            new_version = "2.0"

        new_version = simpledialog.askstring(
            "创建新版本",
            "请输入新版本号:",
            initialvalue=new_version,
        )

        if not new_version:
            return

        try:
            # 创建新版本(这里需要实现服务层的版本管理方法)
            messagebox.showinfo("成功", f"已创建新版本: {new_version}")

            # 刷新模板列表
            self._refresh_templates()

        except Exception as e:
            self.logger.error(f"创建新版本时发生错误: {e}")
            messagebox.showerror("错误", f"创建新版本失败:{e}")

    def _activate_template(self) -> None:
        """激活模板"""
        if not self._selected_template:
            return

        try:
            # 激活模板(这里需要实现服务层的状态管理方法)
            messagebox.showinfo("成功", "模板已激活")
            self._refresh_templates()

        except Exception as e:
            messagebox.showerror("错误", f"激活模板失败:{e}")

    def _archive_template(self) -> None:
        """归档模板"""
        if not self._selected_template:
            return

        try:
            # 归档模板(这里需要实现服务层的状态管理方法)
            messagebox.showinfo("成功", "模板已归档")
            self._refresh_templates()

        except Exception as e:
            messagebox.showerror("错误", f"归档模板失败:{e}")

    def _apply_template(self) -> None:
        """应用模板"""
        if not self._selected_template:
            messagebox.showwarning("提示", "请先选择模板")
            return

        # 触发应用事件
        if self.on_template_applied:
            self.on_template_applied(self._selected_template)
        else:
            messagebox.showinfo("提示", "模板应用功能需要在父组件中实现")

    def _preview_template(self) -> None:
        """预览模板"""
        if not self._selected_template:
            return

        # 清空预览框架
        for widget in self._preview_frame.winfo_children():
            widget.destroy()

        # 显示预览内容
        preview_label = ttk.Label(
            self._preview_frame,
            text="模板预览功能将在后续版本中实现",
            font=("Microsoft YaHei UI", 12),
            foreground="gray",
        )
        preview_label.pack(expand=True)

    def _import_template(self) -> None:
        """导入模板"""
        file_path = filedialog.askopenfilename(
            title="导入模板", filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, encoding="utf-8") as f:
                template_data = json.load(f)

            # 验证模板数据
            if (
                not isinstance(template_data, dict)
                or "template_name" not in template_data
            ):
                messagebox.showerror("错误", "无效的模板文件格式")
                return

            # 创建模板
            template = self._contract_service.create_template(template_data)

            messagebox.showinfo("成功", f"模板已导入,ID: {template.id}")

            # 刷新模板列表
            self._refresh_templates()

        except json.JSONDecodeError:
            messagebox.showerror("错误", "模板文件格式错误")
        except (ServiceError, ValidationError) as e:
            messagebox.showerror("错误", f"导入模板失败:{e}")
        except Exception as e:
            self.logger.error(f"导入模板时发生未知错误: {e}")
            messagebox.showerror("错误", f"导入模板时发生未知错误:{e}")

    def _export_template(self) -> None:
        """导出模板"""
        if not self._selected_template:
            messagebox.showwarning("提示", "请先选择要导出的模板")
            return

        # 选择保存位置
        default_filename = (
            f"{self._selected_template.get('template_name', 'template')}.json"
        )
        file_path = filedialog.asksaveasfilename(
            title="导出模板",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            initialvalue=default_filename,
        )

        if not file_path:
            return

        try:
            # 获取完整模板数据
            template_data = self._selected_template.copy()

            # 移除不需要导出的字段
            export_data = {
                k: v
                for k, v in template_data.items()
                if k not in ["id", "created_at", "updated_at", "last_used_at"]
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("成功", f"模板已导出到:\n{file_path}")

        except Exception as e:
            self.logger.error(f"导出模板时发生错误: {e}")
            messagebox.showerror("错误", f"导出模板失败:{e}")

    def _refresh_templates(self) -> None:
        """刷新模板列表"""
        self._load_templates()

    def get_selected_template(self) -> Optional[Dict[str, Any]]:
        """获取选中的模板

        Returns:
            选中的模板数据
        """
        return self._selected_template

    def get_all_templates(self) -> List[Dict[str, Any]]:
        """获取所有模板

        Returns:
            所有模板数据列表
        """
        return self._templates.copy()

    def cleanup(self) -> None:
        """清理资源"""
        self._templates.clear()
        self._selected_template = None
        self._template_versions.clear()
        super().cleanup()


class ContractTemplateEditDialog:
    """合同模板编辑对话框"""

    def __init__(
        self,
        parent: tk.Widget,
        contract_service: ContractService,
        mode: str = "create",
        template_data: Optional[Dict[str, Any]] = None,
    ):
        """初始化模板编辑对话框

        Args:
            parent: 父组件
            contract_service: 合同服务
            mode: 模式 ('create' 或 'edit')
            template_data: 模板数据(编辑模式时使用)
        """
        self.parent = parent
        self.contract_service = contract_service
        self.mode = mode
        self.template_data = template_data or {}

        self.dialog = None
        self.result = False

        # 表单变量
        self.name_var = tk.StringVar(value=self.template_data.get("template_name", ""))
        self.contract_type_var = tk.StringVar(
            value=self.template_data.get("contract_type", ContractType.SALES.value)
        )
        self.version_var = tk.StringVar(
            value=self.template_data.get("template_version", "1.0")
        )
        self.created_by_var = tk.StringVar(
            value=self.template_data.get("created_by", "当前用户")
        )

    def show(self) -> bool:
        """显示对话框

        Returns:
            是否确认保存
        """
        # 创建对话框窗口
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("新建模板" if self.mode == "create" else "编辑模板")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")

        # 创建界面
        self._create_dialog_ui()

        # 等待对话框关闭
        self.dialog.wait_window()

        return self.result

    def _create_dialog_ui(self) -> None:
        """创建对话框界面"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 基本信息区域
        basic_frame = ttk.LabelFrame(main_frame, text="基本信息", padding=10)
        basic_frame.pack(fill=tk.X, pady=(0, 10))

        # 模板名称
        ttk.Label(basic_frame, text="模板名称:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        name_entry = ttk.Entry(basic_frame, textvariable=self.name_var, width=40)
        name_entry.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=5)

        # 合同类型
        ttk.Label(basic_frame, text="合同类型:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        type_combo = ttk.Combobox(
            basic_frame,
            textvariable=self.contract_type_var,
            values=[t.value for t in ContractType],
            state="readonly",
            width=37,
        )
        type_combo.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=5)

        # 版本号
        ttk.Label(basic_frame, text="版本号:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        version_entry = ttk.Entry(basic_frame, textvariable=self.version_var, width=40)
        version_entry.grid(row=2, column=1, sticky=tk.EW, padx=(10, 0), pady=5)

        # 创建者
        ttk.Label(basic_frame, text="创建者:").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        creator_entry = ttk.Entry(
            basic_frame, textvariable=self.created_by_var, width=40
        )
        creator_entry.grid(row=3, column=1, sticky=tk.EW, padx=(10, 0), pady=5)

        basic_frame.grid_columnconfigure(1, weight=1)

        # 模板内容区域
        content_frame = ttk.LabelFrame(main_frame, text="模板内容", padding=10)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 条款模板
        ttk.Label(content_frame, text="条款模板:").pack(anchor=tk.W, pady=(0, 5))
        self.terms_text = tk.Text(content_frame, height=6, wrap=tk.WORD)
        self.terms_text.pack(fill=tk.X, pady=(0, 10))
        self.terms_text.insert("1.0", self.template_data.get("terms_template", ""))

        # 交付条款模板
        ttk.Label(content_frame, text="交付条款模板:").pack(anchor=tk.W, pady=(0, 5))
        self.delivery_text = tk.Text(content_frame, height=4, wrap=tk.WORD)
        self.delivery_text.pack(fill=tk.X, pady=(0, 10))
        self.delivery_text.insert(
            "1.0", self.template_data.get("delivery_terms_template", "")
        )

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        # 取消按钮
        cancel_btn = ttk.Button(button_frame, text="取消", command=self._cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 确定按钮
        ok_btn = ttk.Button(button_frame, text="确定", command=self._save_template)
        ok_btn.pack(side=tk.RIGHT)

        # 设置焦点
        name_entry.focus_set()

    def _save_template(self) -> None:
        """保存模板"""
        # 验证输入
        name = self.name_var.get().strip()
        contract_type = self.contract_type_var.get()
        version = self.version_var.get().strip()
        created_by = self.created_by_var.get().strip()

        if not name:
            messagebox.showerror("错误", "请输入模板名称")
            return

        if not contract_type:
            messagebox.showerror("错误", "请选择合同类型")
            return

        if not version:
            messagebox.showerror("错误", "请输入版本号")
            return

        if not created_by:
            messagebox.showerror("错误", "请输入创建者")
            return

        try:
            template_data = {
                "template_name": name,
                "contract_type": contract_type,
                "template_version": version,
                "created_by": created_by,
                "terms_template": self.terms_text.get("1.0", tk.END).strip(),
                "delivery_terms_template": self.delivery_text.get(
                    "1.0", tk.END
                ).strip(),
                "template_status": TemplateStatus.DRAFT.value,
                "template_type": TemplateType.USER.value,
            }

            if self.mode == "create":
                # 创建新模板
                template = self.contract_service.create_template(template_data)
                messagebox.showinfo("成功", f"模板已创建,ID: {template.id}")
            else:
                # 更新现有模板
                template_data["last_modified_by"] = created_by
                # 这里需要实现更新方法
                messagebox.showinfo("成功", "模板已更新")

            self.result = True
            self.dialog.destroy()

        except (ServiceError, ValidationError) as e:
            messagebox.showerror("错误", f"保存模板失败:{e}")
        except Exception as e:
            messagebox.showerror("错误", f"保存模板时发生未知错误:{e}")

    def _cancel(self) -> None:
        """取消操作"""
        self.result = False
        self.dialog.destroy()
