"""MiniCRM 表格分页管理器模块"""

import logging
from collections.abc import Callable

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QWidget,
)


class TablePaginationManager:
    """表格分页管理器类"""

    def __init__(self, parent: QWidget, page_size: int = 50):
        """初始化分页管理器"""
        self._parent = parent
        self._page_size = page_size
        self._current_page = 1
        self._total_pages = 1
        self._total_rows = 0
        self._logger = logging.getLogger(__name__)

        # UI组件
        self._pagination_frame: QFrame | None = None
        self._page_label: QLabel | None = None
        self._page_spin: QSpinBox | None = None

        # 回调函数（需要父组件设置）
        self.page_changed: Callable[[int, int], None] | None = None

    def create_pagination_ui(self, layout) -> None:
        """创建分页UI"""
        self._pagination_frame = QFrame()
        pagination_layout = QHBoxLayout(self._pagination_frame)
        pagination_layout.setContentsMargins(0, 0, 0, 0)
        pagination_layout.setSpacing(10)

        # 页面信息
        self._page_label = QLabel("第 1 页，共 1 页")
        pagination_layout.addWidget(self._page_label)

        pagination_layout.addStretch()

        # 页面跳转
        pagination_layout.addWidget(QLabel("跳转到:"))
        self._page_spin = QSpinBox()
        self._page_spin.setMinimum(1)
        self._page_spin.setMaximum(1)
        self._page_spin.setValue(1)
        pagination_layout.addWidget(self._page_spin)

        # 导航按钮
        first_btn = QPushButton("⏮️ 首页")
        first_btn.clicked.connect(lambda: self.go_to_page(1))
        pagination_layout.addWidget(first_btn)

        prev_btn = QPushButton("⏪ 上页")
        prev_btn.clicked.connect(self.previous_page)
        pagination_layout.addWidget(prev_btn)

        next_btn = QPushButton("下页 ⏩")
        next_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(next_btn)

        last_btn = QPushButton("末页 ⏭️")
        last_btn.clicked.connect(lambda: self.go_to_page(self._total_pages))
        pagination_layout.addWidget(last_btn)

        layout.addWidget(self._pagination_frame)

    def setup_connections(self) -> None:
        """设置信号连接"""
        if self._page_spin:
            self._page_spin.valueChanged.connect(self.go_to_page)

    def update_pagination(self, total_rows: int) -> None:
        """更新分页信息"""
        try:
            self._total_rows = total_rows
            self._total_pages = max(
                1, (total_rows + self._page_size - 1) // self._page_size
            )

            # 确保当前页面有效
            if self._current_page > self._total_pages:
                self._current_page = self._total_pages

            # 更新UI
            if self._page_label:
                self._page_label.setText(
                    f"第 {self._current_page} 页，共 {self._total_pages} 页 (总计 {total_rows} 条)"
                )

            if self._page_spin:
                self._page_spin.setMaximum(self._total_pages)
                self._page_spin.setValue(self._current_page)

        except Exception as e:
            self._logger.error(f"更新分页信息失败: {e}")

    def go_to_page(self, page: int) -> None:
        """跳转到指定页面"""
        try:
            if 1 <= page <= self._total_pages:
                self._current_page = page
                self.update_pagination(self._total_rows)

                # 发送页面变化回调
                if self.page_changed:
                    self.page_changed(self._current_page, self._page_size)

        except Exception as e:
            self._logger.error(f"跳转页面失败: {e}")

    def next_page(self) -> None:
        """下一页"""
        if self._current_page < self._total_pages:
            self.go_to_page(self._current_page + 1)

    def previous_page(self) -> None:
        """上一页"""
        if self._current_page > 1:
            self.go_to_page(self._current_page - 1)

    def get_current_page_range(self) -> tuple[int, int]:
        """
        获取当前页的数据范围

        Returns:
            tuple: (start_index, end_index)
        """
        start_index = (self._current_page - 1) * self._page_size
        end_index = start_index + self._page_size
        return start_index, end_index

    def reset_to_first_page(self) -> None:
        """重置到第一页"""
        self._current_page = 1

    @property
    def current_page(self) -> int:
        """当前页码"""
        return self._current_page

    @property
    def page_size(self) -> int:
        """每页大小"""
        return self._page_size

    @property
    def total_pages(self) -> int:
        """总页数"""
        return self._total_pages
