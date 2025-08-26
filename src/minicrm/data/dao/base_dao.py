"""
基础数据访问对象实现

提供通用的数据访问功能,其他DAO可以继承使用.
集成transfunctions中的CRUD模板,确保代码复用和一致性.
"""

import logging
from typing import Any

from minicrm.core.interfaces.dao_interfaces import IBaseDAO
from minicrm.data.database import DatabaseManager
from transfunctions.data_operations import create_crud_template


class BaseDAO(IBaseDAO):
    """
    基础数据访问对象

    提供通用的CRUD操作实现,集成transfunctions的CRUD模板
    """

    def __init__(self, database_manager: DatabaseManager, table_name: str):
        """
        初始化基础DAO

        Args:
            database_manager: 数据库管理器
            table_name: 表名
        """
        self._db = database_manager
        self._table_name = table_name
        self._logger = logging.getLogger(__name__)

        # 创建CRUD模板实例
        self._crud_template = create_crud_template(
            table_name, database_manager, self._logger
        )

    def insert(self, data: dict[str, Any]) -> int:
        """
        插入数据

        Args:
            data: 要插入的数据

        Returns:
            int: 新插入记录的ID
        """
        return self._crud_template.create(data)

    def get_by_id(self, record_id: int) -> dict[str, Any] | None:
        """
        根据ID获取记录

        Args:
            record_id: 记录ID

        Returns:
            Optional[Dict[str, Any]]: 记录数据
        """
        return self._crud_template.read(record_id)

    def update(self, record_id: int, data: dict[str, Any]) -> bool:
        """
        更新记录

        Args:
            record_id: 记录ID
            data: 更新数据

        Returns:
            bool: 更新是否成功
        """
        return self._crud_template.update(record_id, data)

    def delete(self, record_id: int) -> bool:
        """
        删除记录

        Args:
            record_id: 记录ID

        Returns:
            bool: 删除是否成功
        """
        return self._crud_template.delete(record_id)

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
        return self._crud_template.search(conditions, order_by, limit, offset)

    def count(self, conditions: dict[str, Any] | None = None) -> int:
        """
        统计记录数量

        Args:
            conditions: 统计条件

        Returns:
            int: 记录数量
        """
        return self._crud_template.count(conditions)

    def list_all(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """
        获取所有记录

        Args:
            filters: 过滤条件

        Returns:
            List[Dict[str, Any]]: 所有记录列表
        """
        return self.search(filters)

    def _row_to_dict(self, row) -> dict[str, Any]:
        """
        将数据库行转换为字典

        Args:
            row: 数据库行

        Returns:
            Dict[str, Any]: 字典格式的数据
        """
        if hasattr(row, "keys"):
            return dict(row)
        else:
            # 子类需要重写此方法来提供正确的字段映射
            raise NotImplementedError("子类必须实现_row_to_dict方法")
