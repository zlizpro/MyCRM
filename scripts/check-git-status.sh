#!/bin/bash
# GitHub提交前快速检查脚本

echo "🔍 检查Git状态和潜在问题文件..."

# 检查Git状态
echo "📋 当前Git状态:"
git status --porcelain

echo ""
echo "🚨 检查敏感文件模式:"

# 检查是否有数据库文件
find . -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3" | grep -v ".git" | head -10

# 检查是否有大文件
echo ""
echo "📦 检查大文件 (>1MB):"
find . -type f -size +1M | grep -v ".git" | grep -v ".venv" | grep -v "__pycache__" | head -10

# 检查是否有临时文件
echo ""
echo "🗑️ 检查临时文件:"
find . -name "*~" -o -name "*.tmp" -o -name "*.bak" -o -name "*_temp.py" -o -name "*_backup.py" | grep -v ".git" | head -10

# 检查是否有测试数据文件
echo ""
echo "🧪 检查测试数据文件:"
find . -name "test_*.xlsx" -o -name "test_*.pdf" -o -name "test_*.docx" -o -name "dummy.*" | grep -v ".git" | head -10

# 检查缓存目录
echo ""
echo "🔧 检查缓存目录:"
find . -type d -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" | grep -v ".git" | head -10

echo ""
echo "✅ 检查完成！请确认上述文件是否应该被.gitignore排除。"
