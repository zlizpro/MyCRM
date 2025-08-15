"""
供应商财务管理服务单元测试

测试供应商财务服务的核心功能：
- 应付账款管理
- 供应商付款管理
- 账期管理
- 供应商财务风险评估
"""

import unittest
from decimal import Decimal
from unittest.mock import Mock

from minicrm.core.exceptions import BusinessLogicError, ValidationError
from minicrm.services.supplier_finance_service import SupplierFinanceService


class TestSupplierFinanceService(unittest.TestCase):
    """供应商财务服务测试类"""

    def setUp(self):
        """测试准备"""
        self.supplier_dao = Mock()
        self.supplier_finance_service = SupplierFinanceService(self.supplier_dao)

    def test_record_payable_success(self):
        """测试成功记录应付账款"""
        supplier_id = 1
        payable_data = {
            "amount": "20000",
            "due_date": "2025-02-15",
            "description": "原材料采购",
        }

        # 模拟供应商存在
        self.supplier_dao.get_by_id.return_value = {
            "id": supplier_id,
            "name": "测试供应商",
        }

        # 模拟插入应付账款
        self.supplier_dao.insert_payable.return_value = 1

        # 执行测试
        result = self.supplier_finance_service.record_payable(supplier_id, payable_data)

        # 验证结果
        self.assertEqual(result, 1)
        self.supplier_dao.insert_payable.assert_called_once()

    def test_record_payable_supplier_not_found(self):
        """测试供应商不存在时记录应付账款"""
        supplier_id = 999
        payable_data = {
            "amount": "20000",
            "due_date": "2025-02-15",
            "description": "原材料采购",
        }

        # 模拟供应商不存在
        self.supplier_dao.get_by_id.return_value = None

        # 执行测试并验证异常
        with self.assertRaises(BusinessLogicError) as context:
            self.supplier_finance_service.record_payable(supplier_id, payable_data)

        self.assertIn("供应商不存在", str(context.exception))

    def test_record_payable_invalid_amount(self):
        """测试无效应付金额"""
        supplier_id = 1
        payable_data = {
            "amount": "-1000",  # 无效金额
            "due_date": "2025-02-15",
            "description": "原材料采购",
        }

        # 模拟供应商存在
        self.supplier_dao.get_by_id.return_value = {
            "id": supplier_id,
            "name": "测试供应商",
        }

        # 执行测试并验证异常
        with self.assertRaises(ValidationError) as context:
            self.supplier_finance_service.record_payable(supplier_id, payable_data)

        self.assertIn("应付金额必须大于0", str(context.exception))

    def test_record_supplier_payment_success(self):
        """测试成功记录供应商付款"""
        supplier_id = 1
        payment_data = {"amount": "15000", "payment_method": "银行转账"}

        # 模拟供应商存在
        self.supplier_dao.get_by_id.return_value = {
            "id": supplier_id,
            "name": "测试供应商",
        }

        # 模拟待付款应付账款
        self.supplier_dao.get_pending_payables.return_value = [
            {"id": 1, "amount": 20000}
        ]

        # 模拟插入付款记录
        self.supplier_dao.insert_supplier_payment.return_value = 1

        # 执行测试
        result = self.supplier_finance_service.record_supplier_payment(
            supplier_id, payment_data
        )

        # 验证结果
        self.assertEqual(result, 1)
        self.supplier_dao.insert_supplier_payment.assert_called_once()

    def test_record_supplier_payment_exceed_payable(self):
        """测试付款金额超过应付金额"""
        supplier_id = 1
        payment_data = {
            "amount": "25000",  # 超过应付金额
            "payment_method": "银行转账",
        }

        # 模拟供应商存在
        self.supplier_dao.get_by_id.return_value = {
            "id": supplier_id,
            "name": "测试供应商",
        }

        # 模拟待付款应付账款
        self.supplier_dao.get_pending_payables.return_value = [
            {"id": 1, "amount": 20000}
        ]

        # 模拟插入付款记录
        self.supplier_dao.insert_supplier_payment.return_value = 1

        # 执行测试（应该成功但有警告日志）
        result = self.supplier_finance_service.record_supplier_payment(
            supplier_id, payment_data
        )

        # 验证结果
        self.assertEqual(result, 1)

    def test_manage_payment_terms_success(self):
        """测试成功管理账期设置"""
        supplier_id = 1
        terms_data = {"payment_days": 30, "payment_method": "月结30天"}

        # 模拟供应商存在
        self.supplier_dao.get_by_id.return_value = {
            "id": supplier_id,
            "name": "测试供应商",
        }

        # 模拟插入账期设置
        self.supplier_dao.insert_payment_terms.return_value = 1

        # 执行测试
        result = self.supplier_finance_service.manage_payment_terms(
            supplier_id, terms_data
        )

        # 验证结果
        self.assertEqual(result, 1)
        self.supplier_dao.insert_payment_terms.assert_called_once()

    def test_manage_payment_terms_invalid_days(self):
        """测试无效账期天数"""
        supplier_id = 1
        terms_data = {
            "payment_days": -10,  # 无效天数
            "payment_method": "月结30天",
        }

        # 模拟供应商存在
        self.supplier_dao.get_by_id.return_value = {
            "id": supplier_id,
            "name": "测试供应商",
        }

        # 执行测试并验证异常
        with self.assertRaises(ValidationError) as context:
            self.supplier_finance_service.manage_payment_terms(supplier_id, terms_data)

        self.assertIn("账期天数不能为负数", str(context.exception))

    def test_assess_supplier_payment_risk_success(self):
        """测试供应商付款风险评估"""
        supplier_id = 1

        # 模拟供应商存在
        self.supplier_dao.get_by_id.return_value = {
            "id": supplier_id,
            "name": "测试供应商",
        }

        # 模拟财务数据
        self.supplier_dao.get_payables.return_value = [
            {"id": 1, "amount": 20000, "due_date": "2025-01-01", "status": "pending"}
        ]
        self.supplier_dao.get_supplier_payments.return_value = [
            {"id": 1, "amount": 15000}
        ]
        self.supplier_dao.get_payment_terms.return_value = {"payment_days": 30}

        # 执行测试
        result = self.supplier_finance_service.assess_supplier_payment_risk(supplier_id)

        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertEqual(result["supplier_id"], supplier_id)
        self.assertIn("risk_score", result)
        self.assertIn("risk_level", result)
        self.assertIn("warnings", result)

    def test_get_supplier_financial_summary_success(self):
        """测试获取供应商财务汇总"""
        supplier_id = 1

        # 模拟供应商存在
        self.supplier_dao.get_by_id.return_value = {
            "id": supplier_id,
            "name": "测试供应商",
        }

        # 模拟财务数据（添加due_date字段）
        self.supplier_dao.get_payables.return_value = [
            {"id": 1, "amount": 20000, "status": "pending", "due_date": "2026-03-01"},
            {"id": 2, "amount": 15000, "status": "paid", "due_date": "2025-12-01"},
        ]
        self.supplier_dao.get_supplier_payments.return_value = [
            {"id": 1, "amount": 15000}
        ]
        self.supplier_dao.get_payment_terms.return_value = {"payment_days": 30}

        # 执行测试
        result = self.supplier_finance_service.get_supplier_financial_summary(
            supplier_id
        )

        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertEqual(result["supplier_id"], supplier_id)
        self.assertEqual(result["total_payables"], 35000.0)
        self.assertEqual(result["pending_payables"], 20000.0)
        self.assertEqual(result["total_payments"], 15000.0)

    def test_calculate_supplier_overdue_amount(self):
        """测试计算供应商逾期金额"""
        payables = [
            {
                "amount": 20000,
                "due_date": "2024-12-01",  # 已逾期
                "status": "pending",
            },
            {
                "amount": 10000,
                "due_date": "2026-03-01",  # 未逾期（明年）
                "status": "pending",
            },
            {
                "amount": 5000,
                "due_date": "2024-11-01",  # 已逾期但已付款
                "status": "paid",
            },
        ]

        # 执行测试
        overdue_amount = (
            self.supplier_finance_service._calculate_supplier_overdue_amount(payables)
        )

        # 验证结果（只有第一个记录是逾期且未付款的）
        self.assertEqual(overdue_amount, Decimal("20000"))

    def test_calculate_supplier_payment_score(self):
        """测试计算供应商付款历史评分"""
        payments = [{"id": 1, "amount": 10000}, {"id": 2, "amount": 15000}]

        # 执行测试
        score = self.supplier_finance_service._calculate_supplier_payment_score(
            payments
        )

        # 验证结果
        self.assertEqual(score, 10.0)  # 2 * 5

    def test_calculate_terms_compliance(self):
        """测试计算账期遵守情况"""
        payables = [
            {
                "due_date": "2024-12-01",  # 已逾期
                "status": "pending",
            },
            {
                "due_date": "2026-03-01",  # 未逾期（明年）
                "status": "pending",
            },
        ]
        payments = []
        payment_terms = {"payment_days": 30}

        # 执行测试
        compliance = self.supplier_finance_service._calculate_terms_compliance(
            payables, payments, payment_terms
        )

        # 验证结果（50%遵守率）
        self.assertEqual(compliance, 50.0)

    def test_determine_supplier_risk_level(self):
        """测试确定供应商风险等级"""
        # 测试各种风险等级
        self.assertEqual(
            self.supplier_finance_service._determine_supplier_risk_level(90), "低风险"
        )
        self.assertEqual(
            self.supplier_finance_service._determine_supplier_risk_level(70), "中风险"
        )
        self.assertEqual(
            self.supplier_finance_service._determine_supplier_risk_level(50), "高风险"
        )
        self.assertEqual(
            self.supplier_finance_service._determine_supplier_risk_level(30), "极高风险"
        )

    def test_generate_supplier_risk_warnings(self):
        """测试生成供应商风险预警"""
        # 执行测试
        warnings = self.supplier_finance_service._generate_supplier_risk_warnings(
            30, Decimal("10000"), 70.0
        )

        # 验证结果
        self.assertIsInstance(warnings, list)
        self.assertTrue(any("供应商付款风险极高" in w for w in warnings))
        self.assertTrue(any("逾期应付账款" in w for w in warnings))
        self.assertTrue(any("账期遵守率较低" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()
