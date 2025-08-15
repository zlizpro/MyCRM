#!/usr/bin/env python3
"""
自动修复transfunctions使用违规

自动替换重复实现的函数，使用transfunctions中的对应函数。
"""

import re
import sys
from pathlib import Path


class TransfunctionsFixer:
    """Transfunctions使用违规自动修复器"""

    def __init__(self):
        """初始化修复器"""
        self.fixes_applied = 0
        self.files_modified = 0

        # 定义需要替换的函数映射
        self.function_replacements = {
            "format_phone": {
                "module": "transfunctions.formatting",
                "import_line": "from transfunctions.formatting import format_phone",
                "replacement_note": "# 使用transfunctions中的format_phone函数",
            },
            "format_currency": {
                "module": "transfunctions.formatting",
                "import_line": "from transfunctions.formatting import format_currency",
                "replacement_note": "# 使用transfunctions中的format_currency函数",
            },
            "format_date": {
                "module": "transfunctions.formatting",
                "import_line": "from transfunctions.formatting import format_date",
                "replacement_note": "# 使用transfunctions中的format_date函数",
            },
            "validate_customer_data": {
                "module": "transfunctions.validation",
                "import_line": "from transfunctions.validation import validate_customer_data",
                "replacement_note": "# 使用transfunctions中的validate_customer_data函数",
            },
            "validate_supplier_data": {
                "module": "transfunctions.validation",
                "import_line": "from transfunctions.validation import validate_supplier_data",
                "replacement_note": "# 使用transfunctions中的validate_supplier_data函数",
            },
        }

    def _has_import(self, content: str, import_line: str) -> bool:
        """检查文件是否已经有相应的导入"""
        # 检查完整的导入语句
        if import_line in content:
            return True

        # 检查是否有通用的transfunctions导入
        if "from transfunctions import" in content:
            return True

        return False

    def _add_import(self, content: str, import_line: str) -> str:
        """添加导入语句到文件开头"""
        lines = content.split("\n")

        # 找到合适的位置插入导入语句
        insert_index = 0

        # 跳过文档字符串和编码声明
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                # 找到文档字符串的结束
                quote = '"""' if line.strip().startswith('"""') else "'''"
                if line.count(quote) >= 2:
                    insert_index = i + 1
                else:
                    for j in range(i + 1, len(lines)):
                        if quote in lines[j]:
                            insert_index = j + 1
                            break
                break
            elif line.strip().startswith("#") or line.strip() == "":
                continue
            else:
                insert_index = i
                break

        # 找到导入语句的位置
        import_section_start = insert_index
        import_section_end = insert_index

        for i in range(insert_index, len(lines)):
            line = lines[i].strip()
            if line.startswith("import ") or line.startswith("from "):
                if import_section_start == insert_index:
                    import_section_start = i
                import_section_end = i + 1
            elif line == "":
                continue
            else:
                break

        # 插入新的导入语句
        if import_section_start == insert_index:
            # 没有现有的导入语句，在文档字符串后插入
            lines.insert(insert_index, "")
            lines.insert(insert_index + 1, import_line)
            lines.insert(insert_index + 2, "")
        else:
            # 在现有导入语句中插入
            lines.insert(import_section_end, import_line)

        return "\n".join(lines)

    def _remove_function_definition(self, content: str, func_name: str) -> str:
        """移除函数定义"""
        # 找到函数定义的开始
        pattern = rf"def {func_name}\s*\([^)]*\).*?:"
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

        if not match:
            return content

        lines = content.split("\n")
        start_line = content[: match.start()].count("\n")

        # 找到函数的结束位置（下一个同级别的def或class，或文件结束）
        end_line = len(lines)
        func_indent = len(lines[start_line]) - len(lines[start_line].lstrip())

        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if line.strip() == "":
                continue

            current_indent = len(line) - len(line.lstrip())

            # 如果遇到同级别或更高级别的定义，函数结束
            if current_indent <= func_indent and (
                line.strip().startswith("def ")
                or line.strip().startswith("class ")
                or line.strip().startswith("@")
            ):
                end_line = i
                break

        # 移除函数定义
        replacement_comment = (
            f"# {func_name} 函数已移除，请使用 transfunctions.formatting.{func_name}"
        )
        lines[start_line:end_line] = [replacement_comment, ""]

        return "\n".join(lines)

    def fix_file(self, file_path: Path) -> bool:
        """修复单个文件"""
        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            content = original_content
            file_modified = False

            # 检查每个需要替换的函数
            for func_name, replacement_info in self.function_replacements.items():
                # 检查是否存在该函数的定义
                pattern = rf"def {func_name}\s*\("
                if re.search(pattern, content):
                    print(f"  🔧 修复 {file_path} 中的 {func_name} 函数")

                    # 添加导入语句（如果还没有）
                    if not self._has_import(content, replacement_info["import_line"]):
                        content = self._add_import(
                            content, replacement_info["import_line"]
                        )
                        print(f"    ✅ 添加导入: {replacement_info['import_line']}")

                    # 移除函数定义
                    content = self._remove_function_definition(content, func_name)
                    print(f"    ✅ 移除重复实现的 {func_name} 函数")

                    file_modified = True
                    self.fixes_applied += 1

            # 如果文件被修改，写回文件
            if file_modified:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.files_modified += 1
                return True

            return False

        except Exception as e:
            print(f"❌ 修复 {file_path} 时出错: {e}")
            return False

    def fix_project(self) -> int:
        """修复整个项目"""
        src_dir = Path("src")
        if not src_dir.exists():
            print("⚠️  src目录不存在")
            return 0

        print("🔧 开始自动修复transfunctions使用违规...")

        # 需要修复的文件列表（基于检查脚本的结果）
        files_to_fix = [
            "src/minicrm/core/utils.py",
            "src/minicrm/ui/components/table_data_manager.py",
            "src/minicrm/data/dao/model_converter.py",
        ]

        for file_path_str in files_to_fix:
            file_path = Path(file_path_str)
            if file_path.exists():
                print(f"\n📁 处理文件: {file_path}")
                self.fix_file(file_path)
            else:
                print(f"⚠️  文件不存在: {file_path}")

        return self._generate_report()

    def _generate_report(self) -> int:
        """生成修复报告"""
        print("\n📊 修复统计:")
        print(f"   📁 修改文件数: {self.files_modified}")
        print(f"   🔧 应用修复数: {self.fixes_applied}")

        if self.fixes_applied > 0:
            print("\n✅ 修复完成！")
            print("\n💡 后续步骤:")
            print("   1. 检查修改的文件，确保功能正常")
            print("   2. 运行测试确保没有破坏现有功能")
            print("   3. 再次运行检查脚本验证修复效果")
            print("   4. 提交修改到版本控制")

            print("\n🔍 验证修复效果:")
            print("   python scripts/check_transfunctions_usage.py")

            return 0
        else:
            print("ℹ️  没有发现需要修复的问题")
            return 0


def main():
    """主函数"""
    fixer = TransfunctionsFixer()
    return fixer.fix_project()


if __name__ == "__main__":
    sys.exit(main())
