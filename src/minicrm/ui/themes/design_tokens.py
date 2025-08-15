"""
MiniCRM 设计令牌规范

定义了MiniCRM设计系统的核心设计令牌，包括：
- 颜色系统
- 字体系统
- 间距系统
- 圆角系统
- 阴影系统
- 动画系统

这些设计令牌确保整个应用程序的视觉一致性和品牌统一性。
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ColorPalette:
    """颜色调色板"""

    # 主色调
    primary_50: str = "#E3F2FD"
    primary_100: str = "#BBDEFB"
    primary_200: str = "#90CAF9"
    primary_300: str = "#64B5F6"
    primary_400: str = "#42A5F5"
    primary_500: str = "#2196F3"  # 主品牌色
    primary_600: str = "#1E88E5"
    primary_700: str = "#1976D2"
    primary_800: str = "#1565C0"
    primary_900: str = "#0D47A1"

    # 中性色调
    neutral_0: str = "#FFFFFF"
    neutral_50: str = "#FAFAFA"
    neutral_100: str = "#F5F5F5"
    neutral_200: str = "#EEEEEE"
    neutral_300: str = "#E0E0E0"
    neutral_400: str = "#BDBDBD"
    neutral_500: str = "#9E9E9E"
    neutral_600: str = "#757575"
    neutral_700: str = "#616161"
    neutral_800: str = "#424242"
    neutral_900: str = "#212121"

    # 语义色调
    success: str = "#4CAF50"
    success_light: str = "#81C784"
    success_dark: str = "#388E3C"

    warning: str = "#FF9800"
    warning_light: str = "#FFB74D"
    warning_dark: str = "#F57C00"

    error: str = "#F44336"
    error_light: str = "#E57373"
    error_dark: str = "#D32F2F"

    info: str = "#2196F3"
    info_light: str = "#64B5F6"
    info_dark: str = "#1976D2"


@dataclass
class TypographyScale:
    """字体比例系统"""

    # 字体大小（基于16px基准）
    xs: str = "12px"  # 0.75rem
    sm: str = "14px"  # 0.875rem
    base: str = "16px"  # 1rem
    lg: str = "18px"  # 1.125rem
    xl: str = "20px"  # 1.25rem
    xl2: str = "24px"  # 1.5rem
    xl3: str = "30px"  # 1.875rem
    xl4: str = "36px"  # 2.25rem
    xl5: str = "48px"  # 3rem
    xl6: str = "60px"  # 3.75rem

    # 行高
    tight: str = "1.25"
    snug: str = "1.375"
    normal: str = "1.5"
    relaxed: str = "1.625"
    loose: str = "2"

    # 字重
    thin: str = "100"
    extralight: str = "200"
    light: str = "300"
    normal_weight: str = "400"
    medium: str = "500"
    semibold: str = "600"
    bold: str = "700"
    extrabold: str = "800"
    black: str = "900"


@dataclass
class SpacingScale:
    """间距比例系统"""

    # 基于4px网格系统
    px: str = "1px"
    xs: str = "4px"  # 0.25rem
    sm: str = "8px"  # 0.5rem
    md: str = "12px"  # 0.75rem
    base: str = "16px"  # 1rem
    lg: str = "20px"  # 1.25rem
    xl: str = "24px"  # 1.5rem
    xl2: str = "32px"  # 2rem
    xl3: str = "48px"  # 3rem
    xl4: str = "64px"  # 4rem
    xl5: str = "80px"  # 5rem
    xl6: str = "96px"  # 6rem


@dataclass
class BorderRadiusScale:
    """圆角比例系统"""

    none: str = "0px"
    sm: str = "2px"
    base: str = "4px"
    md: str = "6px"
    lg: str = "8px"
    xl: str = "12px"
    xl2: str = "16px"
    xl3: str = "24px"
    full: str = "9999px"


@dataclass
class ShadowScale:
    """阴影比例系统"""

    none: str = "none"
    sm: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    base: str = "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)"
    md: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    lg: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    xl: str = (
        "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)"
    )
    xl2: str = "0 25px 50px -12px rgba(0, 0, 0, 0.25)"
    inner: str = "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)"


@dataclass
class AnimationTokens:
    """动画令牌"""

    # 动画时长
    duration_fast: str = "150ms"
    duration_base: str = "200ms"
    duration_slow: str = "300ms"
    duration_slower: str = "500ms"

    # 动画缓动
    ease_linear: str = "linear"
    ease_in: str = "cubic-bezier(0.4, 0, 1, 1)"
    ease_out: str = "cubic-bezier(0, 0, 0.2, 1)"
    ease_in_out: str = "cubic-bezier(0.4, 0, 0.2, 1)"


class DesignTokens:
    """
    设计令牌管理器

    统一管理所有设计令牌，提供一致的访问接口。
    """

    def __init__(self):
        """初始化设计令牌"""
        self.colors = ColorPalette()
        self.typography = TypographyScale()
        self.spacing = SpacingScale()
        self.border_radius = BorderRadiusScale()
        self.shadows = ShadowScale()
        self.animations = AnimationTokens()

    def to_css_variables(self) -> str:
        """
        生成CSS自定义属性（CSS变量）

        Returns:
            str: CSS变量定义字符串
        """
        css_vars = [":root {"]

        # 颜色变量
        css_vars.extend(
            [
                f"  --color-primary-50: {self.colors.primary_50};",
                f"  --color-primary-100: {self.colors.primary_100};",
                f"  --color-primary-200: {self.colors.primary_200};",
                f"  --color-primary-300: {self.colors.primary_300};",
                f"  --color-primary-400: {self.colors.primary_400};",
                f"  --color-primary-500: {self.colors.primary_500};",
                f"  --color-primary-600: {self.colors.primary_600};",
                f"  --color-primary-700: {self.colors.primary_700};",
                f"  --color-primary-800: {self.colors.primary_800};",
                f"  --color-primary-900: {self.colors.primary_900};",
                "",
                f"  --color-neutral-0: {self.colors.neutral_0};",
                f"  --color-neutral-50: {self.colors.neutral_50};",
                f"  --color-neutral-100: {self.colors.neutral_100};",
                f"  --color-neutral-200: {self.colors.neutral_200};",
                f"  --color-neutral-300: {self.colors.neutral_300};",
                f"  --color-neutral-400: {self.colors.neutral_400};",
                f"  --color-neutral-500: {self.colors.neutral_500};",
                f"  --color-neutral-600: {self.colors.neutral_600};",
                f"  --color-neutral-700: {self.colors.neutral_700};",
                f"  --color-neutral-800: {self.colors.neutral_800};",
                f"  --color-neutral-900: {self.colors.neutral_900};",
                "",
                f"  --color-success: {self.colors.success};",
                f"  --color-success-light: {self.colors.success_light};",
                f"  --color-success-dark: {self.colors.success_dark};",
                f"  --color-warning: {self.colors.warning};",
                f"  --color-warning-light: {self.colors.warning_light};",
                f"  --color-warning-dark: {self.colors.warning_dark};",
                f"  --color-error: {self.colors.error};",
                f"  --color-error-light: {self.colors.error_light};",
                f"  --color-error-dark: {self.colors.error_dark};",
                f"  --color-info: {self.colors.info};",
                f"  --color-info-light: {self.colors.info_light};",
                f"  --color-info-dark: {self.colors.info_dark};",
            ]
        )

        # 字体变量
        css_vars.extend(
            [
                "",
                f"  --font-size-xs: {self.typography.xs};",
                f"  --font-size-sm: {self.typography.sm};",
                f"  --font-size-base: {self.typography.base};",
                f"  --font-size-lg: {self.typography.lg};",
                f"  --font-size-xl: {self.typography.xl};",
                f"  --font-size-2xl: {self.typography.xl2};",
                f"  --font-size-3xl: {self.typography.xl3};",
                f"  --font-size-4xl: {self.typography.xl4};",
                f"  --font-size-5xl: {self.typography.xl5};",
                f"  --font-size-6xl: {self.typography.xl6};",
                "",
                f"  --line-height-tight: {self.typography.tight};",
                f"  --line-height-snug: {self.typography.snug};",
                f"  --line-height-normal: {self.typography.normal};",
                f"  --line-height-relaxed: {self.typography.relaxed};",
                f"  --line-height-loose: {self.typography.loose};",
                "",
                f"  --font-weight-thin: {self.typography.thin};",
                f"  --font-weight-extralight: {self.typography.extralight};",
                f"  --font-weight-light: {self.typography.light};",
                f"  --font-weight-normal: {self.typography.normal_weight};",
                f"  --font-weight-medium: {self.typography.medium};",
                f"  --font-weight-semibold: {self.typography.semibold};",
                f"  --font-weight-bold: {self.typography.bold};",
                f"  --font-weight-extrabold: {self.typography.extrabold};",
                f"  --font-weight-black: {self.typography.black};",
            ]
        )

        # 间距变量
        css_vars.extend(
            [
                "",
                f"  --spacing-px: {self.spacing.px};",
                f"  --spacing-xs: {self.spacing.xs};",
                f"  --spacing-sm: {self.spacing.sm};",
                f"  --spacing-md: {self.spacing.md};",
                f"  --spacing-base: {self.spacing.base};",
                f"  --spacing-lg: {self.spacing.lg};",
                f"  --spacing-xl: {self.spacing.xl};",
                f"  --spacing-2xl: {self.spacing.xl2};",
                f"  --spacing-3xl: {self.spacing.xl3};",
                f"  --spacing-4xl: {self.spacing.xl4};",
                f"  --spacing-5xl: {self.spacing.xl5};",
                f"  --spacing-6xl: {self.spacing.xl6};",
            ]
        )

        # 圆角变量
        css_vars.extend(
            [
                "",
                f"  --border-radius-none: {self.border_radius.none};",
                f"  --border-radius-sm: {self.border_radius.sm};",
                f"  --border-radius-base: {self.border_radius.base};",
                f"  --border-radius-md: {self.border_radius.md};",
                f"  --border-radius-lg: {self.border_radius.lg};",
                f"  --border-radius-xl: {self.border_radius.xl};",
                f"  --border-radius-2xl: {self.border_radius.xl2};",
                f"  --border-radius-3xl: {self.border_radius.xl3};",
                f"  --border-radius-full: {self.border_radius.full};",
            ]
        )

        # 阴影变量
        css_vars.extend(
            [
                "",
                f"  --shadow-none: {self.shadows.none};",
                f"  --shadow-sm: {self.shadows.sm};",
                f"  --shadow-base: {self.shadows.base};",
                f"  --shadow-md: {self.shadows.md};",
                f"  --shadow-lg: {self.shadows.lg};",
                f"  --shadow-xl: {self.shadows.xl};",
                f"  --shadow-2xl: {self.shadows.xl2};",
                f"  --shadow-inner: {self.shadows.inner};",
            ]
        )

        # 动画变量
        css_vars.extend(
            [
                "",
                f"  --duration-fast: {self.animations.duration_fast};",
                f"  --duration-base: {self.animations.duration_base};",
                f"  --duration-slow: {self.animations.duration_slow};",
                f"  --duration-slower: {self.animations.duration_slower};",
                "",
                f"  --ease-linear: {self.animations.ease_linear};",
                f"  --ease-in: {self.animations.ease_in};",
                f"  --ease-out: {self.animations.ease_out};",
                f"  --ease-in-out: {self.animations.ease_in_out};",
            ]
        )

        css_vars.append("}")
        return "\n".join(css_vars)

    def to_theme_config(self) -> dict[str, Any]:
        """
        转换为主题配置格式

        Returns:
            Dict[str, Any]: 主题配置字典
        """
        return {
            "colors": {
                # 主要颜色
                "primary": self.colors.primary_500,
                "primary_light": self.colors.primary_300,
                "primary_dark": self.colors.primary_700,
                "secondary": self.colors.neutral_600,
                "success": self.colors.success,
                "warning": self.colors.warning,
                "danger": self.colors.error,
                "info": self.colors.info,
                # 背景颜色
                "background": self.colors.neutral_0,
                "surface": self.colors.neutral_50,
                "surface_variant": self.colors.neutral_100,
                "card": self.colors.neutral_0,
                # 文本颜色
                "text_primary": self.colors.neutral_900,
                "text_secondary": self.colors.neutral_600,
                "text_muted": self.colors.neutral_400,
                "text_disabled": self.colors.neutral_300,
                "text_on_primary": self.colors.neutral_0,
                "text_on_dark": self.colors.neutral_0,
                # 边框颜色
                "border": self.colors.neutral_300,
                "border_light": self.colors.neutral_200,
                "border_dark": self.colors.neutral_400,
                "border_focus": self.colors.primary_300,
                # 状态颜色
                "hover": self.colors.neutral_50,
                "active": self.colors.neutral_100,
                "focus": self.colors.primary_300,
                "selected": self.colors.primary_50,
                "disabled": self.colors.neutral_100,
            },
            "fonts": {
                "family": "Microsoft YaHei UI, 'Segoe UI', Arial, sans-serif",
                "family_monospace": "'Consolas', 'Monaco', 'Courier New', monospace",
                "size_xs": self.typography.xs,
                "size_small": self.typography.sm,
                "size_normal": self.typography.base,
                "size_large": self.typography.lg,
                "size_xl": self.typography.xl,
                "size_heading": self.typography.xl2,
                "size_title": self.typography.xl3,
                "weight_light": self.typography.light,
                "weight_normal": self.typography.normal_weight,
                "weight_medium": self.typography.medium,
                "weight_bold": self.typography.semibold,
                "weight_black": self.typography.bold,
                "line_height_tight": self.typography.tight,
                "line_height_normal": self.typography.normal,
                "line_height_loose": self.typography.loose,
            },
            "spacing": {
                "xs": self.spacing.xs,
                "sm": self.spacing.sm,
                "md": self.spacing.base,
                "lg": self.spacing.xl,
                "xl": self.spacing.xl2,
                "xxl": self.spacing.xl3,
            },
            "border_radius": {
                "none": self.border_radius.none,
                "small": self.border_radius.base,
                "medium": self.border_radius.md,
                "large": self.border_radius.lg,
                "xl": self.border_radius.xl,
                "round": self.border_radius.full,
            },
            "shadows": {
                "none": self.shadows.none,
                "small": self.shadows.sm,
                "medium": self.shadows.base,
                "large": self.shadows.md,
                "xl": self.shadows.lg,
            },
        }


# 全局设计令牌实例
design_tokens = DesignTokens()

# 导出的公共接口
__all__ = [
    "ColorPalette",
    "TypographyScale",
    "SpacingScale",
    "BorderRadiusScale",
    "ShadowScale",
    "AnimationTokens",
    "DesignTokens",
    "design_tokens",
]
