"""Tests for transfunctions module."""

from datetime import datetime
from decimal import Decimal
from typing import Any

# Import transfunctions
from transfunctions import (
    calculate_customer_value_score,
    calculate_quote_total,
    format_currency,
    format_date,
    format_phone,
    validate_customer_data,
    validate_supplier_data,
)


class TestBusinessValidation:
    """Test business validation functions."""

    def test_validate_customer_data_success(self, sample_customer_data: dict[str, Any]):
        """Test successful customer data validation."""
        result = validate_customer_data(sample_customer_data)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_customer_data_missing_name(self):
        """Test customer data validation with missing name."""
        data = {"phone": "13812345678"}
        result = validate_customer_data(data)
        assert result.is_valid is False
        assert any("name" in error for error in result.errors)

    def test_validate_customer_data_invalid_phone(self):
        """Test customer data validation with invalid phone."""
        data = {"name": "测试公司", "phone": "invalid"}
        result = validate_customer_data(data)
        assert result.is_valid is False
        assert any("电话号码格式不正确" in error for error in result.errors)

    def test_validate_supplier_data_success(self):
        """Test successful supplier data validation."""
        data = {
            "name": "测试供应商",
            "contact_person": "张经理",
            "phone": "13812345678",
            "email": "test@example.com",
        }
        result = validate_supplier_data(data)
        assert result.is_valid is True
        assert len(result.errors) == 0


class TestDataFormatting:
    """Test data formatting functions."""

    def test_format_currency(self):
        """Test currency formatting."""
        assert format_currency(12345.67) == "¥12,345.67"
        assert format_currency(0) == "¥0.00"
        assert format_currency(1000) == "¥1,000.00"

    def test_format_phone_number(self):
        """Test phone number formatting."""
        assert format_phone("13812345678") == "138-1234-5678"
        assert format_phone("") == ""
        assert format_phone("invalid") == "invalid"

    def test_format_date(self):
        """Test date formatting."""
        test_date = datetime(2024, 1, 15, 10, 30, 0)
        assert "2024-01-15" in format_date(test_date)

        # Test Chinese format
        chinese_format = format_date(test_date, "%Y年%m月%d日")
        assert "2024年01月15日" in chinese_format


class TestBusinessCalculations:
    """Test business calculation functions."""

    def test_calculate_quote_total(self, sample_quote_data: dict[str, Any]):
        """Test quote total calculation."""
        items = sample_quote_data["items"]
        result = calculate_quote_total(items)

        # Check that result contains expected keys
        assert "total_amount" in result
        assert "subtotal_before_discount" in result
        assert "tax_amount" in result

        # Verify the result is a Decimal
        assert isinstance(result["total_amount"], Decimal)
        assert result["total_amount"] > 0

    def test_calculate_customer_value_score(self):
        """Test customer value score calculation."""
        customer_data = {
            "id": 1,
            "created_at": "2023-01-01",
            "level": "VIP",
            "industry": "制造业",
        }

        transaction_history = [
            {"amount": 10000, "date": "2024-12-01"},
            {"amount": 15000, "date": "2024-11-01"},
        ]

        interaction_history = [
            {"type": "call", "date": "2024-12-15"},
            {"type": "meeting", "date": "2024-12-10"},
        ]

        metrics = calculate_customer_value_score(
            customer_data, transaction_history, interaction_history
        )

        assert 0 <= metrics.total_score <= 100
        assert isinstance(metrics.total_score, float)
        assert metrics.transaction_value >= 0
        assert metrics.interaction_score >= 0
        assert metrics.loyalty_score >= 0
        assert metrics.potential_score >= 0


class TestCRUDTemplates:
    """Test CRUD template functions."""

    def test_crud_template_basic_functionality(self):
        """Test basic CRUD template functionality."""

        from transfunctions.data_operations import create_crud_template

        # Mock database manager
        class MockDBManager:
            def execute_query(self, sql, params):
                return [{"id": 1, "name": "Test Item"}]

            def execute_insert(self, sql, params):
                return 1

            def execute_update(self, sql, params):
                return 1

            def execute_delete(self, sql, params):
                return 1

        db_manager = MockDBManager()
        crud_template = create_crud_template("test_table", db_manager)

        # Test that the template was created successfully
        assert crud_template.table_name == "test_table"
        assert crud_template.db_manager is db_manager


class TestSearchTemplates:
    """Test search template functions."""

    def test_search_functionality(self):
        """Test search functionality."""
        # This is a basic test to ensure the search functions are importable
        from transfunctions.data_operations import build_search_query

        # Test basic query building
        sql, params = build_search_query(
            table_name="customers", search_fields=["name", "phone"], search_term="test"
        )
        assert "customers" in sql
        assert "name" in sql or "phone" in sql
        assert isinstance(params, list)
