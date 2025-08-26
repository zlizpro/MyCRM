"""
MiniCRM 数据导入服务

提供统一的数据导入功能,包括:
- CSV/Excel数据读取
- 数据预览和字段映射
- 数据验证和批量导入
- 进度跟踪和错误处理

设计原则:
- 遵循MiniCRM分层架构标准
- 使用transfunctions进行数据验证
- 提供完整的错误处理和日志记录
"""

import csv
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from minicrm.core.exceptions import ServiceError
from minicrm.services.contract_service import ContractService
from minicrm.services.customer_service import CustomerService
from minicrm.services.file_validator import FileValidator
from minicrm.services.supplier_service import SupplierService
from transfunctions import (
    validate_customer_data,
    validate_supplier_data,
)
from transfunctions.validation import ValidationResult


class DataImportService:
    """
    数据导入服务

    提供统一的数据导入功能,支持多种格式和数据类型.
    """

    def __init__(
        self,
        customer_service: CustomerService,
        supplier_service: SupplierService,
        contract_service: ContractService,
        file_validator: FileValidator,
    ):
        """
        初始化数据导入服务

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

        self._logger.info("数据导入服务初始化完成")

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

        Raises:
            ServiceError: 预览失败时抛出
        """
        try:
            # 验证文件
            is_valid, error_msg = self._file_validator.validate_import_file(file_path)
            if not is_valid:
                raise ServiceError(f"文件验证失败: {error_msg}")

            file_ext = Path(file_path).suffix.lower()

            if file_ext == ".csv":
                return self._preview_csv_data(file_path, max_rows)
            elif file_ext == ".xlsx":
                return self._preview_excel_data(file_path, max_rows)
            else:
                raise ServiceError(f"不支持预览的文件格式: {file_ext}")

        except Exception as e:
            self._logger.error(f"预览导入数据失败: {e}")
            raise ServiceError(f"预览导入数据失败: {e}") from e

    def _preview_csv_data(
        self, file_path: str, max_rows: int
    ) -> tuple[list[str], list[dict[str, Any]]]:
        """预览CSV数据"""
        with open(file_path, encoding="utf-8-sig") as file:
            # 自动检测分隔符
            sample = file.read(1024)
            file.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter

            reader = csv.DictReader(file, delimiter=delimiter)
            headers = list(reader.fieldnames or [])

            data_rows = []
            for i, row in enumerate(reader):
                if i >= max_rows:
                    break
                data_rows.append(dict(row))

            return headers, data_rows

    def _preview_excel_data(
        self, file_path: str, max_rows: int
    ) -> tuple[list[str], list[dict[str, Any]]]:
        """预览Excel数据"""

        df = pd.read_excel(file_path, nrows=max_rows)
        headers = df.columns.tolist()
        data_rows = df.to_dict("records")

        return headers, data_rows

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

        Raises:
            ServiceError: 导入失败时抛出
        """
        try:
            self._logger.info(f"开始导入数据: {data_type} from {file_path}")

            # 验证数据类型
            if data_type not in self._data_type_services:
                raise ServiceError(f"不支持的数据类型: {data_type}")

            # 验证文件
            is_valid, error_msg = self._file_validator.validate_import_file(file_path)
            if not is_valid:
                raise ServiceError(f"文件验证失败: {error_msg}")

            # 读取文件数据
            file_ext = Path(file_path).suffix.lower()
            if file_ext == ".csv":
                raw_data = self._read_csv_data(file_path)
            elif file_ext == ".xlsx":
                raw_data = self._read_excel_data(file_path)
            else:
                raise ServiceError(f"不支持的文件格式: {file_ext}")

            # 映射字段
            mapped_data = self._map_fields(raw_data, field_mapping)

            # 导入数据
            return self._import_mapped_data(data_type, mapped_data, options or {})

        except Exception as e:
            self._logger.error(f"导入数据失败: {e}")
            raise ServiceError(f"导入数据失败: {e}") from e

    def _read_csv_data(self, file_path: str) -> list[dict[str, Any]]:
        """读取CSV数据"""
        with open(file_path, encoding="utf-8-sig") as file:
            sample = file.read(1024)
            file.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter

            reader = csv.DictReader(file, delimiter=delimiter)
            return list(reader)

    def _read_excel_data(self, file_path: str) -> list[dict[str, Any]]:
        """读取Excel数据"""

        df = pd.read_excel(file_path)
        # 处理NaN值
        df = df.fillna("")
        return df.to_dict("records")

    def _map_fields(
        self, raw_data: list[dict[str, Any]], field_mapping: dict[str, str]
    ) -> list[dict[str, Any]]:
        """映射字段并进行数据格式化"""
        mapped_data = []

        for row in raw_data:
            mapped_row = {}
            for target_field, source_field in field_mapping.items():
                if source_field and source_field in row:
                    value = row[source_field]

                    # 格式化字段值
                    formatted_value = self._format_field_value(target_field, value)
                    mapped_row[target_field] = formatted_value

            # 只保留有效数据行
            if any(mapped_row.values()):
                mapped_data.append(mapped_row)

        return mapped_data

    def _import_mapped_data(
        self, data_type: str, mapped_data: list[dict[str, Any]], options: dict[str, Any]
    ) -> tuple[int, int, list[str]]:
        """导入映射后的数据"""
        success_count = 0
        error_count = 0
        error_messages = []

        # TODO: 实现重复数据处理和更新逻辑
        # skip_duplicates = options.get("skip_duplicates", True)
        # update_existing = options.get("update_existing", False)

        for i, row_data in enumerate(mapped_data):
            try:
                # 验证数据
                validation_result = self._validate_row_data(data_type, row_data)
                if not validation_result.is_valid:
                    errors_str = ", ".join(validation_result.errors)
                    error_msg = f"第{i + 1}行数据验证失败: {errors_str}"
                    error_messages.append(error_msg)
                    error_count += 1
                    continue

                # 创建记录
                record_id = self._create_record_by_type(data_type, row_data)
                if record_id:
                    success_count += 1
                else:
                    error_count += 1
                    error_messages.append(f"第{i + 1}行数据创建失败")

            except Exception as e:
                error_count += 1
                error_messages.append(f"第{i + 1}行处理失败: {e}")

        self._logger.info(f"数据导入完成: 成功{success_count}条, 失败{error_count}条")
        return success_count, error_count, error_messages

    def _validate_row_data(
        self, data_type: str, row_data: dict[str, Any]
    ) -> ValidationResult:
        """验证单行数据"""
        if data_type == "customers":
            return validate_customer_data(row_data)
        elif data_type == "suppliers":
            return validate_supplier_data(row_data)
        else:
            return self._basic_validation(row_data)

    def _create_record_by_type(
        self, data_type: str, row_data: dict[str, Any]
    ) -> int | None:
        """根据数据类型创建记录"""
        if data_type == "customers":
            return self._customer_service.create_customer(row_data)
        elif data_type == "suppliers":
            return self._create_supplier_record(row_data)
        else:
            service = self._data_type_services[data_type]
            return self._create_other_record(service, row_data)

    def _create_supplier_record(self, row_data: dict[str, Any]) -> int | None:
        """创建供应商记录"""
        if hasattr(self._supplier_service, "create_supplier"):
            return self._supplier_service.create_supplier(row_data)
        else:
            return self._create_other_record(self._supplier_service, row_data)

    def _basic_validation(self, data: dict[str, Any]) -> ValidationResult:
        """基本数据验证"""
        errors = []

        # 检查必要字段
        if not data.get("name"):
            errors.append("名称不能为空")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=[])

    def _create_other_record(self, service: Any, data: dict[str, Any]) -> int | None:
        """创建其他类型记录的通用方法"""
        # 这里可以根据具体的服务类型实现不同的创建逻辑
        if hasattr(service, "create"):
            return service.create(data)
        return None

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
        # 定义字段映射规则
        mapping_rules = {
            "customers": {
                "name": ["name", "客户名称", "公司名称", "名称", "company_name"],
                "contact_person": ["contact", "联系人", "姓名", "contact_person"],
                "phone": ["phone", "电话", "手机", "联系电话", "telephone"],
                "email": ["email", "邮箱", "邮件", "电子邮件"],
                "company": ["company", "公司", "企业", "单位"],
                "address": ["address", "地址", "联系地址"],
                "notes": ["notes", "备注", "说明", "描述", "remark"],
            },
            "suppliers": {
                "name": ["name", "供应商名称", "公司名称", "名称"],
                "contact_person": ["contact", "联系人", "姓名"],
                "phone": ["phone", "电话", "手机", "联系电话"],
                "email": ["email", "邮箱", "邮件"],
                "company": ["company", "公司", "企业"],
                "address": ["address", "地址"],
                "notes": ["notes", "备注", "说明"],
            },
        }

        suggestions = {}
        rules = mapping_rules.get(data_type, {})

        for target_field, patterns in rules.items():
            for pattern in patterns:
                for source_field in source_fields:
                    if pattern.lower() in source_field.lower():
                        suggestions[target_field] = source_field
                        break
                if target_field in suggestions:
                    break

        return suggestions

    def _format_field_value(self, field_name: str, value: Any) -> Any:
        """格式化字段值"""
        if not value:
            return value

        # 基本数据格式化
        if field_name == "phone" and value:
            # 清理电话号码格式
            phone_str = str(value).strip().replace("-", "").replace(" ", "")
            return phone_str
        elif field_name in ["amount", "price", "total"] and value:
            # 处理数值字段
            try:
                return float(str(value).replace(",", ""))
            except (ValueError, TypeError):
                return value
        elif field_name in ["date", "created_at", "updated_at"] and value:
            # 处理日期字段 - 保持字符串格式,后续可以进一步处理
            return str(value).strip()
        else:
            # 其他字段进行基本清理
            return str(value).strip() if value else value
