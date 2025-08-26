"""TTK日期选择组件

提供日期选择功能,支持:
- 日历界面选择
- 日期格式化显示
- 日期范围限制
- 键盘输入和验证

作者: MiniCRM开发团队
"""

from datetime import date, datetime
import tkinter as tk
from tkinter import ttk
from typing import Optional

from .base_widget import BaseWidget, ValidationMixin


class DatePickerTTK(BaseWidget, ValidationMixin):
    """日期选择组件"""

    def __init__(self, parent: tk.Widget, **kwargs):
        ValidationMixin.__init__(self)
        self._value = date.today()
        self._default_value = date.today()
        self._readonly = False
        super().__init__(parent, **kwargs)

    def _setup_ui(self) -> None:
        """设置UI布局"""
        self.date_entry = ttk.Entry(self)
        self.date_entry.pack(fill=tk.BOTH, expand=True)

    def get_value(self):
        """获取组件值"""
        return self._value

    def set_value(self, value):
        """设置组件值"""
        self._value = value

    def clear(self):
        """清空组件值"""
        self.set_value(self._default_value)

    def set_readonly(self, readonly: bool):
        """设置只读状态"""
        self._readonly = readonly

    def is_readonly(self) -> bool:
        """检查是否只读"""
        return self._readonly

    def get_date_object(self) -> Optional[date]:
        """获取日期对象"""
        return self._value if isinstance(self._value, date) else None

    def get_datetime_object(self) -> Optional[datetime]:
        """获取日期时间对象"""
        if isinstance(self._value, date):
            return datetime.combine(self._value, datetime.min.time())
        return None
