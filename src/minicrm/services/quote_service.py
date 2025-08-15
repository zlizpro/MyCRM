"""
MiniCRM 报价管理服务

实现报价业务逻辑，包括：
- 报价创建、编辑、删除和查询
- 报价历史比对和分析
- 智能报价建议算法
- 报价成功率统计分析
- 报价过期管理和预警

设计原则：
- 继承CRUDService提供基础功能
- 集成transfunctions进行数据计算和验证
- 支持多种报价类型和状态管理
- 提供智能分析和建议功能
- 确保数据一致性和业务规则
"""

from datetime import datetime, timedelta
from typing import Any

from transfunctions import (
    ValidationError,
    format_currency,
)
from transfunctions.calculations.statistics import calculate_average
from transfunctions.formatting.currency import format_percentage
from transfunctions.validation.core import validate_required_fields

from ..core import BusinessLogicError, ServiceError
from ..models import Quote
from ..models.quote import QuoteStatus
from .base_service import CRUDService, register_service


@register_service("quote_service")
class QuoteService(CRUDService):
    """
    报价管理服务

    提供完整的报价管理功能，包括报价创建、比对分析、
    智能建议和成功率统计等业务逻辑。
    """

    def __init__(self, dao=None):
        """
        初始化报价服务

        Args:
            dao: 报价数据访问对象
        """
        super().__init__(dao, Quote)
        self._price_analysis_cache = {}
        self._success_rate_cache = {}

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "报价管理服务"

    # ==================== 基础CRUD操作 ====================

    def _validate_create_data(self, data: dict[str, Any]) -> None:
        """验证创建报价数据"""
        required_fields = ["customer_name", "items"]
        errors = validate_required_fields(data, required_fields)
        if errors:
            raise ValidationError("; ".join(errors))

        # 验证报价项目
        if not data.get("items") or not isinstance(data["items"], list):
            raise ValidationError("报价必须包含至少一个项目")

        # 验证每个报价项目
        for i, item_data in enumerate(data["items"]):
            # 如果已经是QuoteItem对象，转换为字典进行验证
            if hasattr(item_data, "to_dict"):
                item_dict = item_data.to_dict()
            elif isinstance(item_data, dict):
                item_dict = item_data
            else:
                raise ValidationError(f"报价项目{i + 1}数据格式不正确")

            item_required = ["product_name", "quantity", "unit_price"]
            item_errors = validate_required_fields(item_dict, item_required)
            if item_errors:
                raise ValidationError(f"报价项目{i + 1}: {'; '.join(item_errors)}")

    def _validate_update_data(self, data: dict[str, Any]) -> None:
        """验证更新报价数据"""
        # 更新时不要求所有字段都存在
        if "items" in data:
            if not isinstance(data["items"], list):
                raise ValidationError("报价项目必须是列表格式")

            for i, item_data in enumerate(data["items"]):
                if not isinstance(item_data, dict):
                    raise ValidationError(f"报价项目{i + 1}数据格式不正确")

    def _perform_create(self, data: dict[str, Any]) -> Quote:
        """执行创建报价操作"""
        try:
            # 创建报价实例
            quote = Quote.from_dict(data)
            quote.validate()

            # 计算总金额
            quote.calculate_totals()

            # 如果有DAO，保存到数据库
            if self._dao:
                quote_id = self._dao.insert(quote.to_dict())
                quote.id = quote_id

            # 清除相关缓存
            self._clear_analysis_cache(quote.customer_id)

            self._log_operation(
                "创建报价",
                {
                    "quote_id": quote.id,
                    "customer": quote.customer_name,
                    "total": quote.get_formatted_total(),
                },
            )

            return quote

        except Exception as e:
            raise ServiceError(f"创建报价失败: {e}") from e

    def _perform_get_by_id(self, record_id: int) -> Quote | None:
        """执行根据ID获取报价操作"""
        if not self._dao:
            return None

        try:
            data = self._dao.get_by_id(record_id)
            if data:
                return Quote.from_dict(data)
            return None
        except Exception as e:
            raise ServiceError(f"获取报价失败: {e}") from e

    def _perform_update(self, record_id: int, data: dict[str, Any]) -> Quote:
        """执行更新报价操作"""
        try:
            # 获取现有报价
            existing_quote = self.get_by_id(record_id)
            if not existing_quote:
                raise BusinessLogicError(f"报价不存在: {record_id}")

            # 更新数据
            updated_data = existing_quote.to_dict()
            updated_data.update(data)

            # 创建更新后的报价实例
            updated_quote = Quote.from_dict(updated_data)
            updated_quote.validate()
            updated_quote.calculate_totals()

            # 保存到数据库
            if self._dao:
                self._dao.update(record_id, updated_quote.to_dict())

            # 清除相关缓存
            self._clear_analysis_cache(updated_quote.customer_id)

            self._log_operation(
                "更新报价",
                {"quote_id": record_id, "customer": updated_quote.customer_name},
            )

            return updated_quote

        except Exception as e:
            raise ServiceError(f"更新报价失败: {e}") from e

    def _perform_delete(self, record_id: int) -> bool:
        """执行删除报价操作"""
        try:
            # 获取报价信息用于日志
            quote = self.get_by_id(record_id)
            if not quote:
                raise BusinessLogicError(f"报价不存在: {record_id}")

            # 检查是否可以删除
            if quote.quote_status in [QuoteStatus.ACCEPTED, QuoteStatus.CONVERTED]:
                raise BusinessLogicError("已接受或已转换的报价不能删除")

            # 删除报价
            if self._dao:
                result = self._dao.delete(record_id)
                if result:
                    # 清除相关缓存
                    self._clear_analysis_cache(quote.customer_id)

                    self._log_operation(
                        "删除报价",
                        {"quote_id": record_id, "customer": quote.customer_name},
                    )

                return result

            return False

        except Exception as e:
            raise ServiceError(f"删除报价失败: {e}") from e

    def _perform_list_all(self, filters: dict[str, Any] = None) -> list[Quote]:
        """执行获取所有报价操作"""
        if not self._dao:
            return []

        try:
            data_list = self._dao.search(filters)
            return [Quote.from_dict(data) for data in data_list]
        except Exception as e:
            raise ServiceError(f"获取报价列表失败: {e}") from e

    # ==================== 报价比对功能 ====================

    def compare_quotes(
        self, quote_ids: list[int], comparison_type: str = "detailed"
    ) -> dict[str, Any]:
        """
        比较多个报价

        Args:
            quote_ids: 要比较的报价ID列表
            comparison_type: 比较类型 ('summary', 'detailed', 'trend')

        Returns:
            Dict[str, Any]: 比较结果

        Raises:
            ValidationError: 当参数无效时
            ServiceError: 当比较失败时
        """
        try:
            if len(quote_ids) < 2:
                raise ValidationError("至少需要两个报价进行比较")

            # 获取报价数据
            quotes = []
            for quote_id in quote_ids:
                quote = self.get_by_id(quote_id)
                if not quote:
                    raise BusinessLogicError(f"报价不存在: {quote_id}")
                quotes.append(quote)

            # 根据比较类型执行不同的比较逻辑
            if comparison_type == "summary":
                return self._compare_quotes_summary(quotes)
            elif comparison_type == "detailed":
                return self._compare_quotes_detailed(quotes)
            elif comparison_type == "trend":
                return self._compare_quotes_trend(quotes)
            else:
                raise ValidationError(f"不支持的比较类型: {comparison_type}")

        except Exception as e:
            self._handle_service_error("报价比较", e)

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
                    "quote_date": quote.get_formatted_quote_date(),
                    "total_amount": quote.get_formatted_total(),
                    "status": quote.get_status_display(),
                    "item_count": len(quote.items) if quote.items else 0,
                }
                for quote in quotes
            ],
            "statistics": {
                "min_amount": format_currency(min(total_amounts)),
                "max_amount": format_currency(max(total_amounts)),
                "avg_amount": format_currency(calculate_average(total_amounts)),
                "amount_range": format_currency(
                    max(total_amounts) - min(total_amounts)
                ),
            },
        }

    def _compare_quotes_detailed(self, quotes: list[Quote]) -> dict[str, Any]:
        """生成详细报价比较"""
        # 收集所有产品信息
        all_products = {}
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

        # 计算产品价格统计
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

        return {
            "comparison_type": "detailed",
            "quote_count": len(quotes),
            "quotes": self._compare_quotes_summary(quotes)["quotes"],
            "product_analysis": product_analysis,
            "summary": self._compare_quotes_summary(quotes)["statistics"],
        }

    def _compare_quotes_trend(self, quotes: list[Quote]) -> dict[str, Any]:
        """生成报价趋势比较"""
        # 按日期排序
        sorted_quotes = sorted(quotes, key=lambda q: q.quote_date or datetime.min)

        if len(sorted_quotes) < 2:
            return {"comparison_type": "trend", "error": "需要至少两个报价才能分析趋势"}

        # 计算趋势数据
        dates = []
        amounts = []

        for quote in sorted_quotes:
            if quote.quote_date:
                dates.append(quote.quote_date.strftime("%Y-%m-%d"))
                amounts.append(float(quote.total_amount))

        # 计算增长率
        growth_rates = []
        for i in range(1, len(amounts)):
            if amounts[i - 1] != 0:
                growth_rate = (amounts[i] - amounts[i - 1]) / amounts[i - 1]
                growth_rates.append(growth_rate)

        avg_growth_rate = calculate_average(growth_rates) if growth_rates else 0

        return {
            "comparison_type": "trend",
            "quote_count": len(sorted_quotes),
            "trend_data": [
                {
                    "date": dates[i],
                    "amount": amounts[i],
                    "formatted_amount": format_currency(amounts[i]),
                    "growth_rate": growth_rates[i - 1] if i > 0 else 0,
                    "formatted_growth_rate": format_percentage(growth_rates[i - 1])
                    if i > 0
                    else "基准",
                }
                for i in range(len(sorted_quotes))
            ],
            "statistics": {
                "average_growth_rate": format_percentage(avg_growth_rate),
                "total_change": format_currency(amounts[-1] - amounts[0]),
                "total_change_percentage": format_percentage(
                    (amounts[-1] - amounts[0]) / amounts[0] if amounts[0] != 0 else 0
                ),
                "trend_direction": "上升"
                if avg_growth_rate > 0
                else "下降"
                if avg_growth_rate < 0
                else "平稳",
            },
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
            Dict[str, Any]: 客户报价历史和分析
        """
        try:
            # 获取客户报价
            filters = {"customer_id": customer_id}
            quotes = self._perform_list_all(filters)

            # 按日期排序
            quotes.sort(key=lambda q: q.quote_date or datetime.min, reverse=True)

            # 限制数量
            if limit:
                quotes = quotes[:limit]

            result = {
                "customer_id": customer_id,
                "quote_count": len(quotes),
                "quotes": [quote.to_dict() for quote in quotes],
            }

            if include_analysis and len(quotes) > 1:
                # 添加趋势分析
                result["analysis"] = self._analyze_customer_quote_trend(quotes)

            return result

        except Exception as e:
            self._handle_service_error("获取客户报价历史", e)

    def _analyze_customer_quote_trend(self, quotes: list[Quote]) -> dict[str, Any]:
        """分析客户报价趋势"""
        if len(quotes) < 2:
            return {}

        # 计算基础统计
        amounts = [float(quote.total_amount) for quote in quotes]
        # dates变量暂时不使用，但保留用于未来的时间分析功能
        # dates = [quote.quote_date for quote in quotes if quote.quote_date]

        # 成功率统计
        total_quotes = len(quotes)
        accepted_quotes = len(
            [q for q in quotes if q.quote_status == QuoteStatus.ACCEPTED]
        )
        converted_quotes = len(
            [q for q in quotes if q.quote_status == QuoteStatus.CONVERTED]
        )

        success_rate = (
            (accepted_quotes + converted_quotes) / total_quotes
            if total_quotes > 0
            else 0
        )

        # 平均响应时间
        response_times = []
        for quote in quotes:
            if quote.sent_date and quote.response_date:
                response_time = (quote.response_date - quote.sent_date).days
                response_times.append(response_time)

        avg_response_time = calculate_average(response_times) if response_times else 0

        return {
            "total_quotes": total_quotes,
            "success_rate": format_percentage(success_rate),
            "average_amount": format_currency(calculate_average(amounts)),
            "amount_trend": self._calculate_amount_trend(amounts),
            "average_response_time": f"{avg_response_time:.1f}天",
            "status_distribution": self._calculate_status_distribution(quotes),
            "recommendations": self._generate_customer_recommendations(quotes),
        }

    def _calculate_amount_trend(self, amounts: list[float]) -> str:
        """计算金额趋势"""
        if len(amounts) < 2:
            return "数据不足"

        recent_avg = calculate_average(amounts[:3])  # 最近3个报价
        historical_avg = (
            calculate_average(amounts[3:]) if len(amounts) > 3 else recent_avg
        )

        if recent_avg > historical_avg * 1.1:
            return "上升趋势"
        elif recent_avg < historical_avg * 0.9:
            return "下降趋势"
        else:
            return "平稳"

    def _calculate_status_distribution(self, quotes: list[Quote]) -> dict[str, Any]:
        """计算状态分布"""
        status_count = {}
        for quote in quotes:
            status = quote.quote_status.value
            status_count[status] = status_count.get(status, 0) + 1

        total = len(quotes)
        return {
            status: {"count": count, "percentage": format_percentage(count / total)}
            for status, count in status_count.items()
        }

    # ==================== 智能报价建议 ====================

    def generate_quote_suggestions(
        self,
        customer_id: int,
        product_items: list[dict[str, Any]],
        suggestion_type: str = "comprehensive",
    ) -> dict[str, Any]:
        """
        生成智能报价建议

        Args:
            customer_id: 客户ID
            product_items: 产品项目列表
            suggestion_type: 建议类型 ('price', 'strategy', 'comprehensive')

        Returns:
            Dict[str, Any]: 报价建议
        """
        try:
            # 获取历史数据
            customer_history = self.get_customer_quote_history(customer_id, limit=20)
            market_data = self._get_market_price_data(product_items)

            # 根据建议类型生成不同的建议
            if suggestion_type == "price":
                return self._generate_price_suggestions(
                    customer_history, product_items, market_data
                )
            elif suggestion_type == "strategy":
                return self._generate_strategy_suggestions(
                    customer_history, product_items
                )
            elif suggestion_type == "comprehensive":
                price_suggestions = self._generate_price_suggestions(
                    customer_history, product_items, market_data
                )
                strategy_suggestions = self._generate_strategy_suggestions(
                    customer_history, product_items
                )

                return {
                    "suggestion_type": "comprehensive",
                    "price_suggestions": price_suggestions,
                    "strategy_suggestions": strategy_suggestions,
                    "overall_recommendation": self._generate_overall_recommendation(
                        customer_history, price_suggestions, strategy_suggestions
                    ),
                }
            else:
                raise ValidationError(f"不支持的建议类型: {suggestion_type}")

        except Exception as e:
            self._handle_service_error("生成报价建议", e)

    def _generate_price_suggestions(
        self,
        customer_history: dict[str, Any],
        product_items: list[dict[str, Any]],
        market_data: dict[str, Any],
    ) -> dict[str, Any]:
        """生成价格建议"""
        suggestions = []

        for item in product_items:
            product_name = item.get("product_name", "")

            # 获取历史价格数据
            historical_prices = self._get_historical_prices(
                customer_history, product_name
            )
            market_price = market_data.get(product_name, {})

            # 计算建议价格
            suggested_price = self._calculate_suggested_price(
                historical_prices, market_price, customer_history
            )

            # 价格区间建议
            price_range = self._calculate_price_range(suggested_price, customer_history)

            suggestions.append(
                {
                    "product_name": product_name,
                    "suggested_price": format_currency(suggested_price),
                    "price_range": {
                        "min": format_currency(price_range["min"]),
                        "max": format_currency(price_range["max"]),
                    },
                    "confidence_level": self._calculate_confidence_level(
                        historical_prices
                    ),
                    "reasoning": self._generate_price_reasoning(
                        historical_prices, market_price, suggested_price
                    ),
                }
            )

        return {
            "suggestion_type": "price",
            "product_suggestions": suggestions,
            "overall_strategy": self._determine_pricing_strategy(customer_history),
        }

    def _generate_strategy_suggestions(
        self, customer_history: dict[str, Any], product_items: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """生成策略建议"""
        quotes = customer_history.get("quotes", [])

        # 分析客户行为模式
        behavior_analysis = self._analyze_customer_behavior(quotes)

        # 生成策略建议
        strategies = []

        # 基于成功率的建议
        if customer_history.get("analysis", {}).get("success_rate"):
            success_rate_str = customer_history["analysis"]["success_rate"]
            # 简单解析百分比字符串
            try:
                success_rate = float(success_rate_str.replace("%", "")) / 100
            except (ValueError, AttributeError):
                success_rate = 0

            if success_rate < 0.3:
                strategies.append(
                    {
                        "type": "pricing",
                        "priority": "high",
                        "suggestion": "考虑降低报价以提高成功率",
                        "reasoning": (
                            f"当前成功率仅为{success_rate_str}，建议调整定价策略"
                        ),
                    }
                )
            elif success_rate > 0.8:
                strategies.append(
                    {
                        "type": "pricing",
                        "priority": "medium",
                        "suggestion": "可以适当提高报价获得更好利润",
                        "reasoning": f"当前成功率高达{success_rate_str}，有提价空间",
                    }
                )

        return {
            "suggestion_type": "strategy",
            "strategies": strategies,
            "behavior_analysis": behavior_analysis,
            "recommended_actions": self._generate_recommended_actions(strategies),
        }

    def _analyze_customer_behavior(
        self, quotes: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """分析客户行为模式"""
        if not quotes:
            return {}

        # 决策速度分析
        decision_speeds = [
            "快速" if "accepted" in quote.get("quote_status", "") else "慢速"
            for quote in quotes
            if quote.get("sent_date") and quote.get("response_date")
        ]

        # 价格敏感度分析
        price_sensitivity = "中等"  # 简化实现

        # 季节性模式
        seasonal_pattern = "无明显季节性"  # 简化实现

        return {
            "decision_speed": (
                "快速"
                if len([s for s in decision_speeds if s == "快速"])
                > len(decision_speeds) / 2
                else "慢速"
            ),
            "price_sensitivity": price_sensitivity,
            "seasonal_pattern": seasonal_pattern,
            "preferred_quote_size": self._analyze_preferred_quote_size(quotes),
        }

    def _analyze_preferred_quote_size(self, quotes: list[dict[str, Any]]) -> str:
        """分析偏好的报价规模"""
        if not quotes:
            return "未知"

        amounts = []
        for quote in quotes:
            try:
                # 简化处理，假设total_amount是数字
                amount = float(quote.get("total_amount", 0))
                amounts.append(amount)
            except (ValueError, TypeError):
                continue

        if not amounts:
            return "未知"

        avg_amount = calculate_average(amounts)

        if avg_amount < 10000:
            return "小额订单偏好"
        elif avg_amount < 100000:
            return "中等订单偏好"
        else:
            return "大额订单偏好"

    # ==================== 成功率统计分析 ====================

    def calculate_success_rate_statistics(
        self, filters: dict[str, Any] = None, time_period: int = 12
    ) -> dict[str, Any]:
        """
        计算报价成功率统计

        Args:
            filters: 过滤条件
            time_period: 时间周期（月）

        Returns:
            Dict[str, Any]: 成功率统计数据
        """
        try:
            # 构建时间过滤条件
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_period * 30)

            time_filters = {
                "quote_date_gte": start_date.isoformat(),
                "quote_date_lte": end_date.isoformat(),
            }

            if filters:
                time_filters.update(filters)

            # 获取报价数据
            quotes = self._perform_list_all(time_filters)

            # 计算基础统计
            total_quotes = len(quotes)
            if total_quotes == 0:
                return {
                    "period": f"{time_period}个月",
                    "total_quotes": 0,
                    "message": "指定时间段内无报价数据",
                }

            # 状态统计
            status_stats = {}
            for quote in quotes:
                status = quote.quote_status.value
                status_stats[status] = status_stats.get(status, 0) + 1

            # 成功率计算
            successful_quotes = status_stats.get("accepted", 0) + status_stats.get(
                "converted", 0
            )
            success_rate = successful_quotes / total_quotes

            # 按月份统计
            monthly_stats = self._calculate_monthly_success_rate(quotes)

            return {
                "period": f"{time_period}个月",
                "total_quotes": total_quotes,
                "successful_quotes": successful_quotes,
                "success_rate": format_percentage(success_rate),
                "status_distribution": {
                    status: {
                        "count": count,
                        "percentage": format_percentage(count / total_quotes),
                    }
                    for status, count in status_stats.items()
                },
                "monthly_trends": monthly_stats,
                "insights": self._generate_success_rate_insights(
                    success_rate, monthly_stats
                ),
            }

        except Exception as e:
            self._handle_service_error("计算成功率统计", e)

    def _calculate_monthly_success_rate(
        self, quotes: list[Quote]
    ) -> list[dict[str, Any]]:
        """计算月度成功率"""
        monthly_data = {}

        for quote in quotes:
            if not quote.quote_date:
                continue

            month_key = quote.quote_date.strftime("%Y-%m")
            if month_key not in monthly_data:
                monthly_data[month_key] = {"total": 0, "successful": 0}

            monthly_data[month_key]["total"] += 1
            if quote.quote_status in [QuoteStatus.ACCEPTED, QuoteStatus.CONVERTED]:
                monthly_data[month_key]["successful"] += 1

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
                }
            )

        return monthly_stats

    # ==================== 过期管理 ====================

    def get_expiring_quotes(self, days_ahead: int = 7) -> list[dict[str, Any]]:
        """
        获取即将过期的报价

        Args:
            days_ahead: 提前天数

        Returns:
            List[Dict[str, Any]]: 即将过期的报价列表
        """
        try:
            # 获取所有未完成的报价
            filters = {"quote_status__in": ["draft", "pending", "sent", "viewed"]}
            quotes = self._perform_list_all(filters)

            # 筛选即将过期的报价
            expiring_quotes = [
                {
                    "quote": quote.to_dict(),
                    "remaining_days": quote.get_remaining_days(),
                    "urgency_level": self._calculate_urgency_level(
                        quote.get_remaining_days()
                    ),
                }
                for quote in quotes
                if quote.is_expiring_soon(days_ahead)
            ]

            # 按剩余天数排序
            expiring_quotes.sort(key=lambda x: x["remaining_days"])

            return expiring_quotes

        except Exception as e:
            self._handle_service_error("获取即将过期报价", e)

    def _calculate_urgency_level(self, remaining_days: int) -> str:
        """计算紧急程度"""
        if remaining_days <= 1:
            return "紧急"
        elif remaining_days <= 3:
            return "高"
        elif remaining_days <= 7:
            return "中"
        else:
            return "低"

    def update_expired_quotes(self) -> dict[str, Any]:
        """
        更新已过期的报价状态

        Returns:
            Dict[str, Any]: 更新结果
        """
        try:
            # 获取所有可能过期的报价
            filters = {"quote_status__in": ["pending", "sent", "viewed"]}
            quotes = self._perform_list_all(filters)

            updated_count = 0
            for quote in quotes:
                if quote.is_expired() and quote.quote_status != QuoteStatus.EXPIRED:
                    # 更新状态为已过期
                    self._perform_update(
                        quote.id, {"quote_status": QuoteStatus.EXPIRED.value}
                    )
                    updated_count += 1

            self._log_operation("批量更新过期报价", {"updated_count": updated_count})

            return {
                "updated_count": updated_count,
                "message": f"已更新{updated_count}个过期报价的状态",
            }

        except Exception as e:
            self._handle_service_error("更新过期报价", e)

    # ==================== 辅助方法 ====================

    def _clear_analysis_cache(self, customer_id: int | None = None) -> None:
        """清除分析缓存"""
        if customer_id:
            cache_keys = [
                key for key in self._price_analysis_cache if str(customer_id) in key
            ]
            for key in cache_keys:
                del self._price_analysis_cache[key]
        else:
            self._price_analysis_cache.clear()
            self._success_rate_cache.clear()

    def _get_market_price_data(
        self, product_items: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """获取市场价格数据（简化实现）"""
        # 实际实现应该从外部数据源获取市场价格
        market_data = {}
        for item in product_items:
            product_name = item.get("product_name", "")
            market_data[product_name] = {
                "average_price": 1000.0,  # 简化数据
                "price_trend": "stable",
            }
        return market_data

    def _get_historical_prices(
        self, customer_history: dict[str, Any], product_name: str
    ) -> list[float]:
        """获取历史价格数据"""
        prices = []
        quotes = customer_history.get("quotes", [])

        for quote in quotes:
            items = quote.get("items", [])
            for item in items:
                if item.get("product_name") == product_name:
                    try:
                        price = float(item.get("unit_price", 0))
                        prices.append(price)
                    except (ValueError, TypeError):
                        continue

        return prices

    def _calculate_suggested_price(
        self,
        historical_prices: list[float],
        market_price: dict[str, Any],
        customer_history: dict[str, Any],
    ) -> float:
        """计算建议价格"""
        if not historical_prices:
            return market_price.get("average_price", 1000.0)

        # 基于历史价格的加权平均
        recent_prices = historical_prices[:3]  # 最近3次价格
        historical_avg = calculate_average(historical_prices)
        recent_avg = (
            calculate_average(recent_prices) if recent_prices else historical_avg
        )

        # 考虑市场价格
        market_avg = market_price.get("average_price", historical_avg)

        # 加权计算建议价格
        suggested_price = recent_avg * 0.5 + historical_avg * 0.3 + market_avg * 0.2

        return suggested_price

    def _calculate_price_range(
        self, suggested_price: float, customer_history: dict[str, Any]
    ) -> dict[str, float]:
        """计算价格区间"""
        # 基于客户历史成功率调整价格区间
        analysis = customer_history.get("analysis", {})
        success_rate_str = analysis.get("success_rate", "50%")

        try:
            success_rate = float(success_rate_str.replace("%", "")) / 100
        except (ValueError, AttributeError):
            success_rate = 0.5

        # 成功率高的客户可以报更高价格
        if success_rate > 0.7:
            price_range = {"min": suggested_price * 0.95, "max": suggested_price * 1.15}
        elif success_rate < 0.3:
            price_range = {"min": suggested_price * 0.85, "max": suggested_price * 1.05}
        else:
            price_range = {"min": suggested_price * 0.9, "max": suggested_price * 1.1}

        return price_range

    def _calculate_confidence_level(self, historical_prices: list[float]) -> str:
        """计算置信度"""
        if len(historical_prices) >= 5:
            return "高"
        elif len(historical_prices) >= 2:
            return "中"
        else:
            return "低"

    def _generate_price_reasoning(
        self,
        historical_prices: list[float],
        market_price: dict[str, Any],
        suggested_price: float,
    ) -> str:
        """生成价格推理说明"""
        if not historical_prices:
            return "基于市场平均价格"

        historical_avg = calculate_average(historical_prices)
        # market_avg变量保留用于未来的市场价格比较功能
        # market_avg = market_price.get("average_price", historical_avg)

        if abs(suggested_price - historical_avg) / historical_avg < 0.1:
            return "基于历史价格稳定性"
        elif suggested_price > historical_avg:
            return "考虑市场上涨趋势和客户接受度"
        else:
            return "基于竞争力和成功率优化"

    def _determine_pricing_strategy(self, customer_history: dict[str, Any]) -> str:
        """确定定价策略"""
        analysis = customer_history.get("analysis", {})
        success_rate_str = analysis.get("success_rate", "50%")

        try:
            success_rate = float(success_rate_str.replace("%", "")) / 100
        except (ValueError, AttributeError):
            success_rate = 0.5

        if success_rate > 0.8:
            return "价值定价策略 - 客户接受度高，可适当提价"
        elif success_rate < 0.3:
            return "竞争定价策略 - 需要降低价格提高竞争力"
        else:
            return "平衡定价策略 - 在价格和成功率间寻求平衡"

    def _generate_overall_recommendation(
        self,
        customer_history: dict[str, Any],
        price_suggestions: dict[str, Any],
        strategy_suggestions: dict[str, Any],
    ) -> dict[str, Any]:
        """生成综合建议"""
        return {
            "priority_actions": [
                "根据价格建议调整产品定价",
                "实施推荐的策略建议",
                "监控客户反馈和成功率变化",
            ],
            "risk_assessment": "中等风险",
            "expected_outcome": "预期成功率提升10-20%",
            "follow_up_actions": ["跟踪报价结果", "收集客户反馈", "调整策略参数"],
        }

    def _generate_recommended_actions(
        self, strategies: list[dict[str, Any]]
    ) -> list[str]:
        """生成推荐行动"""
        actions = []

        high_priority = [s for s in strategies if s.get("priority") == "high"]
        if high_priority:
            actions.append("优先处理高优先级策略建议")

        actions.extend(
            ["定期回顾和调整报价策略", "建立客户反馈收集机制", "监控竞争对手价格变化"]
        )

        return actions

    def _generate_customer_recommendations(self, quotes: list[Quote]) -> list[str]:
        """生成客户相关建议"""
        recommendations = []

        if len(quotes) > 5:
            recommendations.append("建立长期合作关系，考虑框架协议")

        # 基于报价状态分布给出建议
        rejected_count = len(
            [q for q in quotes if q.quote_status == QuoteStatus.REJECTED]
        )
        if rejected_count > len(quotes) * 0.5:
            recommendations.append("分析拒绝原因，调整报价策略")

        recommendations.extend(["定期沟通了解客户需求变化", "提供增值服务提高竞争力"])

        return recommendations

    def _generate_success_rate_insights(
        self, overall_success_rate: float, monthly_stats: list[dict[str, Any]]
    ) -> list[str]:
        """生成成功率洞察"""
        insights = []

        if overall_success_rate > 0.7:
            insights.append("整体成功率较高，可考虑适当提高报价获得更好利润")
        elif overall_success_rate < 0.3:
            insights.append("成功率偏低，建议分析失败原因并调整策略")

        # 分析月度趋势
        if len(monthly_stats) >= 2:
            try:
                recent_rate = (
                    float(monthly_stats[-1]["success_rate"].replace("%", "")) / 100
                )
                previous_rate = (
                    float(monthly_stats[-2]["success_rate"].replace("%", "")) / 100
                )

                if recent_rate > previous_rate * 1.1:
                    insights.append("最近成功率有所提升，当前策略有效")
                elif recent_rate < previous_rate * 0.9:
                    insights.append("最近成功率下降，需要关注市场变化")
            except (ValueError, AttributeError):
                pass

        insights.append("建议定期分析成功率数据，持续优化报价策略")

        return insights
