"""MiniCRM 数据表格组件 - 重构版本"""

from typing import Any

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from minicrm.ui.components.base_widget import BaseWidget

from .table_data_manager import SortOrder, TableDataManager
from .table_export_manager import TableExportManager
from .table_filter_manager import TableFilterManager
from .table_pagination_manager import TablePaginationManager


class DataTable(BaseWidget):
    """通用数据表格组件 - 模块化设计"""

    # Qt信号定义
    row_selected = Signal(int, dict)
    row_double_clicked = Signal(int, dict)
    data_changed = Signal(int, str, object, object)
    selection_changed = Signal(list)
    page_changed = Signal(int, int)
    sort_changed = Signal(str, SortOrder)
    filter_changed = Signal(dict)

    def __init__(
        self,
        columns: list[dict[str, Any]],
        editable: bool = False,
        multi_select: bool = True,
        show_pagination: bool = True,
        page_size: int = 50,
        parent: QWidget | None = None,
    ):
        # 表格配置
        self._columns = columns
        self._editable = editable
        self._multi_select = multi_select
        self._show_pagination = show_pagination

        # UI组件
        self._table_widget: QTableWidget | None = None

        # 模块化组件
        self._data_manager = TableDataManager(columns)
        self._filter_manager = TableFilterManager(self, columns)
        self._pagination_manager = TablePaginationManager(self, page_size)
        self._export_manager = TableExportManager(self)

        super().__init__(parent)

    def setup_ui(self) -> None:
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 创建工具栏
        self._create_toolbar(layout)

        # 创建表格
        self._create_table(layout)

        # 创建分页控件
        if self._show_pagination:
            self._pagination_manager.create_pagination_ui(layout)

    def _create_toolbar(self, layout: QVBoxLayout) -> None:
        """创建工具栏"""
        toolbar_frame = QFrame()
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(10)

        # 筛选控件
        self._filter_manager.create_toolbar_ui(toolbar_layout)

        # 弹性空间
        toolbar_layout.addStretch()

        # 操作按钮
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.refresh)
        toolbar_layout.addWidget(refresh_btn)

        export_btn = QPushButton("📤 导出")
        export_btn.clicked.connect(
            lambda: self._export_manager.show_export_menu(export_btn)
        )
        toolbar_layout.addWidget(export_btn)

        layout.addWidget(toolbar_frame)

    def _create_table(self, layout: QVBoxLayout) -> None:
        """创建表格"""
        self._table_widget = QTableWidget()

        # 设置列
        self._table_widget.setColumnCount(len(self._columns))
        headers = [col["title"] for col in self._columns]
        self._table_widget.setHorizontalHeaderLabels(headers)

        # 设置列宽
        header = self._table_widget.horizontalHeader()
        for i, column in enumerate(self._columns):
            if "width" in column:
                self._table_widget.setColumnWidth(i, column["width"])
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        # 设置表格属性
        self._table_widget.setAlternatingRowColors(True)
        self._table_widget.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        if self._multi_select:
            self._table_widget.setSelectionMode(
                QAbstractItemView.SelectionMode.MultiSelection
            )
        else:
            self._table_widget.setSelectionMode(
                QAbstractItemView.SelectionMode.SingleSelection
            )

        # 设置排序和右键菜单
        self._table_widget.setSortingEnabled(True)
        self._table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        layout.addWidget(self._table_widget)

    def setup_connections(self) -> None:
        """设置信号连接"""
        if self._table_widget:
            self._table_widget.itemSelectionChanged.connect(self._on_selection_changed)
            self._table_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
            self._table_widget.itemChanged.connect(self._on_item_changed)
            self._table_widget.customContextMenuRequested.connect(
                self._show_context_menu
            )
            self._table_widget.horizontalHeader().sectionClicked.connect(
                self._on_header_clicked
            )

        # 连接模块化组件
        self._filter_manager.setup_connections()
        self._filter_manager.filter_changed = self._on_filter_changed

        if self._show_pagination:
            self._pagination_manager.setup_connections()
            self._pagination_manager.page_changed = self._emit_page_changed

    def apply_styles(self) -> None:
        """应用样式"""
        self.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                alternate-background-color: #f8f9fa;
                selection-background-color: #007bff;
                selection-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:hover {
                background-color: #e9ecef;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #495057;
                padding: 8px;
                border: none;
                border-right: 1px solid #dee2e6;
                border-bottom: 1px solid #dee2e6;
                font-weight: bold;
            }
            QHeaderView::section:hover {
                background-color: #e9ecef;
            }
            QPushButton {
                padding: 6px 12px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)

    def set_data(self, data: list[dict[str, Any]]) -> None:
        """设置表格数据"""
        self._data_manager.set_data(data)
        self._apply_filters_and_refresh()

    def add_row(self, row_data: dict[str, Any]) -> None:
        """添加行数据"""
        self._data_manager.add_row(row_data)
        self._apply_filters_and_refresh()

    def update_row(self, row_index: int, row_data: dict[str, Any]) -> None:
        """更新行数据"""
        self._data_manager.update_row(row_index, row_data)
        self._apply_filters_and_refresh()

    def remove_row(self, row_index: int) -> None:
        """删除行数据"""
        self._data_manager.remove_row(row_index)
        self._apply_filters_and_refresh()

    def get_selected_data(self) -> list[dict[str, Any]]:
        """获取选中行的数据"""
        if self._table_widget is None:
            return []
        return self._data_manager.get_selected_data(self._table_widget)

    def refresh(self) -> None:
        """刷新表格"""
        self._apply_filters_and_refresh()

    def _apply_filters_and_refresh(self) -> None:
        """应用筛选并刷新表格"""
        # 应用筛选
        filtered_data = self._filter_manager.apply_filters(self._data_manager.data)
        self._data_manager.set_filtered_data(filtered_data)

        # 更新分页
        if self._show_pagination:
            self._pagination_manager.update_pagination(len(filtered_data))
            start_index, end_index = self._pagination_manager.get_current_page_range()
            page_data = self._data_manager.get_page_data(start_index, end_index)
        else:
            page_data = filtered_data

        # 填充表格
        if self._table_widget is not None:
            self._data_manager.populate_table(
                self._table_widget, page_data, self._editable
            )

    def _on_selection_changed(self) -> None:
        """处理选择变化"""
        selected_rows = self._get_selected_rows()
        self.selection_changed.emit(selected_rows)

        if selected_rows and self._table_widget is not None:
            row_data = self._data_manager.get_row_data_from_table(
                self._table_widget, selected_rows[0]
            )
            self.row_selected.emit(selected_rows[0], row_data)

    def _on_item_double_clicked(self, item: QTableWidgetItem) -> None:
        """处理项目双击"""
        if self._table_widget is None:
            return
        row_index = item.row()
        row_data = self._data_manager.get_row_data_from_table(
            self._table_widget, row_index
        )
        self.row_double_clicked.emit(row_index, row_data)

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        """处理项目变化"""
        if not self._editable:
            return

        row_index = item.row()
        col_index = item.column()
        column = self._columns[col_index]
        new_value = item.text()
        self.data_changed.emit(row_index, column["key"], None, new_value)

    def _on_header_clicked(self, logical_index: int) -> None:
        """处理表头点击（排序）"""
        column = self._columns[logical_index]
        column_key = column["key"]

        # 切换排序顺序
        if self._data_manager.sort_column == column_key:
            new_order = (
                SortOrder.DESC
                if self._data_manager.sort_order == SortOrder.ASC
                else SortOrder.ASC
            )
        else:
            new_order = SortOrder.ASC

        self._data_manager.apply_sort(column_key, new_order)
        self._apply_filters_and_refresh()
        self.sort_changed.emit(column_key, new_order)

    def _on_filter_changed(self) -> None:
        """处理筛选变化"""
        self._pagination_manager.reset_to_first_page()
        self._apply_filters_and_refresh()
        filters = self._filter_manager.get_current_filters()
        self.filter_changed.emit(filters)

    def _emit_page_changed(self, page: int, page_size: int) -> None:
        """发送页面变化信号"""
        self.page_changed.emit(page, page_size)

    def _show_context_menu(self, position: QPoint) -> None:
        """显示右键菜单"""
        if not self._table_widget:
            return

        item = self._table_widget.itemAt(position)
        if not item:
            return

        menu = QMenu(self)
        view_action = QAction("查看详情", self)
        view_action.triggered.connect(lambda: self._on_view_details(item.row()))
        menu.addAction(view_action)

        if self._editable:
            edit_action = QAction("编辑", self)
            edit_action.triggered.connect(lambda: self._on_edit_row(item.row()))
            menu.addAction(edit_action)

            menu.addSeparator()
            delete_action = QAction("删除", self)
            delete_action.triggered.connect(lambda: self._on_delete_row(item.row()))
            menu.addAction(delete_action)

        menu.addSeparator()
        export_selected_action = QAction("导出选中行", self)
        export_selected_action.triggered.connect(
            lambda: self._export_manager.export_selected_data(self.get_selected_data())
        )
        menu.addAction(export_selected_action)

        menu.exec_(self._table_widget.mapToGlobal(position))

    def _get_selected_rows(self) -> list[int]:
        """获取选中的行索引"""
        if not self._table_widget:
            return []

        selected_rows = []
        for item in self._table_widget.selectedItems():
            row = item.row()
            if row not in selected_rows:
                selected_rows.append(row)

        return sorted(selected_rows)

    def _on_view_details(self, row_index: int) -> None:
        """查看详情（占位方法）"""
        QMessageBox.information(self, "查看详情", f"查看第 {row_index + 1} 行详情")

    def _on_edit_row(self, row_index: int) -> None:
        """编辑行（占位方法）"""
        QMessageBox.information(self, "编辑", f"编辑第 {row_index + 1} 行")

    def _on_delete_row(self, row_index: int) -> None:
        """删除行（占位方法）"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除第 {row_index + 1} 行吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.remove_row(row_index)

    def cleanup_resources(self) -> None:
        """清理资源"""
        self._filter_manager.cleanup()
