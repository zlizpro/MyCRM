#!/usr/bin/env python3
"""
MiniCRM UI性能优化演示

展示如何使用UI性能优化器和内存管理器来优化UI性能
"""

import logging
import time
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# 添加项目路径
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from minicrm.core.ui_performance_optimizer import ui_performance_optimizer
from minicrm.core.ui_memory_manager import ui_memory_manager


class MockUIComponent:
    """模拟UI组件"""

    def __init__(self, name: str, size: int = 100):
        self.name = name
        self.size = size
        self.data = [f"数据项{i}" for i in range(size)]
        self.children_components = []

    def render(self):
        """模拟渲染操作"""
        # 模拟渲染延迟
        time.sleep(0.01 + self.size * 0.0001)
        return f"已渲染{self.name}组件，包含{len(self.data)}个数据项"

    def add_child(self, child):
        """添加子组件"""
        self.children_components.append(child)

    def cleanup(self):
        """清理资源"""
        self.data.clear()
        self.children_components.clear()


def demonstrate_ui_performance_optimization():
    """演示UI性能优化功能"""
    print("MiniCRM UI性能优化演示")
    print("=" * 50)

    # 1. 启用优化器和内存管理器
    print("\n1. 启用UI性能优化器和内存管理器...")
    ui_performance_optimizer.enable()
    ui_memory_manager.enable()

    # 2. 创建和注册UI组件
    print("\n2. 创建和注册UI组件...")
    components = []

    for i in range(10):
        # 创建不同大小的组件
        size = 50 + i * 20
        component = MockUIComponent(f"组件{i}", size)
        components.append(component)

        # 注册到内存管理器
        component_id = ui_memory_manager.register_component(
            component, f"MockUIComponent", cleanup_callback=component.cleanup
        )

        print(f"  注册组件: {component.name} (ID: {component_id})")

    # 3. 模拟组件渲染和性能监控
    print("\n3. 模拟组件渲染和性能监控...")

    for component in components:
        # 记录渲染开始时间
        start_time = time.perf_counter()

        # 执行渲染
        result = component.render()

        # 计算渲染时间
        render_time = (time.perf_counter() - start_time) * 1000  # 转换为毫秒

        # 记录渲染性能
        ui_performance_optimizer.track_render_time(component.name, render_time)

        # 记录组件访问
        ui_memory_manager.access_component(component)

        print(f"  {result} (渲染时间: {render_time:.2f}ms)")

    # 4. 模拟一些慢渲染组件
    print("\n4. 模拟慢渲染组件...")

    slow_component = MockUIComponent("慢组件", 1000)
    ui_memory_manager.register_component(slow_component, "SlowComponent")

    # 模拟慢渲染
    start_time = time.perf_counter()
    time.sleep(0.15)  # 模拟150ms的慢渲染
    render_time = (time.perf_counter() - start_time) * 1000

    ui_performance_optimizer.track_render_time("慢组件", render_time)
    print(f"  慢组件渲染完成 (渲染时间: {render_time:.2f}ms)")

    # 5. 演示组件缓存
    print("\n5. 演示组件缓存...")

    # 缓存一些组件
    for i, component in enumerate(components[:3]):
        cache_key = f"cached_component_{i}"
        success = ui_memory_manager.cache_component(cache_key, component)
        print(f"  缓存组件 {component.name}: {'成功' if success else '失败'}")

    # 从缓存获取组件
    cached_component = ui_memory_manager.get_cached_component("cached_component_0")
    if cached_component:
        print(f"  从缓存获取组件: {cached_component.name}")

    # 6. 获取性能统计
    print("\n6. 性能统计信息...")

    perf_stats = ui_performance_optimizer.get_performance_statistics()
    print(
        f"  当前内存使用: {perf_stats['memory_statistics'].get('current_memory_mb', 0):.1f}MB"
    )
    print(
        f"  跟踪的组件数量: {perf_stats['cache_statistics']['tracked_widgets_count']}"
    )

    # 显示渲染统计
    render_stats = perf_stats.get("rendering_statistics", {})
    if render_stats:
        print("  渲染统计:")
        for widget_name, stats in render_stats.items():
            print(
                f"    {widget_name}: 平均 {stats['avg_render_time_ms']:.2f}ms, "
                f"最大 {stats['max_render_time_ms']:.2f}ms"
            )

    # 7. 内存管理统计
    print("\n7. 内存管理统计...")

    memory_stats = ui_memory_manager.get_memory_statistics()
    print(f"  跟踪的组件总数: {memory_stats['total_tracked_components']}")
    print(f"  估算内存使用: {memory_stats['total_memory_estimate_kb']:.1f}KB")

    component_stats = memory_stats.get("component_statistics", {})
    if component_stats:
        print("  组件类型统计:")
        for comp_type, stats in component_stats.items():
            print(f"    {comp_type}: {stats['count']} 个, {stats['memory_kb']:.1f}KB")

    # 8. 生成优化建议
    print("\n8. 优化建议...")

    suggestions = ui_performance_optimizer.generate_optimization_suggestions()
    for suggestion in suggestions:
        print(
            f"  [{suggestion.priority.upper()}] {suggestion.category}: {suggestion.description}"
        )
        print(f"    建议操作: {suggestion.action}")
        print(f"    预期收益: {suggestion.estimated_benefit}")
        print()

    # 9. 执行内存优化
    print("\n9. 执行内存优化...")

    optimization_result = ui_performance_optimizer.optimize_memory_usage()
    print(f"  优化前内存: {optimization_result['memory_before_mb']:.1f}MB")
    print(f"  优化后内存: {optimization_result['memory_after_mb']:.1f}MB")
    print(f"  节省内存: {optimization_result['memory_saved_mb']:.1f}MB")
    print(f"  执行的操作: {', '.join(optimization_result['actions_taken'])}")

    # 10. 清理空闲组件
    print("\n10. 清理空闲组件...")

    # 模拟一些组件变为空闲状态（通过不访问它们）
    time.sleep(0.1)  # 等待一小段时间

    cleanup_result = ui_memory_manager.cleanup_idle_components()
    print(f"  清理的组件数量: {cleanup_result['cleaned_components']}")
    print(f"  清理的缓存项: {cleanup_result['cleaned_cache_items']}")
    print(f"  释放的内存: {cleanup_result['memory_freed_kb']:.1f}KB")

    # 11. 内存泄漏检测
    print("\n11. 内存泄漏检测...")

    # 模拟创建大量组件（可能导致泄漏）
    for i in range(20):
        leak_component = MockUIComponent(f"泄漏组件{i}", 10)
        ui_memory_manager.register_component(leak_component, "LeakComponent")

    # 检测泄漏
    leaks = ui_memory_manager.detect_memory_leaks()
    if leaks:
        print("  检测到可能的内存泄漏:")
        for leak in leaks:
            print(
                f"    {leak.component_type}: {leak.leak_count} 个组件, "
                f"估算泄漏大小: {leak.estimated_leak_size_kb:.1f}KB"
            )
    else:
        print("  未检测到内存泄漏")

    # 12. 强制垃圾回收
    print("\n12. 强制垃圾回收...")

    gc_result = ui_memory_manager.force_garbage_collection()
    print(f"  回收的对象数量: {gc_result['collected_objects']}")
    print(f"  清理的组件数量: {gc_result['components_cleaned']}")
    print(f"  清理的缓存项: {gc_result['cache_items_cleaned']}")

    # 13. 最终统计
    print("\n13. 最终性能统计...")

    final_stats = ui_performance_optimizer.get_performance_statistics()
    final_memory = ui_memory_manager.get_memory_statistics()

    print(
        f"  最终内存使用: {final_stats['memory_statistics'].get('current_memory_mb', 0):.1f}MB"
    )
    print(f"  最终组件数量: {final_memory['total_tracked_components']}")
    print(
        f"  缓存命中率: {final_memory['cache_statistics'].get('cache_hit_rate', 0):.1f}%"
    )

    # 14. 清理和关闭
    print("\n14. 清理和关闭...")

    ui_performance_optimizer.clear_all_caches()
    ui_memory_manager.clear_all_caches()

    ui_performance_optimizer.disable()
    ui_memory_manager.disable()

    print("\n演示完成！")


def demonstrate_rendering_optimization():
    """演示渲染优化功能"""
    print("\n" + "=" * 50)
    print("渲染优化演示")
    print("=" * 50)

    # 创建模拟组件
    component = MockUIComponent("测试组件", 200)

    # 模拟优化前的渲染
    print("\n优化前渲染测试:")
    render_times = []
    for i in range(5):
        start_time = time.perf_counter()
        component.render()
        render_time = (time.perf_counter() - start_time) * 1000
        render_times.append(render_time)
        print(f"  第{i + 1}次渲染: {render_time:.2f}ms")

    avg_before = sum(render_times) / len(render_times)
    print(f"  平均渲染时间: {avg_before:.2f}ms")

    # 应用优化
    print("\n应用渲染优化...")
    optimization_result = ui_performance_optimizer.optimize_widget_rendering(component)
    print(
        f"  应用的优化: {', '.join(optimization_result.get('optimizations_applied', []))}"
    )
    print(f"  预期性能提升: {optimization_result.get('estimated_improvement', 0):.1f}%")

    # 模拟优化后的渲染（实际上这里只是演示，真实的优化需要Qt环境）
    print("\n优化后渲染测试:")
    optimized_render_times = []
    for i in range(5):
        start_time = time.perf_counter()
        component.render()
        # 模拟优化效果（减少10%的时间）
        render_time = (time.perf_counter() - start_time) * 1000 * 0.9
        optimized_render_times.append(render_time)
        print(f"  第{i + 1}次渲染: {render_time:.2f}ms")

    avg_after = sum(optimized_render_times) / len(optimized_render_times)
    improvement = ((avg_before - avg_after) / avg_before) * 100

    print(f"  平均渲染时间: {avg_after:.2f}ms")
    print(f"  性能提升: {improvement:.1f}%")


def main():
    """主演示函数"""
    try:
        # 主要演示
        demonstrate_ui_performance_optimization()

        # 渲染优化演示
        demonstrate_rendering_optimization()

        print("\n" + "=" * 50)
        print("所有演示完成！")

    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
