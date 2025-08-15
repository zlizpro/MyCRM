"""
MiniCRM 核心应用程序类

负责管理应用程序的生命周期、资源管理、服务初始化等核心功能。
实现了应用程序的启动、运行和关闭的完整生命周期管理。

严格遵循分层架构：
- 在应用程序层配置依赖关系
- 确保依赖方向正确
- 使用依赖注入管理服务
"""

import logging

from PySide6.QtCore import QObject, Signal

from minicrm.application_config import (
    cleanup_dependencies,
    configure_application_dependencies,
    get_service,
)
from minicrm.core.config import AppConfig
from minicrm.core.exceptions import MiniCRMError
from minicrm.core.interfaces.service_interfaces import (
    IAnalyticsService,
    ICustomerService,
    ISupplierService,
)


class MiniCRMApplication(QObject):
    """
    MiniCRM 核心应用程序类

    这个类是整个应用程序的核心，负责：
    - 应用程序生命周期管理
    - 服务层初始化和管理
    - 数据库连接管理
    - 资源清理和释放
    - 全局状态管理

    Signals:
        startup_completed: 应用程序启动完成信号
        shutdown_started: 应用程序关闭开始信号
        service_error: 服务层错误信号
    """

    # Qt信号定义
    startup_completed = Signal()
    shutdown_started = Signal()
    service_error = Signal(str, str)  # (service_name, error_message)

    def __init__(self, config: AppConfig):
        """
        初始化MiniCRM应用程序

        Args:
            config: 应用程序配置对象
        """
        super().__init__()

        self._config = config
        self._logger = logging.getLogger(__name__)

        # 服务层组件（通过依赖注入获取）
        self._customer_service: ICustomerService | None = None
        self._supplier_service: ISupplierService | None = None
        self._analytics_service: IAnalyticsService | None = None

        # 应用程序状态
        self._is_initialized = False
        self._is_shutting_down = False

        # 初始化应用程序
        self._initialize()

    def _initialize(self) -> None:
        """
        初始化应用程序核心组件

        初始化顺序：
        1. 配置依赖注入
        2. 获取服务实例
        3. 发送启动完成信号
        """
        try:
            self._logger.info("开始初始化MiniCRM应用程序核心组件...")

            # 配置依赖注入
            configure_application_dependencies()

            # 获取服务实例
            self._initialize_services()

            # 标记初始化完成
            self._is_initialized = True
            self._logger.info("MiniCRM应用程序核心组件初始化完成")

            # 发送启动完成信号
            self.startup_completed.emit()

        except Exception as e:
            self._logger.error(f"应用程序初始化失败: {e}", exc_info=True)
            raise MiniCRMError(f"应用程序初始化失败: {e}") from e

    def _initialize_services(self) -> None:
        """
        初始化服务层组件

        通过依赖注入获取服务实例，确保依赖关系正确。
        """
        try:
            self._logger.info("正在初始化服务层组件...")

            # 通过依赖注入获取服务实例
            self._customer_service = get_service(ICustomerService)
            self._logger.debug("客户服务初始化完成")

            self._supplier_service = get_service(ISupplierService)
            self._logger.debug("供应商服务初始化完成")

            self._analytics_service = get_service(IAnalyticsService)
            self._logger.debug("分析服务初始化完成")

            self._logger.info("服务层组件初始化完成")

        except Exception as e:
            self._logger.error(f"服务层初始化失败: {e}", exc_info=True)
            raise MiniCRMError(f"服务层初始化失败: {e}") from e

    def shutdown(self) -> None:
        """
        关闭应用程序

        执行应用程序关闭流程：
        1. 发送关闭开始信号
        2. 清理服务层资源
        3. 关闭数据库连接
        4. 清理其他资源
        """
        if self._is_shutting_down:
            return

        try:
            self._is_shutting_down = True
            self._logger.info("开始关闭MiniCRM应用程序...")

            # 发送关闭开始信号
            self.shutdown_started.emit()

            # 清理服务层资源
            self._cleanup_services()

            self._logger.info("MiniCRM应用程序关闭完成")

        except Exception as e:
            self._logger.error(f"应用程序关闭过程中发生错误: {e}", exc_info=True)

    def _cleanup_services(self) -> None:
        """清理服务层资源"""
        try:
            if self._customer_service:
                if hasattr(self._customer_service, "cleanup"):
                    self._customer_service.cleanup()
                self._customer_service = None

            if self._supplier_service:
                if hasattr(self._supplier_service, "cleanup"):
                    self._supplier_service.cleanup()
                self._supplier_service = None

            if self._analytics_service:
                if hasattr(self._analytics_service, "cleanup"):
                    self._analytics_service.cleanup()
                self._analytics_service = None

            # 清理依赖注入容器
            cleanup_dependencies()

            self._logger.debug("服务层资源清理完成")

        except Exception as e:
            self._logger.error(f"服务层资源清理失败: {e}", exc_info=True)

    # 属性访问器
    @property
    def config(self) -> AppConfig:
        """获取应用程序配置"""
        return self._config

    @property
    def customer_service(self) -> ICustomerService | None:
        """获取客户服务"""
        return self._customer_service

    @property
    def supplier_service(self) -> ISupplierService | None:
        """获取供应商服务"""
        return self._supplier_service

    @property
    def analytics_service(self) -> IAnalyticsService | None:
        """获取分析服务"""
        return self._analytics_service

    @property
    def is_initialized(self) -> bool:
        """检查应用程序是否已初始化"""
        return self._is_initialized

    @property
    def is_shutting_down(self) -> bool:
        """检查应用程序是否正在关闭"""
        return self._is_shutting_down

    def get_service_status(self) -> dict[str, bool]:
        """
        获取所有服务的状态

        Returns:
            Dict[str, bool]: 服务名称到状态的映射
        """
        return {
            "customer_service": self._customer_service is not None,
            "supplier_service": self._supplier_service is not None,
            "analytics_service": self._analytics_service is not None,
        }
