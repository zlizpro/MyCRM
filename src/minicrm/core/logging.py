"""
MiniCRM日志系统

提供统一的日志管理功能,包括:
- 日志配置和初始化
- 多种日志输出方式(文件、控制台)
- 日志轮转和清理
- 结构化日志记录
- 性能监控日志

日志系统支持不同级别的日志记录,并提供了便捷的日志记录接口.
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from .constants import LOG_CONFIG, LOG_DIR
from .exceptions import ConfigurationError
from .utils import ensure_directory_exists


class JSONFormatter(logging.Formatter):
    """
    JSON格式的日志格式化器

    将日志记录格式化为JSON格式,便于日志分析和处理.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录为JSON

        Args:
            record: 日志记录对象

        Returns:
            JSON格式的日志字符串
        """
        # 基本日志信息
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # 添加性能信息
        if hasattr(record, "duration"):
            log_data["duration"] = record.duration

        if hasattr(record, "operation"):
            log_data["operation"] = record.operation

        return json.dumps(log_data, ensure_ascii=False)


class PerformanceLogger:
    """
    性能日志记录器

    专门用于记录性能相关的日志信息.
    """

    def __init__(self, logger_name: str = "minicrm.performance"):
        """
        初始化性能日志记录器

        Args:
            logger_name: 日志记录器名称
        """
        self.logger = logging.getLogger(logger_name)
        self._start_times: dict[str, float] = {}

    def start_operation(self, operation_id: str, operation_name: str, **kwargs) -> None:
        """
        开始记录操作性能

        Args:
            operation_id: 操作唯一标识
            operation_name: 操作名称
            **kwargs: 额外的上下文信息
        """
        import time

        self._start_times[operation_id] = time.time()

        self.logger.info(
            f"操作开始: {operation_name}",
            extra={
                "extra_fields": {
                    "operation_id": operation_id,
                    "operation_name": operation_name,
                    "operation_status": "started",
                    **kwargs,
                }
            },
        )

    def end_operation(
        self, operation_id: str, operation_name: str, success: bool = True, **kwargs
    ) -> float:
        """
        结束记录操作性能

        Args:
            operation_id: 操作唯一标识
            operation_name: 操作名称
            success: 操作是否成功
            **kwargs: 额外的上下文信息

        Returns:
            操作耗时(秒)
        """
        import time

        end_time = time.time()
        start_time = self._start_times.pop(operation_id, end_time)
        duration = end_time - start_time

        level = logging.INFO if success else logging.WARNING
        status = "completed" if success else "failed"

        self.logger.log(
            level,
            f"操作{status}: {operation_name} (耗时: {duration:.3f}秒)",
            extra={
                "extra_fields": {
                    "operation_id": operation_id,
                    "operation_name": operation_name,
                    "operation_status": status,
                    "duration": duration,
                    "success": success,
                    **kwargs,
                }
            },
        )

        return duration

    def log_slow_operation(
        self, operation_name: str, duration: float, threshold: float = 1.0, **kwargs
    ) -> None:
        """
        记录慢操作日志

        Args:
            operation_name: 操作名称
            duration: 操作耗时
            threshold: 慢操作阈值
            **kwargs: 额外的上下文信息
        """
        if duration > threshold:
            self.logger.warning(
                f"慢操作检测: {operation_name} 耗时 {duration:.3f}秒 (阈值: {threshold}秒)",
                extra={
                    "extra_fields": {
                        "operation_name": operation_name,
                        "duration": duration,
                        "threshold": threshold,
                        "is_slow": True,
                        **kwargs,
                    }
                },
            )


class AuditLogger:
    """
    审计日志记录器

    专门用于记录用户操作和系统事件的审计日志.
    """

    def __init__(self, logger_name: str = "minicrm.audit"):
        """
        初始化审计日志记录器

        Args:
            logger_name: 日志记录器名称
        """
        self.logger = logging.getLogger(logger_name)

    def log_user_action(
        self,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        user_id: str | None = None,
        **kwargs,
    ) -> None:
        """
        记录用户操作日志

        Args:
            action: 操作类型 (CREATE, UPDATE, DELETE, VIEW等)
            resource_type: 资源类型 (CUSTOMER, SUPPLIER, QUOTE等)
            resource_id: 资源ID
            user_id: 用户ID
            **kwargs: 额外的上下文信息
        """
        self.logger.info(
            f"用户操作: {action} {resource_type}",
            extra={
                "extra_fields": {
                    "event_type": "user_action",
                    "action": action,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                    **kwargs,
                }
            },
        )

    def log_system_event(self, event_type: str, event_name: str, **kwargs) -> None:
        """
        记录系统事件日志

        Args:
            event_type: 事件类型 (STARTUP, SHUTDOWN, ERROR等)
            event_name: 事件名称
            **kwargs: 额外的上下文信息
        """
        self.logger.info(
            f"系统事件: {event_type} - {event_name}",
            extra={
                "extra_fields": {
                    "event_type": "system_event",
                    "system_event_type": event_type,
                    "event_name": event_name,
                    "timestamp": datetime.now().isoformat(),
                    **kwargs,
                }
            },
        )

    def log_security_event(
        self, event_type: str, description: str, severity: str = "INFO", **kwargs
    ) -> None:
        """
        记录安全事件日志

        Args:
            event_type: 安全事件类型
            description: 事件描述
            severity: 严重程度 (INFO, WARNING, ERROR, CRITICAL)
            **kwargs: 额外的上下文信息
        """
        level = getattr(logging, severity.upper(), logging.INFO)

        self.logger.log(
            level,
            f"安全事件: {event_type} - {description}",
            extra={
                "extra_fields": {
                    "event_type": "security_event",
                    "security_event_type": event_type,
                    "description": description,
                    "severity": severity,
                    "timestamp": datetime.now().isoformat(),
                    **kwargs,
                }
            },
        )


class LogManager:
    """
    日志管理器

    负责日志系统的初始化、配置和管理.
    """

    def __init__(self):
        """初始化日志管理器"""
        self._is_initialized = False
        self._loggers: dict[str, logging.Logger] = {}
        self._handlers: dict[str, logging.Handler] = {}
        self.performance_logger = PerformanceLogger()
        self.audit_logger = AuditLogger()

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        """
        初始化日志系统

        Args:
            config: 日志配置字典,如果为None则使用默认配置

        Raises:
            ConfigurationError: 当日志配置无效时
        """
        if self._is_initialized:
            return

        try:
            # 使用提供的配置或默认配置
            log_config = config or LOG_CONFIG

            # 确保日志目录存在
            ensure_directory_exists(LOG_DIR)

            # 配置根日志记录器
            self._configure_root_logger(log_config)

            # 配置应用程序日志记录器
            self._configure_app_loggers(log_config)

            # 配置特殊日志记录器
            self._configure_special_loggers(log_config)

            self._is_initialized = True

            # 记录日志系统启动
            logger = logging.getLogger("minicrm")
            logger.info("日志系统初始化完成")

        except Exception as e:
            raise ConfigurationError(f"日志系统初始化失败: {e}", original_exception=e)

    def _configure_root_logger(self, config: dict[str, Any]) -> None:
        """
        配置根日志记录器

        Args:
            config: 日志配置
        """
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config["level"]))

        # 清除现有处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def _configure_app_loggers(self, config: dict[str, Any]) -> None:
        """
        配置应用程序日志记录器

        Args:
            config: 日志配置
        """
        # 主应用程序日志记录器
        app_logger = logging.getLogger("minicrm")
        app_logger.setLevel(getattr(logging, config["level"]))

        # 文件处理器
        if config.get("log_to_file", True):
            file_handler = self._create_file_handler(LOG_DIR / "minicrm.log", config)
            app_logger.addHandler(file_handler)
            self._handlers["app_file"] = file_handler

        # 控制台处理器
        if config.get("log_to_console", True):
            console_handler = self._create_console_handler(config)
            app_logger.addHandler(console_handler)
            self._handlers["app_console"] = console_handler

        # 防止日志传播到根记录器
        app_logger.propagate = False

        self._loggers["app"] = app_logger

    def _configure_special_loggers(self, config: dict[str, Any]) -> None:
        """
        配置特殊用途的日志记录器

        Args:
            config: 日志配置
        """
        # 性能日志记录器
        perf_logger = logging.getLogger("minicrm.performance")
        perf_logger.setLevel(logging.INFO)

        perf_file_handler = self._create_file_handler(
            LOG_DIR / "performance.log", config, use_json_format=True
        )
        perf_logger.addHandler(perf_file_handler)
        perf_logger.propagate = False

        self._loggers["performance"] = perf_logger
        self._handlers["perf_file"] = perf_file_handler

        # 审计日志记录器
        audit_logger = logging.getLogger("minicrm.audit")
        audit_logger.setLevel(logging.INFO)

        audit_file_handler = self._create_file_handler(
            LOG_DIR / "audit.log", config, use_json_format=True
        )
        audit_logger.addHandler(audit_file_handler)
        audit_logger.propagate = False

        self._loggers["audit"] = audit_logger
        self._handlers["audit_file"] = audit_file_handler

        # 错误日志记录器
        error_logger = logging.getLogger("minicrm.error")
        error_logger.setLevel(logging.ERROR)

        error_file_handler = self._create_file_handler(LOG_DIR / "error.log", config)
        error_logger.addHandler(error_file_handler)
        error_logger.propagate = False

        self._loggers["error"] = error_logger
        self._handlers["error_file"] = error_file_handler

    def _create_file_handler(
        self, log_file: Path, config: dict[str, Any], use_json_format: bool = False
    ) -> logging.Handler:
        """
        创建文件日志处理器

        Args:
            log_file: 日志文件路径
            config: 日志配置
            use_json_format: 是否使用JSON格式

        Returns:
            文件日志处理器
        """
        # 使用轮转文件处理器
        handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=config.get("max_file_size", 10 * 1024 * 1024),
            backupCount=config.get("backup_count", 5),
            encoding=config.get("encoding", "utf-8"),
        )

        # 设置格式化器
        if use_json_format:
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                fmt=config.get(
                    "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                ),
                datefmt=config.get("date_format", "%Y-%m-%d %H:%M:%S"),
            )

        handler.setFormatter(formatter)
        return handler

    def _create_console_handler(self, config: dict[str, Any]) -> logging.Handler:
        """
        创建控制台日志处理器

        Args:
            config: 日志配置

        Returns:
            控制台日志处理器
        """
        handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(
            fmt=config.get(
                "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ),
            datefmt=config.get("date_format", "%Y-%m-%d %H:%M:%S"),
        )

        handler.setFormatter(formatter)
        return handler

    def get_logger(self, name: str) -> logging.Logger:
        """
        获取日志记录器

        Args:
            name: 日志记录器名称

        Returns:
            日志记录器实例
        """
        if not self._is_initialized:
            self.initialize()

        if name in self._loggers:
            return self._loggers[name]

        # 创建子日志记录器
        logger = logging.getLogger(f"minicrm.{name}")
        self._loggers[name] = logger
        return logger

    def shutdown(self) -> None:
        """
        关闭日志系统

        清理所有日志处理器和资源.
        """
        if not self._is_initialized:
            return

        # 记录关闭日志
        logger = logging.getLogger("minicrm")
        logger.info("日志系统正在关闭")

        # 关闭所有处理器
        for handler in self._handlers.values():
            handler.close()

        # 清理资源
        self._handlers.clear()
        self._loggers.clear()

        self._is_initialized = False

    def set_level(self, logger_name: str, level: str | int) -> None:
        """
        设置日志记录器级别

        Args:
            logger_name: 日志记录器名称
            level: 日志级别
        """
        logger = self.get_logger(logger_name)

        if isinstance(level, str):
            level = getattr(logging, level.upper())

        logger.setLevel(level)

    def add_handler(self, logger_name: str, handler: logging.Handler) -> None:
        """
        为日志记录器添加处理器

        Args:
            logger_name: 日志记录器名称
            handler: 日志处理器
        """
        logger = self.get_logger(logger_name)
        logger.addHandler(handler)

    def remove_handler(self, logger_name: str, handler: logging.Handler) -> None:
        """
        从日志记录器移除处理器

        Args:
            logger_name: 日志记录器名称
            handler: 日志处理器
        """
        logger = self.get_logger(logger_name)
        logger.removeHandler(handler)


# 全局日志管理器实例
log_manager = LogManager()


def get_logger(name: str = "app") -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器实例
    """
    return log_manager.get_logger(name)


def initialize_logging(config: dict[str, Any] | None = None) -> None:
    """
    初始化日志系统

    Args:
        config: 日志配置
    """
    log_manager.initialize(config)


def shutdown_logging() -> None:
    """
    关闭日志系统
    """
    log_manager.shutdown()


def get_performance_logger() -> PerformanceLogger:
    """
    获取性能日志记录器

    Returns:
        性能日志记录器实例
    """
    return log_manager.performance_logger


def get_audit_logger() -> AuditLogger:
    """
    获取审计日志记录器

    Returns:
        审计日志记录器实例
    """
    return log_manager.audit_logger
