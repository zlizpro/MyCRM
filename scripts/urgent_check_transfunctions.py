#!/usr/bin/env python3
"""
紧急检查transfunctions使用情况的脚本

这个脚本会扫描代码中的重复实现，
并建议使用transfunctions中的对应函数。
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


class TransfunctionsChecker:
    """transfunctions使用检查器"""

    def __init__(self):
        # 应该使用transfunctions的函数模式
        self.validation_patterns = [
            r"validate_.*_data",
            r"validate_email",
            r"validate_phone",
            r"validate_.*",
            r"check_.*_valid",
            r"is_valid_.*",
        ]

        self.formatting_patterns = [
            r"format_.*",
            r"_format_.*",
            r"format_cell_value",
            r"format_currency",
            r"format_date",
            r"format_phone",
            r"format_address",
        ]

        self.calculation_patterns = [
            r"calculate_.*",
            r"_calculate_.*",
            r"calc_.*",
            r"compute_.*",
        ]

        # transfunctions中已有的函数
        self.available_transfunctions = {
            "validation": [
                "validate_customer_data",
                "validate_supplier_data",
                "validate_email",
                "validate_phone",
                "validate_required_fields",
                "validate_data_types",
            ],
            "formatting": [
                "format_currency",
                "format_phone",
                "format_date",
                "format_address",
                "format_percentage",
                "format_number",
            ],
            "calculations": [
                "calculate_customer_value_score",
                "calculate_quote_total",
                "calculate_pagination",
                "calculate_age",
                "calculate_discount",
            ],
        }

    def scan_file(self, file_path: Path) -> Dict:
        """扫描文件中的函数定义"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查是否已经导入transfunctions
            has_transfunctions_import = "from transfunctions" in content

            # 解析AST
            tree = ast.parse(content)

            result = {
                "file_path": file_path,
                "has_transfunctions_import": has_transfunctions_import,
                "duplicate_functions": [],
                "missing_imports": [],
                "suggestions": [],
            }

            # 扫描函数定义
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name

                    # 检查是否是应该使用transfunctions的函数
                    suggestions = self._check_function_name(func_name)
                    if suggestions:
                        result["duplicate_functions"].append(
                            {
                                "name": func_name,
                                "lineno": node.lineno,
                                "suggestions": suggestions,
                            }
                        )

            # 检查缺失的导入
            if result["duplicate_functions"] and not has_transfunctions_import:
                needed_modules = set()
                for func_info in result["duplicate_functions"]:
                    for suggestion in func_info["suggestions"]:
                        needed_modules.add(suggestion["module"])

                result["missing_imports"] = list(needed_modules)

            return result

        except Exception as e:
            print(f"❌ 扫描文件 {file_path} 时出错: {e}")
            return None

    def _check_function_name(self, func_name: str) -> List[Dict]:
        """检查函数名是否应该使用transfunctions"""
        suggestions = []

        # 检查验证函数
        for pattern in self.validation_patterns:
            if re.match(pattern, func_name):
                # 查找相似的transfunctions
                similar_funcs = self._find_similar_functions(
                    func_name, self.available_transfunctions["validation"]
                )
                if similar_funcs:
                    suggestions.extend(
                        [
                            {
                                "type": "validation",
                                "module": "transfunctions.validation",
                                "function": func,
                                "reason": f"验证函数应使用transfunctions.validation.{func}",
                            }
                            for func in similar_funcs
                        ]
                    )
                break

        # 检查格式化函数
        for pattern in self.formatting_patterns:
            if re.match(pattern, func_name):
                similar_funcs = self._find_similar_functions(
                    func_name, self.available_transfunctions["formatting"]
                )
                if similar_funcs:
                    suggestions.extend(
                        [
                            {
                                "type": "formatting",
                                "module": "transfunctions.formatting",
                                "function": func,
                                "reason": f"格式化函数应使用transfunctions.formatting.{func}",
                            }
                            for func in similar_funcs
                        ]
                    )
                break

        # 检查计算函数
        for pattern in self.calculation_patterns:
            if re.match(pattern, func_name):
                similar_funcs = self._find_similar_functions(
                    func_name, self.available_transfunctions["calculations"]
                )
                if similar_funcs:
                    suggestions.extend(
                        [
                            {
                                "type": "calculations",
                                "module": "transfunctions.calculations",
                                "function": func,
                                "reason": f"计算函数应使用transfunctions.calculations.{func}",
                            }
                            for func in similar_funcs
                        ]
                    )
                break

        return suggestions

    def _find_similar_functions(
        self, func_name: str, available_funcs: List[str]
    ) -> List[str]:
        """查找相似的函数名"""
        similar = []

        # 精确匹配
        if func_name in available_funcs:
            similar.append(func_name)
            return similar

        # 去掉前缀后匹配
        clean_name = func_name.lstrip("_")
        if clean_name in available_funcs:
            similar.append(clean_name)
            return similar

        # 模糊匹配
        for available_func in available_funcs:
            # 检查关键词匹配
            func_keywords = set(func_name.lower().split("_"))
            available_keywords = set(available_func.lower().split("_"))

            # 如果有共同关键词，认为是相似的
            if func_keywords & available_keywords:
                similar.append(available_func)

        return similar

    def generate_fix_suggestions(self, scan_result: Dict) -> List[str]:
        """生成修复建议"""
        suggestions = []

        if not scan_result or not scan_result["duplicate_functions"]:
            return suggestions

        file_path = scan_result["file_path"]

        # 添加导入建议
        if scan_result["missing_imports"]:
            suggestions.append("📥 添加缺失的导入:")
            for module in scan_result["missing_imports"]:
                suggestions.append(f"   from {module} import *")
            suggestions.append("")

        # 添加函数替换建议
        suggestions.append("🔄 替换重复实现的函数:")
        for func_info in scan_result["duplicate_functions"]:
            func_name = func_info["name"]
            lineno = func_info["lineno"]

            suggestions.append(f"   第{lineno}行: {func_name}()")

            for suggestion in func_info["suggestions"]:
                suggestions.append(
                    f"      → 使用 {suggestion['module']}.{suggestion['function']}"
                )
                suggestions.append(f"        理由: {suggestion['reason']}")

            suggestions.append("")

        return suggestions


def main():
    """主函数"""
    print("🔍 开始检查transfunctions使用情况...")

    # 扫描UI组件目录
    ui_components_dir = Path("src/minicrm/ui/components")

    if not ui_components_dir.exists():
        print(f"❌ 目录不存在: {ui_components_dir}")
        return

    checker = TransfunctionsChecker()

    total_files = 0
    files_with_issues = 0
    total_duplicate_functions = 0

    print(f"📂 扫描目录: {ui_components_dir}")
    print()

    # 扫描所有Python文件
    for py_file in ui_components_dir.glob("**/*.py"):
        if py_file.name == "__init__.py":
            continue

        total_files += 1

        scan_result = checker.scan_file(py_file)
        if not scan_result:
            continue

        duplicate_count = len(scan_result["duplicate_functions"])

        if duplicate_count > 0:
            files_with_issues += 1
            total_duplicate_functions += duplicate_count

            print(f"📄 {py_file.name}")
            print(f"   🔍 发现 {duplicate_count} 个重复实现的函数")

            if not scan_result["has_transfunctions_import"]:
                print(f"   ⚠️  缺少transfunctions导入")

            # 生成修复建议
            suggestions = checker.generate_fix_suggestions(scan_result)
            if suggestions:
                print("   💡 修复建议:")
                for suggestion in suggestions:
                    if suggestion:
                        print(f"      {suggestion}")

            print()

    # 输出总结
    print("📊 检查总结:")
    print(f"   - 检查文件: {total_files} 个")
    print(f"   - 有问题文件: {files_with_issues} 个")
    print(f"   - 重复函数: {total_duplicate_functions} 个")

    if files_with_issues > 0:
        print(f"\n🚨 发现 {files_with_issues} 个文件违反transfunctions使用原则!")
        print(f"   必须立即修复这些重复实现")
    else:
        print(f"\n✅ 所有文件都正确使用了transfunctions")

    print(f"\n🎯 下一步:")
    print(f"   1. 按照建议添加transfunctions导入")
    print(f"   2. 删除重复实现的函数")
    print(f"   3. 使用transfunctions中的对应函数")
    print(f"   4. 运行测试确保功能正常")

    # 生成详细报告
    report_file = Path("transfunctions_usage_report.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Transfunctions使用情况报告\n\n")
        f.write(f"生成时间: {Path().cwd()}\n\n")
        f.write(f"## 检查总结\n\n")
        f.write(f"- 检查文件: {total_files} 个\n")
        f.write(f"- 有问题文件: {files_with_issues} 个\n")
        f.write(f"- 重复函数: {total_duplicate_functions} 个\n\n")

        if files_with_issues > 0:
            f.write(f"## 需要修复的文件\n\n")

            # 重新扫描生成详细报告
            for py_file in ui_components_dir.glob("**/*.py"):
                if py_file.name == "__init__.py":
                    continue

                scan_result = checker.scan_file(py_file)
                if scan_result and scan_result["duplicate_functions"]:
                    f.write(f"### {py_file.name}\n\n")

                    suggestions = checker.generate_fix_suggestions(scan_result)
                    for suggestion in suggestions:
                        f.write(f"{suggestion}\n")

                    f.write("\n")

    print(f"\n📄 详细报告已保存到: {report_file}")


if __name__ == "__main__":
    main()
