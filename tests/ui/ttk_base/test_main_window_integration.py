"""TTK主窗口系统集成测试

测试MainWindowTTK类的完整功能，包括：
- 主窗口的创建和初始化
- 菜单栏、工具栏、状态栏集成
- 导航面板和页面管理集成
- 窗口状态保存和恢复
- 组件间的交互和协作

作者: MiniCRM开发团队
"""

import tkinter as tk
import unittest


# 处理无头环境中的tkinter问题
try:
    # 尝试创建一个测试窗口来检查tkinter是否可用
    test_root = tk.Tk()
    test_root.withdraw()
    test_root.destroy()
    TKINTER_AVAILABLE = True
except Exception:
    TKINTER_AVAILABLE = False

from src.minicrm.ui.ttk_base.main_window_ttk import MainWindowTTK
from src.minicrm.ui.ttk_base.navigation_panel import NavigationItemConfig
from src.minicrm.ui.ttk_base.page_manager import BasePage, PageConfig


# 测试页面类
class TestPage(BasePage):
    """测试页面类"""

    def create_ui(self):
        """创建UI"""
        from tkinter import ttk

        frame = ttk.Frame(self.parent)
        label = ttk.Label(frame, text=f"测试页面: {self.page_id}")
        label.pack(expand=True)
        return frame


@unittest.skipUnless(TKINTER_AVAILABLE, "tkinter not available in this environment")
class TestMainWindowTTKIntegration(unittest.TestCase):
    """MainWindowTTK集成测试"""

    def setUp(self):
        """测试准备"""
        # 创建主窗口
        self.main_window = MainWindowTTK(
            title="测试主窗口",
            size=(1000, 700),
            min_size=(800, 600),
            center=False,  # 不居中以避免在测试环境中的问题
        )
        self.main_window.withdraw()  # 隐藏窗口

    def tearDown(self):
        """测试清理"""
        try:
            if self.main_window:
                self.main_window.cleanup()
                self.main_window.destroy()
        except Exception as e:
            print(f"测试清理失败: {e}")

    def test_main_window_initialization(self):
        """测试主窗口初始化"""
        # 验证窗口基本属性
        self.assertEqual(self.main_window.title(), "测试主窗口")
        self.assertGreaterEqual(self.main_window.winfo_reqwidth(), 800)
        self.assertGreaterEqual(self.main_window.winfo_reqheight(), 600)

        # 验证组件创建
        self.assertIsNotNone(self.main_window.menu_bar_ttk)
        self.assertIsNotNone(self.main_window.tool_bar_ttk)
        self.assertIsNotNone(self.main_window.status_bar_ttk)
        self.assertIsNotNone(self.main_window.navigation_panel_ttk)
        self.assertIsNotNone(self.main_window.page_manager_ttk)
        self.assertIsNotNone(self.main_window.page_router_ttk)

        # 验证布局组件
        self.assertIsNotNone(self.main_window.main_paned_window)
        self.assertIsNotNone(self.main_window.content_frame)

    def test_menu_bar_integration(self):
        """测试菜单栏集成"""
        menu_bar = self.main_window.menu_bar_ttk

        # 验证默认菜单存在
        menu_structure = menu_bar.get_menu_structure()
        self.assertIn("文件(&F)", menu_structure)
        self.assertIn("视图(&V)", menu_structure)
        self.assertIn("帮助(&H)", menu_structure)

        # 验证文件菜单项
        file_menu = menu_structure["文件(&F)"]
        file_items = [
            item["label"] for item in file_menu["items"] if item["type"] != "separator"
        ]
        self.assertIn("新建(&N)", file_items)
        self.assertIn("导入数据(&I)", file_items)
        self.assertIn("导出数据(&E)", file_items)
        self.assertIn("退出(&X)", file_items)

    def test_toolbar_integration(self):
        """测试工具栏集成"""
        toolbar = self.main_window.tool_bar_ttk

        # 验证默认工具按钮存在
        toolbar_info = toolbar.get_toolbar_info()
        self.assertGreater(toolbar_info["button_count"], 0)

        button_ids = list(toolbar_info["buttons"].keys())
        self.assertIn("new", button_ids)
        self.assertIn("refresh", button_ids)
        self.assertIn("settings", button_ids)

        # 验证按钮状态
        for button_id in ["new", "refresh", "settings"]:
            button_info = toolbar_info["buttons"][button_id]
            self.assertEqual(button_info["state"], "normal")

    def test_statusbar_integration(self):
        """测试状态栏集成"""
        statusbar = self.main_window.status_bar_ttk

        # 验证默认状态栏分区存在
        statusbar_info = statusbar.get_statusbar_info()
        self.assertGreater(statusbar_info["section_count"], 0)

        sections = statusbar_info["sections"]
        self.assertIn("main", sections)
        self.assertIn("progress", sections)
        self.assertIn("database", sections)

        # 测试状态文本设置
        self.main_window.set_status_text("测试状态")
        self.assertEqual(statusbar.get_text("main"), "测试状态")

        # 测试进度条设置
        self.main_window.set_progress(50.0)
        self.assertEqual(statusbar.get_progress("progress"), 50.0)

    def test_navigation_panel_integration(self):
        """测试导航面板集成"""
        navigation_panel = self.main_window.navigation_panel_ttk

        # 添加导航项
        nav_item = NavigationItemConfig(
            item_id="test_nav", text="测试导航", tooltip="测试导航项"
        )
        self.main_window.add_navigation_item(nav_item)

        # 验证导航项添加
        nav_info = navigation_panel.get_navigation_info()
        self.assertEqual(nav_info["item_count"], 1)
        self.assertIn("test_nav", nav_info["items"])

        # 测试导航面板折叠
        navigation_panel.collapse_panel()
        self.assertTrue(navigation_panel.is_collapsed)

        navigation_panel.expand_panel()
        self.assertFalse(navigation_panel.is_collapsed)

    def test_page_manager_integration(self):
        """测试页面管理器集成"""
        page_manager = self.main_window.page_manager_ttk

        # 注册测试页面
        page_config = PageConfig(
            page_id="test_page", page_class=TestPage, title="测试页面", cache=True
        )
        self.main_window.register_page(page_config)

        # 验证页面注册
        page_info = page_manager.get_page_info()
        self.assertEqual(page_info["total_pages"], 1)

        # 显示页面
        success = page_manager.show_page("test_page")
        self.assertTrue(success)
        self.assertEqual(page_info["current_page"], "test_page")

    def test_page_router_integration(self):
        """测试页面路由器集成"""
        page_router = self.main_window.page_router_ttk

        # 注册页面和路由
        page_config = PageConfig(
            page_id="routed_page", page_class=TestPage, title="路由页面"
        )
        self.main_window.register_page(page_config)
        self.main_window.register_route("/test", "routed_page")

        # 验证路由注册
        router_info = page_router.get_router_info()
        self.assertEqual(router_info["total_routes"], 1)
        self.assertIn("/test", router_info["routes"])

        # 测试路由导航
        success = self.main_window.navigate_to("/test")
        self.assertTrue(success)
        self.assertEqual(page_router.get_current_route(), "/test")

    def test_navigation_to_page_integration(self):
        """测试导航到页面的完整流程"""
        # 注册页面
        page_config = PageConfig(
            page_id="integration_page", page_class=TestPage, title="集成测试页面"
        )
        self.main_window.register_page(page_config)

        # 添加导航项
        nav_item = NavigationItemConfig(
            item_id="integration_page", text="集成测试页面", tooltip="集成测试页面"
        )
        self.main_window.add_navigation_item(nav_item)

        # 模拟导航选择
        self.main_window._on_navigation_selection("integration_page")

        # 验证页面切换
        current_page = self.main_window.page_manager_ttk.get_current_page()
        self.assertEqual(current_page, "integration_page")

        # 验证状态栏更新
        status_text = self.main_window.status_bar_ttk.get_text("main")
        self.assertIn("integration_page", status_text)

    def test_menu_actions_integration(self):
        """测试菜单操作集成"""
        # 测试新建操作
        self.main_window._on_new_file()
        status_text = self.main_window.status_bar_ttk.get_text("main")
        self.assertIn("新建", status_text)

        # 测试导入操作
        self.main_window._on_import_data()
        status_text = self.main_window.status_bar_ttk.get_text("main")
        self.assertIn("导入", status_text)

        # 测试导出操作
        self.main_window._on_export_data()
        status_text = self.main_window.status_bar_ttk.get_text("main")
        self.assertIn("导出", status_text)

    def test_toolbar_actions_integration(self):
        """测试工具栏操作集成"""
        # 测试刷新操作
        self.main_window._on_refresh()
        status_text = self.main_window.status_bar_ttk.get_text("main")
        self.assertIn("刷新", status_text)

        # 测试设置操作
        self.main_window._on_settings()
        status_text = self.main_window.status_bar_ttk.get_text("main")
        self.assertIn("设置", status_text)

    def test_theme_switching_integration(self):
        """测试主题切换集成"""
        # 测试切换到深色主题
        self.main_window._switch_theme("dark")
        status_text = self.main_window.status_bar_ttk.get_text("main")
        self.assertIn("dark", status_text)

        # 测试切换到浅色主题
        self.main_window._switch_theme("light")
        status_text = self.main_window.status_bar_ttk.get_text("main")
        self.assertIn("light", status_text)

    def test_temporary_message_integration(self):
        """测试临时消息集成"""
        # 显示临时消息
        self.main_window.show_temporary_message("这是一个测试消息", duration=0.1)

        # 验证消息显示
        status_text = self.main_window.status_bar_ttk.get_text("main")
        self.assertEqual(status_text, "这是一个测试消息")

        # 等待消息恢复（在实际测试中可能需要更复杂的异步处理）

    def test_window_info_integration(self):
        """测试窗口信息集成"""
        # 添加一些测试数据
        page_config = PageConfig("info_page", TestPage, "信息页面")
        self.main_window.register_page(page_config)

        nav_item = NavigationItemConfig("info_nav", "信息导航")
        self.main_window.add_navigation_item(nav_item)

        # 获取主窗口信息
        info = self.main_window.get_main_window_info()

        # 验证信息完整性
        self.assertIn("window_info", info)
        self.assertIn("menu_bar", info)
        self.assertIn("toolbar", info)
        self.assertIn("statusbar", info)
        self.assertIn("navigation_panel", info)
        self.assertIn("page_manager", info)
        self.assertIn("page_router", info)

        # 验证具体信息
        self.assertIsNotNone(info["menu_bar"])
        self.assertIsNotNone(info["toolbar"])
        self.assertIsNotNone(info["statusbar"])
        self.assertIsNotNone(info["navigation_panel"])
        self.assertIsNotNone(info["page_manager"])
        self.assertIsNotNone(info["page_router"])

    def test_component_cleanup_integration(self):
        """测试组件清理集成"""
        # 添加一些测试数据
        page_config = PageConfig("cleanup_page", TestPage, "清理页面")
        self.main_window.register_page(page_config)

        nav_item = NavigationItemConfig("cleanup_nav", "清理导航")
        self.main_window.add_navigation_item(nav_item)

        # 显示页面
        self.main_window.page_manager_ttk.show_page("cleanup_page")

        # 执行清理
        self.main_window.cleanup()

        # 验证清理效果（主要验证不抛出异常）
        # 实际的清理验证可能需要更详细的检查

    def test_error_handling_integration(self):
        """测试错误处理集成"""
        # 测试导航到不存在的页面
        self.main_window._on_navigation_selection("nonexistent_page")

        # 验证错误处理（应该不抛出异常）
        status_text = self.main_window.status_bar_ttk.get_text("main")
        self.assertIn("失败", status_text)

        # 测试导航到不存在的路由
        success = self.main_window.navigate_to("/nonexistent")
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()
