"""MiniCRM TTK表格筛选组件

提供完整的表格数据筛选功能,包括快速搜索、高级筛选、筛选历史等.
支持多种筛选条件和复合筛选,适用于板材行业的业务需求.

设计特点:
- 快速搜索功能
- 高级筛选条件设置
- 筛选历史记录
- 实时筛选反馈
- 可扩展的筛选规则
"""

from enum import Enum
import logging
import re
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional

from minicrm.ui.ttk_base.base_widget import BaseWidget


class FilterOperator(Enum):
    """筛选操作符枚举"""

    EQUALS = "等于"
    NOT_EQUALS = "不等于"
    CONTAINS = "包含"
    NOT_CONTAINS = "不包含"
    STARTS_WITH = "开头是"
    ENDS_WITH = "结尾是"
    GREATER_THAN = "大于"
    GREATER_EQUAL = "大于等于"
    LESS_THAN = "小于"
    LESS_EQUAL = "小于等于"
    BETWEEN = "介于"
    IN_LIST = "在列表中"
    NOT_IN_LIST = "不在列表中"
    IS_EMPTY = "为空"
    IS_NOT_EMPTY = "不为空"
    REGEX = "正则表达式"


class FilterCondition:
    """筛选条件类"""

    def __init__(
        self,
        column_id: str,
        operator: FilterOperator,
        value: Any = None,
        value2: Any = None,
        case_sensitive: bool = False,
    ):
        self.column_id = column_id
        self.operator = operator
        self.value = value
        self.value2 = value2  # 用于BETWEEN操作
        self.case_sensitive = case_sensitive

    def apply(self, row_data: Dict[str, Any]) -> bool:
        """应用筛选条件到行数据

        Args:
            row_data: 行数据字典

        Returns:
            是否满足筛选条件
        """
        cell_value = row_data.get(self.column_id, "")

        # 转换为字符串进行比较
        cell_str = str(cell_value) if cell_value is not None else ""
        filter_str = str(self.value) if self.value is not None else ""

        # 大小写处理
        if not self.case_sensitive:
            cell_str = cell_str.lower()
            filter_str = filter_str.lower()

        try:
            if self.operator == FilterOperator.EQUALS:
                return cell_str == filter_str
            if self.operator == FilterOperator.NOT_EQUALS:
                return cell_str != filter_str
            if self.operator == FilterOperator.CONTAINS:
                return filter_str in cell_str
            if self.operator == FilterOperator.NOT_CONTAINS:
                return filter_str not in cell_str
            if self.operator == FilterOperator.STARTS_WITH:
                return cell_str.startswith(filter_str)
            if self.operator == FilterOperator.ENDS_WITH:
                return cell_str.endswith(filter_str)
            if self.operator == FilterOperator.GREATER_THAN:
                return self._numeric_compare(cell_value, self.value, ">")
            if self.operator == FilterOperator.GREATER_EQUAL:
                return self._numeric_compare(cell_value, self.value, ">=")
            if self.operator == FilterOperator.LESS_THAN:
                return self._numeric_compare(cell_value, self.value, "<")
            if self.operator == FilterOperator.LESS_EQUAL:
                return self._numeric_compare(cell_value, self.value, "<=")
            if self.operator == FilterOperator.BETWEEN:
                return self._between_compare(cell_value, self.value, self.value2)
            if self.operator == FilterOperator.IN_LIST:
                return self._in_list_compare(cell_str, filter_str)
            if self.operator == FilterOperator.NOT_IN_LIST:
                return not self._in_list_compare(cell_str, filter_str)
            if self.operator == FilterOperator.IS_EMPTY:
                return cell_str == "" or cell_value is None
            if self.operator == FilterOperator.IS_NOT_EMPTY:
                return cell_str != "" and cell_value is not None
            if self.operator == FilterOperator.REGEX:
                return bool(re.search(filter_str, cell_str))
            return True

        except Exception as e:
            logging.getLogger(__name__).warning(f"筛选条件应用失败: {e}")
            return True

    def _numeric_compare(
        self, cell_value: Any, filter_value: Any, operator: str
    ) -> bool:
        """数值比较"""
        try:
            cell_num = float(cell_value) if cell_value != "" else 0
            filter_num = float(filter_value) if filter_value != "" else 0

            if operator == ">":
                return cell_num > filter_num
            if operator == ">=":
                return cell_num >= filter_num
            if operator == "<":
                return cell_num < filter_num
            if operator == "<=":
                return cell_num <= filter_num

        except (ValueError, TypeError):
            return False

        return False

    def _between_compare(self, cell_value: Any, min_value: Any, max_value: Any) -> bool:
        """区间比较"""
        try:
            cell_num = float(cell_value) if cell_value != "" else 0
            min_num = float(min_value) if min_value != "" else float("-inf")
            max_num = float(max_value) if max_value != "" else float("inf")

            return min_num <= cell_num <= max_num

        except (ValueError, TypeError):
            return False

    def _in_list_compare(self, cell_str: str, filter_str: str) -> bool:
        """列表包含比较"""
        # 支持逗号分隔的列表
        filter_list = [item.strip() for item in filter_str.split(",")]
        return cell_str in filter_list


class TableFilterTTK(BaseWidget):
    """TTK表格筛选组件

    提供完整的表格数据筛选功能,支持快速搜索和高级筛选.
    可以独立使用,也可以集成到DataTableTTK中.
    """

    def __init__(
        self,
        parent,
        columns: List[Dict[str, Any]],
        show_quick_search: bool = True,
        show_advanced_filter: bool = True,
        enable_filter_history: bool = True,
        **kwargs,
    ):
        """初始化筛选组件

        Args:
            parent: 父组件
            columns: 列定义列表
            show_quick_search: 是否显示快速搜索
            show_advanced_filter: 是否显示高级筛选
            enable_filter_history: 是否启用筛选历史
        """
        # 筛选配置
        self.columns = columns
        self.show_quick_search = show_quick_search
        self.show_advanced_filter = show_advanced_filter
        self.enable_filter_history = enable_filter_history

        # 筛选状态
        self.filter_conditions: List[FilterCondition] = []
        self.quick_search_text = ""
        self.filter_history: List[Dict[str, Any]] = []

        # UI组件
        self.search_entry = None
        self.search_column_combo = None
        self.advanced_filter_frame = None
        self.filter_conditions_frame = None
        self.add_condition_btn = None
        self.clear_filters_btn = None
        self.apply_filters_btn = None

        # 事件回调
        self.on_filter_changed: Optional[Callable[[], None]] = None

        # 日志记录
        self.logger = logging.getLogger(__name__)

        super().__init__(parent, **kwargs)

    def _setup_ui(self) -> None:
        """设置UI布局"""
        # 创建主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.X, padx=5, pady=5)

        # 快速搜索区域
        if self.show_quick_search:
            self._create_quick_search(main_frame)

        # 高级筛选区域
        if self.show_advanced_filter:
            self._create_advanced_filter(main_frame)

    def _create_quick_search(self, parent) -> None:
        """创建快速搜索区域"""
        search_frame = ttk.LabelFrame(parent, text="快速搜索", padding=5)
        search_frame.pack(fill=tk.X, pady=(0, 5))

        # 搜索框
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill=tk.X)

        ttk.Label(search_input_frame, text="搜索:").pack(side=tk.LEFT)

        self.search_entry = ttk.Entry(search_input_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        # 搜索列选择
        ttk.Label(search_input_frame, text="在列:").pack(side=tk.LEFT, padx=(10, 0))

        column_options = ["所有列"] + [
            col.get("text", col["id"]) for col in self.columns
        ]
        self.search_column_combo = ttk.Combobox(
            search_input_frame, values=column_options, width=15, state="readonly"
        )
        self.search_column_combo.set("所有列")
        self.search_column_combo.pack(side=tk.LEFT, padx=(5, 0))

        # 搜索按钮
        search_btn = ttk.Button(
            search_input_frame, text="搜索", command=self._apply_quick_search
        )
        search_btn.pack(side=tk.LEFT, padx=(5, 0))

        # 清除搜索按钮
        clear_search_btn = ttk.Button(
            search_input_frame, text="清除", command=self._clear_quick_search
        )
        clear_search_btn.pack(side=tk.LEFT, padx=(5, 0))

    def _create_advanced_filter(self, parent) -> None:
        """创建高级筛选区域"""
        self.advanced_filter_frame = ttk.LabelFrame(parent, text="高级筛选", padding=5)
        self.advanced_filter_frame.pack(fill=tk.BOTH, expand=True)

        # 筛选条件容器
        conditions_container = ttk.Frame(self.advanced_filter_frame)
        conditions_container.pack(fill=tk.BOTH, expand=True)

        # 创建滚动区域
        canvas = tk.Canvas(conditions_container, height=150)
        scrollbar = ttk.Scrollbar(
            conditions_container, orient="vertical", command=canvas.yview
        )
        self.filter_conditions_frame = ttk.Frame(canvas)

        self.filter_conditions_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.filter_conditions_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 操作按钮
        button_frame = ttk.Frame(self.advanced_filter_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        self.add_condition_btn = ttk.Button(
            button_frame, text="添加条件", command=self._add_filter_condition
        )
        self.add_condition_btn.pack(side=tk.LEFT)

        self.clear_filters_btn = ttk.Button(
            button_frame, text="清除所有", command=self._clear_all_filters
        )
        self.clear_filters_btn.pack(side=tk.LEFT, padx=(5, 0))

        self.apply_filters_btn = ttk.Button(
            button_frame, text="应用筛选", command=self._apply_advanced_filters
        )
        self.apply_filters_btn.pack(side=tk.RIGHT)

    def _bind_events(self) -> None:
        """绑定事件"""
        # 快速搜索实时响应
        if self.search_entry:
            self.search_entry.bind("<KeyRelease>", self._on_search_text_changed)
            self.search_entry.bind("<Return>", lambda e: self._apply_quick_search())

        # 搜索列变化
        if self.search_column_combo:
            self.search_column_combo.bind(
                "<<ComboboxSelected>>", lambda e: self._apply_quick_search()
            )

    def _on_search_text_changed(self, event) -> None:
        """搜索文本变化事件"""
        # 实时搜索(延迟执行以避免频繁触发)
        if hasattr(self, "_search_after_id"):
            self.after_cancel(self._search_after_id)

        self._search_after_id = self.after(300, self._apply_quick_search)

    def _apply_quick_search(self) -> None:
        """应用快速搜索"""
        if not self.search_entry:
            return

        search_text = self.search_entry.get().strip()
        search_column = (
            self.search_column_combo.get() if self.search_column_combo else "所有列"
        )

        # 清除之前的快速搜索条件
        self.filter_conditions = [
            cond
            for cond in self.filter_conditions
            if not hasattr(cond, "_is_quick_search")
        ]

        # 添加新的快速搜索条件
        if search_text:
            if search_column == "所有列":
                # 在所有列中搜索
                for col in self.columns:
                    condition = FilterCondition(
                        col["id"],
                        FilterOperator.CONTAINS,
                        search_text,
                        case_sensitive=False,
                    )
                    condition._is_quick_search = True
                    self.filter_conditions.append(condition)
            else:
                # 在指定列中搜索
                column_id = None
                for col in self.columns:
                    if col.get("text", col["id"]) == search_column:
                        column_id = col["id"]
                        break

                if column_id:
                    condition = FilterCondition(
                        column_id,
                        FilterOperator.CONTAINS,
                        search_text,
                        case_sensitive=False,
                    )
                    condition._is_quick_search = True
                    self.filter_conditions.append(condition)

        self.quick_search_text = search_text
        self._emit_filter_changed()

        self.logger.info(f"应用快速搜索: '{search_text}' 在 '{search_column}'")

    def _clear_quick_search(self) -> None:
        """清除快速搜索"""
        if self.search_entry:
            self.search_entry.delete(0, tk.END)

        # 清除快速搜索条件
        self.filter_conditions = [
            cond
            for cond in self.filter_conditions
            if not hasattr(cond, "_is_quick_search")
        ]

        self.quick_search_text = ""
        self._emit_filter_changed()

    def _add_filter_condition(self) -> None:
        """添加筛选条件"""
        condition_frame = ttk.Frame(self.filter_conditions_frame)
        condition_frame.pack(fill=tk.X, pady=2)

        # 列选择
        column_combo = ttk.Combobox(
            condition_frame,
            values=[col.get("text", col["id"]) for col in self.columns],
            width=15,
            state="readonly",
        )
        column_combo.pack(side=tk.LEFT, padx=(0, 5))
        if self.columns:
            column_combo.set(self.columns[0].get("text", self.columns[0]["id"]))

        # 操作符选择
        operator_combo = ttk.Combobox(
            condition_frame,
            values=[op.value for op in FilterOperator],
            width=12,
            state="readonly",
        )
        operator_combo.set(FilterOperator.CONTAINS.value)
        operator_combo.pack(side=tk.LEFT, padx=(0, 5))

        # 值输入
        value_entry = ttk.Entry(condition_frame, width=20)
        value_entry.pack(side=tk.LEFT, padx=(0, 5))

        # 第二个值输入(用于BETWEEN操作)
        value2_entry = ttk.Entry(condition_frame, width=15)
        value2_entry.pack(side=tk.LEFT, padx=(0, 5))
        value2_entry.pack_forget()  # 默认隐藏

        # 删除按钮
        delete_btn = ttk.Button(
            condition_frame,
            text="删除",
            width=6,
            command=lambda: self._remove_filter_condition(condition_frame),
        )
        delete_btn.pack(side=tk.LEFT)

        # 绑定操作符变化事件
        def on_operator_changed(event):
            if operator_combo.get() == FilterOperator.BETWEEN.value:
                value2_entry.pack(side=tk.LEFT, padx=(0, 5), before=delete_btn)
            else:
                value2_entry.pack_forget()

        operator_combo.bind("<<ComboboxSelected>>", on_operator_changed)

        # 存储组件引用
        condition_frame._widgets = {
            "column": column_combo,
            "operator": operator_combo,
            "value": value_entry,
            "value2": value2_entry,
        }

    def _remove_filter_condition(self, condition_frame) -> None:
        """移除筛选条件"""
        condition_frame.destroy()
        self._apply_advanced_filters()

    def _apply_advanced_filters(self) -> None:
        """应用高级筛选"""
        # 清除之前的高级筛选条件
        self.filter_conditions = [
            cond for cond in self.filter_conditions if hasattr(cond, "_is_quick_search")
        ]

        # 收集当前的筛选条件
        for child in self.filter_conditions_frame.winfo_children():
            if hasattr(child, "_widgets"):
                widgets = child._widgets

                # 获取列ID
                column_text = widgets["column"].get()
                column_id = None
                for col in self.columns:
                    if col.get("text", col["id"]) == column_text:
                        column_id = col["id"]
                        break

                if not column_id:
                    continue

                # 获取操作符
                operator_text = widgets["operator"].get()
                operator = None
                for op in FilterOperator:
                    if op.value == operator_text:
                        operator = op
                        break

                if not operator:
                    continue

                # 获取值
                value = widgets["value"].get().strip()
                value2 = (
                    widgets["value2"].get().strip()
                    if operator == FilterOperator.BETWEEN
                    else None
                )

                # 创建筛选条件
                if value or operator in [
                    FilterOperator.IS_EMPTY,
                    FilterOperator.IS_NOT_EMPTY,
                ]:
                    condition = FilterCondition(
                        column_id,
                        operator,
                        value if value else None,
                        value2 if value2 else None,
                    )
                    self.filter_conditions.append(condition)

        self._emit_filter_changed()
        self.logger.info(f"应用高级筛选,共 {len(self.filter_conditions)} 个条件")

    def _clear_all_filters(self) -> None:
        """清除所有筛选"""
        # 清除快速搜索
        self._clear_quick_search()

        # 清除高级筛选条件
        for child in self.filter_conditions_frame.winfo_children():
            child.destroy()

        self.filter_conditions.clear()
        self._emit_filter_changed()

    def apply_filters(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """应用筛选条件到数据

        Args:
            data: 原始数据列表

        Returns:
            筛选后的数据列表
        """
        if not self.filter_conditions:
            return data

        filtered_data = []

        for row_data in data:
            # 快速搜索条件(OR逻辑)
            quick_search_conditions = [
                cond
                for cond in self.filter_conditions
                if hasattr(cond, "_is_quick_search")
            ]

            # 高级筛选条件(AND逻辑)
            advanced_conditions = [
                cond
                for cond in self.filter_conditions
                if not hasattr(cond, "_is_quick_search")
            ]

            # 检查快速搜索条件
            quick_search_match = True
            if quick_search_conditions:
                quick_search_match = any(
                    cond.apply(row_data) for cond in quick_search_conditions
                )

            # 检查高级筛选条件
            advanced_match = all(cond.apply(row_data) for cond in advanced_conditions)

            # 同时满足快速搜索和高级筛选
            if quick_search_match and advanced_match:
                filtered_data.append(row_data)

        self.logger.info(f"筛选结果: {len(filtered_data)}/{len(data)} 条记录")
        return filtered_data

    def get_current_filters(self) -> Dict[str, Any]:
        """获取当前筛选条件

        Returns:
            包含筛选条件信息的字典
        """
        return {
            "quick_search": self.quick_search_text,
            "conditions_count": len(self.filter_conditions),
            "has_filters": bool(self.filter_conditions),
        }

    def _emit_filter_changed(self) -> None:
        """发送筛选变化事件"""
        if self.on_filter_changed:
            self.on_filter_changed()

    def cleanup(self) -> None:
        """清理资源"""
        self.filter_conditions.clear()
        self.filter_history.clear()
        self.on_filter_changed = None
        self.logger.info("筛选组件资源已清理")
