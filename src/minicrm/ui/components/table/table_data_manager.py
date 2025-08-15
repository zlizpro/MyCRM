"""MiniCRM 表格数据管理器模块"""

import logging
from enum import Enum
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


# 导入transfunctions格式化函数
try:
    from transfunctions.formatting import format_currency, format_date

    _TRANSFUNCTIONS_AVAILABLE = True
except ImportError:
    _TRANSFUNCTIONS_AVAILABLE = False


class SortOrder(Enum):
    """排序顺序枚举"""

    ASC = "asc"
    DESC = "desc"


class TableDataManager:
    """表格数据管理器类"""

    def __init__(self, columns: list[dict[str, Any]]):
        """初始化数据管理器"""
        self._columns = columns
        self._logger = logging.getLogger(__name__)

        # 数据
        self._data: list[dict[str, Any]] = []
        self._filtered_data: list[dict[str, Any]] = []

        # 排序
        self._sort_column: str | None = None
        self._sort_order: SortOrder = SortOrder.ASC

    def set_data(self, data: list[dict[str, Any]]) -> None:
        """设置数据"""
        try:
            self._data = data.copy()
            self._filtered_data = data.copy()
            self._logger.debug(f"数据设置完成: {len(data)}行")

        except Exception as e:
            self._logger.error(f"设置数据失败: {e}")

    def add_row(self, row_data: dict[str, Any]) -> None:
        """添加行数据"""
        try:
            self._data.append(row_data)
            self._logger.debug("行数据添加完成")

        except Exception as e:
            self._logger.error(f"添加行数据失败: {e}")

    def update_row(self, row_index: int, row_data: dict[str, Any]) -> None:
        """更新行数据"""
        try:
            if 0 <= row_index < len(self._data):
                self._data[row_index] = row_data
                self._logger.debug(f"行数据更新完成: 第{row_index}行")

        except Exception as e:
            self._logger.error(f"更新行数据失败: {e}")

    def remove_row(self, row_index: int) -> None:
        """删除行数据"""
        try:
            if 0 <= row_index < len(self._data):
                del self._data[row_index]
                self._logger.debug(f"行数据删除完成: 第{row_index}行")

        except Exception as e:
            self._logger.error(f"删除行数据失败: {e}")

    def apply_sort(self, column_key: str, order: SortOrder) -> None:
        """应用排序"""
        try:
            self._sort_column = column_key
            self._sort_order = order

            reverse = order == SortOrder.DESC
            self._filtered_data.sort(
                key=lambda x: str(x.get(column_key, "")), reverse=reverse
            )

            self._logger.debug(f"排序应用完成: {column_key} {order.value}")

        except Exception as e:
            self._logger.error(f"应用排序失败: {e}")

    def set_filtered_data(self, filtered_data: list[dict[str, Any]]) -> None:
        """设置筛选后的数据"""
        self._filtered_data = filtered_data

        # 重新应用排序
        if self._sort_column:
            self.apply_sort(self._sort_column, self._sort_order)

    def get_page_data(self, start_index: int, end_index: int) -> list[dict[str, Any]]:
        """获取指定范围的数据"""
        return self._filtered_data[start_index:end_index]

    def populate_table(
        self,
        table_widget: QTableWidget,
        page_data: list[dict[str, Any]],
        editable: bool = False,
    ) -> None:
        """填充表格数据"""
        try:
            if not table_widget:
                return

            # 设置行数
            table_widget.setRowCount(len(page_data))

            # 填充数据
            for row_index, row_data in enumerate(page_data):
                for col_index, column in enumerate(self._columns):
                    value = row_data.get(column["key"], "")

                    # 格式化值
                    formatted_value = self._format_cell_value(value, column)

                    # 创建表格项
                    item = QTableWidgetItem(str(formatted_value))

                    # 设置编辑属性
                    if not editable or not column.get("editable", True):
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                    # 设置对齐方式
                    alignment = column.get(
                        "alignment",
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    )
                    item.setTextAlignment(alignment)

                    table_widget.setItem(row_index, col_index, item)

        except Exception as e:
            self._logger.error(f"填充表格数据失败: {e}")

    def _format_cell_value(self, value: Any, column: dict[str, Any]) -> str:
        """
        格式化单元格值 - 使用transfunctions标准格式化函数

        Args:
            value: 要格式化的值
            column: 列配置信息

        Returns:
            str: 格式化后的字符串
        """
        try:
            if value is None:
                return ""

            column_type = column.get("type", "text")

            if column_type == "currency":
                try:
                    num_value = float(value)
                    if _TRANSFUNCTIONS_AVAILABLE:
                        return format_currency(num_value)
                    else:
                        return f"¥{num_value:,.2f}"
                except (ValueError, TypeError):
                    return str(value)

            elif column_type == "percentage":
                try:
                    num_value = float(value)
                    return f"{num_value:.1f}%"
                except (ValueError, TypeError):
                    return str(value)

            elif column_type == "date":
                if _TRANSFUNCTIONS_AVAILABLE:
                    return format_date(str(value))
                else:
                    return str(value)

            else:
                return str(value)

        except Exception as e:
            self._logger.error(f"格式化单元格值失败: {e}")
            return str(value)

    def get_row_data_from_table(
        self, table_widget: QTableWidget, row_index: int
    ) -> dict[str, Any]:
        """从表格获取指定行的数据"""
        if not table_widget or row_index >= table_widget.rowCount():
            return {}

        row_data = {}
        for i, column in enumerate(self._columns):
            item = table_widget.item(row_index, i)
            if item:
                row_data[column["key"]] = item.text()

        return row_data

    def get_selected_data(self, table_widget: QTableWidget) -> list[dict[str, Any]]:
        """获取选中行的数据"""
        if not table_widget:
            return []

        selected_rows = []
        for item in table_widget.selectedItems():
            row = item.row()
            if row not in selected_rows:
                selected_rows.append(row)

        return [
            self.get_row_data_from_table(table_widget, row)
            for row in sorted(selected_rows)
        ]

    @property
    def data(self) -> list[dict[str, Any]]:
        """原始数据"""
        return self._data

    @property
    def filtered_data(self) -> list[dict[str, Any]]:
        """筛选后的数据"""
        return self._filtered_data

    @property
    def sort_column(self) -> str | None:
        """当前排序列"""
        return self._sort_column

    @property
    def sort_order(self) -> SortOrder:
        """当前排序顺序"""
        return self._sort_order
