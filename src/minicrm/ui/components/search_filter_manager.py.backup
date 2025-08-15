"""
MiniCRM 搜索筛选器管理器

负责管理搜索栏的高级筛选功能，包括：
- 筛选器组件创建
- 筛选器值管理
- 筛选器信号连接
"""

import logging
from datetime import datetime
from typing import Any

from PySide6.QtCore import QDate, QObject, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from minicrm.ui.components.search_config import FilterConfig


class SearchFilterManager(QObject):
    """
    搜索筛选器管理器

    负责管理搜索栏的高级筛选功能。

    Signals:
        filter_changed: 筛选变化信号 (filters: dict[str, Any])
    """

    # Qt信号定义
    filter_changed = Signal(dict)

    def __init__(self, parent: QObject | None = None):
        """
        初始化筛选器管理器

        Args:
            parent: 父对象
        """
        super().__init__(parent)

        # 日志记录器
        self._logger = logging.getLogger(self.__class__.__name__)

        # 筛选器数据
        self._filter_configs: list[FilterConfig] = []
        self._filter_widgets: dict[str, QWidget] = {}
        self._current_filters: dict[str, Any] = {}

        # UI容器
        self._container: QVBoxLayout | None = None

        self._logger.debug("筛选器管理器初始化完成")

    def set_container(self, container: QVBoxLayout) -> None:
        """
        设置筛选器容器

        Args:
            container: 筛选器容器布局
        """
        self._container = container
        self._logger.debug("筛选器容器已设置")

    def add_filter(self, filter_config: FilterConfig) -> None:
        """
        添加筛选器

        Args:
            filter_config: 筛选器配置
        """
        try:
            self._filter_configs.append(filter_config)

            if self._container:
                self._create_filter_widget(filter_config)

            self._logger.debug(f"添加筛选器: {filter_config.key}")

        except Exception as e:
            self._logger.error(f"添加筛选器失败: {e}")
            raise

    def remove_filter(self, filter_key: str) -> None:
        """
        移除筛选器

        Args:
            filter_key: 筛选器键名
        """
        try:
            # 移除配置
            self._filter_configs = [
                config for config in self._filter_configs if config.key != filter_key
            ]

            # 移除组件
            if filter_key in self._filter_widgets:
                widget = self._filter_widgets[filter_key]
                widget.deleteLater()
                del self._filter_widgets[filter_key]

            # 移除当前筛选值
            if filter_key in self._current_filters:
                del self._current_filters[filter_key]

            self._logger.debug(f"移除筛选器: {filter_key}")

        except Exception as e:
            self._logger.error(f"移除筛选器失败: {e}")

    def clear_filters(self) -> None:
        """清除所有筛选器"""
        try:
            # 清除所有组件
            for widget in self._filter_widgets.values():
                widget.deleteLater()

            # 清除数据
            self._filter_configs.clear()
            self._filter_widgets.clear()
            self._current_filters.clear()

            self._logger.debug("所有筛选器已清除")

        except Exception as e:
            self._logger.error(f"清除筛选器失败: {e}")

    def get_current_filters(self) -> dict[str, Any]:
        """
        获取当前筛选条件

        Returns:
            dict[str, Any]: 当前筛选条件
        """
        return self._current_filters.copy()

    def reset_filters(self) -> None:
        """重置所有筛选器到默认值"""
        try:
            for config in self._filter_configs:
                if config.key in self._filter_widgets:
                    widget = self._filter_widgets[config.key]
                    self._reset_filter_widget(widget, config)

            self._current_filters.clear()
            self.filter_changed.emit(self._current_filters)

            self._logger.debug("筛选器已重置")

        except Exception as e:
            self._logger.error(f"重置筛选器失败: {e}")

    def _create_filter_widget(self, config: FilterConfig) -> None:
        """
        创建筛选器组件

        Args:
            config: 筛选器配置
        """
        try:
            if not self._container:
                return

            # 创建筛选器行
            filter_layout = QHBoxLayout()

            # 标签
            label = QLabel(f"{config.title}:")
            label.setMinimumWidth(80)
            filter_layout.addWidget(label)

            # 根据类型创建组件
            filter_widget = self._create_widget_by_type(config)

            if filter_widget:
                # 设置默认值
                if config.default is not None:
                    self._set_filter_value(filter_widget, config)

                # 连接信号
                self._connect_filter_widget(filter_widget, config)

                # 存储组件
                self._filter_widgets[config.key] = filter_widget

                filter_layout.addWidget(filter_widget)
                filter_layout.addStretch()

                # 添加到容器
                self._container.addLayout(filter_layout)

        except Exception as e:
            self._logger.error(f"创建筛选器组件失败: {e}")

    def _create_widget_by_type(self, config: FilterConfig) -> QWidget | None:
        """
        根据类型创建筛选器组件

        Args:
            config: 筛选器配置

        Returns:
            QWidget | None: 创建的组件
        """
        if config.filter_type == "combo":
            return self._create_combo_widget(config)
        elif config.filter_type == "date":
            return self._create_date_widget(config)
        elif config.filter_type == "number":
            return self._create_number_widget(config)
        elif config.filter_type == "text":
            return self._create_text_widget(config)
        elif config.filter_type == "checkbox":
            return self._create_checkbox_widget(config)

        return None

    def _create_combo_widget(self, config: FilterConfig) -> QComboBox:
        """创建下拉框组件"""
        combo = QComboBox()
        combo.addItem("全部", None)

        if config.options:
            for option in config.options:
                if isinstance(option, dict):
                    combo.addItem(option["label"], option["value"])
                else:
                    combo.addItem(str(option), option)

        return combo

    def _create_date_widget(self, config: FilterConfig) -> QDateEdit:
        """创建日期组件"""
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setSpecialValueText("选择日期")
        return date_edit

    def _create_number_widget(self, config: FilterConfig) -> QSpinBox:
        """创建数字组件"""
        spin_box = QSpinBox()
        spin_box.setMinimum(config.min_value)
        spin_box.setMaximum(config.max_value)
        spin_box.setSpecialValueText("不限")
        return spin_box

    def _create_text_widget(self, config: FilterConfig) -> QLineEdit:
        """创建文本组件"""
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(config.placeholder)
        return line_edit

    def _create_checkbox_widget(self, config: FilterConfig) -> QCheckBox:
        """创建复选框组件"""
        checkbox = QCheckBox(config.checkbox_text)
        return checkbox

    def _set_filter_value(self, widget: QWidget, config: FilterConfig) -> None:
        """
        设置筛选器值

        Args:
            widget: 筛选器组件
            config: 筛选器配置
        """
        try:
            value = config.default

            if config.filter_type == "combo" and isinstance(widget, QComboBox):
                index = widget.findData(value)
                if index >= 0:
                    widget.setCurrentIndex(index)
            elif config.filter_type == "date" and isinstance(widget, QDateEdit):
                if isinstance(value, datetime):
                    q_date = QDate(value.year, value.month, value.day)
                    widget.setDate(q_date)
            elif config.filter_type == "number" and isinstance(widget, QSpinBox):
                widget.setValue(value)
            elif config.filter_type == "text" and isinstance(widget, QLineEdit):
                widget.setText(str(value))
            elif config.filter_type == "checkbox" and isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))

        except Exception as e:
            self._logger.error(f"设置筛选器值失败: {e}")

    def _reset_filter_widget(self, widget: QWidget, config: FilterConfig) -> None:
        """
        重置筛选器组件到默认状态

        Args:
            widget: 筛选器组件
            config: 筛选器配置
        """
        try:
            if config.filter_type == "combo" and isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)  # 选择"全部"
            elif config.filter_type == "date" and isinstance(widget, QDateEdit):
                widget.clear()
            elif config.filter_type == "number" and isinstance(widget, QSpinBox):
                widget.setValue(widget.minimum())
            elif config.filter_type == "text" and isinstance(widget, QLineEdit):
                widget.clear()
            elif config.filter_type == "checkbox" and isinstance(widget, QCheckBox):
                widget.setChecked(False)

        except Exception as e:
            self._logger.error(f"重置筛选器组件失败: {e}")

    def _connect_filter_widget(self, widget: QWidget, config: FilterConfig) -> None:
        """
        连接筛选器组件信号

        Args:
            widget: 筛选器组件
            config: 筛选器配置
        """
        try:
            if config.filter_type == "combo" and isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(self._on_filter_changed)
            elif config.filter_type == "date" and isinstance(widget, QDateEdit):
                widget.dateChanged.connect(self._on_filter_changed)
            elif config.filter_type == "number" and isinstance(widget, QSpinBox):
                widget.valueChanged.connect(self._on_filter_changed)
            elif config.filter_type == "text" and isinstance(widget, QLineEdit):
                widget.textChanged.connect(self._on_filter_changed)
            elif config.filter_type == "checkbox" and isinstance(widget, QCheckBox):
                widget.toggled.connect(self._on_filter_changed)

        except Exception as e:
            self._logger.error(f"连接筛选器信号失败: {e}")

    def _on_filter_changed(self) -> None:
        """处理筛选变化"""
        try:
            self._update_current_filters()
            self.filter_changed.emit(self._current_filters)

        except Exception as e:
            self._logger.error(f"处理筛选变化失败: {e}")

    def _update_current_filters(self) -> None:
        """更新当前筛选条件"""
        try:
            self._current_filters.clear()

            for config in self._filter_configs:
                if config.key in self._filter_widgets:
                    widget = self._filter_widgets[config.key]
                    value = self._get_filter_value(widget, config)

                    if value is not None and value != "":
                        self._current_filters[config.key] = value

        except Exception as e:
            self._logger.error(f"更新筛选条件失败: {e}")

    def _get_filter_value(self, widget: QWidget, config: FilterConfig) -> Any:
        """
        获取筛选器值

        Args:
            widget: 筛选器组件
            config: 筛选器配置

        Returns:
            Any: 筛选器值
        """
        try:
            if config.filter_type == "combo" and isinstance(widget, QComboBox):
                return widget.currentData()
            elif config.filter_type == "date" and isinstance(widget, QDateEdit):
                return widget.date().toPython()
            elif config.filter_type == "number" and isinstance(widget, QSpinBox):
                return widget.value() if widget.value() > widget.minimum() else None
            elif config.filter_type == "text" and isinstance(widget, QLineEdit):
                return widget.text().strip() or None
            elif config.filter_type == "checkbox" and isinstance(widget, QCheckBox):
                return widget.isChecked()

            return None

        except Exception as e:
            self._logger.error(f"获取筛选器值失败: {e}")
            return None
