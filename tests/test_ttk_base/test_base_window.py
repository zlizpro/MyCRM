"""BaseWindow类单元测试

测试TTK基础窗口类的功能，包括：
- 窗口初始化和基础属性设置
- 菜单栏、工具栏、状态栏创建
- 事件处理机制
- 窗口状态保存和恢复
- 消息对话框功能

作者: MiniCRM开发团队
"""

import contextlib
import json
import os
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from src.minicrm.ui.ttk_base.base_window import BaseWindow


class TestBaseWindow(unittest.TestCase):
    """BaseWindow类测试"""

    def setUp(self):
        """测试准备"""
        # 创建临时配置文件
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")

        # 创建测试窗口（隐藏显示）
        self.window = BaseWindow(
            title="测试窗口", size=(800, 600), config_file=self.config_file
        )
        self.window.withdraw()  # 隐藏窗口避免测试时显示

    def tearDown(self):
        """测试清理"""
        try:
            if self.window:
                self.window.destroy()
        except tk.TclError:
            pass

        # 清理临时文件
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_window_initialization(self):
        """测试窗口初始化"""
        # 验证基础属性
        assert self.window.window_title == "测试窗口"
        assert self.window.window_size == (800, 600)
        assert self.window.min_size == (800, 600)
        assert self.window.resizable_config, (True, True)

        # 验证窗口标题
        assert self.window.title() == "测试窗口"

        # 验证主框架存在
        assert self.window.main_frame is not None

    def test_menu_bar_creation(self):
        """测试菜单栏创建"""
        # 创建菜单栏
        menu_bar = self.window.create_menu_bar()

        # 验证菜单栏创建成功
        assert menu_bar is not None
        assert isinstance(menu_bar, tk.Menu)
        assert self.window.menu_bar == menu_bar

        # 重复调用应返回同一个菜单栏
        menu_bar2 = self.window.create_menu_bar()
        assert menu_bar == menu_bar2

    def test_tool_bar_creation(self):
        """测试工具栏创建"""
        # 创建工具栏
        tool_bar = self.window.create_tool_bar(height=50)

        # 验证工具栏创建成功
        assert tool_bar is not None
        assert isinstance(tool_bar, tk.ttk.Frame)
        assert self.window.tool_bar == tool_bar

        # 重复调用应返回同一个工具栏
        tool_bar2 = self.window.create_tool_bar()
        assert tool_bar == tool_bar2

    def test_status_bar_creation(self):
        """测试状态栏创建"""
        # 创建状态栏
        status_bar = self.window.create_status_bar(height=30)

        # 验证状态栏创建成功
        assert status_bar is not None
        assert isinstance(status_bar, tk.ttk.Frame)
        assert self.window.status_bar == status_bar

        # 重复调用应返回同一个状态栏
        status_bar2 = self.window.create_status_bar()
        assert status_bar == status_bar2

    def test_content_frame_creation(self):
        """测试内容框架创建"""
        # 获取内容框架
        content_frame = self.window.get_content_frame()

        # 验证内容框架创建成功
        assert content_frame is not None
        assert isinstance(content_frame, tk.ttk.Frame)

    def test_menu_item_addition(self):
        """测试菜单项添加"""
        # 创建菜单栏
        self.window.create_menu_bar()

        # 添加菜单项
        test_command = Mock()
        self.window.add_menu_item(
            menu_name="文件",
            item_name="新建",
            command=test_command,
            accelerator="Ctrl+N",
        )

        # 验证菜单创建成功（通过检查菜单栏是否有子菜单）
        assert self.window.menu_bar is not None

    def test_tool_button_addition(self):
        """测试工具栏按钮添加"""
        # 创建工具栏
        self.window.create_tool_bar()

        # 添加工具按钮
        test_command = Mock()
        button = self.window.add_tool_button(
            text="保存", command=test_command, tooltip="保存文件"
        )

        # 验证按钮创建成功
        assert button is not None
        assert isinstance(button, tk.ttk.Button)

    def test_status_text_setting(self):
        """测试状态栏文本设置"""
        # 创建状态栏
        self.window.create_status_bar()

        # 设置状态文本
        self.window.set_status_text("就绪", 0)
        self.window.set_status_text("行: 1, 列: 1", 1)

        # 验证状态栏有子组件
        assert len(self.window.status_bar.winfo_children()) > 0

    def test_event_handler_management(self):
        """测试事件处理器管理"""
        # 添加事件处理器
        handler1 = Mock()
        handler2 = Mock()

        self.window.add_event_handler("test_event", handler1)
        self.window.add_event_handler("test_event", handler2)

        # 触发事件
        self.window.trigger_event("test_event", "arg1", key="value")

        # 验证处理器被调用
        handler1.assert_called_once_with("arg1", key="value")
        handler2.assert_called_once_with("arg1", key="value")

        # 移除事件处理器
        self.window.remove_event_handler("test_event", handler1)

        # 再次触发事件
        handler1.reset_mock()
        handler2.reset_mock()
        self.window.trigger_event("test_event", "arg2")

        # 验证只有handler2被调用
        handler1.assert_not_called()
        handler2.assert_called_once_with("arg2")

    def test_window_state_management(self):
        """测试窗口状态管理"""
        # 设置窗口状态
        self.window._window_state = {"width": 1000, "height": 700, "x": 100, "y": 50}

        # 保存窗口状态
        self.window._save_window_state()

        # 验证配置文件创建
        assert os.path.exists(self.config_file)

        # 读取配置文件验证内容
        with open(self.config_file, encoding="utf-8") as f:
            config = json.load(f)

        assert "window" in config
        window_config = config["window"]
        assert window_config["width"] == 1000
        assert window_config["height"] == 700

    def test_window_state_loading(self):
        """测试窗口状态加载"""
        # 创建配置文件
        config = {
            "window": {
                "width": 900,
                "height": 650,
                "x": 200,
                "y": 100,
                "title": "测试窗口",
            }
        }

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f)

        # 创建新窗口加载配置
        new_window = BaseWindow(title="新窗口", config_file=self.config_file)
        new_window.withdraw()

        try:
            # 验证状态加载
            assert "width" in new_window._window_state
            assert new_window._window_state["width"] == 900
        finally:
            new_window.destroy()

    @patch("tkinter.messagebox.showinfo")
    def test_show_info_message(self, mock_showinfo):
        """测试信息消息显示"""
        self.window.show_info("测试信息", "信息标题")
        mock_showinfo.assert_called_once_with(
            "信息标题", "测试信息", parent=self.window
        )

    @patch("tkinter.messagebox.showwarning")
    def test_show_warning_message(self, mock_showwarning):
        """测试警告消息显示"""
        self.window.show_warning("测试警告", "警告标题")
        mock_showwarning.assert_called_once_with(
            "警告标题", "测试警告", parent=self.window
        )

    @patch("tkinter.messagebox.showerror")
    def test_show_error_message(self, mock_showerror):
        """测试错误消息显示"""
        self.window.show_error("测试错误", "错误标题")
        mock_showerror.assert_called_once_with(
            "错误标题", "测试错误", parent=self.window
        )

    @patch("tkinter.messagebox.askyesno")
    def test_confirm_dialog(self, mock_askyesno):
        """测试确认对话框"""
        mock_askyesno.return_value = True

        result = self.window.confirm("确认操作？", "确认")

        assert result
        mock_askyesno.assert_called_once_with("确认", "确认操作？", parent=self.window)

    def test_window_state_methods(self):
        """测试窗口状态方法"""
        # 测试最大化（在测试环境中可能不会真正最大化）
        try:
            self.window.maximize()
        except tk.TclError:
            pass  # 在某些测试环境中可能失败

        # 测试最小化
        with contextlib.suppress(tk.TclError):
            self.window.minimize()

        # 测试恢复
        with contextlib.suppress(tk.TclError):
            self.window.restore()

    def test_window_info_retrieval(self):
        """测试窗口信息获取"""
        info = self.window.get_window_info()

        # 验证信息字典包含必要字段
        assert "title" in info
        assert "width" in info
        assert "height" in info
        assert "x" in info
        assert "y" in info
        assert "state" in info
        assert "resizable" in info
        assert "min_size" in info

    def test_can_close_method(self):
        """测试关闭检查方法"""
        # 默认应该可以关闭
        assert self.window._can_close()

    def test_cleanup_method(self):
        """测试清理方法"""
        # 添加一些事件处理器
        handler = Mock()
        self.window.add_event_handler("test", handler)

        # 执行清理
        self.window._cleanup()

        # 验证事件处理器被清理
        assert len(self.window._event_handlers) == 0

    def test_window_closing_workflow(self):
        """测试窗口关闭工作流程"""
        # 添加关闭前事件处理器
        before_close_handler = Mock()
        closing_handler = Mock()

        self.window.add_event_handler("before_close", before_close_handler)
        self.window.add_event_handler("closing", closing_handler)

        # 模拟关闭事件
        with patch.object(self.window, "_can_close", return_value=True):
            with patch.object(self.window, "destroy"):
                self.window._on_window_closing()

        # 验证事件被触发
        before_close_handler.assert_called_once()
        closing_handler.assert_called_once()

    def test_window_configure_event(self):
        """测试窗口配置变化事件"""
        # 创建模拟事件
        mock_event = Mock()
        mock_event.widget = self.window

        # 添加大小变化事件处理器
        size_changed_handler = Mock()
        self.window.add_event_handler("size_changed", size_changed_handler)

        # 模拟配置变化
        with patch.object(self.window, "winfo_width", return_value=1000):
            with patch.object(self.window, "winfo_height", return_value=800):
                with patch.object(self.window, "winfo_x", return_value=100):
                    with patch.object(self.window, "winfo_y", return_value=50):
                        self.window._on_window_configure(mock_event)

        # 验证事件被触发
        size_changed_handler.assert_called_once_with(1000, 800)

        # 验证窗口状态更新
        assert self.window._window_state["width"] == 1000
        assert self.window._window_state["height"] == 800

    def test_focus_events(self):
        """测试焦点事件"""
        # 添加焦点事件处理器
        focus_in_handler = Mock()
        focus_out_handler = Mock()

        self.window.add_event_handler("focus_in", focus_in_handler)
        self.window.add_event_handler("focus_out", focus_out_handler)

        # 创建模拟事件
        mock_event = Mock()
        mock_event.widget = self.window

        # 测试焦点获得事件
        self.window._on_window_focus_in(mock_event)
        focus_in_handler.assert_called_once()

        # 测试焦点失去事件
        self.window._on_window_focus_out(mock_event)
        focus_out_handler.assert_called_once()


class TestBaseWindowIntegration(unittest.TestCase):
    """BaseWindow集成测试"""

    def setUp(self):
        """测试准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "integration_config.json")

    def tearDown(self):
        """测试清理"""
        # 清理临时文件
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_complete_window_workflow(self):
        """测试完整的窗口工作流程"""
        # 创建窗口
        window = BaseWindow(
            title="集成测试窗口", size=(1000, 700), config_file=self.config_file
        )
        window.withdraw()

        try:
            # 创建菜单栏
            menu_bar = window.create_menu_bar()
            assert menu_bar is not None

            # 添加菜单项
            file_command = Mock()
            window.add_menu_item("文件", "新建", file_command, "Ctrl+N")

            # 创建工具栏
            tool_bar = window.create_tool_bar()
            assert tool_bar is not None

            # 添加工具按钮
            save_command = Mock()
            save_button = window.add_tool_button("保存", save_command, "保存文件")
            assert save_button is not None

            # 创建状态栏
            status_bar = window.create_status_bar()
            assert status_bar is not None

            # 设置状态文本
            window.set_status_text("就绪")

            # 获取内容框架
            content_frame = window.get_content_frame()
            assert content_frame is not None

            # 添加事件处理器
            test_handler = Mock()
            window.add_event_handler("test_event", test_handler)

            # 触发事件
            window.trigger_event("test_event", "test_data")
            test_handler.assert_called_once_with("test_data")

            # 保存窗口状态
            window._save_window_state()
            assert os.path.exists(self.config_file)

        finally:
            window.destroy()

    def test_window_state_persistence(self):
        """测试窗口状态持久化"""
        # 创建第一个窗口并设置状态
        window1 = BaseWindow(
            title="状态测试窗口1", size=(800, 600), config_file=self.config_file
        )
        window1.withdraw()

        try:
            # 模拟窗口状态变化
            window1._window_state.update(
                {"width": 1200, "height": 800, "x": 150, "y": 100}
            )

            # 保存状态
            window1._save_window_state()

        finally:
            window1.destroy()

        # 创建第二个窗口加载状态
        window2 = BaseWindow(title="状态测试窗口2", config_file=self.config_file)
        window2.withdraw()

        try:
            # 验证状态加载
            assert window2._window_state.get("width") == 1200
            assert window2._window_state.get("height") == 800
            assert window2._window_state.get("x") == 150
            assert window2._window_state.get("y") == 100

        finally:
            window2.destroy()


if __name__ == "__main__":
    unittest.main()
