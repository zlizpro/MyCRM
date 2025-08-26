"""增强版客户数据访问对象.

实现客户相关的数据访问操作,集成transfunctions进行数据验证和格式化.
支持客户信息管理、客户分级管理等功能.

主要功能:
- 客户CRUD操作
- 客户搜索和筛选
- 客户数据验证
- 客户统计分析
- 客户等级管理
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
    format_currency,
    format_phone,
    validate_customer_data,
)


if TYPE_CHECKING:
    from minicrm.data.database_manager_enhanced import EnhancedDatabaseManager


class EnhancedCustomerDAO(EnhancedBaseDAO):
    """增强版客户数据访问对象.

    提供完整的客户数据访问功能,包括CRUD操作、搜索筛选、数据验证等.
    """

    def __init__(self, db_manager: EnhancedDatabaseManager):
        """初始化客户DAO.

        Args:
            db_manager: 增强版数据库管理器
        """
        super().__init__(db_manager, "customers")
        self._logger = logging.getLogger(__name__)
        self._sql_builder = SafeSQLBuilder("customers")

    def _get_validation_config(self) -> dict[str, Any]:
        """获取客户数据验证配置.

        Returns:
            dict[str, Any]: 验证配置字典
        """
        return {
            "required_fields": ["name", "phone"],
            "optional_fields": [
                "email",
                "company",
                "address",
                "customer_type_id",
                "level",
                "credit_limit",
            ],
            "field_types": {
                "name": str,
                "phone": str,
                "email": str,
                "company": str,
                "address": str,
                "customer_type_id": int,
                "level": str,
                "credit_limit": float,
            },
            "field_constraints": {
                "name": {"max_length": 100},
                "phone": {"max_length": 20},
                "email": {"max_length": 100},
                "company": {"max_length": 200},
                "address": {"max_length": 500},
                "level": {"choices": ["vip", "important", "normal", "potential"]},
                "credit_limit": {"min_value": 0},
            },
        }

    def _get_table_schema(self) -> dict[str, str]:
        """获取客户表结构定义.

        Returns:
            dict[str, str]: 字段名到类型的映射
        """
        return {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT NOT NULL",
            "phone": "TEXT",
            "email": "TEXT",
            "company": "TEXT",
            "address": "TEXT",
            "customer_type_id": "INTEGER",
            "level": 'TEXT DEFAULT "normal"',
            "credit_limit": "REAL DEFAULT 0",
            "created_at": "TEXT NOT NULL",
            "updated_at": "TEXT NOT NULL",
            "deleted_at": "TEXT",
        }

    def create_customer(self, customer_data: dict[str, Any]) -> int:
        """创建新客户.

        Args:
            customer_data: 客户数据

        Returns:
            int: 新客户ID

        Raises:
            ValidationError: 数据验证失败
        """
        try:
            # 使用transfunctions验证客户数据
            validation_result = validate_customer_data(customer_data)

            if not validation_result.is_valid:
                error_msg = f"客户数据验证失败: {'; '.join(validation_result.errors)}"
                raise ValidationError(error_msg)

            # 使用原始数据(已验证)
            validated_data = customer_data.copy()

            # 格式化电话号码
            if validated_data.get("phone"):
                validated_data["phone"] = format_phone(validated_data["phone"])

            # 创建客户记录
            customer_id = self.create(validated_data)

            self._logger.info(
                "成功创建客户: %s, ID: %s", validated_data.get("name"), customer_id
            )
            return customer_id

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e, "创建", "客户", context={"customer_name": customer_data.get("name")}
            )

    def update_customer(self, customer_id: int, customer_data: dict[str, Any]) -> bool:
        """更新客户信息.

        Args:
            customer_id: 客户ID
            customer_data: 更新数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 验证更新数据
            validation_result = validate_customer_data(customer_data)

            if not validation_result.is_valid:
                error_msg = f"客户数据验证失败: {'; '.join(validation_result.errors)}"
                raise ValidationError(error_msg)

            validated_data = customer_data.copy()

            # 格式化电话号码
            if validated_data.get("phone"):
                validated_data["phone"] = format_phone(validated_data["phone"])

            # 更新客户记录
            success = self.update(customer_id, validated_data)

            if success:
                self._logger.info("成功更新客户: ID %s", customer_id)

            return success

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e, "更新", "客户", context={"customer_id": customer_id}
            )

    def search_customers(
        self,
        query: str | None = None,
        customer_type_id: int | None = None,
        level: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """搜索客户.

        Args:
            query: 搜索关键词(姓名、公司、电话)
            customer_type_id: 客户类型ID
            level: 客户等级
            page: 页码
            page_size: 每页大小

        Returns:
            dict[str, Any]: 分页搜索结果
        """
        try:
            # 构建基础搜索条件
            conditions = {}
            if customer_type_id:
                conditions["customer_type_id"] = customer_type_id
            if level:
                conditions["level"] = level

            # 优化return语句位置:根据查询类型直接返回结果
            if query:
                return self._search_customers_with_query(
                    query, conditions, page, page_size
                )

            # 简化条件判断逻辑:直接返回分页搜索结果
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
                "客户",
                context={
                    "query": query,
                    "customer_type_id": customer_type_id,
                    "level": level,
                },
            )

    def _search_customers_with_query(
        self, query: str, conditions: dict[str, Any], page: int, page_size: int
    ) -> dict[str, Any]:
        """使用关键词搜索客户.

        Args:
            query: 搜索关键词
            conditions: 其他搜索条件
            page: 页码
            page_size: 每页大小

        Returns:
            dict[str, Any]: 搜索结果
        """
        try:
            # 定义可搜索的列名
            search_columns = ["name", "company", "phone"]

            # 计算偏移量
            offset = (page - 1) * page_size

            # 构建安全的计数查询
            count_sql, count_params = self._sql_builder.build_search_with_like(
                search_columns=search_columns,
                search_value=query,
                additional_conditions=conditions,
                include_deleted=False,
            )
            # 将SELECT *替换为COUNT(*)
            count_sql = count_sql.replace("SELECT *", "SELECT COUNT(*) as count", 1)
            # 移除ORDER BY、LIMIT、OFFSET子句(如果存在)
            count_sql = count_sql.split(" ORDER BY")[0]
            count_sql = count_sql.split(" LIMIT")[0]

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

            # 转换结果
            customers = [convert_row_to_dict(row) for row in query_results]

            # 计算分页信息
            pagination = calculate_pagination(page, page_size, total_count)

            return {
                "data": customers,
                "pagination": pagination,
                "total_count": total_count,
            }

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e, "搜索", "客户", context={"query": query, "conditions": conditions}
            )

    def get_customers_by_type(self, customer_type_id: int) -> list[dict[str, Any]]:
        """根据客户类型获取客户列表.

        Args:
            customer_type_id: 客户类型ID

        Returns:
            list[dict[str, Any]]: 客户列表
        """
        try:
            # 使用安全的SQL构建器
            sql, params = self._sql_builder.build_select(
                conditions={"customer_type_id": customer_type_id},
                order_by="name ASC",
                include_deleted=False,
            )

            results = self._db_manager.execute_query(sql, params)
            return [convert_row_to_dict(row) for row in results]

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e, "查询", "客户", context={"customer_type_id": customer_type_id}
            )

    def get_customers_by_level(self, level: str) -> list[dict[str, Any]]:
        """根据客户等级获取客户列表.

        Args:
            level: 客户等级

        Returns:
            list[dict[str, Any]]: 客户列表
        """
        return self.search(conditions={"level": level}, order_by="name ASC")

    def get_customer_statistics(self) -> dict[str, Any]:
        """获取客户统计信息.

        Returns:
            dict[str, Any]: 统计信息
        """
        try:
            # 总客户数
            total_customers = self.count()

            # 按等级统计 - 简化循环逻辑
            level_stats = {}
            for level in ["vip", "important", "normal", "potential"]:
                level_stats[level] = self.count({"level": level})

            # 本月新增客户数 - 使用安全的SQL构建
            current_month = datetime.now(timezone.utc).strftime("%Y-%m")
            table_name = SQLSafetyValidator.validate_table_name(self._table_name)

            # 构建安全的月度统计查询
            monthly_sql = f"""
            SELECT COUNT(*) as count
            FROM {table_name}
            WHERE deleted_at IS NULL AND created_at LIKE ?
            """
            monthly_result = self._db_manager.execute_query(
                monthly_sql, (f"{current_month}%",)
            )
            monthly_new = monthly_result[0]["count"] if monthly_result else 0

            # 总授信额度 - 使用安全的SQL构建
            credit_sql = f"""
            SELECT SUM(credit_limit) as total_credit
            FROM {table_name}
            WHERE deleted_at IS NULL
            """
            credit_result = self._db_manager.execute_query(credit_sql)

            # 简化复杂条件判断逻辑
            total_credit = 0
            if credit_result and credit_result[0]["total_credit"]:
                total_credit = credit_result[0]["total_credit"]

            # 优化return语句位置:直接返回统计结果
            return {
                "total_customers": total_customers,
                "level_statistics": level_stats,
                "monthly_new_customers": monthly_new,
                "total_credit_limit": format_currency(total_credit),
            }

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e, "统计", "客户", context={"operation": "get_customer_statistics"}
            )

    def update_customer_level(self, customer_id: int, new_level: str) -> bool:
        """更新客户等级.

        Args:
            customer_id: 客户ID
            new_level: 新等级

        Returns:
            bool: 更新是否成功
        """
        # 简化条件判断逻辑:提前验证并返回
        valid_levels = ["vip", "important", "normal", "potential"]
        if new_level not in valid_levels:
            error_msg = f"无效的客户等级: {new_level}"
            raise ValidationError(error_msg)

        # 优化return语句位置:直接返回更新结果
        return self.update(customer_id, {"level": new_level})

    def update_credit_limit(self, customer_id: int, credit_limit: float) -> bool:
        """更新客户授信额度.

        Args:
            customer_id: 客户ID
            credit_limit: 授信额度

        Returns:
            bool: 更新是否成功
        """
        if credit_limit < 0:
            error_msg = "授信额度不能为负数"
            raise ValidationError(error_msg)

        return self.update(customer_id, {"credit_limit": credit_limit})

    def get_high_value_customers(
        self, min_credit_limit: float = 100000
    ) -> list[dict[str, Any]]:
        """获取高价值客户列表.

        Args:
            min_credit_limit: 最小授信额度

        Returns:
            list[dict[str, Any]]: 高价值客户列表
        """
        try:
            # 验证表名安全性
            table_name = SQLSafetyValidator.validate_table_name(self._table_name)

            # 构建安全的SQL查询
            sql = f"""
            SELECT * FROM {table_name}
            WHERE deleted_at IS NULL
            AND credit_limit >= ?
            ORDER BY credit_limit DESC
            """

            results = self._db_manager.execute_query(sql, (min_credit_limit,))
            return [convert_row_to_dict(row) for row in results]

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e, "查询", "客户", context={"min_credit_limit": min_credit_limit}
            )


class EnhancedCustomerTypeDAO(EnhancedBaseDAO):
    """增强版客户类型数据访问对象.

    提供客户类型的CRUD操作和管理功能.
    """

    def __init__(self, db_manager: EnhancedDatabaseManager):
        """初始化客户类型DAO.

        Args:
            db_manager: 增强版数据库管理器
        """
        super().__init__(db_manager, "customer_types")
        self._logger = logging.getLogger(__name__)
        self._sql_builder = SafeSQLBuilder("customer_types")

    def _get_validation_config(self) -> dict[str, Any]:
        """获取客户类型数据验证配置.

        Returns:
            dict[str, Any]: 验证配置字典
        """
        return {
            "required_fields": ["name"],
            "optional_fields": ["description", "color_code"],
            "field_types": {"name": str, "description": str, "color_code": str},
            "field_constraints": {
                "name": {"max_length": 50},
                "description": {"max_length": 200},
                "color_code": {"max_length": 7},  # #RRGGBB格式
            },
        }

    def _get_table_schema(self) -> dict[str, str]:
        """获取客户类型表结构定义.

        Returns:
            dict[str, str]: 字段名到类型的映射
        """
        return {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT NOT NULL UNIQUE",
            "description": "TEXT",
            "color_code": "TEXT",
            "created_at": "TEXT NOT NULL",
            "updated_at": "TEXT NOT NULL",
            "deleted_at": "TEXT",
        }

    def create_customer_type(self, type_data: dict[str, Any]) -> int:
        """创建客户类型.

        Args:
            type_data: 客户类型数据

        Returns:
            int: 新客户类型ID
        """
        try:
            # 检查名称是否已存在
            existing = self.search({"name": type_data.get("name")})
            if existing:
                error_msg = f"客户类型名称已存在: {type_data.get('name')}"
                raise ValidationError(error_msg)

            type_id = self.create(type_data)
            self._logger.info(
                "成功创建客户类型: %s, ID: %s", type_data.get("name"), type_id
            )
            return type_id

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e, "创建", "客户类型", context={"type_name": type_data.get("name")}
            )

    def get_customer_type_usage_count(self, type_id: int) -> int:
        """获取客户类型的使用数量.

        Args:
            type_id: 客户类型ID

        Returns:
            int: 使用该类型的客户数量
        """
        try:
            sql = """
            SELECT COUNT(*) as count
            FROM customers
            WHERE customer_type_id = ? AND deleted_at IS NULL
            """

            results = self._db_manager.execute_query(sql, (type_id,))
            return results[0]["count"] if results else 0

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e, "统计", "客户类型", context={"type_id": type_id}
            )

    def delete_customer_type(self, type_id: int, force: bool = False) -> bool:
        """删除客户类型.

        Args:
            type_id: 客户类型ID
            force: 是否强制删除(即使有客户在使用)

        Returns:
            bool: 删除是否成功
        """
        try:
            # 简化复杂条件判断逻辑:提前检查使用情况
            usage_count = self.get_customer_type_usage_count(type_id)

            if usage_count > 0 and not force:
                error_msg = f"无法删除客户类型,仍有 {usage_count} 个客户在使用"
                raise ValidationError(error_msg)

            # 优化return语句位置:直接返回删除结果
            return self.delete(type_id)

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e, "删除", "客户类型", context={"type_id": type_id, "force": force}
            )

    def get_all_customer_types_with_usage(self) -> list[dict[str, Any]]:
        """获取所有客户类型及其使用情况.

        Returns:
            list[dict[str, Any]]: 客户类型列表,包含使用数量
        """
        try:
            types = self.list_all(order_by="name ASC")

            # 为每个类型添加使用数量
            for customer_type in types:
                usage_count = self.get_customer_type_usage_count(customer_type["id"])
                customer_type["usage_count"] = usage_count

            return types

        except Exception as e:
            DAOExceptionHandler.handle_dao_error(
                e, "查询", "客户类型", context={"operation": "get_all_with_usage"}
            )
