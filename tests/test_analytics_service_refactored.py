"""
MiniCRM 重构后分析服务测试

测试拆分后的分析服务架构是否正常工作
"""

import unittest
from unittest.mock import Mock

from minicrm.services.analytics_service import AnalyticsService


class TestAnalyticsServiceRefactored(unittest.TestCase):
    """测试重构后的分析服务"""

    def setUp(self):
        """设置测试环境"""
        self.mock_customer_dao = Mock()
        self.mock_supplier_dao = Mock()

        # 设置基本的模拟返回值
        self.mock_customer_dao.get_statistics.return_value = {
            "total_customers": 100,
            "new_this_month": 10,
            "active_customers": 80,
            "growth_rate": 5.0,
        }

        self.mock_supplier_dao.get_statistics.return_value = {
            "total_suppliers": 50,
            "active_suppliers": 40,
        }

        self.mock_customer_dao.search.return_value = [
            {"id": 1, "name": "客户A", "level": "VIP"},
            {"id": 2, "name": "客户B", "level": "普通"},
        ]

        self.mock_supplier_dao.search.return_value = [
            {"id": 1, "name": "供应商A", "quality_score": 90},
            {"id": 2, "name": "供应商B", "quality_score": 75},
        ]

        self.analytics_service = AnalyticsService(
            self.mock_customer_dao, self.mock_supplier_dao
        )

    def test_service_initialization(self):
        """测试服务初始化"""
        self.assertIsNotNone(self.analytics_service)
        self.assertIsNotNone(self.analytics_service._dashboard_service)
        self.assertIsNotNone(self.analytics_service._customer_analytics_service)
        self.assertIsNotNone(self.analytics_service._supplier_analytics_service)
        self.assertIsNotNone(self.analytics_service._trend_analysis_service)
        self.assertIsNotNone(self.analytics_service._prediction_service)

    def test_get_dashboard_data(self):
        """测试获取仪表盘数据"""
        result = self.analytics_service.get_dashboard_data()

        self.assertIsInstance(result, dict)
        self.assertIn("metrics", result)
        self.assertIn("charts", result)
        self.assertIn("quick_actions", result)
        self.assertIn("alerts", result)

    def test_get_customer_analysis(self):
        """测试获取客户分析"""
        result = self.analytics_service.get_customer_analysis()

        self.assertEqual(type(result).__name__, "CustomerAnalysis")
        self.assertGreaterEqual(result.total_customers, 0)

    def test_get_supplier_analysis(self):
        """测试获取供应商分析"""
        result = self.analytics_service.get_supplier_analysis()

        self.assertEqual(type(result).__name__, "SupplierAnalysis")
        self.assertGreaterEqual(result.total_suppliers, 0)

    def test_get_business_trend_analysis(self):
        """测试获取业务趋势分析"""
        result = self.analytics_service.get_business_trend_analysis(
            "customer_growth", "monthly"
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.metric_name, "customer_growth")
        self.assertEqual(result.period, "monthly")

    def test_get_prediction(self):
        """测试获取预测分析"""
        result = self.analytics_service.get_prediction("customer_growth", 6)

        self.assertIsNotNone(result)
        self.assertEqual(result.metric_name, "customer_growth")
        self.assertGreater(len(result.predicted_values), 0)

    def test_cache_functionality(self):
        """测试缓存功能"""
        # 测试缓存统计
        stats = self.analytics_service.get_cache_statistics()
        self.assertIsInstance(stats, dict)

        # 测试缓存清理
        self.analytics_service.clear_cache()
        # 应该不抛出异常

    def test_cleanup(self):
        """测试资源清理"""
        self.analytics_service.cleanup()
        # 应该不抛出异常


if __name__ == "__main__":
    unittest.main()
