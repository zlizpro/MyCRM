"""
适配器单元测试

测试Qt到TTK适配器的功能，包括：
- QtToTtkAdapter基类测试
- EventAdapter事件适配测试
- StyleAdapter样式适配测试
- 组件映射和转换测试

作者: MiniCRM开发团队
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch


# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from src.minicrm.ui.ttk_base.adapters.event_adapter import (
    EventAdapter,
    EventMapping,
    EventType,
    get_global_event_adapter,
)
from src.minicrm.ui.ttk_base.adapters.qt_to_ttk_adapter import (
    ComponentAdapterRegistry,
    ComponentMapping,
    ComponentType,
    GenericAdapter,
    create_adapter,
    get_adapter_registry,
)
from src.minicrm.ui.ttk_base.adapters.style_adapter import (
    StyleAdapter,
    StyleMapping,
    StyleProperty,
    get_global_style_adapter,
)


class TestComponentAdapterRegistry(unittest.TestCase):
    """组件适配器注册表测试类"""

    def setUp(self):
        """测试准备"""
        self.registry = ComponentAdapterRegistry()

    def test_registry_initialization(self):
        """测试注册表初始化"""
        self.assertIsNotNone(self.registry._adapters)

        # 检查默认适配器是否注册
        self.assertIn("QWidget", self.registry._adapters)
        self.assertIn("QPushButton", self.registry._adapters)
        self.assertIn("QLabel", self.registry._adapters)
        self.assertIn("QLineEdit", self.registry._adapters)

    def test_register_adapter(self):
        """测试注册适配器"""
        from tkinter import ttk

        mapping = ComponentMapping(
            qt_class="QTestWidget",
            ttk_class=ttk.Frame,
            config_mapping={"test": "test_ttk"},
        )

        self.registry.register_adapter("QTestWidget", mapping)

        self.assertIn("QTestWidget", self.registry._adapters)
        retrieved_mapping = self.registry.get_adapter_mapping("QTestWidget")
        self.assertEqual(retrieved_mapping.qt_class, "QTestWidget")
        self.assertEqual(retrieved_mapping.ttk_class, ttk.Frame)

    def test_get_adapter_mapping(self):
        """测试获取适配器映射"""
        mapping = self.registry.get_adapter_mapping("QPushButton")

        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.qt_class, "QPushButton")
        self.assertIsNotNone(mapping.config_mapping)
        self.assertIsNotNone(mapping.event_mapping)

    def test_get_available_adapters(self):
        """测试获取可用适配器列表"""
        adapters = self.registry.get_available_adapters()

        self.assertIsInstance(adapters, list)
        self.assertIn("QWidget", adapters)
        self.assertIn("QPushButton", adapters)
        self.assertIn("QLabel", adapters)


class TestGenericAdapter(unittest.TestCase):
    """通用适配器测试类"""

    def setUp(self):
        """测试准备"""
        # 模拟tkinter组件
        self.mock_parent = Mock()

        # 创建测试配置
        self.qt_config = {
            "properties": {"text": "Test Button", "enabled": True},
            "style": {"background-color": "#FF0000", "color": "#FFFFFF"},
            "events": {"clicked": Mock()},
        }

    def test_generic_adapter_creation(self):
        """测试通用适配器创建"""
        with patch("tkinter.ttk.Button") as mock_button_class:
            mock_button = Mock()
            mock_button_class.return_value = mock_button

            adapter = GenericAdapter("QPushButton", self.qt_config, self.mock_parent)

            self.assertEqual(adapter.qt_class, "QPushButton")
            self.assertIsNotNone(adapter.mapping)
            self.assertEqual(adapter.ttk_widget, mock_button)

    def test_property_conversion(self):
        """测试属性转换"""
        with patch("tkinter.ttk.Button") as mock_button_class:
            mock_button = Mock()
            mock_button_class.return_value = mock_button

            adapter = GenericAdapter("QPushButton", self.qt_config, self.mock_parent)

            # 测试颜色转换
            color = adapter._convert_color("#FF0000")
            self.assertEqual(color, "#FF0000")

            # 测试大小转换
            size = adapter._convert_size("100px")
            self.assertEqual(size, 100)

    def test_set_get_property(self):
        """测试设置和获取属性"""
        with patch("tkinter.ttk.Button") as mock_button_class:
            mock_button = Mock()
            mock_button_class.return_value = mock_button

            adapter = GenericAdapter("QPushButton", self.qt_config, self.mock_parent)

            # 测试设置属性
            adapter.set_property("text", "New Text")
            mock_button.configure.assert_called()

            # 测试获取属性
            mock_button.cget.return_value = "Test Value"
            value = adapter.get_property("text")
            self.assertEqual(value, "Test Value")


class TestEventAdapter(unittest.TestCase):
    """事件适配器测试类"""

    def setUp(self):
        """测试准备"""
        self.event_adapter = EventAdapter()
        self.mock_widget = Mock()
        self.mock_handler = Mock()

    def test_event_adapter_initialization(self):
        """测试事件适配器初始化"""
        self.assertIsNotNone(self.event_adapter.event_mappings)

        # 检查默认事件映射
        self.assertIn("clicked", self.event_adapter.event_mappings)
        self.assertIn("keyPressed", self.event_adapter.event_mappings)
        self.assertIn("focusIn", self.event_adapter.event_mappings)

    def test_register_event_mapping(self):
        """测试注册事件映射"""
        mapping = EventMapping(
            qt_event="customEvent", ttk_event="<Custom>", event_type=EventType.CUSTOM
        )

        self.event_adapter.register_event_mapping("customEvent", mapping)

        self.assertIn("customEvent", self.event_adapter.event_mappings)
        retrieved_mapping = self.event_adapter.event_mappings["customEvent"]
        self.assertEqual(retrieved_mapping.ttk_event, "<Custom>")

    def test_get_ttk_event(self):
        """测试获取TTK事件名称"""
        ttk_event = self.event_adapter.get_ttk_event("clicked")
        self.assertEqual(ttk_event, "<Button-1>")

        # 测试不存在的事件
        ttk_event = self.event_adapter.get_ttk_event("nonexistent")
        self.assertIsNone(ttk_event)

    def test_convert_event_handler(self):
        """测试转换事件处理器"""
        handler = self.event_adapter.convert_event_handler(
            "clicked", self.mock_handler, self.mock_widget
        )

        self.assertIsNotNone(handler)
        self.assertIsInstance(handler, type(lambda: None))

    def test_bind_event(self):
        """测试绑定事件"""
        result = self.event_adapter.bind_event(
            self.mock_widget, "clicked", self.mock_handler
        )

        self.assertTrue(result)
        self.mock_widget.bind.assert_called_once()

    def test_unbind_event(self):
        """测试解绑事件"""
        result = self.event_adapter.unbind_event(self.mock_widget, "clicked")

        self.assertTrue(result)
        self.mock_widget.unbind.assert_called_once()

    def test_mouse_event_conversion(self):
        """测试鼠标事件转换"""
        mock_tk_event = Mock()
        mock_tk_event.x = 100
        mock_tk_event.y = 200
        mock_tk_event.x_root = 300
        mock_tk_event.y_root = 400
        mock_tk_event.state = 0
        mock_tk_event.num = 1

        mouse_event = self.event_adapter._convert_mouse_event(
            mock_tk_event, self.mock_widget
        )

        self.assertEqual(mouse_event.x, 100)
        self.assertEqual(mouse_event.y, 200)
        self.assertEqual(mouse_event.x_root, 300)
        self.assertEqual(mouse_event.y_root, 400)
        self.assertEqual(mouse_event.widget, self.mock_widget)

    def test_keyboard_event_conversion(self):
        """测试键盘事件转换"""
        mock_tk_event = Mock()
        mock_tk_event.keysym = "Return"
        mock_tk_event.char = "\r"
        mock_tk_event.keycode = 13
        mock_tk_event.state = 0

        keyboard_event = self.event_adapter._convert_keyboard_event(
            mock_tk_event, self.mock_widget
        )

        self.assertEqual(keyboard_event.key, "Return")
        self.assertEqual(keyboard_event.char, "\r")
        self.assertEqual(keyboard_event.keycode, 13)
        self.assertTrue(keyboard_event.is_return)
        self.assertEqual(keyboard_event.widget, self.mock_widget)

    def test_clear_cache(self):
        """测试清理缓存"""
        # 先添加一些缓存
        self.event_adapter.handler_cache["test"] = Mock()

        self.event_adapter.clear_cache()

        self.assertEqual(len(self.event_adapter.handler_cache), 0)


class TestStyleAdapter(unittest.TestCase):
    """样式适配器测试类"""

    def setUp(self):
        """测试准备"""
        self.style_adapter = StyleAdapter()
        self.mock_widget = Mock()

    def test_style_adapter_initialization(self):
        """测试样式适配器初始化"""
        self.assertIsNotNone(self.style_adapter.style_mappings)
        self.assertIsNotNone(self.style_adapter.color_mappings)
        self.assertIsNotNone(self.style_adapter.font_mappings)

        # 检查默认样式映射
        self.assertIn("background-color", self.style_adapter.style_mappings)
        self.assertIn("color", self.style_adapter.style_mappings)
        self.assertIn("font", self.style_adapter.style_mappings)

    def test_register_style_mapping(self):
        """测试注册样式映射"""
        mapping = StyleMapping(
            qt_property="custom-property",
            ttk_property="custom_ttk_property",
            converter=lambda x: x.upper(),
        )

        self.style_adapter.register_style_mapping("custom-property", mapping)

        self.assertIn("custom-property", self.style_adapter.style_mappings)
        retrieved_mapping = self.style_adapter.style_mappings["custom-property"]
        self.assertEqual(retrieved_mapping.ttk_property, "custom_ttk_property")

    def test_convert_color(self):
        """测试颜色转换"""
        # 十六进制颜色
        color = self.style_adapter._convert_color("#FF0000")
        self.assertEqual(color, "#FF0000")

        # RGB颜色
        color = self.style_adapter._convert_color("rgb(255, 0, 0)")
        self.assertEqual(color, "#ff0000")

        # 颜色名称
        color = self.style_adapter._convert_color("red")
        self.assertEqual(color, "#FF0000")

        # 未知颜色
        color = self.style_adapter._convert_color("unknown")
        self.assertEqual(color, "unknown")

    def test_convert_font(self):
        """测试字体转换"""
        # 完整字体字符串
        font = self.style_adapter._convert_font("Arial 12px bold italic")
        self.assertEqual(font[0], "Arial")  # family
        self.assertEqual(font[1], 12)  # size
        self.assertEqual(font[2], "bold")  # weight
        self.assertEqual(font[3], "italic")  # slant

        # 简单字体
        font = self.style_adapter._convert_font("Helvetica 14")
        self.assertEqual(font[0], "Helvetica")
        self.assertEqual(font[1], 14)

    def test_convert_single_property(self):
        """测试转换单个属性"""
        # 背景色转换
        result = self.style_adapter.convert_single_property(
            "background-color", "#FF0000"
        )
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "background")
        self.assertEqual(result[1], "#FF0000")

        # 字体大小转换
        result = self.style_adapter.convert_single_property("font-size", "12px")
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "font")
        self.assertEqual(result[1], 12)

        # 不存在的属性
        result = self.style_adapter.convert_single_property("nonexistent", "value")
        self.assertIsNone(result)

    def test_parse_style_sheet(self):
        """测试解析样式表"""
        style_sheet = """
        QPushButton {
            background-color: #FF0000;
            color: white;
            font-size: 12px;
        }

        QLabel {
            color: black;
            font-weight: bold;
        }
        """

        parsed = self.style_adapter._parse_style_sheet(style_sheet)

        self.assertIn("QPushButton", parsed)
        self.assertIn("QLabel", parsed)

        button_styles = parsed["QPushButton"]
        self.assertEqual(button_styles["background-color"], "#FF0000")
        self.assertEqual(button_styles["color"], "white")
        self.assertEqual(button_styles["font-size"], "12px")

        label_styles = parsed["QLabel"]
        self.assertEqual(label_styles["color"], "black")
        self.assertEqual(label_styles["font-weight"], "bold")

    def test_convert_style_sheet(self):
        """测试转换样式表"""
        style_sheet = """
        QPushButton {
            background-color: #FF0000;
            color: white;
        }
        """

        converted = self.style_adapter.convert_style_sheet(style_sheet)

        self.assertIn("QPushButton", converted)
        button_styles = converted["QPushButton"]
        self.assertIn("background", button_styles)
        self.assertIn("foreground", button_styles)
        self.assertEqual(button_styles["background"], "#FF0000")
        self.assertEqual(button_styles["foreground"], "white")

    def test_apply_style_to_widget(self):
        """测试应用样式到组件"""
        style_config = {"background": "#FF0000", "foreground": "white"}

        self.style_adapter.apply_style_to_widget(self.mock_widget, style_config)

        self.mock_widget.configure.assert_called_once_with(**style_config)

    def test_convert_border(self):
        """测试边框转换"""
        # 像素边框
        border = self.style_adapter._convert_border("2px solid black")
        self.assertEqual(border, 2)

        # 数字边框
        border = self.style_adapter._convert_border("3")
        self.assertEqual(border, 3)

        # 默认边框
        border = self.style_adapter._convert_border("solid")
        self.assertEqual(border, 1)

    def test_convert_padding(self):
        """测试内边距转换"""
        # 单个值
        padding = self.style_adapter._convert_padding("5px")
        self.assertEqual(padding, 5)

        # 两个值
        padding = self.style_adapter._convert_padding("5px 10px")
        self.assertEqual(padding, (10, 5))

        # 四个值
        padding = self.style_adapter._convert_padding("5px 10px 15px 20px")
        self.assertEqual(padding, (10, 5))

    def test_clear_cache(self):
        """测试清理缓存"""
        # 先添加一些缓存
        self.style_adapter.style_cache["test"] = {"background": "red"}

        self.style_adapter.clear_cache()

        self.assertEqual(len(self.style_adapter.style_cache), 0)


class TestGlobalAdapters(unittest.TestCase):
    """全局适配器测试类"""

    def test_get_adapter_registry(self):
        """测试获取全局适配器注册表"""
        registry1 = get_adapter_registry()
        registry2 = get_adapter_registry()

        # 应该返回同一个实例
        self.assertIs(registry1, registry2)
        self.assertIsInstance(registry1, ComponentAdapterRegistry)

    def test_get_global_event_adapter(self):
        """测试获取全局事件适配器"""
        adapter1 = get_global_event_adapter()
        adapter2 = get_global_event_adapter()

        # 应该返回同一个实例
        self.assertIs(adapter1, adapter2)
        self.assertIsInstance(adapter1, EventAdapter)

    def test_get_global_style_adapter(self):
        """测试获取全局样式适配器"""
        adapter1 = get_global_style_adapter()
        adapter2 = get_global_style_adapter()

        # 应该返回同一个实例
        self.assertIs(adapter1, adapter2)
        self.assertIsInstance(adapter1, StyleAdapter)

    def test_create_adapter(self):
        """测试创建适配器"""
        with patch("tkinter.ttk.Button") as mock_button_class:
            mock_button = Mock()
            mock_button_class.return_value = mock_button

            adapter = create_adapter("QPushButton", {"text": "Test"})

            self.assertIsNotNone(adapter)
            self.assertIsInstance(adapter, GenericAdapter)

        # 测试不存在的适配器
        adapter = create_adapter("QNonexistentWidget")
        self.assertIsNone(adapter)


class TestComponentTypes(unittest.TestCase):
    """组件类型测试类"""

    def test_component_type_enum(self):
        """测试组件类型枚举"""
        self.assertEqual(ComponentType.WINDOW.value, "window")
        self.assertEqual(ComponentType.BUTTON.value, "button")
        self.assertEqual(ComponentType.LABEL.value, "label")
        self.assertEqual(ComponentType.ENTRY.value, "entry")
        self.assertEqual(ComponentType.TREEVIEW.value, "treeview")


class TestEventTypes(unittest.TestCase):
    """事件类型测试类"""

    def test_event_type_enum(self):
        """测试事件类型枚举"""
        self.assertEqual(EventType.MOUSE.value, "mouse")
        self.assertEqual(EventType.KEYBOARD.value, "keyboard")
        self.assertEqual(EventType.FOCUS.value, "focus")
        self.assertEqual(EventType.WINDOW.value, "window")
        self.assertEqual(EventType.WIDGET.value, "widget")
        self.assertEqual(EventType.CUSTOM.value, "custom")


class TestStyleProperties(unittest.TestCase):
    """样式属性测试类"""

    def test_style_property_enum(self):
        """测试样式属性枚举"""
        self.assertEqual(StyleProperty.BACKGROUND.value, "background")
        self.assertEqual(StyleProperty.FOREGROUND.value, "foreground")
        self.assertEqual(StyleProperty.FONT.value, "font")
        self.assertEqual(StyleProperty.BORDER.value, "border")
        self.assertEqual(StyleProperty.PADDING.value, "padding")


if __name__ == "__main__":
    # 运行所有测试
    unittest.main(verbosity=2)
