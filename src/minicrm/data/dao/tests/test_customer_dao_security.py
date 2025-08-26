"""客户DAO安全性测试.

测试enhanced_customer_dao.py中的SQL注入防护功能.
验证所有修复的安全漏洞已经得到有效防护.
"""

from unittest.mock import Mock

import pytest

from minicrm.core.exceptions import DatabaseError, ValidationError
from minicrm.data.dao.enhanced_customer_dao import (
    EnhancedCustomerDAO,
    EnhancedCustomerTypeDAO,
)
from minicrm.data.database_manager_enhanced import EnhancedDatabaseManager


class TestCustomerDAOSecurity:
    """客户DAO安全性测试类."""

    def setup_method(self):
        """测试前准备."""
        # 创建模拟的数据库管理器
        self.mock_db_manager = Mock(spec=EnhancedDatabaseManager)
        self.customer_dao = EnhancedCustomerDAO(self.mock_db_manager)
        self.customer_type_dao = EnhancedCustomerTypeDAO(self.mock_db_manager)

    def test_sql_injection_prevention_in_search(self):
        """测试搜索功能的SQL注入防护."""
        # 模拟恶意输入
        malicious_inputs = [
            "'; DROP TABLE customers; --",
            "' OR '1'='1",
            "'; INSERT INTO customers (name) VALUES ('hacked'); --",
            "' UNION SELECT * FROM customer_types --",
            "%'; DELETE FROM customers WHERE '1'='1",
        ]

        # 模拟正常的数据库返回
        self.mock_db_manager.execute_query.return_value = [{"count": 0}]

        for malicious_input in malicious_inputs:
            # 测试搜索功能不会被SQL注入攻击
            try:
                result = self.customer_dao.search_customers(
                    query=malicious_input, page=1, page_size=10
                )
                # 验证返回结果结构正确
                assert "data" in result
                assert "pagination" in result
                assert "total_count" in result

                # 验证调用了execute_query且参数是安全的
                assert self.mock_db_manager.execute_query.called

                # 获取最后一次调用的参数
                call_args = self.mock_db_manager.execute_query.call_args
                sql_query = call_args[0][0]
                sql_params = call_args[0][1]

                # 验证SQL语句结构安全(不包含恶意代码)
                assert "DROP" not in sql_query.upper()
                assert "DELETE" not in sql_query.upper()
                assert "INSERT" not in sql_query.upper()
                assert "UNION" not in sql_query.upper()

                # 验证恶意输入被作为参数传递,而不是直接拼接到SQL中
                assert malicious_input not in sql_query
                assert any(malicious_input in str(param) for param in sql_params)

            except (ValidationError, DatabaseError):
                # 如果抛出验证错误,这也是可接受的安全行为
                pass

    def test_table_name_validation(self):
        """测试表名验证功能."""
        # 测试恶意表名
        malicious_table_names = [
            "customers; DROP TABLE users; --",
            "customers UNION SELECT * FROM passwords",
            "../../../etc/passwd",
            "customers' OR '1'='1",
        ]

        # 这些恶意表名应该在SQL构建器中被拒绝
        from minicrm.core.sql_safety import SQLSafetyValidator

        for malicious_name in malicious_table_names:
            with pytest.raises(ValidationError):
                SQLSafetyValidator.validate_table_name(malicious_name)

    def test_column_name_validation(self):
        """测试列名验证功能."""
        from minicrm.core.sql_safety import SQLSafetyValidator

        # 测试有效的列名
        valid_columns = ["name", "phone", "email", "customer_type_id", "created_at"]
        for column in valid_columns:
            # 应该不抛出异常
            validated = SQLSafetyValidator.validate_column_name(column, "customers")
            assert validated == column

        # 测试无效的列名
        invalid_columns = [
            "name; DROP TABLE customers",
            "name' OR '1'='1",
            "../../../etc/passwd",
            "name UNION SELECT password FROM users",
            "invalid_column_name",  # 不在允许列表中
        ]

        for column in invalid_columns:
            with pytest.raises(ValidationError):
                SQLSafetyValidator.validate_column_name(column, "customers")

    def test_safe_where_clause_building(self):
        """测试安全WHERE子句构建."""
        from minicrm.core.sql_safety import SQLSafetyValidator

        # 测试正常条件
        conditions = {"name": "测试公司", "customer_type_id": 1, "level": "vip"}

        where_clause, params = SQLSafetyValidator.build_safe_where_clause(
            conditions, "customers"
        )

        # 验证WHERE子句结构
        assert "name = ?" in where_clause
        assert "customer_type_id = ?" in where_clause
        assert "level = ?" in where_clause
        assert " AND " in where_clause

        # 验证参数列表
        assert len(params) == 3
        assert "测试公司" in params
        assert 1 in params
        assert "vip" in params

        # 测试恶意条件
        malicious_conditions = {
            "name; DROP TABLE customers": "value",
            "name' OR '1'='1": "value",
        }

        with pytest.raises(ValidationError):
            SQLSafetyValidator.build_safe_where_clause(
                malicious_conditions, "customers"
            )

    def test_like_query_safety(self):
        """测试LIKE查询的安全性."""
        from minicrm.core.sql_safety import SQLSafetyValidator

        # 测试正常搜索
        search_columns = ["name", "company", "phone"]
        search_value = "测试公司"

        like_clause, params = SQLSafetyValidator.build_safe_like_conditions(
            search_columns, search_value, "customers"
        )

        # 验证LIKE子句结构
        assert "name LIKE ?" in like_clause
        assert "company LIKE ?" in like_clause
        assert "phone LIKE ?" in like_clause
        assert " OR " in like_clause

        # 验证参数
        assert len(params) == 3
        assert all("%测试公司%" in param for param in params)

        # 测试包含特殊字符的搜索值
        special_search_values = [
            "test%company",  # 包含LIKE通配符
            "test_company",  # 包含LIKE通配符
            "test\\company",  # 包含转义字符
            "'; DROP TABLE customers; --",  # SQL注入尝试
        ]

        for search_value in special_search_values:
            like_clause, params = SQLSafetyValidator.build_safe_like_conditions(
                search_columns, search_value, "customers"
            )

            # 验证特殊字符被正确转义
            for param in params:
                if "%" in search_value:
                    assert "\\%" in param
                if "_" in search_value:
                    assert "\\_" in param
                if "\\" in search_value:
                    assert "\\\\" in param

    def test_order_by_safety(self):
        """测试ORDER BY子句的安全性."""
        from minicrm.core.sql_safety import SQLSafetyValidator

        # 测试有效的排序
        valid_order_bys = [
            "name ASC",
            "created_at DESC",
            "customer_type_id",
            "level DESC",
        ]

        for order_by in valid_order_bys:
            safe_order_by = SQLSafetyValidator.build_safe_order_by(
                order_by, "customers"
            )
            assert safe_order_by == order_by or safe_order_by == f"{order_by} ASC"

        # 测试无效的排序
        invalid_order_bys = [
            "name; DROP TABLE customers",
            "name' OR '1'='1",
            "invalid_column ASC",
            "name INVALID_DIRECTION",
        ]

        for order_by in invalid_order_bys:
            with pytest.raises(ValidationError):
                SQLSafetyValidator.build_safe_order_by(order_by, "customers")

    def test_limit_offset_validation(self):
        """测试LIMIT和OFFSET参数验证."""
        from minicrm.core.sql_safety import SQLSafetyValidator

        # 测试有效值
        valid_limits = [10, 50, 100, 1000]
        valid_offsets = [0, 10, 100, 1000]

        for limit in valid_limits:
            for offset in valid_offsets:
                validated_limit, validated_offset = (
                    SQLSafetyValidator.validate_limit_offset(limit, offset)
                )
                assert validated_limit == limit
                assert validated_offset == offset

        # 测试无效值
        invalid_values = [-1, -10, "invalid", None, 20000]  # 包括过大的值

        for invalid_value in invalid_values:
            if invalid_value is None:
                continue  # None是允许的

            with pytest.raises(ValidationError):
                SQLSafetyValidator.validate_limit_offset(invalid_value, 0)

            with pytest.raises(ValidationError):
                SQLSafetyValidator.validate_limit_offset(10, invalid_value)

    def test_customer_statistics_security(self):
        """测试客户统计功能的安全性."""
        # 模拟数据库返回
        self.mock_db_manager.execute_query.return_value = [{"count": 10}]

        # 调用统计功能
        try:
            stats = self.customer_dao.get_customer_statistics()

            # 验证返回结构
            assert "total_customers" in stats
            assert "level_statistics" in stats
            assert "monthly_new_customers" in stats
            assert "total_credit_limit" in stats

            # 验证数据库调用使用了安全的SQL
            assert self.mock_db_manager.execute_query.called

            # 检查所有SQL调用都是安全的
            for call in self.mock_db_manager.execute_query.call_args_list:
                sql_query = call[0][0]
                # 验证表名是硬编码的,不是动态拼接的
                assert "customers" in sql_query
                # 验证没有危险的SQL关键字
                assert "DROP" not in sql_query.upper()
                assert "DELETE" not in sql_query.upper()
                assert "INSERT" not in sql_query.upper()

        except Exception as e:
            # 如果有异常,应该是预期的验证错误
            assert isinstance(e, (ValidationError, DatabaseError))

    def test_high_value_customers_security(self):
        """测试高价值客户查询的安全性."""
        # 模拟数据库返回
        self.mock_db_manager.execute_query.return_value = []

        # 测试正常调用
        result = self.customer_dao.get_high_value_customers(100000)
        assert isinstance(result, list)

        # 验证SQL调用安全性
        call_args = self.mock_db_manager.execute_query.call_args
        sql_query = call_args[0][0]
        sql_params = call_args[0][1]

        # 验证表名是安全的
        assert "customers" in sql_query
        # 验证参数化查询
        assert "credit_limit >= ?" in sql_query
        assert 100000 in sql_params

        # 测试恶意输入
        malicious_limits = [
            "100000; DROP TABLE customers",
            "100000' OR '1'='1",
        ]

        for malicious_limit in malicious_limits:
            # 这些应该在类型检查时失败,或者被安全处理
            try:
                self.customer_dao.get_high_value_customers(malicious_limit)
            except (TypeError, ValidationError, DatabaseError):
                # 预期的错误类型
                pass


class TestCustomerTypeDAOSecurity:
    """客户类型DAO安全性测试."""

    def setup_method(self):
        """测试前准备."""
        self.mock_db_manager = Mock(spec=EnhancedDatabaseManager)
        self.customer_type_dao = EnhancedCustomerTypeDAO(self.mock_db_manager)

    def test_customer_type_usage_count_security(self):
        """测试客户类型使用数量查询的安全性."""
        # 模拟数据库返回
        self.mock_db_manager.execute_query.return_value = [{"count": 5}]

        # 测试正常调用
        count = self.customer_type_dao.get_customer_type_usage_count(1)
        assert count == 5

        # 验证SQL调用安全性
        call_args = self.mock_db_manager.execute_query.call_args
        sql_query = call_args[0][0]
        sql_params = call_args[0][1]

        # 验证使用了参数化查询
        assert (
            "supplier_type_id = ?" in sql_query or "customer_type_id = ?" in sql_query
        )
        assert 1 in sql_params

        # 验证没有SQL注入风险
        assert "DROP" not in sql_query.upper()
        assert "DELETE" not in sql_query.upper()
        assert "INSERT" not in sql_query.upper()


if __name__ == "__main__":
    pytest.main([__file__])
