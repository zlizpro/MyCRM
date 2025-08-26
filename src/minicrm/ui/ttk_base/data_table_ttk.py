"""MiniCRM TTK数据表格组件.

基于tkinter.ttk.Treeview实现的数据表格组件,用于替换Qt版本的DataTable.
支持数据绑定、排序、筛选、多选、虚拟滚动等功能.

设计特点:
- 使用TTK Treeview作为基础组件
- 模块化设计,支持分页、筛选、导出等功能
- 虚拟滚动支持大数据集显示
- 完整的事件处理和数据绑定机制
"""

from __future__ import annotations

from enum import Enum
import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable

from minicrm.ui.ttk_base.base_widget import BaseWidget
from minicrm.ui.ttk_base.table_export_ttk import TableExportTTK
from minicrm.ui.ttk_base.table_filter_ttk import TableFilterTTK
from minicrm.ui.ttk_base.table_pagination_ttk import TablePaginationTTK


class SortOrder(Enum):
    """排序顺序枚举."""

    ASC = "ascending"
    DESC = "descending"


class VirtualScrollMixin:
    """虚拟滚动混入类 - 支持大数据集的性能优化."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visible_start = 0
        self.visible_count = 50
        self.total_count = 0
        self.item_height = 25
        self._virtual_data = []

    def setup_virtual_scroll(
        self, total_count: int, data: list[dict[str, Any]]
    ) -> None:
        """设置虚拟滚动."""
        self.total_count = total_count
        self._virtual_data = data
        self._update_visible_range()

    def _update_visible_range(self) -> None:
        """更新可见范围."""
        # 计算当前可见的数据范围
        end_index = min(self.visible_start + self.visible_count, self.total_count)
        self._render_visible_items(self.visible_start, end_index)

    def _render_visible_items(self, start: int, end: int) -> None:
        """渲染可见项目 - 子类实现."""

    def _on_scroll(self, _event) -> None:
        """滚动事件处理."""
        # 计算新的可见范围
        # 这里需要根据滚动位置计算新的起始索引


class DataTableTTK(BaseWidget, VirtualScrollMixin):
    """TTK数据表格组件.

    基于tkinter.ttk.Treeview实现的数据表格,提供完整的数据展示和操作功能.
    支持排序、筛选、多选、虚拟滚动等高级功能.
    """

    def __init__(
        self,
        parent,
        columns: list[dict[str, Any]],
        editable: bool = False,
        multi_select: bool = True,
        show_pagination: bool = True,
        page_size: int = 50,
        enable_virtual_scroll: bool = True,
        **kwargs,
    ):
        """初始化数据表格.

        Args:
            parent: 父组件
            columns: 列定义列表,每个元素包含 id, text, width, anchor 等属性
            editable: 是否可编辑
            multi_select: 是否支持多选
            show_pagination: 是否显示分页控件
            page_size: 每页显示的行数
            enable_virtual_scroll: 是否启用虚拟滚动
            **kwargs: 其他参数
        """
        # 初始化混入类
        VirtualScrollMixin.__init__(self)

        # 表格配置
        self.columns = columns
        self.editable = editable
        self.multi_select = multi_select
        self.show_pagination = show_pagination
        self.page_size = page_size
        self.enable_virtual_scroll = enable_virtual_scroll

        # 数据存储
        self.data = []
        self.filtered_data = []
        self.current_page = 1
        self.total_pages = 1

        # 排序状态
        self.sort_column = None
        self.sort_order = SortOrder.ASC

        # UI组件
        self.tree = None
        self.scrollbar_v = None
        self.scrollbar_h = None
        self.pagination_widget = None
        self.filter_widget = None
        self.export_widget = None

        # 事件回调
        self.on_row_selected: Callable | None = None
        self.on_row_double_clicked: Callable | None = None
        self.on_data_changed: Callable | None = None
        self.on_selection_changed: Callable | None = None

        # 日志记录
        self.logger = logging.getLogger(__name__)

        super().__init__(parent, **kwargs)

    def _setup_ui(self) -> None:
        """设置UI布局."""
        # 创建主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建工具栏区域
        self._create_toolbar_area(main_frame)

        # 创建筛选区域
        self._create_filter_area(main_frame)

        # 创建表格区域
        self._create_table_area(main_frame)

        # 创建分页区域
        if self.show_pagination:
            self._create_pagination_area(main_frame)

    def _create_table_area(self, parent) -> None:
        """创建表格区域."""
        # 创建表格框架
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # 创建Treeview
        self.tree = ttk.Treeview(table_frame, show="headings")

        # 配置列
        self._setup_columns()

        # 创建滚动条
        self.scrollbar_v = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.scrollbar_h = ttk.Scrollbar(
            table_frame, orient=tk.HORIZONTAL, command=self.tree.xview
        )

        # 配置滚动
        self.tree.configure(
            yscrollcommand=self.scrollbar_v.set, xscrollcommand=self.scrollbar_h.set
        )

        # 布局
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_v.grid(row=0, column=1, sticky="ns")
        self.scrollbar_h.grid(row=1, column=0, sticky="ew")

        # 配置网格权重
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    def _create_filter_area(self, parent) -> None:
        """创建筛选区域."""
        # 创建筛选组件
        self.filter_widget = TableFilterTTK(
            parent,
            columns=self.columns,
            show_quick_search=True,
            show_advanced_filter=True,
        )
        self.filter_widget.pack(fill=tk.X, pady=(0, 5))

        # 绑定筛选事件
        self.filter_widget.on_filter_changed = self._on_filter_changed

    def _create_toolbar_area(self, parent) -> None:
        """创建工具栏区域."""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))

        # 左侧:信息显示
        info_frame = ttk.Frame(toolbar_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.info_label = ttk.Label(info_frame, text="")
        self.info_label.pack(side=tk.LEFT)

        # 右侧:操作按钮
        button_frame = ttk.Frame(toolbar_frame)
        button_frame.pack(side=tk.RIGHT)

        # 刷新按钮
        refresh_btn = ttk.Button(button_frame, text="🔄 刷新", command=self.refresh)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 导出按钮
        export_btn = ttk.Button(
            button_frame, text="📤 导出", command=self._show_export_dialog
        )
        export_btn.pack(side=tk.LEFT)

        # 创建导出组件
        self.export_widget = TableExportTTK(
            self,
            columns=self.columns,
            enable_excel=True,
            enable_csv=True,
            show_progress=True,
        )

    def _setup_columns(self) -> None:
        """配置表格列."""
        if not self.tree:
            return

        # 设置列ID
        col_ids = [col["id"] for col in self.columns]
        self.tree["columns"] = col_ids

        # 配置每一列
        for col in self.columns:
            col_id = col["id"]

            # 设置列标题和排序
            self.tree.heading(
                col_id,
                text=col.get("text", col_id),
                command=lambda c=col_id: self._sort_by_column(c),
            )

            # 设置列属性
            self.tree.column(
                col_id,
                width=col.get("width", 100),
                anchor=col.get("anchor", "w"),
                minwidth=col.get("minwidth", 50),
            )

    def _create_pagination_area(self, parent) -> None:
        """创建分页区域."""
        # 创建分页组件
        self.pagination_widget = TablePaginationTTK(
            parent,
            page_size=self.page_size,
            show_page_size_selector=True,
            show_page_jumper=True,
            show_total_info=True,
        )
        self.pagination_widget.pack(fill=tk.X, pady=(5, 0))

        # 绑定分页事件
        self.pagination_widget.on_page_changed = self._on_page_changed
        self.pagination_widget.on_page_size_changed = self._on_page_size_changed

    def _bind_events(self) -> None:
        """绑定事件."""
        if not self.tree:
            return

        # 选择事件
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_changed)

        # 双击事件
        self.tree.bind("<Double-1>", self._on_double_click)

        # 右键菜单
        self.tree.bind("<Button-3>", self._show_context_menu)

        # 如果启用虚拟滚动,绑定滚动事件
        if self.enable_virtual_scroll:
            self.tree.bind("<MouseWheel>", self._on_scroll)

    def load_data(self, data: list[dict[str, Any]]) -> None:
        """加载数据到表格.

        Args:
            data: 数据列表,每个元素是包含列数据的字典
        """
        self.data = data.copy()

        # 应用筛选
        self._apply_filters()

        # 更新分页信息
        if self.show_pagination and self.pagination_widget:
            self.pagination_widget.update_pagination(len(self.filtered_data))

        # 刷新显示
        self._refresh_display()

        # 更新信息显示
        self._update_info_display()

        self.logger.info("加载了 %d 条数据到表格", len(data))

    def _refresh_display(self) -> None:
        """刷新表格显示."""
        if not self.tree:
            return

        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 获取当前页数据
        display_data = self._get_current_page_data()

        # 插入数据
        for row_data in display_data:
            values = [row_data.get(col["id"], "") for col in self.columns]
            self.tree.insert("", "end", values=values)

    def _get_current_page_data(self) -> list[dict[str, Any]]:
        """获取当前页的数据."""
        if not self.show_pagination or not self.pagination_widget:
            return self.filtered_data

        start_index, end_index = self.pagination_widget.get_current_page_range()
        return self.filtered_data[start_index:end_index]

    def _sort_by_column(self, column_id: str) -> None:
        """按列排序."""
        # 切换排序顺序
        if self.sort_column == column_id:
            self.sort_order = (
                SortOrder.DESC if self.sort_order == SortOrder.ASC else SortOrder.ASC
            )
        else:
            self.sort_column = column_id
            self.sort_order = SortOrder.ASC

        # 执行排序
        reverse = self.sort_order == SortOrder.DESC
        self.filtered_data.sort(key=lambda x: x.get(column_id, ""), reverse=reverse)

        # 刷新显示
        self._refresh_display()

        self.logger.info("按列 %s 排序,顺序: %s", column_id, self.sort_order.value)

    def _on_selection_changed(self, _event) -> None:
        """处理选择变化事件."""
        selected_items = self.tree.selection()

        if self.on_selection_changed:
            # 获取选中行的数据
            selected_data = []
            for item in selected_items:
                values = self.tree.item(item, "values")
                row_data = {}
                for i, col in enumerate(self.columns):
                    if i < len(values):
                        row_data[col["id"]] = values[i]
                selected_data.append(row_data)

            self.on_selection_changed(selected_data)

        # 如果有单行选择回调
        if self.on_row_selected and selected_items:
            item = selected_items[0]
            values = self.tree.item(item, "values")
            row_data = {}
            for i, col in enumerate(self.columns):
                if i < len(values):
                    row_data[col["id"]] = values[i]
            self.on_row_selected(row_data)

    def _on_double_click(self, _event) -> None:
        """处理双击事件."""
        if not self.on_row_double_clicked:
            return

        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            values = self.tree.item(item, "values")
            row_data = {}
            for i, col in enumerate(self.columns):
                if i < len(values):
                    row_data[col["id"]] = values[i]
            self.on_row_double_clicked(row_data)

    def _show_context_menu(self, event) -> None:
        """显示右键菜单."""
        # 基础右键菜单实现
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="刷新", command=self.refresh)
        menu.add_separator()
        menu.add_command(label="导出选中", command=self._export_selected)
        menu.add_command(label="导出全部", command=self._export_all)

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _export_selected(self) -> None:
        """导出选中数据."""
        selected_data = self.get_selected_data()
        if not selected_data:
            messagebox.showwarning("导出警告", "请先选择要导出的数据")
            return

        if self.export_widget:
            self.export_widget.show_export_dialog(
                data=self.filtered_data,
                selected_data=selected_data,
                current_page_data=self._get_current_page_data(),
            )

    def _export_all(self) -> None:
        """导出全部数据."""
        if not self.filtered_data:
            messagebox.showwarning("导出警告", "没有数据可以导出")
            return

        if self.export_widget:
            self.export_widget.show_export_dialog(
                data=self.filtered_data,
                selected_data=None,
                current_page_data=self._get_current_page_data(),
            )

    def _show_export_dialog(self) -> None:
        """显示导出对话框."""
        if not self.filtered_data:
            messagebox.showwarning("导出警告", "没有数据可以导出")
            return

        if self.export_widget:
            self.export_widget.show_export_dialog(
                data=self.filtered_data,
                selected_data=self.get_selected_data(),
                current_page_data=self._get_current_page_data(),
            )

    def refresh(self) -> None:
        """刷新表格."""
        self._refresh_display()

    def get_selected_data(self) -> list[dict[str, Any]]:
        """获取选中行的数据."""
        selected_items = self.tree.selection()
        selected_data = []

        for item in selected_items:
            values = self.tree.item(item, "values")
            row_data = {}
            for i, col in enumerate(self.columns):
                if i < len(values):
                    row_data[col["id"]] = values[i]
            selected_data.append(row_data)

        return selected_data

    def select_all(self) -> None:
        """全选."""
        if self.multi_select:
            self.tree.selection_set(self.tree.get_children())

    def clear_selection(self) -> None:
        """清除选择."""
        self.tree.selection_remove(self.tree.selection())

    def _apply_filters(self) -> None:
        """应用筛选条件."""
        if self.filter_widget:
            self.filtered_data = self.filter_widget.apply_filters(self.data)
        else:
            self.filtered_data = self.data.copy()

    def _on_filter_changed(self) -> None:
        """处理筛选变化事件."""
        # 应用筛选
        self._apply_filters()

        # 重置到第一页
        if self.pagination_widget:
            self.pagination_widget.reset_to_first_page()
            self.pagination_widget.update_pagination(len(self.filtered_data))

        # 刷新显示
        self._refresh_display()

        # 更新信息显示
        self._update_info_display()

        self.logger.info(
            "筛选后数据: %d/%d 条记录", len(self.filtered_data), len(self.data)
        )

    def _on_page_changed(self, page: int, page_size: int) -> None:
        """处理页面变化事件."""
        self._refresh_display()
        self.logger.info("切换到第 %d 页,每页 %d 条记录", page, page_size)

    def _on_page_size_changed(self, page_size: int) -> None:
        """处理页面大小变化事件."""
        self.page_size = page_size
        self._refresh_display()
        self.logger.info("页面大小已更改为: %d", page_size)

    def _update_info_display(self) -> None:
        """更新信息显示."""
        if hasattr(self, "info_label") and self.info_label:
            total_records = len(self.data)
            filtered_records = len(self.filtered_data)

            if total_records == filtered_records:
                info_text = f"共 {total_records} 条记录"
            else:
                info_text = f"显示 {filtered_records} / {total_records} 条记录"

            self.info_label.config(text=info_text)

    def cleanup(self) -> None:
        """清理资源."""
        self.data.clear()
        self.filtered_data.clear()
        if self.tree:
            for item in self.tree.get_children():
                self.tree.delete(item)

        # 清理子组件
        if self.filter_widget:
            self.filter_widget.cleanup()
        if self.pagination_widget:
            self.pagination_widget.cleanup()
        if self.export_widget:
            self.export_widget.cleanup()

        self.logger.info("数据表格资源已清理")


# 为了保持向后兼容性,提供别名
DataTable = DataTableTTK
