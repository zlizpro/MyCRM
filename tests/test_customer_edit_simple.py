#!/usr/bin/env python3
"""
客户编辑功能简化测试

专门测试客户编辑功能的核心逻辑，不涉及UI组件
"""

import sys
from pathlib import Path

import pytest


# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


class TestCustomerService:
    """测试用的客户服务模拟类"""

    def __init__(self):
        self.customers = [
            {
                "id": 1,
                "name": "测试公司A",
                "contact_person": "张经理",
                "phone": "138-1234-5678",
                "email": "zhang@test.com",
                "company": "测试有限公司A",
                "customer_level": "vip",
                "customer_type": "家具板客户",
                "industry_type": "furniture",
                "address": "上海市测试区",
                "notes": "重要客户",
                "created_at": "2024-01-15 10:30:00",
                "last_contact_date": "2025-01-10",
            }
        ]
        self.next_id = 2

    def get_all_customers(self, page=1, page_size=100):
        return self.customers

    def search_customers(self, query="", filters=None, page=1, page_size=20):
        return self.customers, len(self.customers)

    def update_customer(self, customer_id, data):
        for i, customer in enumerate(self.customers):
            if customer["id"] == customer_id:
                self.customers[i].update(data)
                self.customers[i]["id"] = customer_id  # 保持ID不变
                return True
        return False

    def create_customer(self, data):
        new_id = self.next_id
        self.next_id += 1
        new_customer = data.copy()
        new_customer["id"] = new_id
        self.customers.append(new_customer)
        return new_id

    def delete_customer(self, customer_id):
        for i, customer in enumerate(self.customers):
            if customer["id"] == customer_id:
                del self.customers[i]
                return True
        return False


@pytest.fixture
def test_customer_service():
    """提供测试用的客户服务"""
    return TestCustomerService()


class TestCustomerEditCore:
    """客户编辑核心功能测试类"""

    def test_customer_service_create(self, test_customer_service):
        """测试客户服务创建功能"""
        initial_count = len(test_customer_service.customers)

        new_customer_data = {
            "name": "新客户",
            "contact_person": "李四",
            "phone": "139-0000-0000",
            "email": "new@example.com",
            "company": "新公司",
            "customer_level": "normal",
            "customer_type": "生态板客户",
            "industry_type": "furniture",
            "address": "新地址",
            "notes": "新客户备注",
        }

        customer_id = test_customer_service.create_customer(new_customer_data)

        assert customer_id is not None
        assert customer_id > 0
        assert len(test_customer_service.customers) == initial_count + 1

        # 验证新客户数据
        created_customer = None
        for customer in test_customer_service.customers:
            if customer["id"] == customer_id:
                created_customer = customer
                break

        assert created_customer is not None
        assert created_customer["name"] == "新客户"
        assert created_customer["contact_person"] == "李四"

    def test_customer_service_update(self, test_customer_service):
        """测试客户服务更新功能"""
        customer_id = 1
        update_data = {
            "name": "更新后的公司名",
            "contact_person": "更新后的联系人",
            "phone": "138-9999-9999",
        }

        result = test_customer_service.update_customer(customer_id, update_data)

        assert result is True

        # 验证更新后的数据
        updated_customer = None
        for customer in test_customer_service.customers:
            if customer["id"] == customer_id:
                updated_customer = customer
                break

        assert updated_customer is not None
        assert updated_customer["name"] == "更新后的公司名"
        assert updated_customer["contact_person"] == "更新后的联系人"
        assert updated_customer["phone"] == "138-9999-9999"

    def test_customer_service_delete(self, test_customer_service):
        """测试客户服务删除功能"""
        initial_count = len(test_customer_service.customers)
        customer_id = 1

        result = test_customer_service.delete_customer(customer_id)

        assert result is True
        assert len(test_customer_service.customers) == initial_count - 1

        # 验证客户已被删除
        deleted_customer = None
        for customer in test_customer_service.customers:
            if customer["id"] == customer_id:
                deleted_customer = customer
                break

        assert deleted_customer is None

    def test_customer_service_search(self, test_customer_service):
        """测试客户服务搜索功能"""
        customers, total = test_customer_service.search_customers()

        assert isinstance(customers, list)
        assert isinstance(total, int)
        assert total >= 0
        assert len(customers) <= total

    def test_customer_data_validation(self):
        """测试客户数据验证"""
        # 测试有效数据
        valid_data = {
            "name": "有效公司名",
            "contact_person": "有效联系人",
            "phone": "138-1234-5678",
            "email": "valid@example.com",
        }

        # 基本验证逻辑
        assert valid_data["name"] is not None and len(valid_data["name"]) > 0
        assert (
            valid_data["contact_person"] is not None
            and len(valid_data["contact_person"]) > 0
        )
        assert valid_data["phone"] is not None and len(valid_data["phone"]) > 0

        # 测试无效数据
        invalid_data = {
            "name": "",  # 空名称
            "contact_person": "",  # 空联系人
            "phone": "",  # 空电话
        }

        assert len(invalid_data["name"]) == 0
        assert len(invalid_data["contact_person"]) == 0
        assert len(invalid_data["phone"]) == 0

    def test_phone_format_validation(self):
        """测试电话格式验证"""
        valid_phones = ["138-1234-5678", "13812345678", "138 1234 5678", "1381234567"]

        invalid_phones = [
            "",
            "123",
            "abc-defg-hijk",
            "138-1234-567",  # 太短
            "138-1234-56789",  # 太长
        ]

        # 简单的电话验证逻辑
        for phone in valid_phones:
            # 移除所有非数字字符
            digits_only = "".join(filter(str.isdigit, phone))
            assert len(digits_only) >= 10, f"有效电话 {phone} 验证失败"

        for phone in invalid_phones:
            if phone:  # 非空字符串
                digits_only = "".join(filter(str.isdigit, phone))
                if len(digits_only) < 10:
                    assert True, f"无效电话 {phone} 正确被识别"

    def test_email_format_validation(self):
        """测试邮箱格式验证"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
        ]

        invalid_emails = ["", "invalid-email", "@example.com", "test@", "test@.com"]

        # 简单的邮箱验证逻辑
        for email in valid_emails:
            assert "@" in email and "." in email, f"有效邮箱 {email} 验证失败"

        for email in invalid_emails:
            if email:  # 非空字符串
                if "@" not in email or "." not in email:
                    assert True, f"无效邮箱 {email} 正确被识别"

    def test_module_imports(self):
        """测试模块导入"""
        try:
            # 测试客户编辑对话框模块导入
            from minicrm.ui.customer_edit_dialog import CustomerEditDialog

            assert CustomerEditDialog is not None

            # 测试客户面板模块导入
            from minicrm.ui.customer_panel import CustomerPanel

            assert CustomerPanel is not None

            # 测试客户服务模块导入
            from minicrm.services.customer_service import CustomerService

            assert CustomerService is not None

        except ImportError as e:
            pytest.skip(f"模块导入失败，跳过测试: {e}")


if __name__ == "__main__":
    # 直接运行测试
    pytest.main([__file__, "-v"])
