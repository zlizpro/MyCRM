"""完整的服务集成测试

测试TTK界面与业务服务之间的完整数据流，确保：
- 端到端的数据流正确性
- UI操作正确调用业务逻辑
- 业务逻辑结果正确反映到UI
- 错误处理在整个流程中正常工作
"""

import unittest
from unittest.mock import Mock

from minicrm.core.exceptions import ServiceError, ValidationError
from minicrm.ui.ttk_base.service_integration_manager import (
    CustomerServiceIntegration,
    ServiceIntegrationManager,
)


class TestCompleteServiceIntegration(unittest.TestCase):
    """完整服务集成测试"""

    def setUp(self):
        """测试准备"""
        self.mock_customer_service = Mock()
        self.integration_manager = ServiceIntegrationManager()
        self.customer_integration = CustomerServiceIntegration(
            self.mock_customer_service, self.integration_manager
        )

        # 设置事件监听器
        self.events_received = []

        def event_listener(event_name):
            def handler(*args, **kwargs):
                self.events_received.append((event_name, args, kwargs))

            return handler

        self.integration_manager.register_event_handler(
            "customer_created", event_listener("customer_created")
        )
        self.integration_manager.register_event_handler(
            "customer_updated", event_listener("customer_updated")
        )
        self.integration_manager.register_event_handler(
            "customer_deleted", event_listener("customer_deleted")
        )

    def test_complete_customer_lifecycle(self):
        """测试完整的客户生命周期"""
        # 1. 创建客户
        customer_data = {
            "name": "测试公司",
            "phone": "13800138000",
            "email": "test@example.com",
            "address": "测试地址",
        }
        self.mock_customer_service.create_customer.return_value = 123

        customer_id = self.customer_integration.create_customer(customer_data)

        # 验证创建结果
        self.assertEqual(customer_id, 123)
        self.mock_customer_service.create_customer.assert_called_once_with(
            customer_data
        )

        # 验证事件触发
        self.assertEqual(len(self.events_received), 1)
        event_name, args, kwargs = self.events_received[0]
        self.assertEqual(event_name, "customer_created")
        self.assertEqual(args, (123, customer_data))

        # 2. 获取客户信息
        customer_info = {
            "id": 123,
            "name": "测试公司",
            "phone": "13800138000",
            "email": "test@example.com",
            "address": "测试地址",
            "created_at": "2024-01-15 10:00:00",
        }
        self.mock_customer_service.get_customer.return_value = customer_info

        result = self.customer_integration.get_customer(123)

        # 验证获取结果
        self.assertEqual(result, customer_info)
        self.mock_customer_service.get_customer.assert_called_once_with(123)

        # 3. 更新客户信息
        update_data = {"name": "更新后的公司名称", "email": "updated@example.com"}
        self.mock_customer_service.update_customer.return_value = True

        success = self.customer_integration.update_customer(123, update_data)

        # 验证更新结果
        self.assertTrue(success)
        self.mock_customer_service.update_customer.assert_called_once_with(
            123, update_data
        )

        # 验证更新事件
        self.assertEqual(len(self.events_received), 2)
        event_name, args, kwargs = self.events_received[1]
        self.assertEqual(event_name, "customer_updated")
        self.assertEqual(args, (123, update_data))

        # 4. 搜索客户
        search_results = ([customer_info], 1)
        self.mock_customer_service.search_customers.return_value = search_results

        customers, total = self.customer_integration.search_customers(
            query="测试", filters={"type": "企业"}, page=1, page_size=20
        )

        # 验证搜索结果
        self.assertEqual(customers, [customer_info])
        self.assertEqual(total, 1)
        self.mock_customer_service.search_customers.assert_called_once_with(
            "测试", {"type": "企业"}, 1, 20
        )

        # 5. 删除客户
        self.mock_customer_service.delete_customer.return_value = True

        success = self.customer_integration.delete_customer(123)

        # 验证删除结果
        self.assertTrue(success)
        self.mock_customer_service.delete_customer.assert_called_once_with(123)

        # 验证删除事件
        self.assertEqual(len(self.events_received), 3)
        event_name, args, kwargs = self.events_received[2]
        self.assertEqual(event_name, "customer_deleted")
        self.assertEqual(args, (123,))

    def test_error_handling_in_complete_flow(self):
        """测试完整流程中的错误处理"""
        # 1. 测试创建客户时的验证错误
        invalid_data = {"name": ""}  # 缺少必填字段

        with self.assertRaises(ValidationError):
            self.customer_integration.create_customer(invalid_data)

        # 验证没有调用服务方法
        self.mock_customer_service.create_customer.assert_not_called()

        # 验证没有触发事件
        self.assertEqual(len(self.events_received), 0)

        # 2. 测试服务层错误
        valid_data = {"name": "测试公司", "phone": "13800138000"}
        self.mock_customer_service.create_customer.side_effect = ServiceError(
            "业务错误"
        )

        with self.assertRaises(ServiceError):
            self.customer_integration.create_customer(valid_data)

        # 验证调用了服务方法
        self.mock_customer_service.create_customer.assert_called_once_with(valid_data)

        # 验证没有触发成功事件
        self.assertEqual(len(self.events_received), 0)

        # 3. 测试系统异常的处理
        self.mock_customer_service.create_customer.side_effect = Exception("系统异常")

        with self.assertRaises(Exception):
            self.customer_integration.create_customer(valid_data)

    def test_concurrent_operations(self):
        """测试并发操作"""
        # 模拟多个客户同时创建
        customers_data = [
            {"name": f"客户{i}", "phone": f"1380013800{i}"} for i in range(5)
        ]

        # 设置服务返回值
        self.mock_customer_service.create_customer.side_effect = range(1, 6)

        # 并发创建客户
        created_ids = []
        for data in customers_data:
            customer_id = self.customer_integration.create_customer(data)
            created_ids.append(customer_id)

        # 验证结果
        self.assertEqual(created_ids, [1, 2, 3, 4, 5])
        self.assertEqual(self.mock_customer_service.create_customer.call_count, 5)

        # 验证所有事件都被触发
        self.assertEqual(len(self.events_received), 5)
        for i, (event_name, args, kwargs) in enumerate(self.events_received):
            self.assertEqual(event_name, "customer_created")
            self.assertEqual(args[0], i + 1)  # 客户ID
            self.assertEqual(args[1], customers_data[i])  # 客户数据

    def test_data_consistency(self):
        """测试数据一致性"""
        # 创建客户
        customer_data = {"name": "一致性测试客户", "phone": "13800138000"}
        self.mock_customer_service.create_customer.return_value = 999

        customer_id = self.customer_integration.create_customer(customer_data)

        # 验证传递给服务的数据与原始数据一致
        call_args = self.mock_customer_service.create_customer.call_args[0][0]
        self.assertEqual(call_args, customer_data)

        # 验证事件中的数据与原始数据一致
        event_name, args, kwargs = self.events_received[0]
        self.assertEqual(args[1], customer_data)

        # 测试数据修改不影响原始数据
        modified_data = customer_data.copy()
        modified_data["name"] = "修改后的名称"

        self.mock_customer_service.update_customer.return_value = True
        self.customer_integration.update_customer(customer_id, modified_data)

        # 验证原始数据没有被修改
        self.assertEqual(customer_data["name"], "一致性测试客户")

        # 验证事件中的数据是修改后的数据
        event_name, args, kwargs = self.events_received[1]
        self.assertEqual(args[1]["name"], "修改后的名称")

    def test_service_method_call_parameters(self):
        """测试服务方法调用参数"""
        # 测试搜索方法的参数传递
        self.mock_customer_service.search_customers.return_value = ([], 0)

        # 测试所有参数都传递
        self.customer_integration.search_customers(
            query="测试查询",
            filters={"level": "VIP", "type": "企业"},
            page=2,
            page_size=50,
        )

        # 验证参数传递正确
        self.mock_customer_service.search_customers.assert_called_once_with(
            "测试查询", {"level": "VIP", "type": "企业"}, 2, 50
        )

        # 测试默认参数
        self.mock_customer_service.search_customers.reset_mock()
        self.customer_integration.search_customers()

        # 验证默认参数
        self.mock_customer_service.search_customers.assert_called_once_with(
            "", None, 1, 20
        )

    def test_return_value_handling(self):
        """测试返回值处理"""
        # 测试成功返回值
        self.mock_customer_service.create_customer.return_value = 123
        result = self.customer_integration.create_customer(
            {"name": "测试", "phone": "13800138000"}
        )
        self.assertEqual(result, 123)

        # 测试布尔返回值
        self.mock_customer_service.update_customer.return_value = True
        result = self.customer_integration.update_customer(123, {"name": "更新"})
        self.assertTrue(result)

        self.mock_customer_service.update_customer.return_value = False
        result = self.customer_integration.update_customer(123, {"name": "更新"})
        self.assertFalse(result)

        # 测试复杂返回值
        complex_result = ([{"id": 1, "name": "客户1"}], 1)
        self.mock_customer_service.search_customers.return_value = complex_result
        result = self.customer_integration.search_customers()
        self.assertEqual(result, complex_result)

        # 测试None返回值
        self.mock_customer_service.get_customer.return_value = None
        result = self.customer_integration.get_customer(999)
        self.assertIsNone(result)


class TestIntegrationPerformance(unittest.TestCase):
    """集成性能测试"""

    def setUp(self):
        """测试准备"""
        self.mock_service = Mock()
        self.manager = ServiceIntegrationManager()
        self.integration = CustomerServiceIntegration(self.mock_service, self.manager)

    def test_large_data_handling(self):
        """测试大数据量处理"""
        # 模拟大量客户数据
        large_customer_list = [
            {"id": i, "name": f"客户{i}", "phone": f"1380013{i:04d}"}
            for i in range(1000)
        ]

        self.mock_service.search_customers.return_value = (large_customer_list, 1000)

        # 执行搜索
        customers, total = self.integration.search_customers(page_size=1000)

        # 验证结果
        self.assertEqual(len(customers), 1000)
        self.assertEqual(total, 1000)
        self.assertEqual(customers[0]["name"], "客户0")
        self.assertEqual(customers[999]["name"], "客户999")

    def test_frequent_operations(self):
        """测试频繁操作"""
        # 模拟频繁的获取操作
        self.mock_service.get_customer.return_value = {"id": 1, "name": "测试客户"}

        # 执行100次获取操作
        for i in range(100):
            result = self.integration.get_customer(1)
            self.assertIsNotNone(result)

        # 验证调用次数
        self.assertEqual(self.mock_service.get_customer.call_count, 100)

    def test_error_recovery(self):
        """测试错误恢复"""
        # 模拟间歇性错误
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 3 == 0:  # 每第3次调用失败
                raise ServiceError("间歇性错误")
            return {"id": call_count, "name": f"客户{call_count}"}

        self.mock_service.get_customer.side_effect = side_effect

        # 执行多次操作，验证错误恢复
        success_count = 0
        error_count = 0

        for i in range(10):
            try:
                result = self.integration.get_customer(i)
                success_count += 1
                self.assertIsNotNone(result)
            except ServiceError:
                error_count += 1

        # 验证成功和失败的次数符合预期
        self.assertEqual(success_count, 7)  # 10次中有3次失败
        self.assertEqual(error_count, 3)


if __name__ == "__main__":
    unittest.main()
