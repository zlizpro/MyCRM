"""
MiniCRM 核心接口定义

定义系统各层之间的接口契约，确保：
- 清晰的依赖关系
- 松耦合的架构设计
- 易于测试和扩展
"""

from .dao_interfaces import (
    IBaseDAO,
    ICustomerDAO,
    ISupplierDAO,
)
from .service_interfaces import (
    IAnalyticsService,
    ICustomerService,
    IFinanceService,
    ISupplierService,
)
from .ui_interfaces import (
    IDashboard,
    IDataTable,
    IFormPanel,
)

__all__ = [
    # Service接口
    "ICustomerService",
    "ISupplierService",
    "IFinanceService",
    "IAnalyticsService",
    # DAO接口
    "IBaseDAO",
    "ICustomerDAO",
    "ISupplierDAO",
    # UI接口
    "IDataTable",
    "IDashboard",
    "IFormPanel",
]
