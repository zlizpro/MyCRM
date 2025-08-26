"""TTK高级输入组件.

提供高级输入组件,包括:
- NumberSpinnerTTK: 数字微调器组件
- ColorPickerTTK: 颜色选择组件
- FilePickerTTK: 文件选择组件

作者: MiniCRM开发团队
"""

from abc import abstractmethod
import tkinter as tk
from tkinter import ttk

from .base_widget import BaseWidget, ValidationMixin
from .date_picker_ttk import DatePickerTTK


class AdvancedInputMixin(ValidationMixin):
    """高级输入组件混入类.

    为高级输入组件提供通用功能:
    - 统一的数据访问接口
    - 数据验证和格式化
    - 事件处理和状态管理
    """

    def __init__(self) -> None:
        """初始化高级输入组件混入类."""
        super().__init__()
        self._value: object = None
        self._default_value: object = None
        self._readonly = False

    def get_value(self) -> object:
        """获取组件值.

        Returns:
            组件当前值
        """
        return self._value

    def set_value(self, value: object) -> None:
        """设置组件值.

        Args:
            value: 要设置的值

        Raises:
            ValueError: 当值无效时
        """
        if not self._readonly:
            try:
                old_value = self._value
                self._value = value
                self._update_display()
                self.trigger_event("value_changed", old_value, value)
            except Exception as e:
                error_msg = f"设置值失败: {e}"
                raise ValueError(error_msg) from e

    def clear(self) -> None:
        """清空组件值."""
        self.set_value(self._default_value)

    def set_readonly(self, readonly: bool) -> None:
        """设置只读状态.

        Args:
            readonly: 是否只读
        """
        self._readonly = readonly
        self._update_readonly_state()

    def is_readonly(self) -> bool:
        """检查是否只读.

        Returns:
            是否为只读状态
        """
        return self._readonly

    @abstractmethod
    def _update_display(self) -> None:
        """更新显示 - 子类必须实现."""

    @abstractmethod
    def _update_readonly_state(self) -> None:
        """更新只读状态 - 子类必须实现."""


class NumberSpinnerTTK(BaseWidget, AdvancedInputMixin):
    """数字微调器组件."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        """初始化数字微调器组件.

        Args:
            parent: 父组件
            **kwargs: 其他参数
        """
        AdvancedInputMixin.__init__(self)
        self._default_value = 0
        self._value = 0
        super().__init__(parent, **kwargs)

    def _setup_ui(self) -> None:
        """设置UI布局."""
        self.spinbox = ttk.Spinbox(self)
        self.spinbox.pack(fill=tk.BOTH, expand=True)

    def _update_display(self) -> None:
        """更新显示."""
        if hasattr(self, "spinbox"):
            self.spinbox.set(str(self._value))

    def _update_readonly_state(self) -> None:
        """更新只读状态."""
        if hasattr(self, "spinbox"):
            state = "readonly" if self._readonly else "normal"
            self.spinbox.configure(state=state)


class ColorPickerTTK(BaseWidget, AdvancedInputMixin):
    """颜色选择组件."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        """初始化颜色选择组件.

        Args:
            parent: 父组件
            **kwargs: 其他参数
        """
        AdvancedInputMixin.__init__(self)
        self._default_value = "#FFFFFF"
        self._value = "#FFFFFF"
        super().__init__(parent, **kwargs)

    def _setup_ui(self) -> None:
        """设置UI布局."""
        self.color_entry = ttk.Entry(self)
        self.color_entry.pack(fill=tk.BOTH, expand=True)

    def get_rgb_value(self) -> tuple[int, int, int]:
        """获取RGB值.

        Returns:
            RGB颜色值元组
        """
        return (255, 255, 255)

    def _update_display(self) -> None:
        """更新显示."""
        if hasattr(self, "color_entry"):
            self.color_entry.delete(0, tk.END)
            self.color_entry.insert(0, str(self._value))

    def _update_readonly_state(self) -> None:
        """更新只读状态."""
        if hasattr(self, "color_entry"):
            state = "readonly" if self._readonly else "normal"
            self.color_entry.configure(state=state)


class FilePickerTTK(BaseWidget, AdvancedInputMixin):
    """文件选择组件."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        """初始化文件选择组件.

        Args:
            parent: 父组件
            **kwargs: 其他参数
        """
        AdvancedInputMixin.__init__(self)
        self._default_value = ""
        self._value = ""
        super().__init__(parent, **kwargs)

    def _setup_ui(self) -> None:
        """设置UI布局."""
        self.path_entry = ttk.Entry(self)
        self.path_entry.pack(fill=tk.BOTH, expand=True)

    def _update_display(self) -> None:
        """更新显示."""
        if hasattr(self, "path_entry"):
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, str(self._value))

    def _update_readonly_state(self) -> None:
        """更新只读状态."""
        if hasattr(self, "path_entry"):
            state = "readonly" if self._readonly else "normal"
            self.path_entry.configure(state=state)


# 导出所有高级输入组件
__all__ = [
    "AdvancedInputMixin",
    "ColorPickerTTK",
    "DatePickerTTK",
    "FilePickerTTK",
    "NumberSpinnerTTK",
]
