"""MiniCRM TTK阴影效果工具

提供TTK兼容的阴影效果实现,替代Qt的QGraphicsDropShadowEffect.
由于TTK不支持原生阴影效果,使用边框和颜色模拟阴影效果.
"""

from enum import Enum
import logging
import tkinter as tk
from tkinter import ttk
from typing import Union


class ShadowSize(Enum):
    """阴影尺寸枚举"""

    NONE = "none"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "xl"


class ShadowDirection(Enum):
    """阴影方向枚举"""

    BOTTOM = "bottom"
    TOP = "top"
    LEFT = "left"
    RIGHT = "right"
    ALL = "all"


class TTKShadowEffects:
    """TTK阴影效果管理器

    提供TTK兼容的阴影效果创建和应用接口.
    由于TTK不支持原生阴影,使用边框和背景色模拟阴影效果.
    """

    def __init__(self):
        """初始化阴影效果管理器"""
        self._logger = logging.getLogger(__name__)

        # 阴影配置 - 使用边框和颜色模拟
        self._shadow_configs = {
            ShadowSize.SMALL: {
                "border_width": 1,
                "border_color": "#E0E0E0",
                "background_offset": "#F5F5F5",
                "relief": "solid",
            },
            ShadowSize.MEDIUM: {
                "border_width": 2,
                "border_color": "#D0D0D0",
                "background_offset": "#F0F0F0",
                "relief": "raised",
            },
            ShadowSize.LARGE: {
                "border_width": 3,
                "border_color": "#C0C0C0",
                "background_offset": "#EEEEEE",
                "relief": "raised",
            },
            ShadowSize.EXTRA_LARGE: {
                "border_width": 4,
                "border_color": "#B0B0B0",
                "background_offset": "#ECECEC",
                "relief": "raised",
            },
        }

    def apply_shadow(
        self,
        widget: Union[tk.Widget, ttk.Widget],
        size: ShadowSize = ShadowSize.MEDIUM,
        direction: ShadowDirection = ShadowDirection.BOTTOM,
    ) -> bool:
        """为组件应用阴影效果 - TTK版本

        Args:
            widget: 目标组件
            size: 阴影尺寸
            direction: 阴影方向

        Returns:
            bool: 是否应用成功
        """
        try:
            if size == ShadowSize.NONE:
                # 移除阴影效果
                return self.remove_shadow(widget)

            # 获取配置
            config = self._shadow_configs.get(
                size, self._shadow_configs[ShadowSize.MEDIUM]
            )

            # 应用阴影样式
            if isinstance(widget, ttk.Widget):
                # 对于TTK组件,使用样式配置
                self._apply_ttk_shadow(widget, config, size)
            else:
                # 对于tk组件,直接配置属性
                self._apply_tk_shadow(widget, config)

            self._logger.debug(f"阴影效果已应用到组件: {widget.__class__.__name__}")
            return True

        except Exception as e:
            self._logger.error(f"应用阴影效果失败: {e}")
            return False

    def _apply_ttk_shadow(
        self, widget: ttk.Widget, config: dict, size: ShadowSize
    ) -> None:
        """为TTK组件应用阴影效果"""
        try:
            # 创建自定义样式
            style_name = f"Shadow.{size.value}.T{widget.winfo_class()}"
            style = ttk.Style()

            # 配置样式
            style.configure(
                style_name,
                borderwidth=config["border_width"],
                relief=config["relief"],
                background=config["background_offset"],
            )

            # 应用样式
            widget.configure(style=style_name)

        except Exception as e:
            self._logger.warning(f"TTK阴影样式应用失败: {e}")

    def _apply_tk_shadow(self, widget: tk.Widget, config: dict) -> None:
        """为tk组件应用阴影效果"""
        try:
            # 直接配置组件属性
            widget.configure(
                relief=config["relief"],
                borderwidth=config["border_width"],
                highlightbackground=config["border_color"],
                highlightthickness=1,
            )

            # 如果组件支持背景色,设置背景色
            if hasattr(widget, "configure"):
                try:
                    widget.configure(bg=config["background_offset"])
                except tk.TclError:
                    # 某些组件可能不支持bg选项
                    pass

        except Exception as e:
            self._logger.warning(f"tk阴影样式应用失败: {e}")

    def remove_shadow(self, widget: Union[tk.Widget, ttk.Widget]) -> bool:
        """移除组件的阴影效果

        Args:
            widget: 目标组件

        Returns:
            bool: 是否移除成功
        """
        try:
            if isinstance(widget, ttk.Widget):
                # 重置为默认样式
                widget_class = widget.winfo_class()
                widget.configure(style=f"T{widget_class}")
            else:
                # 重置tk组件属性
                widget.configure(
                    relief="flat",
                    borderwidth=0,
                    highlightthickness=0,
                )

            self._logger.debug(f"阴影效果已移除: {widget.__class__.__name__}")
            return True

        except Exception as e:
            self._logger.error(f"移除阴影效果失败: {e}")
            return False

    def create_card_shadow_frame(
        self, parent: Union[tk.Widget, ttk.Widget], elevated: bool = False
    ) -> tk.Frame:
        """创建带阴影效果的卡片框架

        Args:
            parent: 父组件
            elevated: 是否为提升状态

        Returns:
            tk.Frame: 带阴影效果的框架
        """
        try:
            # 创建外层框架(阴影层)
            shadow_frame = tk.Frame(parent)

            # 创建内层框架(内容层)
            content_frame = tk.Frame(shadow_frame)

            # 应用阴影效果
            size = ShadowSize.MEDIUM if elevated else ShadowSize.SMALL
            config = self._shadow_configs[size]

            # 配置阴影框架
            shadow_frame.configure(
                bg=config["border_color"], relief="flat", borderwidth=0
            )

            # 配置内容框架
            content_frame.configure(
                bg="white", relief="flat", borderwidth=config["border_width"]
            )

            # 布局内容框架,留出阴影空间
            offset = config["border_width"]
            content_frame.place(
                x=0, y=0, relwidth=1, relheight=1, width=-offset, height=-offset
            )

            return shadow_frame

        except Exception as e:
            self._logger.error(f"创建卡片阴影框架失败: {e}")
            return tk.Frame(parent)

    def apply_button_shadow(
        self, button: Union[tk.Button, ttk.Button], pressed: bool = False
    ) -> bool:
        """为按钮应用阴影效果

        Args:
            button: 按钮组件
            pressed: 是否为按下状态

        Returns:
            bool: 是否应用成功
        """
        size = ShadowSize.SMALL
        if pressed:
            # 按下状态使用更小的阴影或无阴影
            size = ShadowSize.NONE

        return self.apply_shadow(button, size=size)

    def apply_dialog_shadow(self, dialog: Union[tk.Toplevel, tk.Tk]) -> bool:
        """为对话框应用阴影效果

        Args:
            dialog: 对话框组件

        Returns:
            bool: 是否应用成功
        """
        # 对话框使用较大的阴影
        return self.apply_shadow(dialog, size=ShadowSize.LARGE)

    def apply_menu_shadow(self, menu: Union[tk.Menu, ttk.Widget]) -> bool:
        """为菜单应用阴影效果

        Args:
            menu: 菜单组件

        Returns:
            bool: 是否应用成功
        """
        return self.apply_shadow(menu, size=ShadowSize.MEDIUM)

    def create_elevated_style(self, widget_class: str, size: ShadowSize) -> str:
        """创建带阴影的TTK样式

        Args:
            widget_class: 组件类名
            size: 阴影尺寸

        Returns:
            str: 样式名称
        """
        try:
            style_name = f"Elevated.{size.value}.T{widget_class}"
            config = self._shadow_configs.get(
                size, self._shadow_configs[ShadowSize.MEDIUM]
            )

            style = ttk.Style()
            style.configure(
                style_name,
                borderwidth=config["border_width"],
                relief=config["relief"],
            )

            return style_name

        except Exception as e:
            self._logger.error(f"创建阴影样式失败: {e}")
            return f"T{widget_class}"


# 全局阴影效果管理器实例
_shadow_manager: TTKShadowEffects | None = None


def get_shadow_manager() -> TTKShadowEffects:
    """获取全局阴影效果管理器实例

    Returns:
        TTKShadowEffects: 阴影效果管理器
    """
    global _shadow_manager
    if _shadow_manager is None:
        _shadow_manager = TTKShadowEffects()
    return _shadow_manager


def apply_card_shadow(
    widget: Union[tk.Widget, ttk.Widget], elevated: bool = False
) -> bool:
    """为卡片组件应用阴影效果

    Args:
        widget: 卡片组件
        elevated: 是否为提升状态

    Returns:
        bool: 是否应用成功
    """
    manager = get_shadow_manager()
    size = ShadowSize.MEDIUM if elevated else ShadowSize.SMALL
    return manager.apply_shadow(widget, size=size)


def apply_button_shadow(
    widget: Union[tk.Button, ttk.Button], pressed: bool = False
) -> bool:
    """为按钮组件应用阴影效果

    Args:
        widget: 按钮组件
        pressed: 是否为按下状态

    Returns:
        bool: 是否应用成功
    """
    manager = get_shadow_manager()
    return manager.apply_button_shadow(widget, pressed=pressed)


def apply_dialog_shadow(widget: Union[tk.Toplevel, tk.Tk]) -> bool:
    """为对话框组件应用阴影效果

    Args:
        widget: 对话框组件

    Returns:
        bool: 是否应用成功
    """
    manager = get_shadow_manager()
    return manager.apply_dialog_shadow(widget)


def apply_menu_shadow(widget: Union[tk.Menu, ttk.Widget]) -> bool:
    """为菜单组件应用阴影效果

    Args:
        widget: 菜单组件

    Returns:
        bool: 是否应用成功
    """
    manager = get_shadow_manager()
    return manager.apply_menu_shadow(widget)


def remove_shadow(widget: Union[tk.Widget, ttk.Widget]) -> bool:
    """移除组件的阴影效果

    Args:
        widget: 目标组件

    Returns:
        bool: 是否移除成功
    """
    manager = get_shadow_manager()
    return manager.remove_shadow(widget)


def create_card_shadow_frame(
    parent: Union[tk.Widget, ttk.Widget], elevated: bool = False
) -> tk.Frame:
    """创建带阴影效果的卡片框架

    Args:
        parent: 父组件
        elevated: 是否为提升状态

    Returns:
        tk.Frame: 带阴影效果的框架
    """
    manager = get_shadow_manager()
    return manager.create_card_shadow_frame(parent, elevated=elevated)


# 导出的公共接口
__all__ = [
    "ShadowDirection",
    "ShadowSize",
    "TTKShadowEffects",
    "apply_button_shadow",
    "apply_card_shadow",
    "apply_dialog_shadow",
    "apply_menu_shadow",
    "create_card_shadow_frame",
    "get_shadow_manager",
    "remove_shadow",
]
