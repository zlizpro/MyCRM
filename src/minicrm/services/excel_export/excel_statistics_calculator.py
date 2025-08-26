"""
Excel统计计算器

负责Excel导出中的各种统计计算功能.
提供客户、供应商等数据的统计分析.
"""

import logging
from datetime import datetime
from typing import Any


class ExcelStatisticsCalculator:
    """
    Excel统计计算器

    提供Excel导出中的统计计算功能.
    """

    def __init__(self):
        """初始化统计计算器"""
        self._logger = logging.getLogger(__name__)

    def calculate_customer_statistics(
        self, customers: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        计算客户统计数据

        Args:
            customers: 客户数据列表

        Returns:
            Dict[str, Any]: 统计数据
        """
        if not customers:
            return {}

        try:
            active_customers = sum(1 for c in customers if c.get("status") == "active")
            high_value_customers = sum(
                1 for c in customers if c.get("value_score", 0) >= 80
            )

            # 计算本月新增(简化实现)
            current_month = datetime.now().strftime("%Y-%m")
            new_this_month = sum(
                1
                for c in customers
                if c.get("created_at", "").startswith(current_month)
            )

            # 计算平均合作时长
            cooperation_months = [
                c.get("cooperation_months", 0)
                for c in customers
                if c.get("cooperation_months")
            ]
            avg_cooperation_months = (
                sum(cooperation_months) / len(cooperation_months)
                if cooperation_months
                else 0
            )

            return {
                "active_customers": active_customers,
                "high_value_customers": high_value_customers,
                "new_this_month": new_this_month,
                "avg_cooperation_months": avg_cooperation_months,
            }

        except Exception as e:
            self._logger.error(f"计算客户统计数据失败: {e}")
            return {}

    def calculate_industry_distribution(
        self, customers: list[dict[str, Any]]
    ) -> dict[str, int]:
        """
        计算行业分布

        Args:
            customers: 客户数据列表

        Returns:
            Dict[str, int]: 行业分布统计
        """
        try:
            distribution = {}
            for customer in customers:
                industry = customer.get("industry", "其他")
                distribution[industry] = distribution.get(industry, 0) + 1
            return distribution

        except Exception as e:
            self._logger.error(f"计算行业分布失败: {e}")
            return {}

    def calculate_value_distribution(
        self, customers: list[dict[str, Any]]
    ) -> dict[str, int]:
        """
        计算客户价值分布

        Args:
            customers: 客户数据列表

        Returns:
            Dict[str, int]: 价值分布统计
        """
        try:
            distribution = {"高价值": 0, "中价值": 0, "低价值": 0, "潜在": 0}

            for customer in customers:
                score = customer.get("value_score", 0)
                if score >= 80:
                    distribution["高价值"] += 1
                elif score >= 60:
                    distribution["中价值"] += 1
                elif score >= 40:
                    distribution["低价值"] += 1
                else:
                    distribution["潜在"] += 1

            return distribution

        except Exception as e:
            self._logger.error(f"计算价值分布失败: {e}")
            return {"高价值": 0, "中价值": 0, "低价值": 0, "潜在": 0}

    def calculate_data_completeness(self, customers: list[dict[str, Any]]) -> float:
        """
        计算数据完整性

        Args:
            customers: 客户数据列表

        Returns:
            float: 数据完整性百分比
        """
        if not customers:
            return 0.0

        try:
            required_fields = ["name", "phone", "email", "industry"]
            total_fields = len(required_fields) * len(customers)
            filled_fields = 0

            for customer in customers:
                for field in required_fields:
                    if customer.get(field):
                        filled_fields += 1

            return (filled_fields / total_fields * 100) if total_fields > 0 else 0.0

        except Exception as e:
            self._logger.error(f"计算数据完整性失败: {e}")
            return 0.0

    def generate_data_quality_report(
        self, customers: list[dict[str, Any]]
    ) -> dict[str, str]:
        """
        生成数据质量报告

        Args:
            customers: 客户数据列表

        Returns:
            Dict[str, str]: 数据质量报告
        """
        if not customers:
            return {}

        try:
            # 计算各种质量指标
            missing_phone = sum(1 for c in customers if not c.get("phone"))
            missing_email = sum(1 for c in customers if not c.get("email"))
            missing_industry = sum(1 for c in customers if not c.get("industry"))

            total = len(customers)

            return {
                "缺失电话号码": f"{missing_phone} ({missing_phone / total * 100:.1f}%)",
                "缺失邮箱地址": f"{missing_email} ({missing_email / total * 100:.1f}%)",
                "缺失行业信息": (
                    f"{missing_industry} ({missing_industry / total * 100:.1f}%)"
                ),
                "数据完整性": f"{self.calculate_data_completeness(customers):.1f}%",
            }

        except Exception as e:
            self._logger.error(f"生成数据质量报告失败: {e}")
            return {}

    def get_top_customers(
        self, customers: list[dict[str, Any]], limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        获取顶级客户列表

        Args:
            customers: 客户数据列表
            limit: 返回数量限制

        Returns:
            List[Dict[str, Any]]: 顶级客户列表
        """
        try:
            return sorted(
                customers, key=lambda x: x.get("value_score", 0), reverse=True
            )[:limit]

        except Exception as e:
            self._logger.error(f"获取顶级客户失败: {e}")
            return []

    def calculate_financial_summary(
        self, customers: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        计算财务汇总数据

        Args:
            customers: 客户数据列表

        Returns:
            Dict[str, Any]: 财务汇总数据
        """
        try:
            total_revenue = sum(c.get("annual_revenue", 0) for c in customers)
            avg_revenue = total_revenue / len(customers) if customers else 0

            return {
                "total_customers": len(customers),
                "total_revenue": total_revenue,
                "avg_revenue": avg_revenue,
                "data_completeness": self.calculate_data_completeness(customers),
            }

        except Exception as e:
            self._logger.error(f"计算财务汇总失败: {e}")
            return {}
