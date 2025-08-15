#!/usr/bin/env python3
"""
MiniCRM 代码覆盖率检查脚本

运行测试并生成代码覆盖率报告，确保代码质量标准。
"""

import subprocess
import sys
from pathlib import Path


class CoverageChecker:
    """代码覆盖率检查器"""

    def __init__(self, min_coverage: float = 80.0):
        """
        初始化覆盖率检查器

        Args:
            min_coverage: 最小覆盖率要求（百分比）
        """
        self.min_coverage = min_coverage
        self.project_root = Path.cwd()
        self.coverage_file = self.project_root / ".coverage"
        self.coverage_config = self.project_root / ".coveragerc"

    def run_tests_with_coverage(self) -> bool:
        """
        运行测试并收集覆盖率数据

        Returns:
            是否成功运行测试
        """
        print("🧪 运行测试并收集覆盖率数据...")

        try:
            # 清理之前的覆盖率数据
            if self.coverage_file.exists():
                self.coverage_file.unlink()

            # 运行pytest with coverage
            cmd = [
                "python",
                "-m",
                "pytest",
                "tests/",
                "--cov=src/minicrm",
                "--cov=src/transfunctions",
                "--cov-config=.coveragerc",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-report=xml:coverage.xml",
                "--cov-report=json:coverage.json",
                "-v",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ 测试运行成功")
                return True
            else:
                print("❌ 测试运行失败")
                print(f"错误输出: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ 运行测试时出错: {e}")
            return False

    def generate_coverage_report(self) -> dict | None:
        """
        生成覆盖率报告

        Returns:
            覆盖率数据字典，如果失败则返回None
        """
        print("📊 生成覆盖率报告...")

        try:
            # 生成终端报告
            cmd = ["python", "-m", "coverage", "report", "--show-missing"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"❌ 生成覆盖率报告失败: {result.stderr}")
                return None

            print("覆盖率报告:")
            print(result.stdout)

            # 获取总体覆盖率
            total_coverage = self._extract_total_coverage(result.stdout)

            return {
                "total_coverage": total_coverage,
                "report_output": result.stdout,
                "html_report": "htmlcov/index.html",
                "xml_report": "coverage.xml",
                "json_report": "coverage.json",
            }

        except Exception as e:
            print(f"❌ 生成覆盖率报告时出错: {e}")
            return None

    def _extract_total_coverage(self, report_output: str) -> float:
        """
        从覆盖率报告中提取总体覆盖率

        Args:
            report_output: 覆盖率报告输出

        Returns:
            总体覆盖率百分比
        """
        lines = report_output.strip().split("\n")
        for line in lines:
            if "TOTAL" in line:
                # 查找百分比
                parts = line.split()
                for part in parts:
                    if part.endswith("%"):
                        try:
                            return float(part[:-1])
                        except ValueError:
                            continue
        return 0.0

    def check_coverage_threshold(self, coverage_data: dict) -> bool:
        """
        检查覆盖率是否达到阈值

        Args:
            coverage_data: 覆盖率数据

        Returns:
            是否达到阈值
        """
        total_coverage = coverage_data.get("total_coverage", 0.0)

        print("\n📈 覆盖率检查结果:")
        print(f"   当前覆盖率: {total_coverage:.2f}%")
        print(f"   最低要求: {self.min_coverage:.2f}%")

        if total_coverage >= self.min_coverage:
            print("✅ 覆盖率达到要求")
            return True
        else:
            print("❌ 覆盖率未达到要求")
            print(f"   需要提高: {self.min_coverage - total_coverage:.2f}%")
            return False

    def generate_coverage_badge(self, coverage: float) -> str:
        """
        生成覆盖率徽章URL

        Args:
            coverage: 覆盖率百分比

        Returns:
            徽章URL
        """
        if coverage >= 90:
            color = "brightgreen"
        elif coverage >= 80:
            color = "green"
        elif coverage >= 70:
            color = "yellowgreen"
        elif coverage >= 60:
            color = "yellow"
        elif coverage >= 50:
            color = "orange"
        else:
            color = "red"

        return f"https://img.shields.io/badge/coverage-{coverage:.1f}%25-{color}"

    def create_coverage_summary(self, coverage_data: dict) -> str:
        """
        创建覆盖率摘要

        Args:
            coverage_data: 覆盖率数据

        Returns:
            覆盖率摘要文本
        """
        total_coverage = coverage_data.get("total_coverage", 0.0)
        badge_url = self.generate_coverage_badge(total_coverage)

        summary = f"""# 代码覆盖率报告

![Coverage Badge]({badge_url})

## 总体覆盖率: {total_coverage:.2f}%

### 报告文件
- HTML报告: {coverage_data.get("html_report", "N/A")}
- XML报告: {coverage_data.get("xml_report", "N/A")}
- JSON报告: {coverage_data.get("json_report", "N/A")}

### 覆盖率要求
- 最低要求: {self.min_coverage:.2f}%
- 当前状态: {"✅ 通过" if total_coverage >= self.min_coverage else "❌ 未通过"}

### 详细报告
```
{coverage_data.get("report_output", "")}
```

### 改进建议
"""

        if total_coverage < self.min_coverage:
            summary += f"""
- 当前覆盖率 ({total_coverage:.2f}%) 低于要求 ({self.min_coverage:.2f}%)
- 建议为未覆盖的代码添加测试用例
- 重点关注核心业务逻辑和关键功能
- 查看HTML报告了解具体未覆盖的代码行
"""
        else:
            summary += """
- 覆盖率已达到要求，继续保持
- 可以考虑提高覆盖率目标
- 关注代码质量，不仅仅是覆盖率数量
"""

        return summary

    def run_full_check(self) -> bool:
        """
        运行完整的覆盖率检查流程

        Returns:
            是否通过覆盖率检查
        """
        print("🚀 开始代码覆盖率检查...")
        print("=" * 50)

        # 1. 运行测试
        if not self.run_tests_with_coverage():
            return False

        # 2. 生成报告
        coverage_data = self.generate_coverage_report()
        if not coverage_data:
            return False

        # 3. 检查阈值
        threshold_passed = self.check_coverage_threshold(coverage_data)

        # 4. 生成摘要
        summary = self.create_coverage_summary(coverage_data)
        with open("coverage-summary.md", "w", encoding="utf-8") as f:
            f.write(summary)

        print("\n📄 覆盖率摘要已保存到: coverage-summary.md")

        return threshold_passed


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="MiniCRM 代码覆盖率检查")
    parser.add_argument(
        "--min-coverage",
        type=float,
        default=80.0,
        help="最小覆盖率要求（默认: 80.0）",
    )
    parser.add_argument(
        "--no-fail", action="store_true", help="即使覆盖率不足也不返回错误代码"
    )

    args = parser.parse_args()

    # 检查是否安装了必要的包
    required_packages = ["pytest", "pytest-cov", "coverage"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ 缺少必要的包，请安装:")
        print(f"   uv add --dev {' '.join(missing_packages)}")
        sys.exit(1)

    # 运行覆盖率检查
    checker = CoverageChecker(min_coverage=args.min_coverage)
    success = checker.run_full_check()

    if success:
        print("\n🎉 代码覆盖率检查通过！")
        sys.exit(0)
    else:
        print("\n💥 代码覆盖率检查失败！")
        if not args.no_fail:
            sys.exit(1)


if __name__ == "__main__":
    main()
