"""
MiniCRM 基础服务类

定义了所有业务服务的基础类和通用功能，包括：
- 基础服务类
- 事务管理
- 错误处理
- 日志记录
- 数据验证
- 缓存管理
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from ..core import (
    BusinessLogicError,
    MiniCRMLogger,
    ServiceError,
    ValidationError,
    get_logger,
)
from ..models import BaseModel


# 泛型类型变量
T = TypeVar("T", bound=BaseModel)


class BaseService(ABC):
    """
    基础服务类

    所有业务服务都应该继承自这个基础类。
    提供通用的业务逻辑处理、错误处理和日志记录功能。
    """

    def __init__(self, dao=None):
        """
        初始化基础服务

        Args:
            dao: 数据访问对象，将在后续任务中实现
        """
        self._dao = dao
        self._logger = get_logger(self.__class__.__name__)
        self._cache = {}  # 简单的内存缓存

    @property
    def logger(self) -> MiniCRMLogger:
        """获取日志记录器"""
        return self._logger

    def _validate_required_fields(
        self, data: dict[str, Any], required_fields: list[str]
    ) -> None:
        """
        验证必填字段

        Args:
            data: 数据字典
            required_fields: 必填字段列表

        Raises:
            ValidationError: 当必填字段缺失时
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)

        if missing_fields:
            raise ValidationError(f"缺少必填字段: {', '.join(missing_fields)}")

    def _validate_data_types(
        self, data: dict[str, Any], type_mapping: dict[str, type]
    ) -> None:
        """
        验证数据类型

        Args:
            data: 数据字典
            type_mapping: 字段名到类型的映射

        Raises:
            ValidationError: 当数据类型不匹配时
        """
        for field, expected_type in type_mapping.items():
            if field in data and data[field] is not None:
                if not isinstance(data[field], expected_type):
                    raise ValidationError(
                        f"字段 {field} 的类型应该是 {expected_type.__name__}，"
                        f"但实际是 {type(data[field]).__name__}"
                    )

    def _handle_service_error(self, operation: str, error: Exception) -> None:
        """
        处理服务错误

        Args:
            operation: 操作名称
            error: 原始错误

        Raises:
            ServiceError: 包装后的服务错误
        """
        error_message = f"{operation}失败: {str(error)}"
        self._logger.error(error_message, exc_info=True)

        if isinstance(error, ValidationError | BusinessLogicError):
            # 业务逻辑错误直接抛出
            raise error
        else:
            # 其他错误包装为服务错误
            raise ServiceError(error_message, self.__class__.__name__, error) from error

    def _cache_get(self, key: str) -> Any:
        """
        从缓存获取数据

        Args:
            key: 缓存键

        Returns:
            Any: 缓存的数据或None
        """
        return self._cache.get(key)

    def _cache_set(self, key: str, value: Any) -> None:
        """
        设置缓存数据

        Args:
            key: 缓存键
            value: 要缓存的数据
        """
        self._cache[key] = value

    def _cache_clear(self, pattern: str = None) -> None:
        """
        清除缓存

        Args:
            pattern: 缓存键模式，如果为None则清除所有缓存
        """
        if pattern is None:
            self._cache.clear()
        else:
            keys_to_remove = [key for key in self._cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self._cache[key]

    def _log_operation(self, operation: str, details: dict[str, Any] = None) -> None:
        """
        记录操作日志

        Args:
            operation: 操作名称
            details: 操作详情
        """
        if details:
            self._logger.info(f"{operation}: {details}")
        else:
            self._logger.info(operation)

    @abstractmethod
    def get_service_name(self) -> str:
        """
        获取服务名称

        Returns:
            str: 服务名称
        """
        pass

    def health_check(self) -> dict[str, Any]:
        """
        健康检查

        Returns:
            Dict[str, Any]: 健康状态信息
        """
        return {
            "service": self.get_service_name(),
            "status": "healthy",
            "cache_size": len(self._cache),
            "dao_connected": self._dao is not None,
        }


class CRUDService(BaseService):
    """
    CRUD服务基类

    为需要基本增删改查功能的服务提供通用实现。
    """

    def __init__(self, dao=None, model_class: type[T] = None):
        """
        初始化CRUD服务

        Args:
            dao: 数据访问对象
            model_class: 模型类
        """
        super().__init__(dao)
        self._model_class = model_class

    def create(self, data: dict[str, Any]) -> T:
        """
        创建新记录

        Args:
            data: 数据字典

        Returns:
            T: 创建的模型实例

        Raises:
            ValidationError: 当数据验证失败时
            ServiceError: 当创建失败时
        """
        try:
            self._log_operation("创建记录", {"service": self.get_service_name()})

            # 验证数据
            self._validate_create_data(data)

            # 创建模型实例
            if self._model_class:
                instance = self._model_class.from_dict(data)
                instance.validate()

            # 调用子类的具体创建逻辑
            result = self._perform_create(data)

            # 清除相关缓存
            self._cache_clear("list_")

            self._log_operation("记录创建成功", {"id": getattr(result, "id", None)})
            return result

        except Exception as e:
            self._handle_service_error("创建记录", e)

    def get_by_id(self, record_id: int) -> T | None:
        """
        根据ID获取记录

        Args:
            record_id: 记录ID

        Returns:
            Optional[T]: 模型实例或None

        Raises:
            ServiceError: 当查询失败时
        """
        try:
            # 检查缓存
            cache_key = f"get_{record_id}"
            cached_result = self._cache_get(cache_key)
            if cached_result is not None:
                return cached_result

            # 从数据源获取
            result = self._perform_get_by_id(record_id)

            # 缓存结果
            if result is not None:
                self._cache_set(cache_key, result)

            return result

        except Exception as e:
            self._handle_service_error("获取记录", e)

    def update(self, record_id: int, data: dict[str, Any]) -> T:
        """
        更新记录

        Args:
            record_id: 记录ID
            data: 更新数据

        Returns:
            T: 更新后的模型实例

        Raises:
            ValidationError: 当数据验证失败时
            BusinessLogicError: 当记录不存在时
            ServiceError: 当更新失败时
        """
        try:
            self._log_operation(
                "更新记录", {"id": record_id, "service": self.get_service_name()}
            )

            # 验证数据
            self._validate_update_data(data)

            # 调用子类的具体更新逻辑
            result = self._perform_update(record_id, data)

            # 清除相关缓存
            self._cache_clear(f"get_{record_id}")
            self._cache_clear("list_")

            self._log_operation("记录更新成功", {"id": record_id})
            return result

        except Exception as e:
            self._handle_service_error("更新记录", e)

    def delete(self, record_id: int) -> bool:
        """
        删除记录

        Args:
            record_id: 记录ID

        Returns:
            bool: 是否删除成功

        Raises:
            BusinessLogicError: 当记录不存在时
            ServiceError: 当删除失败时
        """
        try:
            self._log_operation(
                "删除记录", {"id": record_id, "service": self.get_service_name()}
            )

            # 调用子类的具体删除逻辑
            result = self._perform_delete(record_id)

            # 清除相关缓存
            self._cache_clear(f"get_{record_id}")
            self._cache_clear("list_")

            self._log_operation("记录删除成功", {"id": record_id})
            return result

        except Exception as e:
            self._handle_service_error("删除记录", e)

    def list_all(self, filters: dict[str, Any] = None) -> list[T]:
        """
        获取所有记录

        Args:
            filters: 过滤条件

        Returns:
            List[T]: 模型实例列表

        Raises:
            ServiceError: 当查询失败时
        """
        try:
            # 生成缓存键
            cache_key = f"list_{hash(str(filters)) if filters else 'all'}"
            cached_result = self._cache_get(cache_key)
            if cached_result is not None:
                return cached_result

            # 从数据源获取
            result = self._perform_list_all(filters)

            # 缓存结果
            self._cache_set(cache_key, result)

            return result

        except Exception as e:
            self._handle_service_error("获取记录列表", e)

    # 抽象方法，子类需要实现
    @abstractmethod
    def _validate_create_data(self, data: dict[str, Any]) -> None:
        """验证创建数据"""
        pass

    @abstractmethod
    def _validate_update_data(self, data: dict[str, Any]) -> None:
        """验证更新数据"""
        pass

    @abstractmethod
    def _perform_create(self, data: dict[str, Any]) -> T:
        """执行创建操作"""
        pass

    @abstractmethod
    def _perform_get_by_id(self, record_id: int) -> T | None:
        """执行根据ID获取操作"""
        pass

    @abstractmethod
    def _perform_update(self, record_id: int, data: dict[str, Any]) -> T:
        """执行更新操作"""
        pass

    @abstractmethod
    def _perform_delete(self, record_id: int) -> bool:
        """执行删除操作"""
        pass

    @abstractmethod
    def _perform_list_all(self, filters: dict[str, Any] = None) -> list[T]:
        """执行获取所有记录操作"""
        pass


class ServiceRegistry:
    """
    服务注册表

    管理所有已注册的服务实例，提供服务发现和依赖注入功能。
    """

    _services: dict[str, BaseService] = {}

    @classmethod
    def register(cls, name: str, service: BaseService) -> None:
        """
        注册服务

        Args:
            name: 服务名称
            service: 服务实例
        """
        cls._services[name] = service

    @classmethod
    def get_service(cls, name: str) -> BaseService | None:
        """
        获取服务

        Args:
            name: 服务名称

        Returns:
            Optional[BaseService]: 服务实例或None
        """
        return cls._services.get(name)

    @classmethod
    def get_all_services(cls) -> dict[str, BaseService]:
        """
        获取所有已注册的服务

        Returns:
            Dict[str, BaseService]: 服务名称到服务实例的映射
        """
        return cls._services.copy()

    @classmethod
    def health_check_all(cls) -> dict[str, dict[str, Any]]:
        """
        对所有服务进行健康检查

        Returns:
            Dict[str, Dict[str, Any]]: 所有服务的健康状态
        """
        results = {}
        for name, service in cls._services.items():
            try:
                results[name] = service.health_check()
            except Exception as e:
                results[name] = {
                    "service": name,
                    "status": "unhealthy",
                    "error": str(e),
                }
        return results


# 服务装饰器
def register_service(name: str):
    """
    服务注册装饰器

    Args:
        name: 服务名称

    Returns:
        装饰器函数
    """

    def decorator(service_class: type[BaseService]):
        # 这里可以在应用启动时自动注册服务
        # 实际注册会在服务实例化时进行
        service_class._service_name = name
        return service_class

    return decorator
