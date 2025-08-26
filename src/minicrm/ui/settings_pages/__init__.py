"""
MiniCRM 设置页面模块

包含各种设置页面的实现:
- 通用设置页面
- 主题设置页面
- 数据库设置页面
- 系统设置页面
"""

from .database_settings_page import DatabaseSettingsPage
from .general_settings_page import GeneralSettingsPage
from .system_settings_page import SystemSettingsPage
from .theme_settings_page import ThemeSettingsPage


__all__ = [
    "GeneralSettingsPage",
    "ThemeSettingsPage",
    "DatabaseSettingsPage",
    "SystemSettingsPage",
]
