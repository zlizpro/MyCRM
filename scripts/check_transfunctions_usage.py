#!/usr/bin/env python3
"""
Pre-commit hook: 检查transfunctions使用情况

确保没有重复实现transfunctions中已有的功能，强制使用transfunctions库中的可复用函数。
"""

import re
import sys
from pathlib import Path


class TransfunctionsChecker:
    """Transfunctions使用情况检查器"""

    def __init__(self):
        """初始化检查器"""
        self.issues: list[str] = []
        self.stats = {
            "files_checked": 0,
            "violations_found": 0,
            "functions_to_replace": 0,
        }

        # 定义transfunctions中确实存在的函数
        self.available_functions = {
            "validation": {
                "validate_customer_data",
                "validate_supplier_data",
                "validate_email",
                "validate_phone",
                "validate_required_fields",
                "validate_string_length",
                "validate_numeric_range",
                "validate_date_format",
                "validate_business_rules",
            },
            "formatting": {
                "format_currency",
                "format_phone",
                "format_date",
                "format_address",
                "format_datetime",
                "format_duration",
                "format_percentage",
                "format_number_with_unit",
                "truncate_text",
                "format_file_size",
            },
            "calculations": {
                "calculate_customer_value_score",
                "calculate_quote_total",
                "calculate_pagination",
                "calculate_growth_rate",
                "calculate_average",
                "calculate_weighted_average",
                "calculate_compound_interest",
            },
        }

    def _get_function_patterns(self) -> list[tuple[str, str, str]]:
        """获取需要检查的函数模式 - 只检查确实存在于transfunctions中的函数"""
        patterns = []

        # 只检查具体的已知函数，避免误报
        for module_type, functions in self.available_functions.items():
            patterns.extend(
                [
                    (
                        rf"def {func_name}\s*\(",
                        f"transfunctions.{module_type}.{func_name}",
                        module_type,
                    )
                    for func_name in functions
                ]
            )

        return patterns

    def _check_imports(self, content: str) -> dict[str, bool]:
        """检查文件中的transfunctions导入情况"""
        imports = {
            "validation": False,
            "formatting": False,
            "calculations": False,
            "general": False,
        }

        # 检查各种导入方式
        import_patterns = [
            (r"from transfunctions\.validation import", "validation"),
            (r"from transfunctions\.formatting import", "formatting"),
            (r"from transfunctions\.calculations import", "calculations"),
            (r"from transfunctions import", "general"),
            (r"import transfunctions", "general"),
        ]

        for pattern, import_type in import_patterns:
            if re.search(pattern, content):
                imports[import_type] = True

        return imports

    def _analyze_function_usage(self, content: str, file_path: Path) -> list[str]:
        """分析函数使用情况，检测重复实现"""
        file_issues = []
        patterns = self._get_function_patterns()
        imports = self._check_imports(content)
        found_functions = set()  # 避免重复检测同一个函数

        for pattern, suggested_import, module_type in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)

            for match in matches:
                func_def = match.group(0)
                line_num = content[: match.start()].count("\n") + 1
                func_name = func_def.split("(")[0].replace("def ", "").strip()

                # 避免重复检测同一个函数
                func_key = f"{file_path}:{line_num}:{func_name}"
                if func_key in found_functions:
                    continue
                found_functions.add(func_key)

                # 检查是否已经正确导入
                has_correct_import = (
                    imports[module_type]
                    or imports["general"]
                    or f"from transfunctions.{module_type} import" in content
                    or f"from transfunctions import {func_name}" in content
                )

                if not has_correct_import:
                    self.stats["violations_found"] += 1
                    self.stats["functions_to_replace"] += 1

                    file_issues.append(
                        f"❌ {file_path}:{line_num} - 重复实现: {func_def.strip()}"
                    )
                    file_issues.append(f"   💡 建议使用: {suggested_import}")
                    file_issues.append(
                        f"   🔧 添加导入: from transfunctions.{module_type} "
                        f"import {func_name}"
                    )

        return file_issues

    def check_file(self, file_path: Path) -> None:
        """检查单个文件"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            self.stats["files_checked"] += 1
            file_issues = self._analyze_function_usage(content, file_path)

            if file_issues:
                self.issues.extend(file_issues)
                self.issues.append("")  # 添加空行分隔

        except Exception as e:
            self.issues.append(f"❌ 检查 {file_path} 时出错: {e}")

    def check_project(self) -> int:
        """检查整个项目"""
        src_dir = Path("src")
        if not src_dir.exists():
            print("⚠️  src目录不存在")
            return 0

        print("🔍 开始检查transfunctions使用情况...")

        # 检查所有Python文件
        for py_file in src_dir.glob("**/*.py"):
            if py_file.name == "__init__.py":
                continue

            # 跳过transfunctions目录本身
            if "transfunctions" in str(py_file):
                continue

            self.check_file(py_file)

        return self._generate_report()

    def _generate_report(self) -> int:
        """生成检查报告"""
        print("\n📊 检查统计:")
        print(f"   📁 检查文件数: {self.stats['files_checked']}")
        print(f"   ⚠️  违规数量: {self.stats['violations_found']}")
        print(f"   🔄 需要替换的函数: {self.stats['functions_to_replace']}")

        if self.issues:
            print("\n🚨 发现transfunctions使用违规:")
            for issue in self.issues:
                if issue.strip():  # 跳过空行
                    print(f"   {issue}")

            print("\n💡 修复建议:")
            print("   1. 删除重复实现的函数")
            print("   2. 使用transfunctions中的对应函数")
            print("   3. 添加必要的导入语句")
            print("   4. 更新函数调用为transfunctions版本")

            print("\n🔧 快速修复命令:")
            print("   python scripts/fix_transfunctions_usage.py")

            return 1

        print("✅ Transfunctions使用符合标准")
        return 0


def main():
    """主函数"""
    checker = TransfunctionsChecker()
    return checker.check_project()


if __name__ == "__main__":
    sys.exit(main())
