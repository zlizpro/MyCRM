"""
单一职责原则验证工具

验证类是否遵循单一职责原则：
- 检查类的方法数量
- 分析类的职责范围
- 提供重构建议
"""

import ast
import logging
from pathlib import Path


class SRPValidator:
    """
    单一职责原则验证器

    分析类的职责，检查是否违反单一职责原则
    """

    def __init__(self, project_root: str):
        """
        初始化SRP验证器

        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(__name__)

        # 方法数量阈值
        self.method_thresholds = {
            "warning": 15,  # 警告阈值
            "error": 25,  # 错误阈值
        }

        # 职责关键词
        self.responsibility_keywords = {
            "ui": ["show", "hide", "display", "render", "paint", "draw", "update_ui"],
            "data": ["save", "load", "insert", "update", "delete", "query", "fetch"],
            "validation": ["validate", "check", "verify", "ensure"],
            "formatting": ["format", "parse", "convert", "transform"],
            "calculation": ["calculate", "compute", "sum", "count"],
            "event": ["handle", "on_", "emit", "trigger", "notify"],
            "config": ["configure", "setup", "initialize", "config"],
            "logging": ["log", "debug", "info", "warn", "error"],
        }

    def validate_srp(self) -> dict[str, list[str]]:
        """
        验证单一职责原则

        Returns:
            Dict[str, List[str]]: 验证结果
        """
        results = {"violations": [], "warnings": [], "suggestions": []}

        try:
            # 分析所有Python文件
            for py_file in self.project_root.rglob("*.py"):
                if py_file.name == "__init__.py":
                    continue

                violations = self._analyze_file(py_file)
                results["violations"].extend(violations)

            self.logger.info(f"SRP验证完成: {len(results['violations'])} 个违规")

        except Exception as e:
            results["violations"].append(f"SRP验证失败: {e}")
            self.logger.error(f"SRP验证失败: {e}")

        return results

    def _analyze_file(self, file_path: Path) -> list[str]:
        """分析单个文件"""
        violations = []

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_violations = self._analyze_class(file_path, node)
                    violations.extend(class_violations)

        except Exception as e:
            self.logger.warning(f"分析文件失败 {file_path}: {e}")

        return violations

    def _analyze_class(self, file_path: Path, class_node: ast.ClassDef) -> list[str]:
        """分析单个类"""
        violations = []

        # 获取类的方法
        methods = []
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)

        # 检查方法数量
        method_count = len(methods)
        if method_count > self.method_thresholds["error"]:
            violations.append(
                f"❌ 严重违反SRP: {file_path.relative_to(self.project_root)} "
                f"中的类 {class_node.name} 有 {method_count} 个方法（超过 {self.method_thresholds['error']}）"
            )
        elif method_count > self.method_thresholds["warning"]:
            violations.append(
                f"⚠️ 可能违反SRP: {file_path.relative_to(self.project_root)} "
                f"中的类 {class_node.name} 有 {method_count} 个方法（超过 {self.method_thresholds['warning']}）"
            )

        # 分析职责混合
        responsibilities = self._analyze_responsibilities(methods)
        if len(responsibilities) > 2:
            violations.append(
                f"⚠️ 职责混合: {file_path.relative_to(self.project_root)} "
                f"中的类 {class_node.name} 混合了多种职责: {', '.join(responsibilities)}"
            )

        return violations

    def _analyze_responsibilities(self, methods: list[str]) -> list[str]:
        """分析方法的职责类型"""
        found_responsibilities = set()

        for method in methods:
            method_lower = method.lower()

            for responsibility, keywords in self.responsibility_keywords.items():
                for keyword in keywords:
                    if keyword in method_lower:
                        found_responsibilities.add(responsibility)
                        break

        return list(found_responsibilities)

    def generate_refactoring_suggestions(self, violations: list[str]) -> list[str]:
        """生成重构建议"""
        suggestions = []

        for violation in violations:
            if "严重违反SRP" in violation:
                suggestions.append("🔧 建议将大类拆分为多个小类，每个类只负责一个职责")
            elif "可能违反SRP" in violation:
                suggestions.append("🔧 建议检查类的职责，考虑提取部分方法到新类中")
            elif "职责混合" in violation:
                suggestions.append("🔧 建议按职责类型拆分类，使用组合模式替代继承")

        return list(set(suggestions))  # 去重

    def generate_report(self, results: dict[str, list[str]]) -> str:
        """生成SRP验证报告"""
        report = []
        report.append("# 单一职责原则验证报告")
        report.append("")
        report.append(f"生成时间: {self._get_current_time()}")
        report.append("")

        # 违规部分
        if results["violations"]:
            report.append("## ❌ SRP违规")
            report.append("")
            for violation in results["violations"]:
                report.append(f"- {violation}")
            report.append("")

        # 建议部分
        suggestions = self.generate_refactoring_suggestions(results["violations"])
        if suggestions:
            report.append("## 🔧 重构建议")
            report.append("")
            for suggestion in suggestions:
                report.append(f"- {suggestion}")
            report.append("")

        # 总结
        report.append("## 📊 验证总结")
        report.append("")
        report.append(f"- 违规数量: {len(results['violations'])}")
        report.append(f"- 建议数量: {len(suggestions)}")

        if not results["violations"]:
            report.append("")
            report.append("✅ **单一职责原则验证通过！**")
        else:
            report.append("")
            report.append("❌ **发现SRP违规，建议进行重构。**")

        return "\n".join(report)

    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validate_srp(project_root: str = ".") -> dict[str, list[str]]:
    """
    验证单一职责原则

    Args:
        project_root: 项目根目录

    Returns:
        Dict[str, List[str]]: 验证结果
    """
    validator = SRPValidator(project_root)
    return validator.validate_srp()


def generate_srp_report(project_root: str = ".") -> str:
    """
    生成SRP验证报告

    Args:
        project_root: 项目根目录

    Returns:
        str: 报告内容
    """
    validator = SRPValidator(project_root)
    results = validator.validate_srp()
    return validator.generate_report(results)


if __name__ == "__main__":
    # 运行SRP验证
    results = validate_srp()

    # 打印结果
    for violation in results["violations"]:
        print(violation)

    # 生成报告
    report = generate_srp_report()
    with open("srp_validation_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("\n报告已生成: srp_validation_report.md")
    print(f"违规: {len(results['violations'])}")
