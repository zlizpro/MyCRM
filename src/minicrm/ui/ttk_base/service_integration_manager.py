"""TTK服务集成管理器

负责管理TTK界面与业务服务之间的集成,确保:
- 数据流的完整性和一致性
- 事件处理的标准化
- 错误处理的统一性
- 服务调用的可靠性

设计原则:
- 统一的服务集成接口
- 标准化的错误处理
- 事件驱动的数据更新
- 可测试的集成逻辑
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable

from minicrm.core.exceptions import MiniCRMError, ServiceError, ValidationError


if TYPE_CHECKING:
    from minicrm.core.interfaces.service_interfaces import (
        IContractService,
        ICustomerService,
        IFinanceService,
        ISupplierService,
        ITaskService,
    )


class ServiceIntegrationManager:
    """TTK服务集成管理器.

    提供统一的服务集成接口,确保TTK界面与业务服务的正确集成.
    """

    def __init__(self):
        """初始化服务集成管理器."""
        self._logger = logging.getLogger(__name__)
        self._event_handlers: dict[str, list[Callable]] = {}
        self._service_cache: dict[str, Any] = {}

    def register_event_handler(self, event_name: str, handler: Callable) -> None:
        """注册事件处理器.

        Args:
            event_name: 事件名称
            handler: 事件处理函数
        """
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)

    def emit_event(self, event_name: str, *args, **kwargs) -> None:
        """触发事件.

        Args:
            event_name: 事件名称
            *args: 位置参数
            **kwargs: 关键字参数
        """
        handlers = self._event_handlers.get(event_name, [])
        for handler in handlers:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                self._logger.exception(f"事件处理器执行失败: {event_name}, 错误: {e}")

    def safe_service_call(
        self,
        service_method: Callable,
        *args,
        error_message: str = "服务调用失败",
        default_return=None,
        **kwargs,
    ) -> Any:
        """安全的服务调用.

        Args:
            service_method: 服务方法
            *args: 位置参数
            error_message: 错误消息
            default_return: 默认返回值
            **kwargs: 关键字参数

        Returns:
            服务调用结果或默认值
        """
        try:
            return service_method(*args, **kwargs)
        except ValidationError as e:
            self._logger.warning(f"数据验证失败: {e}")
            raise
        except ServiceError as e:
            self._logger.error(f"业务逻辑错误: {e}")
            raise
        except Exception as e:
            self._logger.exception(f"{error_message}: {e}")
            if default_return is not None:
                return default_return
            raise MiniCRMError(f"{error_message}: {e}") from e

    def validate_service_data(
        self, data: dict[str, Any], required_fields: list[str]
    ) -> None:
        """验证服务数据.

        Args:
            data: 数据字典
            required_fields: 必填字段列表

        Raises:
            ValidationError: 数据验证失败
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)

        if missing_fields:
            error_msg = f"缺少必填字段: {', '.join(missing_fields)}"
            raise ValidationError(error_msg)

    def format_service_error(self, error: Exception, operation: str) -> str:
        """格式化服务错误消息.

        Args:
            error: 异常对象
            operation: 操作描述

        Returns:
            格式化的错误消息
        """
        if isinstance(error, ValidationError):
            return f"{operation}失败: 数据验证错误 - {error}"
        if isinstance(error, ServiceError):
            return f"{operation}失败: 业务逻辑错误 - {error}"
        return f"{operation}失败: 系统错误 - {error}"


class CustomerServiceIntegration:
    """客户服务集成器."""

    def __init__(
        self,
        customer_service: ICustomerService,
        integration_manager: ServiceIntegrationManager,
    ):
        """初始化客户服务集成器.

        Args:
            customer_service: 客户服务实例
            integration_manager: 集成管理器
        """
        self._service = customer_service
        self._manager = integration_manager
        self._logger = logging.getLogger(__name__)

    def create_customer(self, customer_data: dict[str, Any]) -> int:
        """创建客户.

        Args:
            customer_data: 客户数据

        Returns:
            客户ID
        """
        # 验证必填字段
        required_fields = ["name", "phone"]
        self._manager.validate_service_data(customer_data, required_fields)

        # 调用服务
        customer_id = self._manager.safe_service_call(
            self._service.create_customer,
            customer_data,
            error_message="创建客户失败",
        )

        # 触发事件
        self._manager.emit_event("customer_created", customer_id, customer_data)

        return customer_id

    def update_customer(self, customer_id: int, customer_data: dict[str, Any]) -> bool:
        """更新客户.

        Args:
            customer_id: 客户ID
            customer_data: 客户数据

        Returns:
            是否成功
        """
        success = self._manager.safe_service_call(
            self._service.update_customer,
            customer_id,
            customer_data,
            error_message="更新客户失败",
            default_return=False,
        )

        if success:
            self._manager.emit_event("customer_updated", customer_id, customer_data)

        return success

    def delete_customer(self, customer_id: int) -> bool:
        """删除客户.

        Args:
            customer_id: 客户ID

        Returns:
            是否成功
        """
        success = self._manager.safe_service_call(
            self._service.delete_customer,
            customer_id,
            error_message="删除客户失败",
            default_return=False,
        )

        if success:
            self._manager.emit_event("customer_deleted", customer_id)

        return success

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
            (客户列表, 总数)
        """
        return self._manager.safe_service_call(
            self._service.search_customers,
            query,
            filters,
            page,
            page_size,
            error_message="搜索客户失败",
            default_return=([], 0),
        )

    def get_customer(self, customer_id: int) -> dict[str, Any] | None:
        """获取客户信息.

        Args:
            customer_id: 客户ID

        Returns:
            客户信息
        """
        return self._manager.safe_service_call(
            self._service.get_customer,
            customer_id,
            error_message="获取客户信息失败",
            default_return=None,
        )


class SupplierServiceIntegration:
    """供应商服务集成器."""

    def __init__(
        self,
        supplier_service: ISupplierService,
        integration_manager: ServiceIntegrationManager,
    ):
        """初始化供应商服务集成器.

        Args:
            supplier_service: 供应商服务实例
            integration_manager: 集成管理器
        """
        self._service = supplier_service
        self._manager = integration_manager
        self._logger = logging.getLogger(__name__)

    def create_supplier(self, supplier_data: dict[str, Any]) -> int:
        """创建供应商.

        Args:
            supplier_data: 供应商数据

        Returns:
            供应商ID
        """
        # 验证必填字段
        required_fields = ["name", "contact_person", "phone"]
        self._manager.validate_service_data(supplier_data, required_fields)

        # 调用服务
        supplier_id = self._manager.safe_service_call(
            self._service.create_supplier,
            supplier_data,
            error_message="创建供应商失败",
        )

        # 触发事件
        self._manager.emit_event("supplier_created", supplier_id, supplier_data)

        return supplier_id

    def update_supplier(self, supplier_id: int, supplier_data: dict[str, Any]) -> bool:
        """更新供应商.

        Args:
            supplier_id: 供应商ID
            supplier_data: 供应商数据

        Returns:
            是否成功
        """
        success = self._manager.safe_service_call(
            self._service.update_supplier,
            supplier_id,
            supplier_data,
            error_message="更新供应商失败",
            default_return=False,
        )

        if success:
            self._manager.emit_event("supplier_updated", supplier_id, supplier_data)

        return success

    def delete_supplier(self, supplier_id: int) -> bool:
        """删除供应商.

        Args:
            supplier_id: 供应商ID

        Returns:
            是否成功
        """
        success = self._manager.safe_service_call(
            self._service.delete_supplier,
            supplier_id,
            error_message="删除供应商失败",
            default_return=False,
        )

        if success:
            self._manager.emit_event("supplier_deleted", supplier_id)

        return success

    def search_suppliers(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """搜索供应商.

        Args:
            query: 搜索关键词
            filters: 筛选条件
            page: 页码
            page_size: 每页大小

        Returns:
            (供应商列表, 总数)
        """
        return self._manager.safe_service_call(
            self._service.search_suppliers,
            query,
            filters,
            page,
            page_size,
            error_message="搜索供应商失败",
            default_return=([], 0),
        )


class FinanceServiceIntegration:
    """财务服务集成器."""

    def __init__(
        self,
        finance_service: IFinanceService,
        integration_manager: ServiceIntegrationManager,
    ):
        """初始化财务服务集成器.

        Args:
            finance_service: 财务服务实例
            integration_manager: 集成管理器
        """
        self._service = finance_service
        self._manager = integration_manager
        self._logger = logging.getLogger(__name__)

    def get_receivables_summary(self) -> dict[str, Any]:
        """获取应收账款汇总."""
        return self._manager.safe_service_call(
            self._service.get_receivables_summary,
            error_message="获取应收账款汇总失败",
            default_return={},
        )

    def get_payables_summary(self) -> dict[str, Any]:
        """获取应付账款汇总."""
        return self._manager.safe_service_call(
            self._service.get_payables_summary,
            error_message="获取应付账款汇总失败",
            default_return={},
        )

    def record_payment(self, payment_data: dict[str, Any]) -> int:
        """记录收付款.

        Args:
            payment_data: 收付款数据

        Returns:
            记录ID
        """
        # 验证必填字段
        required_fields = ["amount", "payment_type", "payment_date"]
        self._manager.validate_service_data(payment_data, required_fields)

        # 调用服务
        payment_id = self._manager.safe_service_call(
            self._service.record_payment,
            payment_data,
            error_message="记录收付款失败",
        )

        # 触发事件
        self._manager.emit_event("payment_recorded", payment_id, payment_data)

        return payment_id

    def get_financial_statistics(self) -> dict[str, Any]:
        """获取财务统计信息."""
        return self._manager.safe_service_call(
            self._service.get_financial_statistics,
            error_message="获取财务统计信息失败",
            default_return={},
        )


class TaskServiceIntegration:
    """任务服务集成器."""

    def __init__(
        self,
        task_service: ITaskService,
        integration_manager: ServiceIntegrationManager,
    ):
        """初始化任务服务集成器.

        Args:
            task_service: 任务服务实例
            integration_manager: 集成管理器
        """
        self._service = task_service
        self._manager = integration_manager
        self._logger = logging.getLogger(__name__)

    def create_task(self, task_data: dict[str, Any]) -> int:
        """创建任务.

        Args:
            task_data: 任务数据

        Returns:
            任务ID
        """
        # 验证必填字段
        required_fields = ["title", "description", "due_date"]
        self._manager.validate_service_data(task_data, required_fields)

        # 调用服务
        task_id = self._manager.safe_service_call(
            self._service.create_task,
            task_data,
            error_message="创建任务失败",
        )

        # 触发事件
        self._manager.emit_event("task_created", task_id, task_data)

        return task_id

    def update_task(self, task_id: int, task_data: dict[str, Any]) -> bool:
        """更新任务.

        Args:
            task_id: 任务ID
            task_data: 任务数据

        Returns:
            是否成功
        """
        success = self._manager.safe_service_call(
            self._service.update_task,
            task_id,
            task_data,
            error_message="更新任务失败",
            default_return=False,
        )

        if success:
            self._manager.emit_event("task_updated", task_id, task_data)

        return success

    def mark_task_completed(self, task_id: int) -> bool:
        """标记任务为已完成.

        Args:
            task_id: 任务ID

        Returns:
            是否成功
        """
        success = self._manager.safe_service_call(
            self._service.mark_task_completed,
            task_id,
            error_message="标记任务完成失败",
            default_return=False,
        )

        if success:
            self._manager.emit_event("task_completed", task_id)

        return success

    def search_tasks(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """搜索任务.

        Args:
            query: 搜索关键词
            filters: 筛选条件
            page: 页码
            page_size: 每页大小

        Returns:
            (任务列表, 总数)
        """
        return self._manager.safe_service_call(
            self._service.search_tasks,
            query,
            filters,
            page,
            page_size,
            error_message="搜索任务失败",
            default_return=([], 0),
        )

    def get_pending_tasks(self, limit: int = 10) -> list[dict[str, Any]]:
        """获取待办任务.

        Args:
            limit: 限制数量

        Returns:
            待办任务列表
        """
        return self._manager.safe_service_call(
            self._service.get_pending_tasks,
            limit,
            error_message="获取待办任务失败",
            default_return=[],
        )


class ContractServiceIntegration:
    """合同服务集成器."""

    def __init__(
        self,
        contract_service: IContractService,
        integration_manager: ServiceIntegrationManager,
    ):
        """初始化合同服务集成器.

        Args:
            contract_service: 合同服务实例
            integration_manager: 集成管理器
        """
        self._service = contract_service
        self._manager = integration_manager
        self._logger = logging.getLogger(__name__)

    def create_contract(self, contract_data: dict[str, Any]) -> int:
        """创建合同.

        Args:
            contract_data: 合同数据

        Returns:
            合同ID
        """
        # 验证必填字段
        required_fields = ["title", "customer_id", "contract_amount"]
        self._manager.validate_service_data(contract_data, required_fields)

        # 调用服务
        contract_id = self._manager.safe_service_call(
            self._service.create_contract,
            contract_data,
            error_message="创建合同失败",
        )

        # 触发事件
        self._manager.emit_event("contract_created", contract_id, contract_data)

        return contract_id

    def update_contract(self, contract_id: int, contract_data: dict[str, Any]) -> bool:
        """更新合同.

        Args:
            contract_id: 合同ID
            contract_data: 合同数据

        Returns:
            是否成功
        """
        success = self._manager.safe_service_call(
            self._service.update_contract,
            contract_id,
            contract_data,
            error_message="更新合同失败",
            default_return=False,
        )

        if success:
            self._manager.emit_event("contract_updated", contract_id, contract_data)

        return success

    def search_contracts(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """搜索合同.

        Args:
            query: 搜索关键词
            filters: 筛选条件
            page: 页码
            page_size: 每页大小

        Returns:
            (合同列表, 总数)
        """
        return self._manager.safe_service_call(
            self._service.search_contracts,
            query,
            filters,
            page,
            page_size,
            error_message="搜索合同失败",
            default_return=([], 0),
        )


# 全局服务集成管理器实例
_global_integration_manager: ServiceIntegrationManager | None = None


def get_global_integration_manager() -> ServiceIntegrationManager:
    """获取全局服务集成管理器实例."""
    global _global_integration_manager
    if _global_integration_manager is None:
        _global_integration_manager = ServiceIntegrationManager()
    return _global_integration_manager


def create_service_integrations(
    customer_service: ICustomerService,
    supplier_service: ISupplierService,
    finance_service: IFinanceService,
    task_service: ITaskService,
    contract_service: IContractService,
) -> dict[str, Any]:
    """创建所有服务集成器.

    Args:
        customer_service: 客户服务
        supplier_service: 供应商服务
        finance_service: 财务服务
        task_service: 任务服务
        contract_service: 合同服务

    Returns:
        服务集成器字典
    """
    manager = get_global_integration_manager()

    return {
        "customer": CustomerServiceIntegration(customer_service, manager),
        "supplier": SupplierServiceIntegration(supplier_service, manager),
        "finance": FinanceServiceIntegration(finance_service, manager),
        "task": TaskServiceIntegration(task_service, manager),
        "contract": ContractServiceIntegration(contract_service, manager),
        "manager": manager,
    }
