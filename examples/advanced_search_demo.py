#!/usr/bin/env python3
"""
MiniCRM 高级搜索功能演示

展示高级搜索和筛选功能的复杂查询能力，包括：
- 多条件组合查询
- 范围查询和模糊匹配
- 查询结果展示
- 性能测试

使用方法:
    python examples/advanced_search_demo.py
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from minicrm.services.advanced_search_service import AdvancedSearchService
from minicrm.ui.components.advanced_search_dialog import QueryCondition
from unittest.mock import Mock


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def create_mock_dao():
    """创建模拟的DAO对象"""
    mock_dao = Mock()

    # 模拟客户数据
    mock_customer_data = [
        {
            "id": 1,
            "name": "ABC制造公司",
            "phone": "13812345678",
            "email": "contact@abc.com",
            "address": "上海市浦东新区张江路123号",
            "contact_person": "张经理",
            "customer_type_id": 1,
            "created_at": "2024-01-15T10:30:00",
            "updated_at": "2025-01-15T10:30:00",
            "total_orders": 15,
            "total_amount": 250000.00,
            "last_order_date": "2025-01-10",
        },
        {
            "id": 2,
            "name": "XYZ贸易有限公司",
            "phone": "13987654321",
            "email": "info@xyz.com",
            "address": "北京市朝阳区建国路456号",
            "contact_person": "李总",
            "customer_type_id": 2,
            "created_at": "2024-03-20T14:20:00",
            "updated_at": "2025-01-12T16:45:00",
            "total_orders": 8,
            "total_amount": 120000.00,
            "last_order_date": "2025-01-05",
        },
        {
            "id": 3,
            "name": "DEF科技集团",
            "phone": "13765432109",
            "email": "service@def.com",
            "address": "深圳市南山区科技园路789号",
            "contact_person": "王主管",
            "customer_type_id": 1,
            "created_at": "2024-06-10T09:15:00",
            "updated_at": "2025-01-08T11:20:00",
            "total_orders": 22,
            "total_amount": 380000.00,
            "last_order_date": "2025-01-08",
        },
    ]

    # 模拟供应商数据
    mock_supplier_data = [
        {
            "id": 1,
            "name": "优质板材供应商",
            "phone": "13611111111",
            "email": "sales@quality.com",
            "address": "江苏省苏州市工业园区",
            "contact_person": "陈经理",
            "supplier_type_id": 1,
            "quality_rating": 4.8,
            "created_at": "2024-02-01T08:00:00",
            "updated_at": "2025-01-14T17:30:00",
        },
        {
            "id": 2,
            "name": "环保材料有限公司",
            "phone": "13622222222",
            "email": "contact@eco.com",
            "address": "广东省东莞市松山湖",
            "contact_person": "刘总",
            "supplier_type_id": 2,
            "quality_rating": 4.2,
            "created_at": "2024-04-15T10:45:00",
            "updated_at": "2025-01-10T14:15:00",
        },
    ]

    def mock_execute_complex_query(sql, params=None):
        """模拟复杂查询执行"""
        if "COUNT(*)" in sql:
            # 计数查询
            if "customers" in sql:
                return [{"count": len(mock_customer_data)}]
            else:
                return [{"count": len(mock_supplier_data)}]
        else:
            # 数据查询
            if "customers" in sql:
                return mock_customer_data
            else:
                return mock_supplier_data

    mock_dao.execute_complex_query = mock_execute_complex_query
    return mock_dao


def demo_simple_search():
    """演示简单搜索"""
    print("\n" + "=" * 60)
    print("🔍 简单搜索演示")
    print("=" * 60)

    # 创建搜索服务
    customer_dao = create_mock_dao()
    supplier_dao = create_mock_dao()
    search_service = AdvancedSearchService(customer_dao, supplier_dao)

    # 简单名称搜索
    conditions = [
        QueryCondition("name", "LIKE", "%公司%", "AND"),
    ]

    print("搜索条件: 客户名称包含'公司'")
    result = search_service.search_customers(conditions)

    print(f"搜索结果: {result.total_count} 条记录")
    print(f"查询耗时: {result.query_time:.3f} 秒")
    print(f"当前页: {result.page}/{result.total_pages}")

    for customer in result.data:
        print(f"  - {customer['name']} ({customer['phone']})")


def demo_complex_search():
    """演示复杂搜索"""
    print("\n" + "=" * 60)
    print("🔧 复杂搜索演示")
    print("=" * 60)

    # 创建搜索服务
    customer_dao = create_mock_dao()
    supplier_dao = create_mock_dao()
    search_service = AdvancedSearchService(customer_dao, supplier_dao)

    # 复杂查询条件
    conditions = [
        QueryCondition("name", "LIKE", "%公司%", "AND"),
        QueryCondition("total_orders", ">=", 10, "AND"),
        QueryCondition("total_amount", "BETWEEN", [100000, 300000], "AND"),
        QueryCondition("created_at", ">=", "2024-01-01", "AND"),
    ]

    print("复杂搜索条件:")
    print("  1. 客户名称包含'公司'")
    print("  2. 订单数量 >= 10")
    print("  3. 交易总额在 10万-30万 之间")
    print("  4. 创建时间 >= 2024-01-01")

    result = search_service.search_customers(conditions)

    print(f"\n搜索结果: {result.total_count} 条记录")
    print(f"查询耗时: {result.query_time:.3f} 秒")

    for customer in result.data:
        print(f"  - {customer['name']}")
        print(f"    电话: {customer['phone']}")
        print(f"    订单数: {customer.get('total_orders', 0)}")
        print(f"    交易额: ¥{customer.get('total_amount', 0):,.2f}")
        print()


def demo_supplier_search():
    """演示供应商搜索"""
    print("\n" + "=" * 60)
    print("🏭 供应商搜索演示")
    print("=" * 60)

    # 创建搜索服务
    customer_dao = create_mock_dao()
    supplier_dao = create_mock_dao()
    search_service = AdvancedSearchService(customer_dao, supplier_dao)

    # 供应商质量评级搜索
    conditions = [
        QueryCondition("quality_rating", ">=", 4.0, "AND"),
        QueryCondition("name", "LIKE", "%材料%", "OR"),
    ]

    print("搜索条件:")
    print("  1. 质量评级 >= 4.0")
    print("  2. 或者名称包含'材料'")

    result = search_service.search_suppliers(conditions)

    print(f"\n搜索结果: {result.total_count} 条记录")
    print(f"查询耗时: {result.query_time:.3f} 秒")

    for supplier in result.data:
        print(f"  - {supplier['name']}")
        print(f"    联系人: {supplier['contact_person']}")
        print(f"    质量评级: {supplier.get('quality_rating', 0):.1f}")
        print(f"    地址: {supplier['address']}")
        print()


def demo_pagination():
    """演示分页功能"""
    print("\n" + "=" * 60)
    print("📄 分页功能演示")
    print("=" * 60)

    # 创建搜索服务
    customer_dao = create_mock_dao()
    supplier_dao = create_mock_dao()
    search_service = AdvancedSearchService(customer_dao, supplier_dao)

    conditions = [
        QueryCondition("name", "LIKE", "%公司%", "AND"),
    ]

    # 第一页
    result_page1 = search_service.search_customers(conditions, page=1, page_size=2)
    print(f"第1页 (每页2条): {len(result_page1.data)} 条记录")
    print(f"总记录数: {result_page1.total_count}")
    print(f"总页数: {result_page1.total_pages}")

    for customer in result_page1.data:
        print(f"  - {customer['name']}")

    # 第二页
    if result_page1.total_pages > 1:
        result_page2 = search_service.search_customers(conditions, page=2, page_size=2)
        print(f"\n第2页 (每页2条): {len(result_page2.data)} 条记录")

        for customer in result_page2.data:
            print(f"  - {customer['name']}")


def demo_cache_functionality():
    """演示缓存功能"""
    print("\n" + "=" * 60)
    print("💾 缓存功能演示")
    print("=" * 60)

    # 创建搜索服务
    customer_dao = create_mock_dao()
    supplier_dao = create_mock_dao()
    search_service = AdvancedSearchService(customer_dao, supplier_dao)

    conditions = [
        QueryCondition("name", "LIKE", "%公司%", "AND"),
    ]

    # 第一次搜索（会缓存）
    print("第一次搜索（创建缓存）...")
    result1 = search_service.search_customers(conditions, use_cache=True)
    print(f"查询耗时: {result1.query_time:.3f} 秒")

    # 第二次搜索（使用缓存）
    print("\n第二次搜索（使用缓存）...")
    result2 = search_service.search_customers(conditions, use_cache=True)
    print(f"查询耗时: {result2.query_time:.3f} 秒")

    # 缓存统计
    cache_stats = search_service.get_cache_stats()
    print(f"\n缓存统计:")
    print(f"  总缓存条目: {cache_stats['total_entries']}")
    print(f"  有效条目: {cache_stats['valid_entries']}")
    print(f"  过期条目: {cache_stats['expired_entries']}")
    print(f"  缓存TTL: {cache_stats['cache_ttl_minutes']:.1f} 分钟")

    # 清除缓存
    search_service.clear_cache()
    print("\n缓存已清除")

    cache_stats_after = search_service.get_cache_stats()
    print(f"清除后缓存条目: {cache_stats_after['total_entries']}")


def demo_search_fields():
    """演示搜索字段配置"""
    print("\n" + "=" * 60)
    print("⚙️ 搜索字段配置演示")
    print("=" * 60)

    # 创建搜索服务
    customer_dao = create_mock_dao()
    supplier_dao = create_mock_dao()
    search_service = AdvancedSearchService(customer_dao, supplier_dao)

    # 客户搜索字段
    print("客户搜索字段:")
    customer_fields = search_service.get_customer_search_fields()
    for field in customer_fields[:5]:  # 只显示前5个
        print(f"  - {field['label']} ({field['key']}) - {field['type']}")
    print(f"  ... 共 {len(customer_fields)} 个字段")

    # 供应商搜索字段
    print("\n供应商搜索字段:")
    supplier_fields = search_service.get_supplier_search_fields()
    for field in supplier_fields[:5]:  # 只显示前5个
        print(f"  - {field['label']} ({field['key']}) - {field['type']}")
    print(f"  ... 共 {len(supplier_fields)} 个字段")


def demo_error_handling():
    """演示错误处理"""
    print("\n" + "=" * 60)
    print("⚠️ 错误处理演示")
    print("=" * 60)

    # 创建搜索服务
    customer_dao = create_mock_dao()
    supplier_dao = create_mock_dao()
    search_service = AdvancedSearchService(customer_dao, supplier_dao)

    # 测试空条件
    try:
        search_service.search_customers([])
    except Exception as e:
        print(f"空条件错误: {e}")

    # 测试无效字段
    try:
        invalid_conditions = [
            QueryCondition("invalid_field", "=", "value", "AND"),
        ]
        search_service.search_customers(invalid_conditions)
    except Exception as e:
        print(f"无效字段错误: {e}")

    # 测试无效操作符
    try:
        invalid_conditions = [
            QueryCondition("name", "INVALID_OP", "value", "AND"),
        ]
        search_service.search_customers(invalid_conditions)
    except Exception as e:
        print(f"无效操作符错误: {e}")


def main():
    """主函数"""
    setup_logging()

    print("🚀 MiniCRM 高级搜索功能演示")
    print("=" * 60)
    print("本演示展示了高级搜索和筛选功能的各种能力")

    try:
        # 运行各种演示
        demo_simple_search()
        demo_complex_search()
        demo_supplier_search()
        demo_pagination()
        demo_cache_functionality()
        demo_search_fields()
        demo_error_handling()

        print("\n" + "=" * 60)
        print("✅ 演示完成！")
        print("=" * 60)
        print("高级搜索功能包括:")
        print("  ✓ 多条件组合查询")
        print("  ✓ 范围查询和模糊匹配")
        print("  ✓ 分页和排序")
        print("  ✓ 查询缓存优化")
        print("  ✓ 灵活的字段配置")
        print("  ✓ 完善的错误处理")
        print("\n可以通过高级搜索对话框或API直接使用这些功能。")

    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
