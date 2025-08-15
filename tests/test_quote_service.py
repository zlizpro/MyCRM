"""
报价服务单元测试

测试报价管理服务的所有功能，包括：
- 基础CRUD操作
- 报价比对功能
- 历史分析功能
- 智能建议算法
- 成功率统计
- 过期管理
"""

import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from minicrm.core import BusinessLogicError, ServiceError, ValidationError
from minicrm.models import Quote, QuoteStatus
from minicrm.services.quote_service import QuoteService


class TestQuoteService(unittest.TestCase):
    """报价服务测试类"""

    def setUp(self):
        """测试准备"""
        self.mock_dao = MagicMock()
        self.quote_service = QuoteService(self.mock_dao)

        # 准备测试数据
        self.sample_quote_data = {
            "name": "测试报价单",  # 添加必需的name字段
            "customer_name": "测试客户",
            "contact_person": "张经理",
            "items": [
                {
                    "product_name": "生态板",
                    "specification": "18mm",
                    "quantity": 100,
                    "unit_price": 150.0,
                    "unit": "张",
                }
            ],
            "payment_terms": "货到付款",
            "delivery_terms": "送货上门",
        }

        self.sample_quote = Quote.from_dict(self.sample_quote_data)
        self.sample_quote.id = 1

    def test_service_name(self):
        """测试服务名称"""
        self.assertEqual(self.quote_service.get_service_name(), "报价管理服务")

    # ==================== 基础CRUD测试 ====================

    def test_create_quote_success(self):
        """测试成功创建报价"""
        self.mock_dao.insert.return_value = 1

        result = self.quote_service.create(self.sample_quote_data)

        self.assertIsInstance(result, Quote)
        self.assertEqual(result.customer_name, "测试客户")
        self.assertEqual(len(result.items), 1)
        self.mock_dao.insert.assert_called_once()

    def test_create_quote_validation_error(self):
        """测试创建报价验证错误"""
        invalid_data = {"customer_name": ""}  # 缺少必填字段

        with self.assertRaises(ValidationError):
            self.quote_service.create(invalid_data)

    def test_create_quote_empty_items(self):
        """测试创建报价时项目为空"""
        invalid_data = self.sample_quote_data.copy()
        invalid_data["items"] = []

        with self.assertRaises(ValidationError):
            self.quote_service.create(invalid_data)

    def test_get_quote_by_id_success(self):
        """测试成功获取报价"""
        self.mock_dao.get_by_id.return_value = self.sample_quote.to_dict()

        result = self.quote_service.get_by_id(1)

        self.assertIsInstance(result, Quote)
        self.assertEqual(result.customer_name, "测试客户")
        self.mock_dao.get_by_id.assert_called_once_with(1)

    def test_get_quote_by_id_not_found(self):
        """测试获取不存在的报价"""
        self.mock_dao.get_by_id.return_value = None

        result = self.quote_service.get_by_id(999)

        self.assertIsNone(result)

    def test_update_quote_success(self):
        """测试成功更新报价"""
        self.mock_dao.get_by_id.return_value = self.sample_quote.to_dict()
        self.mock_dao.update.return_value = True

        update_data = {"contact_person": "李经理"}
        result = self.quote_service.update(1, update_data)

        self.assertIsInstance(result, Quote)
        self.assertEqual(result.contact_person, "李经理")
        self.mock_dao.update.assert_called_once()

    def test_update_quote_not_found(self):
        """测试更新不存在的报价"""
        self.mock_dao.get_by_id.return_value = None

        with self.assertRaises(BusinessLogicError):
            self.quote_service.update(999, {"contact_person": "李经理"})

    def test_delete_quote_success(self):
        """测试成功删除报价"""
        self.mock_dao.get_by_id.return_value = self.sample_quote.to_dict()
        self.mock_dao.delete.return_value = True

        result = self.quote_service.delete(1)

        self.assertTrue(result)
        self.mock_dao.delete.assert_called_once_with(1)

    def test_delete_accepted_quote_error(self):
        """测试删除已接受的报价"""
        accepted_quote = self.sample_quote.copy()
        accepted_quote.quote_status = QuoteStatus.ACCEPTED
        self.mock_dao.get_by_id.return_value = accepted_quote.to_dict()

        with self.assertRaises(BusinessLogicError):
            self.quote_service.delete(1)

    def test_list_all_quotes(self):
        """测试获取所有报价"""
        quote_data_list = [self.sample_quote.to_dict()]
        self.mock_dao.search.return_value = quote_data_list

        result = self.quote_service.list_all()

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], Quote)

    # ==================== 报价比对测试 ====================

    def test_compare_quotes_summary(self):
        """测试报价摘要比较"""
        # 模拟DAO返回基础数据，避免计算字段问题
        quote1_basic = {
            "id": 1,
            "name": "报价1",
            "customer_name": "测试客户",
            "total_amount": 15000,
            "quote_status": "draft",
            "items": [
                {
                    "product_name": "生态板",
                    "specification": "18mm",
                    "quantity": 100,
                    "unit_price": 150.0,
                    "unit": "张",
                }
            ],
        }
        quote2_basic = {
            "id": 2,
            "name": "报价2",
            "customer_name": "测试客户",
            "total_amount": 18000,
            "quote_status": "draft",
            "items": [
                {
                    "product_name": "生态板",
                    "specification": "18mm",
                    "quantity": 120,
                    "unit_price": 150.0,
                    "unit": "张",
                }
            ],
        }

        self.mock_dao.get_by_id.side_effect = [quote1_basic, quote2_basic]

        result = self.quote_service.compare_quotes([1, 2], "summary")

        self.assertEqual(result["comparison_type"], "summary")
        self.assertEqual(result["quote_count"], 2)
        self.assertIn("statistics", result)
        self.assertIn("quotes", result)

    def test_compare_quotes_insufficient_data(self):
        """测试比较报价数据不足"""
        with self.assertRaises(ValidationError):
            self.quote_service.compare_quotes([1])

    def test_compare_quotes_not_found(self):
        """测试比较不存在的报价"""
        self.mock_dao.get_by_id.return_value = None

        with self.assertRaises(BusinessLogicError):
            self.quote_service.compare_quotes([1, 2])

    def test_compare_quotes_detailed(self):
        """测试详细报价比较"""
        # 准备测试数据
        quote1 = self.sample_quote.copy()
        quote1.id = 1

        quote2 = self.sample_quote.copy()
        quote2.id = 2
        quote2.items[0].unit_price = Decimal("160")  # 不同价格

        self.mock_dao.get_by_id.side_effect = [quote1.to_dict(), quote2.to_dict()]

        result = self.quote_service.compare_quotes([1, 2], "detailed")

        self.assertEqual(result["comparison_type"], "detailed")
        self.assertIn("product_analysis", result)
        self.assertTrue(len(result["product_analysis"]) > 0)

    def test_compare_quotes_trend(self):
        """测试报价趋势比较"""
        # 准备有日期的报价
        quote1 = self.sample_quote.copy()
        quote1.id = 1
        quote1.quote_date = datetime.now() - timedelta(days=30)
        quote1.total_amount = Decimal("15000")

        quote2 = self.sample_quote.copy()
        quote2.id = 2
        quote2.quote_date = datetime.now()
        quote2.total_amount = Decimal("18000")

        self.mock_dao.get_by_id.side_effect = [quote1.to_dict(), quote2.to_dict()]

        result = self.quote_service.compare_quotes([1, 2], "trend")

        self.assertEqual(result["comparison_type"], "trend")
        self.assertIn("trend_data", result)
        self.assertIn("statistics", result)

    def test_get_customer_quote_history(self):
        """测试获取客户报价历史"""
        quote_data_list = [self.sample_quote.to_dict()]
        self.mock_dao.search.return_value = quote_data_list

        result = self.quote_service.get_customer_quote_history(1)

        self.assertEqual(result["customer_id"], 1)
        self.assertEqual(result["quote_count"], 1)
        self.assertIn("quotes", result)

    # ==================== 智能建议测试 ====================

    @patch.object(QuoteService, "get_customer_quote_history")
    @patch.object(QuoteService, "_get_market_price_data")
    def test_generate_quote_suggestions_price(self, mock_market_data, mock_history):
        """测试生成价格建议"""
        # 模拟历史数据
        mock_history.return_value = {
            "customer_id": 1,
            "quote_count": 3,
            "quotes": [self.sample_quote.to_dict()],
            "analysis": {"success_rate": "60%", "average_response_time": "5.0天"},
        }

        # 模拟市场数据
        mock_market_data.return_value = {
            "生态板": {"average_price": 155.0, "price_trend": "stable"}
        }

        product_items = [{"product_name": "生态板"}]
        result = self.quote_service.generate_quote_suggestions(
            1, product_items, "price"
        )

        self.assertEqual(result["suggestion_type"], "price")
        self.assertIn("product_suggestions", result)
        self.assertIn("overall_strategy", result)

    @patch.object(QuoteService, "get_customer_quote_history")
    def test_generate_quote_suggestions_strategy(self, mock_history):
        """测试生成策略建议"""
        mock_history.return_value = {
            "customer_id": 1,
            "quote_count": 5,
            "quotes": [self.sample_quote.to_dict()],
            "analysis": {
                "success_rate": "20%",  # 低成功率
                "average_response_time": "10.0天",
            },
        }

        product_items = [{"product_name": "生态板"}]
        result = self.quote_service.generate_quote_suggestions(
            1, product_items, "strategy"
        )

        self.assertEqual(result["suggestion_type"], "strategy")
        self.assertIn("strategies", result)
        self.assertIn("behavior_analysis", result)

        # 检查是否有针对低成功率的建议
        strategies = result["strategies"]
        pricing_strategies = [s for s in strategies if s["type"] == "pricing"]
        self.assertTrue(len(pricing_strategies) > 0)

    @patch.object(QuoteService, "get_customer_quote_history")
    @patch.object(QuoteService, "_get_market_price_data")
    def test_generate_quote_suggestions_comprehensive(
        self, mock_market_data, mock_history
    ):
        """测试生成综合建议"""
        mock_history.return_value = {
            "customer_id": 1,
            "quote_count": 3,
            "quotes": [self.sample_quote.to_dict()],
            "analysis": {"success_rate": "60%"},
        }

        mock_market_data.return_value = {"生态板": {"average_price": 155.0}}

        product_items = [{"product_name": "生态板"}]
        result = self.quote_service.generate_quote_suggestions(
            1, product_items, "comprehensive"
        )

        self.assertEqual(result["suggestion_type"], "comprehensive")
        self.assertIn("price_suggestions", result)
        self.assertIn("strategy_suggestions", result)
        self.assertIn("overall_recommendation", result)

    def test_generate_quote_suggestions_invalid_type(self):
        """测试无效的建议类型"""
        with self.assertRaises(ValidationError):
            self.quote_service.generate_quote_suggestions(1, [], "invalid_type")

    # ==================== 成功率统计测试 ====================

    def test_calculate_success_rate_statistics(self):
        """测试计算成功率统计"""
        # 准备测试数据 - 直接创建字典数据避免copy问题
        quotes_data = []
        for i in range(10):
            quote_data = {
                "id": i + 1,
                "name": f"报价{i + 1}",
                "customer_name": "测试客户",
                "quote_date": (datetime.now() - timedelta(days=i * 10)).isoformat(),
                "total_amount": 15000,
                "items": [
                    {
                        "product_name": "生态板",
                        "specification": "18mm",
                        "quantity": 100,
                        "unit_price": 150.0,
                        "unit": "张",
                    }
                ],
            }

            # 设置不同状态
            if i < 3:
                quote_data["quote_status"] = "accepted"
            elif i < 6:
                quote_data["quote_status"] = "rejected"
            else:
                quote_data["quote_status"] = "sent"

            quotes_data.append(quote_data)

        self.mock_dao.search.return_value = quotes_data

        result = self.quote_service.calculate_success_rate_statistics()

        self.assertEqual(result["total_quotes"], 10)
        self.assertEqual(result["successful_quotes"], 3)
        self.assertIn("success_rate", result)
        self.assertIn("status_distribution", result)
        self.assertIn("monthly_trends", result)
        self.assertIn("insights", result)

    def test_calculate_success_rate_statistics_no_data(self):
        """测试无数据时的成功率统计"""
        self.mock_dao.search.return_value = []

        result = self.quote_service.calculate_success_rate_statistics()

        self.assertEqual(result["total_quotes"], 0)
        self.assertIn("message", result)

    def test_calculate_success_rate_statistics_with_filters(self):
        """测试带过滤条件的成功率统计"""
        # 使用简单的字典数据避免计算字段问题
        simple_quote_data = {
            "id": 1,
            "name": "测试报价",
            "customer_name": "测试客户",
            "quote_status": "draft",
            "total_amount": 15000,
            "items": [
                {
                    "product_name": "生态板",
                    "specification": "18mm",
                    "quantity": 100,
                    "unit_price": 150.0,
                    "unit": "张",
                }
            ],
        }
        self.mock_dao.search.return_value = [simple_quote_data]

        filters = {"customer_id": 1}
        result = self.quote_service.calculate_success_rate_statistics(filters)

        self.assertIsInstance(result, dict)
        # 验证过滤条件被传递
        self.mock_dao.search.assert_called_once()

    # ==================== 过期管理测试 ====================

    def test_get_expiring_quotes(self):
        """测试获取即将过期的报价"""
        # 准备即将过期的报价
        expiring_quote = self.sample_quote.copy()
        expiring_quote.valid_until = datetime.now() + timedelta(days=2)
        expiring_quote.quote_status = QuoteStatus.SENT

        self.mock_dao.search.return_value = [expiring_quote.to_dict()]

        result = self.quote_service.get_expiring_quotes(7)

        self.assertEqual(len(result), 1)
        self.assertIn("quote", result[0])
        self.assertIn("remaining_days", result[0])
        self.assertIn("urgency_level", result[0])

    def test_update_expired_quotes(self):
        """测试更新过期报价"""
        # 准备过期报价
        expired_quote = self.sample_quote.copy()
        expired_quote.id = 1
        expired_quote.valid_until = datetime.now() - timedelta(days=1)
        expired_quote.quote_status = QuoteStatus.SENT

        self.mock_dao.search.return_value = [expired_quote.to_dict()]
        self.mock_dao.get_by_id.return_value = expired_quote.to_dict()
        self.mock_dao.update.return_value = True

        result = self.quote_service.update_expired_quotes()

        self.assertEqual(result["updated_count"], 1)
        self.assertIn("message", result)

    def test_calculate_urgency_level(self):
        """测试计算紧急程度"""
        service = self.quote_service

        self.assertEqual(service._calculate_urgency_level(0), "紧急")
        self.assertEqual(service._calculate_urgency_level(2), "高")
        self.assertEqual(service._calculate_urgency_level(5), "中")
        self.assertEqual(service._calculate_urgency_level(10), "低")

    # ==================== 辅助方法测试 ====================

    def test_get_historical_prices(self):
        """测试获取历史价格"""
        customer_history = {
            "quotes": [
                {
                    "items": [
                        {"product_name": "生态板", "unit_price": 150.0},
                        {"product_name": "家具板", "unit_price": 120.0},
                    ]
                },
                {"items": [{"product_name": "生态板", "unit_price": 155.0}]},
            ]
        }

        prices = self.quote_service._get_historical_prices(customer_history, "生态板")

        self.assertEqual(len(prices), 2)
        self.assertIn(150.0, prices)
        self.assertIn(155.0, prices)

    def test_calculate_suggested_price(self):
        """测试计算建议价格"""
        historical_prices = [150.0, 155.0, 160.0]
        market_price = {"average_price": 158.0}
        customer_history = {"analysis": {"success_rate": "70%"}}

        suggested_price = self.quote_service._calculate_suggested_price(
            historical_prices, market_price, customer_history
        )

        self.assertIsInstance(suggested_price, float)
        self.assertGreater(suggested_price, 0)

    def test_calculate_price_range(self):
        """测试计算价格区间"""
        suggested_price = 155.0
        customer_history = {"analysis": {"success_rate": "80%"}}  # 高成功率

        price_range = self.quote_service._calculate_price_range(
            suggested_price, customer_history
        )

        self.assertIn("min", price_range)
        self.assertIn("max", price_range)
        self.assertLess(price_range["min"], suggested_price)
        self.assertGreater(price_range["max"], suggested_price)

    def test_calculate_confidence_level(self):
        """测试计算置信度"""
        service = self.quote_service

        self.assertEqual(service._calculate_confidence_level([1, 2, 3, 4, 5]), "高")
        self.assertEqual(service._calculate_confidence_level([1, 2]), "中")
        self.assertEqual(service._calculate_confidence_level([1]), "低")
        self.assertEqual(service._calculate_confidence_level([]), "低")

    def test_analyze_preferred_quote_size(self):
        """测试分析偏好报价规模"""
        quotes = [
            {"total_amount": 5000},  # 小额
            {"total_amount": 50000},  # 中等
            {"total_amount": 150000},  # 大额
        ]

        result = self.quote_service._analyze_preferred_quote_size(quotes)
        self.assertIn("订单偏好", result)

    def test_clear_analysis_cache(self):
        """测试清除分析缓存"""
        # 设置一些缓存数据
        self.quote_service._price_analysis_cache = {
            "customer_1_product_A": "data1",
            "customer_2_product_B": "data2",
        }

        # 清除特定客户的缓存
        self.quote_service._clear_analysis_cache(1)

        # 验证只清除了相关缓存
        remaining_keys = list(self.quote_service._price_analysis_cache.keys())
        self.assertNotIn("customer_1_product_A", remaining_keys)
        self.assertIn("customer_2_product_B", remaining_keys)

    # ==================== 错误处理测试 ====================

    def test_dao_error_handling(self):
        """测试DAO错误处理"""
        self.mock_dao.insert.side_effect = Exception("数据库错误")

        with self.assertRaises(ServiceError):
            self.quote_service.create(self.sample_quote_data)

    def test_validation_error_propagation(self):
        """测试验证错误传播"""
        # 测试验证错误是否正确传播
        with self.assertRaises(ValidationError) as context:
            self.quote_service.create({"customer_name": ""})

        self.assertIn("customer_name", str(context.exception))

    def test_business_logic_error_propagation(self):
        """测试业务逻辑错误传播"""
        self.mock_dao.get_by_id.return_value = None

        with self.assertRaises(BusinessLogicError) as context:
            self.quote_service.update(999, {"customer_name": "新客户"})

        self.assertIn("不存在", str(context.exception))

    # ==================== 集成测试 ====================

    def test_complete_quote_workflow(self):
        """测试完整的报价工作流"""
        # 1. 创建报价
        self.mock_dao.insert.return_value = 1
        quote = self.quote_service.create(self.sample_quote_data)
        self.assertIsInstance(quote, Quote)

        # 2. 获取报价
        self.mock_dao.get_by_id.return_value = quote.to_dict()
        retrieved_quote = self.quote_service.get_by_id(1)
        self.assertEqual(retrieved_quote.customer_name, quote.customer_name)

        # 3. 更新报价
        self.mock_dao.update.return_value = True
        updated_quote = self.quote_service.update(1, {"contact_person": "新联系人"})
        self.assertEqual(updated_quote.contact_person, "新联系人")

        # 4. 删除报价
        self.mock_dao.delete.return_value = True
        result = self.quote_service.delete(1)
        self.assertTrue(result)

    def test_quote_analysis_workflow(self):
        """测试报价分析工作流"""
        # 准备多个报价数据
        quotes = []
        for i in range(3):
            quote = self.sample_quote.copy()
            quote.id = i + 1
            quote.total_amount = Decimal(str(15000 + i * 1000))
            quotes.append(quote)

        # 模拟DAO返回
        self.mock_dao.get_by_id.side_effect = [q.to_dict() for q in quotes]

        # 执行比较分析
        result = self.quote_service.compare_quotes([1, 2, 3], "summary")

        self.assertEqual(result["quote_count"], 3)
        self.assertIn("statistics", result)

    def test_health_check(self):
        """测试健康检查"""
        health_status = self.quote_service.health_check()

        self.assertEqual(health_status["service"], "报价管理服务")
        self.assertEqual(health_status["status"], "healthy")
        self.assertTrue(health_status["dao_connected"])


if __name__ == "__main__":
    unittest.main()
