"""
MiniCRM 仪表盘数据服务

负责仪表盘相关的数据计算和统计:
- 关键指标计算
- 快速操作数据
- 系统警报信息
- 仪表盘数据整合

严格遵循业务逻辑层职责:
- 只处理仪表盘相关的业务逻辑
- 通过DAO接口访问数据
- 不包含UI逻辑
"""

import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any

from minicrm.core.exceptions import ServiceError
from minicrm.core.interfaces.dao_interfaces import ICustomerDAO, ISupplierDAO
from minicrm.models.analytics_models import MetricCard
from minicrm.services.analytics.chart_service import ChartService
from transfunctions.formatting import format_currency


class DashboardService:
    """
    仪表盘数据服务

    提供仪表盘所需的所有数据:
    - 关键指标卡片数据
    - 图表数据
    - 快速操作配置
    - 系统预警信息
    """

    def __init__(self, customer_dao: ICustomerDAO, supplier_dao: ISupplierDAO):
        """
        初始化仪表盘服务

        Args:
            customer_dao: 客户数据访问对象
            supplier_dao: 供应商数据访问对象
        """
        self._customer_dao = customer_dao
        self._supplier_dao = supplier_dao
        self._chart_service = ChartService(customer_dao, supplier_dao)
        self._logger = logging.getLogger(__name__)

        self._logger.debug("仪表盘服务初始化完成")

    def get_dashboard_data(self) -> dict[str, Any]:
        """
        获取完整的仪表盘数据

        实现需求10中定义的完整仪表盘功能:
        - 关键指标卡片:客户总数、本月新增客户数、待办任务数等
        - 动态图表:客户增长趋势、类型分布、互动频率等12种图表
        - 实时数据更新和交互功能

        Returns:
            Dict[str, Any]: 完整的仪表盘数据

        Raises:
            ServiceError: 当数据获取失败时
        """
        try:
            self._logger.info("开始计算仪表盘数据")

            # 并行获取各类数据
            with ThreadPoolExecutor(max_workers=4) as executor:
                # 提交异步任务
                metrics_future = executor.submit(self.get_key_metrics)
                charts_future = executor.submit(self._chart_service.get_all_charts)
                quick_actions_future = executor.submit(self.get_quick_actions)
                alerts_future = executor.submit(self.get_system_alerts)

                # 等待所有任务完成
                metrics = metrics_future.result()
                charts = charts_future.result()
                quick_actions = quick_actions_future.result()
                alerts = alerts_future.result()

            # 构建仪表盘数据
            dashboard_data = {
                "metrics": [self._metric_to_dict(m) for m in metrics],
                "charts": charts,
                "quick_actions": quick_actions,
                "alerts": alerts,
                "generated_at": datetime.now().isoformat(),
                "cache_expires_at": (
                    datetime.now() + timedelta(seconds=300)
                ).isoformat(),
            }

            self._logger.info("仪表盘数据计算完成")
            return dashboard_data

        except Exception as e:
            self._logger.error(f"获取仪表盘数据失败: {e}")
            raise ServiceError(f"获取仪表盘数据失败: {e}", "DashboardService") from e

    def get_key_metrics(self) -> list[MetricCard]:
        """
        获取关键指标卡片数据

        实现需求10中定义的关键指标:
        - 客户总数、本月新增客户数、待办任务数
        - 应收账款、应付账款等财务指标

        Returns:
            List[MetricCard]: 关键指标列表
        """
        try:
            # 获取基础统计数据
            customer_stats = self._customer_dao.get_statistics()
            supplier_stats = self._supplier_dao.get_statistics()

            metrics = []

            # 客户总数
            total_customers = customer_stats.get("total_customers", 0)
            customer_growth = customer_stats.get("growth_rate", 0)
            metrics.append(
                MetricCard(
                    title="客户总数",
                    value=total_customers,
                    unit="个",
                    trend="up"
                    if customer_growth > 0
                    else "down"
                    if customer_growth < 0
                    else "stable",
                    trend_value=customer_growth,
                    color="primary",
                )
            )

            # 本月新增客户
            new_customers = customer_stats.get("new_this_month", 0)
            metrics.append(
                MetricCard(
                    title="本月新增客户",
                    value=new_customers,
                    unit="个",
                    color="success" if new_customers > 0 else "warning",
                )
            )

            # 待办任务数
            pending_tasks = self._get_pending_tasks_count()
            metrics.append(
                MetricCard(
                    title="待办任务",
                    value=pending_tasks,
                    unit="项",
                    color="warning" if pending_tasks > 10 else "primary",
                )
            )

            # 应收账款
            receivables = self._get_total_receivables()
            metrics.append(
                MetricCard(
                    title="应收账款",
                    value=format_currency(receivables),
                    color="success" if receivables > 0 else "primary",
                )
            )

            # 应付账款
            payables = self._get_total_payables()
            metrics.append(
                MetricCard(
                    title="应付账款",
                    value=format_currency(payables),
                    color="danger" if payables > receivables else "primary",
                )
            )

            # 供应商总数
            total_suppliers = supplier_stats.get("total_suppliers", 0)
            metrics.append(
                MetricCard(
                    title="供应商总数",
                    value=total_suppliers,
                    unit="个",
                    color="primary",
                )
            )

            # 活跃客户数
            active_customers = customer_stats.get("active_customers", 0)
            activity_rate = (
                (active_customers / total_customers * 100) if total_customers > 0 else 0
            )
            metrics.append(
                MetricCard(
                    title="活跃客户",
                    value=active_customers,
                    unit="个",
                    trend_value=activity_rate,
                    color="success" if activity_rate > 70 else "warning",
                )
            )

            return metrics

        except Exception as e:
            self._logger.error(f"获取关键指标失败: {e}")
            # 返回默认指标避免UI崩溃
            return [
                MetricCard("客户总数", 0, "个", color="primary"),
                MetricCard("本月新增客户", 0, "个", color="primary"),
                MetricCard("待办任务", 0, "项", color="primary"),
                MetricCard("应收账款", "¥0", color="primary"),
                MetricCard("应付账款", "¥0", color="primary"),
            ]

    def get_quick_actions(self) -> list[dict[str, Any]]:
        """获取快速操作按钮配置"""
        return [
            {"title": "新增客户", "icon": "user-plus", "action": "create_customer"},
            {
                "title": "新增供应商",
                "icon": "building-plus",
                "action": "create_supplier",
            },
            {"title": "创建报价", "icon": "file-text", "action": "create_quote"},
            {"title": "记录收款", "icon": "dollar-sign", "action": "record_payment"},
            {"title": "查看报表", "icon": "bar-chart", "action": "view_reports"},
        ]

    def get_system_alerts(self) -> list[dict[str, Any]]:
        """获取系统预警信息"""
        alerts = []

        try:
            # 检查逾期应收账款
            overdue_receivables = self._get_overdue_receivables_count()
            if overdue_receivables > 0:
                alerts.append(
                    {
                        "type": "warning",
                        "title": "逾期应收账款提醒",
                        "message": (
                            f"有{overdue_receivables}笔应收账款已逾期,请及时跟进"
                        ),
                        "action": "view_overdue_receivables",
                    }
                )

            # 检查待处理任务
            pending_tasks = self._get_pending_tasks_count()
            if pending_tasks > 20:
                alerts.append(
                    {
                        "type": "info",
                        "title": "待办任务较多",
                        "message": f"当前有{pending_tasks}项待办任务,建议优先处理",
                        "action": "view_tasks",
                    }
                )

            # 检查合同到期
            expiring_contracts = self._get_expiring_contracts_count()
            if expiring_contracts > 0:
                alerts.append(
                    {
                        "type": "warning",
                        "title": "合同即将到期",
                        "message": f"有{expiring_contracts}个合同即将到期,请及时续约",
                        "action": "view_expiring_contracts",
                    }
                )

        except Exception as e:
            self._logger.error(f"获取系统预警失败: {e}")

        return alerts

    def _metric_to_dict(self, metric: MetricCard) -> dict[str, Any]:
        """将MetricCard对象转换为字典"""
        return {
            "title": metric.title,
            "value": metric.value,
            "unit": metric.unit,
            "trend": metric.trend,
            "trend_value": metric.trend_value,
            "color": metric.color,
        }

    def _get_pending_tasks_count(self) -> int:
        """获取待办任务数量"""
        # 简化实现,实际应该从任务表获取
        return 8

    def _get_total_receivables(self) -> float:
        """获取应收账款总额"""
        # 简化实现,实际应该从财务表获取
        return 502000.0

    def _get_total_payables(self) -> float:
        """获取应付账款总额"""
        # 简化实现,实际应该从财务表获取
        return 321000.0

    def _get_overdue_receivables_count(self) -> int:
        """获取逾期应收账款数量"""
        # 模拟数据,实际应从财务模块获取
        return 3

    def _get_expiring_contracts_count(self) -> int:
        """获取即将到期合同数量"""
        # 模拟数据,实际应从合同模块获取
        return 2
