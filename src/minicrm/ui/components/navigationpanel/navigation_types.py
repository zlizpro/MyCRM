"""
MiniCRM 导航面板类型定义

定义导航面板相关的数据类型和枚举
"""

from dataclasses import dataclass


@dataclass
class NavigationItem:
    """导航项数据类"""

    name: str
    display_name: str
    icon: str | None = None
    parent: str | None = None
    page_name: str | None = None
    children: list["NavigationItem"] | None = None
