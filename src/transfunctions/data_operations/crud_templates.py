"""
Transfunctions - CRUD操作模板

提供标准化的CRUD操作模板，确保数据访问的一致性和可复用性。
这些模板可以被各种DAO类使用，减少重复代码。
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from minicrm.core.exceptions import DatabaseError, ValidationError


class CRUDTemplate(ABC):
    """
    CRUD操作模板基类

    定义标准的CRUD操作接口，子类需要实现具体的数据库操作逻辑。
    """

    def __init__(
        self, table_name: str, db_manager, logger: logging.Logger | None = None
    ):
        """
        初始化CRUD模板

        Args:
            table_name: 数据表名
            db_manager: 数据库管理器
            logger: 日志记录器
        """
        self.table_name = table_name
        self.db_manager = db_manager
        self.logger = logger or logging.getLogger(__name__)

    def create(
        self, data: dict[str, Any], validate_func: Callable | None = None
    ) -> int:
        """
        创建记录模板

        Args:
            data: 要创建的数据
            validate_func: 数据验证函数

        Returns:
            int: 新创建记录的ID

        Raises:
            ValidationError: 数据验证失败
            DatabaseError: 数据库操作失败
        """
        try:
            # 数据验证
            if validate_func:
                validated_data = validate_func(data)
                if not validated_data:
                    raise ValidationError("数据验证失败")
                data = validated_data

            # 构建插入SQL
            columns = list(data.keys())
            placeholders = ", ".join(["?" for _ in columns])
            sql = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders})"

            # 执行插入
            params = list(data.values())
            record_id = self.db_manager.execute_insert(sql, tuple(params))

            self.logger.info(f"成功创建{self.table_name}记录，ID: {record_id}")
            return record_id

        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"创建{self.table_name}记录失败: {e}")
            raise DatabaseError(f"创建{self.table_name}记录失败: {e}") from e

    def read(self, record_id: int) -> dict[str, Any] | None:
        """
        读取记录模板

        Args:
            record_id: 记录ID

        Returns:
            Optional[Dict[str, Any]]: 记录数据，不存在时返回None
        """
        try:
            sql = f"SELECT * FROM {self.table_name} WHERE id = ?"
            result = self.db_manager.execute_query(sql, (record_id,))

            if result:
                return self._row_to_dict(result[0])
            return None

        except Exception as e:
            self.logger.error(f"读取{self.table_name}记录失败: {e}")
            raise DatabaseError(f"读取{self.table_name}记录失败: {e}") from e

    def update(
        self,
        record_id: int,
        data: dict[str, Any],
        validate_func: Callable | None = None,
    ) -> bool:
        """
        更新记录模板

        Args:
            record_id: 记录ID
            data: 更新数据
            validate_func: 数据验证函数

        Returns:
            bool: 更新是否成功
        """
        try:
            # 数据验证
            if validate_func:
                validated_data = validate_func(data)
                if not validated_data:
                    raise ValidationError("数据验证失败")
                data = validated_data

            # 构建更新SQL
            set_clauses = []
            params = []

            for key, value in data.items():
                if key != "id":  # 不更新ID字段
                    set_clauses.append(f"{key} = ?")
                    params.append(value)

            if not set_clauses:
                return False

            sql = f"UPDATE {self.table_name} SET {', '.join(set_clauses)} WHERE id = ?"
            params.append(record_id)

            # 执行更新
            rows_affected = self.db_manager.execute_update(sql, tuple(params))
            success = rows_affected > 0

            if success:
                self.logger.info(f"成功更新{self.table_name}记录，ID: {record_id}")

            return success

        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"更新{self.table_name}记录失败: {e}")
            raise DatabaseError(f"更新{self.table_name}记录失败: {e}") from e

    def delete(self, record_id: int) -> bool:
        """
        删除记录模板

        Args:
            record_id: 记录ID

        Returns:
            bool: 删除是否成功
        """
        try:
            sql = f"DELETE FROM {self.table_name} WHERE id = ?"
            rows_affected = self.db_manager.execute_delete(sql, (record_id,))
            success = rows_affected > 0

            if success:
                self.logger.info(f"成功删除{self.table_name}记录，ID: {record_id}")

            return success

        except Exception as e:
            self.logger.error(f"删除{self.table_name}记录失败: {e}")
            raise DatabaseError(f"删除{self.table_name}记录失败: {e}") from e

    def search(
        self,
        conditions: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        搜索记录模板

        Args:
            conditions: 搜索条件
            order_by: 排序字段
            limit: 限制数量
            offset: 偏移量

        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        try:
            sql = f"SELECT * FROM {self.table_name}"
            params = []

            # 构建WHERE子句
            if conditions:
                where_clauses = []
                for key, value in conditions.items():
                    if isinstance(value, (list, tuple)):
                        # IN查询
                        placeholders = ", ".join(["?" for _ in value])
                        where_clauses.append(f"{key} IN ({placeholders})")
                        params.extend(value)
                    elif isinstance(value, str) and "%" in value:
                        # LIKE查询
                        where_clauses.append(f"{key} LIKE ?")
                        params.append(value)
                    else:
                        # 等值查询
                        where_clauses.append(f"{key} = ?")
                        params.append(value)

                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)

            # 添加排序
            if order_by:
                sql += f" ORDER BY {order_by}"

            # 添加分页
            if limit:
                sql += f" LIMIT {limit}"
                if offset:
                    sql += f" OFFSET {offset}"

            # 执行查询
            results = self.db_manager.execute_query(sql, tuple(params))
            return [self._row_to_dict(row) for row in results]

        except Exception as e:
            self.logger.error(f"搜索{self.table_name}记录失败: {e}")
            raise DatabaseError(f"搜索{self.table_name}记录失败: {e}") from e

    def count(self, conditions: dict[str, Any] | None = None) -> int:
        """
        统计记录数量模板

        Args:
            conditions: 统计条件

        Returns:
            int: 记录数量
        """
        try:
            sql = f"SELECT COUNT(*) FROM {self.table_name}"
            params = []

            # 构建WHERE子句
            if conditions:
                where_clauses = []
                for key, value in conditions.items():
                    if isinstance(value, (list, tuple)):
                        placeholders = ", ".join(["?" for _ in value])
                        where_clauses.append(f"{key} IN ({placeholders})")
                        params.extend(value)
                    elif isinstance(value, str) and "%" in value:
                        where_clauses.append(f"{key} LIKE ?")
                        params.append(value)
                    else:
                        where_clauses.append(f"{key} = ?")
                        params.append(value)

                if where_clauses:
                    sql += " WHERE " + " AND ".join(where_clauses)

            # 执行查询
            result = self.db_manager.execute_query(sql, tuple(params))
            return result[0][0] if result else 0

        except Exception as e:
            self.logger.error(f"统计{self.table_name}记录失败: {e}")
            raise DatabaseError(f"统计{self.table_name}记录失败: {e}") from e

    @abstractmethod
    def _row_to_dict(self, row) -> dict[str, Any]:
        """
        将数据库行转换为字典

        Args:
            row: 数据库行

        Returns:
            Dict[str, Any]: 字典格式的数据
        """
        pass


class StandardCRUDTemplate(CRUDTemplate):
    """
    标准CRUD模板实现

    适用于大多数标准表结构的CRUD操作。
    """

    def _row_to_dict(self, row) -> dict[str, Any]:
        """将数据库行转换为字典"""
        if hasattr(row, "keys"):
            return dict(row)
        else:
            # 如果是元组，需要子类提供字段映射
            raise NotImplementedError("元组行需要子类提供字段映射")


def create_crud_template(
    table_name: str, db_manager, logger: logging.Logger | None = None
) -> StandardCRUDTemplate:
    """
    创建标准CRUD模板实例

    Args:
        table_name: 表名
        db_manager: 数据库管理器
        logger: 日志记录器

    Returns:
        StandardCRUDTemplate: CRUD模板实例
    """
    return StandardCRUDTemplate(table_name, db_manager, logger)


def paginated_search_template(
    crud_template: CRUDTemplate,
    conditions: dict[str, Any] | None = None,
    page: int = 1,
    page_size: int = 20,
    order_by: str | None = None,
) -> tuple[list[dict[str, Any]], int, int]:
    """
    分页搜索模板

    Args:
        crud_template: CRUD模板实例
        conditions: 搜索条件
        page: 页码（从1开始）
        page_size: 每页大小
        order_by: 排序字段

    Returns:
        Tuple[List[Dict[str, Any]], int, int]: (数据列表, 总记录数, 总页数)
    """
    try:
        # 计算偏移量
        offset = (page - 1) * page_size

        # 获取总记录数
        total_count = crud_template.count(conditions)

        # 计算总页数
        total_pages = (total_count + page_size - 1) // page_size

        # 获取当前页数据
        data = crud_template.search(
            conditions=conditions, order_by=order_by, limit=page_size, offset=offset
        )

        return data, total_count, total_pages

    except Exception as e:
        crud_template.logger.error(f"分页搜索失败: {e}")
        raise DatabaseError(f"分页搜索失败: {e}") from e


def batch_operation_template(
    crud_template: CRUDTemplate,
    operation: str,
    data_list: list[dict[str, Any]],
    validate_func: Callable | None = None,
) -> list[int]:
    """
    批量操作模板

    Args:
        crud_template: CRUD模板实例
        operation: 操作类型 ('create', 'update', 'delete')
        data_list: 数据列表
        validate_func: 数据验证函数

    Returns:
        List[int]: 操作结果列表（创建时返回ID列表，更新/删除时返回影响行数列表）

    Raises:
        ValueError: 不支持的操作类型
        DatabaseError: 批量操作失败
    """
    if operation not in ["create", "update", "delete"]:
        raise ValueError(f"不支持的操作类型: {operation}")

    results = []
    failed_count = 0

    try:
        for i, data in enumerate(data_list):
            try:
                if operation == "create":
                    result = crud_template.create(data, validate_func)
                elif operation == "update":
                    record_id = data.get("id")
                    if not record_id:
                        raise ValueError(f"更新操作缺少ID字段，索引: {i}")
                    result = (
                        1 if crud_template.update(record_id, data, validate_func) else 0
                    )
                elif operation == "delete":
                    record_id = data.get("id")
                    if not record_id:
                        raise ValueError(f"删除操作缺少ID字段，索引: {i}")
                    result = 1 if crud_template.delete(record_id) else 0

                results.append(result)

            except Exception as e:
                crud_template.logger.warning(f"批量操作第{i + 1}项失败: {e}")
                results.append(0)
                failed_count += 1

        if failed_count > 0:
            crud_template.logger.warning(
                f"批量{operation}操作完成，失败{failed_count}项"
            )
        else:
            crud_template.logger.info(
                f"批量{operation}操作全部成功，共{len(data_list)}项"
            )

        return results

    except Exception as e:
        crud_template.logger.error(f"批量{operation}操作失败: {e}")
        raise DatabaseError(f"批量{operation}操作失败: {e}") from e
