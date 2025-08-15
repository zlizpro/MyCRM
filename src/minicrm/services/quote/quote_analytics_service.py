"""
MiniCRM 报价统计分析服务

专门负责报价成功率统计和分析，从原始quote_service.py中提取。
"""

from datetime import datetime, timedelta
from typing import Any

from transfunctions.calculations.statistics import calculate_average
from transfunctions.formatting.currency import format_currency, format_percentage

from ...core import ServiceError
from ...models.quote import QuoteStatus
from ..base_service import BaseService, register_service


@register_service("quote_analytics_service")
class QuoteAnalyticsService(BaseService):
    """
    报价统计分析服务

    专门负责报价成功率统计、趋势分析和业务洞察。
    """

    def __init__(self, quote_core_service=None):
        """初始化统计分析服务"""
        super().__init__()
        self._quote_core_service = quote_core_service
        self._success_rate_cache = {}

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "报价统计分析服务"

    def calculate_success_rate_statistics(
        self, filters: dict[str, Any] | None = None, time_period: int = 12
    ) -> dict[str, Any]:
        """
        计算报价成功率统计

        Args:
            filters: 筛选条件
            time_period: 统计时间段（月）

        Returns:
            成功率统计结果
        """
        try:
            # 设置时间范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_period * 30)

            # 构建查询条件
            query_filters = filters or {}
            query_filters.update(
                {"quote_date_start": start_date, "quote_date_end": end_date}
            )

            # 获取报价数据
            quotes = self._quote_core_service.list_all(query_filters)

            if not quotes:
                return self._empty_statistics_result()

            # 计算总体统计
            total_quotes = len(quotes)
            successful_quotes = len(
                [
                    q
                    for q in quotes
                    if q.quote_status in [QuoteStatus.ACCEPTED, QuoteStatus.CONVERTED]
                ]
            )
            overall_success_rate = (
                successful_quotes / total_quotes if total_quotes > 0 else 0
            )

            # 计算月度统计
            monthly_stats = self._calculate_monthly_success_rate(quotes)

            # 按状态分组统计
            status_stats: dict[str, Any] = {}
            for quote in quotes:
                status = quote.quote_status.value if quote.quote_status else "未知"
                if status not in status_stats:
                    status_stats[status] = {
                        "count": 0,
                        "total_amount": 0.0,
                        "percentage": 0.0,
                    }
                status_stats[status]["count"] += 1
                status_stats[status]["total_amount"] += float(quote.total_amount)

            # 计算百分比
            for status_data in status_stats.values():
                status_data["percentage"] = status_data["count"] / total_quotes * 100
                status_data["formatted_amount"] = format_currency(
                    status_data["total_amount"]
                )
                status_data["formatted_percentage"] = (
                    f"{status_data['percentage']:.1f}%"
                )

            # 计算金额统计
            amounts = [float(q.total_amount) for q in quotes]
            successful_amounts = [
                float(q.total_amount)
                for q in quotes
                if q.quote_status in [QuoteStatus.ACCEPTED, QuoteStatus.CONVERTED]
            ]

            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "months": time_period,
                },
                "overall_statistics": {
                    "total_quotes": total_quotes,
                    "successful_quotes": successful_quotes,
                    "success_rate": format_percentage(overall_success_rate),
                    "total_amount": format_currency(sum(amounts)),
                    "successful_amount": format_currency(sum(successful_amounts)),
                    "average_quote_amount": format_currency(calculate_average(amounts)),
                    "average_successful_amount": format_currency(
                        calculate_average(successful_amounts)
                        if successful_amounts
                        else 0
                    ),
                },
                "monthly_statistics": monthly_stats,
                "status_distribution": status_stats,
                "insights": self._generate_success_rate_insights(
                    overall_success_rate, monthly_stats
                ),
                "recommendations": self._generate_customer_recommendations(quotes),
            }

        except Exception as e:
            raise ServiceError(f"计算成功率统计失败: {e}") from e

    def _calculate_monthly_success_rate(self, quotes: list) -> list[dict[str, Any]]:
        """计算月度成功率"""
        # 按月分组
        monthly_data = {}

        for quote in quotes:
            if not quote.quote_date:
                continue

            month_key = quote.quote_date.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "total": 0,
                    "successful": 0,
                    "total_amount": 0.0,
                    "successful_amount": 0.0,
                }

            monthly_data[month_key]["total"] += 1
            monthly_data[month_key]["total_amount"] += float(quote.total_amount)

            if quote.quote_status in [QuoteStatus.ACCEPTED, QuoteStatus.CONVERTED]:
                monthly_data[month_key]["successful"] += 1
                monthly_data[month_key]["successful_amount"] += float(
                    quote.total_amount
                )

        # 转换为列表并计算成功率
        monthly_stats = []
        for month, data in sorted(monthly_data.items()):
            success_rate = (
                data["successful"] / data["total"] if data["total"] > 0 else 0
            )

            monthly_stats.append(
                {
                    "month": month,
                    "total_quotes": data["total"],
                    "successful_quotes": data["successful"],
                    "success_rate": format_percentage(success_rate),
                    "total_amount": format_currency(data["total_amount"]),
                    "successful_amount": format_currency(data["successful_amount"]),
                    "average_amount": format_currency(
                        data["total_amount"] / data["total"] if data["total"] > 0 else 0
                    ),
                }
            )

        return monthly_stats

    def _empty_statistics_result(self) -> dict[str, Any]:
        """返回空统计结果"""
        return {
            "period": {
                "start_date": datetime.now().isoformat(),
                "end_date": datetime.now().isoformat(),
                "months": 0,
            },
            "overall_statistics": {
                "total_quotes": 0,
                "successful_quotes": 0,
                "success_rate": "0.0%",
                "total_amount": "¥0.00",
                "successful_amount": "¥0.00",
                "average_quote_amount": "¥0.00",
                "average_successful_amount": "¥0.00",
            },
            "monthly_statistics": [],
            "status_distribution": {},
            "insights": ["暂无数据进行分析"],
            "recommendations": ["开始创建报价以获得统计数据"],
        }

    def _generate_success_rate_insights(
        self, overall_success_rate: float, monthly_stats: list[dict[str, Any]]
    ) -> list[str]:
        """生成成功率洞察"""
        insights = []

        # 总体成功率分析
        if overall_success_rate > 0.7:
            insights.append("报价成功率较高，定价策略效果良好")
        elif overall_success_rate > 0.4:
            insights.append("报价成功率中等，有优化空间")
        else:
            insights.append("报价成功率偏低，建议调整定价策略")

        # 趋势分析
        if len(monthly_stats) >= 3:
            recent_rates = []
            for stat in monthly_stats[-3:]:
                rate_str = stat["success_rate"].replace("%", "")
                try:
                    rate = float(rate_str) / 100
                    recent_rates.append(rate)
                except ValueError:
                    continue

            if len(recent_rates) >= 2:
                if recent_rates[-1] > recent_rates[0] * 1.1:
                    insights.append("近期成功率呈上升趋势")
                elif recent_rates[-1] < recent_rates[0] * 0.9:
                    insights.append("近期成功率呈下降趋势，需要关注")
                else:
                    insights.append("近期成功率相对稳定")

        # 季节性分析
        if len(monthly_stats) >= 12:
            insights.append("数据充足，可进行季节性分析")

        return insights

    def _generate_customer_recommendations(self, quotes: list) -> list[str]:
        """生成客户相关建议"""
        recommendations = []

        if not quotes:
            return ["开始创建报价以获得个性化建议"]

        # 基于报价数量的建议
        if len(quotes) < 10:
            recommendations.append("增加报价频率，积累更多数据以优化策略")

        # 基于金额分布的建议
        amounts = [float(q.total_amount) for q in quotes]
        if amounts and max(amounts) / min(amounts) > 5:
            recommendations.append("报价金额差异较大，考虑按客户类型制定不同策略")

        return recommendations

    def get_quote_performance_metrics(self, time_period: int = 6) -> dict[str, Any]:
        """
        获取报价绩效指标

        Args:
            time_period: 统计时间段（月）

        Returns:
            绩效指标数据
        """
        try:
            # 获取统计数据
            stats = self.calculate_success_rate_statistics(time_period=time_period)

            # 计算关键绩效指标
            overall_stats = stats["overall_statistics"]
            monthly_stats = stats["monthly_statistics"]

            # 计算平均响应时间（模拟数据）
            avg_response_time = "3.5天"  # 实际应该从数据库计算

            # 计算转换漏斗
            conversion_funnel = self._calculate_conversion_funnel(stats)

            return {
                "kpi_summary": {
                    "success_rate": overall_stats["success_rate"],
                    "total_revenue": overall_stats["successful_amount"],
                    "average_deal_size": overall_stats["average_successful_amount"],
                    "quote_volume": overall_stats["total_quotes"],
                    "response_time": avg_response_time,
                },
                "trends": {
                    "monthly_performance": monthly_stats,
                    "growth_rate": self._calculate_growth_rate(monthly_stats),
                    "seasonality": self._analyze_seasonality(monthly_stats),
                },
                "conversion_funnel": conversion_funnel,
                "benchmarks": {
                    "industry_average": "45%",  # 行业平均值
                    "target_rate": "60%",  # 目标成功率
                    "performance_vs_target": self._compare_with_target(
                        overall_stats["success_rate"], "60%"
                    ),
                },
            }

        except Exception as e:
            raise ServiceError(f"获取绩效指标失败: {e}") from e

    def _calculate_conversion_funnel(self, stats: dict[str, Any]) -> dict[str, Any]:
        """计算转换漏斗"""
        status_dist = stats["status_distribution"]
        total_quotes = stats["overall_statistics"]["total_quotes"]

        funnel_stages = {
            "created": total_quotes,
            "sent": status_dist.get("sent", {}).get("count", 0),
            "viewed": status_dist.get("sent", {}).get("count", 0),  # 假设发送即被查看
            "accepted": status_dist.get("accepted", {}).get("count", 0),
            "converted": status_dist.get("converted", {}).get("count", 0),
        }

        # 计算转换率
        conversion_rates = {}
        prev_stage_count = total_quotes
        for stage, count in funnel_stages.items():
            if prev_stage_count > 0:
                conversion_rates[stage] = f"{(count / prev_stage_count * 100):.1f}%"
            else:
                conversion_rates[stage] = "0.0%"
            prev_stage_count = count

        return {
            "stages": funnel_stages,
            "conversion_rates": conversion_rates,
            "bottlenecks": self._identify_bottlenecks(funnel_stages),
        }

    def _calculate_growth_rate(self, monthly_stats: list[dict[str, Any]]) -> str:
        """计算增长率"""
        if len(monthly_stats) < 2:
            return "数据不足"

        # 比较最近两个月
        current_month = monthly_stats[-1]
        previous_month = monthly_stats[-2]

        current_success = current_month["successful_quotes"]
        previous_success = previous_month["successful_quotes"]

        if previous_success > 0:
            growth_rate = (
                (current_success - previous_success) / previous_success
            ) * 100
            return f"{growth_rate:+.1f}%"
        else:
            return "N/A"

    def _analyze_seasonality(
        self, monthly_stats: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """分析季节性"""
        if len(monthly_stats) < 12:
            return {"analysis": "数据不足，需要至少12个月数据"}

        # 简单的季节性分析
        quarterly_data = {}
        for stat in monthly_stats:
            month = int(stat["month"].split("-")[1])
            quarter = (month - 1) // 3 + 1

            if quarter not in quarterly_data:
                quarterly_data[quarter] = {"total": 0, "successful": 0}

            quarterly_data[quarter]["total"] += stat["total_quotes"]
            quarterly_data[quarter]["successful"] += stat["successful_quotes"]

        # 计算各季度成功率
        quarterly_rates = {}
        for quarter, data in quarterly_data.items():
            if data["total"] > 0:
                rate = data["successful"] / data["total"]
                quarterly_rates[f"Q{quarter}"] = f"{rate * 100:.1f}%"

        return {
            "quarterly_performance": quarterly_rates,
            "peak_quarter": max(
                quarterly_rates.items(), key=lambda x: float(x[1].replace("%", ""))
            )[0],
            "analysis": "基于历史数据的季节性分析",
        }

    def _compare_with_target(self, current_rate: str, target_rate: str) -> str:
        """与目标对比"""
        try:
            current = float(current_rate.replace("%", ""))
            target = float(target_rate.replace("%", ""))

            if current >= target:
                return f"超出目标 {current - target:.1f}%"
            else:
                return f"低于目标 {target - current:.1f}%"
        except ValueError:
            return "无法比较"

    def _identify_bottlenecks(self, funnel_stages: dict[str, int]) -> list[str]:
        """识别转换瓶颈"""
        bottlenecks = []

        stages = list(funnel_stages.items())
        for i in range(1, len(stages)):
            current_stage, current_count = stages[i]
            prev_stage, prev_count = stages[i - 1]

            if prev_count > 0:
                conversion_rate = current_count / prev_count
                if conversion_rate < 0.5:  # 转换率低于50%
                    bottlenecks.append(
                        f"{prev_stage} -> {current_stage}: "
                        f"转换率仅{conversion_rate * 100:.1f}%"
                    )

        return bottlenecks if bottlenecks else ["无明显瓶颈"]
