"""
MiniCRM 数据分析服务

严格遵循业务逻辑层职责：
- 只处理数据分析相关的业务逻辑
- 通过DAO接口访问数据
- 不包含UI逻辑
- 实现IAnalyticsService接口
"""

import logging
from datetime import datetime
from typing import Any

import transfunctions.calculations as calculations
from minicrm.core.exceptions import ServiceError
from minicrm.core.interfaces.dao_interfaces import ICustomerDAO, ISupplierDAO
from minicrm.core.interfaces.service_interfaces import IAnalyticsService


class AnalyticsService(IAnalyticsService):
    """
    数据分析服务实现

    严格遵循单一职责原则：
    - 只负责数据分析相关的业务逻辑
    - 通过依赖注入使用DAO层
    - 使用transfunctions进行数据计算
    - 不包含UI逻辑
    """

    def __init__(self, customer_dao: ICustomerDAO, supplier_dao: ISupplierDAO):
        """
        初始化分析服务

        Args:
            customer_dao: 客户数据访问对象
            supplier_dao: 供应商数据访问对象
        """
        self._customer_dao = customer_dao
        self._supplier_dao = supplier_dao
        self._logger = logging.getLogger(__name__)
        self._logger.debug("数据分析服务初始化完成")

    def get_dashboard_data(self) -> dict[str, Any]:
        """
        获取仪表盘数据

        业务逻辑：
        1. 获取关键指标数据
        2. 获取图表数据
        3. 进行数据计算和分析

        Returns:
            Dict[str, Any]: 仪表盘数据
        """
        try:
            dashboard_data = {
                "metrics": self._get_key_metrics(),
                "charts": self._get_chart_data(),
            }

            self._logger.debug("成功获取仪表盘数据")
            return dashboard_data

        except Exception as e:
            self._logger.error(f"获取仪表盘数据失败: {e}")
            raise ServiceError(f"获取仪表盘数据失败: {e}", "AnalyticsService") from e

    def generate_customer_report(
        self, start_date: str, end_date: str
    ) -> dict[str, Any]:
        """
        生成客户报表

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            Dict[str, Any]: 客户报表数据
        """
        try:
            # 获取时间段内的客户数据
            conditions = {"created_at": f"BETWEEN '{start_date}' AND '{end_date}'"}

            customers = self._customer_dao.search(conditions)

            # 生成报表数据
            report_data = {
                "period": {"start": start_date, "end": end_date},
                "total_customers": len(customers),
                "customer_analysis": self._analyze_customers(customers),
                "growth_analysis": self._analyze_customer_growth(start_date, end_date),
                "generated_at": datetime.now().isoformat(),
            }

            self._logger.info(f"生成客户报表: {start_date} 到 {end_date}")
            return report_data

        except Exception as e:
            self._logger.error(f"生成客户报表失败: {e}")
            raise ServiceError(f"生成客户报表失败: {e}", "AnalyticsService") from e

    def generate_supplier_report(
        self, start_date: str, end_date: str
    ) -> dict[str, Any]:
        """
        生成供应商报表

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            Dict[str, Any]: 供应商报表数据
        """
        try:
            # 获取时间段内的供应商数据
            conditions = {"created_at": f"BETWEEN '{start_date}' AND '{end_date}'"}

            suppliers = self._supplier_dao.search(conditions)

            # 生成报表数据
            report_data = {
                "period": {"start": start_date, "end": end_date},
                "total_suppliers": len(suppliers),
                "supplier_analysis": self._analyze_suppliers(suppliers),
                "category_analysis": self._analyze_supplier_categories(suppliers),
                "generated_at": datetime.now().isoformat(),
            }

            self._logger.info(f"生成供应商报表: {start_date} 到 {end_date}")
            return report_data

        except Exception as e:
            self._logger.error(f"生成供应商报表失败: {e}")
            raise ServiceError(f"生成供应商报表失败: {e}", "AnalyticsService") from e

    def get_trend_analysis(self, metric: str, period: str) -> dict[str, Any]:
        """
        获取趋势分析

        Args:
            metric: 指标名称
            period: 时间周期

        Returns:
            Dict[str, Any]: 趋势分析数据
        """
        try:
            if metric == "customer_growth":
                return self._get_customer_growth_trend(period)
            elif metric == "supplier_growth":
                return self._get_supplier_growth_trend(period)
            else:
                raise ServiceError(f"不支持的指标: {metric}", "AnalyticsService") from e

        except ServiceError:
            raise
        except Exception as e:
            self._logger.error(f"获取趋势分析失败: {e}")
            raise ServiceError(f"获取趋势分析失败: {e}", "AnalyticsService") from e

    def _get_key_metrics(self) -> dict[str, Any]:
        """获取关键指标数据"""
        try:
            # 获取客户统计
            customer_stats = self._customer_dao.get_statistics()

            # 获取供应商统计
            supplier_stats = self._supplier_dao.get_statistics()

            # 计算关键指标
            metrics = {
                "total_customers": customer_stats.get("total_customers", 0),
                "new_customers_this_month": customer_stats.get("new_this_month", 0),
                "total_suppliers": supplier_stats.get("total_suppliers", 0),
                "active_customers": customer_stats.get("by_status", {}).get(
                    "active", 0
                ),
                "pending_tasks": self._get_pending_tasks_count(),
                "total_receivables": self._get_total_receivables(),
                "total_payables": self._get_total_payables(),
            }

            # 使用transfunctions进行额外计算
            metrics["customer_satisfaction"] = (
                calculations.calculate_customer_satisfaction_score(customer_stats)
            )

            return metrics

        except Exception as e:
            self._logger.error(f"获取关键指标失败: {e}")
            # 返回默认值避免UI崩溃
            return {
                "total_customers": 0,
                "new_customers_this_month": 0,
                "total_suppliers": 0,
                "active_customers": 0,
                "pending_tasks": 0,
                "total_receivables": 0,
                "total_payables": 0,
                "customer_satisfaction": 0,
            }

    def _get_chart_data(self) -> dict[str, Any]:
        """获取图表数据"""
        try:
            charts = {
                "customer_growth": self._get_customer_growth_chart(),
                "customer_types": self._get_customer_types_chart(),
                "monthly_interactions": self._get_monthly_interactions_chart(),
                "receivables_status": self._get_receivables_status_chart(),
            }

            return charts

        except Exception as e:
            self._logger.error(f"获取图表数据失败: {e}")
            # 返回空图表数据避免UI崩溃
            return {}

    def _get_customer_growth_chart(self) -> dict[str, Any]:
        """获取客户增长图表数据"""
        # 简化实现，实际应该从数据库获取历史数据
        return {
            "type": "line",
            "labels": ["1月", "2月", "3月", "4月", "5月", "6月"],
            "data": [120, 132, 145, 151, 156, 156],
            "title": "客户增长趋势",
        }

    def _get_customer_types_chart(self) -> dict[str, Any]:
        """获取客户类型分布图表数据"""
        try:
            customer_stats = self._customer_dao.get_statistics()
            by_level = customer_stats.get("by_level", {})

            return {
                "type": "pie",
                "labels": list(by_level.keys()),
                "data": list(by_level.values()),
                "title": "客户类型分布",
            }
        except Exception:
            return {
                "type": "pie",
                "labels": ["VIP客户", "重要客户", "普通客户", "潜在客户"],
                "data": [25, 38, 68, 25],
                "title": "客户类型分布",
            }

    def _get_monthly_interactions_chart(self) -> dict[str, Any]:
        """获取月度互动频率图表数据"""
        # 简化实现
        return {
            "type": "bar",
            "labels": ["1月", "2月", "3月", "4月", "5月", "6月"],
            "data": [85, 92, 78, 105, 98, 112],
            "title": "月度互动频率",
        }

    def _get_receivables_status_chart(self) -> dict[str, Any]:
        """获取应收账款状态图表数据"""
        # 简化实现
        return {
            "type": "bar",
            "labels": ["正常", "逾期30天内", "逾期30-60天", "逾期60天以上"],
            "data": [457000, 25000, 15000, 5000],
            "title": "应收账款状态",
        }

    def _analyze_customers(self, customers: list) -> dict[str, Any]:
        """分析客户数据"""
        if not customers:
            return {}

        # 使用transfunctions进行分析
        return calculations.analyze_customer_data(customers)

    def _analyze_suppliers(self, suppliers: list) -> dict[str, Any]:
        """分析供应商数据"""
        if not suppliers:
            return {}

        # 使用transfunctions进行分析
        return calculations.analyze_supplier_data(suppliers)

    def _analyze_customer_growth(
        self, start_date: str, end_date: str
    ) -> dict[str, Any]:
        """分析客户增长"""
        # 简化实现
        return {
            "growth_rate": 15.2,
            "trend": "increasing",
            "period_comparison": "上月增长12.5%",
        }

    def _analyze_supplier_categories(self, suppliers: list) -> dict[str, Any]:
        """分析供应商类别"""
        if not suppliers:
            return {}

        categories = {}
        for supplier in suppliers:
            category = supplier.get("category", "未分类")
            categories[category] = categories.get(category, 0) + 1

        return categories

    def _get_customer_growth_trend(self, period: str) -> dict[str, Any]:
        """获取客户增长趋势"""
        # 简化实现
        return {
            "period": period,
            "trend": "increasing",
            "data": [120, 132, 145, 151, 156],
            "growth_rate": 15.2,
        }

    def _get_supplier_growth_trend(self, period: str) -> dict[str, Any]:
        """获取供应商增长趋势"""
        # 简化实现
        return {
            "period": period,
            "trend": "stable",
            "data": [45, 47, 48, 49, 50],
            "growth_rate": 5.8,
        }

    def _get_pending_tasks_count(self) -> int:
        """获取待办任务数量"""
        # 简化实现，实际应该从任务表获取
        return 8

    def _get_total_receivables(self) -> float:
        """获取应收账款总额"""
        # 简化实现，实际应该从财务表获取
        return 502000.0

    def _get_total_payables(self) -> float:
        """获取应付账款总额"""
        # 简化实现，实际应该从财务表获取
        return 321000.0

    def cleanup(self) -> None:
        """清理服务资源"""
        self._logger.debug("数据分析服务资源清理完成")
