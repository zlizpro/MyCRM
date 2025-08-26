"""TTK基础对话框类

提供所有TTK对话框的基础功能,包括:
- 模态显示和非模态显示
- 标准按钮布局(确定/取消)
- 键盘事件处理(ESC关闭、Enter确认)
- 对话框居中显示和定位
- 结果返回机制
- 事件处理和数据管理

设计目标:
1. 为所有TTK对话框提供统一的基础功能
2. 简化对话框开发和维护
3. 确保对话框的一致性和用户体验
4. 提供良好的扩展性

作者: MiniCRM开发团队
"""

from abc import ABC, abstractmethod
import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Tuple


class DialogResult:
    """对话框结果枚举"""

    OK = "ok"
    CANCEL = "cancel"
    YES = "yes"
    NO = "no"
    RETRY = "retry"
    IGNORE = "ignore"
    ABORT = "abort"


class BaseDialogTTK(tk.Toplevel, ABC):
    """TTK基础对话框类

    所有自定义TTK对话框的基类,提供统一的对话框管理、
    事件处理、模态显示等基础功能.
    """

    def __init__(
        self,
        parent: Optional[tk.Widget] = None,
        title: str = "对话框",
        size: Tuple[int, int] = (400, 300),
        min_size: Optional[Tuple[int, int]] = None,
        max_size: Optional[Tuple[int, int]] = None,
        resizable: Tuple[bool, bool] = (True, True),
        modal: bool = True,
        center: bool = True,
        **kwargs,
    ):
        """初始化基础对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            size: 对话框大小 (宽度, 高度)
            min_size: 最小大小 (宽度, 高度)
            max_size: 最大大小 (宽度, 高度)
            resizable: 是否可调整大小 (水平, 垂直)
            modal: 是否模态显示
            center: 是否居中显示
            **kwargs: 其他参数
        """
        super().__init__(parent, **kwargs)

        # 基础属性
        self.parent_window = parent
        self.dialog_title = title
        self.dialog_size = size
        self.min_size = min_size or (300, 200)
        self.max_size = max_size
        self.resizable_config = resizable
        self.is_modal = modal
        self.center_dialog = center

        # 日志记录器
        self.logger = logging.getLogger(self.__class__.__name__)

        # 对话框状态
        self.result = None
        self.return_value = None
        self._is_closing = False
        self._initialized = False

        # 事件处理器存储
        self._event_handlers: Dict[str, List[Callable]] = {}

        # 对话框组件
        self.main_frame: Optional[ttk.Frame] = None
        self.content_frame: Optional[ttk.Frame] = None
        self.button_frame: Optional[ttk.Frame] = None
        self.buttons: Dict[str, ttk.Button] = {}

        # 数据存储
        self._data: Dict[str, Any] = {}

        # 执行初始化流程
        self._initialize()

    def _initialize(self) -> None:
        """对话框初始化流程"""
        try:
            self._setup_dialog_properties()
            self._setup_dialog_layout()
            self._setup_content()
            self._setup_buttons()
            self._bind_events()
            self._apply_styles()
            self._post_initialize()

            self._initialized = True
            self.logger.debug(f"对话框 '{self.dialog_title}' 初始化完成")

        except Exception as e:
            self.logger.error(f"对话框初始化失败: {e}")
            raise

    def _setup_dialog_properties(self) -> None:
        """设置对话框基础属性"""
        # 设置标题
        self.title(self.dialog_title)

        # 设置大小
        self.geometry(f"{self.dialog_size[0]}x{self.dialog_size[1]}")

        # 设置最小和最大大小
        self.minsize(*self.min_size)
        if self.max_size:
            self.maxsize(*self.max_size)

        # 设置是否可调整大小
        self.resizable(*self.resizable_config)

        # 设置为对话框窗口
        self.transient(self.parent_window)

        # 居中显示
        if self.center_dialog:
            self._center_dialog()

        # 设置模态
        if self.is_modal:
            self.grab_set()

        # 设置焦点
        self.focus_set()

    def _center_dialog(self) -> None:
        """将对话框居中显示"""
        self.update_idletasks()

        # 获取对话框大小
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        # 获取父窗口信息或屏幕信息
        if self.parent_window:
            parent_x = self.parent_window.winfo_x()
            parent_y = self.parent_window.winfo_y()
            parent_width = self.parent_window.winfo_width()
            parent_height = self.parent_window.winfo_height()

            # 相对于父窗口居中
            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
        else:
            # 相对于屏幕居中
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width - dialog_width) // 2
            y = (screen_height - dialog_height) // 2

        # 确保对话框在屏幕范围内
        x = max(0, min(x, self.winfo_screenwidth() - dialog_width))
        y = max(0, min(y, self.winfo_screenheight() - dialog_height))

        # 设置位置
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

    def _setup_dialog_layout(self) -> None:
        """设置对话框布局"""
        # 创建主框架
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建内容框架
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 创建按钮框架
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM)

    @abstractmethod
    def _setup_content(self) -> None:
        """设置对话框内容

        子类必须实现此方法来创建具体的对话框内容.
        """

    def _setup_buttons(self) -> None:
        """设置对话框按钮

        子类可以重写此方法来自定义按钮.
        默认实现创建确定和取消按钮.
        """
        self.add_button("取消", self._on_cancel, DialogResult.CANCEL)
        self.add_button("确定", self._on_ok, DialogResult.OK, default=True)

    def add_button(
        self,
        text: str,
        command: Callable,
        result: str = None,
        default: bool = False,
        **kwargs,
    ) -> ttk.Button:
        """添加按钮

        Args:
            text: 按钮文本
            command: 点击命令
            result: 对话框结果
            default: 是否为默认按钮
            **kwargs: 其他按钮参数

        Returns:
            创建的按钮
        """
        button = ttk.Button(self.button_frame, text=text, command=command, **kwargs)
        button.pack(side=tk.RIGHT, padx=(5, 0))

        # 存储按钮
        self.buttons[text] = button

        # 设置默认按钮
        if default:
            button.configure(style="Accent.TButton")
            self.bind("<Return>", lambda e: command())

        # 存储结果
        if result:
            button.result = result

        return button

    def remove_button(self, text: str) -> None:
        """移除按钮

        Args:
            text: 按钮文本
        """
        if text in self.buttons:
            self.buttons[text].destroy()
            del self.buttons[text]

    def _bind_events(self) -> None:
        """绑定事件处理"""
        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # 绑定键盘事件
        self.bind("<Escape>", lambda e: self._on_cancel())
        self.bind("<Alt-F4>", lambda e: self._on_close())

        # 绑定焦点事件
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _apply_styles(self) -> None:
        """应用样式

        子类可以重写此方法来应用特定样式.
        """

    def _post_initialize(self) -> None:
        """初始化后处理

        子类可以重写此方法来执行初始化后的处理.
        """

    def _on_ok(self) -> None:
        """确定按钮处理"""
        if self._validate_input():
            self.result = DialogResult.OK
            self.return_value = self._get_result_data()
            self._close_dialog()

    def _on_cancel(self) -> None:
        """取消按钮处理"""
        self.result = DialogResult.CANCEL
        self.return_value = None
        self._close_dialog()

    def _on_close(self) -> None:
        """关闭按钮处理"""
        if not self._is_closing:
            self._on_cancel()

    def _validate_input(self) -> bool:
        """验证输入数据

        子类可以重写此方法来实现输入验证.

        Returns:
            是否验证通过
        """
        return True

    def _get_result_data(self) -> Any:
        """获取结果数据

        子类可以重写此方法来返回特定的结果数据.

        Returns:
            结果数据
        """
        return self._data.copy()

    def _close_dialog(self) -> None:
        """关闭对话框"""
        if self._is_closing:
            return

        self._is_closing = True

        try:
            # 触发关闭前事件
            self.trigger_event("before_close")

            # 释放模态
            if self.is_modal:
                self.grab_release()

            # 触发关闭事件
            self.trigger_event("closing")

            # 清理资源
            self._cleanup()

            # 销毁对话框
            self.destroy()

        except Exception as e:
            self.logger.error(f"关闭对话框失败: {e}")

    def _cleanup(self) -> None:
        """清理对话框资源"""
        try:
            # 清理事件处理器
            self._event_handlers.clear()

            # 清理数据
            self._data.clear()

            self.logger.debug("对话框资源清理完成")

        except Exception as e:
            self.logger.error(f"对话框资源清理失败: {e}")

    def _on_focus_in(self, event) -> None:
        """焦点进入事件处理"""
        if event.widget == self:
            self.trigger_event("focus_in")

    def _on_focus_out(self, event) -> None:
        """焦点离开事件处理"""
        if event.widget == self:
            self.trigger_event("focus_out")

    # ==================== 事件处理方法 ====================

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

    # ==================== 数据管理方法 ====================

    def set_data(self, key: str, value: Any) -> None:
        """设置对话框数据

        Args:
            key: 数据键
            value: 数据值
        """
        old_value = self._data.get(key)
        self._data[key] = value

        # 触发数据变化事件
        self.trigger_event("data_changed", key, old_value, value)

    def get_data(self, key: str, default: Any = None) -> Any:
        """获取对话框数据

        Args:
            key: 数据键
            default: 默认值

        Returns:
            数据值
        """
        return self._data.get(key, default)

    def get_all_data(self) -> Dict[str, Any]:
        """获取所有对话框数据

        Returns:
            数据字典
        """
        return self._data.copy()

    def clear_data(self) -> None:
        """清空对话框数据"""
        old_data = self._data.copy()
        self._data.clear()
        self.trigger_event("data_cleared", old_data)

    # ==================== 公共接口方法 ====================

    def show_dialog(self) -> Tuple[str, Any]:
        """显示对话框并等待结果

        Returns:
            (结果类型, 结果数据) 元组
        """
        # 显示对话框
        self.deiconify()

        # 如果是模态对话框,等待关闭
        if self.is_modal:
            self.wait_window()

        return self.result, self.return_value

    def close_dialog(
        self, result: str = DialogResult.CANCEL, return_value: Any = None
    ) -> None:
        """关闭对话框

        Args:
            result: 对话框结果
            return_value: 返回值
        """
        self.result = result
        self.return_value = return_value
        self._close_dialog()

    def set_button_enabled(self, text: str, enabled: bool) -> None:
        """设置按钮启用状态

        Args:
            text: 按钮文本
            enabled: 是否启用
        """
        if text in self.buttons:
            state = "normal" if enabled else "disabled"
            self.buttons[text].configure(state=state)

    def set_button_text(self, old_text: str, new_text: str) -> None:
        """设置按钮文本

        Args:
            old_text: 原按钮文本
            new_text: 新按钮文本
        """
        if old_text in self.buttons:
            button = self.buttons[old_text]
            button.configure(text=new_text)
            # 更新字典键
            self.buttons[new_text] = self.buttons.pop(old_text)

    def get_button(self, text: str) -> Optional[ttk.Button]:
        """获取按钮对象

        Args:
            text: 按钮文本

        Returns:
            按钮对象或None
        """
        return self.buttons.get(text)

    def show_error(self, message: str, title: str = "错误") -> None:
        """显示错误消息

        Args:
            message: 错误消息
            title: 消息标题
        """
        from tkinter import messagebox

        messagebox.showerror(title, message, parent=self)

    def show_warning(self, message: str, title: str = "警告") -> None:
        """显示警告消息

        Args:
            message: 警告消息
            title: 消息标题
        """
        from tkinter import messagebox

        messagebox.showwarning(title, message, parent=self)

    def show_info(self, message: str, title: str = "信息") -> None:
        """显示信息消息

        Args:
            message: 信息消息
            title: 消息标题
        """
        from tkinter import messagebox

        messagebox.showinfo(title, message, parent=self)

    def confirm(self, message: str, title: str = "确认") -> bool:
        """显示确认对话框

        Args:
            message: 确认消息
            title: 消息标题

        Returns:
            用户是否确认
        """
        from tkinter import messagebox

        return messagebox.askyesno(title, message, parent=self)


class SimpleDialogMixin:
    """简单对话框混入类

    为对话框提供简单的输入和显示功能.
    """

    def create_label_entry_pair(
        self,
        parent: tk.Widget,
        label_text: str,
        entry_var: Optional[tk.StringVar] = None,
        entry_width: int = 30,
        required: bool = False,
    ) -> Tuple[ttk.Label, ttk.Entry]:
        """创建标签-输入框对

        Args:
            parent: 父容器
            label_text: 标签文本
            entry_var: 输入框变量
            entry_width: 输入框宽度
            required: 是否必填

        Returns:
            (标签, 输入框) 元组
        """
        # 创建框架
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)

        # 创建标签
        label_text_display = f"{label_text} *" if required else label_text
        label = ttk.Label(frame, text=label_text_display)
        label.pack(side=tk.LEFT)

        # 创建输入框
        if entry_var is None:
            entry_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=entry_var, width=entry_width)
        entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        return label, entry

    def create_label_combobox_pair(
        self,
        parent: tk.Widget,
        label_text: str,
        values: List[str],
        combo_var: Optional[tk.StringVar] = None,
        combo_width: int = 30,
        required: bool = False,
    ) -> Tuple[ttk.Label, ttk.Combobox]:
        """创建标签-下拉框对

        Args:
            parent: 父容器
            label_text: 标签文本
            values: 下拉框选项
            combo_var: 下拉框变量
            combo_width: 下拉框宽度
            required: 是否必填

        Returns:
            (标签, 下拉框) 元组
        """
        # 创建框架
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)

        # 创建标签
        label_text_display = f"{label_text} *" if required else label_text
        label = ttk.Label(frame, text=label_text_display)
        label.pack(side=tk.LEFT)

        # 创建下拉框
        if combo_var is None:
            combo_var = tk.StringVar()
        combobox = ttk.Combobox(
            frame,
            textvariable=combo_var,
            values=values,
            width=combo_width,
            state="readonly",
        )
        combobox.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        return label, combobox
