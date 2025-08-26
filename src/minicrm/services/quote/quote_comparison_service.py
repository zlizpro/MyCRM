"""
MiniCRM 报价比对分析服务

专门负责报价比对和分析功能,从原始quote_service.py中提取.
"""

from datetime import datetime
from typing import Any

from transfunctions.calculations.statistics import calculate_average
from transfunctions.formatting.currency import format_currency, format_percentage

from ...core import ServiceError
from ...models import Quote
from ..base_service import BaseService, register_service


@register_service("quote_comparison_service")
class QuoteComparisonService(BaseService):
    """
    报价比对分析服务

    专门负责报价比对、分析和趋势计算.
    """

    def __init__(self, quote_core_service=None):
        """初始化报价比对服务"""
        super().__init__()
        self._quote_core_service = quote_core_service

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "报价比对分析服务"

    def compare_quotes(
        self, quote_ids: list[int], comparison_type: str = "detailed"
    ) -> dict[str, Any]:
        """
        比较多个报价

        Args:
            quote_ids: 报价ID列表
            comparison_type: 比较类型 (summary/detailed/trend)

        Returns:
            比较结果字典
        """
        try:
            # 获取报价数据
            quotes = []
            for quote_id in quote_ids:
                quote = self._quote_core_service.get_by_id(quote_id)
                if quote:
                    quotes.append(quote)

            if len(quotes) < 2:
                raise ServiceError("至少需要2个报价进行比较")

            # 根据比较类型执行不同的比较逻辑
            if comparison_type == "summary":
                return self._compare_quotes_summary(quotes)
            elif comparison_type == "detailed":
                return self._compare_quotes_detailed(quotes)
            elif comparison_type == "trend":
                return self._compare_quotes_trend(quotes)
            else:
                raise ServiceError(f"不支持的比较类型: {comparison_type}")

        except Exception as e:
            raise ServiceError(f"报价比较失败: {e}") from e

    def _compare_quotes_summary(self, quotes: list[Quote]) -> dict[str, Any]:
        """生成报价摘要比较"""
        total_amounts = [float(quote.total_amount) for quote in quotes]

        return {
            "comparison_type": "summary",
            "quote_count": len(quotes),
            "quotes": [
                {
                    "id": quote.id,
                    "quote_number": quote.quote_number,
                    "customer_name": quote.customer_name,
                    "total_amount": float(quote.total_amount),
                    "formatted_amount": format_currency(quote.total_amount),
                    "quote_date": quote.quote_date.isoformat()
                    if quote.quote_date
                    else None,
                    "status": quote.quote_status.value if quote.quote_status else None,
                }
                for quote in quotes
            ],
            "statistics": {
                "min_amount": format_currency(min(total_amounts)),
                "max_amount": format_currency(max(total_amounts)),
                "avg_amount": format_currency(calculate_average(total_amounts)),
                "amount_variance": format_currency(
                    max(total_amounts) - min(total_amounts)
                ),
                "variance_percentage": format_percentage(
                    (max(total_amounts) - min(total_amounts))
                    / calculate_average(total_amounts)
                    if calculate_average(total_amounts) > 0
                    else 0
                ),
            },
        }

    def _compare_quotes_detailed(self, quotes: list[Quote]) -> dict[str, Any]:
        """生成详细报价比较"""
        # 收集所有产品信息
        all_products = self._collect_product_info(quotes)

        # 计算产品价格统计
        product_analysis = self._generate_product_analysis(all_products)

        # 生成趋势分析
        trend_analysis = self._compare_quotes_trend(quotes)

        # 生成智能建议
        intelligent_suggestions = self._generate_intelligent_suggestions(
            quotes, product_analysis
        )

        # 计算竞争力分析
        competitiveness_analysis = self._analyze_quote_competitiveness(quotes)

        return {
            "comparison_type": "detailed",
            "quote_count": len(quotes),
            "quotes": self._compare_quotes_summary(quotes)["quotes"],
            "product_analysis": product_analysis,
            "trend_analysis": trend_analysis.get("overall_trend", {}),
            "intelligent_suggestions": intelligent_suggestions,
            "competitiveness_analysis": competitiveness_analysis,
            "summary": self._compare_quotes_summary(quotes)["statistics"],
        }

    def _collect_product_info(self, quotes: list[Quote]) -> dict[str, Any]:
        """收集产品信息"""
        all_products: dict[str, dict[str, Any]] = {}

        for quote in quotes:
            if quote.items:
                for item in quote.items:
                    product_key = f"{item.product_name}_{item.specification}"
                    if product_key not in all_products:
                        all_products[product_key] = {
                            "product_name": item.product_name,
                            "specification": item.specification,
                            "unit": item.unit,
                            "prices": [],
                        }

        # 收集每个产品在不同报价中的价格
        for quote in quotes:
            quote_products = {}
            if quote.items:
                for item in quote.items:
                    product_key = f"{item.product_name}_{item.specification}"
                    quote_products[product_key] = item

            for product_key in all_products:
                if product_key in quote_products:
                    item = quote_products[product_key]
                    all_products[product_key]["prices"].append(
                        {
                            "quote_id": quote.id,
                            "quote_number": quote.quote_number,
                            "unit_price": float(item.unit_price),
                            "quantity": float(item.quantity),
                            "total": float(item.get_total()),
                            "formatted_unit_price": item.get_formatted_unit_price(),
                            "formatted_total": item.get_formatted_total(),
                        }
                    )
                else:
                    all_products[product_key]["prices"].append(
                        {
                            "quote_id": quote.id,
                            "quote_number": quote.quote_number,
                            "unit_price": None,
                            "quantity": None,
                            "total": None,
                            "formatted_unit_price": "未报价",
                            "formatted_total": "未报价",
                        }
                    )

        return all_products

    def _generate_product_analysis(
        self, all_products: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """生成产品分析"""
        product_analysis = []

        for product_info in all_products.values():
            valid_prices = [
                p["unit_price"]
                for p in product_info["prices"]
                if p["unit_price"] is not None
            ]

            if valid_prices:
                price_stats = {
                    "min_price": min(valid_prices),
                    "max_price": max(valid_prices),
                    "avg_price": calculate_average(valid_prices),
                    "price_variance": max(valid_prices) - min(valid_prices)
                    if len(valid_prices) > 1
                    else 0,
                }
            else:
                price_stats = {
                    "min_price": 0,
                    "max_price": 0,
                    "avg_price": 0,
                    "price_variance": 0,
                }

            product_analysis.append(
                {
                    "product_name": product_info["product_name"],
                    "specification": product_info["specification"],
                    "unit": product_info["unit"],
                    "prices": product_info["prices"],
                    "statistics": {
                        "min_price": format_currency(price_stats["min_price"]),
                        "max_price": format_currency(price_stats["max_price"]),
                        "avg_price": format_currency(price_stats["avg_price"]),
                        "price_variance": format_currency(
                            price_stats["price_variance"]
                        ),
                        "variance_percentage": format_percentage(
                            price_stats["price_variance"] / price_stats["avg_price"]
                            if price_stats["avg_price"] > 0
                            else 0
                        ),
                    },
                }
            )

        return product_analysis

    def _compare_quotes_trend(self, quotes: list[Quote]) -> dict[str, Any]:
        """生成报价趋势比较"""
        # 按日期排序
        sorted_quotes = sorted(quotes, key=lambda q: q.quote_date or datetime.min)

        # 计算趋势数据
        trend_data = []
        for i, quote in enumerate(sorted_quotes):
            trend_point = {
                "sequence": i + 1,
                "quote_id": quote.id,
                "quote_number": quote.quote_number,
                "quote_date": quote.quote_date.isoformat()
                if quote.quote_date
                else None,
                "total_amount": float(quote.total_amount),
                "formatted_amount": format_currency(quote.total_amount),
            }

            # 计算与前一个报价的变化
            if i > 0:
                prev_amount = float(sorted_quotes[i - 1].total_amount)
                current_amount = float(quote.total_amount)
                change = current_amount - prev_amount
                change_percentage = (
                    (change / prev_amount * 100) if prev_amount > 0 else 0
                )

                trend_point.update(
                    {
                        "amount_change": change,
                        "formatted_change": format_currency(abs(change)),
                        "change_percentage": f"{change_percentage:.1f}%",
                        "trend_direction": "上升"
                        if change > 0
                        else "下降"
                        if change < 0
                        else "持平",
                    }
                )

            trend_data.append(trend_point)

        # 计算整体趋势
        if len(sorted_quotes) >= 2:
            first_amount = float(sorted_quotes[0].total_amount)
            last_amount = float(sorted_quotes[-1].total_amount)
            overall_change = last_amount - first_amount
            overall_percentage = (
                (overall_change / first_amount * 100) if first_amount > 0 else 0
            )

            overall_trend = {
                "total_change": format_currency(abs(overall_change)),
                "change_percentage": f"{overall_percentage:.1f}%",
                "trend_direction": "上升"
                if overall_change > 0
                else "下降"
                if overall_change < 0
                else "持平",
                "period_days": (
                    sorted_quotes[-1].quote_date - sorted_quotes[0].quote_date
                ).days
                if sorted_quotes[-1].quote_date and sorted_quotes[0].quote_date
                else 0,
            }
        else:
            overall_trend = {
                "total_change": "0.00",
                "change_percentage": "0.0%",
                "trend_direction": "无变化",
                "period_days": 0,
            }

        return {
            "comparison_type": "trend",
            "quote_count": len(quotes),
            "trend_data": trend_data,
            "overall_trend": overall_trend,
            "summary": self._compare_quotes_summary(quotes)["statistics"],
        }

    def get_customer_quote_history(
        self, customer_id: int, limit: int = 10, include_analysis: bool = True
    ) -> dict[str, Any]:
        """
        获取客户报价历史

        Args:
            customer_id: 客户ID
            limit: 返回数量限制
            include_analysis: 是否包含分析数据

        Returns:
            客户报价历史和分析
        """
        try:
            # 获取客户报价
            filters = {"customer_id": customer_id}
            quotes = self._quote_core_service.list_all(filters)

            # 按日期排序并限制数量
            quotes = sorted(
                quotes, key=lambda q: q.quote_date or datetime.min, reverse=True
            )
            quotes = quotes[:limit]

            result = {
                "customer_id": customer_id,
                "quote_count": len(quotes),
                "quotes": [
                    {
                        "id": quote.id,
                        "quote_number": quote.quote_number,
                        "total_amount": float(quote.total_amount),
                        "formatted_amount": format_currency(quote.total_amount),
                        "quote_date": quote.quote_date.isoformat()
                        if quote.quote_date
                        else None,
                        "status": quote.quote_status.value
                        if quote.quote_status
                        else None,
                    }
                    for quote in quotes
                ],
            }

            if include_analysis and len(quotes) >= 2:
                result["analysis"] = self._analyze_customer_quote_trend(quotes)

            return result

        except Exception as e:
            raise ServiceError(f"获取客户报价历史失败: {e}") from e

    def _analyze_customer_quote_trend(self, quotes: list[Quote]) -> dict[str, Any]:
        """分析客户报价趋势"""
        if len(quotes) < 2:
            return {"trend": "数据不足", "analysis": "需要至少2个报价进行趋势分析"}

        # 计算金额趋势
        amounts = [float(quote.total_amount) for quote in quotes]
        trend = self._calculate_amount_trend(amounts)

        # 计算平均响应时间(如果有发送和接受时间)
        response_times: list[float] = []
        for quote in quotes:
            if (
                hasattr(quote, "sent_date")
                and hasattr(quote, "response_date")
                and quote.sent_date
                and quote.response_date
            ):
                response_time = float((quote.response_date - quote.sent_date).days)
                response_times.append(response_time)

        avg_response_time = calculate_average(response_times) if response_times else 0

        # 计算状态分布
        status_distribution = self._calculate_status_distribution(quotes)

        return {
            "trend": trend,
            "average_amount": format_currency(calculate_average(amounts)),
            "amount_variance": format_currency(max(amounts) - min(amounts)),
            "average_response_time": f"{avg_response_time:.1f}天",
            "status_distribution": status_distribution,
            "total_quotes": len(quotes),
            "analysis_period": f"{len(quotes)}个报价",
        }

    def _calculate_amount_trend(self, amounts: list[float]) -> str:
        """计算金额趋势"""
        if len(amounts) < 2:
            return "无趋势"

        # 简单的趋势计算:比较前半部分和后半部分的平均值
        mid = len(amounts) // 2
        first_half_avg = calculate_average(amounts[:mid])
        second_half_avg = calculate_average(amounts[mid:])

        if second_half_avg > first_half_avg * 1.1:
            return "上升"
        elif second_half_avg < first_half_avg * 0.9:
            return "下降"
        else:
            return "平稳"

    def _calculate_status_distribution(self, quotes: list[Quote]) -> dict[str, Any]:
        """计算状态分布"""
        status_count: dict[str, int] = {}
        for quote in quotes:
            status = quote.quote_status.value if quote.quote_status else "未知"
            status_count[status] = status_count.get(status, 0) + 1

        total = len(quotes)
        return {
            status: {"count": count, "percentage": f"{(count / total * 100):.1f}%"}
            for status, count in status_count.items()
        }

    def _generate_intelligent_suggestions(
        self, quotes: list[Quote], product_analysis: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """生成智能建议"""
        suggestions: dict[str, list[dict[str, str]]] = {
            "pricing_strategy": [],
            "product_optimization": [],
            "market_insights": [],
            "risk_warnings": [],
        }

        # 价格策略建议
        amounts = [float(quote.total_amount) for quote in quotes]
        if len(amounts) >= 2:
            recent_trend = self._calculate_amount_trend(
                amounts[-3:] if len(amounts) >= 3 else amounts
            )

            if recent_trend == "上升":
                suggestions["pricing_strategy"].append(
                    {
                        "type": "价格上升趋势",
                        "suggestion": (
                            "报价呈上升趋势,可能反映了产品价值提升或市场需求增长,"
                            "建议保持当前定价策略"
                        ),
                        "priority": "中等",
                    }
                )
            elif recent_trend == "下降":
                suggestions["pricing_strategy"].append(
                    {
                        "type": "价格下降趋势",
                        "suggestion": (
                            "报价呈下降趋势,建议分析成本结构和竞争环境,"
                            "考虑价值重新定位"
                        ),
                        "priority": "高",
                    }
                )

        # 产品优化建议
        if product_analysis:
            # 找出价格波动最大的产品
            max_variance_product = max(
                product_analysis,
                key=lambda x: float(
                    x.get("statistics", {})
                    .get("price_variance", "0")
                    .replace("¥", "")
                    .replace(",", "")
                    or "0"
                ),
            )

            suggestions["product_optimization"].append(
                {
                    "type": "价格波动分析",
                    "suggestion": (
                        f"{max_variance_product.get('product_name', '未知产品')} "
                        "价格波动较大,建议制定更稳定的定价策略"
                    ),
                    "priority": "中等",
                }
            )

        # 市场洞察
        success_quotes = [
            q
            for q in quotes
            if q.quote_status and q.quote_status.value in ["accepted", "converted"]
        ]
        success_rate = (len(success_quotes) / len(quotes)) * 100 if quotes else 0

        if success_rate > 70:
            suggestions["market_insights"].append(
                {
                    "type": "高成功率",
                    "suggestion": (
                        f"报价成功率达到 {success_rate:.1f}%,"
                        "表明定价策略与市场需求匹配度较高"
                    ),
                    "priority": "低",
                }
            )
        elif success_rate < 30:
            suggestions["market_insights"].append(
                {
                    "type": "低成功率",
                    "suggestion": (
                        f"报价成功率仅为 {success_rate:.1f}%,"
                        "建议重新评估定价策略和产品竞争力"
                    ),
                    "priority": "高",
                }
            )

        # 风险预警
        if len(amounts) >= 3:
            recent_amounts = amounts[-3:]
            if all(
                recent_amounts[i] < recent_amounts[i - 1]
                for i in range(1, len(recent_amounts))
            ):
                suggestions["risk_warnings"].append(
                    {
                        "type": "连续降价风险",
                        "suggestion": (
                            "最近3次报价呈连续下降趋势,可能影响利润率,"
                            "建议评估成本和市场定位"
                        ),
                        "priority": "高",
                    }
                )

        return suggestions

    def _analyze_quote_competitiveness(self, quotes: list[Quote]) -> dict[str, Any]:
        """分析报价竞争力"""
        if len(quotes) < 2:
            return {"analysis": "数据不足,需要至少2个报价进行竞争力分析"}

        amounts = [float(quote.total_amount) for quote in quotes]
        avg_amount = calculate_average(amounts)

        # 计算每个报价相对于平均值的竞争力
        competitiveness_scores = []
        for quote in quotes:
            amount = float(quote.total_amount)
            # 价格越低,竞争力越高(简化模型)
            # 防止除零错误
            if avg_amount > 0:
                competitiveness = max(0, (avg_amount - amount) / avg_amount * 100 + 50)
            else:
                competitiveness = 50  # 默认中等竞争力

            competitiveness_scores.append(
                {
                    "quote_id": quote.id,
                    "quote_number": quote.quote_number,
                    "amount": amount,
                    "formatted_amount": format_currency(amount),
                    "competitiveness_score": round(competitiveness, 1),
                    "competitiveness_level": self._get_competitiveness_level(
                        competitiveness
                    ),
                }
            )

        # 排序(按竞争力得分降序)
        competitiveness_scores.sort(
            key=lambda x: float(x["competitiveness_score"])
            if x["competitiveness_score"] is not None
            else 0.0,
            reverse=True,
        )

        return {
            "analysis": "基于价格的竞争力分析",
            "average_amount": format_currency(avg_amount),
            "competitiveness_ranking": competitiveness_scores,
            "insights": self._generate_competitiveness_insights(competitiveness_scores),
        }

    def _get_competitiveness_level(self, score: float) -> str:
        """获取竞争力等级"""
        if score >= 80:
            return "极强"
        elif score >= 60:
            return "较强"
        elif score >= 40:
            return "一般"
        elif score >= 20:
            return "较弱"
        else:
            return "很弱"

    def _generate_competitiveness_insights(self, scores: list[dict]) -> list[str]:
        """生成竞争力洞察"""
        insights = []

        if scores:
            best_quote = scores[0]
            worst_quote = scores[-1]

            insights.append(
                f"最具竞争力的报价是 {best_quote['quote_number']},"
                f"竞争力得分 {best_quote['competitiveness_score']}"
            )

            if len(scores) > 1:
                insights.append(
                    f"竞争力最弱的报价是 {worst_quote['quote_number']},"
                    f"竞争力得分 {worst_quote['competitiveness_score']}"
                )

                score_diff = (
                    best_quote["competitiveness_score"]
                    - worst_quote["competitiveness_score"]
                )
                if score_diff > 40:
                    insights.append("报价间竞争力差异较大,建议统一定价策略")
                elif score_diff < 10:
                    insights.append("报价竞争力相对均衡,定价策略一致性较好")

        return insights
