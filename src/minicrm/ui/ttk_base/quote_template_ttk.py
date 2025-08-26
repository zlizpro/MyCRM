"""MiniCRM TTK报价模板管理组件

基于TTK框架实现的报价模板管理组件,用于替换Qt版本的模板管理功能.
支持模板创建、编辑、删除、预览、应用等完整的模板管理功能.

设计特点:
- 使用TTK组件构建模板管理界面
- 支持多种模板类型和样式
- 提供模板预览和编辑功能
- 集成模板导入导出功能
- 遵循MiniCRM开发标准

作者: MiniCRM开发团队
"""

from datetime import datetime
import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Any, Callable, Dict, List, Optional

from minicrm.core.exceptions import ServiceError, ValidationError
from minicrm.services.quote_template_service import QuoteTemplateService
from minicrm.ui.ttk_base.base_widget import BaseWidget


class QuoteTemplateTTK(BaseWidget):
    """TTK报价模板管理组件

    提供完整的报价模板管理功能:
    - 模板列表显示和管理
    - 模板创建、编辑、删除
    - 模板预览和应用
    - 模板导入导出
    - 默认模板设置
    """

    def __init__(
        self,
        parent: tk.Widget,
        template_service: Optional[QuoteTemplateService] = None,
        **kwargs,
    ):
        """初始化报价模板管理组件

        Args:
            parent: 父组件
            template_service: 模板服务实例,如果为None则自动创建
            **kwargs: 其他参数
        """
        self._template_service = template_service or QuoteTemplateService()

        # 数据存储
        self._templates: List[Dict[str, Any]] = []
        self._selected_template: Optional[Dict[str, Any]] = None

        # UI组件
        self._template_tree: Optional[ttk.Treeview] = None
        self._detail_frame: Optional[ttk.Frame] = None
        self._preview_frame: Optional[ttk.Frame] = None

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
            title_frame, text="报价模板管理", font=("Microsoft YaHei UI", 14, "bold")
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
        columns = ("name", "description", "type", "created_at")
        self._template_tree = ttk.Treeview(
            tree_frame, columns=columns, show="tree headings", selectmode="extended"
        )

        # 配置列
        self._template_tree.heading("#0", text="状态")
        self._template_tree.heading("name", text="模板名称")
        self._template_tree.heading("description", text="描述")
        self._template_tree.heading("type", text="类型")
        self._template_tree.heading("created_at", text="创建时间")

        self._template_tree.column("#0", width=60, minwidth=60)
        self._template_tree.column("name", width=150, minwidth=100)
        self._template_tree.column("description", width=200, minwidth=150)
        self._template_tree.column("type", width=80, minwidth=80)
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

        # 初始化详情显示
        self._show_empty_detail()

    def _load_templates(self) -> None:
        """加载模板数据"""
        try:
            self._templates = self._template_service.get_all_templates()
            self._refresh_template_list()
            self._update_stats()

            self.logger.info(f"加载了 {len(self._templates)} 个模板")

        except ServiceError as e:
            self.logger.error(f"加载模板失败: {e}")
            messagebox.showerror("错误", f"加载模板失败:{e}")
        except Exception as e:
            self.logger.error(f"加载模板时发生未知错误: {e}")
            messagebox.showerror("错误", f"加载模板时发生未知错误:{e}")

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
            if template.get("is_default", False):
                status_icon = "⭐"  # 默认模板
            elif template.get("is_system", False):
                status_icon = "🔒"  # 系统模板
            else:
                status_icon = "📄"  # 普通模板

            # 格式化创建时间
            created_at = template.get("created_at", "")
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    created_at = dt.strftime("%Y-%m-%d")
                except:
                    pass

            # 插入项目
            self._template_tree.insert(
                "",
                "end",
                text=status_icon,
                values=(
                    template.get("name", ""),
                    template.get("description", ""),
                    "系统" if template.get("is_system", False) else "自定义",
                    created_at,
                ),
                tags=("default" if template.get("is_default", False) else "normal",),
            )

        # 配置标签样式
        self._template_tree.tag_configure("default", background="#e6f3ff")

    def _update_stats(self) -> None:
        """更新统计信息"""
        total_count = len(self._templates)
        system_count = sum(1 for t in self._templates if t.get("is_system", False))
        custom_count = total_count - system_count

        stats_text = (
            f"共 {total_count} 个模板 (系统: {system_count}, 自定义: {custom_count})"
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

        # 设置默认
        if self._selected_template and not self._selected_template.get(
            "is_default", False
        ):
            context_menu.add_command(label="设为默认", command=self._set_as_default)

        context_menu.add_separator()
        context_menu.add_command(label="导出模板", command=self._export_template)

        # 删除操作(系统模板不能删除)
        if self._selected_template and not self._selected_template.get(
            "is_system", False
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
            ("模板名称", template.get("name", "")),
            ("描述", template.get("description", "")),
            ("版本", template.get("version", "")),
            ("类型", "系统模板" if template.get("is_system", False) else "自定义模板"),
            ("默认模板", "是" if template.get("is_default", False) else "否"),
            ("创建时间", self._format_datetime(template.get("created_at", ""))),
            ("更新时间", self._format_datetime(template.get("updated_at", ""))),
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

        # 配置信息区域
        config_frame = ttk.LabelFrame(parent, text="配置信息", padding=10)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 显示配置的关键信息
        config = template.get("config", {})
        if config:
            # 页面设置
            page_info = config.get("page_size", "A4")
            margins = config.get("margins", {})
            margin_text = f"上:{margins.get('top', 0)} 下:{margins.get('bottom', 0)} 左:{margins.get('left', 0)} 右:{margins.get('right', 0)}"

            config_info = [
                ("页面大小", page_info),
                ("页边距", margin_text),
                ("主要字体", config.get("fonts", {}).get("default", "SimHei")),
                ("主色调", config.get("colors", {}).get("primary", "#1f4e79")),
            ]

            for label, value in config_info:
                info_frame = ttk.Frame(config_frame)
                info_frame.pack(fill=tk.X, pady=2)

                ttk.Label(info_frame, text=f"{label}:", width=12, anchor=tk.W).pack(
                    side=tk.LEFT
                )
                ttk.Label(info_frame, text=str(value), anchor=tk.W).pack(
                    side=tk.LEFT, fill=tk.X, expand=True
                )

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

        # 设为默认按钮
        if not template.get("is_default", False):
            default_btn = ttk.Button(
                action_frame, text="⭐ 设为默认", command=self._set_as_default
            )
            default_btn.pack(side=tk.LEFT, padx=(0, 5))

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

    def _update_button_states(self) -> None:
        """更新按钮状态"""
        has_selection = self._selected_template is not None
        is_system = (
            self._selected_template.get("is_system", False) if has_selection else False
        )

        # 编辑按钮(系统模板不能编辑)
        self._edit_btn.config(
            state=tk.NORMAL if has_selection and not is_system else tk.DISABLED
        )

        # 复制按钮
        self._copy_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)

        # 删除按钮(系统模板和默认模板不能删除)
        can_delete = (
            has_selection
            and not is_system
            and not self._selected_template.get("is_default", False)
        )
        self._delete_btn.config(state=tk.NORMAL if can_delete else tk.DISABLED)

        # 导出按钮
        self._export_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)

    def _format_datetime(self, datetime_str: str) -> str:
        """格式化日期时间字符串"""
        if not datetime_str:
            return "未知"

        try:
            dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return datetime_str

    # ==================== 模板操作方法 ====================

    def _create_new_template(self) -> None:
        """创建新模板"""
        # 打开模板创建对话框
        dialog = TemplateEditDialog(self, self._template_service, mode="create")
        if dialog.show():
            # 刷新模板列表
            self._refresh_templates()

    def _edit_template(self) -> None:
        """编辑模板"""
        if not self._selected_template:
            messagebox.showwarning("提示", "请先选择要编辑的模板")
            return

        if self._selected_template.get("is_system", False):
            messagebox.showwarning("提示", "系统模板不能编辑")
            return

        # 打开模板编辑对话框
        dialog = TemplateEditDialog(
            self,
            self._template_service,
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
            initialvalue=f"{self._selected_template.get('name', '')} - 副本",
        )

        if not new_name:
            return

        try:
            # 复制模板
            new_template_id = self._template_service.duplicate_template(
                self._selected_template["id"],
                new_name,
                f"复制自 {self._selected_template.get('name', '')}",
            )

            messagebox.showinfo("成功", f"模板已复制,新模板ID: {new_template_id}")

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

        if self._selected_template.get("is_system", False):
            messagebox.showwarning("提示", "系统模板不能删除")
            return

        if self._selected_template.get("is_default", False):
            messagebox.showwarning("提示", "默认模板不能删除")
            return

        # 确认删除
        template_name = self._selected_template.get("name", "")
        if not messagebox.askyesno(
            "确认删除", f"确定要删除模板 '{template_name}' 吗?"
        ):
            return

        try:
            # 删除模板
            success = self._template_service.delete_template(
                self._selected_template["id"]
            )

            if success:
                messagebox.showinfo("成功", "模板已删除")

                # 刷新模板列表
                self._refresh_templates()
            else:
                messagebox.showerror("错误", "删除模板失败")

        except (ServiceError, ValidationError) as e:
            messagebox.showerror("错误", f"删除模板失败:{e}")
        except Exception as e:
            self.logger.error(f"删除模板时发生未知错误: {e}")
            messagebox.showerror("错误", f"删除模板时发生未知错误:{e}")

    def _set_as_default(self) -> None:
        """设置为默认模板"""
        if not self._selected_template:
            messagebox.showwarning("提示", "请先选择模板")
            return

        try:
            # 设置默认模板
            success = self._template_service.set_default_template(
                self._selected_template["id"]
            )

            if success:
                messagebox.showinfo("成功", "已设置为默认模板")

                # 刷新模板列表
                self._refresh_templates()
            else:
                messagebox.showerror("错误", "设置默认模板失败")

        except (ServiceError, ValidationError) as e:
            messagebox.showerror("错误", f"设置默认模板失败:{e}")
        except Exception as e:
            self.logger.error(f"设置默认模板时发生未知错误: {e}")
            messagebox.showerror("错误", f"设置默认模板时发生未知错误:{e}")

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
            if not isinstance(template_data, dict) or "name" not in template_data:
                messagebox.showerror("错误", "无效的模板文件格式")
                return

            # 创建模板
            template_id = self._template_service.create_template(template_data)

            messagebox.showinfo("成功", f"模板已导入,ID: {template_id}")

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

        # 获取完整模板数据
        template_id = self._selected_template["id"]
        full_template = self._template_service.get_template(template_id)

        if not full_template:
            messagebox.showerror("错误", "无法获取模板数据")
            return

        # 选择保存位置
        default_filename = f"{self._selected_template.get('name', 'template')}.json"
        file_path = filedialog.asksaveasfilename(
            title="导出模板",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            initialvalue=default_filename,
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(full_template, f, ensure_ascii=False, indent=2)

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
        super().cleanup()


class TemplateEditDialog:
    """模板编辑对话框"""

    def __init__(
        self,
        parent: tk.Widget,
        template_service: QuoteTemplateService,
        mode: str = "create",
        template_data: Optional[Dict[str, Any]] = None,
    ):
        """初始化模板编辑对话框

        Args:
            parent: 父组件
            template_service: 模板服务
            mode: 模式 ('create' 或 'edit')
            template_data: 模板数据(编辑模式时使用)
        """
        self.parent = parent
        self.template_service = template_service
        self.mode = mode
        self.template_data = template_data or {}

        self.dialog = None
        self.result = False

        # 表单变量
        self.name_var = tk.StringVar(value=self.template_data.get("name", ""))
        self.description_var = tk.StringVar(
            value=self.template_data.get("description", "")
        )
        self.version_var = tk.StringVar(value=self.template_data.get("version", "1.0"))

    def show(self) -> bool:
        """显示对话框

        Returns:
            是否确认保存
        """
        # 创建对话框窗口
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("新建模板" if self.mode == "create" else "编辑模板")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")

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

        # 描述
        ttk.Label(basic_frame, text="描述:").grid(row=1, column=0, sticky=tk.W, pady=5)
        desc_entry = ttk.Entry(basic_frame, textvariable=self.description_var, width=40)
        desc_entry.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=5)

        # 版本
        ttk.Label(basic_frame, text="版本:").grid(row=2, column=0, sticky=tk.W, pady=5)
        version_entry = ttk.Entry(basic_frame, textvariable=self.version_var, width=40)
        version_entry.grid(row=2, column=1, sticky=tk.EW, padx=(10, 0), pady=5)

        basic_frame.grid_columnconfigure(1, weight=1)

        # 配置区域(简化版)
        config_frame = ttk.LabelFrame(main_frame, text="配置信息", padding=10)
        config_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        config_label = ttk.Label(
            config_frame,
            text="详细配置功能将在后续版本中实现\n当前将使用默认配置创建模板",
            foreground="gray",
        )
        config_label.pack(expand=True)

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
        description = self.description_var.get().strip()
        version = self.version_var.get().strip()

        if not name:
            messagebox.showerror("错误", "请输入模板名称")
            return

        if not description:
            messagebox.showerror("错误", "请输入模板描述")
            return

        try:
            template_data = {
                "name": name,
                "description": description,
                "version": version,
            }

            if self.mode == "create":
                # 创建新模板
                template_id = self.template_service.create_template(template_data)
                messagebox.showinfo("成功", f"模板已创建,ID: {template_id}")
            else:
                # 更新现有模板
                success = self.template_service.update_template(
                    self.template_data["id"], template_data
                )
                if success:
                    messagebox.showinfo("成功", "模板已更新")
                else:
                    messagebox.showerror("错误", "更新模板失败")
                    return

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
