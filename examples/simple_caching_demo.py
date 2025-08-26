#!/usr/bin/env python3
"""
MiniCRM 简化的数据缓存和懒加载演示

展示基本的缓存和懒加载功能，避免循环依赖
"""

import logging
import random
import time
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# 添加项目路径
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from minicrm.core.data_cache_manager import data_cache_manager
from minicrm.core.lazy_loading_manager import lazy_loading_manager, LazyLoadConfig


# 模拟数据源
class SimpleDataSource:
    """简单数据源"""

    def __init__(self):
        self.customers = [
            {"id": i, "name": f"客户{i}", "phone": f"138{i:08d}"}
            for i in range(1, 101)  # 100个客户
        ]
        self.access_count = 0

    def get_customer_by_id(self, customer_id: int) -> dict:
        """根据ID获取客户"""
        self.access_count += 1
        print(f"    [数据源] 访问客户 {customer_id} (总访问次数: {self.access_count})")

        # 模拟查询延迟
        time.sleep(0.1)

        for customer in self.customers:
            if customer["id"] == customer_id:
                return customer

        return None

    def get_customers_page(self, page: int = 0, page_size: int = 10, **kwargs) -> dict:
        """分页获取客户"""
        self.access_count += 1
        print(f"    [数据源] 访问客户页面 {page} (总访问次数: {self.access_count})")

        # 模拟查询延迟
        time.sleep(0.05)

        start_idx = page * page_size
        end_idx = min(start_idx + page_size, len(self.customers))

        return {
            "data": self.customers[start_idx:end_idx],
            "total": len(self.customers),
            "page": page,
            "page_size": page_size,
            "has_more": end_idx < len(self.customers),
        }


def demonstrate_basic_caching():
    """演示基本缓存功能"""
    print("基本缓存功能演示")
    print("-" * 30)

    # 创建数据源
    data_source = SimpleDataSource()

    # 1. 基本缓存操作
    print("\n1. 基本缓存操作...")

    # 存储数据
    test_data = {"message": "Hello Cache", "value": 42}
    success = data_cache_manager.put("test_key", test_data)
    print(f"  存储数据: {'成功' if success else '失败'}")

    # 获取数据
    cached_data = data_cache_manager.get("test_key")
    print(f"  获取数据: {cached_data}")

    # 2. 缓存性能测试
    print("\n2. 缓存性能测试...")

    # 第一次获取（无缓存）
    start_time = time.time()
    customer1 = data_source.get_customer_by_id(1)
    first_time = (time.time() - start_time) * 1000

    # 缓存数据
    data_cache_manager.put("customer_1", customer1)

    # 第二次获取（有缓存）
    start_time = time.time()
    cached_customer = data_cache_manager.get("customer_1")
    second_time = (time.time() - start_time) * 1000

    print(f"  第一次获取时间: {first_time:.2f}ms")
    print(f"  第二次获取时间: {second_time:.2f}ms")
    print(f"  性能提升: {((first_time - second_time) / first_time * 100):.1f}%")

    # 3. 缓存统计
    print("\n3. 缓存统计...")

    # 执行一些缓存操作
    for i in range(2, 6):
        customer = data_source.get_customer_by_id(i)
        data_cache_manager.put(f"customer_{i}", customer)

    # 访问缓存数据
    for i in range(1, 4):
        data_cache_manager.get(f"customer_{i}")

    # 访问不存在的数据
    for i in range(10, 13):
        data_cache_manager.get(f"customer_{i}")

    stats = data_cache_manager.get_statistics()
    print(f"  缓存条目数: {stats.total_entries}")
    print(f"  命中率: {stats.hit_rate:.1f}%")
    print(f"  内存使用: {stats.memory_usage_mb:.2f}MB")


def demonstrate_lazy_loading():
    """演示懒加载功能"""
    print("\n" + "=" * 50)
    print("懒加载功能演示")
    print("-" * 30)

    # 创建数据源
    data_source = SimpleDataSource()

    # 配置懒加载
    config = LazyLoadConfig(
        batch_size=10,
        max_concurrent_loads=2,
        preload_enabled=False,  # 暂时禁用预加载避免复杂性
    )

    # 重新配置懒加载管理器
    lazy_loading_manager.disable()
    lazy_loading_manager._config = config
    lazy_loading_manager.enable()

    # 1. 注册加载器
    print("\n1. 注册数据加载器...")

    lazy_loading_manager.register_loader(
        "customer_by_id", data_source.get_customer_by_id, cache_ttl_minutes=5
    )

    lazy_loading_manager.register_loader(
        "customers_page",
        data_source.get_customers_page,
        batch_size=10,
        cache_ttl_minutes=10,
    )

    print("  注册了2个数据加载器")

    # 2. 基本懒加载
    print("\n2. 基本懒加载...")

    print("  加载单个客户...")
    start_time = time.time()

    future = lazy_loading_manager.load_data(
        "customer_by_id", customer_id=5, cache_key="customer_5"
    )

    result = future.result(timeout=10)
    load_time = (time.time() - start_time) * 1000

    print(f"    结果: {result['name']}")
    print(f"    加载时间: {load_time:.2f}ms")

    # 3. 分页懒加载
    print("\n3. 分页懒加载...")

    print("  加载客户页面...")
    start_time = time.time()

    future = lazy_loading_manager.load_page("customers_page", page=0, page_size=5)

    result = future.result(timeout=10)
    load_time = (time.time() - start_time) * 1000

    print(f"    页面数据: {len(result['data'])} 个客户")
    print(f"    总数: {result['total']}")
    print(f"    加载时间: {load_time:.2f}ms")

    # 4. 缓存效果测试
    print("\n4. 缓存效果测试...")

    # 第一次加载
    print("  第一次加载页面1...")
    start_time = time.time()
    future = lazy_loading_manager.load_page("customers_page", page=1, page_size=5)
    result1 = future.result(timeout=10)
    first_time = (time.time() - start_time) * 1000

    # 第二次加载（应该从缓存获取）
    print("  第二次加载页面1...")
    start_time = time.time()
    future = lazy_loading_manager.load_page("customers_page", page=1, page_size=5)
    result2 = future.result(timeout=10)
    second_time = (time.time() - start_time) * 1000

    print(f"    第一次加载时间: {first_time:.2f}ms")
    print(f"    第二次加载时间: {second_time:.2f}ms")
    print(f"    性能提升: {((first_time - second_time) / first_time * 100):.1f}%")

    # 5. 并发加载测试
    print("\n5. 并发加载测试...")

    print("  启动并发加载...")
    start_time = time.time()

    futures = []
    for i in range(10, 15):
        future = lazy_loading_manager.load_data(
            "customer_by_id", customer_id=i, cache_key=f"customer_{i}"
        )
        futures.append(future)

    # 等待所有加载完成
    results = []
    for future in futures:
        try:
            result = future.result(timeout=10)
            results.append(result)
        except Exception as e:
            print(f"    加载失败: {e}")

    concurrent_time = (time.time() - start_time) * 1000
    print(f"    并发加载完成: {len(results)} 个客户")
    print(f"    总时间: {concurrent_time:.2f}ms")

    # 6. 统计信息
    print("\n6. 加载统计...")

    stats = lazy_loading_manager.get_statistics()
    print(f"  总任务数: {stats.total_tasks}")
    print(f"  完成任务数: {stats.completed_tasks}")
    print(f"  缓存命中数: {stats.cached_hits}")
    print(f"  平均加载时间: {stats.avg_load_time_ms:.2f}ms")

    print(f"\n  数据源总访问次数: {data_source.access_count}")


def main():
    """主演示函数"""
    print("MiniCRM 数据缓存和懒加载简化演示")
    print("=" * 50)

    try:
        # 启用管理器
        data_cache_manager.enable()
        lazy_loading_manager.enable()

        # 基本缓存演示
        demonstrate_basic_caching()

        # 懒加载演示
        demonstrate_lazy_loading()

        print("\n" + "=" * 50)
        print("演示完成！")

    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # 清理
        data_cache_manager.clear()
        lazy_loading_manager.clear_cache()

        # 禁用管理器
        data_cache_manager.disable()
        lazy_loading_manager.disable()


if __name__ == "__main__":
    main()
