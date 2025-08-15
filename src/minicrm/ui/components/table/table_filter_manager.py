"""MiniCRM 表格筛选管理器模块"""

import logging
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QWidget,
)


class TableFilterManager:
    """表格筛选管理器类"""

    def __init__(self, parent: QWidget, columns: list[dict[str, Any]]):
        """初始化筛选管理器"""
        self._parent = parent
        self._columns = columns
        self._logger = logging.getLogger(__name__)

        # 筛选组件
        self._search_box: QLineEdit | None = None
        self._filter_widgets: dict[str, QWidget] = {}

        # 搜索定时器（防抖）
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)

        # 回调函数（需要父组件设置）
        self.filter_changed: Callable[[], None] | None = None

    def create_toolbar_ui(self, layout: QHBoxLayout) -> None:
        """创建工具栏UI"""
        # 搜索框
        search_label = QLabel("搜索:")
        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText("输入关键词搜索...")
        self._search_box.setMaximumWidth(200)

        layout.addWidget(search_label)
        layout.addWidget(self._search_box)

        # 筛选控件
        self._create_filter_widgets(layout)

    def _create_filter_widgets(self, layout: QHBoxLayout) -> None:
        """创建筛选控件"""
        for column in self._columns:
            if column.get("filterable", False):
                filter_type = column.get("filter_type", "text")

                if filter_type == "combo":
                    # 下拉筛选
                    combo = QComboBox()
                    combo.addItem("全部")
                    combo.setMinimumWidth(100)

                    # 添加筛选选项
                    options = column.get("filter_options", [])
                    for option in options:
                        combo.addItem(str(option))

                    self._filter_widgets[column["key"]] = combo

                    layout.addWidget(QLabel(f"{column['title']}:"))
                    layout.addWidget(combo)

                elif filter_type == "text":
                    # 文本筛选
                    filter_edit = QLineEdit()
                    filter_edit.setPlaceholderText(f"筛选{column['title']}...")
                    filter_edit.setMaximumWidth(120)

                    self._filter_widgets[column["key"]] = filter_edit

                    layout.addWidget(QLabel(f"{column['title']}:"))
                    layout.addWidget(filter_edit)

    def setup_connections(self) -> None:
        """设置信号连接"""
        # 搜索框
        if self._search_box:
            self._search_box.textChanged.connect(self._on_search_text_changed)

        # 筛选控件
        for widget in self._filter_widgets.values():
            if isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(self._on_filter_changed)
            elif isinstance(widget, QLineEdit):
                widget.textChanged.connect(self._on_filter_changed)

        # 搜索定时器
        self._search_timer.timeout.connect(self._apply_search)

    def apply_filters(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        应用筛选条件

        Args:
            data: 原始数据

        Returns:
            list: 筛选后的数据
        """
        try:
            filtered_data = data.copy()

            # 应用搜索
            search_text = self._search_box.text().lower() if self._search_box else ""
            if search_text:
                filtered_data = [
                    row
                    for row in filtered_data
                    if any(
                        search_text in str(row.get(col["key"], "")).lower()
                        for col in self._columns
                    )
                ]

            # 应用筛选器
            for column_key, widget in self._filter_widgets.items():
                if isinstance(widget, QComboBox):
                    filter_value = widget.currentText()
                    if filter_value != "全部":
                        filtered_data = [
                            row
                            for row in filtered_data
                            if str(row.get(column_key, "")) == filter_value
                        ]
                elif isinstance(widget, QLineEdit):
                    filter_text = widget.text().lower()
                    if filter_text:
                        filtered_data = [
                            row
                            for row in filtered_data
                            if filter_text in str(row.get(column_key, "")).lower()
                        ]

            return filtered_data

        except Exception as e:
            self._logger.error(f"应用筛选失败: {e}")
            return data

    def _on_search_text_changed(self) -> None:
        """处理搜索文本变化（防抖）"""
        self._search_timer.start(300)  # 300ms延迟

    def _apply_search(self) -> None:
        """应用搜索"""
        try:
            # 通知父组件应用筛选
            if self.filter_changed:
                self.filter_changed()

        except Exception as e:
            self._logger.error(f"应用搜索失败: {e}")

    def _on_filter_changed(self) -> None:
        """处理筛选变化"""
        try:
            # 通知父组件应用筛选
            if self.filter_changed:
                self.filter_changed()

        except Exception as e:
            self._logger.error(f"处理筛选变化失败: {e}")

    def get_current_filters(self) -> dict[str, Any]:
        """获取当前筛选条件"""
        filters = {}

        # 搜索文本
        if self._search_box and self._search_box.text():
            filters["search"] = self._search_box.text()

        # 筛选器
        for column_key, widget in self._filter_widgets.items():
            if isinstance(widget, QComboBox):
                value = widget.currentText()
                if value != "全部":
                    filters[column_key] = value
            elif isinstance(widget, QLineEdit):
                value = widget.text()
                if value:
                    filters[column_key] = value

        return filters

    def clear_filters(self) -> None:
        """清除所有筛选条件"""
        try:
            if self._search_box:
                self._search_box.clear()

            for widget in self._filter_widgets.values():
                if isinstance(widget, QComboBox):
                    widget.setCurrentIndex(0)  # 设置为"全部"
                elif isinstance(widget, QLineEdit):
                    widget.clear()

        except Exception as e:
            self._logger.error(f"清除筛选条件失败: {e}")

    def cleanup(self) -> None:
        """清理资源"""
        try:
            if self._search_timer.isActive():
                self._search_timer.stop()

        except Exception as e:
            self._logger.error(f"清理筛选管理器资源失败: {e}")
