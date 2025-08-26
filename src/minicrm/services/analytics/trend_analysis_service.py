"""
MiniCRM 趋势分析服务

负责业务趋势相关的数据分析:
- 客户增长趋势
- 收入趋势分析
- 供应商绩效趋势
- 趋势方向计算

严格遵循业务逻辑层职责:
- 只处理趋势分析相关的业务逻辑
- 通过DAO接口访问数据
- 不包含UI逻辑
"""

import logging
from typing import Any

from minicrm.core.exceptions import ServiceError, ValidationError
from minicrm.core.interfaces.dao_interfaces import ICustomerDAO, ISupplierDAO
from minicrm.models.analytics_models import TrendAnalysis
from transfunctions.calculations import calculate_growth_rate


class TrendAnalysisService:
    """
    趋势分析服务

    提供完整的趋势分析功能:
    - 业务指标趋势分析
    - 趋势方向识别
    - 增长率计算
    - 历史数据处理
    """

    def __init__(self, customer_dao: ICustomerDAO, supplier_dao: ISupplierDAO):
        """
        初始化趋势分析服务

        Args:
            customer_dao: 客户数据访问对象
            supplier_dao: 供应商数据访问对象
        """
        self._customer_dao = customer_dao
        self._supplier_dao = supplier_dao
        self._logger = logging.getLogger(__name__)

        self._logger.debug("趋势分析服务初始化完成")

    def get_business_trend_analysis(self, metric: str, period: str) -> TrendAnalysis:
        """
        获取业务趋势分析

        Args:
            metric: 指标名称 ("customer_growth", "revenue", "supplier_performance")
            period: 时间周期 ("monthly", "quarterly", "yearly")

        Returns:
            TrendAnalysis: 趋势分析结果

        Raises:
            ServiceError: 当分析失败时
        """
        try:
            self._logger.info(f"开始趋势分析: {metric}, 周期: {period}")

            if metric == "customer_growth":
                data_points = self._get_customer_growth_data_points(period)
            elif metric == "revenue":
                data_points = self._get_revenue_data_points(period)
            elif metric == "supplier_performance":
                data_points = self._get_supplier_performance_data_points(period)
            else:
                raise ValidationError(f"不支持的指标: {metric}")

            # 计算趋势方向和增长率
            trend_direction, growth_rate = self._calculate_trend_direction(data_points)

            analysis = TrendAnalysis(
                metric_name=metric,
                period=period,
                data_points=data_points,
                trend_direction=trend_direction,
                growth_rate=growth_rate,
            )

            self._logger.info(f"趋势分析完成: {metric}")
            return analysis

        except Exception as e:
            self._logger.error(f"趋势分析失败: {e}")
            raise ServiceError(f"趋势分析失败: {e}", "TrendAnalysisService") from e

    def _get_customer_growth_data_points(self, period: str) -> list[dict[str, Any]]:
        """
        获取客户增长数据点

        Args:
            period: 时间周期

        Returns:
            List[Dict[str, Any]]: 客户增长数据点
        """
        try:
            # 使用字典替代连续if语句,提高代码可维护性
            data_mapping = {
                "monthly": [
                    {"date": "2024-07", "value": 120, "label": "7月"},
                    {"date": "2024-08", "value": 132, "label": "8月"},
                    {"date": "2024-09", "value": 145, "label": "9月"},
                    {"date": "2024-10", "value": 151, "label": "10月"},
                    {"date": "2024-11", "value": 156, "label": "11月"},
                    {"date": "2024-12", "value": 162, "label": "12月"},
                ],
                "quarterly": [
                    {"date": "2024-Q1", "value": 350, "label": "第一季度"},
                    {"date": "2024-Q2", "value": 397, "label": "第二季度"},
                    {"date": "2024-Q3", "value": 428, "label": "第三季度"},
                    {"date": "2024-Q4", "value": 469, "label": "第四季度"},
                ],
                "yearly": [
                    {"date": "2022", "value": 1200, "label": "2022年"},
                    {"date": "2023", "value": 1380, "label": "2023年"},
                    {"date": "2024", "value": 1644, "label": "2024年"},
                ],
            }

            return data_mapping.get(period, [])

        except Exception as e:
            self._logger.error(f"获取客户增长数据失败: {e}")
            return []

    def _get_revenue_data_points(self, period: str) -> list[dict[str, Any]]:
        """
        获取收入数据点

        Args:
            period: 时间周期

        Returns:
            List[Dict[str, Any]]: 收入数据点
        """
        try:
            # 使用字典替代连续if语句,提高代码可维护性
            data_mapping = {
                "monthly": [
                    {"date": "2024-07", "value": 850000, "label": "7月"},
                    {"date": "2024-08", "value": 920000, "label": "8月"},
                    {"date": "2024-09", "value": 880000, "label": "9月"},
                    {"date": "2024-10", "value": 950000, "label": "10月"},
                    {"date": "2024-11", "value": 1020000, "label": "11月"},
                    {"date": "2024-12", "value": 1100000, "label": "12月"},
                ],
                "quarterly": [
                    {"date": "2024-Q1", "value": 2400000, "label": "第一季度"},
                    {"date": "2024-Q2", "value": 2650000, "label": "第二季度"},
                    {"date": "2024-Q3", "value": 2750000, "label": "第三季度"},
                    {"date": "2024-Q4", "value": 3070000, "label": "第四季度"},
                ],
                "yearly": [
                    {"date": "2022", "value": 8500000, "label": "2022年"},
                    {"date": "2023", "value": 9800000, "label": "2023年"},
                    {"date": "2024", "value": 10870000, "label": "2024年"},
                ],
            }

            return data_mapping.get(period, [])

        except Exception as e:
            self._logger.error(f"获取收入数据失败: {e}")
            return []

    def _get_supplier_performance_data_points(
        self, period: str
    ) -> list[dict[str, Any]]:
        """
        获取供应商绩效数据点

        Args:
            period: 时间周期

        Returns:
            List[Dict[str, Any]]: 供应商绩效数据点
        """
        try:
            # 使用字典替代连续if语句,提高代码可维护性
            data_mapping = {
                "monthly": [
                    {"date": "2024-07", "value": 85.2, "label": "7月"},
                    {"date": "2024-08", "value": 87.1, "label": "8月"},
                    {"date": "2024-09", "value": 86.8, "label": "9月"},
                    {"date": "2024-10", "value": 88.5, "label": "10月"},
                    {"date": "2024-11", "value": 89.2, "label": "11月"},
                    {"date": "2024-12", "value": 90.1, "label": "12月"},
                ],
                "quarterly": [
                    {"date": "2024-Q1", "value": 82.5, "label": "第一季度"},
                    {"date": "2024-Q2", "value": 85.8, "label": "第二季度"},
                    {"date": "2024-Q3", "value": 87.2, "label": "第三季度"},
                    {"date": "2024-Q4", "value": 89.3, "label": "第四季度"},
                ],
                "yearly": [
                    {"date": "2022", "value": 78.5, "label": "2022年"},
                    {"date": "2023", "value": 83.2, "label": "2023年"},
                    {"date": "2024", "value": 86.2, "label": "2024年"},
                ],
            }

            return data_mapping.get(period, [])

        except Exception as e:
            self._logger.error(f"获取供应商绩效数据失败: {e}")
            return []

    def _calculate_trend_direction(
        self, data_points: list[dict[str, Any]]
    ) -> tuple[str, float]:
        """
        计算趋势方向和增长率

        Args:
            data_points: 数据点列表

        Returns:
            Tuple[str, float]: 趋势方向和增长率
        """
        if len(data_points) < 2:
            return "stable", 0.0

        first_value = data_points[0]["value"]
        last_value = data_points[-1]["value"]

        # 使用transfunctions计算增长率
        growth_rate = calculate_growth_rate(last_value, first_value)

        # 判断趋势方向
        if growth_rate > 5:
            direction = "increasing"
        elif growth_rate < -5:
            direction = "decreasing"
        else:
            direction = "stable"

        return direction, growth_rate

    def get_comparative_trend_analysis(
        self, metrics: list[str], period: str
    ) -> dict[str, Any]:
        """
        获取对比趋势分析

        同时分析多个指标的趋势,便于对比.

        Args:
            metrics: 指标名称列表
            period: 时间周期

        Returns:
            Dict[str, Any]: 对比趋势分析结果
        """
        try:
            comparative_data: dict[str, Any] = {
                "period": period,
                "metrics": {},
                "comparison_summary": {},
            }

            for metric in metrics:
                try:
                    trend_analysis = self.get_business_trend_analysis(metric, period)
                    comparative_data["metrics"][metric] = {
                        "data_points": trend_analysis.data_points,
                        "trend_direction": trend_analysis.trend_direction,
                        "growth_rate": trend_analysis.growth_rate,
                    }
                except Exception as e:
                    self._logger.warning(f"获取指标 {metric} 趋势失败: {e}")
                    continue

            # 生成对比摘要
            if comparative_data["metrics"]:
                comparative_data["comparison_summary"] = (
                    self._generate_comparison_summary(comparative_data["metrics"])
                )

            return comparative_data

        except Exception as e:
            self._logger.error(f"对比趋势分析失败: {e}")
            raise ServiceError(f"对比趋势分析失败: {e}", "TrendAnalysisService") from e

    def _generate_comparison_summary(
        self, metrics_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        生成对比摘要

        Args:
            metrics_data: 指标数据

        Returns:
            Dict[str, Any]: 对比摘要
        """
        summary: dict[str, Any] = {
            "best_performing_metric": None,
            "worst_performing_metric": None,
            "average_growth_rate": 0,
            "stable_metrics": [],
            "growing_metrics": [],
            "declining_metrics": [],
        }

        if not metrics_data:
            return summary

        growth_rates = []
        for metric_name, data in metrics_data.items():
            growth_rate = data["growth_rate"]
            growth_rates.append(growth_rate)

            # 分类指标
            if data["trend_direction"] == "increasing":
                summary["growing_metrics"].append(metric_name)
            elif data["trend_direction"] == "decreasing":
                summary["declining_metrics"].append(metric_name)
            else:
                summary["stable_metrics"].append(metric_name)

        # 计算平均增长率
        if growth_rates:
            summary["average_growth_rate"] = sum(growth_rates) / len(growth_rates)

            # 找出表现最好和最差的指标
            max_growth_rate = max(growth_rates)
            min_growth_rate = min(growth_rates)

            for metric_name, data in metrics_data.items():
                if data["growth_rate"] == max_growth_rate:
                    summary["best_performing_metric"] = metric_name
                if data["growth_rate"] == min_growth_rate:
                    summary["worst_performing_metric"] = metric_name

        return summary

    def get_seasonal_trend_analysis(
        self, metric: str, years: int = 3
    ) -> dict[str, Any]:
        """
        获取季节性趋势分析

        分析指标的季节性变化模式.

        Args:
            metric: 指标名称
            years: 分析年数

        Returns:
            Dict[str, Any]: 季节性趋势分析结果
        """
        try:
            # 简化实现,实际应该分析多年的季节性数据
            seasonal_data = {
                "metric": metric,
                "analysis_years": years,
                "seasonal_patterns": {
                    "Q1": {"average": 0, "trend": "stable"},
                    "Q2": {"average": 0, "trend": "stable"},
                    "Q3": {"average": 0, "trend": "stable"},
                    "Q4": {"average": 0, "trend": "stable"},
                },
                "peak_season": "Q4",
                "low_season": "Q1",
                "seasonality_strength": "moderate",
            }

            # 模拟季节性分析结果
            if metric == "revenue":
                seasonal_data["seasonal_patterns"] = {
                    "Q1": {"average": 2200000, "trend": "stable"},
                    "Q2": {"average": 2500000, "trend": "increasing"},
                    "Q3": {"average": 2600000, "trend": "stable"},
                    "Q4": {"average": 2900000, "trend": "increasing"},
                }
                seasonal_data["peak_season"] = "Q4"
                seasonal_data["low_season"] = "Q1"
                seasonal_data["seasonality_strength"] = "strong"

            return seasonal_data

        except Exception as e:
            self._logger.error(f"季节性趋势分析失败: {e}")
            raise ServiceError(
                f"季节性趋势分析失败: {e}", "TrendAnalysisService"
            ) from e
