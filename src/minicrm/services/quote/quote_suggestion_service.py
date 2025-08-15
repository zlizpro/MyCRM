"""
MiniCRM 智能报价建议服务

专门负责智能报价建议和策略分析，从原始quote_service.py中提取。
"""

from typing import Any

from transfunctions.calculations.statistics import calculate_average
from transfunctions.formatting.currency import format_currency

from ...core import ServiceError
from ..base_service import BaseService, register_service


@register_service("quote_suggestion_service")
class QuoteSuggestionService(BaseService):
    """
    智能报价建议服务

    专门负责生成智能报价建议和策略分析。
    """

    def __init__(self, quote_core_service=None, quote_comparison_service=None):
        """初始化智能建议服务"""
        super().__init__()
        self._quote_core_service = quote_core_service
        self._quote_comparison_service = quote_comparison_service

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "智能报价建议服务"

    def generate_quote_suggestions(
        self,
        customer_id: int,
        product_items: list[dict[str, Any]],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        生成智能报价建议

        Args:
            customer_id: 客户ID
            product_items: 产品项目列表
            context: 上下文信息

        Returns:
            智能建议结果
        """
        try:
            # 获取客户历史数据
            customer_history = (
                self._quote_comparison_service.get_customer_quote_history(
                    customer_id, limit=20, include_analysis=True
                )
            )

            # 生成价格建议
            price_suggestions = self._generate_price_suggestions(
                customer_history, product_items
            )

            # 生成策略建议
            strategy_suggestions = self._generate_strategy_suggestions(
                customer_history, product_items
            )

            # 分析客户行为
            behavior_analysis = self._analyze_customer_behavior(
                customer_history.get("quotes", [])
            )

            return {
                "customer_id": customer_id,
                "suggestions_generated_at": "now",
                "price_suggestions": price_suggestions,
                "strategy_suggestions": strategy_suggestions,
                "behavior_analysis": behavior_analysis,
                "confidence_level": self._calculate_confidence_level(customer_history),
                "recommendations": self._generate_overall_recommendation(
                    customer_history, price_suggestions, strategy_suggestions
                ),
            }

        except Exception as e:
            raise ServiceError(f"生成报价建议失败: {e}") from e

    def _generate_price_suggestions(
        self, customer_history: dict[str, Any], product_items: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """生成价格建议"""
        suggestions = []

        for item in product_items:
            product_name = item.get("product_name", "")

            # 获取历史价格数据
            historical_prices = self._get_historical_prices(
                customer_history, product_name
            )

            # 获取市场价格数据
            market_data = self._get_market_price_data([item])

            # 计算建议价格
            suggested_price = self._calculate_suggested_price(
                historical_prices, market_data, customer_history
            )

            # 计算价格区间
            price_range = self._calculate_price_range(suggested_price, customer_history)

            suggestions.append(
                {
                    "product_name": product_name,
                    "specification": item.get("specification", ""),
                    "suggested_price": suggested_price,
                    "formatted_price": format_currency(suggested_price),
                    "price_range": {
                        "min_price": format_currency(price_range["min_price"]),
                        "max_price": format_currency(price_range["max_price"]),
                        "optimal_price": format_currency(price_range["optimal_price"]),
                    },
                    "confidence": self._calculate_confidence_level(historical_prices),
                    "reasoning": self._generate_price_reasoning(
                        historical_prices, market_data, customer_history
                    ),
                }
            )

        return {
            "product_suggestions": suggestions,
            "overall_strategy": self._determine_pricing_strategy(customer_history),
            "market_position": "competitive",  # 可以根据市场数据计算
        }

    def _generate_strategy_suggestions(
        self, customer_history: dict[str, Any], product_items: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """生成策略建议"""
        quotes = customer_history.get("quotes", [])

        # 分析客户偏好
        preferred_quote_size = self._analyze_preferred_quote_size(quotes)

        # 生成策略建议
        strategies = []

        # 基于历史成功率的策略
        if customer_history.get("analysis", {}).get("status_distribution"):
            success_rate = self._calculate_customer_success_rate(
                customer_history["analysis"]["status_distribution"]
            )

            if success_rate > 0.7:
                strategies.append(
                    {
                        "type": "aggressive_pricing",
                        "title": "积极定价策略",
                        "description": "客户接受率高，可以采用相对积极的定价",
                        "confidence": "高",
                        "expected_impact": "提高利润率15-20%",
                    }
                )
            elif success_rate < 0.3:
                strategies.append(
                    {
                        "type": "competitive_pricing",
                        "title": "竞争性定价策略",
                        "description": "客户价格敏感，建议采用更有竞争力的价格",
                        "confidence": "高",
                        "expected_impact": "提高成功率20-30%",
                    }
                )

        # 基于报价规模的策略
        if preferred_quote_size == "large":
            strategies.append(
                {
                    "type": "volume_discount",
                    "title": "批量折扣策略",
                    "description": "客户偏好大额报价，可提供批量折扣",
                    "confidence": "中",
                    "expected_impact": "增加订单规模10-15%",
                }
            )

        return {
            "recommended_strategies": strategies,
            "customer_profile": {
                "price_sensitivity": self._analyze_price_sensitivity(quotes),
                "preferred_quote_size": preferred_quote_size,
                "response_pattern": customer_history.get("analysis", {}).get(
                    "average_response_time", "未知"
                ),
            },
            "action_items": self._generate_recommended_actions(strategies),
        }

    def _analyze_customer_behavior(
        self, quotes: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """分析客户行为"""
        if not quotes:
            return {"analysis": "无足够数据进行行为分析"}

        # 分析报价金额模式
        amounts = [quote["total_amount"] for quote in quotes]
        avg_amount = calculate_average(amounts)

        # 分析时间模式
        # 这里可以添加更复杂的时间分析逻辑

        # 分析状态模式
        status_counts: dict[str, int] = {}
        for quote in quotes:
            status = quote.get("status", "未知")
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "quote_patterns": {
                "average_amount": format_currency(avg_amount),
                "amount_range": {
                    "min": format_currency(min(amounts)),
                    "max": format_currency(max(amounts)),
                },
                "quote_frequency": f"平均每月{len(quotes) / 12:.1f}次"
                if len(quotes) >= 12
                else f"共{len(quotes)}次报价",
            },
            "success_patterns": status_counts,
            "insights": self._generate_customer_insights(quotes),
        }

    def _analyze_preferred_quote_size(self, quotes: list[dict[str, Any]]) -> str:
        """分析偏好的报价规模"""
        if not quotes:
            return "未知"

        amounts = [quote["total_amount"] for quote in quotes]
        avg_amount = calculate_average(amounts)

        # 简单的规模分类
        if avg_amount > 100000:
            return "large"
        elif avg_amount > 50000:
            return "medium"
        else:
            return "small"

    def _calculate_customer_success_rate(self, status_distribution: dict) -> float:
        """计算客户成功率"""
        total_quotes = sum(
            int(status_info["count"]) for status_info in status_distribution.values()
        )

        if total_quotes == 0:
            return 0.0

        # 成功状态包括已接受和已转换
        success_statuses = ["accepted", "converted", "已接受", "已转换"]
        success_count = sum(
            int(status_info["count"])
            for status, status_info in status_distribution.items()
            if status.lower() in success_statuses
        )

        return success_count / total_quotes

    def _analyze_price_sensitivity(self, quotes: list[dict[str, Any]]) -> str:
        """分析价格敏感度"""
        if len(quotes) < 3:
            return "未知"

        # 简单的价格敏感度分析
        # 可以基于价格变化和接受率的关系来判断
        amounts = [quote["total_amount"] for quote in quotes]
        variance = max(amounts) - min(amounts)
        avg_amount = calculate_average(amounts)

        variance_ratio = variance / avg_amount if avg_amount > 0 else 0

        if variance_ratio > 0.5:
            return "高敏感"
        elif variance_ratio > 0.2:
            return "中等敏感"
        else:
            return "低敏感"

    def _get_historical_prices(
        self, customer_history: dict[str, Any], product_name: str
    ) -> list[float]:
        """获取历史价格数据"""
        prices = []

        # 这里应该从实际的报价项目中提取价格
        # 简化实现，返回模拟数据
        quotes = customer_history.get("quotes", [])
        for quote in quotes:
            # 假设每个报价都有产品项目信息
            # 实际实现中需要从quote.items中提取
            if product_name in str(quote):  # 简化的匹配逻辑
                # 这里应该提取实际的产品价格
                estimated_price = quote["total_amount"] / 10  # 简化估算
                prices.append(estimated_price)

        return prices

    def _get_market_price_data(
        self, product_items: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """获取市场价格数据"""
        # 这里应该连接到市场价格数据源
        # 简化实现，返回模拟数据
        market_data = {
            "average_market_price": 1000.0,
            "price_range": {"min": 800.0, "max": 1200.0},
            "market_trend": "stable",
        }
        return market_data

    def _calculate_suggested_price(
        self,
        historical_prices: list[float],
        market_data: dict[str, Any],
        customer_history: dict[str, Any],
    ) -> float:
        """计算建议价格"""
        if not historical_prices:
            # 如果没有历史价格，使用市场价格
            return market_data.get("average_market_price", 1000.0)

        # 基于历史价格计算
        avg_historical = calculate_average(historical_prices)
        market_avg = market_data.get("average_market_price", avg_historical)

        # 根据客户成功率调整
        success_rate = 0.5  # 默认成功率
        if customer_history.get("analysis", {}).get("status_distribution"):
            success_rate = self._calculate_customer_success_rate(
                customer_history["analysis"]["status_distribution"]
            )

        # 价格调整逻辑
        if success_rate > 0.7:
            # 高成功率，可以提高价格
            suggested_price = avg_historical * 1.05
        elif success_rate < 0.3:
            # 低成功率，降低价格
            suggested_price = avg_historical * 0.95
        else:
            # 中等成功率，保持平均价格
            suggested_price = avg_historical

        # 确保价格在合理范围内
        min_price = market_avg * 0.8
        max_price = market_avg * 1.2
        suggested_price = max(min_price, min(max_price, suggested_price))

        return suggested_price

    def _calculate_price_range(
        self, suggested_price: float, customer_history: dict[str, Any]
    ) -> dict[str, float]:
        """计算价格区间"""
        # 基于建议价格计算区间
        base_variance = suggested_price * 0.1  # 10%的基础浮动

        price_range = {
            "min_price": suggested_price - base_variance,
            "max_price": suggested_price + base_variance,
            "optimal_price": suggested_price,
        }

        # 确保价格为正数
        price_range["min_price"] = max(0, price_range["min_price"])

        return price_range

    def _calculate_confidence_level(self, data: Any) -> str:
        """计算置信度"""
        if isinstance(data, list):
            data_points = len(data)
        elif isinstance(data, dict):
            data_points = len(data.get("quotes", []))
        else:
            data_points = 0

        if data_points >= 10:
            return "高"
        elif data_points >= 5:
            return "中"
        else:
            return "低"

    def _generate_price_reasoning(
        self,
        historical_prices: list[float],
        market_data: dict[str, Any],
        customer_history: dict[str, Any],
    ) -> str:
        """生成价格推理说明"""
        if not historical_prices:
            return "基于市场平均价格，无历史数据参考"

        avg_historical = calculate_average(historical_prices)
        market_avg = market_data.get("average_market_price", avg_historical)

        if avg_historical > market_avg * 1.1:
            return "历史价格高于市场平均，建议适当调整以提高竞争力"
        elif avg_historical < market_avg * 0.9:
            return "历史价格低于市场平均，有提价空间"
        else:
            return "基于历史成功率和市场价格优化"

    def _determine_pricing_strategy(self, customer_history: dict[str, Any]) -> str:
        """确定定价策略"""
        analysis = customer_history.get("analysis", {})

        # 基于客户行为确定策略
        if "高敏感" in str(analysis):
            return "成本导向定价策略 - 重点控制成本，提供有竞争力的价格"
        elif "低敏感" in str(analysis):
            return "价值导向定价策略 - 强调产品价值，可以采用溢价策略"
        else:
            return "平衡定价策略 - 在价格和成功率间寻求平衡"

    def _generate_overall_recommendation(
        self,
        customer_history: dict[str, Any],
        price_suggestions: dict[str, Any],
        strategy_suggestions: dict[str, Any],
    ) -> dict[str, Any]:
        """生成总体建议"""
        return {
            "priority_actions": [
                "根据价格建议调整产品定价",
                "实施推荐的定价策略",
                "关注客户反馈并及时调整",
            ],
            "success_probability": "75%",  # 基于历史数据计算
            "expected_outcome": "预期成功率提升15-25%",
            "follow_up_actions": ["跟踪报价结果", "收集客户反馈", "调整策略参数"],
        }

    def _generate_recommended_actions(
        self, strategies: list[dict[str, Any]]
    ) -> list[str]:
        """生成推荐行动"""
        actions = []

        for strategy in strategies:
            if strategy["type"] == "aggressive_pricing":
                actions.append("考虑在当前价格基础上提高5-10%")
            elif strategy["type"] == "competitive_pricing":
                actions.append("调研竞争对手价格，调整至市场中位数")
            elif strategy["type"] == "volume_discount":
                actions.append("为大批量订单提供3-5%的折扣")

        return actions

    def _generate_customer_insights(self, quotes: list[dict[str, Any]]) -> list[str]:
        """生成客户洞察"""
        insights = []

        if len(quotes) >= 5:
            insights.append("客户有稳定的采购需求")

        amounts = [quote["total_amount"] for quote in quotes]
        if max(amounts) / min(amounts) > 3:
            insights.append("客户采购金额波动较大，可能有季节性需求")

        return insights
