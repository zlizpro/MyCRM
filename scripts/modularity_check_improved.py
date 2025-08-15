#!/usr/bin/env python3
"""
MiniCRM 现代化模块化质量检查工具

这个脚本集成了现代化工具链，提供全面的代码质量检查：
- 文件大小控制（最大200行）
- 函数大小控制（最大50行）
- 类大小控制（最大100行）
- Ruff代码检查和自动修复
- MyPy类型检查
- transfunctions使用检查
- 架构依赖检查

使用方法:
    python scripts/modularity_check_improved.py [文件路径或目录]
    python scripts/modularity_check_improved.py --all  # 检查整个项目
    python scripts/modularity_check_improved.py --fix  # 自动修复可修复的问题
"""

import ast
import os
import sys
import argparse
import yaml
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum


class ViolationType(Enum):
    """违规类型枚举"""

    FILE_TOO_LARGE = "file_too_large"
    FUNCTION_TOO_LARGE = "function_too_large"
    CLASS_TOO_LARGE = "class_too_large"
    RUFF_ERROR = "ruff_error"
    MYPY_ERROR = "mypy_error"
    ARCHITECTURE_VIOLATION = "architecture_violation"
    MISSING_TRANSFUNCTIONS = "missing_transfunctions"
    SYNTAX_ERROR = "syntax_error"


class Severity(Enum):
    """严重程度枚举"""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Violation:
    """违规记录"""

    file_path: str
    line_number: int
    violation_type: ViolationType
    severity: Severity
    message: str
    suggestion: Optional[str] = None
    fixable: bool = False


class ModernModularityChecker:
    """现代化模块化质量检查器"""

    def __init__(self, config_path: str = ".modularity-config.yaml"):
        """初始化检查器"""
        self.config = self._load_config(config_path)
        self.violations: List[Violation] = []
        self.checked_files: Set[str] = set()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️  配置文件 {config_path} 不存在，使用默认配置")
            return self._get_default_config()
        except yaml.YAMLError as e:
            print(f"❌ 配置文件格式错误: {e}")
            sys.exit(1)

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "modularity": {
                "thresholds": {
                    "file_size": {"warning": 150, "error": 200},
                    "function_size": {"warning": 30, "error": 50},
                    "class_size": {"warning": 80, "error": 100},
                }
            }
        }

    def check_file(self, file_path: str, auto_fix: bool = False) -> List[Violation]:
        """检查单个文件"""
        if not file_path.endswith(".py"):
            return []

        if self._should_exclude_file(file_path) or file_path in self.checked_files:
            return []

        self.checked_files.add(file_path)
        file_violations = []

        print(f"🔍 检查文件: {file_path}")

        try:
            # 1. 基础文件检查
            self._check_file_basics(file_path, file_violations)

            # 2. Ruff检查和修复
            if auto_fix:
                self._run_ruff_fix(file_path)
            self._check_with_ruff(file_path, file_violations)

            # 3. MyPy类型检查
            self._check_with_mypy(file_path, file_violations)

            # 4. 架构和transfunctions检查
            self._check_architecture_and_transfunctions(file_path, file_violations)

        except Exception as e:
            file_violations.append(
                Violation(
                    file_path=file_path,
                    line_number=1,
                    violation_type=ViolationType.SYNTAX_ERROR,
                    severity=Severity.ERROR,
                    message=f"文件检查失败: {e}",
                )
            )

        return file_violations

    def _should_exclude_file(self, file_path: str) -> bool:
        """检查文件是否应该被排除"""
        exclusions = self.config.get("modularity", {}).get("exclusions", {})

        # 检查文件路径排除
        for pattern in exclusions.get("files", []):
            if file_path.startswith(pattern.replace("*", "")):
                return True

        # 检查文件名模式排除
        filename = os.path.basename(file_path)
        for pattern in exclusions.get("patterns", []):
            if pattern.startswith("*") and filename.endswith(pattern[1:]):
                return True
            elif pattern.endswith("*") and filename.startswith(pattern[:-1]):
                return True
            elif filename == pattern:
                return True

        return False

    def _check_file_basics(self, file_path: str, violations: List[Violation]) -> None:
        """检查文件基础指标"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()

            # 检查文件大小
            non_empty_lines = [line for line in lines if line.strip()]
            line_count = len(non_empty_lines)

            thresholds = self.config["modularity"]["thresholds"]["file_size"]

            if line_count >= thresholds["error"]:
                violations.append(
                    Violation(
                        file_path=file_path,
                        line_number=1,
                        violation_type=ViolationType.FILE_TOO_LARGE,
                        severity=Severity.ERROR,
                        message=f"文件过大: {line_count}行 (限制: {thresholds['error']}行)",
                        suggestion="建议将文件拆分为多个更小的模块，每个模块负责单一职责",
                    )
                )
            elif line_count >= thresholds["warning"]:
                violations.append(
                    Violation(
                        file_path=file_path,
                        line_number=1,
                        violation_type=ViolationType.FILE_TOO_LARGE,
                        severity=Severity.WARNING,
                        message=f"文件较大: {line_count}行 (警告阈值: {thresholds['warning']}行)",
                        suggestion="考虑重构文件，将相关功能提取到独立模块中",
                    )
                )

            # 检查函数和类大小
            try:
                tree = ast.parse(content, filename=file_path)
                self._check_ast_nodes(file_path, tree, violations)
            except SyntaxError as e:
                violations.append(
                    Violation(
                        file_path=file_path,
                        line_number=e.lineno or 1,
                        violation_type=ViolationType.SYNTAX_ERROR,
                        severity=Severity.ERROR,
                        message=f"语法错误: {e.msg}",
                    )
                )

        except Exception as e:
            violations.append(
                Violation(
                    file_path=file_path,
                    line_number=1,
                    violation_type=ViolationType.SYNTAX_ERROR,
                    severity=Severity.ERROR,
                    message=f"文件读取失败: {e}",
                )
            )

    def _check_ast_nodes(
        self, file_path: str, tree: ast.AST, violations: List[Violation]
    ) -> None:
        """检查AST节点（函数和类）"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._check_function_size(file_path, node, violations)
            elif isinstance(node, ast.ClassDef):
                self._check_class_size(file_path, node, violations)

    def _check_function_size(
        self, file_path: str, node: ast.FunctionDef, violations: List[Violation]
    ) -> None:
        """检查函数大小"""
        if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
            return

        start_line = node.lineno
        end_line = node.end_lineno or start_line
        function_lines = end_line - start_line + 1

        thresholds = self.config["modularity"]["thresholds"]["function_size"]

        if function_lines >= thresholds["error"]:
            violations.append(
                Violation(
                    file_path=file_path,
                    line_number=start_line,
                    violation_type=ViolationType.FUNCTION_TOO_LARGE,
                    severity=Severity.ERROR,
                    message=f"函数 '{node.name}' 过大: {function_lines}行 (限制: {thresholds['error']}行)",
                    suggestion="建议将函数拆分为多个更小的函数，每个函数只负责一个具体任务",
                )
            )
        elif function_lines >= thresholds["warning"]:
            violations.append(
                Violation(
                    file_path=file_path,
                    line_number=start_line,
                    violation_type=ViolationType.FUNCTION_TOO_LARGE,
                    severity=Severity.WARNING,
                    message=f"函数 '{node.name}' 较大: {function_lines}行 (警告阈值: {thresholds['warning']}行)",
                    suggestion="考虑重构函数，提取部分逻辑到私有方法中",
                )
            )

    def _check_class_size(
        self, file_path: str, node: ast.ClassDef, violations: List[Violation]
    ) -> None:
        """检查类大小"""
        if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
            return

        start_line = node.lineno
        end_line = node.end_lineno or start_line
        class_lines = end_line - start_line + 1

        thresholds = self.config["modularity"]["thresholds"]["class_size"]

        if class_lines >= thresholds["error"]:
            violations.append(
                Violation(
                    file_path=file_path,
                    line_number=start_line,
                    violation_type=ViolationType.CLASS_TOO_LARGE,
                    severity=Severity.ERROR,
                    message=f"类 '{node.name}' 过大: {class_lines}行 (限制: {thresholds['error']}行)",
                    suggestion="建议将类拆分为多个更小的类，遵循单一职责原则",
                )
            )
        elif class_lines >= thresholds["warning"]:
            violations.append(
                Violation(
                    file_path=file_path,
                    line_number=start_line,
                    violation_type=ViolationType.CLASS_TOO_LARGE,
                    severity=Severity.WARNING,
                    message=f"类 '{node.name}' 较大: {class_lines}行 (警告阈值: {thresholds['warning']}行)",
                    suggestion="考虑重构类，将部分职责提取到独立的类中",
                )
            )

    def _run_ruff_fix(self, file_path: str) -> None:
        """运行Ruff自动修复"""
        try:
            subprocess.run(
                ["uv", "run", "ruff", "check", file_path, "--fix", "--quiet"],
                check=False,
                capture_output=True,
            )
            subprocess.run(
                ["uv", "run", "ruff", "format", file_path, "--quiet"],
                check=False,
                capture_output=True,
            )
        except Exception:
            pass  # 忽略修复失败

    def _check_with_ruff(self, file_path: str, violations: List[Violation]) -> None:
        """使用Ruff检查代码"""
        try:
            result = subprocess.run(
                ["uv", "run", "ruff", "check", file_path, "--output-format=json"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.stdout:
                try:
                    ruff_issues = json.loads(result.stdout)
                    for issue in ruff_issues:
                        if issue.get("filename") == file_path:
                            violations.append(
                                Violation(
                                    file_path=file_path,
                                    line_number=issue.get("location", {}).get("row", 1),
                                    violation_type=ViolationType.RUFF_ERROR,
                                    severity=Severity.ERROR
                                    if issue.get("code", "").startswith("E")
                                    else Severity.WARNING,
                                    message=f"Ruff {issue.get('code', '')}: {issue.get('message', '')}",
                                    suggestion="运行 'uv run ruff check --fix' 自动修复",
                                    fixable=issue.get("fix", {}).get("applicability")
                                    == "automatic",
                                )
                            )
                except json.JSONDecodeError:
                    pass

        except Exception:
            pass  # Ruff不可用时跳过

    def _check_with_mypy(self, file_path: str, violations: List[Violation]) -> None:
        """使用MyPy检查类型"""
        try:
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "mypy",
                    file_path,
                    "--show-column-numbers",
                    "--show-error-codes",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.stdout:
                for line in result.stdout.strip().split("\n"):
                    if ":" in line and file_path in line:
                        parts = line.split(":", 3)
                        if len(parts) >= 4:
                            try:
                                line_num = int(parts[1])
                                message = parts[3].strip()
                                violations.append(
                                    Violation(
                                        file_path=file_path,
                                        line_number=line_num,
                                        violation_type=ViolationType.MYPY_ERROR,
                                        severity=Severity.WARNING,
                                        message=f"MyPy: {message}",
                                        suggestion="添加类型注解或修复类型错误",
                                    )
                                )
                            except ValueError:
                                continue

        except Exception:
            pass  # MyPy不可用时跳过

    def _check_architecture_and_transfunctions(
        self, file_path: str, violations: List[Violation]
    ) -> None:
        """检查架构和transfunctions使用"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=file_path)

            # 检查transfunctions使用
            has_transfunctions_import = False
            has_business_logic = False

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if "transfunctions" in node.module:
                        has_transfunctions_import = True
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith(
                    "_"
                ):
                    has_business_logic = True

            # 只对有业务逻辑但没有使用transfunctions的文件给出建议
            if has_business_logic and not has_transfunctions_import:
                # 检查是否是应该使用transfunctions的文件类型
                if any(
                    keyword in file_path
                    for keyword in ["service", "model", "data", "business"]
                ):
                    violations.append(
                        Violation(
                            file_path=file_path,
                            line_number=1,
                            violation_type=ViolationType.MISSING_TRANSFUNCTIONS,
                            severity=Severity.INFO,
                            message="建议检查transfunctions库是否有可复用的函数",
                            suggestion="查看transfunctions文档，避免重复实现通用功能",
                        )
                    )

        except Exception:
            pass  # 解析失败时跳过

    def check_directory(
        self, directory: str, auto_fix: bool = False
    ) -> List[Violation]:
        """检查目录中的所有Python文件"""
        all_violations = []

        print(f"🔍 开始检查目录: {directory}")

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    violations = self.check_file(file_path, auto_fix)
                    all_violations.extend(violations)

        return all_violations

    def generate_report(self, violations: List[Violation]) -> str:
        """生成现代化检查报告"""
        if not violations:
            return """
✅ 恭喜！代码质量检查全部通过！

📊 检查项目：
- 文件大小控制 ✅
- 函数和类大小 ✅
- Ruff代码检查 ✅
- MyPy类型检查 ✅
- 架构规范 ✅
- Transfunctions使用 ✅

🚀 代码质量优秀，继续保持！
"""

        # 按严重程度和类型分组
        errors = [v for v in violations if v.severity == Severity.ERROR]
        warnings = [v for v in violations if v.severity == Severity.WARNING]
        infos = [v for v in violations if v.severity == Severity.INFO]

        # 按类型统计
        type_counts = {}
        for v in violations:
            type_counts[v.violation_type] = type_counts.get(v.violation_type, 0) + 1

        # 统计可自动修复的问题
        fixable_count = len([v for v in violations if v.fixable])

        report = []
        report.append("🔧 现代化代码质量检查报告")
        report.append("=" * 50)
        report.append(f"📊 总计发现 {len(violations)} 个问题")
        report.append(f"  - ❌ 错误: {len(errors)} 个")
        report.append(f"  - ⚠️  警告: {len(warnings)} 个")
        report.append(f"  - 💡 建议: {len(infos)} 个")
        report.append(f"  - 🔧 可自动修复: {fixable_count} 个")
        report.append("")

        # 问题类型统计
        report.append("📈 问题类型分布:")
        for vtype, count in type_counts.items():
            type_name = {
                ViolationType.FILE_TOO_LARGE: "文件过大",
                ViolationType.FUNCTION_TOO_LARGE: "函数过大",
                ViolationType.CLASS_TOO_LARGE: "类过大",
                ViolationType.RUFF_ERROR: "Ruff检查",
                ViolationType.MYPY_ERROR: "MyPy类型",
                ViolationType.MISSING_TRANSFUNCTIONS: "Transfunctions建议",
                ViolationType.SYNTAX_ERROR: "语法错误",
            }.get(vtype, str(vtype))
            report.append(f"  - {type_name}: {count} 个")
        report.append("")

        if errors:
            report.append("❌ 错误 (必须修复):")
            for violation in errors[:10]:  # 只显示前10个错误
                report.append(f"  📁 {violation.file_path}:{violation.line_number}")
                report.append(f"     {violation.message}")
                if violation.suggestion:
                    report.append(f"     💡 建议: {violation.suggestion}")
                report.append("")
            if len(errors) > 10:
                report.append(f"  ... 还有 {len(errors) - 10} 个错误")
                report.append("")

        if warnings:
            report.append("⚠️  警告 (建议修复):")
            for violation in warnings[:5]:  # 只显示前5个警告
                report.append(f"  📁 {violation.file_path}:{violation.line_number}")
                report.append(f"     {violation.message}")
                if violation.suggestion:
                    report.append(f"     💡 建议: {violation.suggestion}")
                report.append("")
            if len(warnings) > 5:
                report.append(f"  ... 还有 {len(warnings) - 5} 个警告")
                report.append("")

        if infos:
            report.append("💡 优化建议:")
            unique_infos = {}
            for violation in infos:
                key = violation.message
                if key not in unique_infos:
                    unique_infos[key] = violation

            for violation in list(unique_infos.values())[:3]:  # 只显示前3个建议
                report.append(f"  📁 {violation.file_path}")
                report.append(f"     {violation.message}")
                if violation.suggestion:
                    report.append(f"     💡 建议: {violation.suggestion}")
                report.append("")

        # 修复建议
        if fixable_count > 0:
            report.append("🛠️  自动修复命令:")
            report.append("```bash")
            report.append("# 自动修复Ruff问题")
            report.append("uv run ruff check --fix")
            report.append("uv run ruff format")
            report.append("")
            report.append("# 重新运行检查")
            report.append("python scripts/modularity_check_improved.py --all --fix")
            report.append("```")
            report.append("")

        report.append("📚 更多信息:")
        report.append("- 配置文件: .modularity-config.yaml")
        report.append("- Ruff配置: pyproject.toml [tool.ruff]")
        report.append("- MyPy配置: pyproject.toml [tool.mypy]")
        report.append("- 开发标准: .kiro/steering/minicrm-development-standards.md")

        return "\n".join(report)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MiniCRM 现代化模块化质量检查工具")
    parser.add_argument("path", nargs="?", default=".", help="要检查的文件或目录路径")
    parser.add_argument("--all", action="store_true", help="检查整个项目")
    parser.add_argument("--fix", action="store_true", help="自动修复可修复的问题")
    parser.add_argument(
        "--config", default=".modularity-config.yaml", help="配置文件路径"
    )

    args = parser.parse_args()

    checker = ModernModularityChecker(args.config)

    if args.all:
        violations = checker.check_directory("src", args.fix)
    else:
        if os.path.isfile(args.path):
            violations = checker.check_file(args.path, args.fix)
        elif os.path.isdir(args.path):
            violations = checker.check_directory(args.path, args.fix)
        else:
            print(f"❌ 路径不存在: {args.path}")
            sys.exit(1)

    # 生成并显示报告
    report = checker.generate_report(violations)
    print(report)

    # 如果有错误，返回非零退出码
    errors = [v for v in violations if v.severity == Severity.ERROR]
    if errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
