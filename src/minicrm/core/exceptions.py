"""MiniCRM异常类定义

定义了系统中使用的所有自定义异常类,提供了清晰的错误分类和处理机制.
所有异常都继承自MiniCRMError基类,便于统一处理.

异常层次结构:
    MiniCRMError (基础异常)
    ├── ValidationError (数据验证异常)
    ├── DatabaseError (数据库操作异常)
    ├── BusinessLogicError (业务逻辑异常)
    ├── ConfigurationError (配置相关异常)
    └── UIError (界面相关异常)
"""

import logging
from typing import Any


logger = logging.getLogger(__name__)


class MiniCRMError(Exception):
    """MiniCRM系统基础异常类

    所有MiniCRM相关的异常都应该继承自这个类.
    提供了统一的异常处理接口和日志记录功能.

    Attributes:
        message: 错误消息
        error_code: 错误代码,用于程序化处理
        details: 错误详细信息字典
        original_exception: 原始异常对象(如果有)
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
        original_exception: Exception | None = None,
    ):
        """初始化异常

        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详细信息
            original_exception: 原始异常对象
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.original_exception = original_exception

        # 记录异常日志
        logger.error(
            f"MiniCRM异常: {self.error_code} - {message}",
            extra={
                "error_code": self.error_code,
                "details": self.details,
                "original_exception": str(original_exception)
                if original_exception
                else None,
            },
        )

    def __str__(self) -> str:
        """返回异常的字符串表示"""
        return f"[{self.error_code}] {self.message}"

    def to_dict(self) -> dict[str, Any]:
        """将异常转换为字典格式

        Returns:
            包含异常信息的字典
        """
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "original_exception": str(self.original_exception)
            if self.original_exception
            else None,
        }


class ValidationError(MiniCRMError):
    r"""数据验证异常

    当数据验证失败时抛出此异常.
    通常用于表单验证、数据格式检查等场景.

    Examples:
        >>> if not customer_name:
        ...     raise ValidationError("客户名称不能为空", "EMPTY_CUSTOMER_NAME")
        >>>
        >>> if not re.match(r"^1[3-9]\d{9}$", phone):
        ...     raise ValidationError("电话号码格式不正确", "INVALID_PHONE_FORMAT")
    """

    def __init__(
        self,
        message: str,
        field_name: str | None = None,
        field_value: Any | None = None,
        **kwargs,
    ):
        """初始化验证异常

        Args:
            message: 错误消息
            field_name: 验证失败的字段名
            field_value: 验证失败的字段值
            **kwargs: 其他参数传递给父类
        """
        details = kwargs.get("details", {})
        if field_name:
            details["field_name"] = field_name
        if field_value is not None:
            details["field_value"] = str(field_value)

        kwargs["details"] = details
        super().__init__(message, **kwargs)


class DatabaseError(MiniCRMError):
    """数据库操作异常

    当数据库操作失败时抛出此异常.
    包括连接失败、SQL执行错误、事务回滚等.

    Examples:
        >>> try:
        ...     cursor.execute(sql, params)
        ... except sqlite3.Error as e:
        ...     raise DatabaseError("数据库查询失败", original_exception=e)
    """

    def __init__(
        self,
        message: str,
        sql_statement: str | None = None,
        sql_params: tuple | None = None,
        **kwargs,
    ):
        """初始化数据库异常

        Args:
            message: 错误消息
            sql_statement: 执行失败的SQL语句
            sql_params: SQL参数
            **kwargs: 其他参数传递给父类
        """
        details = kwargs.get("details", {})
        if sql_statement:
            details["sql_statement"] = sql_statement
        if sql_params:
            details["sql_params"] = str(sql_params)

        kwargs["details"] = details
        super().__init__(message, **kwargs)


class BusinessLogicError(MiniCRMError):
    """业务逻辑异常

    当业务规则验证失败时抛出此异常.
    例如:客户信用额度超限、重复创建客户等.

    Examples:
        >>> if customer_exists(customer_name):
        ...     raise BusinessLogicError("客户已存在", "DUPLICATE_CUSTOMER")
        >>>
        >>> if order_amount > credit_limit:
        ...     raise BusinessLogicError(
        ...         "订单金额超过信用额度", "CREDIT_LIMIT_EXCEEDED"
        ...     )
    """

    def __init__(
        self,
        message: str,
        business_rule: str | None = None,
        context: dict[str, Any] | None = None,
        **kwargs,
    ):
        """初始化业务逻辑异常

        Args:
            message: 错误消息
            business_rule: 违反的业务规则名称
            context: 业务上下文信息
            **kwargs: 其他参数传递给父类
        """
        details = kwargs.get("details", {})
        if business_rule:
            details["business_rule"] = business_rule
        if context:
            details["context"] = context

        kwargs["details"] = details
        super().__init__(message, **kwargs)


class ConfigurationError(MiniCRMError):
    """配置相关异常

    当系统配置错误或缺失时抛出此异常.
    例如:配置文件不存在、配置项无效等.

    Examples:
        >>> if not os.path.exists(config_file):
        ...     raise ConfigurationError("配置文件不存在", "CONFIG_FILE_NOT_FOUND")
        >>>
        >>> if database_path is None:
        ...     raise ConfigurationError(
        ...         "数据库路径未配置", "DATABASE_PATH_MISSING"
        ...     )
    """

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        config_file: str | None = None,
        **kwargs,
    ):
        """初始化配置异常

        Args:
            message: 错误消息
            config_key: 相关的配置键名
            config_file: 相关的配置文件路径
            **kwargs: 其他参数传递给父类
        """
        details = kwargs.get("details", {})
        if config_key:
            details["config_key"] = config_key
        if config_file:
            details["config_file"] = config_file

        kwargs["details"] = details
        super().__init__(message, **kwargs)


class ServiceError(MiniCRMError):
    """服务层异常

    当服务层操作失败时抛出此异常.
    例如:服务初始化失败、服务调用错误等.

    Examples:
        >>> if not service.is_available():
        ...     raise ServiceError("服务不可用", "SERVICE_UNAVAILABLE")
        >>>
        >>> if operation_failed:
        ...     raise ServiceError("服务操作失败", "OPERATION_FAILED")
    """

    def __init__(
        self,
        message: str,
        service_name: str | None = None,
        operation: str | None = None,
        **kwargs,
    ):
        """初始化服务异常

        Args:
            message: 错误消息
            service_name: 相关的服务名称
            operation: 相关的操作名称
            **kwargs: 其他参数传递给父类
        """
        details = kwargs.get("details", {})
        if service_name:
            details["service_name"] = service_name
        if operation:
            details["operation"] = operation

        kwargs["details"] = details
        super().__init__(message, **kwargs)


class UIError(MiniCRMError):
    """用户界面相关异常

    当UI操作失败时抛出此异常.
    例如:窗口创建失败、控件初始化错误等.

    Examples:
        >>> if not widget.isVisible():
        ...     raise UIError("窗口显示失败", "WINDOW_DISPLAY_FAILED")
        >>>
        >>> if theme_file is None:
        ...     raise UIError("主题文件加载失败", "THEME_LOAD_FAILED")
    """

    def __init__(
        self,
        message: str,
        widget_name: str | None = None,
        ui_operation: str | None = None,
        **kwargs,
    ):
        """初始化UI异常

        Args:
            message: 错误消息
            widget_name: 相关的控件名称
            ui_operation: 相关的UI操作
            **kwargs: 其他参数传递给父类
        """
        details = kwargs.get("details", {})
        if widget_name:
            details["widget_name"] = widget_name
        if ui_operation:
            details["ui_operation"] = ui_operation

        kwargs["details"] = details
        super().__init__(message, **kwargs)


class DependencyError(MiniCRMError):
    """依赖注入相关异常

    当依赖注入操作失败时抛出此异常.
    例如:依赖未注册、循环依赖、注入失败等.

    Examples:
        >>> if service_type not in self._services:
        ...     raise DependencyError("服务未注册", "SERVICE_NOT_REGISTERED")
        >>>
        >>> if circular_dependency_detected:
        ...     raise DependencyError("检测到循环依赖", "CIRCULAR_DEPENDENCY")
    """

    def __init__(
        self,
        message: str,
        dependency_type: str | None = None,
        dependency_name: str | None = None,
        **kwargs,
    ):
        """初始化依赖异常

        Args:
            message: 错误消息
            dependency_type: 依赖类型
            dependency_name: 依赖名称
            **kwargs: 其他参数传递给父类
        """
        details = kwargs.get("details", {})
        if dependency_type:
            details["dependency_type"] = dependency_type
        if dependency_name:
            details["dependency_name"] = dependency_name

        kwargs["details"] = details
        super().__init__(message, **kwargs)


# 异常处理工具函数
def handle_exception(func):
    """异常处理装饰器

    用于统一处理函数中的异常,将未捕获的异常转换为MiniCRMError.

    Args:
        func: 要装饰的函数

    Returns:
        装饰后的函数
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MiniCRMError:
            # MiniCRM异常直接重新抛出
            raise
        except Exception as e:
            # 其他异常转换为MiniCRMError
            logger.error(f"未处理的异常在函数 {func.__name__}: {e}")
            raise MiniCRMError(
                f"函数 {func.__name__} 执行失败: {e!s}",
                error_code="UNHANDLED_EXCEPTION",
                original_exception=e,
            )

    return wrapper


def log_exception(exception: Exception, context: dict[str, Any] | None = None):
    """记录异常日志

    Args:
        exception: 要记录的异常
        context: 额外的上下文信息
    """
    context = context or {}

    if isinstance(exception, MiniCRMError):
        logger.error(
            f"MiniCRM异常: {exception.error_code} - {exception.message}",
            extra={
                "error_code": exception.error_code,
                "details": exception.details,
                "context": context,
            },
        )
    else:
        logger.error(
            f"系统异常: {exception.__class__.__name__} - {exception!s}",
            extra={"exception_type": exception.__class__.__name__, "context": context},
        )
