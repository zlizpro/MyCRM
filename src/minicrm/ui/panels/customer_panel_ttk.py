"""MiniCRM 客户管理面板TTK组件.

实现完整的客户管理界面,包括:
- 客户列表显示和管理
- 搜索和筛选功能
- 客户操作(新增、编辑、删除)
- 客户详情预览
- 批量操作支持

设计原则:
- 继承BaseWidget提供标准组件功能
- 集成现有TTK组件(DataTableTTK、CustomerDetailTTK等)
- 连接CustomerServiceFacade处理业务逻辑
- 遵循模块化设计和文件大小限制
"""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Any

from minicrm.core.exceptions import ServiceError
from minicrm.models.customer import CustomerLevel, CustomerType, IndustryType
from minicrm.ui.panels.customer_detail_ttk import CustomerDetailTTK
from minicrm.ui.panels.customer_edit_dialog_ttk import CustomerEditDialogTTK
from minicrm.ui.ttk_base.base_widget import BaseWidget
from minicrm.ui.ttk_base.data_table_ttk import DataTableTTK


if TYPE_CHECKING:
    from minicrm.services.customer.customer_service_facade import CustomerServiceFacade


class CustomerPanelTTK(BaseWidget):
    """客户管理面板TTK组件.

    提供完整的客户管理功能:
    - 客户列表显示和分页
    - 实时搜索和高级筛选
    - 客户CRUD操作
    - 客户详情预览
    - 批量操作支持
    """

    def __init__(
        self,
        parent: tk.Widget,
        customer_service: CustomerServiceFacade,
        **kwargs,
    ):
        """初始化客户管理面板.

        Args:
            parent: 父组件
            customer_service: 客户服务实例
            **kwargs: 其他参数
        """
        self._customer_service = customer_service
        self._logger = logging.getLogger(__name__)

        # UI组件引用
        self._search_entry: ttk.Entry | None = None
        self._filter_frame: ttk.Frame | None = None
        self._customer_table: DataTableTTK | None = None
        self._detail_panel: CustomerDetailTTK | None = None
        self._splitter: ttk.PanedWindow | None = None

        # 数据状态
        self._current_customers: list[dict[str, Any]] = []
        self._selected_customer_id: int | None = None
        self._search_query: str = ""
        self._current_filters: dict[str, Any] = {}

        # 搜索防抖定时器
        self._search_timer_id: str | None = None

        super().__init__(parent, **kwargs)

        # 初始化数据
        self._load_customers()

    def _setup_ui(self) -> None:
        """设置UI布局."""
        # 创建主容器
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建搜索区域
        self._create_search_area(main_frame)

        # 创建操作工具栏
        self._create_toolbar(main_frame)

        # 创建分割器(客户列表 + 详情面板)
        self._create_splitter(main_frame)

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

        # 客户等级筛选
        level_frame = ttk.Frame(self._filter_frame)
        level_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(level_frame, text="客户等级:").pack(side=tk.TOP, anchor=tk.W)
        self._level_filter = ttk.Combobox(
            level_frame,
            values=["全部"] + [level.value for level in CustomerLevel],
            state="readonly",
            width=12,
        )
        self._level_filter.set("全部")
        self._level_filter.pack(side=tk.TOP)
        self._level_filter.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # 客户类型筛选
        type_frame = ttk.Frame(self._filter_frame)
        type_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(type_frame, text="客户类型:").pack(side=tk.TOP, anchor=tk.W)
        self._type_filter = ttk.Combobox(
            type_frame,
            values=["全部"] + [ctype.value for ctype in CustomerType],
            state="readonly",
            width=12,
        )
        self._type_filter.set("全部")
        self._type_filter.pack(side=tk.TOP)
        self._type_filter.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # 行业类型筛选
        industry_frame = ttk.Frame(self._filter_frame)
        industry_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(industry_frame, text="行业类型:").pack(side=tk.TOP, anchor=tk.W)
        self._industry_filter = ttk.Combobox(
            industry_frame,
            values=["全部"] + [industry.value for industry in IndustryType],
            state="readonly",
            width=12,
        )
        self._industry_filter.set("全部")
        self._industry_filter.pack(side=tk.TOP)
        self._industry_filter.bind("<<ComboboxSelected>>", self._on_filter_changed)

    def _create_toolbar(self, parent: tk.Widget) -> None:
        """创建操作工具栏."""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))

        # 左侧按钮组
        left_buttons = ttk.Frame(toolbar_frame)
        left_buttons.pack(side=tk.LEFT)

        # 新增客户按钮
        self._add_button = ttk.Button(
            left_buttons, text="➕ 新增客户", command=self._on_add_customer
        )
        self._add_button.pack(side=tk.LEFT, padx=(0, 5))

        # 编辑客户按钮
        self._edit_button = ttk.Button(
            left_buttons, text="✏️ 编辑客户", command=self._on_edit_customer
        )
        self._edit_button.pack(side=tk.LEFT, padx=(0, 5))
        self._edit_button.config(state=tk.DISABLED)

        # 删除客户按钮
        self._delete_button = ttk.Button(
            left_buttons, text="🗑️ 删除客户", command=self._on_delete_customer
        )
        self._delete_button.pack(side=tk.LEFT, padx=(0, 5))
        self._delete_button.config(state=tk.DISABLED)

        # 右侧按钮组
        right_buttons = ttk.Frame(toolbar_frame)
        right_buttons.pack(side=tk.RIGHT)

        # 批量删除按钮
        self._batch_delete_button = ttk.Button(
            right_buttons, text="🗑️ 批量删除", command=self._on_batch_delete
        )
        self._batch_delete_button.pack(side=tk.RIGHT, padx=(5, 0))
        self._batch_delete_button.config(state=tk.DISABLED)

        # 导出按钮
        self._export_button = ttk.Button(
            right_buttons, text="📥 导出", command=self._on_export_customers
        )
        self._export_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 刷新按钮
        self._refresh_button = ttk.Button(
            right_buttons, text="🔄 刷新", command=self._on_refresh
        )
        self._refresh_button.pack(side=tk.RIGHT, padx=(5, 0))

    def _create_splitter(self, parent: tk.Widget) -> None:
        """创建分割器(客户列表 + 详情面板)."""
        self._splitter = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        self._splitter.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 创建客户列表
        self._create_customer_table()
        self._splitter.add(self._customer_table, weight=7)

        # 创建详情面板
        self._create_detail_panel()
        self._splitter.add(self._detail_panel, weight=3)

    def _create_customer_table(self) -> None:
        """创建客户数据表格."""
        # 定义表格列
        columns = [
            {"id": "id", "text": "ID", "width": 60, "anchor": "center"},
            {"id": "name", "text": "客户名称", "width": 150, "anchor": "w"},
            {"id": "phone", "text": "联系电话", "width": 120, "anchor": "center"},
            {"id": "company_name", "text": "公司名称", "width": 150, "anchor": "w"},
            {
                "id": "customer_level",
                "text": "客户等级",
                "width": 80,
                "anchor": "center",
            },
            {
                "id": "customer_type",
                "text": "客户类型",
                "width": 80,
                "anchor": "center",
            },
            {
                "id": "industry_type",
                "text": "行业类型",
                "width": 100,
                "anchor": "center",
            },
            {"id": "created_at", "text": "创建时间", "width": 120, "anchor": "center"},
        ]

        # 创建数据表格
        self._customer_table = DataTableTTK(
            self._splitter,
            columns=columns,
            multi_select=True,
            show_pagination=True,
            page_size=50,
        )

        # 绑定事件
        self._customer_table.on_selection_changed = self._on_customer_selected
        self._customer_table.on_row_double_clicked = self._on_customer_double_clicked

    def _create_detail_panel(self) -> None:
        """创建客户详情面板."""
        detail_frame = ttk.LabelFrame(self._splitter, text="客户详情", padding=10)

        # 创建客户详情组件
        self._detail_panel = CustomerDetailTTK(
            detail_frame,
            self._customer_service,
            on_edit_callback=self._on_edit_from_detail,
        )
        self._detail_panel.pack(fill=tk.BOTH, expand=True)

        # 初始显示提示信息
        self._show_detail_placeholder()

    def _create_status_bar(self, parent: tk.Widget) -> None:
        """创建状态栏."""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)

        # 客户数量标签
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

    def _load_customers(self) -> None:
        """加载客户数据."""
        try:
            # 从服务层获取客户数据
            customers, total = self._customer_service.search_customers(
                query=self._search_query,
                filters=self._current_filters,
                page=1,
                page_size=1000,  # 暂时加载所有数据
            )

            self._current_customers = customers

            # 更新表格数据
            if self._customer_table:
                self._customer_table.load_data(customers)

            # 更新状态栏
            self._update_status_bar(len(customers), total)

            self._logger.info(f"成功加载 {len(customers)} 个客户")

        except ServiceError as e:
            self._logger.exception(f"加载客户数据失败: {e}")
            messagebox.showerror("错误", f"加载客户数据失败:{e}")
        except Exception as e:
            self._logger.exception(f"加载客户数据时发生未知错误: {e}")
            messagebox.showerror("错误", f"加载客户数据时发生未知错误:{e}")

    def _perform_search(self) -> None:
        """执行搜索."""
        try:
            # 获取搜索条件
            query = self._search_query
            filters = self._build_filters()

            # 调用服务层搜索
            customers, total = self._customer_service.search_customers(
                query=query,
                filters=filters,
                page=1,
                page_size=1000,
            )

            self._current_customers = customers

            # 更新表格数据
            if self._customer_table:
                self._customer_table.load_data(customers)

            # 更新状态栏
            self._update_status_bar(len(customers), total)

            self._logger.info(f"搜索完成,找到 {len(customers)} 个客户")

        except ServiceError as e:
            self._logger.exception(f"搜索客户失败: {e}")
            messagebox.showerror("错误", f"搜索客户失败:{e}")
        except Exception as e:
            self._logger.exception(f"搜索时发生未知错误: {e}")
            messagebox.showerror("错误", f"搜索时发生未知错误:{e}")

    def _build_filters(self) -> dict[str, Any]:
        """构建筛选条件."""
        filters = {}

        # 客户等级筛选
        if hasattr(self, "_level_filter") and self._level_filter.get() != "全部":
            filters["customer_level"] = self._level_filter.get()

        # 客户类型筛选
        if hasattr(self, "_type_filter") and self._type_filter.get() != "全部":
            filters["customer_type"] = self._type_filter.get()

        # 行业类型筛选
        if hasattr(self, "_industry_filter") and self._industry_filter.get() != "全部":
            filters["industry_type"] = self._industry_filter.get()

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
        self._load_customers()

    def _on_customer_selected(self, selected_data: list[dict[str, Any]]) -> None:
        """处理客户选中."""
        if selected_data:
            customer_data = selected_data[0]  # 取第一个选中的客户
            customer_id = customer_data.get("id")

            if customer_id:
                self._selected_customer_id = customer_id
                self._update_button_states(True, len(selected_data) > 1)

                # 在详情面板显示客户信息
                if self._detail_panel:
                    self._detail_panel.load_customer(customer_id)

                # 更新选择状态
                self._update_selection_status(len(selected_data))
        else:
            self._selected_customer_id = None
            self._update_button_states(False, False)
            self._show_detail_placeholder()
            self._update_selection_status(0)

    def _on_customer_double_clicked(self, customer_data: dict[str, Any]) -> None:
        """处理客户双击."""
        self._on_edit_customer()

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

    def _show_detail_placeholder(self) -> None:
        """显示详情面板占位符."""
        # 这里可以显示一个提示信息,或者清空详情面板

    def _update_status_bar(self, displayed_count: int, total_count: int) -> None:
        """更新状态栏."""
        if displayed_count == total_count:
            status_text = f"共 {total_count} 个客户"
        else:
            status_text = f"显示 {displayed_count} / {total_count} 个客户"

        if self._status_label:
            self._status_label.config(text=status_text)

    def _update_selection_status(self, selection_count: int) -> None:
        """更新选择状态."""
        if selection_count == 0:
            selection_text = ""
        elif selection_count == 1:
            selection_text = "已选择 1 个客户"
        else:
            selection_text = f"已选择 {selection_count} 个客户"

        if self._selection_label:
            self._selection_label.config(text=selection_text)

    # ==================== 操作按钮事件处理 ====================

    def _on_add_customer(self) -> None:
        """处理新增客户."""
        try:
            result = CustomerEditDialogTTK.show_new_customer_dialog(
                parent=self,
                customer_service=self._customer_service,
                on_save_callback=self._on_customer_saved,
            )

            if result:
                self._logger.info(f"新增客户成功: {result}")

        except Exception as e:
            self._logger.exception(f"打开新增客户对话框失败: {e}")
            messagebox.showerror("错误", f"打开新增客户对话框失败:{e}")

    def _on_edit_customer(self) -> None:
        """处理编辑客户."""
        if not self._selected_customer_id:
            messagebox.showwarning("提示", "请先选择要编辑的客户")
            return

        try:
            result = CustomerEditDialogTTK.show_edit_customer_dialog(
                parent=self,
                customer_service=self._customer_service,
                customer_id=self._selected_customer_id,
                on_save_callback=self._on_customer_saved,
            )

            if result:
                self._logger.info(f"编辑客户成功: {result}")

        except Exception as e:
            self._logger.exception(f"打开编辑客户对话框失败: {e}")
            messagebox.showerror("错误", f"打开编辑客户对话框失败:{e}")

    def _on_edit_from_detail(self, customer_id: int) -> None:
        """从详情面板编辑客户."""
        self._selected_customer_id = customer_id
        self._on_edit_customer()

    def _on_delete_customer(self) -> None:
        """处理删除客户."""
        if not self._selected_customer_id:
            messagebox.showwarning("提示", "请先选择要删除的客户")
            return

        # 确认删除
        result = messagebox.askyesno(
            "确认删除", "确定要删除选中的客户吗?\n\n此操作不可撤销!", icon="warning"
        )

        if result:
            try:
                success = self._customer_service.delete_customer(
                    self._selected_customer_id
                )
                if success:
                    messagebox.showinfo("成功", "客户删除成功!")
                    self._load_customers()  # 刷新数据
                else:
                    messagebox.showerror("错误", "客户删除失败")

            except ServiceError as e:
                self._logger.exception(f"删除客户失败: {e}")
                messagebox.showerror("错误", f"删除客户失败:{e}")
            except Exception as e:
                self._logger.exception(f"删除客户时发生未知错误: {e}")
                messagebox.showerror("错误", f"删除客户时发生未知错误:{e}")

    def _on_batch_delete(self) -> None:
        """处理批量删除客户."""
        selected_customers = (
            self._customer_table.get_selected_data() if self._customer_table else []
        )

        if len(selected_customers) < 2:
            messagebox.showwarning("提示", "请选择至少2个客户进行批量删除")
            return

        # 确认删除
        count = len(selected_customers)
        result = messagebox.askyesno(
            "确认批量删除",
            f"确定要批量删除选中的 {count} 个客户吗?\n\n此操作不可撤销!",
            icon="warning",
        )

        if result:
            try:
                deleted_count = 0
                failed_customers = []

                for customer_data in selected_customers:
                    customer_id = customer_data.get("id")
                    customer_name = customer_data.get("name", "未知客户")

                    if customer_id:
                        try:
                            success = self._customer_service.delete_customer(
                                customer_id
                            )
                            if success:
                                deleted_count += 1
                            else:
                                failed_customers.append(customer_name)
                        except Exception as e:
                            self._logger.exception(f"删除客户 {customer_id} 失败: {e}")
                            failed_customers.append(customer_name)

                # 刷新数据
                self._load_customers()

                # 显示结果
                if failed_customers:
                    failed_names = ", ".join(failed_customers)
                    messagebox.showwarning(
                        "部分删除失败",
                        f"成功删除 {deleted_count} 个客户\n\n以下客户删除失败:\n{failed_names}",
                    )
                else:
                    messagebox.showinfo("成功", f"成功批量删除 {deleted_count} 个客户")

            except Exception as e:
                self._logger.exception(f"批量删除客户时发生错误: {e}")
                messagebox.showerror("错误", f"批量删除客户时发生错误:{e}")

    def _on_export_customers(self) -> None:
        """处理导出客户."""
        if not self._current_customers:
            messagebox.showwarning("提示", "没有可导出的客户数据")
            return

        # TODO: 实现导出功能
        messagebox.showinfo("提示", "导出功能将在后续任务中实现")

    def _on_refresh(self) -> None:
        """处理刷新."""
        self._load_customers()
        messagebox.showinfo("提示", "数据已刷新")

    def _on_customer_saved(self, customer_id: int, is_new: bool) -> None:
        """客户保存回调."""
        # 刷新数据
        self._load_customers()

        # 如果是新客户,选中它
        if is_new and self._customer_table:
            # TODO: 实现选中新创建的客户
            pass

    def _on_destroy(self, event) -> None:
        """组件销毁时清理资源."""
        if self._search_timer_id:
            self.after_cancel(self._search_timer_id)

    # ==================== 公共接口方法 ====================

    def refresh_data(self) -> None:
        """刷新数据(公共接口)."""
        self._load_customers()

    def select_customer(self, customer_id: int) -> None:
        """选中指定客户(公共接口)."""
        # TODO: 实现选中指定客户的功能
        self._selected_customer_id = customer_id
        if self._detail_panel:
            self._detail_panel.load_customer(customer_id)

    def get_selected_customer_id(self) -> int | None:
        """获取当前选中的客户ID."""
        return self._selected_customer_id

    def cleanup(self) -> None:
        """清理资源."""
        if self._search_timer_id:
            self.after_cancel(self._search_timer_id)

        if self._detail_panel:
            self._detail_panel.cleanup()

        super().cleanup()
