"""增强版基础数据访问对象.

集成EnhancedDatabaseManager和transfunctions的完整DAO基类实现.
提供通用的CRUD操作、数据验证、分页查询等功能.

主要功能:
- 集成transfunctions的CRUD模板
- 支持数据验证和格式化
- 分页查询支持
- 软删除支持
- 审计日志集成
- 事务管理
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import logging
from typing import TYPE_CHECKING, Any

from minicrm.core.exceptions import DatabaseError, ValidationError
from transfunctions import (
    ValidationError as TransValidationError,
    calculate_pagination,
    convert_row_to_dict,
    create_crud_template,
)


if TYPE_CHECKING:
    from minicrm.data.database_manager_enhanced import EnhancedDatabaseManager


class EnhancedBaseDAO(ABC):
    """增强版基础数据访问对象.

    提供完整的CRUD操作、数据验证、分页查询等功能.
    所有具体DAO类都应该继承此基类.
    """

    def __init__(self, db_manager: EnhancedDatabaseManager, table_name: str):
        """初始化增强版基础DAO.

        Args:
            db_manager: 增强版数据库管理器
            table_name: 表名
        """
        self._db_manager = db_manager
        self._table_name = table_name
        self._logger = logging.getLogger(__name__)

        # 创建CRUD模板实例
        self._crud_template = create_crud_template(
            table_name=table_name, db_manager=db_manager, logger=self._logger
        )

        self._logger.debug("增强版DAO初始化完成: %s", table_name)

    @abstractmethod
    def _get_validation_config(self) -> dict[str, Any]:
        """获取数据验证配置.

        子类必须实现此方法,返回该实体的验证配置.

        Returns:
            dict[str, Any]: 验证配置字典
        """

    @abstractmethod
    def _get_table_schema(self) -> dict[str, str]:
        """获取表结构定义.

        子类必须实现此方法,返回表的字段定义.

        Returns:
            dict[str, str]: 字段名到类型的映射
        """

    def create(self, data: dict[str, Any]) -> int:
        """创建新记录.

        Args:
            data: 要创建的数据

        Returns:
            int: 新创建记录的ID

        Raises:
            ValidationError: 数据验证失败
            DatabaseError: 数据库操作失败
        """
        try:
            # 数据预处理
            processed_data = self._preprocess_create_data(data)

            # 使用CRUD模板创建记录
            record_id = self._crud_template.create(processed_data)

            self._logger.info("成功创建%s记录,ID: %s", self._table_name, record_id)
            return record_id
        except TransValidationError as e:
            error_msg = f"{self._table_name}数据验证失败: {e}"
            raise ValidationError(error_msg) from e
        except Exception as e:
            error_msg = f"创建{self._table_name}记录失败: {e}"
            raise DatabaseError(error_msg) from e

    def get_by_id(self, record_id: int) -> dict[str, Any] | None:
        """根据ID获取记录.

        Args:
            record_id: 记录ID

        Returns:
            dict[str, Any] | None: 记录数据,不存在时返回None
        """
        try:
            sql = "SELECT * FROM ? WHERE id = ? AND deleted_at IS NULL"
            results = self._db_manager.execute_query(
                sql, (self._table_name, record_id), table_name=self._table_name
            )

            # 优化return语句位置,直接返回结果
            if not results:
                return None
            return convert_row_to_dict(results[0])

        except Exception as e:
            error_msg = f"获取{self._table_name}记录失败: {e}"
            raise DatabaseError(error_msg) from e

    def update(self, record_id: int, data: dict[str, Any]) -> bool:
        """更新记录.

        Args:
            record_id: 记录ID
            data: 更新数据

        Returns:
            bool: 更新是否成功

        Raises:
            ValidationError: 数据验证失败
            DatabaseError: 数据库操作失败
        """
        try:
            # 检查记录是否存在
            existing_record = self.get_by_id(record_id)
            if not existing_record:
                error_msg = f"{self._table_name}记录不存在: {record_id}"
                raise ValidationError(error_msg)

            # 数据预处理
            processed_data = self._preprocess_update_data(data)

            # 使用CRUD模板更新记录
            success = self._crud_template.update(record_id, processed_data)

            if success:
                self._logger.info("成功更新%s记录,ID: %s", self._table_name, record_id)
            return success
        except TransValidationError as e:
            error_msg = f"{self._table_name}数据验证失败: {e}"
            raise ValidationError(error_msg) from e
        except ValidationError:
            raise
        except Exception as e:
            error_msg = f"更新{self._table_name}记录失败: {e}"
            raise DatabaseError(error_msg) from e

    def delete(self, record_id: int, soft_delete: bool = True) -> bool:
        """删除记录.

        Args:
            record_id: 记录ID
            soft_delete: 是否软删除(默认True)

        Returns:
            bool: 删除是否成功
        """
        try:
            if soft_delete:
                # 软删除: 设置deleted_at字段
                return self.soft_delete(record_id)
            # 硬删除: 物理删除记录
            return self.hard_delete(record_id)
        except Exception as e:
            error_msg = f"删除{self._table_name}记录失败: {e}"
            raise DatabaseError(error_msg) from e

    def soft_delete(self, record_id: int) -> bool:
        """软删除记录.

        Args:
            record_id: 记录ID

        Returns:
            bool: 删除是否成功
        """
        try:
            sql = "UPDATE ? SET deleted_at = ?, updated_at = ? WHERE id = ?"
            now = datetime.now(timezone.utc).isoformat()

            affected_rows = self._db_manager.execute_update(
                sql,
                (self._table_name, now, now, record_id),
                table_name=self._table_name,
            )

            success = affected_rows > 0
            if success:
                self._logger.info(
                    "成功软删除%s记录,ID: %s", self._table_name, record_id
                )
            return success
        except Exception as e:
            error_msg = f"软删除{self._table_name}记录失败: {e}"
            raise DatabaseError(error_msg) from e

    def hard_delete(self, record_id: int) -> bool:
        """硬删除记录.

        Args:
            record_id: 记录ID

        Returns:
            bool: 删除是否成功
        """
        try:
            sql = "DELETE FROM ? WHERE id = ?"

            deleted_rows = self._db_manager.execute_delete(
                sql, (self._table_name, record_id), table_name=self._table_name
            )

            success = deleted_rows > 0
            if success:
                self._logger.info(
                    "成功硬删除%s记录,ID: %s", self._table_name, record_id
                )
            return success
        except Exception as e:
            error_msg = f"硬删除{self._table_name}记录失败: {e}"
            raise DatabaseError(error_msg) from e

    def search(
        self,
        conditions: dict[str, Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
        include_deleted: bool = False,
    ) -> list[dict[str, Any]]:
        """搜索记录.

        Args:
            conditions: 搜索条件
            order_by: 排序字段
            limit: 限制数量
            offset: 偏移量
            include_deleted: 是否包含已删除记录

        Returns:
            list[dict[str, Any]]: 搜索结果列表
        """
        try:
            # 构建WHERE子句和参数
            where_clauses, params = self._build_where_clause(
                conditions, include_deleted
            )

            # 构建SQL语句
            sql = "SELECT * FROM ?"
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)

            if order_by:
                sql += f" ORDER BY {order_by}"

            if limit:
                sql += f" LIMIT {limit}"
                if offset:
                    sql += f" OFFSET {offset}"

            # 优化元组连接操作,使用列表构建
            query_params = [self._table_name]
            query_params.extend(params)

            results = self._db_manager.execute_query(
                sql, tuple(query_params), table_name=self._table_name
            )

            # 优化return语句,直接返回转换结果
            return [convert_row_to_dict(row) for row in results]
        except Exception as e:
            error_msg = f"搜索{self._table_name}记录失败: {e}"
            raise DatabaseError(error_msg) from e

    def paginated_search(
        self,
        page: int = 1,
        page_size: int = 20,
        conditions: dict[str, Any] | None = None,
        order_by: str | None = None,
        include_deleted: bool = False,
    ) -> dict[str, Any]:
        """分页搜索记录.

        Args:
            page: 页码(从1开始)
            page_size: 每页大小
            conditions: 搜索条件
            order_by: 排序字段
            include_deleted: 是否包含已删除记录

        Returns:
            dict[str, Any]: 分页搜索结果,包含数据和分页信息
        """
        try:
            # 计算偏移量
            offset = (page - 1) * page_size

            # 获取总数
            total_count = self.count(conditions, include_deleted)

            # 获取数据
            data = self.search(
                conditions=conditions,
                order_by=order_by,
                limit=page_size,
                offset=offset,
                include_deleted=include_deleted,
            )

            # 计算分页信息
            pagination = calculate_pagination(page, page_size, total_count)

            return {"data": data, "pagination": pagination, "total_count": total_count}

        except Exception as e:
            error_msg = f"分页搜索{self._table_name}记录失败: {e}"
            raise DatabaseError(error_msg) from e

    def count(
        self, conditions: dict[str, Any] | None = None, include_deleted: bool = False
    ) -> int:
        """统计记录数量.

        Args:
            conditions: 统计条件
            include_deleted: 是否包含已删除记录

        Returns:
            int: 记录数量
        """
        try:
            # 构建WHERE子句和参数
            where_clauses, params = self._build_where_clause(
                conditions, include_deleted
            )

            # 构建SQL语句
            sql = "SELECT COUNT(*) as count FROM ?"
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)

            # 优化元组连接操作,使用列表构建
            query_params = [self._table_name]
            query_params.extend(params)

            results = self._db_manager.execute_query(
                sql, tuple(query_params), table_name=self._table_name
            )

            # 优化return语句,简化逻辑
            return results[0]["count"] if results else 0

        except Exception as e:
            error_msg = f"统计{self._table_name}记录数量失败: {e}"
            raise DatabaseError(error_msg) from e

    def list_all(
        self, order_by: str | None = None, include_deleted: bool = False
    ) -> list[dict[str, Any]]:
        """获取所有记录.

        Args:
            order_by: 排序字段
            include_deleted: 是否包含已删除记录

        Returns:
            list[dict[str, Any]]: 所有记录列表
        """
        # 优化return语句,直接返回search结果
        return self.search(
            conditions=None, order_by=order_by, include_deleted=include_deleted
        )

    def batch_insert(self, data_list: list[dict[str, Any]]) -> list[int]:
        """批量插入记录.

        Args:
            data_list: 要插入的数据列表

        Returns:
            list[int]: 新插入记录的ID列表
        """
        record_ids = []

        with self._db_manager.transaction():
            for data in data_list:
                record_id = self.create(data)
                record_ids.append(record_id)

        self._logger.info("批量插入%d条%s记录", len(record_ids), self._table_name)
        return record_ids

    def batch_update(self, updates: list[tuple[int, dict[str, Any]]]) -> int:
        """批量更新记录.

        Args:
            updates: 更新列表,每个元素为(record_id, update_data)

        Returns:
            int: 成功更新的记录数
        """
        success_count = 0

        with self._db_manager.transaction():
            for record_id, data in updates:
                if self.update(record_id, data):
                    success_count += 1

        # 优化return语句位置,记录日志后直接返回
        self._logger.info("批量更新%d条%s记录", success_count, self._table_name)
        return success_count

    def _preprocess_create_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """预处理创建数据.

        Args:
            data: 原始数据

        Returns:
            dict[str, Any]: 处理后的数据
        """
        processed_data = data.copy()

        # 添加时间戳
        now = datetime.now(timezone.utc).isoformat()
        processed_data["created_at"] = now
        processed_data["updated_at"] = now

        # 确保deleted_at为None
        processed_data["deleted_at"] = None

        return processed_data

    def _preprocess_update_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """预处理更新数据.

        Args:
            data: 原始数据

        Returns:
            dict[str, Any]: 处理后的数据
        """
        processed_data = data.copy()

        # 更新时间戳
        processed_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        # 移除不应该被更新的字段
        processed_data.pop("id", None)
        processed_data.pop("created_at", None)

        return processed_data

    def _build_where_clause(
        self, conditions: dict[str, Any] | None = None, include_deleted: bool = False
    ) -> tuple[list[str], list[Any]]:
        """构建WHERE子句和参数列表.

        提取重复的WHERE子句构建逻辑,提高代码复用性.

        Args:
            conditions: 查询条件
            include_deleted: 是否包含已删除记录

        Returns:
            tuple[list[str], list[Any]]: WHERE子句列表和参数列表
        """
        where_clauses = []
        params = []

        # 添加删除状态过滤
        if not include_deleted:
            where_clauses.append("deleted_at IS NULL")

        # 添加查询条件
        if conditions:
            for field, value in conditions.items():
                if value is not None:
                    where_clauses.append(f"{field} = ?")
                    params.append(value)

        return where_clauses, params

    @property
    def table_name(self) -> str:
        """获取表名.

        Returns:
            str: 表名
        """
        return self._table_name

    @property
    def db_manager(self) -> EnhancedDatabaseManager:
        """获取数据库管理器.

        Returns:
            EnhancedDatabaseManager: 数据库管理器实例
        """
        return self._db_manager
