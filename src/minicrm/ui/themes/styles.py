"""
MiniCRM 统一样式定义

定义了整个应用程序的统一样式规范，包括：
- 颜色规范
- 字体规范
- 间距规范
- 圆角规范
- 阴影规范
- 组件样式模板
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ComponentSize(Enum):
    """组件尺寸枚举"""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class ComponentVariant(Enum):
    """组件变体枚举"""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"


@dataclass
class StyleToken:
    """样式令牌数据类"""

    name: str
    value: str
    description: str = ""


class StyleTokens:
    """
    样式令牌管理器

    定义了设计系统中的所有样式令牌，确保整个应用程序的视觉一致性。
    样式令牌是设计系统的基础，包含颜色、字体、间距等基础样式值。
    """

    def __init__(self, theme_config: dict[str, Any]):
        """
        初始化样式令牌

        Args:
            theme_config: 主题配置字典
        """
        self._theme_config = theme_config
        self._colors = theme_config.get("colors", {})
        self._fonts = theme_config.get("fonts", {})
        self._spacing = theme_config.get("spacing", {})
        self._border_radius = theme_config.get("border_radius", {})
        self._shadows = theme_config.get("shadows", {})

    # 颜色令牌
    def get_color_token(self, name: str, fallback: str = "#000000") -> StyleToken:
        """获取颜色令牌"""
        value = self._colors.get(name, fallback)
        return StyleToken(
            name=f"color-{name}", value=value, description=f"主题颜色: {name}"
        )

    def get_semantic_color(self, semantic: str, fallback: str = "#000000") -> str:
        """获取语义化颜色"""
        semantic_mapping = {
            "text": self._colors.get("text_primary", fallback),
            "text-secondary": self._colors.get("text_secondary", fallback),
            "text-muted": self._colors.get("text_muted", fallback),
            "background": self._colors.get("background", fallback),
            "surface": self._colors.get("surface", fallback),
            "border": self._colors.get("border", fallback),
            "primary": self._colors.get("primary", fallback),
            "success": self._colors.get("success", fallback),
            "warning": self._colors.get("warning", fallback),
            "danger": self._colors.get("danger", fallback),
        }
        return semantic_mapping.get(semantic, fallback)

    # 字体令牌
    def get_font_token(self, name: str, fallback: str = "14px") -> StyleToken:
        """获取字体令牌"""
        value = self._fonts.get(name, fallback)
        return StyleToken(
            name=f"font-{name}", value=value, description=f"字体属性: {name}"
        )

    def get_font_family(self) -> str:
        """获取字体族"""
        return self._fonts.get("family", "Microsoft YaHei UI, Arial, sans-serif")

    def get_font_size(self, size: str) -> str:
        """获取字体大小"""
        return self._fonts.get(f"size_{size}", "14px")

    def get_font_weight(self, weight: str) -> str:
        """获取字体粗细"""
        return self._fonts.get(f"weight_{weight}", "400")

    # 间距令牌
    def get_spacing_token(self, name: str, fallback: str = "8px") -> StyleToken:
        """获取间距令牌"""
        value = self._spacing.get(name, fallback)
        return StyleToken(
            name=f"spacing-{name}", value=value, description=f"间距: {name}"
        )

    def get_spacing(self, size: str) -> str:
        """获取间距值"""
        return self._spacing.get(size, "8px")

    # 圆角令牌
    def get_border_radius_token(self, name: str, fallback: str = "4px") -> StyleToken:
        """获取圆角令牌"""
        value = self._border_radius.get(name, fallback)
        return StyleToken(
            name=f"border-radius-{name}", value=value, description=f"圆角: {name}"
        )

    def get_border_radius(self, size: str) -> str:
        """获取圆角值"""
        return self._border_radius.get(size, "4px")

    # 阴影令牌
    def get_shadow_token(self, name: str, fallback: str = "none") -> StyleToken:
        """获取阴影令牌"""
        value = self._shadows.get(name, fallback)
        return StyleToken(
            name=f"shadow-{name}", value=value, description=f"阴影: {name}"
        )

    def get_shadow(self, size: str) -> str:
        """获取阴影值"""
        return self._shadows.get(size, "none")


class ComponentStyleGenerator:
    """
    组件样式生成器

    基于样式令牌生成具体组件的样式，确保组件样式的一致性和可维护性。
    """

    def __init__(self, style_tokens: StyleTokens):
        """
        初始化组件样式生成器

        Args:
            style_tokens: 样式令牌管理器
        """
        self.tokens = style_tokens

    def generate_button_style(
        self,
        variant: ComponentVariant = ComponentVariant.PRIMARY,
        size: ComponentSize = ComponentSize.MEDIUM,
    ) -> str:
        """
        生成按钮样式

        Args:
            variant: 按钮变体
            size: 按钮尺寸

        Returns:
            str: CSS样式字符串
        """
        # 基础样式
        base_style = f"""
            font-family: {self.tokens.get_font_family()};
            font-weight: {self.tokens.get_font_weight("medium")};
            border: none;
            cursor: pointer;
            transition: all 0.2s ease;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            border-radius: {self.tokens.get_border_radius("medium")};
        """

        # 尺寸样式
        size_styles = {
            ComponentSize.SMALL: f"""
                font-size: {self.tokens.get_font_size("small")};
                padding: {self.tokens.get_spacing("xs")} {self.tokens.get_spacing("sm")};
                min-height: 28px;
            """,
            ComponentSize.MEDIUM: f"""
                font-size: {self.tokens.get_font_size("normal")};
                padding: {self.tokens.get_spacing("sm")} {self.tokens.get_spacing("md")};
                min-height: 36px;
            """,
            ComponentSize.LARGE: f"""
                font-size: {self.tokens.get_font_size("large")};
                padding: {self.tokens.get_spacing("md")} {self.tokens.get_spacing("lg")};
                min-height: 44px;
            """,
        }

        # 变体样式
        variant_styles = {
            ComponentVariant.PRIMARY: f"""
                background-color: {self.tokens.get_semantic_color("primary")};
                color: {self.tokens.get_semantic_color("text")};
            """,
            ComponentVariant.SECONDARY: f"""
                background-color: {self.tokens.get_semantic_color("surface")};
                color: {self.tokens.get_semantic_color("text")};
                border: 1px solid {self.tokens.get_semantic_color("border")};
            """,
            ComponentVariant.SUCCESS: f"""
                background-color: {self.tokens.get_semantic_color("success")};
                color: white;
            """,
            ComponentVariant.WARNING: f"""
                background-color: {self.tokens.get_semantic_color("warning")};
                color: {self.tokens.get_semantic_color("text")};
            """,
            ComponentVariant.DANGER: f"""
                background-color: {self.tokens.get_semantic_color("danger")};
                color: white;
            """,
        }

        return base_style + size_styles[size] + variant_styles[variant]

    def generate_input_style(self, size: ComponentSize = ComponentSize.MEDIUM) -> str:
        """
        生成输入框样式

        Args:
            size: 输入框尺寸

        Returns:
            str: CSS样式字符串
        """
        base_style = f"""
            font-family: {self.tokens.get_font_family()};
            background-color: {self.tokens.get_semantic_color("background")};
            border: 1px solid {self.tokens.get_semantic_color("border")};
            border-radius: {self.tokens.get_border_radius("small")};
            color: {self.tokens.get_semantic_color("text")};
            transition: border-color 0.2s ease;
        """

        size_styles = {
            ComponentSize.SMALL: f"""
                font-size: {self.tokens.get_font_size("small")};
                padding: {self.tokens.get_spacing("xs")} {self.tokens.get_spacing("sm")};
                min-height: 28px;
            """,
            ComponentSize.MEDIUM: f"""
                font-size: {self.tokens.get_font_size("normal")};
                padding: {self.tokens.get_spacing("sm")} {self.tokens.get_spacing("md")};
                min-height: 36px;
            """,
            ComponentSize.LARGE: f"""
                font-size: {self.tokens.get_font_size("large")};
                padding: {self.tokens.get_spacing("md")} {self.tokens.get_spacing("lg")};
                min-height: 44px;
            """,
        }

        return base_style + size_styles[size]

    def generate_card_style(self) -> str:
        """生成卡片样式"""
        return f"""
            background-color: {self.tokens.get_semantic_color("surface")};
            border: 1px solid {self.tokens.get_semantic_color("border")};
            border-radius: {self.tokens.get_border_radius("medium")};
            box-shadow: {self.tokens.get_shadow("small")};
            padding: {self.tokens.get_spacing("md")};
        """

    def generate_table_style(self) -> str:
        """生成表格样式"""
        return f"""
            background-color: {self.tokens.get_semantic_color("background")};
            border: 1px solid {self.tokens.get_semantic_color("border")};
            border-radius: {self.tokens.get_border_radius("medium")};
            font-family: {self.tokens.get_font_family()};
            font-size: {self.tokens.get_font_size("normal")};
        """

    def generate_menu_style(self) -> str:
        """生成菜单样式"""
        return f"""
            background-color: {self.tokens.get_semantic_color("surface")};
            border: 1px solid {self.tokens.get_semantic_color("border")};
            border-radius: {self.tokens.get_border_radius("medium")};
            box-shadow: {self.tokens.get_shadow("medium")};
            padding: {self.tokens.get_spacing("xs")};
        """

    def generate_dialog_style(self) -> str:
        """生成对话框样式"""
        return f"""
            background-color: {self.tokens.get_semantic_color("background")};
            border: 1px solid {self.tokens.get_semantic_color("border")};
            border-radius: {self.tokens.get_border_radius("large")};
            box-shadow: {self.tokens.get_shadow("large")};
            padding: {self.tokens.get_spacing("lg")};
        """


class StyleGuide:
    """
    样式指南

    提供设计系统的样式指南和最佳实践，帮助开发者正确使用样式系统。
    """

    @staticmethod
    def get_color_guidelines() -> dict[str, str]:
        """获取颜色使用指南"""
        return {
            "primary": "用于主要操作按钮、链接和重要元素",
            "secondary": "用于次要操作和辅助元素",
            "success": "用于成功状态、确认操作和正面反馈",
            "warning": "用于警告状态、需要注意的信息",
            "danger": "用于错误状态、危险操作和负面反馈",
            "info": "用于信息提示和中性反馈",
            "text_primary": "用于主要文本内容",
            "text_secondary": "用于次要文本和说明文字",
            "text_muted": "用于弱化文本和占位符",
            "background": "用于页面主背景",
            "surface": "用于卡片、面板等表面背景",
            "border": "用于边框和分割线",
        }

    @staticmethod
    def get_typography_guidelines() -> dict[str, str]:
        """获取字体使用指南"""
        return {
            "size_xs": "用于辅助信息、标签等小号文字",
            "size_small": "用于次要信息、说明文字",
            "size_normal": "用于正文内容、表单输入",
            "size_large": "用于重要信息、子标题",
            "size_xl": "用于页面标题、重要标题",
            "size_heading": "用于章节标题",
            "size_title": "用于页面主标题",
            "weight_light": "用于大段文字阅读",
            "weight_normal": "用于正文内容",
            "weight_medium": "用于重要信息强调",
            "weight_bold": "用于标题和重点强调",
            "weight_black": "用于主标题和品牌文字",
        }

    @staticmethod
    def get_spacing_guidelines() -> dict[str, str]:
        """获取间距使用指南"""
        return {
            "xs": "用于紧密相关元素间的小间距",
            "sm": "用于相关元素间的标准间距",
            "md": "用于组件内部的标准间距",
            "lg": "用于组件间的标准间距",
            "xl": "用于区块间的大间距",
            "xxl": "用于页面级别的大间距",
        }

    @staticmethod
    def get_component_guidelines() -> dict[str, str]:
        """获取组件使用指南"""
        return {
            "buttons": "使用合适的变体和尺寸，保持操作层级清晰",
            "inputs": "保持一致的尺寸和样式，提供清晰的状态反馈",
            "cards": "用于组织相关内容，保持适当的内边距",
            "tables": "保持良好的可读性和交互性",
            "menus": "提供清晰的层级结构和导航",
            "dialogs": "保持适当的尺寸和内容组织",
        }


def create_style_system(
    theme_config: dict[str, Any],
) -> tuple[StyleTokens, ComponentStyleGenerator]:
    """
    创建样式系统

    Args:
        theme_config: 主题配置

    Returns:
        tuple: (样式令牌管理器, 组件样式生成器)
    """
    style_tokens = StyleTokens(theme_config)
    component_generator = ComponentStyleGenerator(style_tokens)
    return style_tokens, component_generator


# 导出的公共接口
__all__ = [
    "ComponentSize",
    "ComponentVariant",
    "StyleToken",
    "StyleTokens",
    "ComponentStyleGenerator",
    "StyleGuide",
    "create_style_system",
]
