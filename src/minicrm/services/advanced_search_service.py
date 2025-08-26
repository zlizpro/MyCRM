"""
MiniCRM 高级搜索服务

提供复杂查询功能的业务逻辑层,包括:
- 多条件组合查询
- 范围查询和模糊匹配
- 关联查询和跨表搜索
- 查询结果缓存和优化

设计原则:
- 遵循业务逻辑层职责
- 支持灵活的查询条件组合
- 提供高性能的查询优化
- 统一的搜索接口设计
"""

import contextlib
import logging
from datetime import datetime, timedelta
from typing import Any

from minicrm.core.exceptions import BusinessLogicError, ValidationError
from minicrm.data.dao.customer_dao import CustomerDAO
from minicrm.data.dao.supplier_dao import SupplierDAO
from minicrm.ui.components.advanced_search_dialog import QueryCondition
from transfunctions.data_operations.query_builder import (
    ComparisonOperator,
    LogicalOperator,
    QueryBuilder,
)


class SearchField:
    """搜索字段定义"""

    def __init__(
        self,
        key: str,
        label: str,
        field_type: str,
        table_name: str,
        column_name: str,
        searchable: bool = True,
        filterable: bool = True,
        options: list[dict[str, Any]] | None = None,
    ):
        self.key = key
        self.label = label
        self.field_type = field_type  # text, number, date, boolean, select
        self.table_name = table_name
        self.column_name = column_name
        self.searchable = searchable
        self.filterable = filterable
        self.options = options or []


class SearchResult:
    """搜索结果封装"""

    def __init__(
        self,
        data: list[dict[str, Any]],
        total_count: int,
        page: int = 1,
        page_size: int = 50,
        query_time: float = 0.0,
    ):
        self.data = data
        self.total_count = total_count
        self.page = page
        self.page_size = page_size
        self.query_time = query_time
        self.total_pages = (total_count + page_size - 1) // page_size


class AdvancedSearchService:
    """
    高级搜索服务

    提供复杂查询功能的业务逻辑,支持:
    - 多条件组合查询
    - 范围查询和模糊匹配
    - 关联查询和跨表搜索
    - 查询性能优化
    """

    def __init__(self, customer_dao: CustomerDAO, supplier_dao: SupplierDAO):
        """
        初始化高级搜索服务

        Args:
            customer_dao: 客户数据访问对象
            supplier_dao: 供应商数据访问对象
        """
        self._customer_dao = customer_dao
        self._supplier_dao = supplier_dao
        self._logger = logging.getLogger(__name__)

        # 搜索字段定义
        self._customer_fields = self._init_customer_fields()
        self._supplier_fields = self._init_supplier_fields()

        # 查询缓存(简单的内存缓存)
        self._query_cache: dict[str, tuple[SearchResult, datetime]] = {}
        self._cache_ttl = timedelta(minutes=5)  # 缓存5分钟

    def _init_customer_fields(self) -> list[SearchField]:
        """初始化客户搜索字段"""
        return [
            SearchField("name", "客户名称", "text", "customers", "name"),
            SearchField("phone", "联系电话", "text", "customers", "phone"),
            SearchField("email", "邮箱地址", "text", "customers", "email"),
            SearchField("address", "地址", "text", "customers", "address"),
            SearchField(
                "contact_person", "联系人", "text", "customers", "contact_person"
            ),
            SearchField(
                "customer_type_id",
                "客户类型",
                "select",
                "customers",
                "customer_type_id",
            ),
            SearchField("created_at", "创建时间", "date", "customers", "created_at"),
            SearchField("updated_at", "更新时间", "date", "customers", "updated_at"),
            # 关联字段
            SearchField("total_orders", "订单总数", "number", "orders", "COUNT(*)"),
            SearchField("total_amount", "交易总额", "number", "orders", "SUM(amount)"),
            SearchField(
                "last_order_date", "最后订单日期", "date", "orders", "MAX(order_date)"
            ),
        ]

    def _init_supplier_fields(self) -> list[SearchField]:
        """初始化供应商搜索字段"""
        return [
            SearchField("name", "供应商名称", "text", "suppliers", "name"),
            SearchField("phone", "联系电话", "text", "suppliers", "phone"),
            SearchField("email", "邮箱地址", "text", "suppliers", "email"),
            SearchField("address", "地址", "text", "suppliers", "address"),
            SearchField(
                "contact_person", "联系人", "text", "suppliers", "contact_person"
            ),
            SearchField(
                "supplier_type_id",
                "供应商类型",
                "select",
                "suppliers",
                "supplier_type_id",
            ),
            SearchField(
                "quality_rating", "质量评级", "number", "suppliers", "quality_rating"
            ),
            SearchField("created_at", "创建时间", "date", "suppliers", "created_at"),
            SearchField("updated_at", "更新时间", "date", "suppliers", "updated_at"),
        ]

    def get_customer_search_fields(self) -> list[dict[str, Any]]:
        """
        获取客户搜索字段配置

        Returns:
            List[Dict[str, Any]]: 搜索字段配置列表
        """
        return [
            {
                "key": field.key,
                "label": field.label,
                "type": field.field_type,
                "searchable": field.searchable,
                "filterable": field.filterable,
                "options": field.options,
            }
            for field in self._customer_fields
        ]

    def get_supplier_search_fields(self) -> list[dict[str, Any]]:
        """
        获取供应商搜索字段配置

        Returns:
            List[Dict[str, Any]]: 搜索字段配置列表
        """
        return [
            {
                "key": field.key,
                "label": field.label,
                "type": field.field_type,
                "searchable": field.searchable,
                "filterable": field.filterable,
                "options": field.options,
            }
            for field in self._supplier_fields
        ]

    def search_customers(
        self,
        conditions: list[QueryCondition],
        page: int = 1,
        page_size: int = 50,
        order_by: str | None = None,
        use_cache: bool = True,
    ) -> SearchResult:
        """
        执行客户高级搜索

        Args:
            conditions: 查询条件列表
            page: 页码
            page_size: 每页大小
            order_by: 排序字段
            use_cache: 是否使用缓存

        Returns:
            SearchResult: 搜索结果

        Raises:
            ValidationError: 查询条件验证失败
            BusinessLogicError: 业务逻辑错误
        """
        try:
            start_time = datetime.now()

            # 验证查询条件
            self._validate_conditions(conditions, "customer")

            # 检查缓存
            cache_key = self._generate_cache_key(
                "customer", conditions, page, page_size, order_by
            )
            if use_cache and cache_key in self._query_cache:
                cached_result, cached_time = self._query_cache[cache_key]
                if datetime.now() - cached_time < self._cache_ttl:
                    self._logger.debug(f"使用缓存结果: {cache_key}")
                    return cached_result

            # 构建查询
            query_builder = self._build_customer_query(conditions, order_by)

            # 执行查询
            data_sql, data_params = query_builder.paginate(page, page_size).build()
            count_sql, count_params = query_builder.build_count()

            # 获取数据
            data_rows = self._customer_dao.execute_complex_query(
                data_sql, tuple(data_params)
            )
            count_result = self._customer_dao.execute_complex_query(
                count_sql, tuple(count_params)
            )
            total_count = count_result[0]["count"] if count_result else 0

            # 转换数据格式
            data = [self._format_customer_row(row) for row in data_rows]

            # 计算查询时间
            query_time = (datetime.now() - start_time).total_seconds()

            # 创建结果
            result = SearchResult(data, total_count, page, page_size, query_time)

            # 缓存结果
            if use_cache:
                self._query_cache[cache_key] = (result, datetime.now())

            self._logger.info(
                f"客户搜索完成: {len(data)}条记录, 总计{total_count}条, "
                f"耗时{query_time:.3f}秒"
            )

            return result

        except Exception as e:
            self._logger.error(f"客户搜索失败: {e}")
            if isinstance(e, ValidationError | BusinessLogicError):
                raise
            raise BusinessLogicError(f"搜索执行失败: {e}") from e

    def search_suppliers(
        self,
        conditions: list[QueryCondition],
        page: int = 1,
        page_size: int = 50,
        order_by: str | None = None,
        use_cache: bool = True,
    ) -> SearchResult:
        """
        执行供应商高级搜索

        Args:
            conditions: 查询条件列表
            page: 页码
            page_size: 每页大小
            order_by: 排序字段
            use_cache: 是否使用缓存

        Returns:
            SearchResult: 搜索结果

        Raises:
            ValidationError: 查询条件验证失败
            BusinessLogicError: 业务逻辑错误
        """
        try:
            start_time = datetime.now()

            # 验证查询条件
            self._validate_conditions(conditions, "supplier")

            # 检查缓存
            cache_key = self._generate_cache_key(
                "supplier", conditions, page, page_size, order_by
            )
            if use_cache and cache_key in self._query_cache:
                cached_result, cached_time = self._query_cache[cache_key]
                if datetime.now() - cached_time < self._cache_ttl:
                    self._logger.debug(f"使用缓存结果: {cache_key}")
                    return cached_result

            # 构建查询
            query_builder = self._build_supplier_query(conditions, order_by)

            # 执行查询
            data_sql, data_params = query_builder.paginate(page, page_size).build()
            count_sql, count_params = query_builder.build_count()

            # 获取数据
            data_rows = self._supplier_dao.execute_complex_query(
                data_sql, tuple(data_params)
            )
            count_result = self._supplier_dao.execute_complex_query(
                count_sql, tuple(count_params)
            )
            total_count = count_result[0]["count"] if count_result else 0

            # 转换数据格式
            data = [self._format_supplier_row(row) for row in data_rows]

            # 计算查询时间
            query_time = (datetime.now() - start_time).total_seconds()

            # 创建结果
            result = SearchResult(data, total_count, page, page_size, query_time)

            # 缓存结果
            if use_cache:
                self._query_cache[cache_key] = (result, datetime.now())

            self._logger.info(
                f"供应商搜索完成: {len(data)}条记录, 总计{total_count}条, "
                f"耗时{query_time:.3f}秒"
            )

            return result

        except Exception as e:
            self._logger.error(f"供应商搜索失败: {e}")
            if isinstance(e, ValidationError | BusinessLogicError):
                raise
            raise BusinessLogicError(f"搜索执行失败: {e}") from e

    def _validate_conditions(
        self, conditions: list[QueryCondition], entity_type: str
    ) -> None:
        """
        验证查询条件

        Args:
            conditions: 查询条件列表
            entity_type: 实体类型 (customer/supplier)

        Raises:
            ValidationError: 验证失败
        """
        if not conditions:
            raise ValidationError("查询条件不能为空")

        # 获取有效字段
        valid_fields = (
            self._customer_fields
            if entity_type == "customer"
            else self._supplier_fields
        )
        valid_field_keys = {field.key for field in valid_fields}

        for condition in conditions:
            # 验证字段名
            if condition.field not in valid_field_keys:
                raise ValidationError(f"无效的搜索字段: {condition.field}")

            # 验证操作符
            if condition.operator not in [op.value for op in ComparisonOperator]:
                raise ValidationError(f"无效的操作符: {condition.operator}")

            # 验证逻辑操作符
            if condition.logic not in ["AND", "OR", "NOT"]:
                raise ValidationError(f"无效的逻辑操作符: {condition.logic}")

            # 验证值
            if (
                condition.operator not in ["IS NULL", "IS NOT NULL"]
                and condition.value is None
            ):
                raise ValidationError(f"字段 {condition.field} 的值不能为空")

    def _build_customer_query(
        self, conditions: list[QueryCondition], order_by: str | None = None
    ) -> QueryBuilder:
        """
        构建客户查询

        Args:
            conditions: 查询条件列表
            order_by: 排序字段

        Returns:
            QueryBuilder: 查询构建器
        """
        builder = QueryBuilder("customers")

        # 添加基本字段
        builder.select(
            "customers.id",
            "customers.name",
            "customers.phone",
            "customers.email",
            "customers.address",
            "customers.contact_person",
            "customers.customer_type_id",
            "customers.created_at",
            "customers.updated_at",
        )

        # 检查是否需要关联查询
        needs_order_join = any(
            condition.field in ["total_orders", "total_amount", "last_order_date"]
            for condition in conditions
        )

        if needs_order_join:
            builder.join("orders", "customers.id = orders.customer_id", "LEFT")
            builder.select(
                "COUNT(orders.id) as total_orders",
                "COALESCE(SUM(orders.amount), 0) as total_amount",
                "MAX(orders.order_date) as last_order_date",
            )
            builder.group_by("customers.id")

        # 添加查询条件
        for i, condition in enumerate(conditions):
            logical_op = (
                LogicalOperator.AND if i == 0 else LogicalOperator(condition.logic)
            )
            self._add_condition_to_builder(builder, condition, logical_op, "customer")

        # 添加排序
        if order_by:
            if " " in order_by:
                field, direction = order_by.split(" ", 1)
                builder.order_by(field, direction)
            else:
                builder.order_by(order_by)
        else:
            builder.order_by("customers.updated_at", "DESC")

        return builder

    def _build_supplier_query(
        self, conditions: list[QueryCondition], order_by: str | None = None
    ) -> QueryBuilder:
        """
        构建供应商查询

        Args:
            conditions: 查询条件列表
            order_by: 排序字段

        Returns:
            QueryBuilder: 查询构建器
        """
        builder = QueryBuilder("suppliers")

        # 添加基本字段
        builder.select(
            "suppliers.id",
            "suppliers.name",
            "suppliers.phone",
            "suppliers.email",
            "suppliers.address",
            "suppliers.contact_person",
            "suppliers.supplier_type_id",
            "suppliers.quality_rating",
            "suppliers.created_at",
            "suppliers.updated_at",
        )

        # 添加查询条件
        for i, condition in enumerate(conditions):
            logical_op = (
                LogicalOperator.AND if i == 0 else LogicalOperator(condition.logic)
            )
            self._add_condition_to_builder(builder, condition, logical_op, "supplier")

        # 添加排序
        if order_by:
            if " " in order_by:
                field, direction = order_by.split(" ", 1)
                builder.order_by(field, direction)
            else:
                builder.order_by(order_by)
        else:
            builder.order_by("suppliers.updated_at", "DESC")

        return builder

    def _add_condition_to_builder(
        self,
        builder: QueryBuilder,
        condition: QueryCondition,
        logical_op: LogicalOperator,
        entity_type: str,
    ) -> None:
        """
        将查询条件添加到构建器

        Args:
            builder: 查询构建器
            condition: 查询条件
            logical_op: 逻辑操作符
            entity_type: 实体类型
        """
        # 获取字段信息
        fields = (
            self._customer_fields
            if entity_type == "customer"
            else self._supplier_fields
        )
        field_info = next((f for f in fields if f.key == condition.field), None)

        if not field_info:
            return

        # 构建完整字段名
        if field_info.table_name == "customers" or field_info.table_name == "suppliers":
            full_field_name = f"{field_info.table_name}.{field_info.column_name}"
        else:
            full_field_name = field_info.column_name

        # 转换操作符
        operator = ComparisonOperator(condition.operator)

        # 处理特殊值转换
        value = condition.value
        if field_info.field_type == "date" and isinstance(value, str):
            # 日期字符串转换
            with contextlib.suppress(ValueError):
                datetime.strptime(value, "%Y-%m-%d")

        elif (
            field_info.field_type == "text"
            and operator in [ComparisonOperator.LIKE, ComparisonOperator.NOT_LIKE]
            and not value.startswith("%")
            and not value.endswith("%")
        ):
            # 文本模糊匹配
            value = f"%{value}%"

        # 添加条件
        builder.where(full_field_name, operator, value, logical_op)

    def _format_customer_row(self, row: dict[str, Any]) -> dict[str, Any]:
        """
        格式化客户数据行

        Args:
            row: 原始数据行

        Returns:
            Dict[str, Any]: 格式化后的数据
        """
        return {
            "id": row.get("id"),
            "name": row.get("name", ""),
            "phone": row.get("phone", ""),
            "email": row.get("email", ""),
            "address": row.get("address", ""),
            "contact_person": row.get("contact_person", ""),
            "customer_type_id": row.get("customer_type_id"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
            # 统计字段
            "total_orders": row.get("total_orders", 0),
            "total_amount": row.get("total_amount", 0.0),
            "last_order_date": row.get("last_order_date"),
        }

    def _format_supplier_row(self, row: dict[str, Any]) -> dict[str, Any]:
        """
        格式化供应商数据行

        Args:
            row: 原始数据行

        Returns:
            Dict[str, Any]: 格式化后的数据
        """
        return {
            "id": row.get("id"),
            "name": row.get("name", ""),
            "phone": row.get("phone", ""),
            "email": row.get("email", ""),
            "address": row.get("address", ""),
            "contact_person": row.get("contact_person", ""),
            "supplier_type_id": row.get("supplier_type_id"),
            "quality_rating": row.get("quality_rating", 0),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }

    def _generate_cache_key(
        self,
        entity_type: str,
        conditions: list[QueryCondition],
        page: int,
        page_size: int,
        order_by: str | None,
    ) -> str:
        """
        生成缓存键

        Args:
            entity_type: 实体类型
            conditions: 查询条件
            page: 页码
            page_size: 每页大小
            order_by: 排序字段

        Returns:
            str: 缓存键
        """
        import hashlib

        # 构建缓存键字符串
        key_parts = [
            entity_type,
            str(page),
            str(page_size),
            order_by or "",
        ]

        # 添加条件信息
        for condition in conditions:
            key_parts.extend(
                [
                    condition.field,
                    condition.operator,
                    str(condition.value),
                    condition.logic,
                ]
            )

        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def clear_cache(self) -> None:
        """清除查询缓存"""
        self._query_cache.clear()
        self._logger.debug("查询缓存已清除")

    def get_cache_stats(self) -> dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            Dict[str, Any]: 缓存统计信息
        """
        now = datetime.now()
        valid_entries = 0
        expired_entries = 0

        for _, cached_time in self._query_cache.values():
            if now - cached_time < self._cache_ttl:
                valid_entries += 1
            else:
                expired_entries += 1

        return {
            "total_entries": len(self._query_cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_ttl_minutes": self._cache_ttl.total_seconds() / 60,
        }
