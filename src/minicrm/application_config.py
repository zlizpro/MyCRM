"""
MiniCRM 应用程序配置

在应用程序层配置依赖关系,确保:
- 遵循依赖方向:UI → Services → Data → Models
- core层不导入其他层的具体实现
- 依赖注入配置集中管理
"""

import logging

from minicrm.core.dependency_injection import container


def configure_application_dependencies():
    """
    配置应用程序依赖关系

    在应用程序层配置所有依赖,确保依赖方向正确
    """
    logger = logging.getLogger(__name__)

    try:
        # 导入接口

        # 注册数据库管理器(最底层)
        # 使用工厂方法创建 DatabaseManager,提供数据库路径
        from pathlib import Path

        from minicrm.core.interfaces.dao_interfaces import (
            ICustomerDAO,
            ISupplierDAO,
        )
        from minicrm.core.interfaces.service_interfaces import (
            IAnalyticsService,
            IBackupService,
            IContractService,
            ICustomerService,
            IFinanceService,
            IQuoteService,
            ISettingsService,
            ISupplierService,
            ITaskService,
        )
        from minicrm.data.dao.business_dao import QuoteDAO
        from minicrm.data.dao.customer_dao import CustomerDAO
        from minicrm.data.dao.interaction_dao import InteractionDAO
        from minicrm.data.dao.supplier_dao import SupplierDAO
        from minicrm.data.database import DatabaseManager
        from minicrm.services.analytics_service import AnalyticsService

        # 导入实现类
        from minicrm.services.backup_service import BackupService
        from minicrm.services.contract_service import ContractService
        from minicrm.services.customer_service import CustomerService
        from minicrm.services.finance_service import FinanceService
        from minicrm.services.quote_service import QuoteServiceRefactored
        from minicrm.services.settings_service import SettingsService
        from minicrm.services.supplier_service import SupplierService
        from minicrm.services.task_service import TaskService

        def create_database_manager():
            # 获取用户数据目录
            data_dir = Path.home() / "Library" / "Application Support" / "MiniCRM"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "minicrm.db"
            return DatabaseManager(db_path)

        container.register_factory(DatabaseManager, create_database_manager)

        # 注册DAO层(依赖DatabaseManager)
        container.register_singleton(ICustomerDAO, CustomerDAO)
        container.register_singleton(ISupplierDAO, SupplierDAO)
        # 同时注册具体类,以支持直接依赖
        container.register_singleton(CustomerDAO, CustomerDAO)
        container.register_singleton(SupplierDAO, SupplierDAO)
        container.register_singleton(InteractionDAO, InteractionDAO)
        container.register_singleton(QuoteDAO, QuoteDAO)

        # 注册Service层(依赖DAO层)
        container.register_singleton(ICustomerService, CustomerService)
        container.register_singleton(ISupplierService, SupplierService)
        container.register_singleton(IAnalyticsService, AnalyticsService)
        container.register_singleton(IFinanceService, FinanceService)
        container.register_singleton(IBackupService, BackupService)
        container.register_singleton(IContractService, ContractService)
        container.register_singleton(IQuoteService, QuoteServiceRefactored)
        container.register_singleton(ISettingsService, SettingsService)
        container.register_singleton(ITaskService, TaskService)
        # 注意:ImportExportService有依赖问题,暂时跳过注册
        # container.register_singleton(IImportExportService, ImportExportService)

        # 同时注册具体类,以支持直接依赖
        container.register_singleton(FinanceService, FinanceService)
        container.register_singleton(BackupService, BackupService)
        container.register_singleton(ContractService, ContractService)
        container.register_singleton(QuoteServiceRefactored, QuoteServiceRefactored)
        container.register_singleton(SettingsService, SettingsService)
        container.register_singleton(TaskService, TaskService)
        # 注意:ImportExportService有依赖问题,暂时跳过注册
        # container.register_singleton(ImportExportService, ImportExportService)

        logger.info("✅ 应用程序依赖关系配置完成 - 遵循UI → Services → Data → Models")

    except Exception as e:
        logger.error(f"❌ 依赖关系配置失败: {e}")
        raise


def get_service(interface_type):
    """
    获取服务实例

    Args:
        interface_type: 服务接口类型

    Returns:
        服务实例
    """
    return container.resolve(interface_type)


def cleanup_dependencies():
    """清理依赖关系"""
    container.clear()
    logging.getLogger(__name__).info("依赖关系已清理")
