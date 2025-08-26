"""
财务管理服务单元测试

测试财务服务的核心功能：
- 客户授信管理
- 应收账款管理
- 收款记录管理
- 财务风险评估
"""

import unittest
from decimal import Decimal
from unittest.mock import Mock

from minicrm.core.exceptions import BusinessLogicError, ValidationError
from minicrm.services.finance_service import FinanceService


class TestFinanceService(unittest.TestCase):
    """财务服务测试类"""

    def setUp(self):
        """测试准备"""
        self.customer_dao = Mock()
        self.supplier_dao = Mock()
        self.finance_service = FinanceService(self.customer_dao, self.supplier_dao)

    def test_manage_customer_credit_success(self):
        """测试成功管理客户授信"""
        # 准备测试数据
        customer_id = 1
        credit_data = {"credit_amount": "50000", "credit_period": 30}

        # 模拟客户存在
        self.customer_dao.get_by_id.return_value = {
            "id": customer_id,
            "name": "测试客户",
        }

        # 模拟历史数据
        self.customer_dao.get_transaction_history.return_value = [
            {"id": 1, "amount": 10000},
            {"id": 2, "amount": 20000},
        ]
        self.customer_dao.get_payments.return_value = [{"id": 1, "amount": 5000}]

        # 模拟插入授信记录
        self.customer_dao.insert_credit_record.return_value = 1

        # 执行测试
        result = self.finance_service.manage_customer_credit(customer_id, credit_data)

        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertEqual(result["customer_id"], customer_id)
        self.assertEqual(result["credit_amount"], 50000.0)
        self.assertIn("risk_assessment", result)

        # 验证调用
        self.customer_dao.get_by_id.assert_called_once_with(customer_id)
        self.customer_dao.insert_credit_record.assert_called_once()

    def test_manage_customer_credit_customer_not_found(self):
        """测试客户不存在时的授信管理"""
        customer_id = 999
        credit_data = {"credit_amount": "50000", "credit_period": 30}

        # 模拟客户不存在
        self.customer_dao.get_by_id.return_value = None

        # 执行测试并验证异常
        with self.assertRaises(BusinessLogicError) as context:
            self.finance_service.manage_customer_credit(customer_id, credit_data)

        self.assertIn("客户不存在", str(context.exception))

    def test_manage_customer_credit_invalid_amount(self):
        """测试无效授信金额"""
        customer_id = 1
        credit_data = {
            "credit_amount": "0",  # 无效金额
            "credit_period": 30,
        }

        # 模拟客户存在
        self.customer_dao.get_by_id.return_value = {
            "id": customer_id,
            "name": "测试客户",
        }

        # 执行测试并验证异常
        with self.assertRaises(ValidationError) as context:
            self.finance_service.manage_customer_credit(customer_id, credit_data)

        self.assertIn("授信金额必须大于0", str(context.exception))

    def test_record_receivable_success(self):
        """测试成功记录应收账款"""
        customer_id = 1
        receivable_data = {
            "amount": "10000",
            "due_date": "2025-02-15",
            "description": "产品销售",
        }

        # 模拟客户存在
        self.customer_dao.get_by_id.return_value = {
            "id": customer_id,
            "name": "测试客户",
        }

        # 模拟授信信息
        self.customer_dao.get_credit_info.return_value = {"credit_amount": 100000}
        self.customer_dao.get_receivables_total.return_value = Decimal("5000")

        # 模拟插入应收账款
        self.customer_dao.insert_receivable.return_value = 1

        # 执行测试
        result = self.finance_service.record_receivable(customer_id, receivable_data)

        # 验证结果
        self.assertEqual(result, 1)
        self.customer_dao.insert_receivable.assert_called_once()

    def test_record_receivable_exceed_credit_limit(self):
        """测试超出授信额度"""
        customer_id = 1
        receivable_data = {
            "amount": "60000",  # 超出授信额度
            "due_date": "2025-02-15",
            "description": "产品销售",
        }

        # 模拟客户存在
        self.customer_dao.get_by_id.return_value = {
            "id": customer_id,
            "name": "测试客户",
        }

        # 模拟授信信息
        self.customer_dao.get_credit_info.return_value = {"credit_amount": 50000}
        self.customer_dao.get_receivables_total.return_value = Decimal("40000")

        # 执行测试并验证异常
        with self.assertRaises(BusinessLogicError) as context:
            self.finance_service.record_receivable(customer_id, receivable_data)

        self.assertIn("超出授信额度限制", str(context.exception))

    def test_record_payment_success(self):
        """测试成功记录收款"""
        customer_id = 1
        payment_data = {"amount": "5000", "payment_method": "银行转账"}

        # 模拟客户存在
        self.customer_dao.get_by_id.return_value = {
            "id": customer_id,
            "name": "测试客户",
        }

        # 模拟待收款应收账款
        self.customer_dao.get_pending_receivables.return_value = [
            {"id": 1, "amount": 10000}
        ]

        # 模拟插入收款记录
        self.customer_dao.insert_payment.return_value = 1

        # 执行测试
        result = self.finance_service.record_payment(customer_id, payment_data)

        # 验证结果
        self.assertEqual(result, 1)
        self.customer_dao.insert_payment.assert_called_once()
        self.customer_dao.update_receivable_amount.assert_called_once()

    def test_assess_financial_risk_success(self):
        """测试财务风险评估"""
        customer_id = 1

        # 模拟客户存在
        self.customer_dao.get_by_id.return_value = {
            "id": customer_id,
            "name": "测试客户",
        }

        # 模拟财务数据
        self.customer_dao.get_receivables.return_value = [
            {"id": 1, "amount": 10000, "due_date": "2025-01-01", "status": "pending"}
        ]
        self.customer_dao.get_payments.return_value = [{"id": 1, "amount": 5000}]
        self.customer_dao.get_credit_info.return_value = {"credit_amount": 50000}

        # 执行测试
        result = self.finance_service.assess_financial_risk(customer_id)

        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertEqual(result["customer_id"], customer_id)
        self.assertIn("risk_score", result)
        self.assertIn("risk_level", result)
        self.assertIn("warnings", result)

    def test_get_financial_summary_success(self):
        """测试获取财务汇总"""
        # 模拟应收账款汇总
        self.customer_dao.get_receivables_summary.return_value = {
            "total_amount": 100000,
            "overdue_amount": 10000,
        }

        # 模拟应付账款汇总
        self.supplier_dao.get_payables_summary.return_value = {
            "total_amount": 80000,
            "overdue_amount": 5000,
        }

        # 执行测试
        result = self.finance_service.get_financial_summary()

        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertEqual(result["total_receivables"], 100000)
        self.assertEqual(result["total_payables"], 80000)
        self.assertEqual(result["net_position"], 20000)
        self.assertIn("generated_at", result)

    def test_validate_required_fields_missing(self):
        """测试必填字段验证"""
        data = {"amount": "1000"}  # 缺少必填字段
        required_fields = ["amount", "due_date", "description"]

        # 执行测试并验证异常
        with self.assertRaises(ValidationError) as context:
            self.finance_service._validate_required_fields(data, required_fields)

        self.assertIn("缺少必填字段", str(context.exception))

    def test_calculate_overdue_amount(self):
        """测试计算逾期金额"""
        receivables = [
            {
                "amount": 10000,
                "due_date": "2024-12-01",  # 已逾期
                "status": "pending",
            },
            {
                "amount": 5000,
                "due_date": "2026-03-01",  # 未逾期（明年）
                "status": "pending",
            },
            {
                "amount": 3000,
                "due_date": "2024-11-01",  # 已逾期但已付款
                "status": "paid",
            },
        ]

        # 执行测试
        overdue_amount = self.finance_service._calculate_overdue_amount(receivables)

        # 验证结果（只有第一个记录是逾期且未付款的）
        self.assertEqual(overdue_amount, Decimal("10000"))

    def test_calculate_credit_utilization(self):
        """测试计算授信使用率"""
        receivables = [{"amount": 10000}, {"amount": 5000}]
        credit_info = {"credit_amount": 50000}

        # 执行测试
        utilization = self.finance_service._calculate_credit_utilization(
            receivables, credit_info
        )

        # 验证结果
        self.assertEqual(utilization, 30.0)  # 15000 / 50000 * 100

    def test_calculate_credit_utilization_no_credit(self):
        """测试无授信时的使用率计算"""
        receivables = [{"amount": 10000}]
        credit_info = None

        # 执行测试
        utilization = self.finance_service._calculate_credit_utilization(
            receivables, credit_info
        )

        # 验证结果
        self.assertEqual(utilization, 0.0)

    def test_determine_risk_level(self):
        """测试风险等级确定"""
        # 测试各种风险等级
        self.assertEqual(self.finance_service._determine_risk_level(90), "低风险")
        self.assertEqual(self.finance_service._determine_risk_level(70), "中风险")
        self.assertEqual(self.finance_service._determine_risk_level(50), "高风险")
        self.assertEqual(self.finance_service._determine_risk_level(30), "极高风险")

    def test_get_total_receivables_success(self):
        """测试获取应收账款总额成功"""
        # 模拟DAO返回应收账款汇总
        mock_summary = {"total_amount": 125000.50, "overdue_amount": 15000.00}
        self.customer_dao.get_receivables_summary.return_value = mock_summary

        # 执行测试
        result = self.finance_service.get_total_receivables()

        # 验证结果
        self.assertEqual(result, 125000.50)
        self.assertIsInstance(result, float)
        self.customer_dao.get_receivables_summary.assert_called_once()

    def test_get_total_receivables_zero(self):
        """测试获取应收账款总额为零"""
        # 模拟DAO返回零应收账款
        mock_summary = {"total_amount": 0, "overdue_amount": 0}
        self.customer_dao.get_receivables_summary.return_value = mock_summary

        # 执行测试
        result = self.finance_service.get_total_receivables()

        # 验证结果
        self.assertEqual(result, 0.0)
        self.assertIsInstance(result, float)

    def test_get_total_receivables_missing_data(self):
        """测试获取应收账款总额时数据缺失"""
        # 模拟DAO返回不完整数据
        mock_summary = {}
        self.customer_dao.get_receivables_summary.return_value = mock_summary

        # 执行测试
        result = self.finance_service.get_total_receivables()

        # 验证结果（应该返回默认值0）
        self.assertEqual(result, 0.0)
        self.assertIsInstance(result, float)

    def test_get_total_receivables_database_error(self):
        """测试获取应收账款总额时数据库错误"""
        from minicrm.core.exceptions import ServiceError

        # 模拟数据库异常
        self.customer_dao.get_receivables_summary.side_effect = Exception(
            "数据库连接失败"
        )

        # 执行测试并验证异常
        with self.assertRaises(ServiceError) as context:
            self.finance_service.get_total_receivables()

        # 验证异常信息
        self.assertIn("获取应收账款总额失败", str(context.exception))


if __name__ == "__main__":
    unittest.main()
