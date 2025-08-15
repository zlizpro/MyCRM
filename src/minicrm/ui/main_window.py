"""
MiniCRM 主窗口

实现应用程序的主窗口界面，包括：
- 现代化的窗口布局
- 侧边导航面板
- 中央内容区域
- 菜单栏和工具栏
- 状态栏
- 主题切换支持
"""

import logging

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QWidget,
)

from minicrm.application import MiniCRMApplication
from minicrm.core.exceptions import UIError
from minicrm.ui.components.dashboard import Dashboard
from minicrm.ui.components.navigation_panel import NavigationPanel
from minicrm.ui.themes.theme_manager import ThemeManager


class MainWindow(QMainWindow):
    """
    MiniCRM 主窗口类

    这是应用程序的主窗口，负责：
    - 整体布局管理
    - 导航和页面切换
    - 菜单和工具栏管理
    - 状态信息显示
    - 主题切换
    - 窗口状态保存和恢复

    Signals:
        page_changed: 页面切换信号 (page_name: str)
        theme_changed: 主题切换信号 (theme_name: str)
    """

    # Qt信号定义
    page_changed = Signal(str)
    theme_changed = Signal(str)

    def __init__(self, app: MiniCRMApplication):
        """
        初始化主窗口

        Args:
            app: MiniCRM应用程序实例
        """
        super().__init__()

        self._app = app
        self._logger = logging.getLogger(__name__)

        # UI组件
        self._central_widget: QWidget | None = None
        self._splitter: QSplitter | None = None
        self._navigation_panel: NavigationPanel | None = None
        self._content_stack: QStackedWidget | None = None
        self._dashboard: Dashboard | None = None

        # 主题管理器
        self._theme_manager = ThemeManager()

        # 状态栏组件
        self._status_label: QLabel | None = None
        self._db_status_label: QLabel | None = None

        # 定时器（用于状态更新）
        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._update_status)

        # 初始化窗口
        self._setup_window()
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_central_widget()
        self._create_status_bar()
        self._setup_connections()
        self._restore_window_state()

        # 应用主题
        self._apply_theme()

        # 启动状态更新定时器
        self._status_timer.start(5000)  # 每5秒更新一次状态

        self._logger.info("主窗口初始化完成")

    def _setup_window(self) -> None:
        """设置窗口基本属性"""
        try:
            # 设置窗口标题和图标
            self.setWindowTitle("MiniCRM - 客户关系管理系统")

            # 设置窗口最小尺寸
            self.setMinimumSize(1024, 768)

            # 设置默认窗口大小
            geometry = self._app.config.get_window_geometry()
            self.resize(geometry["width"], geometry["height"])

            if geometry["maximized"]:
                self.showMaximized()

            # 设置窗口居中
            self._center_window()

        except Exception as e:
            self._logger.error(f"窗口设置失败: {e}")
            raise UIError(f"窗口设置失败: {e}", "MainWindow") from e

    def _center_window(self) -> None:
        """将窗口居中显示"""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())

    def _create_menu_bar(self) -> None:
        """创建菜单栏"""
        try:
            menu_bar = self.menuBar()

            # 文件菜单
            file_menu = menu_bar.addMenu("文件(&F)")

            # 新建菜单项
            new_action = QAction("新建客户(&N)", self)
            new_action.setShortcut(QKeySequence.New)
            new_action.setStatusTip("创建新客户")
            new_action.triggered.connect(self._on_new_customer)
            file_menu.addAction(new_action)

            file_menu.addSeparator()

            # 导入导出菜单项
            import_action = QAction("导入数据(&I)", self)
            import_action.setStatusTip("从文件导入数据")
            import_action.triggered.connect(self._on_import_data)
            file_menu.addAction(import_action)

            export_action = QAction("导出数据(&E)", self)
            export_action.setStatusTip("导出数据到文件")
            export_action.triggered.connect(self._on_export_data)
            file_menu.addAction(export_action)

            file_menu.addSeparator()

            # 退出菜单项
            exit_action = QAction("退出(&X)", self)
            exit_action.setShortcut(QKeySequence.Quit)
            exit_action.setStatusTip("退出应用程序")
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            # 视图菜单
            view_menu = menu_bar.addMenu("视图(&V)")

            # 主题切换菜单项
            light_theme_action = QAction("浅色主题", self)
            light_theme_action.setCheckable(True)
            light_theme_action.triggered.connect(lambda: self._switch_theme("light"))
            view_menu.addAction(light_theme_action)

            dark_theme_action = QAction("深色主题", self)
            dark_theme_action.setCheckable(True)
            dark_theme_action.triggered.connect(lambda: self._switch_theme("dark"))
            view_menu.addAction(dark_theme_action)

            # 帮助菜单
            help_menu = menu_bar.addMenu("帮助(&H)")

            about_action = QAction("关于(&A)", self)
            about_action.setStatusTip("关于MiniCRM")
            about_action.triggered.connect(self._show_about)
            help_menu.addAction(about_action)

        except Exception as e:
            self._logger.error(f"菜单栏创建失败: {e}")
            raise UIError(f"菜单栏创建失败: {e}", "MainWindow") from e

    def _create_tool_bar(self) -> None:
        """创建工具栏"""
        try:
            tool_bar = self.addToolBar("主工具栏")
            tool_bar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

            # 新建客户按钮
            new_customer_action = QAction("新建客户", self)
            new_customer_action.setStatusTip("创建新客户")
            new_customer_action.triggered.connect(self._on_new_customer)
            tool_bar.addAction(new_customer_action)

            tool_bar.addSeparator()

            # 刷新按钮
            refresh_action = QAction("刷新", self)
            refresh_action.setShortcut(QKeySequence.Refresh)
            refresh_action.setStatusTip("刷新当前页面")
            refresh_action.triggered.connect(self._on_refresh)
            tool_bar.addAction(refresh_action)

            tool_bar.addSeparator()

            # 设置按钮
            settings_action = QAction("设置", self)
            settings_action.setStatusTip("打开设置")
            settings_action.triggered.connect(self._on_settings)
            tool_bar.addAction(settings_action)

        except Exception as e:
            self._logger.error(f"工具栏创建失败: {e}")
            raise UIError(f"工具栏创建失败: {e}", "MainWindow") from e

    def _create_central_widget(self) -> None:
        """创建中央部件"""
        try:
            # 创建中央部件
            self._central_widget = QWidget()
            self.setCentralWidget(self._central_widget)

            # 创建主布局
            main_layout = QHBoxLayout(self._central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)

            # 创建分割器
            self._splitter = QSplitter(Qt.Horizontal)
            main_layout.addWidget(self._splitter)

            # 创建导航面板
            self._navigation_panel = NavigationPanel()
            self._navigation_panel.setMaximumWidth(300)
            self._navigation_panel.setMinimumWidth(200)
            self._splitter.addWidget(self._navigation_panel)

            # 创建内容堆栈
            self._content_stack = QStackedWidget()
            self._splitter.addWidget(self._content_stack)

            # 设置分割器比例
            sidebar_width = self._app.config.get_sidebar_width()
            self._splitter.setSizes([sidebar_width, 1000])

            # 创建页面
            self._create_pages()

        except Exception as e:
            self._logger.error(f"中央部件创建失败: {e}")
            raise UIError(f"中央部件创建失败: {e}", "MainWindow") from e

    def _create_pages(self) -> None:
        """创建各个页面"""
        try:
            # 创建仪表盘页面
            self._dashboard = Dashboard(self._app)
            self._content_stack.addWidget(self._dashboard)

            # TODO: 创建其他页面
            # - 客户管理页面
            # - 供应商管理页面
            # - 报表页面
            # - 设置页面

            # 设置默认页面
            self._content_stack.setCurrentWidget(self._dashboard)

        except Exception as e:
            self._logger.error(f"页面创建失败: {e}")
            raise UIError(f"页面创建失败: {e}", "MainWindow") from e

    def _create_status_bar(self) -> None:
        """创建状态栏"""
        try:
            status_bar = self.statusBar()

            # 主状态标签
            self._status_label = QLabel("就绪")
            status_bar.addWidget(self._status_label)

            # 添加分隔符
            status_bar.addPermanentWidget(QLabel("|"))

            # 数据库状态标签
            self._db_status_label = QLabel("数据库: 未连接")
            status_bar.addPermanentWidget(self._db_status_label)

            # 更新初始状态
            self._update_status()

        except Exception as e:
            self._logger.error(f"状态栏创建失败: {e}")
            raise UIError(f"状态栏创建失败: {e}", "MainWindow") from e

    def _setup_connections(self) -> None:
        """设置信号连接"""
        try:
            # 导航面板信号连接
            if self._navigation_panel:
                self._navigation_panel.page_requested.connect(self._switch_page)

            # 应用程序信号连接
            self._app.startup_completed.connect(self._on_app_startup_completed)
            self._app.shutdown_started.connect(self._on_app_shutdown_started)
            self._app.service_error.connect(self._on_service_error)

        except Exception as e:
            self._logger.error(f"信号连接设置失败: {e}")

    def _apply_theme(self) -> None:
        """应用主题"""
        try:
            theme_mode = self._app.config.get_theme_mode()
            theme_stylesheet = self._theme_manager.get_stylesheet(theme_mode.value)
            self.setStyleSheet(theme_stylesheet)

            self._logger.debug(f"应用主题: {theme_mode.value}")

        except Exception as e:
            self._logger.error(f"主题应用失败: {e}")

    def _switch_theme(self, theme_name: str) -> None:
        """切换主题"""
        try:
            from minicrm.core.config import ThemeMode

            theme_mode = ThemeMode(theme_name)
            self._app.config.set_theme_mode(theme_mode)

            self._apply_theme()
            self.theme_changed.emit(theme_name)

            self._logger.info(f"主题切换为: {theme_name}")

        except Exception as e:
            self._logger.error(f"主题切换失败: {e}")
            self._show_error("主题切换失败", str(e))

    def _switch_page(self, page_name: str) -> None:
        """切换页面"""
        try:
            # TODO: 根据页面名称切换到对应页面
            if page_name == "dashboard" and self._dashboard:
                self._content_stack.setCurrentWidget(self._dashboard)

            self.page_changed.emit(page_name)
            self._logger.debug(f"切换到页面: {page_name}")

        except Exception as e:
            self._logger.error(f"页面切换失败: {e}")
            self._show_error("页面切换失败", str(e))

    def _update_status(self) -> None:
        """更新状态栏信息"""
        try:
            # 更新数据库状态
            if self._app.database_manager:
                self._db_status_label.setText("数据库: 已连接")
            else:
                self._db_status_label.setText("数据库: 未连接")

            # 更新主状态
            if self._app.is_initialized:
                self._status_label.setText("就绪")
            else:
                self._status_label.setText("正在初始化...")

        except Exception as e:
            self._logger.error(f"状态更新失败: {e}")

    def _restore_window_state(self) -> None:
        """恢复窗口状态"""
        try:
            # 恢复窗口几何信息
            geometry = self._app.config.get_qt_setting("window_geometry")
            if geometry:
                self.restoreGeometry(geometry)

            # 恢复窗口状态
            state = self._app.config.get_qt_setting("window_state")
            if state:
                self.restoreState(state)

        except Exception as e:
            self._logger.error(f"窗口状态恢复失败: {e}")

    def _save_window_state(self) -> None:
        """保存窗口状态"""
        try:
            # 保存窗口几何信息
            self._app.config.set_qt_setting("window_geometry", self.saveGeometry())

            # 保存窗口状态
            self._app.config.set_qt_setting("window_state", self.saveState())

            # 保存分割器状态
            if self._splitter:
                sizes = self._splitter.sizes()
                if len(sizes) >= 2:
                    self._app.config.set_sidebar_width(sizes[0])

        except Exception as e:
            self._logger.error(f"窗口状态保存失败: {e}")

    # 事件处理方法
    def _on_new_customer(self) -> None:
        """新建客户"""
        # TODO: 实现新建客户功能
        self._show_info("功能开发中", "新建客户功能正在开发中...")

    def _on_import_data(self) -> None:
        """导入数据"""
        # TODO: 实现数据导入功能
        self._show_info("功能开发中", "数据导入功能正在开发中...")

    def _on_export_data(self) -> None:
        """导出数据"""
        # TODO: 实现数据导出功能
        self._show_info("功能开发中", "数据导出功能正在开发中...")

    def _on_refresh(self) -> None:
        """刷新当前页面"""
        try:
            current_widget = self._content_stack.currentWidget()
            if hasattr(current_widget, "refresh"):
                current_widget.refresh()

            self._logger.debug("页面刷新完成")

        except Exception as e:
            self._logger.error(f"页面刷新失败: {e}")
            self._show_error("刷新失败", str(e))

    def _on_settings(self) -> None:
        """打开设置"""
        # TODO: 实现设置功能
        self._show_info("功能开发中", "设置功能正在开发中...")

    def _show_about(self) -> None:
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 MiniCRM",
            "MiniCRM v0.1.0\n\n"
            "一个现代化的客户关系管理系统\n"
            "基于 Python 和 PySide6 开发\n\n"
            "© 2025 MiniCRM Team",
        )

    # 应用程序事件处理
    def _on_app_startup_completed(self) -> None:
        """应用程序启动完成"""
        self._logger.info("应用程序启动完成")
        self._update_status()

    def _on_app_shutdown_started(self) -> None:
        """应用程序开始关闭"""
        self._logger.info("应用程序开始关闭")
        self._status_label.setText("正在关闭...")

    def _on_service_error(self, service_name: str, error_message: str) -> None:
        """服务错误处理"""
        self._logger.error(f"服务错误 [{service_name}]: {error_message}")
        self._show_error(f"{service_name}服务错误", error_message)

    # 工具方法
    def _show_info(self, title: str, message: str) -> None:
        """显示信息对话框"""
        QMessageBox.information(self, title, message)

    def _show_warning(self, title: str, message: str) -> None:
        """显示警告对话框"""
        QMessageBox.warning(self, title, message)

    def _show_error(self, title: str, message: str) -> None:
        """显示错误对话框"""
        QMessageBox.critical(self, title, message)

    # Qt事件重写
    def closeEvent(self, event) -> None:  # noqa: N802
        """窗口关闭事件"""
        try:
            # 保存窗口状态
            self._save_window_state()

            # 停止定时器
            self._status_timer.stop()

            # 关闭应用程序
            self._app.shutdown()

            # 接受关闭事件
            event.accept()

            self._logger.info("主窗口关闭")

        except Exception as e:
            self._logger.error(f"窗口关闭处理失败: {e}")
            event.accept()  # 即使出错也要关闭窗口

    def resizeEvent(self, event) -> None:  # noqa: N802
        """窗口大小改变事件"""
        super().resizeEvent(event)

        # 保存窗口大小到配置
        if not self.isMaximized():
            size = event.size()
            self._app.config.set_window_geometry(
                size.width(), size.height(), self.isMaximized()
            )
