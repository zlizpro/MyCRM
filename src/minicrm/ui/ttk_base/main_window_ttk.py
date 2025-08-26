"""TTK主窗口系统

整合所有TTK组件,提供完整的主窗口功能,包括:
- 菜单栏、工具栏、状态栏集成
- 导航面板和页面管理
- 窗口状态保存和恢复
- 主题和样式管理

设计目标:
1. 提供完整的主窗口功能
2. 整合所有TTK组件
3. 替换Qt主窗口
4. 保持良好的用户体验

作者: MiniCRM开发团队
"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Optional

from .base_window import BaseWindow
from .menu_bar import MenuBarTTK, MenuConfig
from .navigation_panel import NavigationItemConfig, NavigationPanelTTK
from .navigation_registry_ttk import NavigationRegistryTTK, register_all_ttk_pages
from .page_manager import PageConfig, PageManagerTTK, PageRouterTTK
from .statusbar import StatusBarTTK, StatusSectionConfig
from .toolbar import ToolBarTTK, ToolButtonConfig


class MainWindowTTK(BaseWindow):
    """TTK主窗口类

    整合菜单栏、工具栏、状态栏、导航面板和页面管理功能,
    提供完整的主窗口解决方案.
    """

    def __init__(
        self,
        title: str = "MiniCRM",
        size: tuple = (1200, 800),
        min_size: tuple = (800, 600),
        **kwargs,
    ):
        """初始化主窗口

        Args:
            title: 窗口标题
            size: 窗口大小
            min_size: 最小大小
            **kwargs: 其他BaseWindow参数
        """
        super().__init__(title, size, min_size, **kwargs)

        # 日志记录器
        self.logger = logging.getLogger(self.__class__.__name__)

        # 组件管理
        self.menu_bar_ttk: Optional[MenuBarTTK] = None
        self.tool_bar_ttk: Optional[ToolBarTTK] = None
        self.status_bar_ttk: Optional[StatusBarTTK] = None
        self.navigation_panel_ttk: Optional[NavigationPanelTTK] = None
        self.page_manager_ttk: Optional[PageManagerTTK] = None
        self.page_router_ttk: Optional[PageRouterTTK] = None
        self.navigation_registry_ttk: Optional[NavigationRegistryTTK] = None

        # 布局管理
        self.main_paned_window: Optional[ttk.PanedWindow] = None
        self.content_frame: Optional[ttk.Frame] = None

        # 初始化主窗口组件
        self._setup_main_window()

    def _setup_main_window(self) -> None:
        """设置主窗口组件"""
        try:
            # 创建菜单栏
            self._create_menu_bar_ttk()

            # 创建工具栏
            self._create_tool_bar_ttk()

            # 创建主要内容区域
            self._create_main_content()

            # 创建状态栏
            self._create_status_bar_ttk()

            # 设置默认菜单和工具栏
            self._setup_default_menus()
            self._setup_default_toolbar()
            self._setup_default_statusbar()

            self.logger.info("TTK主窗口初始化完成")

        except Exception as e:
            self.logger.error(f"TTK主窗口初始化失败: {e}")
            raise

    def _create_menu_bar_ttk(self) -> None:
        """创建TTK菜单栏"""
        self.menu_bar_ttk = MenuBarTTK(self)

    def _create_tool_bar_ttk(self) -> None:
        """创建TTK工具栏"""
        toolbar_frame = self.create_tool_bar(height=40)
        self.tool_bar_ttk = ToolBarTTK(
            parent=toolbar_frame, orientation="horizontal", height=40
        )
        # 将工具栏框架添加到工具栏容器
        self.tool_bar_ttk.get_frame().pack(fill=tk.BOTH, expand=True)

    def _create_status_bar_ttk(self) -> None:
        """创建TTK状态栏"""
        statusbar_frame = self.create_status_bar(height=25)
        self.status_bar_ttk = StatusBarTTK(parent=statusbar_frame, height=25)
        # 将状态栏框架添加到状态栏容器
        self.status_bar_ttk.get_frame().pack(fill=tk.BOTH, expand=True)

    def _create_main_content(self) -> None:
        """创建主要内容区域"""
        # 获取内容框架
        content_frame = self.get_content_frame()

        # 创建水平分割窗口
        self.main_paned_window = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        self.main_paned_window.pack(fill=tk.BOTH, expand=True)

        # 创建导航面板
        self.navigation_panel_ttk = NavigationPanelTTK(
            parent=self.main_paned_window, width=250, min_width=50, collapsible=True
        )

        # 创建页面内容框架
        self.content_frame = ttk.Frame(self.main_paned_window)

        # 添加到分割窗口
        self.main_paned_window.add(self.navigation_panel_ttk.get_frame(), weight=0)
        self.main_paned_window.add(self.content_frame, weight=1)

        # 创建页面管理器
        self.page_manager_ttk = PageManagerTTK(
            container=self.content_frame,
            max_cache_size=10,
            preload_enabled=True,
            lazy_load_enabled=True,
        )

        # 创建页面路由器
        self.page_router_ttk = PageRouterTTK(self.page_manager_ttk)

        # 连接导航面板和页面路由器
        self.navigation_panel_ttk.add_selection_callback(self._on_navigation_selection)

    def setup_navigation_registry(self, app) -> None:
        """设置导航注册系统

        Args:
            app: MiniCRM应用程序实例
        """
        try:
            if not all(
                [self.page_manager_ttk, self.page_router_ttk, self.navigation_panel_ttk]
            ):
                raise ValueError("TTK组件未完全初始化")

            # 创建导航注册系统
            self.navigation_registry_ttk = NavigationRegistryTTK(
                app=app,
                page_manager=self.page_manager_ttk,
                page_router=self.page_router_ttk,
                navigation_panel=self.navigation_panel_ttk,
            )

            # 注册所有TTK页面
            register_all_ttk_pages(self.navigation_registry_ttk)

            self.logger.info("TTK导航注册系统设置完成")

        except Exception as e:
            self.logger.error(f"TTK导航注册系统设置失败: {e}")
            raise

    def _setup_default_menus(self) -> None:
        """设置默认菜单"""
        if not self.menu_bar_ttk:
            return

        # 文件菜单
        file_menu = MenuConfig("文件(&F)", underline=0)
        file_menu.add_command(
            "新建(&N)", command=self._on_new_file, accelerator="Ctrl+N", underline=0
        )
        file_menu.add_separator()
        file_menu.add_command("导入数据(&I)", command=self._on_import_data, underline=0)
        file_menu.add_command("导出数据(&E)", command=self._on_export_data, underline=0)
        file_menu.add_separator()
        file_menu.add_command(
            "退出(&X)", command=self._on_exit, accelerator="Ctrl+Q", underline=0
        )
        self.menu_bar_ttk.add_menu(file_menu)

        # 视图菜单
        view_menu = MenuConfig("视图(&V)", underline=0)

        # 主题选择变量
        theme_var = tk.StringVar(value="light")
        self.menu_bar_ttk.set_menu_item_variable("theme", theme_var)

        view_menu.add_radiobutton(
            "浅色主题", theme_var, "light", command=lambda: self._switch_theme("light")
        )
        view_menu.add_radiobutton(
            "深色主题", theme_var, "dark", command=lambda: self._switch_theme("dark")
        )
        view_menu.add_separator()

        # 导航面板显示控制
        nav_visible_var = tk.BooleanVar(value=True)
        self.menu_bar_ttk.set_menu_item_variable("nav_visible", nav_visible_var)

        view_menu.add_checkbutton(
            "显示导航面板", nav_visible_var, command=self._toggle_navigation_panel
        )

        self.menu_bar_ttk.add_menu(view_menu)

        # 帮助菜单
        help_menu = MenuConfig("帮助(&H)", underline=0)
        help_menu.add_command("关于(&A)", command=self._show_about, underline=0)
        self.menu_bar_ttk.add_menu(help_menu)

    def _setup_default_toolbar(self) -> None:
        """设置默认工具栏"""
        if not self.tool_bar_ttk:
            return

        # 新建按钮
        new_button = ToolButtonConfig(
            button_id="new",
            text="新建",
            command=self._on_new_file,
            tooltip="创建新文件 (Ctrl+N)",
            button_type="button",
        )
        self.tool_bar_ttk.add_button(new_button)

        # 分隔符
        separator1 = ToolButtonConfig(button_id="sep1", button_type="separator")
        self.tool_bar_ttk.add_button(separator1)

        # 刷新按钮
        refresh_button = ToolButtonConfig(
            button_id="refresh",
            text="刷新",
            command=self._on_refresh,
            tooltip="刷新当前页面 (F5)",
            button_type="button",
        )
        self.tool_bar_ttk.add_button(refresh_button)

        # 设置按钮
        settings_button = ToolButtonConfig(
            button_id="settings",
            text="设置",
            command=self._on_settings,
            tooltip="打开设置",
            button_type="button",
        )
        self.tool_bar_ttk.add_button(settings_button)

    def _setup_default_statusbar(self) -> None:
        """设置默认状态栏"""
        if not self.status_bar_ttk:
            return

        # 主状态分区
        main_status = StatusSectionConfig(
            section_id="main", section_type="label", text="就绪", width=200, weight=1
        )
        self.status_bar_ttk.add_section(main_status)

        # 分隔符
        separator = StatusSectionConfig(section_id="sep1", section_type="separator")
        self.status_bar_ttk.add_section(separator)

        # 进度条分区
        progress_section = StatusSectionConfig(
            section_id="progress", section_type="progressbar", width=150
        )
        self.status_bar_ttk.add_section(progress_section)

        # 数据库状态分区
        db_status = StatusSectionConfig(
            section_id="database",
            section_type="label",
            text="数据库: 未连接",
            width=120,
        )
        self.status_bar_ttk.add_section(db_status)

    def _on_navigation_selection(self, item_id: str) -> None:
        """导航选择事件处理

        Args:
            item_id: 选中的导航项ID
        """
        try:
            # 通过路由器导航到对应页面
            success = self.page_router_ttk.navigate_to_page(item_id)
            if success:
                self.set_status_text(f"已切换到: {item_id}")
            else:
                self.set_status_text(f"页面切换失败: {item_id}")

        except Exception as e:
            self.logger.error(f"导航选择处理失败: {e}")
            self.set_status_text(f"导航错误: {e}")

    # 菜单和工具栏事件处理方法
    def _on_new_file(self) -> None:
        """新建文件"""
        self.set_status_text("新建文件功能")

    def _on_import_data(self) -> None:
        """导入数据"""
        self.set_status_text("导入数据功能")

    def _on_export_data(self) -> None:
        """导出数据"""
        self.set_status_text("导出数据功能")

    def _on_exit(self) -> None:
        """退出应用程序"""
        self.quit()

    def _switch_theme(self, theme_name: str) -> None:
        """切换主题

        Args:
            theme_name: 主题名称
        """
        self.set_status_text(f"切换到{theme_name}主题")

    def _toggle_navigation_panel(self) -> None:
        """切换导航面板显示"""
        if self.navigation_panel_ttk:
            self.navigation_panel_ttk.toggle_panel()

    def _on_refresh(self) -> None:
        """刷新当前页面"""
        current_page = (
            self.page_manager_ttk.get_current_page() if self.page_manager_ttk else None
        )
        if current_page:
            self.set_status_text(f"刷新页面: {current_page}")
        else:
            self.set_status_text("没有当前页面")

    def _on_settings(self) -> None:
        """打开设置"""
        self.set_status_text("打开设置功能")

    def _show_about(self) -> None:
        """显示关于对话框"""
        self.show_info(
            "MiniCRM TTK版本\n\n基于Python tkinter/ttk开发的客户关系管理系统",
            "关于 MiniCRM",
        )

    # 公共接口方法
    def add_navigation_item(self, item_config: NavigationItemConfig) -> None:
        """添加导航项

        Args:
            item_config: 导航项配置
        """
        if self.navigation_panel_ttk:
            self.navigation_panel_ttk.add_navigation_item(item_config)

    def register_page(self, page_config: PageConfig) -> None:
        """注册页面

        Args:
            page_config: 页面配置
        """
        if self.page_manager_ttk:
            self.page_manager_ttk.register_page(page_config)

    def register_route(self, route_path: str, page_id: str) -> None:
        """注册路由

        Args:
            route_path: 路由路径
            page_id: 页面ID
        """
        if self.page_router_ttk:
            self.page_router_ttk.register_route(route_path, page_id)

    def navigate_to(self, route_path: str) -> bool:
        """导航到指定路由

        Args:
            route_path: 路由路径

        Returns:
            是否导航成功
        """
        if self.page_router_ttk:
            return self.page_router_ttk.navigate_to(route_path)
        return False

    def set_status_text(self, text: str, section_id: str = "main") -> None:
        """设置状态栏文本

        Args:
            text: 状态文本
            section_id: 状态栏分区ID
        """
        if self.status_bar_ttk:
            self.status_bar_ttk.set_text(section_id, text)

    def set_progress(
        self, value: float, maximum: float = 100.0, section_id: str = "progress"
    ) -> None:
        """设置进度条

        Args:
            value: 进度值
            maximum: 最大值
            section_id: 进度条分区ID
        """
        if self.status_bar_ttk:
            self.status_bar_ttk.set_progress(section_id, value, maximum)

    def show_temporary_message(self, message: str, duration: float = 3.0) -> None:
        """显示临时消息

        Args:
            message: 消息内容
            duration: 显示时长(秒)
        """
        if self.status_bar_ttk:
            self.status_bar_ttk.show_message(message, duration)

    def get_main_window_info(self) -> Dict[str, Any]:
        """获取主窗口信息

        Returns:
            主窗口信息字典
        """
        info = {
            "window_info": self.get_window_info(),
            "menu_bar": None,
            "toolbar": None,
            "statusbar": None,
            "navigation_panel": None,
            "page_manager": None,
            "page_router": None,
        }

        if self.menu_bar_ttk:
            info["menu_bar"] = self.menu_bar_ttk.get_menu_structure()

        if self.tool_bar_ttk:
            info["toolbar"] = self.tool_bar_ttk.get_toolbar_info()

        if self.status_bar_ttk:
            info["statusbar"] = self.status_bar_ttk.get_statusbar_info()

        if self.navigation_panel_ttk:
            info["navigation_panel"] = self.navigation_panel_ttk.get_navigation_info()

        if self.page_manager_ttk:
            info["page_manager"] = self.page_manager_ttk.get_page_info()

        if self.page_router_ttk:
            info["page_router"] = self.page_router_ttk.get_router_info()

        return info

    def cleanup(self) -> None:
        """清理主窗口资源"""
        try:
            # 清理各个组件
            if self.menu_bar_ttk:
                self.menu_bar_ttk.cleanup()

            if self.tool_bar_ttk:
                self.tool_bar_ttk.cleanup()

            if self.status_bar_ttk:
                self.status_bar_ttk.cleanup()

            if self.navigation_panel_ttk:
                self.navigation_panel_ttk.cleanup()

            if self.page_manager_ttk:
                self.page_manager_ttk.cleanup()

            # 调用父类清理
            super().cleanup()

            self.logger.debug("TTK主窗口资源清理完成")

        except Exception as e:
            self.logger.error(f"TTK主窗口资源清理失败: {e}")

    def _can_close(self) -> bool:
        """检查是否可以关闭窗口

        Returns:
            是否可以关闭
        """
        # 可以在这里添加关闭前的检查逻辑
        # 例如检查是否有未保存的数据等
        return True
