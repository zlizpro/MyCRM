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


def _get_empty_quote_total() -> dict[str, Decimal]:
    """获取空的报价总计"""
    return {
        "subtotal": Decimal("0"),
        "discount_amount": Decimal("0"),
        "taxable_amount": Decimal("0"),
        "tax_amount": Decimal("0"),
        "total_amount": Decimal("0"),
    }
