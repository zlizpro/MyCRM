#!/usr/bin/env python3
"""
代码质量检查Hook激活脚本
用于在Kiro IDE中激活和配置代码质量检查功能
"""

import json
import sys
from pathlib import Path


def create_kiro_hook_config():
    """创建Kiro IDE Hook配置"""
    hook_config = {
        "name": "code-quality-check",
        "displayName": "代码质量检查",
        "description": "自动检查Python代码质量，包括PEP8、类型注解、文档字符串等",
        "version": "1.0.0",
        "author": "MiniCRM Team",
        "triggers": [
            {
                "event": "file:save",
                "patterns": ["*.py"],
                "exclude": ["__pycache__/**", "*.pyc", "venv/**", ".git/**"]
            }
        ],
        "execution": {
            "command": "python",
            "args": [
                ".kiro/hooks/scripts/kiro_integration.py",
                "file_save",
                "${filePath}"
            ],
            "cwd": "${workspaceRoot}",
            "timeout": 30000,
            "shell": False
        },
        "output": {
            "format": "json",
            "showInProblems": True,
            "showInOutput": True,
            "showNotification": True
        },
        "settings": {
            "enabled": True,
            "autoFix": True,
            "severity": {
                "error": "error",
                "warning": "warning",
                "info": "info"
            }
        },
        "manual": {
            "command": "python",
            "args": [
                ".kiro/hooks/scripts/kiro_integration.py",
                "manual",
                "${selectedFiles}"
            ],
            "title": "检查选中文件的代码质量",
            "icon": "🔍"
        }
    }

    return hook_config


def create_activation_script():
    """创建激活脚本内容"""
    script_content = """#!/bin/bash
# MiniCRM 代码质量检查Hook激活脚本

echo "🚀 正在激活MiniCRM代码质量检查Hook..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3环境"
    exit 1
fi

# 检查必要文件
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQUIRED_FILES=(
    "$SCRIPT_DIR/code_quality_checker.py"
    "$SCRIPT_DIR/kiro_integration.py"
    "$SCRIPT_DIR/quality_config.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ 错误: 缺少必要文件 $file"
        exit 1
    fi
done

# 测试代码质量检查器
echo "🧪 测试代码质量检查器..."
cd "$SCRIPT_DIR"
python3 kiro_integration.py test test_sample.py > /dev/null 2>&1

if [[ $? -eq 0 ]] || [[ $? -eq 2 ]]; then
    echo "✅ 代码质量检查器测试通过"
else
    echo "❌ 代码质量检查器测试失败"
    exit 1
fi

# 创建Hook配置
echo "📝 创建Hook配置..."
python3 activate_hook.py create_config

echo "✅ MiniCRM代码质量检查Hook激活成功！"
echo ""
echo "📋 使用说明:"
echo "   • 保存Python文件时自动触发质量检查"
echo "   • 在问题面板中查看检查结果"
echo "   • 右键选择文件可手动触发检查"
echo "   • 配置文件: .kiro/hooks/scripts/quality_config.json"
echo ""
echo "🎯 下一步:"
echo "   1. 在Kiro IDE中重新加载Hook配置"
echo "   2. 保存一个Python文件测试功能"
echo "   3. 查看问题面板中的检查结果"
"""

    return script_content


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "create_config":
        # 创建Hook配置文件
        config = create_kiro_hook_config()
        config_path = Path(".kiro/hooks/code-quality-check.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"✅ Hook配置已创建: {config_path}")
        return

    # 创建激活脚本
    script_content = create_activation_script()
    script_path = Path(".kiro/hooks/scripts/activate.sh")

    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)

    # 设置执行权限
    script_path.chmod(0o755)

    print("✅ 激活脚本已创建")
    print(f"📁 脚本位置: {script_path}")
    print("🚀 运行以下命令激活Hook:")
    print(f"   bash {script_path}")


if __name__ == '__main__':
    main()
