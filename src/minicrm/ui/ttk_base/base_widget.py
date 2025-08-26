"""TTK基础组件类

提供所有TTK自定义组件的基础类,包含:
- 统一的组件生命周期管理
- 事件处理机制集成
- 样式管理集成
- 数据绑定基础接口
- 组件间通信机制

设计目标:
1. 为所有自定义组件提供统一的基础功能
2. 简化组件开发和维护
3. 确保组件的一致性和可复用性
4. 提供良好的扩展性

作者: MiniCRM开发团队
"""

from abc import ABC, abstractmethod
import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional


class BaseWidget(ttk.Frame, ABC):
    """TTK基础组件类

    所有自定义TTK组件的基类,提供统一的生命周期管理、
    事件处理、样式管理等基础功能.
    """

    def __init__(self, parent: tk.Widget, **kwargs):
        """初始化基础组件

        Args:
            parent: 父容器组件
            **kwargs: 其他参数
        """
        super().__init__(parent, **kwargs)

        self.parent = parent
        self.logger = logging.getLogger(self.__class__.__name__)

        # 组件状态管理
        self._initialized = False
        self._visible = True
        self._enabled = True
        self._data = {}

        # 事件处理器存储
        self._event_handlers: Dict[str, List[Callable]] = {}

        # 子组件存储
        self._child_widgets: List[tk.Widget] = []

        # 数据绑定存储
        self._data_bindings: Dict[str, Any] = {}

        # 执行初始化流程
        self._initialize()

    def _initialize(self) -> None:
        """组件初始化流程

        按顺序执行:UI设置 -> 事件绑定 -> 样式应用 -> 数据初始化
        """
        try:
            self._setup_ui()
            self._bind_events()
            self._apply_styles()
            self._initialize_data()
            self._initialized = True
            self.logger.debug(f"{self.__class__.__name__} 初始化完成")
        except Exception as e:
            self.logger.error(f"{self.__class__.__name__} 初始化失败: {e}")
            raise

    @abstractmethod
    def _setup_ui(self) -> None:
        """设置UI布局

        子类必须实现此方法来创建具体的UI界面.
        在此方法中应该创建所有子组件并设置布局.
        """

    def _bind_events(self) -> None:
        """绑定事件处理

        子类可以重写此方法来绑定特定的事件处理器.
        默认实现为空,子类根据需要添加事件绑定.
        """

    def _apply_styles(self) -> None:
        """应用样式

        子类可以重写此方法来应用特定的样式.
        默认实现为空,子类根据需要添加样式设置.
        """

    def _initialize_data(self) -> None:
        """初始化数据

        子类可以重写此方法来初始化组件数据.
        默认实现为空,子类根据需要添加数据初始化.
        """

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
            handler: 要移除的事件处理函数
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

    def add_child_widget(self, widget: tk.Widget) -> None:
        """添加子组件

        Args:
            widget: 子组件
        """
        self._child_widgets.append(widget)

    def remove_child_widget(self, widget: tk.Widget) -> None:
        """移除子组件

        Args:
            widget: 要移除的子组件
        """
        if widget in self._child_widgets:
            self._child_widgets.remove(widget)
            if hasattr(widget, "destroy"):
                widget.destroy()

    def get_child_widgets(self) -> List[tk.Widget]:
        """获取所有子组件

        Returns:
            子组件列表
        """
        return self._child_widgets.copy()

    def set_data(self, key: str, value: Any) -> None:
        """设置组件数据

        Args:
            key: 数据键
            value: 数据值
        """
        old_value = self._data.get(key)
        self._data[key] = value

        # 触发数据变化事件
        self.trigger_event("data_changed", key, old_value, value)

    def get_data(self, key: str, default: Any = None) -> Any:
        """获取组件数据

        Args:
            key: 数据键
            default: 默认值

        Returns:
            数据值
        """
        return self._data.get(key, default)

    def get_all_data(self) -> Dict[str, Any]:
        """获取所有组件数据

        Returns:
            数据字典
        """
        return self._data.copy()

    def clear_data(self) -> None:
        """清空组件数据"""
        old_data = self._data.copy()
        self._data.clear()
        self.trigger_event("data_cleared", old_data)

    def bind_data(
        self,
        key: str,
        widget: tk.Widget,
        getter: Optional[Callable] = None,
        setter: Optional[Callable] = None,
    ) -> None:
        """绑定数据到组件

        Args:
            key: 数据键
            widget: 目标组件
            getter: 获取组件值的函数
            setter: 设置组件值的函数
        """
        self._data_bindings[key] = {
            "widget": widget,
            "getter": getter or self._default_getter,
            "setter": setter or self._default_setter,
        }

    def _default_getter(self, widget: tk.Widget) -> Any:
        """默认的组件值获取器

        Args:
            widget: 组件对象

        Returns:
            组件的值
        """
        if hasattr(widget, "get"):
            return widget.get()
        if hasattr(widget, "cget"):
            return widget.cget("text")
        return None

    def _default_setter(self, widget: tk.Widget, value: Any) -> None:
        """默认的组件值设置器

        Args:
            widget: 组件对象
            value: 要设置的值
        """
        if hasattr(widget, "set"):
            widget.set(value)
        elif hasattr(widget, "delete") and hasattr(widget, "insert"):
            widget.delete(0, tk.END)
            widget.insert(0, str(value))
        elif hasattr(widget, "config"):
            widget.config(text=str(value))

    def sync_data_to_widgets(self) -> None:
        """将数据同步到绑定的组件"""
        for key, binding in self._data_bindings.items():
            if key in self._data:
                value = self._data[key]
                widget = binding["widget"]
                setter = binding["setter"]
                try:
                    setter(widget, value)
                except Exception as e:
                    self.logger.error(f"数据同步到组件失败 [{key}]: {e}")

    def sync_widgets_to_data(self) -> None:
        """将绑定组件的值同步到数据"""
        for key, binding in self._data_bindings.items():
            widget = binding["widget"]
            getter = binding["getter"]
            try:
                value = getter(widget)
                self._data[key] = value
            except Exception as e:
                self.logger.error(f"组件值同步到数据失败 [{key}]: {e}")

    def set_visible(self, visible: bool) -> None:
        """设置组件可见性

        Args:
            visible: 是否可见
        """
        self._visible = visible
        if visible:
            self.pack()
        else:
            self.pack_forget()

        self.trigger_event("visibility_changed", visible)

    def is_visible(self) -> bool:
        """检查组件是否可见

        Returns:
            是否可见
        """
        return self._visible

    def set_enabled(self, enabled: bool) -> None:
        """设置组件启用状态

        Args:
            enabled: 是否启用
        """
        self._enabled = enabled
        state = "normal" if enabled else "disabled"

        # 设置自身状态
        try:
            self.config(state=state)
        except tk.TclError:
            pass  # 某些组件可能不支持state属性

        # 设置子组件状态
        for child in self._child_widgets:
            try:
                if hasattr(child, "config"):
                    child.config(state=state)
            except tk.TclError:
                pass

        self.trigger_event("enabled_changed", enabled)

    def is_enabled(self) -> bool:
        """检查组件是否启用

        Returns:
            是否启用
        """
        return self._enabled

    def refresh(self) -> None:
        """刷新组件

        重新同步数据并更新显示.子类可以重写此方法
        来实现特定的刷新逻辑.
        """
        try:
            self.sync_data_to_widgets()
            self.update_idletasks()
            self.trigger_event("refreshed")
        except Exception as e:
            self.logger.error(f"组件刷新失败: {e}")

    def validate(self) -> tuple[bool, List[str]]:
        """验证组件数据

        子类可以重写此方法来实现特定的验证逻辑.

        Returns:
            (是否有效, 错误信息列表) 元组
        """
        return True, []

    def cleanup(self) -> None:
        """清理组件资源

        在组件销毁前调用,用于清理资源、解绑事件等.
        子类可以重写此方法来实现特定的清理逻辑.
        """
        try:
            # 清理事件处理器
            self._event_handlers.clear()

            # 清理子组件
            for child in self._child_widgets:
                if hasattr(child, "cleanup"):
                    child.cleanup()
                elif hasattr(child, "destroy"):
                    child.destroy()
            self._child_widgets.clear()

            # 清理数据绑定
            self._data_bindings.clear()

            # 清理数据
            self._data.clear()

            self.logger.debug(f"{self.__class__.__name__} 清理完成")

        except Exception as e:
            self.logger.error(f"组件清理失败: {e}")

    def __del__(self):
        """析构函数,确保资源被清理"""
        try:
            self.cleanup()
        except:
            pass  # 忽略析构时的异常


class DataBindingMixin:
    """数据绑定混入类

    为组件提供高级数据绑定功能,包括双向绑定、
    数据验证、格式化等功能.
    """

    def __init__(self):
        self._binding_validators: Dict[str, Callable] = {}
        self._binding_formatters: Dict[str, Callable] = {}
        self._auto_sync = False

    def set_binding_validator(self, key: str, validator: Callable[[Any], bool]) -> None:
        """设置数据绑定验证器

        Args:
            key: 数据键
            validator: 验证函数,返回True表示有效
        """
        self._binding_validators[key] = validator

    def set_binding_formatter(self, key: str, formatter: Callable[[Any], str]) -> None:
        """设置数据绑定格式化器

        Args:
            key: 数据键
            formatter: 格式化函数
        """
        self._binding_formatters[key] = formatter

    def enable_auto_sync(self, enabled: bool = True) -> None:
        """启用自动数据同步

        Args:
            enabled: 是否启用自动同步
        """
        self._auto_sync = enabled

    def validate_binding_data(self, key: str, value: Any) -> bool:
        """验证绑定数据

        Args:
            key: 数据键
            value: 数据值

        Returns:
            是否有效
        """
        if key in self._binding_validators:
            validator = self._binding_validators[key]
            try:
                return validator(value)
            except Exception as e:
                logging.getLogger(__name__).error(f"数据验证失败 [{key}]: {e}")
                return False
        return True

    def format_binding_data(self, key: str, value: Any) -> str:
        """格式化绑定数据

        Args:
            key: 数据键
            value: 数据值

        Returns:
            格式化后的字符串
        """
        if key in self._binding_formatters:
            formatter = self._binding_formatters[key]
            try:
                return formatter(value)
            except Exception as e:
                logging.getLogger(__name__).error(f"数据格式化失败 [{key}]: {e}")
                return str(value)
        return str(value)


class ResponsiveMixin:
    """响应式混入类

    为组件提供响应式布局功能,能够根据容器大小
    自动调整布局和显示方式.
    """

    def __init__(self):
        self._breakpoints: Dict[int, Callable] = {}
        self._current_breakpoint: Optional[int] = None

    def add_breakpoint(self, width: int, layout_func: Callable) -> None:
        """添加响应式断点

        Args:
            width: 宽度阈值
            layout_func: 布局函数
        """
        self._breakpoints[width] = layout_func

    def handle_resize(self, width: int, height: int) -> None:
        """处理大小变化

        Args:
            width: 新宽度
            height: 新高度
        """
        # 找到合适的断点
        suitable_breakpoint = None
        for breakpoint_width in sorted(self._breakpoints.keys(), reverse=True):
            if width >= breakpoint_width:
                suitable_breakpoint = breakpoint_width
                break

        # 如果断点发生变化,应用新布局
        if suitable_breakpoint != self._current_breakpoint:
            self._current_breakpoint = suitable_breakpoint
            if suitable_breakpoint is not None:
                layout_func = self._breakpoints[suitable_breakpoint]
                try:
                    layout_func(width, height)
                except Exception as e:
                    logging.getLogger(__name__).error(f"响应式布局应用失败: {e}")


class ValidationMixin:
    """验证混入类

    为组件提供数据验证功能,支持多种验证规则
    和自定义验证器.
    """

    def __init__(self):
        self._validators: Dict[str, List[Callable]] = {}
        self._validation_messages: Dict[str, str] = {}

    def add_validator(
        self, field: str, validator: Callable[[Any], bool], message: str = "验证失败"
    ) -> None:
        """添加验证器

        Args:
            field: 字段名
            validator: 验证函数
            message: 验证失败消息
        """
        if field not in self._validators:
            self._validators[field] = []
        self._validators[field].append(validator)
        self._validation_messages[f"{field}_{len(self._validators[field])}"] = message

    def validate_field(self, field: str, value: Any) -> tuple[bool, List[str]]:
        """验证单个字段

        Args:
            field: 字段名
            value: 字段值

        Returns:
            (是否有效, 错误消息列表) 元组
        """
        if field not in self._validators:
            return True, []

        errors = []
        for i, validator in enumerate(self._validators[field]):
            try:
                if not validator(value):
                    message_key = f"{field}_{i + 1}"
                    message = self._validation_messages.get(message_key, "验证失败")
                    errors.append(message)
            except Exception as e:
                errors.append(f"验证器执行失败: {e}")

        return len(errors) == 0, errors

    def validate_all_fields(
        self, data: Dict[str, Any]
    ) -> tuple[bool, Dict[str, List[str]]]:
        """验证所有字段

        Args:
            data: 数据字典

        Returns:
            (是否全部有效, 字段错误字典) 元组
        """
        all_valid = True
        field_errors = {}

        for field, value in data.items():
            is_valid, errors = self.validate_field(field, value)
            if not is_valid:
                all_valid = False
                field_errors[field] = errors

        return all_valid, field_errors
