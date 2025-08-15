"""
MiniCRM 应用程序配置

在应用程序层配置依赖关系，确保：
- 遵循依赖方向：UI → Services → Data → Models
- core层不导入其他层的具体实现
- 依赖注入配置集中管理
"""

import logging

from minicrm.core.dependency_injection import container


def configure_application_dependencies():
    """
    配置应用程序依赖关系

    在应用程序层配置所有依赖，确保依赖方向正确
    """
    logger = logging.getLogger(__name__)

    try:
        # 导入接口
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

        # 导入实现类
        from minicrm.services.customer_service import CustomerService
        from minicrm.services.supplier_service import SupplierService

        # 注册数据库管理器（最底层）
        container.register_singleton(DatabaseManager, DatabaseManager)

        # 注册DAO层（依赖DatabaseManager）
        container.register_singleton(ICustomerDAO, CustomerDAO)
        container.register_singleton(ISupplierDAO, SupplierDAO)

        # 注册Service层（依赖DAO层）
        container.register_singleton(ICustomerService, CustomerService)
        container.register_singleton(ISupplierService, SupplierService)
        container.register_singleton(IAnalyticsService, AnalyticsService)

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
