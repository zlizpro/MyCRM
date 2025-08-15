#!/bin/bash
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
