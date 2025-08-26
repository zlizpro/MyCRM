"""MiniCRM TTK应用程序类

负责管理TTK应用程序的生命周期、资源管理、服务初始化等核心功能.
实现了应用程序的启动、运行和关闭的完整生命周期管理.

严格遵循分层架构:
- 在应用程序层配置依赖关系
- 确保依赖方向正确
- 使用依赖注入管理服务
- 集成所有TTK组件和业务服务

作者: MiniCRM开发团队
"""

import logging
from typing import Any, Dict, Optional

from minicrm.application_config import (
    cleanup_dependencies,
    configure_application_dependencies,
    get_service,
)
from minicrm.config.settings import ConfigManager
from minicrm.core.exceptions import MiniCRMError
from minicrm.core.interfaces.service_interfaces import (
    IAnalyticsService,
    ICustomerService,
    ISettingsService,
    ISupplierService,
    ITaskService,
)
from minicrm.core.ttk_error_handler import TTKErrorHandler
from minicrm.ui.ttk_base.event_manager import EventManager, get_global_event_manager
from minicrm.ui.ttk_base.main_window_ttk import MainWindowTTK
from minicrm.ui.ttk_base.service_integration_manager import (
    create_service_integrations,
    get_global_integration_manager,
)
from minicrm.ui.ttk_base.theme_manager import TTKThemeManager


class MiniCRMApplicationTTK:
    """MiniCRM TTK应用程序类

    这个类是整个TTK应用程序的核心,负责:
    - 应用程序生命周期管理
    - 服务层初始化和管理
    - TTK组件集成和管理
    - 数据库连接管理
    - 资源清理和释放
    - 全局状态管理
    - 导航和页面管理
    """

    def __init__(self, config: ConfigManager):
        """初始化MiniCRM TTK应用程序.

        Args:
            config: 应用程序配置管理器
        """
        self._config = config
        self._logger = logging.getLogger(__name__)

        # 服务层组件(通过依赖注入获取)
        self._customer_service: Optional[ICustomerService] = None
        self._supplier_service: Optional[ISupplierService] = None
        self._analytics_service: Optional[IAnalyticsService] = None
        self._settings_service: Optional[ISettingsService] = None
        self._task_service: Optional[ITaskService] = None

        # 数据库管理器
        self._database_manager = None

        # TTK组件
        self._main_window: Optional[MainWindowTTK] = None
        self._event_manager: Optional[EventManager] = None
        self._theme_manager: Optional[TTKThemeManager] = None
        self._error_handler: Optional[TTKErrorHandler] = None

        # 业务面板引用
        self._panels: Dict[str, Any] = {}

        # 服务集成管理器
        self._integration_manager = None
        self._service_integrations: Dict[str, Any] = {}

        # 应用程序状态
        self._is_initialized = False
        self._is_running = False
        self._is_shutting_down = False

        # 初始化应用程序
        self._initialize()

    def _initialize(self) -> None:
        """初始化应用程序核心组件

        初始化顺序:
        1. 配置依赖注入
        2. 获取服务实例
        3. 初始化TTK组件
        4. 设置主窗口和面板
        5. 配置导航和路由
        """
        try:
            self._logger.info("开始初始化MiniCRM TTK应用程序...")

            # 配置依赖注入
            configure_application_dependencies()

            # 获取服务实例
            self._initialize_services()

            # 初始化TTK组件
            self._initialize_ttk_components()

            # 初始化服务集成
            self._initialize_service_integrations()

            # 设置主窗口
            self._setup_main_window()

            # 配置导航系统(包含业务面板注册)
            self._setup_navigation()

            # 标记初始化完成
            self._is_initialized = True
            self._logger.info("MiniCRM TTK应用程序初始化完成")

        except Exception as e:
            self._logger.error(f"TTK应用程序初始化失败: {e}", exc_info=True)
            raise MiniCRMError(f"TTK应用程序初始化失败: {e}") from e

    def _initialize_services(self) -> None:
        """初始化服务层组件

        通过依赖注入获取服务实例,确保依赖关系正确.
        """
        try:
            self._logger.info("正在初始化服务层组件...")

            # 首先获取数据库管理器并初始化数据库
            from minicrm.data.database import DatabaseManager

            self._database_manager = get_service(DatabaseManager)
            self._database_manager.initialize_database()
            self._logger.debug("数据库管理器初始化完成")

            # 通过依赖注入获取服务实例
            self._customer_service = get_service(ICustomerService)
            self._logger.debug("客户服务初始化完成")

            self._supplier_service = get_service(ISupplierService)
            self._logger.debug("供应商服务初始化完成")

            self._analytics_service = get_service(IAnalyticsService)
            self._logger.debug("分析服务初始化完成")

            self._settings_service = get_service(ISettingsService)
            self._logger.debug("设置服务初始化完成")

            self._task_service = get_service(ITaskService)
            self._logger.debug("任务服务初始化完成")

            self._logger.info("服务层组件初始化完成")

        except Exception as e:
            self._logger.error(f"服务层初始化失败: {e}", exc_info=True)
            raise MiniCRMError(f"服务层初始化失败: {e}") from e

    def _initialize_ttk_components(self) -> None:
        """初始化TTK核心组件"""
        try:
            self._logger.info("正在初始化TTK核心组件...")

            # 初始化事件管理器
            self._event_manager = get_global_event_manager()
            self._logger.debug("事件管理器初始化完成")

            # 初始化主题管理器
            self._theme_manager = TTKThemeManager()
            self._logger.debug("主题管理器初始化完成")

            # 初始化错误处理器
            self._error_handler = TTKErrorHandler()
            self._logger.debug("错误处理器初始化完成")

            self._logger.info("TTK核心组件初始化完成")

        except Exception as e:
            self._logger.error(f"TTK组件初始化失败: {e}", exc_info=True)
            raise MiniCRMError(f"TTK组件初始化失败: {e}") from e

    def _initialize_service_integrations(self) -> None:
        """初始化服务集成"""
        try:
            self._logger.info("正在初始化服务集成...")

            # 获取全局集成管理器
            self._integration_manager = get_global_integration_manager()

            # 导入服务类
            from minicrm.services.contract_service import ContractService
            from minicrm.services.finance_service import FinanceService

            # 创建服务集成器
            self._service_integrations = create_service_integrations(
                customer_service=self._customer_service,
                supplier_service=self._supplier_service,
                finance_service=get_service(FinanceService),
                task_service=self._task_service,
                contract_service=get_service(ContractService),
            )

            # 注册全局事件处理器
            self._register_global_event_handlers()

            self._logger.info("服务集成初始化完成")

        except Exception as e:
            self._logger.error(f"服务集成初始化失败: {e}", exc_info=True)
            raise MiniCRMError(f"服务集成初始化失败: {e}") from e

    def _register_global_event_handlers(self) -> None:
        """注册全局事件处理器"""
        if not self._integration_manager:
            return

        # 客户相关事件
        self._integration_manager.register_event_handler(
            "customer_created", self._on_customer_created
        )
        self._integration_manager.register_event_handler(
            "customer_updated", self._on_customer_updated
        )
        self._integration_manager.register_event_handler(
            "customer_deleted", self._on_customer_deleted
        )

        # 供应商相关事件
        self._integration_manager.register_event_handler(
            "supplier_created", self._on_supplier_created
        )
        self._integration_manager.register_event_handler(
            "supplier_updated", self._on_supplier_updated
        )
        self._integration_manager.register_event_handler(
            "supplier_deleted", self._on_supplier_deleted
        )

        # 任务相关事件
        self._integration_manager.register_event_handler(
            "task_created", self._on_task_created
        )
        self._integration_manager.register_event_handler(
            "task_updated", self._on_task_updated
        )
        self._integration_manager.register_event_handler(
            "task_completed", self._on_task_completed
        )

        # 合同相关事件
        self._integration_manager.register_event_handler(
            "contract_created", self._on_contract_created
        )
        self._integration_manager.register_event_handler(
            "contract_updated", self._on_contract_updated
        )

        # 财务相关事件
        self._integration_manager.register_event_handler(
            "payment_recorded", self._on_payment_recorded
        )

    def _setup_main_window(self) -> None:
        """设置主窗口"""
        try:
            self._logger.info("正在设置主窗口...")

            # 创建主窗口
            self._main_window = MainWindowTTK(
                title="MiniCRM - 板材行业客户关系管理系统",
                size=(1400, 900),
                min_size=(1000, 700),
            )

            # 设置窗口关闭事件
            self._main_window.add_event_handler("before_close", self._on_before_close)
            self._main_window.add_event_handler("closing", self._on_window_closing)

            # 应用默认主题
            if self._theme_manager:
                self._theme_manager.set_theme("default")

            # 设置状态栏信息
            self._main_window.set_status_text("MiniCRM TTK版本已启动")
            self._main_window.set_status_text("数据库: 已连接", "database")

            self._logger.info("主窗口设置完成")

        except Exception as e:
            self._logger.error(f"主窗口设置失败: {e}", exc_info=True)
            raise MiniCRMError(f"主窗口设置失败: {e}") from e

    def _setup_navigation(self) -> None:
        """设置导航系统"""
        try:
            self._logger.info("正在设置TTK导航注册系统...")

            # 临时跳过复杂的导航系统设置,直接显示主窗口
            self._logger.info("使用简化的导航系统(临时方案)")

            # TODO: 后续需要修复完整的导航系统
            # self._main_window.setup_navigation_registry(self)

            self._logger.info("TTK导航注册系统设置完成(简化版本)")

        except Exception as e:
            self._logger.error(f"导航系统设置失败: {e}", exc_info=True)
            raise MiniCRMError(f"导航系统设置失败: {e}") from e

    def run(self) -> None:
        """运行应用程序"""
        if not self._is_initialized:
            raise MiniCRMError("应用程序未初始化")

        if self._is_running:
            self._logger.warning("应用程序已在运行")
            return

        try:
            self._is_running = True
            self._logger.info("启动MiniCRM TTK应用程序...")

            # 显示主窗口
            if self._main_window:
                self._main_window.deiconify()  # 确保窗口可见
                self._main_window.lift()  # 提升到前台
                self._main_window.focus_force()  # 获得焦点

                # 进入主事件循环
                self._main_window.mainloop()

        except Exception as e:
            self._logger.error(f"应用程序运行失败: {e}", exc_info=True)
            raise MiniCRMError(f"应用程序运行失败: {e}") from e
        finally:
            self._is_running = False

    def shutdown(self) -> None:
        """关闭应用程序

        执行应用程序关闭流程:
        1. 检查是否可以关闭
        2. 清理TTK组件资源
        3. 清理服务层资源
        4. 关闭数据库连接
        5. 清理其他资源
        """
        if self._is_shutting_down:
            return

        try:
            self._is_shutting_down = True
            self._logger.info("开始关闭MiniCRM TTK应用程序...")

            # 清理TTK组件资源
            self._cleanup_ttk_components()

            # 清理服务层资源
            self._cleanup_services()

            self._logger.info("MiniCRM TTK应用程序关闭完成")

        except Exception as e:
            self._logger.error(f"应用程序关闭过程中发生错误: {e}", exc_info=True)

    def _cleanup_ttk_components(self) -> None:
        """清理TTK组件资源"""
        try:
            # 清理主窗口
            if self._main_window:
                self._main_window.cleanup()
                self._main_window = None

            # 清理事件管理器
            if self._event_manager:
                self._event_manager.cleanup()
                self._event_manager = None

            # 清理主题管理器
            if self._theme_manager:
                self._theme_manager = None

            # 清理错误处理器
            if self._error_handler:
                self._error_handler = None

            # 清理面板引用
            self._panels.clear()

            self._logger.debug("TTK组件资源清理完成")

        except Exception as e:
            self._logger.error(f"TTK组件资源清理失败: {e}", exc_info=True)

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

            if self._settings_service:
                if hasattr(self._settings_service, "cleanup"):
                    self._settings_service.cleanup()
                self._settings_service = None

            if self._task_service:
                if hasattr(self._task_service, "cleanup"):
                    self._task_service.cleanup()
                self._task_service = None

            # 清理依赖注入容器
            cleanup_dependencies()

            self._logger.debug("服务层资源清理完成")

        except Exception as e:
            self._logger.error(f"服务层资源清理失败: {e}", exc_info=True)

    def _on_before_close(self) -> None:
        """窗口关闭前事件处理"""
        self._logger.info("准备关闭应用程序...")

    def _on_window_closing(self) -> None:
        """窗口关闭事件处理"""
        self.shutdown()

    # 属性访问器
    @property
    def config(self) -> ConfigManager:
        """获取应用程序配置."""
        return self._config

    @property
    def main_window(self) -> Optional[MainWindowTTK]:
        """获取主窗口"""
        return self._main_window

    @property
    def customer_service(self) -> Optional[ICustomerService]:
        """获取客户服务"""
        return self._customer_service

    @property
    def supplier_service(self) -> Optional[ISupplierService]:
        """获取供应商服务"""
        return self._supplier_service

    @property
    def analytics_service(self) -> Optional[IAnalyticsService]:
        """获取分析服务"""
        return self._analytics_service

    @property
    def settings_service(self) -> Optional[ISettingsService]:
        """获取设置服务"""
        return self._settings_service

    @property
    def task_service(self) -> Optional[ITaskService]:
        """获取任务服务"""
        return self._task_service

    @property
    def database_manager(self):
        """获取数据库管理器"""
        return self._database_manager

    @property
    def is_initialized(self) -> bool:
        """检查应用程序是否已初始化"""
        return self._is_initialized

    @property
    def is_running(self) -> bool:
        """检查应用程序是否正在运行"""
        return self._is_running

    @property
    def is_shutting_down(self) -> bool:
        """检查应用程序是否正在关闭"""
        return self._is_shutting_down

    def get_service_status(self) -> Dict[str, bool]:
        """获取所有服务的状态

        Returns:
            Dict[str, bool]: 服务名称到状态的映射
        """
        return {
            "customer_service": self._customer_service is not None,
            "supplier_service": self._supplier_service is not None,
            "analytics_service": self._analytics_service is not None,
            "settings_service": self._settings_service is not None,
            "task_service": self._task_service is not None,
        }

    def get_service(self, service_type):
        """获取指定类型的服务实例

        Args:
            service_type: 服务接口类型或服务名称字符串

        Returns:
            服务实例

        Raises:
            MiniCRMError: 当服务未初始化或获取失败时
        """
        try:
            # 如果传入的是字符串,转换为对应的服务实例
            if isinstance(service_type, str):
                service_map = {
                    "analytics": self._analytics_service,
                    "customer": self._customer_service,
                    "supplier": self._supplier_service,
                    "settings": self._settings_service,
                    "task": self._task_service,
                    "finance": get_service,  # 通过依赖注入获取
                    "backup": get_service,  # 通过依赖注入获取
                    "contract": get_service,  # 通过依赖注入获取
                    "quote": get_service,  # 通过依赖注入获取
                }

                if service_type in service_map:
                    service_getter = service_map[service_type]
                    if service_getter == get_service:
                        # 映射服务名称到实际的服务类
                        # 导入服务类
                        from minicrm.services.backup_service import BackupService
                        from minicrm.services.contract_service import ContractService
                        from minicrm.services.finance_service import FinanceService
                        from minicrm.services.quote_service import (
                            QuoteServiceRefactored,
                        )

                        service_class_map = {
                            "finance": FinanceService,
                            "backup": BackupService,
                            "contract": ContractService,
                            "quote": QuoteServiceRefactored,
                        }

                        service_class = service_class_map.get(service_type)
                        if service_class:
                            return get_service(service_class)
                        raise MiniCRMError(f"未知的服务类型: {service_type}")
                    return service_getter
                raise MiniCRMError(f"未知的服务类型: {service_type}")
            # 直接使用应用程序配置中的 get_service 函数
            return get_service(service_type)
        except Exception as e:
            self._logger.error(f"获取服务失败: {service_type}, 错误: {e}")
            raise MiniCRMError(f"获取服务失败: {service_type}") from e

    def get_application_info(self) -> Dict[str, Any]:
        """获取应用程序信息

        Returns:
            应用程序信息字典
        """
        info = {
            "application_type": "TTK",
            "is_initialized": self._is_initialized,
            "is_running": self._is_running,
            "is_shutting_down": self._is_shutting_down,
            "services": self.get_service_status(),
            "main_window": None,
        }

        if self._main_window:
            info["main_window"] = self._main_window.get_main_window_info()

        return info

    # ==================== 事件处理方法 ====================

    def _on_customer_created(
        self, customer_id: int, customer_data: dict[str, Any]
    ) -> None:
        """处理客户创建事件"""
        self._logger.info(
            f"客户已创建: ID={customer_id}, 名称={customer_data.get('name')}"
        )
        # 可以在这里添加其他处理逻辑,如刷新相关面板

    def _on_customer_updated(
        self, customer_id: int, customer_data: dict[str, Any]
    ) -> None:
        """处理客户更新事件"""
        self._logger.info(f"客户已更新: ID={customer_id}")
        # 可以在这里添加其他处理逻辑,如刷新相关面板

    def _on_customer_deleted(self, customer_id: int) -> None:
        """处理客户删除事件"""
        self._logger.info(f"客户已删除: ID={customer_id}")
        # 可以在这里添加其他处理逻辑,如刷新相关面板

    def _on_supplier_created(
        self, supplier_id: int, supplier_data: dict[str, Any]
    ) -> None:
        """处理供应商创建事件"""
        self._logger.info(
            f"供应商已创建: ID={supplier_id}, 名称={supplier_data.get('name')}"
        )

    def _on_supplier_updated(
        self, supplier_id: int, supplier_data: dict[str, Any]
    ) -> None:
        """处理供应商更新事件"""
        self._logger.info(f"供应商已更新: ID={supplier_id}")

    def _on_supplier_deleted(self, supplier_id: int) -> None:
        """处理供应商删除事件"""
        self._logger.info(f"供应商已删除: ID={supplier_id}")

    def _on_task_created(self, task_id: int, task_data: dict[str, Any]) -> None:
        """处理任务创建事件"""
        self._logger.info(f"任务已创建: ID={task_id}, 标题={task_data.get('title')}")

    def _on_task_updated(self, task_id: int, task_data: dict[str, Any]) -> None:
        """处理任务更新事件"""
        self._logger.info(f"任务已更新: ID={task_id}")

    def _on_task_completed(self, task_id: int) -> None:
        """处理任务完成事件"""
        self._logger.info(f"任务已完成: ID={task_id}")

    def _on_contract_created(
        self, contract_id: int, contract_data: dict[str, Any]
    ) -> None:
        """处理合同创建事件"""
        self._logger.info(
            f"合同已创建: ID={contract_id}, 标题={contract_data.get('title')}"
        )

    def _on_contract_updated(
        self, contract_id: int, contract_data: dict[str, Any]
    ) -> None:
        """处理合同更新事件"""
        self._logger.info(f"合同已更新: ID={contract_id}")

    def _on_payment_recorded(
        self, payment_id: int, payment_data: dict[str, Any]
    ) -> None:
        """处理收付款记录事件"""
        self._logger.info(
            f"收付款已记录: ID={payment_id}, 金额={payment_data.get('amount')}"
        )

    # ==================== 服务集成访问器 ====================

    @property
    def service_integrations(self) -> dict[str, Any]:
        """获取服务集成器字典"""
        return self._service_integrations

    @property
    def integration_manager(self):
        """获取集成管理器"""
        return self._integration_manager

    def get_service_integration(self, service_name: str) -> Any:
        """获取指定的服务集成器

        Args:
            service_name: 服务名称 (customer, supplier, finance, task, contract)

        Returns:
            服务集成器实例
        """
        return self._service_integrations.get(service_name)
