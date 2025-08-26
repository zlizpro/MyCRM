"""MiniCRM 主题管理器 - TTK版本

重构后的主题管理器,使用TTK模块化设计.
完全基于TTK,无Qt依赖.
"""

# 导出TTK版本的主题管理器
from ..ttk_base.theme_manager import (
    TTKThemeManager as ThemeManager,
    apply_global_ttk_theme,
    get_global_ttk_theme_manager,
)

# 导出TTK版本的组件样式应用器
from .component_styler import ComponentStyler


# 为了向后兼容,提供一些别名
TTKThemeManager = ThemeManager
get_theme_manager = get_global_ttk_theme_manager
apply_theme = apply_global_ttk_theme

# 保持向后兼容性
__all__ = [
    "ComponentStyler",
    "TTKThemeManager",
    "ThemeManager",
    "apply_global_ttk_theme",
    "apply_theme",
    "get_global_ttk_theme_manager",
    "get_theme_manager",
]
