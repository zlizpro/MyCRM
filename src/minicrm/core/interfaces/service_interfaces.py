"""
业务服务层接口定义

定义所有业务服务的接口契约,确保:
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
            Optional[Dict[str, Any]]: 客户信息,不存在时返回None
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


class IBackupService(ABC):
    """备份管理服务接口"""

    @abstractmethod
    def create_backup(self, backup_type: str = "full") -> dict[str, Any]:
        """创建备份"""
        pass

    @abstractmethod
    def restore_backup(self, backup_path: str) -> bool:
        """恢复备份"""
        pass

    @abstractmethod
    def list_backups(self) -> list[dict[str, Any]]:
        """列出所有备份"""
        pass

    @abstractmethod
    def delete_backup(self, backup_id: str) -> bool:
        """删除备份"""
        pass


class IContractService(ABC):
    """合同管理服务接口"""

    @abstractmethod
    def create_contract(self, contract_data: dict[str, Any]) -> int:
        """创建合同"""
        pass

    @abstractmethod
    def get_contract(self, contract_id: int) -> dict[str, Any] | None:
        """获取合同信息"""
        pass

    @abstractmethod
    def update_contract(self, contract_id: int, data: dict[str, Any]) -> bool:
        """更新合同信息"""
        pass

    @abstractmethod
    def delete_contract(self, contract_id: int) -> bool:
        """删除合同"""
        pass

    @abstractmethod
    def search_contracts(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """搜索合同"""
        pass


class IQuoteService(ABC):
    """报价管理服务接口"""

    @abstractmethod
    def create_quote(self, quote_data: dict[str, Any]) -> int:
        """创建报价"""
        pass

    @abstractmethod
    def get_quote(self, quote_id: int) -> dict[str, Any] | None:
        """获取报价信息"""
        pass

    @abstractmethod
    def update_quote(self, quote_id: int, data: dict[str, Any]) -> bool:
        """更新报价信息"""
        pass

    @abstractmethod
    def delete_quote(self, quote_id: int) -> bool:
        """删除报价"""
        pass

    @abstractmethod
    def search_quotes(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """搜索报价"""
        pass


class IImportExportService(ABC):
    """数据导入导出服务接口"""

    @abstractmethod
    def import_data(
        self, file_path: str, data_type: str, options: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """导入数据"""
        pass

    @abstractmethod
    def export_data(
        self,
        data_type: str,
        filters: dict[str, Any] | None = None,
        format: str = "excel",
    ) -> str:
        """导出数据"""
        pass

    @abstractmethod
    def get_import_templates(self) -> list[dict[str, Any]]:
        """获取导入模板"""
        pass

    @abstractmethod
    def validate_import_file(self, file_path: str, data_type: str) -> dict[str, Any]:
        """验证导入文件"""
        pass


class ISettingsService(ABC):
    """设置管理服务接口"""

    @abstractmethod
    def get_setting(self, category: str, key: str | None = None) -> Any:
        """获取设置值"""
        pass

    @abstractmethod
    def set_setting(self, category: str, key: str, value: Any) -> None:
        """设置值"""
        pass

    @abstractmethod
    def update_settings(self, category: str, settings: dict[str, Any]) -> None:
        """批量更新设置"""
        pass

    @abstractmethod
    def reset_settings(self, category: str | None = None) -> None:
        """重置设置到默认值"""
        pass

    @abstractmethod
    def get_all_settings(self) -> dict[str, Any]:
        """获取所有设置"""
        pass

    @abstractmethod
    def export_settings(self, file_path: str) -> None:
        """导出设置到文件"""
        pass

    @abstractmethod
    def import_settings(self, file_path: str, merge: bool = True) -> None:
        """从文件导入设置"""
        pass


class ITaskService(ABC):
    """任务管理服务接口"""

    @abstractmethod
    def create_task(self, task_data: dict[str, Any]) -> int:
        """创建任务"""
        pass

    @abstractmethod
    def get_task(self, task_id: int) -> dict[str, Any] | None:
        """获取任务信息"""
        pass

    @abstractmethod
    def update_task(self, task_id: int, data: dict[str, Any]) -> bool:
        """更新任务信息"""
        pass

    @abstractmethod
    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        pass

    @abstractmethod
    def search_tasks(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """搜索任务"""
        pass

    @abstractmethod
    def get_pending_tasks(self, limit: int = 10) -> list[dict[str, Any]]:
        """获取待办任务"""
        pass

    @abstractmethod
    def mark_task_completed(self, task_id: int) -> bool:
        """标记任务为已完成"""
        pass
