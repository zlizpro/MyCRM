"""Pytest configuration and fixtures for MiniCRM tests."""

from pathlib import Path
import sys
import tkinter as tk
from unittest.mock import Mock

import pytest


# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def tkapp():
    """Create a tkinter root instance for testing TTK widgets.

    This fixture ensures that there's always a tkinter root instance
    available for TTK widget tests.

    Returns:
        tk.Tk: The tkinter root instance
    """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    yield root
    try:
        root.destroy()
    except tk.TclError:
        pass  # 窗口已经被销毁


@pytest.fixture
def sample_customer_data() -> dict:
    """Provide sample customer data for testing.

    Returns:
        dict: Sample customer data
    """
    return {
        "name": "测试公司",
        "phone": "13812345678",
        "email": "test@example.com",
        "company": "测试有限公司",
        "address": "北京市朝阳区测试街道123号",
    }


@pytest.fixture
def sample_supplier_data() -> dict:
    """Provide sample supplier data for testing.

    Returns:
        dict: Sample supplier data
    """
    return {
        "name": "测试供应商",
        "contact_person": "张经理",
        "phone": "13987654321",
        "email": "supplier@example.com",
        "address": "上海市浦东新区供应商路456号",
    }


@pytest.fixture
def sample_quote_data() -> dict:
    """Provide sample quote data for testing.

    Returns:
        dict: Sample quote data
    """
    return {
        "customer_id": 1,
        "quote_number": "Q2024001",
        "items": [
            {
                "product_name": "产品A",
                "quantity": 10,
                "unit_price": 100.0,
                "description": "高质量产品A",
            },
            {
                "product_name": "产品B",
                "quantity": 5,
                "unit_price": 200.0,
                "description": "优质产品B",
            },
        ],
        "valid_until": "2024-12-31",
        "notes": "测试报价单",
    }


@pytest.fixture
def temp_database(tmp_path: Path) -> Path:
    """Create a temporary database file for testing.

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        Path: Path to temporary database file
    """
    return tmp_path / "test_minicrm.db"


@pytest.fixture
def mock_database_manager():
    """Provide a mock database manager for testing.

    Returns:
        Mock database manager instance
    """

    mock_db = Mock()
    mock_db.execute_query.return_value = []
    mock_db.execute_insert.return_value = 1
    mock_db.execute_update.return_value = True
    mock_db.execute_delete.return_value = True

    return mock_db


@pytest.fixture
def sample_service_ticket_data() -> dict:
    """Provide sample service ticket data for testing.

    Returns:
        dict: Sample service ticket data
    """
    return {
        "customer_id": 1,
        "ticket_number": "ST2024001",
        "title": "产品质量问题",
        "description": "客户反馈产品存在质量问题,需要及时处理",
        "priority": "高",
        "status": "待处理",
        "assigned_to": "张工程师",
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "ui: marks tests as UI tests (require display)")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add 'unit' marker to all tests by default
        if not any(
            marker.name in ["integration", "ui", "slow"]
            for marker in item.iter_markers()
        ):
            item.add_marker(pytest.mark.unit)

        # Add 'ui' marker to tests that use tkapp fixture
        if "tkapp" in item.fixturenames:
            item.add_marker(pytest.mark.ui)

        # Add 'integration' marker to tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
