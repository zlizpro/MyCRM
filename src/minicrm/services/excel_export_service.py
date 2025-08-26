"""
MiniCRM Excel导出服务 (向后兼容接口)

这是Excel导出服务的向后兼容接口,内部委托给新的模块化实现.

新的模块化实现位于 excel_export/ 目录下:
- ExcelExportService: 主协调器
- CustomerExcelExporter: 客户数据导出
- SupplierExcelExporter: 供应商数据导出
- FinancialExcelExporter: 财务报表导出
- ExcelFormatters: 格式化器
- ExcelStatisticsCalculator: 统计计算器

此文件保持向后兼容,委托给新的实现.
"""

import logging
from typing import Any

from minicrm.services.excel_export.excel_export_service import (
    ExcelExportService as NewExcelExportService,
)


class ExcelExportService:
    """
    Excel导出服务 (向后兼容接口)

    委托给新的模块化实现,保持API兼容性.
    """

    def __init__(self):
        """初始化Excel导出服务"""
        self._logger = logging.getLogger(__name__)

        # 委托给新的实现
        self._service = NewExcelExportService()

        self._logger.info("Excel导出服务 (兼容接口) 初始化完成")

    def export_customer_data(
        self,
        customers: list[dict[str, Any]],
        output_path: str,
        include_analysis: bool = True,
    ) -> bool:
        """
        导出客户数据到Excel

        Args:
            customers: 客户数据列表
            output_path: 输出文件路径
            include_analysis: 是否包含分析数据

        Returns:
            bool: 导出是否成功
        """
        return self._service.export_customer_data(
            customers, output_path, include_analysis
        )

    def export_supplier_data(
        self, suppliers: list[dict[str, Any]], output_path: str
    ) -> bool:
        """
        导出供应商数据到Excel

        Args:
            suppliers: 供应商数据列表
            output_path: 输出文件路径

        Returns:
            bool: 导出是否成功
        """
        return self._service.export_supplier_data(suppliers, output_path)

    def export_financial_report(
        self, financial_data: dict[str, Any], output_path: str
    ) -> bool:
        """
        导出财务报表到Excel

        Args:
            financial_data: 财务数据
            output_path: 输出文件路径

        Returns:
            bool: 导出是否成功
        """
        return self._service.export_financial_report(financial_data, output_path)

    def export_batch_data(
        self, export_configs: list[dict[str, Any]]
    ) -> dict[str, bool]:
        """
        批量导出数据

        Args:
            export_configs: 导出配置列表

        Returns:
            Dict[str, bool]: 各导出任务的结果
        """
        return self._service.export_batch_data(export_configs)

    def get_export_status(self) -> dict[str, Any]:
        """
        获取导出服务状态

        Returns:
            Dict[str, Any]: 服务状态信息
        """
        return self._service.get_export_status()

    def validate_export_config(self, config: dict[str, Any]) -> bool:
        """
        验证导出配置

        Args:
            config: 导出配置

        Returns:
            bool: 配置是否有效
        """
        return self._service.validate_export_config(config)
