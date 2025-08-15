#!/usr/bin/env python3
"""
MiniCRM 模块化质量检查工具

这个脚本用于检查Python文件是否符合模块化标准，包括：
- 文件大小控制（最大200行）
- 函数大小控制（最大50行）
- 类大小控制（最大100行）
- 架构依赖检查
- transfunctions使用检查

使用方法:
    python scripts/modularity_check.py [文件路径或目录]
    python scripts/modularity_check.py --all  # 检查整个项目
    python scripts/modularity_check.py --pre-commit  # Git pre-commit模式
"""

import ast
import os
import sys
import argparse
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ViolationType(Enum):
    """违规类型枚举"""

    FILE_TOO_LARGE = "file_too_large"
    FUNCTION_TOO_LARGE = "function_too_large"
    CLASS_TOO_LARGE = "class_too_large"
    ARCHITECTURE_VIOLATION = "architecture_violation"
    MISSING_TRANSFUNCTIONS = "missing_transfunctions"
    CODE_DUPLICATION = "code_duplication"


class Severity(Enum):
    """严重程度枚举"""

    WARNING = "warning"
    ERROR = "error"
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


class ModularityChecker:
    """模块化质量检查器"""

    def __init__(self, config_path: str = ".modularity-config.yaml"):
        """初始化检查器"""
        self.config = self._load_config(config_path)
        self.violations: List[Violation] = []

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

    def check_file(self, file_path: str) -> List[Violation]:
        """检查单个文件"""
        if not file_path.endswith(".py"):
            return []

        if self._should_exclude_file(file_path):
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()

            # 解析AST
            try:
                tree = ast.parse(content, filename=file_path)
            except SyntaxError as e:
                self.violations.append(
                    Violation(
                        file_path=file_path,
                        line_number=e.lineno or 1,
                        violation_type=ViolationType.FILE_TOO_LARGE,
                        severity=Severity.ERROR,
                        message=f"语法错误: {e.msg}",
                    )
                )
                return self.violations

            # 检查文件大小
            self._check_file_size(file_path, lines)

            # 检查函数和类大小
            self._check_ast_nodes(file_path, tree, lines)

            # 检查架构违规
            self._check_architecture_violations(file_path, tree)

            # 检查transfunctions使用
            self._check_transfunctions_usage(file_path, tree)

        except Exception as e:
            self.violations.append(
                Violation(
                    file_path=file_path,
                    line_number=1,
                    violation_type=ViolationType.FILE_TOO_LARGE,
                    severity=Severity.ERROR,
                    message=f"文件检查失败: {e}",
                )
            )

        return self.violations

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

    def _check_file_size(self, file_path: str, lines: List[str]) -> None:
        """检查文件大小"""
        # 计算非空行数
        non_empty_lines = [line for line in lines if line.strip()]
        line_count = len(non_empty_lines)

        thresholds = self.config["modularity"]["thresholds"]["file_size"]

        if line_count >= thresholds["error"]:
            self.violations.append(
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
            self.violations.append(
                Violation(
                    file_path=file_path,
                    line_number=1,
                    violation_type=ViolationType.FILE_TOO_LARGE,
                    severity=Severity.WARNING,
                    message=f"文件较大: {line_count}行 (警告阈值: {thresholds['warning']}行)",
                    suggestion="考虑重构文件，将相关功能提取到独立模块中",
                )
            )

    def _check_ast_nodes(self, file_path: str, tree: ast.AST, lines: List[str]) -> None:
        """检查AST节点（函数和类）"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._check_function_size(file_path, node, lines)
            elif isinstance(node, ast.ClassDef):
                self._check_class_size(file_path, node, lines)

    def _check_function_size(
        self, file_path: str, node: ast.FunctionDef, lines: List[str]
    ) -> None:
        """检查函数大小"""
        if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
            return

        start_line = node.lineno
        end_line = node.end_lineno or start_line
        function_lines = end_line - start_line + 1

        thresholds = self.config["modularity"]["thresholds"]["function_size"]

        if function_lines >= thresholds["error"]:
            self.violations.append(
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
            self.violations.append(
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
        self, file_path: str, node: ast.ClassDef, lines: List[str]
    ) -> None:
        """检查类大小"""
        if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
            return

        start_line = node.lineno
        end_line = node.end_lineno or start_line
        class_lines = end_line - start_line + 1

        thresholds = self.config["modularity"]["thresholds"]["class_size"]

        if class_lines >= thresholds["error"]:
            self.violations.append(
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
            self.violations.append(
                Violation(
                    file_path=file_path,
                    line_number=start_line,
                    violation_type=ViolationType.CLASS_TOO_LARGE,
                    severity=Severity.WARNING,
                    message=f"类 '{node.name}' 较大: {class_lines}行 (警告阈值: {thresholds['warning']}行)",
                    suggestion="考虑重构类，将部分职责提取到独立的类中",
                )
            )

    def _check_architecture_violations(self, file_path: str, tree: ast.AST) -> None:
        """检查架构违规"""
        # 简化的架构检查，检查导入语句
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                self._check_import_violations(file_path, node)

    def _check_import_violations(self, file_path: str, node: ast.AST) -> None:
        """检查导入违规"""
        # 这里可以实现更复杂的架构依赖检查
        # 目前只做简单的示例检查
        if isinstance(node, ast.ImportFrom) and node.module:
            # 检查是否有跨层导入
            current_layer = self._get_file_layer(file_path)
            imported_layer = self._get_module_layer(node.module)

            if current_layer and imported_layer:
                if not self._is_import_allowed(current_layer, imported_layer):
                    self.violations.append(
                        Violation(
                            file_path=file_path,
                            line_number=node.lineno,
                            violation_type=ViolationType.ARCHITECTURE_VIOLATION,
                            severity=Severity.ERROR,
                            message=f"架构违规: {current_layer}层不能导入{imported_layer}层的模块",
                            suggestion="请通过合适的层次进行访问，遵循分层架构原则",
                        )
                    )

    def _get_file_layer(self, file_path: str) -> Optional[str]:
        """获取文件所属的架构层"""
        layers = (
            self.config.get("modularity", {}).get("architecture", {}).get("layers", [])
        )
        for layer in layers:
            if layer["path"] in file_path:
                return layer["name"]
        return None

    def _get_module_layer(self, module_name: str) -> Optional[str]:
        """获取模块所属的架构层"""
        # 简化实现，基于模块名推断层次
        if "ui" in module_name:
            return "ui"
        elif "services" in module_name:
            return "services"
        elif "data" in module_name:
            return "data"
        elif "models" in module_name:
            return "models"
        elif "core" in module_name:
            return "core"
        elif "transfunctions" in module_name:
            return "transfunctions"
        return None

    def _is_import_allowed(self, from_layer: str, to_layer: str) -> bool:
        """检查导入是否被允许"""
        layers = (
            self.config.get("modularity", {}).get("architecture", {}).get("layers", [])
        )
        for layer in layers:
            if layer["name"] == from_layer:
                return to_layer in layer.get("can_import", [])
        return True

    def _check_transfunctions_usage(self, file_path: str, tree: ast.AST) -> None:
        """检查transfunctions使用情况"""
        # 简化实现，检查是否导入了transfunctions
        has_transfunctions_import = False

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "transfunctions" in node.module:
                    has_transfunctions_import = True
                    break

        # 如果文件中有业务逻辑但没有使用transfunctions，给出建议
        if not has_transfunctions_import and self._has_business_logic(tree):
            self.violations.append(
                Violation(
                    file_path=file_path,
                    line_number=1,
                    violation_type=ViolationType.MISSING_TRANSFUNCTIONS,
                    severity=Severity.INFO,
                    message="建议使用transfunctions中的可复用函数",
                    suggestion="检查transfunctions库是否有可用的函数来避免重复实现",
                )
            )

    def _has_business_logic(self, tree: ast.AST) -> bool:
        """检查是否包含业务逻辑"""
        # 简化实现，检查是否有函数定义
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                return True
        return False

    def check_directory(self, directory: str) -> List[Violation]:
        """检查目录中的所有Python文件"""
        all_violations = []

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    violations = self.check_file(file_path)
                    all_violations.extend(violations)

        return all_violations

    def generate_report(self, violations: List[Violation]) -> str:
        """生成检查报告"""
        if not violations:
            return "✅ 恭喜！所有文件都符合模块化标准。"

        # 按严重程度分组
        errors = [v for v in violations if v.severity == Severity.ERROR]
        warnings = [v for v in violations if v.severity == Severity.WARNING]
        infos = [v for v in violations if v.severity == Severity.INFO]

        report = []
        report.append("🔍 模块化质量检查报告")
        report.append("=" * 50)
        report.append(f"总计发现 {len(violations)} 个问题")
        report.append(f"  - 错误: {len(errors)} 个")
        report.append(f"  - 警告: {len(warnings)} 个")
        report.append(f"  - 建议: {len(infos)} 个")
        report.append("")

        if errors:
            report.append("❌ 错误 (必须修复):")
            for violation in errors:
                report.append(f"  📁 {violation.file_path}:{violation.line_number}")
                report.append(f"     {violation.message}")
                if violation.suggestion:
                    report.append(f"     💡 建议: {violation.suggestion}")
                report.append("")

        if warnings:
            report.append("⚠️  警告 (建议修复):")
            for violation in warnings:
                report.append(f"  📁 {violation.file_path}:{violation.line_number}")
                report.append(f"     {violation.message}")
                if violation.suggestion:
                    report.append(f"     💡 建议: {violation.suggestion}")
                report.append("")

        if infos:
            report.append("💡 建议 (可选优化):")
            for violation in infos:
                report.append(f"  📁 {violation.file_path}:{violation.line_number}")
                report.append(f"     {violation.message}")
                if violation.suggestion:
                    report.append(f"     💡 建议: {violation.suggestion}")
                report.append("")

        return "\n".join(report)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="MiniCRM 模块化质量检查工具")
    parser.add_argument("path", nargs="?", default=".", help="要检查的文件或目录路径")
    parser.add_argument("--all", action="store_true", help="检查整个项目")
    parser.add_argument("--pre-commit", action="store_true", help="Git pre-commit模式")
    parser.add_argument(
        "--config", default=".modularity-config.yaml", help="配置文件路径"
    )

    args = parser.parse_args()

    checker = ModularityChecker(args.config)

    if args.all:
        violations = checker.check_directory("src")
    elif args.pre_commit:
        # Git pre-commit模式，只检查暂存的文件
        import subprocess

        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                capture_output=True,
                text=True,
                check=True,
            )
            staged_files = result.stdout.strip().split("\n")
            violations = []
            for file_path in staged_files:
                if file_path.endswith(".py") and os.path.exists(file_path):
                    violations.extend(checker.check_file(file_path))
        except subprocess.CalledProcessError:
            print("❌ 无法获取Git暂存文件列表")
            sys.exit(1)
    else:
        if os.path.isfile(args.path):
            violations = checker.check_file(args.path)
        elif os.path.isdir(args.path):
            violations = checker.check_directory(args.path)
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
