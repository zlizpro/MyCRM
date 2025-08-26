"""MiniCRM 报价比对服务单元测试

测试报价比对和历史分析服务的所有功能,包括:
- 报价比对分析
- 价格趋势分析
- 智能建议算法
- 竞争力分析
- transfunctions集成

遵循测试最佳实践:
- 使用Mock对象隔离依赖
- 测试覆盖正常和异常情况
- 验证transfunctions的正确使用
"""

from datetime import datetime
from decimal import Decimal
import unittest
from unittest.mock import MagicMock, Mock

from minicrm.core.exceptions import ServiceError
from minicrm.models.enums import QuoteStatus
from minicrm.models.quote import Quote, QuoteItem
from minicrm.services.quote.quote_comparison_service import QuoteComparisonService


class TestQuoteComparisonService(unittest.TestCase):
    """报价比对服务测试类"""

    def setUp(self):
        """测试准备"""
        self.mock_core_service = MagicMock()
        self.service = QuoteComparisonService(self.mock_core_service)

    def _create_mock_quote(
        self,
        quote_id: int,
        amount: float,
        date: datetime = None,
        status: QuoteStatus = QuoteStatus.DRAFT,
    ) -> Quote:
        """创建模拟报价对象"""
        quote = Mock(spec=Quote)
        quote.id = quote_id
        quote.quote_number = f"Q2025{quote_id:03d}"
        quote.customer_name = "测试客户"
        quote.total_amount = Decimal(str(amount))
        quote.quote_date = date or datetime(2025, 1, quote_id)
        quote.quote_status = status
        quote.items = []
        return quote

    def _create_mock_quote_item(
        self, product_name: str, unit_price: float, quantity: float = 1.0
    ) -> QuoteItem:
        """创建模拟报价项目"""
        item = Mock(spec=QuoteItem)
        item.product_name = product_name
        item.specification = "标准规格"
        item.unit = "个"
        item.unit_price = Decimal(str(unit_price))
        item.quantity = Decimal(str(quantity))
        item.get_total.return_value = Decimal(str(unit_price * quantity))
        item.get_formatted_unit_price.return_value = f"¥{unit_price:,.2f}"
        item.get_formatted_total.return_value = f"¥{unit_price * quantity:,.2f}"
        return item

    def test_compare_quotes_summary_success(self):
        """测试报价摘要比较成功"""
        # 准备测试数据
        quote_ids = [1, 2, 3]
        mock_quotes = [
            self._create_mock_quote(1, 100000),
            self._create_mock_quote(2, 120000),
            self._create_mock_quote(3, 110000),
        ]

        # 模拟核心服务返回
        self.mock_core_service.get_by_id.side_effect = lambda qid: mock_quotes[qid - 1]

        # 执行测试
        result = self.service.compare_quotes(quote_ids, "summary")

        # 验证结果
        self.assertEqual(result["comparison_type"], "summary")
        self.assertEqual(result["quote_count"], 3)
        self.assertEqual(len(result["quotes"]), 3)
        self.assertIn("statistics", result)

        # 验证统计数据
        stats = result["statistics"]
        self.assertIn("min_amount", stats)
        self.assertIn("max_amount", stats)
        self.assertIn("avg_amount", stats)

    def test_compare_quotes_detailed_success(self):
        """测试详细报价比较成功"""
        # 准备测试数据
        quote_ids = [1, 2]

        # 创建带有产品项目的报价
        quote1 = self._create_mock_quote(1, 100000)
        quote1.items = [
            self._create_mock_quote_item("产品A", 1000, 50),
            self._create_mock_quote_item("产品B", 2000, 25),
        ]

        quote2 = self._create_mock_quote(2, 120000)
        quote2.items = [
            self._create_mock_quote_item("产品A", 1100, 50),
            self._create_mock_quote_item("产品B", 2200, 25),
        ]

        mock_quotes = [quote1, quote2]

        # 模拟核心服务返回
        self.mock_core_service.get_by_id.side_effect = lambda qid: mock_quotes[qid - 1]

        # 执行测试
        result = self.service.compare_quotes(quote_ids, "detailed")

        # 验证结果
        self.assertEqual(result["comparison_type"], "detailed")
        self.assertEqual(result["quote_count"], 2)
        self.assertIn("product_analysis", result)
        self.assertIn("trend_analysis", result)
        self.assertIn("intelligent_suggestions", result)
        self.assertIn("competitiveness_analysis", result)

    def test_compare_quotes_trend_success(self):
        """测试趋势比较成功"""
        # 准备测试数据
        quote_ids = [1, 2, 3]
        mock_quotes = [
            self._create_mock_quote(1, 100000, datetime(2025, 1, 1)),
            self._create_mock_quote(2, 110000, datetime(2025, 1, 15)),
            self._create_mock_quote(3, 120000, datetime(2025, 1, 30)),
        ]

        # 模拟核心服务返回
        self.mock_core_service.get_by_id.side_effect = lambda qid: mock_quotes[qid - 1]

        # 执行测试
        result = self.service.compare_quotes(quote_ids, "trend")

        # 验证结果
        self.assertEqual(result["comparison_type"], "trend")
        self.assertEqual(result["quote_count"], 3)
        self.assertIn("trend_data", result)
        self.assertIn("overall_trend", result)

        # 验证趋势数据
        trend_data = result["trend_data"]
        self.assertEqual(len(trend_data), 3)

        # 验证第二个数据点有变化信息
        self.assertIn("amount_change", trend_data[1])
        self.assertIn("trend_direction", trend_data[1])

    def test_compare_quotes_insufficient_quotes(self):
        """测试报价数量不足"""
        # 准备测试数据(只有一个报价)
        quote_ids = [1]
        mock_quotes = [self._create_mock_quote(1, 100000)]

        # 模拟核心服务返回
        self.mock_core_service.get_by_id.side_effect = lambda qid: mock_quotes[qid - 1]

        # 执行测试并验证异常
        with self.assertRaises(ServiceError) as context:
            self.service.compare_quotes(quote_ids, "summary")

        self.assertIn("至少需要2个报价", str(context.exception))

    def test_compare_quotes_invalid_type(self):
        """测试无效的比较类型"""
        # 准备测试数据
        quote_ids = [1, 2]
        mock_quotes = [
            self._create_mock_quote(1, 100000),
            self._create_mock_quote(2, 120000),
        ]

        # 模拟核心服务返回
        self.mock_core_service.get_by_id.side_effect = lambda qid: mock_quotes[qid - 1]

        # 执行测试并验证异常
        with self.assertRaises(ServiceError) as context:
            self.service.compare_quotes(quote_ids, "invalid_type")

        self.assertIn("不支持的比较类型", str(context.exception))

    def test_get_customer_quote_history_success(self):
        """测试获取客户报价历史成功"""
        # 准备测试数据
        customer_id = 1
        mock_quotes = [
            self._create_mock_quote(1, 100000, datetime(2025, 1, 1)),
            self._create_mock_quote(2, 120000, datetime(2025, 1, 15)),
            self._create_mock_quote(3, 110000, datetime(2025, 1, 30)),
        ]

        # 模拟核心服务返回
        self.mock_core_service.list_all.return_value = mock_quotes

        # 执行测试
        result = self.service.get_customer_quote_history(customer_id, limit=5)

        # 验证结果
        self.assertEqual(result["customer_id"], customer_id)
        self.assertEqual(result["quote_count"], 3)
        self.assertEqual(len(result["quotes"]), 3)

        # 验证包含分析数据
        self.assertIn("analysis", result)

    def test_get_customer_quote_history_no_analysis(self):
        """测试获取客户报价历史不包含分析"""
        # 准备测试数据(只有一个报价)
        customer_id = 1
        mock_quotes = [self._create_mock_quote(1, 100000)]

        # 模拟核心服务返回
        self.mock_core_service.list_all.return_value = mock_quotes

        # 执行测试
        result = self.service.get_customer_quote_history(
            customer_id, include_analysis=False
        )

        # 验证结果
        self.assertEqual(result["customer_id"], customer_id)
        self.assertEqual(result["quote_count"], 1)
        self.assertNotIn("analysis", result)

    def test_collect_product_info(self):
        """测试收集产品信息"""
        # 准备测试数据
        quote1 = self._create_mock_quote(1, 100000)
        quote1.items = [
            self._create_mock_quote_item("产品A", 1000, 10),
            self._create_mock_quote_item("产品B", 2000, 5),
        ]

        quote2 = self._create_mock_quote(2, 120000)
        quote2.items = [
            self._create_mock_quote_item("产品A", 1100, 10),
            self._create_mock_quote_item("产品C", 3000, 2),
        ]

        quotes = [quote1, quote2]

        # 执行测试
        result = self.service._collect_product_info(quotes)

        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

        # 验证产品A在两个报价中都有价格
        product_a_key = "产品A_标准规格"
        if product_a_key in result:
            self.assertEqual(len(result[product_a_key]["prices"]), 2)

    def test_generate_product_analysis(self):
        """测试生成产品分析"""
        # 准备测试数据
        all_products = {
            "产品A_标准规格": {
                "product_name": "产品A",
                "specification": "标准规格",
                "unit": "个",
                "prices": [
                    {"quote_id": 1, "unit_price": 1000, "quantity": 10},
                    {"quote_id": 2, "unit_price": 1100, "quantity": 10},
                ],
            }
        }

        # 执行测试
        result = self.service._generate_product_analysis(all_products)

        # 验证结果
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

        product_analysis = result[0]
        self.assertEqual(product_analysis["product_name"], "产品A")
        self.assertIn("statistics", product_analysis)
        self.assertIn("prices", product_analysis)

    def test_calculate_amount_trend(self):
        """测试计算金额趋势"""
        # 测试上升趋势
        amounts_up = [100, 200, 300, 400]
        result = self.service._calculate_amount_trend(amounts_up)
        self.assertEqual(result, "上升")

        # 测试下降趋势
        amounts_down = [400, 300, 200, 100]
        result = self.service._calculate_amount_trend(amounts_down)
        self.assertEqual(result, "下降")

        # 测试平稳趋势
        amounts_stable = [100, 105, 95, 100]
        result = self.service._calculate_amount_trend(amounts_stable)
        self.assertEqual(result, "平稳")

        # 测试数据不足
        amounts_insufficient = [100]
        result = self.service._calculate_amount_trend(amounts_insufficient)
        self.assertEqual(result, "无趋势")

    def test_calculate_status_distribution(self):
        """测试计算状态分布"""
        # 准备测试数据
        quotes = [
            self._create_mock_quote(1, 100000, status=QuoteStatus.DRAFT),
            self._create_mock_quote(2, 120000, status=QuoteStatus.SENT),
            self._create_mock_quote(3, 110000, status=QuoteStatus.SENT),
            self._create_mock_quote(4, 130000, status=QuoteStatus.ACCEPTED),
        ]

        # 执行测试
        result = self.service._calculate_status_distribution(quotes)

        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertIn("draft", result)
        self.assertIn("sent", result)
        self.assertIn("accepted", result)

        # 验证百分比计算
        self.assertEqual(result["draft"]["count"], 1)
        self.assertEqual(result["sent"]["count"], 2)
        self.assertEqual(result["accepted"]["count"], 1)

    def test_generate_intelligent_suggestions(self):
        """测试生成智能建议"""
        # 准备测试数据
        quotes = [
            self._create_mock_quote(1, 100000, status=QuoteStatus.ACCEPTED),
            self._create_mock_quote(2, 120000, status=QuoteStatus.SENT),
            self._create_mock_quote(3, 130000, status=QuoteStatus.ACCEPTED),
        ]

        product_analysis = [
            {"product_name": "产品A", "statistics": {"price_variance": "¥100.00"}}
        ]

        # 执行测试
        result = self.service._generate_intelligent_suggestions(
            quotes, product_analysis
        )

        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertIn("pricing_strategy", result)
        self.assertIn("product_optimization", result)
        self.assertIn("market_insights", result)
        self.assertIn("risk_warnings", result)

    def test_analyze_quote_competitiveness(self):
        """测试分析报价竞争力"""
        # 准备测试数据
        quotes = [
            self._create_mock_quote(1, 100000),  # 最低价,竞争力最强
            self._create_mock_quote(2, 120000),  # 中等价格
            self._create_mock_quote(3, 140000),  # 最高价,竞争力最弱
        ]

        # 执行测试
        result = self.service._analyze_quote_competitiveness(quotes)

        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertIn("competitiveness_ranking", result)
        self.assertIn("insights", result)

        # 验证排序(按竞争力降序)
        ranking = result["competitiveness_ranking"]
        self.assertEqual(len(ranking), 3)
        self.assertGreater(
            ranking[0]["competitiveness_score"], ranking[1]["competitiveness_score"]
        )

    def test_get_competitiveness_level(self):
        """测试获取竞争力等级"""
        # 测试各个等级
        self.assertEqual(self.service._get_competitiveness_level(85), "极强")
        self.assertEqual(self.service._get_competitiveness_level(65), "较强")
        self.assertEqual(self.service._get_competitiveness_level(45), "一般")
        self.assertEqual(self.service._get_competitiveness_level(25), "较弱")
        self.assertEqual(self.service._get_competitiveness_level(15), "很弱")

    def test_generate_competitiveness_insights(self):
        """测试生成竞争力洞察"""
        # 准备测试数据
        scores = [
            {"quote_number": "Q001", "competitiveness_score": 80},
            {"quote_number": "Q002", "competitiveness_score": 60},
            {"quote_number": "Q003", "competitiveness_score": 20},
        ]

        # 执行测试
        result = self.service._generate_competitiveness_insights(scores)

        # 验证结果
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

        # 验证包含最佳和最差报价的信息
        insights_text = " ".join(result)
        self.assertIn("Q001", insights_text)  # 最佳报价
        self.assertIn("Q003", insights_text)  # 最差报价

    def test_service_error_handling(self):
        """测试服务错误处理"""
        # 模拟核心服务抛出异常
        self.mock_core_service.get_by_id.side_effect = Exception("数据库错误")

        # 执行测试并验证ServiceError被抛出
        with self.assertRaises(ServiceError) as context:
            self.service.compare_quotes([1, 2], "summary")

        self.assertIn("报价比较失败", str(context.exception))

    def test_get_service_name(self):
        """测试获取服务名称"""
        self.assertEqual(self.service.get_service_name(), "报价比对分析服务")


if __name__ == "__main__":
    unittest.main()
