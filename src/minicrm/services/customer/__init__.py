"""MiniCRM 客户服务模块.

提供客户相关的所有业务逻辑服务:
- CustomerService: 统一的客户服务门面(推荐使用)
- CustomerCoreService: 客户核心CRUD操作
- CustomerSearchService: 客户搜索和筛选
- CustomerValueService: 客户价值评分和统计

使用示例:
    from minicrm.services.customer import CustomerService

    # 创建服务实例
    customer_service = CustomerService(customer_dao)

    # 使用服务
    customer_id = customer_service.create_customer(customer_data)
"""

from minicrm.services.customer.customer_core_service import CustomerCoreService
from minicrm.services.customer.customer_search_service import CustomerSearchService
from minicrm.services.customer.customer_service_facade import (
    CustomerService,  # 别名, 保持向后兼容性
    CustomerServiceFacade,
)
from minicrm.services.customer.customer_value_service import CustomerValueService


__all__ = [
    "CustomerCoreService",  # 核心服务
    "CustomerSearchService",  # 搜索服务
    "CustomerService",  # 主要接口
    "CustomerServiceFacade",  # 门面实现
    "CustomerValueService",  # 价值评分服务
]
