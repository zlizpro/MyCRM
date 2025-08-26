#!/bin/bash

# MiniCRM 依赖修复脚本
# 基于UV依赖管理检查结果的自动修复

echo "🔧 开始修复MiniCRM项目依赖..."

# 1. 备份当前配置
echo "📦 备份当前pyproject.toml..."
cp pyproject.toml pyproject.toml.backup

# 2. 使用修复后的配置
echo "🔄 应用修复后的依赖配置..."
cp pyproject_fixed.toml pyproject.toml

# 3. 同步依赖
echo "⬇️ 同步依赖到虚拟环境..."
uv sync

# 4. 检查依赖状态
echo "🔍 检查依赖状态..."
uv tree

# 5. 安全检查
echo "🛡️ 执行安全检查..."
uv run safety check || echo "⚠️ 安全检查发现问题，请查看详情"

# 6. 验证核心功能
echo "✅ 验证核心依赖导入..."
uv run python -c "
try:
    import tkinter
    import tkinter.ttk
    print('✅ tkinter/ttk: OK')
except ImportError as e:
    print(f'❌ tkinter/ttk: {e}')

try:
    import docxtpl
    print('✅ docxtpl: OK')
except ImportError as e:
    print(f'❌ docxtpl: {e}')

try:
    import openpyxl
    print('✅ openpyxl: OK')
except ImportError as e:
    print(f'❌ openpyxl: {e}')

try:
    import pydantic
    print('✅ pydantic: OK')
except ImportError as e:
    print(f'❌ pydantic: {e}')
"

echo "🎉 依赖修复完成！"
echo ""
echo "📋 修复总结："
echo "  - 移除了未使用的核心依赖 (pandas, numpy, matplotlib等)"
echo "  - 将核心功能依赖移到主依赖 (docxtpl, openpyxl, pydantic)"
echo "  - 保持可选依赖的灵活性"
echo "  - 统一使用tkinter/ttk作为GUI框架"
echo ""
echo "🚀 下一步建议："
echo "  1. 运行测试: uv run pytest"
echo "  2. 检查代码质量: uv run ruff check"
echo "  3. 更新任务文档中的技术栈说明"
