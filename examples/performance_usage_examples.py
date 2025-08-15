"""
MiniCRM 性能优化使用示例
演示如何在实际代码中使用性能优化工具
"""

import random
import time
from typing import Any

from src.minicrm.config.performance_config import current_config

# 导入性能优化模块
from src.minicrm.core.performance import (
    PerformanceTracker,
    SmartCache,
    memory_context,
    performance_monitor,
)


# 示例1: 使用性能监控装饰器
@performance_monitor("customer_data_processing")
def process_customer_data(customers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """处理客户数据的示例函数"""
    processed = []

    for customer in customers:
        # 模拟数据处理
        processed_customer = {
            "id": customer["id"],
            "name": customer["name"].upper(),
            "email": customer["email"].lower(),
            "score": calculate_customer_score(customer),
        }
        processed.append(processed_customer)

        # 模拟一些处理时间
        time.sleep(0.001)

    return processed


def calculate_customer_score(customer: dict[str, Any]) -> float:
    """计算客户评分"""
    # 模拟复杂计算
    base_score = random.uniform(0.5, 1.0)

    # 根据客户数据调整评分
    if customer.get("email"):
        base_score += 0.1
    if customer.get("phone"):
        base_score += 0.1
    if customer.get("company"):
        base_score += 0.2

    return min(base_score, 1.0)


# 示例2: 使用智能缓存
class CustomerService:
    """客户服务类 - 演示缓存使用"""

    def __init__(self):
        self.cache = SmartCache(max_size=100, ttl_seconds=300)
        self.db_call_count = 0  # 模拟数据库调用计数

    def get_customer(self, customer_id: int) -> dict[str, Any]:
        """获取客户信息 - 带缓存"""
        cache_key = f"customer_{customer_id}"

        # 尝试从缓存获取
        cached_customer = self.cache.get(cache_key)
        if cached_customer is not None:
            print(f"✅ 缓存命中: customer_{customer_id}")
            return cached_customer

        # 缓存未命中，从"数据库"获取
        print(f"🔍 缓存未命中，查询数据库: customer_{customer_id}")
        customer = self._fetch_from_database(customer_id)

        # 存入缓存
        self.cache.set(cache_key, customer)

        return customer

    def _fetch_from_database(self, customer_id: int) -> dict[str, Any]:
        """模拟数据库查询"""
        self.db_call_count += 1

        # 模拟数据库查询延迟
        time.sleep(0.1)

        return {
            "id": customer_id,
            "name": f"Customer {customer_id}",
            "email": f"customer{customer_id}@example.com",
            "phone": f"138{customer_id:08d}",
            "company": f"Company {customer_id}",
        }

    def get_cache_stats(self) -> dict[str, Any]:
        """获取缓存统计"""
        return self.cache.get_stats()


# 示例3: 使用内存上下文管理器
def process_large_dataset():
    """处理大数据集的示例"""

    with memory_context("大数据集处理") as memory_manager:
        # 生成大量数据
        print("生成测试数据...")
        large_dataset = []

        for i in range(50000):
            large_dataset.append(
                {
                    "id": i,
                    "name": f"Item {i}",
                    "value": random.uniform(0, 1000),
                    "category": random.choice(["A", "B", "C", "D"]),
                    "timestamp": time.time(),
                }
            )

        # 检查内存使用
        memory_status = memory_manager.check_memory_status()
        print(
            f"数据生成后内存状态: {memory_status['status']} ({memory_status['current_mb']:.1f}MB)"
        )

        # 处理数据
        print("处理数据...")
        processed_data = []

        for item in large_dataset:
            if item["value"] > 500:  # 只处理值大于500的项
                processed_item = {
                    "id": item["id"],
                    "name": item["name"],
                    "high_value": True,
                    "processed_at": time.time(),
                }
                processed_data.append(processed_item)

        print(f"处理完成，筛选出 {len(processed_data)} 个高价值项目")

        # 如果内存使用过高，强制垃圾回收
        if memory_status["status"] in ["warning", "critical"]:
            print("执行垃圾回收...")
            gc_result = memory_manager.force_garbage_collection()
            print(f"垃圾回收完成，释放了 {gc_result['memory_freed_mb']:.1f}MB 内存")


# 示例4: 批量数据库操作优化
class OptimizedDataAccess:
    """优化的数据访问类"""

    def __init__(self):
        self.batch_size = current_config.DB_BATCH_SIZE
        self.operation_count = 0

    def batch_insert_customers(self, customers: list[dict[str, Any]]) -> None:
        """批量插入客户数据"""

        with memory_context("批量插入客户") as memory_manager:
            print(f"开始批量插入 {len(customers)} 个客户，批量大小: {self.batch_size}")

            # 分批处理
            for i in range(0, len(customers), self.batch_size):
                batch = customers[i : i + self.batch_size]
                self._insert_batch(batch)

                # 每处理1000条记录检查一次内存
                if (i + self.batch_size) % 1000 == 0:
                    memory_status = memory_manager.check_memory_status()
                    if memory_status["status"] == "warning":
                        print(f"⚠️ 内存使用警告: {memory_status['current_mb']:.1f}MB")

                print(
                    f"已处理 {min(i + self.batch_size, len(customers))}/{len(customers)} 条记录"
                )

    @performance_monitor("database_batch_insert")
    def _insert_batch(self, batch: list[dict[str, Any]]) -> None:
        """插入一批数据"""
        # 模拟数据库批量插入
        self.operation_count += 1
        time.sleep(0.01 * len(batch))  # 模拟数据库操作时间

        print(f"  批次 {self.operation_count}: 插入 {len(batch)} 条记录")


# 示例5: 性能分析和报告
def performance_analysis_example():
    """性能分析示例"""

    print("=== 性能分析示例 ===\n")

    # 创建服务实例
    customer_service = CustomerService()
    data_access = OptimizedDataAccess()

    # 1. 测试缓存性能
    print("1. 测试缓存性能")
    print("-" * 30)

    # 第一次访问（缓存未命中）
    start_time = time.time()
    customer1 = customer_service.get_customer(1)
    first_access_time = time.time() - start_time

    # 第二次访问（缓存命中）
    start_time = time.time()
    customer1_cached = customer_service.get_customer(1)
    second_access_time = time.time() - start_time

    print(f"首次访问时间: {first_access_time:.4f}秒")
    print(f"缓存访问时间: {second_access_time:.4f}秒")
    print(f"性能提升: {first_access_time / second_access_time:.1f}倍")

    # 显示缓存统计
    cache_stats = customer_service.get_cache_stats()
    print(f"缓存统计: {cache_stats}")

    print()

    # 2. 测试大数据处理
    print("2. 测试大数据处理")
    print("-" * 30)
    process_large_dataset()

    print()

    # 3. 测试批量操作
    print("3. 测试批量操作")
    print("-" * 30)

    # 生成测试数据
    test_customers = []
    for i in range(500):
        test_customers.append(
            {
                "id": i,
                "name": f"Test Customer {i}",
                "email": f"test{i}@example.com",
            }
        )

    data_access.batch_insert_customers(test_customers)

    print()

    # 4. 显示性能跟踪结果
    print("4. 性能跟踪结果")
    print("-" * 30)

    tracker = PerformanceTracker.instance()
    performance_summary = tracker.get_performance_summary()

    for func_name, stats in performance_summary.items():
        print(f"{func_name}:")
        print(f"  平均执行时间: {stats['avg_time']:.4f}秒")
        print(f"  最大执行时间: {stats['max_time']:.4f}秒")
        print(f"  调用次数: {stats['call_count']}")
        print(f"  平均内存变化: {stats['avg_memory_delta']:+.2f}MB")
        print()

    # 显示最慢的函数
    slowest_functions = tracker.get_slowest_functions(top_n=3)
    print("最慢的函数:")
    for i, (func_name, stats) in enumerate(slowest_functions, 1):
        print(f"  {i}. {func_name}: {stats['avg_time']:.4f}秒")


if __name__ == "__main__":
    # 运行性能分析示例
    performance_analysis_example()

    print("\n=== 性能优化建议 ===")
    print("1. 使用 @performance_monitor 装饰器监控关键函数")
    print("2. 使用 SmartCache 缓存频繁访问的数据")
    print("3. 使用 memory_context 监控内存使用")
    print("4. 使用批量操作处理大量数据")
    print("5. 定期检查 PerformanceTracker 的统计信息")
    print("6. 根据配置调整性能参数")

    print(f"\n当前配置环境: {current_config.__name__}")
    print("可通过环境变量 MINICRM_ENV 切换配置 (development/production)")
