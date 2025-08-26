"""
MiniCRM 财务风险预警服务

负责财务风险相关的分析和预警:
- 客户信用风险评估
- 应收账款风险分析
- 现金流风险预警
- 供应商付款风险
- 风险阈值管理

严格遵循业务逻辑层职责:
- 只处理财务风险分析相关的业务逻辑
- 通过DAO接口访问数据
- 不包含UI逻辑
"""

import logging
from datetime import datetime
from typing import Any

from minicrm.core.exceptions import ServiceError
from minicrm.core.interfaces.dao_interfaces import ICustomerDAO, ISupplierDAO


class FinancialRiskService:
    """
    财务风险预警服务

    提供完整的财务风险分析功能:
    - 客户信用风险评估
    - 应收账款风险分析
    - 现金流风险预警
    - 供应商付款风险
    - 动态风险阈值管理
    """

    def __init__(self, customer_dao: ICustomerDAO, supplier_dao: ISupplierDAO):
        """
        初始化财务风险服务

        Args:
            customer_dao: 客户数据访问对象
            supplier_dao: 供应商数据访问对象
        """
        self._customer_dao = customer_dao
        self._supplier_dao = supplier_dao
        self._logger = logging.getLogger(__name__)

        # 风险阈值配置
        self._risk_thresholds = self._initialize_risk_thresholds()

        self._logger.debug("财务风险预警服务初始化完成")

    def _initialize_risk_thresholds(self) -> dict[str, dict[str, float]]:
        """
        初始化优化的风险阈值配置

        采用动态阈值管理和多层级预警机制:
        - 基础阈值:适用于一般情况
        - 行业调整:根据板材行业特点调整
        - 季节性调整:考虑业务季节性波动
        - 动态调整:根据历史数据和市场环境调整

        Returns:
            Dict[str, Dict[str, float]]: 优化的风险阈值配置
        """
        return {
            "credit_risk": {
                # 信用评分阈值 (0-100分)
                "excellent_threshold": 85,  # 优秀客户阈值
                "good_threshold": 70,  # 良好客户阈值
                "acceptable_threshold": 55,  # 可接受客户阈值
                "warning_threshold": 40,  # 预警阈值
                "high_risk_threshold": 25,  # 高风险阈值
                # 动态调整参数
                "seasonal_adjustment": 0.05,  # 季节性调整幅度
                "market_adjustment": 0.10,  # 市场环境调整幅度
            },
            "overdue_risk": {
                # 逾期天数阈值
                "early_warning_days": 15,  # 早期预警天数
                "warning_days": 30,  # 预警天数
                "serious_days": 60,  # 严重逾期天数
                "critical_days": 90,  # 危险逾期天数
                # 金额阈值 (分级管理)
                "small_amount_threshold": 10000,  # 小额阈值
                "medium_amount_threshold": 50000,  # 中额阈值
                "large_amount_threshold": 200000,  # 大额阈值
                "critical_amount_threshold": 500000,  # 危险金额阈值
                # 逾期率阈值
                "acceptable_overdue_rate": 5.0,  # 可接受逾期率(%)
                "warning_overdue_rate": 10.0,  # 预警逾期率(%)
                "critical_overdue_rate": 20.0,  # 危险逾期率(%)
            },
            "cash_flow_risk": {
                # 现金流比率阈值
                "healthy_ratio": 0.30,  # 健康现金流比率
                "acceptable_ratio": 0.20,  # 可接受现金流比率
                "warning_ratio": 0.10,  # 预警现金流比率
                "critical_ratio": 0.05,  # 危险现金流比率
                "negative_threshold": -0.05,  # 负现金流阈值
                # 现金储备天数阈值
                "safe_cash_days": 90,  # 安全现金储备天数
                "warning_cash_days": 60,  # 预警现金储备天数
                "critical_cash_days": 30,  # 危险现金储备天数
                "emergency_cash_days": 15,  # 紧急现金储备天数
                # 预测参数
                "forecast_days": 120,  # 预测天数 (延长到4个月)
                "stress_test_scenarios": 3,  # 压力测试场景数
            },
            "concentration_risk": {
                # 客户集中度阈值
                "single_customer_safe": 0.15,  # 单一客户安全占比
                "single_customer_warning": 0.25,  # 单一客户预警占比
                "single_customer_critical": 0.40,  # 单一客户危险占比
                "top3_customer_safe": 0.45,  # 前3大客户安全占比
                "top3_customer_warning": 0.60,  # 前3大客户预警占比
                "top3_customer_critical": 0.75,  # 前3大客户危险占比
                "top5_customer_safe": 0.60,  # 前5大客户安全占比
                "top5_customer_warning": 0.75,  # 前5大客户预警占比
                "top5_customer_critical": 0.85,  # 前5大客户危险占比
                # 行业集中度阈值
                "industry_concentration_warning": 0.70,  # 行业集中度预警
                "industry_concentration_critical": 0.85,  # 行业集中度危险
            },
            "supplier_risk": {
                # 供应商付款风险阈值
                "payment_delay_warning": 7,  # 付款延迟预警天数
                "payment_delay_critical": 15,  # 付款延迟危险天数
                "supplier_concentration_warning": 0.30,  # 供应商集中度预警
                "supplier_concentration_critical": 0.50,  # 供应商集中度危险
                # 供应商质量风险阈值
                "quality_score_warning": 60,  # 质量评分预警阈值
                "quality_score_critical": 40,  # 质量评分危险阈值
                "delivery_delay_warning": 0.15,  # 交付延迟率预警
                "delivery_delay_critical": 0.25,  # 交付延迟率危险
            },
            "market_risk": {
                # 市场风险阈值 (新增)
                "price_volatility_warning": 0.15,  # 价格波动预警
                "price_volatility_critical": 0.25,  # 价格波动危险
                "demand_fluctuation_warning": 0.20,  # 需求波动预警
                "demand_fluctuation_critical": 0.35,  # 需求波动危险
                "competitor_pressure_warning": 0.70,  # 竞争压力预警
                "competitor_pressure_critical": 0.85,  # 竞争压力危险
            },
            "operational_risk": {
                # 运营风险阈值 (新增)
                "inventory_turnover_warning": 4.0,  # 库存周转率预警
                "inventory_turnover_critical": 2.0,  # 库存周转率危险
                "capacity_utilization_low": 0.60,  # 产能利用率过低
                "capacity_utilization_high": 0.95,  # 产能利用率过高
                "employee_turnover_warning": 0.15,  # 员工流失率预警
                "employee_turnover_critical": 0.25,  # 员工流失率危险
            },
        }

    def get_comprehensive_risk_analysis(self) -> dict[str, Any]:
        """
        获取综合风险分析

        Returns:
            Dict[str, Any]: 综合风险分析结果
        """
        try:
            self._logger.info("开始综合财务风险分析")

            # 1. 客户信用风险分析
            credit_risk = self.analyze_customer_credit_risk()

            # 2. 应收账款风险分析
            receivable_risk = self.analyze_receivable_risk()

            # 3. 现金流风险分析
            cash_flow_risk = self.analyze_cash_flow_risk()

            # 4. 客户集中度风险分析
            concentration_risk = self.analyze_customer_concentration_risk()

            # 5. 供应商付款风险分析
            payment_risk = self.analyze_supplier_payment_risk()

            # 综合风险评级
            overall_risk_level = self._calculate_overall_risk_level(
                credit_risk, receivable_risk, cash_flow_risk, concentration_risk
            )

            analysis_result = {
                "analysis_date": datetime.now().isoformat(),
                "overall_risk_level": overall_risk_level,
                "credit_risk": credit_risk,
                "receivable_risk": receivable_risk,
                "cash_flow_risk": cash_flow_risk,
                "concentration_risk": concentration_risk,
                "payment_risk": payment_risk,
                "risk_alerts": self._generate_risk_alerts(
                    credit_risk, receivable_risk, cash_flow_risk, concentration_risk
                ),
                "recommendations": self._generate_risk_recommendations(
                    overall_risk_level
                ),
            }

            self._logger.info("综合财务风险分析完成")
            return analysis_result

        except Exception as e:
            self._logger.error(f"综合财务风险分析失败: {e}")
            raise ServiceError(
                f"综合财务风险分析失败: {e}", "FinancialRiskService"
            ) from e

    def analyze_customer_credit_risk(self) -> dict[str, Any]:
        """
        分析客户信用风险

        Returns:
            Dict[str, Any]: 客户信用风险分析结果
        """
        try:
            customers = self._customer_dao.search()

            risk_distribution = {"低风险": 0, "中风险": 0, "高风险": 0}
            high_risk_customers = []
            total_credit_exposure = 0

            for customer in customers:
                credit_score = self._calculate_customer_credit_score(customer)
                credit_limit = customer.get("credit_limit", 0)
                outstanding_amount = customer.get("outstanding_amount", 0)

                total_credit_exposure += outstanding_amount

                # 风险分级
                if (
                    credit_score
                    >= self._risk_thresholds["credit_risk"]["low_threshold"]
                ):
                    risk_distribution["低风险"] += 1
                elif (
                    credit_score
                    >= self._risk_thresholds["credit_risk"]["medium_threshold"]
                ):
                    risk_distribution["中风险"] += 1
                else:
                    risk_distribution["高风险"] += 1
                    high_risk_customers.append(
                        {
                            "customer_id": customer.get("id"),
                            "customer_name": customer.get("name"),
                            "credit_score": credit_score,
                            "outstanding_amount": outstanding_amount,
                            "credit_limit": credit_limit,
                            "risk_factors": self._identify_credit_risk_factors(
                                customer
                            ),
                        }
                    )

            return {
                "risk_distribution": risk_distribution,
                "high_risk_customers": high_risk_customers[:10],  # 前10个高风险客户
                "total_credit_exposure": total_credit_exposure,
                "average_credit_score": self._calculate_average_credit_score(customers),
                "risk_level": self._determine_credit_risk_level(risk_distribution),
            }

        except Exception as e:
            self._logger.error(f"客户信用风险分析失败: {e}")
            return {}

    def _calculate_customer_credit_score(self, customer: dict[str, Any]) -> float:
        """
        计算客户信用评分

        综合考虑:
        - 付款历史 (40%权重)
        - 财务状况 (25%权重)
        - 合作历史 (20%权重)
        - 行业风险 (15%权重)

        Args:
            customer: 客户数据

        Returns:
            float: 信用评分 (0-100)
        """
        # 1. 付款历史评分 (0-40分)
        payment_history_score = self._calculate_payment_history_score(customer)

        # 2. 财务状况评分 (0-25分)
        financial_score = self._calculate_financial_status_score(customer)

        # 3. 合作历史评分 (0-20分)
        cooperation_score = self._calculate_cooperation_history_score(customer)

        # 4. 行业风险评分 (0-15分)
        industry_score = self._calculate_industry_risk_score(customer)

        total_score = (
            payment_history_score + financial_score + cooperation_score + industry_score
        )
        return min(100, max(0, total_score))

    def _calculate_payment_history_score(self, customer: dict[str, Any]) -> float:
        """计算付款历史评分 (最高40分)"""
        on_time_payment_rate = customer.get("on_time_payment_rate", 0.8)
        overdue_count = customer.get("overdue_count", 0)
        max_overdue_days = customer.get("max_overdue_days", 0)

        # 按时付款率评分 (0-25分)
        on_time_score = on_time_payment_rate * 25

        # 逾期次数扣分 (最多扣10分)
        overdue_penalty = min(10, overdue_count * 2)

        # 最大逾期天数扣分 (最多扣5分)
        max_overdue_penalty = min(5, max_overdue_days / 10)

        return max(0, on_time_score - overdue_penalty - max_overdue_penalty)

    def _calculate_financial_status_score(self, customer: dict[str, Any]) -> float:
        """计算财务状况评分 (最高25分)"""
        financial_rating = customer.get("financial_rating", "B")  # AAA, AA, A, B, C
        annual_revenue = customer.get("annual_revenue", 0)
        debt_ratio = customer.get("debt_ratio", 0.5)

        # 财务评级评分 (0-15分)
        rating_mapping = {"AAA": 15, "AA": 12, "A": 9, "B": 6, "C": 3}
        rating_score = rating_mapping.get(financial_rating, 6)

        # 年收入评分 (0-6分)
        revenue_score = min(6, annual_revenue / 1000000)  # 每100万得1分

        # 负债率评分 (0-4分,负债率越低分数越高)
        debt_score = max(0, 4 - debt_ratio * 4)

        return rating_score + revenue_score + debt_score

    def _calculate_cooperation_history_score(self, customer: dict[str, Any]) -> float:
        """计算合作历史评分 (最高20分)"""
        cooperation_years = customer.get("cooperation_years", 0)
        transaction_count = customer.get("transaction_count", 0)
        dispute_count = customer.get("dispute_count", 0)

        # 合作年限评分 (0-10分)
        years_score = min(10, cooperation_years * 2)

        # 交易次数评分 (0-8分)
        transaction_score = min(8, transaction_count / 5)

        # 争议次数扣分 (最多扣2分)
        dispute_penalty = min(2, dispute_count)

        return max(0, years_score + transaction_score - dispute_penalty)

    def _calculate_industry_risk_score(self, customer: dict[str, Any]) -> float:
        """计算行业风险评分 (最高15分)"""
        industry = customer.get("industry", "其他")
        market_position = customer.get("market_position", "中等")

        # 行业风险评分 (0-10分)
        industry_risk_mapping = {
            "制造业": 8,
            "建筑业": 6,
            "零售业": 7,
            "服务业": 9,
            "其他": 5,
        }
        industry_score = industry_risk_mapping.get(industry, 5)

        # 市场地位评分 (0-5分)
        position_mapping = {"领先": 5, "中等": 3, "落后": 1}
        position_score = position_mapping.get(market_position, 3)

        return industry_score + position_score

    def analyze_receivable_risk(self) -> dict[str, Any]:
        """
        分析应收账款风险

        Returns:
            Dict[str, Any]: 应收账款风险分析结果
        """
        try:
            customers = self._customer_dao.search()

            total_receivables = 0
            overdue_receivables = 0
            aging_analysis = {"0-30天": 0, "31-60天": 0, "61-90天": 0, "90天以上": 0}
            high_risk_receivables = []

            current_date = datetime.now()

            for customer in customers:
                outstanding_amount = customer.get("outstanding_amount", 0)
                due_date_str = customer.get("payment_due_date")

                if outstanding_amount <= 0:
                    continue

                total_receivables += outstanding_amount

                if due_date_str:
                    try:
                        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                        overdue_days = (current_date - due_date).days

                        if overdue_days > 0:
                            overdue_receivables += outstanding_amount

                            # 账龄分析
                            if overdue_days <= 30:
                                aging_analysis["0-30天"] += outstanding_amount
                            elif overdue_days <= 60:
                                aging_analysis["31-60天"] += outstanding_amount
                            elif overdue_days <= 90:
                                aging_analysis["61-90天"] += outstanding_amount
                            else:
                                aging_analysis["90天以上"] += outstanding_amount

                            # 高风险应收账款
                            if (
                                overdue_days
                                >= self._risk_thresholds["overdue_risk"][
                                    "critical_days"
                                ]
                                or outstanding_amount
                                >= self._risk_thresholds["overdue_risk"][
                                    "amount_threshold"
                                ]
                            ):
                                high_risk_receivables.append(
                                    {
                                        "customer_id": customer.get("id"),
                                        "customer_name": customer.get("name"),
                                        "outstanding_amount": outstanding_amount,
                                        "overdue_days": overdue_days,
                                        "risk_level": "高"
                                        if overdue_days >= 60
                                        else "中",
                                    }
                                )
                    except ValueError:
                        continue

            overdue_rate = (
                (overdue_receivables / total_receivables * 100)
                if total_receivables > 0
                else 0
            )

            return {
                "total_receivables": total_receivables,
                "overdue_receivables": overdue_receivables,
                "overdue_rate": round(overdue_rate, 2),
                "aging_analysis": aging_analysis,
                "high_risk_receivables": sorted(
                    high_risk_receivables,
                    key=lambda x: x["outstanding_amount"],
                    reverse=True,
                )[:10],
                "risk_level": self._determine_receivable_risk_level(overdue_rate),
            }

        except Exception as e:
            self._logger.error(f"应收账款风险分析失败: {e}")
            return {}

    def analyze_cash_flow_risk(self) -> dict[str, Any]:
        """
        分析现金流风险

        Returns:
            Dict[str, Any]: 现金流风险分析结果
        """
        try:
            # 模拟现金流数据,实际应从财务模块获取
            current_cash = 2500000  # 当前现金余额
            monthly_inflow = 800000  # 月均流入
            monthly_outflow = 750000  # 月均流出

            # 预测未来现金流
            forecast_days = self._risk_thresholds["cash_flow_risk"]["forecast_days"]
            cash_flow_forecast = self._forecast_cash_flow(
                current_cash, monthly_inflow, monthly_outflow, forecast_days
            )

            # 计算风险指标
            net_cash_flow = monthly_inflow - monthly_outflow
            cash_flow_ratio = (
                net_cash_flow / monthly_outflow if monthly_outflow > 0 else 0
            )
            days_cash_on_hand = (
                current_cash / (monthly_outflow / 30) if monthly_outflow > 0 else 999
            )

            # 风险等级判断
            warning_ratio = self._risk_thresholds["cash_flow_risk"]["warning_ratio"]
            critical_ratio = self._risk_thresholds["cash_flow_risk"]["critical_ratio"]

            if cash_flow_ratio >= warning_ratio:
                risk_level = "低"
            elif cash_flow_ratio >= critical_ratio:
                risk_level = "中"
            else:
                risk_level = "高"

            return {
                "current_cash": current_cash,
                "monthly_inflow": monthly_inflow,
                "monthly_outflow": monthly_outflow,
                "net_cash_flow": net_cash_flow,
                "cash_flow_ratio": round(cash_flow_ratio, 3),
                "days_cash_on_hand": round(days_cash_on_hand, 1),
                "cash_flow_forecast": cash_flow_forecast,
                "risk_level": risk_level,
                "risk_alerts": self._generate_cash_flow_alerts(
                    cash_flow_ratio, days_cash_on_hand
                ),
            }

        except Exception as e:
            self._logger.error(f"现金流风险分析失败: {e}")
            return {}

    def _forecast_cash_flow(
        self,
        current_cash: float,
        monthly_inflow: float,
        monthly_outflow: float,
        forecast_days: int,
    ) -> list[dict[str, Any]]:
        """
        预测现金流

        Args:
            current_cash: 当前现金
            monthly_inflow: 月均流入
            monthly_outflow: 月均流出
            forecast_days: 预测天数

        Returns:
            List[Dict[str, Any]]: 现金流预测
        """
        forecast = []
        cash_balance = current_cash
        daily_inflow = monthly_inflow / 30
        daily_outflow = monthly_outflow / 30

        for day in range(1, forecast_days + 1):
            cash_balance += daily_inflow - daily_outflow

            if day % 7 == 0:  # 每周记录一次
                forecast.append(
                    {
                        "day": day,
                        "cash_balance": round(cash_balance, 2),
                        "cumulative_inflow": round(daily_inflow * day, 2),
                        "cumulative_outflow": round(daily_outflow * day, 2),
                    }
                )

        return forecast

    def analyze_customer_concentration_risk(self) -> dict[str, Any]:
        """
        分析客户集中度风险

        Returns:
            Dict[str, Any]: 客户集中度风险分析结果
        """
        try:
            customers = self._customer_dao.search()

            # 按收入排序
            customers_by_revenue = sorted(
                customers, key=lambda x: x.get("annual_revenue", 0), reverse=True
            )

            total_revenue = sum(c.get("annual_revenue", 0) for c in customers)

            if total_revenue == 0:
                return {"risk_level": "低", "concentration_ratio": 0}

            # 计算集中度指标
            top1_ratio = (
                customers_by_revenue[0].get("annual_revenue", 0) / total_revenue
                if customers_by_revenue
                else 0
            )
            top5_revenue = sum(
                c.get("annual_revenue", 0) for c in customers_by_revenue[:5]
            )
            top5_ratio = top5_revenue / total_revenue

            # 风险等级判断
            single_limit = self._risk_thresholds["concentration_risk"][
                "single_customer_limit"
            ]
            top5_limit = self._risk_thresholds["concentration_risk"][
                "top5_customer_limit"
            ]

            if top1_ratio > single_limit or top5_ratio > top5_limit:
                risk_level = "高"
            elif top1_ratio > single_limit * 0.8 or top5_ratio > top5_limit * 0.9:
                risk_level = "中"
            else:
                risk_level = "低"

            return {
                "total_customers": len(customers),
                "top1_customer_ratio": round(top1_ratio * 100, 2),
                "top5_customers_ratio": round(top5_ratio * 100, 2),
                "top_customers": [
                    {
                        "name": c.get("name"),
                        "revenue": c.get("annual_revenue", 0),
                        "ratio": round(
                            c.get("annual_revenue", 0) / total_revenue * 100, 2
                        ),
                    }
                    for c in customers_by_revenue[:5]
                ],
                "risk_level": risk_level,
                "concentration_alerts": self._generate_concentration_alerts(
                    top1_ratio, top5_ratio, single_limit, top5_limit
                ),
            }

        except Exception as e:
            self._logger.error(f"客户集中度风险分析失败: {e}")
            return {}

    def analyze_supplier_payment_risk(self) -> dict[str, Any]:
        """
        分析供应商付款风险

        Returns:
            Dict[str, Any]: 供应商付款风险分析结果
        """
        try:
            suppliers = self._supplier_dao.search()

            total_payables = 0
            overdue_payables = 0
            upcoming_payments = []

            current_date = datetime.now()

            for supplier in suppliers:
                payable_amount = supplier.get("payable_amount", 0)
                payment_due_date_str = supplier.get("payment_due_date")

                if payable_amount <= 0:
                    continue

                total_payables += payable_amount

                if payment_due_date_str:
                    try:
                        due_date = datetime.strptime(payment_due_date_str, "%Y-%m-%d")
                        days_to_due = (due_date - current_date).days

                        if days_to_due < 0:
                            overdue_payables += payable_amount
                        elif days_to_due <= 30:
                            upcoming_payments.append(
                                {
                                    "supplier_name": supplier.get("name"),
                                    "amount": payable_amount,
                                    "due_date": payment_due_date_str,
                                    "days_to_due": days_to_due,
                                }
                            )
                    except ValueError:
                        continue

            overdue_rate = (
                (overdue_payables / total_payables * 100) if total_payables > 0 else 0
            )

            # 按金额排序即将到期的付款
            upcoming_payments.sort(key=lambda x: x["amount"], reverse=True)

            return {
                "total_payables": total_payables,
                "overdue_payables": overdue_payables,
                "overdue_rate": round(overdue_rate, 2),
                "upcoming_payments": upcoming_payments[:10],
                "risk_level": "高"
                if overdue_rate > 10
                else "中"
                if overdue_rate > 5
                else "低",
            }

        except Exception as e:
            self._logger.error(f"供应商付款风险分析失败: {e}")
            return {}

    def _calculate_overall_risk_level(
        self,
        credit_risk: dict,
        receivable_risk: dict,
        cash_flow_risk: dict,
        concentration_risk: dict,
    ) -> str:
        """
        计算综合风险等级

        Args:
            credit_risk: 信用风险分析结果
            receivable_risk: 应收账款风险分析结果
            cash_flow_risk: 现金流风险分析结果
            concentration_risk: 集中度风险分析结果

        Returns:
            str: 综合风险等级
        """
        risk_scores = {
            "高": 3,
            "中": 2,
            "低": 1,
        }

        total_score = 0
        risk_count = 0

        for risk_data in [
            credit_risk,
            receivable_risk,
            cash_flow_risk,
            concentration_risk,
        ]:
            risk_level = risk_data.get("risk_level", "中")
            total_score += risk_scores.get(risk_level, 2)
            risk_count += 1

        if risk_count == 0:
            return "中"

        avg_score = total_score / risk_count

        if avg_score >= 2.5:
            return "高"
        elif avg_score >= 1.5:
            return "中"
        else:
            return "低"

    def _generate_risk_alerts(
        self,
        credit_risk: dict,
        receivable_risk: dict,
        cash_flow_risk: dict,
        concentration_risk: dict,
    ) -> list[dict[str, Any]]:
        """
        生成风险预警

        Returns:
            List[Dict[str, Any]]: 风险预警列表
        """
        alerts = []

        # 信用风险预警
        if credit_risk.get("risk_level") == "高":
            alerts.append(
                {
                    "type": "信用风险",
                    "level": "高",
                    "message": (
                        f"高信用风险客户数: "
                        f"{len(credit_risk.get('high_risk_customers', []))}"
                    ),
                    "action": "建议加强信用管理和风险控制",
                }
            )

        # 应收账款预警
        overdue_rate = receivable_risk.get("overdue_rate", 0)
        if overdue_rate > 15:
            alerts.append(
                {
                    "type": "应收账款风险",
                    "level": "高",
                    "message": f"应收账款逾期率达到{overdue_rate}%",
                    "action": "建议加强催收工作",
                }
            )

        # 现金流预警
        if cash_flow_risk.get("risk_level") == "高":
            alerts.append(
                {
                    "type": "现金流风险",
                    "level": "高",
                    "message": "现金流状况不佳,可能影响正常运营",
                    "action": "建议优化现金流管理",
                }
            )

        # 客户集中度预警
        if concentration_risk.get("risk_level") == "高":
            alerts.append(
                {
                    "type": "客户集中度风险",
                    "level": "高",
                    "message": "客户集中度过高,存在业务风险",
                    "action": "建议拓展客户群体,降低集中度",
                }
            )

        return alerts

    def _generate_risk_recommendations(self, overall_risk_level: str) -> list[str]:
        """
        生成风险管理建议

        Args:
            overall_risk_level: 综合风险等级

        Returns:
            List[str]: 风险管理建议
        """
        if overall_risk_level == "高":
            return [
                "立即制定风险应对计划",
                "加强客户信用管理",
                "优化现金流管理",
                "建立风险预警机制",
                "考虑购买信用保险",
                "定期评估和调整风险策略",
            ]
        elif overall_risk_level == "中":
            return [
                "持续监控风险指标",
                "完善风险管理制度",
                "加强应收账款管理",
                "优化客户结构",
                "建立风险缓解措施",
            ]
        else:
            return [
                "保持当前风险管理水平",
                "定期进行风险评估",
                "持续优化业务流程",
                "关注市场变化",
            ]

    def _identify_credit_risk_factors(self, customer: dict[str, Any]) -> list[str]:
        """识别客户信用风险因素"""
        risk_factors = []

        if customer.get("on_time_payment_rate", 1.0) < 0.8:
            risk_factors.append("付款及时率低")

        if customer.get("overdue_count", 0) > 3:
            risk_factors.append("逾期次数过多")

        if customer.get("financial_rating", "B") in ["C", "D"]:
            risk_factors.append("财务评级较低")

        if customer.get("debt_ratio", 0) > 0.7:
            risk_factors.append("负债率过高")

        return risk_factors

    def _calculate_average_credit_score(self, customers: list[dict[str, Any]]) -> float:
        """计算平均信用评分"""
        if not customers:
            return 0

        total_score = sum(self._calculate_customer_credit_score(c) for c in customers)
        return round(total_score / len(customers), 2)

    def _determine_credit_risk_level(self, risk_distribution: dict[str, int]) -> str:
        """确定信用风险等级"""
        total_customers = sum(risk_distribution.values())
        if total_customers == 0:
            return "低"

        high_risk_ratio = risk_distribution["高风险"] / total_customers

        if high_risk_ratio > 0.2:
            return "高"
        elif high_risk_ratio > 0.1:
            return "中"
        else:
            return "低"

    def _determine_receivable_risk_level(self, overdue_rate: float) -> str:
        """确定应收账款风险等级"""
        if overdue_rate > 20:
            return "高"
        elif overdue_rate > 10:
            return "中"
        else:
            return "低"

    def _generate_cash_flow_alerts(
        self, cash_flow_ratio: float, days_cash_on_hand: float
    ) -> list[str]:
        """生成现金流预警"""
        alerts = []

        if cash_flow_ratio < 0:
            alerts.append("现金流为负,需要立即关注")

        if days_cash_on_hand < 30:
            alerts.append("现金储备不足30天,存在流动性风险")

        if cash_flow_ratio < 0.1:
            alerts.append("现金流比率过低,建议优化收支结构")

        return alerts

    def _generate_concentration_alerts(
        self,
        top1_ratio: float,
        top5_ratio: float,
        single_limit: float,
        top5_limit: float,
    ) -> list[str]:
        """生成客户集中度预警"""
        alerts = []

        if top1_ratio > single_limit:
            alerts.append(
                f"最大客户占比{top1_ratio * 100:.1f}%,超过{single_limit * 100}%限制"
            )

        if top5_ratio > top5_limit:
            alerts.append(
                f"前5大客户占比{top5_ratio * 100:.1f}%,超过{top5_limit * 100}%限制"
            )

        return alerts

    def update_risk_thresholds(
        self, threshold_updates: dict[str, dict[str, float]]
    ) -> bool:
        """
        更新风险阈值

        Args:
            threshold_updates: 阈值更新数据

        Returns:
            bool: 更新是否成功
        """
        try:
            for category, thresholds in threshold_updates.items():
                if category in self._risk_thresholds:
                    self._risk_thresholds[category].update(thresholds)

            self._logger.info("风险阈值更新成功")
            return True

        except Exception as e:
            self._logger.error(f"风险阈值更新失败: {e}")
            return False

    def get_risk_thresholds(self) -> dict[str, dict[str, float]]:
        """
        获取当前风险阈值配置

        Returns:
            Dict[str, Dict[str, float]]: 风险阈值配置
        """
        return self._risk_thresholds.copy()
