"""
MiniCRM 高级搜索服务测试

测试高级搜索功能的各个方面，包括：
- 查询条件验证
- 复杂查询构建
- 搜索结果处理
- 缓存机制
- 性能测试

设计原则：
- 全面覆盖搜索功能
- 测试各种查询条件组合
- 验证错误处理
- 性能基准测试
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from minicrm.core.exceptions import BusinessLogicError, ValidationError
from minicrm.services.advanced_search_service import (
    AdvancedSearchService,
    SearchField,
    SearchResult,
)
from minicrm.ui.components.advanced_search_dialog import QueryCondition


class TestAdvancedSearchService(unittest.TestCase):
    """高级搜索服务测试类"""

    def setUp(self):
        """测试准备"""
        # 创建模拟的DAO对象
        self.mock_customer_dao = Mock()
        self.mock_supplier_dao = Mock()

        # 创建搜索服务
        self.search_service = AdvancedSearchService(
            self.mock_customer_dao, self.mock_supplier_dao
        )

    def test_get_customer_search_fields(self):
        """测试获取客户搜索字段配置"""
        fields = self.search_service.get_customer_search_fields()

        # 验证返回的字段配置
        self.assertIsInstance(fields, list)
        self.assertGreater(len(fields), 0)

        # 验证字段结构
        for field in fields:
            self.assertIn("key", field)
            self.assertIn("label", field)
            self.assertIn("type", field)
            self.assertIn("searchable", field)
            self.assertIn("filterable", field)

        # 验证必要字段存在
        field_keys = {field["key"] for field in fields}
        expected_keys = {"name", "phone", "email", "address", "contact_person"}
        self.assertTrue(expected_keys.issubset(field_keys))

    def test_get_supplier_search_fields(self):
        """测试获取供应商搜索字段配置"""
        fields = self.search_service.get_supplier_search_fields()

        # 验证返回的字段配置
        self.assertIsInstance(fields, list)
        self.assertGreater(len(fields), 0)

        # 验证必要字段存在
        field_keys = {field["key"] for field in fields}
        expected_keys = {"name", "phone", "email", "quality_rating"}
        self.assertTrue(expected_keys.issubset(field_keys))

    def test_validate_conditions_success(self):
        """测试查询条件验证成功"""
        conditions = [
            QueryCondition("name", "LIKE", "测试公司", "AND"),
            QueryCondition("phone", "=", "13812345678", "OR"),
        ]

        # 应该不抛出异常
        try:
            self.search_service._validate_conditions(conditions, "customer")
        except Exception as e:
            self.fail(f"验证应该成功，但抛出了异常: {e}")

    def test_validate_conditions_empty(self):
        """测试空查询条件验证"""
        with self.assertRaises(ValidationError) as context:
            self.search_service._validate_conditions([], "customer")

        self.assertIn("查询条件不能为空", str(context.exception))

    def test_validate_conditions_invalid_field(self):
        """测试无效字段验证"""
        conditions = [
            QueryCondition("invalid_field", "=", "value", "AND"),
        ]

        with self.assertRaises(ValidationError) as context:
            self.search_service._validate_conditions(conditions, "customer")

        self.assertIn("无效的搜索字段", str(context.exception))

    def test_validate_conditions_invalid_operator(self):
        """测试无效操作符验证"""
        conditions = [
            QueryCondition("name", "INVALID_OP", "value", "AND"),
        ]

        with self.assertRaises(ValidationError) as context:
            self.search_service._validate_conditions(conditions, "customer")

        self.assertIn("无效的操作符", str(context.exception))

    def test_validate_conditions_invalid_logic(self):
        """测试无效逻辑操作符验证"""
        conditions = [
            QueryCondition("name", "=", "value", "INVALID_LOGIC"),
        ]

        with self.assertRaises(ValidationError) as context:
            self.search_service._validate_conditions(conditions, "customer")

        self.assertIn("无效的逻辑操作符", str(context.exception))

    def test_validate_conditions_missing_value(self):
        """测试缺失值验证"""
        conditions = [
            QueryCondition("name", "=", None, "AND"),
        ]

        with self.assertRaises(ValidationError) as context:
            self.search_service._validate_conditions(conditions, "customer")

        self.assertIn("值不能为空", str(context.exception))

    def test_validate_conditions_null_operators(self):
        """测试NULL操作符不需要值"""
        conditions = [
            QueryCondition("name", "IS NULL", None, "AND"),
            QueryCondition("phone", "IS NOT NULL", None, "OR"),
        ]

        # 应该不抛出异常
        try:
            self.search_service._validate_conditions(conditions, "customer")
        except Exception as e:
            self.fail(f"NULL操作符验证应该成功，但抛出了异常: {e}")

    @patch("minicrm.services.advanced_search_service.datetime")
    def test_search_customers_success(self, mock_datetime):
        """测试客户搜索成功"""
        # 设置时间模拟
        mock_now = datetime(2025, 1, 15, 10, 30, 0)
        mock_datetime.now.return_value = mock_now

        # 准备测试数据
        conditions = [
            QueryCondition("name", "LIKE", "%测试%", "AND"),
        ]

        mock_data = [
            {
                "id": 1,
                "name": "测试公司1",
                "phone": "13812345678",
                "email": "test1@example.com",
                "address": "测试地址1",
                "contact_person": "张三",
                "customer_type_id": 1,
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-15T10:00:00",
            }
        ]

        mock_count_result = [{"count": 1}]

        # 设置DAO模拟
        self.mock_customer_dao.execute_complex_query.side_effect = [
            mock_data,  # 数据查询结果
            mock_count_result,  # 计数查询结果
        ]

        # 执行搜索
        result = self.search_service.search_customers(conditions)

        # 验证结果
        self.assertIsInstance(result, SearchResult)
        self.assertEqual(result.total_count, 1)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0]["name"], "测试公司1")
        self.assertEqual(result.page, 1)
        self.assertEqual(result.page_size, 50)
        self.assertGreaterEqual(result.query_time, 0)

        # 验证DAO调用
        self.assertEqual(self.mock_customer_dao.execute_complex_query.call_count, 2)

    def test_search_customers_with_pagination(self):
        """测试客户搜索分页"""
        conditions = [
            QueryCondition("name", "LIKE", "%测试%", "AND"),
        ]

        mock_data = []
        mock_count_result = [{"count": 100}]

        self.mock_customer_dao.execute_complex_query.side_effect = [
            mock_data,
            mock_count_result,
        ]

        # 执行搜索（第2页，每页20条）
        result = self.search_service.search_customers(conditions, page=2, page_size=20)

        # 验证分页信息
        self.assertEqual(result.page, 2)
        self.assertEqual(result.page_size, 20)
        self.assertEqual(result.total_count, 100)
        self.assertEqual(result.total_pages, 5)

    @patch("minicrm.services.advanced_search_service.datetime")
    def test_search_suppliers_success(self, mock_datetime):
        """测试供应商搜索成功"""
        # 设置时间模拟
        mock_now = datetime(2025, 1, 15, 10, 30, 0)
        mock_datetime.now.return_value = mock_now

        conditions = [
            QueryCondition("quality_rating", ">=", 4.0, "AND"),
        ]

        mock_data = [
            {
                "id": 1,
                "name": "优质供应商",
                "phone": "13987654321",
                "quality_rating": 4.5,
            }
        ]

        mock_count_result = [{"count": 1}]

        self.mock_supplier_dao.execute_complex_query.side_effect = [
            mock_data,
            mock_count_result,
        ]

        # 执行搜索
        result = self.search_service.search_suppliers(conditions)

        # 验证结果
        self.assertIsInstance(result, SearchResult)
        self.assertEqual(result.total_count, 1)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0]["name"], "优质供应商")

    def test_search_with_dao_error(self):
        """测试DAO错误处理"""
        conditions = [
            QueryCondition("name", "=", "测试", "AND"),
        ]

        # 设置DAO抛出异常
        self.mock_customer_dao.execute_complex_query.side_effect = Exception(
            "数据库错误"
        )

        # 执行搜索应该抛出业务逻辑异常
        with self.assertRaises(BusinessLogicError) as context:
            self.search_service.search_customers(conditions)

        self.assertIn("搜索执行失败", str(context.exception))

    def test_cache_functionality(self):
        """测试缓存功能"""
        conditions = [
            QueryCondition("name", "=", "测试", "AND"),
        ]

        mock_data = [{"id": 1, "name": "测试公司"}]
        mock_count_result = [{"count": 1}]

        self.mock_customer_dao.execute_complex_query.side_effect = [
            mock_data,
            mock_count_result,
        ]

        # 第一次搜索
        result1 = self.search_service.search_customers(conditions, use_cache=True)

        # 重置DAO模拟
        self.mock_customer_dao.reset_mock()

        # 第二次搜索（应该使用缓存）
        result2 = self.search_service.search_customers(conditions, use_cache=True)

        # 验证第二次没有调用DAO
        self.mock_customer_dao.execute_complex_query.assert_not_called()

        # 验证结果一致
        self.assertEqual(result1.total_count, result2.total_count)

    def test_cache_expiry(self):
        """测试缓存过期"""
        # 修改缓存TTL为很短的时间
        original_ttl = self.search_service._cache_ttl
        self.search_service._cache_ttl = timedelta(milliseconds=1)

        try:
            conditions = [
                QueryCondition("name", "=", "测试", "AND"),
            ]

            mock_data = [{"id": 1, "name": "测试公司"}]
            mock_count_result = [{"count": 1}]

            self.mock_customer_dao.execute_complex_query.side_effect = [
                mock_data,
                mock_count_result,
                mock_data,  # 第二次查询
                mock_count_result,
            ]

            # 第一次搜索
            self.search_service.search_customers(conditions, use_cache=True)

            # 等待缓存过期
            import time

            time.sleep(0.002)

            # 第二次搜索（缓存已过期，应该重新查询）
            self.search_service.search_customers(conditions, use_cache=True)

            # 验证调用了两次DAO
            self.assertEqual(self.mock_customer_dao.execute_complex_query.call_count, 4)

        finally:
            # 恢复原始TTL
            self.search_service._cache_ttl = original_ttl

    def test_clear_cache(self):
        """测试清除缓存"""
        conditions = [
            QueryCondition("name", "=", "测试", "AND"),
        ]

        mock_data = [{"id": 1, "name": "测试公司"}]
        mock_count_result = [{"count": 1}]

        self.mock_customer_dao.execute_complex_query.side_effect = [
            mock_data,
            mock_count_result,
            mock_data,  # 清除缓存后的查询
            mock_count_result,
        ]

        # 第一次搜索
        self.search_service.search_customers(conditions, use_cache=True)

        # 清除缓存
        self.search_service.clear_cache()

        # 第二次搜索（缓存已清除，应该重新查询）
        self.search_service.search_customers(conditions, use_cache=True)

        # 验证调用了两次DAO
        self.assertEqual(self.mock_customer_dao.execute_complex_query.call_count, 4)

    def test_get_cache_stats(self):
        """测试获取缓存统计"""
        # 初始状态
        stats = self.search_service.get_cache_stats()
        self.assertEqual(stats["total_entries"], 0)
        self.assertEqual(stats["valid_entries"], 0)

        # 添加一些缓存条目
        conditions = [
            QueryCondition("name", "=", "测试", "AND"),
        ]

        mock_data = [{"id": 1, "name": "测试公司"}]
        mock_count_result = [{"count": 1}]

        self.mock_customer_dao.execute_complex_query.side_effect = [
            mock_data,
            mock_count_result,
        ]

        # 执行搜索以创建缓存条目
        self.search_service.search_customers(conditions, use_cache=True)

        # 检查统计
        stats = self.search_service.get_cache_stats()
        self.assertEqual(stats["total_entries"], 1)
        self.assertEqual(stats["valid_entries"], 1)
        self.assertEqual(stats["expired_entries"], 0)

    def test_complex_query_conditions(self):
        """测试复杂查询条件"""
        conditions = [
            QueryCondition("name", "LIKE", "%公司%", "AND"),
            QueryCondition("phone", "IS NOT NULL", None, "AND"),
            QueryCondition(
                "created_at", "BETWEEN", ["2025-01-01", "2025-01-31"], "AND"
            ),
            QueryCondition("customer_type_id", "IN", [1, 2, 3], "OR"),
        ]

        mock_data = []
        mock_count_result = [{"count": 0}]

        self.mock_customer_dao.execute_complex_query.side_effect = [
            mock_data,
            mock_count_result,
        ]

        # 执行搜索
        result = self.search_service.search_customers(conditions)

        # 验证查询被执行
        self.assertEqual(self.mock_customer_dao.execute_complex_query.call_count, 2)

        # 验证结果
        self.assertIsInstance(result, SearchResult)

    def test_format_customer_row(self):
        """测试客户数据行格式化"""
        raw_row = {
            "id": 1,
            "name": "测试公司",
            "phone": "13812345678",
            "email": "test@example.com",
            "address": "测试地址",
            "contact_person": "张三",
            "customer_type_id": 1,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-15T10:00:00",
            "total_orders": 5,
            "total_amount": 10000.50,
            "last_order_date": "2025-01-10",
        }

        formatted_row = self.search_service._format_customer_row(raw_row)

        # 验证格式化结果
        self.assertEqual(formatted_row["id"], 1)
        self.assertEqual(formatted_row["name"], "测试公司")
        self.assertEqual(formatted_row["phone"], "13812345678")
        self.assertEqual(formatted_row["total_orders"], 5)
        self.assertEqual(formatted_row["total_amount"], 10000.50)

    def test_format_supplier_row(self):
        """测试供应商数据行格式化"""
        raw_row = {
            "id": 1,
            "name": "测试供应商",
            "phone": "13987654321",
            "quality_rating": 4.5,
        }

        formatted_row = self.search_service._format_supplier_row(raw_row)

        # 验证格式化结果
        self.assertEqual(formatted_row["id"], 1)
        self.assertEqual(formatted_row["name"], "测试供应商")
        self.assertEqual(formatted_row["quality_rating"], 4.5)

    def test_generate_cache_key(self):
        """测试缓存键生成"""
        conditions = [
            QueryCondition("name", "=", "测试", "AND"),
        ]

        key1 = self.search_service._generate_cache_key(
            "customer", conditions, 1, 50, None
        )
        key2 = self.search_service._generate_cache_key(
            "customer", conditions, 1, 50, None
        )
        key3 = self.search_service._generate_cache_key(
            "customer",
            conditions,
            2,
            50,
            None,  # 不同页码
        )

        # 相同参数应该生成相同的键
        self.assertEqual(key1, key2)

        # 不同参数应该生成不同的键
        self.assertNotEqual(key1, key3)

        # 键应该是字符串
        self.assertIsInstance(key1, str)


class TestSearchField(unittest.TestCase):
    """搜索字段测试类"""

    def test_search_field_creation(self):
        """测试搜索字段创建"""
        field = SearchField(
            key="name",
            label="客户名称",
            field_type="text",
            table_name="customers",
            column_name="name",
            searchable=True,
            filterable=True,
            options=[{"label": "选项1", "value": "value1"}],
        )

        self.assertEqual(field.key, "name")
        self.assertEqual(field.label, "客户名称")
        self.assertEqual(field.field_type, "text")
        self.assertEqual(field.table_name, "customers")
        self.assertEqual(field.column_name, "name")
        self.assertTrue(field.searchable)
        self.assertTrue(field.filterable)
        self.assertEqual(len(field.options), 1)


class TestSearchResult(unittest.TestCase):
    """搜索结果测试类"""

    def test_search_result_creation(self):
        """测试搜索结果创建"""
        data = [{"id": 1, "name": "测试"}]
        result = SearchResult(
            data=data,
            total_count=100,
            page=2,
            page_size=20,
            query_time=0.5,
        )

        self.assertEqual(result.data, data)
        self.assertEqual(result.total_count, 100)
        self.assertEqual(result.page, 2)
        self.assertEqual(result.page_size, 20)
        self.assertEqual(result.query_time, 0.5)
        self.assertEqual(result.total_pages, 5)  # 100 / 20 = 5

    def test_search_result_total_pages_calculation(self):
        """测试总页数计算"""
        # 整除情况
        result1 = SearchResult([], 100, 1, 20, 0.0)
        self.assertEqual(result1.total_pages, 5)

        # 有余数情况
        result2 = SearchResult([], 101, 1, 20, 0.0)
        self.assertEqual(result2.total_pages, 6)

        # 空结果
        result3 = SearchResult([], 0, 1, 20, 0.0)
        self.assertEqual(result3.total_pages, 0)


if __name__ == "__main__":
    unittest.main()
