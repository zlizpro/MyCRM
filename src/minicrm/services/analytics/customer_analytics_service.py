"""
MiniCRM 客户分析服务

负责客户相关的数据分析:
- 客户价值分析
- 客户增长趋势分析
- 顶级客户识别
- 客户分布统计

严格遵循业务逻辑层职责:
- 只处理客户分析相关的业务逻辑
- 通过DAO接口访问数据
- 不包含UI逻辑
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from minicrm.core.exceptions import ServiceError
from minicrm.core.interfaces.dao_interfaces import ICustomerDAO
from minicrm.models.analytics_models import CustomerAnalysis
from transfunctions.calculations import calculate_customer_value_score


class CustomerAnalyticsService:
    """
    客户分析服务

    提供完整的客户分析功能:
    - 客户价值评估和分布
    - 客户增长趋势分析
    - 顶级客户识别
    - 客户行为分析
    """

    def __init__(self, customer_dao: ICustomerDAO):
        """
        初始化客户分析服务

        Args:
            customer_dao: 客户数据访问对象
        """
        self._customer_dao = customer_dao
        self._logger = logging.getLogger(__name__)

        self._logger.debug("客户分析服务初始化完成")

    def get_customer_analysis(self, time_period_months: int = 12) -> CustomerAnalysis:
        """
        获取客户分析数据

        Args:
            time_period_months: 分析时间段(月)

        Returns:
            CustomerAnalysis: 客户分析结果

        Raises:
            ServiceError: 当分析失败时
        """
        try:
            self._logger.info(f"开始客户分析,时间段: {time_period_months}个月")

            # 获取客户统计数据
            customer_stats = self._customer_dao.get_statistics()

            # 获取所有客户数据
            all_customers = self._customer_dao.search()

            # 计算客户价值分布
            value_distribution = self.calculate_customer_value_distribution(
                all_customers
            )

            # 获取顶级客户
            top_customers = self.get_top_customers(all_customers, limit=10)

            # 计算增长趋势
            growth_trend = self.calculate_customer_growth_trend(time_period_months)

            analysis = CustomerAnalysis(
                total_customers=customer_stats.get("total_customers", 0),
                new_customers_this_month=customer_stats.get("new_this_month", 0),
                active_customers=customer_stats.get("active_customers", 0),
                customer_value_distribution=value_distribution,
                top_customers=top_customers,
                growth_trend=growth_trend,
            )

            self._logger.info("客户分析完成")
            return analysis

        except Exception as e:
            self._logger.error(f"客户分析失败: {e}")
            raise ServiceError(f"客户分析失败: {e}", "CustomerAnalyticsService") from e

    def calculate_customer_value_distribution(
        self, customers: list[dict[str, Any]]
    ) -> dict[str, int]:
        """
        计算客户价值分布

        基于客户的交易历史、互动频率等因素计算价值评分,
        并按价值等级进行分布统计.

        优化后的算法考虑:
        - 交易金额权重
        - 互动频率权重
        - 合作时长权重
        - 忠诚度指标
        - 增长潜力评估

        Args:
            customers: 客户数据列表

        Returns:
            Dict[str, int]: 客户价值分布统计
        """
        distribution = {"高价值": 0, "中价值": 0, "低价值": 0, "潜在": 0}

        for customer in customers:
            # 使用优化的客户价值评分算法
            try:
                score = self._calculate_enhanced_customer_value_score(customer)

                # 优化的价值分级阈值
                if score >= 85:
                    distribution["高价值"] += 1
                elif score >= 70:
                    distribution["中价值"] += 1
                elif score >= 50:
                    distribution["低价值"] += 1
                else:
                    distribution["潜在"] += 1
            except Exception as e:
                self._logger.warning(f"计算客户价值失败: {e}")
                distribution["潜在"] += 1

        return distribution

    def _calculate_enhanced_customer_value_score(
        self, customer: dict[str, Any]
    ) -> float:
        """
        计算增强的客户价值评分 - 优化版本

        综合考虑多个维度的客户价值指标,采用动态权重算法:
        1. 交易价值 (35-45%权重,根据客户类型调整)
        2. 互动质量 (20-30%权重,根据行业特点调整)
        3. 合作稳定性 (15-25%权重,根据合作阶段调整)
        4. 增长潜力 (10-20%权重,根据市场环境调整)
        5. 行业影响因子 (5%权重,新增)

        优化特性:
        - 动态权重分配
        - 行业特定调整
        - 时间衰减因子
        - 风险调整机制

        Args:
            customer: 客户数据

        Returns:
            float: 客户价值评分 (0-100)
        """
        try:
            # 获取客户基本信息
            customer_type = customer.get("customer_type", "standard")
            industry = customer.get("industry", "general")
            cooperation_months = customer.get("cooperation_months", 0)

            # 动态权重计算
            weights = self._calculate_dynamic_weights(
                customer_type, industry, cooperation_months
            )

            # 1. 交易价值评分
            transaction_score = self._calculate_enhanced_transaction_value_score(
                customer
            )

            # 2. 互动质量评分
            interaction_score = self._calculate_enhanced_interaction_quality_score(
                customer
            )

            # 3. 合作稳定性评分
            stability_score = self._calculate_enhanced_cooperation_stability_score(
                customer
            )

            # 4. 增长潜力评分
            growth_score = self._calculate_enhanced_growth_potential_score(customer)

            # 5. 行业影响因子评分
            industry_score = self._calculate_industry_impact_score(customer)

            # 加权总分计算
            total_score = (
                transaction_score * weights["transaction"]
                + interaction_score * weights["interaction"]
                + stability_score * weights["stability"]
                + growth_score * weights["growth"]
                + industry_score * weights["industry"]
            )

            # 应用时间衰减因子
            time_factor = self._calculate_time_decay_factor(customer)
            adjusted_score = total_score * time_factor

            # 应用风险调整
            risk_factor = self._calculate_risk_adjustment_factor(customer)
            final_score = adjusted_score * risk_factor

            return min(100, max(0, final_score))

        except Exception as e:
            self._logger.error(f"计算增强客户价值评分失败: {e}")
            return 50  # 默认中等评分

    def _calculate_dynamic_weights(
        self, customer_type: str, industry: str, cooperation_months: int
    ) -> dict[str, float]:
        """
        计算动态权重

        根据客户类型、行业和合作阶段动态调整各维度权重

        Args:
            customer_type: 客户类型
            industry: 行业类别
            cooperation_months: 合作月数

        Returns:
            Dict[str, float]: 各维度权重
        """
        # 基础权重
        base_weights = {
            "transaction": 0.40,
            "interaction": 0.25,
            "stability": 0.20,
            "growth": 0.15,
            "industry": 0.05,
        }

        # 客户类型调整
        if customer_type == "vip":
            base_weights["transaction"] += 0.05
            base_weights["stability"] += 0.03
        elif customer_type == "potential":
            base_weights["growth"] += 0.08
            base_weights["interaction"] += 0.05

        # 行业调整
        if industry in ["furniture", "construction"]:  # 板材行业相关
            base_weights["stability"] += 0.05
            base_weights["transaction"] += 0.03
        elif industry == "technology":
            base_weights["growth"] += 0.05
            base_weights["interaction"] += 0.03

        # 合作阶段调整
        if cooperation_months < 6:  # 新客户
            base_weights["interaction"] += 0.05
            base_weights["growth"] += 0.03
        elif cooperation_months > 24:  # 老客户
            base_weights["stability"] += 0.05
            base_weights["transaction"] += 0.03

        # 归一化权重
        total_weight = sum(base_weights.values())
        return {k: v / total_weight for k, v in base_weights.items()}

    def _calculate_enhanced_transaction_value_score(
        self, customer: dict[str, Any]
    ) -> float:
        """计算增强的交易价值评分 (0-100分)"""
        total_amount = customer.get("total_transaction_amount", 0)
        avg_order_value = customer.get("average_order_value", 0)
        transaction_frequency = customer.get("transaction_frequency", 0)
        payment_punctuality = customer.get("payment_punctuality", 0.8)
        order_growth_rate = customer.get("order_growth_rate", 0.0)

        # 交易金额评分 (0-35分) - 使用对数函数避免线性增长
        import math

        amount_score = min(35, 35 * (1 - math.exp(-total_amount / 100000)))

        # 平均订单价值评分 (0-25分) - 考虑订单价值稳定性
        avg_score = min(25, avg_order_value / 2000)

        # 交易频率评分 (0-20分) - 考虑频率的合理性
        frequency_score = min(20, transaction_frequency * 1.5)

        # 付款及时性评分 (0-15分) - 新增
        payment_score = payment_punctuality * 15

        # 订单增长率评分 (0-5分) - 新增
        growth_score = min(5, max(0, order_growth_rate * 50))

        return amount_score + avg_score + frequency_score + payment_score + growth_score

    def _calculate_enhanced_interaction_quality_score(
        self, customer: dict[str, Any]
    ) -> float:
        """计算增强的互动质量评分 (0-100分)"""
        interaction_count = customer.get("interaction_count", 0)
        response_rate = customer.get("response_rate", 0.5)
        satisfaction_score = customer.get("satisfaction_score", 3.0)
        interaction_depth = customer.get(
            "interaction_depth", "shallow"
        )  # shallow, medium, deep
        proactive_interactions = customer.get("proactive_interactions", 0)
        complaint_resolution_rate = customer.get("complaint_resolution_rate", 0.8)

        # 互动频率评分 (0-25分) - 使用平方根函数避免过度奖励
        import math

        frequency_score = min(25, 25 * math.sqrt(interaction_count / 50))

        # 响应率评分 (0-20分) - 提高权重
        response_score = response_rate * 20

        # 满意度评分 (0-20分) - 使用非线性转换
        satisfaction_normalized = ((satisfaction_score - 1) / 4) ** 0.8 * 20

        # 互动深度评分 (0-15分) - 新增
        depth_mapping = {"shallow": 5, "medium": 10, "deep": 15}
        depth_score = depth_mapping.get(interaction_depth, 5)

        # 主动互动评分 (0-10分) - 新增
        proactive_score = min(10, proactive_interactions * 2)

        # 投诉解决率评分 (0-10分) - 新增
        complaint_score = complaint_resolution_rate * 10

        return (
            frequency_score
            + response_score
            + satisfaction_normalized
            + depth_score
            + proactive_score
            + complaint_score
        )

    def _calculate_enhanced_cooperation_stability_score(
        self, customer: dict[str, Any]
    ) -> float:
        """计算增强的合作稳定性评分 (0-100分)"""
        cooperation_months = customer.get("cooperation_months", 0)
        contract_count = customer.get("contract_count", 0)
        payment_punctuality = customer.get("payment_punctuality", 0.8)
        contract_renewal_rate = customer.get("contract_renewal_rate", 0.7)
        dispute_count = customer.get("dispute_count", 0)
        loyalty_indicators = customer.get("loyalty_indicators", [])

        # 合作时长评分 (0-30分) - 使用对数函数
        import math

        duration_score = min(30, 30 * (1 - math.exp(-cooperation_months / 12)))

        # 合同数量评分 (0-20分) - 考虑合同质量
        contract_score = min(20, contract_count * 3)

        # 付款及时性评分 (0-20分) - 提高权重
        payment_score = payment_punctuality * 20

        # 合同续约率评分 (0-15分) - 新增
        renewal_score = contract_renewal_rate * 15

        # 争议处理评分 (0-10分) - 新增,争议越少分数越高
        dispute_score = max(0, 10 - dispute_count * 2)

        # 忠诚度指标评分 (0-5分) - 新增
        loyalty_score = min(5, len(loyalty_indicators))

        return (
            duration_score
            + contract_score
            + payment_score
            + renewal_score
            + dispute_score
            + loyalty_score
        )

    def _calculate_enhanced_growth_potential_score(
        self, customer: dict[str, Any]
    ) -> float:
        """计算增强的增长潜力评分 (0-100分)"""
        industry_growth = customer.get("industry_growth_rate", 0.05)
        company_size = customer.get("company_size", "small")
        expansion_plans = customer.get("has_expansion_plans", False)
        market_position = customer.get(
            "market_position", "follower"
        )  # leader, challenger, follower, nicher
        innovation_capacity = customer.get(
            "innovation_capacity", "low"
        )  # low, medium, high
        financial_health = customer.get(
            "financial_health", "stable"
        )  # poor, stable, good, excellent

        # 行业增长率评分 (0-25分) - 考虑行业周期
        industry_score = min(25, industry_growth * 400)

        # 公司规模评分 (0-20分) - 更细化的分级
        size_mapping = {
            "micro": 5,
            "small": 10,
            "medium": 15,
            "large": 20,
            "enterprise": 18,
        }
        size_score = size_mapping.get(company_size, 10)

        # 扩张计划评分 (0-15分) - 新增具体计划评估
        expansion_score = 15 if expansion_plans else 0
        if expansion_plans and customer.get("expansion_budget", 0) > 0:
            expansion_score = min(
                15, expansion_score + customer.get("expansion_budget", 0) / 100000
            )

        # 市场地位评分 (0-20分) - 新增
        position_mapping = {
            "leader": 20,
            "challenger": 15,
            "follower": 10,
            "nicher": 12,
        }
        position_score = position_mapping.get(market_position, 10)

        # 创新能力评分 (0-15分) - 新增
        innovation_mapping = {"low": 5, "medium": 10, "high": 15}
        innovation_score = innovation_mapping.get(innovation_capacity, 5)

        # 财务健康度评分 (0-5分) - 新增
        financial_mapping = {"poor": 0, "stable": 2, "good": 4, "excellent": 5}
        financial_score = financial_mapping.get(financial_health, 2)

        return (
            industry_score
            + size_score
            + expansion_score
            + position_score
            + innovation_score
            + financial_score
        )

    def _calculate_industry_impact_score(self, customer: dict[str, Any]) -> float:
        """计算行业影响因子评分 (0-100分)"""
        industry = customer.get("industry", "general")
        market_share = customer.get("market_share", 0.01)
        industry_influence = customer.get(
            "industry_influence", "low"
        )  # low, medium, high

        # 板材行业特定评分
        if industry in ["furniture", "construction", "decoration"]:
            base_score = 80  # 高相关性
        elif industry in ["manufacturing", "real_estate"]:
            base_score = 60  # 中等相关性
        else:
            base_score = 40  # 低相关性

        # 市场份额调整
        share_adjustment = min(20, market_share * 2000)

        # 行业影响力调整
        influence_mapping = {"low": 0, "medium": 10, "high": 20}
        influence_adjustment = influence_mapping.get(industry_influence, 0)

        return min(100, base_score + share_adjustment + influence_adjustment)

    def _calculate_time_decay_factor(self, customer: dict[str, Any]) -> float:
        """计算时间衰减因子"""
        last_interaction_days = customer.get("days_since_last_interaction", 30)

        # 30天内无衰减,之后逐渐衰减
        if last_interaction_days <= 30:
            return 1.0
        elif last_interaction_days <= 90:
            return 0.95
        elif last_interaction_days <= 180:
            return 0.90
        else:
            return 0.85

    def _calculate_risk_adjustment_factor(self, customer: dict[str, Any]) -> float:
        """计算风险调整因子"""
        credit_rating = customer.get("credit_rating", "B")  # AAA, AA, A, BBB, BB, B, C
        payment_delays = customer.get("payment_delays", 0)
        dispute_severity = customer.get(
            "dispute_severity", "none"
        )  # none, low, medium, high

        # 信用评级调整
        rating_mapping = {
            "AAA": 1.05,
            "AA": 1.02,
            "A": 1.0,
            "BBB": 0.98,
            "BB": 0.95,
            "B": 0.92,
            "C": 0.85,
        }
        rating_factor = rating_mapping.get(credit_rating, 0.92)

        # 付款延迟调整
        delay_factor = max(0.8, 1.0 - payment_delays * 0.02)

        # 争议严重程度调整
        dispute_mapping = {"none": 1.0, "low": 0.98, "medium": 0.95, "high": 0.90}
        dispute_factor = dispute_mapping.get(dispute_severity, 1.0)

        return rating_factor * delay_factor * dispute_factor

    def get_top_customers(
        self, customers: list[dict[str, Any]], limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        获取顶级客户

        基于客户价值评分排序,返回价值最高的客户列表.

        Args:
            customers: 客户数据列表
            limit: 返回数量限制

        Returns:
            List[Dict[str, Any]]: 顶级客户列表
        """
        try:
            # 计算每个客户的价值评分
            customers_with_scores = []
            for customer in customers:
                try:
                    value_metrics = calculate_customer_value_score(customer, [], [])
                    customer_data = customer.copy()
                    customer_data["value_score"] = value_metrics.total_score
                    customers_with_scores.append(customer_data)
                except Exception:
                    customer_data = customer.copy()
                    customer_data["value_score"] = 0
                    customers_with_scores.append(customer_data)

            # 按价值评分排序
            sorted_customers = sorted(
                customers_with_scores,
                key=lambda x: x.get("value_score", 0),
                reverse=True,
            )

            return sorted_customers[:limit]

        except Exception as e:
            self._logger.error(f"获取顶级客户失败: {e}")
            # 返回前N个客户作为备选
            return customers[:limit]

    def calculate_customer_growth_trend(self, months: int) -> list[dict[str, Any]]:
        """
        计算客户增长趋势

        分析指定时间段内的客户增长情况,包括新增客户数和总客户数变化.

        Args:
            months: 分析月数

        Returns:
            List[Dict[str, Any]]: 增长趋势数据
        """
        try:
            # 模拟数据,实际应从数据库获取历史数据
            trend_data = []
            base_date = datetime.now() - timedelta(days=months * 30)

            for i in range(months):
                month_date = base_date + timedelta(days=i * 30)

                # 实际实现中应该查询数据库获取该月的真实数据
                # 这里使用模拟数据展示数据结构
                trend_data.append(
                    {
                        "date": month_date.strftime("%Y-%m"),
                        "new_customers": 10 + i * 2,  # 模拟增长
                        "total_customers": 100 + i * 12,
                        "growth_rate": ((10 + i * 2) / (100 + (i - 1) * 12) * 100)
                        if i > 0
                        else 0,
                    }
                )

            return trend_data

        except Exception as e:
            self._logger.error(f"计算客户增长趋势失败: {e}")
            return []

    def analyze_customer_segments(
        self, customers: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        分析客户细分

        根据客户的行业、规模、地区等维度进行细分分析.

        Args:
            customers: 客户数据列表

        Returns:
            Dict[str, Any]: 客户细分分析结果
        """
        try:
            # 按行业分布
            industry_distribution: dict[str, int] = {}
            # 按地区分布
            region_distribution: dict[str, int] = {}
            # 按规模分布
            size_distribution: dict[str, int] = {}

            for customer in customers:
                # 行业分布
                industry = customer.get("industry", "其他")
                industry_distribution[industry] = (
                    industry_distribution.get(industry, 0) + 1
                )

                # 地区分布
                region = customer.get("region", "其他")
                region_distribution[region] = region_distribution.get(region, 0) + 1

                # 规模分布
                size = customer.get("company_size", "小型")
                size_distribution[size] = size_distribution.get(size, 0) + 1

            return {
                "industry_distribution": industry_distribution,
                "region_distribution": region_distribution,
                "size_distribution": size_distribution,
                "total_segments": len(customers),
            }

        except Exception as e:
            self._logger.error(f"客户细分分析失败: {e}")
            return {}

    def get_customer_activity_analysis(self, customer_id: int) -> dict[str, Any]:
        """
        获取单个客户的活动分析

        Args:
            customer_id: 客户ID

        Returns:
            Dict[str, Any]: 客户活动分析结果
        """
        try:
            # 获取客户基本信息
            customer = self._customer_dao.get_by_id(customer_id)
            if not customer:
                raise ServiceError(
                    f"客户不存在: {customer_id}", "CustomerAnalyticsService"
                )

            # 分析客户活动(简化实现)
            activity_analysis = {
                "customer_id": customer_id,
                "customer_name": customer.get("name", ""),
                "last_interaction_date": customer.get("last_interaction_date"),
                "total_interactions": customer.get("interaction_count", 0),
                "interaction_frequency": "高"
                if customer.get("interaction_count", 0) > 10
                else "低",
                "value_score": 75,  # 简化实现
                "activity_trend": "stable",
            }

            return activity_analysis

        except Exception as e:
            self._logger.error(f"客户活动分析失败: {e}")
            raise ServiceError(
                f"客户活动分析失败: {e}", "CustomerAnalyticsService"
            ) from e
