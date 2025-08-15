"""
MiniCRM 页面管理器组合组件

集成页面管理器、面包屑导航、历史记录等功能
"""

import logging

from PySide6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget

from .history_widget import NavigationHistoryWidget
from .navigation_widgets import BreadcrumbWidget, NavigationToolbar
from .page_manager import PageManager
from .page_router import PageRouter


class PageManagerWidget(QWidget):
    """
    页面管理器组合组件

    集成页面管理器、面包屑导航、历史记录等功能
    """

    def __init__(self, parent: QWidget | None = None):
        """
        初始化页面管理器组合组件

        Args:
            parent: 父组件
        """
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)

        # 创建组件
        self._content_stack = QStackedWidget()
        self._page_manager = PageManager(self._content_stack, self)
        self._page_router = PageRouter(self._page_manager)
        self._breadcrumb_widget = BreadcrumbWidget()
        self._navigation_toolbar = NavigationToolbar()
        self._history_widget = NavigationHistoryWidget()

        # 设置UI
        self._setup_ui()
        self._setup_connections()

        # 注册默认路由
        self._setup_default_routes()

    def _setup_ui(self) -> None:
        """设置用户界面"""

        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 添加导航工具栏
        layout.addWidget(self._navigation_toolbar)

        # 添加面包屑导航
        layout.addWidget(self._breadcrumb_widget)

        # 添加内容区域
        layout.addWidget(self._content_stack)

        # 历史记录组件默认隐藏
        self._history_widget.hide()

    def _setup_connections(self) -> None:
        """设置信号连接"""
        # 页面管理器信号
        self._page_manager.breadcrumb_changed.connect(
            self._breadcrumb_widget.update_breadcrumb
        )
        self._page_manager.history_changed.connect(self._history_widget.update_history)

        # 面包屑点击
        self._breadcrumb_widget.breadcrumb_clicked.connect(self._on_breadcrumb_clicked)

        # 导航工具栏信号
        self._navigation_toolbar.back_clicked.connect(self._page_manager.go_back)
        self._navigation_toolbar.forward_clicked.connect(self._page_manager.go_forward)
        self._navigation_toolbar.refresh_clicked.connect(
            self._page_manager.refresh_current_page
        )
        self._navigation_toolbar.home_clicked.connect(self._on_home_clicked)

        # 历史记录点击
        self._history_widget.history_item_clicked.connect(self._on_history_item_clicked)

    def _setup_default_routes(self) -> None:
        """设置默认路由"""
        # TODO: 根据实际需要添加默认路由
        pass

    def _on_breadcrumb_clicked(self, breadcrumb_title: str) -> None:
        """处理面包屑点击"""
        try:
            # 根据面包屑标题查找对应的页面
            for page_name, page_info in self._page_manager.get_all_pages().items():
                if page_info.title == breadcrumb_title:
                    self._page_manager.navigate_to(page_name)
                    break

        except Exception as e:
            self._logger.error(f"面包屑导航失败: {e}")

    def _on_home_clicked(self) -> None:
        """处理主页按钮点击"""
        try:
            self._page_router.navigate_to_default()
        except Exception as e:
            self._logger.error(f"主页导航失败: {e}")

    def _on_history_item_clicked(self, page_name: str, params: dict) -> None:
        """处理历史记录点击"""
        try:
            self._page_manager.navigate_to(page_name, params)
        except Exception as e:
            self._logger.error(f"历史记录导航失败: {e}")

    # 公共接口方法
    @property
    def page_manager(self) -> PageManager:
        """获取页面管理器"""
        return self._page_manager

    @property
    def page_router(self) -> PageRouter:
        """获取页面路由器"""
        return self._page_router

    @property
    def content_stack(self) -> QStackedWidget:
        """获取内容堆栈"""
        return self._content_stack

    def show_history_widget(self) -> None:
        """显示历史记录组件"""
        self._history_widget.show()

    def hide_history_widget(self) -> None:
        """隐藏历史记录组件"""
        self._history_widget.hide()

    def cleanup(self) -> None:
        """清理资源"""
        try:
            self._page_manager.cleanup()
            self._logger.debug("页面管理器组合组件清理完成")
        except Exception as e:
            self._logger.error(f"页面管理器组合组件清理失败: {e}")
