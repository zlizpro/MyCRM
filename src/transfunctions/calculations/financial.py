"""
Transfunctions - 财务计算

提供报价、财务等相关的计算功能.
"""

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Any


# 配置日志
logger = logging.getLogger(__name__)


class CalculationError(Exception):
    """计算异常类"""

    def __init__(self, message: str, context=None):
        """初始化计算异常

        Args:
            message: 错误消息
            context: 错误上下文信息
        """
        self.message = message
        self.context = context or {}
        super().__init__(self.message)


@dataclass
class QuoteItem:
    """报价项目数据类"""

    product_name: str
    unit_price: Decimal
    quantity: int
    discount_rate: float = 0.0  # 折扣率 (0-1)
    tax_rate: float = 0.13  # 税率,默认13%

    @property
    def subtotal(self) -> Decimal:
        """计算小计金额(含折扣,不含税)"""
        base_amount = self.unit_price * self.quantity
        discount_amount = base_amount * Decimal(str(self.discount_rate))
        return base_amount - discount_amount

    @property
    def tax_amount(self) -> Decimal:
        """计算税额"""
        return self.subtotal * Decimal(str(self.tax_rate))

    @property
    def total_amount(self) -> Decimal:
        """计算总金额(含税)"""
        return self.subtotal + self.tax_amount


def calculate_quote_total(
    quote_items: list[dict[str, Any]],
    global_discount_rate: float = 0.0,
    additional_fees: dict[str, Decimal] | None = None,
) -> dict[str, Decimal]:
    """计算报价总额

    Args:
        quote_items: 报价项目列表
        global_discount_rate: 全局折扣率
        additional_fees: 额外费用(如运费、安装费等)

    Returns:
        Dict[str, Decimal]: 包含各项金额的字典

    Raises:
        CalculationError: 当计算参数无效时

    Example:
        >>> items = [{"product_name": "产品A", "unit_price": 100, "quantity": 10}]
        >>> result = calculate_quote_total(items)
        >>> print(f"总金额: {result['total_amount']}")
    """
    try:
        if not quote_items:
            raise CalculationError("报价项目不能为空")

        # 转换为QuoteItem对象
        items = []
        for item_data in quote_items:
            item = QuoteItem(
                product_name=item_data.get("product_name", ""),
                unit_price=Decimal(str(item_data.get("unit_price", 0))),
                quantity=int(item_data.get("quantity", 0)),
                discount_rate=float(item_data.get("discount_rate", 0)),
                tax_rate=float(item_data.get("tax_rate", 0.13)),
            )
            items.append(item)

        # 计算各项金额
        subtotal_before_discount = sum(
            item.unit_price * item.quantity for item in items
        )
        item_discount_amount = sum(
            item.unit_price * item.quantity * Decimal(str(item.discount_rate))
            for item in items
        )
        subtotal_after_item_discount = subtotal_before_discount - item_discount_amount

        # 应用全局折扣
        global_discount_amount = subtotal_after_item_discount * Decimal(
            str(global_discount_rate)
        )
        subtotal_after_all_discounts = (
            subtotal_after_item_discount - global_discount_amount
        )

        # 计算税额
        total_tax_amount = sum(item.tax_amount for item in items)

        # 额外费用
        additional_fees = additional_fees or {}
        total_additional_fees = Decimal(str(sum(additional_fees.values())))

        # 最终总额
        total_amount = (
            subtotal_after_all_discounts + total_tax_amount + total_additional_fees
        )

        result = {
            "subtotal_before_discount": subtotal_before_discount.quantize(
                Decimal("0.01")
            ),
            "item_discount_amount": item_discount_amount.quantize(Decimal("0.01")),
            "global_discount_amount": global_discount_amount.quantize(Decimal("0.01")),
            "subtotal_after_discounts": subtotal_after_all_discounts.quantize(
                Decimal("0.01")
            ),
            "tax_amount": total_tax_amount.quantize(Decimal("0.01")),
            "additional_fees": total_additional_fees.quantize(Decimal("0.01")),
            "total_amount": total_amount.quantize(Decimal("0.01")),
        }

        logger.info(f"报价总额计算完成: {result['total_amount']}")
        return result

    except (ValueError, TypeError, ArithmeticError) as e:
        raise CalculationError(
            f"报价总额计算失败: {str(e)}",
            {"items_count": len(quote_items), "global_discount": global_discount_rate},
        ) from e


def calculate_compound_interest(principal: float, rate: float, periods: int) -> float:
    """计算复利

    Args:
        principal: 本金
        rate: 利率(如0.05表示5%)
        periods: 期数

    Returns:
        float: 复利后的金额
    """
    if rate <= 0 or periods <= 0:
        return principal

    return principal * ((1 + rate) ** periods)


def _calculate_subtotal(items: list[dict[str, Any]]) -> Decimal:
    """计算小计金额"""
    subtotal = Decimal("0")
    for item in items:
        quantity = Decimal(str(item.get("quantity", 0)))
        unit_price = Decimal(str(item.get("unit_price", 0)))
        item_total = quantity * unit_price
        subtotal += item_total
    return subtotal


def calculate_price_comparison(
    current_quote: dict[str, Any],
    historical_quotes: list[dict[str, Any]]
) -> dict[str, Any]:
    """计算价格比对分析

    Args:
        current_quote: 当前报价数据
        historical_quotes: 历史报价数据列表

    Returns:
        Dict[str, Any]: 价格比对分析结果

    Example:
        >>> current = {"total_amount": 120000, "items": [...]}
        >>> historical = [{"total_amount": 125000, "quote_date": "2024-12-01"}, ...]
        >>> result = calculate_price_comparison(current, historical)
        >>> print(f"价格变化: {result['price_change_percentage']}")
    """
    try:
        if not historical_quotes:
            return {
                "has_comparison": False,
                "message": "无历史报价数据进行比对"
            }

        current_amount = Decimal(str(current_quote.get("total_amount", 0)))
        
        # 按日期排序历史报价
        sorted_quotes = sorted(
            historical_quotes,
            key=lambda x: x.get("quote_date", ""),
            reverse=True
        )
        
        # 最近一次报价
        last_quote = sorted_quotes[0] if sorted_quotes else None
        last_amount = Decimal(str(last_quote.get("total_amount", 0))) if last_quote else Decimal("0")
        
        # 计算价格变化
        price_change = current_amount - last_amount
        price_change_percentage = (
            (price_change / last_amount * 100) if last_amount > 0 else Decimal("0")
        )
        
        # 计算历史平均价格
        historical_amounts = [Decimal(str(q.get("total_amount", 0))) for q in historical_quotes]
        avg_historical_price = sum(historical_amounts) / len(historical_amounts) if historical_amounts else Decimal("0")
        
        # 与平均价格比较
        avg_price_change = current_amount - avg_historical_price
        avg_price_change_percentage = (
            (avg_price_change / avg_historical_price * 100) if avg_historical_price > 0 else Decimal("0")
        )
        
        # 价格趋势分析
        trend = "稳定"
        if price_change_percentage > 5:
            trend = "上涨"
        elif price_change_percentage < -5:
            trend = "下降"
        
        # 竞争力分析
        competitiveness = "中等"
        if avg_price_change_percentage < -10:
            competitiveness = "很强"
        elif avg_price_change_percentage < -5:
            competitiveness = "较强"
        elif avg_price_change_percentage > 10:
            competitiveness = "较弱"
        elif avg_price_change_percentage > 5:
            competitiveness = "一般"
        
        result = {
            "has_comparison": True,
            "current_amount": float(current_amount),
            "last_amount": float(last_amount),
            "price_change": float(price_change),
            "price_change_percentage": float(price_change_percentage.quantize(Decimal("0.01"))),
            "avg_historical_price": float(avg_historical_price),
            "avg_price_change": float(avg_price_change),
            "avg_price_change_percentage": float(avg_price_change_percentage.quantize(Decimal("0.01"))),
            "trend": trend,
            "competitiveness": competitiveness,
            "historical_count": len(historical_quotes),
            "recommendations": _generate_price_recommendations(
                price_change_percentage, avg_price_change_percentage, trend
            )
        }
        
        logger.info(f"价格比对分析完成: 变化{price_change_percentage:.2f}%")
        return result
        
    except Exception as e:
        logger.error(f"价格比对分析失败: {e}")
        return {
            "has_comparison": False,
            "error": str(e)
        }


def calculate_trend_analysis(
    data_points: list[dict[str, Any]],
    value_field: str = "total_amount",
    date_field: str = "quote_date"
) -> dict[str, Any]:
    """计算价格趋势分析

    Args:
        data_points: 数据点列表
        value_field: 值字段名
        date_field: 日期字段名

    Returns:
        Dict[str, Any]: 趋势分析结果

    Example:
        >>> data = [{"total_amount": 100000, "quote_date": "2024-01-01"}, ...]
        >>> result = calculate_trend_analysis(data)
        >>> print(f"趋势: {result['trend_direction']}")
    """
    try:
        if len(data_points) < 2:
            return {
                "has_trend": False,
                "message": "数据点不足，无法分析趋势"
            }
        
        # 按日期排序
        sorted_data = sorted(data_points, key=lambda x: x.get(date_field, ""))
        
        # 提取数值
        values = []
        dates = []
        for point in sorted_data:
            try:
                value = float(point.get(value_field, 0))
                date = point.get(date_field, "")
                values.append(value)
                dates.append(date)
            except (ValueError, TypeError):
                continue
        
        if len(values) < 2:
            return {
                "has_trend": False,
                "message": "有效数据点不足"
            }
        
        # 计算趋势
        n = len(values)
        x_values = list(range(n))
        
        # 简单线性回归计算斜率
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        # 计算相关系数
        mean_x = sum_x / n
        mean_y = sum_y / n
        
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, values))
        denominator_x = sum((x - mean_x) ** 2 for x in x_values)
        denominator_y = sum((y - mean_y) ** 2 for y in values)
        
        correlation = numerator / (denominator_x * denominator_y) ** 0.5 if denominator_x * denominator_y > 0 else 0
        
        # 趋势方向
        if slope > 0.01:
            trend_direction = "上升"
        elif slope < -0.01:
            trend_direction = "下降"
        else:
            trend_direction = "稳定"
        
        # 趋势强度
        abs_correlation = abs(correlation)
        if abs_correlation > 0.8:
            trend_strength = "强"
        elif abs_correlation > 0.5:
            trend_strength = "中等"
        else:
            trend_strength = "弱"
        
        # 计算变化率
        first_value = values[0]
        last_value = values[-1]
        total_change_rate = ((last_value - first_value) / first_value * 100) if first_value != 0 else 0
        
        # 平均变化率
        period_count = n - 1
        avg_change_rate = total_change_rate / period_count if period_count > 0 else 0
        
        result = {
            "has_trend": True,
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "slope": round(slope, 4),
            "correlation": round(correlation, 4),
            "total_change_rate": round(total_change_rate, 2),
            "avg_change_rate": round(avg_change_rate, 2),
            "data_points_count": n,
            "first_value": first_value,
            "last_value": last_value,
            "predicted_next": round(intercept + slope * n, 2),
            "analysis_summary": _generate_trend_summary(
                trend_direction, trend_strength, total_change_rate
            )
        }
        
        logger.info(f"趋势分析完成: {trend_direction}趋势，强度{trend_strength}")
        return result
        
    except Exception as e:
        logger.error(f"趋势分析失败: {e}")
        return {
            "has_trend": False,
            "error": str(e)
        }


def calculate_contract_status(contract_data: dict[str, Any]) -> dict[str, Any]:
    """计算合同状态信息

    Args:
        contract_data: 合同数据

    Returns:
        Dict[str, Any]: 合同状态分析结果
    """
    try:
        from datetime import datetime, timedelta
        
        current_date = datetime.now()
        
        # 获取关键日期
        sign_date_str = contract_data.get("sign_date")
        effective_date_str = contract_data.get("effective_date")
        expiry_date_str = contract_data.get("expiry_date")
        
        sign_date = datetime.strptime(sign_date_str, "%Y-%m-%d") if sign_date_str else None
        effective_date = datetime.strptime(effective_date_str, "%Y-%m-%d") if effective_date_str else None
        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d") if expiry_date_str else None
        
        # 计算状态
        status_info = {
            "current_status": contract_data.get("contract_status", "unknown"),
            "is_active": False,
            "is_expired": False,
            "days_to_expiry": None,
            "days_since_signed": None,
            "contract_duration": None,
            "progress_percentage": contract_data.get("progress_percentage", 0),
            "alerts": []
        }
        
        # 计算签署后天数
        if sign_date:
            status_info["days_since_signed"] = (current_date - sign_date).days
        
        # 计算到期天数
        if expiry_date:
            days_to_expiry = (expiry_date - current_date).days
            status_info["days_to_expiry"] = days_to_expiry
            
            if days_to_expiry < 0:
                status_info["is_expired"] = True
                status_info["alerts"].append(f"合同已过期{abs(days_to_expiry)}天")
            elif days_to_expiry <= 30:
                status_info["alerts"].append(f"合同将在{days_to_expiry}天后到期")
            elif days_to_expiry <= 90:
                status_info["alerts"].append(f"合同将在{days_to_expiry}天后到期，建议提前准备续约")
        
        # 计算合同期限
        if effective_date and expiry_date:
            status_info["contract_duration"] = (expiry_date - effective_date).days
        
        # 判断是否生效
        if effective_date and expiry_date:
            if effective_date <= current_date <= expiry_date:
                status_info["is_active"] = True
        
        # 进度检查
        progress = float(status_info["progress_percentage"])
        if progress < 10 and status_info["days_since_signed"] and status_info["days_since_signed"] > 30:
            status_info["alerts"].append("合同执行进度较慢，建议跟进")
        
        logger.info(f"合同状态计算完成: {status_info['current_status']}")
        return status_info
        
    except Exception as e:
        logger.error(f"合同状态计算失败: {e}")
        return {
            "current_status": "unknown",
            "error": str(e)
        }


def _generate_price_recommendations(
    price_change_pct: Decimal,
    avg_change_pct: Decimal,
    trend: str
) -> list[str]:
    """生成价格建议"""
    recommendations = []
    
    if price_change_pct > 10:
        recommendations.append("价格上涨较大，可能影响客户接受度")
    elif price_change_pct < -10:
        recommendations.append("价格下降较大，建议确认成本控制")
    
    if avg_change_pct < -5:
        recommendations.append("价格低于历史平均水平，竞争力较强")
    elif avg_change_pct > 5:
        recommendations.append("价格高于历史平均水平，建议评估合理性")
    
    if trend == "上涨":
        recommendations.append("价格呈上涨趋势，注意市场接受度")
    elif trend == "下降":
        recommendations.append("价格呈下降趋势，有利于市场竞争")
    
    return recommendations or ["价格水平合理"]


def _generate_trend_summary(direction: str, strength: str, change_rate: float) -> str:
    """生成趋势总结"""
    if direction == "稳定":
        return f"价格保持稳定，变化幅度较小({change_rate:.1f}%)"
    else:
        return f"价格呈{direction}趋势，趋势强度{strength}，总变化率{change_rate:.1f}%"


def _get_empty_quote_total() -> dict[str, Decimal]:
    """获取空的报价总计"""
    return {
        "subtotal": Decimal("0"),
        "discount_amount": Decimal("0"),
        "taxable_amount": Decimal("0"),
        "tax_amount": Decimal("0"),
        "total_amount": Decimal("0"),
    }
