"""样式适配器

处理Qt样式到TTK样式的转换,包括:
- 样式属性映射
- 颜色和字体转换
- 样式表解析
- 主题适配

设计目标:
1. 提供Qt到TTK样式的无缝转换
2. 保持样式效果的一致性
3. 支持复杂样式的适配
4. 优化样式应用性能

作者: MiniCRM开发团队
"""

from dataclasses import dataclass
from enum import Enum
import logging
import re
import tkinter as tk
from typing import Any, Dict, Optional, Tuple, Union


class StyleProperty(Enum):
    """样式属性枚举"""

    BACKGROUND = "background"
    FOREGROUND = "foreground"
    FONT = "font"
    BORDER = "border"
    PADDING = "padding"
    MARGIN = "margin"
    WIDTH = "width"
    HEIGHT = "height"
    COLOR = "color"
    SIZE = "size"


@dataclass
class StyleMapping:
    """样式映射配置"""

    qt_property: str
    ttk_property: str
    converter: Optional[callable] = None
    validator: Optional[callable] = None
    default_value: Any = None


class StyleAdapter:
    """样式适配器

    处理Qt样式到TTK样式的转换和适配.
    """

    def __init__(self):
        """初始化样式适配器"""
        self.logger = logging.getLogger(__name__)

        # 样式映射表
        self.style_mappings: Dict[str, StyleMapping] = {}

        # 颜色映射表
        self.color_mappings: Dict[str, str] = {}

        # 字体映射表
        self.font_mappings: Dict[str, str] = {}

        # 样式缓存
        self.style_cache: Dict[str, Dict[str, Any]] = {}

        # 初始化默认映射
        self._initialize_default_mappings()

    def _initialize_default_mappings(self) -> None:
        """初始化默认样式映射"""
        # 背景色映射
        self.register_style_mapping(
            "background-color",
            StyleMapping(
                qt_property="background-color",
                ttk_property="background",
                converter=self._convert_color,
            ),
        )

        self.register_style_mapping(
            "background",
            StyleMapping(
                qt_property="background",
                ttk_property="background",
                converter=self._convert_color,
            ),
        )

        # 前景色映射
        self.register_style_mapping(
            "color",
            StyleMapping(
                qt_property="color",
                ttk_property="foreground",
                converter=self._convert_color,
            ),
        )

        self.register_style_mapping(
            "foreground",
            StyleMapping(
                qt_property="foreground",
                ttk_property="foreground",
                converter=self._convert_color,
            ),
        )

        # 字体映射
        self.register_style_mapping(
            "font-family",
            StyleMapping(
                qt_property="font-family",
                ttk_property="font",
                converter=self._convert_font_family,
            ),
        )

        self.register_style_mapping(
            "font-size",
            StyleMapping(
                qt_property="font-size",
                ttk_property="font",
                converter=self._convert_font_size,
            ),
        )

        self.register_style_mapping(
            "font-weight",
            StyleMapping(
                qt_property="font-weight",
                ttk_property="font",
                converter=self._convert_font_weight,
            ),
        )

        self.register_style_mapping(
            "font-style",
            StyleMapping(
                qt_property="font-style",
                ttk_property="font",
                converter=self._convert_font_style,
            ),
        )

        self.register_style_mapping(
            "font",
            StyleMapping(
                qt_property="font", ttk_property="font", converter=self._convert_font
            ),
        )

        # 边框映射
        self.register_style_mapping(
            "border",
            StyleMapping(
                qt_property="border",
                ttk_property="borderwidth",
                converter=self._convert_border,
            ),
        )

        self.register_style_mapping(
            "border-width",
            StyleMapping(
                qt_property="border-width",
                ttk_property="borderwidth",
                converter=self._convert_border_width,
            ),
        )

        self.register_style_mapping(
            "border-color",
            StyleMapping(
                qt_property="border-color",
                ttk_property="bordercolor",
                converter=self._convert_color,
            ),
        )

        self.register_style_mapping(
            "border-style",
            StyleMapping(
                qt_property="border-style",
                ttk_property="relief",
                converter=self._convert_border_style,
            ),
        )

        # 内边距映射
        self.register_style_mapping(
            "padding",
            StyleMapping(
                qt_property="padding",
                ttk_property="padding",
                converter=self._convert_padding,
            ),
        )

        self.register_style_mapping(
            "padding-left",
            StyleMapping(
                qt_property="padding-left",
                ttk_property="padx",
                converter=self._convert_size,
            ),
        )

        self.register_style_mapping(
            "padding-right",
            StyleMapping(
                qt_property="padding-right",
                ttk_property="padx",
                converter=self._convert_size,
            ),
        )

        self.register_style_mapping(
            "padding-top",
            StyleMapping(
                qt_property="padding-top",
                ttk_property="pady",
                converter=self._convert_size,
            ),
        )

        self.register_style_mapping(
            "padding-bottom",
            StyleMapping(
                qt_property="padding-bottom",
                ttk_property="pady",
                converter=self._convert_size,
            ),
        )

        # 大小映射
        self.register_style_mapping(
            "width",
            StyleMapping(
                qt_property="width", ttk_property="width", converter=self._convert_size
            ),
        )

        self.register_style_mapping(
            "height",
            StyleMapping(
                qt_property="height",
                ttk_property="height",
                converter=self._convert_size,
            ),
        )

        self.register_style_mapping(
            "min-width",
            StyleMapping(
                qt_property="min-width",
                ttk_property="minwidth",
                converter=self._convert_size,
            ),
        )

        self.register_style_mapping(
            "min-height",
            StyleMapping(
                qt_property="min-height",
                ttk_property="minheight",
                converter=self._convert_size,
            ),
        )

        # 文本对齐映射
        self.register_style_mapping(
            "text-align",
            StyleMapping(
                qt_property="text-align",
                ttk_property="anchor",
                converter=self._convert_text_align,
            ),
        )

        # 初始化颜色映射
        self._initialize_color_mappings()

        # 初始化字体映射
        self._initialize_font_mappings()

    def _initialize_color_mappings(self) -> None:
        """初始化颜色映射"""
        self.color_mappings.update(
            {
                # Qt颜色名称到标准颜色
                "red": "#FF0000",
                "green": "#00FF00",
                "blue": "#0000FF",
                "white": "#FFFFFF",
                "black": "#000000",
                "gray": "#808080",
                "grey": "#808080",
                "yellow": "#FFFF00",
                "cyan": "#00FFFF",
                "magenta": "#FF00FF",
                "transparent": "",
                # Qt系统颜色
                "window": "#F0F0F0",
                "windowText": "#000000",
                "base": "#FFFFFF",
                "alternateBase": "#F7F7F7",
                "toolTipBase": "#FFFFDC",
                "toolTipText": "#000000",
                "text": "#000000",
                "button": "#E1E1E1",
                "buttonText": "#000000",
                "brightText": "#FFFFFF",
                "highlight": "#0078D4",
                "highlightedText": "#FFFFFF",
                "link": "#0000FF",
                "linkVisited": "#800080",
            }
        )

    def _initialize_font_mappings(self) -> None:
        """初始化字体映射"""
        self.font_mappings.update(
            {
                # Qt字体族到系统字体
                "Arial": "Arial",
                "Helvetica": "Helvetica",
                "Times": "Times",
                "Times New Roman": "Times New Roman",
                "Courier": "Courier",
                "Courier New": "Courier New",
                "Verdana": "Verdana",
                "Georgia": "Georgia",
                "Palatino": "Palatino",
                "Garamond": "Garamond",
                "Bookman": "Bookman",
                "Comic Sans MS": "Comic Sans MS",
                "Trebuchet MS": "Trebuchet MS",
                "Arial Black": "Arial Black",
                "Impact": "Impact",
                # 中文字体
                "SimSun": "SimSun",
                "SimHei": "SimHei",
                "Microsoft YaHei": "Microsoft YaHei",
                "Microsoft YaHei UI": "Microsoft YaHei UI",
                "NSimSun": "NSimSun",
                "FangSong": "FangSong",
                "KaiTi": "KaiTi",
                "LiSu": "LiSu",
                "YouYuan": "YouYuan",
                # 通用字体族
                "serif": "Times",
                "sans-serif": "Arial",
                "monospace": "Courier",
                "cursive": "Comic Sans MS",
                "fantasy": "Impact",
            }
        )

    def register_style_mapping(self, qt_property: str, mapping: StyleMapping) -> None:
        """注册样式映射

        Args:
            qt_property: Qt样式属性名
            mapping: 样式映射配置
        """
        self.style_mappings[qt_property] = mapping
        self.logger.debug(f"注册样式映射: {qt_property} -> {mapping.ttk_property}")

    def convert_style_sheet(self, style_sheet: str) -> Dict[str, Any]:
        """转换Qt样式表到TTK样式

        Args:
            style_sheet: Qt样式表字符串

        Returns:
            TTK样式配置字典
        """
        # 检查缓存
        cache_key = hash(style_sheet)
        if cache_key in self.style_cache:
            return self.style_cache[cache_key]

        try:
            # 解析样式表
            parsed_styles = self._parse_style_sheet(style_sheet)

            # 转换样式
            ttk_styles = {}
            for selector, properties in parsed_styles.items():
                ttk_properties = self._convert_properties(properties)
                if ttk_properties:
                    ttk_styles[selector] = ttk_properties

            # 缓存结果
            self.style_cache[cache_key] = ttk_styles

            return ttk_styles

        except Exception as e:
            self.logger.error(f"转换样式表失败: {e}")
            return {}

    def convert_single_property(
        self, qt_property: str, value: Any
    ) -> Optional[Tuple[str, Any]]:
        """转换单个样式属性

        Args:
            qt_property: Qt属性名
            value: 属性值

        Returns:
            (TTK属性名, 转换后的值) 或 None
        """
        mapping = self.style_mappings.get(qt_property)
        if not mapping:
            self.logger.debug(f"未找到样式映射: {qt_property}")
            return None

        try:
            # 转换值
            if mapping.converter:
                converted_value = mapping.converter(value)
            else:
                converted_value = value

            # 验证值
            if mapping.validator and not mapping.validator(converted_value):
                self.logger.warning(f"样式值验证失败: {qt_property}={value}")
                return None

            return (mapping.ttk_property, converted_value)

        except Exception as e:
            self.logger.error(f"转换样式属性失败 [{qt_property}]: {e}")
            return None

    def apply_style_to_widget(
        self, widget: tk.Widget, style_config: Dict[str, Any]
    ) -> None:
        """应用样式到组件

        Args:
            widget: TTK组件
            style_config: 样式配置
        """
        try:
            if hasattr(widget, "configure"):
                widget.configure(**style_config)
            else:
                # 对于不支持configure的组件,尝试直接设置属性
                for prop, value in style_config.items():
                    try:
                        widget[prop] = value
                    except:
                        pass
        except Exception as e:
            self.logger.error(f"应用样式失败: {e}")

    def _parse_style_sheet(self, style_sheet: str) -> Dict[str, Dict[str, str]]:
        """解析Qt样式表

        Args:
            style_sheet: 样式表字符串

        Returns:
            解析后的样式字典
        """
        styles = {}

        # 移除注释
        style_sheet = re.sub(r"/\*.*?\*/", "", style_sheet, flags=re.DOTALL)

        # 分割选择器和属性块
        blocks = re.findall(r"([^{]+)\{([^}]+)\}", style_sheet)

        for selector, properties_block in blocks:
            selector = selector.strip()

            # 解析属性
            properties = {}
            property_pairs = re.findall(r"([^:;]+):([^:;]+)(?:;|$)", properties_block)

            for prop, value in property_pairs:
                prop = prop.strip()
                value = value.strip()
                properties[prop] = value

            styles[selector] = properties

        return styles

    def _convert_properties(self, properties: Dict[str, str]) -> Dict[str, Any]:
        """转换属性字典

        Args:
            properties: Qt属性字典

        Returns:
            TTK属性字典
        """
        ttk_properties = {}

        for qt_prop, value in properties.items():
            result = self.convert_single_property(qt_prop, value)
            if result:
                ttk_prop, converted_value = result
                ttk_properties[ttk_prop] = converted_value

        return ttk_properties

    def _convert_color(self, color: str) -> str:
        """转换颜色值

        Args:
            color: Qt颜色值

        Returns:
            TTK颜色值
        """
        color = color.strip()

        # 已经是十六进制颜色
        if color.startswith("#"):
            return color

        # RGB颜色
        rgb_match = re.match(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", color)
        if rgb_match:
            r, g, b = map(int, rgb_match.groups())
            return f"#{r:02x}{g:02x}{b:02x}"

        # RGBA颜色
        rgba_match = re.match(r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*[\d.]+\)", color)
        if rgba_match:
            r, g, b = map(int, rgba_match.groups())
            return f"#{r:02x}{g:02x}{b:02x}"

        # 颜色名称映射
        return self.color_mappings.get(color.lower(), color)

    def _convert_font(self, font: str) -> Tuple[str, int, str, str]:
        """转换字体值

        Args:
            font: Qt字体字符串

        Returns:
            TTK字体元组 (family, size, weight, slant)
        """
        # 默认字体配置
        family = "Arial"
        size = 9
        weight = "normal"
        slant = "roman"

        # 解析字体字符串
        parts = font.split()

        for part in parts:
            part = part.strip(",")

            # 字体大小
            if part.endswith("px") or part.endswith("pt"):
                try:
                    size = int(part[:-2])
                except ValueError:
                    pass
            elif part.isdigit():
                size = int(part)

            # 字体粗细
            elif part.lower() in ["bold", "bolder"]:
                weight = "bold"
            elif part.lower() in ["normal", "lighter"]:
                weight = "normal"

            # 字体样式
            elif part.lower() == "italic" or part.lower() == "oblique":
                slant = "italic"

            # 字体族
            elif part.replace('"', "").replace("'", "") in self.font_mappings:
                family = self.font_mappings[part.replace('"', "").replace("'", "")]
            elif part.lower() not in [
                "bold",
                "italic",
                "normal",
                "bolder",
                "lighter",
                "oblique",
            ]:
                family = part.replace('"', "").replace("'", "")

        return (family, size, weight, slant)

    def _convert_font_family(self, family: str) -> str:
        """转换字体族"""
        family = family.replace('"', "").replace("'", "").strip()
        return self.font_mappings.get(family, family)

    def _convert_font_size(self, size: str) -> int:
        """转换字体大小"""
        if size.endswith("px") or size.endswith("pt"):
            try:
                return int(size[:-2])
            except ValueError:
                return 9
        elif size.isdigit():
            return int(size)
        return 9

    def _convert_font_weight(self, weight: str) -> str:
        """转换字体粗细"""
        weight = weight.lower()
        if weight in ["bold", "bolder", "700", "800", "900"]:
            return "bold"
        return "normal"

    def _convert_font_style(self, style: str) -> str:
        """转换字体样式"""
        style = style.lower()
        if style in ["italic", "oblique"]:
            return "italic"
        return "roman"

    def _convert_border(self, border: str) -> int:
        """转换边框"""
        # 解析边框字符串,提取宽度
        match = re.search(r"(\d+)px", border)
        if match:
            return int(match.group(1))

        # 简单的数字
        if border.isdigit():
            return int(border)

        return 1

    def _convert_border_width(self, width: str) -> int:
        """转换边框宽度"""
        if width.endswith("px"):
            try:
                return int(width[:-2])
            except ValueError:
                return 1
        elif width.isdigit():
            return int(width)
        return 1

    def _convert_border_style(self, style: str) -> str:
        """转换边框样式"""
        style_mapping = {
            "solid": "solid",
            "dashed": "dashed",
            "dotted": "dotted",
            "double": "solid",
            "groove": "groove",
            "ridge": "ridge",
            "inset": "sunken",
            "outset": "raised",
            "none": "flat",
        }
        return style_mapping.get(style.lower(), "solid")

    def _convert_padding(self, padding: str) -> Union[int, Tuple[int, int]]:
        """转换内边距"""
        # 解析内边距值
        values = re.findall(r"\d+", padding)

        if len(values) == 1:
            return int(values[0])
        if len(values) == 2:
            return (int(values[0]), int(values[1]))
        if len(values) == 4:
            # 上右下左 -> 水平垂直
            return (int(values[1]), int(values[0]))

        return 5  # 默认值

    def _convert_size(self, size: str) -> int:
        """转换大小值"""
        if size.endswith("px"):
            try:
                return int(size[:-2])
            except ValueError:
                return 0
        elif size.isdigit():
            return int(size)
        return 0

    def _convert_text_align(self, align: str) -> str:
        """转换文本对齐"""
        align_mapping = {"left": "w", "center": "center", "right": "e", "justify": "w"}
        return align_mapping.get(align.lower(), "w")

    def clear_cache(self) -> None:
        """清理样式缓存"""
        self.style_cache.clear()
        self.logger.debug("清理样式缓存")

    def get_style_mappings(self) -> Dict[str, str]:
        """获取所有样式映射

        Returns:
            样式映射字典
        """
        return {
            qt_prop: mapping.ttk_property
            for qt_prop, mapping in self.style_mappings.items()
        }


# 全局样式适配器实例
_global_style_adapter: Optional[StyleAdapter] = None


def get_global_style_adapter() -> StyleAdapter:
    """获取全局样式适配器实例

    Returns:
        样式适配器
    """
    global _global_style_adapter
    if _global_style_adapter is None:
        _global_style_adapter = StyleAdapter()
    return _global_style_adapter
