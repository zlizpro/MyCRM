"""
MiniCRM 表格分页管理器

负责表格的分页功能，包括分页控件创建、页面导航和分页状态管理。
支持自定义页面大小和分页信息显示。
"""

import logging
from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


# 导入transfunctions计算函数
try:
    from transfunctions.calculations import calculate_pagination

    _TRANSFUNCTIONS_AVAILABLE = True
except ImportError:
    _TRANSFUNCTIONS_AVAILABLE = False


class TablePaginationManager(QObject):
    """
    表格分页管理器类

    提供完整的分页功能：
    - 分页控件创建和管理
    - 页面导航
    - 分页状态管理
    - 分页信息显示
    """

    # 信号定义
    page_changed = Signal(int)  # 页面变化
    page_size_changed = Signal(int)  # 页面大小变化

    def __init__(self, page_size: int = 50, parent: QObject = None):
        """
        初始化分页管理器

        Args:
            page_size: 每页显示的行数
            parent: 父对象
        """
        super().__init__(parent)

        self._logger = logging.getLogger(f"{__name__}.TablePaginationManager")

        # 分页配置
        self._page_size = page_size
        self._current_page = 1
        self._total_rows = 0
        self._total_pages = 0

        # UI组件
        self._pagination_frame: QFrame | None = None
        self._info_label: QLabel | None = None
        self._first_button: QPushButton | None = None
        self._prev_button: QPushButton | None = None
        self._next_button: QPushButton | None = None
        self._last_button: QPushButton | None = None
        self._page_spin: QSpinBox | None = None
        self._page_size_spin: QSpinBox | None = None

        self._logger.debug(f"分页管理器初始化完成: 每页{page_size}行")

    def create_pagination_widget(self, layout: QVBoxLayout) -> None:
        """
        创建分页控件

        Args:
            layout: 布局容器
        """
        try:
            self._pagination_frame = QFrame()
            self._pagination_frame.setObjectName("paginationFrame")

            pagination_layout = QHBoxLayout(self._pagination_frame)
            pagination_layout.setContentsMargins(10, 5, 10, 5)
            pagination_layout.setSpacing(10)

            # 信息标签
            self._info_label = QLabel()
            pagination_layout.addWidget(self._info_label)

            # 弹性空间
            pagination_layout.addStretch()

            # 页面大小选择
            self._create_page_size_selector(pagination_layout)

            # 导航按钮
            self._create_navigation_buttons(pagination_layout)

            # 页面跳转
            self._create_page_jumper(pagination_layout)

            layout.addWidget(self._pagination_frame)

            # 初始化状态
            self._update_pagination_info()
            self._update_button_states()

            self._logger.debug("分页控件创建完成")

        except Exception as e:
            self._logger.error(f"创建分页控件失败: {e}")

    def _create_page_size_selector(self, layout: QHBoxLayout) -> None:
        """创建页面大小选择器"""
        layout.addWidget(QLabel("每页显示:"))

        self._page_size_spin = QSpinBox()
        self._page_size_spin.setMinimum(10)
        self._page_size_spin.setMaximum(500)
        self._page_size_spin.setValue(self._page_size)
        self._page_size_spin.setSuffix(" 行")
        self._page_size_spin.valueChanged.connect(self._on_page_size_changed)

        layout.addWidget(self._page_size_spin)

    def _create_navigation_buttons(self, layout: QHBoxLayout) -> None:
        """创建导航按钮"""
        # 首页按钮
        self._first_button = QPushButton("首页")
        self._first_button.clicked.connect(self.go_to_first_page)
        layout.addWidget(self._first_button)

        # 上一页按钮
        self._prev_button = QPushButton("上一页")
        self._prev_button.clicked.connect(self.go_to_previous_page)
        layout.addWidget(self._prev_button)

        # 下一页按钮
        self._next_button = QPushButton("下一页")
        self._next_button.clicked.connect(self.go_to_next_page)
        layout.addWidget(self._next_button)

        # 末页按钮
        self._last_button = QPushButton("末页")
        self._last_button.clicked.connect(self.go_to_last_page)
        layout.addWidget(self._last_button)

    def _create_page_jumper(self, layout: QHBoxLayout) -> None:
        """创建页面跳转器"""
        layout.addWidget(QLabel("跳转到第"))

        self._page_spin = QSpinBox()
        self._page_spin.setMinimum(1)
        self._page_spin.setValue(self._current_page)
        self._page_spin.valueChanged.connect(self._on_page_spin_changed)

        layout.addWidget(self._page_spin)
        layout.addWidget(QLabel("页"))

    def set_total_rows(self, total_rows: int) -> None:
        """
        设置总行数

        Args:
            total_rows: 总行数
        """
        try:
            self._total_rows = total_rows
            self._calculate_total_pages()
            self._update_pagination_info()
            self._update_button_states()

            # 如果当前页超出范围，跳转到最后一页
            if self._current_page > self._total_pages and self._total_pages > 0:
                self.go_to_page(self._total_pages)

            self._logger.debug(f"设置总行数: {total_rows}, 总页数: {self._total_pages}")

        except Exception as e:
            self._logger.error(f"设置总行数失败: {e}")

    def _calculate_total_pages(self) -> None:
        """计算总页数 - 使用transfunctions标准计算函数"""
        if _TRANSFUNCTIONS_AVAILABLE:
            try:
                result = calculate_pagination(self._total_rows, self._page_size)
                self._total_pages = result.total_pages
                return
            except Exception as e:
                self._logger.warning(f"transfunctions计算失败，使用本地实现: {e}")

        # 本地实现作为回退
        if self._page_size > 0:
            self._total_pages = max(
                1, (self._total_rows + self._page_size - 1) // self._page_size
            )
        else:
            self._total_pages = 1

    def go_to_page(self, page: int) -> None:
        """
        跳转到指定页面

        Args:
            page: 页面号（从1开始）
        """
        try:
            if 1 <= page <= self._total_pages:
                old_page = self._current_page
                self._current_page = page

                self._update_pagination_info()
                self._update_button_states()

                if self._page_spin:
                    self._page_spin.setValue(page)

                if old_page != page:
                    self.page_changed.emit(page)

                self._logger.debug(f"跳转到第{page}页")

        except Exception as e:
            self._logger.error(f"跳转页面失败: {e}")

    def go_to_first_page(self) -> None:
        """跳转到首页"""
        self.go_to_page(1)

    def go_to_last_page(self) -> None:
        """跳转到末页"""
        self.go_to_page(self._total_pages)

    def go_to_next_page(self) -> None:
        """跳转到下一页"""
        if self._current_page < self._total_pages:
            self.go_to_page(self._current_page + 1)

    def go_to_previous_page(self) -> None:
        """跳转到上一页"""
        if self._current_page > 1:
            self.go_to_page(self._current_page - 1)

    def _on_page_spin_changed(self, page: int) -> None:
        """处理页面跳转器变化"""
        self.go_to_page(page)

    def _on_page_size_changed(self, page_size: int) -> None:
        """处理页面大小变化"""
        try:
            old_page_size = self._page_size
            self._page_size = page_size

            # 重新计算页面
            self._calculate_total_pages()

            # 尝试保持当前数据位置
            current_row = (self._current_page - 1) * old_page_size
            new_page = max(1, (current_row // page_size) + 1)

            self._current_page = min(new_page, self._total_pages)

            self._update_pagination_info()
            self._update_button_states()

            if self._page_spin:
                self._page_spin.setValue(self._current_page)

            self.page_size_changed.emit(page_size)
            self.page_changed.emit(self._current_page)

            self._logger.debug(f"页面大小变更: {old_page_size} -> {page_size}")

        except Exception as e:
            self._logger.error(f"处理页面大小变化失败: {e}")

    def _update_pagination_info(self) -> None:
        """更新分页信息显示"""
        try:
            if not self._info_label:
                return

            if self._total_rows == 0:
                info_text = "暂无数据"
            else:
                start_row = (self._current_page - 1) * self._page_size + 1
                end_row = min(self._current_page * self._page_size, self._total_rows)

                info_text = (
                    f"显示第 {start_row}-{end_row} 条，共 {self._total_rows} 条记录"
                )

            self._info_label.setText(info_text)

        except Exception as e:
            self._logger.error(f"更新分页信息失败: {e}")

    def _update_button_states(self) -> None:
        """更新按钮状态"""
        try:
            has_data = self._total_rows > 0
            is_first_page = self._current_page <= 1
            is_last_page = self._current_page >= self._total_pages

            if self._first_button:
                self._first_button.setEnabled(has_data and not is_first_page)

            if self._prev_button:
                self._prev_button.setEnabled(has_data and not is_first_page)

            if self._next_button:
                self._next_button.setEnabled(has_data and not is_last_page)

            if self._last_button:
                self._last_button.setEnabled(has_data and not is_last_page)

            if self._page_spin:
                self._page_spin.setEnabled(has_data)
                self._page_spin.setMaximum(max(1, self._total_pages))

        except Exception as e:
            self._logger.error(f"更新按钮状态失败: {e}")

    def get_current_page(self) -> int:
        """
        获取当前页面号

        Returns:
            int: 当前页面号
        """
        return self._current_page

    def get_page_size(self) -> int:
        """
        获取页面大小

        Returns:
            int: 页面大小
        """
        return self._page_size

    def get_total_pages(self) -> int:
        """
        获取总页数

        Returns:
            int: 总页数
        """
        return self._total_pages

    def get_total_rows(self) -> int:
        """
        获取总行数

        Returns:
            int: 总行数
        """
        return self._total_rows

    def get_page_range(self) -> tuple[int, int]:
        """
        获取当前页面的数据范围

        Returns:
            tuple[int, int]: (起始索引, 结束索引)，用于数据切片
        """
        start_index = (self._current_page - 1) * self._page_size
        end_index = start_index + self._page_size
        return start_index, end_index

    def is_pagination_enabled(self) -> bool:
        """
        检查是否启用分页

        Returns:
            bool: 是否启用分页
        """
        return self._total_rows > self._page_size

    def set_visible(self, visible: bool) -> None:
        """
        设置分页控件可见性

        Args:
            visible: 是否可见
        """
        if self._pagination_frame:
            self._pagination_frame.setVisible(visible)

    def get_pagination_info(self) -> dict[str, Any]:
        """
        获取分页信息

        Returns:
            Dict[str, Any]: 分页信息字典
        """
        return {
            "current_page": self._current_page,
            "page_size": self._page_size,
            "total_pages": self._total_pages,
            "total_rows": self._total_rows,
            "start_row": (self._current_page - 1) * self._page_size + 1,
            "end_row": min(self._current_page * self._page_size, self._total_rows),
            "has_previous": self._current_page > 1,
            "has_next": self._current_page < self._total_pages,
        }

    def reset(self) -> None:
        """重置分页状态"""
        try:
            self._current_page = 1
            self._total_rows = 0
            self._total_pages = 0

            self._update_pagination_info()
            self._update_button_states()

            if self._page_spin:
                self._page_spin.setValue(1)

            self._logger.debug("分页状态已重置")

        except Exception as e:
            self._logger.error(f"重置分页状态失败: {e}")

    def apply_styles(self) -> None:
        """应用样式"""
        if self._pagination_frame:
            self._pagination_frame.setStyleSheet("""
                QFrame#paginationFrame {
                    border-top: 1px solid #dee2e6;
                    background-color: #f8f9fa;
                }

                QPushButton {
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    padding: 6px 12px;
                    background-color: white;
                    min-width: 60px;
                }

                QPushButton:hover {
                    background-color: #e9ecef;
                }

                QPushButton:pressed {
                    background-color: #dee2e6;
                }

                QPushButton:disabled {
                    color: #6c757d;
                    background-color: #e9ecef;
                    border-color: #dee2e6;
                }

                QSpinBox {
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    padding: 4px;
                    background-color: white;
                }

                QLabel {
                    color: #495057;
                }
            """)
