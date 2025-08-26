"""TTK表单构建器

提供动态表单生成功能,包括:
- FormBuilderTTK: 动态表单构建器类
- 各种输入组件的集成
- 表单验证机制和错误提示
- 数据绑定和自动同步

设计目标:
1. 提供简单易用的表单构建API
2. 支持多种输入组件类型
3. 集成数据绑定和验证功能
4. 提供良好的用户体验

作者: MiniCRM开发团队
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional

from .advanced_input_components import ColorPickerTTK, FilePickerTTK, NumberSpinnerTTK
from .base_widget import BaseWidget
from .date_picker_ttk import DatePickerTTK
from .form_data_binding import (
    CommonFormatters,
    CommonParsers,
    CommonValidators,
    DataBinding,
)


class FormBuilderTTK(BaseWidget):
    """TTK表单构建器

    支持动态表单生成,包括:
    - 多种输入组件类型
    - 自动布局管理
    - 数据绑定和验证
    - 错误提示显示
    """

    def __init__(
        self,
        parent: tk.Widget,
        fields: List[Dict[str, Any]],
        columns: int = 2,
        **kwargs,
    ):
        """初始化表单构建器

        Args:
            parent: 父容器
            fields: 字段定义列表
            columns: 列数
            **kwargs: 其他参数
        """
        self.fields = fields
        self.columns = columns

        # 组件存储
        self.widgets: Dict[str, tk.Widget] = {}
        self.labels: Dict[str, ttk.Label] = {}
        self.error_labels: Dict[str, ttk.Label] = {}

        # 数据绑定
        self.data_binding = DataBinding()

        # 初始化基础组件
        super().__init__(parent, **kwargs)

        # 设置数据绑定
        self._setup_data_binding()

    def _setup_ui(self) -> None:
        """设置UI布局"""
        # 创建滚动框架
        self._create_scroll_frame()

        # 创建表单字段
        self._create_form_fields()

        # 创建按钮区域
        self._create_button_area()

    def _create_scroll_frame(self) -> None:
        """创建滚动框架"""
        # 创建Canvas和Scrollbar
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = ttk.Frame(self.canvas)

        # 配置滚动
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 布局
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _create_form_fields(self) -> None:
        """创建表单字段"""
        for i, field in enumerate(self.fields):
            row = i // self.columns
            col = (i % self.columns) * 2  # 每个字段占用2列(标签+输入框)

            self._create_field(field, row, col)

    def _create_field(self, field: Dict[str, Any], row: int, col: int) -> None:
        """创建单个字段

        Args:
            field: 字段定义
            row: 行号
            col: 列号
        """
        field_id = field.get("id", f"field_{row}_{col}")
        field_type = field.get("type", "entry")
        label_text = field.get("label", field_id)
        required = field.get("required", False)

        # 创建标签
        label_text_with_required = f"{label_text}{'*' if required else ''}"
        label = ttk.Label(self.scrollable_frame, text=label_text_with_required)
        label.grid(row=row, column=col, sticky="w", padx=(0, 5), pady=2)
        self.labels[field_id] = label

        # 创建输入组件
        widget = self._create_input_widget(field)
        widget.grid(row=row, column=col + 1, sticky="ew", padx=(0, 10), pady=2)
        self.widgets[field_id] = widget

        # 创建错误提示标签
        error_label = ttk.Label(
            self.scrollable_frame, text="", foreground="red", font=("", 8)
        )
        error_label.grid(row=row + 1, column=col + 1, sticky="w", padx=(0, 10))
        self.error_labels[field_id] = error_label

        # 配置列权重
        self.scrollable_frame.columnconfigure(col + 1, weight=1)

    def _create_input_widget(self, field: Dict[str, Any]) -> tk.Widget:
        """创建输入组件

        Args:
            field: 字段定义

        Returns:
            创建的组件
        """
        field_type = field.get("type", "entry")

        if field_type == "entry":
            widget = ttk.Entry(self.scrollable_frame)

        elif field_type == "text":
            widget = tk.Text(
                self.scrollable_frame,
                height=field.get("height", 4),
                width=field.get("width", 40),
            )

        elif field_type == "combobox":
            widget = ttk.Combobox(
                self.scrollable_frame,
                values=field.get("options", []),
                state=field.get("state", "normal"),
            )

        elif field_type == "checkbox":
            widget = ttk.Checkbutton(self.scrollable_frame)

        elif field_type == "radiobutton":
            # 创建单选按钮组
            frame = ttk.Frame(self.scrollable_frame)
            var = tk.StringVar()
            options = field.get("options", [])

            for option in options:
                rb = ttk.Radiobutton(frame, text=option, variable=var, value=option)
                rb.pack(anchor="w")

            widget = frame
            widget.variable = var  # 保存变量引用

        elif field_type == "scale":
            widget = ttk.Scale(
                self.scrollable_frame,
                from_=field.get("from_", 0),
                to=field.get("to", 100),
                orient=field.get("orient", "horizontal"),
            )

        elif field_type == "spinbox":
            widget = ttk.Spinbox(
                self.scrollable_frame,
                from_=field.get("from_", 0),
                to=field.get("to", 100),
                increment=field.get("increment", 1),
            )

        elif field_type == "number_spinner":
            widget = NumberSpinnerTTK(
                self.scrollable_frame,
                min_value=field.get("min_value", 0),
                max_value=field.get("max_value", 100),
                step=field.get("step", 1),
                decimal_places=field.get("decimal_places", 0),
                unit=field.get("unit", ""),
            )

        elif field_type == "color_picker":
            widget = ColorPickerTTK(
                self.scrollable_frame, preset_colors=field.get("preset_colors")
            )

        elif field_type == "file_picker":
            widget = FilePickerTTK(
                self.scrollable_frame,
                file_types=field.get("file_types"),
                multiple=field.get("multiple", False),
            )

        elif field_type == "date_picker":
            widget = DatePickerTTK(
                self.scrollable_frame, date_format=field.get("date_format", "%Y-%m-%d")
            )

        else:
            # 默认使用Entry
            widget = ttk.Entry(self.scrollable_frame)

        return widget

    def _create_button_area(self) -> None:
        """创建按钮区域"""
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(fill=tk.X, pady=(10, 0))

        # 提交按钮
        self.submit_button = ttk.Button(
            self.button_frame, text="提交", command=self._on_submit
        )
        self.submit_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 重置按钮
        self.reset_button = ttk.Button(
            self.button_frame, text="重置", command=self._on_reset
        )
        self.reset_button.pack(side=tk.RIGHT)

        # 验证按钮
        self.validate_button = ttk.Button(
            self.button_frame, text="验证", command=self._on_validate
        )
        self.validate_button.pack(side=tk.RIGHT, padx=(0, 5))

    def _setup_data_binding(self) -> None:
        """设置数据绑定"""
        for field in self.fields:
            field_id = field.get("id", "")
            if not field_id or field_id not in self.widgets:
                continue

            widget = self.widgets[field_id]

            # 设置格式化器
            formatter = self._get_field_formatter(field)
            if formatter:
                self.data_binding.set_formatter(field_id, formatter)

            # 设置解析器
            parser = self._get_field_parser(field)
            if parser:
                self.data_binding.set_parser(field_id, parser)

            # 设置验证器
            validator = self._get_field_validator(field)
            if validator:
                self.data_binding.set_validator(field_id, validator)

            # 绑定组件
            self.data_binding.bind(
                field_id,
                widget,
                formatter=formatter,
                parser=parser,
                validator=validator,
                auto_sync=field.get("auto_sync", False),
            )

    def _get_field_formatter(self, field: Dict[str, Any]) -> Optional[Callable]:
        """获取字段格式化器"""
        field_type = field.get("type", "entry")

        if field_type == "date_picker":
            return CommonFormatters.date_formatter(field.get("date_format", "%Y-%m-%d"))
        if field_type == "number_spinner" or field.get("format") == "number":
            return CommonFormatters.number_formatter(field.get("decimal_places", 2))
        if field.get("format") == "currency":
            return CommonFormatters.currency_formatter(
                field.get("currency_symbol", "¥")
            )
        if field.get("format") == "percentage":
            return CommonFormatters.percentage_formatter()

        return field.get("formatter")

    def _get_field_parser(self, field: Dict[str, Any]) -> Optional[Callable]:
        """获取字段解析器"""
        field_type = field.get("type", "entry")

        if field_type == "date_picker":
            return CommonParsers.date_parser(field.get("date_format", "%Y-%m-%d"))
        if field_type == "number_spinner" or field.get("format") == "number":
            return CommonParsers.number_parser()
        if field.get("format") == "currency":
            return CommonParsers.currency_parser()
        if field.get("format") == "percentage":
            return CommonParsers.percentage_parser()

        return field.get("parser")

    def _get_field_validator(self, field: Dict[str, Any]) -> Optional[Callable]:
        """获取字段验证器"""
        validators = []

        # 必填验证
        if field.get("required", False):
            validators.append(CommonValidators.required_validator())

        # 邮箱验证
        if field.get("format") == "email":
            validators.append(CommonValidators.email_validator())

        # 电话验证
        if field.get("format") == "phone":
            validators.append(CommonValidators.phone_validator())

        # 范围验证
        if "min_value" in field and "max_value" in field:
            validators.append(
                CommonValidators.range_validator(field["min_value"], field["max_value"])
            )

        # 自定义验证器
        if "validator" in field:
            validators.append(field["validator"])

        # 组合多个验证器
        if len(validators) == 0:
            return None
        if len(validators) == 1:
            return validators[0]

        def combined_validator(value):
            for validator in validators:
                if not validator(value):
                    return False
            return True

        return combined_validator

    def _on_submit(self) -> None:
        """处理提交事件"""
        # 同步所有组件数据
        self.data_binding.sync_all_widgets_to_data()

        # 验证数据
        is_valid, errors = self.data_binding.validate_all()

        if is_valid:
            # 清除错误提示
            self._clear_error_messages()

            # 触发提交事件
            data = self.data_binding.get_all_data()
            self.trigger_event("form_submit", data)
        else:
            # 显示错误提示
            self._show_error_messages(errors)

    def _on_reset(self) -> None:
        """处理重置事件"""
        # 清空数据
        self.data_binding.clear_data()

        # 清除错误提示
        self._clear_error_messages()

        # 触发重置事件
        self.trigger_event("form_reset")

    def _on_validate(self) -> None:
        """处理验证事件"""
        # 同步所有组件数据
        self.data_binding.sync_all_widgets_to_data()

        # 验证数据
        is_valid, errors = self.data_binding.validate_all()

        if is_valid:
            self._clear_error_messages()
            self.trigger_event("form_valid", self.data_binding.get_all_data())
        else:
            self._show_error_messages(errors)
            self.trigger_event("form_invalid", errors)

    def _show_error_messages(self, errors: Dict[str, str]) -> None:
        """显示错误消息

        Args:
            errors: 错误消息字典
        """
        # 先清除所有错误消息
        self._clear_error_messages()

        # 显示新的错误消息
        for field_id, error_message in errors.items():
            if field_id in self.error_labels:
                self.error_labels[field_id].config(text=error_message)

    def _clear_error_messages(self) -> None:
        """清除所有错误消息"""
        for error_label in self.error_labels.values():
            error_label.config(text="")

    def get_form_data(self) -> Dict[str, Any]:
        """获取表单数据

        Returns:
            表单数据字典
        """
        self.data_binding.sync_all_widgets_to_data()
        return self.data_binding.get_all_data()

    def set_form_data(self, data: Dict[str, Any]) -> None:
        """设置表单数据

        Args:
            data: 表单数据字典
        """
        self.data_binding.set_all_data(data)

    def validate_form(self) -> tuple[bool, Dict[str, str]]:
        """验证表单

        Returns:
            (是否有效, 错误消息字典) 元组
        """
        self.data_binding.sync_all_widgets_to_data()
        return self.data_binding.validate_all()

    def clear_form(self) -> None:
        """清空表单"""
        self.data_binding.clear_data()
        self._clear_error_messages()

    def set_field_value(self, field_id: str, value: Any) -> None:
        """设置字段值

        Args:
            field_id: 字段ID
            value: 字段值
        """
        self.data_binding.set_data(field_id, value)

    def get_field_value(self, field_id: str, default: Any = None) -> Any:
        """获取字段值

        Args:
            field_id: 字段ID
            default: 默认值

        Returns:
            字段值
        """
        return self.data_binding.get_data(field_id, default)

    def set_field_enabled(self, field_id: str, enabled: bool) -> None:
        """设置字段启用状态

        Args:
            field_id: 字段ID
            enabled: 是否启用
        """
        if field_id in self.widgets:
            widget = self.widgets[field_id]
            state = "normal" if enabled else "disabled"
            try:
                widget.config(state=state)
            except tk.TclError:
                pass  # 某些组件可能不支持state属性

    def set_field_visible(self, field_id: str, visible: bool) -> None:
        """设置字段可见性

        Args:
            field_id: 字段ID
            visible: 是否可见
        """
        widgets_to_toggle = []

        if field_id in self.widgets:
            widgets_to_toggle.append(self.widgets[field_id])
        if field_id in self.labels:
            widgets_to_toggle.append(self.labels[field_id])
        if field_id in self.error_labels:
            widgets_to_toggle.append(self.error_labels[field_id])

        for widget in widgets_to_toggle:
            if visible:
                widget.grid()
            else:
                widget.grid_remove()


# 导出表单构建器
__all__ = ["FormBuilderTTK"]
