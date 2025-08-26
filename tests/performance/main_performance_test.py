"""MiniCRM主性能测试运行器

为任务10提供完整的性能基准测试执行：
- 集成所有性能测试模块
- 自动运行Qt vs TTK性能对比
- 生成综合性能报告
- 提供性能优化建议和行动计划

使用方法:
    python main_performance_test.py [选项]

作者: MiniCRM开发团队
"""

import argparse
import logging
from pathlib import Path
import sys
import time
from typing import Dict, List, Tuple


# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from tests.performance.memory_usage_benchmark import MemoryUsageBenchmark
from tests.performance.performance_benchmark_framework import (
    BenchmarkResult,
    PerformanceBenchmarkSuite,
    PerformanceMetrics,
)
from tests.performance.performance_report_generator import ComprehensiveReportGenerator
from tests.performance.startup_performance_test import ApplicationStartupBenchmark


class MiniCRMPerformanceTestSuite:
    """MiniCRM完整性能测试套件"""

    def __init__(self, verbose: bool = False):
        """初始化测试套件

        Args:
            verbose: 是否详细输出
        """
        self.verbose = verbose
        self.logger = logging.getLogger(self.__class__.__name__)

        # 性能要求基准（来自需求11.1-11.6）
        self.performance_requirements = {
            "max_startup_time": 3.0,  # 启动时间不超过3秒
            "max_response_time": 0.2,  # 响应时间不超过200毫秒
            "max_memory_mb": 200.0,  # 内存占用不超过200MB
            "max_cpu_percent": 10.0,  # CPU占用不超过10%
            "min_page_switch_speed": 0.1,  # 页面切换在100毫秒内
            "min_operations_per_second": 100.0,  # 最小操作速度
        }

        # 测试结果
        self.test_results: List[Tuple[BenchmarkResult, BenchmarkResult]] = []
        self.test_summary: Dict[str, any] = {}

    def run_comprehensive_performance_tests(self) -> Dict[str, any]:
        """运行综合性能测试"""
        self.logger.info("开始MiniCRM综合性能测试...")

        start_time = time.time()

        try:
            # 1. 运行启动性能测试
            self.logger.info("=" * 60)
            self.logger.info("1. 启动性能测试")
            self.logger.info("=" * 60)
            startup_results = self._run_startup_performance_test()

            # 2. 运行内存使用测试
            self.logger.info("=" * 60)
            self.logger.info("2. 内存使用性能测试")
            self.logger.info("=" * 60)
            memory_results = self._run_memory_usage_test()

            # 3. 运行UI响应性能测试
            self.logger.info("=" * 60)
            self.logger.info("3. UI响应性能测试")
            self.logger.info("=" * 60)
            ui_results = self._run_ui_response_test()

            # 4. 运行数据处理性能测试
            self.logger.info("=" * 60)
            self.logger.info("4. 数据处理性能测试")
            self.logger.info("=" * 60)
            data_results = self._run_data_processing_test()

            # 5. 运行综合压力测试
            self.logger.info("=" * 60)
            self.logger.info("5. 综合压力测试")
            self.logger.info("=" * 60)
            stress_results = self._run_stress_test()

            # 收集所有结果
            all_results = [
                startup_results,
                memory_results,
                ui_results,
                data_results,
                stress_results,
            ]

            # 生成测试摘要
            total_time = time.time() - start_time
            self.test_summary = self._generate_test_summary(all_results, total_time)

            # 生成综合报告数据
            report_data = self._generate_comprehensive_report_data(all_results)

            self.logger.info("=" * 60)
            self.logger.info("MiniCRM综合性能测试完成")
            self.logger.info("=" * 60)

            return report_data

        except Exception as e:
            self.logger.error(f"综合性能测试失败: {e}", exc_info=True)
            raise

    def _run_startup_performance_test(self) -> Tuple[BenchmarkResult, BenchmarkResult]:
        """运行启动性能测试"""
        try:
            benchmark = ApplicationStartupBenchmark()
            qt_result, ttk_result = benchmark.run_benchmark()

            # 输出结果摘要
            self._log_test_summary("启动性能", qt_result, ttk_result)

            # 验证性能要求
            self._validate_startup_requirements(ttk_result)

            return qt_result, ttk_result

        except Exception as e:
            self.logger.error(f"启动性能测试失败: {e}")
            raise

    def _run_memory_usage_test(self) -> Tuple[BenchmarkResult, BenchmarkResult]:
        """运行内存使用测试"""
        try:
            benchmark = MemoryUsageBenchmark()
            qt_result, ttk_result = benchmark.run_benchmark()

            # 输出结果摘要
            self._log_test_summary("内存使用", qt_result, ttk_result)

            # 验证性能要求
            self._validate_memory_requirements(ttk_result)

            return qt_result, ttk_result

        except Exception as e:
            self.logger.error(f"内存使用测试失败: {e}")
            raise

    def _run_ui_response_test(self) -> Tuple[BenchmarkResult, BenchmarkResult]:
        """运行UI响应测试"""
        try:
            from tests.performance.performance_benchmark_framework import (
                UIResponseBenchmark,
            )

            benchmark = UIResponseBenchmark()
            qt_result, ttk_result = benchmark.run_benchmark()

            # 输出结果摘要
            self._log_test_summary("UI响应", qt_result, ttk_result)

            # 验证性能要求
            self._validate_ui_requirements(ttk_result)

            return qt_result, ttk_result

        except Exception as e:
            self.logger.error(f"UI响应测试失败: {e}")
            raise

    def _run_data_processing_test(self) -> Tuple[BenchmarkResult, BenchmarkResult]:
        """运行数据处理测试"""
        try:
            from tests.performance.performance_benchmark_framework import (
                DataLoadBenchmark,
            )

            benchmark = DataLoadBenchmark()
            qt_result, ttk_result = benchmark.run_benchmark()

            # 输出结果摘要
            self._log_test_summary("数据处理", qt_result, ttk_result)

            # 验证性能要求
            self._validate_data_requirements(ttk_result)

            return qt_result, ttk_result

        except Exception as e:
            self.logger.error(f"数据处理测试失败: {e}")
            raise

    def _run_stress_test(self) -> Tuple[BenchmarkResult, BenchmarkResult]:
        """运行压力测试"""
        try:
            # 创建压力测试基准
            benchmark = self._create_stress_benchmark()
            qt_result, ttk_result = benchmark.run_benchmark()

            # 输出结果摘要
            self._log_test_summary("压力测试", qt_result, ttk_result)

            return qt_result, ttk_result

        except Exception as e:
            self.logger.error(f"压力测试失败: {e}")
            raise

    def _create_stress_benchmark(self):
        """创建压力测试基准"""
        from tests.performance.performance_benchmark_framework import BaseBenchmark

        class StressBenchmark(BaseBenchmark):
            def __init__(self):
                super().__init__("stress_test")

            def run_qt_test(self) -> PerformanceMetrics:
                metrics = PerformanceMetrics()
                try:
                    # 模拟Qt压力测试
                    start_time = time.time()

                    # 创建大量对象
                    objects = []
                    for i in range(10000):
                        obj = {
                            "id": i,
                            "data": f"test_data_{i}" * 10,
                            "timestamp": time.time(),
                        }
                        objects.append(obj)

                    # 模拟处理操作
                    processed = 0
                    for obj in objects:
                        if obj["id"] % 2 == 0:
                            obj["processed"] = True
                            processed += 1

                    metrics.operations_per_second = processed / (
                        time.time() - start_time
                    )

                    # 清理
                    objects.clear()

                except Exception as e:
                    self.logger.error(f"Qt压力测试失败: {e}")

                return metrics

            def run_ttk_test(self) -> PerformanceMetrics:
                metrics = PerformanceMetrics()
                try:
                    import tkinter as tk
                    from tkinter import ttk

                    # 创建测试环境
                    root = tk.Tk()
                    root.withdraw()

                    start_time = time.time()

                    # 创建大量UI组件
                    components = []
                    for i in range(1000):
                        frame = ttk.Frame(root)
                        label = ttk.Label(frame, text=f"压力测试{i}")
                        entry = ttk.Entry(frame)
                        components.extend([frame, label, entry])

                    # 模拟操作
                    operations = 0
                    for component in components:
                        if isinstance(component, ttk.Entry):
                            component.insert(0, "test")
                            operations += 1
                        elif isinstance(component, ttk.Label):
                            component.config(text="updated")
                            operations += 1

                    test_time = time.time() - start_time
                    metrics.operations_per_second = (
                        operations / test_time if test_time > 0 else 0
                    )

                    # 清理
                    for component in components:
                        try:
                            component.destroy()
                        except:
                            pass
                    root.destroy()

                except Exception as e:
                    self.logger.error(f"TTK压力测试失败: {e}")

                return metrics

        return StressBenchmark()

    def _log_test_summary(
        self, test_name: str, qt_result: BenchmarkResult, ttk_result: BenchmarkResult
    ) -> None:
        """记录测试摘要"""
        self.logger.info(f"\n{test_name}测试结果:")
        self.logger.info("-" * 40)

        if qt_result.success and ttk_result.success:
            # 启动时间对比
            if (
                hasattr(qt_result.metrics, "startup_time")
                and qt_result.metrics.startup_time > 0
            ):
                qt_time = qt_result.metrics.startup_time
                ttk_time = ttk_result.metrics.startup_time
                improvement = (
                    ((qt_time - ttk_time) / qt_time * 100) if qt_time > 0 else 0
                )

                self.logger.info(
                    f"启动时间: Qt={qt_time:.3f}s, TTK={ttk_time:.3f}s "
                    f"({'改善' if improvement > 0 else '退化'}{abs(improvement):.1f}%)"
                )

            # 内存使用对比
            if qt_result.metrics.peak_memory > 0 and ttk_result.metrics.peak_memory > 0:
                qt_memory = qt_result.metrics.peak_memory
                ttk_memory = ttk_result.metrics.peak_memory
                memory_diff = ttk_memory - qt_memory

                self.logger.info(
                    f"峰值内存: Qt={qt_memory:.1f}MB, TTK={ttk_memory:.1f}MB "
                    f"({'增加' if memory_diff > 0 else '减少'}{abs(memory_diff):.1f}MB)"
                )

            # 操作性能对比
            if (
                qt_result.metrics.operations_per_second > 0
                and ttk_result.metrics.operations_per_second > 0
            ):
                qt_ops = qt_result.metrics.operations_per_second
                ttk_ops = ttk_result.metrics.operations_per_second
                ops_improvement = (
                    ((ttk_ops - qt_ops) / qt_ops * 100) if qt_ops > 0 else 0
                )

                self.logger.info(
                    f"操作速度: Qt={qt_ops:.0f}ops/s, TTK={ttk_ops:.0f}ops/s "
                    f"({'改善' if ops_improvement > 0 else '退化'}{abs(ops_improvement):.1f}%)"
                )
        else:
            if not qt_result.success:
                self.logger.warning(f"Qt测试失败: {qt_result.error_message}")
            if not ttk_result.success:
                self.logger.warning(f"TTK测试失败: {ttk_result.error_message}")

    def _validate_startup_requirements(self, result: BenchmarkResult) -> None:
        """验证启动性能要求"""
        if not result.success:
            return

        startup_time = result.metrics.startup_time
        requirement = self.performance_requirements["max_startup_time"]

        if startup_time <= requirement:
            self.logger.info(
                f"✓ 启动时间要求满足: {startup_time:.3f}s ≤ {requirement}s"
            )
        else:
            self.logger.warning(
                f"✗ 启动时间要求不满足: {startup_time:.3f}s > {requirement}s"
            )

    def _validate_memory_requirements(self, result: BenchmarkResult) -> None:
        """验证内存性能要求"""
        if not result.success:
            return

        peak_memory = result.metrics.peak_memory
        requirement = self.performance_requirements["max_memory_mb"]

        if peak_memory <= requirement:
            self.logger.info(
                f"✓ 内存使用要求满足: {peak_memory:.1f}MB ≤ {requirement}MB"
            )
        else:
            self.logger.warning(
                f"✗ 内存使用要求不满足: {peak_memory:.1f}MB > {requirement}MB"
            )

    def _validate_ui_requirements(self, result: BenchmarkResult) -> None:
        """验证UI性能要求"""
        if not result.success:
            return

        response_time = result.metrics.ui_response_time
        requirement = self.performance_requirements["max_response_time"]

        if response_time <= requirement:
            self.logger.info(
                f"✓ UI响应要求满足: {response_time * 1000:.1f}ms ≤ {requirement * 1000:.1f}ms"
            )
        else:
            self.logger.warning(
                f"✗ UI响应要求不满足: {response_time * 1000:.1f}ms > {requirement * 1000:.1f}ms"
            )

    def _validate_data_requirements(self, result: BenchmarkResult) -> None:
        """验证数据处理要求"""
        if not result.success:
            return

        ops_per_second = result.metrics.operations_per_second
        requirement = self.performance_requirements["min_operations_per_second"]

        if ops_per_second >= requirement:
            self.logger.info(
                f"✓ 数据处理要求满足: {ops_per_second:.0f}ops/s ≥ {requirement}ops/s"
            )
        else:
            self.logger.warning(
                f"✗ 数据处理要求不满足: {ops_per_second:.0f}ops/s < {requirement}ops/s"
            )

    def _generate_test_summary(
        self,
        all_results: List[Tuple[BenchmarkResult, BenchmarkResult]],
        total_time: float,
    ) -> Dict[str, any]:
        """生成测试摘要"""
        total_tests = len(all_results)
        successful_qt = sum(1 for qt_result, _ in all_results if qt_result.success)
        successful_ttk = sum(1 for _, ttk_result in all_results if ttk_result.success)

        # 计算性能改善统计
        improvements = {
            "startup_time": [],
            "memory_usage": [],
            "response_time": [],
            "operations_speed": [],
        }

        for qt_result, ttk_result in all_results:
            if qt_result.success and ttk_result.success:
                # 启动时间改善
                if (
                    qt_result.metrics.startup_time > 0
                    and ttk_result.metrics.startup_time > 0
                ):
                    improvement = (
                        (
                            qt_result.metrics.startup_time
                            - ttk_result.metrics.startup_time
                        )
                        / qt_result.metrics.startup_time
                        * 100
                    )
                    improvements["startup_time"].append(improvement)

                # 内存使用变化
                if (
                    qt_result.metrics.peak_memory > 0
                    and ttk_result.metrics.peak_memory > 0
                ):
                    change = (
                        (ttk_result.metrics.peak_memory - qt_result.metrics.peak_memory)
                        / qt_result.metrics.peak_memory
                        * 100
                    )
                    improvements["memory_usage"].append(change)

                # 响应时间改善
                if (
                    qt_result.metrics.ui_response_time > 0
                    and ttk_result.metrics.ui_response_time > 0
                ):
                    improvement = (
                        (
                            qt_result.metrics.ui_response_time
                            - ttk_result.metrics.ui_response_time
                        )
                        / qt_result.metrics.ui_response_time
                        * 100
                    )
                    improvements["response_time"].append(improvement)

                # 操作速度改善
                if (
                    qt_result.metrics.operations_per_second > 0
                    and ttk_result.metrics.operations_per_second > 0
                ):
                    improvement = (
                        (
                            ttk_result.metrics.operations_per_second
                            - qt_result.metrics.operations_per_second
                        )
                        / qt_result.metrics.operations_per_second
                        * 100
                    )
                    improvements["operations_speed"].append(improvement)

        return {
            "total_tests": total_tests,
            "successful_qt_tests": successful_qt,
            "successful_ttk_tests": successful_ttk,
            "qt_success_rate": successful_qt / total_tests if total_tests > 0 else 0,
            "ttk_success_rate": successful_ttk / total_tests if total_tests > 0 else 0,
            "total_test_time": total_time,
            "performance_improvements": improvements,
            "requirements_compliance": self._check_requirements_compliance(all_results),
        }

    def _check_requirements_compliance(
        self, all_results: List[Tuple[BenchmarkResult, BenchmarkResult]]
    ) -> Dict[str, any]:
        """检查需求合规性"""
        compliance = {
            "overall_compliant": True,
            "failed_requirements": [],
            "requirement_details": {},
        }

        for qt_result, ttk_result in all_results:
            if not ttk_result.success:
                continue

            test_name = ttk_result.test_name

            # 检查启动时间要求
            if (
                ttk_result.metrics.startup_time
                > self.performance_requirements["max_startup_time"]
            ):
                compliance["failed_requirements"].append(
                    f"{test_name}: 启动时间超过3秒"
                )
                compliance["overall_compliant"] = False

            # 检查内存使用要求
            if (
                ttk_result.metrics.peak_memory
                > self.performance_requirements["max_memory_mb"]
            ):
                compliance["failed_requirements"].append(
                    f"{test_name}: 内存使用超过200MB"
                )
                compliance["overall_compliant"] = False

            # 检查响应时间要求
            if (
                ttk_result.metrics.ui_response_time
                > self.performance_requirements["max_response_time"]
            ):
                compliance["failed_requirements"].append(
                    f"{test_name}: 响应时间超过200ms"
                )
                compliance["overall_compliant"] = False

            # 记录详细信息
            compliance["requirement_details"][test_name] = {
                "startup_time_compliant": ttk_result.metrics.startup_time
                <= self.performance_requirements["max_startup_time"],
                "memory_compliant": ttk_result.metrics.peak_memory
                <= self.performance_requirements["max_memory_mb"],
                "response_time_compliant": ttk_result.metrics.ui_response_time
                <= self.performance_requirements["max_response_time"],
            }

        return compliance

    def _generate_comprehensive_report_data(
        self, all_results: List[Tuple[BenchmarkResult, BenchmarkResult]]
    ) -> Dict[str, any]:
        """生成综合报告数据"""
        # 使用现有的PerformanceBenchmarkSuite来生成报告结构
        suite = PerformanceBenchmarkSuite()
        suite.results = all_results

        # 生成基础报告
        report_data = suite.generate_performance_report()

        # 添加额外的摘要信息
        report_data["test_execution_summary"] = self.test_summary

        # 添加详细的性能分析
        report_data["detailed_performance_analysis"] = self._generate_detailed_analysis(
            all_results
        )

        return report_data

    def _generate_detailed_analysis(
        self, all_results: List[Tuple[BenchmarkResult, BenchmarkResult]]
    ) -> Dict[str, any]:
        """生成详细性能分析"""
        analysis = {
            "performance_trends": {},
            "bottleneck_analysis": {},
            "optimization_opportunities": [],
            "risk_assessment": {},
        }

        # 分析性能趋势
        for qt_result, ttk_result in all_results:
            if qt_result.success and ttk_result.success:
                test_name = qt_result.test_name

                # 性能趋势分析
                analysis["performance_trends"][test_name] = {
                    "startup_time_trend": "improved"
                    if ttk_result.metrics.startup_time < qt_result.metrics.startup_time
                    else "degraded",
                    "memory_trend": "improved"
                    if ttk_result.metrics.peak_memory < qt_result.metrics.peak_memory
                    else "degraded",
                    "overall_trend": "positive"
                    if (
                        ttk_result.metrics.startup_time < qt_result.metrics.startup_time
                        and ttk_result.metrics.peak_memory
                        < qt_result.metrics.peak_memory
                    )
                    else "mixed",
                }

                # 瓶颈分析
                bottlenecks = []
                if ttk_result.metrics.startup_time > 2.0:
                    bottlenecks.append("启动时间较长")
                if ttk_result.metrics.peak_memory > 150.0:
                    bottlenecks.append("内存使用较高")
                if ttk_result.metrics.ui_response_time > 0.1:
                    bottlenecks.append("UI响应较慢")

                analysis["bottleneck_analysis"][test_name] = bottlenecks

        # 优化机会识别
        for qt_result, ttk_result in all_results:
            if ttk_result.success:
                test_name = ttk_result.test_name

                if ttk_result.metrics.startup_time > 1.5:
                    analysis["optimization_opportunities"].append(
                        {
                            "area": f"{test_name} - 启动优化",
                            "current_value": f"{ttk_result.metrics.startup_time:.3f}s",
                            "target_value": "< 1.5s",
                            "priority": "high"
                            if ttk_result.metrics.startup_time > 2.5
                            else "medium",
                        }
                    )

                if ttk_result.metrics.peak_memory > 100.0:
                    analysis["optimization_opportunities"].append(
                        {
                            "area": f"{test_name} - 内存优化",
                            "current_value": f"{ttk_result.metrics.peak_memory:.1f}MB",
                            "target_value": "< 100MB",
                            "priority": "high"
                            if ttk_result.metrics.peak_memory > 150.0
                            else "medium",
                        }
                    )

        return analysis


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MiniCRM主性能测试运行器")
    parser.add_argument(
        "--output-dir", default="reports", help="报告输出目录 (默认: reports)"
    )
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--no-charts", action="store_true", help="不生成图表")
    parser.add_argument("--no-pdf", action="store_true", help="不生成PDF报告")

    args = parser.parse_args()

    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger("main")

    try:
        print("🚀 开始MiniCRM性能基准测试...")
        print("=" * 80)

        # 创建测试套件
        test_suite = MiniCRMPerformanceTestSuite(verbose=args.verbose)

        # 运行综合性能测试
        logger.info("运行综合性能测试套件...")
        report_data = test_suite.run_comprehensive_performance_tests()

        # 生成报告
        logger.info("生成性能报告...")
        report_generator = ComprehensiveReportGenerator(args.output_dir)

        generated_files = report_generator.generate_comprehensive_report(
            report_data, include_charts=not args.no_charts, include_pdf=not args.no_pdf
        )

        # 输出测试结果摘要
        print("\n" + "=" * 80)
        print("🎯 MiniCRM性能基准测试完成")
        print("=" * 80)

        summary = report_data.get("summary", {})
        print(f"📊 总测试数: {summary.get('total_tests', 0)}")
        print(f"📈 Qt成功率: {summary.get('qt_success_rate', 0):.1%}")
        print(f"📈 TTK成功率: {summary.get('ttk_success_rate', 0):.1%}")

        # 输出合规性检查结果
        compliance = report_data.get("compliance_check", {})
        overall_compliant = compliance.get("overall_compliant", False)
        print(f"✅ 需求合规性: {'合规' if overall_compliant else '不合规'}")

        if not overall_compliant:
            failed_count = len(compliance.get("failed_requirements", []))
            print(f"⚠️  未满足需求: {failed_count}项")

        # 输出性能分析
        analysis = report_data.get("performance_analysis", {})
        assessment = analysis.get("overall_assessment", "未知")
        print(f"🎖️  性能评估: {assessment}")

        bottlenecks = analysis.get("bottlenecks", [])
        if bottlenecks:
            print(f"🔍 发现瓶颈: {len(bottlenecks)}个")
        else:
            print("✨ 未发现明显瓶颈")

        # 输出生成的文件
        print("\n📁 生成的报告文件:")
        for file_type, file_path in generated_files.items():
            print(f"   📄 {file_type.upper()}: {file_path}")

        # 输出优化建议摘要
        recommendations = report_data.get("optimization_recommendations", [])
        if recommendations:
            print(f"\n💡 优化建议: {len(recommendations)}项")
            for i, rec in enumerate(recommendations[:3], 1):  # 只显示前3项
                priority = rec.get("priority", "中")
                category = rec.get("category", "未分类")
                print(f"   {i}. {category} (优先级: {priority})")

        print("\n🎉 性能基准测试完成！")

        # 如果有不合规的需求，返回非零退出码
        return 0 if overall_compliant else 1

    except KeyboardInterrupt:
        logger.info("用户中断测试")
        print("\n⏹️  测试被用户中断")
        return 130

    except Exception as e:
        logger.error(f"性能基准测试失败: {e}", exc_info=True)
        print(f"\n❌ 错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
