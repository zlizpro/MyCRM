"""TTK导航面板系统集成测试

测试NavigationPanelTTK类的各项功能，包括：
- 导航面板的创建和初始化
- 导航项的添加和管理
- 页面切换和选择功能
- 折叠展开功能
- 导航状态保存和恢复
- 层级导航结构

作者: MiniCRM开发团队
"""

import json
import os
import tempfile
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

from src.minicrm.ui.ttk_base.navigation_panel import (
    NavigationItemConfig,
    NavigationPanelTTK,
)


@unittest.skipUnless(TKINTER_AVAILABLE, "tkinter not available in this environment")
class TestNavigationPanelTTK(unittest.TestCase):
    """NavigationPanelTTK类测试"""

    def setUp(self):
        """测试准备"""
        # 创建测试窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        # 创建临时配置文件
        self.temp_config = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        self.temp_config_path = self.temp_config.name
        self.temp_config.close()

        # 创建导航面板实例
        self.navigation_panel = NavigationPanelTTK(
            parent=self.root,
            width=250,
            min_width=50,
            collapsible=True,
            config_file=self.temp_config_path,
            auto_save_config=False,
        )

        # 创建模拟命令函数
        self.mock_command = Mock()
        self.selection_callback = Mock()
        self.collapse_callback = Mock()

    def tearDown(self):
        """测试清理"""
        try:
            # 清理导航面板
            if self.navigation_panel:
                self.navigation_panel.cleanup()

            # 销毁测试窗口
            if self.root:
                self.root.destroy()

            # 删除临时配置文件
            if os.path.exists(self.temp_config_path):
                os.unlink(self.temp_config_path)

        except Exception as e:
            print(f"测试清理失败: {e}")

    def test_navigation_panel_initialization(self):
        """测试导航面板初始化"""
        # 验证导航面板创建成功
        self.assertIsNotNone(self.navigation_panel.navigation_frame)
        self.assertIsNotNone(self.navigation_panel.canvas)
        self.assertIsNotNone(self.navigation_panel.scrollbar)
        self.assertIsNotNone(self.navigation_panel.scroll_frame)

        # 验证初始状态
        self.assertEqual(self.navigation_panel.width, 250)
        self.assertEqual(self.navigation_panel.min_width, 50)
        self.assertTrue(self.navigation_panel.collapsible)
        self.assertFalse(self.navigation_panel.is_collapsed)

        # 验证初始数据
        self.assertEqual(len(self.navigation_panel.navigation_items), 0)
        self.assertEqual(len(self.navigation_panel.item_configs), 0)
        self.assertIsNone(self.navigation_panel.selected_item)

    def test_navigation_item_config_creation(self):
        """测试导航项配置创建"""
        # 创建导航项配置
        item_config = NavigationItemConfig(
            item_id="dashboard",
            text="仪表板",
            command=self.mock_command,
            tooltip="查看系统概览",
            item_type="button",
            state="normal",
        )

        # 验证配置属性
        self.assertEqual(item_config.item_id, "dashboard")
        self.assertEqual(item_config.text, "仪表板")
        self.assertEqual(item_config.command, self.mock_command)
        self.assertEqual(item_config.tooltip, "查看系统概览")
        self.assertEqual(item_config.item_type, "button")
        self.assertEqual(item_config.state, "normal")

    def test_add_navigation_button(self):
        """测试添加导航按钮"""
        # 创建导航按钮配置
        item_config = NavigationItemConfig(
            item_id="customers",
            text="客户管理",
            command=self.mock_command,
            tooltip="管理客户信息",
            item_type="button",
        )

        # 添加导航项
        item = self.navigation_panel.add_navigation_item(item_config)

        # 验证导航项创建
        self.assertIsNotNone(item)

        # 验证导航项保存
        self.assertIn("customers", self.navigation_panel.navigation_items)
        self.assertIn("customers", self.navigation_panel.item_configs)
        self.assertIn("customers", self.navigation_panel.item_states)

        # 验证导航项状态
        self.assertEqual(self.navigation_panel.item_states["customers"], "normal")

    def test_add_navigation_group(self):
        """测试添加导航分组"""
        # 创建导航分组配置
        group_config = NavigationItemConfig(
            item_id="business_group",
            text="业务管理",
            item_type="group",
            collapsible=True,
            expanded=True,
        )

        # 添加导航分组
        group = self.navigation_panel.add_navigation_item(group_config)

        # 验证分组创建
        self.assertIsNotNone(group)
        self.assertIn("business_group", self.navigation_panel.navigation_items)

        # 验证分组属性
        config = self.navigation_panel.item_configs["business_group"]
        self.assertEqual(config.item_type, "group")
        self.assertTrue(config.collapsible)
        self.assertTrue(config.expanded)

    def test_add_hierarchical_items(self):
        """测试添加层级导航项"""
        # 添加父级分组
        parent_config = NavigationItemConfig(
            item_id="management", text="管理模块", item_type="group", collapsible=True
        )
        self.navigation_panel.add_navigation_item(parent_config)

        # 添加子级按钮
        child_config = NavigationItemConfig(
            item_id="user_management",
            text="用户管理",
            parent_id="management",
            command=self.mock_command,
            item_type="button",
        )
        self.navigation_panel.add_navigation_item(child_config)

        # 验证层级关系
        self.assertEqual(self.navigation_panel.item_levels["management"], 0)
        self.assertEqual(self.navigation_panel.item_levels["user_management"], 1)

        # 验证父子关系
        self.assertIn("management", self.navigation_panel.item_hierarchy)
        self.assertIn(
            "user_management", self.navigation_panel.item_hierarchy["management"]
        )

    def test_add_separator(self):
        """测试添加分隔符"""
        # 创建分隔符配置
        separator_config = NavigationItemConfig(
            item_id="separator1", item_type="separator"
        )

        # 添加分隔符
        separator = self.navigation_panel.add_navigation_item(separator_config)

        # 验证分隔符创建
        self.assertIsNotNone(separator)
        self.assertEqual(len(self.navigation_panel.separators), 1)

    def test_item_selection(self):
        """测试导航项选择"""
        # 添加导航项
        item_config = NavigationItemConfig(
            item_id="reports",
            text="报表",
            command=self.mock_command,
            item_type="button",
        )
        self.navigation_panel.add_navigation_item(item_config)

        # 添加选择回调
        self.navigation_panel.add_selection_callback(self.selection_callback)

        # 选择导航项
        self.navigation_panel.select_item("reports")

        # 验证选择状态
        self.assertEqual(self.navigation_panel.get_selected_item(), "reports")
        self.assertEqual(self.navigation_panel.get_item_state("reports"), "selected")

        # 验证回调调用
        self.selection_callback.assert_called_with("reports")

    def test_item_state_management(self):
        """测试导航项状态管理"""
        # 添加导航项
        item_config = NavigationItemConfig(
            item_id="settings",
            text="设置",
            command=self.mock_command,
            item_type="button",
        )
        self.navigation_panel.add_navigation_item(item_config)

        # 测试设置状态
        self.navigation_panel.set_item_state("settings", "disabled")
        self.assertEqual(self.navigation_panel.get_item_state("settings"), "disabled")

        # 测试启用/禁用方法
        self.navigation_panel.disable_item("settings")
        self.assertEqual(self.navigation_panel.get_item_state("settings"), "disabled")

        self.navigation_panel.enable_item("settings")
        self.assertEqual(self.navigation_panel.get_item_state("settings"), "normal")

    def test_update_item_properties(self):
        """测试更新导航项属性"""
        # 添加导航项
        item_config = NavigationItemConfig(
            item_id="profile",
            text="个人资料",
            command=self.mock_command,
            item_type="button",
        )
        self.navigation_panel.add_navigation_item(item_config)

        # 测试更新文本
        self.navigation_panel.update_item_text("profile", "用户资料")
        self.assertEqual(self.navigation_panel.item_configs["profile"].text, "用户资料")

        # 测试更新徽章
        self.navigation_panel.update_item_badge("profile", "5", "blue")
        config = self.navigation_panel.item_configs["profile"]
        self.assertEqual(config.badge_text, "5")
        self.assertEqual(config.badge_color, "blue")

    def test_group_toggle(self):
        """测试分组折叠切换"""
        # 添加可折叠分组
        group_config = NavigationItemConfig(
            item_id="tools_group",
            text="工具",
            item_type="group",
            collapsible=True,
            expanded=True,
        )
        self.navigation_panel.add_navigation_item(group_config)

        # 添加折叠回调
        self.navigation_panel.add_collapse_callback(self.collapse_callback)

        # 切换分组状态
        self.navigation_panel._toggle_group("tools_group")

        # 验证状态变化
        config = self.navigation_panel.item_configs["tools_group"]
        self.assertFalse(config.expanded)
        self.assertIn("tools_group", self.navigation_panel.collapsed_groups)

        # 验证回调调用
        self.collapse_callback.assert_called_with("tools_group", False)

    def test_panel_collapse_expand(self):
        """测试面板折叠展开"""
        # 测试折叠面板
        self.navigation_panel.collapse_panel()
        self.assertTrue(self.navigation_panel.is_collapsed)

        # 测试展开面板
        self.navigation_panel.expand_panel()
        self.assertFalse(self.navigation_panel.is_collapsed)

        # 测试切换面板
        self.navigation_panel.toggle_panel()
        self.assertTrue(self.navigation_panel.is_collapsed)

        self.navigation_panel.toggle_panel()
        self.assertFalse(self.navigation_panel.is_collapsed)

    def test_remove_item(self):
        """测试移除导航项"""
        # 添加导航项
        item_config = NavigationItemConfig(
            item_id="temp_item",
            text="临时项",
            command=self.mock_command,
            item_type="button",
        )
        self.navigation_panel.add_navigation_item(item_config)

        # 验证导航项存在
        self.assertIn("temp_item", self.navigation_panel.navigation_items)

        # 移除导航项
        self.navigation_panel.remove_item("temp_item")

        # 验证导航项移除
        self.assertNotIn("temp_item", self.navigation_panel.navigation_items)
        self.assertNotIn("temp_item", self.navigation_panel.item_configs)
        self.assertNotIn("temp_item", self.navigation_panel.item_states)

    def test_remove_hierarchical_items(self):
        """测试移除层级导航项"""
        # 添加父级分组
        parent_config = NavigationItemConfig(
            item_id="parent_group", text="父级分组", item_type="group"
        )
        self.navigation_panel.add_navigation_item(parent_config)

        # 添加子级项
        child_config = NavigationItemConfig(
            item_id="child_item",
            text="子级项",
            parent_id="parent_group",
            command=self.mock_command,
            item_type="button",
        )
        self.navigation_panel.add_navigation_item(child_config)

        # 验证层级关系
        self.assertIn("parent_group", self.navigation_panel.item_hierarchy)
        self.assertIn(
            "child_item", self.navigation_panel.item_hierarchy["parent_group"]
        )

        # 移除父级项（应该同时移除子级项）
        self.navigation_panel.remove_item("parent_group")

        # 验证父子项都被移除
        self.assertNotIn("parent_group", self.navigation_panel.navigation_items)
        self.assertNotIn("child_item", self.navigation_panel.navigation_items)

    def test_clear_all_items(self):
        """测试清除所有导航项"""
        # 添加多个导航项
        for i in range(3):
            item_config = NavigationItemConfig(
                item_id=f"item_{i}",
                text=f"项目{i}",
                command=self.mock_command,
                item_type="button",
            )
            self.navigation_panel.add_navigation_item(item_config)

        # 验证导航项存在
        self.assertEqual(len(self.navigation_panel.navigation_items), 3)

        # 清除所有导航项
        self.navigation_panel.clear_all_items()

        # 验证导航项清除
        self.assertEqual(len(self.navigation_panel.navigation_items), 0)
        self.assertEqual(len(self.navigation_panel.item_configs), 0)
        self.assertEqual(len(self.navigation_panel.item_states), 0)
        self.assertIsNone(self.navigation_panel.selected_item)

    def test_callback_management(self):
        """测试回调管理"""
        # 添加回调
        self.navigation_panel.add_selection_callback(self.selection_callback)
        self.navigation_panel.add_collapse_callback(self.collapse_callback)

        # 验证回调添加
        self.assertIn(
            self.selection_callback, self.navigation_panel.selection_callbacks
        )
        self.assertIn(self.collapse_callback, self.navigation_panel.collapse_callbacks)

        # 移除回调
        self.navigation_panel.remove_selection_callback(self.selection_callback)
        self.navigation_panel.remove_collapse_callback(self.collapse_callback)

        # 验证回调移除
        self.assertNotIn(
            self.selection_callback, self.navigation_panel.selection_callbacks
        )
        self.assertNotIn(
            self.collapse_callback, self.navigation_panel.collapse_callbacks
        )

    def test_config_save_and_load(self):
        """测试配置保存和加载"""
        # 添加导航项
        item_config = NavigationItemConfig(
            item_id="test_item",
            text="测试项",
            command=self.mock_command,
            tooltip="测试工具提示",
            item_type="button",
            badge_text="NEW",
            badge_color="green",
        )
        self.navigation_panel.add_navigation_item(item_config)

        # 选择导航项
        self.navigation_panel.select_item("test_item")

        # 保存配置
        self.navigation_panel.save_config()

        # 验证配置文件存在
        self.assertTrue(os.path.exists(self.temp_config_path))

        # 读取配置文件内容
        with open(self.temp_config_path, encoding="utf-8") as f:
            config_data = json.load(f)

        # 验证配置内容
        self.assertIn("panel", config_data)
        self.assertIn("selected_item", config_data)
        self.assertIn("items", config_data)

        self.assertEqual(config_data["selected_item"], "test_item")
        self.assertEqual(len(config_data["items"]), 1)

        item_data = config_data["items"][0]
        self.assertEqual(item_data["id"], "test_item")
        self.assertEqual(item_data["text"], "测试项")
        self.assertEqual(item_data["tooltip"], "测试工具提示")
        self.assertEqual(item_data["badge_text"], "NEW")
        self.assertEqual(item_data["badge_color"], "green")

    def test_get_navigation_info(self):
        """测试获取导航面板信息"""
        # 添加导航项
        item_config = NavigationItemConfig(
            item_id="info_item",
            text="信息项",
            command=self.mock_command,
            item_type="button",
            badge_text="1",
        )
        self.navigation_panel.add_navigation_item(item_config)

        # 选择导航项
        self.navigation_panel.select_item("info_item")

        # 获取导航面板信息
        info = self.navigation_panel.get_navigation_info()

        # 验证信息
        self.assertEqual(info["width"], 250)
        self.assertEqual(info["min_width"], 50)
        self.assertFalse(info["is_collapsed"])
        self.assertTrue(info["collapsible"])
        self.assertEqual(info["item_count"], 1)
        self.assertEqual(info["selected_item"], "info_item")
        self.assertIn("info_item", info["items"])

        item_info = info["items"]["info_item"]
        self.assertEqual(item_info["text"], "信息项")
        self.assertEqual(item_info["type"], "button")
        self.assertEqual(item_info["state"], "selected")
        self.assertEqual(item_info["level"], 0)
        self.assertEqual(item_info["badge_text"], "1")

    def test_navigation_click_simulation(self):
        """测试导航点击模拟"""
        # 添加导航项
        item_config = NavigationItemConfig(
            item_id="click_item",
            text="点击项",
            command=self.mock_command,
            item_type="button",
        )
        self.navigation_panel.add_navigation_item(item_config)

        # 添加选择回调
        self.navigation_panel.add_selection_callback(self.selection_callback)

        # 模拟点击事件
        self.navigation_panel._on_navigation_click("click_item")

        # 验证选择状态
        self.assertEqual(self.navigation_panel.get_selected_item(), "click_item")

        # 验证回调调用
        self.selection_callback.assert_called_with("click_item")


if __name__ == "__main__":
    unittest.main()
