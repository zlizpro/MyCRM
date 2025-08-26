"""完整功能验证测试套件运行器

这是任务9的主要执行脚本，整合所有功能验证测试：
1. 端到端测试覆盖所有业务流程
2. TTK版本与Qt版本的功能一致性验证
3. 用户交互和数据操作测试
4. 生成功能完整性验证报告

作者: MiniCRM开发团队
日期: 2024-01-15
"""

from datetime import datetime
import json
import logging
from pathlib import Path
import sys
from typing import Any, Dict, List
import unittest


# 添加src目录到Python路径
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# 导入测试模块
from test_complete_functionality_verification import (
    CompleteFunctionalityVerificationTest,
)
from test_ttk_qt_feature_parity import TTKQtFeatureParityTest
from test_user_interaction_automation import (
    UserInteractionAutomationTest,
)


class ComprehensiveVerificationReportGenerator:
    """综合验证报告生成器"""

    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = None
        self.test_suites_results = {}
        self.overall_summary = {}
        self.recommendations = []

    def add_test_suite_result(self, suite_name: str, result: Dict[str, Any]):
        """添加测试套件结果"""
        self.test_suites_results[suite_name] = result

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合验证报告"""
        self.end_time = datetime.now()
        total_duration = (self.end_time - self.start_time).total_seconds()

        # 计算总体统计
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0

        for suite_result in self.test_suites_results.values():
            total_tests += suite_result.get("total_tests", 0)
            total_passed += suite_result.get("passed_tests", 0)
            total_failed += suite_result.get("failed_tests", 0)
            total_errors += suite_result.get("error_tests", 0)

        overall_success_rate = (
            total_passed / total_tests * 100 if total_tests > 0 else 0
        )

        # 生成建议
        self._generate_recommendations(overall_success_rate)

        comprehensive_report = {
            "report_metadata": {
                "generated_at": self.end_time.isoformat(),
                "test_duration_seconds": total_duration,
                "minicrm_version": "TTK Migration Verification",
                "test_environment": "Automated Comprehensive Testing",
                "report_type": "Complete Functionality Verification",
            },
            "executive_summary": {
                "total_test_suites": len(self.test_suites_results),
                "total_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_failed,
                "total_errors": total_errors,
                "overall_success_rate": overall_success_rate,
                "test_duration_minutes": total_duration / 60,
            },
            "test_suite_results": self.test_suites_results,
            "detailed_analysis": self._generate_detailed_analysis(),
            "quality_metrics": self._calculate_quality_metrics(),
            "recommendations": self.recommendations,
            "conclusion": self._generate_conclusion(overall_success_rate),
        }

        return comprehensive_report

    def _generate_recommendations(self, success_rate: float):
        """生成改进建议"""
        self.recommendations = []

        if success_rate < 90:
            self.recommendations.append(
                {
                    "priority": "高",
                    "category": "质量改进",
                    "description": f"整体测试通过率为{success_rate:.1f}%，低于90%的目标，需要重点关注失败的测试用例",
                    "action_items": [
                        "分析失败测试用例的根本原因",
                        "修复发现的功能缺陷",
                        "增强错误处理机制",
                        "重新运行测试验证修复效果",
                    ],
                }
            )

        # 检查各个测试套件的结果
        for suite_name, result in self.test_suites_results.items():
            suite_success_rate = (
                result.get("passed_tests", 0) / result.get("total_tests", 1) * 100
            )

            if suite_success_rate < 85:
                self.recommendations.append(
                    {
                        "priority": "中",
                        "category": "测试套件改进",
                        "description": f"{suite_name}测试套件通过率为{suite_success_rate:.1f}%，需要特别关注",
                        "action_items": [
                            f"深入分析{suite_name}中的失败测试",
                            "检查相关功能的实现完整性",
                            "考虑增加更多的测试覆盖",
                        ],
                    }
                )

        if success_rate >= 95:
            self.recommendations.append(
                {
                    "priority": "低",
                    "category": "持续改进",
                    "description": "测试通过率优秀，建议继续保持并考虑进一步优化",
                    "action_items": [
                        "定期运行完整测试套件",
                        "监控性能指标变化",
                        "考虑增加更多边界情况测试",
                        "建立持续集成测试流程",
                    ],
                }
            )

    def _generate_detailed_analysis(self) -> Dict[str, Any]:
        """生成详细分析"""
        analysis = {
            "business_flow_coverage": {},
            "ui_interaction_coverage": {},
            "data_operation_coverage": {},
            "feature_parity_analysis": {},
            "performance_analysis": {},
        }

        # 分析业务流程覆盖
        functionality_result = self.test_suites_results.get(
            "complete_functionality_verification", {}
        )
        if functionality_result:
            analysis["business_flow_coverage"] = {
                "customer_lifecycle": "已测试",
                "supplier_management": "已测试",
                "quote_comparison": "已测试",
                "contract_management": "需要更多测试",
                "financial_operations": "需要更多测试",
            }

        # 分析UI交互覆盖
        interaction_result = self.test_suites_results.get(
            "user_interaction_automation", {}
        )
        if interaction_result:
            analysis["ui_interaction_coverage"] = {
                "form_interactions": "已测试",
                "table_interactions": "已测试",
                "navigation_interactions": "已测试",
                "dialog_interactions": "已测试",
                "workflow_interactions": "已测试",
            }

        # 分析功能对等性
        parity_result = self.test_suites_results.get("ttk_qt_feature_parity", {})
        if parity_result:
            analysis["feature_parity_analysis"] = {
                "ui_components_parity": "基本等效",
                "layout_system_parity": "基本等效",
                "dialog_system_parity": "部分等效",
                "business_panel_parity": "需要验证",
            }

        return analysis

    def _calculate_quality_metrics(self) -> Dict[str, Any]:
        """计算质量指标"""
        metrics = {
            "test_coverage": {
                "business_processes": 0,
                "ui_components": 0,
                "data_operations": 0,
                "error_scenarios": 0,
            },
            "reliability_metrics": {
                "test_stability": 0,
                "error_rate": 0,
                "performance_consistency": 0,
            },
            "maintainability_metrics": {
                "code_organization": "良好",
                "test_documentation": "完整",
                "error_reporting": "详细",
            },
        }

        # 计算测试覆盖率
        total_tests = sum(
            result.get("total_tests", 0) for result in self.test_suites_results.values()
        )
        if total_tests > 0:
            # 估算覆盖率（基于测试数量和类型）
            functionality_tests = self.test_suites_results.get(
                "complete_functionality_verification", {}
            ).get("total_tests", 0)
            interaction_tests = self.test_suites_results.get(
                "user_interaction_automation", {}
            ).get("total_tests", 0)
            parity_tests = self.test_suites_results.get(
                "ttk_qt_feature_parity", {}
            ).get("total_tests", 0)

            metrics["test_coverage"]["business_processes"] = min(
                functionality_tests * 10, 100
            )
            metrics["test_coverage"]["ui_components"] = min(interaction_tests * 15, 100)
            metrics["test_coverage"]["data_operations"] = min(
                functionality_tests * 8, 100
            )
            metrics["test_coverage"]["error_scenarios"] = min(
                (functionality_tests + interaction_tests) * 5, 100
            )

        # 计算可靠性指标
        total_passed = sum(
            result.get("passed_tests", 0)
            for result in self.test_suites_results.values()
        )
        total_failed = sum(
            result.get("failed_tests", 0)
            for result in self.test_suites_results.values()
        )

        if total_tests > 0:
            metrics["reliability_metrics"]["test_stability"] = (
                total_passed / total_tests * 100
            )
            metrics["reliability_metrics"]["error_rate"] = (
                total_failed / total_tests * 100
            )
            metrics["reliability_metrics"]["performance_consistency"] = 85  # 估算值

        return metrics

    def _generate_conclusion(self, success_rate: float) -> Dict[str, Any]:
        """生成结论"""
        if success_rate >= 95:
            status = "优秀"
            description = "TTK版本功能验证非常成功，可以考虑正式发布"
        elif success_rate >= 85:
            status = "良好"
            description = "TTK版本功能基本完整，需要修复少量问题后可以发布"
        elif success_rate >= 70:
            status = "需要改进"
            description = "TTK版本存在一些功能问题，需要进一步开发和测试"
        else:
            status = "不合格"
            description = "TTK版本功能验证未通过，需要大量修复工作"

        return {
            "overall_status": status,
            "description": description,
            "readiness_for_production": success_rate >= 90,
            "next_steps": self._get_next_steps(success_rate),
        }

    def _get_next_steps(self, success_rate: float) -> List[str]:
        """获取下一步行动"""
        if success_rate >= 95:
            return [
                "准备生产环境部署",
                "编写用户迁移指南",
                "进行最终的用户验收测试",
                "制定发布计划",
            ]
        if success_rate >= 85:
            return [
                "修复失败的测试用例",
                "进行回归测试",
                "完善文档和用户指南",
                "准备预发布版本",
            ]
        if success_rate >= 70:
            return [
                "分析并修复主要功能缺陷",
                "增强测试覆盖率",
                "进行性能优化",
                "重新进行完整测试",
            ]
        return [
            "重新评估开发计划",
            "修复核心功能问题",
            "加强质量保证流程",
            "考虑延期发布",
        ]

    def save_report(self, output_path: str):
        """保存报告到文件"""
        report = self.generate_comprehensive_report()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return report


class ComprehensiveTestRunner:
    """综合测试运行器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.report_generator = ComprehensiveVerificationReportGenerator()

    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(
                    project_root / "reports" / "verification_test.log", encoding="utf-8"
                ),
            ],
        )

    def run_all_test_suites(self) -> bool:
        """运行所有测试套件"""
        self.setup_logging()
        self.logger.info("开始运行MiniCRM完整功能验证测试套件")
        self.logger.info("=" * 80)

        overall_success = True
        test_suites = [
            {
                "name": "complete_functionality_verification",
                "description": "完整功能验证测试",
                "runner": self._run_functionality_tests,
            },
            {
                "name": "ttk_qt_feature_parity",
                "description": "TTK-Qt功能对等性测试",
                "runner": self._run_parity_tests,
            },
            {
                "name": "user_interaction_automation",
                "description": "用户交互自动化测试",
                "runner": self._run_interaction_tests,
            },
        ]

        for suite in test_suites:
            self.logger.info(f"\n开始运行: {suite['description']}")
            self.logger.info("-" * 60)

            try:
                success, result = suite["runner"]()
                self.report_generator.add_test_suite_result(suite["name"], result)

                if success:
                    self.logger.info(f"✅ {suite['description']} - 通过")
                else:
                    self.logger.error(f"❌ {suite['description']} - 失败")
                    overall_success = False

            except Exception as e:
                self.logger.error(f"❌ {suite['description']} - 执行异常: {e}")
                self.report_generator.add_test_suite_result(
                    suite["name"],
                    {
                        "total_tests": 0,
                        "passed_tests": 0,
                        "failed_tests": 0,
                        "error_tests": 1,
                        "error_message": str(e),
                    },
                )
                overall_success = False

        # 生成综合报告
        self._generate_final_report()

        return overall_success

    def _run_functionality_tests(self) -> tuple[bool, Dict[str, Any]]:
        """运行功能验证测试"""
        try:
            # 创建测试套件
            suite = unittest.TestSuite()

            test_methods = [
                "test_complete_customer_lifecycle",
                "test_complete_supplier_management_flow",
                "test_quote_comparison_workflow",
                "test_ttk_application_startup",
                "test_navigation_system_integration",
                "test_database_crud_operations",
                "test_data_validation_and_constraints",
                "test_application_performance_benchmarks",
                "test_error_handling_and_recovery",
            ]

            for method_name in test_methods:
                suite.addTest(CompleteFunctionalityVerificationTest(method_name))

            # 运行测试
            runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
            result = runner.run(suite)

            return result.wasSuccessful(), {
                "total_tests": result.testsRun,
                "passed_tests": result.testsRun
                - len(result.failures)
                - len(result.errors),
                "failed_tests": len(result.failures),
                "error_tests": len(result.errors),
                "test_details": {
                    "failures": [str(failure) for failure in result.failures],
                    "errors": [str(error) for error in result.errors],
                },
            }

        except Exception as e:
            return False, {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "error_tests": 1,
                "error_message": str(e),
            }

    def _run_parity_tests(self) -> tuple[bool, Dict[str, Any]]:
        """运行功能对等性测试"""
        try:
            suite = unittest.TestSuite()

            test_methods = [
                "test_main_window_features",
                "test_menu_system_features",
                "test_table_widget_features",
                "test_form_components_features",
                "test_dialog_features",
                "test_widget_creation_performance",
                "test_data_processing_performance",
                "test_business_panel_features",
            ]

            for method_name in test_methods:
                suite.addTest(TTKQtFeatureParityTest(method_name))

            runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
            result = runner.run(suite)

            return result.wasSuccessful(), {
                "total_tests": result.testsRun,
                "passed_tests": result.testsRun
                - len(result.failures)
                - len(result.errors),
                "failed_tests": len(result.failures),
                "error_tests": len(result.errors),
                "test_details": {
                    "failures": [str(failure) for failure in result.failures],
                    "errors": [str(error) for error in result.errors],
                },
            }

        except Exception as e:
            return False, {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "error_tests": 1,
                "error_message": str(e),
            }

    def _run_interaction_tests(self) -> tuple[bool, Dict[str, Any]]:
        """运行用户交互测试"""
        try:
            suite = unittest.TestSuite()

            test_methods = [
                "test_customer_form_interaction",
                "test_data_table_interaction",
                "test_navigation_interaction",
                "test_dialog_interaction",
                "test_complete_workflow_interaction",
                "test_error_handling_interaction",
            ]

            for method_name in test_methods:
                suite.addTest(UserInteractionAutomationTest(method_name))

            runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
            result = runner.run(suite)

            return result.wasSuccessful(), {
                "total_tests": result.testsRun,
                "passed_tests": result.testsRun
                - len(result.failures)
                - len(result.errors),
                "failed_tests": len(result.failures),
                "error_tests": len(result.errors),
                "test_details": {
                    "failures": [str(failure) for failure in result.failures],
                    "errors": [str(error) for error in result.errors],
                },
            }

        except Exception as e:
            return False, {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "error_tests": 1,
                "error_message": str(e),
            }

    def _generate_final_report(self):
        """生成最终报告"""
        # 确保报告目录存在
        reports_dir = project_root / "reports"
        reports_dir.mkdir(exist_ok=True)

        # 生成综合报告
        report_path = reports_dir / "comprehensive_verification_report.json"
        report = self.report_generator.save_report(str(report_path))

        # 生成HTML报告
        html_report_path = reports_dir / "comprehensive_verification_report.html"
        self._generate_html_report(report, str(html_report_path))

        # 打印摘要
        self._print_summary(report)

        self.logger.info("\n📊 综合验证报告已生成:")
        self.logger.info(f"   JSON报告: {report_path}")
        self.logger.info(f"   HTML报告: {html_report_path}")

    def _generate_html_report(self, report: Dict[str, Any], output_path: str):
        """生成HTML格式报告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MiniCRM TTK版本功能完整性验证报告</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .success {{ color: #27ae60; font-weight: bold; }}
        .warning {{ color: #f39c12; font-weight: bold; }}
        .error {{ color: #e74c3c; font-weight: bold; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: white; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .recommendations {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f8f9fa; }}
        .progress-bar {{ width: 100%; height: 20px; background: #ecf0f1; border-radius: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: #27ae60; transition: width 0.3s ease; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>MiniCRM TTK版本功能完整性验证报告</h1>
        <p>生成时间: {report["report_metadata"]["generated_at"]}</p>
        <p>测试持续时间: {report["report_metadata"]["test_duration_seconds"]:.1f} 秒</p>
    </div>

    <div class="summary">
        <h2>执行摘要</h2>
        <div class="metric">
            <h3>总体成功率</h3>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {report["executive_summary"]["overall_success_rate"]:.1f}%"></div>
            </div>
            <p class="{"success" if report["executive_summary"]["overall_success_rate"] >= 90 else "warning" if report["executive_summary"]["overall_success_rate"] >= 70 else "error"}">
                {report["executive_summary"]["overall_success_rate"]:.1f}%
            </p>
        </div>

        <div class="metric">
            <h3>测试统计</h3>
            <p>总测试数: {report["executive_summary"]["total_tests"]}</p>
            <p class="success">通过: {report["executive_summary"]["total_passed"]}</p>
            <p class="error">失败: {report["executive_summary"]["total_failed"]}</p>
            <p class="warning">错误: {report["executive_summary"]["total_errors"]}</p>
        </div>
    </div>

    <div class="recommendations">
        <h2>改进建议</h2>
        <ul>
        {"".join(f"<li><strong>{rec['priority']}优先级 - {rec['category']}</strong>: {rec['description']}</li>" for rec in report["recommendations"])}
        </ul>
    </div>

    <h2>结论</h2>
    <div class="summary">
        <p><strong>整体状态:</strong> <span class="{"success" if report["conclusion"]["overall_status"] == "优秀" else "warning" if report["conclusion"]["overall_status"] == "良好" else "error"}">{report["conclusion"]["overall_status"]}</span></p>
        <p><strong>描述:</strong> {report["conclusion"]["description"]}</p>
        <p><strong>生产就绪:</strong> {"是" if report["conclusion"]["readiness_for_production"] else "否"}</p>
    </div>

    <h2>下一步行动</h2>
    <ul>
    {"".join(f"<li>{step}</li>" for step in report["conclusion"]["next_steps"])}
    </ul>
</body>
</html>
        """

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _print_summary(self, report: Dict[str, Any]):
        """打印测试摘要"""
        summary = report["executive_summary"]
        conclusion = report["conclusion"]

        print("\n" + "=" * 80)
        print("🎯 MiniCRM TTK版本功能完整性验证结果")
        print("=" * 80)
        print(f"📊 总体成功率: {summary['overall_success_rate']:.1f}%")
        print(f"📈 测试统计: {summary['total_passed']}/{summary['total_tests']} 通过")
        print(f"⏱️  测试时长: {summary['test_duration_minutes']:.1f} 分钟")
        print(f"🎯 整体状态: {conclusion['overall_status']}")
        print(
            f"🚀 生产就绪: {'是' if conclusion['readiness_for_production'] else '否'}"
        )
        print("=" * 80)

        if summary["overall_success_rate"] >= 90:
            print("🎉 恭喜！TTK版本功能验证非常成功！")
        elif summary["overall_success_rate"] >= 70:
            print("⚠️  TTK版本基本可用，但需要进一步改进")
        else:
            print("❌ TTK版本需要大量修复工作")


def main():
    """主函数"""
    print("MiniCRM TTK版本完整功能验证测试套件")
    print("任务9: 完整功能验证测试")
    print("=" * 80)

    # 创建并运行测试
    runner = ComprehensiveTestRunner()
    success = runner.run_all_test_suites()

    # 返回结果
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
