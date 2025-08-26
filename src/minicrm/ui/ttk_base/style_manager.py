"""TTK样式管理系统

提供TTK样式配置和主题切换功能,包括:
- TTK样式配置和管理
- 主题切换和自定义主题支持
- 样式模板系统
- 动态样式更新
- 跨平台样式兼容性

设计目标:
1. 提供统一的样式管理接口
2. 支持多主题切换
3. 简化样式配置和应用
4. 确保跨平台兼容性

作者: MiniCRM开发团队
"""

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from enum import Enum
import json
import logging
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional


class ThemeType(Enum):
    """主题类型枚举"""

    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    HIGH_CONTRAST = "high_contrast"
    CUSTOM = "custom"


@dataclass
class ColorScheme:
    """颜色方案数据类"""

    # 主要颜色
    primary: str = "#007BFF"
    secondary: str = "#6C757D"
    success: str = "#28A745"
    warning: str = "#FFC107"
    danger: str = "#DC3545"
    info: str = "#17A2B8"

    # 背景颜色
    bg_primary: str = "#FFFFFF"
    bg_secondary: str = "#F8F9FA"
    bg_tertiary: str = "#E9ECEF"

    # 文本颜色
    text_primary: str = "#212529"
    text_secondary: str = "#6C757D"
    text_muted: str = "#ADB5BD"
    text_white: str = "#FFFFFF"

    # 边框颜色
    border_primary: str = "#DEE2E6"
    border_secondary: str = "#CED4DA"
    border_focus: str = "#80BDFF"

    # 状态颜色
    hover: str = "#E9ECEF"
    active: str = "#007BFF"
    disabled: str = "#6C757D"


@dataclass
class FontConfig:
    """字体配置数据类"""

    family: str = "Microsoft YaHei UI"
    size: int = 9
    weight: str = "normal"
    slant: str = "roman"

    def to_tuple(self) -> tuple:
        """转换为tkinter字体元组"""
        return (self.family, self.size, self.weight, self.slant)


@dataclass
class SpacingConfig:
    """间距配置数据类"""

    # 内边距
    padding_small: int = 2
    padding_medium: int = 5
    padding_large: int = 10

    # 外边距
    margin_small: int = 2
    margin_medium: int = 5
    margin_large: int = 10

    # 边框宽度
    border_width: int = 1
    focus_border_width: int = 2


class BaseTheme(ABC):
    """基础主题抽象类

    定义主题的基本接口和通用功能.
    """

    def __init__(self, name: str):
        """初始化基础主题

        Args:
            name: 主题名称
        """
        self.name = name
        self.colors = ColorScheme()
        self.fonts = {
            "default": FontConfig(),
            "heading": FontConfig(size=12, weight="bold"),
            "small": FontConfig(size=8),
            "large": FontConfig(size=11),
        }
        self.spacing = SpacingConfig()
        self.custom_styles: Dict[str, Dict[str, Any]] = {}

    @abstractmethod
    def configure_colors(self) -> None:
        """配置主题颜色"""

    def configure_fonts(self) -> None:
        """配置主题字体(可选重写)"""

    def configure_spacing(self) -> None:
        """配置主题间距(可选重写)"""

    def get_style_config(self) -> Dict[str, Any]:
        """获取样式配置

        Returns:
            样式配置字典
        """
        return {
            "colors": asdict(self.colors),
            "fonts": {name: asdict(font) for name, font in self.fonts.items()},
            "spacing": asdict(self.spacing),
            "custom_styles": self.custom_styles,
        }

    def apply_to_style(self, style: ttk.Style) -> None:
        """应用主题到TTK样式

        Args:
            style: TTK样式对象
        """
        self.configure_colors()
        self.configure_fonts()
        self.configure_spacing()

        # 应用基础样式
        self._apply_base_styles(style)

        # 应用组件样式
        self._apply_component_styles(style)

        # 应用自定义样式
        self._apply_custom_styles(style)

    def _apply_base_styles(self, style: ttk.Style) -> None:
        """应用基础样式"""
        # 配置默认字体
        default_font = self.fonts["default"].to_tuple()
        style.configure(".", font=default_font)

        # 配置基础颜色
        style.configure(
            ".",
            background=self.colors.bg_primary,
            foreground=self.colors.text_primary,
            bordercolor=self.colors.border_primary,
            focuscolor=self.colors.border_focus,
        )

    def _apply_component_styles(self, style: ttk.Style) -> None:
        """应用组件样式"""
        # Button样式
        style.configure(
            "TButton",
            background=self.colors.primary,
            foreground=self.colors.text_white,
            borderwidth=self.spacing.border_width,
            focuscolor=self.colors.border_focus,
            padding=(self.spacing.padding_medium, self.spacing.padding_small),
        )

        style.map(
            "TButton",
            background=[
                ("active", self.colors.hover),
                ("pressed", self.colors.active),
                ("disabled", self.colors.disabled),
            ],
        )

        # Entry样式
        style.configure(
            "TEntry",
            fieldbackground=self.colors.bg_primary,
            borderwidth=self.spacing.border_width,
            insertcolor=self.colors.text_primary,
            padding=self.spacing.padding_small,
        )

        style.map(
            "TEntry",
            focuscolor=[("focus", self.colors.border_focus)],
            bordercolor=[("focus", self.colors.border_focus)],
        )

        # Label样式
        style.configure(
            "TLabel",
            background=self.colors.bg_primary,
            foreground=self.colors.text_primary,
        )

        # Frame样式
        style.configure("TFrame", background=self.colors.bg_primary, borderwidth=0)

        # Notebook样式
        style.configure(
            "TNotebook",
            background=self.colors.bg_secondary,
            borderwidth=self.spacing.border_width,
        )

        style.configure(
            "TNotebook.Tab",
            background=self.colors.bg_tertiary,
            foreground=self.colors.text_primary,
            padding=(self.spacing.padding_medium, self.spacing.padding_small),
        )

        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", self.colors.bg_primary),
                ("active", self.colors.hover),
            ],
        )

        # Treeview样式
        style.configure(
            "Treeview",
            background=self.colors.bg_primary,
            foreground=self.colors.text_primary,
            fieldbackground=self.colors.bg_primary,
            borderwidth=self.spacing.border_width,
        )

        style.configure(
            "Treeview.Heading",
            background=self.colors.bg_secondary,
            foreground=self.colors.text_primary,
            font=self.fonts["default"].to_tuple(),
        )

        # Scrollbar样式
        style.configure(
            "TScrollbar",
            background=self.colors.bg_secondary,
            troughcolor=self.colors.bg_tertiary,
            borderwidth=0,
            arrowcolor=self.colors.text_secondary,
        )

        # Combobox样式
        style.configure(
            "TCombobox",
            fieldbackground=self.colors.bg_primary,
            background=self.colors.bg_primary,
            foreground=self.colors.text_primary,
            borderwidth=self.spacing.border_width,
            padding=self.spacing.padding_small,
        )

        # Checkbutton样式
        style.configure(
            "TCheckbutton",
            background=self.colors.bg_primary,
            foreground=self.colors.text_primary,
            focuscolor=self.colors.border_focus,
        )

        # Radiobutton样式
        style.configure(
            "TRadiobutton",
            background=self.colors.bg_primary,
            foreground=self.colors.text_primary,
            focuscolor=self.colors.border_focus,
        )

        # Progressbar样式
        style.configure(
            "TProgressbar",
            background=self.colors.primary,
            troughcolor=self.colors.bg_tertiary,
            borderwidth=0,
            lightcolor=self.colors.primary,
            darkcolor=self.colors.primary,
        )

    def _apply_custom_styles(self, style: ttk.Style) -> None:
        """应用自定义样式"""
        for style_name, style_config in self.custom_styles.items():
            style.configure(style_name, **style_config)


class DefaultTheme(BaseTheme):
    """默认主题"""

    def __init__(self):
        super().__init__("default")

    def configure_colors(self) -> None:
        """配置默认主题颜色"""
        # 使用默认的ColorScheme配置


class DarkTheme(BaseTheme):
    """深色主题"""

    def __init__(self):
        super().__init__("dark")

    def configure_colors(self) -> None:
        """配置深色主题颜色"""
        self.colors.bg_primary = "#2B2B2B"
        self.colors.bg_secondary = "#3C3C3C"
        self.colors.bg_tertiary = "#4D4D4D"

        self.colors.text_primary = "#FFFFFF"
        self.colors.text_secondary = "#CCCCCC"
        self.colors.text_muted = "#999999"

        self.colors.border_primary = "#555555"
        self.colors.border_secondary = "#666666"

        self.colors.hover = "#404040"
        self.colors.disabled = "#666666"


class LightTheme(BaseTheme):
    """浅色主题"""

    def __init__(self):
        super().__init__("light")

    def configure_colors(self) -> None:
        """配置浅色主题颜色"""
        self.colors.bg_primary = "#FAFAFA"
        self.colors.bg_secondary = "#F0F0F0"
        self.colors.bg_tertiary = "#E8E8E8"

        self.colors.text_primary = "#333333"
        self.colors.text_secondary = "#666666"

        self.colors.border_primary = "#DDDDDD"
        self.colors.border_secondary = "#CCCCCC"


class HighContrastTheme(BaseTheme):
    """高对比度主题"""

    def __init__(self):
        super().__init__("high_contrast")

    def configure_colors(self) -> None:
        """配置高对比度主题颜色"""
        self.colors.bg_primary = "#FFFFFF"
        self.colors.bg_secondary = "#F0F0F0"
        self.colors.bg_tertiary = "#E0E0E0"

        self.colors.text_primary = "#000000"
        self.colors.text_secondary = "#333333"

        self.colors.primary = "#0000FF"
        self.colors.danger = "#FF0000"
        self.colors.success = "#008000"

        self.colors.border_primary = "#000000"
        self.colors.border_secondary = "#333333"
        self.colors.border_focus = "#0000FF"


class StyleManager:
    """TTK样式管理器

    提供统一的样式管理功能,包括主题切换、
    自定义样式、样式模板等功能.
    """

    def __init__(self, root: Optional[tk.Tk] = None):
        """初始化样式管理器

        Args:
            root: 根窗口对象
        """
        self.root = root
        self.style = ttk.Style()
        self.logger = logging.getLogger(__name__)

        # 主题存储
        self.themes: Dict[str, BaseTheme] = {
            ThemeType.DEFAULT.value: DefaultTheme(),
            ThemeType.DARK.value: DarkTheme(),
            ThemeType.LIGHT.value: LightTheme(),
            ThemeType.HIGH_CONTRAST.value: HighContrastTheme(),
        }

        # 当前主题
        self.current_theme: Optional[BaseTheme] = None

        # 样式模板存储
        self.style_templates: Dict[str, Dict[str, Any]] = {}

        # 主题变化回调
        self.theme_change_callbacks: List[Callable[[str], None]] = []

        # 加载默认主题
        self.apply_theme(ThemeType.DEFAULT.value)

    def register_theme(self, theme: BaseTheme) -> None:
        """注册自定义主题

        Args:
            theme: 主题对象
        """
        self.themes[theme.name] = theme
        self.logger.info(f"注册主题: {theme.name}")

    def apply_theme(self, theme_name: str) -> bool:
        """应用主题

        Args:
            theme_name: 主题名称

        Returns:
            是否应用成功
        """
        if theme_name not in self.themes:
            self.logger.warning(f"主题不存在: {theme_name}")
            return False

        try:
            theme = self.themes[theme_name]
            theme.apply_to_style(self.style)
            self.current_theme = theme

            # 触发主题变化回调
            for callback in self.theme_change_callbacks:
                try:
                    callback(theme_name)
                except Exception as e:
                    self.logger.error(f"主题变化回调执行失败: {e}")

            self.logger.info(f"应用主题: {theme_name}")
            return True

        except Exception as e:
            self.logger.error(f"应用主题失败 [{theme_name}]: {e}")
            return False

    def get_current_theme(self) -> Optional[BaseTheme]:
        """获取当前主题

        Returns:
            当前主题对象
        """
        return self.current_theme

    def get_available_themes(self) -> List[str]:
        """获取可用主题列表

        Returns:
            主题名称列表
        """
        return list(self.themes.keys())

    def create_custom_style(
        self, style_name: str, base_style: Optional[str] = None, **style_options
    ) -> None:
        """创建自定义样式

        Args:
            style_name: 样式名称
            base_style: 基础样式名称
            **style_options: 样式选项
        """
        try:
            if base_style:
                # 基于现有样式创建
                base_config = self.style.configure(base_style)
                if base_config:
                    style_options = {**base_config, **style_options}

            self.style.configure(style_name, **style_options)
            self.logger.debug(f"创建自定义样式: {style_name}")

        except Exception as e:
            self.logger.error(f"创建自定义样式失败 [{style_name}]: {e}")

    def create_style_template(
        self, template_name: str, style_config: Dict[str, Any]
    ) -> None:
        """创建样式模板

        Args:
            template_name: 模板名称
            style_config: 样式配置
        """
        self.style_templates[template_name] = style_config
        self.logger.debug(f"创建样式模板: {template_name}")

    def apply_style_template(
        self, style_name: str, template_name: str, **overrides
    ) -> None:
        """应用样式模板

        Args:
            style_name: 目标样式名称
            template_name: 模板名称
            **overrides: 覆盖选项
        """
        if template_name not in self.style_templates:
            self.logger.warning(f"样式模板不存在: {template_name}")
            return

        try:
            template_config = self.style_templates[template_name].copy()
            template_config.update(overrides)

            self.style.configure(style_name, **template_config)
            self.logger.debug(f"应用样式模板: {style_name} <- {template_name}")

        except Exception as e:
            self.logger.error(f"应用样式模板失败: {e}")

    def configure_widget_style(
        self, widget: tk.Widget, style_name: Optional[str] = None, **style_options
    ) -> None:
        """配置组件样式

        Args:
            widget: 目标组件
            style_name: 样式名称
            **style_options: 样式选项
        """
        try:
            if style_name:
                # 应用命名样式
                if hasattr(widget, "configure"):
                    widget.configure(style=style_name)

            # 应用直接样式选项
            if style_options and hasattr(widget, "configure"):
                widget.configure(**style_options)

        except Exception as e:
            self.logger.error(f"配置组件样式失败: {e}")

    def add_theme_change_callback(self, callback: Callable[[str], None]) -> None:
        """添加主题变化回调

        Args:
            callback: 回调函数,接收主题名称参数
        """
        self.theme_change_callbacks.append(callback)

    def remove_theme_change_callback(self, callback: Callable[[str], None]) -> None:
        """移除主题变化回调

        Args:
            callback: 要移除的回调函数
        """
        if callback in self.theme_change_callbacks:
            self.theme_change_callbacks.remove(callback)

    def save_theme_to_file(self, theme_name: str, file_path: str) -> bool:
        """保存主题到文件

        Args:
            theme_name: 主题名称
            file_path: 文件路径

        Returns:
            是否保存成功
        """
        if theme_name not in self.themes:
            self.logger.warning(f"主题不存在: {theme_name}")
            return False

        try:
            theme = self.themes[theme_name]
            theme_config = theme.get_style_config()

            # 确保目录存在
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(theme_config, f, indent=2, ensure_ascii=False)

            self.logger.info(f"保存主题到文件: {theme_name} -> {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"保存主题失败: {e}")
            return False

    def load_theme_from_file(
        self, file_path: str, theme_name: Optional[str] = None
    ) -> bool:
        """从文件加载主题

        Args:
            file_path: 文件路径
            theme_name: 主题名称,None则使用文件名

        Returns:
            是否加载成功
        """
        if not os.path.exists(file_path):
            self.logger.warning(f"主题文件不存在: {file_path}")
            return False

        try:
            with open(file_path, encoding="utf-8") as f:
                theme_config = json.load(f)

            # 创建自定义主题
            if theme_name is None:
                theme_name = Path(file_path).stem

            custom_theme = CustomTheme(theme_name, theme_config)
            self.register_theme(custom_theme)

            self.logger.info(f"从文件加载主题: {file_path} -> {theme_name}")
            return True

        except Exception as e:
            self.logger.error(f"加载主题失败: {e}")
            return False

    def get_style_info(self, style_name: str) -> Dict[str, Any]:
        """获取样式信息

        Args:
            style_name: 样式名称

        Returns:
            样式信息字典
        """
        try:
            config = self.style.configure(style_name)
            layout = self.style.layout(style_name)
            element_options = {}

            # 获取元素选项
            if layout:
                for element_name, element_config in layout:
                    try:
                        options = self.style.element_options(element_name)
                        element_options[element_name] = options
                    except tk.TclError:
                        pass

            return {
                "configure": config,
                "layout": layout,
                "element_options": element_options,
            }

        except Exception as e:
            self.logger.error(f"获取样式信息失败 [{style_name}]: {e}")
            return {}

    def reset_to_default(self) -> None:
        """重置为默认样式"""
        try:
            # 重新创建样式对象
            self.style = ttk.Style()

            # 应用默认主题
            self.apply_theme(ThemeType.DEFAULT.value)

            self.logger.info("重置为默认样式")

        except Exception as e:
            self.logger.error(f"重置样式失败: {e}")


class CustomTheme(BaseTheme):
    """自定义主题"""

    def __init__(self, name: str, config: Dict[str, Any]):
        """初始化自定义主题

        Args:
            name: 主题名称
            config: 主题配置
        """
        super().__init__(name)
        self._load_config(config)

    def _load_config(self, config: Dict[str, Any]) -> None:
        """加载主题配置

        Args:
            config: 配置字典
        """
        # 加载颜色配置
        if "colors" in config:
            color_config = config["colors"]
            for key, value in color_config.items():
                if hasattr(self.colors, key):
                    setattr(self.colors, key, value)

        # 加载字体配置
        if "fonts" in config:
            font_config = config["fonts"]
            for font_name, font_data in font_config.items():
                self.fonts[font_name] = FontConfig(**font_data)

        # 加载间距配置
        if "spacing" in config:
            spacing_config = config["spacing"]
            for key, value in spacing_config.items():
                if hasattr(self.spacing, key):
                    setattr(self.spacing, key, value)

        # 加载自定义样式
        if "custom_styles" in config:
            self.custom_styles = config["custom_styles"]

    def configure_colors(self) -> None:
        """配置颜色(已在_load_config中处理)"""


# 全局样式管理器实例
_global_style_manager: Optional[StyleManager] = None


def get_global_style_manager() -> StyleManager:
    """获取全局样式管理器实例

    Returns:
        全局样式管理器
    """
    global _global_style_manager
    if _global_style_manager is None:
        _global_style_manager = StyleManager()
    return _global_style_manager


def apply_global_theme(theme_name: str) -> bool:
    """应用全局主题

    Args:
        theme_name: 主题名称

    Returns:
        是否应用成功
    """
    return get_global_style_manager().apply_theme(theme_name)


def create_themed_widget(
    widget_class, parent, theme_style: Optional[str] = None, **kwargs
):
    """创建带主题的组件

    Args:
        widget_class: 组件类
        parent: 父容器
        theme_style: 主题样式名称
        **kwargs: 其他参数

    Returns:
        创建的组件
    """
    widget = widget_class(parent, **kwargs)

    if theme_style and hasattr(widget, "configure"):
        try:
            widget.configure(style=theme_style)
        except tk.TclError:
            pass  # 忽略不支持的样式

    return widget
