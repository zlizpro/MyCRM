"""
MiniCRM 导航面板组件

实现左侧导航面板，提供：
- 树形导航结构
- 图标和文字显示
- 展开/折叠功能
- 选中状态管理
- 现代化样式
"""

import logging

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .navigation_config import NavigationConfig
from .navigation_styles import NavigationStyles
from .navigation_types import NavigationItem


class NavigationPanel(QWidget):
    """
    导航面板组件

    提供应用程序的主要导航功能，包括：
    - 分层的导航结构
    - 图标和文字显示
    - 展开/折叠状态管理
    - 选中项高亮显示
    - 响应式布局

    Signals:
        page_requested: 页面请求信号 (page_name: str)
        item_selected: 导航项选中信号 (item_name: str)
    """

    # Qt信号定义
    page_requested = Signal(str)
    item_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        """
        初始化导航面板

        Args:
            parent: 父组件
        """
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)

        # UI组件
        self._tree_widget: QTreeWidget | None = None
        self._title_label: QLabel | None = None

        # 导航数据
        self._navigation_items: dict[str, NavigationItem] = {}
        self._tree_items: dict[str, QTreeWidgetItem] = {}

        # 配置和样式管理器
        self._config = NavigationConfig()
        self._styles = NavigationStyles()

        # 设置组件
        self._setup_ui()
        self._setup_navigation_items()
        self._setup_connections()

        self._logger.debug("导航面板初始化完成")

    def _setup_ui(self) -> None:
        """设置用户界面"""
        try:
            # 设置主布局
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            # 创建标题区域
            self._create_title_area(layout)

            # 创建导航树
            self._create_navigation_tree(layout)

            # 设置样式
            self._apply_styles()

        except Exception as e:
            self._logger.error(f"导航面板UI设置失败: {e}")
            raise

    def _create_title_area(self, layout: QVBoxLayout) -> None:
        """创建标题区域"""
        # 创建标题容器
        title_frame = QFrame()
        title_frame.setObjectName("navigationTitle")
        title_frame.setFixedHeight(60)

        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(15, 10, 15, 10)

        # 创建标题标签
        self._title_label = QLabel("MiniCRM")
        self._title_label.setObjectName("navigationTitleLabel")

        # 设置标题字体
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self._title_label.setFont(title_font)

        title_layout.addWidget(self._title_label)
        layout.addWidget(title_frame)

    def _create_navigation_tree(self, layout: QVBoxLayout) -> None:
        """创建导航树"""
        # 创建树形控件
        self._tree_widget = QTreeWidget()
        self._tree_widget.setObjectName("navigationTree")

        # 设置树形控件属性
        self._tree_widget.setHeaderHidden(True)
        self._tree_widget.setRootIsDecorated(True)
        self._tree_widget.setIndentation(20)
        self._tree_widget.setUniformRowHeights(True)
        self._tree_widget.setAnimated(True)

        # 设置选择模式
        self._tree_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self._tree_widget.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        # 设置项目高度
        self._tree_widget.setIconSize(QSize(20, 20))

        layout.addWidget(self._tree_widget)

    def _setup_navigation_items(self) -> None:
        """设置导航项"""
        try:
            # 获取导航数据
            navigation_data = self._config.get_default_navigation_items()

            # 构建导航树
            self._build_navigation_tree(navigation_data)

            # 展开所有顶级项
            self._tree_widget.expandAll()

            # 选中默认项（仪表盘）
            if "dashboard" in self._tree_items:
                self._tree_widget.setCurrentItem(self._tree_items["dashboard"])

        except Exception as e:
            self._logger.error(f"导航项设置失败: {e}")
            raise

    def _build_navigation_tree(self, navigation_data: list[NavigationItem]) -> None:
        """构建导航树"""
        # 清空现有项
        self._tree_widget.clear()
        self._navigation_items.clear()
        self._tree_items.clear()

        # 添加顶级项
        for item_data in navigation_data:
            self._add_navigation_item(item_data)

    def _add_navigation_item(
        self, item_data: NavigationItem, parent_item: QTreeWidgetItem | None = None
    ) -> QTreeWidgetItem:
        """添加导航项"""
        # 创建树项
        if parent_item:
            tree_item = QTreeWidgetItem(parent_item)
        else:
            tree_item = QTreeWidgetItem(self._tree_widget)

        # 设置文本
        tree_item.setText(0, item_data.display_name)

        # 设置数据
        tree_item.setData(0, Qt.ItemDataRole.UserRole, item_data.name)

        # 设置图标（如果有）
        if item_data.icon:
            icon = QIcon(item_data.icon)
            tree_item.setIcon(0, icon)

        # 存储项目
        self._navigation_items[item_data.name] = item_data
        self._tree_items[item_data.name] = tree_item

        # 添加子项
        if item_data.children:
            for child_data in item_data.children:
                self._add_navigation_item(child_data, tree_item)

        return tree_item

    def _setup_connections(self) -> None:
        """设置信号连接"""
        if self._tree_widget:
            self._tree_widget.itemClicked.connect(self._on_item_clicked)
            self._tree_widget.itemDoubleClicked.connect(self._on_item_double_clicked)

    def _apply_styles(self) -> None:
        """应用样式"""
        stylesheet = self._styles.get_default_stylesheet()
        self.setStyleSheet(stylesheet)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """处理项目点击事件"""
        try:
            item_name = item.data(0, Qt.ItemDataRole.UserRole)
            if item_name in self._navigation_items:
                nav_item = self._navigation_items[item_name]

                # 发送选中信号
                self.item_selected.emit(item_name)

                # 如果有页面名称，发送页面请求信号
                if nav_item.page_name:
                    self.page_requested.emit(nav_item.page_name)
                    self._logger.debug(f"请求页面: {nav_item.page_name}")

        except Exception as e:
            self._logger.error(f"导航项点击处理失败: {e}")

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """处理项目双击事件"""
        try:
            # 双击时展开/折叠项目
            if item.childCount() > 0:
                item.setExpanded(not item.isExpanded())

        except Exception as e:
            self._logger.error(f"导航项双击处理失败: {e}")

    def select_item(self, item_name: str) -> bool:
        """
        选中指定的导航项

        Args:
            item_name: 导航项名称

        Returns:
            bool: 是否成功选中
        """
        try:
            if item_name in self._tree_items:
                tree_item = self._tree_items[item_name]
                self._tree_widget.setCurrentItem(tree_item)

                # 确保父项展开
                parent = tree_item.parent()
                while parent:
                    parent.setExpanded(True)
                    parent = parent.parent()

                return True

            return False

        except Exception as e:
            self._logger.error(f"选中导航项失败: {e}")
            return False

    def get_selected_item(self) -> str | None:
        """
        获取当前选中的导航项

        Returns:
            Optional[str]: 选中的导航项名称，如果没有选中则返回None
        """
        try:
            current_item = self._tree_widget.currentItem()
            if current_item:
                return current_item.data(0, Qt.ItemDataRole.UserRole)
            return None

        except Exception as e:
            self._logger.error(f"获取选中项失败: {e}")
            return None

    def expand_all(self) -> None:
        """展开所有项目"""
        if self._tree_widget:
            self._tree_widget.expandAll()

    def collapse_all(self) -> None:
        """折叠所有项目"""
        if self._tree_widget:
            self._tree_widget.collapseAll()

    def refresh(self) -> None:
        """刷新导航面板"""
        try:
            # 保存当前选中项
            selected_item = self.get_selected_item()

            # 重新设置导航项
            self._setup_navigation_items()

            # 恢复选中项
            if selected_item:
                self.select_item(selected_item)

            self._logger.debug("导航面板刷新完成")

        except Exception as e:
            self._logger.error(f"导航面板刷新失败: {e}")

    def set_item_enabled(self, item_name: str, enabled: bool) -> None:
        """
        设置导航项的启用状态

        Args:
            item_name: 导航项名称
            enabled: 是否启用
        """
        try:
            if item_name in self._tree_items:
                tree_item = self._tree_items[item_name]
                tree_item.setDisabled(not enabled)

        except Exception as e:
            self._logger.error(f"设置导航项状态失败: {e}")

    def add_badge(self, item_name: str, badge_text: str) -> None:
        """
        为导航项添加徽章

        Args:
            item_name: 导航项名称
            badge_text: 徽章文本
        """
        try:
            if item_name in self._tree_items and item_name in self._navigation_items:
                tree_item = self._tree_items[item_name]
                nav_item = self._navigation_items[item_name]

                # 更新显示文本，添加徽章
                display_text = f"{nav_item.display_name} ({badge_text})"
                tree_item.setText(0, display_text)

        except Exception as e:
            self._logger.error(f"添加徽章失败: {e}")

    def remove_badge(self, item_name: str) -> None:
        """
        移除导航项的徽章

        Args:
            item_name: 导航项名称
        """
        try:
            if item_name in self._tree_items and item_name in self._navigation_items:
                tree_item = self._tree_items[item_name]
                nav_item = self._navigation_items[item_name]

                # 恢复原始显示文本
                tree_item.setText(0, nav_item.display_name)

        except Exception as e:
            self._logger.error(f"移除徽章失败: {e}")

    def set_theme(self, theme_name: str) -> None:
        """
        设置主题

        Args:
            theme_name: 主题名称 ('light' 或 'dark')
        """
        try:
            if theme_name == "dark":
                stylesheet = self._styles.get_dark_theme_stylesheet()
            else:
                stylesheet = self._styles.get_default_stylesheet()

            self.setStyleSheet(stylesheet)
            self._logger.debug(f"导航面板主题切换为: {theme_name}")

        except Exception as e:
            self._logger.error(f"主题切换失败: {e}")
