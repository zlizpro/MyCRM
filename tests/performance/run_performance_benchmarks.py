"""MiniCRM性能基准测试运行器

为任务10提供完整的性能基准测试执行：
- 自动运行Qt vs TTK性能对比测试
- 生成详细的性能报告
- 提供性能优化建议
- 验证性能需求合规性

使用方法:
    python run_performance_benchmarks.py [--output-dir OUTPUT_DIR] [--format FORMAT]

作者: MiniCRM开发团队
"""

import argparse
from datetime import datetime
import json
import logging
from pathlib import Path
import sys


# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from tests.performance.performance_benchmark_framework import PerformanceBenchmarkSuite


class PerformanceReportGenerator:
    """性能报告生成器"""

    def __init__(self, output_dir: str = "reports"):
        """初始化报告生成器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate_html_report(self, report_data: dict, filename: str = None) -> str:
        """生成HTML格式报告

        Args:
            report_data: 报告数据
            filename: 文件名（可选）

        Returns:
            生成的HTML文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.html"

        filepath = self.output_dir / filename

        html_content = self._generate_html_content(report_data)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.logger.info(f"HTML报告已生成: {filepath}")
        return str(filepath)

    def _generate_html_content(self, report_data: dict) -> str:
        """生成HTML内容"""
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
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 25px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-card h4 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .summary-card .value {{
            font-size: 24px;
            font-weight: bold;
        }}
        .test-result {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 20px;
            margin: 15px 0;
        }}
        .test-result h4 {{
            color: #495057;
            margin-top: 0;
        }}
        .metrics-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        .metrics-table th,
        .metrics-table td {{
            border: 1px solid #dee2e6;
            padding: 8px 12px;
            text-align: left;
        }}
        .metrics-table th {{
            background-color: #e9ecef;
            font-weight: bold;
        }}
        .comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
            margin: 15px 0;
        }}
        .comparison-item {{
            text-align: center;
            padding: 10px;
            border-radius: 4px;
        }}
        .qt-result {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
        }}
        .ttk-result {{
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
        }}
        .comparison-result {{
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
        }}
        .improvement {{
            color: #28a745;
            font-weight: bold;
        }}
        .regression {{
            color: #dc3545;
            font-weight: bold;
        }}
        .recommendation {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 10px 0;
        }}
        .recommendation h5 {{
            color: #856404;
            margin-top: 0;
        }}
        .recommendation ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .compliance-check {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
        }}
        .compliant {{
            color: #28a745;
            font-weight: bold;
        }}
        .non-compliant {{
            color: #dc3545;
            font-weight: bold;
        }}
        .system-info {{
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 12px;
        }}
        .timestamp {{
            text-align: right;
            color: #6c757d;
            font-size: 12px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>MiniCRM性能基准测试报告</h1>

        {self._generate_summary_section(report_data.get("summary", {}))}

        {self._generate_detailed_results_section(report_data.get("detailed_results", []))}

        {self._generate_analysis_section(report_data.get("performance_analysis", {}))}

        {self._generate_recommendations_section(report_data.get("optimization_recommendations", []))}

        {self._generate_compliance_section(report_data.get("compliance_check", {}))}

        {self._generate_system_info_section(report_data.get("system_info", {}))}

        <div class="timestamp">
            报告生成时间: {report_data.get("timestamp", "Unknown")}
        </div>
    </div>
</body>
</html>
"""
        return html

    def _generate_summary_section(self, summary: dict) -> str:
        """生成摘要部分"""
        return f"""
        <h2>测试摘要</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <h4>总测试数</h4>
                <div class="value">{summary.get("total_tests", 0)}</div>
            </div>
            <div class="summary-card">
                <h4>Qt成功率</h4>
                <div class="value">{summary.get("qt_success_rate", 0):.1%}</div>
            </div>
            <div class="summary-card">
                <h4>TTK成功率</h4>
                <div class="value">{summary.get("ttk_success_rate", 0):.1%}</div>
            </div>
        </div>
        """

    def _generate_detailed_results_section(self, detailed_results: list) -> str:
        """生成详细结果部分"""
        html = "<h2>详细测试结果</h2>"

        for result in detailed_results:
            test_name = result.get("test_name", "Unknown")
            qt_result = result.get("qt_result", {})
            ttk_result = result.get("ttk_result", {})
            comparison = result.get("comparison", {})

            html += f"""
            <div class="test-result">
                <h4>{test_name}</h4>
                {self._generate_comparison_grid(qt_result, ttk_result, comparison)}
                {self._generate_metrics_table(qt_result, ttk_result)}
            </div>
            """

        return html

    def _generate_comparison_grid(
        self, qt_result: dict, ttk_result: dict, comparison: dict
    ) -> str:
        """生成对比网格"""
        if not comparison.get("comparison_available", False):
            return "<p>对比数据不可用</p>"

        qt_metrics = qt_result.get("metrics", {})
        ttk_metrics = ttk_result.get("metrics", {})

        # 启动时间对比
        startup_comparison = ""
        if "startup_time_improvement_percent" in comparison:
            improvement = comparison["startup_time_improvement_percent"]
            if improvement > 0:
                startup_comparison = (
                    f'<span class="improvement">改善 {improvement:.1f}%</span>'
                )
            else:
                startup_comparison = (
                    f'<span class="regression">退化 {abs(improvement):.1f}%</span>'
                )

        # 内存使用对比
        memory_comparison = ""
        if "memory_change_percent" in comparison:
            change = comparison["memory_change_percent"]
            if change < 0:
                memory_comparison = (
                    f'<span class="improvement">减少 {abs(change):.1f}%</span>'
                )
            else:
                memory_comparison = (
                    f'<span class="regression">增加 {change:.1f}%</span>'
                )

        return f"""
        <div class="comparison">
            <div class="comparison-item qt-result">
                <h5>Qt版本</h5>
                <p>启动: {qt_metrics.get("startup_time", 0):.3f}s</p>
                <p>内存: {qt_metrics.get("peak_memory", 0):.1f}MB</p>
            </div>
            <div class="comparison-item ttk-result">
                <h5>TTK版本</h5>
                <p>启动: {ttk_metrics.get("startup_time", 0):.3f}s</p>
                <p>内存: {ttk_metrics.get("peak_memory", 0):.1f}MB</p>
            </div>
            <div class="comparison-item comparison-result">
                <h5>对比结果</h5>
                <p>{startup_comparison}</p>
                <p>{memory_comparison}</p>
            </div>
        </div>
        """

    def _generate_metrics_table(self, qt_result: dict, ttk_result: dict) -> str:
        """生成指标表格"""
        qt_metrics = qt_result.get("metrics", {})
        ttk_metrics = ttk_result.get("metrics", {})

        return f"""
        <table class="metrics-table">
            <thead>
                <tr>
                    <th>指标</th>
                    <th>Qt版本</th>
                    <th>TTK版本</th>
                    <th>单位</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>启动时间</td>
                    <td>{qt_metrics.get("startup_time", 0):.3f}</td>
                    <td>{ttk_metrics.get("startup_time", 0):.3f}</td>
                    <td>秒</td>
                </tr>
                <tr>
                    <td>UI响应时间</td>
                    <td>{qt_metrics.get("ui_response_time", 0):.3f}</td>
                    <td>{ttk_metrics.get("ui_response_time", 0):.3f}</td>
                    <td>秒</td>
                </tr>
                <tr>
                    <td>数据加载时间</td>
                    <td>{qt_metrics.get("data_load_time", 0):.3f}</td>
                    <td>{ttk_metrics.get("data_load_time", 0):.3f}</td>
                    <td>秒</td>
                </tr>
                <tr>
                    <td>峰值内存</td>
                    <td>{qt_metrics.get("peak_memory", 0):.1f}</td>
                    <td>{ttk_metrics.get("peak_memory", 0):.1f}</td>
                    <td>MB</td>
                </tr>
                <tr>
                    <td>平均CPU使用</td>
                    <td>{qt_metrics.get("avg_cpu_usage", 0):.1f}</td>
                    <td>{ttk_metrics.get("avg_cpu_usage", 0):.1f}</td>
                    <td>%</td>
                </tr>
                <tr>
                    <td>操作速度</td>
                    <td>{qt_metrics.get("operations_per_second", 0):.0f}</td>
                    <td>{ttk_metrics.get("operations_per_second", 0):.0f}</td>
                    <td>ops/s</td>
                </tr>
            </tbody>
        </table>
        """

    def _generate_analysis_section(self, analysis: dict) -> str:
        """生成分析部分"""
        assessment = analysis.get("overall_assessment", "未知")
        bottlenecks = analysis.get("bottlenecks", [])

        bottlenecks_html = ""
        if bottlenecks:
            bottlenecks_html = "<ul>"
            for bottleneck in bottlenecks:
                bottlenecks_html += f"<li>{bottleneck}</li>"
            bottlenecks_html += "</ul>"
        else:
            bottlenecks_html = "<p>未发现明显的性能瓶颈</p>"

        return f"""
        <h2>性能分析</h2>
        <div class="test-result">
            <h4>总体评估: {assessment}</h4>
            <h5>发现的性能瓶颈:</h5>
            {bottlenecks_html}
        </div>
        """

    def _generate_recommendations_section(self, recommendations: list) -> str:
        """生成建议部分"""
        html = "<h2>优化建议</h2>"

        if not recommendations:
            html += "<p>暂无优化建议，性能表现良好。</p>"
            return html

        for rec in recommendations:
            category = rec.get("category", "未分类")
            priority = rec.get("priority", "中")
            description = rec.get("description", "")
            suggestions = rec.get("suggestions", [])

            suggestions_html = "<ul>"
            for suggestion in suggestions:
                suggestions_html += f"<li>{suggestion}</li>"
            suggestions_html += "</ul>"

            html += f"""
            <div class="recommendation">
                <h5>{category} (优先级: {priority})</h5>
                <p>{description}</p>
                <strong>建议措施:</strong>
                {suggestions_html}
            </div>
            """

        return html

    def _generate_compliance_section(self, compliance: dict) -> str:
        """生成合规性检查部分"""
        overall_compliant = compliance.get("overall_compliant", False)
        failed_requirements = compliance.get("failed_requirements", [])

        status_class = "compliant" if overall_compliant else "non-compliant"
        status_text = "合规" if overall_compliant else "不合规"

        html = f"""
        <h2>需求合规性检查</h2>
        <div class="compliance-check">
            <h4>总体状态: <span class="{status_class}">{status_text}</span></h4>
        """

        if failed_requirements:
            html += "<h5>未满足的需求:</h5><ul>"
            for req in failed_requirements:
                html += f"<li>{req}</li>"
            html += "</ul>"
        else:
            html += "<p>所有性能需求均已满足。</p>"

        html += "</div>"
        return html

    def _generate_system_info_section(self, system_info: dict) -> str:
        """生成系统信息部分"""
        return f"""
        <h2>系统信息</h2>
        <div class="system-info">
            <p>平台: {system_info.get("platform", "Unknown")}</p>
            <p>Python版本: {system_info.get("python_version", "Unknown")}</p>
            <p>CPU核心数: {system_info.get("cpu_count", "Unknown")}</p>
            <p>总内存: {system_info.get("memory_total_gb", 0):.1f} GB</p>
            <p>磁盘使用率: {system_info.get("disk_usage_percent", 0):.1f}%</p>
        </div>
        """

    def generate_json_report(self, report_data: dict, filename: str = None) -> str:
        """生成JSON格式报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"

        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        self.logger.info(f"JSON报告已生成: {filepath}")
        return str(filepath)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MiniCRM性能基准测试运行器")
    parser.add_argument(
        "--output-dir", default="reports", help="报告输出目录 (默认: reports)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "html", "both"],
        default="both",
        help="报告格式 (默认: both)",
    )
    parser.add_argument("--verbose", action="store_true", help="详细输出")

    args = parser.parse_args()

    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger("main")

    try:
        logger.info("开始MiniCRM性能基准测试...")

        # 创建测试套件
        suite = PerformanceBenchmarkSuite()

        # 运行所有基准测试
        logger.info("运行性能基准测试套件...")
        results = suite.run_all_benchmarks()

        # 生成性能报告
        logger.info("生成性能报告...")
        report_data = suite.generate_performance_report()

        # 创建报告生成器
        report_generator = PerformanceReportGenerator(args.output_dir)

        # 生成报告文件
        generated_files = []

        if args.format in ["json", "both"]:
            json_file = report_generator.generate_json_report(report_data)
            generated_files.append(json_file)

        if args.format in ["html", "both"]:
            html_file = report_generator.generate_html_report(report_data)
            generated_files.append(html_file)

        # 输出结果摘要
        print("\n" + "=" * 60)
        print("MiniCRM性能基准测试完成")
        print("=" * 60)

        summary = report_data.get("summary", {})
        print(f"总测试数: {summary.get('total_tests', 0)}")
        print(f"Qt成功率: {summary.get('qt_success_rate', 0):.1%}")
        print(f"TTK成功率: {summary.get('ttk_success_rate', 0):.1%}")

        # 输出合规性检查结果
        compliance = report_data.get("compliance_check", {})
        overall_compliant = compliance.get("overall_compliant", False)
        print(f"需求合规性: {'✓ 合规' if overall_compliant else '✗ 不合规'}")

        # 输出性能分析
        analysis = report_data.get("performance_analysis", {})
        assessment = analysis.get("overall_assessment", "未知")
        print(f"性能评估: {assessment}")

        bottlenecks = analysis.get("bottlenecks", [])
        if bottlenecks:
            print(f"发现瓶颈: {len(bottlenecks)}个")
        else:
            print("未发现明显瓶颈")

        # 输出生成的文件
        print("\n生成的报告文件:")
        for file_path in generated_files:
            print(f"  - {file_path}")

        print("\n性能基准测试完成！")

        # 如果有不合规的需求，返回非零退出码
        return 0 if overall_compliant else 1

    except Exception as e:
        logger.error(f"性能基准测试失败: {e}", exc_info=True)
        print(f"\n错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
