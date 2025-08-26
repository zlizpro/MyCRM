#!/usr/bin/env python3
"""
FinanceService.get_total_receivables方法单元测试

验证任务1.2的实现：在FinanceService中添加get_total_receivables方法
"""

import os
import sys
import unittest
from unittest.mock import Mock


# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from minicrm.core.exceptions import ServiceError
from minicrm.data.dao.customer_dao import CustomerDAO
from minicrm.data.dao.supplier_dao import SupplierDAO
from minicrm.services.finance_service import FinanceService


class TestFinanceServiceGetTotalReceivables(unittest.TestCase):
    """FinanceService.get_total_receivables方法单元测试"""

    def setUp(self):
        """测试准备"""
        # 创建模拟的DAO对象
        self.mock_customer_dao = Mock(spec=CustomerDAO)
        self.mock_supplier_dao = Mock(spec=SupplierDAO)

        # 创建FinanceService实例
        self.finance_service = FinanceService(
            customer_dao=self.mock_customer_dao, supplier_dao=self.mock_supplier_dao
        )

    def test_get_total_receivables_success(self):
        """测试获取应收账款总额成功"""
        # 模拟DAO返回应收账款汇总
        mock_summary = {"total_amount": 125000.50, "overdue_amount": 15000.00}
        self.mock_customer_dao.get_receivables_summary.return_value = mock_summary

        # 执行测试
        result = self.finance_service.get_total_receivables()

        # 验证结果
        self.assertEqual(result, 125000.50)
        self.assertIsInstance(result, float)
        self.mock_customer_dao.get_receivables_summary.assert_called_once()

    def test_get_total_receivables_zero(self):
        """测试获取应收账款总额为零"""
        # 模拟DAO返回零应收账款
        mock_summary = {"total_amount": 0, "overdue_amount": 0}
        self.mock_customer_dao.get_receivables_summary.return_value = mock_summary

        # 执行测试
        result = self.finance_service.get_total_receivables()

        # 验证结果
        self.assertEqual(result, 0.0)
        self.assertIsInstance(result, float)

    def test_get_total_receivables_missing_data(self):
        """测试获取应收账款总额时数据缺失"""
        # 模拟DAO返回不完整数据
        mock_summary = {}
        self.mock_customer_dao.get_receivables_summary.return_value = mock_summary

        # 执行测试
        result = self.finance_service.get_total_receivables()

        # 验证结果（应该返回默认值0）
        self.assertEqual(result, 0.0)
        self.assertIsInstance(result, float)

    def test_get_total_receivables_database_error(self):
        """测试获取应收账款总额时数据库错误"""
        # 模拟数据库异常
        self.mock_customer_dao.get_receivables_summary.side_effect = Exception(
            "数据库连接失败"
        )

        # 执行测试并验证异常
        with self.assertRaises(ServiceError) as context:
            self.finance_service.get_total_receivables()

        # 验证异常信息
        self.assertIn("获取应收账款总额失败", str(context.exception))

    def test_method_exists_and_callable(self):
        """测试方法存在且可调用"""
        # 验证方法存在
        self.assertTrue(hasattr(self.finance_service, "get_total_receivables"))

        # 验证方法可调用
        self.assertTrue(callable(self.finance_service.get_total_receivables))

        # 验证方法签名（不需要额外参数）
        import inspect

        method = self.finance_service.get_total_receivables
        signature = inspect.signature(method)
        self.assertEqual(len(signature.parameters), 0)  # 不包括self

    def test_return_type_consistency(self):
        """测试返回类型一致性"""
        test_cases = [
            {"total_amount": 100.50},
            {"total_amount": 0},
            {"total_amount": 999999.99},
            {},  # 缺失数据的情况
        ]

        for test_data in test_cases:
            with self.subTest(test_data=test_data):
                self.mock_customer_dao.get_receivables_summary.return_value = test_data
                result = self.finance_service.get_total_receivables()

                # 验证返回类型始终为float
                self.assertIsInstance(result, float)
                expected_value = float(test_data.get("total_amount", 0))
                self.assertEqual(result, expected_value)


def run_test():
    """运行测试"""
    print("=" * 60)
    print("FinanceService.get_total_receivables方法单元测试")
    print("=" * 60)

    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestFinanceServiceGetTotalReceivables
    )

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要:")
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ 所有单元测试通过！")
        print("✅ 任务1.2实现验证成功：")
        print("   - FinanceService.get_total_receivables()方法已正确实现")
        print("   - 方法签名符合要求")
        print("   - 异常处理机制完善")
        print("   - 返回类型一致性良好")
        return True
    else:
        print("\n❌ 部分单元测试失败，需要修复")
        return False


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
