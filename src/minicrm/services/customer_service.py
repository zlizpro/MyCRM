"""MiniCRM 客户管理服务 - 兼容性包装器.

⚠️ 重要提示: 此文件已重构为兼容性包装器
新的模块化实现位于: src/minicrm/services/customer/

推荐使用新的导入方式:
    from minicrm.services.customer import CustomerService

此文件保持向后兼容性,但建议迁移到新的模块化结构.

重构收益:
- 文件大小从757行减少到4个专门的服务文件
- 符合MiniCRM架构标准(每个文件<600行)
- 提高代码可维护性和团队协作效率
- 更好的单一职责原则实现
"""

from __future__ import annotations

from typing import Any
import warnings

from minicrm.data.dao.customer_dao import CustomerDAO

# 导入新的模块化实现
from minicrm.services.customer import CustomerService as NewCustomerService


class CustomerService:
    """客户管理服务 - 兼容性包装器.

    ⚠️ 此类已重构为兼容性包装器,实际功能由新的模块化服务提供.

    建议迁移到新的导入方式:
        from minicrm.services.customer import CustomerService

    此包装器保持完全的向后兼容性.
    """

    def __init__(self, customer_dao: CustomerDAO):
        """初始化客户服务.

        Args:
            customer_dao: 客户数据访问对象
        """
        # 发出弃用警告
        warnings.warn(
            "直接导入 CustomerService 已弃用,请使用: "
            "from minicrm.services.customer import CustomerService",
            DeprecationWarning,
            stacklevel=2,
        )

        # 委托给新的实现
        self._service = NewCustomerService(customer_dao)

    # ========== 委托所有方法到新的实现 ==========

    def create_customer(self, customer_data: dict[str, Any]) -> int:
        """创建新客户."""
        return self._service.create_customer(customer_data)

    def update_customer(self, customer_id: int, data: dict[str, Any]) -> bool:
        """更新客户信息."""
        return self._service.update_customer(customer_id, data)

    def delete_customer(self, customer_id: int) -> bool:
        """删除客户."""
        return self._service.delete_customer(customer_id)

    def calculate_customer_value_score(self, customer_id: int) -> dict[str, Any]:
        """计算客户价值评分."""
        return self._service.calculate_customer_value_score(customer_id)

    def search_customers(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """搜索客户."""
        return self._service.search_customers(query, filters, page, page_size)

    def get_all_customers(
        self, page: int = 1, page_size: int = 100
    ) -> list[dict[str, Any]]:
        """获取所有客户列表."""
        return self._service.get_all_customers(page, page_size)

    def get_customer_by_id(self, customer_id: int) -> dict[str, Any] | None:
        """根据ID获取客户信息."""
        return self._service.get_customer_by_id(customer_id)

    def get_total_count(self) -> int:
        """获取客户总数."""
        return self._service.get_total_count()

    def get_customer_statistics(self) -> dict[str, Any]:
        """获取客户统计信息."""
        return self._service.get_customer_statistics()

    def get_advanced_search_filters(self) -> dict[str, Any]:
        """获取高级搜索筛选器配置."""
        return self._service.get_advanced_search_filters()
