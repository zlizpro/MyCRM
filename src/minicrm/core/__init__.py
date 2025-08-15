"""
MiniCRM 核心模块

包含应用程序的核心功能，包括：
- 应用程序生命周期管理
- 配置管理
- 日志系统
- 异常处理
- 性能监控
- 工具函数

这个模块为整个MiniCRM应用程序提供基础设施和公共功能。
所有其他模块都可以依赖这个核心模块，但核心模块不应该依赖其他业务模块。
"""

# 版本信息
__version__ = "1.0.0"
__author__ = "MiniCRM Team"

# 导入核心组件，提供便捷的访问接口
# 从transfunctions导入格式化和验证函数（避免重复实现）
from transfunctions.formatting import format_currency, format_date, format_phone
from transfunctions.validation import validate_email, validate_phone

from .config import AppConfig, DatabaseConfig, LoggingConfig, ThemeMode, UIConfig
from .constants import (
    APP_NAME,
    APP_VERSION,
    BOARD_INDUSTRY,
    BUSINESS_RULES,
    COLORS,
    DARK_COLORS,
    DATE_FORMATS,
    DEFAULT_PAGE_SIZE,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    ERROR_MESSAGES,
    FILE_EXTENSIONS,
    FILE_PATHS,
    SUCCESS_MESSAGES,
)
from .exceptions import (
    AuthenticationError,
    BusinessLogicError,
    ConfigurationError,
    DatabaseError,
    FileOperationError,
    MiniCRMError,
    PermissionError,
    ServiceError,
    UIError,
    ValidationError,
    create_user_friendly_message,
    handle_exception,
)
from .logger import MiniCRMLogger, get_logger, setup_logging
from .utils import (
    batch_process,
    clean_string,
    dict_to_flat,
    ensure_directory,
    generate_unique_filename,
    get_file_size_mb,
    safe_get,
    truncate_string,
)

# 导出的公共接口
__all__ = [
    # 配置管理
    "AppConfig",
    "DatabaseConfig",
    "UIConfig",
    "LoggingConfig",
    "ThemeMode",
    # 常量
    "APP_NAME",
    "APP_VERSION",
    "BOARD_INDUSTRY",
    "BUSINESS_RULES",
    "COLORS",
    "DARK_COLORS",
    "DATE_FORMATS",
    "DEFAULT_PAGE_SIZE",
    "DEFAULT_WINDOW_WIDTH",
    "DEFAULT_WINDOW_HEIGHT",
    "ERROR_MESSAGES",
    "FILE_EXTENSIONS",
    "FILE_PATHS",
    "SUCCESS_MESSAGES",
    # 异常处理
    "MiniCRMError",
    "ValidationError",
    "DatabaseError",
    "BusinessLogicError",
    "ConfigurationError",
    "ServiceError",
    "UIError",
    "FileOperationError",
    "AuthenticationError",
    "PermissionError",
    "handle_exception",
    "create_user_friendly_message",
    # 日志系统
    "setup_logging",
    "get_logger",
    "MiniCRMLogger",
    # 工具函数（核心模块）
    "safe_get",
    "clean_string",
    "truncate_string",
    "ensure_directory",
    "get_file_size_mb",
    "dict_to_flat",
    "batch_process",
    "generate_unique_filename",
    # 格式化和验证函数（来自transfunctions）
    "validate_email",
    "validate_phone",
    "format_phone",
    "format_currency",
    "format_date",
]
