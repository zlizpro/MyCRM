"""
MiniCRM 文档生成服务协调器

提供Word和PDF文档生成功能的统一接口,包括:
- 合同文档生成
- 报价单文档生成
- 客户报告生成
- 模板管理协调

设计原则:
- 协调各专门服务
- 提供统一接口
- 完整的错误处理和日志记录
- 遵循单一职责原则
"""

import logging
from typing import Any

from minicrm.core.exceptions import ServiceError

from .pdf_document_service import PdfDocumentService
from .template_manager_service import TemplateManagerService
from .word_document_service import WordDocumentService


class DocumentGenerationService:
    """
    文档生成服务协调器

    协调模板管理、Word文档生成和PDF文档生成服务.
    """

    def __init__(self):
        """初始化文档生成服务"""
        self._logger = logging.getLogger(__name__)

        # 初始化专门服务
        self._template_manager = TemplateManagerService()
        self._word_service = WordDocumentService()
        self._pdf_service = PdfDocumentService()

        # 延迟初始化Excel服务
        try:
            from .excel_export_service import ExcelExportService

            self._excel_service = ExcelExportService()
        except ImportError:
            self._excel_service = None
            self._logger.warning("Excel导出服务不可用")

        self._logger.info("文档生成服务协调器初始化完成")

    # 模板管理方法(委托给模板管理服务)

    def get_available_templates(self) -> list[str]:
        """
        获取可用的模板列表

        Returns:
            List[str]: 可用模板类型列表
        """
        return self._template_manager.get_available_templates()

    def create_custom_template(
        self, template_name: str, template_content: str, template_type: str = "custom"
    ) -> bool:
        """
        创建自定义模板

        Args:
            template_name: 模板名称
            template_content: 模板内容
            template_type: 模板类型

        Returns:
            bool: 创建是否成功
        """
        return self._template_manager.create_custom_template(
            template_name, template_content, template_type
        )

    def update_template(self, template_name: str, template_content: str) -> bool:
        """
        更新现有模板

        Args:
            template_name: 模板名称
            template_content: 新的模板内容

        Returns:
            bool: 更新是否成功
        """
        return self._template_manager.update_template(template_name, template_content)

    def delete_template(self, template_name: str) -> bool:
        """
        删除模板

        Args:
            template_name: 模板名称

        Returns:
            bool: 删除是否成功
        """
        return self._template_manager.delete_template(template_name)

    def get_template_content(self, template_name: str) -> str:
        """
        获取模板内容

        Args:
            template_name: 模板名称

        Returns:
            str: 模板内容
        """
        return self._template_manager.get_template_content(template_name)

    # Word文档生成方法(委托给Word文档服务)

    def generate_word_document(
        self, template_type: str, data: dict[str, Any], output_path: str
    ) -> bool:
        """
        生成Word文档

        Args:
            template_type: 模板类型 (contract, quote, customer_report)
            data: 数据字典
            output_path: 输出文件路径

        Returns:
            bool: 生成是否成功

        Raises:
            ServiceError: 生成失败时抛出
        """
        try:
            self._logger.info(f"开始生成Word文档: {template_type} -> {output_path}")

            # 获取模板路径
            template_path = self._template_manager.get_template_path(template_type)

            if template_path and template_path.exists():
                # 使用模板生成
                return self._word_service.generate_from_template(
                    template_path, data, output_path
                )
            else:
                # 使用简单方式生成
                return self._word_service.generate_simple_document(
                    data, output_path, template_type
                )

        except Exception as e:
            self._logger.error(f"生成Word文档失败: {e}")
            raise ServiceError(f"生成Word文档失败: {e}") from e

    # PDF文档生成方法(委托给PDF文档服务)

    def convert_to_pdf(self, word_file_path: str, pdf_output_path: str) -> bool:
        """
        将Word文档转换为PDF

        Args:
            word_file_path: Word文件路径
            pdf_output_path: PDF输出路径

        Returns:
            bool: 转换是否成功
        """
        return self._pdf_service.convert_word_to_pdf(word_file_path, pdf_output_path)

    def generate_enhanced_pdf_report(
        self, report_type: str, data: dict[str, Any], output_path: str
    ) -> bool:
        """
        生成增强的PDF报表

        Args:
            report_type: 报表类型 (customer_report, financial_report, analytics_report)
            data: 报表数据
            output_path: 输出路径

        Returns:
            bool: 生成是否成功
        """
        return self._pdf_service.generate_enhanced_pdf_report(
            report_type, data, output_path
        )

    # 便捷方法

    def generate_contract_document(
        self, contract_data: dict[str, Any], output_path: str, format_type: str = "word"
    ) -> bool:
        """
        生成合同文档

        Args:
            contract_data: 合同数据
            output_path: 输出路径
            format_type: 格式类型 ("word" 或 "pdf")

        Returns:
            bool: 生成是否成功
        """
        try:
            if format_type.lower() == "pdf":
                return self._pdf_service.generate_enhanced_pdf_report(
                    "contract", contract_data, output_path
                )
            else:
                return self.generate_word_document(
                    "contract", contract_data, output_path
                )

        except Exception as e:
            self._logger.error(f"生成合同文档失败: {e}")
            return False

    def generate_quote_document(
        self, quote_data: dict[str, Any], output_path: str, format_type: str = "word"
    ) -> bool:
        """
        生成报价单文档

        Args:
            quote_data: 报价单数据
            output_path: 输出路径
            format_type: 格式类型 ("word" 或 "pdf")

        Returns:
            bool: 生成是否成功
        """
        try:
            if format_type.lower() == "pdf":
                return self._pdf_service.generate_enhanced_pdf_report(
                    "quote", quote_data, output_path
                )
            else:
                return self.generate_word_document("quote", quote_data, output_path)

        except Exception as e:
            self._logger.error(f"生成报价单文档失败: {e}")
            return False

    def generate_customer_report(
        self, report_data: dict[str, Any], output_path: str, format_type: str = "pdf"
    ) -> bool:
        """
        生成客户报告

        Args:
            report_data: 报告数据
            output_path: 输出路径
            format_type: 格式类型 ("word" 或 "pdf")

        Returns:
            bool: 生成是否成功
        """
        try:
            if format_type.lower() == "word":
                return self.generate_word_document(
                    "customer_report", report_data, output_path
                )
            else:
                return self._pdf_service.generate_enhanced_pdf_report(
                    "customer_report", report_data, output_path
                )

        except Exception as e:
            self._logger.error(f"生成客户报告失败: {e}")
            return False

    # 服务状态和信息方法

    # Excel导出方法(委托给Excel导出服务)

    def export_customer_data_excel(
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
        if self._excel_service is None:
            self._logger.error("Excel导出服务不可用")
            return False
        return self._excel_service.export_customer_data(
            customers, output_path, include_analysis
        )

    def export_supplier_data_excel(
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
        return self._excel_service.export_supplier_data(suppliers, output_path)

    def export_financial_report_excel(
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
        return self._excel_service.export_financial_report(financial_data, output_path)

    def generate_batch_documents(
        self, document_configs: list[dict[str, Any]]
    ) -> dict[str, bool]:
        """
        批量生成文档 - 新增功能

        支持批量生成Word、PDF、Excel等多种格式的文档

        Args:
            document_configs: 文档配置列表,每个配置包含:
                - document_type: 文档类型 (word, pdf, excel)
                - template_type: 模板类型 (contract, quote, customer_report等)
                - data: 文档数据
                - output_path: 输出路径
                - options: 额外选项

        Returns:
            Dict[str, bool]: 各文档生成结果
        """
        results = {}

        try:
            self._logger.info(f"开始批量生成{len(document_configs)}个文档")

            for config in document_configs:
                document_type = config.get("document_type", "word")
                template_type = config.get("template_type", "generic")
                data = config.get("data", {})
                output_path = config.get("output_path", "")
                options = config.get("options", {})

                try:
                    if document_type == "word":
                        success = self.generate_word_document(
                            template_type, data, output_path
                        )
                    elif document_type == "pdf":
                        success = self.generate_enhanced_pdf_report(
                            template_type, data, output_path
                        )
                    elif document_type == "excel":
                        if template_type == "customer_data":
                            success = self.export_customer_data_excel(
                                data.get("customers", []),
                                output_path,
                                options.get("include_analysis", True),
                            )
                        elif template_type == "supplier_data":
                            success = self.export_supplier_data_excel(
                                data.get("suppliers", []), output_path
                            )
                        elif template_type == "financial_report":
                            success = self.export_financial_report_excel(
                                data, output_path
                            )
                        else:
                            success = False
                    else:
                        success = False

                    results[output_path] = success

                    if success:
                        self._logger.info(f"文档生成成功: {output_path}")
                    else:
                        self._logger.warning(f"文档生成失败: {output_path}")

                except Exception as e:
                    self._logger.error(f"生成文档{output_path}时出错: {e}")
                    results[output_path] = False

            success_count = sum(1 for success in results.values() if success)
            self._logger.info(
                f"批量文档生成完成: {success_count}/{len(document_configs)} 成功"
            )

            return results

        except Exception as e:
            self._logger.error(f"批量生成文档失败: {e}")
            return {}

    def generate_print_ready_documents(
        self, print_configs: list[dict[str, Any]]
    ) -> dict[str, bool]:
        """
        生成打印就绪的文档 - 新增功能

        为批量打印优化文档格式和布局

        Args:
            print_configs: 打印配置列表

        Returns:
            Dict[str, bool]: 各文档生成结果
        """
        results = {}

        try:
            self._logger.info(f"开始生成{len(print_configs)}个打印就绪文档")

            for config in print_configs:
                document_type = config.get("document_type", "pdf")  # 默认PDF适合打印
                data = config.get("data", {})
                output_path = config.get("output_path", "")

                # 为打印优化数据
                print_optimized_data = self._optimize_data_for_print(data, config)

                try:
                    if document_type == "pdf":
                        success = self._pdf_service.generate_enhanced_pdf_report(
                            "print_optimized", print_optimized_data, output_path
                        )
                    elif document_type == "word":
                        success = self._word_service.generate_simple_document(
                            print_optimized_data, output_path, "print_optimized"
                        )
                    else:
                        success = False

                    results[output_path] = success

                except Exception as e:
                    self._logger.error(f"生成打印文档{output_path}时出错: {e}")
                    results[output_path] = False

            return results

        except Exception as e:
            self._logger.error(f"生成打印就绪文档失败: {e}")
            return {}

    def _optimize_data_for_print(
        self, data: dict[str, Any], config: dict[str, Any]
    ) -> dict[str, Any]:
        """
        为打印优化数据格式

        Args:
            data: 原始数据
            config: 打印配置

        Returns:
            Dict[str, Any]: 优化后的数据
        """
        optimized_data = data.copy()

        # 添加打印特定的格式设置
        optimized_data.update(
            {
                "print_date": self._get_current_timestamp(),
                "page_orientation": config.get("page_orientation", "portrait"),
                "font_size": config.get("font_size", 11),
                "margin_size": config.get("margin_size", "normal"),
                "include_page_numbers": config.get("include_page_numbers", True),
                "include_header": config.get("include_header", True),
                "include_footer": config.get("include_footer", True),
            }
        )

        return optimized_data

    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_service_status(self) -> dict[str, Any]:
        """
        获取增强的服务状态

        Returns:
            Dict[str, Any]: 服务状态信息
        """
        return {
            "template_manager": "运行中",
            "word_service": "运行中",
            "pdf_service": "运行中",
            "excel_service": "运行中",
            "available_templates": self.get_available_templates(),
            "supported_formats": ["word", "pdf", "excel"],
            "supported_document_types": [
                "contract",
                "quote",
                "customer_report",
                "supplier_report",
                "financial_report",
            ],
            "batch_processing": "支持",
            "print_optimization": "支持",
            "template_customization": "支持",
        }

    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 这里可以添加清理逻辑
            self._logger.info("文档生成服务资源清理完成")
        except Exception as e:
            self._logger.error(f"清理资源失败: {e}")
