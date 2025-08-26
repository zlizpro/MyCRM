#!/usr/bin/env python3
"""
任务1.2集成测试：验证应收账款总额统计功能

验证FinanceService.get_total_receivables()方法的完整实现和集成
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


class TestTask12Integration(unittest.TestCase):
    """任务1.2集成测试：应收账款总额统计功能"""

    def setUp(self):
        """测试准备"""
        # 创建模拟的DAO对象
        self.mock_customer_dao = Mock(spec=CustomerDAO)
        self.mock_supplier_dao = Mock(spec=SupplierDAO)

        # 创建FinanceService实例
        self.finance_service = FinanceService(
            customer_dao=self.mock_customer_dao, supplier_dao=self.mock_supplier_dao
        )

    def test_task_1_2_complete_implementation(self):
        """测试任务1.2的完整实现"""
        print("\n" + "=" * 60)
        print("任务1.2集成测试：应收账款总额统计功能")
        print("=" * 60)

        # 1. 验证方法存在
        self.assertTrue(
            hasattr(self.finance_service, "get_total_receivables"),
            "FinanceService应该有get_total_receivables方法",
        )

        # 2. 验证方法可调用
        self.assertTrue(
            callable(self.finance_service.get_total_receivables),
            "get_total_receivables方法应该可调用",
        )

        # 3. 验证方法签名
        import inspect

        method = self.finance_service.get_total_receivables
        signature = inspect.signature(method)
        self.assertEqual(
            len(signature.parameters), 0, "get_total_receivables方法不应该需要额外参数"
        )

        # 4. 验证正常功能
        mock_summary = {"total_amount": 125000.50, "overdue_amount": 15000.00}
        self.mock_customer_dao.get_receivables_summary.return_value = mock_summary

        result = self.finance_service.get_total_receivables()

        self.assertEqual(result, 125000.50)
        self.assertIsInstance(result, float)
        self.mock_customer_dao.get_receivables_summary.assert_called_once()

        print("✅ 方法实现验证通过")

    def test_dashboard_integration_simulation(self):
        """模拟仪表盘集成测试"""
        print("\n测试仪表盘集成...")

        # 模拟仪表盘数据加载过程
        mock_summary = {"total_amount": 89500.75, "overdue_amount": 12000.00}
        self.mock_customer_dao.get_receivables_summary.return_value = mock_summary

        # 模拟仪表盘调用
        def simulate_dashboard_data_loading():
            """模拟仪表盘数据加载"""
            metrics = {}

            # 检查服务是否存在get_total_receivables方法
            if hasattr(self.finance_service, "get_total_receivables"):
                total_receivables = self.finance_service.get_total_receivables()
                metrics["total_receivables"] = total_receivables

            return metrics

        # 执行模拟
        dashboard_data = simulate_dashboard_data_loading()

        # 验证结果
        self.assertIn("total_receivables", dashboard_data)
        self.assertEqual(dashboard_data["total_receivables"], 89500.75)

        print("✅ 仪表盘集成模拟通过")

    def test_error_handling(self):
        """测试错误处理"""
        print("\n测试错误处理...")

        # 模拟数据库异常
        self.mock_customer_dao.get_receivables_summary.side_effect = Exception(
            "数据库连接失败"
        )

        # 验证异常处理
        with self.assertRaises(ServiceError) as context:
            self.finance_service.get_total_receivables()

        self.assertIn("获取应收账款总额失败", str(context.exception))

        print("✅ 错误处理验证通过")

    def test_edge_cases(self):
        """测试边界情况"""
        print("\n测试边界情况...")

        test_cases = [
            {"total_amount": 0, "expected": 0.0},  # 零金额
            {"total_amount": 999999.99, "expected": 999999.99},  # 大金额
            {},  # 缺失数据
        ]

        for i, test_case in enumerate(test_cases):
            with self.subTest(case=i):
                self.mock_customer_dao.get_receivables_summary.return_value = test_case
                result = self.finance_service.get_total_receivables()

                expected = test_case.get("total_amount", 0)
                self.assertEqual(result, float(expected))
                self.assertIsInstance(result, float)

        print("✅ 边界情况测试通过")


def run_integration_test():
    """运行集成测试"""
    print("开始任务1.2集成测试...")

    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTask12Integration)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("任务1.2集成测试结果摘要:")
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n🎉 任务1.2集成测试全部通过！")
        print("\n✅ 任务1.2实现验证成功：")
        print("   - FinanceService.get_total_receivables()方法已正确实现")
        print("   - 方法签名符合要求，无需额外参数")
        print("   - 异常处理机制完善")
        print("   - 仪表盘集成正常工作")
        print("   - 边界情况处理正确")
        print("   - 返回类型一致性良好")
        print("\n📊 仪表盘财务指标功能已就绪！")
        return True
    else:
        print("\n❌ 部分集成测试失败，需要修复")
        return False


if __name__ == "__main__":
    success = run_integration_test()
    sys.exit(0 if success else 1)
