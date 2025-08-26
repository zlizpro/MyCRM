"""TTK消息对话框集合

提供各种消息对话框功能,包括:
- MessageBoxTTK - 消息显示对话框
- ConfirmDialogTTK - 确认对话框
- InputDialogTTK - 输入对话框
- 支持不同的消息类型和图标
- 提供标准的用户交互模式

设计目标:
1. 提供统一的消息对话框接口
2. 支持多种消息类型和样式
3. 确保用户体验的一致性
4. 简化对话框的使用

作者: MiniCRM开发团队
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, List, Optional, Union

from .base_dialog import BaseDialogTTK, DialogResult


class MessageType:
    """消息类型枚举"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    QUESTION = "question"
    SUCCESS = "success"


class MessageBoxTTK(BaseDialogTTK):
    """TTK消息对话框

    显示各种类型的消息,支持信息、警告、错误等不同样式.
    """

    def __init__(
        self,
        parent: Optional[tk.Widget] = None,
        title: str = "消息",
        message: str = "",
        message_type: str = MessageType.INFO,
        detail: Optional[str] = None,
        buttons: Optional[List[str]] = None,
        default_button: Optional[str] = None,
        **kwargs,
    ):
        """初始化消息对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            message: 主要消息内容
            message_type: 消息类型
            detail: 详细信息
            buttons: 自定义按钮列表
            default_button: 默认按钮
            **kwargs: 其他参数
        """
        self.message = message
        self.message_type = message_type
        self.detail = detail
        self.custom_buttons = buttons
        self.default_button = default_button

        # 消息组件
        self.icon_label: Optional[ttk.Label] = None
        self.message_label: Optional[ttk.Label] = None
        self.detail_text: Optional[tk.Text] = None

        # 根据消息类型设置默认标题
        if title == "消息":
            title = self._get_default_title()

        # 设置对话框大小
        kwargs.setdefault("size", (400, 200))
        kwargs.setdefault("resizable", (False, False))

        super().__init__(parent, title, **kwargs)

    def _get_default_title(self) -> str:
        """获取默认标题"""
        titles = {
            MessageType.INFO: "信息",
            MessageType.WARNING: "警告",
            MessageType.ERROR: "错误",
            MessageType.QUESTION: "确认",
            MessageType.SUCCESS: "成功",
        }
        return titles.get(self.message_type, "消息")

    def _setup_content(self) -> None:
        """设置对话框内容"""
        # 创建主内容框架
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建图标和消息框架
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 创建图标
        self._create_icon(content_frame)

        # 创建消息内容框架
        message_frame = ttk.Frame(content_frame)
        message_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # 创建主消息标签
        self.message_label = ttk.Label(
            message_frame,
            text=self.message,
            font=("Microsoft YaHei UI", 9),
            wraplength=300,
            justify=tk.LEFT,
        )
        self.message_label.pack(anchor=tk.W, pady=(0, 10))

        # 创建详细信息(如果有)
        if self.detail:
            self._create_detail_text(message_frame)

    def _create_icon(self, parent: tk.Widget) -> None:
        """创建消息图标"""
        # 根据消息类型选择图标
        icons = {
            MessageType.INFO: "ℹ️",
            MessageType.WARNING: "⚠️",
            MessageType.ERROR: "❌",
            MessageType.QUESTION: "❓",
            MessageType.SUCCESS: "✅",
        }

        icon_text = icons.get(self.message_type, "ℹ️")

        self.icon_label = ttk.Label(parent, text=icon_text, font=("Segoe UI Emoji", 24))
        self.icon_label.pack(side=tk.LEFT, padx=(0, 10), pady=(0, 10))

    def _create_detail_text(self, parent: tk.Widget) -> None:
        """创建详细信息文本框"""
        # 创建详细信息框架
        detail_frame = ttk.LabelFrame(parent, text="详细信息")
        detail_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        # 创建文本框和滚动条
        text_frame = ttk.Frame(detail_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.detail_text = tk.Text(
            text_frame, height=6, wrap=tk.WORD, font=("Consolas", 8), state=tk.DISABLED
        )

        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.detail_text.yview
        )
        self.detail_text.configure(yscrollcommand=scrollbar.set)

        # 插入详细信息
        self.detail_text.configure(state=tk.NORMAL)
        self.detail_text.insert(tk.END, self.detail)
        self.detail_text.configure(state=tk.DISABLED)

        # 布局
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _setup_buttons(self) -> None:
        """设置对话框按钮"""
        if self.custom_buttons:
            # 使用自定义按钮
            for i, button_text in enumerate(reversed(self.custom_buttons)):
                is_default = button_text == self.default_button
                result = button_text.lower()
                self.add_button(
                    button_text,
                    lambda r=result: self._on_button_click(r),
                    result,
                    is_default,
                )
        # 使用默认按钮
        elif self.message_type == MessageType.QUESTION:
            self.add_button(
                "否", lambda: self._on_button_click(DialogResult.NO), DialogResult.NO
            )
            self.add_button(
                "是",
                lambda: self._on_button_click(DialogResult.YES),
                DialogResult.YES,
                True,
            )
        else:
            self.add_button(
                "确定",
                lambda: self._on_button_click(DialogResult.OK),
                DialogResult.OK,
                True,
            )

    def _on_button_click(self, result: str) -> None:
        """按钮点击处理"""
        self.result = result
        self.return_value = result
        self._close_dialog()

    def _validate_input(self) -> bool:
        """验证输入(消息对话框不需要验证)"""
        return True

    def _get_result_data(self) -> Any:
        """获取结果数据"""
        return self.result


class ConfirmDialogTTK(BaseDialogTTK):
    """TTK确认对话框

    显示确认消息,提供是/否或确定/取消选择.
    """

    def __init__(
        self,
        parent: Optional[tk.Widget] = None,
        title: str = "确认",
        message: str = "确定要执行此操作吗?",
        confirm_text: str = "确定",
        cancel_text: str = "取消",
        icon_type: str = MessageType.QUESTION,
        **kwargs,
    ):
        """初始化确认对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            message: 确认消息
            confirm_text: 确认按钮文本
            cancel_text: 取消按钮文本
            icon_type: 图标类型
            **kwargs: 其他参数
        """
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.icon_type = icon_type

        # 消息组件
        self.icon_label: Optional[ttk.Label] = None
        self.message_label: Optional[ttk.Label] = None

        # 设置对话框大小
        kwargs.setdefault("size", (350, 150))
        kwargs.setdefault("resizable", (False, False))

        super().__init__(parent, title, **kwargs)

    def _setup_content(self) -> None:
        """设置对话框内容"""
        # 创建主内容框架
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 创建图标
        icons = {
            MessageType.INFO: "ℹ️",
            MessageType.WARNING: "⚠️",
            MessageType.ERROR: "❌",
            MessageType.QUESTION: "❓",
            MessageType.SUCCESS: "✅",
        }

        icon_text = icons.get(self.icon_type, "❓")

        self.icon_label = ttk.Label(
            main_frame, text=icon_text, font=("Segoe UI Emoji", 20)
        )
        self.icon_label.pack(side=tk.LEFT, padx=(0, 15))

        # 创建消息标签
        self.message_label = ttk.Label(
            main_frame,
            text=self.message,
            font=("Microsoft YaHei UI", 9),
            wraplength=250,
            justify=tk.LEFT,
        )
        self.message_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _setup_buttons(self) -> None:
        """设置对话框按钮"""
        self.add_button(self.cancel_text, self._on_cancel_confirm, DialogResult.CANCEL)
        self.add_button(self.confirm_text, self._on_confirm, DialogResult.OK, True)

    def _on_confirm(self) -> None:
        """确认处理"""
        self.result = DialogResult.OK
        self.return_value = True
        self._close_dialog()

    def _on_cancel_confirm(self) -> None:
        """取消处理"""
        self.result = DialogResult.CANCEL
        self.return_value = False
        self._close_dialog()

    def _validate_input(self) -> bool:
        """验证输入(确认对话框不需要验证)"""
        return True

    def _get_result_data(self) -> Any:
        """获取结果数据"""
        return self.return_value


class InputDialogTTK(BaseDialogTTK):
    """TTK输入对话框

    提供用户输入功能,支持单行和多行输入.
    """

    def __init__(
        self,
        parent: Optional[tk.Widget] = None,
        title: str = "输入",
        message: str = "请输入:",
        initial_value: str = "",
        multiline: bool = False,
        password: bool = False,
        validation_func: Optional[callable] = None,
        **kwargs,
    ):
        """初始化输入对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            message: 输入提示消息
            initial_value: 初始值
            multiline: 是否多行输入
            password: 是否密码输入
            validation_func: 验证函数
            **kwargs: 其他参数
        """
        self.message = message
        self.initial_value = initial_value
        self.multiline = multiline
        self.password = password
        self.validation_func = validation_func

        # 输入组件
        self.message_label: Optional[ttk.Label] = None
        self.input_var = tk.StringVar(value=initial_value)
        self.input_widget: Optional[Union[ttk.Entry, tk.Text]] = None

        # 设置对话框大小
        if multiline:
            kwargs.setdefault("size", (400, 300))
        else:
            kwargs.setdefault("size", (350, 150))
        kwargs.setdefault("resizable", (True, multiline))

        super().__init__(parent, title, **kwargs)

        # 设置焦点到输入框
        if self.input_widget:
            self.input_widget.focus_set()

    def _setup_content(self) -> None:
        """设置对话框内容"""
        # 创建消息标签
        self.message_label = ttk.Label(
            self.content_frame, text=self.message, font=("Microsoft YaHei UI", 9)
        )
        self.message_label.pack(anchor=tk.W, pady=(0, 10))

        # 创建输入组件
        if self.multiline:
            self._create_multiline_input()
        else:
            self._create_single_line_input()

    def _create_single_line_input(self) -> None:
        """创建单行输入框"""
        show_char = "*" if self.password else None

        self.input_widget = ttk.Entry(
            self.content_frame,
            textvariable=self.input_var,
            font=("Microsoft YaHei UI", 9),
            show=show_char,
        )
        self.input_widget.pack(fill=tk.X, pady=(0, 10))

        # 绑定回车键
        self.input_widget.bind("<Return>", lambda e: self._on_ok())

        # 选中初始文本
        if self.initial_value:
            self.input_widget.select_range(0, tk.END)

    def _create_multiline_input(self) -> None:
        """创建多行输入框"""
        # 创建文本框框架
        text_frame = ttk.Frame(self.content_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 创建文本框
        self.input_widget = tk.Text(
            text_frame, font=("Microsoft YaHei UI", 9), wrap=tk.WORD, height=8
        )

        # 创建滚动条
        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.input_widget.yview
        )
        self.input_widget.configure(yscrollcommand=scrollbar.set)

        # 插入初始值
        if self.initial_value:
            self.input_widget.insert(tk.END, self.initial_value)

        # 布局
        self.input_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定Ctrl+Enter提交
        self.input_widget.bind("<Control-Return>", lambda e: self._on_ok())

    def _setup_buttons(self) -> None:
        """设置对话框按钮"""
        self.add_button("取消", self._on_cancel, DialogResult.CANCEL)
        self.add_button("确定", self._on_ok, DialogResult.OK, True)

    def _validate_input(self) -> bool:
        """验证输入"""
        value = self.get_input_value()

        # 检查是否为空
        if not value.strip():
            self.show_error("输入不能为空")
            return False

        # 自定义验证
        if self.validation_func:
            try:
                if not self.validation_func(value):
                    self.show_error("输入格式不正确")
                    return False
            except Exception as e:
                self.show_error(f"验证失败: {e}")
                return False

        return True

    def get_input_value(self) -> str:
        """获取输入值"""
        if self.multiline and isinstance(self.input_widget, tk.Text):
            return self.input_widget.get("1.0", tk.END).rstrip("\n")
        return self.input_var.get()

    def set_input_value(self, value: str) -> None:
        """设置输入值"""
        if self.multiline and isinstance(self.input_widget, tk.Text):
            self.input_widget.delete("1.0", tk.END)
            self.input_widget.insert("1.0", value)
        else:
            self.input_var.set(value)

    def _get_result_data(self) -> Any:
        """获取结果数据"""
        return self.get_input_value()


# 便利函数
def show_message(
    parent: Optional[tk.Widget] = None,
    title: str = "消息",
    message: str = "",
    message_type: str = MessageType.INFO,
    detail: Optional[str] = None,
) -> str:
    """显示消息对话框

    Args:
        parent: 父窗口
        title: 对话框标题
        message: 消息内容
        message_type: 消息类型
        detail: 详细信息

    Returns:
        用户选择的结果
    """
    dialog = MessageBoxTTK(
        parent=parent,
        title=title,
        message=message,
        message_type=message_type,
        detail=detail,
    )

    result, data = dialog.show_dialog()
    return data


def show_info(
    parent: Optional[tk.Widget] = None, message: str = "", title: str = "信息"
) -> str:
    """显示信息消息"""
    return show_message(parent, title, message, MessageType.INFO)


def show_warning(
    parent: Optional[tk.Widget] = None, message: str = "", title: str = "警告"
) -> str:
    """显示警告消息"""
    return show_message(parent, title, message, MessageType.WARNING)


def show_error(
    parent: Optional[tk.Widget] = None, message: str = "", title: str = "错误"
) -> str:
    """显示错误消息"""
    return show_message(parent, title, message, MessageType.ERROR)


def show_success(
    parent: Optional[tk.Widget] = None, message: str = "", title: str = "成功"
) -> str:
    """显示成功消息"""
    return show_message(parent, title, message, MessageType.SUCCESS)


def confirm(
    parent: Optional[tk.Widget] = None,
    message: str = "确定要执行此操作吗?",
    title: str = "确认",
    confirm_text: str = "确定",
    cancel_text: str = "取消",
) -> bool:
    """显示确认对话框

    Args:
        parent: 父窗口
        message: 确认消息
        title: 对话框标题
        confirm_text: 确认按钮文本
        cancel_text: 取消按钮文本

    Returns:
        用户是否确认
    """
    dialog = ConfirmDialogTTK(
        parent=parent,
        title=title,
        message=message,
        confirm_text=confirm_text,
        cancel_text=cancel_text,
    )

    result, data = dialog.show_dialog()
    return data if result == DialogResult.OK else False


def get_input(
    parent: Optional[tk.Widget] = None,
    title: str = "输入",
    message: str = "请输入:",
    initial_value: str = "",
    multiline: bool = False,
    password: bool = False,
    validation_func: Optional[callable] = None,
) -> Optional[str]:
    """显示输入对话框

    Args:
        parent: 父窗口
        title: 对话框标题
        message: 输入提示
        initial_value: 初始值
        multiline: 是否多行输入
        password: 是否密码输入
        validation_func: 验证函数

    Returns:
        用户输入的内容,取消则返回None
    """
    dialog = InputDialogTTK(
        parent=parent,
        title=title,
        message=message,
        initial_value=initial_value,
        multiline=multiline,
        password=password,
        validation_func=validation_func,
    )

    result, data = dialog.show_dialog()
    return data if result == DialogResult.OK else None


def get_password(
    parent: Optional[tk.Widget] = None,
    title: str = "输入密码",
    message: str = "请输入密码:",
    validation_func: Optional[callable] = None,
) -> Optional[str]:
    """显示密码输入对话框

    Args:
        parent: 父窗口
        title: 对话框标题
        message: 输入提示
        validation_func: 验证函数

    Returns:
        用户输入的密码,取消则返回None
    """
    return get_input(
        parent=parent,
        title=title,
        message=message,
        password=True,
        validation_func=validation_func,
    )


def get_multiline_input(
    parent: Optional[tk.Widget] = None,
    title: str = "输入",
    message: str = "请输入:",
    initial_value: str = "",
    validation_func: Optional[callable] = None,
) -> Optional[str]:
    """显示多行输入对话框

    Args:
        parent: 父窗口
        title: 对话框标题
        message: 输入提示
        initial_value: 初始值
        validation_func: 验证函数

    Returns:
        用户输入的内容,取消则返回None
    """
    return get_input(
        parent=parent,
        title=title,
        message=message,
        initial_value=initial_value,
        multiline=True,
        validation_func=validation_func,
    )
