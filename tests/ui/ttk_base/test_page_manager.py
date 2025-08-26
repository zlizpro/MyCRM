"""TTK页面管理系统单元测试

测试PageManagerTTK和PageRouterTTK类的各项功能，包括：
- 页面生命周期管理
- 页面路由和切换
- 页面缓存和预加载
- 懒加载和内存管理
- 页面状态保存和恢复

作者: MiniCRM开发团队
"""

import time
import tkinter as tk
import unittest
from unittest.mock import Mock


# 处理无头环境中的tkinter问题
try:
    # 尝试创建一个测试窗口来检查tkinter是否可用
    test_root = tk.Tk()
    test_root.withdraw()
    test_root.destroy()
    TKINTER_AVAILABLE = True
except Exception:
    TKINTER_AVAILABLE = False

from src.minicrm.ui.ttk_base.page_manager import (
    BasePage,
    PageConfig,
    PageLifecycleEvent,
    PageManagerTTK,
    PageRouterTTK,
    PageState,
)


# 测试页面类
class TestPage(BasePage):
    """测试页面类"""

    def __init__(self, page_id: str, parent: tk.Widget):
        super().__init__(page_id, parent)
        self.create_ui_called = False
        self.on_show_called = False
        self.on_hide_called = False
        self.on_destroy_called = False
        self.on_cache_called = False
        self.on_restore_called = False

    def create_ui(self):
        """创建UI"""
        from tkinter import ttk

        self.create_ui_called = True
        frame = ttk.Frame(self.parent)
        label = ttk.Label(frame, text=f"页面: {self.page_id}")
        label.pack()
        return frame

    def on_show(self):
        self.on_show_called = True

    def on_hide(self):
        self.on_hide_called = True

    def on_destroy(self):
        self.on_destroy_called = True

    def on_cache(self):
        self.on_cache_called = True

    def on_restore_from_cache(self):
        self.on_restore_called = True


@unittest.skipUnless(TKINTER_AVAILABLE, "tkinter not available in this environment")
class TestBasePage(unittest.TestCase):
    """BasePage类测试"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.page = TestPage("test_page", self.root)

    def tearDown(self):
        """测试清理"""
        try:
            if self.page:
                self.page.destroy()
            if self.root:
                self.root.destroy()
        except Exception as e:
            print(f"测试清理失败: {e}")

    def test_page_initialization(self):
        """测试页面初始化"""
        self.assertEqual(self.page.page_id, "test_page")
        self.assertEqual(self.page.parent, self.root)
        self.assertEqual(self.page.state, PageState.UNLOADED)
        self.assertIsNone(self.page.frame)
        self.assertEqual(len(self.page.data), 0)

    def test_page_load(self):
        """测试页面加载"""
        # 加载页面
        self.page.load()

        # 验证加载状态
        self.assertEqual(self.page.state, PageState.LOADED)
        self.assertIsNotNone(self.page.frame)
        self.assertTrue(self.page.create_ui_called)

        # 重复加载应该不执行
        self.page.create_ui_called = False
        self.page.load()
        self.assertFalse(self.page.create_ui_called)

    def test_page_show_hide(self):
        """测试页面显示隐藏"""
        # 加载页面
        self.page.load()

        # 显示页面
        self.page.show()
        self.assertEqual(self.page.state, PageState.ACTIVE)
        self.assertTrue(self.page.on_show_called)

        # 隐藏页面
        self.page.hide()
        self.assertEqual(self.page.state, PageState.INACTIVE)
        self.assertTrue(self.page.on_hide_called)

    def test_page_cache_restore(self):
        """测试页面缓存恢复"""
        # 加载并隐藏页面
        self.page.load()
        self.page.show()
        self.page.hide()

        # 缓存页面
        self.page.cache()
        self.assertEqual(self.page.state, PageState.CACHED)
        self.assertTrue(self.page.on_cache_called)

        # 从缓存恢复
        self.page.restore_from_cache()
        self.assertEqual(self.page.state, PageState.INACTIVE)
        self.assertTrue(self.page.on_restore_called)

    def test_page_destroy(self):
        """测试页面销毁"""
        # 加载页面
        self.page.load()

        # 销毁页面
        self.page.destroy()
        self.assertEqual(self.page.state, PageState.DESTROYED)
        self.assertTrue(self.page.on_destroy_called)
        self.assertIsNone(self.page.frame)

    def test_page_data_management(self):
        """测试页面数据管理"""
        # 设置数据
        self.page.set_data("key1", "value1")
        self.page.set_data("key2", 123)

        # 获取数据
        self.assertEqual(self.page.get_data("key1"), "value1")
        self.assertEqual(self.page.get_data("key2"), 123)
        self.assertIsNone(self.page.get_data("key3"))
        self.assertEqual(self.page.get_data("key3", "default"), "default")


@unittest.skipUnless(TKINTER_AVAILABLE, "tkinter not available in this environment")
class TestPageManagerTTK(unittest.TestCase):
    """PageManagerTTK类测试"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()

        # 创建页面管理器
        self.page_manager = PageManagerTTK(
            container=self.root,
            max_cache_size=3,
            default_cache_timeout=1.0,  # 1秒用于测试
            preload_enabled=False,  # 禁用预加载以简化测试
            lazy_load_enabled=True,
        )

        # 创建测试页面配置
        self.page_config1 = PageConfig(
            page_id="page1",
            page_class=TestPage,
            title="页面1",
            cache=True,
            preload=False,
        )

        self.page_config2 = PageConfig(
            page_id="page2",
            page_class=TestPage,
            title="页面2",
            cache=True,
            preload=False,
        )

        # 创建生命周期回调
        self.lifecycle_callback = Mock()

    def tearDown(self):
        """测试清理"""
        try:
            if self.page_manager:
                self.page_manager.cleanup()
            if self.root:
                self.root.destroy()
        except Exception as e:
            print(f"测试清理失败: {e}")

    def test_page_manager_initialization(self):
        """测试页面管理器初始化"""
        self.assertEqual(self.page_manager.container, self.root)
        self.assertEqual(self.page_manager.max_cache_size, 3)
        self.assertEqual(self.page_manager.default_cache_timeout, 1.0)
        self.assertFalse(self.page_manager.preload_enabled)
        self.assertTrue(self.page_manager.lazy_load_enabled)

        # 验证初始状态
        self.assertEqual(len(self.page_manager.page_configs), 0)
        self.assertEqual(len(self.page_manager.pages), 0)
        self.assertIsNone(self.page_manager.current_page)
        self.assertEqual(len(self.page_manager.page_history), 0)

    def test_register_unregister_page(self):
        """测试页面注册注销"""
        # 注册页面
        self.page_manager.register_page(self.page_config1)

        # 验证注册
        self.assertIn("page1", self.page_manager.page_configs)
        self.assertEqual(self.page_manager.page_configs["page1"], self.page_config1)

        # 注销页面
        self.page_manager.unregister_page("page1")

        # 验证注销
        self.assertNotIn("page1", self.page_manager.page_configs)

    def test_get_page(self):
        """测试获取页面实例"""
        # 注册页面
        self.page_manager.register_page(self.page_config1)

        # 获取页面实例
        page = self.page_manager.get_page("page1")

        # 验证页面实例
        self.assertIsNotNone(page)
        self.assertIsInstance(page, TestPage)
        self.assertEqual(page.page_id, "page1")
        self.assertIn("page1", self.page_manager.pages)

        # 再次获取应该返回同一实例
        page2 = self.page_manager.get_page("page1")
        self.assertEqual(page, page2)

        # 获取不存在的页面
        page3 = self.page_manager.get_page("nonexistent")
        self.assertIsNone(page3)

    def test_load_page(self):
        """测试页面加载"""
        # 注册页面
        self.page_manager.register_page(self.page_config1)

        # 加载页面
        success = self.page_manager.load_page("page1")

        # 验证加载成功
        self.assertTrue(success)
        page = self.page_manager.pages["page1"]
        self.assertEqual(page.state, PageState.LOADED)
        self.assertTrue(page.create_ui_called)

        # 加载不存在的页面
        success = self.page_manager.load_page("nonexistent")
        self.assertFalse(success)

    def test_show_hide_page(self):
        """测试页面显示隐藏"""
        # 注册页面
        self.page_manager.register_page(self.page_config1)
        self.page_manager.register_page(self.page_config2)

        # 显示页面1
        success = self.page_manager.show_page("page1")
        self.assertTrue(success)
        self.assertEqual(self.page_manager.current_page, "page1")

        page1 = self.page_manager.pages["page1"]
        self.assertEqual(page1.state, PageState.ACTIVE)
        self.assertTrue(page1.on_show_called)

        # 显示页面2（应该隐藏页面1）
        success = self.page_manager.show_page("page2")
        self.assertTrue(success)
        self.assertEqual(self.page_manager.current_page, "page2")

        # 验证页面1被隐藏
        self.assertTrue(page1.on_hide_called)
        self.assertIn(page1.state, [PageState.INACTIVE, PageState.CACHED])

        # 验证页面2显示
        page2 = self.page_manager.pages["page2"]
        self.assertEqual(page2.state, PageState.ACTIVE)
        self.assertTrue(page2.on_show_called)

    def test_destroy_page(self):
        """测试页面销毁"""
        # 注册并显示页面
        self.page_manager.register_page(self.page_config1)
        self.page_manager.show_page("page1")

        # 获取页面引用
        page = self.page_manager.pages["page1"]

        # 销毁页面
        success = self.page_manager.destroy_page("page1")
        self.assertTrue(success)

        # 验证页面销毁
        self.assertEqual(page.state, PageState.DESTROYED)
        self.assertTrue(page.on_destroy_called)
        self.assertNotIn("page1", self.page_manager.pages)
        self.assertIsNone(self.page_manager.current_page)

    def test_page_history(self):
        """测试页面历史记录"""
        # 注册页面
        self.page_manager.register_page(self.page_config1)
        self.page_manager.register_page(self.page_config2)

        # 显示页面1
        self.page_manager.show_page("page1")
        self.assertEqual(self.page_manager.page_history, ["page1"])

        # 显示页面2
        self.page_manager.show_page("page2")
        self.assertEqual(self.page_manager.page_history, ["page1", "page2"])

        # 返回上一页
        success = self.page_manager.go_back()
        self.assertTrue(success)
        self.assertEqual(self.page_manager.current_page, "page1")

        # 清空历史记录
        self.page_manager.clear_history()
        self.assertEqual(len(self.page_manager.page_history), 0)

    def test_page_caching(self):
        """测试页面缓存"""
        # 注册页面
        config = PageConfig(
            page_id="cache_page",
            page_class=TestPage,
            title="缓存页面",
            cache=True,
            cache_timeout=0.5,  # 0.5秒超时
        )
        self.page_manager.register_page(config)

        # 显示页面
        self.page_manager.show_page("cache_page")
        page = self.page_manager.pages["cache_page"]

        # 隐藏页面（应该被缓存）
        self.page_manager.hide_page("cache_page")
        self.assertEqual(page.state, PageState.CACHED)
        self.assertTrue(page.on_cache_called)
        self.assertIn("cache_page", self.page_manager.cached_pages)

        # 再次显示页面（应该从缓存恢复）
        self.page_manager.show_page("cache_page")
        self.assertTrue(page.on_restore_called)

    def test_cache_cleanup(self):
        """测试缓存清理"""
        # 创建多个页面配置
        configs = []
        for i in range(5):
            config = PageConfig(
                page_id=f"cache_page_{i}",
                page_class=TestPage,
                title=f"缓存页面{i}",
                cache=True,
                cache_timeout=0.1,  # 0.1秒超时
            )
            configs.append(config)
            self.page_manager.register_page(config)

        # 显示并隐藏所有页面
        for i in range(5):
            self.page_manager.show_page(f"cache_page_{i}")
            self.page_manager.hide_page(f"cache_page_{i}")

        # 验证缓存数量限制
        self.assertLessEqual(
            len(self.page_manager.cached_pages), self.page_manager.max_cache_size
        )

        # 等待缓存超时
        time.sleep(0.2)

        # 触发缓存清理
        self.page_manager._cleanup_cache()

        # 验证过期页面被清理
        self.assertEqual(len(self.page_manager.cached_pages), 0)

    def test_lifecycle_callbacks(self):
        """测试生命周期回调"""
        # 添加生命周期回调
        self.page_manager.add_lifecycle_callback(
            PageLifecycleEvent.AFTER_SHOW, self.lifecycle_callback
        )

        # 注册并显示页面
        self.page_manager.register_page(self.page_config1)
        self.page_manager.show_page("page1")

        # 验证回调被调用
        self.lifecycle_callback.assert_called_once()
        args = self.lifecycle_callback.call_args[0]
        self.assertEqual(args[0], "page1")  # page_id
        self.assertIsInstance(args[1], TestPage)  # page instance

        # 移除回调
        self.page_manager.remove_lifecycle_callback(
            PageLifecycleEvent.AFTER_SHOW, self.lifecycle_callback
        )

    def test_get_page_info(self):
        """测试获取页面管理器信息"""
        # 注册页面
        self.page_manager.register_page(self.page_config1)
        self.page_manager.show_page("page1")

        # 获取信息
        info = self.page_manager.get_page_info()

        # 验证信息
        self.assertEqual(info["current_page"], "page1")
        self.assertEqual(info["total_pages"], 1)
        self.assertEqual(info["loaded_pages"], 1)
        self.assertEqual(info["max_cache_size"], 3)
        self.assertFalse(info["preload_enabled"])
        self.assertTrue(info["lazy_load_enabled"])
        self.assertIn("page1", info["pages"])


@unittest.skipUnless(TKINTER_AVAILABLE, "tkinter not available in this environment")
class TestPageRouterTTK(unittest.TestCase):
    """PageRouterTTK类测试"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()

        # 创建页面管理器和路由器
        self.page_manager = PageManagerTTK(container=self.root, preload_enabled=False)
        self.router = PageRouterTTK(self.page_manager)

        # 注册页面
        self.page_config1 = PageConfig("page1", TestPage, "页面1")
        self.page_config2 = PageConfig("page2", TestPage, "页面2")

        self.page_manager.register_page(self.page_config1)
        self.page_manager.register_page(self.page_config2)

        # 创建守卫函数
        self.before_guard = Mock(return_value=True)
        self.after_guard = Mock()

    def tearDown(self):
        """测试清理"""
        try:
            if self.page_manager:
                self.page_manager.cleanup()
            if self.root:
                self.root.destroy()
        except Exception as e:
            print(f"测试清理失败: {e}")

    def test_router_initialization(self):
        """测试路由器初始化"""
        self.assertEqual(self.router.page_manager, self.page_manager)
        self.assertEqual(len(self.router.routes), 0)
        self.assertIsNone(self.router.current_route)

    def test_register_unregister_route(self):
        """测试路由注册注销"""
        # 注册路由
        self.router.register_route("/home", "page1")
        self.router.register_route("/about", "page2", {"param1": "value1"})

        # 验证注册
        self.assertEqual(self.router.routes["/home"], "page1")
        self.assertEqual(self.router.routes["/about"], "page2")
        self.assertEqual(self.router.route_params["/about"]["param1"], "value1")

        # 注销路由
        self.router.unregister_route("/home")

        # 验证注销
        self.assertNotIn("/home", self.router.routes)

    def test_navigate_to_route(self):
        """测试路由导航"""
        # 注册路由
        self.router.register_route("/page1", "page1")
        self.router.register_route("/page2", "page2")

        # 导航到页面1
        success = self.router.navigate_to("/page1")
        self.assertTrue(success)
        self.assertEqual(self.router.current_route, "/page1")
        self.assertEqual(self.page_manager.current_page, "page1")

        # 导航到页面2
        success = self.router.navigate_to("/page2")
        self.assertTrue(success)
        self.assertEqual(self.router.current_route, "/page2")
        self.assertEqual(self.page_manager.current_page, "page2")

        # 导航到不存在的路由
        success = self.router.navigate_to("/nonexistent")
        self.assertFalse(success)

    def test_navigate_to_page_directly(self):
        """测试直接页面导航"""
        # 直接导航到页面
        success = self.router.navigate_to_page("page1")
        self.assertTrue(success)
        self.assertEqual(self.page_manager.current_page, "page1")

        # 带参数导航
        params = {"key1": "value1", "key2": 123}
        success = self.router.navigate_to_page("page2", params)
        self.assertTrue(success)

        # 验证参数设置
        page = self.page_manager.get_page("page2")
        self.assertEqual(page.get_data("key1"), "value1")
        self.assertEqual(page.get_data("key2"), 123)

    def test_navigation_guards(self):
        """测试导航守卫"""
        # 注册路由
        self.router.register_route("/guarded", "page1")

        # 添加守卫
        self.router.add_before_navigate_guard(self.before_guard)
        self.router.add_after_navigate_guard(self.after_guard)

        # 导航（守卫允许）
        success = self.router.navigate_to("/guarded")
        self.assertTrue(success)

        # 验证守卫被调用
        self.before_guard.assert_called_once_with("/guarded", "page1", None)
        self.after_guard.assert_called_once_with("/guarded", "page1", None)

        # 设置守卫阻止导航
        self.before_guard.return_value = False
        self.before_guard.reset_mock()

        # 导航（守卫阻止）
        success = self.router.navigate_to("/guarded")
        self.assertFalse(success)
        self.before_guard.assert_called_once()

        # 移除守卫
        self.router.remove_before_navigate_guard(self.before_guard)
        self.router.remove_after_navigate_guard(self.after_guard)

    def test_go_back(self):
        """测试返回上一页"""
        # 注册路由
        self.router.register_route("/page1", "page1")
        self.router.register_route("/page2", "page2")

        # 导航到页面1，然后页面2
        self.router.navigate_to("/page1")
        self.router.navigate_to("/page2")

        # 返回上一页
        success = self.router.go_back()
        self.assertTrue(success)
        self.assertEqual(self.page_manager.current_page, "page1")

    def test_get_router_info(self):
        """测试获取路由器信息"""
        # 注册路由和守卫
        self.router.register_route("/home", "page1")
        self.router.register_route("/about", "page2")
        self.router.add_before_navigate_guard(self.before_guard)
        self.router.add_after_navigate_guard(self.after_guard)

        # 导航到页面
        self.router.navigate_to("/home")

        # 获取信息
        info = self.router.get_router_info()

        # 验证信息
        self.assertEqual(info["current_route"], "/home")
        self.assertEqual(info["total_routes"], 2)
        self.assertEqual(info["before_guards"], 1)
        self.assertEqual(info["after_guards"], 1)
        self.assertIn("/home", info["routes"])
        self.assertIn("/about", info["routes"])


if __name__ == "__main__":
    unittest.main()
