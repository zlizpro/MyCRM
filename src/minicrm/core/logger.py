"""MiniCRM 日志系统

提供统一的日志记录功能,支持:
- 控制台输出
- 文件输出
- 日志轮转
- 不同级别的日志
- 中文友好的日志格式
"""

import logging
import logging.handlers
import os
from pathlib import Path
import platform
import sys


def _get_app_data_dir() -> Path:
    """获取应用程序数据目录 - 替代Qt的QStandardPaths"""
    system = platform.system()

    if system == "Windows":
        # Windows: %APPDATA%/MiniCRM
        base_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
        return Path(base_dir) / "MiniCRM"
    if system == "Darwin":
        # macOS: ~/Library/Application Support/MiniCRM
        return Path.home() / "Library" / "Application Support" / "MiniCRM"
    # Linux/Unix: ~/.local/share/MiniCRM
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home) / "MiniCRM"
    return Path.home() / ".local" / "share" / "MiniCRM"


def setup_logging(
    level: str = "INFO",
    console_enabled: bool = True,
    file_enabled: bool = True,
    log_file: Path | None = None,
    max_file_size_mb: int = 10,
    backup_count: int = 5,
) -> None:
    """设置应用程序日志系统

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_enabled: 是否启用控制台输出
        file_enabled: 是否启用文件输出
        log_file: 日志文件路径,如果为None则使用默认路径
        max_file_size_mb: 单个日志文件最大大小(MB)
        backup_count: 保留的日志文件数量
    """
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 创建日志格式器
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台处理器
    if console_enabled:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # 文件处理器
    if file_enabled:
        if log_file is None:
            # 使用默认日志文件路径
            app_data_dir = _get_app_data_dir()
            app_data_dir.mkdir(parents=True, exist_ok=True)
            logs_dir = app_data_dir / "logs"
            logs_dir.mkdir(exist_ok=True)
            log_file = logs_dir / "minicrm.log"

        # 使用轮转文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_file_size_mb * 1024 * 1024,  # 转换为字节
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # 记录日志系统初始化完成
    logger = logging.getLogger(__name__)
    logger.info("日志系统初始化完成")
    logger.info(f"日志级别: {level}")
    logger.info(f"控制台输出: {'启用' if console_enabled else '禁用'}")
    logger.info(f"文件输出: {'启用' if file_enabled else '禁用'}")
    if file_enabled and log_file:
        logger.info(f"日志文件: {log_file}")


class MiniCRMLogger:
    """MiniCRM专用日志记录器包装类

    提供便捷的日志记录方法和上下文管理.
    """

    def __init__(self, name: str):
        """初始化日志记录器

        Args:
            name: 日志记录器名称,通常使用模块的__name__
        """
        self._logger = logging.getLogger(name)

    def debug(self, message: str, *args, **kwargs) -> None:
        """记录调试信息"""
        self._logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """记录一般信息"""
        self._logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """记录警告信息"""
        self._logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """记录错误信息"""
        self._logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """记录严重错误信息"""
        self._logger.critical(message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """记录异常信息(包含堆栈跟踪)"""
        self._logger.exception(message, *args, **kwargs)

    @property
    def logger(self) -> logging.Logger:
        """获取底层的Logger对象"""
        return self._logger


def get_logger(name: str) -> MiniCRMLogger:
    """获取MiniCRM日志记录器实例

    Args:
        name: 日志记录器名称

    Returns:
        MiniCRMLogger: 日志记录器实例
    """
    return MiniCRMLogger(name)
