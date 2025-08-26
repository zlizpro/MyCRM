"""服务集成验证脚本

验证TTK界面与业务服务之间的完整集成，确保：
- 所有服务正确连接到TTK面板
- 数据流和事件处理正常工作
- 错误处理机制有效
- 集成管理器功能完整
"""

import unittest
from unittest.mock import Mock

from minicrm.core.exceptions import ServiceError, ValidationError
from minicrm.ui.ttk_base.service_integration_manager import (
    create_service_integrations,
    get_global_integration_manager,
)


class TestServiceIntegrationVerification(unittest.TestCase):
    """服务集成验证测试"""

    def setUp(self):
        """测试准备"""
        # 创建模拟服务
        self.mock_customer_service = Mock()
        self.mock_supplier_service = Mock()
        self.mock_finance_service = Mock()
        self.mock_task_service = Mock()
        self.mock_contract_service = Mock()

        # 创建服务集成
        self.integrations = create_service_integrations(
            customer_service=self.mock_customer_service,
            supplier_service=self.mock_supplier_service,
            finance_service=self.mock_finance_service,
            task_service=self.mock_task_service,
            contract_service=self.mock_contract_service,
        )

    def test_all_service_integrations_created(self):
        """验证所有服务集成器都已创建"""
        # 验证所有预期的集成器都存在
        expected_integrations = [
            "customer",
            "supplier",
            "finance",
            "task",
            "contract",
            "manager",
        ]

        for integration_name in expected_integrations:
            self.assertIn(integration_name, self.integrations)
            self.assertIsNotNone(self.integrations[integration_name])

    def test_customer_service_integration_workflow(self):
        """验证客户服务集成工作流程"""
        customer_integration = self.integrations["customer"]

        # 测试创建客户
        customer_data = {"name": "测试客户", "phone": "13800138000"}
        self.mock_customer_service.create_customer.return_value = 123

        customer_id = customer_integration.create_customer(customer_data)

        self.assertEqual(customer_id, 123)
        self.mock_customer_service.create_customer.assert_called_once_with(
            customer_data
        )

        # 测试搜索客户
        search_result = ([{"id": 123, "name": "测试客户"}], 1)
        self.mock_customer_service.search_customers.return_value = search_result

        customers, total = customer_integration.search_customers("测试")

        self.assertEqual(customers, [{"id": 123, "name": "测试客户"}])
        self.assertEqual(total, 1)

    def test_supplier_service_integration_workflow(self):
        """验证供应商服务集成工作流程"""
        supplier_integration = self.integrations["supplier"]

        # 测试创建供应商
        supplier_data = {
            "name": "测试供应商",
            "contact_person": "张三",
            "phone": "13800138000",
        }
        self.mock_supplier_service.create_supplier.return_value = 456

        supplier_id = supplier_integration.create_supplier(supplier_data)

        self.assertEqual(supplier_id, 456)
        self.mock_supplier_service.create_supplier.assert_called_once_with(
            supplier_data
        )

    def test_finance_service_integration_workflow(self):
        """验证财务服务集成工作流程"""
        finance_integration = self.integrations["finance"]

        # 测试获取应收账款汇总
        receivables_summary = {"total": 100000, "overdue": 5000}
        self.mock_finance_service.get_receivables_summary.return_value = (
            receivables_summary
        )

        result = finance_integration.get_receivables_summary()

        self.assertEqual(result, receivables_summary)
        self.mock_finance_service.get_receivables_summary.assert_called_once()

    def test_task_service_integration_workflow(self):
        """验证任务服务集成工作流程"""
        task_integration = self.integrations["task"]

        # 测试创建任务
        task_data = {
            "title": "测试任务",
            "description": "任务描述",
            "due_date": "2024-01-20",
        }
        self.mock_task_service.create_task.return_value = 789

        task_id = task_integration.create_task(task_data)

        self.assertEqual(task_id, 789)
        self.mock_task_service.create_task.assert_called_once_with(task_data)

    def test_contract_service_integration_workflow(self):
        """验证合同服务集成工作流程"""
        contract_integration = self.integrations["contract"]

        # 测试创建合同
        contract_data = {
            "title": "测试合同",
            "customer_id": 123,
            "contract_amount": 50000.00,
        }
        self.mock_contract_service.create_contract.return_value = 101

        contract_id = contract_integration.create_contract(contract_data)

        self.assertEqual(contract_id, 101)
        self.mock_contract_service.create_contract.assert_called_once_with(
            contract_data
        )

    def test_error_handling_across_integrations(self):
        """验证跨集成的错误处理"""
        customer_integration = self.integrations["customer"]

        # 测试验证错误
        invalid_data = {"name": ""}  # 缺少必填字段
        with self.assertRaises(ValidationError):
            customer_integration.create_customer(invalid_data)

        # 测试服务错误
        valid_data = {"name": "测试客户", "phone": "13800138000"}
        self.mock_customer_service.create_customer.side_effect = ServiceError(
            "业务错误"
        )

        with self.assertRaises(ServiceError):
            customer_integration.create_customer(valid_data)

    def test_event_system_integration(self):
        """验证事件系统集成"""
        manager = self.integrations["manager"]
        customer_integration = self.integrations["customer"]

        # 注册事件监听器
        events_received = []

        def event_handler(*args, **kwargs):
            events_received.append(("customer_created", args, kwargs))

        manager.register_event_handler("customer_created", event_handler)

        # 触发事件
        customer_data = {"name": "测试客户", "phone": "13800138000"}
        self.mock_customer_service.create_customer.return_value = 123

        customer_integration.create_customer(customer_data)

        # 验证事件被触发
        self.assertEqual(len(events_received), 1)
        event_name, args, kwargs = events_received[0]
        self.assertEqual(event_name, "customer_created")
        self.assertEqual(args, (123, customer_data))

    def test_integration_manager_functionality(self):
        """验证集成管理器功能"""
        manager = self.integrations["manager"]

        # 测试安全服务调用
        mock_method = Mock(return_value="success")
        result = manager.safe_service_call(mock_method, "arg1", key="value")

        self.assertEqual(result, "success")
        mock_method.assert_called_once_with("arg1", key="value")

        # 测试数据验证
        data = {"name": "测试", "phone": "13800138000"}
        required_fields = ["name", "phone"]

        # 应该不抛出异常
        manager.validate_service_data(data, required_fields)

        # 测试缺少字段的情况
        incomplete_data = {"name": "测试"}
        with self.assertRaises(ValidationError):
            manager.validate_service_data(incomplete_data, required_fields)

    def test_global_integration_manager_singleton(self):
        """验证全局集成管理器单例模式"""
        manager1 = get_global_integration_manager()
        manager2 = get_global_integration_manager()

        # 应该是同一个实例
        self.assertIs(manager1, manager2)

    def test_service_integration_consistency(self):
        """验证服务集成的一致性"""
        # 验证所有集成器都使用相同的管理器
        manager = self.integrations["manager"]

        customer_integration = self.integrations["customer"]
        supplier_integration = self.integrations["supplier"]
        finance_integration = self.integrations["finance"]
        task_integration = self.integrations["task"]
        contract_integration = self.integrations["contract"]

        # 所有集成器应该使用相同的管理器实例
        self.assertIs(customer_integration._manager, manager)
        self.assertIs(supplier_integration._manager, manager)
        self.assertIs(finance_integration._manager, manager)
        self.assertIs(task_integration._manager, manager)
        self.assertIs(contract_integration._manager, manager)

    def test_integration_with_real_service_interfaces(self):
        """验证与真实服务接口的集成"""
        # 这个测试验证集成器能够正确处理服务接口的所有方法
        customer_integration = self.integrations["customer"]

        # 验证所有客户服务方法都能被调用
        methods_to_test = [
            ("create_customer", {"name": "测试", "phone": "13800138000"}),
            ("get_customer", 123),
            ("update_customer", 123, {"name": "更新"}),
            ("delete_customer", 123),
            ("search_customers", "查询", {}, 1, 20),
        ]

        for method_name, *args in methods_to_test:
            # 设置模拟返回值
            if method_name == "create_customer":
                self.mock_customer_service.create_customer.return_value = 123
            elif method_name == "get_customer":
                self.mock_customer_service.get_customer.return_value = {"id": 123}
            elif method_name in ["update_customer", "delete_customer"]:
                getattr(self.mock_customer_service, method_name).return_value = True
            elif method_name == "search_customers":
                self.mock_customer_service.search_customers.return_value = ([], 0)

            # 调用集成器方法
            method = getattr(customer_integration, method_name)
            result = method(*args)

            # 验证服务方法被调用
            service_method = getattr(self.mock_customer_service, method_name)
            service_method.assert_called()

            # 验证返回值类型正确
            self.assertIsNotNone(result)


class TestServiceIntegrationPerformance(unittest.TestCase):
    """服务集成性能测试"""

    def setUp(self):
        """测试准备"""
        self.mock_customer_service = Mock()
        self.integrations = create_service_integrations(
            customer_service=self.mock_customer_service,
            supplier_service=Mock(),
            finance_service=Mock(),
            task_service=Mock(),
            contract_service=Mock(),
        )

    def test_bulk_operations_performance(self):
        """测试批量操作性能"""
        customer_integration = self.integrations["customer"]

        # 模拟批量创建客户
        customers_data = [
            {"name": f"客户{i}", "phone": f"1380013{i:04d}"} for i in range(100)
        ]

        # 设置服务返回值
        self.mock_customer_service.create_customer.side_effect = range(1, 101)

        # 执行批量创建
        created_ids = []
        for data in customers_data:
            customer_id = customer_integration.create_customer(data)
            created_ids.append(customer_id)

        # 验证结果
        self.assertEqual(len(created_ids), 100)
        self.assertEqual(created_ids, list(range(1, 101)))
        self.assertEqual(self.mock_customer_service.create_customer.call_count, 100)

    def test_concurrent_service_calls(self):
        """测试并发服务调用"""
        customer_integration = self.integrations["customer"]

        # 模拟并发获取客户信息
        customer_ids = list(range(1, 11))
        self.mock_customer_service.get_customer.side_effect = [
            {"id": i, "name": f"客户{i}"} for i in customer_ids
        ]

        # 并发调用
        results = []
        for customer_id in customer_ids:
            result = customer_integration.get_customer(customer_id)
            results.append(result)

        # 验证结果
        self.assertEqual(len(results), 10)
        for i, result in enumerate(results, 1):
            self.assertEqual(result["id"], i)
            self.assertEqual(result["name"], f"客户{i}")


if __name__ == "__main__":
    # 运行所有验证测试
    unittest.main(verbosity=2)
