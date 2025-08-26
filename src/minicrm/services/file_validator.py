"""
MiniCRM 文件验证服务

提供统一的文件验证功能,包括:
- 文件格式验证
- 文件大小检查
- CSV/Excel文件结构验证
- 编码格式检查

设计原则:
- 遵循MiniCRM分层架构标准
- 提供完整的错误处理和日志记录
- 支持多种文件格式验证
"""

import csv
import logging
import os
from pathlib import Path


class FileValidator:
    """
    文件验证服务

    提供统一的文件验证功能,支持多种格式和验证规则.
    """

    def __init__(self):
        """初始化文件验证服务"""
        self._logger = logging.getLogger(__name__)

        # 支持的文件格式
        self._supported_import_formats = [".csv", ".xlsx"]
        self._supported_export_formats = [".csv", ".xlsx", ".pdf", ".docx"]

        # 文件大小限制(50MB)
        self._max_file_size = 50 * 1024 * 1024

        self._logger.info("文件验证服务初始化完成")

    def get_supported_formats(self) -> dict[str, list[str]]:
        """
        获取支持的文件格式

        Returns:
            Dict[str, List[str]]: 支持的导入和导出格式
        """
        return {
            "import": self._supported_import_formats,
            "export": self._supported_export_formats,
        }

    def validate_import_file(self, file_path: str) -> tuple[bool, str]:
        """
        验证导入文件

        Args:
            file_path: 文件路径

        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False, "文件不存在"

            # 检查文件扩展名
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self._supported_import_formats:
                return False, f"不支持的文件格式: {file_ext}"

            # 检查文件大小
            file_size = os.path.getsize(file_path)
            if file_size > self._max_file_size:
                max_mb = self._max_file_size // (1024 * 1024)
                return False, f"文件过大,最大支持 {max_mb}MB"

            # 根据文件类型进行具体验证
            if file_ext == ".csv":
                return self._validate_csv_file(file_path)
            elif file_ext == ".xlsx":
                return self._validate_excel_file(file_path)

            return True, ""

        except Exception as e:
            self._logger.error(f"验证导入文件失败: {e}")
            return False, f"文件验证失败: {e}"

    def _validate_csv_file(self, file_path: str) -> tuple[bool, str]:
        """
        验证CSV文件

        Args:
            file_path: CSV文件路径

        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            with open(file_path, encoding="utf-8-sig") as file:
                # 读取前几行检查格式
                sample = file.read(1024)
                if not sample.strip():
                    return False, "文件为空"

                # 检查是否包含有效的CSV数据
                file.seek(0)
                reader = csv.reader(file)
                headers = next(reader, None)
                if not headers:
                    return False, "CSV文件没有标题行"

            return True, ""

        except UnicodeDecodeError:
            return False, "文件编码错误,请使用UTF-8编码"
        except Exception as e:
            return False, f"CSV文件格式错误: {e}"

    def _validate_excel_file(self, file_path: str) -> tuple[bool, str]:
        """
        验证Excel文件

        Args:
            file_path: Excel文件路径

        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            import pandas as pd

            # 尝试读取Excel文件
            df = pd.read_excel(file_path, nrows=0)  # 只读取标题行
            if df.empty:
                return False, "Excel文件为空"

            return True, ""

        except ImportError:
            return False, "需要安装pandas和openpyxl库来处理Excel文件"
        except Exception as e:
            return False, f"Excel文件格式错误: {e}"

    def validate_export_format(self, export_format: str) -> tuple[bool, str]:
        """
        验证导出格式

        Args:
            export_format: 导出格式

        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if export_format not in self._supported_export_formats:
            return False, f"不支持的导出格式: {export_format}"

        return True, ""

    def validate_output_path(self, output_path: str) -> tuple[bool, str]:
        """
        验证输出路径

        Args:
            output_path: 输出路径

        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            # 检查目录是否存在
            output_dir = Path(output_path).parent
            if not output_dir.exists():
                return False, f"输出目录不存在: {output_dir}"

            # 检查目录是否可写
            if not os.access(output_dir, os.W_OK):
                return False, f"输出目录不可写: {output_dir}"

            return True, ""

        except Exception as e:
            return False, f"输出路径验证失败: {e}"
