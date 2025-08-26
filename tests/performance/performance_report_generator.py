"""MiniCRM性能报告生成器

为任务10提供详细的性能报告生成功能：
- 生成HTML格式的可视化报告
- 生成PDF格式的正式报告
- 性能趋势图表生成
- 优化建议和行动计划
- 合规性检查报告

作者: MiniCRM开发团队
"""

from datetime import datetime
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List


try:
    import matplotlib

    matplotlib.use("Agg")  # 使用非交互式后端
    import matplotlib.dates as mdates
    from matplotlib.font_manager import FontProperties
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        Image,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PerformanceChartGenerator:
    """性能图表生成器"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        # 设置中文字体
        if MATPLOTLIB_AVAILABLE:
            plt.rcParams["font.sans-serif"] = [
                "Microsoft YaHei",
                "SimHei",
                "DejaVu Sans",
            ]
            plt.rcParams["axes.unicode_minus"] = False

    def generate_performance_comparison_chart(
        self, qt_results: Dict[str, Any], ttk_results: Dict[str, Any], output_path: str
    ) -> str:
        """生成性能对比图表"""
        if not MATPLOTLIB_AVAILABLE:
            self.logger.warning("matplotlib不可用，跳过图表生成")
            return ""

        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle("MiniCRM Qt vs TTK 性能对比", fontsize=16, fontweight="bold")

            # 1. 启动时间对比
            self._plot_startup_time_comparison(ax1, qt_results, ttk_results)

            # 2. 内存使用对比
            self._plot_memory_usage_comparison(ax2, qt_results, ttk_results)

            # 3. 响应时间对比
            self._plot_response_time_comparison(ax3, qt_results, ttk_results)

            # 4. 综合性能评分
            self._plot_overall_performance_score(ax4, qt_results, ttk_results)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()

            self.logger.info(f"性能对比图表已生成: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"生成性能对比图表失败: {e}")
            return ""

    def _plot_startup_time_comparison(self, ax, qt_results: Dict, ttk_results: Dict):
        """绘制启动时间对比"""
        categories = []
        qt_times = []
        ttk_times = []

        for result in qt_results.get("detailed_results", []):
            test_name = result.get("test_name", "")
            if "startup" in test_name.lower():
                categories.append("启动时间")
                qt_times.append(
                    result.get("qt_result", {})
                    .get("metrics", {})
                    .get("startup_time", 0)
                )
                ttk_times.append(
                    result.get("ttk_result", {})
                    .get("metrics", {})
                    .get("startup_time", 0)
                )

        if categories:
            x = range(len(categories))
            width = 0.35

            ax.bar(
                [i - width / 2 for i in x],
                qt_times,
                width,
                label="Qt版本",
                color="#ff7f0e",
                alpha=0.8,
            )
            ax.bar(
                [i + width / 2 for i in x],
                ttk_times,
                width,
                label="TTK版本",
                color="#2ca02c",
                alpha=0.8,
            )

            ax.set_xlabel("测试类型")
            ax.set_ylabel("时间 (秒)")
            ax.set_title("启动时间对比")
            ax.set_xticks(x)
            ax.set_xticklabels(categories)
            ax.legend()
            ax.grid(True, alpha=0.3)

    def _plot_memory_usage_comparison(self, ax, qt_results: Dict, ttk_results: Dict):
        """绘制内存使用对比"""
        categories = []
        qt_memory = []
        ttk_memory = []

        for result in qt_results.get("detailed_results", []):
            test_name = result.get("test_name", "")
            categories.append(test_name.replace("_", " ").title())
            qt_memory.append(
                result.get("qt_result", {}).get("metrics", {}).get("peak_memory", 0)
            )
            ttk_memory.append(
                result.get("ttk_result", {}).get("metrics", {}).get("peak_memory", 0)
            )

        if categories:
            x = range(len(categories))
            width = 0.35

            ax.bar(
                [i - width / 2 for i in x],
                qt_memory,
                width,
                label="Qt版本",
                color="#ff7f0e",
                alpha=0.8,
            )
            ax.bar(
                [i + width / 2 for i in x],
                ttk_memory,
                width,
                label="TTK版本",
                color="#2ca02c",
                alpha=0.8,
            )

            ax.set_xlabel("测试类型")
            ax.set_ylabel("内存使用 (MB)")
            ax.set_title("峰值内存使用对比")
            ax.set_xticks(x)
            ax.set_xticklabels(categories, rotation=45, ha="right")
            ax.legend()
            ax.grid(True, alpha=0.3)

    def _plot_response_time_comparison(self, ax, qt_results: Dict, ttk_results: Dict):
        """绘制响应时间对比"""
        categories = []
        qt_response = []
        ttk_response = []

        for result in qt_results.get("detailed_results", []):
            test_name = result.get("test_name", "")
            if "response" in test_name.lower() or "ui" in test_name.lower():
                categories.append("UI响应")
                qt_response.append(
                    result.get("qt_result", {})
                    .get("metrics", {})
                    .get("ui_response_time", 0)
                    * 1000
                )  # 转换为毫秒
                ttk_response.append(
                    result.get("ttk_result", {})
                    .get("metrics", {})
                    .get("ui_response_time", 0)
                    * 1000
                )

        if categories:
            x = range(len(categories))
            width = 0.35

            ax.bar(
                [i - width / 2 for i in x],
                qt_response,
                width,
                label="Qt版本",
                color="#ff7f0e",
                alpha=0.8,
            )
            ax.bar(
                [i + width / 2 for i in x],
                ttk_response,
                width,
                label="TTK版本",
                color="#2ca02c",
                alpha=0.8,
            )

            ax.set_xlabel("测试类型")
            ax.set_ylabel("响应时间 (毫秒)")
            ax.set_title("UI响应时间对比")
            ax.set_xticks(x)
            ax.set_xticklabels(categories)
            ax.legend()
            ax.grid(True, alpha=0.3)

            # 添加性能要求线
            ax.axhline(
                y=200, color="red", linestyle="--", alpha=0.7, label="性能要求(200ms)"
            )
            ax.legend()

    def _plot_overall_performance_score(self, ax, qt_results: Dict, ttk_results: Dict):
        """绘制综合性能评分"""
        # 计算综合性能评分
        qt_score = self._calculate_performance_score(qt_results)
        ttk_score = self._calculate_performance_score(ttk_results)

        categories = ["启动性能", "内存效率", "UI响应", "数据处理", "综合评分"]
        qt_scores = [
            qt_score.get(cat, 0)
            for cat in ["startup", "memory", "ui", "data", "overall"]
        ]
        ttk_scores = [
            ttk_score.get(cat, 0)
            for cat in ["startup", "memory", "ui", "data", "overall"]
        ]

        x = range(len(categories))
        width = 0.35

        ax.bar(
            [i - width / 2 for i in x],
            qt_scores,
            width,
            label="Qt版本",
            color="#ff7f0e",
            alpha=0.8,
        )
        ax.bar(
            [i + width / 2 for i in x],
            ttk_scores,
            width,
            label="TTK版本",
            color="#2ca02c",
            alpha=0.8,
        )

        ax.set_xlabel("性能维度")
        ax.set_ylabel("评分 (0-100)")
        ax.set_title("综合性能评分对比")
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha="right")
        ax.set_ylim(0, 100)
        ax.legend()
        ax.grid(True, alpha=0.3)

    def _calculate_performance_score(self, results: Dict) -> Dict[str, float]:
        """计算性能评分"""
        scores = {"startup": 0, "memory": 0, "ui": 0, "data": 0, "overall": 0}

        try:
            detailed_results = results.get("detailed_results", [])

            for result in detailed_results:
                test_name = result.get("test_name", "")
                metrics = result.get("ttk_result", {}).get("metrics", {})

                # 启动性能评分 (3秒为满分)
                if "startup" in test_name:
                    startup_time = metrics.get("startup_time", float("inf"))
                    scores["startup"] = max(
                        0, min(100, (3.0 - startup_time) / 3.0 * 100)
                    )

                # 内存效率评分 (200MB为满分)
                if "memory" in test_name:
                    peak_memory = metrics.get("peak_memory", float("inf"))
                    scores["memory"] = max(
                        0, min(100, (200.0 - peak_memory) / 200.0 * 100)
                    )

                # UI响应评分 (200ms为满分)
                if "ui" in test_name or "response" in test_name:
                    response_time = metrics.get("ui_response_time", float("inf"))
                    scores["ui"] = max(0, min(100, (0.2 - response_time) / 0.2 * 100))

                # 数据处理评分
                if "data" in test_name:
                    data_time = metrics.get("data_load_time", float("inf"))
                    scores["data"] = max(0, min(100, (1.0 - data_time) / 1.0 * 100))

            # 综合评分
            valid_scores = [score for score in scores.values() if score > 0]
            scores["overall"] = (
                sum(valid_scores) / len(valid_scores) if valid_scores else 0
            )

        except Exception as e:
            self.logger.error(f"计算性能评分失败: {e}")

        return scores

    def generate_memory_trend_chart(
        self, memory_data: List[float], output_path: str
    ) -> str:
        """生成内存使用趋势图"""
        if not MATPLOTLIB_AVAILABLE or not memory_data:
            return ""

        try:
            fig, ax = plt.subplots(figsize=(12, 6))

            time_points = list(range(len(memory_data)))
            ax.plot(
                time_points,
                memory_data,
                linewidth=2,
                color="#1f77b4",
                marker="o",
                markersize=3,
            )
            ax.fill_between(time_points, memory_data, alpha=0.3, color="#1f77b4")

            ax.set_xlabel("时间点")
            ax.set_ylabel("内存使用 (MB)")
            ax.set_title("内存使用趋势")
            ax.grid(True, alpha=0.3)

            # 添加统计信息
            avg_memory = sum(memory_data) / len(memory_data)
            max_memory = max(memory_data)
            ax.axhline(
                y=avg_memory,
                color="orange",
                linestyle="--",
                alpha=0.7,
                label=f"平均: {avg_memory:.1f}MB",
            )
            ax.axhline(
                y=max_memory,
                color="red",
                linestyle="--",
                alpha=0.7,
                label=f"峰值: {max_memory:.1f}MB",
            )
            ax.legend()

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            plt.close()

            return output_path

        except Exception as e:
            self.logger.error(f"生成内存趋势图失败: {e}")
            return ""


class PDFReportGenerator:
    """PDF报告生成器"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        if REPORTLAB_AVAILABLE:
            # 注册中文字体
            try:
                # 尝试注册系统中文字体
                font_paths = [
                    "C:/Windows/Fonts/msyh.ttc",  # Windows 微软雅黑
                    "/System/Library/Fonts/PingFang.ttc",  # macOS 苹方
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                ]

                for font_path in font_paths:
                    if os.path.exists(font_path):
                        pdfmetrics.registerFont(TTFont("ChineseFont", font_path))
                        break

            except Exception as e:
                self.logger.warning(f"注册中文字体失败: {e}")

    def generate_pdf_report(self, report_data: Dict[str, Any], output_path: str) -> str:
        """生成PDF报告"""
        if not REPORTLAB_AVAILABLE:
            self.logger.warning("reportlab不可用，跳过PDF报告生成")
            return ""

        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()

            # 创建自定义样式
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=18,
                spaceAfter=30,
                alignment=1,  # 居中
            )

            heading_style = ParagraphStyle(
                "CustomHeading", parent=styles["Heading2"], fontSize=14, spaceAfter=12
            )

            story = []

            # 标题
            story.append(Paragraph("MiniCRM性能基准测试报告", title_style))
            story.append(Spacer(1, 20))

            # 报告信息
            report_info = [
                ["报告生成时间", report_data.get("timestamp", "Unknown")],
                [
                    "测试环境",
                    f"{report_data.get('system_info', {}).get('platform', 'Unknown')}",
                ],
                [
                    "Python版本",
                    report_data.get("system_info", {}).get("python_version", "Unknown"),
                ],
                [
                    "CPU核心数",
                    str(report_data.get("system_info", {}).get("cpu_count", "Unknown")),
                ],
                [
                    "总内存",
                    f"{report_data.get('system_info', {}).get('memory_total_gb', 0):.1f} GB",
                ],
            ]

            info_table = Table(report_info, colWidths=[2 * inch, 3 * inch])
            info_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )

            story.append(info_table)
            story.append(Spacer(1, 20))

            # 测试摘要
            story.append(Paragraph("测试摘要", heading_style))
            summary = report_data.get("summary", {})
            summary_data = [
                ["总测试数", str(summary.get("total_tests", 0))],
                ["Qt成功率", f"{summary.get('qt_success_rate', 0):.1%}"],
                ["TTK成功率", f"{summary.get('ttk_success_rate', 0):.1%}"],
            ]

            summary_table = Table(summary_data, colWidths=[2 * inch, 2 * inch])
            summary_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )

            story.append(summary_table)
            story.append(Spacer(1, 20))

            # 性能分析
            story.append(Paragraph("性能分析", heading_style))
            analysis = report_data.get("performance_analysis", {})
            assessment = analysis.get("overall_assessment", "未知")
            story.append(Paragraph(f"总体评估: {assessment}", styles["Normal"]))

            bottlenecks = analysis.get("bottlenecks", [])
            if bottlenecks:
                story.append(Paragraph("发现的性能瓶颈:", styles["Normal"]))
                for bottleneck in bottlenecks:
                    story.append(Paragraph(f"• {bottleneck}", styles["Normal"]))
            else:
                story.append(Paragraph("未发现明显的性能瓶颈", styles["Normal"]))

            story.append(Spacer(1, 20))

            # 合规性检查
            story.append(Paragraph("需求合规性检查", heading_style))
            compliance = report_data.get("compliance_check", {})
            overall_compliant = compliance.get("overall_compliant", False)
            status = "合规" if overall_compliant else "不合规"
            story.append(Paragraph(f"总体状态: {status}", styles["Normal"]))

            failed_requirements = compliance.get("failed_requirements", [])
            if failed_requirements:
                story.append(Paragraph("未满足的需求:", styles["Normal"]))
                for req in failed_requirements:
                    story.append(Paragraph(f"• {req}", styles["Normal"]))

            story.append(Spacer(1, 20))

            # 优化建议
            story.append(Paragraph("优化建议", heading_style))
            recommendations = report_data.get("optimization_recommendations", [])

            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    category = rec.get("category", "未分类")
                    priority = rec.get("priority", "中")
                    description = rec.get("description", "")

                    story.append(
                        Paragraph(
                            f"{i}. {category} (优先级: {priority})", styles["Normal"]
                        )
                    )
                    story.append(Paragraph(description, styles["Normal"]))

                    suggestions = rec.get("suggestions", [])
                    for suggestion in suggestions:
                        story.append(Paragraph(f"   • {suggestion}", styles["Normal"]))

                    story.append(Spacer(1, 10))
            else:
                story.append(
                    Paragraph("暂无优化建议，性能表现良好。", styles["Normal"])
                )

            # 构建PDF
            doc.build(story)

            self.logger.info(f"PDF报告已生成: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"生成PDF报告失败: {e}")
            return ""


class ComprehensiveReportGenerator:
    """综合报告生成器"""

    def __init__(self, output_dir: str = "reports"):
        """初始化报告生成器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.chart_generator = PerformanceChartGenerator()
        self.pdf_generator = PDFReportGenerator()

    def generate_comprehensive_report(
        self,
        report_data: Dict[str, Any],
        include_charts: bool = True,
        include_pdf: bool = True,
    ) -> Dict[str, str]:
        """生成综合报告

        Args:
            report_data: 报告数据
            include_charts: 是否包含图表
            include_pdf: 是否包含PDF

        Returns:
            生成的文件路径字典
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        generated_files = {}

        try:
            # 1. 生成JSON报告
            json_path = self.output_dir / f"performance_report_{timestamp}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            generated_files["json"] = str(json_path)

            # 2. 生成HTML报告
            html_path = self.output_dir / f"performance_report_{timestamp}.html"
            html_content = self._generate_enhanced_html_report(report_data)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            generated_files["html"] = str(html_path)

            # 3. 生成图表
            if include_charts and MATPLOTLIB_AVAILABLE:
                chart_path = self.output_dir / f"performance_charts_{timestamp}.png"
                chart_file = self.chart_generator.generate_performance_comparison_chart(
                    report_data, report_data, str(chart_path)
                )
                if chart_file:
                    generated_files["chart"] = chart_file

            # 4. 生成PDF报告
            if include_pdf and REPORTLAB_AVAILABLE:
                pdf_path = self.output_dir / f"performance_report_{timestamp}.pdf"
                pdf_file = self.pdf_generator.generate_pdf_report(
                    report_data, str(pdf_path)
                )
                if pdf_file:
                    generated_files["pdf"] = pdf_file

            # 5. 生成执行摘要
            summary_path = self.output_dir / f"executive_summary_{timestamp}.txt"
            summary_content = self._generate_executive_summary(report_data)
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(summary_content)
            generated_files["summary"] = str(summary_path)

            self.logger.info(f"综合报告生成完成，共{len(generated_files)}个文件")
            return generated_files

        except Exception as e:
            self.logger.error(f"生成综合报告失败: {e}")
            return generated_files

    def _generate_enhanced_html_report(self, report_data: Dict[str, Any]) -> str:
        """生成增强的HTML报告"""
        # 这里可以使用更复杂的HTML模板
        # 为了简化，我们使用基本的HTML结构

        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MiniCRM性能基准测试报告</title>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #667eea;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }}
        .header .subtitle {{
            color: #7f8c8d;
            margin-top: 10px;
            font-size: 1.1em;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .metric-card h3 {{
            margin: 0 0 15px 0;
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .metric-card .value {{
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .metric-card .unit {{
            font-size: 0.9em;
            opacity: 0.8;
        }}
        .section {{
            margin: 40px 0;
            padding: 25px;
            background-color: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }}
        .section h2 {{
            color: #2c3e50;
            margin-top: 0;
            font-size: 1.8em;
        }}
        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .comparison-table th,
        .comparison-table td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}
        .comparison-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: bold;
        }}
        .comparison-table tr:hover {{
            background-color: #f1f3f4;
        }}
        .status-badge {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .status-success {{
            background-color: #d4edda;
            color: #155724;
        }}
        .status-warning {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .status-danger {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .recommendation {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
        }}
        .recommendation h4 {{
            color: #856404;
            margin-top: 0;
        }}
        .recommendation ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>MiniCRM性能基准测试报告</h1>
            <div class="subtitle">Qt vs TTK 框架性能对比分析</div>
            <div class="subtitle">报告生成时间: {report_data.get("timestamp", "Unknown")}</div>
        </div>

        {self._generate_metrics_grid(report_data)}

        {self._generate_detailed_comparison(report_data)}

        {self._generate_performance_analysis_section(report_data)}

        {self._generate_recommendations_section(report_data)}

        {self._generate_compliance_section(report_data)}

        <div class="footer">
            <p>MiniCRM性能基准测试系统 | 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _generate_metrics_grid(self, report_data: Dict[str, Any]) -> str:
        """生成指标网格"""
        summary = report_data.get("summary", {})

        # 计算关键指标
        total_tests = summary.get("total_tests", 0)
        ttk_success_rate = summary.get("ttk_success_rate", 0)

        # 从详细结果中提取性能数据
        performance_score = self._calculate_overall_performance_score(report_data)

        return f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>总测试数</h3>
                <div class="value">{total_tests}</div>
                <div class="unit">项测试</div>
            </div>
            <div class="metric-card">
                <h3>TTK成功率</h3>
                <div class="value">{ttk_success_rate:.1%}</div>
                <div class="unit">测试通过</div>
            </div>
            <div class="metric-card">
                <h3>性能评分</h3>
                <div class="value">{performance_score:.0f}</div>
                <div class="unit">分 (满分100)</div>
            </div>
            <div class="metric-card">
                <h3>合规状态</h3>
                <div class="value">{"✓" if report_data.get("compliance_check", {}).get("overall_compliant", False) else "✗"}</div>
                <div class="unit">需求合规</div>
            </div>
        </div>
        """

    def _generate_detailed_comparison(self, report_data: Dict[str, Any]) -> str:
        """生成详细对比"""
        detailed_results = report_data.get("detailed_results", [])

        table_rows = ""
        for result in detailed_results:
            test_name = result.get("test_name", "Unknown")
            qt_result = result.get("qt_result", {})
            ttk_result = result.get("ttk_result", {})
            comparison = result.get("comparison", {})

            qt_metrics = qt_result.get("metrics", {})
            ttk_metrics = ttk_result.get("metrics", {})

            # 格式化数据
            startup_time = f"{ttk_metrics.get('startup_time', 0):.3f}s"
            memory_usage = f"{ttk_metrics.get('peak_memory', 0):.1f}MB"
            response_time = f"{ttk_metrics.get('ui_response_time', 0) * 1000:.1f}ms"

            # 状态标记
            status_class = (
                "status-success"
                if ttk_result.get("success", False)
                else "status-danger"
            )
            status_text = "通过" if ttk_result.get("success", False) else "失败"

            table_rows += f"""
            <tr>
                <td>{test_name.replace("_", " ").title()}</td>
                <td>{startup_time}</td>
                <td>{memory_usage}</td>
                <td>{response_time}</td>
                <td><span class="status-badge {status_class}">{status_text}</span></td>
            </tr>
            """

        return f"""
        <div class="section">
            <h2>详细性能对比</h2>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>测试项目</th>
                        <th>启动时间</th>
                        <th>内存使用</th>
                        <th>响应时间</th>
                        <th>状态</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        """

    def _generate_performance_analysis_section(
        self, report_data: Dict[str, Any]
    ) -> str:
        """生成性能分析部分"""
        analysis = report_data.get("performance_analysis", {})
        assessment = analysis.get("overall_assessment", "未知")
        bottlenecks = analysis.get("bottlenecks", [])

        bottlenecks_html = ""
        if bottlenecks:
            bottlenecks_html = "<ul>"
            for bottleneck in bottlenecks:
                bottlenecks_html += f"<li>{bottleneck}</li>"
            bottlenecks_html += "</ul>"
        else:
            bottlenecks_html = "<p>未发现明显的性能瓶颈，系统性能表现良好。</p>"

        return f"""
        <div class="section">
            <h2>性能分析</h2>
            <h3>总体评估: {assessment}</h3>
            <h4>性能瓶颈分析:</h4>
            {bottlenecks_html}
        </div>
        """

    def _generate_recommendations_section(self, report_data: Dict[str, Any]) -> str:
        """生成建议部分"""
        recommendations = report_data.get("optimization_recommendations", [])

        if not recommendations:
            return """
            <div class="section">
                <h2>优化建议</h2>
                <p>系统性能表现良好，暂无特殊优化建议。</p>
            </div>
            """

        recommendations_html = ""
        for i, rec in enumerate(recommendations, 1):
            category = rec.get("category", "未分类")
            priority = rec.get("priority", "中")
            description = rec.get("description", "")
            suggestions = rec.get("suggestions", [])

            suggestions_html = "<ul>"
            for suggestion in suggestions:
                suggestions_html += f"<li>{suggestion}</li>"
            suggestions_html += "</ul>"

            recommendations_html += f"""
            <div class="recommendation">
                <h4>{i}. {category} (优先级: {priority})</h4>
                <p>{description}</p>
                <strong>建议措施:</strong>
                {suggestions_html}
            </div>
            """

        return f"""
        <div class="section">
            <h2>优化建议</h2>
            {recommendations_html}
        </div>
        """

    def _generate_compliance_section(self, report_data: Dict[str, Any]) -> str:
        """生成合规性部分"""
        compliance = report_data.get("compliance_check", {})
        overall_compliant = compliance.get("overall_compliant", False)
        failed_requirements = compliance.get("failed_requirements", [])

        status_class = "status-success" if overall_compliant else "status-danger"
        status_text = "合规" if overall_compliant else "不合规"

        failed_html = ""
        if failed_requirements:
            failed_html = "<h4>未满足的需求:</h4><ul>"
            for req in failed_requirements:
                failed_html += f"<li>{req}</li>"
            failed_html += "</ul>"
        else:
            failed_html = "<p>所有性能需求均已满足。</p>"

        return f"""
        <div class="section">
            <h2>需求合规性检查</h2>
            <h3>总体状态: <span class="status-badge {status_class}">{status_text}</span></h3>
            {failed_html}
        </div>
        """

    def _generate_executive_summary(self, report_data: Dict[str, Any]) -> str:
        """生成执行摘要"""
        summary = report_data.get("summary", {})
        analysis = report_data.get("performance_analysis", {})
        compliance = report_data.get("compliance_check", {})

        return f"""
MiniCRM性能基准测试执行摘要
================================

测试概况:
- 测试时间: {report_data.get("timestamp", "Unknown")}
- 总测试数: {summary.get("total_tests", 0)}
- TTK成功率: {summary.get("ttk_success_rate", 0):.1%}
- 性能评估: {analysis.get("overall_assessment", "未知")}
- 合规状态: {"合规" if compliance.get("overall_compliant", False) else "不合规"}

关键发现:
{self._format_key_findings(report_data)}

建议行动:
{self._format_action_items(report_data)}

结论:
{self._format_conclusion(report_data)}

---
报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    def _format_key_findings(self, report_data: Dict[str, Any]) -> str:
        """格式化关键发现"""
        findings = []

        # 分析性能数据
        detailed_results = report_data.get("detailed_results", [])
        for result in detailed_results:
            comparison = result.get("comparison", {})
            if comparison.get("comparison_available", False):
                test_name = result.get("test_name", "")

                if "startup_time_improvement_percent" in comparison:
                    improvement = comparison["startup_time_improvement_percent"]
                    if improvement > 0:
                        findings.append(
                            f"- {test_name}: 启动时间改善{improvement:.1f}%"
                        )
                    else:
                        findings.append(
                            f"- {test_name}: 启动时间退化{abs(improvement):.1f}%"
                        )

                if "memory_change_percent" in comparison:
                    change = comparison["memory_change_percent"]
                    if change < 0:
                        findings.append(
                            f"- {test_name}: 内存使用减少{abs(change):.1f}%"
                        )
                    else:
                        findings.append(f"- {test_name}: 内存使用增加{change:.1f}%")

        return "\n".join(findings) if findings else "- 未发现显著的性能变化"

    def _format_action_items(self, report_data: Dict[str, Any]) -> str:
        """格式化行动项目"""
        recommendations = report_data.get("optimization_recommendations", [])

        if not recommendations:
            return "- 系统性能良好，无需特殊优化"

        actions = []
        for rec in recommendations:
            category = rec.get("category", "")
            priority = rec.get("priority", "")
            actions.append(f"- {category} (优先级: {priority})")

        return "\n".join(actions)

    def _format_conclusion(self, report_data: Dict[str, Any]) -> str:
        """格式化结论"""
        compliance = report_data.get("compliance_check", {})
        analysis = report_data.get("performance_analysis", {})

        if compliance.get("overall_compliant", False):
            conclusion = "TTK版本满足所有性能需求，可以投入生产使用。"
        else:
            failed_count = len(compliance.get("failed_requirements", []))
            conclusion = f"TTK版本有{failed_count}项需求不满足，需要进一步优化。"

        assessment = analysis.get("overall_assessment", "")
        if assessment:
            conclusion += f" 总体性能评估为：{assessment}。"

        return conclusion

    def _calculate_overall_performance_score(
        self, report_data: Dict[str, Any]
    ) -> float:
        """计算总体性能评分"""
        detailed_results = report_data.get("detailed_results", [])
        scores = []

        for result in detailed_results:
            ttk_result = result.get("ttk_result", {})
            if ttk_result.get("success", False):
                metrics = ttk_result.get("metrics", {})

                # 启动时间评分 (3秒为满分)
                startup_time = metrics.get("startup_time", float("inf"))
                startup_score = max(0, min(100, (3.0 - startup_time) / 3.0 * 100))

                # 内存使用评分 (200MB为满分)
                peak_memory = metrics.get("peak_memory", float("inf"))
                memory_score = max(0, min(100, (200.0 - peak_memory) / 200.0 * 100))

                # UI响应评分 (200ms为满分)
                response_time = metrics.get("ui_response_time", float("inf"))
                response_score = max(0, min(100, (0.2 - response_time) / 0.2 * 100))

                # 计算平均分
                test_scores = [
                    s for s in [startup_score, memory_score, response_score] if s > 0
                ]
                if test_scores:
                    scores.append(sum(test_scores) / len(test_scores))

        return sum(scores) / len(scores) if scores else 0


if __name__ == "__main__":
    # 测试报告生成器
    generator = ComprehensiveReportGenerator()

    # 模拟测试数据
    test_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": {"total_tests": 4, "qt_success_rate": 1.0, "ttk_success_rate": 1.0},
        "detailed_results": [
            {
                "test_name": "startup_performance",
                "qt_result": {
                    "success": True,
                    "metrics": {"startup_time": 2.5, "peak_memory": 150.0},
                },
                "ttk_result": {
                    "success": True,
                    "metrics": {"startup_time": 2.2, "peak_memory": 120.0},
                },
                "comparison": {
                    "comparison_available": True,
                    "startup_time_improvement_percent": 12.0,
                    "memory_change_percent": -20.0,
                },
            }
        ],
        "performance_analysis": {"overall_assessment": "良好", "bottlenecks": []},
        "compliance_check": {"overall_compliant": True, "failed_requirements": []},
        "optimization_recommendations": [],
        "system_info": {
            "platform": "Windows-10",
            "python_version": "3.11.0",
            "cpu_count": 8,
            "memory_total_gb": 16.0,
        },
    }

    files = generator.generate_comprehensive_report(test_data)
    print("生成的报告文件:")
    for file_type, file_path in files.items():
        print(f"  {file_type}: {file_path}")
