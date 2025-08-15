"""
MiniCRM 表单字段工厂

负责创建各种类型的表单字段组件
"""

import logging
from datetime import date
from enum import Enum
from typing import Any

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDoubleSpinBox,
    QLabel,
    QLineEdit,
    QRadioButton,
    QSpinBox,
    QTextEdit,
    QWidget,
)


class FieldType(Enum):
    """字段类型枚举"""

    TEXT = "text"
    PASSWORD = "password"
    EMAIL = "email"
    PHONE = "phone"
    NUMBER = "number"
    DECIMAL = "decimal"
    DATE = "date"
    DATETIME = "datetime"
    TEXTAREA = "textarea"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"


class FormFieldFactory:
    """表单字段创建工厂"""

    def __init__(self):
        """初始化字段工厂"""
        self._logger = logging.getLogger(__name__)

    def create_field_widget(
        self, field: dict[str, Any]
    ) -> tuple[QWidget | None, QLabel | None]:
        """
        创建字段组件

        Args:
            field: 字段配置字典

        Returns:
            tuple: (字段组件, 错误标签)
        """
        try:
            field_type = field.get("type", "text")
            field_key = field.get("key", "")

            # 创建字段组件
            widget = self._create_widget_by_type(field_type, field)
            if not widget:
                return None, None

            # 设置基本属性
            self._setup_widget_properties(widget, field)

            # 创建错误标签
            error_label = self._create_error_label(field_key)

            return widget, error_label

        except Exception as e:
            self._logger.error(f"创建字段组件失败: {e}")
            return None, None

    def _create_widget_by_type(
        self, field_type: str, field: dict[str, Any]
    ) -> QWidget | None:
        """根据类型创建组件"""
        try:
            if field_type in ["text", "password", "email", "phone"]:
                return self._create_line_edit(field_type, field)
            elif field_type == "number":
                return self._create_spin_box(field)
            elif field_type == "decimal":
                return self._create_double_spin_box(field)
            elif field_type == "date":
                return self._create_date_edit(field)
            elif field_type == "datetime":
                return self._create_datetime_edit(field)
            elif field_type == "textarea":
                return self._create_text_edit(field)
            elif field_type == "select":
                return self._create_combo_box(field)
            elif field_type == "radio":
                return self._create_radio_group(field)
            elif field_type == "checkbox":
                return self._create_checkbox(field)
            else:
                self._logger.warning(f"未知字段类型: {field_type}")
                return None

        except Exception as e:
            self._logger.error(f"创建{field_type}组件失败: {e}")
            return None

    def _create_line_edit(self, field_type: str, field: dict[str, Any]) -> QLineEdit:
        """创建文本输入框"""
        widget = QLineEdit()

        # 设置占位符
        if placeholder := field.get("placeholder"):
            widget.setPlaceholderText(placeholder)

        # 设置密码模式
        if field_type == "password":
            widget.setEchoMode(QLineEdit.EchoMode.Password)

        # 设置最大长度
        if max_length := field.get("max_length"):
            widget.setMaxLength(max_length)

        return widget

    def _create_spin_box(self, field: dict[str, Any]) -> QSpinBox:
        """创建数字输入框"""
        widget = QSpinBox()

        # 设置范围
        widget.setMinimum(field.get("min_value", 0))
        widget.setMaximum(field.get("max_value", 999999))

        # 设置步长
        if step := field.get("step"):
            widget.setSingleStep(step)

        return widget

    def _create_double_spin_box(self, field: dict[str, Any]) -> QDoubleSpinBox:
        """创建小数输入框"""
        widget = QDoubleSpinBox()

        # 设置范围
        widget.setMinimum(field.get("min_value", 0.0))
        widget.setMaximum(field.get("max_value", 999999.99))

        # 设置小数位数
        widget.setDecimals(field.get("decimals", 2))

        # 设置步长
        if step := field.get("step"):
            widget.setSingleStep(step)

        return widget

    def _create_date_edit(self, field: dict[str, Any]) -> QDateEdit:
        """创建日期选择器"""
        widget = QDateEdit()
        widget.setCalendarPopup(True)

        # 设置日期格式
        widget.setDisplayFormat(field.get("format", "yyyy-MM-dd"))

        # 设置默认日期
        if default_date := field.get("default"):
            if isinstance(default_date, str):
                widget.setDate(QDate.fromString(default_date, "yyyy-MM-dd"))
            elif isinstance(default_date, date):
                widget.setDate(
                    QDate(default_date.year, default_date.month, default_date.day)
                )

        return widget

    def _create_datetime_edit(self, field: dict[str, Any]) -> QDateTimeEdit:
        """创建日期时间选择器"""
        widget = QDateTimeEdit()
        widget.setCalendarPopup(True)

        # 设置日期时间格式
        widget.setDisplayFormat(field.get("format", "yyyy-MM-dd hh:mm:ss"))

        return widget

    def _create_text_edit(self, field: dict[str, Any]) -> QTextEdit:
        """创建多行文本框"""
        widget = QTextEdit()

        # 设置占位符
        if placeholder := field.get("placeholder"):
            widget.setPlaceholderText(placeholder)

        # 设置高度
        if height := field.get("height"):
            widget.setFixedHeight(height)

        return widget

    def _create_combo_box(self, field: dict[str, Any]) -> QComboBox:
        """创建下拉选择框"""
        widget = QComboBox()

        # 添加选项
        if options := field.get("options", []):
            for option in options:
                if isinstance(option, dict):
                    widget.addItem(option.get("label", ""), option.get("value"))
                else:
                    widget.addItem(str(option), option)

        # 设置是否可编辑
        if field.get("editable", False):
            widget.setEditable(True)

        return widget

    def _create_radio_group(self, field: dict[str, Any]) -> QWidget:
        """创建单选按钮组"""
        from PySide6.QtWidgets import QHBoxLayout, QWidget

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        button_group = QButtonGroup(container)

        # 添加单选按钮
        if options := field.get("options", []):
            for i, option in enumerate(options):
                if isinstance(option, dict):
                    text = option.get("label", "")
                    value = option.get("value")
                else:
                    text = str(option)
                    value = option

                radio_button = QRadioButton(text)
                radio_button.setProperty("value", value)
                button_group.addButton(radio_button, i)
                layout.addWidget(radio_button)

        # 存储按钮组引用
        container.setProperty("button_group", button_group)

        return container

    def _create_checkbox(self, field: dict[str, Any]) -> QCheckBox:
        """创建复选框"""
        text = field.get("label", "")
        widget = QCheckBox(text)

        return widget

    def _setup_widget_properties(self, widget: QWidget, field: dict[str, Any]) -> None:
        """设置组件通用属性"""
        try:
            # 设置启用状态
            if "enabled" in field:
                widget.setEnabled(field["enabled"])

            # 设置可见性
            if "visible" in field:
                widget.setVisible(field["visible"])

            # 设置工具提示
            if tooltip := field.get("tooltip"):
                widget.setToolTip(tooltip)

            # 设置样式
            if style := field.get("style"):
                widget.setStyleSheet(style)

        except Exception as e:
            self._logger.error(f"设置组件属性失败: {e}")

    def _create_error_label(self, field_key: str) -> QLabel:
        """创建错误标签"""
        error_label = QLabel()
        error_label.setObjectName(f"error_label_{field_key}")
        error_label.setStyleSheet("color: red; font-size: 12px;")
        error_label.hide()

        return error_label
