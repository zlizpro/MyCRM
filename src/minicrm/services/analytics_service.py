"""
MiniCRM 数据分析服务主协调器

作为分析服务的统一入口,负责:
- 服务协调和依赖注入
- 缓存管理和性能优化
- 报表生成和数据整合
- 对外接口统一

严格遵循业务逻辑层职责:
- 协调各个分析子服务
- 通过DAO接口访问数据
- 不包含UI逻辑
- 实现IAnalyticsService接口
"""

import logging
from datetime import datetime
from typing import Any

from minicrm.core.exceptions import ServiceError
from minicrm.core.interfaces.dao_interfaces import ICustomerDAO, ISupplierDAO
from minicrm.core.interfaces.service_interfaces import IAnalyticsService
from minicrm.models.analytics_models import (
    CustomerAnalysis,
    MetricCard,
    PredictionResult,
    SupplierAnalysis,
    TrendAnalysis,
)
from minicrm.services.analytics.cache_manager import CacheManager
from minicrm.services.analytics.customer_analytics_service import (
    CustomerAnalyticsService,
)
from minicrm.services.analytics.dashboard_service import DashboardService
from minicrm.services.analytics.financial_risk_service import FinancialRiskService
from minicrm.services.analytics.prediction_service import PredictionService
from minicrm.services.analytics.supplier_analytics_service import (
    SupplierAnalyticsService,
)
from minicrm.services.analytics.trend_analysis_service import TrendAnalysisService


class AnalyticsService(IAnalyticsService):
    """
    数据分析服务主协调器

    作为分析服务的统一入口,协调各个子服务:
    - 仪表盘服务:关键指标和图表数据
    - 客户分析服务:客户价值和增长分析
    - 供应商分析服务:供应商质量和绩效分析
    - 趋势分析服务:业务趋势和方向分析
    - 预测服务:业务预测和预测评估
    - 缓存管理:性能优化和数据缓存
    """

    def __init__(self, customer_dao: ICustomerDAO, supplier_dao: ISupplierDAO):
        """
        初始化分析服务协调器

        Args:
            customer_dao: 客户数据访问对象
            supplier_dao: 供应商数据访问对象
        """
        self._customer_dao = customer_dao
        self._supplier_dao = supplier_dao
        self._logger = logging.getLogger(__name__)

        # 初始化缓存管理器
        self._cache_manager = CacheManager(cache_ttl=300)  # 5分钟缓存

        # 初始化各个分析服务
        self._dashboard_service = DashboardService(customer_dao, supplier_dao)
        self._customer_analytics_service = CustomerAnalyticsService(customer_dao)
        self._supplier_analytics_service = SupplierAnalyticsService(supplier_dao)
        self._trend_analysis_service = TrendAnalysisService(customer_dao, supplier_dao)
        self._prediction_service = PredictionService(customer_dao, supplier_dao)
        self._financial_risk_service = FinancialRiskService(customer_dao, supplier_dao)

        self._logger.debug("数据分析服务协调器初始化完成")

    def get_dashboard_data(self) -> dict[str, Any]:
        """
        获取仪表盘数据

        委托给仪表盘服务处理,并提供缓存支持.

        Returns:
            Dict[str, Any]: 完整的仪表盘数据

        Raises:
            ServiceError: 当数据获取失败时
        """
        try:
            # 检查缓存
            cache_key = "dashboard_data"
            cached_data = self._cache_manager.get(cache_key)
            if cached_data:
                self._logger.debug("从缓存获取仪表盘数据")
                return cached_data

            self._logger.info("开始获取仪表盘数据")

            # 委托给仪表盘服务
            dashboard_data = self._dashboard_service.get_dashboard_data()

            # 缓存结果
            self._cache_manager.set(cache_key, dashboard_data)

            self._logger.info("仪表盘数据获取完成")
            return dashboard_data

        except Exception as e:
            self._logger.error(f"获取仪表盘数据失败: {e}")
            raise ServiceError(f"获取仪表盘数据失败: {e}", "AnalyticsService") from e

    def generate_customer_report(
        self, start_date: str, end_date: str
    ) -> dict[str, Any]:
        """
        生成客户报表

        整合客户分析服务的数据生成完整报表.

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

            # 使用客户分析服务进行分析
            customer_analysis = self._customer_analytics_service.get_customer_analysis()
            customer_segments = (
                self._customer_analytics_service.analyze_customer_segments(customers)
            )

            # 生成报表数据
            report_data = {
                "period": {"start": start_date, "end": end_date},
                "total_customers": len(customers),
                "customer_analysis": {
                    "total_customers": customer_analysis.total_customers,
                    "new_customers_this_month": (
                        customer_analysis.new_customers_this_month
                    ),
                    "active_customers": customer_analysis.active_customers,
                    "value_distribution": customer_analysis.customer_value_distribution,
                    "top_customers": customer_analysis.top_customers[
                        :5
                    ],  # 报表中只显示前5名
                },
                "customer_segments": customer_segments,
                "growth_trend": customer_analysis.growth_trend,
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

        整合供应商分析服务的数据生成完整报表.

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

            # 使用供应商分析服务进行分析
            supplier_analysis = self._supplier_analytics_service.get_supplier_analysis()
            performance_analysis = (
                self._supplier_analytics_service.analyze_supplier_performance(suppliers)
            )
            risk_analysis = self._supplier_analytics_service.get_supplier_risk_analysis(
                suppliers
            )

            # 生成报表数据
            report_data = {
                "period": {"start": start_date, "end": end_date},
                "total_suppliers": len(suppliers),
                "supplier_analysis": {
                    "total_suppliers": supplier_analysis.total_suppliers,
                    "active_suppliers": supplier_analysis.active_suppliers,
                    "quality_distribution": supplier_analysis.quality_distribution,
                    "top_suppliers": supplier_analysis.top_suppliers[
                        :5
                    ],  # 报表中只显示前5名
                    "category_distribution": supplier_analysis.category_distribution,
                },
                "performance_analysis": performance_analysis,
                "risk_analysis": risk_analysis,
                "generated_at": datetime.now().isoformat(),
            }

            self._logger.info(f"生成供应商报表: {start_date} 到 {end_date}")
            return report_data

        except Exception as e:
            self._logger.error(f"生成供应商报表失败: {e}")
            raise ServiceError(f"生成供应商报表失败: {e}", "AnalyticsService") from e

    def _get_key_metrics(self) -> list[MetricCard]:
        """
        获取关键指标卡片数据

        实现需求10中定义的关键指标:
        - 客户总数、本月新增客户数、待办任务数
        - 应收账款、应付账款等财务指标
        """
        # 委托给仪表盘服务处理
        return self._dashboard_service.get_key_metrics()

    def _get_chart_data(self) -> dict[str, Any]:
        """获取图表数据"""
        # 委托给图表服务处理
        return self._chart_service.get_all_charts()

    def get_customer_analysis(self, time_period_months: int = 12) -> CustomerAnalysis:
        """
        获取客户分析数据

        委托给客户分析服务处理.

        Args:
            time_period_months: 分析时间段(月)

        Returns:
            CustomerAnalysis: 客户分析结果
        """
        try:
            return self._customer_analytics_service.get_customer_analysis(
                time_period_months
            )
        except Exception as e:
            self._logger.error(f"获取客户分析失败: {e}")
            raise ServiceError(f"获取客户分析失败: {e}", "AnalyticsService") from e

    def get_supplier_analysis(self, time_period_months: int = 12) -> SupplierAnalysis:
        """
        获取供应商分析数据

        委托给供应商分析服务处理.

        Args:
            time_period_months: 分析时间段(月)

        Returns:
            SupplierAnalysis: 供应商分析结果
        """
        try:
            return self._supplier_analytics_service.get_supplier_analysis(
                time_period_months
            )
        except Exception as e:
            self._logger.error(f"获取供应商分析失败: {e}")
            raise ServiceError(f"获取供应商分析失败: {e}", "AnalyticsService") from e

    def get_business_trend_analysis(self, metric: str, period: str) -> TrendAnalysis:
        """
        获取业务趋势分析

        委托给趋势分析服务处理.

        Args:
            metric: 指标名称
            period: 时间周期

        Returns:
            TrendAnalysis: 趋势分析结果
        """
        try:
            return self._trend_analysis_service.get_business_trend_analysis(
                metric, period
            )
        except Exception as e:
            self._logger.error(f"获取趋势分析失败: {e}")
            raise ServiceError(f"获取趋势分析失败: {e}", "AnalyticsService") from e

    def get_prediction(
        self, metric: str, prediction_months: int = 6
    ) -> PredictionResult:
        """
        获取业务预测

        委托给预测服务处理.

        Args:
            metric: 预测指标
            prediction_months: 预测月数

        Returns:
            PredictionResult: 预测结果
        """
        try:
            return self._prediction_service.get_prediction(metric, prediction_months)
        except Exception as e:
            self._logger.error(f"获取预测分析失败: {e}")
            raise ServiceError(f"获取预测分析失败: {e}", "AnalyticsService") from e

    def clear_cache(self, pattern: str | None = None) -> None:
        """
        清除缓存

        Args:
            pattern: 缓存键模式,如果为None则清除所有缓存
        """
        self._cache_manager.clear(pattern)
        self._logger.info(f"缓存清理完成: {pattern or '全部'}")

    def get_cache_statistics(self) -> dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            Dict[str, Any]: 缓存统计数据
        """
        return self._cache_manager.get_statistics()

    def get_financial_risk_analysis(self) -> dict[str, Any]:
        """
        获取财务风险分析

        委托给财务风险服务处理.

        Returns:
            Dict[str, Any]: 财务风险分析结果
        """
        try:
            return self._financial_risk_service.get_comprehensive_risk_analysis()
        except Exception as e:
            self._logger.error(f"获取财务风险分析失败: {e}")
            raise ServiceError(f"获取财务风险分析失败: {e}", "AnalyticsService") from e

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
            return self._financial_risk_service.update_risk_thresholds(
                threshold_updates
            )
        except Exception as e:
            self._logger.error(f"更新风险阈值失败: {e}")
            return False

    def get_risk_thresholds(self) -> dict[str, dict[str, float]]:
        """
        获取当前风险阈值配置

        Returns:
            Dict[str, Dict[str, float]]: 风险阈值配置
        """
        try:
            return self._financial_risk_service.get_risk_thresholds()
        except Exception as e:
            self._logger.error(f"获取风险阈值失败: {e}")
            return {}

    def cleanup(self) -> None:
        """清理服务资源"""
        self._cache_manager.clear()
        self._logger.debug("数据分析服务资源清理完成")

    # 兼容性方法 - 保持向后兼容
    def get_trend_analysis(self, metric: str, period: str) -> dict[str, Any]:
        """
        获取趋势分析(兼容性方法)

        Args:
            metric: 指标名称
            period: 时间周期

        Returns:
            Dict[str, Any]: 趋势分析数据
        """
        try:
            trend_analysis = self.get_business_trend_analysis(metric, period)

            # 转换为字典格式以保持兼容性
            return {
                "metric_name": trend_analysis.metric_name,
                "period": trend_analysis.period,
                "data_points": trend_analysis.data_points,
                "trend_direction": trend_analysis.trend_direction,
                "growth_rate": trend_analysis.growth_rate,
                "prediction": trend_analysis.prediction,
            }
        except Exception as e:
            self._logger.error(f"获取趋势分析失败: {e}")
            raise ServiceError(f"获取趋势分析失败: {e}", "AnalyticsService") from e
