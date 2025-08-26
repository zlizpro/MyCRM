"""增强版供应商数据访问对象.

实现供应商相关的数据访问操作,集成transfunctions进行数据验证和格式化.
支持供应商信息管理、供应商分级管理等功能.

主要功能:
- 供应商CRUD操作
- 供应商搜索和筛选
- 供应商数据验证
- 供应商统计分析
- 供应商等级管理
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import TYPE_CHECKING, Any

from minicrm.core.exceptions import ValidationError
from minicrm.core.sql_safety import SafeSQLBuilder, SQLSafetyValidator
from minicrm.data.dao.dao_exception_handler import DAOExceptionHandler
from minicrm.data.dao.enhanced_base_dao import EnhancedBaseDAO
from transfunctions import (
    calculate_pagination,
    convert_row_to_dict,
    format_phone,
    validate_supplier_data,
)


if TYPE_CHECKING:
    from minicrm.data.database_manager_enhanced import EnhancedDatabaseManager


class EnhancedSupplierDAO(EnhancedBaseDAO):
    """增强版供应商数据访问对象.

    提供完整的供应商数据访问功能,包括CRUD操作、搜索筛选、数据验证等.
    """

    def __init__(self, db_manager: EnhancedDatabaseManager):
        """初始化供应商DAO.

        Args:
            db_manager: 增强版数据库管理器
        """
        super().__init__(db_manager, "suppliers")
        self._logger = logging.getLogger(__name__)
        self._sql_builder = SafeSQLBuilder("suppliers")

    def _get_validation_config(self) -> dict[str, Any]:
        """获取供应商数据验证配置.

        Returns:
            dict[str, Any]: 验证配置字典
        """
        return {
            "required_fields": ["name", "contact_person", "phone"],
            "optional_fields": [
                "email",
                "company",
                "address",
                "supplier_type_id",
                "level",
                "business_license",
            ],
            "field_types": {
                "name": str,
                "contact_person": str,
                "phone": str,
                "email": str,
                "company": str,
                "address": str,
                "supplier_type_id": int,
                "level": str,
                "business_license": str,
            },
        }

    def _get_table_schema(self) -> dict[str, str]:
        """获取供应商表结构定义."""
        return {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT NOT NULL",
            "contact_person": "TEXT NOT NULL",
            "phone": "TEXT",
            "email": "TEXT",
            "company": "TEXT",
            "address": "TEXT",
            "supplier_type_id": "INTEGER",
            "level": 'TEXT DEFAULT "normal"',
            "business_license": "TEXT",
            "created_at": "TEXT NOT NULL",
            "updated_at": "TEXT NOT NULL",
            "deleted_at": "TEXT",
        }

    def create_supplier(self, supplier_data: dict[str, Any]) -> int:
        """创建新供应商.

        Args:
            supplier_data: 供应商数据

        Returns:
            int: 新供应商ID
        """
        try:
            # 使用transfunctions验证供应商数据
            validation_result = validate_supplier_data(supplier_data)

            if not validation_result.is_valid:
                error_msg = f"供应商数据验证失败: {'; '.join(validation_result.errors)}"
                raise ValidationError(error_msg)

            validated_data = supplier_data.copy()

            # 格式化电话号码
            if validated_data.get("phone"):
                validated_data["phone"] = format_phone(validated_data["phone"])

            # 创建供应商记录
            supplier_id = self.create(validated_data)

            self._logger.info(
                "成功创建供应商: %s, ID: %s", validated_data.get("name"), supplier_id
            )
            return supplier_id

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e,
                "创建",
                "供应商",
                context={
                    "supplier_name": validated_data.get("name")
                    if "validated_data" in locals()
                    else supplier_data.get("name")
                },
            )

    def update_supplier(self, supplier_id: int, supplier_data: dict[str, Any]) -> bool:
        """更新供应商信息.

        Args:
            supplier_id: 供应商ID
            supplier_data: 更新数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 验证更新数据
            validation_result = validate_supplier_data(supplier_data)

            if not validation_result.is_valid:
                error_msg = f"供应商数据验证失败: {'; '.join(validation_result.errors)}"
                raise ValidationError(error_msg)

            validated_data = supplier_data.copy()

            # 格式化电话号码
            if validated_data.get("phone"):
                validated_data["phone"] = format_phone(validated_data["phone"])

            # 更新供应商记录
            success = self.update(supplier_id, validated_data)

            if success:
                self._logger.info("成功更新供应商: ID %s", supplier_id)

            return success

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e, "更新", "供应商", context={"supplier_id": supplier_id}
            )

    def search_suppliers(
        self,
        query: str | None = None,
        supplier_type_id: int | None = None,
        level: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """搜索供应商.

        Args:
            query: 搜索关键词
            supplier_type_id: 供应商类型ID
            level: 供应商等级
            page: 页码
            page_size: 每页大小

        Returns:
            dict[str, Any]: 分页搜索结果
        """
        try:
            # 优化复杂方法结构:简化条件构建
            conditions = {}
            if supplier_type_id:
                conditions["supplier_type_id"] = supplier_type_id
            if level:
                conditions["level"] = level

            # 优化return语句位置:根据查询类型直接返回
            if query:
                return self._search_suppliers_with_query(
                    query, conditions, page, page_size
                )

            # 确保与其他DAO文件一致性:统一返回格式
            return self.paginated_search(
                page=page,
                page_size=page_size,
                conditions=conditions,
                order_by="created_at DESC",
            )

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e,
                "搜索",
                "供应商",
                context={
                    "query": query,
                    "supplier_type_id": supplier_type_id,
                    "level": level,
                },
            )

    def _search_suppliers_with_query(
        self, query: str, conditions: dict[str, Any], page: int, page_size: int
    ) -> dict[str, Any]:
        """使用关键词搜索供应商.

        Args:
            query: 搜索关键词
            conditions: 附加搜索条件
            page: 页码
            page_size: 每页大小

        Returns:
            dict[str, Any]: 搜索结果包含数据和分页信息
        """
        try:
            # 定义可搜索的列名
            search_columns = ["name", "company", "contact_person", "phone"]
            offset = (page - 1) * page_size

            # 构建安全的计数查询
            count_sql, count_params = self._sql_builder.build_search_with_like(
                search_columns=search_columns,
                search_value=query,
                additional_conditions=conditions,
                include_deleted=False,
            )
            # 优化复杂方法结构:简化SQL处理
            count_sql = count_sql.replace("SELECT *", "SELECT COUNT(*) as count", 1)
            count_sql = count_sql.split(" ORDER BY")[0].split(" LIMIT")[0]

            # 构建安全的数据查询
            data_sql, data_params = self._sql_builder.build_search_with_like(
                search_columns=search_columns,
                search_value=query,
                additional_conditions=conditions,
                order_by="created_at DESC",
                limit=page_size,
                offset=offset,
                include_deleted=False,
            )

            # 执行查询
            count_result = self._db_manager.execute_query(count_sql, count_params)
            total_count = count_result[0]["count"] if count_result else 0

            query_results = self._db_manager.execute_query(data_sql, data_params)

            # 提高代码可读性:分步处理结果
            suppliers = [convert_row_to_dict(row) for row in query_results]
            pagination = calculate_pagination(page, page_size, total_count)

            # 优化return语句位置:直接返回结果字典
            return {
                "data": suppliers,
                "pagination": pagination,
                "total_count": total_count,
            }

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e, "搜索", "供应商", context={"query": query, "conditions": conditions}
            )

    def get_supplier_statistics(self) -> dict[str, Any]:
        """获取供应商统计信息.

        Returns:
            dict[str, Any]: 包含总数、等级统计和月度新增的统计信息
        """
        try:
            # 总供应商数
            total_suppliers = self.count()

            # 按等级统计 - 提高代码可读性
            level_stats = {}
            for level in ["strategic", "important", "normal", "backup"]:
                level_stats[level] = self.count({"level": level})

            # 本月新增供应商数 - 确保与其他DAO文件一致性
            current_month = datetime.now(timezone.utc).strftime("%Y-%m")
            table_name = SQLSafetyValidator.validate_table_name(self._table_name)

            monthly_sql = f"""
            SELECT COUNT(*) as count
            FROM {table_name}
            WHERE deleted_at IS NULL AND created_at LIKE ?
            """
            monthly_result = self._db_manager.execute_query(
                monthly_sql, (f"{current_month}%",)
            )
            monthly_new = monthly_result[0]["count"] if monthly_result else 0

            # 优化return语句位置:直接返回统计结果
            return {
                "total_suppliers": total_suppliers,
                "level_statistics": level_stats,
                "monthly_new_suppliers": monthly_new,
            }

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e, "统计", "供应商", context={"operation": "get_supplier_statistics"}
            )


class EnhancedSupplierTypeDAO(EnhancedBaseDAO):
    """增强版供应商类型数据访问对象."""

    def __init__(self, db_manager: EnhancedDatabaseManager):
        """初始化供应商类型DAO."""
        super().__init__(db_manager, "supplier_types")
        self._logger = logging.getLogger(__name__)
        self._sql_builder = SafeSQLBuilder("supplier_types")

    def _get_validation_config(self) -> dict[str, Any]:
        """获取供应商类型数据验证配置."""
        return {
            "required_fields": ["name"],
            "optional_fields": ["description", "color_code"],
            "field_types": {"name": str, "description": str, "color_code": str},
        }

    def _get_table_schema(self) -> dict[str, str]:
        """获取供应商类型表结构定义."""
        return {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT NOT NULL UNIQUE",
            "description": "TEXT",
            "color_code": "TEXT",
            "created_at": "TEXT NOT NULL",
            "updated_at": "TEXT NOT NULL",
            "deleted_at": "TEXT",
        }

    def create_supplier_type(self, type_data: dict[str, Any]) -> int:
        """创建供应商类型."""
        try:
            # 检查名称是否已存在
            existing = self.search({"name": type_data.get("name")})
            if existing:
                error_msg = f"供应商类型名称已存在: {type_data.get('name')}"
                raise ValidationError(error_msg)

            type_id = self.create(type_data)
            self._logger.info(
                "成功创建供应商类型: %s, ID: %s", type_data.get("name"), type_id
            )
            return type_id

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e, "创建", "供应商类型", context={"type_name": type_data.get("name")}
            )

    def get_supplier_type_usage_count(self, type_id: int) -> int:
        """获取供应商类型的使用数量."""
        try:
            sql = """
            SELECT COUNT(*) as count
            FROM suppliers
            WHERE supplier_type_id = ? AND deleted_at IS NULL
            """

            results = self._db_manager.execute_query(sql, (type_id,))
            return results[0]["count"] if results else 0

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e, "统计", "供应商类型", context={"type_id": type_id}
            )
