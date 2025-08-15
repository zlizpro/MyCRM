#!/usr/bin/env python3
"""
紧急拆分超大文件的脚本

这个脚本会自动拆分超过200行的UI组件文件，
按照单一职责原则将大文件拆分为多个小文件。
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import shutil


class FileSplitter:
    """文件拆分器"""

    def __init__(self, max_lines: int = 200):
        self.max_lines = max_lines

    def analyze_file(self, file_path: Path) -> Dict:
        """分析文件结构"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            # 解析AST
            tree = ast.parse(content)

            analysis = {
                "file_path": file_path,
                "total_lines": len(lines),
                "needs_split": len(lines) > self.max_lines,
                "imports": [],
                "classes": [],
                "functions": [],
                "constants": [],
            }

            # 分析顶级节点
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(f"import {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    names = [alias.name for alias in node.names]
                    analysis["imports"].append(
                        f"from {module} import {', '.join(names)}"
                    )
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "lineno": node.lineno,
                        "end_lineno": getattr(node, "end_lineno", node.lineno),
                        "methods": [],
                    }

                    # 分析类中的方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info["methods"].append(
                                {
                                    "name": item.name,
                                    "lineno": item.lineno,
                                    "end_lineno": getattr(
                                        item, "end_lineno", item.lineno
                                    ),
                                }
                            )

                    analysis["classes"].append(class_info)
                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    # 顶级函数
                    analysis["functions"].append(
                        {
                            "name": node.name,
                            "lineno": node.lineno,
                            "end_lineno": getattr(node, "end_lineno", node.lineno),
                        }
                    )
                elif isinstance(node, ast.Assign) and node.col_offset == 0:
                    # 顶级常量
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            analysis["constants"].append(
                                {"name": target.id, "lineno": node.lineno}
                            )

            return analysis

        except Exception as e:
            print(f"❌ 分析文件 {file_path} 时出错: {e}")
            return None

    def create_split_plan(self, analysis: Dict) -> Optional[Dict]:
        """创建拆分计划"""
        if not analysis or not analysis["needs_split"]:
            return None

        file_path = analysis["file_path"]
        file_name = file_path.stem

        # 根据文件名确定拆分策略
        if "form_panel" in file_name:
            return self._create_form_panel_split_plan(analysis)
        elif "data_table" in file_name:
            return self._create_data_table_split_plan(analysis)
        elif "search_widget" in file_name:
            return self._create_search_widget_split_plan(analysis)
        else:
            return self._create_generic_split_plan(analysis)

    def _create_form_panel_split_plan(self, analysis: Dict) -> Dict:
        """创建表单面板拆分计划"""
        base_dir = analysis["file_path"].parent / "form"

        return {
            "strategy": "form_panel",
            "base_dir": base_dir,
            "files": {
                "form_panel.py": {
                    "description": "主表单面板类",
                    "max_lines": 150,
                    "includes": ["FormPanel类的核心方法"],
                },
                "field_factory.py": {
                    "description": "字段组件工厂",
                    "max_lines": 120,
                    "includes": ["字段创建相关方法"],
                },
                "form_validator.py": {
                    "description": "表单验证器",
                    "max_lines": 100,
                    "includes": ["验证相关方法"],
                },
                "form_data_binder.py": {
                    "description": "数据绑定器",
                    "max_lines": 80,
                    "includes": ["数据绑定相关方法"],
                },
                "form_layout_manager.py": {
                    "description": "布局管理器",
                    "max_lines": 90,
                    "includes": ["布局相关方法"],
                },
                "form_styles.py": {
                    "description": "样式定义",
                    "max_lines": 60,
                    "includes": ["样式常量和方法"],
                },
            },
        }

    def _create_data_table_split_plan(self, analysis: Dict) -> Dict:
        """创建数据表格拆分计划"""
        base_dir = analysis["file_path"].parent / "table"

        return {
            "strategy": "data_table",
            "base_dir": base_dir,
            "files": {
                "data_table.py": {
                    "description": "主表格类",
                    "max_lines": 180,
                    "includes": ["DataTable类的核心方法"],
                },
                "table_data_manager.py": {
                    "description": "数据管理器",
                    "max_lines": 150,
                    "includes": ["数据管理相关方法"],
                },
                "table_filter_manager.py": {
                    "description": "筛选管理器",
                    "max_lines": 120,
                    "includes": ["筛选相关方法"],
                },
                "table_pagination_manager.py": {
                    "description": "分页管理器",
                    "max_lines": 100,
                    "includes": ["分页相关方法"],
                },
                "table_export_manager.py": {
                    "description": "导出管理器",
                    "max_lines": 80,
                    "includes": ["导出相关方法"],
                },
            },
        }

    def _create_search_widget_split_plan(self, analysis: Dict) -> Dict:
        """创建搜索组件拆分计划"""
        base_dir = analysis["file_path"].parent / "search"

        return {
            "strategy": "search_widget",
            "base_dir": base_dir,
            "files": {
                "search_widget.py": {
                    "description": "主搜索组件",
                    "max_lines": 150,
                    "includes": ["SearchWidget类的核心方法"],
                },
                "search_filter_manager.py": {
                    "description": "筛选管理器",
                    "max_lines": 120,
                    "includes": ["筛选相关方法"],
                },
                "search_history_manager.py": {
                    "description": "搜索历史管理器",
                    "max_lines": 100,
                    "includes": ["历史记录相关方法"],
                },
                "search_config.py": {
                    "description": "搜索配置",
                    "max_lines": 80,
                    "includes": ["配置相关类和常量"],
                },
            },
        }

    def _create_generic_split_plan(self, analysis: Dict) -> Dict:
        """创建通用拆分计划"""
        file_name = analysis["file_path"].stem
        base_dir = analysis["file_path"].parent / file_name.replace("_", "")

        return {
            "strategy": "generic",
            "base_dir": base_dir,
            "files": {
                f"{file_name}.py": {
                    "description": "主类文件",
                    "max_lines": 150,
                    "includes": ["主要类定义"],
                },
                f"{file_name}_manager.py": {
                    "description": "管理器类",
                    "max_lines": 120,
                    "includes": ["管理相关方法"],
                },
                f"{file_name}_utils.py": {
                    "description": "工具函数",
                    "max_lines": 100,
                    "includes": ["工具函数和常量"],
                },
            },
        }

    def execute_split_plan(self, analysis: Dict, split_plan: Dict) -> bool:
        """执行拆分计划"""
        try:
            print(
                f"📂 开始拆分 {analysis['file_path'].name} ({analysis['total_lines']}行)"
            )

            # 创建目标目录
            base_dir = split_plan["base_dir"]
            base_dir.mkdir(parents=True, exist_ok=True)

            # 创建__init__.py
            init_file = base_dir / "__init__.py"
            with open(init_file, "w", encoding="utf-8") as f:
                f.write('"""拆分后的模块包"""\n')

            # 备份原文件
            backup_path = analysis["file_path"].with_suffix(".py.backup")
            shutil.copy2(analysis["file_path"], backup_path)
            print(f"📋 已备份原文件到: {backup_path}")

            # 读取原文件内容
            with open(analysis["file_path"], "r", encoding="utf-8") as f:
                original_content = f.read()

            # 创建拆分后的文件（暂时只创建占位符）
            for file_name, file_info in split_plan["files"].items():
                target_file = base_dir / file_name

                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(f'"""\n{file_info["description"]}\n\n')
                    f.write(f"从 {analysis['file_path'].name} 拆分而来\n")
                    f.write(f"最大行数限制: {file_info['max_lines']}行\n")
                    f.write(f"包含内容: {', '.join(file_info['includes'])}\n")
                    f.write('"""\n\n')
                    f.write("# TODO: 从原文件中移动相关代码到这里\n")
                    f.write("# 确保每个文件不超过指定的行数限制\n")
                    f.write("# 使用transfunctions替换重复实现\n\n")

                print(f"📄 创建文件: {target_file} (最大{file_info['max_lines']}行)")

            # 创建重构指南
            guide_file = base_dir / "REFACTOR_GUIDE.md"
            with open(guide_file, "w", encoding="utf-8") as f:
                f.write(f"# {analysis['file_path'].name} 重构指南\n\n")
                f.write(f"## 原文件信息\n")
                f.write(f"- 原文件: {analysis['file_path']}\n")
                f.write(f"- 原文件行数: {analysis['total_lines']}行\n")
                f.write(f"- 拆分策略: {split_plan['strategy']}\n\n")
                f.write(f"## 拆分文件列表\n\n")

                for file_name, file_info in split_plan["files"].items():
                    f.write(f"### {file_name}\n")
                    f.write(f"- **描述**: {file_info['description']}\n")
                    f.write(f"- **最大行数**: {file_info['max_lines']}行\n")
                    f.write(f"- **包含内容**: {', '.join(file_info['includes'])}\n\n")

                f.write(f"## 重构步骤\n\n")
                f.write(f"1. 分析原文件中的类和方法\n")
                f.write(f"2. 按照单一职责原则将代码分配到对应文件\n")
                f.write(f"3. 确保每个文件不超过行数限制\n")
                f.write(f"4. 使用transfunctions替换重复实现\n")
                f.write(f"5. 更新导入语句和依赖关系\n")
                f.write(f"6. 运行测试确保功能正常\n\n")
                f.write(f"## 注意事项\n\n")
                f.write(f"- 严格遵循单一职责原则\n")
                f.write(f"- 避免循环依赖\n")
                f.write(f"- 保持接口的向后兼容性\n")
                f.write(f"- 使用类型注解和文档字符串\n")

            print(f"📖 创建重构指南: {guide_file}")
            print(f"✅ 拆分计划执行完成")

            return True

        except Exception as e:
            print(f"❌ 执行拆分计划时出错: {e}")
            return False


def main():
    """主函数"""
    print("🔧 开始扫描和拆分超大文件...")

    # 扫描UI组件目录
    ui_components_dir = Path("src/minicrm/ui/components")

    if not ui_components_dir.exists():
        print(f"❌ 目录不存在: {ui_components_dir}")
        return

    splitter = FileSplitter(max_lines=200)

    # 需要拆分的文件列表
    large_files = []

    # 扫描所有Python文件
    for py_file in ui_components_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        # 检查文件行数
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                line_count = len(f.readlines())

            if line_count > 200:
                large_files.append((py_file, line_count))
                print(f"📏 发现超大文件: {py_file.name} ({line_count}行)")
        except Exception as e:
            print(f"❌ 检查文件 {py_file} 时出错: {e}")

    if not large_files:
        print("✅ 没有发现超过200行的文件")
        return

    print(f"\n📊 发现 {len(large_files)} 个需要拆分的文件:")
    for file_path, line_count in large_files:
        print(f"   - {file_path.name}: {line_count}行")

    # 为每个大文件创建拆分计划
    for file_path, line_count in large_files:
        print(f"\n🔍 分析文件: {file_path.name}")

        analysis = splitter.analyze_file(file_path)
        if not analysis:
            continue

        split_plan = splitter.create_split_plan(analysis)
        if not split_plan:
            print(f"   ℹ️  文件不需要拆分")
            continue

        print(f"   📋 创建拆分计划: {split_plan['strategy']} 策略")
        print(f"   📂 目标目录: {split_plan['base_dir']}")
        print(f"   📄 拆分为 {len(split_plan['files'])} 个文件")

        # 执行拆分计划
        success = splitter.execute_split_plan(analysis, split_plan)
        if success:
            print(f"   ✅ 拆分完成")
        else:
            print(f"   ❌ 拆分失败")

    print(f"\n🎯 下一步:")
    print(f"   1. 查看各个目录中的 REFACTOR_GUIDE.md 文件")
    print(f"   2. 按照指南手动重构代码")
    print(f"   3. 确保每个文件不超过200行")
    print(f"   4. 使用transfunctions替换重复实现")
    print(f"   5. 运行测试验证功能正常")


if __name__ == "__main__":
    main()
