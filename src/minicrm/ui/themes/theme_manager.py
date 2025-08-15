"""
MiniCRM 主题管理器

重构后的主题管理器，使用模块化设计。
为了保持向后兼容性，这里重新导出新的模块化组件。
"""

# 重新导出新的模块化组件
from .managers.stylesheet_generator import StylesheetGenerator
from .managers.theme_applicator import ThemeApplicator
from .managers.theme_definitions import get_theme_definitions
from .managers.theme_io_manager import ThemeIOManager
from .managers.theme_manager import ThemeManager


# 保持向后兼容性
__all__ = [
    "ThemeManager",
    "StylesheetGenerator",
    "ThemeApplicator",
    "ThemeIOManager",
    "get_theme_definitions",
]
