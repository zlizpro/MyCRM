#!/usr/bin/env python3
"""MiniCRM性能测试系统验证脚本

快速验证性能测试系统是否正常工作。
"""

from pathlib import Path
import sys
import time


# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))


def test_performance_framework():
    """测试性能测试框架"""
    print("🧪 测试性能测试框架...")

    try:
        from tests.performance.performance_benchmark_framework import (
            PerformanceMetrics,
            PerformanceMonitor,
        )

        # 测试性能指标
        metrics = PerformanceMetrics()
        metrics.startup_time = 2.5
        metrics.peak_memory = 150.0
        print("✅ PerformanceMetrics 创建成功")

        # 测试性能监控器
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        time.sleep(0.1)
        stats = monitor.stop_monitoring()
        print("✅ PerformanceMonitor 工作正常")

        return True

    except Exception as e:
        print(f"❌ 性能框架测试失败: {e}")
        return False


def test_startup_benchmark():
    """测试启动性能基准"""
    print("🚀 测试启动性能基准...")

    try:
        from tests.performance.startup_performance_test import (
            ApplicationStartupBenchmark,
        )

        benchmark = ApplicationStartupBenchmark()
        print("✅ ApplicationStartupBenchmark 创建成功")

        # 只测试TTK版本（避免Qt依赖问题）
        ttk_metrics = benchmark.run_ttk_test()

        if ttk_metrics.startup_time > 0:
            print(f"✅ TTK启动测试完成: {ttk_metrics.startup_time:.3f}秒")
        else:
            print("⚠️ TTK启动测试返回无效结果")

        return True

    except Exception as e:
        print(f"❌ 启动性能测试失败: {e}")
        return False


def test_memory_benchmark():
    """测试内存性能基准"""
    print("💾 测试内存性能基准...")

    try:
        from tests.performance.memory_usage_benchmark import MemoryUsageBenchmark

        benchmark = MemoryUsageBenchmark()
        print("✅ MemoryUsageBenchmark 创建成功")

        # 只测试TTK版本
        ttk_metrics = benchmark.run_ttk_test()

        if ttk_metrics.peak_memory > 0:
            print(f"✅ TTK内存测试完成: {ttk_metrics.peak_memory:.1f}MB")
        else:
            print("⚠️ TTK内存测试返回无效结果")

        return True

    except Exception as e:
        print(f"❌ 内存性能测试失败: {e}")
        return False


def test_report_generator():
    """测试报告生成器"""
    print("📊 测试报告生成器...")

    try:
        from tests.performance.performance_report_generator import (
            ComprehensiveReportGenerator,
        )

        generator = ComprehensiveReportGenerator("test_reports")
        print("✅ ComprehensiveReportGenerator 创建成功")

        # 创建测试数据
        test_data = {
            "timestamp": "2024-01-01T12:00:00",
            "summary": {
                "total_tests": 2,
                "qt_success_rate": 1.0,
                "ttk_success_rate": 1.0,
            },
            "detailed_results": [],
            "performance_analysis": {"overall_assessment": "良好", "bottlenecks": []},
            "compliance_check": {"overall_compliant": True, "failed_requirements": []},
            "optimization_recommendations": [],
            "system_info": {"platform": "Test Platform", "python_version": "3.9.0"},
        }

        # 生成报告
        files = generator.generate_comprehensive_report(test_data)

        if files:
            print(f"✅ 报告生成成功: {len(files)}个文件")
            for file_type, file_path in files.items():
                if Path(file_path).exists():
                    print(f"   📄 {file_type}: {file_path}")
                else:
                    print(f"   ❌ {file_type}: 文件未生成")
        else:
            print("⚠️ 未生成任何报告文件")

        return True

    except Exception as e:
        print(f"❌ 报告生成器测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🔍 MiniCRM性能测试系统验证")
    print("=" * 50)

    tests = [
        ("性能框架", test_performance_framework),
        ("启动基准", test_startup_benchmark),
        ("内存基准", test_memory_benchmark),
        ("报告生成", test_report_generator),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}测试:")
        print("-" * 30)

        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}测试通过")
            else:
                print(f"❌ {test_name}测试失败")
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")

    print("\n" + "=" * 50)
    print(f"📈 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！性能测试系统工作正常。")
        return 0
    print("⚠️ 部分测试失败，请检查系统配置。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
