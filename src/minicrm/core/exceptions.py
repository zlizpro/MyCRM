"""
MiniCRM 自定义异常类

定义了应用程序中使用的所有自定义异常类型，
提供更精确的错误处理和用户友好的错误信息。
"""


class MiniCRMError(Exception):
    """
    MiniCRM基础异常类

    所有MiniCRM相关的异常都应该继承自这个类。
    提供统一的异常处理接口和错误信息格式。
    """

    def __init__(self, message: str, error_code: str = None):
        """
        初始化异常

        Args:
            message: 错误消息
            error_code: 错误代码（可选）
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        """返回异常的字符串表示"""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ValidationError(MiniCRMError):
    """
    数据验证异常

    当数据验证失败时抛出此异常。
    通常用于表单验证、数据格式检查等场景。
    """

    def __init__(self, message: str, field_name: str = None):
        """
        初始化验证异常

        Args:
            message: 错误消息
            field_name: 验证失败的字段名（可选）
        """
        super().__init__(message, "VALIDATION_ERROR")
        self.field_name = field_name


class DatabaseError(MiniCRMError):
    """
    数据库操作异常

    当数据库操作失败时抛出此异常。
    包括连接失败、查询错误、事务失败等。
    """

    def __init__(self, message: str, sql: str = None):
        """
        初始化数据库异常

        Args:
            message: 错误消息
            sql: 导致错误的SQL语句（可选）
        """
        super().__init__(message, "DATABASE_ERROR")
        self.sql = sql


class BusinessLogicError(MiniCRMError):
    """
    业务逻辑异常

    当业务规则验证失败时抛出此异常。
    例如：重复创建客户、违反业务约束等。
    """

    def __init__(self, message: str, business_rule: str = None):
        """
        初始化业务逻辑异常

        Args:
            message: 错误消息
            business_rule: 违反的业务规则（可选）
        """
        super().__init__(message, "BUSINESS_LOGIC_ERROR")
        self.business_rule = business_rule


class ConfigurationError(MiniCRMError):
    """
    配置错误异常

    当应用程序配置有问题时抛出此异常。
    例如：配置文件损坏、必需的配置项缺失等。
    """

    def __init__(self, message: str, config_key: str = None):
        """
        初始化配置错误异常

        Args:
            message: 错误消息
            config_key: 有问题的配置键（可选）
        """
        super().__init__(message, "CONFIGURATION_ERROR")
        self.config_key = config_key


class ServiceError(MiniCRMError):
    """
    服务层异常

    当服务层操作失败时抛出此异常。
    通常包装底层异常，提供更高级别的错误信息。
    """

    def __init__(
        self, message: str, service_name: str = None, original_error: Exception = None
    ):
        """
        初始化服务异常

        Args:
            message: 错误消息
            service_name: 服务名称（可选）
            original_error: 原始异常（可选）
        """
        super().__init__(message, "SERVICE_ERROR")
        self.service_name = service_name
        self.original_error = original_error


class UIError(MiniCRMError):
    """
    用户界面异常

    当UI操作失败时抛出此异常。
    例如：组件初始化失败、界面更新错误等。
    """

    def __init__(self, message: str, component_name: str = None):
        """
        初始化UI异常

        Args:
            message: 错误消息
            component_name: 组件名称（可选）
        """
        super().__init__(message, "UI_ERROR")
        self.component_name = component_name


class FileOperationError(MiniCRMError):
    """
    文件操作异常

    当文件操作失败时抛出此异常。
    例如：文件读写失败、路径不存在等。
    """

    def __init__(self, message: str, file_path: str = None, operation: str = None):
        """
        初始化文件操作异常

        Args:
            message: 错误消息
            file_path: 文件路径（可选）
            operation: 操作类型（可选）
        """
        super().__init__(message, "FILE_OPERATION_ERROR")
        self.file_path = file_path
        self.operation = operation


class AuthenticationError(MiniCRMError):
    """
    认证异常

    当用户认证失败时抛出此异常。
    （为将来可能的用户认证功能预留）
    """

    def __init__(self, message: str, username: str = None):
        """
        初始化认证异常

        Args:
            message: 错误消息
            username: 用户名（可选）
        """
        super().__init__(message, "AUTHENTICATION_ERROR")
        self.username = username


class PermissionError(MiniCRMError):
    """
    权限异常

    当用户没有足够权限执行操作时抛出此异常。
    （为将来可能的权限管理功能预留）
    """

    def __init__(self, message: str, required_permission: str = None):
        """
        初始化权限异常

        Args:
            message: 错误消息
            required_permission: 所需权限（可选）
        """
        super().__init__(message, "PERMISSION_ERROR")
        self.required_permission = required_permission


# 异常处理工具函数
def handle_exception(exception: Exception, logger=None) -> str:
    """
    统一异常处理函数

    Args:
        exception: 要处理的异常
        logger: 日志记录器（可选）

    Returns:
        str: 用户友好的错误消息
    """
    if isinstance(exception, MiniCRMError):
        # MiniCRM自定义异常，直接返回消息
        error_message = str(exception)
    else:
        # 其他异常，包装为通用错误
        error_message = f"系统错误: {str(exception)}"

    # 记录日志
    if logger:
        logger.error(f"异常处理: {error_message}", exc_info=True)

    return error_message


def create_user_friendly_message(exception: Exception) -> str:
    """
    创建用户友好的错误消息

    Args:
        exception: 异常对象

    Returns:
        str: 用户友好的错误消息
    """
    if isinstance(exception, ValidationError):
        if exception.field_name:
            return f"数据验证失败：{exception.field_name} - {exception.message}"
        return f"数据验证失败：{exception.message}"

    elif isinstance(exception, DatabaseError):
        return f"数据库操作失败：{exception.message}"

    elif isinstance(exception, BusinessLogicError):
        return f"业务规则验证失败：{exception.message}"

    elif isinstance(exception, ConfigurationError):
        return f"配置错误：{exception.message}"

    elif isinstance(exception, ServiceError):
        if exception.service_name:
            return f"{exception.service_name}服务错误：{exception.message}"
        return f"服务错误：{exception.message}"

    elif isinstance(exception, UIError):
        return f"界面错误：{exception.message}"

    elif isinstance(exception, FileOperationError):
        return f"文件操作失败：{exception.message}"

    elif isinstance(exception, AuthenticationError):
        return f"认证失败：{exception.message}"

    elif isinstance(exception, PermissionError):
        return f"权限不足：{exception.message}"

    else:
        return f"系统错误：{str(exception)}"
