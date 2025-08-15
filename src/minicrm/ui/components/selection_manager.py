"""
MiniCRM 表格选择管理器

负责表格行选择状态的管理，包括单选、多选、选择变更通知等功能。
"""

import logging

from PySide6.QtCore import QObject, Signal


class SelectionManager(QObject):
    """
    表格选择管理器类

    负责管理表格行的选择状态，提供选择变更通知。
    支持单选和多选模式。
    """

    # 信号定义
    selection_changed = Signal(list)  # 选中行索引列表

    def __init__(self, parent: QObject = None):
        """
        初始化选择管理器

        Args:
            parent: 父对象
        """
        super().__init__(parent)

        self._logger = logging.getLogger(f"{__name__}.SelectionManager")

        # 选择状态
        self._selected_rows: list[int] = []
        self._max_rows = 0

        self._logger.debug("选择管理器初始化完成")

    def set_max_rows(self, max_rows: int) -> None:
        """
        设置最大行数

        Args:
            max_rows: 最大行数
        """
        self._max_rows = max_rows
        # 清理超出范围的选择
        self._selected_rows = [
            row for row in self._selected_rows if 0 <= row < max_rows
        ]

    def get_selected_rows(self) -> list[int]:
        """
        获取选中的行索引

        Returns:
            List[int]: 选中行索引列表
        """
        return self._selected_rows.copy()

    def set_selected_rows(self, row_indices: list[int]) -> None:
        """
        设置选中的行

        Args:
            row_indices: 行索引列表
        """
        # 过滤有效的行索引
        valid_rows = [i for i in row_indices if 0 <= i < self._max_rows]

        if valid_rows != self._selected_rows:
            self._selected_rows = valid_rows
            self.selection_changed.emit(self._selected_rows)
            self._logger.debug(f"选择已更新: {len(self._selected_rows)}行")

    def add_selection(self, row_index: int) -> None:
        """
        添加行到选择

        Args:
            row_index: 行索引
        """
        if 0 <= row_index < self._max_rows and row_index not in self._selected_rows:
            self._selected_rows.append(row_index)
            self.selection_changed.emit(self._selected_rows)

    def remove_selection(self, row_index: int) -> None:
        """
        从选择中移除行

        Args:
            row_index: 行索引
        """
        if row_index in self._selected_rows:
            self._selected_rows.remove(row_index)
            self.selection_changed.emit(self._selected_rows)

    def toggle_selection(self, row_index: int) -> None:
        """
        切换行的选择状态

        Args:
            row_index: 行索引
        """
        if row_index in self._selected_rows:
            self.remove_selection(row_index)
        else:
            self.add_selection(row_index)

    def clear_selection(self) -> None:
        """清除所有选择"""
        if self._selected_rows:
            self._selected_rows.clear()
            self.selection_changed.emit(self._selected_rows)

    def select_all(self) -> None:
        """选择所有行"""
        all_rows = list(range(self._max_rows))
        if all_rows != self._selected_rows:
            self._selected_rows = all_rows
            self.selection_changed.emit(self._selected_rows)

    def is_selected(self, row_index: int) -> bool:
        """
        检查行是否被选中

        Args:
            row_index: 行索引

        Returns:
            bool: 是否被选中
        """
        return row_index in self._selected_rows

    def get_selection_count(self) -> int:
        """
        获取选中行数量

        Returns:
            int: 选中行数量
        """
        return len(self._selected_rows)

    def has_selection(self) -> bool:
        """
        检查是否有选中的行

        Returns:
            bool: 是否有选中的行
        """
        return bool(self._selected_rows)
