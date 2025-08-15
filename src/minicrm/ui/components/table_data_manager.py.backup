"""
MiniCRM 表格数据管理器

负责表格数据的管理，包括数据设置、获取、增删改查操作。
提供统一的数据接口和格式化功能。
"""

import logging
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

# 导入单元格格式化器和选择管理器
from .cell_formatter import format_cell_value
from .selection_manager import SelectionManager


class TableDataManager(QObject):
    """
    表格数据管理器类

    负责表格数据的完整生命周期管理：
    - 数据存储和访问
    - 数据格式化和转换
    - 数据变更通知
    - 选择状态管理
    """

    # 信号定义
    data_changed = Signal()
    selection_changed = Signal(list)  # 选中行索引列表
    row_added = Signal(int)  # 新增行索引
    row_updated = Signal(int)  # 更新行索引
    row_removed = Signal(int)  # 删除行索引

    def __init__(self, columns: list[dict[str, Any]], parent: QObject = None):
        """
        初始化数据管理器

        Args:
            columns: 列配置列表
            parent: 父对象
        """
        super().__init__(parent)

        self._logger = logging.getLogger(f"{__name__}.TableDataManager")

        # 数据存储
        self._columns = columns
        self._data: list[dict[str, Any]] = []
        self._filtered_data: list[dict[str, Any]] = []
        self._original_data: list[dict[str, Any]] = []

        # 表格组件引用
        self._table_widget: QTableWidget | None = None

        # 状态管理
        self._selection_manager = SelectionManager(self)
        self._modified_rows: set[int] = set()

        # 连接选择管理器信号
        self._selection_manager.selection_changed.connect(self.selection_changed.emit)

        self._logger.debug(f"数据管理器初始化完成: {len(columns)}列")

    def set_table_widget(self, table_widget: QTableWidget) -> None:
        """
        设置表格组件引用

        Args:
            table_widget: 表格组件
        """
        self._table_widget = table_widget
        self._logger.debug("表格组件引用已设置")

    def set_data(self, data: list[dict[str, Any]]) -> None:
        """
        设置表格数据

        Args:
            data: 数据列表
        """
        try:
            self._data = data.copy()
            self._original_data = data.copy()
            self._filtered_data = data.copy()
            self._modified_rows.clear()

            self._populate_table()

            # 更新选择管理器的最大行数
            self._selection_manager.set_max_rows(len(self._filtered_data))

            self.data_changed.emit()

            self._logger.debug(f"设置表格数据完成: {len(data)}行")

        except Exception as e:
            self._logger.error(f"设置表格数据失败: {e}")

    def get_data(self) -> list[dict[str, Any]]:
        """
        获取当前数据

        Returns:
            List[Dict[str, Any]]: 当前数据列表
        """
        return self._data.copy()

    def get_filtered_data(self) -> list[dict[str, Any]]:
        """
        获取筛选后的数据

        Returns:
            List[Dict[str, Any]]: 筛选后的数据列表
        """
        return self._filtered_data.copy()

    def add_row(self, row_data: dict[str, Any]) -> int:
        """
        添加行数据

        Args:
            row_data: 行数据

        Returns:
            int: 新行的索引
        """
        try:
            # 添加到原始数据
            self._data.append(row_data)

            # 检查是否符合当前筛选条件
            if self._should_include_in_filter(row_data):
                self._filtered_data.append(row_data)
                new_index = len(self._filtered_data) - 1
                self._add_table_row(new_index, row_data)

            row_index = len(self._data) - 1
            self.row_added.emit(row_index)
            self.data_changed.emit()

            self._logger.debug(f"添加行数据完成: 索引 {row_index}")
            return row_index

        except Exception as e:
            self._logger.error(f"添加行数据失败: {e}")
            return -1

    def update_row(self, row_index: int, row_data: dict[str, Any]) -> bool:
        """
        更新行数据

        Args:
            row_index: 行索引
            row_data: 新的行数据

        Returns:
            bool: 是否更新成功
        """
        try:
            if 0 <= row_index < len(self._data):
                self._data[row_index] = row_data
                self._modified_rows.add(row_index)

                # 更新筛选数据
                self._update_filtered_data()
                self._populate_table()

                self.row_updated.emit(row_index)
                self.data_changed.emit()

                self._logger.debug(f"更新行数据完成: 索引 {row_index}")
                return True

            return False

        except Exception as e:
            self._logger.error(f"更新行数据失败: {e}")
            return False

    def remove_row(self, row_index: int) -> bool:
        """
        删除行数据

        Args:
            row_index: 行索引

        Returns:
            bool: 是否删除成功
        """
        try:
            if 0 <= row_index < len(self._data):
                removed_data = self._data.pop(row_index)

                # 从筛选数据中移除
                if removed_data in self._filtered_data:
                    self._filtered_data.remove(removed_data)

                # 更新修改状态
                self._modified_rows.discard(row_index)
                # 调整其他修改行的索引
                self._modified_rows = {
                    i - 1 if i > row_index else i for i in self._modified_rows
                }

                self._populate_table()

                self.row_removed.emit(row_index)
                self.data_changed.emit()

                self._logger.debug(f"删除行数据完成: 索引 {row_index}")
                return True

            return False

        except Exception as e:
            self._logger.error(f"删除行数据失败: {e}")
            return False

    def get_row_data(self, row_index: int) -> dict[str, Any] | None:
        """
        获取指定行的数据

        Args:
            row_index: 行索引

        Returns:
            Optional[Dict[str, Any]]: 行数据，如果索引无效则返回None
        """
        try:
            if 0 <= row_index < len(self._filtered_data):
                return self._filtered_data[row_index].copy()
            return None

        except Exception as e:
            self._logger.error(f"获取行数据失败: {e}")
            return None

    def get_selected_rows(self) -> list[int]:
        """
        获取选中的行索引

        Returns:
            List[int]: 选中行索引列表
        """
        return self._selection_manager.get_selected_rows()

    def get_selected_data(self) -> list[dict[str, Any]]:
        """
        获取选中行的数据

        Returns:
            List[Dict[str, Any]]: 选中行数据列表
        """
        return [
            self.get_row_data(row_index)
            for row_index in self._selection_manager.get_selected_rows()
            if self.get_row_data(row_index) is not None
        ]

    def set_selected_rows(self, row_indices: list[int]) -> None:
        """
        设置选中的行

        Args:
            row_indices: 行索引列表
        """
        self._selection_manager.set_selected_rows(row_indices)

    def format_cell_value(self, value: Any, column: dict[str, Any]) -> str:
        """
        格式化单元格值 - 委托给专门的格式化器

        Args:
            value: 原始值
            column: 列配置

        Returns:
            str: 格式化后的字符串
        """
        return format_cell_value(value, column)

    def apply_filter(self, filter_func: Callable) -> None:
        """
        应用筛选条件

        Args:
            filter_func: 筛选函数，接受行数据，返回bool
        """
        try:
            self._filtered_data = [row for row in self._data if filter_func(row)]

            self._populate_table()
            self.data_changed.emit()

            self._logger.debug(
                f"应用筛选完成: {len(self._filtered_data)}/{len(self._data)}行"
            )

        except Exception as e:
            self._logger.error(f"应用筛选失败: {e}")

    def clear_filter(self) -> None:
        """清除筛选条件"""
        self._filtered_data = self._data.copy()
        self._populate_table()
        self.data_changed.emit()
        self._logger.debug("筛选条件已清除")

    def is_modified(self) -> bool:
        """
        检查数据是否已修改

        Returns:
            bool: 是否已修改
        """
        return bool(self._modified_rows) or len(self._data) != len(self._original_data)

    def get_modified_rows(self) -> list[int]:
        """
        获取已修改的行索引

        Returns:
            List[int]: 已修改行索引列表
        """
        return list(self._modified_rows)

    def reset_modifications(self) -> None:
        """重置修改状态"""
        self._modified_rows.clear()
        self._original_data = self._data.copy()

    def _populate_table(self) -> None:
        """填充表格数据"""
        try:
            if not self._table_widget:
                return

            # 设置行数和列数
            self._table_widget.setRowCount(len(self._filtered_data))
            self._table_widget.setColumnCount(len(self._columns))

            # 设置表头
            headers = [col.get("title", col.get("key", "")) for col in self._columns]
            self._table_widget.setHorizontalHeaderLabels(headers)

            # 填充数据
            for row_index, row_data in enumerate(self._filtered_data):
                for col_index, column in enumerate(self._columns):
                    column_key = column.get("key", "")
                    raw_value = row_data.get(column_key, "")

                    # 格式化值
                    formatted_value = self.format_cell_value(raw_value, column)

                    # 创建表格项
                    item = QTableWidgetItem(formatted_value)

                    # 设置原始值作为用户数据
                    item.setData(0x0100, raw_value)  # Qt.UserRole

                    # 设置只读属性
                    if column.get("readonly", False):
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                    self._table_widget.setItem(row_index, col_index, item)

        except Exception as e:
            self._logger.error(f"填充表格数据失败: {e}")

    def _add_table_row(self, row_index: int, row_data: dict[str, Any]) -> None:
        """添加表格行"""
        try:
            if not self._table_widget:
                return

            self._table_widget.insertRow(row_index)

            for col_index, column in enumerate(self._columns):
                column_key = column.get("key", "")
                raw_value = row_data.get(column_key, "")
                formatted_value = self.format_cell_value(raw_value, column)

                item = QTableWidgetItem(formatted_value)
                item.setData(0x0100, raw_value)

                if column.get("readonly", False):
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                self._table_widget.setItem(row_index, col_index, item)

        except Exception as e:
            self._logger.error(f"添加表格行失败: {e}")

    def _should_include_in_filter(self, row_data: dict[str, Any]) -> bool:
        """
        检查行数据是否应该包含在筛选结果中

        Args:
            row_data: 行数据

        Returns:
            bool: 是否包含
        """
        # 这里可以实现具体的筛选逻辑
        # 目前返回True表示包含所有数据
        return True

    def _update_filtered_data(self) -> None:
        """更新筛选数据"""
        # 重新应用当前的筛选条件
        # 这里简化处理，实际应该保存筛选条件并重新应用
        self._filtered_data = self._data.copy()

    def get_column_config(self, column_key: str) -> dict[str, Any] | None:
        """
        获取列配置

        Args:
            column_key: 列键名

        Returns:
            Optional[Dict[str, Any]]: 列配置，如果不存在则返回None
        """
        for column in self._columns:
            if column.get("key") == column_key:
                return column.copy()
        return None

    def get_columns(self) -> list[dict[str, Any]]:
        """
        获取所有列配置

        Returns:
            List[Dict[str, Any]]: 列配置列表
        """
        return self._columns.copy()

    def get_row_count(self) -> int:
        """获取数据行数"""
        return len(self._filtered_data)

    def get_total_row_count(self) -> int:
        """获取总行数（未筛选）"""
        return len(self._data)
