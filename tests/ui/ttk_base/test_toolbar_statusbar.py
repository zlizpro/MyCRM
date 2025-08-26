"""TTK工具栏和状态栏系统单元测试

测试ToolBarTTK和StatusBarTTK类的各项功能，包括：
- 工具栏的创建和按钮管理
- 状态栏的创建和分区管理
- 按钮状态管理和事件处理
- 进度条显示和控制
- 配置的保存和加载

作者: MiniCRM开发团队
"""

import os
import tempfile
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

from src.minicrm.ui.ttk_base.statusbar import StatusBarTTK, StatusSectionConfig
from src.minicrm.ui.ttk_base.toolbar import ToolBarTTK, ToolButtonConfig


@unittest.skipUnless(TKINTER_AVAILABLE, "tkinter not available in this environment")
class TestToolBarTTK(unittest.TestCase):
    """ToolBarTTK类测试"""

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

        # 创建工具栏实例
        self.toolbar = ToolBarTTK(
            parent=self.root,
            orientation="horizontal",
            height=40,
            config_file=self.temp_config_path,
            auto_save_config=False,
        )

        # 创建测试变量
        self.test_bool_var = tk.BooleanVar()
        self.test_string_var = tk.StringVar()

        # 创建模拟命令函数
        self.mock_command = Mock()

    def tearDown(self):
        """测试清理"""
        try:
            # 清理工具栏
            if self.toolbar:
                self.toolbar.cleanup()

            # 销毁测试窗口
            if self.root:
                self.root.destroy()

            # 删除临时配置文件
            if os.path.exists(self.temp_config_path):
                os.unlink(self.temp_config_path)

        except Exception as e:
            print(f"测试清理失败: {e}")

    def test_toolbar_initialization(self):
        """测试工具栏初始化"""
        # 验证工具栏创建成功
        self.assertIsNotNone(self.toolbar.toolbar_frame)
        self.assertEqual(self.toolbar.orientation, "horizontal")

        # 验证初始状态
        self.assertEqual(len(self.toolbar.buttons), 0)
        self.assertEqual(len(self.toolbar.button_configs), 0)
        self.assertEqual(len(self.toolbar.separators), 0)

    def test_button_config_creation(self):
        """测试按钮配置创建"""
        # 创建按钮配置
        button_config = ToolButtonConfig(
            button_id="test_button",
            text="测试按钮",
            command=self.mock_command,
            tooltip="这是一个测试按钮",
            state="normal",
            button_type="button",
        )

        # 验证配置属性
        self.assertEqual(button_config.button_id, "test_button")
        self.assertEqual(button_config.text, "测试按钮")
        self.assertEqual(button_config.command, self.mock_command)
        self.assertEqual(button_config.tooltip, "这是一个测试按钮")
        self.assertEqual(button_config.button_type, "button")

    def test_add_button(self):
        """测试添加按钮"""
        # 创建按钮配置
        button_config = ToolButtonConfig(
            button_id="new_button",
            text="新建",
            command=self.mock_command,
            tooltip="创建新文件",
        )

        # 添加按钮
        button = self.toolbar.add_button(button_config)

        # 验证按钮创建
        self.assertIsNotNone(button)

        # 验证按钮保存
        self.assertIn("new_button", self.toolbar.buttons)
        self.assertIn("new_button", self.toolbar.button_configs)
        self.assertIn("new_button", self.toolbar.button_states)

        # 验证按钮状态
        self.assertEqual(self.toolbar.button_states["new_button"], "normal")

    def test_add_checkbutton(self):
        """测试添加复选按钮"""
        # 创建复选按钮配置
        button_config = ToolButtonConfig(
            button_id="check_button",
            text="显示工具栏",
            button_type="checkbutton",
            variable=self.test_bool_var,
            command=self.mock_command,
        )

        # 添加按钮
        button = self.toolbar.add_button(button_config)

        # 验证按钮创建
        self.assertIsNotNone(button)
        self.assertIn("check_button", self.toolbar.buttons)

        # 设置变量并验证
        self.test_bool_var.set(True)
        self.assertTrue(self.test_bool_var.get())

    def test_add_radiobutton(self):
        """测试添加单选按钮"""
        # 创建单选按钮配置
        button_config = ToolButtonConfig(
            button_id="radio_button",
            text="选项1",
            button_type="radiobutton",
            variable=self.test_string_var,
            value="option1",
            command=self.mock_command,
        )

        # 添加按钮
        button = self.toolbar.add_button(button_config)

        # 验证按钮创建
        self.assertIsNotNone(button)
        self.assertIn("radio_button", self.toolbar.buttons)

        # 设置变量并验证
        self.test_string_var.set("option1")
        self.assertEqual(self.test_string_var.get(), "option1")

    def test_add_separator(self):
        """测试添加分隔符"""
        # 创建分隔符配置
        separator_config = ToolButtonConfig(
            button_id="separator1", button_type="separator"
        )

        # 添加分隔符
        separator = self.toolbar.add_button(separator_config)

        # 验证分隔符创建
        self.assertIsNotNone(separator)
        self.assertEqual(len(self.toolbar.separators), 1)

    def test_button_state_management(self):
        """测试按钮状态管理"""
        # 添加按钮
        button_config = ToolButtonConfig(
            button_id="state_button", text="状态测试", command=self.mock_command
        )
        self.toolbar.add_button(button_config)

        # 测试设置按钮状态
        self.toolbar.set_button_state("state_button", "disabled")
        self.assertEqual(self.toolbar.get_button_state("state_button"), "disabled")

        # 测试启用/禁用方法
        self.toolbar.disable_button("state_button")
        self.assertEqual(self.toolbar.get_button_state("state_button"), "disabled")

        self.toolbar.enable_button("state_button")
        self.assertEqual(self.toolbar.get_button_state("state_button"), "normal")

    def test_update_button_properties(self):
        """测试更新按钮属性"""
        # 添加按钮
        button_config = ToolButtonConfig(
            button_id="update_button", text="原始文本", command=self.mock_command
        )
        self.toolbar.add_button(button_config)

        # 测试更新文本
        self.toolbar.update_button_text("update_button", "新文本")
        self.assertEqual(self.toolbar.button_configs["update_button"].text, "新文本")

        # 测试更新命令
        new_command = Mock()
        self.toolbar.update_button_command("update_button", new_command)
        self.assertEqual(
            self.toolbar.button_configs["update_button"].command, new_command
        )

    def test_remove_button(self):
        """测试移除按钮"""
        # 添加按钮
        button_config = ToolButtonConfig(
            button_id="remove_button", text="待移除", command=self.mock_command
        )
        self.toolbar.add_button(button_config)

        # 验证按钮存在
        self.assertIn("remove_button", self.toolbar.buttons)

        # 移除按钮
        self.toolbar.remove_button("remove_button")

        # 验证按钮移除
        self.assertNotIn("remove_button", self.toolbar.buttons)
        self.assertNotIn("remove_button", self.toolbar.button_configs)
        self.assertNotIn("remove_button", self.toolbar.button_states)

    def test_clear_all_buttons(self):
        """测试清除所有按钮"""
        # 添加多个按钮
        for i in range(3):
            button_config = ToolButtonConfig(
                button_id=f"button_{i}", text=f"按钮{i}", command=self.mock_command
            )
            self.toolbar.add_button(button_config)

        # 验证按钮存在
        self.assertEqual(len(self.toolbar.buttons), 3)

        # 清除所有按钮
        self.toolbar.clear_all_buttons()

        # 验证按钮清除
        self.assertEqual(len(self.toolbar.buttons), 0)
        self.assertEqual(len(self.toolbar.button_configs), 0)
        self.assertEqual(len(self.toolbar.button_states), 0)

    def test_get_toolbar_info(self):
        """测试获取工具栏信息"""
        # 添加按钮
        button_config = ToolButtonConfig(
            button_id="info_button",
            text="信息按钮",
            command=self.mock_command,
            tooltip="信息提示",
        )
        self.toolbar.add_button(button_config)

        # 获取工具栏信息
        info = self.toolbar.get_toolbar_info()

        # 验证信息
        self.assertEqual(info["orientation"], "horizontal")
        self.assertEqual(info["button_count"], 1)
        self.assertIn("info_button", info["buttons"])

        button_info = info["buttons"]["info_button"]
        self.assertEqual(button_info["text"], "信息按钮")
        self.assertEqual(button_info["type"], "button")
        self.assertEqual(button_info["tooltip"], "信息提示")


@unittest.skipUnless(TKINTER_AVAILABLE, "tkinter not available in this environment")
class TestStatusBarTTK(unittest.TestCase):
    """StatusBarTTK类测试"""

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

        # 创建状态栏实例
        self.statusbar = StatusBarTTK(
            parent=self.root,
            height=25,
            config_file=self.temp_config_path,
            auto_save_config=False,
        )

        # 创建模拟命令函数
        self.mock_command = Mock()

    def tearDown(self):
        """测试清理"""
        try:
            # 清理状态栏
            if self.statusbar:
                self.statusbar.cleanup()

            # 销毁测试窗口
            if self.root:
                self.root.destroy()

            # 删除临时配置文件
            if os.path.exists(self.temp_config_path):
                os.unlink(self.temp_config_path)

        except Exception as e:
            print(f"测试清理失败: {e}")

    def test_statusbar_initialization(self):
        """测试状态栏初始化"""
        # 验证状态栏创建成功
        self.assertIsNotNone(self.statusbar.statusbar_frame)
        self.assertEqual(self.statusbar.height, 25)

        # 验证初始状态
        self.assertEqual(len(self.statusbar.sections), 0)
        self.assertEqual(len(self.statusbar.section_configs), 0)

    def test_section_config_creation(self):
        """测试分区配置创建"""
        # 创建分区配置
        section_config = StatusSectionConfig(
            section_id="main_status",
            section_type="label",
            text="就绪",
            width=200,
            anchor="w",
        )

        # 验证配置属性
        self.assertEqual(section_config.section_id, "main_status")
        self.assertEqual(section_config.section_type, "label")
        self.assertEqual(section_config.text, "就绪")
        self.assertEqual(section_config.width, 200)
        self.assertEqual(section_config.anchor, "w")

    def test_add_label_section(self):
        """测试添加标签分区"""
        # 创建标签分区配置
        section_config = StatusSectionConfig(
            section_id="status_label",
            section_type="label",
            text="状态：正常",
            width=150,
        )

        # 添加分区
        section = self.statusbar.add_section(section_config)

        # 验证分区创建
        self.assertIsNotNone(section)

        # 验证分区保存
        self.assertIn("status_label", self.statusbar.sections)
        self.assertIn("status_label", self.statusbar.section_configs)
        self.assertIn("status_label", self.statusbar.section_texts)

        # 验证分区文本
        self.assertEqual(self.statusbar.section_texts["status_label"], "状态：正常")

    def test_add_progressbar_section(self):
        """测试添加进度条分区"""
        # 创建进度条分区配置
        section_config = StatusSectionConfig(
            section_id="progress_bar", section_type="progressbar", width=200
        )

        # 添加分区
        section = self.statusbar.add_section(section_config)

        # 验证分区创建
        self.assertIsNotNone(section)
        self.assertIn("progress_bar", self.statusbar.sections)

        # 验证进度值初始化
        self.assertIn("progress_bar", self.statusbar.progress_values)
        self.assertEqual(self.statusbar.progress_values["progress_bar"], 0.0)

    def test_add_button_section(self):
        """测试添加按钮分区"""
        # 创建按钮分区配置
        section_config = StatusSectionConfig(
            section_id="status_button", section_type="button", text="设置", width=60
        )

        # 添加分区
        section = self.statusbar.add_section(section_config)

        # 验证分区创建
        self.assertIsNotNone(section)
        self.assertIn("status_button", self.statusbar.sections)

    def test_add_separator_section(self):
        """测试添加分隔符分区"""
        # 创建分隔符分区配置
        section_config = StatusSectionConfig(
            section_id="separator1", section_type="separator"
        )

        # 添加分区
        section = self.statusbar.add_section(section_config)

        # 验证分区创建
        self.assertIsNotNone(section)
        self.assertIn("separator1", self.statusbar.sections)

    def test_text_management(self):
        """测试文本管理"""
        # 添加标签分区
        section_config = StatusSectionConfig(
            section_id="text_section", section_type="label", text="初始文本"
        )
        self.statusbar.add_section(section_config)

        # 测试设置文本
        self.statusbar.set_text("text_section", "新文本")
        self.assertEqual(self.statusbar.get_text("text_section"), "新文本")

        # 测试不存在的分区
        self.assertIsNone(self.statusbar.get_text("不存在"))

    def test_progress_management(self):
        """测试进度管理"""
        # 添加进度条分区
        section_config = StatusSectionConfig(
            section_id="progress_section", section_type="progressbar", width=200
        )
        self.statusbar.add_section(section_config)

        # 测试设置进度
        self.statusbar.set_progress("progress_section", 50.0, 100.0)
        self.assertEqual(self.statusbar.get_progress("progress_section"), 50.0)

        # 测试启动和停止进度动画
        self.statusbar.start_progress("progress_section")
        self.statusbar.stop_progress("progress_section")

    def test_button_command_setting(self):
        """测试按钮命令设置"""
        # 添加按钮分区
        section_config = StatusSectionConfig(
            section_id="command_button", section_type="button", text="点击我"
        )
        self.statusbar.add_section(section_config)

        # 设置按钮命令
        self.statusbar.set_button_command("command_button", self.mock_command)

        # 验证命令设置（这里主要验证方法调用不出错）
        # 实际的命令验证需要通过按钮点击来测试，这在单元测试中比较困难

    def test_remove_section(self):
        """测试移除分区"""
        # 添加分区
        section_config = StatusSectionConfig(
            section_id="remove_section", section_type="label", text="待移除"
        )
        self.statusbar.add_section(section_config)

        # 验证分区存在
        self.assertIn("remove_section", self.statusbar.sections)

        # 移除分区
        self.statusbar.remove_section("remove_section")

        # 验证分区移除
        self.assertNotIn("remove_section", self.statusbar.sections)
        self.assertNotIn("remove_section", self.statusbar.section_configs)
        self.assertNotIn("remove_section", self.statusbar.section_texts)

    def test_clear_all_sections(self):
        """测试清除所有分区"""
        # 添加多个分区
        for i in range(3):
            section_config = StatusSectionConfig(
                section_id=f"section_{i}", section_type="label", text=f"分区{i}"
            )
            self.statusbar.add_section(section_config)

        # 验证分区存在
        self.assertEqual(len(self.statusbar.sections), 3)

        # 清除所有分区
        self.statusbar.clear_all_sections()

        # 验证分区清除
        self.assertEqual(len(self.statusbar.sections), 0)
        self.assertEqual(len(self.statusbar.section_configs), 0)
        self.assertEqual(len(self.statusbar.section_texts), 0)

    def test_show_message(self):
        """测试显示临时消息"""
        # 添加标签分区
        section_config = StatusSectionConfig(
            section_id="message_section", section_type="label", text="原始文本"
        )
        self.statusbar.add_section(section_config)

        # 显示临时消息
        self.statusbar.show_message(
            "临时消息", duration=0.1, section_id="message_section"
        )

        # 验证消息显示
        self.assertEqual(self.statusbar.get_text("message_section"), "临时消息")

        # 等待消息恢复（短暂等待）
        time.sleep(0.2)

        # 验证消息恢复
        self.assertEqual(self.statusbar.get_text("message_section"), "原始文本")

    def test_update_callbacks(self):
        """测试更新回调"""
        # 添加分区
        section_config = StatusSectionConfig(
            section_id="callback_section", section_type="label", text="回调测试"
        )
        self.statusbar.add_section(section_config)

        # 创建回调函数
        callback = Mock()

        # 添加更新回调
        self.statusbar.add_update_callback("callback_section", callback)

        # 验证回调添加
        self.assertIn("callback_section", self.statusbar.update_callbacks)
        self.assertIn(callback, self.statusbar.update_callbacks["callback_section"])

        # 移除更新回调
        self.statusbar.remove_update_callback("callback_section", callback)

        # 验证回调移除
        self.assertNotIn(callback, self.statusbar.update_callbacks["callback_section"])

    def test_auto_update(self):
        """测试自动更新"""
        # 添加分区
        section_config = StatusSectionConfig(
            section_id="auto_update_section", section_type="label", text="自动更新测试"
        )
        self.statusbar.add_section(section_config)

        # 创建更新回调
        update_count = [0]  # 使用列表来在闭包中修改值

        def update_callback(section_id):
            update_count[0] += 1
            self.statusbar.set_text(section_id, f"更新次数: {update_count[0]}")

        # 添加回调
        self.statusbar.add_update_callback("auto_update_section", update_callback)

        # 启动自动更新
        self.statusbar.start_auto_update(interval=0.1)

        # 等待几次更新
        time.sleep(0.3)

        # 停止自动更新
        self.statusbar.stop_auto_update()

        # 验证更新执行
        self.assertGreater(update_count[0], 0)

    def test_get_statusbar_info(self):
        """测试获取状态栏信息"""
        # 添加分区
        section_config = StatusSectionConfig(
            section_id="info_section", section_type="label", text="信息测试"
        )
        self.statusbar.add_section(section_config)

        # 获取状态栏信息
        info = self.statusbar.get_statusbar_info()

        # 验证信息
        self.assertEqual(info["height"], 25)
        self.assertEqual(info["section_count"], 1)
        self.assertFalse(info["auto_update_enabled"])
        self.assertIn("info_section", info["sections"])

        section_info = info["sections"]["info_section"]
        self.assertEqual(section_info["type"], "label")
        self.assertEqual(section_info["text"], "信息测试")


if __name__ == "__main__":
    unittest.main()
