"""
MiniCRM配置管理模块

提供应用程序配置的加载、验证、保存和管理功能.
支持JSON格式的配置文件,提供默认配置和用户自定义配置的合并.
"""

from .settings import (
    ConfigManager,
    ApplicationConfig,
    DatabaseConfig,
    UIConfig,
    LoggingConfig,
    ValidationConfig,
    BusinessConfig,
    DocumentConfig,
)

__all__ = [
    "ConfigManager",
    "ApplicationConfig",
    "DatabaseConfig",
    "UIConfig",
    "LoggingConfig",
    "ValidationConfig",
    "BusinessConfig",
    "DocumentConfig",
]
