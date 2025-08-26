"""
数据访问层接口定义

定义所有数据访问对象的接口契约,确保:
- 数据访问的标准化
- 数据层的松耦合
- 易于数据源切换
"""

from abc import ABC, abstractmethod
from typing import Any


class IBaseDAO(ABC):
    """基础数据访问对象接口"""

    @abstractmethod
    def insert(self, data: dict[str, Any]) -> int:
        """
        插入数据

        Args:
            data: 要插入的数据

        Returns:
            int: 新插入记录的ID

        Raises:
            DatabaseError: 数据库操作失败
        """
        pass

    @abstractmethod
    def get_by_id(self, record_id: int) -> dict[str, Any] | None:
        """
        根据ID获取记录

        Args:
            record_id: 记录ID

        Returns:
            Optional[Dict[str, Any]]: 记录数据,不存在时返回None
        """
        pass

    @abstractmethod
    def update(self, record_id: int, data: dict[str, Any]) -> bool:
        """
        更新记录

        Args:
            record_id: 记录ID
            data: 更新数据

        Returns:
            bool: 更新是否成功
        """
        pass

    @abstractmethod
    def delete(self, record_id: int) -> bool:
        """
        删除记录

        Args:
            record_id: 记录ID

        Returns:
            bool: 删除是否成功
        """
        pass

    @abstractmethod
    def search(
        self,
        conditions: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        搜索记录

        Args:
            conditions: 搜索条件
            order_by: 排序字段
            limit: 限制数量
            offset: 偏移量

        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        pass

    @abstractmethod
    def count(self, conditions: dict[str, Any] | None = None) -> int:
        """
        统计记录数量

        Args:
            conditions: 统计条件

        Returns:
            int: 记录数量
        """
        pass


class ICustomerDAO(IBaseDAO):
    """客户数据访问对象接口"""

    @abstractmethod
    def search_by_name_or_phone(self, query: str) -> list[dict[str, Any]]:
        """
        根据姓名或电话搜索客户

        Args:
            query: 搜索关键词

        Returns:
            List[Dict[str, Any]]: 匹配的客户列表
        """
        pass

    @abstractmethod
    def get_by_type(self, customer_type_id: int) -> list[dict[str, Any]]:
        """
        根据客户类型获取客户列表

        Args:
            customer_type_id: 客户类型ID

        Returns:
            List[Dict[str, Any]]: 客户列表
        """
        pass

    @abstractmethod
    def get_statistics(self) -> dict[str, Any]:
        """
        获取客户统计信息

        Returns:
            Dict[str, Any]: 统计数据
        """
        pass

    @abstractmethod
    def get_recent_interactions(
        self, customer_id: int, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        获取客户最近互动记录

        Args:
            customer_id: 客户ID
            limit: 限制数量

        Returns:
            List[Dict[str, Any]]: 互动记录列表
        """
        pass


class ISupplierDAO(IBaseDAO):
    """供应商数据访问对象接口"""

    @abstractmethod
    def search_by_name_or_contact(self, query: str) -> list[dict[str, Any]]:
        """
        根据名称或联系方式搜索供应商

        Args:
            query: 搜索关键词

        Returns:
            List[Dict[str, Any]]: 匹配的供应商列表
        """
        pass

    @abstractmethod
    def get_by_quality_rating(self, min_rating: float) -> list[dict[str, Any]]:
        """
        根据质量评级获取供应商列表

        Args:
            min_rating: 最低质量评级

        Returns:
            List[Dict[str, Any]]: 供应商列表
        """
        pass

    @abstractmethod
    def get_statistics(self) -> dict[str, Any]:
        """
        获取供应商统计信息

        Returns:
            Dict[str, Any]: 统计数据
        """
        pass

    @abstractmethod
    def get_quality_ratings(self, supplier_id: int) -> list[dict[str, Any]]:
        """
        获取供应商质量评级记录

        Args:
            supplier_id: 供应商ID

        Returns:
            List[Dict[str, Any]]: 质量评级记录列表
        """
        pass
