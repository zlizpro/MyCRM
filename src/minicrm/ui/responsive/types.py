"""
MiniCRM 响应式布局类型定义

包含响应式布局系统使用的枚举、数据类和类型定义。
从 responsive_layout.py 拆分而来，符合MiniCRM模块化标准。
"""

from dataclasses import dataclass
from enum import Enum


class ScreenSize(Enum):
    """屏幕尺寸枚举"""

    SMALL = "small"  # < 1024px
    MEDIUM = "medium"  # 1024px - 1440px
    LARGE = "large"  # 1440px - 1920px
    XLARGE = "xlarge"  # > 1920px


@dataclass
class BreakPoint:
    """断点配置"""

    name: str
    min_width: int
    max_width: int | None = None
    sidebar_width: int = 250
    content_padding: int = 20
    font_scale: float = 1.0
    icon_scale: float = 1.0


@dataclass
class LayoutConfig:
    """布局配置"""

    min_window_width: int = 1024
    min_window_height: int = 768
    sidebar_min_width: int = 200
    sidebar_max_width: int = 400
    content_min_width: int = 600
    toolbar_height: int = 40
    statusbar_height: int = 25
