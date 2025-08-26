"""增强版DAO集成测试.

测试客户、供应商、业务流程相关DAO的功能.
"""

from datetime import datetime
from pathlib import Path
import shutil
import tempfile
import unittest

from minicrm.core.exceptions import ValidationError
from minicrm.data.dao.enhanced_business_dao import (
    EnhancedContractDAO,
    EnhancedQuoteDAO,
    EnhancedServiceTicketDAO,
)
from minicrm.data.dao.enhanced_customer_dao import (
    EnhancedCustomerDAO,
    EnhancedCustomerTypeDAO,
)
from minicrm.data.dao.enhanced_supplier_dao import (
    EnhancedSupplierDAO,
    EnhancedSupplierTypeDAO,
)
from minicrm.data.database_manager_enhanced import create_database_manager


class TestEnhancedDAO(unittest.TestCase):
    """增强版DAO测试类."""

    def setUp(self):
        """测试准备."""
        # 创建临时数据库
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_dao.db"

        # 创建数据库管理器和DAO实例
        self.db_manager = create_database_manager(self.db_path)
        self.db_manager.initialize_database()

        # 创建DAO实例
        self.customer_dao = EnhancedCustomerDAO(self.db_manager)
        self.customer_type_dao = EnhancedCustomerTypeDAO(self.db_manager)
        self.supplier_dao = EnhancedSupplierDAO(self.db_manager)
        self.supplier_type_dao = EnhancedSupplierTypeDAO(self.db_manager)
        self.quote_dao = EnhancedQuoteDAO(self.db_manager)
        self.contract_dao = EnhancedContractDAO(self.db_manager)
        self.service_ticket_dao = EnhancedServiceTicketDAO(self.db_manager)

    def tearDown(self):
        """测试清理."""
        self.db_manager.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_customer_type_dao(self):
        """测试客户类型DAO."""
        # 创建客户类型
        type_data = {
            "name": "测试客户类型",
            "description": "这是一个测试客户类型",
            "color_code": "#FF0000",
        }

        type_id = self.customer_type_dao.create_customer_type(type_data)
        assert isinstance(type_id, int)
        assert type_id > 0

        # 获取客户类型
        retrieved_type = self.customer_type_dao.get_by_id(type_id)
        assert retrieved_type is not None
        assert retrieved_type["name"] == "测试客户类型"

        # 测试重复名称
        try:
            self.customer_type_dao.create_customer_type(type_data)
            assert False, "应该抛出ValidationError异常"
        except ValidationError:
            pass  # 预期的异常

        # 获取使用数量
        usage_count = self.customer_type_dao.get_customer_type_usage_count(type_id)
        assert usage_count == 0

        # 删除客户类型
        success = self.customer_type_dao.delete_customer_type(type_id)
        assert success

    def test_customer_dao(self):
        """测试客户DAO."""
        # 先创建客户类型
        type_data = {"name": "制造企业", "description": "制造类企业客户"}
        type_id = self.customer_type_dao.create_customer_type(type_data)

        # 创建客户
        customer_data = {
            "name": "测试客户公司",
            "phone": "13812345678",
            "email": "test@example.com",
            "company": "测试公司",
            "address": "测试地址",
            "customer_type_id": type_id,
            "level": "vip",
            "credit_limit": 100000.0,
        }

        customer_id = self.customer_dao.create_customer(customer_data)
        assert isinstance(customer_id, int)
        assert customer_id > 0

        # 获取客户
        retrieved_customer = self.customer_dao.get_by_id(customer_id)
        assert retrieved_customer is not None
        assert retrieved_customer["name"] == "测试客户公司"
        assert retrieved_customer["level"] == "vip"

        # 更新客户
        update_data = {"name": "更新后的客户公司", "level": "important"}
        success = self.customer_dao.update_customer(customer_id, update_data)
        assert success

        # 验证更新
        updated_customer = self.customer_dao.get_by_id(customer_id)
        assert updated_customer["name"] == "更新后的客户公司"
        assert updated_customer["level"] == "important"

        # 搜索客户
        search_results = self.customer_dao.search_customers(
            query="测试", page=1, page_size=10
        )
        assert "data" in search_results
        assert "pagination" in search_results
        assert len(search_results["data"]) > 0

        # 获取客户统计
        stats = self.customer_dao.get_customer_statistics()
        assert "total_customers" in stats
        assert "level_statistics" in stats
        assert stats["total_customers"] == 1

        # 更新客户等级
        success = self.customer_dao.update_customer_level(customer_id, "normal")
        assert success

        # 更新授信额度
        success = self.customer_dao.update_credit_limit(customer_id, 200000.0)
        assert success

        # 获取高价值客户
        high_value_customers = self.customer_dao.get_high_value_customers(50000.0)
        assert len(high_value_customers) == 1

        # 软删除客户
        success = self.customer_dao.delete(customer_id, soft_delete=True)
        assert success

        # 验证软删除
        deleted_customer = self.customer_dao.get_by_id(customer_id)
        assert deleted_customer is None

    def test_supplier_dao(self):
        """测试供应商DAO."""
        # 先创建供应商类型
        type_data = {"name": "板材供应商", "description": "提供板材产品的供应商"}
        type_id = self.supplier_type_dao.create_supplier_type(type_data)

        # 创建供应商
        supplier_data = {
            "name": "测试供应商",
            "contact_person": "张经理",
            "phone": "13987654321",
            "email": "supplier@example.com",
            "company": "测试供应商公司",
            "address": "供应商地址",
            "supplier_type_id": type_id,
            "level": "strategic",
            "business_license": "123456789",
        }

        supplier_id = self.supplier_dao.create_supplier(supplier_data)
        assert isinstance(supplier_id, int)
        assert supplier_id > 0

        # 获取供应商
        retrieved_supplier = self.supplier_dao.get_by_id(supplier_id)
        assert retrieved_supplier is not None
        assert retrieved_supplier["name"] == "测试供应商"
        assert retrieved_supplier["level"] == "strategic"

        # 搜索供应商
        search_results = self.supplier_dao.search_suppliers(
            query="测试", page=1, page_size=10
        )
        assert "data" in search_results
        assert len(search_results["data"]) > 0

        # 获取供应商统计
        stats = self.supplier_dao.get_supplier_statistics()
        assert "total_suppliers" in stats
        assert stats["total_suppliers"] == 1

    def test_quote_dao(self):
        """测试报价DAO."""
        # 先创建客户
        customer_data = {"name": "报价测试客户", "phone": "13812345678"}
        customer_id = self.customer_dao.create_customer(customer_data)

        # 创建报价
        quote_data = {
            "customer_id": customer_id,
            "quote_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "valid_until": "2025-02-19",
            "total_amount": 50000.0,
            "status": "draft",
            "notes": "测试报价",
        }

        quote_id = self.quote_dao.create_quote(quote_data)
        assert isinstance(quote_id, int)
        assert quote_id > 0

        # 获取报价
        retrieved_quote = self.quote_dao.get_by_id(quote_id)
        assert retrieved_quote is not None
        assert retrieved_quote["customer_id"] == customer_id
        assert retrieved_quote["quote_number"] is not None  # 应该自动生成

        # 获取客户报价
        customer_quotes = self.quote_dao.get_customer_quotes(customer_id)
        assert len(customer_quotes) == 1

        # 获取报价统计
        stats = self.quote_dao.get_quote_statistics()
        assert "total_quotes" in stats
        assert stats["total_quotes"] == 1

    def test_pagination(self):
        """测试分页功能."""
        # 创建多个客户
        for i in range(25):
            customer_data = {"name": f"客户{i + 1}", "phone": f"138{i:08d}"}
            self.customer_dao.create_customer(customer_data)

        # 测试分页搜索
        page1 = self.customer_dao.paginated_search(page=1, page_size=10)
        assert len(page1["data"]) == 10
        assert "pagination" in page1

        page2 = self.customer_dao.paginated_search(page=2, page_size=10)
        assert len(page2["data"]) == 10

        page3 = self.customer_dao.paginated_search(page=3, page_size=10)
        assert len(page3["data"]) == 5  # 剩余5个

        # 验证分页信息
        pagination = page1["pagination"]
        assert pagination["current_page"] == 1
        assert pagination["page_size"] == 10
        assert pagination["total_pages"] == 3
        assert pagination["total_count"] == 25

    def test_batch_operations(self):
        """测试批量操作."""
        # 批量插入客户
        customers_data = [
            {"name": f"批量客户{i}", "phone": f"139{i:08d}"} for i in range(5)
        ]

        customer_ids = self.customer_dao.batch_insert(customers_data)
        assert len(customer_ids) == 5

        # 批量更新
        updates = [(customer_id, {"level": "vip"}) for customer_id in customer_ids]

        success_count = self.customer_dao.batch_update(updates)
        assert success_count == 5

        # 验证更新结果
        for customer_id in customer_ids:
            customer = self.customer_dao.get_by_id(customer_id)
            assert customer["level"] == "vip"


if __name__ == "__main__":
    unittest.main()
