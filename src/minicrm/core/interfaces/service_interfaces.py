"""
业务服务层接口定义

定义所有业务服务的接口契约，确保：
- 业务逻辑的标准化
- 服务间的松耦合
- 易于单元测试
"""

from abc import ABC, abstractmethod
from typing import Any


class ICustomerService(ABC):
    """客户管理服务接口"""

    @abstractmethod
    def create_customer(self, customer_data: dict[str, Any]) -> int:
        """
        创建新客户

        Args:
            customer_data: 客户数据字典

        Returns:
            int: 新创建的客户ID

        Raises:
            ValidationError: 数据验证失败
            ServiceError: 业务逻辑错误
        """
        pass

    @abstractmethod
    def get_customer(self, customer_id: int) -> dict[str, Any] | None:
        """
        获取客户信息

        Args:
            customer_id: 客户ID

        Returns:
            Optional[Dict[str, Any]]: 客户信息，不存在时返回None
        """
        pass

    @abstractmethod
    def update_customer(self, customer_id: int, data: dict[str, Any]) -> bool:
        """
        更新客户信息

        Args:
            customer_id: 客户ID
            data: 更新数据

        Returns:
            bool: 更新是否成功
        """
        pass

    @abstractmethod
    def delete_customer(self, customer_id: int) -> bool:
        """
        删除客户

        Args:
            customer_id: 客户ID

        Returns:
            bool: 删除是否成功
        """
        pass

    @abstractmethod
    def search_customers(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        搜索客户

        Args:
            query: 搜索关键词
            filters: 筛选条件
            page: 页码
            page_size: 每页大小

        Returns:
            Tuple[List[Dict[str, Any]], int]: (客户列表, 总数)
        """
        pass

    @abstractmethod
    def get_customer_statistics(self) -> dict[str, Any]:
        """
        获取客户统计信息

        Returns:
            Dict[str, Any]: 统计数据
        """
        pass


class ISupplierService(ABC):
    """供应商管理服务接口"""

    @abstractmethod
    def create_supplier(self, supplier_data: dict[str, Any]) -> int:
        """创建新供应商"""
        pass

    @abstractmethod
    def get_supplier(self, supplier_id: int) -> dict[str, Any] | None:
        """获取供应商信息"""
        pass

    @abstractmethod
    def update_supplier(self, supplier_id: int, data: dict[str, Any]) -> bool:
        """更新供应商信息"""
        pass

    @abstractmethod
    def delete_supplier(self, supplier_id: int) -> bool:
        """删除供应商"""
        pass

    @abstractmethod
    def search_suppliers(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """搜索供应商"""
        pass

    @abstractmethod
    def get_supplier_statistics(self) -> dict[str, Any]:
        """获取供应商统计信息"""
        pass


class IFinanceService(ABC):
    """财务管理服务接口"""

    @abstractmethod
    def get_receivables_summary(self) -> dict[str, Any]:
        """获取应收账款汇总"""
        pass

    @abstractmethod
    def get_payables_summary(self) -> dict[str, Any]:
        """获取应付账款汇总"""
        pass

    @abstractmethod
    def record_payment(self, payment_data: dict[str, Any]) -> int:
        """记录收付款"""
        pass

    @abstractmethod
    def get_financial_statistics(self) -> dict[str, Any]:
        """获取财务统计信息"""
        pass


class IAnalyticsService(ABC):
    """数据分析服务接口"""

    @abstractmethod
    def get_dashboard_data(self) -> dict[str, Any]:
        """获取仪表盘数据"""
        pass

    @abstractmethod
    def generate_customer_report(
        self, start_date: str, end_date: str
    ) -> dict[str, Any]:
        """生成客户报表"""
        pass

    @abstractmethod
    def generate_supplier_report(
        self, start_date: str, end_date: str
    ) -> dict[str, Any]:
        """生成供应商报表"""
        pass

    @abstractmethod
    def get_trend_analysis(self, metric: str, period: str) -> dict[str, Any]:
        """获取趋势分析"""
        pass
