"""TTK基础窗口类

提供TTK应用程序的基础窗口功能,包括:
- 窗口基础属性管理(大小、位置、图标等)
- 菜单栏、工具栏、状态栏集成
- 窗口事件处理(关闭、最小化、最大化等)
- 窗口状态保存和恢复
- 主题和样式管理集成

设计目标:
1. 为TTK应用程序提供统一的窗口基础
2. 简化窗口管理和配置
3. 提供良好的用户体验
4. 支持跨平台兼容性

作者: MiniCRM开发团队
"""

import json
import logging
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable, Dict, Optional, Tuple


class BaseWindow(tk.Tk):
    """TTK基础窗口类

    所有TTK应用程序窗口的基类,提供统一的窗口管理、
    事件处理、状态保存等基础功能.
    """

    def __init__(
        self,
        title: str = "MiniCRM",
        size: Tuple[int, int] = (1200, 800),
        min_size: Optional[Tuple[int, int]] = None,
        max_size: Optional[Tuple[int, int]] = None,
        resizable: Tuple[bool, bool] = (True, True),
        center: bool = True,
        icon_path: Optional[str] = None,
        config_file: Optional[str] = None,
    ):
        """初始化基础窗口

        Args:
            title: 窗口标题
            size: 窗口大小 (宽度, 高度)
            min_size: 最小大小 (宽度, 高度)
            max_size: 最大大小 (宽度, 高度)
            resizable: 是否可调整大小 (水平, 垂直)
            center: 是否居中显示
            icon_path: 图标文件路径
            config_file: 配置文件路径
        """
        super().__init__()

        # 基础属性
        self.window_title = title
        self.window_size = size
        self.min_size = min_size or (800, 600)
        self.max_size = max_size
        self.resizable_config = resizable
        self.center_window = center
        self.icon_path = icon_path
        self.config_file = config_file or "window_config.json"

        # 日志记录器
        self.logger = logging.getLogger(self.__class__.__name__)

        # 窗口组件
        self.menu_bar: Optional[tk.Menu] = None
        self.tool_bar: Optional[ttk.Frame] = None
        self.status_bar: Optional[ttk.Frame] = None
        self.main_frame: Optional[ttk.Frame] = None

        # 状态管理
        self._window_state = {}
        self._is_closing = False
        self._event_handlers: Dict[str, list] = {}

        # 初始化窗口
        self._initialize_window()

    def _initialize_window(self) -> None:
        """初始化窗口"""
        try:
            self._setup_window_properties()
            self._load_window_state()
            self._setup_window_layout()
            self._bind_window_events()
            self._apply_window_styles()

            self.logger.info(f"窗口 '{self.window_title}' 初始化完成")

        except Exception as e:
            self.logger.error(f"窗口初始化失败: {e}")
            raise

    def _setup_window_properties(self) -> None:
        """设置窗口基础属性"""
        # 设置标题
        self.title(self.window_title)

        # 设置大小
        self.geometry(f"{self.window_size[0]}x{self.window_size[1]}")

        # 设置最小和最大大小
        self.minsize(*self.min_size)
        if self.max_size:
            self.maxsize(*self.max_size)

        # 设置是否可调整大小
        self.resizable(*self.resizable_config)

        # 设置图标
        if self.icon_path and os.path.exists(self.icon_path):
            try:
                self.iconbitmap(self.icon_path)
            except tk.TclError as e:
                self.logger.warning(f"设置图标失败: {e}")

        # 居中显示
        if self.center_window:
            self._center_window()

    def _center_window(self) -> None:
        """将窗口居中显示"""
        self.update_idletasks()

        # 获取窗口大小
        window_width = self.winfo_width()
        window_height = self.winfo_height()

        # 获取屏幕大小
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # 设置窗口位置
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _setup_window_layout(self) -> None:
        """设置窗口布局"""
        # 创建主框架
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 配置主框架的网格权重
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

    def _bind_window_events(self) -> None:
        """绑定窗口事件"""
        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_window_closing)

        # 绑定大小变化事件
        self.bind("<Configure>", self._on_window_configure)

        # 绑定焦点事件
        self.bind("<FocusIn>", self._on_window_focus_in)
        self.bind("<FocusOut>", self._on_window_focus_out)

    def _apply_window_styles(self) -> None:
        """应用窗口样式"""
        # 子类可以重写此方法来应用特定样式

    def create_menu_bar(self) -> tk.Menu:
        """创建菜单栏

        Returns:
            菜单栏对象
        """
        if self.menu_bar is None:
            self.menu_bar = tk.Menu(self)
            self.config(menu=self.menu_bar)
        return self.menu_bar

    def create_tool_bar(self, height: int = 40) -> ttk.Frame:
        """创建工具栏

        Args:
            height: 工具栏高度

        Returns:
            工具栏框架
        """
        if self.tool_bar is None:
            self.tool_bar = ttk.Frame(self.main_frame, height=height)
            self.tool_bar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
            self.tool_bar.pack_propagate(False)  # 保持固定高度
        return self.tool_bar

    def create_status_bar(self, height: int = 25) -> ttk.Frame:
        """创建状态栏

        Args:
            height: 状态栏高度

        Returns:
            状态栏框架
        """
        if self.status_bar is None:
            self.status_bar = ttk.Frame(self.main_frame, height=height)
            self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=2)
            self.status_bar.pack_propagate(False)  # 保持固定高度
        return self.status_bar

    def get_content_frame(self) -> ttk.Frame:
        """获取内容框架

        Returns:
            内容框架,用于放置主要内容
        """
        # 创建内容框架(在工具栏和状态栏之间)
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=2, pady=2)
        return content_frame

    def add_menu_item(
        self,
        menu_name: str,
        item_name: str,
        command: Callable,
        accelerator: str = "",
        separator_before: bool = False,
        separator_after: bool = False,
    ) -> None:
        """添加菜单项

        Args:
            menu_name: 菜单名称
            item_name: 菜单项名称
            command: 命令函数
            accelerator: 快捷键显示
            separator_before: 在此项前添加分隔符
            separator_after: 在此项后添加分隔符
        """
        if self.menu_bar is None:
            self.create_menu_bar()

        # 查找或创建菜单
        menu = None
        try:
            menu_end = self.menu_bar.index(tk.END)
            if menu_end is not None:
                for i in range(menu_end + 1):
                    try:
                        if self.menu_bar.entrycget(i, "label") == menu_name:
                            menu = self.menu_bar.nametowidget(
                                self.menu_bar.entrycget(i, "menu")
                            )
                            break
                    except tk.TclError:
                        continue
        except tk.TclError:
            # 菜单栏为空的情况
            pass

        if menu is None:
            menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label=menu_name, menu=menu)

        # 添加分隔符(前)
        if separator_before:
            menu.add_separator()

        # 添加菜单项
        menu.add_command(label=item_name, command=command, accelerator=accelerator)

        # 添加分隔符(后)
        if separator_after:
            menu.add_separator()

    def add_tool_button(
        self,
        text: str,
        command: Callable,
        tooltip: str = "",
        icon: Optional[str] = None,
    ) -> ttk.Button:
        """添加工具栏按钮

        Args:
            text: 按钮文本
            command: 点击命令
            tooltip: 工具提示
            icon: 图标路径

        Returns:
            创建的按钮
        """
        if self.tool_bar is None:
            self.create_tool_bar()

        # 创建按钮
        button = ttk.Button(self.tool_bar, text=text, command=command)

        # 设置图标
        if icon and os.path.exists(icon):
            try:
                # 这里可以添加图标加载逻辑
                pass
            except Exception as e:
                self.logger.warning(f"加载图标失败 [{icon}]: {e}")

        # 添加到工具栏
        button.pack(side=tk.LEFT, padx=2, pady=2)

        # 添加工具提示
        if tooltip:
            self._add_tooltip(button, tooltip)

        return button

    def set_status_text(self, text: str, section: int = 0) -> None:
        """设置状态栏文本

        Args:
            text: 状态文本
            section: 状态栏分区索引
        """
        if self.status_bar is None:
            self.create_status_bar()

        # 查找或创建状态标签
        status_labels = [
            child
            for child in self.status_bar.winfo_children()
            if isinstance(child, ttk.Label)
        ]

        while len(status_labels) <= section:
            label = ttk.Label(self.status_bar, text="")
            label.pack(side=tk.LEFT, padx=5, pady=2)
            status_labels.append(label)

        # 设置文本
        status_labels[section].config(text=text)

    def _add_tooltip(self, widget: tk.Widget, text: str) -> None:
        """为组件添加工具提示

        Args:
            widget: 目标组件
            text: 提示文本
        """

        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            label = ttk.Label(tooltip, text=text, background="lightyellow")
            label.pack()
            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, "tooltip"):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def add_event_handler(self, event_name: str, handler: Callable) -> None:
        """添加事件处理器

        Args:
            event_name: 事件名称
            handler: 事件处理函数
        """
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)

    def remove_event_handler(self, event_name: str, handler: Callable) -> None:
        """移除事件处理器

        Args:
            event_name: 事件名称
            handler: 事件处理函数
        """
        if event_name in self._event_handlers:
            try:
                self._event_handlers[event_name].remove(handler)
            except ValueError:
                self.logger.warning(f"事件处理器不存在: {event_name}")

    def trigger_event(self, event_name: str, *args, **kwargs) -> None:
        """触发事件

        Args:
            event_name: 事件名称
            *args: 事件参数
            **kwargs: 事件关键字参数
        """
        if event_name in self._event_handlers:
            for handler in self._event_handlers[event_name]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"事件处理器执行失败 [{event_name}]: {e}")

    def _on_window_closing(self) -> None:
        """窗口关闭事件处理"""
        if self._is_closing:
            return

        self._is_closing = True

        # 触发关闭前事件
        self.trigger_event("before_close")

        # 检查是否可以关闭
        if self._can_close():
            # 保存窗口状态
            self._save_window_state()

            # 触发关闭事件
            self.trigger_event("closing")

            # 清理资源
            self._cleanup()

            # 销毁窗口
            self.destroy()
        else:
            self._is_closing = False

    def _can_close(self) -> bool:
        """检查是否可以关闭窗口

        子类可以重写此方法来实现关闭前的检查逻辑

        Returns:
            是否可以关闭
        """
        return True

    def _on_window_configure(self, event) -> None:
        """窗口配置变化事件处理"""
        if event.widget == self:
            # 更新窗口状态
            self._window_state.update(
                {
                    "width": self.winfo_width(),
                    "height": self.winfo_height(),
                    "x": self.winfo_x(),
                    "y": self.winfo_y(),
                }
            )

            # 触发大小变化事件
            self.trigger_event("size_changed", self.winfo_width(), self.winfo_height())

    def _on_window_focus_in(self, event) -> None:
        """窗口获得焦点事件处理"""
        if event.widget == self:
            self.trigger_event("focus_in")

    def _on_window_focus_out(self, event) -> None:
        """窗口失去焦点事件处理"""
        if event.widget == self:
            self.trigger_event("focus_out")

    def _load_window_state(self) -> None:
        """加载窗口状态"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, encoding="utf-8") as f:
                    config = json.load(f)

                window_config = config.get("window", {})

                # 恢复窗口大小和位置
                if "width" in window_config and "height" in window_config:
                    width = window_config["width"]
                    height = window_config["height"]
                    x = window_config.get("x", 100)
                    y = window_config.get("y", 100)

                    self.geometry(f"{width}x{height}+{x}+{y}")

                # 恢复其他状态
                self._window_state.update(window_config)

                self.logger.debug("窗口状态加载完成")

        except Exception as e:
            self.logger.warning(f"加载窗口状态失败: {e}")

    def _save_window_state(self) -> None:
        """保存窗口状态"""
        try:
            # 更新当前状态
            self._window_state.update(
                {
                    "width": self.winfo_width(),
                    "height": self.winfo_height(),
                    "x": self.winfo_x(),
                    "y": self.winfo_y(),
                    "title": self.title(),
                }
            )

            # 读取现有配置
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, encoding="utf-8") as f:
                    config = json.load(f)

            # 更新窗口配置
            config["window"] = self._window_state

            # 确保配置目录存在
            config_dir = os.path.dirname(self.config_file)
            if config_dir:
                Path(config_dir).mkdir(parents=True, exist_ok=True)

            # 保存配置
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            self.logger.debug("窗口状态保存完成")

        except Exception as e:
            self.logger.warning(f"保存窗口状态失败: {e}")

    def _cleanup(self) -> None:
        """清理窗口资源"""
        try:
            # 清理事件处理器
            self._event_handlers.clear()

            # 清理菜单
            if self.menu_bar:
                self.menu_bar.destroy()

            self.logger.debug("窗口资源清理完成")

        except Exception as e:
            self.logger.error(f"窗口资源清理失败: {e}")

    def show_message(self, title: str, message: str, msg_type: str = "info") -> None:
        """显示消息对话框

        Args:
            title: 对话框标题
            message: 消息内容
            msg_type: 消息类型 ("info", "warning", "error", "question")
        """
        if msg_type == "info":
            messagebox.showinfo(title, message, parent=self)
        elif msg_type == "warning":
            messagebox.showwarning(title, message, parent=self)
        elif msg_type == "error":
            messagebox.showerror(title, message, parent=self)
        elif msg_type == "question":
            return messagebox.askyesno(title, message, parent=self)

    def show_error(self, message: str, title: str = "错误") -> None:
        """显示错误消息

        Args:
            message: 错误消息
            title: 对话框标题
        """
        self.show_message(title, message, "error")

    def show_warning(self, message: str, title: str = "警告") -> None:
        """显示警告消息

        Args:
            message: 警告消息
            title: 对话框标题
        """
        self.show_message(title, message, "warning")

    def show_info(self, message: str, title: str = "信息") -> None:
        """显示信息消息

        Args:
            message: 信息消息
            title: 对话框标题
        """
        self.show_message(title, message, "info")

    def confirm(self, message: str, title: str = "确认") -> bool:
        """显示确认对话框

        Args:
            message: 确认消息
            title: 对话框标题

        Returns:
            用户是否确认
        """
        return self.show_message(title, message, "question")

    def set_window_state(self, state: str) -> None:
        """设置窗口状态

        Args:
            state: 窗口状态 ("normal", "iconic", "withdrawn", "zoomed")
        """
        try:
            self.state(state)
        except tk.TclError as e:
            self.logger.warning(f"设置窗口状态失败: {e}")

    def maximize(self) -> None:
        """最大化窗口"""
        self.set_window_state("zoomed")

    def minimize(self) -> None:
        """最小化窗口"""
        self.set_window_state("iconic")

    def restore(self) -> None:
        """恢复窗口"""
        self.set_window_state("normal")

    def get_window_info(self) -> Dict[str, Any]:
        """获取窗口信息

        Returns:
            窗口信息字典
        """
        return {
            "title": self.title(),
            "width": self.winfo_width(),
            "height": self.winfo_height(),
            "x": self.winfo_x(),
            "y": self.winfo_y(),
            "state": self.state(),
            "resizable": self.resizable_config,
            "min_size": self.min_size,
            "max_size": self.max_size,
        }
