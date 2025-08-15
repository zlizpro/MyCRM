"""
MiniCRM 服务层模块

包含所有业务逻辑服务：
- 基础服务类
- 客户管理服务
- 供应商管理服务
- 财务管理服务
- 分析服务
- 报价管理服务
- 合同管理服务
- 任务管理服务

这个模块实现了应用程序的核心业务逻辑，处理数据验证、业务规则和流程控制。
服务层位于UI层和数据层之间，提供统一的业务接口。
"""

# 版本信息
__version__ = "1.0.0"

# 导入基础服务类
from .base_service import BaseService, CRUDService, ServiceRegistry, register_service

# 导入具体业务服务（将在后续任务中实现）
# from .customer_service import CustomerService
# from .supplier_service import SupplierService
# from .finance_service import FinanceService
# from .analytics_service import AnalyticsService
# from .quote_service import QuoteService
# from .contract_service import ContractService
# from .task_service import TaskService

# 导出的公共接口
__all__ = [
    # 基础服务
    "BaseService",
    "CRUDService",
    "ServiceRegistry",
    "register_service",
    # 具体业务服务（将在后续任务中添加）
    # "CustomerService",
    # "SupplierService",
    # "FinanceService",
    # "AnalyticsService",
    # "QuoteService",
    # "ContractService",
    # "TaskService",
]
