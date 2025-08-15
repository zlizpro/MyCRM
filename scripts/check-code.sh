#!/bin/bash

# MiniCRM 现代化代码质量检查脚本
# 集成了模块化检查、Ruff、MyPy等工具

set -e

echo "🔧 MiniCRM 现代化代码质量检查"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否在项目根目录
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv未安装，请先安装uv包管理器${NC}"
    echo "安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo -e "${BLUE}📊 开始代码质量检查...${NC}"

# 1. 运行模块化检查
echo -e "${BLUE}🔍 1. 模块化质量检查${NC}"
if python scripts/modularity_check_improved.py --all; then
    echo -e "${GREEN}✅ 模块化检查通过${NC}"
else
    echo -e "${YELLOW}⚠️  发现模块化问题，建议修复${NC}"
fi

echo ""

# 2. 运行Ruff检查
echo -e "${BLUE}🔍 2. Ruff代码检查${NC}"
if uv run ruff check src/ --output-format=concise; then
    echo -e "${GREEN}✅ Ruff检查通过${NC}"
else
    echo -e "${YELLOW}⚠️  发现Ruff问题，可运行自动修复${NC}"
    echo "修复命令: uv run ruff check src/ --fix"
fi

echo ""

# 3. 运行Ruff格式检查
echo -e "${BLUE}🔍 3. Ruff格式检查${NC}"
if uv run ruff format src/ --check; then
    echo -e "${GREEN}✅ 代码格式正确${NC}"
else
    echo -e "${YELLOW}⚠️  代码格式需要调整${NC}"
    echo "修复命令: uv run ruff format src/"
fi

echo ""

# 4. 运行MyPy类型检查
echo -e "${BLUE}🔍 4. MyPy类型检查${NC}"
if uv run mypy src/minicrm/ --show-error-codes --no-error-summary; then
    echo -e "${GREEN}✅ 类型检查通过${NC}"
else
    echo -e "${YELLOW}⚠️  发现类型问题，建议添加类型注解${NC}"
fi

echo ""

# 5. 运行测试（如果存在）
if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
    echo -e "${BLUE}🔍 5. 运行测试${NC}"
    if uv run pytest tests/ -v; then
        echo -e "${GREEN}✅ 测试通过${NC}"
    else
        echo -e "${RED}❌ 测试失败${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  未找到测试文件${NC}"
fi

echo ""

# 6. 检查依赖安全性（可选）
echo -e "${BLUE}🔍 6. 依赖安全检查${NC}"
if command -v safety &> /dev/null; then
    if uv run safety check; then
        echo -e "${GREEN}✅ 依赖安全检查通过${NC}"
    else
        echo -e "${YELLOW}⚠️  发现安全问题${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Safety未安装，跳过安全检查${NC}"
fi

echo ""
echo -e "${BLUE}📋 检查完成总结${NC}"
echo "=================================="

# 提供修复建议
echo -e "${BLUE}🛠️  快速修复命令:${NC}"
echo "# 自动修复Ruff问题"
echo "uv run ruff check src/ --fix"
echo "uv run ruff format src/"
echo ""
echo "# 重新运行完整检查"
echo "./scripts/check-code.sh"
echo ""
echo "# 运行模块化检查并自动修复"
echo "python scripts/modularity_check_improved.py --all --fix"

echo ""
echo -e "${GREEN}🚀 代码质量检查完成！${NC}"
