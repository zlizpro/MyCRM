"""测试服务集成管理器

测试TTK界面与业务服务之间的集成功能，确保：
- 服务调用的正确性
- 错误处理的完整性
- 事件处理的可靠性
- 数据验证的有效性
"""

import unittest
from unittest.mock import Mock

from minicrm.core.exceptions import ServiceError, ValidationError
from minicrm.ui.ttk_base.service_integration_manager import (
    ContractServiceIntegration,
    CustomerServiceIntegration,
    FinanceServiceIntegration,
    ServiceIntegrationManager,
    SupplierServiceIntegration,
    TaskServiceIntegration,
)


class TestServiceIntegrationManager(unittest.TestCase):
    """测试服务集成管理器"""

    def setUp(self):
        """测试准备"""
        self.manager = ServiceIntegrationManager()

    def test_register_and_emit_event(self):
        """测试事件注册和触发"""
        # 准备
        handler_called = False
        handler_args = None
        handler_kwargs = None

        def test_handler(*args, **kwargs):
            nonlocal handler_called, handler_args, handler_kwargs
            handler_called = True
            handler_args = args
            handler_kwargs = kwargs

        # 注册事件处理器
        self.manager.register_event_handler("test_event", test_handler)

        # 触发事件
        self.manager.emit_event("test_event", "arg1", "arg2", key1="value1")

        # 验证
        self.assertTrue(handler_called)
        self.assertEqual(handler_args, ("arg1", "arg2"))
        self.assertEqual(handler_kwargs, {"key1": "value1"})

    def test_safe_service_call_success(self):
        """测试安全服务调用成功"""
        # 准备
        mock_service = Mock()
        mock_service.test_method.return_value = "success"

        # 执行
        result = self.manager.safe_service_call(
            mock_service.test_method, "arg1", key1="value1"
        )

        # 验证
        self.assertEqual(result, "success")
        mock_service.test_method.assert_called_once_with("arg1", key1="value1")

    def test_safe_service_call_validation_error(self):
        """测试安全服务调用验证错误"""
        # 准备
        mock_service = Mock()
        mock_service.test_method.side_effect = ValidationError("验证失败")

        # 执行和验证
        with self.assertRaises(ValidationError):
            self.manager.safe_service_call(mock_service.test_method)

    def test_safe_service_call_service_error(self):
        """测试安全服务调用业务错误"""
        # 准备
        mock_service = Mock()
        mock_service.test_method.side_effect = ServiceError("业务错误")

        # 执行和验证
        with self.assertRaises(ServiceError):
            self.manager.safe_service_call(mock_service.test_method)

    def test_safe_service_call_with_default_return(self):
        """测试安全服务调用返回默认值"""
        # 准备
        mock_service = Mock()
        mock_service.test_method.side_effect = Exception("未知错误")

        # 执行
        result = self.manager.safe_service_call(
            mock_service.test_method, default_return="default"
        )

        # 验证
        self.assertEqual(result, "default")

    def test_validate_service_data_success(self):
        """测试数据验证成功"""
        # 准备
        data = {"name": "测试", "phone": "13800138000", "email": "test@example.com"}
        required_fields = ["name", "phone"]

        # 执行（不应抛出异常）
        self.manager.validate_service_data(data, required_fields)

    def test_validate_service_data_missing_fields(self):
        """测试数据验证缺少字段"""
        # 准备
        data = {"name": "测试"}
        required_fields = ["name", "phone", "email"]

        # 执行和验证
        with self.assertRaises(ValidationError) as context:
            self.manager.validate_service_data(data, required_fields)

        self.assertIn("缺少必填字段", str(context.exception))
        self.assertIn("phone", str(context.exception))
        self.assertIn("email", str(context.exception))

    def test_format_service_error(self):
        """测试错误消息格式化"""
        # 验证错误类型
        validation_error = ValidationError("数据无效")
        formatted = self.manager.format_service_error(validation_error, "创建客户")
        self.assertIn("数据验证错误", formatted)

        service_error = ServiceError("业务规则违反")
        formatted = self.manager.format_service_error(service_error, "更新客户")
        self.assertIn("业务逻辑错误", formatted)

        general_error = Exception("系统异常")
        formatted = self.manager.format_service_error(general_error, "删除客户")
        self.assertIn("系统错误", formatted)


class TestCustomerServiceIntegration(unittest.TestCase):
    """测试客户服务集成器"""

    def setUp(self):
        """测试准备"""
        self.mock_service = Mock()
        self.manager = ServiceIntegrationManager()
        self.integration = CustomerServiceIntegration(self.mock_service, self.manager)

    def test_create_customer_success(self):
        """测试创建客户成功"""
        # 准备
        customer_data = {"name": "测试客户", "phone": "13800138000"}
        self.mock_service.create_customer.return_value = 123

        # 监听事件
        event_triggered = False
        event_data = None

        def event_handler(customer_id, data):
            nonlocal event_triggered, event_data
            event_triggered = True
            event_data = (customer_id, data)

        self.manager.register_event_handler("customer_created", event_handler)

        # 执行
        result = self.integration.create_customer(customer_data)

        # 验证
        self.assertEqual(result, 123)
        self.mock_service.create_customer.assert_called_once_with(customer_data)
        self.assertTrue(event_triggered)
        self.assertEqual(event_data, (123, customer_data))

    def test_create_customer_validation_error(self):
        """测试创建客户验证错误"""
        # 准备
        customer_data = {"name": ""}  # 缺少必填字段

        # 执行和验证
        with self.assertRaises(ValidationError):
            self.integration.create_customer(customer_data)

    def test_update_customer_success(self):
        """测试更新客户成功"""
        # 准备
        customer_data = {"name": "更新后的客户"}
        self.mock_service.update_customer.return_value = True

        # 执行
        result = self.integration.update_customer(123, customer_data)

        # 验证
        self.assertTrue(result)
        self.mock_service.update_customer.assert_called_once_with(123, customer_data)

    def test_delete_customer_success(self):
        """测试删除客户成功"""
        # 准备
        self.mock_service.delete_customer.return_value = True

        # 执行
        result = self.integration.delete_customer(123)

        # 验证
        self.assertTrue(result)
        self.mock_service.delete_customer.assert_called_once_with(123)

    def test_search_customers_success(self):
        """测试搜索客户成功"""
        # 准备
        expected_result = ([{"id": 1, "name": "客户1"}], 1)
        self.mock_service.search_customers.return_value = expected_result

        # 执行
        result = self.integration.search_customers("测试", {"type": "企业"}, 1, 20)

        # 验证
        self.assertEqual(result, expected_result)
        self.mock_service.search_customers.assert_called_once_with(
            "测试", {"type": "企业"}, 1, 20
        )

    def test_get_customer_success(self):
        """测试获取客户成功"""
        # 准备
        expected_customer = {"id": 123, "name": "测试客户"}
        self.mock_service.get_customer.return_value = expected_customer

        # 执行
        result = self.integration.get_customer(123)

        # 验证
        self.assertEqual(result, expected_customer)
        self.mock_service.get_customer.assert_called_once_with(123)


class TestSupplierServiceIntegration(unittest.TestCase):
    """测试供应商服务集成器"""

    def setUp(self):
        """测试准备"""
        self.mock_service = Mock()
        self.manager = ServiceIntegrationManager()
        self.integration = SupplierServiceIntegration(self.mock_service, self.manager)

    def test_create_supplier_success(self):
        """测试创建供应商成功"""
        # 准备
        supplier_data = {
            "name": "测试供应商",
            "contact_person": "张三",
            "phone": "13800138000",
        }
        self.mock_service.create_supplier.return_value = 456

        # 执行
        result = self.integration.create_supplier(supplier_data)

        # 验证
        self.assertEqual(result, 456)
        self.mock_service.create_supplier.assert_called_once_with(supplier_data)

    def test_create_supplier_validation_error(self):
        """测试创建供应商验证错误"""
        # 准备
        supplier_data = {"name": "测试供应商"}  # 缺少必填字段

        # 执行和验证
        with self.assertRaises(ValidationError):
            self.integration.create_supplier(supplier_data)

    def test_search_suppliers_success(self):
        """测试搜索供应商成功"""
        # 准备
        expected_result = ([{"id": 1, "name": "供应商1"}], 1)
        self.mock_service.search_suppliers.return_value = expected_result

        # 执行
        result = self.integration.search_suppliers("测试", {"level": "A"}, 1, 20)

        # 验证
        self.assertEqual(result, expected_result)
        self.mock_service.search_suppliers.assert_called_once_with(
            "测试", {"level": "A"}, 1, 20
        )


class TestFinanceServiceIntegration(unittest.TestCase):
    """测试财务服务集成器"""

    def setUp(self):
        """测试准备"""
        self.mock_service = Mock()
        self.manager = ServiceIntegrationManager()
        self.integration = FinanceServiceIntegration(self.mock_service, self.manager)

    def test_get_receivables_summary_success(self):
        """测试获取应收账款汇总成功"""
        # 准备
        expected_summary = {"total": 100000, "overdue": 5000}
        self.mock_service.get_receivables_summary.return_value = expected_summary

        # 执行
        result = self.integration.get_receivables_summary()

        # 验证
        self.assertEqual(result, expected_summary)
        self.mock_service.get_receivables_summary.assert_called_once()

    def test_record_payment_success(self):
        """测试记录收付款成功"""
        # 准备
        payment_data = {
            "amount": 5000.00,
            "payment_type": "收款",
            "payment_date": "2024-01-15",
        }
        self.mock_service.record_payment.return_value = 789

        # 执行
        result = self.integration.record_payment(payment_data)

        # 验证
        self.assertEqual(result, 789)
        self.mock_service.record_payment.assert_called_once_with(payment_data)

    def test_record_payment_validation_error(self):
        """测试记录收付款验证错误"""
        # 准备
        payment_data = {"amount": 5000.00}  # 缺少必填字段

        # 执行和验证
        with self.assertRaises(ValidationError):
            self.integration.record_payment(payment_data)


class TestTaskServiceIntegration(unittest.TestCase):
    """测试任务服务集成器"""

    def setUp(self):
        """测试准备"""
        self.mock_service = Mock()
        self.manager = ServiceIntegrationManager()
        self.integration = TaskServiceIntegration(self.mock_service, self.manager)

    def test_create_task_success(self):
        """测试创建任务成功"""
        # 准备
        task_data = {
            "title": "测试任务",
            "description": "任务描述",
            "due_date": "2024-01-20",
        }
        self.mock_service.create_task.return_value = 101

        # 执行
        result = self.integration.create_task(task_data)

        # 验证
        self.assertEqual(result, 101)
        self.mock_service.create_task.assert_called_once_with(task_data)

    def test_mark_task_completed_success(self):
        """测试标记任务完成成功"""
        # 准备
        self.mock_service.mark_task_completed.return_value = True

        # 执行
        result = self.integration.mark_task_completed(101)

        # 验证
        self.assertTrue(result)
        self.mock_service.mark_task_completed.assert_called_once_with(101)

    def test_get_pending_tasks_success(self):
        """测试获取待办任务成功"""
        # 准备
        expected_tasks = [{"id": 1, "title": "任务1"}, {"id": 2, "title": "任务2"}]
        self.mock_service.get_pending_tasks.return_value = expected_tasks

        # 执行
        result = self.integration.get_pending_tasks(5)

        # 验证
        self.assertEqual(result, expected_tasks)
        self.mock_service.get_pending_tasks.assert_called_once_with(5)


class TestContractServiceIntegration(unittest.TestCase):
    """测试合同服务集成器"""

    def setUp(self):
        """测试准备"""
        self.mock_service = Mock()
        self.manager = ServiceIntegrationManager()
        self.integration = ContractServiceIntegration(self.mock_service, self.manager)

    def test_create_contract_success(self):
        """测试创建合同成功"""
        # 准备
        contract_data = {
            "title": "测试合同",
            "customer_id": 123,
            "contract_amount": 50000.00,
        }
        self.mock_service.create_contract.return_value = 202

        # 执行
        result = self.integration.create_contract(contract_data)

        # 验证
        self.assertEqual(result, 202)
        self.mock_service.create_contract.assert_called_once_with(contract_data)

    def test_create_contract_validation_error(self):
        """测试创建合同验证错误"""
        # 准备
        contract_data = {"title": "测试合同"}  # 缺少必填字段

        # 执行和验证
        with self.assertRaises(ValidationError):
            self.integration.create_contract(contract_data)

    def test_search_contracts_success(self):
        """测试搜索合同成功"""
        # 准备
        expected_result = ([{"id": 1, "title": "合同1"}], 1)
        self.mock_service.search_contracts.return_value = expected_result

        # 执行
        result = self.integration.search_contracts("测试", {"status": "active"}, 1, 20)

        # 验证
        self.assertEqual(result, expected_result)
        self.mock_service.search_contracts.assert_called_once_with(
            "测试", {"status": "active"}, 1, 20
        )


if __name__ == "__main__":
    unittest.main()
