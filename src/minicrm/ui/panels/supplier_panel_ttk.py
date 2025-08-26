"""MiniCRM 供应商管理面板TTK组件.

实现完整的供应商管理界面,包括:
- 供应商列表显示和管理
- 搜索和筛选功能
- 供应商操作(新增、编辑、删除)
- 供应商详情预览
- 批量操作支持
- 供应商对比和评估功能

设计原则:
- 继承BaseWidget提供标准组件功能
- 集成现有TTK组件(DataTableTTK、SupplierComparisonTTK等)
- 连接SupplierService处理业务逻辑
- 遵循模块化设计和文件大小限制
"""

from __future__ import annotations

import logging
import tkinter as tk
from typing import TYPE_CHECKING

from minicrm.ui.ttk_base.base_widget import BaseWidget


if TYPE_CHECKING:
    from minicrm.services.supplier_service import SupplierService


class SupplierPanelTTK(BaseWidget):
    """供应商管理面板TTK组件.

    提供完整的供应商管理功能:
    - 供应商列表显示和分页
    - 实时搜索和高级筛选
    - 供应商CRUD操作
    - 供应商详情预览
    - 批量操作支持
    - 供应商对比和评估
    """

    def __init__(
        self,
        parent: tk.Widget,
        supplier_service: SupplierService,
        **kwargs,
    ):
        """初始化供应商管理面板.

        Args:
            parent: 父组件
            supplier_service: 供应商服务实例
            **kwargs: 其他参数
        """
        self._supplier_service = supplier_service
        self._logger = logging.getLogger(__name__)

        super().__init__(parent, **kwargs)
        # UI组件引用
        self._search_entry: ttk.Entry | None = None
        self._filter_frame: ttk.Frame | None = None
        self._supplier_table: DataTableTTK | None = None
        self._detail_panel: ttk.Frame | None = None
        self._comparison_panel: SupplierComparisonTTK | None = None
        self._splitter: ttk.PanedWindow | None = None
        self._notebook: ttk.Notebook | None = None

        # 数据状态
        self._current_suppliers: list[dict[str, Any]] = []
        self._selected_supplier_id: int | None = None
        self._search_query: str = ""
        self._current_filters: dict[str, Any] = {}

        # 搜索防抖定时器
        self._search_timer_id: str | None = None

        # 初始化数据
        self._load_suppliers()

    def _setup_ui(self) -> None:
        """设置UI布局."""
        # 创建主容器
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建搜索区域
        self._create_search_area(main_frame)

        # 创建操作工具栏
        self._create_toolbar(main_frame)

        # 创建主要内容区域(使用标签页)
        self._create_main_content(main_frame)

        # 创建状态栏
        self._create_status_bar(main_frame)

    def _create_search_area(self, parent: tk.Widget) -> None:
        """创建搜索区域."""
        search_frame = ttk.LabelFrame(parent, text="搜索和筛选", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        # 搜索输入框
        search_row = ttk.Frame(search_frame)
        search_row.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_row, text="搜索:").pack(side=tk.LEFT, padx=(0, 5))

        self._search_entry = ttk.Entry(search_row, width=30)
        self._search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self._search_entry.bind("<KeyRelease>", self._on_search_changed)

        # 清除搜索按钮
        clear_button = ttk.Button(search_row, text="清除", command=self._clear_search)
        clear_button.pack(side=tk.LEFT, padx=(0, 10))

        # 筛选器区域
        self._create_filters(search_frame)

    def _create_filters(self, parent: tk.Widget) -> None:
        """创建筛选器."""
        self._filter_frame = ttk.Frame(parent)
        self._filter_frame.pack(fill=tk.X)

        # 供应商等级筛选
        level_frame = ttk.Frame(self._filter_frame)
        level_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(level_frame, text="供应商等级:").pack(side=tk.TOP, anchor=tk.W)
        self._level_filter = ttk.Combobox(
            level_frame,
            values=["全部"] + [level.value for level in SupplierLevel],
            state="readonly",
            width=12,
        )
        self._level_filter.set("全部")
        self._level_filter.pack(side=tk.TOP)
        self._level_filter.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # 供应商类型筛选
        type_frame = ttk.Frame(self._filter_frame)
        type_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(type_frame, text="供应商类型:").pack(side=tk.TOP, anchor=tk.W)
        self._type_filter = ttk.Combobox(
            type_frame,
            values=["全部"] + [stype.value for stype in SupplierType],
            state="readonly",
            width=12,
        )
        self._type_filter.set("全部")
        self._type_filter.pack(side=tk.TOP)
        self._type_filter.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # 质量等级筛选
        quality_frame = ttk.Frame(self._filter_frame)
        quality_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(quality_frame, text="质量等级:").pack(side=tk.TOP, anchor=tk.W)
        self._quality_filter = ttk.Combobox(
            quality_frame,
            values=["全部"] + [rating.value for rating in QualityRating],
            state="readonly",
            width=12,
        )
        self._quality_filter.set("全部")
        self._quality_filter.pack(side=tk.TOP)
        self._quality_filter.bind("<<ComboboxSelected>>", self._on_filter_changed)

    def _create_toolbar(self, parent: tk.Widget) -> None:
        """创建操作工具栏."""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))

        # 左侧按钮组
        left_buttons = ttk.Frame(toolbar_frame)
        left_buttons.pack(side=tk.LEFT)

        # 新增供应商按钮
        self._add_button = ttk.Button(
            left_buttons, text="➕ 新增供应商", command=self._on_add_supplier
        )
        self._add_button.pack(side=tk.LEFT, padx=(0, 5))

        # 编辑供应商按钮
        self._edit_button = ttk.Button(
            left_buttons, text="✏️ 编辑供应商", command=self._on_edit_supplier
        )
        self._edit_button.pack(side=tk.LEFT, padx=(0, 5))
        self._edit_button.config(state=tk.DISABLED)

        # 删除供应商按钮
        self._delete_button = ttk.Button(
            left_buttons, text="🗑️ 删除供应商", command=self._on_delete_supplier
        )
        self._delete_button.pack(side=tk.LEFT, padx=(0, 5))
        self._delete_button.config(state=tk.DISABLED)

        # 右侧按钮组
        right_buttons = ttk.Frame(toolbar_frame)
        right_buttons.pack(side=tk.RIGHT)

        # 供应商对比按钮
        self._compare_button = ttk.Button(
            right_buttons, text="🔍 供应商对比", command=self._on_compare_suppliers
        )
        self._compare_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 批量删除按钮
        self._batch_delete_button = ttk.Button(
            right_buttons, text="🗑️ 批量删除", command=self._on_batch_delete
        )
        self._batch_delete_button.pack(side=tk.RIGHT, padx=(5, 0))
        self._batch_delete_button.config(state=tk.DISABLED)

        # 导出按钮
        self._export_button = ttk.Button(
            right_buttons, text="📥 导出", command=self._on_export_suppliers
        )
        self._export_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 刷新按钮
        self._refresh_button = ttk.Button(
            right_buttons, text="🔄 刷新", command=self._on_refresh
        )
        self._refresh_button.pack(side=tk.RIGHT, padx=(5, 0))

    def _create_main_content(self, parent: tk.Widget) -> None:
        """创建主要内容区域."""
        # 创建标签页控件
        self._notebook = ttk.Notebook(parent)
        self._notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 供应商列表标签页
        self._create_supplier_list_tab()

        # 供应商对比标签页
        self._create_comparison_tab()

    def _create_supplier_list_tab(self) -> None:
        """创建供应商列表标签页."""
        list_frame = ttk.Frame(self._notebook)
        self._notebook.add(list_frame, text="供应商列表")

        # 创建分割器(供应商列表 + 详情面板)
        self._splitter = ttk.PanedWindow(list_frame, orient=tk.HORIZONTAL)
        self._splitter.pack(fill=tk.BOTH, expand=True)

        # 创建供应商列表
        self._create_supplier_table()
        self._splitter.add(self._supplier_table, weight=7)

        # 创建详情面板
        self._create_detail_panel()
        self._splitter.add(self._detail_panel, weight=3)

    def _create_comparison_tab(self) -> None:
        """创建供应商对比标签页."""
        comparison_frame = ttk.Frame(self._notebook)
        self._notebook.add(comparison_frame, text="供应商对比")

        # 创建供应商对比组件
        self._comparison_panel = SupplierComparisonTTK(
            comparison_frame, self._supplier_service
        )
        self._comparison_panel.pack(fill=tk.BOTH, expand=True)

    def _create_supplier_table(self) -> None:
        """创建供应商数据表格."""
        # 定义表格列
        columns = [
            {"id": "id", "text": "ID", "width": 60, "anchor": "center"},
            {"id": "name", "text": "供应商名称", "width": 150, "anchor": "w"},
            {"id": "company_name", "text": "公司名称", "width": 150, "anchor": "w"},
            {"id": "contact_person", "text": "联系人", "width": 100, "anchor": "w"},
            {"id": "phone", "text": "联系电话", "width": 120, "anchor": "center"},
            {
                "id": "supplier_level",
                "text": "供应商等级",
                "width": 100,
                "anchor": "center",
            },
            {
                "id": "supplier_type",
                "text": "供应商类型",
                "width": 100,
                "anchor": "center",
            },
            {
                "id": "quality_rating",
                "text": "质量等级",
                "width": 80,
                "anchor": "center",
            },
            {
                "id": "quality_score",
                "text": "质量评分",
                "width": 80,
                "anchor": "center",
            },
            {
                "id": "cooperation_years",
                "text": "合作年限",
                "width": 80,
                "anchor": "center",
            },
            {"id": "created_at", "text": "创建时间", "width": 120, "anchor": "center"},
        ]

        # 创建数据表格
        self._supplier_table = DataTableTTK(
            self._splitter,
            columns=columns,
            multi_select=True,
            show_pagination=True,
            page_size=50,
        )

        # 绑定事件
        self._supplier_table.on_selection_changed = self._on_supplier_selected
        self._supplier_table.on_row_double_clicked = self._on_supplier_double_clicked

    def _create_detail_panel(self) -> None:
        """创建供应商详情面板."""
        self._detail_panel = ttk.LabelFrame(
            self._splitter, text="供应商详情", padding=10
        )

        # 创建滚动区域
        canvas = tk.Canvas(self._detail_panel)
        scrollbar = ttk.Scrollbar(
            self._detail_panel, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 详情内容
        self._detail_content = scrollable_frame

        # 初始显示提示信息
        self._show_detail_placeholder()

    def _create_status_bar(self, parent: tk.Widget) -> None:
        """创建状态栏."""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)

        # 供应商数量标签
        self._status_label = ttk.Label(status_frame, text="就绪")
        self._status_label.pack(side=tk.LEFT)

        # 选择状态标签
        self._selection_label = ttk.Label(status_frame, text="")
        self._selection_label.pack(side=tk.RIGHT)

    def _bind_events(self) -> None:
        """绑定事件处理."""
        # 窗口关闭时清理资源
        self.bind("<Destroy>", self._on_destroy)

    # ==================== 数据加载方法 ====================

    def _load_suppliers(self) -> None:
        """加载供应商数据."""
        try:
            # 从服务层获取供应商数据
            suppliers, total = self._supplier_service.search_suppliers(
                query=self._search_query,
                filters=self._current_filters,
                page=1,
                page_size=1000,  # 暂时加载所有数据
            )

            self._current_suppliers = suppliers

            # 更新表格数据
            if self._supplier_table:
                self._supplier_table.load_data(suppliers)

            # 更新状态栏
            self._update_status_bar(len(suppliers), total)

            self._logger.info(f"成功加载 {len(suppliers)} 个供应商")

        except ServiceError as e:
            self._logger.exception(f"加载供应商数据失败: {e}")
            messagebox.showerror("错误", f"加载供应商数据失败:{e}")
        except Exception as e:
            self._logger.exception(f"加载供应商数据时发生未知错误: {e}")
            messagebox.showerror("错误", f"加载供应商数据时发生未知错误:{e}")

    def _perform_search(self) -> None:
        """执行搜索."""
        try:
            # 获取搜索条件
            query = self._search_query
            filters = self._build_filters()

            # 调用服务层搜索
            suppliers, total = self._supplier_service.search_suppliers(
                query=query,
                filters=filters,
                page=1,
                page_size=1000,
            )

            self._current_suppliers = suppliers

            # 更新表格数据
            if self._supplier_table:
                self._supplier_table.load_data(suppliers)

            # 更新状态栏
            self._update_status_bar(len(suppliers), total)

            self._logger.info(f"搜索完成,找到 {len(suppliers)} 个供应商")

        except ServiceError as e:
            self._logger.exception(f"搜索供应商失败: {e}")
            messagebox.showerror("错误", f"搜索供应商失败:{e}")
        except Exception as e:
            self._logger.exception(f"搜索时发生未知错误: {e}")
            messagebox.showerror("错误", f"搜索时发生未知错误:{e}")

    def _build_filters(self) -> dict[str, Any]:
        """构建筛选条件."""
        filters = {}

        # 供应商等级筛选
        if hasattr(self, "_level_filter") and self._level_filter.get() != "全部":
            filters["supplier_level"] = self._level_filter.get()

        # 供应商类型筛选
        if hasattr(self, "_type_filter") and self._type_filter.get() != "全部":
            filters["supplier_type"] = self._type_filter.get()

        # 质量等级筛选
        if hasattr(self, "_quality_filter") and self._quality_filter.get() != "全部":
            filters["quality_rating"] = self._quality_filter.get()

        return filters

    # ==================== 事件处理方法 ====================

    def _on_search_changed(self, event) -> None:
        """处理搜索输入变化."""
        # 取消之前的定时器
        if self._search_timer_id:
            self.after_cancel(self._search_timer_id)

        # 获取搜索内容
        self._search_query = self._search_entry.get().strip()

        # 设置新的定时器(防抖)
        self._search_timer_id = self.after(300, self._perform_search)

    def _on_filter_changed(self, event) -> None:
        """处理筛选变化."""
        self._perform_search()

    def _clear_search(self) -> None:
        """清除搜索."""
        if self._search_entry:
            self._search_entry.delete(0, tk.END)

        self._search_query = ""
        self._load_suppliers()

    def _on_supplier_selected(self, selected_data: list[dict[str, Any]]) -> None:
        """处理供应商选中."""
        if selected_data:
            supplier_data = selected_data[0]  # 取第一个选中的供应商
            supplier_id = supplier_data.get("id")

            if supplier_id:
                self._selected_supplier_id = supplier_id
                self._update_button_states(True, len(selected_data) > 1)

                # 在详情面板显示供应商信息
                self._show_supplier_detail(supplier_data)

                # 更新选择状态
                self._update_selection_status(len(selected_data))
        else:
            self._selected_supplier_id = None
            self._update_button_states(False, False)
            self._show_detail_placeholder()
            self._update_selection_status(0)

    def _on_supplier_double_clicked(self, supplier_data: dict[str, Any]) -> None:
        """处理供应商双击."""
        self._on_edit_supplier()

    def _update_button_states(
        self, has_selection: bool, multiple_selection: bool
    ) -> None:
        """更新按钮状态."""
        # 单选操作按钮
        state = tk.NORMAL if has_selection else tk.DISABLED
        self._edit_button.config(state=state)
        self._delete_button.config(state=state)

        # 批量操作按钮
        batch_state = tk.NORMAL if multiple_selection else tk.DISABLED
        self._batch_delete_button.config(state=batch_state)

        # 对比按钮(需要至少选择2个供应商)
        compare_state = tk.NORMAL if multiple_selection else tk.DISABLED
        self._compare_button.config(state=compare_state)

    def _show_supplier_detail(self, supplier_data: dict[str, Any]) -> None:
        """显示供应商详情."""
        # 清空现有内容
        for widget in self._detail_content.winfo_children():
            widget.destroy()

        # 基本信息
        basic_frame = ttk.LabelFrame(self._detail_content, text="基本信息", padding=10)
        basic_frame.pack(fill=tk.X, pady=(0, 10))

        # 供应商名称
        name_frame = ttk.Frame(basic_frame)
        name_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            name_frame, text="供应商名称:", font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)
        ttk.Label(name_frame, text=supplier_data.get("name", "-")).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        # 公司名称
        company_frame = ttk.Frame(basic_frame)
        company_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            company_frame, text="公司名称:", font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)
        ttk.Label(company_frame, text=supplier_data.get("company_name", "-")).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        # 联系人
        contact_frame = ttk.Frame(basic_frame)
        contact_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            contact_frame, text="联系人:", font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)
        ttk.Label(contact_frame, text=supplier_data.get("contact_person", "-")).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        # 联系电话
        phone_frame = ttk.Frame(basic_frame)
        phone_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            phone_frame, text="联系电话:", font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)
        ttk.Label(phone_frame, text=supplier_data.get("phone", "-")).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        # 邮箱
        email_frame = ttk.Frame(basic_frame)
        email_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            email_frame, text="邮箱:", font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)
        ttk.Label(email_frame, text=supplier_data.get("email", "-")).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        # 地址
        address_frame = ttk.Frame(basic_frame)
        address_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            address_frame, text="地址:", font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)
        ttk.Label(address_frame, text=supplier_data.get("address", "-")).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        # 分类信息
        category_frame = ttk.LabelFrame(
            self._detail_content, text="分类信息", padding=10
        )
        category_frame.pack(fill=tk.X, pady=(0, 10))

        # 供应商等级
        level_frame = ttk.Frame(category_frame)
        level_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            level_frame, text="供应商等级:", font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)
        ttk.Label(level_frame, text=supplier_data.get("supplier_level", "-")).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        # 供应商类型
        type_frame = ttk.Frame(category_frame)
        type_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            type_frame, text="供应商类型:", font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)
        ttk.Label(type_frame, text=supplier_data.get("supplier_type", "-")).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        # 质量信息
        quality_frame = ttk.LabelFrame(
            self._detail_content, text="质量信息", padding=10
        )
        quality_frame.pack(fill=tk.X, pady=(0, 10))

        # 质量等级
        rating_frame = ttk.Frame(quality_frame)
        rating_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            rating_frame, text="质量等级:", font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)
        ttk.Label(rating_frame, text=supplier_data.get("quality_rating", "-")).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        # 质量评分
        score_frame = ttk.Frame(quality_frame)
        score_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            score_frame, text="质量评分:", font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)
        score_text = (
            f"{supplier_data.get('quality_score', 0):.1f}"
            if supplier_data.get("quality_score")
            else "-"
        )
        ttk.Label(score_frame, text=score_text).pack(side=tk.LEFT, padx=(10, 0))

        # 交期评分
        delivery_frame = ttk.Frame(quality_frame)
        delivery_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            delivery_frame, text="交期评分:", font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)
        delivery_text = (
            f"{supplier_data.get('delivery_rating', 0):.1f}"
            if supplier_data.get("delivery_rating")
            else "-"
        )
        ttk.Label(delivery_frame, text=delivery_text).pack(side=tk.LEFT, padx=(10, 0))

        # 服务评分
        service_frame = ttk.Frame(quality_frame)
        service_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            service_frame, text="服务评分:", font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)
        service_text = (
            f"{supplier_data.get('service_rating', 0):.1f}"
            if supplier_data.get("service_rating")
            else "-"
        )
        ttk.Label(service_frame, text=service_text).pack(side=tk.LEFT, padx=(10, 0))

        # 合作信息
        cooperation_frame = ttk.LabelFrame(
            self._detail_content, text="合作信息", padding=10
        )
        cooperation_frame.pack(fill=tk.X, pady=(0, 10))

        # 合作年限
        years_frame = ttk.Frame(cooperation_frame)
        years_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            years_frame, text="合作年限:", font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)
        years_text = f"{supplier_data.get('cooperation_years', 0)} 年"
        ttk.Label(years_frame, text=years_text).pack(side=tk.LEFT, padx=(10, 0))

        # 总订单数
        orders_frame = ttk.Frame(cooperation_frame)
        orders_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            orders_frame, text="总订单数:", font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)
        ttk.Label(orders_frame, text=str(supplier_data.get("total_orders", 0))).pack(
            side=tk.LEFT, padx=(10, 0)
        )

        # 总交易额
        amount_frame = ttk.Frame(cooperation_frame)
        amount_frame.pack(fill=tk.X, pady=2)
        ttk.Label(
            amount_frame, text="总交易额:", font=("Microsoft YaHei UI", 9, "bold")
        ).pack(side=tk.LEFT)
        amount_text = f"¥{supplier_data.get('total_amount', 0):,.2f}"
        ttk.Label(amount_frame, text=amount_text).pack(side=tk.LEFT, padx=(10, 0))

        # 操作按钮
        button_frame = ttk.Frame(self._detail_content)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        edit_detail_button = ttk.Button(
            button_frame, text="编辑供应商", command=self._on_edit_supplier
        )
        edit_detail_button.pack(side=tk.LEFT, padx=(0, 5))

        view_history_button = ttk.Button(
            button_frame,
            text="查看历史",
            command=lambda: self._on_view_supplier_history(supplier_data.get("id")),
        )
        view_history_button.pack(side=tk.LEFT, padx=(0, 5))

    def _show_detail_placeholder(self) -> None:
        """显示详情面板占位符."""
        # 清空现有内容
        for widget in self._detail_content.winfo_children():
            widget.destroy()

        # 显示提示信息
        placeholder_label = ttk.Label(
            self._detail_content,
            text="请选择一个供应商查看详情",
            font=("Microsoft YaHei UI", 12),
            foreground="gray",
        )
        placeholder_label.pack(expand=True)

    def _update_status_bar(self, displayed_count: int, total_count: int) -> None:
        """更新状态栏."""
        if displayed_count == total_count:
            status_text = f"共 {total_count} 个供应商"
        else:
            status_text = f"显示 {displayed_count} / {total_count} 个供应商"

        if self._status_label:
            self._status_label.config(text=status_text)

    def _update_selection_status(self, selection_count: int) -> None:
        """更新选择状态."""
        if selection_count == 0:
            selection_text = ""
        elif selection_count == 1:
            selection_text = "已选择 1 个供应商"
        else:
            selection_text = f"已选择 {selection_count} 个供应商"

        if self._selection_label:
            self._selection_label.config(text=selection_text)

    # ==================== 操作按钮事件处理 ====================

    def _on_add_supplier(self) -> None:
        """处理新增供应商."""
        # TODO: 实现新增供应商对话框
        messagebox.showinfo("提示", "新增供应商功能将在后续任务中实现")

    def _on_edit_supplier(self) -> None:
        """处理编辑供应商."""
        if not self._selected_supplier_id:
            messagebox.showwarning("提示", "请先选择要编辑的供应商")
            return

        # TODO: 实现编辑供应商对话框
        messagebox.showinfo(
            "提示",
            f"编辑供应商功能将在后续任务中实现\n供应商ID: {self._selected_supplier_id}",
        )

    def _on_delete_supplier(self) -> None:
        """处理删除供应商."""
        if not self._selected_supplier_id:
            messagebox.showwarning("提示", "请先选择要删除的供应商")
            return

        # 确认删除
        result = messagebox.askyesno(
            "确认删除", "确定要删除选中的供应商吗?\n\n此操作不可撤销!", icon="warning"
        )

        if result:
            try:
                success = self._supplier_service.delete_supplier(
                    self._selected_supplier_id
                )
                if success:
                    messagebox.showinfo("成功", "供应商删除成功!")
                    self._load_suppliers()  # 刷新数据
                else:
                    messagebox.showerror("错误", "供应商删除失败")

            except ServiceError as e:
                self._logger.exception(f"删除供应商失败: {e}")
                messagebox.showerror("错误", f"删除供应商失败:{e}")
            except Exception as e:
                self._logger.exception(f"删除供应商时发生未知错误: {e}")
                messagebox.showerror("错误", f"删除供应商时发生未知错误:{e}")

    def _on_batch_delete(self) -> None:
        """处理批量删除供应商."""
        selected_suppliers = (
            self._supplier_table.get_selected_data() if self._supplier_table else []
        )

        if len(selected_suppliers) < 2:
            messagebox.showwarning("提示", "请选择至少2个供应商进行批量删除")
            return

        # 确认删除
        count = len(selected_suppliers)
        result = messagebox.askyesno(
            "确认批量删除",
            f"确定要批量删除选中的 {count} 个供应商吗?\n\n此操作不可撤销!",
            icon="warning",
        )

        if result:
            try:
                deleted_count = 0
                failed_suppliers = []

                for supplier_data in selected_suppliers:
                    supplier_id = supplier_data.get("id")
                    supplier_name = supplier_data.get("name", "未知供应商")

                    if supplier_id:
                        try:
                            success = self._supplier_service.delete_supplier(
                                supplier_id
                            )
                            if success:
                                deleted_count += 1
                            else:
                                failed_suppliers.append(supplier_name)
                        except Exception as e:
                            self._logger.exception(
                                f"删除供应商 {supplier_id} 失败: {e}"
                            )
                            failed_suppliers.append(supplier_name)

                # 刷新数据
                self._load_suppliers()

                # 显示结果
                if failed_suppliers:
                    failed_names = ", ".join(failed_suppliers)
                    messagebox.showwarning(
                        "部分删除失败",
                        f"成功删除 {deleted_count} 个供应商\n\n以下供应商删除失败:\n{failed_names}",
                    )
                else:
                    messagebox.showinfo(
                        "成功", f"成功批量删除 {deleted_count} 个供应商"
                    )

            except Exception as e:
                self._logger.exception(f"批量删除供应商时发生错误: {e}")
                messagebox.showerror("错误", f"批量删除供应商时发生错误:{e}")

    def _on_compare_suppliers(self) -> None:
        """处理供应商对比."""
        selected_suppliers = (
            self._supplier_table.get_selected_data() if self._supplier_table else []
        )

        if len(selected_suppliers) < 2:
            messagebox.showwarning("提示", "请选择至少2个供应商进行对比")
            return

        if len(selected_suppliers) > 4:
            messagebox.showwarning("提示", "最多只能对比4个供应商")
            return

        try:
            # 获取选中供应商的ID列表
            supplier_ids = [s.get("id") for s in selected_suppliers if s.get("id")]

            # 切换到对比标签页
            self._notebook.select(1)  # 选择第二个标签页(供应商对比)

            # 加载供应商到对比组件
            if self._comparison_panel:
                self._comparison_panel.load_suppliers_for_comparison(supplier_ids)

            messagebox.showinfo(
                "成功", f"已加载 {len(supplier_ids)} 个供应商到对比页面"
            )

        except Exception as e:
            self._logger.exception(f"加载供应商对比失败: {e}")
            messagebox.showerror("错误", f"加载供应商对比失败:{e}")

    def _on_export_suppliers(self) -> None:
        """处理导出供应商."""
        if not self._current_suppliers:
            messagebox.showwarning("提示", "没有可导出的供应商数据")
            return

        # TODO: 实现导出功能
        messagebox.showinfo("提示", "导出功能将在后续任务中实现")

    def _on_refresh(self) -> None:
        """处理刷新."""
        self._load_suppliers()
        messagebox.showinfo("提示", "数据已刷新")

    def _on_view_supplier_history(self, supplier_id: int) -> None:
        """查看供应商历史."""
        if not supplier_id:
            return

        # TODO: 实现供应商历史查看功能
        messagebox.showinfo(
            "提示", f"供应商历史查看功能将在后续任务中实现\n供应商ID: {supplier_id}"
        )

    def _on_destroy(self, event) -> None:
        """组件销毁时清理资源."""
        if self._search_timer_id:
            self.after_cancel(self._search_timer_id)

    # ==================== 公共接口方法 ====================

    def refresh_data(self) -> None:
        """刷新数据(公共接口)."""
        self._load_suppliers()

    def select_supplier(self, supplier_id: int) -> None:
        """选中指定供应商(公共接口)."""
        self._selected_supplier_id = supplier_id
        # TODO: 实现选中指定供应商的功能

    def get_selected_supplier_id(self) -> int | None:
        """获取当前选中的供应商ID."""
        return self._selected_supplier_id

    def switch_to_comparison_tab(self) -> None:
        """切换到供应商对比标签页."""
        if self._notebook:
            self._notebook.select(1)

    def switch_to_list_tab(self) -> None:
        """切换到供应商列表标签页."""
        if self._notebook:
            self._notebook.select(0)

    def cleanup(self) -> None:
        """清理资源."""
        if self._search_timer_id:
            self.after_cancel(self._search_timer_id)

        if self._comparison_panel:
            self._comparison_panel.cleanup()

        super().cleanup()
