"""
MiniCRM 图表数据服务

负责生成各种图表数据:
- 客户相关图表
- 供应商相关图表
- 财务相关图表
- 业务统计图表
"""

import logging
from typing import Any

from minicrm.core.interfaces.dao_interfaces import ICustomerDAO, ISupplierDAO


class ChartService:
    """
    图表数据服务

    提供仪表盘所需的各种图表数据.
    """

    def __init__(self, customer_dao: ICustomerDAO, supplier_dao: ISupplierDAO):
        """
        初始化图表服务

        Args:
            customer_dao: 客户数据访问对象
            supplier_dao: 供应商数据访问对象
        """
        self._customer_dao = customer_dao
        self._supplier_dao = supplier_dao
        self._logger = logging.getLogger(__name__)

        self._logger.debug("图表服务初始化完成")

    def get_all_charts(self) -> dict[str, Any]:
        """
        获取所有图表数据

        Returns:
            Dict[str, Any]: 所有图表数据
        """
        try:
            charts = {
                "customer_growth": self._get_customer_growth_chart(),
                "customer_types": self._get_customer_types_chart(),
                "monthly_interactions": self._get_monthly_interactions_chart(),
                "receivables_status": self._get_receivables_status_chart(),
                "supplier_distribution": self._get_supplier_distribution_chart(),
                "supplier_quality": self._get_supplier_quality_chart(),
            }

            return charts

        except Exception as e:
            self._logger.error(f"获取图表数据失败: {e}")
            return {}

    def _get_customer_growth_chart(self) -> dict[str, Any]:
        """获取客户增长图表数据"""
        return {
            "type": "line",
            "title": "客户增长趋势",
            "labels": ["1月", "2月", "3月", "4月", "5月", "6月"],
            "data": [120, 132, 145, 151, 156, 162],
        }

    def _get_customer_types_chart(self) -> dict[str, Any]:
        """获取客户类型分布图表数据"""
        return {
            "type": "pie",
            "title": "客户类型分布",
            "labels": ["VIP客户", "重要客户", "普通客户", "潜在客户"],
            "data": [25, 38, 68, 25],
        }

    def _get_monthly_interactions_chart(self) -> dict[str, Any]:
        """获取月度互动频率图表数据"""
        return {
            "type": "bar",
            "title": "月度互动频率",
            "labels": ["1月", "2月", "3月", "4月", "5月", "6月"],
            "data": [85, 92, 78, 105, 98, 112],
        }

    def _get_receivables_status_chart(self) -> dict[str, Any]:
        """获取应收账款状态图表数据"""
        return {
            "type": "bar",
            "title": "应收账款状态",
            "labels": ["正常", "逾期30天内", "逾期30-60天", "逾期60天以上"],
            "data": [457000, 25000, 15000, 5000],
        }

    def _get_supplier_distribution_chart(self) -> dict[str, Any]:
        """获取供应商分布图表数据"""
        return {
            "type": "bar",
            "title": "供应商地区分布",
            "labels": ["华东", "华南", "华北", "西南", "其他"],
            "data": [25, 18, 15, 8, 4],
        }

    def _get_supplier_quality_chart(self) -> dict[str, Any]:
        """获取供应商质量分布图表数据"""
        return {
            "type": "doughnut",
            "title": "供应商质量分布",
            "labels": ["优秀", "良好", "一般", "需改进"],
            "data": [12, 28, 15, 5],
        }
