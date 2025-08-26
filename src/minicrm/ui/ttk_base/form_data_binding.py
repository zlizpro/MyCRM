"""TTK表单数据绑定系统

提供表单数据绑定功能,包括:
- DataBinding: 双向数据绑定类
- 数据格式化和转换功能
- 表单数据的自动同步和验证
- 数据变化监听和通知

设计目标:
1. 提供简单易用的数据绑定API
2. 支持双向数据同步
3. 提供数据格式化和验证功能
4. 支持数据变化监听

作者: MiniCRM开发团队
"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional


class DataBinding:
    """数据绑定类

    提供双向数据绑定功能,支持:
    - 数据到组件的绑定
    - 组件到数据的绑定
    - 数据格式化和转换
    - 数据验证
    - 变化监听
    """

    def __init__(self):
        """初始化数据绑定"""
        self.logger = logging.getLogger(__name__)

        # 数据存储
        self._data: Dict[str, Any] = {}

        # 绑定信息存储
        self._bindings: Dict[str, Dict[str, Any]] = {}

        # 格式化器存储
        self._formatters: Dict[str, Callable[[Any], str]] = {}

        # 解析器存储
        self._parsers: Dict[str, Callable[[str], Any]] = {}

        # 验证器存储
        self._validators: Dict[str, Callable[[Any], bool]] = {}

        # 变化监听器存储
        self._listeners: Dict[str, List[Callable[[str, Any, Any], None]]] = {}

        # 自动同步标志
        self._auto_sync = False

    def bind(
        self,
        key: str,
        widget: tk.Widget,
        formatter: Optional[Callable[[Any], str]] = None,
        parser: Optional[Callable[[str], Any]] = None,
        validator: Optional[Callable[[Any], bool]] = None,
        auto_sync: bool = False,
    ) -> None:
        """绑定数据到组件

        Args:
            key: 数据键
            widget: 目标组件
            formatter: 数据格式化器
            parser: 数据解析器
            validator: 数据验证器
            auto_sync: 是否自动同步
        """
        # 存储绑定信息
        self._bindings[key] = {
            "widget": widget,
            "getter": self._get_default_getter(widget),
            "setter": self._get_default_setter(widget),
            "auto_sync": auto_sync,
        }

        # 存储格式化器
        if formatter:
            self._formatters[key] = formatter

        # 存储解析器
        if parser:
            self._parsers[key] = parser

        # 存储验证器
        if validator:
            self._validators[key] = validator

        # 如果启用自动同步,绑定事件
        if auto_sync:
            self._bind_auto_sync_events(key, widget)

        self.logger.debug(f"绑定数据键 {key} 到组件 {widget}")

    def _get_default_getter(self, widget: tk.Widget) -> Callable[[tk.Widget], Any]:
        """获取默认的组件值获取器

        Args:
            widget: 组件对象

        Returns:
            获取器函数
        """
        if isinstance(widget, (ttk.Entry, ttk.Combobox)):
            return lambda w: w.get()
        if isinstance(widget, tk.Text):
            return lambda w: w.get("1.0", tk.END).strip()
        if isinstance(widget, (ttk.Checkbutton, tk.Checkbutton)):
            return (
                lambda w: w.instate(["selected"])
                if hasattr(w, "instate")
                else bool(w.cget("variable").get())
            )
        if isinstance(widget, ttk.Scale) or isinstance(widget, ttk.Spinbox):
            return lambda w: w.get()
        # 尝试通用方法
        if hasattr(widget, "get"):
            return lambda w: w.get()
        if hasattr(widget, "cget"):
            return lambda w: w.cget("text")
        return lambda w: None

    def _get_default_setter(
        self, widget: tk.Widget
    ) -> Callable[[tk.Widget, Any], None]:
        """获取默认的组件值设置器

        Args:
            widget: 组件对象

        Returns:
            设置器函数
        """
        if isinstance(widget, ttk.Entry):

            def entry_setter(w, value):
                w.delete(0, tk.END)
                w.insert(0, str(value) if value is not None else "")

            return entry_setter

        if isinstance(widget, ttk.Combobox):

            def combobox_setter(w, value):
                w.set(str(value) if value is not None else "")

            return combobox_setter

        if isinstance(widget, tk.Text):

            def text_setter(w, value):
                w.delete("1.0", tk.END)
                w.insert("1.0", str(value) if value is not None else "")

            return text_setter

        if isinstance(widget, (ttk.Checkbutton, tk.Checkbutton)):

            def checkbutton_setter(w, value):
                if hasattr(w, "state"):
                    if value:
                        w.state(["selected"])
                    else:
                        w.state(["!selected"])
                elif hasattr(w, "cget") and w.cget("variable"):
                    w.cget("variable").set(bool(value))

            return checkbutton_setter

        if isinstance(widget, ttk.Scale):

            def scale_setter(w, value):
                try:
                    w.set(float(value) if value is not None else 0)
                except (ValueError, TypeError):
                    w.set(0)

            return scale_setter

        if isinstance(widget, ttk.Spinbox):

            def spinbox_setter(w, value):
                w.set(str(value) if value is not None else "")

            return spinbox_setter

        # 尝试通用方法
        if hasattr(widget, "set"):
            return lambda w, v: w.set(str(v) if v is not None else "")
        if hasattr(widget, "config"):
            return lambda w, v: w.config(text=str(v) if v is not None else "")
        return lambda w, v: None

    def _bind_auto_sync_events(self, key: str, widget: tk.Widget) -> None:
        """绑定自动同步事件

        Args:
            key: 数据键
            widget: 组件对象
        """

        def on_change(*args):
            try:
                self.sync_widget_to_data(key)
            except Exception as e:
                self.logger.error(f"自动同步失败 [{key}]: {e}")

        # 根据组件类型绑定不同的事件
        if isinstance(widget, (ttk.Entry, ttk.Combobox, ttk.Spinbox)) or isinstance(
            widget, tk.Text
        ):
            widget.bind("<KeyRelease>", on_change)
            widget.bind("<FocusOut>", on_change)
        elif isinstance(widget, (ttk.Checkbutton, tk.Checkbutton)):
            widget.bind("<Button-1>", lambda e: widget.after(1, on_change))
        elif isinstance(widget, ttk.Scale):
            widget.bind("<ButtonRelease-1>", on_change)
            widget.bind("<B1-Motion>", on_change)

    def set_data(self, key: str, value: Any) -> None:
        """设置数据值

        Args:
            key: 数据键
            value: 数据值
        """
        old_value = self._data.get(key)

        # 验证数据
        if key in self._validators:
            if not self._validators[key](value):
                raise ValueError(f"数据验证失败: {key} = {value}")

        # 设置数据
        self._data[key] = value

        # 触发变化监听器
        self._trigger_listeners(key, old_value, value)

        # 同步到组件
        if key in self._bindings:
            self.sync_data_to_widget(key)

        self.logger.debug(f"设置数据: {key} = {value}")

    def get_data(self, key: str, default: Any = None) -> Any:
        """获取数据值

        Args:
            key: 数据键
            default: 默认值

        Returns:
            数据值
        """
        return self._data.get(key, default)

    def get_all_data(self) -> Dict[str, Any]:
        """获取所有数据

        Returns:
            数据字典
        """
        return self._data.copy()

    def set_all_data(self, data: Dict[str, Any]) -> None:
        """设置所有数据

        Args:
            data: 数据字典
        """
        for key, value in data.items():
            self.set_data(key, value)

    def clear_data(self) -> None:
        """清空所有数据"""
        old_data = self._data.copy()
        self._data.clear()

        # 同步到所有绑定的组件
        for key in self._bindings:
            self.sync_data_to_widget(key)

        # 触发清空事件
        for key, old_value in old_data.items():
            self._trigger_listeners(key, old_value, None)

    def sync_data_to_widget(self, key: str) -> None:
        """将数据同步到组件

        Args:
            key: 数据键
        """
        if key not in self._bindings:
            return

        binding = self._bindings[key]
        widget = binding["widget"]
        setter = binding["setter"]

        try:
            # 获取数据值
            value = self._data.get(key)

            # 格式化数据
            if key in self._formatters and value is not None:
                formatted_value = self._formatters[key](value)
            else:
                formatted_value = value

            # 设置到组件
            setter(widget, formatted_value)

        except Exception as e:
            self.logger.error(f"数据同步到组件失败 [{key}]: {e}")

    def sync_widget_to_data(self, key: str) -> None:
        """将组件值同步到数据

        Args:
            key: 数据键
        """
        if key not in self._bindings:
            return

        binding = self._bindings[key]
        widget = binding["widget"]
        getter = binding["getter"]

        try:
            # 从组件获取值
            raw_value = getter(widget)

            # 解析数据
            if key in self._parsers and raw_value is not None:
                parsed_value = self._parsers[key](raw_value)
            else:
                parsed_value = raw_value

            # 设置数据(会触发验证和监听器)
            self.set_data(key, parsed_value)

        except Exception as e:
            self.logger.error(f"组件值同步到数据失败 [{key}]: {e}")

    def sync_all_data_to_widgets(self) -> None:
        """将所有数据同步到组件"""
        for key in self._bindings:
            self.sync_data_to_widget(key)

    def sync_all_widgets_to_data(self) -> None:
        """将所有组件值同步到数据"""
        for key in self._bindings:
            self.sync_widget_to_data(key)

    def add_listener(self, key: str, listener: Callable[[str, Any, Any], None]) -> None:
        """添加数据变化监听器

        Args:
            key: 数据键
            listener: 监听器函数,接收(key, old_value, new_value)参数
        """
        if key not in self._listeners:
            self._listeners[key] = []
        self._listeners[key].append(listener)

    def remove_listener(
        self, key: str, listener: Callable[[str, Any, Any], None]
    ) -> None:
        """移除数据变化监听器

        Args:
            key: 数据键
            listener: 要移除的监听器函数
        """
        if key in self._listeners:
            try:
                self._listeners[key].remove(listener)
            except ValueError:
                pass

    def _trigger_listeners(self, key: str, old_value: Any, new_value: Any) -> None:
        """触发数据变化监听器

        Args:
            key: 数据键
            old_value: 旧值
            new_value: 新值
        """
        if key in self._listeners:
            for listener in self._listeners[key]:
                try:
                    listener(key, old_value, new_value)
                except Exception as e:
                    self.logger.error(f"监听器执行失败 [{key}]: {e}")

    def validate_all(self) -> tuple[bool, Dict[str, str]]:
        """验证所有数据

        Returns:
            (是否全部有效, 错误信息字典) 元组
        """
        errors = {}

        for key, validator in self._validators.items():
            value = self._data.get(key)
            try:
                if not validator(value):
                    errors[key] = f"数据验证失败: {key}"
            except Exception as e:
                errors[key] = f"验证器执行失败: {e}"

        return len(errors) == 0, errors

    def set_formatter(self, key: str, formatter: Callable[[Any], str]) -> None:
        """设置数据格式化器

        Args:
            key: 数据键
            formatter: 格式化器函数
        """
        self._formatters[key] = formatter

    def set_parser(self, key: str, parser: Callable[[str], Any]) -> None:
        """设置数据解析器

        Args:
            key: 数据键
            parser: 解析器函数
        """
        self._parsers[key] = parser

    def set_validator(self, key: str, validator: Callable[[Any], bool]) -> None:
        """设置数据验证器

        Args:
            key: 数据键
            validator: 验证器函数
        """
        self._validators[key] = validator


class CommonFormatters:
    """常用格式化器"""

    @staticmethod
    def date_formatter(date_format: str = "%Y-%m-%d") -> Callable[[Any], str]:
        """日期格式化器

        Args:
            date_format: 日期格式

        Returns:
            格式化器函数
        """

        def formatter(value):
            from datetime import date, datetime

            if isinstance(value, (date, datetime)):
                return value.strftime(date_format)
            return str(value) if value is not None else ""

        return formatter

    @staticmethod
    def number_formatter(decimal_places: int = 2) -> Callable[[Any], str]:
        """数字格式化器

        Args:
            decimal_places: 小数位数

        Returns:
            格式化器函数
        """

        def formatter(value):
            try:
                if value is None:
                    return ""
                return f"{float(value):.{decimal_places}f}"
            except (ValueError, TypeError):
                return str(value)

        return formatter

    @staticmethod
    def currency_formatter(symbol: str = "¥") -> Callable[[Any], str]:
        """货币格式化器

        Args:
            symbol: 货币符号

        Returns:
            格式化器函数
        """

        def formatter(value):
            try:
                if value is None:
                    return ""
                return f"{symbol}{float(value):.2f}"
            except (ValueError, TypeError):
                return str(value)

        return formatter

    @staticmethod
    def percentage_formatter() -> Callable[[Any], str]:
        """百分比格式化器

        Returns:
            格式化器函数
        """

        def formatter(value):
            try:
                if value is None:
                    return ""
                return f"{float(value) * 100:.1f}%"
            except (ValueError, TypeError):
                return str(value)

        return formatter


class CommonParsers:
    """常用解析器"""

    @staticmethod
    def date_parser(date_format: str = "%Y-%m-%d") -> Callable[[str], Any]:
        """日期解析器

        Args:
            date_format: 日期格式

        Returns:
            解析器函数
        """

        def parser(value):
            if not value or not isinstance(value, str):
                return None
            try:
                from datetime import datetime

                return datetime.strptime(value.strip(), date_format).date()
            except ValueError:
                return None

        return parser

    @staticmethod
    def number_parser() -> Callable[[str], Any]:
        """数字解析器

        Returns:
            解析器函数
        """

        def parser(value):
            if not value or not isinstance(value, str):
                return None
            try:
                # 尝试解析为整数
                if "." not in value:
                    return int(value.strip())
                # 解析为浮点数
                return float(value.strip())
            except ValueError:
                return None

        return parser

    @staticmethod
    def currency_parser() -> Callable[[str], Any]:
        """货币解析器

        Returns:
            解析器函数
        """

        def parser(value):
            if not value or not isinstance(value, str):
                return None
            try:
                # 移除货币符号和空格
                cleaned = value.strip()
                for symbol in ["¥", "$", "€", "£"]:
                    cleaned = cleaned.replace(symbol, "")
                return float(cleaned.strip())
            except ValueError:
                return None

        return parser

    @staticmethod
    def percentage_parser() -> Callable[[str], Any]:
        """百分比解析器

        Returns:
            解析器函数
        """

        def parser(value):
            if not value or not isinstance(value, str):
                return None
            try:
                # 移除百分号
                cleaned = value.strip().replace("%", "")
                return float(cleaned) / 100
            except ValueError:
                return None

        return parser


class CommonValidators:
    """常用验证器"""

    @staticmethod
    def required_validator() -> Callable[[Any], bool]:
        """必填验证器

        Returns:
            验证器函数
        """

        def validator(value):
            if value is None:
                return False
            if isinstance(value, str):
                return len(value.strip()) > 0
            return True

        return validator

    @staticmethod
    def email_validator() -> Callable[[Any], bool]:
        """邮箱验证器

        Returns:
            验证器函数
        """
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        def validator(value):
            if not value:
                return True  # 空值通过验证,由required_validator处理
            if not isinstance(value, str):
                return False
            return re.match(email_pattern, value.strip()) is not None

        return validator

    @staticmethod
    def phone_validator() -> Callable[[Any], bool]:
        """电话号码验证器

        Returns:
            验证器函数
        """
        import re

        phone_pattern = r"^1[3-9]\d{9}$"

        def validator(value):
            if not value:
                return True  # 空值通过验证
            if not isinstance(value, str):
                return False
            return re.match(phone_pattern, value.strip()) is not None

        return validator

    @staticmethod
    def range_validator(min_value: float, max_value: float) -> Callable[[Any], bool]:
        """范围验证器

        Args:
            min_value: 最小值
            max_value: 最大值

        Returns:
            验证器函数
        """

        def validator(value):
            if value is None:
                return True  # 空值通过验证
            try:
                num_value = float(value)
                return min_value <= num_value <= max_value
            except (ValueError, TypeError):
                return False

        return validator


# 导出所有类
__all__ = ["CommonFormatters", "CommonParsers", "CommonValidators", "DataBinding"]
