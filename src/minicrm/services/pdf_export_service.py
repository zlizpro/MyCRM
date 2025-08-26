"""
MiniCRM PDF导出服务

提供报价单PDF导出功能,包括:
- 专业的报价单PDF生成
- 中文字体支持和格式化
- 可配置的模板样式
- 完整的错误处理和日志记录

设计原则:
- 使用reportlab生成高质量PDF
- 支持中文字体和复杂布局
- 遵循MiniCRM开发标准
- 提供清晰的接口和错误处理
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from minicrm.core.exceptions import ServiceError


class QuotePDFExportService:
    """
    报价单PDF导出服务

    提供专业的报价单PDF生成功能,支持中文字体和复杂布局.
    """

    def __init__(self):
        """初始化PDF导出服务"""
        self._logger = logging.getLogger(__name__)
        self._fonts_registered = False
        self._setup_fonts()

        # 初始化模板服务
        from minicrm.services.quote_template_service import QuoteTemplateService

        self._template_service = QuoteTemplateService()

    def _setup_fonts(self) -> None:
        """设置中文字体"""
        try:
            # 尝试注册中文字体
            font_paths = self._get_chinese_font_paths()

            for font_name, font_path in font_paths.items():
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    self._fonts_registered = True
                    self._logger.info(f"成功注册字体: {font_name}")
                    break

            if not self._fonts_registered:
                self._logger.warning("未找到中文字体文件,将使用默认字体")

        except Exception as e:
            self._logger.error(f"设置字体失败: {e}")

    def _get_chinese_font_paths(self) -> dict[str, str]:
        """获取中文字体路径"""
        import platform

        system = platform.system()
        font_paths = {}

        if system == "Windows":
            # Windows系统字体路径
            windows_fonts = Path("C:/Windows/Fonts")
            font_paths.update(
                {
                    "SimHei": str(windows_fonts / "simhei.ttf"),
                    "SimSun": str(windows_fonts / "simsun.ttc"),
                    "Microsoft-YaHei": str(windows_fonts / "msyh.ttc"),
                }
            )
        elif system == "Darwin":  # macOS
            # macOS系统字体路径
            macos_fonts = Path("/System/Library/Fonts")
            font_paths.update(
                {
                    "PingFang": str(macos_fonts / "PingFang.ttc"),
                    "STHeiti": str(macos_fonts / "STHeiti Medium.ttc"),
                }
            )
        else:  # Linux
            # Linux系统字体路径
            linux_fonts = Path("/usr/share/fonts")
            font_paths.update(
                {
                    "WenQuanYi": str(linux_fonts / "truetype/wqy/wqy-microhei.ttc"),
                    "Noto": str(linux_fonts / "truetype/noto/NotoSansCJK-Regular.ttc"),
                }
            )

        return font_paths

    def export_quote_to_pdf(
        self,
        quote_data: dict[str, Any],
        output_path: str,
        template_id: str = "standard",
    ) -> bool:
        """
        导出报价单为PDF文件

        Args:
            quote_data: 报价数据字典
            output_path: 输出文件路径
            template_id: 模板ID

        Returns:
            bool: 导出是否成功

        Raises:
            ServiceError: 导出失败时抛出
        """
        try:
            self._logger.info(
                f"开始导出报价单PDF: {quote_data.get('quote_number', 'N/A')}"
            )

            # 验证数据
            self._validate_quote_data(quote_data)

            # 获取模板配置
            template_config = self._get_template_config(template_id)

            # 创建PDF文档
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2 * cm,
                leftMargin=2 * cm,
                topMargin=2 * cm,
                bottomMargin=2 * cm,
            )

            # 构建PDF内容
            story = []

            # 添加页眉
            story.extend(self._create_header(quote_data))
            story.append(Spacer(1, 12))

            # 添加客户信息
            story.extend(self._create_customer_info(quote_data))
            story.append(Spacer(1, 12))

            # 添加报价信息
            story.extend(self._create_quote_info(quote_data))
            story.append(Spacer(1, 12))

            # 添加产品清单表格
            story.extend(self._create_items_table(quote_data))
            story.append(Spacer(1, 12))

            # 添加汇总信息
            story.extend(self._create_totals_section(quote_data))
            story.append(Spacer(1, 12))

            # 添加条款信息
            story.extend(self._create_terms_section(quote_data))
            story.append(Spacer(1, 12))

            # 添加页脚信息
            story.extend(self._create_footer_section())

            # 生成PDF
            doc.build(story)

            self._logger.info(f"PDF导出成功: {output_path}")
            return True

        except Exception as e:
            self._logger.error(f"PDF导出失败: {e}")
            raise ServiceError(f"PDF导出失败: {e}")

    def _validate_quote_data(self, quote_data: dict[str, Any]) -> None:
        """验证报价数据"""
        required_fields = [
            "quote_number",
            "customer_name",
            "contact_person",
            "quote_date",
            "valid_until",
            "items",
        ]

        for field in required_fields:
            if not quote_data.get(field):
                raise ServiceError(f"缺少必要字段: {field}")

        items = quote_data.get("items", [])
        if not items:
            raise ServiceError("报价必须包含至少一个产品项目")

    def _get_font_name(self) -> str:
        """获取可用的中文字体名称"""
        if self._fonts_registered:
            # 返回第一个成功注册的字体
            font_names = [
                "SimHei",
                "Microsoft-YaHei",
                "PingFang",
                "STHeiti",
                "WenQuanYi",
                "Noto",
            ]
            for font_name in font_names:
                try:
                    # 测试字体是否可用
                    pdfmetrics.getFont(font_name)
                    return font_name
                except:
                    continue

        # 如果没有中文字体,使用默认字体
        return "Helvetica"

    def _create_header(self, quote_data: dict[str, Any]) -> list:
        """创建PDF页眉"""
        font_name = self._get_font_name()

        # 创建样式
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=getSampleStyleSheet()["Heading1"],
            fontName=font_name,
            fontSize=18,
            spaceAfter=12,
            alignment=1,  # 居中对齐
            textColor=colors.darkblue,
        )

        subtitle_style = ParagraphStyle(
            "CustomSubtitle",
            parent=getSampleStyleSheet()["Normal"],
            fontName=font_name,
            fontSize=12,
            spaceAfter=6,
            alignment=1,  # 居中对齐
            textColor=colors.grey,
        )

        # 创建页眉内容
        header_content = []

        # 公司名称和标题
        header_content.append(Paragraph("MiniCRM 板材销售管理系统", title_style))
        header_content.append(Paragraph("产品报价单", subtitle_style))

        return header_content

    def _create_customer_info(self, quote_data: dict[str, Any]) -> list:
        """创建客户信息部分"""
        font_name = self._get_font_name()

        # 创建样式
        info_style = ParagraphStyle(
            "InfoStyle",
            parent=getSampleStyleSheet()["Normal"],
            fontName=font_name,
            fontSize=10,
            spaceAfter=3,
        )

        # 客户信息数据
        customer_info = [
            ["客户信息", ""],
            ["客户名称:", quote_data.get("customer_name", "")],
            ["联系人:", quote_data.get("contact_person", "")],
            ["报价编号:", quote_data.get("quote_number", "")],
            ["报价日期:", self._format_date(quote_data.get("quote_date"))],
            ["有效期至:", self._format_date(quote_data.get("valid_until"))],
        ]

        # 创建表格
        table = Table(customer_info, colWidths=[4 * cm, 8 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("SPAN", (0, 0), (1, 0)),  # 合并标题行
                    ("BACKGROUND", (0, 0), (1, 0), colors.lightgrey),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("FONTNAME", (0, 0), (1, 0), font_name),
                    ("FONTSIZE", (0, 0), (1, 0), 12),
                    ("TEXTCOLOR", (0, 0), (1, 0), colors.darkblue),
                ]
            )
        )

        return [table]

    def _create_quote_info(self, quote_data: dict[str, Any]) -> list:
        """创建报价信息部分"""
        font_name = self._get_font_name()

        # 报价信息数据
        quote_info = [
            ["报价详情", ""],
            ["报价类型:", quote_data.get("quote_type_display", "标准报价")],
            ["报价状态:", quote_data.get("status_display", "草稿")],
            ["有效期:", f"{quote_data.get('validity_days', 30)} 天"],
            ["剩余天数:", f"{quote_data.get('remaining_days', 0)} 天"],
        ]

        # 创建表格
        table = Table(quote_info, colWidths=[4 * cm, 8 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("SPAN", (0, 0), (1, 0)),  # 合并标题行
                    ("BACKGROUND", (0, 0), (1, 0), colors.lightgrey),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("FONTNAME", (0, 0), (1, 0), font_name),
                    ("FONTSIZE", (0, 0), (1, 0), 12),
                    ("TEXTCOLOR", (0, 0), (1, 0), colors.darkblue),
                ]
            )
        )

        return [table]

    def _create_items_table(self, quote_data: dict[str, Any]) -> list:
        """创建产品清单表格"""
        font_name = self._get_font_name()
        items = quote_data.get("items", [])

        # 表格标题行
        table_data = [["序号", "产品名称", "规格型号", "单位", "数量", "单价", "小计"]]

        # 添加产品数据
        for i, item in enumerate(items, 1):
            row = [
                str(i),
                item.get("product_name", ""),
                item.get("specification", ""),
                item.get("unit", "件"),
                str(item.get("quantity", 0)),
                self._format_currency(item.get("unit_price", 0)),
                self._format_currency(item.get("total", 0)),
            ]
            table_data.append(row)

        # 创建表格
        table = Table(
            table_data,
            colWidths=[1 * cm, 4 * cm, 3 * cm, 1.5 * cm, 1.5 * cm, 2 * cm, 2 * cm],
        )

        # 设置表格样式
        table.setStyle(
            TableStyle(
                [
                    # 字体设置
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    # 标题行样式
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    # 数据行样式
                    ("ALIGN", (0, 1), (0, -1), "CENTER"),  # 序号居中
                    ("ALIGN", (1, 1), (2, -1), "LEFT"),  # 产品名称和规格左对齐
                    ("ALIGN", (3, 1), (-1, -1), "RIGHT"),  # 数量、单价、小计右对齐
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    # 边框
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    # 交替行颜色
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.lightgrey],
                    ),
                ]
            )
        )

        return [table]

    def _create_totals_section(self, quote_data: dict[str, Any]) -> list:
        """创建汇总信息部分"""
        font_name = self._get_font_name()

        # 汇总数据
        totals_data = [
            [
                "",
                "小计金额:",
                self._format_currency(quote_data.get("subtotal_amount", 0)),
            ],
            ["", "税额:", self._format_currency(quote_data.get("tax_amount", 0))],
            ["", "总金额:", self._format_currency(quote_data.get("total_amount", 0))],
        ]

        # 创建表格
        table = Table(totals_data, colWidths=[8 * cm, 3 * cm, 4 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 11),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    # 总金额行特殊样式
                    ("BACKGROUND", (1, 2), (2, 2), colors.lightblue),
                    ("FONTSIZE", (1, 2), (2, 2), 12),
                    ("TEXTCOLOR", (1, 2), (2, 2), colors.darkblue),
                    # 边框
                    ("LINEBELOW", (1, 0), (2, 0), 0.5, colors.black),
                    ("LINEBELOW", (1, 1), (2, 1), 0.5, colors.black),
                    ("LINEABOVE", (1, 2), (2, 2), 1, colors.darkblue),
                    ("LINEBELOW", (1, 2), (2, 2), 1, colors.darkblue),
                ]
            )
        )

        return [table]

    def _create_terms_section(self, quote_data: dict[str, Any]) -> list:
        """创建条款信息部分"""
        font_name = self._get_font_name()

        # 创建样式
        terms_style = ParagraphStyle(
            "TermsStyle",
            parent=getSampleStyleSheet()["Normal"],
            fontName=font_name,
            fontSize=10,
            spaceAfter=6,
            leftIndent=12,
        )

        title_style = ParagraphStyle(
            "TermsTitleStyle",
            parent=getSampleStyleSheet()["Heading3"],
            fontName=font_name,
            fontSize=12,
            spaceAfter=6,
            textColor=colors.darkblue,
        )

        terms_content = []

        # 付款条款
        payment_terms = quote_data.get("payment_terms", "")
        if payment_terms:
            terms_content.append(Paragraph("付款条款:", title_style))
            terms_content.append(Paragraph(payment_terms, terms_style))

        # 交付条款
        delivery_terms = quote_data.get("delivery_terms", "")
        if delivery_terms:
            terms_content.append(Paragraph("交付条款:", title_style))
            terms_content.append(Paragraph(delivery_terms, terms_style))

        # 备注信息
        notes = quote_data.get("notes", "")
        if notes:
            terms_content.append(Paragraph("备注:", title_style))
            terms_content.append(Paragraph(notes, terms_style))

        return terms_content

    def _create_footer_section(self) -> list:
        """创建页脚信息部分"""
        font_name = self._get_font_name()

        # 创建样式
        footer_style = ParagraphStyle(
            "FooterStyle",
            parent=getSampleStyleSheet()["Normal"],
            fontName=font_name,
            fontSize=9,
            alignment=1,  # 居中对齐
            textColor=colors.grey,
        )

        signature_style = ParagraphStyle(
            "SignatureStyle",
            parent=getSampleStyleSheet()["Normal"],
            fontName=font_name,
            fontSize=10,
            spaceAfter=12,
        )

        footer_content = []

        # 签名区域
        signature_data = [
            ["销售代表:", "_______________", "客户确认:", "_______________"],
            ["签名日期:", "_______________", "签名日期:", "_______________"],
        ]

        signature_table = Table(
            signature_data, colWidths=[2.5 * cm, 3 * cm, 2.5 * cm, 3 * cm]
        )
        signature_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )

        footer_content.append(signature_table)
        footer_content.append(Spacer(1, 12))

        # 公司信息
        company_info = f"MiniCRM 板材销售管理系统 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        footer_content.append(Paragraph(company_info, footer_style))

        return footer_content

    def _format_currency(self, amount: float) -> str:
        """格式化货币金额"""
        try:
            return format_currency(amount)
        except:
            return f"¥{amount:,.2f}"

    def _format_date(self, date_value) -> str:
        """格式化日期"""
        if not date_value:
            return ""

        try:
            if isinstance(date_value, str):
                # 尝试解析ISO格式日期
                from datetime import datetime

                date_obj = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
                return format_date(date_obj, "%Y-%m-%d")
            elif hasattr(date_value, "strftime"):
                return format_date(date_value, "%Y-%m-%d")
            else:
                return str(date_value)
        except:
            return str(date_value)

    def get_supported_templates(self) -> list[dict[str, str]]:
        """获取支持的模板列表"""
        return [
            {
                "id": "standard",
                "name": "标准模板",
                "description": "适用于一般报价的标准模板",
            },
            {
                "id": "professional",
                "name": "专业模板",
                "description": "适用于正式商务报价的专业模板",
            },
            {
                "id": "simple",
                "name": "简洁模板",
                "description": "适用于快速报价的简洁模板",
            },
        ]

    def preview_quote_pdf(self, quote_data: dict[str, Any]) -> str:
        """
        预览报价PDF(生成临时文件)

        Args:
            quote_data: 报价数据

        Returns:
            str: 临时PDF文件路径
        """
        import tempfile

        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(
            suffix=".pdf", delete=False, prefix="quote_preview_"
        )
        temp_path = temp_file.name
        temp_file.close()

        # 生成PDF
        success = self.export_quote_to_pdf(quote_data, temp_path)

        if success:
            return temp_path
        else:
            # 清理临时文件
            try:
                os.unlink(temp_path)
            except:
                pass
            raise ServiceError("PDF预览生成失败")

    def _get_template_config(self, template_id: str) -> dict[str, Any]:
        """获取模板配置"""
        try:
            template = self._template_service.get_template(template_id)
            if template and template.get("config"):
                return template["config"]
            else:
                # 如果模板不存在或没有配置,使用默认模板
                self._logger.warning(f"模板 {template_id} 不存在,使用默认模板")
                default_template = self._template_service.get_default_template()
                if default_template and default_template.get("config"):
                    return default_template["config"]
                else:
                    # 如果默认模板也不存在,返回基本配置
                    return self._get_fallback_config()

        except Exception as e:
            self._logger.error(f"获取模板配置失败 {template_id}: {e}")
            return self._get_fallback_config()

    def _get_fallback_config(self) -> dict[str, Any]:
        """获取后备配置(当模板不可用时)"""
        return {
            "page_size": "A4",
            "margins": {"top": 2.0, "bottom": 2.0, "left": 2.0, "right": 2.0},
            "fonts": {"default": "SimHei", "title": "SimHei", "content": "SimHei"},
            "colors": {
                "primary": "#1f4e79",
                "secondary": "#4472c4",
                "text": "#000000",
                "background": "#ffffff",
            },
            "header": {
                "show_section": True,
                "company_name": "MiniCRM 板材销售管理系统",
                "title": "产品报价单",
                "title_size": 18,
                "subtitle_size": 12,
            },
            "customer_info": {"show_section": True, "title": "客户信息"},
            "quote_info": {"show_section": True, "title": "报价详情"},
            "items_table": {"show_section": True, "title": "产品清单"},
            "totals": {"show_section": True, "title": "汇总信息"},
            "terms": {"show_section": True, "title": "条款信息"},
            "footer": {"show_section": True},
        }
