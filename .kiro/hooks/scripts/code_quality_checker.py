#!/usr/bin/env python3
"""
MiniCRM 代码质量检查器
自动检查Python代码的质量，包括PEP8、类型注解、文档字符串等
"""

import ast
import re
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class QualityIssue:
    """代码质量问题数据类"""
    file_path: str
    line_number: int
    column: int
    issue_type: str
    severity: str  # 'error', 'warning', 'info'
    message: str
    suggestion: Optional[str] = None
    auto_fixable: bool = False


class CodeQualityChecker:
    """代码质量检查器主类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.issues: List[QualityIssue] = []

    def check_file(self, file_path: Path) -> List[QualityIssue]:
        """检查单个Python文件的代码质量"""
        self.issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                self.issues.append(QualityIssue(
                    file_path=str(file_path),
                    line_number=e.lineno or 1,
                    column=e.offset or 0,
                    issue_type="syntax_error",
                    severity="error",
                    message=f"语法错误: {e.msg}",
                    auto_fixable=False
                ))
                return self.issues

            # 执行各种检查
            self._check_imports(content, str(file_path))
            self._check_line_length(content, str(file_path))
            self._check_naming_conventions(tree, str(file_path))
            self._check_docstrings(tree, str(file_path))
            self._check_type_hints(tree, str(file_path))
            self._check_code_structure(tree, str(file_path))

        except Exception as e:
            self.issues.append(QualityIssue(
                file_path=str(file_path),
                line_number=1,
                column=0,
                issue_type="check_error",
                severity="error",
                message=f"检查文件时出错: {str(e)}",
                auto_fixable=False
            ))

        return self.issues

    def _check_imports(self, content: str, file_path: str):
        """检查导入语句规范"""
        lines = content.split('\n')

        # 检查导入顺序和分组
        import_sections = {'stdlib': [], 'third_party': [], 'local': []}
        current_section = None

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                # 简化的导入分类逻辑
                if any(stdlib in line for stdlib in ['os', 'sys', 'json', 'datetime', 're', 'pathlib']):
                    section = 'stdlib'
                elif any(third in line for third in ['tkinter', 'matplotlib', 'reportlab']):
                    section = 'third_party'
                else:
                    section = 'local'

                import_sections[section].append((i, line))

                # 检查是否有未使用的导入（简化检查）
                module_name = self._extract_module_name(line)
                if module_name and module_name not in content:
                    self.issues.append(QualityIssue(
                        file_path=file_path,
                        line_number=i,
                        column=0,
                        issue_type="unused_import",
                        severity="warning",
                        message=f"未使用的导入: {module_name}",
                        suggestion=f"删除未使用的导入语句",
                        auto_fixable=True
                    ))

    def _extract_module_name(self, import_line: str) -> str:
        """从导入语句中提取模块名"""
        if import_line.startswith('import '):
            return import_line.replace('import ', '').split('.')[0].split(' as ')[0]
        elif import_line.startswith('from '):
            parts = import_line.split(' import ')
            if len(parts) > 1:
                return parts[1].split(',')[0].strip().split(' as ')[0]
        return ""

    def _check_line_length(self, content: str, file_path: str):
        """检查行长度"""
        max_length = self.config.get('max_line_length', 88)
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            if len(line) > max_length:
                self.issues.append(QualityIssue(
                    file_path=file_path,
                    line_number=i,
                    column=max_length,
                    issue_type="line_too_long",
                    severity="warning",
                    message=f"行长度超过{max_length}字符 (当前: {len(line)})",
                    suggestion="考虑将长行拆分为多行",
                    auto_fixable=True
                ))

    def _check_naming_conventions(self, tree: ast.AST, file_path: str):
        """检查命名规范"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 类名应该使用大驼峰命名
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    self.issues.append(QualityIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        issue_type="naming_convention",
                        severity="warning",
                        message=f"类名 '{node.name}' 应使用大驼峰命名法",
                        suggestion=f"建议改为: {self._to_pascal_case(node.name)}",
                        auto_fixable=True
                    ))

            elif isinstance(node, ast.FunctionDef):
                # 函数名应该使用下划线命名
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and not node.name.startswith('__'):
                    self.issues.append(QualityIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        issue_type="naming_convention",
                        severity="warning",
                        message=f"函数名 '{node.name}' 应使用下划线命名法",
                        suggestion=f"建议改为: {self._to_snake_case(node.name)}",
                        auto_fixable=True
                    ))

    def _check_docstrings(self, tree: ast.AST, file_path: str):
        """检查文档字符串"""
        if not self.config.get('check_docstrings', True):
            return

        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                # 跳过私有方法和特殊方法的docstring检查
                if node.name.startswith('_') and not node.name.startswith('__'):
                    continue

                docstring = ast.get_docstring(node)
                if not docstring:
                    node_type = "类" if isinstance(node, ast.ClassDef) else "函数"
                    self.issues.append(QualityIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        issue_type="missing_docstring",
                        severity="info",
                        message=f"{node_type} '{node.name}' 缺少文档字符串",
                        suggestion=f"添加描述{node_type}功能的文档字符串",
                        auto_fixable=True
                    ))
                elif len(docstring.strip()) < 10:
                    self.issues.append(QualityIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        issue_type="inadequate_docstring",
                        severity="info",
                        message=f"文档字符串过于简短: '{node.name}'",
                        suggestion="提供更详细的功能描述",
                        auto_fixable=False
                    ))

    def _check_type_hints(self, tree: ast.AST, file_path: str):
        """检查类型注解"""
        if not self.config.get('check_type_hints', True):
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 跳过私有方法和特殊方法
                if node.name.startswith('_'):
                    continue

                # 检查参数类型注解
                for arg in node.args.args:
                    if arg.arg != 'self' and not arg.annotation:
                        self.issues.append(QualityIssue(
                            file_path=file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            issue_type="missing_type_hint",
                            severity="info",
                            message=f"参数 '{arg.arg}' 缺少类型注解",
                            suggestion=f"为参数 '{arg.arg}' 添加类型注解",
                            auto_fixable=True
                        ))

                # 检查返回值类型注解
                if not node.returns and node.name != '__init__':
                    self.issues.append(QualityIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        issue_type="missing_return_type",
                        severity="info",
                        message=f"函数 '{node.name}' 缺少返回值类型注解",
                        suggestion=f"为函数 '{node.name}' 添加返回值类型注解",
                        auto_fixable=True
                    ))

    def _check_code_structure(self, tree: ast.AST, file_path: str):
        """检查代码结构"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数复杂度（简化版）
                complexity = self._calculate_complexity(node)
                if complexity > 10:
                    self.issues.append(QualityIssue(
                        file_path=file_path,
                        line_number=node.lineno,
                        column=node.col_offset,
                        issue_type="high_complexity",
                        severity="warning",
                        message=f"函数 '{node.name}' 复杂度过高 (复杂度: {complexity})",
                        suggestion="考虑将函数拆分为更小的函数",
                        auto_fixable=False
                    ))

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """计算函数的圈复杂度（简化版）"""
        complexity = 1  # 基础复杂度

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _to_pascal_case(self, name: str) -> str:
        """转换为大驼峰命名"""
        return ''.join(word.capitalize() for word in name.split('_'))

    def _to_snake_case(self, name: str) -> str:
        """转换为下划线命名"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def generate_report(issues: List[QualityIssue], output_format: str = 'json') -> str:
    """生成质量检查报告"""
    if output_format == 'json':
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_issues': len(issues),
            'issues_by_severity': {
                'error': len([i for i in issues if i.severity == 'error']),
                'warning': len([i for i in issues if i.severity == 'warning']),
                'info': len([i for i in issues if i.severity == 'info'])
            },
            'auto_fixable_count': len([i for i in issues if i.auto_fixable]),
            'issues': [
                {
                    'file_path': issue.file_path,
                    'line_number': issue.line_number,
                    'column': issue.column,
                    'issue_type': issue.issue_type,
                    'severity': issue.severity,
                    'message': issue.message,
                    'suggestion': issue.suggestion,
                    'auto_fixable': issue.auto_fixable
                }
                for issue in issues
            ]
        }
        return json.dumps(report_data, ensure_ascii=False, indent=2)

    elif output_format == 'text':
        lines = []
        lines.append("=" * 60)
        lines.append("MiniCRM 代码质量检查报告")
        lines.append("=" * 60)
        lines.append(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"总问题数: {len(issues)}")

        if issues:
            lines.append("\n问题详情:")
            lines.append("-" * 40)

            for issue in sorted(issues, key=lambda x: (x.severity, x.file_path, x.line_number)):
                severity_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}
                fix_icon = "🔧" if issue.auto_fixable else "📝"

                lines.append(
                    f"\n{severity_icon[issue.severity]} {fix_icon} {issue.file_path}:{issue.line_number}:{issue.column}")
                lines.append(f"   类型: {issue.issue_type}")
                lines.append(f"   问题: {issue.message}")
                if issue.suggestion:
                    lines.append(f"   建议: {issue.suggestion}")
        else:
            lines.append("\n🎉 恭喜！没有发现代码质量问题。")

        return "\n".join(lines)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='MiniCRM 代码质量检查器')
    parser.add_argument('files', nargs='+', help='要检查的Python文件')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument(
        '--format', choices=['json', 'text'], default='json', help='输出格式')
    parser.add_argument('--output', help='输出文件路径')

    args = parser.parse_args()

    # 加载配置
    config = {
        'check_pep8': True,
        'check_type_hints': True,
        'check_docstrings': True,
        'check_imports': True,
        'max_line_length': 88
    }

    if args.config and Path(args.config).exists():
        with open(args.config, 'r', encoding='utf-8') as f:
            config.update(json.load(f))

    # 执行检查
    checker = CodeQualityChecker(config)
    all_issues = []

    for file_path in args.files:
        path = Path(file_path)
        if path.exists() and path.suffix == '.py':
            issues = checker.check_file(path)
            all_issues.extend(issues)

    # 生成报告
    report = generate_report(all_issues, args.format)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存到: {args.output}")
    else:
        print(report)

    # 返回适当的退出码
    error_count = len([i for i in all_issues if i.severity == 'error'])
    sys.exit(1 if error_count > 0 else 0)


if __name__ == '__main__':
    main()
