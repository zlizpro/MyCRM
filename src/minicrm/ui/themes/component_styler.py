"""MiniCRM 组件样式应用器 - TTK版本

提供统一的TTK组件样式应用机制,确保所有TTK组件都能正确应用主题样式.
完全基于tkinter/ttk,无Qt依赖.
"""

from enum import Enum
import logging
import tkinter as tk
from tkinter import ttk
from typing import Union

from .styles import (
    ComponentSize,
    ComponentStyleGenerator,
    ComponentVariant,
    StyleTokens,
)


# TTK组件类型定义
TTKWidget = Union[tk.Widget, ttk.Widget]
TTKButton = Union[ttk.Button, tk.Button]
TTKEntry = Union[ttk.Entry, tk.Entry]
TTKText = Union[tk.Text, ttk.Treeview]
TTKCombobox = ttk.Combobox
TTKTreeview = ttk.Treeview
TTKFrame = Union[ttk.Frame, tk.Frame]
TTKLabel = Union[ttk.Label, tk.Label]


class StyleClass(Enum):
    """样式类枚举"""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"
    OUTLINE = "outline"
    GHOST = "ghost"
    LINK = "link"


class ComponentStyler:
    """组件样式应用器 - TTK版本

    提供统一的TTK组件样式应用接口,支持:
    - 按钮样式应用
    - 输入框样式应用
    - 容器样式应用
    - 表格样式应用
    - 自定义样式应用
    """

    def __init__(
        self, style_tokens: StyleTokens, style_generator: ComponentStyleGenerator
    ):
        """初始化组件样式应用器

        Args:
            style_tokens: 样式令牌管理器
            style_generator: 组件样式生成器
        """
        self._logger = logging.getLogger(__name__)
        self.tokens = style_tokens
        self.generator = style_generator

    def apply_button_style(
        self,
        button: TTKButton,
        variant: ComponentVariant = ComponentVariant.PRIMARY,
        size: ComponentSize = ComponentSize.MEDIUM,
        style_class: StyleClass | None = None,
    ) -> None:
        """应用按钮样式 - TTK版本

        Args:
            button: TTK按钮组件
            variant: 按钮变体
            size: 按钮尺寸
            style_class: 样式类
        """
        try:
            # 获取主题颜色
            colors = self._get_theme_colors()

            # 根据变体选择颜色
            if variant == ComponentVariant.PRIMARY:
                bg_color = colors.get("primary", "#007BFF")
                fg_color = colors.get("primary_text", "#FFFFFF")
            elif variant == ComponentVariant.SECONDARY:
                bg_color = colors.get("secondary", "#6C757D")
                fg_color = colors.get("secondary_text", "#FFFFFF")
            else:
                bg_color = colors.get("background", "#FFFFFF")
                fg_color = colors.get("text", "#000000")

            # 应用TTK样式
            if isinstance(button, ttk.Button):
                # 为TTK按钮创建自定义样式
                style_name = f"{variant.value}.{size.value}.TButton"
                style = ttk.Style()

                style.configure(
                    style_name,
                    background=bg_color,
                    foreground=fg_color,
                    font=self._get_font_for_size(size),
                )

                button.configure(style=style_name)
            else:
                # 对于tk.Button直接配置
                button.configure(
                    bg=bg_color,
                    fg=fg_color,
                    font=self._get_font_for_size(size),
                    relief="flat",
                    borderwidth=0,
                )

            self._logger.debug(f"按钮样式已应用: {variant.value}, {size.value}")

        except Exception as e:
            self._logger.error(f"应用按钮样式失败: {e}")

    def apply_input_style(
        self,
        input_widget: Union[TTKEntry, TTKText, TTKCombobox],
        size: ComponentSize = ComponentSize.MEDIUM,
        state: str | None = None,
    ) -> None:
        """应用输入框样式 - TTK版本

        Args:
            input_widget: TTK输入框组件
            size: 输入框尺寸
            state: 状态(error, success, warning等)
        """
        try:
            # 获取主题颜色
            colors = self._get_theme_colors()

            bg_color = colors.get("background", "#FFFFFF")
            fg_color = colors.get("text", "#000000")
            border_color = colors.get("border", "#CCCCCC")

            # 根据状态调整颜色
            if state == "error":
                border_color = colors.get("danger", "#DC3545")
            elif state == "success":
                border_color = colors.get("success", "#28A745")
            elif state == "warning":
                border_color = colors.get("warning", "#FFC107")

            # 应用TTK样式
            if isinstance(input_widget, (ttk.Entry, ttk.Combobox)):
                style_name = f"{state or 'normal'}.{size.value}.TEntry"
                style = ttk.Style()

                style.configure(
                    style_name,
                    fieldbackground=bg_color,
                    foreground=fg_color,
                    bordercolor=border_color,
                    font=self._get_font_for_size(size),
                )

                input_widget.configure(style=style_name)
            elif isinstance(input_widget, tk.Text):
                # 对于tk.Text直接配置
                input_widget.configure(
                    bg=bg_color,
                    fg=fg_color,
                    font=self._get_font_for_size(size),
                    relief="solid",
                    borderwidth=1,
                    highlightcolor=border_color,
                )

            self._logger.debug(f"输入框样式已应用: {size.value}")

        except Exception as e:
            self._logger.error(f"应用输入框样式失败: {e}")

    def apply_card_style(
        self, widget: TTKFrame, elevated: bool = False, interactive: bool = False
    ) -> None:
        """应用卡片样式 - TTK版本

        Args:
            widget: TTK组件
            elevated: 是否有阴影效果
            interactive: 是否可交互
        """
        try:
            # 获取主题颜色
            colors = self._get_theme_colors()

            bg_color = colors.get("surface", "#FFFFFF")
            border_color = colors.get("border", "#E0E0E0")

            # 应用基础样式
            if isinstance(widget, ttk.Frame):
                style_name = "Card.TFrame"
                style = ttk.Style()

                style.configure(
                    style_name, background=bg_color, borderwidth=1, relief="solid"
                )

                widget.configure(style=style_name)
            else:
                # 对于tk.Frame直接配置
                widget.configure(
                    bg=bg_color,
                    relief="solid",
                    borderwidth=1,
                    highlightbackground=border_color,
                )

            # 交互效果需要通过事件绑定实现
            if interactive:
                self._add_hover_effect(widget, colors)

            self._logger.debug("卡片样式已应用")

        except Exception as e:
            self._logger.error(f"应用卡片样式失败: {e}")

    def apply_table_style(
        self,
        table: TTKTreeview,
        striped: bool = True,
        hoverable: bool = True,
    ) -> None:
        """应用表格样式 - TTK版本

        Args:
            table: TTK表格组件
            striped: 是否显示斑马纹
            hoverable: 是否支持悬停效果
        """
        try:
            # 获取主题颜色
            colors = self._get_theme_colors()

            # 配置Treeview样式
            style_name = "Custom.Treeview"
            style = ttk.Style()

            style.configure(
                style_name,
                background=colors.get("background", "#FFFFFF"),
                foreground=colors.get("text", "#000000"),
                fieldbackground=colors.get("surface", "#F8F9FA"),
                font=self._get_font_for_size(ComponentSize.MEDIUM),
            )

            # 配置标题样式
            style.configure(
                f"{style_name}.Heading",
                background=colors.get("secondary", "#6C757D"),
                foreground=colors.get("secondary_text", "#FFFFFF"),
                font=self._get_font_for_size(ComponentSize.MEDIUM),
            )

            table.configure(style=style_name)

            # 斑马纹效果
            if striped:
                table.tag_configure(
                    "oddrow", background=colors.get("surface", "#F8F9FA")
                )
                table.tag_configure(
                    "evenrow", background=colors.get("background", "#FFFFFF")
                )

            self._logger.debug("表格样式已应用")

        except Exception as e:
            self._logger.error(f"应用表格样式失败: {e}")

    def apply_container_style(
        self,
        container: TTKFrame,
        padding: str | None = None,
        margin: str | None = None,
        border: bool = False,
    ) -> None:
        """应用容器样式 - TTK版本

        Args:
            container: TTK容器组件
            padding: 内边距
            margin: 外边距
            border: 是否显示边框
        """
        try:
            # 获取主题颜色
            colors = self._get_theme_colors()

            bg_color = colors.get("background", "#FFFFFF")
            border_color = colors.get("border", "#E0E0E0")

            # 应用样式
            if isinstance(container, ttk.Frame):
                style_name = "Container.TFrame"
                style = ttk.Style()

                configure_options = {
                    "background": bg_color,
                }

                if border:
                    configure_options.update({"borderwidth": 1, "relief": "solid"})

                style.configure(style_name, **configure_options)
                container.configure(style=style_name)
            else:
                # 对于tk.Frame直接配置
                configure_options = {
                    "bg": bg_color,
                }

                if border:
                    configure_options.update(
                        {
                            "relief": "solid",
                            "borderwidth": 1,
                            "highlightbackground": border_color,
                        }
                    )

                container.configure(**configure_options)

            self._logger.debug("容器样式已应用")

        except Exception as e:
            self._logger.error(f"应用容器样式失败: {e}")

    def apply_text_style(
        self,
        label: TTKLabel,
        variant: str = "body",
        color: str | None = None,
        weight: str | None = None,
    ) -> None:
        """应用文本样式 - TTK版本

        Args:
            label: TTK文本标签
            variant: 文本变体(heading, title, body, caption等)
            color: 文本颜色
            weight: 字体粗细
        """
        try:
            # 获取主题颜色
            colors = self._get_theme_colors()

            # 字体配置
            font_configs = {
                "title": ("Microsoft YaHei UI", 14, "bold"),
                "heading": ("Microsoft YaHei UI", 12, "bold"),
                "body": ("Microsoft YaHei UI", 9, "normal"),
                "caption": ("Microsoft YaHei UI", 8, "normal"),
                "small": ("Microsoft YaHei UI", 7, "normal"),
            }

            font_config = font_configs.get(variant, font_configs["body"])

            # 文本颜色
            text_color = (
                colors.get(color, colors.get("text", "#000000"))
                if color
                else colors.get("text", "#000000")
            )

            # 应用样式
            if isinstance(label, ttk.Label):
                style_name = f"{variant}.TLabel"
                style = ttk.Style()

                style.configure(style_name, foreground=text_color, font=font_config)

                label.configure(style=style_name)
            else:
                # 对于tk.Label直接配置
                label.configure(fg=text_color, font=font_config)

            self._logger.debug(f"文本样式已应用: {variant}")

        except Exception as e:
            self._logger.error(f"应用文本样式失败: {e}")

    def apply_custom_style(self, widget: TTKWidget, style_dict: dict[str, str]) -> None:
        """应用自定义样式 - TTK版本

        Args:
            widget: TTK组件
            style_dict: 样式字典
        """
        try:
            if hasattr(widget, "configure"):
                # 转换样式属性名
                ttk_options = {}
                for key, value in style_dict.items():
                    # 将CSS样式名转换为TTK选项名
                    if key == "background-color":
                        ttk_options["background"] = value
                    elif key == "color":
                        ttk_options["foreground"] = value
                    elif key == "font-size":
                        # 字体大小需要与字体族一起设置
                        pass
                    else:
                        # 直接使用原始键名
                        ttk_options[key.replace("-", "")] = value

                widget.configure(**ttk_options)

            self._logger.debug("自定义样式已应用")

        except Exception as e:
            self._logger.error(f"应用自定义样式失败: {e}")

    def remove_style(self, widget: TTKWidget) -> None:
        """移除组件样式 - TTK版本

        Args:
            widget: TTK组件
        """
        try:
            if isinstance(widget, ttk.Widget):
                # 重置为默认样式
                widget_class = widget.winfo_class()
                widget.configure(style=f"T{widget_class}")
            # 对于tk组件,重置基本属性
            elif hasattr(widget, "configure"):
                widget.configure(bg="SystemButtonFace", fg="SystemButtonText")

            self._logger.debug("组件样式已移除")

        except Exception as e:
            self._logger.error(f"移除组件样式失败: {e}")

    def _get_font_for_size(self, size: ComponentSize) -> tuple[str, int]:
        """根据尺寸获取字体配置

        Args:
            size: 组件尺寸

        Returns:
            字体配置元组 (family, size)
        """
        font_sizes = {
            ComponentSize.SMALL: 8,
            ComponentSize.MEDIUM: 9,
            ComponentSize.LARGE: 11,
        }

        return ("Microsoft YaHei UI", font_sizes.get(size, 9))

    def _get_theme_colors(self) -> dict[str, str]:
        """获取当前主题颜色

        Returns:
            颜色配置字典
        """
        try:
            if hasattr(self.tokens, "get_semantic_colors"):
                return self.tokens.get_semantic_colors()
            # 默认颜色配置
            return {
                "primary": "#007BFF",
                "primary_text": "#FFFFFF",
                "secondary": "#6C757D",
                "secondary_text": "#FFFFFF",
                "background": "#FFFFFF",
                "surface": "#F8F9FA",
                "text": "#212529",
                "border": "#DEE2E6",
                "success": "#28A745",
                "warning": "#FFC107",
                "danger": "#DC3545",
                "info": "#17A2B8",
            }
        except Exception as e:
            self._logger.warning(f"获取主题颜色失败: {e}")
            return {}

    def _add_hover_effect(self, widget: TTKWidget, colors: dict[str, str]) -> None:
        """为组件添加悬停效果

        Args:
            widget: 目标组件
            colors: 颜色配置
        """
        try:
            original_bg = colors.get("surface", "#FFFFFF")
            hover_bg = colors.get("hover", "#F0F0F0")

            def on_enter(event):
                if hasattr(widget, "configure"):
                    try:
                        widget.configure(bg=hover_bg)
                    except tk.TclError:
                        pass

            def on_leave(event):
                if hasattr(widget, "configure"):
                    try:
                        widget.configure(bg=original_bg)
                    except tk.TclError:
                        pass

            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        except Exception as e:
            self._logger.warning(f"添加悬停效果失败: {e}")


# 导出的公共接口
__all__ = [
    "ComponentStyler",
    "StyleClass",
    "TTKButton",
    "TTKCombobox",
    "TTKEntry",
    "TTKFrame",
    "TTKLabel",
    "TTKText",
    "TTKTreeview",
    "TTKWidget",
]
