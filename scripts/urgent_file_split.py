#!/usr/bin/env python3
"""
紧急文件拆分脚本

自动拆分超大文件，确保每个文件不超过200行限制。
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# 文件拆分配置
SPLIT_CONFIG = {
    "form_panel.py": {
        "target_dir": "src/minicrm/ui/components/form/",
        "splits": [
            {
                "name": "form_panel.py",
                "lines": 150,
                "pattern": r"class FormPanel.*?(?=class|\Z)",
                "desc": "主面板",
            },
            {
                "name": "field_factory.py",
                "lines": 120,
                "pattern": r"def _create_.*?field.*?(?=def|\Z)",
                "desc": "字段工厂",
            },
            {
                "name": "form_validator.py",
                "lines": 100,
                "pattern": r"def validate.*?(?=def|\Z)",
                "desc": "验证器",
            },
            {
                "name": "form_data_binder.py",
                "lines": 80,
                "pattern": r"def.*?data.*?(?=def|\Z)",
                "desc": "数据绑定",
            },
            {
                "name": "form_layout_manager.py",
                "lines": 90,
                "pattern": r"def.*?layout.*?(?=def|\Z)",
                "desc": "布局管理",
            },
            {
                "name": "form_styles.py",
                "lines": 60,
                "pattern": r".*style.*",
                "desc": "样式定义",
            },
        ],
    },
    "data_table.py": {
        "target_dir": "src/minicrm/ui/components/table/",
        "splits": [
            {
                "name": "data_table.py",
                "lines": 180,
                "pattern": r"class DataTable.*?(?=class|\Z)",
                "desc": "主表格",
            },
            {
                "name": "table_export_manager.py",
                "lines": 80,
                "pattern": r"def.*?export.*?(?=def|\Z)",
                "desc": "导出管理",
            },
        ],
    },
}


def analyze_file_structure(file_path: Path) -> Dict:
    """分析文件结构"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 分析类和函数
        classes = re.findall(r"^class\s+(\w+).*?:", content, re.MULTILINE)
        functions = re.findall(r"^def\s+(\w+).*?:", content, re.MULTILINE)

        return {
            "total_lines": len(content.split("\n")),
            "classes": classes,
            "functions": functions,
            "imports": re.findall(r"^(?:from|import)\s+.*", content, re.MULTILINE),
        }
    except Exception as e:
        print(f"❌ 分析文件失败 {file_path}: {e}")
        return {}


def create_split_plan(file_path: Path) -> List[Dict]:
    """创建拆分计划"""
    file_name = file_path.name

    if file_name not in SPLIT_CONFIG:
        # 自动生成拆分计划
        analysis = analyze_file_structure(file_path)
        total_lines = analysis.get("total_lines", 0)

        if total_lines <= 200:
            return []

        # 简单拆分策略：按类拆分
        splits = []
        classes = analysis.get("classes", [])

        if len(classes) > 1:
            for i, class_name in enumerate(classes):
                splits.append(
                    {
                        "name": f"{file_path.stem}_{class_name.lower()}.py",
                        "lines": min(200, total_lines // len(classes)),
                        "pattern": f"class {class_name}.*?(?=class|\\Z)",
                        "desc": f"{class_name}类",
                    }
                )
        else:
            # 按函数组拆分
            functions = analysis.get("functions", [])
            chunk_size = max(1, len(functions) // ((total_lines // 200) + 1))

            for i in range(0, len(functions), chunk_size):
                chunk_functions = functions[i : i + chunk_size]
                splits.append(
                    {
                        "name": f"{file_path.stem}_part{i // chunk_size + 1}.py",
                        "lines": 200,
                        "pattern": "|".join(
                            [f"def {func}.*?(?=def|\\Z)" for func in chunk_functions]
                        ),
                        "desc": f"功能模块{i // chunk_size + 1}",
                    }
                )

        return splits

    return SPLIT_CONFIG[file_name]["splits"]


def main():
    """主函数"""
    print("🔧 开始紧急文件拆分...")

    # 扫描超大文件
    ui_components_dir = Path("src/minicrm/ui/components")
    large_files = []

    for py_file in ui_components_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                line_count = len(f.readlines())

            if line_count > 200:
                large_files.append((py_file, line_count))
        except Exception as e:
            print(f"❌ 检查文件失败 {py_file}: {e}")

    # 按行数排序
    large_files.sort(key=lambda x: x[1], reverse=True)

    print(f"\n📊 发现 {len(large_files)} 个超大文件:")
    for file_path, line_count in large_files:
        percentage = (line_count / 200) * 100
        print(f"   - {file_path.name}: {line_count}行 ({percentage:.0f}% 超标)")

    # 生成拆分计划
    print(f"\n📋 生成拆分计划:")
    for file_path, line_count in large_files[:5]:  # 只处理前5个最大的文件
        splits = create_split_plan(file_path)

        if splits:
            print(f"\n🔧 {file_path.name} 拆分计划:")
            for split in splits:
                print(f"   → {split['name']}: {split['desc']} (~{split['lines']}行)")
        else:
            print(f"\n⚠️  {file_path.name}: 需要手动拆分")

    print(f"\n🎯 下一步:")
    print(f"   1. 手动执行文件拆分（按照上述计划）")
    print(f"   2. 确保每个拆分文件不超过200行")
    print(f"   3. 更新导入关系")
    print(f"   4. 运行测试验证功能完整性")


if __name__ == "__main__":
    main()
