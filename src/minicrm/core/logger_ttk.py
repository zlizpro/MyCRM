"""MiniCRM 日志配置模块 - TTK版本

提供统一的日志配置和管理功能,使用Python标准库替代Qt依赖
"""

import logging
import logging.handlers
import os
from pathlib import Path
import platform


def get_standard_paths() -> dict[str, Path]:
    """获取标准路径 - 替代Qt的QStandardPaths

    Returns:
        dict[str, Path]: 标准路径字典
    """
    system = platform.system()
    home = Path.home()

    if system == "Windows":
        app_data = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
        local_app_data = Path(
            os.environ.get("LOCALAPPDATA", home / "AppData" / "Local")
        )
        return {
            "config": app_data,
            "data": local_app_data,
            "cache": local_app_data,
            "temp": Path(os.environ.get("TEMP", "/tmp")),
            "documents": home / "Documents",
        }
    if system == "Darwin":  # macOS
        return {
            "config": home / "Library" / "Preferences",
            "data": home / "Library" / "Application Support",
            "cache": home / "Library" / "Caches",
            "temp": Path("/tmp"),
            "documents": home / "Documents",
        }
    # Linux and other Unix-like systems
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
    data_home = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share"))
    cache_home = Path(os.environ.get("XDG_CACHE_HOME", home / ".cache"))
    return {
        "config": config_home,
        "data": data_home,
        "cache": cache_home,
        "temp": Path("/tmp"),
        "documents": home / "Documents",
    }


def setup_logging(
    level: str = "INFO",
    console_enabled: bool = True,
    file_enabled: bool = True,
    log_file: Path | None = None,
    max_file_size_mb: int = 10,
    backup_count: int = 5,
    format_string: str | None = None,
) -> logging.Logger:
    """设置应用程序日志配置

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_enabled: 是否启用控制台输出
        file_enabled: 是否启用文件输出
        log_file: 日志文件路径,如果为None则使用默认路径
        max_file_size_mb: 单个日志文件最大大小(MB)
        backup_count: 保留的备份文件数量
        format_string: 自定义日志格式字符串

    Returns:
        logging.Logger: 配置好的根日志记录器
    """
    # 获取根日志记录器
    root_logger = logging.getLogger()

    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 设置日志级别
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)

    # 设置日志格式
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )

    formatter = logging.Formatter(format_string)

    # 控制台处理器
    if console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # 文件处理器
    if file_enabled:
        if log_file is None:
            # 使用默认日志文件路径
            standard_paths = get_standard_paths()
            log_dir = standard_paths["data"] / "MiniCRM" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "minicrm.log"
        else:
            # 确保日志文件目录存在
            log_file.parent.mkdir(parents=True, exist_ok=True)

        # 使用RotatingFileHandler进行日志轮转
        max_bytes = max_file_size_mb * 1024 * 1024
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # 记录配置信息
    root_logger.info(f"日志系统已初始化 - 级别: {level}")
    if file_enabled and log_file:
        root_logger.info(f"日志文件: {log_file}")

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name)


def set_log_level(level: str) -> None:
    """动态设置日志级别

    Args:
        level: 新的日志级别
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # 同时更新所有处理器的级别
    for handler in root_logger.handlers:
        handler.setLevel(numeric_level)


def add_file_handler(
    log_file: Path,
    level: str = "INFO",
    max_file_size_mb: int = 10,
    backup_count: int = 5,
) -> None:
    """添加额外的文件处理器

    Args:
        log_file: 日志文件路径
        level: 日志级别
        max_file_size_mb: 最大文件大小(MB)
        backup_count: 备份文件数量
    """
    root_logger = logging.getLogger()

    # 确保目录存在
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # 创建文件处理器
    max_bytes = max_file_size_mb * 1024 * 1024
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )

    # 设置级别和格式
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    file_handler.setLevel(numeric_level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # 添加到根日志记录器
    root_logger.addHandler(file_handler)


def configure_module_logger(
    module_name: str,
    level: str | None = None,
    file_path: Path | None = None,
) -> logging.Logger:
    """配置特定模块的日志记录器

    Args:
        module_name: 模块名称
        level: 日志级别,如果为None则使用根日志记录器的级别
        file_path: 专用日志文件路径

    Returns:
        logging.Logger: 配置好的模块日志记录器
    """
    logger = logging.getLogger(module_name)

    if level is not None:
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(numeric_level)

    if file_path is not None:
        add_file_handler(file_path, level or "INFO")

    return logger


class MiniCRMLogger:
    """MiniCRM日志记录器包装类 - TTK版本"""

    def __init__(self, name: str):
        """初始化日志记录器

        Args:
            name: 日志记录器名称
        """
        self._logger = logging.getLogger(name)
        self._name = name

    def debug(self, message: str, *args, **kwargs) -> None:
        """记录调试信息"""
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """记录信息"""
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """记录警告"""
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """记录错误"""
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """记录严重错误"""
        self._logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """记录异常信息"""
        self._logger.exception(message, *args, **kwargs)

    @property
    def name(self) -> str:
        """获取日志记录器名称"""
        return self._name

    @property
    def level(self) -> int:
        """获取日志级别"""
        return self._logger.level

    def set_level(self, level: str) -> None:
        """设置日志级别"""
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        self._logger.setLevel(numeric_level)


# 便捷函数
def get_minicrm_logger(name: str) -> MiniCRMLogger:
    """获取MiniCRM日志记录器实例

    Args:
        name: 日志记录器名称

    Returns:
        MiniCRMLogger: 日志记录器实例
    """
    return MiniCRMLogger(name)


# 为了兼容性,保持原有的函数名
def get_app_data_dir() -> Path:
    """获取应用数据目录"""
    standard_paths = get_standard_paths()
    app_data_dir = standard_paths["data"] / "MiniCRM"
    app_data_dir.mkdir(parents=True, exist_ok=True)
    return app_data_dir


def get_log_dir() -> Path:
    """获取日志目录"""
    log_dir = get_app_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir
