#!/usr/bin/env python3
"""
紧急代码质量门禁脚本

这个脚本会运行所有必要的代码质量检查，
确保代码符合MiniCRM的开发标准。
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import json


class QualityGate:
    """代码质量门禁"""

    def __init__(self):
        self.ui_components_dir = Path("src/minicrm/ui/components")
        self.max_file_lines = 200
        self.warning_file_lines = 150

    def check_file_sizes(self) -> Tuple[bool, List[str]]:
        """检查文件大小"""
        print("📏 检查文件大小...")

        issues = []
        all_passed = True

        if not self.ui_components_dir.exists():
            issues.append(f"❌ 目录不存在: {self.ui_components_dir}")
            return False, issues

        for py_file in self.ui_components_dir.glob("**/*.py"):
            if py_file.name == "__init__.py":
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    line_count = len(f.readlines())

                if line_count > self.max_file_lines:
                    issues.append(
                        f"❌ {py_file.name}: {line_count}行 (超过{self.max_file_lines}行限制)"
                    )
                    all_passed = False
                elif line_count > self.warning_file_lines:
                    issues.append(f"⚠️  {py_file.name}: {line_count}行 (建议拆分)")
                else:
                    issues.append(f"✅ {py_file.name}: {line_count}行")

            except Exception as e:
                issues.append(f"❌ 检查 {py_file.name} 时出错: {e}")
                all_passed = False

        return all_passed, issues

    def run_ruff_check(self) -> Tuple[bool, List[str]]:
        """运行Ruff代码检查"""
        print("🔍 运行Ruff代码检查...")

        try:
            # 运行ruff检查
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "ruff",
                    "check",
                    str(self.ui_components_dir),
                    "--output-format=json",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                return True, ["✅ Ruff检查通过"]

            # 解析JSON输出
            issues = []
            try:
                ruff_output = json.loads(result.stdout)
                for issue in ruff_output:
                    filename = Path(issue["filename"]).name
                    line = issue["location"]["row"]
                    code = issue["code"]
                    message = issue["message"]
                    issues.append(f"❌ {filename}:{line} [{code}] {message}")
            except json.JSONDecodeError:
                # 如果不是JSON格式，直接显示输出
                issues = result.stdout.split("\n") if result.stdout else []
                if result.stderr:
                    issues.extend(result.stderr.split("\n"))

            return False, issues

        except subprocess.TimeoutExpired:
            return False, ["❌ Ruff检查超时"]
        except Exception as e:
            return False, [f"❌ 运行Ruff检查时出错: {e}"]

    def run_mypy_check(self) -> Tuple[bool, List[str]]:
        """运行MyPy类型检查"""
        print("🔍 运行MyPy类型检查...")

        try:
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "mypy",
                    str(self.ui_components_dir),
                    "--show-error-codes",
                    "--show-column-numbers",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                return True, ["✅ MyPy类型检查通过"]

            # 解析输出
            issues = []
            if result.stdout:
                for line in result.stdout.split("\n"):
                    if line.strip() and "error:" in line:
                        issues.append(f"❌ {line.strip()}")

            if result.stderr:
                for line in result.stderr.split("\n"):
                    if line.strip():
                        issues.append(f"⚠️  {line.strip()}")

            return False, issues

        except subprocess.TimeoutExpired:
            return False, ["❌ MyPy检查超时"]
        except Exception as e:
            return False, [f"❌ 运行MyPy检查时出错: {e}"]

    def check_transfunctions_usage(self) -> Tuple[bool, List[str]]:
        """检查transfunctions使用情况"""
        print("🔍 检查transfunctions使用情况...")

        try:
            # 运行transfunctions检查脚本
            result = subprocess.run(
                [sys.executable, "scripts/urgent_check_transfunctions.py"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            issues = []
            if result.stdout:
                issues.extend(result.stdout.split("\n"))

            if result.stderr:
                issues.extend(
                    [f"⚠️  {line}" for line in result.stderr.split("\n") if line.strip()]
                )

            # 简单检查：如果输出中包含"重复函数"，说明有问题
            has_duplicates = any("重复函数" in line for line in issues)

            return not has_duplicates, issues

        except subprocess.TimeoutExpired:
            return False, ["❌ Transfunctions检查超时"]
        except Exception as e:
            return False, [f"❌ 运行Transfunctions检查时出错: {e}"]

    def check_imports(self) -> Tuple[bool, List[str]]:
        """检查导入语句"""
        print("🔍 检查导入语句...")

        issues = []
        all_passed = True

        # 检查常见的导入问题
        required_typing_imports = ["Dict", "List", "Optional", "Any"]

        for py_file in self.ui_components_dir.glob("**/*.py"):
            if py_file.name == "__init__.py":
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # 检查是否使用了类型注解但没有导入
                for type_name in required_typing_imports:
                    if f": {type_name}[" in content or f"-> {type_name}[" in content:
                        if (
                            f"from typing import" not in content
                            or type_name not in content
                        ):
                            issues.append(
                                f"❌ {py_file.name}: 使用了{type_name}但未导入"
                            )
                            all_passed = False

                # 检查是否有未使用的导入
                if "from typing import" in content:
                    issues.append(f"✅ {py_file.name}: 有typing导入")

            except Exception as e:
                issues.append(f"❌ 检查 {py_file.name} 导入时出错: {e}")
                all_passed = False

        return all_passed, issues

    def run_all_checks(self) -> Dict[str, Tuple[bool, List[str]]]:
        """运行所有检查"""
        print("🚀 开始运行代码质量门禁检查...\n")

        checks = {
            "文件大小检查": self.check_file_sizes,
            "导入语句检查": self.check_imports,
            "Ruff代码检查": self.run_ruff_check,
            "MyPy类型检查": self.run_mypy_check,
            "Transfunctions使用检查": self.check_transfunctions_usage,
        }

        results = {}

        for check_name, check_func in checks.items():
            print(f"\n{'=' * 50}")
            print(f"🔍 {check_name}")
            print("=" * 50)

            try:
                passed, issues = check_func()
                results[check_name] = (passed, issues)

                if passed:
                    print(f"✅ {check_name} 通过")
                else:
                    print(f"❌ {check_name} 失败")

                # 显示详细信息
                for issue in issues[:10]:  # 只显示前10个问题
                    print(f"   {issue}")

                if len(issues) > 10:
                    print(f"   ... 还有 {len(issues) - 10} 个问题")

            except Exception as e:
                print(f"❌ 运行 {check_name} 时出错: {e}")
                results[check_name] = (False, [str(e)])

        return results

    def generate_report(self, results: Dict[str, Tuple[bool, List[str]]]) -> str:
        """生成检查报告"""
        report = []
        report.append("# MiniCRM UI组件代码质量检查报告\n")

        # 总结
        total_checks = len(results)
        passed_checks = sum(1 for passed, _ in results.values() if passed)

        report.append(f"## 检查总结\n")
        report.append(f"- 总检查项: {total_checks}")
        report.append(f"- 通过检查: {passed_checks}")
        report.append(f"- 失败检查: {total_checks - passed_checks}")
        report.append(f"- 通过率: {passed_checks / total_checks * 100:.1f}%\n")

        if passed_checks == total_checks:
            report.append("🎉 **所有检查都通过了！代码质量符合标准。**\n")
        else:
            report.append("🚨 **发现代码质量问题，需要立即修复！**\n")

        # 详细结果
        report.append("## 详细检查结果\n")

        for check_name, (passed, issues) in results.items():
            status = "✅ 通过" if passed else "❌ 失败"
            report.append(f"### {check_name} - {status}\n")

            if issues:
                for issue in issues:
                    report.append(f"- {issue}")
                report.append("")

        # 修复建议
        if passed_checks < total_checks:
            report.append("## 🛠️ 修复建议\n")

            for check_name, (passed, issues) in results.items():
                if not passed:
                    report.append(f"### {check_name}\n")

                    if "文件大小" in check_name:
                        report.append("**修复方法:**")
                        report.append(
                            "1. 运行 `python scripts/urgent_split_large_files.py`"
                        )
                        report.append("2. 按照生成的重构指南拆分文件")
                        report.append("3. 确保每个文件不超过200行\n")

                    elif "MyPy" in check_name:
                        report.append("**修复方法:**")
                        report.append("1. 运行 `python scripts/urgent_fix_qt_api.py`")
                        report.append("2. 添加缺失的typing导入")
                        report.append("3. 修复类型注解错误\n")

                    elif "Transfunctions" in check_name:
                        report.append("**修复方法:**")
                        report.append("1. 删除重复实现的函数")
                        report.append("2. 使用transfunctions中的对应函数")
                        report.append("3. 添加必要的导入语句\n")

                    elif "Ruff" in check_name:
                        report.append("**修复方法:**")
                        report.append(
                            "1. 运行 `uv run ruff check --fix src/minicrm/ui/components/`"
                        )
                        report.append(
                            "2. 运行 `uv run ruff format src/minicrm/ui/components/`"
                        )
                        report.append("3. 手动修复无法自动修复的问题\n")

        return "\n".join(report)


def main():
    """主函数"""
    gate = QualityGate()

    # 运行所有检查
    results = gate.run_all_checks()

    # 生成报告
    report = gate.generate_report(results)

    # 显示总结
    print(f"\n{'=' * 60}")
    print("📊 质量门禁检查完成")
    print("=" * 60)

    total_checks = len(results)
    passed_checks = sum(1 for passed, _ in results.values() if passed)

    print(f"通过检查: {passed_checks}/{total_checks}")

    if passed_checks == total_checks:
        print("🎉 所有检查都通过了！")
        print("✅ 代码质量符合MiniCRM开发标准")
        sys.exit(0)
    else:
        print("🚨 发现代码质量问题！")
        print("❌ 必须修复所有问题才能继续开发")

        # 保存详细报告
        report_file = Path("quality_gate_report.md")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📄 详细报告已保存到: {report_file}")
        sys.exit(1)


if __name__ == "__main__":
    main()
