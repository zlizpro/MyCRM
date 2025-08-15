#!/bin/bash
# 测试配置文件是否正确

set -e

echo "🔧 测试代码质量配置..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 创建测试文件
cat > test_sample.py << 'EOF'
def hello_world():
    print("Hello, World!")
    return "success"

class TestClass:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name
EOF

echo "📝 创建测试文件: test_sample.py"

# 测试标准配置
echo ""
echo "🧪 测试标准配置..."

if uv run ruff check test_sample.py 2>/dev/null; then
    print_success "标准Ruff配置正常"
else
    print_warning "标准Ruff配置有警告（正常）"
fi

if uv run mypy test_sample.py 2>/dev/null; then
    print_success "标准MyPy配置正常"
else
    print_warning "标准MyPy配置有警告（正常）"
fi

# 测试宽松配置
echo ""
echo "🧪 测试宽松配置..."

if uv run ruff check test_sample.py --config ruff.toml 2>/dev/null; then
    print_success "宽松Ruff配置正常"
else
    print_error "宽松Ruff配置失败"
fi

if uv run mypy test_sample.py --config-file mypy.ini 2>/dev/null; then
    print_success "宽松MyPy配置正常"
else
    print_warning "宽松MyPy配置有警告（可接受）"
fi

# 测试格式化
echo ""
echo "🎨 测试代码格式化..."

if uv run ruff format test_sample.py 2>/dev/null; then
    print_success "代码格式化正常"
else
    print_error "代码格式化失败"
fi

# 清理测试文件
rm -f test_sample.py

echo ""
echo "✅ 配置测试完成！"
echo ""
echo "💡 使用建议:"
echo "  开发阶段: RELAXED_MODE=true ./scripts/check-code.sh"
echo "  提交前:   ./scripts/check-code.sh"
echo "  快速检查: make check-relaxed"
echo "  标准检查: make check"
