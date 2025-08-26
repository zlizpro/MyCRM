"""MiniCRM 客户搜索服务.

提供客户搜索和筛选功能的业务逻辑处理:
- 客户搜索和筛选功能
- 分页查询
- 高级搜索筛选器配置

严格遵循分层架构和模块化原则.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from minicrm.core.exceptions import ServiceError


if TYPE_CHECKING:
    from minicrm.data.dao.customer_dao import CustomerDAO


# 导入transfunctions模块
try:
    from minicrm.transfunctions.data_formatting import format_currency, format_phone
    from minicrm.transfunctions.search_templates import paginated_search_template
except ImportError:
    # 如果transfunctions模块不存在, 提供临时实现
    def format_phone(phone: str) -> str:
        """临时电话格式化函数."""
        return phone

    def format_currency(amount: float) -> str:
        """临时货币格式化函数."""
        return f"¥{amount:,.2f}"

    def paginated_search_template(
        dao: Any,
        query: str,
        filters: dict[str, Any],
        page: int,
        page_size: int,
        config: dict[str, Any],
    ) -> Any:
        """临时分页搜索模板函数."""
        # 使用未使用的参数避免警告
        _ = dao, query, filters, page, page_size, config
        return type("SearchResult", (), {"items": [], "total": 0})()


class CustomerSearchService:
    """客户搜索服务实现.

    负责客户搜索相关的业务逻辑:
    - 客户搜索和筛选
    - 分页查询
    - 搜索结果格式化

    严格遵循单一职责原则和模块化标准.
    """

    def __init__(self, customer_dao: CustomerDAO):
        """初始化客户搜索服务.

        Args:
            customer_dao: 客户数据访问对象
        """
        self._customer_dao = customer_dao
        self._logger = logging.getLogger(__name__)
        self._logger.info("客户搜索服务初始化完成")

    def search_customers(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """搜索客户 - 使用transfunctions分页搜索模板.

        Args:
            query: 搜索关键词
            filters: 筛选条件
            page: 页码
            page_size: 每页大小

        Returns:
            Tuple[List[Dict[str, Any]], int]: (客户列表, 总数)
        """
        try:
            # 使用transfunctions分页搜索模板
            search_config = {
                "search_fields": ["name", "phone", "company_name", "email"],
                "filter_fields": ["customer_level", "customer_type", "status"],
                "order_by": "created_at DESC",
            }

            result = paginated_search_template(
                dao=self._customer_dao,
                query=query,
                filters=filters or {},
                page=page,
                page_size=page_size,
                config=search_config,
            )

            # 格式化客户数据
            formatted_customers = []
            for customer in result.items:
                formatted_customer = customer.copy()
                # 使用transfunctions格式化显示字段
                if customer.get("phone"):
                    formatted_customer["formatted_phone"] = format_phone(
                        customer["phone"]
                    )
                if customer.get("credit_limit"):
                    formatted_customer["formatted_credit_limit"] = format_currency(
                        float(customer["credit_limit"])
                    )
                formatted_customers.append(formatted_customer)

        except Exception as e:
            error_msg = f"搜索客户失败: {e}"
            self._logger.exception(error_msg)
            service_error_msg = f"搜索客户失败: {e}"
            raise ServiceError(service_error_msg) from e
        else:
            return formatted_customers, result.total

    def get_all_customers(
        self, page: int = 1, page_size: int = 100
    ) -> list[dict[str, Any]]:
        """获取所有客户列表.

        Args:
            page: 页码, 默认第1页
            page_size: 每页大小, 默认100条

        Returns:
            List[Dict[str, Any]]: 客户列表

        Raises:
            ServiceError: 当获取失败时
        """
        try:
            customers, _ = self.search_customers(
                query="", filters=None, page=page, page_size=page_size
            )
        except Exception as e:
            error_msg = f"获取所有客户失败: {e}"
            self._logger.exception(error_msg)
            service_error_msg = f"获取所有客户失败: {e}"
            raise ServiceError(service_error_msg) from e
        else:
            return customers

    def get_total_count(self) -> int:
        """获取客户总数.

        用于仪表盘显示客户总数指标.

        Returns:
            int: 客户总数

        Raises:
            ServiceError: 当获取失败时
        """
        try:
            total_count = self._customer_dao.count()
            debug_msg = f"获取客户总数: {total_count}"
            self._logger.debug(debug_msg)
        except Exception as e:
            error_msg = f"获取客户总数失败: {e}"
            self._logger.exception(error_msg)
            service_error_msg = f"获取客户总数失败: {e}"
            raise ServiceError(service_error_msg) from e
        else:
            return total_count

    def get_advanced_search_filters(self) -> dict[str, Any]:
        """获取高级搜索筛选器配置.

        Returns:
            Dict[str, Any]: 筛选器配置
        """
        return {
            "customer_level": {
                "type": "select",
                "options": [
                    {"value": "vip", "label": "VIP客户"},
                    {"value": "important", "label": "重要客户"},
                    {"value": "normal", "label": "普通客户"},
                    {"value": "potential", "label": "潜在客户"},
                ],
            },
            "customer_type": {
                "type": "select",
                "options": [
                    {"value": "enterprise", "label": "企业客户"},
                    {"value": "individual", "label": "个人客户"},
                    {"value": "government", "label": "政府客户"},
                    {"value": "nonprofit", "label": "非营利组织"},
                ],
            },
            "created_date_range": {"type": "date_range", "label": "创建日期范围"},
            "credit_limit_range": {"type": "number_range", "label": "授信额度范围"},
            "has_recent_interaction": {"type": "boolean", "label": "最近有互动"},
        }
