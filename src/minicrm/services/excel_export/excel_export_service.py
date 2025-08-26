"""
Excel导出服务协调器

作为Excel导出功能的主要协调器,负责:
- 协调各种专门的导出器
- 提供统一的导出接口
- 管理批量导出任务
- 处理导出配置和错误

设计原则:
- 协调器模式:委托给专门的导出器
- 统一接口:保持向后兼容
- 错误处理:统一的异常处理和日志记录
"""

import logging
from typing import Any

from minicrm.core.exceptions import ServiceError

from .customer_excel_exporter import CustomerExcelExporter
from .financial_excel_exporter import FinancialExcelExporter
from .supplier_excel_exporter import SupplierExcelExporter


class ExcelExportService:
    """
    Excel导出服务协调器

    负责协调各种Excel导出功能,提供统一的导出接口.
    """

    def __init__(self):
        """初始化Excel导出服务协调器"""
        self._logger = logging.getLogger(__name__)

        # 初始化专门的导出器
        self._customer_exporter = CustomerExcelExporter()
        self._supplier_exporter = SupplierExcelExporter()
        self._financial_exporter = FinancialExcelExporter()

        self._logger.info("Excel导出服务协调器初始化完成")

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
        try:
            return self._customer_exporter.export_customer_data(
                customers, output_path, include_analysis
            )
        except Exception as e:
            self._logger.error(f"客户数据导出失败: {e}")
            raise ServiceError(f"客户数据导出失败: {e}", "ExcelExportService") from e

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
        try:
            return self._supplier_exporter.export_supplier_data(suppliers, output_path)
        except Exception as e:
            self._logger.error(f"供应商数据导出失败: {e}")
            raise ServiceError(f"供应商数据导出失败: {e}", "ExcelExportService") from e

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
        try:
            return self._financial_exporter.export_financial_report(
                financial_data, output_path
            )
        except Exception as e:
            self._logger.error(f"财务报表导出失败: {e}")
            raise ServiceError(f"财务报表导出失败: {e}", "ExcelExportService") from e

    def export_batch_data(
        self, export_configs: list[dict[str, Any]]
    ) -> dict[str, bool]:
        """
        批量导出数据

        Args:
            export_configs: 导出配置列表,每个配置包含:
                - type: 导出类型 (customer/supplier/financial)
                - data: 导出数据
                - output_path: 输出路径

        Returns:
            Dict[str, bool]: 各导出任务的结果
        """
        results = {}

        try:
            self._logger.info(f"开始批量导出{len(export_configs)}个数据文件")

            for i, config in enumerate(export_configs):
                export_type = config.get("type", "customer")
                data = config.get("data", [])
                output_path = config.get("output_path", "")

                task_key = f"task_{i}_{export_type}"

                try:
                    if export_type == "customer":
                        success = self.export_customer_data(data, output_path)
                    elif export_type == "supplier":
                        success = self.export_supplier_data(data, output_path)
                    elif export_type == "financial":
                        success = self.export_financial_report(data, output_path)
                    else:
                        self._logger.warning(f"未知的导出类型: {export_type}")
                        success = False

                    results[task_key] = success

                    if success:
                        self._logger.info(f"批量导出任务 {task_key} 成功")
                    else:
                        self._logger.warning(f"批量导出任务 {task_key} 失败")

                except Exception as e:
                    self._logger.error(f"批量导出任务 {task_key} 异常: {e}")
                    results[task_key] = False

            successful_tasks = sum(1 for success in results.values() if success)
            self._logger.info(
                f"批量导出完成: {successful_tasks}/{len(export_configs)} 个任务成功"
            )

            return results

        except Exception as e:
            self._logger.error(f"批量导出失败: {e}")
            raise ServiceError(f"批量导出失败: {e}", "ExcelExportService") from e

    def get_export_status(self) -> dict[str, Any]:
        """
        获取导出服务状态

        Returns:
            Dict[str, Any]: 服务状态信息
        """
        return {
            "service_name": "ExcelExportService",
            "version": "2.0.0",
            "exporters": {
                "customer_exporter": "available",
                "supplier_exporter": "available",
                "financial_exporter": "available",
            },
            "supported_formats": ["xlsx", "csv"],
            "features": [
                "customer_data_export",
                "supplier_data_export",
                "financial_report_export",
                "batch_export",
                "analysis_reports",
                "multiple_formats",
            ],
        }

    def validate_export_config(self, config: dict[str, Any]) -> bool:
        """
        验证导出配置

        Args:
            config: 导出配置

        Returns:
            bool: 配置是否有效
        """
        try:
            required_fields = ["type", "data", "output_path"]

            for field in required_fields:
                if field not in config:
                    self._logger.error(f"导出配置缺少必需字段: {field}")
                    return False

            export_type = config.get("type")
            if export_type not in ["customer", "supplier", "financial"]:
                self._logger.error(f"不支持的导出类型: {export_type}")
                return False

            output_path = config.get("output_path", "")
            if not output_path:
                self._logger.error("输出路径不能为空")
                return False

            return True

        except Exception as e:
            self._logger.error(f"验证导出配置失败: {e}")
            return False
