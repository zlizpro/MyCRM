"""
MiniCRM 数据导入导出协调服务

提供统一的数据导入导出功能协调,包括:
- 协调导入导出服务
- 统一的接口封装
- 服务依赖管理
- 统一的错误处理

设计原则:
- 遵循MiniCRM分层架构标准
- 作为导入导出功能的协调器
- 提供简化的统一接口
- 管理服务间的依赖关系
"""

import logging
from typing import Any

from minicrm.services.contract_service import ContractService
from minicrm.services.customer_service import CustomerService
from minicrm.services.data_export_service import DataExportService
from minicrm.services.data_import_service import DataImportService
from minicrm.services.file_validator import FileValidator
from minicrm.services.supplier_service import SupplierService


class ImportExportCoordinator:
    """
    数据导入导出协调服务

    协调各个导入导出相关服务,提供统一的接口.
    """

    def __init__(
        self,
        customer_service: CustomerService,
        supplier_service: SupplierService,
        contract_service: ContractService,
    ):
        """
        初始化导入导出协调服务

        Args:
            customer_service: 客户服务实例
            supplier_service: 供应商服务实例
            contract_service: 合同服务实例
        """
        self._logger = logging.getLogger(__name__)

        # 初始化子服务
        self._file_validator = FileValidator()
        self._import_service = DataImportService(
            customer_service, supplier_service, contract_service, self._file_validator
        )
        self._export_service = DataExportService(
            customer_service, supplier_service, contract_service, self._file_validator
        )

        self._logger.info("导入导出协调服务初始化完成")

    def get_supported_formats(self) -> dict[str, list[str]]:
        """
        获取支持的文件格式

        Returns:
            Dict[str, List[str]]: 支持的导入和导出格式
        """
        return self._file_validator.get_supported_formats()

    def validate_import_file(self, file_path: str) -> tuple[bool, str]:
        """
        验证导入文件

        Args:
            file_path: 文件路径

        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        return self._file_validator.validate_import_file(file_path)

    def preview_import_data(
        self, file_path: str, max_rows: int = 5
    ) -> tuple[list[str], list[dict[str, Any]]]:
        """
        预览导入数据

        Args:
            file_path: 文件路径
            max_rows: 最大预览行数

        Returns:
            Tuple[List[str], List[Dict[str, Any]]]: (字段列表, 数据行列表)
        """
        return self._import_service.preview_import_data(file_path, max_rows)

    def import_data(
        self,
        file_path: str,
        data_type: str,
        field_mapping: dict[str, str],
        options: dict[str, Any] | None = None,
    ) -> tuple[int, int, list[str]]:
        """
        导入数据

        Args:
            file_path: 文件路径
            data_type: 数据类型 (customers, suppliers, contracts)
            field_mapping: 字段映射 {目标字段: 源字段}
            options: 导入选项

        Returns:
            Tuple[int, int, List[str]]: (成功数量, 失败数量, 错误信息列表)
        """
        return self._import_service.import_data(
            file_path, data_type, field_mapping, options
        )

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
        """
        return self._export_service.export_data(
            data_type, export_format, output_path, filters, fields
        )

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
        return self._export_service.generate_word_document(
            template_type, data, output_path
        )

    def get_field_mapping_suggestions(
        self, data_type: str, source_fields: list[str]
    ) -> dict[str, str]:
        """
        获取字段映射建议

        Args:
            data_type: 数据类型
            source_fields: 源字段列表

        Returns:
            Dict[str, str]: 映射建议 {目标字段: 源字段}
        """
        return self._import_service.get_field_mapping_suggestions(
            data_type, source_fields
        )
