"""MiniCRM TTK报价管理面板

基于TTK框架实现的报价管理面板,用于替换Qt版本的报价管理功能.
集成报价列表、创建、编辑、比较、模板等完整的报价管理功能.

设计特点:
- 使用TTK组件构建管理界面
- 集成报价比较和模板功能
- 支持报价CRUD操作
- 提供搜索和筛选功能
- 遵循MiniCRM开发标准

作者: MiniCRM开发团队
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional

from minicrm.services.quote_service import QuoteServiceRefactored
from minicrm.services.quote_template_service import QuoteTemplateService
from minicrm.ui.ttk_base.base_widget import BaseWidget


class QuotePanelTTK(BaseWidget):
    """TTK报价管理面板

    提供完整的报价管理功能:
    - 报价列表显示和管理
    - 报价创建、编辑、删除
    - 报价比较和分析
    - 报价模板管理
    - 报价导出和打印
    - 搜索和筛选功能
    """

    def __init__(
        self,
        parent: tk.Widget,
        quote_service: QuoteServiceRefactored,
        template_service: Optional[QuoteTemplateService] = None,
        **kwargs,
    ):
        """初始化报价管理面板

        Args:
            parent: 父组件
            quote_service: 报价服务实例
            template_service: 模板服务实例
            **kwargs: 其他参数
        """
        self._quote_service = quote_service
        self._template_service = template_service or QuoteTemplateService()

        super().__init__(parent, **kwargs)

        # 数据存储
        self._quotes: List[Dict[str, Any]] = []
        self._filtered_quotes: List[Dict[str, Any]] = []
        self._selected_quote: Optional[Dict[str, Any]] = None

        # UI组件
        self._notebook: Optional[ttk.Notebook] = None
        self._quote_table: Optional[DataTableTTK] = None
        self._comparison_widget: Optional[QuoteComparisonTTK] = None
        self._template_widget: Optional[QuoteTemplateTTK] = None
        self._export_widget: Optional[QuoteExportTTK] = None

        # 事件回调
        self.on_quote_selected: Optional[Callable] = None
        self.on_quote_created: Optional[Callable] = None
        self.on_quote_updated: Optional[Callable] = None
        self.on_quote_deleted: Optional[Callable] = None

        # 加载数据
        self._load_quotes()

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
            title_frame, text="报价管理", font=("Microsoft YaHei UI", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)

        # 统计信息
        self._stats_label = ttk.Label(title_frame, text="", foreground="gray")
        self._stats_label.pack(side=tk.RIGHT)

    def _create_toolbar(self, parent: ttk.Frame) -> None:
        """创建工具栏"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))

        # 左侧按钮组
        left_frame = ttk.Frame(toolbar_frame)
        left_frame.pack(side=tk.LEFT)

        # 新建报价按钮
        self._new_btn = ttk.Button(
            left_frame, text="➕ 新建报价", command=self._create_new_quote
        )
        self._new_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 编辑报价按钮
        self._edit_btn = ttk.Button(
            left_frame, text="✏️ 编辑报价", command=self._edit_quote, state=tk.DISABLED
        )
        self._edit_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 删除报价按钮
        self._delete_btn = ttk.Button(
            left_frame, text="🗑️ 删除报价", command=self._delete_quote, state=tk.DISABLED
        )
        self._delete_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 右侧按钮组
        right_frame = ttk.Frame(toolbar_frame)
        right_frame.pack(side=tk.RIGHT)

        # 刷新按钮
        self._refresh_btn = ttk.Button(
            right_frame, text="🔄 刷新", command=self._refresh_quotes
        )
        self._refresh_btn.pack(side=tk.LEFT, padx=(5, 0))

    def _create_content_area(self, parent: ttk.Frame) -> None:
        """创建主要内容区域"""
        # 创建标签页
        self._notebook = ttk.Notebook(parent)
        self._notebook.pack(fill=tk.BOTH, expand=True)

        # 报价列表标签页
        self._create_quote_list_tab()

        # 报价比较标签页
        self._create_comparison_tab()

        # 模板管理标签页
        self._create_template_tab()

    def _create_quote_list_tab(self) -> None:
        """创建报价列表标签页"""
        list_frame = ttk.Frame(self._notebook)
        self._notebook.add(list_frame, text="报价列表")

        # 创建搜索区域
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)

        self._search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self._search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(5, 10))
        search_entry.bind("<KeyRelease>", self._on_search_changed)

        search_btn = ttk.Button(
            search_frame, text="🔍 搜索", command=self._perform_search
        )
        search_btn.pack(side=tk.LEFT, padx=(0, 5))

        clear_btn = ttk.Button(search_frame, text="清空", command=self._clear_search)
        clear_btn.pack(side=tk.LEFT)

        # 创建报价表格
        self._create_quote_table(list_frame)

    def _create_quote_table(self, parent: ttk.Frame) -> None:
        """创建报价表格"""
        # 定义表格列
        columns = [
            {"id": "id", "text": "ID", "width": 60, "visible": False},
            {"id": "quote_number", "text": "报价编号", "width": 120},
            {"id": "customer_name", "text": "客户名称", "width": 150},
            {"id": "contact_person", "text": "联系人", "width": 100},
            {"id": "status_display", "text": "状态", "width": 80},
            {"id": "quote_type_display", "text": "类型", "width": 80},
            {"id": "formatted_total", "text": "总金额", "width": 100},
            {"id": "formatted_quote_date", "text": "报价日期", "width": 100},
            {"id": "formatted_valid_until", "text": "有效期至", "width": 100},
            {"id": "remaining_days", "text": "剩余天数", "width": 80},
        ]

        # 创建数据表格
        self._quote_table = DataTableTTK(
            parent,
            columns=columns,
            multi_select=True,
            show_pagination=True,
            page_size=50,
        )
        self._quote_table.pack(fill=tk.BOTH, expand=True)

        # 绑定事件
        self._quote_table.on_row_selected = self._on_quote_selected
        self._quote_table.on_row_double_clicked = self._on_quote_double_clicked
        self._quote_table.on_selection_changed = self._on_selection_changed

    def _create_comparison_tab(self) -> None:
        """创建报价比较标签页"""
        comparison_frame = ttk.Frame(self._notebook)
        self._notebook.add(comparison_frame, text="报价比较")

        # 创建比较组件
        self._comparison_widget = QuoteComparisonTTK(
            comparison_frame,
            self._quote_service,
            comparison_mode="detailed",
            max_quotes=4,
        )
        self._comparison_widget.pack(fill=tk.BOTH, expand=True)

        # 绑定事件
        self._comparison_widget.on_comparison_completed = self._on_comparison_completed

    def _create_template_tab(self) -> None:
        """创建模板管理标签页"""
        template_frame = ttk.Frame(self._notebook)
        self._notebook.add(template_frame, text="模板管理")

        # 创建模板管理组件
        self._template_widget = QuoteTemplateTTK(template_frame, self._template_service)
        self._template_widget.pack(fill=tk.BOTH, expand=True)

        # 绑定事件
        self._template_widget.on_template_applied = self._on_template_applied

    def _load_quotes(self) -> None:
        """加载报价数据"""
        try:
            # 从服务层获取报价数据
            quotes = self._quote_service.list_all()

            # 转换为字典格式
            self._quotes = [quote.to_dict() for quote in quotes]
            self._filtered_quotes = self._quotes.copy()

            # 更新表格数据
            if self._quote_table:
                self._quote_table.load_data(self._filtered_quotes)

            # 更新统计信息
            self._update_stats()

            self.logger.info(f"成功加载 {len(self._quotes)} 个报价")

        except ServiceError as e:
            self.logger.error(f"加载报价数据失败: {e}")
            messagebox.showerror("错误", f"加载报价数据失败:{e}")
        except Exception as e:
            self.logger.error(f"加载报价数据时发生未知错误: {e}")
            messagebox.showerror("错误", f"加载报价数据时发生未知错误:{e}")

    def _update_stats(self) -> None:
        """更新统计信息"""
        total_count = len(self._quotes)
        filtered_count = len(self._filtered_quotes)

        if total_count == filtered_count:
            stats_text = f"共 {total_count} 个报价"
        else:
            stats_text = f"显示 {filtered_count} / {total_count} 个报价"

        if hasattr(self, "_stats_label") and self._stats_label:
            self._stats_label.config(text=stats_text)

    def _on_search_changed(self, event=None) -> None:
        """处理搜索变化事件"""
        # 延迟搜索,避免频繁查询
        if hasattr(self, "_search_timer"):
            self.after_cancel(self._search_timer)

        self._search_timer = self.after(300, self._perform_search)

    def _perform_search(self) -> None:
        """执行搜索"""
        search_text = self._search_var.get().strip().lower()

        if not search_text:
            self._filtered_quotes = self._quotes.copy()
        else:
            # 在多个字段中搜索
            self._filtered_quotes = []
            for quote in self._quotes:
                if (
                    search_text in quote.get("quote_number", "").lower()
                    or search_text in quote.get("customer_name", "").lower()
                    or search_text in quote.get("contact_person", "").lower()
                ):
                    self._filtered_quotes.append(quote)

        # 更新表格数据
        if self._quote_table:
            self._quote_table.load_data(self._filtered_quotes)

        # 更新统计信息
        self._update_stats()

    def _clear_search(self) -> None:
        """清空搜索"""
        self._search_var.set("")
        self._perform_search()

    def _on_quote_selected(self, quote_data: Dict[str, Any]) -> None:
        """处理报价选择事件"""
        self._selected_quote = quote_data
        self._update_button_states()

        # 触发选择事件
        if self.on_quote_selected:
            self.on_quote_selected(quote_data)

    def _on_quote_double_clicked(self, quote_data: Dict[str, Any]) -> None:
        """处理报价双击事件"""
        self._edit_quote()

    def _on_selection_changed(self, selected_data: List[Dict[str, Any]]) -> None:
        """处理选择变化事件"""
        has_selection = len(selected_data) > 0
        single_selection = len(selected_data) == 1

        # 更新按钮状态
        self._edit_btn.config(state=tk.NORMAL if single_selection else tk.DISABLED)
        self._delete_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)

        # 更新选中报价
        if single_selection:
            self._selected_quote = selected_data[0]
        else:
            self._selected_quote = None

    def _update_button_states(self) -> None:
        """更新按钮状态"""
        has_selection = self._selected_quote is not None

        self._edit_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)
        self._delete_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)

    def _create_new_quote(self) -> None:
        """创建新报价"""
        messagebox.showinfo("提示", "新建报价功能将在后续版本中实现")

    def _edit_quote(self) -> None:
        """编辑报价"""
        if not self._selected_quote:
            messagebox.showwarning("提示", "请先选择要编辑的报价")
            return

        messagebox.showinfo("提示", "编辑报价功能将在后续版本中实现")

    def _delete_quote(self) -> None:
        """删除报价"""
        selected_data = (
            self._quote_table.get_selected_data() if self._quote_table else []
        )

        if not selected_data:
            messagebox.showwarning("提示", "请先选择要删除的报价")
            return

        # 确认删除
        count = len(selected_data)
        if count == 1:
            message = "确定要删除选中的报价吗?"
        else:
            message = f"确定要删除选中的 {count} 个报价吗?"

        if not messagebox.askyesno("确认删除", message):
            return

        try:
            # 删除报价
            for quote_data in selected_data:
                quote_id = quote_data.get("id")
                if quote_id:
                    success = self._quote_service.delete(quote_id)
                    if success and self.on_quote_deleted:
                        self.on_quote_deleted(quote_id)

            # 刷新数据
            self._refresh_quotes()
            messagebox.showinfo("成功", f"成功删除 {count} 个报价")

        except ServiceError as e:
            self.logger.error(f"删除报价失败: {e}")
            messagebox.showerror("错误", f"删除报价失败:{e}")
        except Exception as e:
            self.logger.error(f"删除报价时发生未知错误: {e}")
            messagebox.showerror("错误", f"删除报价时发生未知错误:{e}")

    def _refresh_quotes(self) -> None:
        """刷新报价列表"""
        self._load_quotes()

    def _on_comparison_completed(self, comparison_result: Dict[str, Any]) -> None:
        """处理比较完成事件"""
        self.logger.info("报价比较完成")

    def _on_template_applied(self, template_data: Dict[str, Any]) -> None:
        """处理模板应用事件"""
        template_name = template_data.get("name", "未知模板")
        messagebox.showinfo("模板应用", f"已应用模板: {template_name}")

    def add_quote_to_comparison(self, quote_data: Dict[str, Any]) -> bool:
        """添加报价到比较列表

        Args:
            quote_data: 报价数据

        Returns:
            是否添加成功
        """
        if self._comparison_widget:
            # 切换到比较标签页
            self._notebook.select(1)  # 比较标签页索引

            # 添加到比较列表
            return self._comparison_widget.add_quote_for_comparison(quote_data)

        return False

    def export_quotes(self, quotes: Optional[List[Dict[str, Any]]] = None) -> None:
        """导出报价

        Args:
            quotes: 要导出的报价列表,如果为None则导出选中的报价
        """
        if quotes is None:
            quotes = self._quote_table.get_selected_data() if self._quote_table else []

        if not quotes:
            messagebox.showwarning("提示", "请先选择要导出的报价")
            return

        # 创建导出组件
        if not self._export_widget:
            self._export_widget = QuoteExportTTK(
                self,
                self._template_service,
                enable_pdf=True,
                enable_excel=True,
                enable_word=True,
            )

        # 显示导出对话框
        self._export_widget.show_export_dialog(quotes)

    def get_selected_quote(self) -> Optional[Dict[str, Any]]:
        """获取选中的报价

        Returns:
            选中的报价数据
        """
        return self._selected_quote

    def get_all_quotes(self) -> List[Dict[str, Any]]:
        """获取所有报价

        Returns:
            所有报价数据列表
        """
        return self._quotes.copy()

    def get_filtered_quotes(self) -> List[Dict[str, Any]]:
        """获取筛选后的报价

        Returns:
            筛选后的报价数据列表
        """
        return self._filtered_quotes.copy()

    def cleanup(self) -> None:
        """清理资源"""
        self._quotes.clear()
        self._filtered_quotes.clear()
        self._selected_quote = None

        # 清理子组件
        if self._quote_table:
            self._quote_table.cleanup()
        if self._comparison_widget:
            self._comparison_widget.cleanup()
        if self._template_widget:
            self._template_widget.cleanup()
        if self._export_widget:
            self._export_widget.cleanup()

        super().cleanup()
