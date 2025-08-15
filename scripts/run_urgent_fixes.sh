#!/bin/bash
# MiniCRM紧急修复执行脚本
#
# 这个脚本会按顺序执行所有紧急修复任务，
# 确保代码质量符合MiniCRM开发标准。

set -e  # 遇到错误立即退出

echo "🚨 开始执行MiniCRM紧急代码质量修复..."
echo "=================================================="

# 检查必要的工具
echo "🔧 检查开发工具..."
if ! command -v uv &> /dev/null; then
    echo "❌ 错误: 未安装uv包管理器"
    echo "请先安装uv: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未安装Python"
    exit 1
fi

echo "✅ 开发工具检查完成"

# 步骤1: 运行初始质量检查
echo ""
echo "📊 步骤1: 运行初始质量检查..."
echo "=================================================="
python scripts/urgent_quality_gate.py || echo "⚠️  发现质量问题，继续修复流程..."

# 步骤2: 修复Qt API使用错误
echo ""
echo "🔧 步骤2: 修复Qt API使用错误..."
echo "=================================================="
python scripts/urgent_fix_qt_api.py

# 步骤3: 检查transfunctions使用情况
echo ""
echo "🔍 步骤3: 检查transfunctions使用情况..."
echo "=================================================="
python scripts/urgent_check_transfunctions.py

# 步骤4: 创建文件拆分计划
echo ""
echo "📂 步骤4: 创建文件拆分计划..."
echo "=================================================="
python scripts/urgent_split_large_files.py

# 步骤5: 运行自动格式化
echo ""
echo "🎨 步骤5: 运行代码格式化..."
echo "=================================================="
echo "运行Ruff格式化..."
uv run ruff format src/minicrm/ui/components/ || echo "⚠️  格式化过程中有警告"

echo "运行Ruff自动修复..."
uv run ruff check src/minicrm/ui/components/ --fix || echo "⚠️  自动修复过程中有警告"

# 步骤6: 运行最终质量检查
echo ""
echo "✅ 步骤6: 运行最终质量检查..."
echo "=================================================="
if python scripts/urgent_quality_gate.py; then
    echo ""
    echo "🎉 恭喜！所有紧急修复任务已完成！"
    echo "=================================================="
    echo "✅ 代码质量现在符合MiniCRM开发标准"
    echo "✅ 可以继续进行功能开发"
    echo ""
    echo "📋 下一步建议:"
    echo "1. 查看生成的重构指南文件"
    echo "2. 手动完成文件拆分工作"
    echo "3. 运行完整的测试套件"
    echo "4. 提交代码到版本控制"
else
    echo ""
    echo "⚠️  仍有部分问题需要手动修复"
    echo "=================================================="
    echo "📄 请查看 quality_gate_report.md 了解详细信息"
    echo "🛠️  按照报告中的修复建议继续处理"
    echo ""
    echo "🔄 修复完成后，重新运行此脚本验证:"
    echo "   ./scripts/run_urgent_fixes.sh"
fi

echo ""
echo "📊 修复过程统计:"
echo "- Qt API修复: 已完成"
echo "- Transfunctions检查: 已完成"
echo "- 文件拆分计划: 已创建"
echo "- 代码格式化: 已完成"
echo "- 质量门禁: $(python scripts/urgent_quality_gate.py >/dev/null 2>&1 && echo '通过' || echo '需要手动修复')"

echo ""
echo "🎯 重要提醒:"
echo "在完成所有紧急修复任务之前，请勿进行新功能开发！"
