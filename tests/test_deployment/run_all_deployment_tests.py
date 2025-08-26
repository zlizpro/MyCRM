"""部署测试套件运行器.

统一运行所有部署相关的测试，包括跨平台兼容性测试、
部署集成测试、端到端测试和性能基准测试。
"""

from pathlib import Path
import platform
import sys
import time


# 添加src目录到Python路径
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# 导入测试模块
from test_cross_platform_compatibility import run_compatibility_tests
from test_deployment_integration import run_deployment_tests
from test_end_to_end import run_end_to_end_tests
from test_performance_benchmarks import run_performance_benchmarks


class DeploymentTestRunner:
    """部署测试运行器."""

    def __init__(self):
        """初始化测试运行器."""
        self.project_root = project_root
        self.test_results = {}
        self.start_time = None
        self.end_time = None

        # 系统信息
        self.platform = platform.system()
        self.platform_version = platform.release()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.architecture = platform.machine()

    def print_system_info(self):
        """打印系统信息."""
        print("=" * 80)
        print("MiniCRM 部署测试套件")
        print("=" * 80)
        print(f"操作系统: {self.platform} {self.platform_version}")
        print(f"系统架构: {self.architecture}")
        print(f"Python版本: {self.python_version}")
        print(f"项目根目录: {self.project_root}")
        print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

    def run_test_suite(self, test_name: str, test_function) -> bool:
        """运行测试套件."""
        print(f"\n🧪 运行 {test_name}...")
        print("-" * 60)

        start_time = time.time()

        try:
            success = test_function()
            end_time = time.time()
            duration = end_time - start_time

            self.test_results[test_name] = {
                "success": success,
                "duration": duration,
                "error": None,
            }

            status = "✅ 通过" if success else "❌ 失败"
            print(f"\n{status} - {test_name} (耗时: {duration:.2f}秒)")

            return success

        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time

            self.test_results[test_name] = {
                "success": False,
                "duration": duration,
                "error": str(e),
            }

            print(f"\n❌ 错误 - {test_name}: {e}")
            return False

    def check_dependencies(self) -> bool:
        """检查测试依赖."""
        print("\n🔍 检查测试依赖...")

        required_modules = ["tkinter", "sqlite3", "unittest", "pathlib", "platform"]

        optional_modules = ["psutil", "matplotlib", "PIL"]

        missing_required = []
        missing_optional = []

        # 检查必需模块
        for module in required_modules:
            try:
                __import__(module)
                print(f"  ✅ {module}")
            except ImportError:
                missing_required.append(module)
                print(f"  ❌ {module} (必需)")

        # 检查可选模块
        for module in optional_modules:
            try:
                __import__(module)
                print(f"  ✅ {module}")
            except ImportError:
                missing_optional.append(module)
                print(f"  ⚠️  {module} (可选)")

        if missing_required:
            print(f"\n❌ 缺少必需依赖: {', '.join(missing_required)}")
            return False

        if missing_optional:
            print(f"\n⚠️  缺少可选依赖: {', '.join(missing_optional)}")
            print("   某些测试可能会跳过或功能受限")

        print("\n✅ 依赖检查完成")
        return True

    def run_pre_test_checks(self) -> bool:
        """运行测试前检查."""
        print("\n🔧 运行测试前检查...")

        checks = []

        # 检查项目结构
        required_paths = [
            self.project_root / "src" / "minicrm",
            self.project_root / "tests",
            self.project_root / "build",
        ]

        for path in required_paths:
            if path.exists():
                print(f"  ✅ {path.relative_to(self.project_root)}")
                checks.append(True)
            else:
                print(f"  ❌ {path.relative_to(self.project_root)} (不存在)")
                checks.append(False)

        # 检查Python路径
        if str(src_path) in sys.path:
            print("  ✅ Python路径配置正确")
            checks.append(True)
        else:
            print("  ❌ Python路径配置错误")
            checks.append(False)

        # 检查写入权限
        try:
            test_file = self.project_root / "test_write_permission.tmp"
            test_file.write_text("test")
            test_file.unlink()
            print("  ✅ 写入权限正常")
            checks.append(True)
        except Exception as e:
            print(f"  ❌ 写入权限错误: {e}")
            checks.append(False)

        all_passed = all(checks)
        if all_passed:
            print("\n✅ 测试前检查通过")
        else:
            print("\n❌ 测试前检查失败")

        return all_passed

    def run_all_tests(self) -> bool:
        """运行所有部署测试."""
        self.start_time = time.time()

        # 打印系统信息
        self.print_system_info()

        # 检查依赖
        if not self.check_dependencies():
            return False

        # 运行测试前检查
        if not self.run_pre_test_checks():
            return False

        # 定义测试套件
        test_suites = [
            ("跨平台兼容性测试", run_compatibility_tests),
            ("部署集成测试", run_deployment_tests),
            ("端到端测试", run_end_to_end_tests),
            ("性能基准测试", run_performance_benchmarks),
        ]

        # 运行所有测试套件
        all_success = True
        for test_name, test_function in test_suites:
            success = self.run_test_suite(test_name, test_function)
            if not success:
                all_success = False

        self.end_time = time.time()

        # 生成测试报告
        self.generate_test_report()

        return all_success

    def generate_test_report(self):
        """生成测试报告."""
        print("\n" + "=" * 80)
        print("测试报告")
        print("=" * 80)

        total_duration = (
            self.end_time - self.start_time if self.end_time and self.start_time else 0
        )

        # 统计信息
        total_tests = len(self.test_results)
        passed_tests = sum(
            1 for result in self.test_results.values() if result["success"]
        )
        failed_tests = total_tests - passed_tests

        print(f"总测试套件数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"总耗时: {total_duration:.2f}秒")
        print(f"成功率: {(passed_tests / total_tests * 100):.1f}%")

        # 详细结果
        print("\n详细结果:")
        print("-" * 60)

        for test_name, result in self.test_results.items():
            status = "✅ 通过" if result["success"] else "❌ 失败"
            duration = result["duration"]
            print(f"{status} {test_name:<30} ({duration:.2f}秒)")

            if result["error"]:
                print(f"     错误: {result['error']}")

        # 失败测试详情
        failed_tests_list = [
            name for name, result in self.test_results.items() if not result["success"]
        ]
        if failed_tests_list:
            print("\n失败的测试套件:")
            for test_name in failed_tests_list:
                error = self.test_results[test_name]["error"]
                print(f"  ❌ {test_name}")
                if error:
                    print(f"     原因: {error}")

        # 性能统计
        print("\n性能统计:")
        print("-" * 60)

        durations = [result["duration"] for result in self.test_results.values()]
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)

            print(f"平均耗时: {avg_duration:.2f}秒")
            print(f"最长耗时: {max_duration:.2f}秒")
            print(f"最短耗时: {min_duration:.2f}秒")

        # 系统信息
        print("\n系统信息:")
        print("-" * 60)
        print(f"操作系统: {self.platform} {self.platform_version}")
        print(f"系统架构: {self.architecture}")
        print(f"Python版本: {self.python_version}")

        # 建议
        print("\n建议:")
        print("-" * 60)

        if failed_tests == 0:
            print("🎉 所有测试通过！系统已准备好部署。")
        else:
            print("⚠️  存在失败的测试，建议在部署前解决以下问题：")
            for test_name in failed_tests_list:
                print(f"   - 修复 {test_name} 中的问题")

        # 保存报告到文件
        self.save_report_to_file()

    def save_report_to_file(self):
        """保存测试报告到文件."""
        try:
            report_dir = self.project_root / "reports"
            report_dir.mkdir(exist_ok=True)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            report_file = report_dir / f"deployment_test_report_{timestamp}.txt"

            with open(report_file, "w", encoding="utf-8") as f:
                f.write("MiniCRM 部署测试报告\n")
                f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"操作系统: {self.platform} {self.platform_version}\n")
                f.write(f"Python版本: {self.python_version}\n")
                f.write(f"系统架构: {self.architecture}\n\n")

                # 测试结果
                total_tests = len(self.test_results)
                passed_tests = sum(
                    1 for result in self.test_results.values() if result["success"]
                )

                f.write("测试统计:\n")
                f.write(f"  总测试套件数: {total_tests}\n")
                f.write(f"  通过: {passed_tests}\n")
                f.write(f"  失败: {total_tests - passed_tests}\n")
                f.write(f"  成功率: {(passed_tests / total_tests * 100):.1f}%\n\n")

                # 详细结果
                f.write("详细结果:\n")
                for test_name, result in self.test_results.items():
                    status = "通过" if result["success"] else "失败"
                    f.write(f"  {status}: {test_name} ({result['duration']:.2f}秒)\n")
                    if result["error"]:
                        f.write(f"    错误: {result['error']}\n")

            print(f"\n📄 测试报告已保存到: {report_file}")

        except Exception as e:
            print(f"\n⚠️  无法保存测试报告: {e}")

    def run_specific_test(self, test_name: str) -> bool:
        """运行特定的测试套件."""
        test_mapping = {
            "compatibility": ("跨平台兼容性测试", run_compatibility_tests),
            "deployment": ("部署集成测试", run_deployment_tests),
            "e2e": ("端到端测试", run_end_to_end_tests),
            "performance": ("性能基准测试", run_performance_benchmarks),
        }

        if test_name not in test_mapping:
            print(f"❌ 未知的测试套件: {test_name}")
            print(f"可用的测试套件: {', '.join(test_mapping.keys())}")
            return False

        self.print_system_info()

        if not self.check_dependencies():
            return False

        if not self.run_pre_test_checks():
            return False

        test_display_name, test_function = test_mapping[test_name]
        return self.run_test_suite(test_display_name, test_function)


def main():
    """主函数."""
    import argparse

    parser = argparse.ArgumentParser(description="MiniCRM部署测试套件运行器")
    parser.add_argument(
        "--test",
        choices=["compatibility", "deployment", "e2e", "performance", "all"],
        default="all",
        help="要运行的测试套件",
    )
    parser.add_argument("--verbose", action="store_true", help="显示详细输出")

    args = parser.parse_args()

    # 设置详细输出
    if args.verbose:
        import logging

        logging.basicConfig(level=logging.DEBUG)

    # 创建测试运行器
    runner = DeploymentTestRunner()

    # 运行测试
    if args.test == "all":
        success = runner.run_all_tests()
    else:
        success = runner.run_specific_test(args.test)

    # 返回退出代码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
