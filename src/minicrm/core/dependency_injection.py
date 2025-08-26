"""
MiniCRM 依赖注入容器

提供依赖注入功能,确保:
- 松耦合的架构设计
- 易于测试和扩展
- 统一的依赖管理
"""

import logging
from collections.abc import Callable
from typing import Any, TypeVar

from minicrm.core.exceptions import DependencyError


T = TypeVar("T")


class DIContainer:
    """
    依赖注入容器

    管理系统中所有组件的依赖关系,支持:
    - 单例模式
    - 工厂模式
    - 接口绑定
    - 生命周期管理
    """

    def __init__(self):
        """初始化依赖注入容器"""
        self._services: dict[str, Any] = {}
        self._factories: dict[str, Callable] = {}
        self._singletons: dict[str, Any] = {}
        self._bindings: dict[type, type] = {}
        self._logger = logging.getLogger(__name__)

    def register_singleton(self, interface: type[T], implementation: type[T]) -> None:
        """
        注册单例服务

        Args:
            interface: 接口类型
            implementation: 实现类型
        """
        key = self._get_key(interface)
        self._bindings[interface] = implementation
        self._logger.debug(f"注册单例服务: {key}")

    def register_transient(self, interface: type[T], implementation: type[T]) -> None:
        """
        注册瞬态服务(每次创建新实例)

        Args:
            interface: 接口类型
            implementation: 实现类型
        """
        key = self._get_key(interface)
        self._bindings[interface] = implementation
        self._logger.debug(f"注册瞬态服务: {key}")

    def register_factory(self, interface: type[T], factory: Callable[[], T]) -> None:
        """
        注册工厂方法

        Args:
            interface: 接口类型
            factory: 工厂方法
        """
        key = self._get_key(interface)
        self._factories[key] = factory
        self._logger.debug(f"注册工厂方法: {key}")

    def register_instance(self, interface: type[T], instance: T) -> None:
        """
        注册实例

        Args:
            interface: 接口类型
            instance: 实例对象
        """
        key = self._get_key(interface)
        self._singletons[key] = instance
        self._logger.debug(f"注册实例: {key}")

    def resolve(self, interface: type[T]) -> T:
        """
        解析依赖

        Args:
            interface: 接口类型

        Returns:
            T: 实现实例

        Raises:
            DependencyError: 依赖解析失败
        """
        key = self._get_key(interface)

        try:
            # 检查是否有已注册的实例
            if key in self._singletons:
                return self._singletons[key]

            # 检查是否有工厂方法
            if key in self._factories:
                instance = self._factories[key]()
                self._singletons[key] = instance
                return instance

            # 检查是否有绑定的实现
            if interface in self._bindings:
                implementation = self._bindings[interface]
                instance = self._create_instance(implementation)
                self._singletons[key] = instance
                return instance

            raise DependencyError(f"未找到接口的实现: {interface}")

        except Exception as e:
            self._logger.error(f"依赖解析失败: {interface}, 错误: {e}")
            raise DependencyError(f"依赖解析失败: {interface}") from e

    def _create_instance(self, implementation: type[T]) -> T:
        """
        创建实例

        Args:
            implementation: 实现类型

        Returns:
            T: 创建的实例
        """
        try:
            # 获取构造函数参数
            import inspect
            from typing import get_type_hints

            signature = inspect.signature(implementation.__init__)

            # 使用get_type_hints来正确处理字符串类型注解
            try:
                type_hints = get_type_hints(implementation.__init__)
            except (NameError, AttributeError):
                # 如果无法获取类型提示,则使用原始的annotation
                type_hints = {}
                for param_name, param in signature.parameters.items():
                    if param.annotation != inspect.Parameter.empty:
                        type_hints[param_name] = param.annotation

            # 解析构造函数依赖
            kwargs = {}
            for param_name, param in signature.parameters.items():
                if param_name == "self":
                    continue

                # 优先使用type_hints,fallback到原始annotation
                param_type = type_hints.get(param_name, param.annotation)

                if param_type != inspect.Parameter.empty and param_type is not None:
                    # 跳过字符串类型的注解,如果无法解析
                    if isinstance(param_type, str):
                        self._logger.warning(f"跳过字符串类型注解: {param_name}: {param_type}")
                        continue

                    # 递归解析依赖
                    dependency = self.resolve(param_type)
                    kwargs[param_name] = dependency

            return implementation(**kwargs)

        except Exception as e:
            self._logger.error(f"创建实例失败: {implementation}, 错误: {e}")
            raise DependencyError(f"创建实例失败: {implementation}") from e

    def _get_key(self, interface: type) -> str:
        """
        获取接口的键名

        Args:
            interface: 接口类型

        Returns:
            str: 键名
        """
        return f"{interface.__module__}.{interface.__name__}"

    def clear(self) -> None:
        """清理所有注册的服务"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._bindings.clear()
        self._logger.debug("依赖注入容器已清理")


# 全局依赖注入容器实例
container = DIContainer()


def inject(interface: type[T]) -> T:
    """
    依赖注入装饰器函数

    Args:
        interface: 接口类型

    Returns:
        T: 实现实例
    """
    return container.resolve(interface)


def configure_dependencies():
    """
    配置系统依赖关系

    确保依赖方向正确:UI → Services → Data → Models
    """
    from minicrm.core.interfaces.dao_interfaces import (
        ICustomerDAO,
        ISupplierDAO,
    )
    from minicrm.core.interfaces.service_interfaces import (
        IAnalyticsService,
        ICustomerService,
        ISupplierService,
    )
    from minicrm.data.dao.customer_dao import CustomerDAO
    from minicrm.data.dao.supplier_dao import SupplierDAO
    from minicrm.data.database import DatabaseManager
    from minicrm.services.analytics_service import AnalyticsService
    from minicrm.services.customer_service import CustomerService
    from minicrm.services.supplier_service import SupplierService

    # 注册数据库管理器(最底层)
    container.register_singleton(DatabaseManager, DatabaseManager)

    # 注册DAO层(依赖DatabaseManager)
    container.register_singleton(ICustomerDAO, CustomerDAO)
    container.register_singleton(ISupplierDAO, SupplierDAO)

    # 注册Service层(依赖DAO层)
    container.register_singleton(ICustomerService, CustomerService)
    container.register_singleton(ISupplierService, SupplierService)
    container.register_singleton(IAnalyticsService, AnalyticsService)

    # UI层将通过构造函数注入Service层依赖

    logging.getLogger(__name__).info(
        "依赖关系配置完成 - 遵循UI → Services → Data → Models"
    )
