#!/bin/bash

# MiniCRM 启动脚本 (macOS/Linux版本)
# 这个脚本会自动检测环境并选择合适的方式启动MiniCRM应用程序

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 打印横幅
print_banner() {
    echo "============================================================"
    echo "🏢 MiniCRM 客户关系管理系统"
    echo "💼 基于 Python + tkinter/ttk"
    echo "🚀 正在启动应用程序..."
    echo "============================================================"
    echo ""
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查UV是否可用
check_uv() {
    if command_exists uv; then
        echo -e "${GREEN}✅ 检测到 UV 包管理器${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  未检测到 UV 包管理器${NC}"
        return 1
    fi
}

# 检查虚拟环境
check_venv() {
    if [ -d ".venv" ]; then
        echo -e "${GREEN}✅ 检测到虚拟环境${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  未检测到虚拟环境${NC}"
        return 1
    fi
}

# 检查Python
check_python() {
    if command_exists python3; then
        echo -e "${GREEN}✅ 检测到 Python3${NC}"
        return 0
    elif command_exists python; then
        echo -e "${GREEN}✅ 检测到 Python${NC}"
        return 0
    else
        echo -e "${RED}❌ 未检测到 Python${NC}"
        return 1
    fi
}

# 使用UV运行
run_with_uv() {
    echo -e "${BLUE}🔧 使用 UV 包管理器启动...${NC}"
    uv run minicrm
    return $?
}

# 使用虚拟环境运行
run_with_venv() {
    echo -e "${BLUE}🏠 使用虚拟环境启动...${NC}"
    source .venv/bin/activate
    python -m minicrm
    return $?
}

# 使用Python模块运行
run_with_python() {
    echo -e "${BLUE}🐍 使用 Python 模块启动...${NC}"
    if command_exists python3; then
        python3 -m minicrm
    else
        python -m minicrm
    fi
    return $?
}

# 直接运行main.py
run_direct() {
    echo -e "${BLUE}📁 直接运行主程序文件...${NC}"
    if [ -f "src/minicrm/main.py" ]; then
        if command_exists python3; then
            python3 src/minicrm/main.py
        else
            python src/minicrm/main.py
        fi
        return $?
    else
        echo -e "${RED}❌ 主程序文件未找到: src/minicrm/main.py${NC}"
        return 1
    fi
}

# 显示帮助信息
show_help() {
    echo -e "${RED}❌ 所有启动方法都失败了！${NC}"
    echo ""
    echo -e "${PURPLE}🔧 请检查以下内容：${NC}"
    echo "1. 确保已安装Python 3.9+"
    echo "2. 确保已安装项目依赖"
    echo "   - 使用UV: uv sync --dev"
    echo "   - 使用pip: pip install -e ."
    echo "3. 确保tkinter已正确安装（通常随Python内置）"
    echo "4. 检查项目路径是否正确"
    echo ""
    echo -e "${PURPLE}📖 更多信息请查看 README.md 文件${NC}"
    echo ""
    echo -e "${PURPLE}🛠️  手动安装依赖：${NC}"
    echo "# 如果没有UV，可以安装："
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "# 安装项目依赖："
    echo "uv sync --dev"
    echo "# 或者"
    echo "pip install docxtpl openpyxl pydantic python-dateutil"
}

# 主函数
main() {
    # 切换到脚本所在目录
    cd "$(dirname "$0")" || exit 1

    print_banner

    echo -e "${YELLOW}🔍 检测运行环境...${NC}"

    # 检查基本环境
    if ! check_python; then
        echo -e "${RED}❌ 请先安装 Python 3.9+${NC}"
        exit 1
    fi

    # 按优先级尝试启动
    # 1. 尝试UV
    if check_uv; then
        if run_with_uv; then
            exit 0
        fi
    fi

    # 2. 尝试虚拟环境
    if check_venv; then
        if run_with_venv; then
            exit 0
        fi
    fi

    # 3. 尝试Python模块
    echo -e "${YELLOW}💻 尝试使用 Python 模块方式...${NC}"
    if run_with_python; then
        exit 0
    fi

    # 4. 尝试直接运行
    echo -e "${YELLOW}📄 最后尝试直接运行主程序文件...${NC}"
    if run_direct; then
        exit 0
    fi

    # 所有方法都失败
    show_help
    exit 1
}

# 捕获Ctrl+C
trap 'echo -e "\n${YELLOW}👋 用户中断，正在退出...${NC}"; exit 0' INT

# 运行主函数
main "$@"
