"""事件适配器

处理Qt事件到TTK事件的转换,包括:
- 事件名称映射
- 事件参数转换
- 事件处理器包装
- 事件传播控制

设计目标:
1. 提供Qt到TTK事件的无缝转换
2. 保持事件处理的一致性
3. 支持复杂事件的适配
4. 优化事件处理性能

作者: MiniCRM开发团队
"""

from dataclasses import dataclass
from enum import Enum
import logging
import tkinter as tk
from typing import Any, Callable, Dict, Optional


class EventType(Enum):
    """事件类型枚举"""

    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    FOCUS = "focus"
    WINDOW = "window"
    WIDGET = "widget"
    CUSTOM = "custom"


@dataclass
class EventMapping:
    """事件映射配置"""

    qt_event: str
    ttk_event: str
    event_type: EventType
    converter: Optional[Callable] = None
    validator: Optional[Callable] = None


class EventAdapter:
    """事件适配器

    处理Qt事件到TTK事件的转换和适配.
    """

    def __init__(self):
        """初始化事件适配器"""
        self.logger = logging.getLogger(__name__)

        # 事件映射表
        self.event_mappings: Dict[str, EventMapping] = {}

        # 事件处理器缓存
        self.handler_cache: Dict[str, Callable] = {}

        # 初始化默认映射
        self._initialize_default_mappings()

    def _initialize_default_mappings(self) -> None:
        """初始化默认事件映射"""
        # 鼠标事件映射
        self.register_event_mapping(
            "clicked",
            EventMapping(
                qt_event="clicked",
                ttk_event="<Button-1>",
                event_type=EventType.MOUSE,
                converter=self._convert_mouse_event,
            ),
        )

        self.register_event_mapping(
            "doubleClicked",
            EventMapping(
                qt_event="doubleClicked",
                ttk_event="<Double-Button-1>",
                event_type=EventType.MOUSE,
                converter=self._convert_mouse_event,
            ),
        )

        self.register_event_mapping(
            "rightClicked",
            EventMapping(
                qt_event="rightClicked",
                ttk_event="<Button-3>",
                event_type=EventType.MOUSE,
                converter=self._convert_mouse_event,
            ),
        )

        self.register_event_mapping(
            "mousePressed",
            EventMapping(
                qt_event="mousePressed",
                ttk_event="<ButtonPress-1>",
                event_type=EventType.MOUSE,
                converter=self._convert_mouse_event,
            ),
        )

        self.register_event_mapping(
            "mouseReleased",
            EventMapping(
                qt_event="mouseReleased",
                ttk_event="<ButtonRelease-1>",
                event_type=EventType.MOUSE,
                converter=self._convert_mouse_event,
            ),
        )

        self.register_event_mapping(
            "mouseMoved",
            EventMapping(
                qt_event="mouseMoved",
                ttk_event="<Motion>",
                event_type=EventType.MOUSE,
                converter=self._convert_mouse_event,
            ),
        )

        self.register_event_mapping(
            "mouseEntered",
            EventMapping(
                qt_event="mouseEntered",
                ttk_event="<Enter>",
                event_type=EventType.MOUSE,
                converter=self._convert_mouse_event,
            ),
        )

        self.register_event_mapping(
            "mouseLeft",
            EventMapping(
                qt_event="mouseLeft",
                ttk_event="<Leave>",
                event_type=EventType.MOUSE,
                converter=self._convert_mouse_event,
            ),
        )

        # 键盘事件映射
        self.register_event_mapping(
            "keyPressed",
            EventMapping(
                qt_event="keyPressed",
                ttk_event="<KeyPress>",
                event_type=EventType.KEYBOARD,
                converter=self._convert_keyboard_event,
            ),
        )

        self.register_event_mapping(
            "keyReleased",
            EventMapping(
                qt_event="keyReleased",
                ttk_event="<KeyRelease>",
                event_type=EventType.KEYBOARD,
                converter=self._convert_keyboard_event,
            ),
        )

        self.register_event_mapping(
            "returnPressed",
            EventMapping(
                qt_event="returnPressed",
                ttk_event="<Return>",
                event_type=EventType.KEYBOARD,
                converter=self._convert_keyboard_event,
            ),
        )

        self.register_event_mapping(
            "escapePressed",
            EventMapping(
                qt_event="escapePressed",
                ttk_event="<Escape>",
                event_type=EventType.KEYBOARD,
                converter=self._convert_keyboard_event,
            ),
        )

        # 焦点事件映射
        self.register_event_mapping(
            "focusIn",
            EventMapping(
                qt_event="focusIn",
                ttk_event="<FocusIn>",
                event_type=EventType.FOCUS,
                converter=self._convert_focus_event,
            ),
        )

        self.register_event_mapping(
            "focusOut",
            EventMapping(
                qt_event="focusOut",
                ttk_event="<FocusOut>",
                event_type=EventType.FOCUS,
                converter=self._convert_focus_event,
            ),
        )

        # 窗口事件映射
        self.register_event_mapping(
            "resized",
            EventMapping(
                qt_event="resized",
                ttk_event="<Configure>",
                event_type=EventType.WINDOW,
                converter=self._convert_window_event,
            ),
        )

        self.register_event_mapping(
            "moved",
            EventMapping(
                qt_event="moved",
                ttk_event="<Configure>",
                event_type=EventType.WINDOW,
                converter=self._convert_window_event,
            ),
        )

        self.register_event_mapping(
            "closed",
            EventMapping(
                qt_event="closed",
                ttk_event="<Destroy>",
                event_type=EventType.WINDOW,
                converter=self._convert_window_event,
            ),
        )

        # 组件特定事件映射
        self.register_event_mapping(
            "textChanged",
            EventMapping(
                qt_event="textChanged",
                ttk_event="<KeyRelease>",
                event_type=EventType.WIDGET,
                converter=self._convert_text_event,
            ),
        )

        self.register_event_mapping(
            "valueChanged",
            EventMapping(
                qt_event="valueChanged",
                ttk_event="<<ValueChanged>>",
                event_type=EventType.WIDGET,
                converter=self._convert_value_event,
            ),
        )

        self.register_event_mapping(
            "selectionChanged",
            EventMapping(
                qt_event="selectionChanged",
                ttk_event="<<TreeviewSelect>>",
                event_type=EventType.WIDGET,
                converter=self._convert_selection_event,
            ),
        )

        self.register_event_mapping(
            "itemClicked",
            EventMapping(
                qt_event="itemClicked",
                ttk_event="<<TreeviewSelect>>",
                event_type=EventType.WIDGET,
                converter=self._convert_item_event,
            ),
        )

        self.register_event_mapping(
            "currentTextChanged",
            EventMapping(
                qt_event="currentTextChanged",
                ttk_event="<<ComboboxSelected>>",
                event_type=EventType.WIDGET,
                converter=self._convert_combobox_event,
            ),
        )

    def register_event_mapping(self, qt_event: str, mapping: EventMapping) -> None:
        """注册事件映射

        Args:
            qt_event: Qt事件名称
            mapping: 事件映射配置
        """
        self.event_mappings[qt_event] = mapping
        self.logger.debug(f"注册事件映射: {qt_event} -> {mapping.ttk_event}")

    def get_ttk_event(self, qt_event: str) -> Optional[str]:
        """获取对应的TTK事件名称

        Args:
            qt_event: Qt事件名称

        Returns:
            TTK事件名称
        """
        mapping = self.event_mappings.get(qt_event)
        return mapping.ttk_event if mapping else None

    def convert_event_handler(
        self, qt_event: str, qt_handler: Callable, widget: tk.Widget
    ) -> Optional[Callable]:
        """转换事件处理器

        Args:
            qt_event: Qt事件名称
            qt_handler: Qt事件处理器
            widget: TTK组件

        Returns:
            TTK事件处理器
        """
        mapping = self.event_mappings.get(qt_event)
        if not mapping:
            self.logger.warning(f"未找到事件映射: {qt_event}")
            return None

        # 创建缓存键
        cache_key = f"{qt_event}_{id(qt_handler)}_{id(widget)}"

        # 检查缓存
        if cache_key in self.handler_cache:
            return self.handler_cache[cache_key]

        # 创建包装的事件处理器
        def wrapped_handler(tk_event):
            try:
                # 转换事件对象
                converted_event = self._convert_event_object(mapping, tk_event, widget)

                # 验证事件
                if mapping.validator and not mapping.validator(converted_event):
                    return None

                # 调用原始处理器
                return qt_handler(converted_event)

            except Exception as e:
                self.logger.error(f"事件处理器执行失败 [{qt_event}]: {e}")

        # 缓存处理器
        self.handler_cache[cache_key] = wrapped_handler

        return wrapped_handler

    def bind_event(
        self, widget: tk.Widget, qt_event: str, qt_handler: Callable
    ) -> bool:
        """绑定事件

        Args:
            widget: TTK组件
            qt_event: Qt事件名称
            qt_handler: Qt事件处理器

        Returns:
            是否绑定成功
        """
        ttk_event = self.get_ttk_event(qt_event)
        if not ttk_event:
            return False

        ttk_handler = self.convert_event_handler(qt_event, qt_handler, widget)
        if not ttk_handler:
            return False

        try:
            widget.bind(ttk_event, ttk_handler)
            self.logger.debug(f"绑定事件: {qt_event} -> {ttk_event}")
            return True
        except Exception as e:
            self.logger.error(f"绑定事件失败 [{qt_event}]: {e}")
            return False

    def unbind_event(self, widget: tk.Widget, qt_event: str) -> bool:
        """解绑事件

        Args:
            widget: TTK组件
            qt_event: Qt事件名称

        Returns:
            是否解绑成功
        """
        ttk_event = self.get_ttk_event(qt_event)
        if not ttk_event:
            return False

        try:
            widget.unbind(ttk_event)
            self.logger.debug(f"解绑事件: {qt_event} -> {ttk_event}")
            return True
        except Exception as e:
            self.logger.error(f"解绑事件失败 [{qt_event}]: {e}")
            return False

    def _convert_event_object(
        self, mapping: EventMapping, tk_event, widget: tk.Widget
    ) -> Any:
        """转换事件对象

        Args:
            mapping: 事件映射配置
            tk_event: Tkinter事件对象
            widget: TTK组件

        Returns:
            转换后的事件对象
        """
        if mapping.converter:
            return mapping.converter(tk_event, widget)
        return self._create_generic_event_object(tk_event, widget)

    def _create_generic_event_object(self, tk_event, widget: tk.Widget) -> Any:
        """创建通用事件对象

        Args:
            tk_event: Tkinter事件对象
            widget: TTK组件

        Returns:
            通用事件对象
        """

        class GenericEvent:
            def __init__(self, tk_event, widget):
                self.widget = widget
                self.type = getattr(tk_event, "type", None)
                self.x = getattr(tk_event, "x", 0)
                self.y = getattr(tk_event, "y", 0)
                self.x_root = getattr(tk_event, "x_root", 0)
                self.y_root = getattr(tk_event, "y_root", 0)
                self.key = getattr(tk_event, "keysym", "")
                self.char = getattr(tk_event, "char", "")
                self.state = getattr(tk_event, "state", 0)
                self.delta = getattr(tk_event, "delta", 0)
                self.width = getattr(tk_event, "width", 0)
                self.height = getattr(tk_event, "height", 0)

        return GenericEvent(tk_event, widget)

    def _convert_mouse_event(self, tk_event, widget: tk.Widget) -> Any:
        """转换鼠标事件"""

        class MouseEvent:
            def __init__(self, tk_event, widget):
                self.widget = widget
                self.x = getattr(tk_event, "x", 0)
                self.y = getattr(tk_event, "y", 0)
                self.x_root = getattr(tk_event, "x_root", 0)
                self.y_root = getattr(tk_event, "y_root", 0)
                self.button = self._get_button_number(tk_event)
                self.state = getattr(tk_event, "state", 0)

                # 修饰键状态
                self.ctrl_pressed = bool(self.state & 0x4)
                self.shift_pressed = bool(self.state & 0x1)
                self.alt_pressed = bool(self.state & 0x8)

            def _get_button_number(self, tk_event):
                """获取按钮编号"""
                if hasattr(tk_event, "num"):
                    return tk_event.num
                return 1  # 默认左键

        return MouseEvent(tk_event, widget)

    def _convert_keyboard_event(self, tk_event, widget: tk.Widget) -> Any:
        """转换键盘事件"""

        class KeyboardEvent:
            def __init__(self, tk_event, widget):
                self.widget = widget
                self.key = getattr(tk_event, "keysym", "")
                self.char = getattr(tk_event, "char", "")
                self.keycode = getattr(tk_event, "keycode", 0)
                self.state = getattr(tk_event, "state", 0)

                # 修饰键状态
                self.ctrl_pressed = bool(self.state & 0x4)
                self.shift_pressed = bool(self.state & 0x1)
                self.alt_pressed = bool(self.state & 0x8)

                # 特殊键判断
                self.is_return = self.key == "Return"
                self.is_escape = self.key == "Escape"
                self.is_tab = self.key == "Tab"
                self.is_backspace = self.key == "BackSpace"
                self.is_delete = self.key == "Delete"

        return KeyboardEvent(tk_event, widget)

    def _convert_focus_event(self, tk_event, widget: tk.Widget) -> Any:
        """转换焦点事件"""

        class FocusEvent:
            def __init__(self, tk_event, widget):
                self.widget = widget
                self.focus_in = tk_event.type == "9"  # FocusIn
                self.focus_out = tk_event.type == "10"  # FocusOut

        return FocusEvent(tk_event, widget)

    def _convert_window_event(self, tk_event, widget: tk.Widget) -> Any:
        """转换窗口事件"""

        class WindowEvent:
            def __init__(self, tk_event, widget):
                self.widget = widget
                self.width = getattr(tk_event, "width", 0)
                self.height = getattr(tk_event, "height", 0)
                self.x = getattr(tk_event, "x", 0)
                self.y = getattr(tk_event, "y", 0)

        return WindowEvent(tk_event, widget)

    def _convert_text_event(self, tk_event, widget: tk.Widget) -> Any:
        """转换文本事件"""

        class TextEvent:
            def __init__(self, tk_event, widget):
                self.widget = widget
                self.text = self._get_widget_text(widget)

            def _get_widget_text(self, widget):
                """获取组件文本"""
                try:
                    if hasattr(widget, "get"):
                        if isinstance(widget, tk.Text):
                            return widget.get("1.0", tk.END).rstrip("\n")
                        return widget.get()
                    return ""
                except:
                    return ""

        return TextEvent(tk_event, widget)

    def _convert_value_event(self, tk_event, widget: tk.Widget) -> Any:
        """转换值变化事件"""

        class ValueEvent:
            def __init__(self, tk_event, widget):
                self.widget = widget
                self.value = self._get_widget_value(widget)

            def _get_widget_value(self, widget):
                """获取组件值"""
                try:
                    if hasattr(widget, "get"):
                        return widget.get()
                    if hasattr(widget, "cget"):
                        return widget.cget("text")
                    return None
                except:
                    return None

        return ValueEvent(tk_event, widget)

    def _convert_selection_event(self, tk_event, widget: tk.Widget) -> Any:
        """转换选择事件"""

        class SelectionEvent:
            def __init__(self, tk_event, widget):
                self.widget = widget
                self.selection = self._get_selection(widget)

            def _get_selection(self, widget):
                """获取选择项"""
                try:
                    if hasattr(widget, "selection"):
                        return widget.selection()
                    if hasattr(widget, "curselection"):
                        return widget.curselection()
                    return []
                except:
                    return []

        return SelectionEvent(tk_event, widget)

    def _convert_item_event(self, tk_event, widget: tk.Widget) -> Any:
        """转换项目事件"""

        class ItemEvent:
            def __init__(self, tk_event, widget):
                self.widget = widget
                self.item = self._get_current_item(widget)

            def _get_current_item(self, widget):
                """获取当前项目"""
                try:
                    if hasattr(widget, "focus"):
                        return widget.focus()
                    if hasattr(widget, "selection"):
                        selection = widget.selection()
                        return selection[0] if selection else None
                    return None
                except:
                    return None

        return ItemEvent(tk_event, widget)

    def _convert_combobox_event(self, tk_event, widget: tk.Widget) -> Any:
        """转换下拉框事件"""

        class ComboboxEvent:
            def __init__(self, tk_event, widget):
                self.widget = widget
                self.current_text = self._get_current_text(widget)
                self.current_index = self._get_current_index(widget)

            def _get_current_text(self, widget):
                """获取当前文本"""
                try:
                    if hasattr(widget, "get"):
                        return widget.get()
                    return ""
                except:
                    return ""

            def _get_current_index(self, widget):
                """获取当前索引"""
                try:
                    if hasattr(widget, "current"):
                        return widget.current()
                    return -1
                except:
                    return -1

        return ComboboxEvent(tk_event, widget)

    def clear_cache(self) -> None:
        """清理处理器缓存"""
        self.handler_cache.clear()
        self.logger.debug("清理事件处理器缓存")

    def get_event_mappings(self) -> Dict[str, str]:
        """获取所有事件映射

        Returns:
            事件映射字典
        """
        return {
            qt_event: mapping.ttk_event
            for qt_event, mapping in self.event_mappings.items()
        }


# 全局事件适配器实例
_global_event_adapter: Optional[EventAdapter] = None


def get_global_event_adapter() -> EventAdapter:
    """获取全局事件适配器实例

    Returns:
        事件适配器
    """
    global _global_event_adapter
    if _global_event_adapter is None:
        _global_event_adapter = EventAdapter()
    return _global_event_adapter
