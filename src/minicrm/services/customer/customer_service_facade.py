"""MiniCRM 客户服务门面.

提供统一的客户服务接口,整合所有客户相关的业务逻辑:
- 客户核心CRUD操作
- 客户搜索和筛选
- 客户价值评分和统计
- 业务逻辑Hooks和审计日志

这是客户服务的统一入口点,保持向后兼容性.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any

from minicrm.core.exceptions import ServiceError
from minicrm.data.dao.customer_dao import CustomerDAO
from minicrm.services.customer.customer_core_service import CustomerCoreService
from minicrm.services.customer.customer_search_service import CustomerSearchService
from minicrm.services.customer.customer_value_service import CustomerValueService


class CustomerServiceFacade:
    """客户服务门面实现.

    整合所有客户相关的业务逻辑服务:
    - 客户核心CRUD操作
    - 客户搜索和筛选
    - 客户价值评分和统计
    - 业务逻辑Hooks和审计日志

    提供统一的接口,保持向后兼容性.
    """

    def __init__(self, customer_dao: CustomerDAO):
        """初始化客户服务门面.

        Args:
            customer_dao: 客户数据访问对象
        """
        self._customer_dao = customer_dao
        self._logger = logging.getLogger(__name__)

        # 初始化各个子服务
        self._core_service = CustomerCoreService(customer_dao)
        self._search_service = CustomerSearchService(customer_dao)
        self._value_service = CustomerValueService(customer_dao)

        self._logger.info("客户服务门面初始化完成")

    # ========== 核心CRUD操作 ==========

    def create_customer(self, customer_data: dict[str, Any]) -> int:
        """创建新客户.

        Args:
            customer_data: 客户数据字典,包含姓名、电话等信息

        Returns:
            int: 新创建的客户ID
        """
        try:
            # 审计日志 - 记录创建操作开始
            self._log_audit_operation(
                "创建客户开始",
                {
                    "customer_name": customer_data.get("name", ""),
                    "operation_type": "create",
                },
            )

            # 调用核心服务创建客户
            customer_id = self._core_service.create_customer(customer_data)

            # 执行创建后的业务逻辑Hooks
            self._execute_post_create_hooks(customer_id, customer_data)

            # 审计日志 - 记录创建操作成功
            self._log_audit_operation(
                "创建客户成功",
                {
                    "customer_id": customer_id,
                    "customer_name": customer_data.get("name", ""),
                    "operation_type": "create",
                },
            )

            return customer_id

        except Exception as e:
            # 审计日志 - 记录创建操作失败
            self._log_audit_operation(
                "创建客户失败",
                {
                    "customer_name": customer_data.get("name", ""),
                    "operation_type": "create",
                    "error": str(e),
                },
            )
            raise

    def update_customer(self, customer_id: int, data: dict[str, Any]) -> bool:
        """更新客户信息.

        Args:
            customer_id: 客户ID
            data: 更新数据

        Returns:
            bool: 更新是否成功
        """
        return self._core_service.update_customer(customer_id, data)

    def delete_customer(self, customer_id: int) -> bool:
        """删除客户.

        Args:
            customer_id: 客户ID

        Returns:
            bool: 删除是否成功
        """
        return self._core_service.delete_customer(customer_id)

    def get_customer_by_id(self, customer_id: int) -> dict[str, Any] | None:
        """根据ID获取客户信息.

        Args:
            customer_id: 客户ID

        Returns:
            Dict[str, Any] | None: 客户信息,不存在时返回None
        """
        return self._core_service.get_customer_by_id(customer_id)

    # ========== 搜索和查询操作 ==========

    def search_customers(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """搜索客户.

        Args:
            query: 搜索关键词
            filters: 筛选条件
            page: 页码
            page_size: 每页大小

        Returns:
            Tuple[List[Dict[str, Any]], int]: (客户列表, 总数)
        """
        return self._search_service.search_customers(query, filters, page, page_size)

    def get_all_customers(
        self, page: int = 1, page_size: int = 100
    ) -> list[dict[str, Any]]:
        """获取所有客户列表.

        Args:
            page: 页码,默认第1页
            page_size: 每页大小,默认100条

        Returns:
            List[Dict[str, Any]]: 客户列表
        """
        return self._search_service.get_all_customers(page, page_size)

    def get_total_count(self) -> int:
        """获取客户总数.

        Returns:
            int: 客户总数
        """
        return self._search_service.get_total_count()

    def get_advanced_search_filters(self) -> dict[str, Any]:
        """获取高级搜索筛选器配置.

        Returns:
            Dict[str, Any]: 筛选器配置
        """
        return self._search_service.get_advanced_search_filters()

    # ========== 价值评分和统计操作 ==========

    def calculate_customer_value_score(self, customer_id: int) -> dict[str, Any]:
        """计算客户价值评分.

        Args:
            customer_id: 客户ID

        Returns:
            Dict[str, Any]: 包含详细评分指标的字典
        """
        return self._value_service.calculate_customer_value_score(customer_id)

    def get_customer_statistics(self) -> dict[str, Any]:
        """获取客户统计信息.

        Returns:
            Dict[str, Any]: 客户统计数据
        """
        try:
            # 审计日志 - 记录统计查询操作
            self._log_audit_operation(
                "获取客户统计", {"operation_type": "statistics_query"}
            )

            # 获取统计数据
            statistics = self._value_service.get_customer_statistics()

            # 业务逻辑Hook - 统计生成后处理
            self._execute_post_statistics_hooks(statistics)

            return statistics

        except Exception as e:
            error_msg = f"获取客户统计失败: {e}"
            self._logger.exception(error_msg)
            service_error_msg = f"获取客户统计失败: {e}"
            raise ServiceError(service_error_msg) from e

    # ========== 业务逻辑Hooks和审计 ==========

    def _log_audit_operation(self, operation: str, details: dict[str, Any]) -> None:
        """记录审计日志.

        Args:
            operation: 操作名称
            details: 操作详情
        """
        audit_log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "CustomerServiceFacade",
            "operation": operation,
            "details": details,
            "user": details.get("user_id", "system"),  # 实际应该从上下文获取
        }

        # 记录到审计日志
        audit_msg = f"AUDIT: {audit_log}"
        self._logger.info(audit_msg)

    def _execute_post_create_hooks(
        self, customer_id: int, customer_data: dict[str, Any]
    ) -> None:
        """执行创建后的业务逻辑Hooks.

        Args:
            customer_id: 客户ID
            customer_data: 客户数据
        """
        try:
            # Hook 1: 创建默认互动记录
            self._create_default_interaction(customer_id)

            # Hook 2: 发送欢迎通知
            self._send_welcome_notification(customer_id, customer_data)

            # Hook 3: 更新统计缓存
            self._update_statistics_cache()

        except Exception as e:
            warning_msg = f"创建后Hook执行失败: {e}"
            self._logger.warning(warning_msg)
            # 创建后Hook失败不应该影响主流程

    def _execute_post_statistics_hooks(self, statistics: dict[str, Any]) -> None:
        """执行统计生成后的业务逻辑Hooks.

        Args:
            statistics: 统计数据
        """
        try:
            # Hook 1: 缓存统计数据
            self._cache_statistics(statistics)

            # Hook 2: 检查异常指标
            self._check_abnormal_metrics(statistics)

        except Exception as e:
            warning_msg = f"统计后Hook执行失败: {e}"
            self._logger.warning(warning_msg)

    def _create_default_interaction(self, customer_id: int) -> None:
        """创建默认互动记录."""
        try:
            # 这里应该调用InteractionService创建欢迎互动记录
            # 简化实现,只记录日志
            info_msg = f"为客户 {customer_id} 创建默认互动记录"
            self._logger.info(info_msg)
        except Exception as e:
            warning_msg = f"创建默认互动记录失败: {e}"
            self._logger.warning(warning_msg)

    def _send_welcome_notification(
        self, customer_id: int, customer_data: dict[str, Any]
    ) -> None:
        """发送欢迎通知."""
        try:
            # 这里应该集成通知系统
            # 简化实现,只记录日志
            customer_name = customer_data.get("name", "新客户")
            info_msg = f"为客户 {customer_name}({customer_id}) 发送欢迎通知"
            self._logger.info(info_msg)
        except Exception as e:
            warning_msg = f"发送欢迎通知失败: {e}"
            self._logger.warning(warning_msg)

    def _update_statistics_cache(self) -> None:
        """更新统计缓存."""
        try:
            # 清除统计相关缓存
            # 实际实现应该更新Redis或内存缓存
            self._logger.debug("统计缓存已更新")
        except Exception as e:
            warning_msg = f"更新统计缓存失败: {e}"
            self._logger.warning(warning_msg)

    def _cache_statistics(self, statistics: dict[str, Any]) -> None:
        """缓存统计数据."""
        try:
            # 实际实现应该将统计数据缓存到Redis
            cache_key = (
                f"customer_statistics_{datetime.now(timezone.utc).strftime('%Y%m%d')}"
            )
            debug_msg = f"统计数据已缓存: {cache_key}"
            self._logger.debug(debug_msg)
        except Exception as e:
            warning_msg = f"缓存统计数据失败: {e}"
            self._logger.warning(warning_msg)

    def _check_abnormal_metrics(self, statistics: dict[str, Any]) -> None:
        """检查异常指标."""
        try:
            total_customers = statistics.get("total_customers", 0)

            # 检查客户数量异常
            if total_customers == 0:
                self._logger.warning("客户数量为0,可能存在数据问题")
            elif total_customers > 10000:
                info_msg = f"客户数量达到 {total_customers},建议考虑数据分片"
                self._logger.info(info_msg)

        except Exception as e:
            warning_msg = f"检查异常指标失败: {e}"
            self._logger.warning(warning_msg)


# 为了保持向后兼容性,提供别名
CustomerService = CustomerServiceFacade
