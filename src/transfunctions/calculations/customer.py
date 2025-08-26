"""
Transfunctions - 客户相关计算

提供客户价值评分等客户相关的计算功能.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
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
class CustomerValueMetrics:
    """客户价值评分指标"""

    transaction_value: float  # 交易价值评分 (0-40)
    interaction_score: float  # 互动评分 (0-25)
    loyalty_score: float  # 忠诚度评分 (0-20)
    potential_score: float  # 潜力评分 (0-15)
    total_score: float  # 总评分 (0-100)

    def to_dict(self) -> dict[str, float]:
        """转换为字典格式"""
        return {
            "transaction_value": self.transaction_value,
            "interaction_score": self.interaction_score,
            "loyalty_score": self.loyalty_score,
            "potential_score": self.potential_score,
            "total_score": self.total_score,
        }


def calculate_customer_value_score(
    customer_data: dict[str, Any],
    transaction_history: list[dict[str, Any]],
    interaction_history: list[dict[str, Any]],
    time_period_months: int = 12,
) -> CustomerValueMetrics:
    """计算客户价值评分

    基于客户的交易历史、互动频率、合作时长等多个维度,
    计算客户的综合价值评分,适用于板材行业的客户评估.

    Args:
        customer_data: 客户基本信息
        transaction_history: 交易历史记录
        interaction_history: 互动历史记录
        time_period_months: 评估时间段(月)

    Returns:
        CustomerValueMetrics: 客户价值评分指标

    Raises:
        CalculationError: 当计算参数无效时

    Example:
        >>> customer = {"created_at": "2023-01-01", "level": "VIP"}
        >>> transactions = [{"amount": 10000, "date": "2024-12-01"}]
        >>> interactions = [{"type": "call", "date": "2024-12-15"}]
        >>> metrics = calculate_customer_value_score(customer, transactions, interactions)
        >>> print(f"客户价值评分: {metrics.total_score}")
    """
    try:
        # 参数验证
        if not customer_data:
            raise CalculationError("客户数据不能为空")

        if time_period_months <= 0:
            raise CalculationError("时间段必须大于0")

        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=time_period_months * 30)

        # 1. 交易价值评分 (0-40分)
        transaction_value = _calculate_transaction_value_score(
            transaction_history, start_date, end_date
        )

        # 2. 互动评分 (0-25分)
        interaction_score = _calculate_interaction_score_new(
            interaction_history, start_date, end_date
        )

        # 3. 忠诚度评分 (0-20分)
        loyalty_score = _calculate_loyalty_score_new(customer_data, transaction_history)

        # 4. 潜力评分 (0-15分)
        potential_score = _calculate_potential_score_new(
            customer_data, transaction_history, interaction_history
        )

        # 计算总分
        total_score = (
            transaction_value + interaction_score + loyalty_score + potential_score
        )

        # 确保总分在0-100范围内
        total_score = max(0, min(100, total_score))

        metrics = CustomerValueMetrics(
            transaction_value=transaction_value,
            interaction_score=interaction_score,
            loyalty_score=loyalty_score,
            potential_score=potential_score,
            total_score=total_score,
        )

        logger.info(f"客户价值评分计算完成: {total_score:.1f}分")
        return metrics

    except Exception as e:
        raise CalculationError(
            f"客户价值评分计算失败: {str(e)}",
            {"customer_id": customer_data.get("id"), "time_period": time_period_months},
        ) from e


def _calculate_transaction_value_score(
    transactions: list[dict[str, Any]], start_date: datetime, end_date: datetime
) -> float:
    """计算交易价值评分"""
    if not transactions:
        return 0.0

    # 筛选时间范围内的交易
    period_transactions = [
        t
        for t in transactions
        if start_date <= datetime.fromisoformat(t.get("date", "1900-01-01")) <= end_date
    ]

    if not period_transactions:
        return 0.0

    # 计算总交易金额
    from decimal import Decimal

    total_amount = sum(Decimal(str(t.get("amount", 0))) for t in period_transactions)

    # 计算交易频次
    transaction_count = len(period_transactions)

    # 评分逻辑(可根据行业特点调整)
    amount_score = min(30, float(total_amount) / 10000)  # 每万元得1分,最高30分
    frequency_score = min(10, transaction_count * 2)  # 每笔交易得2分,最高10分

    return amount_score + frequency_score


def _calculate_interaction_score_new(
    interactions: list[dict[str, Any]], start_date: datetime, end_date: datetime
) -> float:
    """计算互动评分"""
    if not interactions:
        return 0.0

    # 筛选时间范围内的互动
    period_interactions = [
        i
        for i in interactions
        if start_date <= datetime.fromisoformat(i.get("date", "1900-01-01")) <= end_date
    ]

    if not period_interactions:
        return 0.0

    # 不同互动类型的权重
    interaction_weights = {
        "meeting": 5,  # 面谈
        "call": 3,  # 电话
        "email": 2,  # 邮件
        "message": 1,  # 短信
        "other": 1,  # 其他
    }

    # 计算加权互动分数
    weighted_score = sum(
        interaction_weights.get(i.get("type", "other"), 1) for i in period_interactions
    )

    # 最高25分
    return min(25, weighted_score)


def _calculate_loyalty_score_new(
    customer_data: dict[str, Any], transactions: list[dict[str, Any]]
) -> float:
    """计算忠诚度评分"""
    # 合作时长评分
    created_at = customer_data.get("created_at")
    if created_at:
        cooperation_months = (
            datetime.now() - datetime.fromisoformat(created_at)
        ).days / 30
        time_score = min(10, cooperation_months / 6)  # 每半年得1分,最高10分
    else:
        time_score = 0

    # 客户等级评分
    level_scores = {"VIP": 10, "重要": 7, "普通": 4, "潜在": 1}
    level_score = level_scores.get(customer_data.get("level", "普通"), 4)

    return time_score + level_score


def _calculate_potential_score_new(
    customer_data: dict[str, Any],
    transactions: list[dict[str, Any]],
    interactions: list[dict[str, Any]],
) -> float:
    """计算潜力评分"""
    score = 0

    # 行业潜力评分
    industry_scores = {"制造业": 8, "建筑业": 7, "装饰业": 6, "其他": 3}
    industry = customer_data.get("industry", "其他")
    score += industry_scores.get(industry, 3)

    # 增长趋势评分
    if len(transactions) >= 2:
        from decimal import Decimal

        recent_amount = sum(
            Decimal(str(t.get("amount", 0)))
            for t in transactions[-3:]  # 最近3笔交易
        )
        earlier_amount = sum(
            Decimal(str(t.get("amount", 0)))
            for t in transactions[-6:-3]  # 之前3笔交易
        )

        if earlier_amount > 0 and recent_amount > earlier_amount:
            score += 7  # 增长趋势良好

    return min(15, score)


def _calculate_transaction_score(transaction_history: list[dict[str, Any]]) -> float:
    """计算交易评分 (40%权重)"""
    if not transaction_history:
        return 0.0

    total_amount = sum(t.get("amount", 0) for t in transaction_history)
    transaction_count = len(transaction_history)

    # 基于交易总额评分 (0-40分)
    if total_amount >= 1000000:  # 100万以上
        score = 40
    elif total_amount >= 500000:  # 50万以上
        score = 30
    elif total_amount >= 100000:  # 10万以上
        score = 20
    elif total_amount >= 50000:  # 5万以上
        score = 10
    else:
        score = total_amount / 50000 * 10

    # 交易频率加分
    if transaction_count >= 20:
        score += 5
    elif transaction_count >= 10:
        score += 3
    elif transaction_count >= 5:
        score += 1

    return min(45, score)  # 最高45分


def _calculate_interaction_score(interaction_history: list[dict[str, Any]]) -> float:
    """计算互动评分 (25%权重)"""
    if not interaction_history:
        return 0.0

    interaction_count = len(interaction_history)
    recent_interactions = [
        i for i in interaction_history if _days_ago(i.get("created_at", "")) <= 90
    ]

    # 基于互动频率评分 (0-25分)
    if interaction_count >= 50:
        score = 25
    elif interaction_count >= 30:
        score = 20
    elif interaction_count >= 15:
        score = 15
    elif interaction_count >= 5:
        score = 10
    else:
        score = interaction_count * 2

    # 近期活跃度加分
    if len(recent_interactions) >= 5:
        score += 3

    return min(28, score)  # 最高28分


def _calculate_loyalty_score(customer_data: dict[str, Any]) -> float:
    """计算忠诚度评分 (25%权重)"""
    customer_age_days = _days_ago(customer_data.get("created_at", ""))

    if customer_age_days <= 0:
        return 0.0

    # 基于合作时长评分 (0-25分)
    if customer_age_days >= 730:  # 2年以上
        return 25
    elif customer_age_days >= 365:  # 1年以上
        return 20
    elif customer_age_days >= 180:  # 半年以上
        return 15
    elif customer_age_days >= 90:  # 3个月以上
        return 10
    else:
        return customer_age_days / 90 * 10


def _calculate_potential_score(customer_data: dict[str, Any]) -> float:
    """计算潜力评分 (10%权重)"""
    customer_type = customer_data.get("customer_type", "")

    if customer_type == "VIP":
        return 10
    elif customer_type in ["生态板客户", "家具板客户"]:
        return 8
    elif customer_type == "阻燃板客户":
        return 6
    else:
        return 4


def _days_ago(date_str: str) -> int:
    """计算距离指定日期的天数"""
    if not date_str:
        return 0

    try:
        # 尝试解析不同格式的日期
        for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d"]:
            try:
                target_date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        else:
            return 0

        delta = datetime.now() - target_date
        return delta.days

    except Exception:
        return 0
