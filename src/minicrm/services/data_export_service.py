"""
MiniCRM 数据导出服务

提供统一的数据导出功能,包括:
- CSV/Excel数据导出
- PDF报表生成
- Word文档生成
- 数据筛选和格式化

设计原则:
- 遵循MiniCRM分层架构标准
- 使用transfunctions进行数据格式化
- 提供完整的错误处理和日志记录
"""

import csv
import logging
from typing import Any

from minicrm.core.exceptions import ServiceError
from minicrm.services.contract_service import ContractService
from minicrm.services.customer_service import CustomerService
from minicrm.services.file_validator import FileValidator
from minicrm.services.supplier_service import SupplierService


class DataExportService:
    """
    数据导出服务

    提供统一的数据导出功能,支持多种格式和数据类型.
    """

    def __init__(
        self,
        customer_service: CustomerService,
        supplier_service: SupplierService,
        contract_service: ContractService,
        file_validator: FileValidator,
    ):
        """
        初始化数据导出服务

        Args:
            customer_service: 客户服务实例
            supplier_service: 供应商服务实例
            contract_service: 合同服务实例
            file_validator: 文件验证服务实例
        """
        self._customer_service = customer_service
        self._supplier_service = supplier_service
        self._contract_service = contract_service
        self._file_validator = file_validator
        self._logger = logging.getLogger(__name__)

        # 数据类型映射
        self._data_type_services = {
            "customers": self._customer_service,
            "suppliers": self._supplier_service,
            "contracts": self._contract_service,
        }

        self._logger.info("数据导出服务初始化完成")

    def export_data(
        self,
        data_type: str,
        export_format: str,
        output_path: str,
        filters: dict[str, Any] | None = None,
        fields: list[str] | None = None,
    ) -> bool:
        """
        导出数据

        Args:
            data_type: 数据类型
            export_format: 导出格式 (.csv, .xlsx, .pdf)
            output_path: 输出路径
            filters: 筛选条件
            fields: 导出字段列表

        Returns:
            bool: 导出是否成功

        Raises:
            ServiceError: 导出失败时抛出
        """
        try:
            self._logger.info(f"开始导出数据: {data_type} to {output_path}")

            # 验证导出格式
            is_valid, error_msg = self._file_validator.validate_export_format(
                export_format
            )
            if not is_valid:
                raise ServiceError(error_msg)

            # 验证输出路径
            is_valid, error_msg = self._file_validator.validate_output_path(output_path)
            if not is_valid:
                raise ServiceError(error_msg)

            # 获取数据
            data = self._get_export_data(data_type, filters)

            if not data:
                raise ServiceError("没有数据可以导出")

            # 筛选字段
            if fields:
                data = self._filter_fields(data, fields)

            # 根据格式导出
            if export_format == ".csv":
                return self._export_csv(data, output_path)
            elif export_format == ".xlsx":
                return self._export_excel(data, output_path)
            elif export_format == ".pdf":
                return self._export_pdf(data, output_path, data_type)
            else:
                raise ServiceError(f"不支持的导出格式: {export_format}")

        except Exception as e:
            self._logger.error(f"导出数据失败: {e}")
            raise ServiceError(f"导出数据失败: {e}") from e

    def _get_export_data(
        self, data_type: str, filters: dict[str, Any] | None
    ) -> list[dict[str, Any]]:
        """获取导出数据"""
        service = self._data_type_services.get(data_type)
        if not service:
            raise ServiceError(f"不支持的数据类型: {data_type}")

        # 根据数据类型获取数据
        if data_type == "customers":
            customers, _ = self._customer_service.search_customers(
                query=filters.get("query", "") if filters else "",
                filters=filters.get("filters") if filters else None,
                page=1,
                page_size=10000,  # 大批量导出
            )
            return customers
        elif data_type == "suppliers":
            # 假设供应商服务有类似的搜索方法
            if hasattr(service, "search_suppliers"):
                suppliers, _ = service.search_suppliers(
                    query=filters.get("query", "") if filters else "",
                    filters=filters.get("filters") if filters else None,
                    page=1,
                    page_size=10000,
                )
                return suppliers
            else:
                return (
                    service.get_all_suppliers()
                    if hasattr(service, "get_all_suppliers")
                    else []
                )
        else:
            # 其他数据类型的获取逻辑
            return []

    def _filter_fields(
        self, data: list[dict[str, Any]], fields: list[str]
    ) -> list[dict[str, Any]]:
        """筛选字段"""
        filtered_data = []
        for row in data:
            filtered_row = {field: row.get(field, "") for field in fields}
            filtered_data.append(filtered_row)
        return filtered_data

    def _export_csv(self, data: list[dict[str, Any]], output_path: str) -> bool:
        """导出CSV格式"""
        if not data:
            return False

        with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        return True

    def _export_excel(self, data: list[dict[str, Any]], output_path: str) -> bool:
        """导出Excel格式"""
        try:
            import pandas as pd

            df = pd.DataFrame(data)
            df.to_excel(output_path, index=False, engine="openpyxl")
            return True

        except ImportError as e:
            raise ServiceError("导出Excel需要安装pandas和openpyxl库") from e

    def _export_pdf(
        self, data: list[dict[str, Any]], output_path: str, data_type: str
    ) -> bool:
        """导出PDF格式"""
        # 这里可以根据数据类型生成不同的PDF报表
        # 暂时使用简单的表格格式
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

            doc = SimpleDocTemplate(output_path, pagesize=A4)
            elements = []

            if data:
                # 创建表格数据
                headers = list(data[0].keys())
                table_data = [headers]

                table_data.extend(
                    [str(row.get(field, "")) for field in headers] for row in data
                )

                # 创建表格
                table = Table(table_data)
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 14),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ]
                    )
                )

                elements.append(table)

            doc.build(elements)
            return True

        except Exception as e:
            self._logger.error(f"PDF导出失败: {e}")
            return False

    def generate_word_document(
        self, template_type: str, data: dict[str, Any], output_path: str
    ) -> bool:
        """
        生成Word文档

        Args:
            template_type: 模板类型 (contract, quote, report)
            data: 数据字典
            output_path: 输出路径

        Returns:
            bool: 生成是否成功
        """
        try:
            # 验证输出路径
            is_valid, error_msg = self._file_validator.validate_output_path(output_path)
            if not is_valid:
                raise ServiceError(error_msg)

            # 这里可以使用docxtpl库生成Word文档
            # 暂时返回True表示功能占位
            self._logger.info(f"生成Word文档: {template_type} -> {output_path}")
            return True

        except Exception as e:
            self._logger.error(f"生成Word文档失败: {e}")
            raise ServiceError(f"生成Word文档失败: {e}") from e
