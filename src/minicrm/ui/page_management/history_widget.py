"""
MiniCRM 导航历史记录组件

显示用户的页面访问历史，支持快速导航
"""

import datetime
import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .page_base import NavigationHistory


class NavigationHistoryWidget(QWidget):
    """
    导航历史记录组件

    显示用户的页面访问历史，支持快速导航
    """

    # 历史记录点击信号
    history_item_clicked = Signal(str, dict)

    def __init__(self, parent: QWidget | None = None):
        """
        初始化历史记录组件

        Args:
            parent: 父组件
        """
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)
        self._history_items: list[NavigationHistory] = []

        # 设置UI
        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置用户界面"""

        # 创建垂直布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # 标题
        title_label = QLabel("访问历史")
        title_label.setStyleSheet("font-weight: bold; color: #495057;")
        layout.addWidget(title_label)

        # 历史记录列表
        self._history_list = QListWidget()
        self._history_list.setMaximumHeight(200)
        self._history_list.itemClicked.connect(self._on_history_item_clicked)
        layout.addWidget(self._history_list)

        # 设置样式
        self.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }

            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f8f9fa;
            }

            QListWidget::item:hover {
                background-color: #e9ecef;
            }

            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)

    def update_history(self, history_items: list[NavigationHistory]) -> None:
        """
        更新历史记录

        Args:
            history_items: 历史记录列表
        """
        try:
            self._history_items = history_items.copy()
            self._history_list.clear()

            # 显示最近的历史记录（倒序）
            for history_item in reversed(history_items[-10:]):  # 只显示最近10条
                self._add_history_item(history_item)

        except Exception as e:
            self._logger.error(f"历史记录更新失败: {e}")

    def _add_history_item(self, history_item: NavigationHistory) -> None:
        """添加历史记录项"""

        # 格式化时间
        timestamp = datetime.datetime.fromtimestamp(history_item.timestamp)
        time_str = timestamp.strftime("%H:%M:%S")

        # 创建列表项
        item_text = f"{time_str} - {history_item.page_name}"
        list_item = QListWidgetItem(item_text)
        list_item.setData(Qt.ItemDataRole.UserRole, history_item)

        self._history_list.addItem(list_item)

    def _on_history_item_clicked(self, item: QListWidgetItem) -> None:
        """处理历史记录项点击"""
        try:
            history_item = item.data(Qt.ItemDataRole.UserRole)
            if history_item:
                self.history_item_clicked.emit(
                    history_item.page_name, history_item.params
                )
                self._logger.debug(f"历史记录点击: {history_item.page_name}")

        except Exception as e:
            self._logger.error(f"历史记录点击处理失败: {e}")
