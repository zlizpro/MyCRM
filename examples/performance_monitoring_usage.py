#!/usr/bin/env python3
"""
MiniCRM 性能监控使用示例

展示如何使用数据库查询性能监控和UI响应时间监控功能
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

from minicrm.core.performance_integration import performance_integration
from minicrm.core.performance_hooks import (
    monitor_db_query,
    monitor_ui_operation,
    monitor_render_operation,
    monitor_data_refresh,
)


class ExampleDatabaseService:
    """示例数据库服务"""

    @monitor_db_query("select")
    def get_customers(self, limit: int = 10):
        """获取客户列表"""
        # 模拟数据库查询
        time.sleep(0.05)  # 模拟查询延迟
        return [{"id": i, "name": f"客户{i}"} for i in range(limit)]

    @monitor_db_query("insert")
    def create_customer(self, customer_data: dict):
        """创建客户"""
        # 模拟数据库插入
        time.sleep(0.02)
        return {"id": 123, **customer_data}


class ExampleUIComponent:
    """示例UI组件"""

    def __init__(self):
        self.data = []

    @monitor_ui_operation("load_data")
    def load_data(self):
        """加载数据"""
        # 模拟数据加载
        time.sleep(0.1)
        self.data = [f"数据项{i}" for i in range(20)]
        return self.data

    @monitor_render_operation()
    def render_view(self):
        """渲染视图"""
        # 模拟界面渲染
        time.sleep(0.03)
        return f"已渲染{len(self.data)}个数据项"

    @monitor_data_refresh("customers")
    def refresh_customers(self):
        """刷新客户数据"""
        # 模拟数据刷新
        time.sleep(0.15)
        self.data = [f"客户{i}" for i in range(10)]
        return self.data


def demonstrate_performance_monitoring():
    """演示性能监控功能"""
    print("MiniCRM 性能监控使用示例")
    print("=" * 50)

    # 1. 初始化性能监控
    print("\n1. 初始化性能监控...")
    performance_integration.initialize()

    # 2. 创建示例服务和组件
    db_service = ExampleDatabaseService()
    ui_component = ExampleUIComponent()

    # 3. 执行一些操作
    print("\n2. 执行数据库操作...")
    customers = db_service.get_customers(5)
    print(f"获取到 {len(customers)} 个客户")

    new_customer = db_service.create_customer(
        {"name": "新客户", "phone": "13800000000"}
    )
    print(f"创建客户: {new_customer['name']}")

    print("\n3. 执行UI操作...")
    data = ui_component.load_data()
    print(f"加载数据: {len(data)} 项")

    render_result = ui_component.render_view()
    print(f"渲染结果: {render_result}")

    customers = ui_component.refresh_customers()
    print(f"刷新客户: {len(customers)} 个")

    # 4. 获取性能报告
    print("\n4. 性能监控报告...")
    report = performance_integration.get_performance_report()

    # 显示数据库性能
    db_stats = report["performance_data"]["database"]
    print(f"\n数据库性能:")
    print(f"  操作数量: {db_stats['operations_count']}")
    print(f"  总耗时: {db_stats['total_duration_ms']:.2f}ms")

    if (
        "detailed_analysis" in db_stats
        and "overall_statistics" in db_stats["detailed_analysis"]
    ):
        db_detailed = db_stats["detailed_analysis"]["overall_statistics"]
        print(f"  平均查询时间: {db_detailed['avg_execution_time_ms']:.2f}ms")
        print(f"  慢查询数量: {db_detailed['slow_queries_count']}")

    # 显示UI性能
    ui_stats = report["performance_data"]["ui"]
    print(f"\nUI性能:")
    print(f"  操作数量: {ui_stats['operations_count']}")
    print(f"  总耗时: {ui_stats['total_duration_ms']:.2f}ms")

    if (
        "detailed_analysis" in ui_stats
        and "overall_statistics" in ui_stats["detailed_analysis"]
    ):
        ui_detailed = ui_stats["detailed_analysis"]["overall_statistics"]
        print(f"  平均响应时间: {ui_detailed['avg_response_time_ms']:.2f}ms")
        print(f"  慢操作数量: {ui_detailed['slow_operations_count']}")

    # 显示性能建议
    print(f"\n性能建议:")
    for recommendation in report["recommendations"]:
        print(f"  - {recommendation}")

    # 5. 清理
    print("\n5. 关闭性能监控...")
    performance_integration.shutdown()

    print("\n示例完成！")


if __name__ == "__main__":
    demonstrate_performance_monitoring()
