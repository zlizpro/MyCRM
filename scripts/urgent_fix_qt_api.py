#!/usr/bin/env python3
"""
紧急修复Qt API使用错误的脚本

这个脚本会自动修复UI组件中的Qt API使用错误，
将旧的枚举值替换为正确的新版本。
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Qt API修复映射表
QT_API_FIXES = {
    # ScrollBar相关
    r"Qt\.ScrollBarAsNeeded": "Qt.ScrollBarPolicy.ScrollBarAsNeeded",
    r"Qt\.ScrollBarAlwaysOff": "Qt.ScrollBarPolicy.ScrollBarAlwaysOff",
    r"Qt\.ScrollBarAlwaysOn": "Qt.ScrollBarPolicy.ScrollBarAlwaysOn",
    # QHeaderView相关
    r"QHeaderView\.Stretch": "QHeaderView.ResizeMode.Stretch",
    r"QHeaderView\.Fixed": "QHeaderView.ResizeMode.Fixed",
    r"QHeaderView\.Interactive": "QHeaderView.ResizeMode.Interactive",
    # QTableWidget/QAbstractItemView相关
    r"QTableWidget\.SelectRows": "QAbstractItemView.SelectionBehavior.SelectRows",
    r"QTableWidget\.SelectColumns": "QAbstractItemView.SelectionBehavior.SelectColumns",
    r"QTableWidget\.SelectItems": "QAbstractItemView.SelectionBehavior.SelectItems",
    r"QTableWidget\.MultiSelection": "QAbstractItemView.SelectionMode.MultiSelection",
    r"QTableWidget\.SingleSelection": "QAbstractItemView.SelectionMode.SingleSelection",
    r"QTableWidget\.ExtendedSelection": "QAbstractItemView.SelectionMode.ExtendedSelection",
    # Qt Context Menu相关
    r"Qt\.CustomContextMenu": "Qt.ContextMenuPolicy.CustomContextMenu",
    r"Qt\.NoContextMenu": "Qt.ContextMenuPolicy.NoContextMenu",
    # QLineEdit相关
    r"QLineEdit\.Password": "QLineEdit.EchoMode.Password",
    r"QLineEdit\.Normal": "QLineEdit.EchoMode.Normal",
    # QMessageBox相关
    r"QMessageBox\.Yes": "QMessageBox.StandardButton.Yes",
    r"QMessageBox\.No": "QMessageBox.StandardButton.No",
    r"QMessageBox\.Ok": "QMessageBox.StandardButton.Ok",
    r"QMessageBox\.Cancel": "QMessageBox.StandardButton.Cancel",
    # Qt Date Format相关
    r"Qt\.ISODate": "Qt.DateFormat.ISODate",
    r"Qt\.TextDate": "Qt.DateFormat.TextDate",
    # Qt Alignment相关
    r"Qt\.AlignLeft": "Qt.AlignmentFlag.AlignLeft",
    r"Qt\.AlignRight": "Qt.AlignmentFlag.AlignRight",
    r"Qt\.AlignCenter": "Qt.AlignmentFlag.AlignCenter",
    r"Qt\.AlignTop": "Qt.AlignmentFlag.AlignTop",
    r"Qt\.AlignBottom": "Qt.AlignmentFlag.AlignBottom",
}

# 需要添加的导入
REQUIRED_IMPORTS = {
    "QAbstractItemView": "from PySide6.QtWidgets import QAbstractItemView",
}


def fix_qt_api_in_file(file_path: Path) -> Tuple[bool, List[str]]:
    """
    修复单个文件中的Qt API使用错误

    Args:
        file_path: 文件路径

    Returns:
        (是否有修改, 修改列表)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        changes = []

        # 应用Qt API修复
        for old_pattern, new_value in QT_API_FIXES.items():
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_value, content)
                changes.append(f"替换 {old_pattern} -> {new_value}")

        # 检查是否需要添加导入
        imports_to_add = []
        for import_name, import_statement in REQUIRED_IMPORTS.items():
            if import_name in content and import_statement not in content:
                imports_to_add.append(import_statement)

        # 添加缺失的导入
        if imports_to_add:
            # 找到最后一个from PySide6导入的位置
            lines = content.split("\n")
            insert_index = 0

            for i, line in enumerate(lines):
                if line.strip().startswith("from PySide6"):
                    insert_index = i + 1

            # 在适当位置插入导入
            for import_stmt in imports_to_add:
                lines.insert(insert_index, import_stmt)
                insert_index += 1
                changes.append(f"添加导入: {import_stmt}")

            content = "\n".join(lines)

        # 如果有修改，写回文件
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, changes

        return False, []

    except Exception as e:
        print(f"❌ 修复文件 {file_path} 时出错: {e}")
        return False, []


def main():
    """主函数"""
    print("🔧 开始修复Qt API使用错误...")

    # 扫描UI组件目录
    ui_components_dir = Path("src/minicrm/ui/components")

    if not ui_components_dir.exists():
        print(f"❌ 目录不存在: {ui_components_dir}")
        return

    total_files = 0
    fixed_files = 0
    all_changes = []

    # 遍历所有Python文件
    for py_file in ui_components_dir.glob("**/*.py"):
        if py_file.name == "__init__.py":
            continue

        total_files += 1
        print(f"\n📁 检查文件: {py_file}")

        has_changes, changes = fix_qt_api_in_file(py_file)

        if has_changes:
            fixed_files += 1
            print(f"✅ 修复完成，共 {len(changes)} 处修改:")
            for change in changes:
                print(f"   - {change}")
            all_changes.extend([(py_file, change) for change in changes])
        else:
            print("   ℹ️  无需修复")

    # 输出总结
    print(f"\n📊 修复总结:")
    print(f"   - 检查文件: {total_files} 个")
    print(f"   - 修复文件: {fixed_files} 个")
    print(f"   - 总修改数: {len(all_changes)} 处")

    if all_changes:
        print(f"\n📝 详细修改列表:")
        for file_path, change in all_changes:
            print(f"   {file_path.name}: {change}")

    print(f"\n🎯 下一步:")
    print(f"   1. 运行 'uv run mypy src/minicrm/ui/components/' 验证修复")
    print(f"   2. 运行 'uv run ruff check src/minicrm/ui/components/' 检查代码质量")
    print(f"   3. 测试UI组件功能是否正常")


if __name__ == "__main__":
    main()
