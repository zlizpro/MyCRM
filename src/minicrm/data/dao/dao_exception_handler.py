"""DAO层统一异常处理器.

提供统一的异常处理机制,消除DAO层中重复的异常处理代码.
支持多种异常类型的智能转换、统一的错误消息格式和完整的日志记录.

主要功能:
1. 统一异常类型转换和处理
2. 标准化错误消息格式
3. 集成日志记录功能
4. 提供装饰器模式简化使用

使用示例:
    # 方法1: 直接调用
    try:
        # DAO操作
        pass
    except Exception as e:
        DAOExceptionHandler.handle_dao_error(e, "创建", "客户")

    # 方法2: 装饰器模式
    @dao_exception_handler("创建", "客户")
    def create_customer(self, data):
        # DAO操作
        pass
"""

from __future__ import annotations

from functools import wraps
import logging
import sqlite3
from typing import Any, Callable, ClassVar

from minicrm.core.exceptions import DatabaseError, ValidationError
from transfunctions import ValidationError as TransValidationError


logger = logging.getLogger(__name__)


class DAOExceptionHandler:
    """DAO层统一异常处理器.

    提供标准化的异常处理方法,包括异常类型转换、消息格式化和日志记录.
    所有方法都是静态方法,不需要实例化即可使用.
    """

    # 操作类型映射,用于生成标准化的错误消息
    OPERATION_MAPPING: ClassVar[dict[str, str]] = {
        "create": "创建",
        "update": "更新",
        "delete": "删除",
        "query": "查询",
        "search": "搜索",
        "get": "获取",
        "list": "列表",
        "count": "统计",
        "exists": "检查存在性",
    }

    # 实体类型映射
    ENTITY_MAPPING: ClassVar[dict[str, str]] = {
        "customer": "客户",
        "supplier": "供应商",
        "quote": "报价",
        "contract": "合同",
        "order": "订单",
        "interaction": "互动记录",
        "task": "任务",
        "customer_type": "客户类型",
        "supplier_type": "供应商类型",
    }

    @staticmethod
    def handle_dao_error(
        error: Exception,
        operation: str,
        entity_type: str,
        context: dict[str, Any] | None = None,
        sql_info: dict[str, Any] | None = None,
    ) -> None:
        """处理DAO层异常的主要方法.

        根据异常类型进行智能转换和处理,生成标准化的错误消息并记录日志.

        Args:
            error: 捕获的原始异常
            operation: 操作类型 (如: "创建", "更新", "查询")
            entity_type: 实体类型 (如: "客户", "供应商")
            context: 额外的上下文信息
            sql_info: SQL相关信息 (语句, 参数等)

        Raises:
            ValidationError: 当原始异常是验证相关错误时
            DatabaseError: 当原始异常是数据库相关错误时
        """
        context = context or {}

        # 处理验证异常
        if isinstance(error, (TransValidationError, ValidationError)):
            DAOExceptionHandler._handle_validation_error(
                error, operation, entity_type, context
            )

        # 处理数据库异常
        elif isinstance(error, (sqlite3.Error, DatabaseError)):
            DAOExceptionHandler._handle_database_error(
                error, operation, entity_type, context, sql_info
            )

        # 处理其他异常,在DAO层通常转换为数据库异常
        else:
            DAOExceptionHandler._handle_general_error(
                error, operation, entity_type, context
            )

    @staticmethod
    def _handle_validation_error(
        error: Exception, operation: str, entity_type: str, context: dict[str, Any]
    ) -> None:
        """处理验证异常."""
        # 如果已经是ValidationError,直接重新抛出
        if isinstance(error, ValidationError):
            raise error

        # 转换TransValidationError为ValidationError
        error_msg = DAOExceptionHandler.format_error_message(
            operation, entity_type, str(error)
        )

        # 记录警告日志,验证错误通常是用户输入问题
        DAOExceptionHandler._log_error(logging.WARNING, error_msg, error, context)

        # 抛出标准化的ValidationError
        raise ValidationError(
            error_msg,
            error_code=f"{entity_type.upper()}_VALIDATION_ERROR",
            details=context,
            original_exception=error,
        ) from error

    @staticmethod
    def _handle_database_error(
        error: Exception,
        operation: str,
        entity_type: str,
        context: dict[str, Any],
        sql_info: dict[str, Any] | None = None,
    ) -> None:
        """处理数据库异常."""
        # 如果已经是DatabaseError,直接重新抛出
        if isinstance(error, DatabaseError):
            raise error

        error_msg = DAOExceptionHandler.format_error_message(
            operation, entity_type, str(error)
        )

        # 记录错误日志
        log_context = context.copy()
        if sql_info:
            log_context.update(sql_info)

        DAOExceptionHandler._log_error(logging.ERROR, error_msg, error, log_context)

        # 抛出标准化的DatabaseError
        raise DatabaseError(
            error_msg,
            error_code=f"{entity_type.upper()}_DATABASE_ERROR",
            details=context,
            sql_statement=sql_info.get("sql") if sql_info else None,
            sql_params=sql_info.get("params") if sql_info else None,
            original_exception=error,
        ) from error

    @staticmethod
    def _handle_general_error(
        error: Exception, operation: str, entity_type: str, context: dict[str, Any]
    ) -> None:
        """处理通用异常,在DAO层转换为数据库异常."""
        error_msg = DAOExceptionHandler.format_error_message(
            operation, entity_type, str(error)
        )

        # 记录错误日志
        DAOExceptionHandler._log_error(logging.ERROR, error_msg, error, context)

        # 在DAO层,通用异常通常转换为DatabaseError
        raise DatabaseError(
            error_msg,
            error_code=f"{entity_type.upper()}_OPERATION_ERROR",
            details=context,
            original_exception=error,
        ) from error

    @staticmethod
    def format_error_message(
        operation: str, entity_type: str, error_detail: str
    ) -> str:
        """格式化错误消息.

        生成标准化的错误消息格式: "{操作}{实体类型}失败: {错误详情}"

        Args:
            operation: 操作类型
            entity_type: 实体类型
            error_detail: 错误详情

        Returns:
            格式化后的错误消息
        """
        # 标准化操作和实体类型名称
        operation_name = DAOExceptionHandler.OPERATION_MAPPING.get(
            operation.lower(), operation
        )
        entity_name = DAOExceptionHandler.ENTITY_MAPPING.get(
            entity_type.lower(), entity_type
        )

        return f"{operation_name}{entity_name}失败: {error_detail}"

    @staticmethod
    def _log_error(
        level: int, message: str, error: Exception, context: dict[str, Any]
    ) -> None:
        """记录错误日志.

        Args:
            level: 日志级别
            message: 日志消息
            error: 原始异常
            context: 上下文信息
        """
        logger.log(
            level,
            message,
            extra={
                "exception_type": error.__class__.__name__,
                "exception_message": str(error),
                "context": context,
            },
            exc_info=level >= logging.ERROR,  # ERROR及以上级别记录异常堆栈
        )


def dao_exception_handler(
    operation: str, entity_type: str, context: dict[str, Any] | None = None
) -> Callable:
    """DAO异常处理装饰器.

    提供装饰器模式的异常处理,简化DAO方法的异常处理代码.

    Args:
        operation: 操作类型
        entity_type: 实体类型
        context: 额外的上下文信息

    Returns:
        装饰器函数

    Example:
        @dao_exception_handler("创建", "客户")
        def create_customer(self, customer_data):
            # DAO操作代码
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            try:
                return func(*args, **kwargs)
            except (ValidationError, DatabaseError, sqlite3.Error) as e:
                # 构建上下文信息
                func_context = {
                    "function_name": func.__name__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                }
                if context:
                    func_context.update(context)

                # 处理异常
                DAOExceptionHandler.handle_dao_error(
                    e, operation, entity_type, func_context
                )
                # 这里不会到达, 因为handle_dao_error总是抛出异常
                return None  # 为了满足类型检查

        return wrapper

    return decorator


# 便捷的异常处理函数,用于常见的DAO操作
def handle_create_error(error: Exception, entity_type: str, **kwargs: object) -> None:
    """处理创建操作异常的便捷函数."""
    DAOExceptionHandler.handle_dao_error(error, "创建", entity_type, kwargs)


def handle_update_error(error: Exception, entity_type: str, **kwargs: object) -> None:
    """处理更新操作异常的便捷函数."""
    DAOExceptionHandler.handle_dao_error(error, "更新", entity_type, kwargs)


def handle_query_error(error: Exception, entity_type: str, **kwargs: object) -> None:
    """处理查询操作异常的便捷函数."""
    DAOExceptionHandler.handle_dao_error(error, "查询", entity_type, kwargs)


def handle_delete_error(error: Exception, entity_type: str, **kwargs: object) -> None:
    """处理删除操作异常的便捷函数."""
    DAOExceptionHandler.handle_dao_error(error, "删除", entity_type, kwargs)
