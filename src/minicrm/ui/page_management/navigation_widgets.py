"""
MiniCRM 导航组件

包含面包屑导航和导航工具栏组件
"""

import logging

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QToolButton,
    QWidget,
)


class BreadcrumbWidget(QWidget):
    """
    面包屑导航组件

    显示当前页面的导航路径
    """

    # 面包屑点击信号
    breadcrumb_clicked = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        """
        初始化面包屑组件

        Args:
            parent: 父组件
        """
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)
        self._breadcrumb_items: list[str] = []

        # 设置UI
        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置用户界面"""

        # 创建水平布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)

        # 设置样式
        self.setStyleSheet("""
            BreadcrumbWidget {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }

            QPushButton {
                background: transparent;
                border: none;
                color: #007bff;
                text-decoration: underline;
                padding: 2px 4px;
            }

            QPushButton:hover {
                color: #0056b3;
            }

            QLabel {
                color: #6c757d;
                margin: 0 2px;
            }
        """)

    def update_breadcrumb(self, breadcrumb_items: list[str]) -> None:
        """
        更新面包屑内容

        Args:
            breadcrumb_items: 面包屑项目列表
        """
        try:
            # 清空现有内容
            self._clear_layout()

            # 保存面包屑项目
            self._breadcrumb_items = breadcrumb_items.copy()

            if not breadcrumb_items:
                return

            layout = self.layout()
            if layout is None:
                return

            # 添加面包屑项目
            for i, item in enumerate(breadcrumb_items):
                # 添加分隔符（除了第一个项目）
                if i > 0:
                    separator = QLabel(" > ")
                    layout.addWidget(separator)

                # 添加面包屑按钮
                if i < len(breadcrumb_items) - 1:
                    # 可点击的面包屑项目
                    button = QPushButton(item)
                    button.clicked.connect(
                        lambda checked, idx=i: self._on_breadcrumb_clicked(idx)
                    )
                    layout.addWidget(button)
                else:
                    # 当前页面（不可点击）
                    label = QLabel(item)
                    label.setStyleSheet("color: #495057; font-weight: bold;")
                    layout.addWidget(label)

            # 添加弹性空间
            if hasattr(layout, "addStretch"):
                layout.addStretch()

        except Exception as e:
            self._logger.error(f"面包屑更新失败: {e}")

    def _clear_layout(self) -> None:
        """清空布局中的所有组件"""
        layout = self.layout()
        if layout is None:
            return

        while layout.count():
            child = layout.takeAt(0)
            if child and child.widget():
                child.widget().deleteLater()

    def _on_breadcrumb_clicked(self, index: int) -> None:
        """处理面包屑点击事件"""
        try:
            if 0 <= index < len(self._breadcrumb_items):
                item = self._breadcrumb_items[index]
                self.breadcrumb_clicked.emit(item)
                self._logger.debug(f"面包屑点击: {item}")

        except Exception as e:
            self._logger.error(f"面包屑点击处理失败: {e}")


class NavigationToolbar(QWidget):
    """
    导航工具栏

    提供导航相关的工具按钮，如前进、后退、刷新等
    """

    # 工具栏信号
    back_clicked = Signal()
    forward_clicked = Signal()
    refresh_clicked = Signal()
    home_clicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        """
        初始化导航工具栏

        Args:
            parent: 父组件
        """
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)

        # 设置UI
        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置用户界面"""

        # 创建水平布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        # 后退按钮
        self._back_button = QToolButton()
        self._back_button.setText("◀")
        self._back_button.setToolTip("后退")
        self._back_button.setFixedSize(QSize(30, 30))
        self._back_button.clicked.connect(self.back_clicked.emit)
        layout.addWidget(self._back_button)

        # 前进按钮
        self._forward_button = QToolButton()
        self._forward_button.setText("▶")
        self._forward_button.setToolTip("前进")
        self._forward_button.setFixedSize(QSize(30, 30))
        self._forward_button.clicked.connect(self.forward_clicked.emit)
        layout.addWidget(self._forward_button)

        # 分隔符
        layout.addSpacing(10)

        # 刷新按钮
        self._refresh_button = QToolButton()
        self._refresh_button.setText("🔄")
        self._refresh_button.setToolTip("刷新")
        self._refresh_button.setFixedSize(QSize(30, 30))
        self._refresh_button.clicked.connect(self.refresh_clicked.emit)
        layout.addWidget(self._refresh_button)

        # 主页按钮
        self._home_button = QToolButton()
        self._home_button.setText("🏠")
        self._home_button.setToolTip("主页")
        self._home_button.setFixedSize(QSize(30, 30))
        self._home_button.clicked.connect(self.home_clicked.emit)
        layout.addWidget(self._home_button)

        # 弹性空间
        layout.addStretch()

        # 设置样式
        self.setStyleSheet("""
            QToolButton {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }

            QToolButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }

            QToolButton:pressed {
                background-color: #dee2e6;
            }

            QToolButton:disabled {
                color: #6c757d;
                background-color: #f8f9fa;
                border-color: #dee2e6;
            }
        """)

    def set_back_enabled(self, enabled: bool) -> None:
        """设置后退按钮状态"""
        self._back_button.setEnabled(enabled)

    def set_forward_enabled(self, enabled: bool) -> None:
        """设置前进按钮状态"""
        self._forward_button.setEnabled(enabled)
