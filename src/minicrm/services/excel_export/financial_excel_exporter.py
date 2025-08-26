"""
财务Excel导出器

专门负责财务报表的Excel导出功能.
支持财务数据分析和报表生成.
"""

import csv
import logging
from datetime import datetime
from typing import Any

from minicrm.core.exceptions import ServiceError


class FinancialExcelExporter:
    """
    财务Excel导出器

    专门负责财务报表的Excel导出功能.
    """

    def __init__(self):
        """初始化财务Excel导出器"""
        self._logger = logging.getLogger(__name__)

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
            self._logger.info(f"开始导出财务报表到Excel: {output_path}")

            # 使用简化的CSV实现
            csv_path = output_path.replace(".xlsx", ".csv")
            return self._export_as_csv(financial_data, csv_path)

        except Exception as e:
            self._logger.error(f"导出财务报表失败: {e}")
            raise ServiceError(
                f"导出财务报表失败: {e}", "FinancialExcelExporter"
            ) from e

    def _export_as_csv(self, financial_data: dict[str, Any], output_path: str) -> bool:
        """导出财务数据为CSV格式"""
        try:
            with open(output_path, "w", newline="", encoding="utf-8-sig") as csvfile:
                writer = csv.writer(csvfile)

                # 写入标题
                writer.writerow(["财务报表"])
                writer.writerow(
                    [f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]
                )
                writer.writerow([])  # 空行

                # 写入财务数据
                for key, value in financial_data.items():
                    if isinstance(value, dict):
                        writer.writerow([key])
                        for sub_key, sub_value in value.items():
                            writer.writerow([f"  {sub_key}", sub_value])
                    else:
                        writer.writerow([key, value])

            self._logger.info(f"导出财务报表成功: {output_path}")
            return True

        except Exception as e:
            self._logger.error(f"导出财务报表为CSV失败: {e}")
            return False
