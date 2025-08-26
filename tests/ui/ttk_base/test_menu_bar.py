"""TTK菜单栏系统单元测试

测试MenuBarTTK类的各项功能，包括：
- 菜单栏的创建和初始化
- 菜单和菜单项的添加和管理
- 快捷键绑定功能
- 菜单项状态管理
- 配置的保存和加载
- 各种类型菜单项的支持

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

from src.minicrm.ui.ttk_base.menu_bar import MenuBarTTK, MenuConfig, MenuItemConfig


@unittest.skipUnless(TKINTER_AVAILABLE, "tkinter not available in this environment")
class TestMenuBarTTK(unittest.TestCase):
    """MenuBarTTK类测试"""

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

        # 创建菜单栏实例
        self.menu_bar = MenuBarTTK(
            parent=self.root, config_file=self.temp_config_path, auto_save_config=False
        )

        # 创建测试变量
        self.test_bool_var = tk.BooleanVar()
        self.test_string_var = tk.StringVar()

        # 创建模拟命令函数
        self.mock_command = Mock()

    def tearDown(self):
        """测试清理"""
        try:
            # 清理菜单栏
            if self.menu_bar:
                self.menu_bar.cleanup()

            # 销毁测试窗口
            if self.root:
                self.root.destroy()

            # 删除临时配置文件
            if os.path.exists(self.temp_config_path):
                os.unlink(self.temp_config_path)

        except Exception as e:
            print(f"测试清理失败: {e}")

    def test_menu_bar_initialization(self):
        """测试菜单栏初始化"""
        # 验证菜单栏创建成功
        self.assertIsNotNone(self.menu_bar.menu_bar)
        self.assertIsInstance(self.menu_bar.menu_bar, tk.Menu)

        # 验证父窗口菜单设置
        self.assertEqual(self.root.cget("menu"), str(self.menu_bar.menu_bar))

        # 验证初始状态
        self.assertEqual(len(self.menu_bar.menus), 0)
        self.assertEqual(len(self.menu_bar.menu_configs), 0)
        self.assertEqual(len(self.menu_bar.menu_items), 0)

    def test_menu_config_creation(self):
        """测试菜单配置创建"""
        # 创建菜单配置
        menu_config = MenuConfig("文件", underline=0)

        # 验证基本属性
        self.assertEqual(menu_config.label, "文件")
        self.assertEqual(menu_config.underline, 0)
        self.assertEqual(len(menu_config.items), 0)

        # 添加命令菜单项
        menu_config.add_command(
            label="新建", command=self.mock_command, accelerator="Ctrl+N", underline=0
        )

        # 验证菜单项添加
        self.assertEqual(len(menu_config.items), 1)
        item = menu_config.items[0]
        self.assertEqual(item.label, "新建")
        self.assertEqual(item.command, self.mock_command)
        self.assertEqual(item.accelerator, "Ctrl+N")
        self.assertEqual(item.item_type, "command")

    def test_menu_item_config_creation(self):
        """测试菜单项配置创建"""
        # 测试命令菜单项
        command_item = MenuItemConfig(
            label="保存",
            command=self.mock_command,
            accelerator="Ctrl+S",
            underline=0,
            state="normal",
            item_type="command",
        )

        self.assertEqual(command_item.label, "保存")
        self.assertEqual(command_item.command, self.mock_command)
        self.assertEqual(command_item.accelerator, "Ctrl+S")
        self.assertEqual(command_item.item_type, "command")

        # 测试复选框菜单项
        check_item = MenuItemConfig(
            label="显示工具栏", item_type="checkbutton", variable=self.test_bool_var
        )

        self.assertEqual(check_item.label, "显示工具栏")
        self.assertEqual(check_item.item_type, "checkbutton")
        self.assertEqual(check_item.variable, self.test_bool_var)

        # 测试单选按钮菜单项
        radio_item = MenuItemConfig(
            label="浅色主题",
            item_type="radiobutton",
            variable=self.test_string_var,
            value="light",
        )

        self.assertEqual(radio_item.label, "浅色主题")
        self.assertEqual(radio_item.item_type, "radiobutton")
        self.assertEqual(radio_item.variable, self.test_string_var)
        self.assertEqual(radio_item.value, "light")

    def test_add_menu(self):
        """测试添加菜单"""
        # 创建菜单配置
        menu_config = MenuConfig("文件", underline=0)
        menu_config.add_command("新建", self.mock_command, "Ctrl+N")
        menu_config.add_separator()
        menu_config.add_command("退出", self.mock_command, "Ctrl+Q")

        # 添加菜单
        menu = self.menu_bar.add_menu(menu_config)

        # 验证菜单创建
        self.assertIsNotNone(menu)
        self.assertIsInstance(menu, tk.Menu)

        # 验证菜单保存
        self.assertIn("文件", self.menu_bar.menus)
        self.assertIn("文件", self.menu_bar.menu_configs)
        self.assertIn("文件", self.menu_bar.menu_items)
        self.assertIn("文件", self.menu_bar.menu_states)

        # 验证菜单项索引
        self.assertIn("新建", self.menu_bar.menu_items["文件"])
        self.assertIn("退出", self.menu_bar.menu_items["文件"])

        # 验证菜单项状态
        self.assertEqual(self.menu_bar.menu_states["文件"]["新建"], "normal")
        self.assertEqual(self.menu_bar.menu_states["文件"]["退出"], "normal")

    def test_menu_item_state_management(self):
        """测试菜单项状态管理"""
        # 创建并添加菜单
        menu_config = MenuConfig("编辑")
        menu_config.add_command("复制", self.mock_command)
        menu_config.add_command("粘贴", self.mock_command)
        self.menu_bar.add_menu(menu_config)

        # 测试设置菜单项状态
        self.menu_bar.set_menu_item_state("编辑", "复制", "disabled")
        self.assertEqual(self.menu_bar.get_menu_item_state("编辑", "复制"), "disabled")

        # 测试启用/禁用方法
        self.menu_bar.disable_menu_item("编辑", "粘贴")
        self.assertEqual(self.menu_bar.get_menu_item_state("编辑", "粘贴"), "disabled")

        self.menu_bar.enable_menu_item("编辑", "粘贴")
        self.assertEqual(self.menu_bar.get_menu_item_state("编辑", "粘贴"), "normal")

        # 测试不存在的菜单项
        self.assertIsNone(self.menu_bar.get_menu_item_state("编辑", "不存在"))

    def test_accelerator_conversion(self):
        """测试快捷键转换"""
        # 测试常见快捷键转换
        test_cases = [
            ("Ctrl+N", "<Control-n>"),
            ("Ctrl+Shift+S", "<Control-Shift-s>"),
            ("Alt+F4", "<Alt-F4>"),
            ("F1", "<F1>"),
            ("", None),
            ("InvalidKey", None),
        ]

        for accelerator, expected in test_cases:
            result = self.menu_bar._convert_accelerator_to_binding(accelerator)
            self.assertEqual(result, expected, f"转换失败: {accelerator}")

    def test_accelerator_binding(self):
        """测试快捷键绑定"""
        # 创建菜单配置
        menu_config = MenuConfig("文件")
        menu_config.add_command("新建", self.mock_command, "Ctrl+N")
        self.menu_bar.add_menu(menu_config)

        # 验证快捷键绑定
        self.assertIn("<Control-n>", self.menu_bar.accelerator_bindings)
        self.assertEqual(
            self.menu_bar.accelerator_bindings["<Control-n>"], self.mock_command
        )

    def test_checkbutton_menu_item(self):
        """测试复选框菜单项"""
        # 创建菜单配置
        menu_config = MenuConfig("视图")
        menu_config.add_checkbutton(
            "显示状态栏", self.test_bool_var, command=self.mock_command
        )
        self.menu_bar.add_menu(menu_config)

        # 验证菜单项创建
        self.assertIn("显示状态栏", self.menu_bar.menu_items["视图"])

        # 设置变量并验证
        self.test_bool_var.set(True)
        self.assertTrue(self.test_bool_var.get())

    def test_radiobutton_menu_item(self):
        """测试单选按钮菜单项"""
        # 创建菜单配置
        menu_config = MenuConfig("主题")
        menu_config.add_radiobutton(
            "浅色主题", self.test_string_var, "light", command=self.mock_command
        )
        menu_config.add_radiobutton(
            "深色主题", self.test_string_var, "dark", command=self.mock_command
        )
        self.menu_bar.add_menu(menu_config)

        # 验证菜单项创建
        self.assertIn("浅色主题", self.menu_bar.menu_items["主题"])
        self.assertIn("深色主题", self.menu_bar.menu_items["主题"])

        # 设置变量并验证
        self.test_string_var.set("dark")
        self.assertEqual(self.test_string_var.get(), "dark")

    def test_menu_variable_management(self):
        """测试菜单变量管理"""
        # 设置变量
        self.menu_bar.set_menu_item_variable("theme", self.test_string_var)

        # 验证变量获取
        retrieved_var = self.menu_bar.get_menu_item_variable("theme")
        self.assertEqual(retrieved_var, self.test_string_var)

        # 测试不存在的变量
        self.assertIsNone(self.menu_bar.get_menu_item_variable("不存在"))

    def test_update_menu_item_command(self):
        """测试更新菜单项命令"""
        # 创建菜单
        menu_config = MenuConfig("工具")
        menu_config.add_command("选项", self.mock_command)
        self.menu_bar.add_menu(menu_config)

        # 创建新命令
        new_command = Mock()

        # 更新命令
        self.menu_bar.update_menu_item_command("工具", "选项", new_command)

        # 验证命令更新（这里主要验证方法调用不出错）
        # 实际的命令验证需要通过菜单点击来测试，这在单元测试中比较困难

    def test_remove_menu(self):
        """测试移除菜单"""
        # 创建并添加菜单
        menu_config = MenuConfig("测试菜单")
        menu_config.add_command("测试项", self.mock_command)
        self.menu_bar.add_menu(menu_config)

        # 验证菜单存在
        self.assertIn("测试菜单", self.menu_bar.menus)

        # 移除菜单
        self.menu_bar.remove_menu("测试菜单")

        # 验证菜单移除
        self.assertNotIn("测试菜单", self.menu_bar.menus)
        self.assertNotIn("测试菜单", self.menu_bar.menu_configs)
        self.assertNotIn("测试菜单", self.menu_bar.menu_items)
        self.assertNotIn("测试菜单", self.menu_bar.menu_states)

    def test_clear_all_menus(self):
        """测试清除所有菜单"""
        # 添加多个菜单
        for menu_name in ["文件", "编辑", "视图"]:
            menu_config = MenuConfig(menu_name)
            menu_config.add_command("测试", self.mock_command)
            self.menu_bar.add_menu(menu_config)

        # 验证菜单存在
        self.assertEqual(len(self.menu_bar.menus), 3)

        # 清除所有菜单
        self.menu_bar.clear_all_menus()

        # 验证菜单清除
        self.assertEqual(len(self.menu_bar.menus), 0)
        self.assertEqual(len(self.menu_bar.menu_configs), 0)
        self.assertEqual(len(self.menu_bar.menu_items), 0)
        self.assertEqual(len(self.menu_bar.menu_states), 0)
        self.assertEqual(len(self.menu_bar.accelerator_bindings), 0)

    def test_config_save_and_load(self):
        """测试配置保存和加载"""
        # 创建菜单配置
        menu_config = MenuConfig("文件", underline=0)
        menu_config.add_command(
            "新建", self.mock_command, accelerator="Ctrl+N", underline=0
        )
        menu_config.add_separator()
        menu_config.add_command("退出", self.mock_command, accelerator="Ctrl+Q")

        # 添加菜单
        self.menu_bar.add_menu(menu_config)

        # 保存配置
        self.menu_bar.save_config()

        # 验证配置文件存在
        self.assertTrue(os.path.exists(self.temp_config_path))

        # 读取配置文件内容
        with open(self.temp_config_path, encoding="utf-8") as f:
            config_data = json.load(f)

        # 验证配置内容
        self.assertIn("menus", config_data)
        self.assertEqual(len(config_data["menus"]), 1)

        menu_data = config_data["menus"][0]
        self.assertEqual(menu_data["label"], "文件")
        self.assertEqual(menu_data["underline"], 0)
        self.assertEqual(len(menu_data["items"]), 3)  # 2个命令 + 1个分隔符

        # 验证菜单项数据
        new_item = menu_data["items"][0]
        self.assertEqual(new_item["label"], "新建")
        self.assertEqual(new_item["accelerator"], "Ctrl+N")
        self.assertEqual(new_item["type"], "command")

    def test_get_menu_structure(self):
        """测试获取菜单结构"""
        # 创建菜单
        menu_config = MenuConfig("文件")
        menu_config.add_command("新建", self.mock_command, "Ctrl+N")
        menu_config.add_command("保存", self.mock_command, "Ctrl+S")
        self.menu_bar.add_menu(menu_config)

        # 获取菜单结构
        structure = self.menu_bar.get_menu_structure()

        # 验证结构
        self.assertIn("文件", structure)
        file_menu = structure["文件"]
        self.assertEqual(file_menu["label"], "文件")
        self.assertEqual(len(file_menu["items"]), 2)

        # 验证菜单项信息
        new_item = file_menu["items"][0]
        self.assertEqual(new_item["label"], "新建")
        self.assertEqual(new_item["type"], "command")
        self.assertEqual(new_item["accelerator"], "Ctrl+N")
        self.assertEqual(new_item["state"], "normal")

    def test_get_menu(self):
        """测试获取菜单对象"""
        # 创建菜单
        menu_config = MenuConfig("测试")
        menu_config.add_command("项目", self.mock_command)
        menu = self.menu_bar.add_menu(menu_config)

        # 测试获取菜单
        retrieved_menu = self.menu_bar.get_menu("测试")
        self.assertEqual(retrieved_menu, menu)

        # 测试获取不存在的菜单
        self.assertIsNone(self.menu_bar.get_menu("不存在"))

    def test_cleanup(self):
        """测试资源清理"""
        # 创建菜单和快捷键绑定
        menu_config = MenuConfig("文件")
        menu_config.add_command("新建", self.mock_command, "Ctrl+N")
        self.menu_bar.add_menu(menu_config)

        # 设置变量
        self.menu_bar.set_menu_item_variable("test", self.test_bool_var)

        # 验证资源存在
        self.assertTrue(len(self.menu_bar.menus) > 0)
        self.assertTrue(len(self.menu_bar.accelerator_bindings) > 0)
        self.assertTrue(len(self.menu_bar.menu_variables) > 0)

        # 执行清理
        self.menu_bar.cleanup()

        # 验证资源清理
        self.assertEqual(len(self.menu_bar.menus), 0)
        self.assertEqual(len(self.menu_bar.menu_configs), 0)
        self.assertEqual(len(self.menu_bar.menu_items), 0)
        self.assertEqual(len(self.menu_bar.menu_states), 0)
        self.assertEqual(len(self.menu_bar.accelerator_bindings), 0)
        self.assertEqual(len(self.menu_bar.menu_variables), 0)

    def test_error_handling(self):
        """测试错误处理"""
        # 测试添加菜单到不存在的菜单栏
        broken_menu_bar = MenuBarTTK(self.root)
        broken_menu_bar.menu_bar = None

        menu_config = MenuConfig("测试")
        with self.assertRaises(ValueError):
            broken_menu_bar.add_menu(menu_config)

        # 测试设置不存在菜单的状态
        self.menu_bar.set_menu_item_state("不存在", "项目", "disabled")
        # 应该不抛出异常，只是记录警告

        # 测试移除不存在的菜单
        self.menu_bar.remove_menu("不存在")
        # 应该不抛出异常，只是记录警告


@unittest.skipUnless(TKINTER_AVAILABLE, "tkinter not available in this environment")
class TestMenuConfigMethods(unittest.TestCase):
    """MenuConfig类方法测试"""

    def setUp(self):
        """测试准备"""
        # 创建测试窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        self.menu_config = MenuConfig("测试菜单", underline=0)
        self.mock_command = Mock()
        self.test_var = tk.BooleanVar()
        self.test_string_var = tk.StringVar()

    def tearDown(self):
        """测试清理"""
        try:
            # 销毁测试窗口
            if self.root:
                self.root.destroy()
        except Exception as e:
            print(f"测试清理失败: {e}")

    def test_add_separator(self):
        """测试添加分隔符"""
        initial_count = len(self.menu_config.items)
        self.menu_config.add_separator()

        self.assertEqual(len(self.menu_config.items), initial_count + 1)
        separator = self.menu_config.items[-1]
        self.assertEqual(separator.item_type, "separator")

    def test_add_command(self):
        """测试添加命令菜单项"""
        self.menu_config.add_command(
            "测试命令",
            self.mock_command,
            accelerator="Ctrl+T",
            underline=0,
            state="normal",
        )

        self.assertEqual(len(self.menu_config.items), 1)
        item = self.menu_config.items[0]
        self.assertEqual(item.label, "测试命令")
        self.assertEqual(item.command, self.mock_command)
        self.assertEqual(item.accelerator, "Ctrl+T")
        self.assertEqual(item.item_type, "command")

    def test_add_checkbutton(self):
        """测试添加复选框菜单项"""
        self.menu_config.add_checkbutton(
            "测试复选框", self.test_var, command=self.mock_command
        )

        self.assertEqual(len(self.menu_config.items), 1)
        item = self.menu_config.items[0]
        self.assertEqual(item.label, "测试复选框")
        self.assertEqual(item.variable, self.test_var)
        self.assertEqual(item.item_type, "checkbutton")

    def test_add_radiobutton(self):
        """测试添加单选按钮菜单项"""
        self.menu_config.add_radiobutton(
            "测试单选", self.test_string_var, "test_value", command=self.mock_command
        )

        self.assertEqual(len(self.menu_config.items), 1)
        item = self.menu_config.items[0]
        self.assertEqual(item.label, "测试单选")
        self.assertEqual(item.variable, self.test_string_var)
        self.assertEqual(item.value, "test_value")
        self.assertEqual(item.item_type, "radiobutton")


if __name__ == "__main__":
    unittest.main()
