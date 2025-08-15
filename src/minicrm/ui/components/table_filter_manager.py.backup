"""
MiniCRM 表格筛选管理器

负责表格的筛选功能，包括筛选控件创建、筛选条件管理和搜索功能。
支持多种筛选类型和复合筛选条件。
"""

import logging
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QWidget,
)


class TableFilterManager(QObject):
    """
    表格筛选管理器类

    提供完整的表格筛选功能：
    - 筛选控件创建和管理
    - 筛选条件组合
    - 搜索功能
    - 筛选状态管理
    """

    # 信号定义
    filter_changed = Signal(dict)  # 筛选条件变化
    search_changed = Signal(str)  # 搜索条件变化

    def __init__(self, columns: list[dict[str, Any]], parent: QObject = None):
        """
        初始化筛选管理器

        Args:
            columns: 列配置列表
            parent: 父对象
        """
        super().__init__(parent)

        self._logger = logging.getLogger(f"{__name__}.TableFilterManager")

        # 配置
        self._columns = columns
        self._filterable_columns = [
            col for col in columns if col.get("filterable", False)
        ]

        # 筛选状态
        self._current_filters: dict[str, Any] = {}
        self._search_text = ""

        # UI组件
        self._filter_widgets: dict[str, QWidget] = {}
        self._search_widget: QLineEdit | None = None

        # 搜索防抖定时器
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._emit_search_changed)

        self._logger.debug(
            f"筛选管理器初始化完成: {len(self._filterable_columns)}个可筛选列"
        )

    def create_filter_widgets(self, layout: QHBoxLayout) -> None:
        """
        创建筛选控件

        Args:
            layout: 布局容器
        """
        try:
            # 创建搜索框
            if self._should_show_search():
                self._create_search_widget(layout)

            # 创建筛选控件
            for column in self._filterable_columns:
                self._create_filter_widget(column, layout)

            self._logger.debug("筛选控件创建完成")

        except Exception as e:
            self._logger.error(f"创建筛选控件失败: {e}")

    def _create_search_widget(self, layout: QHBoxLayout) -> None:
        """创建搜索控件"""
        # 搜索标签
        search_label = QLabel("搜索:")
        layout.addWidget(search_label)

        # 搜索输入框
        self._search_widget = QLineEdit()
        self._search_widget.setPlaceholderText("输入关键词搜索...")
        self._search_widget.setMaximumWidth(200)
        self._search_widget.textChanged.connect(self._on_search_text_changed)
        layout.addWidget(self._search_widget)

    def _create_filter_widget(
        self, column: dict[str, Any], layout: QHBoxLayout
    ) -> None:
        """
        创建单个筛选控件

        Args:
            column: 列配置
            layout: 布局容器
        """
        try:
            column_key = column.get("key", "")
            column_title = column.get("title", column_key)
            filter_type = column.get("filter_type", "text")

            # 创建标签
            label = QLabel(f"{column_title}:")
            layout.addWidget(label)

            # 根据类型创建筛选控件
            filter_widget: QWidget | None = None
            if filter_type == "combo":
                filter_widget = self._create_combo_filter(column)
            elif filter_type == "text":
                filter_widget = self._create_text_filter(column)
            else:
                filter_widget = self._create_text_filter(column)

            if filter_widget:
                filter_widget.setMaximumWidth(150)
                self._filter_widgets[column_key] = filter_widget
                layout.addWidget(filter_widget)

                # 连接信号
                self._connect_filter_widget(filter_widget, filter_type)

        except Exception as e:
            self._logger.error(f"创建筛选控件失败 {column.get('key', '')}: {e}")

    def _create_combo_filter(self, column: dict[str, Any]) -> QComboBox:
        """创建下拉框筛选控件"""
        combo_box = QComboBox()
        combo_box.addItem("全部", None)

        # 添加筛选选项
        filter_options = column.get("filter_options", [])
        for option in filter_options:
            if isinstance(option, dict):
                combo_box.addItem(option["label"], option["value"])
            else:
                combo_box.addItem(str(option), option)

        return combo_box

    def _create_text_filter(self, column: dict[str, Any]) -> QLineEdit:
        """创建文本筛选控件"""
        line_edit = QLineEdit()
        column_title = column.get("title", column.get("key", ""))
        line_edit.setPlaceholderText(f"筛选{column_title}...")
        return line_edit

    def _connect_filter_widget(self, widget: QWidget, filter_type: str) -> None:
        """
        连接筛选控件信号

        Args:
            widget: 筛选控件
            filter_type: 筛选类型
        """
        try:
            if filter_type == "combo" and isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(self._on_filter_changed)
            elif filter_type == "text" and isinstance(widget, QLineEdit):
                widget.textChanged.connect(self._on_filter_changed)

        except Exception as e:
            self._logger.error(f"连接筛选控件信号失败: {e}")

    def _on_search_text_changed(self) -> None:
        """处理搜索文本变化"""
        if self._search_widget:
            self._search_text = self._search_widget.text().strip()
            # 使用防抖，避免频繁触发
            self._search_timer.start(300)

    def _emit_search_changed(self) -> None:
        """发送搜索变化信号"""
        self.search_changed.emit(self._search_text)

    def _on_filter_changed(self) -> None:
        """处理筛选条件变化"""
        try:
            self._update_current_filters()
            self.filter_changed.emit(self._current_filters)

        except Exception as e:
            self._logger.error(f"处理筛选变化失败: {e}")

    def _update_current_filters(self) -> None:
        """更新当前筛选条件"""
        try:
            self._current_filters.clear()

            for column in self._filterable_columns:
                column_key = column.get("key", "")
                filter_type = column.get("filter_type", "text")

                if column_key in self._filter_widgets:
                    widget = self._filter_widgets[column_key]
                    value = self._get_filter_value(widget, filter_type)

                    if value is not None and value != "":
                        self._current_filters[column_key] = value

        except Exception as e:
            self._logger.error(f"更新筛选条件失败: {e}")

    def _get_filter_value(self, widget: QWidget, filter_type: str) -> Any:
        """
        获取筛选控件的值

        Args:
            widget: 筛选控件
            filter_type: 筛选类型

        Returns:
            Any: 筛选值
        """
        try:
            if filter_type == "combo" and isinstance(widget, QComboBox):
                return widget.currentData()
            elif filter_type == "text" and isinstance(widget, QLineEdit):
                text = widget.text().strip()
                return text if text else None

            return None

        except Exception as e:
            self._logger.error(f"获取筛选值失败: {e}")
            return None

    def create_filter_function(self) -> Callable:
        """
        创建筛选函数

        Returns:
            callable: 筛选函数，接受行数据，返回bool
        """

        def filter_func(row_data: dict[str, Any]) -> bool:
            try:
                # 应用搜索条件
                if self._search_text and not self._match_search(
                    row_data, self._search_text
                ):
                    return False

                # 应用筛选条件
                for column_key, filter_value in self._current_filters.items():
                    if not self._match_filter(row_data, column_key, filter_value):
                        return False

                return True

            except Exception as e:
                self._logger.error(f"筛选函数执行失败: {e}")
                return True  # 出错时包含该行

        return filter_func

    def _match_search(self, row_data: dict[str, Any], search_text: str) -> bool:
        """
        检查行数据是否匹配搜索条件

        Args:
            row_data: 行数据
            search_text: 搜索文本

        Returns:
            bool: 是否匹配
        """
        try:
            search_lower = search_text.lower()

            # 在所有可搜索列中查找
            for column in self._columns:
                if column.get("searchable", True):  # 默认可搜索
                    column_key = column.get("key", "")
                    value = row_data.get(column_key, "")

                    if search_lower in str(value).lower():
                        return True

            return False

        except Exception as e:
            self._logger.error(f"搜索匹配失败: {e}")
            return False

    def _match_filter(
        self, row_data: dict[str, Any], column_key: str, filter_value: Any
    ) -> bool:
        """
        检查行数据是否匹配筛选条件

        Args:
            row_data: 行数据
            column_key: 列键名
            filter_value: 筛选值

        Returns:
            bool: 是否匹配
        """
        try:
            row_value = row_data.get(column_key)

            # 获取列配置
            column = self._get_column_config(column_key)
            if not column:
                return True

            filter_type = column.get("filter_type", "text")

            if filter_type == "combo":
                return row_value == filter_value
            elif filter_type == "text":
                if isinstance(filter_value, str):
                    return filter_value.lower() in str(row_value).lower()
                return True

            return True

        except Exception as e:
            self._logger.error(f"筛选匹配失败: {e}")
            return True

    def _get_column_config(self, column_key: str) -> dict[str, Any] | None:
        """获取列配置"""
        for column in self._columns:
            if column.get("key") == column_key:
                return column
        return None

    def _should_show_search(self) -> bool:
        """是否应该显示搜索框"""
        return any(col.get("searchable", True) for col in self._columns)

    def get_current_filters(self) -> dict[str, Any]:
        """
        获取当前筛选条件

        Returns:
            Dict[str, Any]: 当前筛选条件
        """
        return self._current_filters.copy()

    def get_search_text(self) -> str:
        """
        获取当前搜索文本

        Returns:
            str: 搜索文本
        """
        return self._search_text

    def set_filter_value(self, column_key: str, value: Any) -> None:
        """
        设置筛选值

        Args:
            column_key: 列键名
            value: 筛选值
        """
        try:
            if column_key in self._filter_widgets:
                widget = self._filter_widgets[column_key]
                column = self._get_column_config(column_key)

                if column:
                    filter_type = column.get("filter_type", "text")

                    if filter_type == "combo" and isinstance(widget, QComboBox):
                        index = widget.findData(value)
                        if index >= 0:
                            widget.setCurrentIndex(index)
                    elif filter_type == "text" and isinstance(widget, QLineEdit):
                        widget.setText(str(value) if value is not None else "")

        except Exception as e:
            self._logger.error(f"设置筛选值失败: {e}")

    def set_search_text(self, text: str) -> None:
        """
        设置搜索文本

        Args:
            text: 搜索文本
        """
        if self._search_widget:
            self._search_widget.setText(text)

    def clear_filters(self) -> None:
        """清除所有筛选条件"""
        try:
            # 清除筛选控件
            for widget in self._filter_widgets.values():
                if isinstance(widget, QComboBox):
                    widget.setCurrentIndex(0)  # 选择"全部"
                elif isinstance(widget, QLineEdit):
                    widget.clear()

            # 清除搜索
            if self._search_widget:
                self._search_widget.clear()

            # 清除状态
            self._current_filters.clear()
            self._search_text = ""

            # 发送信号
            self.filter_changed.emit(self._current_filters)
            self.search_changed.emit(self._search_text)

            self._logger.debug("筛选条件已清除")

        except Exception as e:
            self._logger.error(f"清除筛选条件失败: {e}")

    def has_active_filters(self) -> bool:
        """
        检查是否有活动的筛选条件

        Returns:
            bool: 是否有活动筛选
        """
        return bool(self._current_filters) or bool(self._search_text)

    def get_filter_summary(self) -> str:
        """
        获取筛选条件摘要

        Returns:
            str: 筛选摘要文本
        """
        try:
            parts = []

            if self._search_text:
                parts.append(f"搜索: {self._search_text}")

            for column_key, value in self._current_filters.items():
                column = self._get_column_config(column_key)
                if column:
                    column_title = column.get("title", column_key)
                    parts.append(f"{column_title}: {value}")

            return " | ".join(parts) if parts else "无筛选条件"

        except Exception as e:
            self._logger.error(f"获取筛选摘要失败: {e}")
            return "筛选摘要获取失败"
