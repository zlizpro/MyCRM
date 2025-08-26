"""
MiniCRM 错误处理工具

提供统一的错误分类和处理功能,包括:
- 错误类型分类
- 错误恢复策略
- 错误信息格式化
- 错误统计和报告

设计原则:
- 统一的错误分类标准
- 可配置的错误处理策略
- 详细的错误信息记录
- 支持错误恢复和重试
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ErrorType(Enum):
    """错误类型枚举"""

    VALIDATION_ERROR = "validation_error"  # 数据验证错误
    FILE_FORMAT_ERROR = "file_format_error"  # 文件格式错误
    DATABASE_ERROR = "database_error"  # 数据库操作错误
    NETWORK_ERROR = "network_error"  # 网络连接错误
    PERMISSION_ERROR = "permission_error"  # 权限错误
    BUSINESS_LOGIC_ERROR = "business_logic_error"  # 业务逻辑错误
    SYSTEM_ERROR = "system_error"  # 系统错误
    USER_INPUT_ERROR = "user_input_error"  # 用户输入错误
    TIMEOUT_ERROR = "timeout_error"  # 超时错误
    UNKNOWN_ERROR = "unknown_error"  # 未知错误


class ErrorSeverity(Enum):
    """错误严重程度枚举"""

    LOW = "low"  # 低级错误,可以继续处理
    MEDIUM = "medium"  # 中级错误,需要用户注意
    HIGH = "high"  # 高级错误,需要停止当前操作
    CRITICAL = "critical"  # 严重错误,需要立即处理


class ErrorAction(Enum):
    """错误处理动作枚举"""

    SKIP = "skip"  # 跳过当前项目
    RETRY = "retry"  # 重试操作
    STOP = "stop"  # 停止处理
    CONTINUE = "continue"  # 继续处理
    ASK_USER = "ask_user"  # 询问用户


@dataclass
class ErrorInfo:
    """错误信息数据类"""

    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    details: str = ""
    context: dict[str, Any] = None
    suggested_action: ErrorAction = ErrorAction.ASK_USER
    is_recoverable: bool = True
    retry_count: int = 0
    max_retries: int = 3

    def __post_init__(self):
        if self.context is None:
            self.context = {}


class ErrorHandler:
    """
    错误处理器

    提供统一的错误分类、处理和恢复功能.
    """

    def __init__(self):
        """初始化错误处理器"""
        self._logger = logging.getLogger(__name__)

        # 错误统计
        self._error_counts: dict[ErrorType, int] = {}
        self._error_history: list[ErrorInfo] = []

        # 错误处理策略配置
        self._error_strategies: dict[ErrorType, ErrorAction] = {
            ErrorType.VALIDATION_ERROR: ErrorAction.SKIP,
            ErrorType.FILE_FORMAT_ERROR: ErrorAction.STOP,
            ErrorType.DATABASE_ERROR: ErrorAction.RETRY,
            ErrorType.NETWORK_ERROR: ErrorAction.RETRY,
            ErrorType.PERMISSION_ERROR: ErrorAction.STOP,
            ErrorType.BUSINESS_LOGIC_ERROR: ErrorAction.ASK_USER,
            ErrorType.SYSTEM_ERROR: ErrorAction.STOP,
            ErrorType.USER_INPUT_ERROR: ErrorAction.ASK_USER,
            ErrorType.TIMEOUT_ERROR: ErrorAction.RETRY,
            ErrorType.UNKNOWN_ERROR: ErrorAction.ASK_USER,
        }

        # 严重程度配置
        self._severity_mapping: dict[ErrorType, ErrorSeverity] = {
            ErrorType.VALIDATION_ERROR: ErrorSeverity.LOW,
            ErrorType.FILE_FORMAT_ERROR: ErrorSeverity.HIGH,
            ErrorType.DATABASE_ERROR: ErrorSeverity.MEDIUM,
            ErrorType.NETWORK_ERROR: ErrorSeverity.MEDIUM,
            ErrorType.PERMISSION_ERROR: ErrorSeverity.HIGH,
            ErrorType.BUSINESS_LOGIC_ERROR: ErrorSeverity.MEDIUM,
            ErrorType.SYSTEM_ERROR: ErrorSeverity.CRITICAL,
            ErrorType.USER_INPUT_ERROR: ErrorSeverity.LOW,
            ErrorType.TIMEOUT_ERROR: ErrorSeverity.MEDIUM,
            ErrorType.UNKNOWN_ERROR: ErrorSeverity.HIGH,
        }

    def classify_error(
        self, exception: Exception, context: dict[str, Any] = None
    ) -> ErrorInfo:
        """
        分类错误

        Args:
            exception: 异常对象
            context: 错误上下文信息

        Returns:
            ErrorInfo: 错误信息对象
        """
        if context is None:
            context = {}

        # 根据异常类型分类
        error_type = self._determine_error_type(exception)
        severity = self._severity_mapping.get(error_type, ErrorSeverity.MEDIUM)
        suggested_action = self._error_strategies.get(error_type, ErrorAction.ASK_USER)

        # 创建错误信息
        error_info = ErrorInfo(
            error_type=error_type,
            severity=severity,
            message=str(exception),
            details=self._extract_error_details(exception),
            context=context,
            suggested_action=suggested_action,
            is_recoverable=self._is_recoverable_error(error_type),
        )

        # 记录错误
        self._record_error(error_info)

        return error_info

    def _determine_error_type(self, exception: Exception) -> ErrorType:
        """确定错误类型"""
        exception_name = type(exception).__name__
        exception_message = str(exception).lower()

        # 根据异常类型和消息内容判断错误类型
        if "validation" in exception_name.lower() or "invalid" in exception_message:
            return ErrorType.VALIDATION_ERROR
        elif "file" in exception_message or "format" in exception_message:
            return ErrorType.FILE_FORMAT_ERROR
        elif "database" in exception_message or "sql" in exception_message:
            return ErrorType.DATABASE_ERROR
        elif "network" in exception_message or "connection" in exception_message:
            return ErrorType.NETWORK_ERROR
        elif "permission" in exception_message or "access" in exception_message:
            return ErrorType.PERMISSION_ERROR
        elif "timeout" in exception_message:
            return ErrorType.TIMEOUT_ERROR
        elif hasattr(exception, "error_type"):
            # 如果异常对象有error_type属性,直接使用
            return getattr(exception, "error_type", ErrorType.UNKNOWN_ERROR)
        else:
            return ErrorType.UNKNOWN_ERROR

    def _extract_error_details(self, exception: Exception) -> str:
        """提取错误详细信息"""
        details = []

        # 添加异常类型
        details.append(f"异常类型: {type(exception).__name__}")

        # 添加异常消息
        if str(exception):
            details.append(f"错误消息: {str(exception)}")

        # 添加异常属性(如果有)
        if hasattr(exception, "__dict__"):
            for key, value in exception.__dict__.items():
                if not key.startswith("_"):
                    details.append(f"{key}: {value}")

        return "\n".join(details)

    def _is_recoverable_error(self, error_type: ErrorType) -> bool:
        """判断错误是否可恢复"""
        recoverable_errors = {
            ErrorType.VALIDATION_ERROR,
            ErrorType.DATABASE_ERROR,
            ErrorType.NETWORK_ERROR,
            ErrorType.BUSINESS_LOGIC_ERROR,
            ErrorType.USER_INPUT_ERROR,
            ErrorType.TIMEOUT_ERROR,
        }
        return error_type in recoverable_errors

    def _record_error(self, error_info: ErrorInfo) -> None:
        """记录错误"""
        # 更新错误计数
        if error_info.error_type not in self._error_counts:
            self._error_counts[error_info.error_type] = 0
        self._error_counts[error_info.error_type] += 1

        # 添加到错误历史
        self._error_history.append(error_info)

        # 记录日志
        log_level = self._get_log_level(error_info.severity)
        self._logger.log(
            log_level,
            f"错误分类: {error_info.error_type.value} | "
            f"严重程度: {error_info.severity.value} | "
            f"消息: {error_info.message}",
        )

    def _get_log_level(self, severity: ErrorSeverity) -> int:
        """获取日志级别"""
        level_mapping = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL,
        }
        return level_mapping.get(severity, logging.WARNING)

    def handle_error(
        self,
        error_info: ErrorInfo,
        user_callback: Callable[[ErrorInfo], ErrorAction] | None = None,
    ) -> ErrorAction:
        """
        处理错误

        Args:
            error_info: 错误信息
            user_callback: 用户决策回调函数

        Returns:
            ErrorAction: 处理动作
        """
        # 如果需要询问用户且有回调函数
        if error_info.suggested_action == ErrorAction.ASK_USER and user_callback:
            try:
                return user_callback(error_info)
            except Exception as e:
                self._logger.error(f"用户回调失败: {e}")
                return ErrorAction.STOP

        # 检查是否可以重试
        if (
            error_info.suggested_action == ErrorAction.RETRY
            and error_info.retry_count >= error_info.max_retries
        ):
            self._logger.warning(f"重试次数已达上限,改为跳过: {error_info.message}")
            return ErrorAction.SKIP

        return error_info.suggested_action

    def should_continue_processing(self, error_info: ErrorInfo) -> bool:
        """
        判断是否应该继续处理

        Args:
            error_info: 错误信息

        Returns:
            bool: 是否继续处理
        """
        # 严重错误应该停止处理
        if error_info.severity == ErrorSeverity.CRITICAL:
            return False

        # 高级错误根据类型决定
        if error_info.severity == ErrorSeverity.HIGH:
            return error_info.error_type in [
                ErrorType.VALIDATION_ERROR,
                ErrorType.USER_INPUT_ERROR,
            ]

        # 中低级错误可以继续处理
        return True

    def get_error_summary(self) -> dict[str, Any]:
        """
        获取错误摘要

        Returns:
            Dict[str, Any]: 错误摘要信息
        """
        total_errors = len(self._error_history)

        # 按严重程度统计
        severity_counts = {}
        for severity in ErrorSeverity:
            severity_counts[severity.value] = sum(
                1 for error in self._error_history if error.severity == severity
            )

        # 按类型统计
        type_counts = {
            error_type.value: count for error_type, count in self._error_counts.items()
        }

        # 最近的错误
        recent_errors = [
            {
                "type": error.error_type.value,
                "severity": error.severity.value,
                "message": error.message,
                "is_recoverable": error.is_recoverable,
            }
            for error in self._error_history[-10:]  # 最近10个错误
        ]

        return {
            "total_errors": total_errors,
            "severity_counts": severity_counts,
            "type_counts": type_counts,
            "recent_errors": recent_errors,
        }

    def format_error_message(self, error_info: ErrorInfo) -> str:
        """
        格式化错误消息

        Args:
            error_info: 错误信息

        Returns:
            str: 格式化的错误消息
        """
        severity_icons = {
            ErrorSeverity.LOW: "ℹ️",
            ErrorSeverity.MEDIUM: "⚠️",
            ErrorSeverity.HIGH: "❌",
            ErrorSeverity.CRITICAL: "🚨",
        }

        icon = severity_icons.get(error_info.severity, "❓")

        message_parts = [f"{icon} {error_info.message}"]

        if error_info.details:
            message_parts.append(f"详细信息: {error_info.details}")

        if error_info.context:
            context_str = ", ".join(f"{k}: {v}" for k, v in error_info.context.items())
            message_parts.append(f"上下文: {context_str}")

        if error_info.is_recoverable:
            message_parts.append("💡 此错误可以恢复,建议重试或跳过")

        return "\n".join(message_parts)

    def clear_error_history(self) -> None:
        """清除错误历史"""
        self._error_history.clear()
        self._error_counts.clear()
        self._logger.info("错误历史已清除")

    def set_error_strategy(self, error_type: ErrorType, action: ErrorAction) -> None:
        """
        设置错误处理策略

        Args:
            error_type: 错误类型
            action: 处理动作
        """
        self._error_strategies[error_type] = action
        self._logger.debug(f"设置错误策略: {error_type.value} -> {action.value}")

    def get_error_statistics(self) -> dict[str, int]:
        """
        获取错误统计信息

        Returns:
            Dict[str, int]: 错误统计数据
        """
        return {
            "total_errors": len(self._error_history),
            "recoverable_errors": sum(
                1 for error in self._error_history if error.is_recoverable
            ),
            "critical_errors": sum(
                1
                for error in self._error_history
                if error.severity == ErrorSeverity.CRITICAL
            ),
            "unique_error_types": len(self._error_counts),
        }
