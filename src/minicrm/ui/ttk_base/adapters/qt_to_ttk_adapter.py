"""Qt到TTK适配器基类

提供Qt组件到TTK组件的适配接口,包括:
- 组件适配基础架构
- 配置映射和转换
- 属性和方法适配
- 生命周期管理

设计目标:
1. 提供统一的适配器接口
2. 简化Qt到TTK的迁移过程
3. 保持组件功能的完整性
4. 支持配置驱动的适配

作者: MiniCRM开发团队
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Type, Union


class ComponentType(Enum):
    """组件类型枚举"""

    WINDOW = "window"
    WIDGET = "widget"
    BUTTON = "button"
    LABEL = "label"
    ENTRY = "entry"
    TEXT = "text"
    COMBOBOX = "combobox"
    LISTBOX = "listbox"
    TREEVIEW = "treeview"
    FRAME = "frame"
    NOTEBOOK = "notebook"
    SCROLLBAR = "scrollbar"
    PROGRESSBAR = "progressbar"
    CHECKBUTTON = "checkbutton"
    RADIOBUTTON = "radiobutton"
    SCALE = "scale"
    SPINBOX = "spinbox"
    MENU = "menu"
    DIALOG = "dialog"


@dataclass
class ComponentMapping:
    """组件映射配置"""

    qt_class: str
    ttk_class: Type
    adapter_class: Optional[Type] = None
    config_mapping: Optional[Dict[str, str]] = None
    method_mapping: Optional[Dict[str, str]] = None
    event_mapping: Optional[Dict[str, str]] = None
    special_handling: Optional[Callable] = None


class QtToTtkAdapter(ABC):
    """Qt到TTK适配器基类

    定义Qt组件到TTK组件适配的基本接口和通用功能.
    """

    def __init__(
        self,
        qt_config: Optional[Dict[str, Any]] = None,
        parent: Optional[tk.Widget] = None,
    ):
        """初始化适配器

        Args:
            qt_config: Qt组件配置
            parent: TTK父组件
        """
        self.qt_config = qt_config or {}
        self.parent = parent
        self.ttk_widget: Optional[tk.Widget] = None
        self.logger = logging.getLogger(self.__class__.__name__)

        # 配置映射表
        self.config_mapping: Dict[str, str] = {}
        self.method_mapping: Dict[str, str] = {}
        self.event_mapping: Dict[str, str] = {}

        # 初始化映射表
        self._initialize_mappings()

        # 创建TTK组件
        self._create_ttk_widget()

        # 应用配置
        self._apply_configuration()

    @abstractmethod
    def _initialize_mappings(self) -> None:
        """初始化映射表(子类实现)"""

    @abstractmethod
    def _create_ttk_widget(self) -> None:
        """创建TTK组件(子类实现)"""

    def _apply_configuration(self) -> None:
        """应用Qt配置到TTK组件"""
        if not self.ttk_widget:
            return

        # 应用几何配置
        self._apply_geometry_config()

        # 应用样式配置
        self._apply_style_config()

        # 应用属性配置
        self._apply_property_config()

        # 应用事件配置
        self._apply_event_config()

    def _apply_geometry_config(self) -> None:
        """应用几何配置"""
        geometry = self.qt_config.get("geometry", {})

        # 位置和大小
        if "x" in geometry and "y" in geometry:
            x, y = geometry["x"], geometry["y"]
            if hasattr(self.ttk_widget, "geometry"):
                current_geometry = self.ttk_widget.geometry()
                if "x" in current_geometry:
                    # 更新位置
                    width = geometry.get("width", 300)
                    height = geometry.get("height", 200)
                    self.ttk_widget.geometry(f"{width}x{height}+{x}+{y}")

        # 最小和最大大小
        if "min_width" in geometry and "min_height" in geometry:
            if hasattr(self.ttk_widget, "minsize"):
                self.ttk_widget.minsize(geometry["min_width"], geometry["min_height"])

        if "max_width" in geometry and "max_height" in geometry:
            if hasattr(self.ttk_widget, "maxsize"):
                self.ttk_widget.maxsize(geometry["max_width"], geometry["max_height"])

    def _apply_style_config(self) -> None:
        """应用样式配置"""
        style_config = self.qt_config.get("style", {})

        for qt_property, value in style_config.items():
            ttk_property = self.config_mapping.get(qt_property, qt_property)

            try:
                if hasattr(self.ttk_widget, "configure"):
                    # 转换属性值
                    converted_value = self._convert_property_value(qt_property, value)
                    self.ttk_widget.configure(**{ttk_property: converted_value})
            except Exception as e:
                self.logger.warning(f"应用样式配置失败 [{qt_property}]: {e}")

    def _apply_property_config(self) -> None:
        """应用属性配置"""
        properties = self.qt_config.get("properties", {})

        for qt_property, value in properties.items():
            ttk_property = self.config_mapping.get(qt_property, qt_property)

            try:
                # 使用setter方法或直接配置
                setter_method = f"set_{ttk_property}"
                if hasattr(self.ttk_widget, setter_method):
                    getattr(self.ttk_widget, setter_method)(value)
                elif hasattr(self.ttk_widget, "configure"):
                    converted_value = self._convert_property_value(qt_property, value)
                    self.ttk_widget.configure(**{ttk_property: converted_value})
            except Exception as e:
                self.logger.warning(f"应用属性配置失败 [{qt_property}]: {e}")

    def _apply_event_config(self) -> None:
        """应用事件配置"""
        events = self.qt_config.get("events", {})

        for qt_event, handler in events.items():
            ttk_event = self.event_mapping.get(qt_event, qt_event)

            try:
                if hasattr(self.ttk_widget, "bind"):
                    # 包装事件处理器
                    wrapped_handler = self._wrap_event_handler(qt_event, handler)
                    self.ttk_widget.bind(ttk_event, wrapped_handler)
            except Exception as e:
                self.logger.warning(f"绑定事件失败 [{qt_event}]: {e}")

    def _convert_property_value(self, property_name: str, value: Any) -> Any:
        """转换属性值

        Args:
            property_name: 属性名称
            value: Qt属性值

        Returns:
            TTK属性值
        """
        # 颜色转换
        if "color" in property_name.lower() or "background" in property_name.lower():
            return self._convert_color(value)

        # 字体转换
        if "font" in property_name.lower():
            return self._convert_font(value)

        # 大小转换
        if (
            "size" in property_name.lower()
            or "width" in property_name.lower()
            or "height" in property_name.lower()
        ):
            return self._convert_size(value)

        # 布尔值转换
        if isinstance(value, bool):
            return value

        # 字符串转换
        if isinstance(value, str):
            return value

        # 数值转换
        if isinstance(value, (int, float)):
            return value

        return value

    def _convert_color(self, color: Any) -> str:
        """转换颜色值

        Args:
            color: Qt颜色值

        Returns:
            TTK颜色字符串
        """
        if isinstance(color, str):
            # 已经是颜色字符串
            if color.startswith("#") or color in [
                "red",
                "green",
                "blue",
                "white",
                "black",
            ]:
                return color

        # Qt颜色对象转换(如果有的话)
        if hasattr(color, "name"):
            return color.name()

        # 默认返回字符串形式
        return str(color)

    def _convert_font(self, font: Any) -> Union[str, tuple]:
        """转换字体值

        Args:
            font: Qt字体值

        Returns:
            TTK字体格式
        """
        if isinstance(font, str):
            return font

        if isinstance(font, tuple):
            return font

        # Qt字体对象转换(如果有的话)
        if hasattr(font, "family") and hasattr(font, "pointSize"):
            family = font.family()
            size = font.pointSize()
            weight = "bold" if hasattr(font, "bold") and font.bold() else "normal"
            slant = "italic" if hasattr(font, "italic") and font.italic() else "roman"
            return (family, size, weight, slant)

        return font

    def _convert_size(self, size: Any) -> int:
        """转换大小值

        Args:
            size: Qt大小值

        Returns:
            TTK大小值
        """
        if isinstance(size, (int, float)):
            return int(size)

        # Qt大小对象转换(如果有的话)
        if hasattr(size, "width") and hasattr(size, "height"):
            return (int(size.width()), int(size.height()))

        return int(size) if size else 0

    def _wrap_event_handler(self, qt_event: str, handler: Callable) -> Callable:
        """包装事件处理器

        Args:
            qt_event: Qt事件名称
            handler: Qt事件处理器

        Returns:
            TTK事件处理器
        """

        def wrapped_handler(event):
            try:
                # 转换事件对象
                converted_event = self._convert_event_object(qt_event, event)
                return handler(converted_event)
            except Exception as e:
                self.logger.error(f"事件处理器执行失败 [{qt_event}]: {e}")

        return wrapped_handler

    def _convert_event_object(self, qt_event: str, tk_event) -> Any:
        """转换事件对象

        Args:
            qt_event: Qt事件名称
            tk_event: Tkinter事件对象

        Returns:
            转换后的事件对象
        """

        # 创建简单的事件对象包装
        class EventWrapper:
            def __init__(self, tk_event):
                self.widget = tk_event.widget
                self.x = getattr(tk_event, "x", 0)
                self.y = getattr(tk_event, "y", 0)
                self.x_root = getattr(tk_event, "x_root", 0)
                self.y_root = getattr(tk_event, "y_root", 0)
                self.key = getattr(tk_event, "keysym", "")
                self.char = getattr(tk_event, "char", "")
                self.state = getattr(tk_event, "state", 0)
                self.delta = getattr(tk_event, "delta", 0)

        return EventWrapper(tk_event)

    def get_ttk_widget(self) -> Optional[tk.Widget]:
        """获取TTK组件

        Returns:
            TTK组件对象
        """
        return self.ttk_widget

    def set_property(self, property_name: str, value: Any) -> None:
        """设置属性

        Args:
            property_name: 属性名称
            value: 属性值
        """
        if not self.ttk_widget:
            return

        ttk_property = self.config_mapping.get(property_name, property_name)
        converted_value = self._convert_property_value(property_name, value)

        try:
            if hasattr(self.ttk_widget, "configure"):
                self.ttk_widget.configure(**{ttk_property: converted_value})
        except Exception as e:
            self.logger.warning(f"设置属性失败 [{property_name}]: {e}")

    def get_property(self, property_name: str) -> Any:
        """获取属性

        Args:
            property_name: 属性名称

        Returns:
            属性值
        """
        if not self.ttk_widget:
            return None

        ttk_property = self.config_mapping.get(property_name, property_name)

        try:
            if hasattr(self.ttk_widget, "cget"):
                return self.ttk_widget.cget(ttk_property)
            if hasattr(self.ttk_widget, ttk_property):
                return getattr(self.ttk_widget, ttk_property)
        except Exception as e:
            self.logger.warning(f"获取属性失败 [{property_name}]: {e}")

        return None

    def call_method(self, method_name: str, *args, **kwargs) -> Any:
        """调用方法

        Args:
            method_name: 方法名称
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            方法返回值
        """
        if not self.ttk_widget:
            return None

        ttk_method = self.method_mapping.get(method_name, method_name)

        try:
            if hasattr(self.ttk_widget, ttk_method):
                method = getattr(self.ttk_widget, ttk_method)
                return method(*args, **kwargs)
        except Exception as e:
            self.logger.warning(f"调用方法失败 [{method_name}]: {e}")

        return None

    def bind_event(self, event_name: str, handler: Callable) -> None:
        """绑定事件

        Args:
            event_name: 事件名称
            handler: 事件处理器
        """
        if not self.ttk_widget:
            return

        ttk_event = self.event_mapping.get(event_name, event_name)
        wrapped_handler = self._wrap_event_handler(event_name, handler)

        try:
            if hasattr(self.ttk_widget, "bind"):
                self.ttk_widget.bind(ttk_event, wrapped_handler)
        except Exception as e:
            self.logger.warning(f"绑定事件失败 [{event_name}]: {e}")

    def unbind_event(self, event_name: str) -> None:
        """解绑事件

        Args:
            event_name: 事件名称
        """
        if not self.ttk_widget:
            return

        ttk_event = self.event_mapping.get(event_name, event_name)

        try:
            if hasattr(self.ttk_widget, "unbind"):
                self.ttk_widget.unbind(ttk_event)
        except Exception as e:
            self.logger.warning(f"解绑事件失败 [{event_name}]: {e}")


class ComponentAdapterRegistry:
    """组件适配器注册表"""

    def __init__(self):
        """初始化注册表"""
        self._adapters: Dict[str, ComponentMapping] = {}
        self._register_default_adapters()

    def _register_default_adapters(self) -> None:
        """注册默认适配器"""
        # 基础组件映射
        self.register_adapter(
            "QWidget",
            ComponentMapping(
                qt_class="QWidget",
                ttk_class=ttk.Frame,
                config_mapping={
                    "windowTitle": "text",
                    "styleSheet": "style",
                    "enabled": "state",
                    "visible": "state",
                },
                event_mapping={
                    "clicked": "<Button-1>",
                    "doubleClicked": "<Double-Button-1>",
                    "rightClicked": "<Button-3>",
                    "keyPressed": "<KeyPress>",
                    "focusIn": "<FocusIn>",
                    "focusOut": "<FocusOut>",
                },
            ),
        )

        self.register_adapter(
            "QPushButton",
            ComponentMapping(
                qt_class="QPushButton",
                ttk_class=ttk.Button,
                config_mapping={
                    "text": "text",
                    "enabled": "state",
                    "styleSheet": "style",
                },
                event_mapping={
                    "clicked": "<Button-1>",
                    "pressed": "<ButtonPress-1>",
                    "released": "<ButtonRelease-1>",
                },
            ),
        )

        self.register_adapter(
            "QLabel",
            ComponentMapping(
                qt_class="QLabel",
                ttk_class=ttk.Label,
                config_mapping={
                    "text": "text",
                    "alignment": "anchor",
                    "styleSheet": "style",
                },
            ),
        )

        self.register_adapter(
            "QLineEdit",
            ComponentMapping(
                qt_class="QLineEdit",
                ttk_class=ttk.Entry,
                config_mapping={
                    "text": "textvariable",
                    "placeholderText": "placeholder",
                    "readOnly": "state",
                    "maxLength": "validate",
                },
                event_mapping={
                    "textChanged": "<KeyRelease>",
                    "returnPressed": "<Return>",
                    "focusIn": "<FocusIn>",
                    "focusOut": "<FocusOut>",
                },
            ),
        )

        self.register_adapter(
            "QTextEdit",
            ComponentMapping(
                qt_class="QTextEdit",
                ttk_class=tk.Text,
                config_mapping={
                    "plainText": "text",
                    "readOnly": "state",
                    "wordWrap": "wrap",
                },
                event_mapping={
                    "textChanged": "<KeyRelease>",
                    "focusIn": "<FocusIn>",
                    "focusOut": "<FocusOut>",
                },
            ),
        )

        self.register_adapter(
            "QComboBox",
            ComponentMapping(
                qt_class="QComboBox",
                ttk_class=ttk.Combobox,
                config_mapping={
                    "currentText": "textvariable",
                    "editable": "state",
                    "items": "values",
                },
                event_mapping={
                    "currentTextChanged": "<<ComboboxSelected>>",
                    "activated": "<<ComboboxSelected>>",
                },
            ),
        )

    def register_adapter(self, qt_class: str, mapping: ComponentMapping) -> None:
        """注册适配器

        Args:
            qt_class: Qt类名
            mapping: 组件映射配置
        """
        self._adapters[qt_class] = mapping

    def get_adapter_mapping(self, qt_class: str) -> Optional[ComponentMapping]:
        """获取适配器映射

        Args:
            qt_class: Qt类名

        Returns:
            组件映射配置
        """
        return self._adapters.get(qt_class)

    def get_available_adapters(self) -> List[str]:
        """获取可用适配器列表

        Returns:
            Qt类名列表
        """
        return list(self._adapters.keys())


# 全局适配器注册表
_global_adapter_registry: Optional[ComponentAdapterRegistry] = None


def get_adapter_registry() -> ComponentAdapterRegistry:
    """获取全局适配器注册表

    Returns:
        适配器注册表
    """
    global _global_adapter_registry
    if _global_adapter_registry is None:
        _global_adapter_registry = ComponentAdapterRegistry()
    return _global_adapter_registry


def create_adapter(
    qt_class: str,
    qt_config: Optional[Dict[str, Any]] = None,
    parent: Optional[tk.Widget] = None,
) -> Optional[QtToTtkAdapter]:
    """创建适配器

    Args:
        qt_class: Qt类名
        qt_config: Qt配置
        parent: 父组件

    Returns:
        适配器实例
    """
    registry = get_adapter_registry()
    mapping = registry.get_adapter_mapping(qt_class)

    if not mapping:
        logging.getLogger(__name__).warning(f"未找到适配器: {qt_class}")
        return None

    if mapping.adapter_class:
        return mapping.adapter_class(qt_config, parent)
    # 使用通用适配器
    return GenericAdapter(qt_class, qt_config, parent)


class GenericAdapter(QtToTtkAdapter):
    """通用适配器"""

    def __init__(
        self,
        qt_class: str,
        qt_config: Optional[Dict[str, Any]] = None,
        parent: Optional[tk.Widget] = None,
    ):
        """初始化通用适配器

        Args:
            qt_class: Qt类名
            qt_config: Qt配置
            parent: 父组件
        """
        self.qt_class = qt_class
        self.mapping = get_adapter_registry().get_adapter_mapping(qt_class)
        super().__init__(qt_config, parent)

    def _initialize_mappings(self) -> None:
        """初始化映射表"""
        if self.mapping:
            self.config_mapping = self.mapping.config_mapping or {}
            self.method_mapping = self.mapping.method_mapping or {}
            self.event_mapping = self.mapping.event_mapping or {}

    def _create_ttk_widget(self) -> None:
        """创建TTK组件"""
        if self.mapping and self.mapping.ttk_class:
            try:
                if self.parent:
                    self.ttk_widget = self.mapping.ttk_class(self.parent)
                else:
                    self.ttk_widget = self.mapping.ttk_class()
            except Exception as e:
                self.logger.error(f"创建TTK组件失败 [{self.qt_class}]: {e}")
        else:
            self.logger.warning(f"未找到TTK类映射: {self.qt_class}")
