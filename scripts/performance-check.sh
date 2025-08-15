#!/bin/bash
# MiniCRM 性能检查脚本

set -e

echo "🚀 MiniCRM 性能检查工具"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "未在虚拟环境中，尝试激活..."
    if [ -f .venv/bin/activate ]; then
        source .venv/bin/activate
        print_success "虚拟环境已激活"
    else
        print_error "虚拟环境不存在，请运行 ./scripts/setup-dev.sh"
        exit 1
    fi
fi

echo ""
echo "🔍 开始性能检查..."
echo ""

# 1. 检查系统资源
print_status "检查系统资源..."

# 获取系统信息
TOTAL_RAM=$(python3 -c "import psutil; print(f'{psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f}')")
AVAILABLE_RAM=$(python3 -c "import psutil; print(f'{psutil.virtual_memory().available / 1024 / 1024 / 1024:.1f}')")
CPU_COUNT=$(python3 -c "import psutil; print(psutil.cpu_count())")
CPU_PERCENT=$(python3 -c "import psutil; print(f'{psutil.cpu_percent(interval=1):.1f}')")

echo "  总内存: ${TOTAL_RAM}GB"
echo "  可用内存: ${AVAILABLE_RAM}GB"
echo "  CPU核心数: ${CPU_COUNT}"
echo "  CPU使用率: ${CPU_PERCENT}%"

# 2. 检查Python性能
print_status "检查Python环境性能..."

# 创建性能测试脚本
cat > temp_perf_test.py << 'EOF'
import time
import sys
import psutil
import gc

def test_import_performance():
    """测试导入性能"""
    start = time.time()
    try:
        import PySide6.QtWidgets
        import matplotlib.pyplot
        import sqlite3
        import pandas
    except ImportError as e:
        print(f"导入失败: {e}")
        return None

    return time.time() - start

def test_memory_allocation():
    """测试内存分配性能"""
    process = psutil.Process()
    start_memory = process.memory_info().rss

    # 分配大量对象
    data = []
    for i in range(100000):
        data.append({'id': i, 'name': f'item_{i}', 'value': i * 1.5})

    end_memory = process.memory_info().rss
    memory_used = (end_memory - start_memory) / 1024 / 1024  # MB

    # 清理
    del data
    gc.collect()

    return memory_used

def test_database_performance():
    """测试数据库性能"""
    import sqlite3
    import tempfile
    import os

    # 创建临时数据库
    with tempfile.NamedTemporaryFile(delete=False) as f:
        db_path = f.name

    try:
        start = time.time()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 创建表
        cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value REAL
            )
        ''')

        # 批量插入数据
        data = [(i, f'name_{i}', i * 1.5) for i in range(10000)]
        cursor.executemany('INSERT INTO test_table VALUES (?, ?, ?)', data)

        # 查询测试
        cursor.execute('SELECT COUNT(*) FROM test_table WHERE value > 5000')
        result = cursor.fetchone()

        conn.commit()
        conn.close()

        return time.time() - start

    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)

if __name__ == '__main__':
    print("=== Python性能测试 ===")

    # 导入性能测试
    import_time = test_import_performance()
    if import_time is not None:
        print(f"导入性能: {import_time:.3f}秒")
        if import_time > 2.0:
            print("⚠️ 导入时间较长，可能影响启动速度")
        else:
            print("✅ 导入性能良好")

    # 内存分配测试
    memory_used = test_memory_allocation()
    print(f"内存分配测试: {memory_used:.1f}MB")
    if memory_used > 50:
        print("⚠️ 内存使用较高")
    else:
        print("✅ 内存使用正常")

    # 数据库性能测试
    db_time = test_database_performance()
    print(f"数据库性能: {db_time:.3f}秒")
    if db_time > 1.0:
        print("⚠️ 数据库操作较慢")
    else:
        print("✅ 数据库性能良好")
EOF

# 运行性能测试
uv run python temp_perf_test.py

# 清理临时文件
rm -f temp_perf_test.py

echo ""

# 3. 检查依赖包性能
print_status "检查关键依赖包..."

# 检查包大小
echo "关键依赖包大小:"
uv run python -c "
import sys
import importlib.util

packages = ['PySide6', 'matplotlib', 'pandas', 'sqlite3']
for pkg in packages:
    try:
        if pkg == 'sqlite3':
            import sqlite3
            print(f'  {pkg}: 内置模块')
        else:
            spec = importlib.util.find_spec(pkg)
            if spec and spec.origin:
                import os
                size = os.path.getsize(spec.origin) / 1024 / 1024
                print(f'  {pkg}: {size:.1f}MB')
            else:
                print(f'  {pkg}: 未找到')
    except Exception as e:
        print(f'  {pkg}: 检查失败 - {e}')
"

echo ""

# 4. 生成性能报告
print_status "生成性能报告..."

cat > performance_report.md << EOF
# MiniCRM 性能检查报告

生成时间: $(date)

## 系统环境
- 总内存: ${TOTAL_RAM}GB
- 可用内存: ${AVAILABLE_RAM}GB
- CPU核心数: ${CPU_COUNT}
- CPU使用率: ${CPU_PERCENT}%

## 性能建议

### 内存优化建议
- 如果可用内存 < 2GB，建议增加内存或优化内存使用
- 使用分页加载处理大数据集
- 实施智能缓存策略

### CPU优化建议
- 如果CPU使用率 > 80%，考虑异步处理
- 使用多线程处理耗时操作
- 优化算法复杂度

### 数据库优化建议
- 使用连接池管理数据库连接
- 创建适当的索引
- 使用批量操作处理大量数据

### UI优化建议
- 使用虚拟化表格显示大数据集
- 实施延迟加载策略
- 优化图表渲染性能

## 下一步行动
1. 实施高优先级优化措施
2. 建立性能监控体系
3. 定期进行性能测试
4. 根据实际使用情况调整优化策略

EOF

print_success "性能报告已生成: performance_report.md"

echo ""
echo "🎯 性能检查完成！"
echo ""
echo "📊 查看详细报告: cat performance_report.md"
echo "📚 查看优化指南: docs/PERFORMANCE_OPTIMIZATION.md"
echo "🔧 开始优化: 按照文档中的优先级实施优化措施"
