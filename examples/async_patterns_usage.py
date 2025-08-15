"""
MiniCRM 异步模式使用示例

展示如何在MiniCRM项目中使用统一的同步/异步操作接口。
这些示例受pomponchik/transfunctions库启发，但适配了我们的具体需求。
"""

import asyncio
import sqlite3
from typing import Dict, List, Any

# 假设的导入（在实际项目中这些会是真实的导入）
from src.transfunctions.async_patterns import (
    create_unified_database,
    create_unified_api_client,
    create_unified_file_ops,
    unified_operation,
)
from src.transfunctions.validation import validate_customer_data
from src.transfunctions.formatting import format_currency, format_phone


class CustomerService:
    """客户服务 - 使用统一异步模式的示例"""

    def __init__(self, db_connection):
        self.db = create_unified_database(db_connection)
        self.api = create_unified_api_client("https://api.minicrm.com")
        self.file_ops = create_unified_file_ops()

    @unified_operation
    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建客户 - 统一同步/异步接口

        这个函数可以在同步或异步上下文中调用，
        会自动选择合适的执行方式。
        """
        # 1. 数据验证（使用MiniCRM transfunctions）
        errors = validate_customer_data(customer_data)
        if errors:
            raise ValueError(f"客户数据验证失败: {errors}")

        # 2. 格式化数据
        formatted_data = {
            "name": customer_data["name"],
            "phone": format_phone(customer_data["phone"]),
            "email": customer_data.get("email", ""),
            "customer_type": customer_data.get("customer_type", "其他"),
        }

        # 3. 保存到数据库（自动选择同步/异步）
        sql = """
        INSERT INTO customers (name, phone, email, customer_type, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        """
        customer_id = self.db.execute(
            sql,
            (
                formatted_data["name"],
                formatted_data["phone"],
                formatted_data["email"],
                formatted_data["customer_type"],
            ),
        )

        # 4. 记录日志（自动选择同步/异步文件操作）
        log_entry = f"客户创建: ID={customer_id}, 姓名={formatted_data['name']}\n"
        self.file_ops.write_file("logs/customer_operations.log", log_entry)

        # 5. 返回结果
        return {
            "id": customer_id,
            "name": formatted_data["name"],
            "phone": formatted_data["phone"],
            "status": "created",
        }

    @unified_operation
    def get_customer_statistics(self) -> Dict[str, Any]:
        """获取客户统计信息"""
        # 查询数据库
        stats_sql = """
        SELECT
            customer_type,
            COUNT(*) as count,
            AVG(CASE WHEN last_order_amount IS NOT NULL THEN last_order_amount ELSE 0 END) as avg_amount
        FROM customers
        GROUP BY customer_type
        """

        results = self.db.query(stats_sql)

        # 格式化统计结果
        formatted_stats = {}
        total_customers = 0
        total_amount = 0

        for row in results:
            customer_type = row["customer_type"]
            count = row["count"]
            avg_amount = row["avg_amount"]

            formatted_stats[customer_type] = {
                "count": count,
                "average_amount": format_currency(avg_amount),
                "percentage": 0,  # 稍后计算
            }

            total_customers += count
            total_amount += avg_amount * count

        # 计算百分比
        for stats in formatted_stats.values():
            stats["percentage"] = round(stats["count"] / total_customers * 100, 1)

        return {
            "total_customers": total_customers,
            "total_amount": format_currency(total_amount),
            "by_type": formatted_stats,
        }


class ReportService:
    """报表服务 - 异步模式示例"""

    def __init__(self, db_connection):
        self.db = create_unified_database(db_connection)
        self.file_ops = create_unified_file_ops()

    @unified_operation
    def generate_monthly_report(self, year: int, month: int) -> str:
        """生成月度报表"""
        # 查询月度数据
        sql = """
        SELECT
            DATE(created_at) as date,
            COUNT(*) as new_customers,
            SUM(COALESCE(last_order_amount, 0)) as daily_revenue
        FROM customers
        WHERE strftime('%Y', created_at) = ?
        AND strftime('%m', created_at) = ?
        GROUP BY DATE(created_at)
        ORDER BY date
        """

        data = self.db.query(sql, (str(year), f"{month:02d}"))

        # 生成报表内容
        report_lines = [
            f"# {year}年{month}月客户报表",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 每日统计",
            "",
        ]

        total_customers = 0
        total_revenue = 0

        for row in data:
            date = row["date"]
            new_customers = row["new_customers"]
            daily_revenue = row["daily_revenue"]

            report_lines.append(
                f"- {date}: {new_customers}个新客户, "
                f"收入 {format_currency(daily_revenue)}"
            )

            total_customers += new_customers
            total_revenue += daily_revenue

        report_lines.extend(
            [
                "",
                "## 月度汇总",
                f"- 新增客户: {total_customers}个",
                f"- 总收入: {format_currency(total_revenue)}",
                f"- 平均日收入: {format_currency(total_revenue / len(data) if data else 0)}",
            ]
        )

        report_content = "\n".join(report_lines)

        # 保存报表文件
        filename = f"reports/monthly_report_{year}_{month:02d}.md"
        self.file_ops.write_file(filename, report_content)

        return filename


# 使用示例
def sync_usage_example():
    """同步使用示例"""
    print("=== 同步使用示例 ===")

    # 创建数据库连接
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            customer_type TEXT,
            last_order_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 创建服务实例
    customer_service = CustomerService(conn)

    # 同步调用
    customer_data = {
        "name": "测试公司",
        "phone": "13812345678",
        "email": "test@example.com",
        "customer_type": "生态板客户",
    }

    result = customer_service.create_customer(customer_data)
    print(f"创建客户结果: {result}")

    stats = customer_service.get_customer_statistics()
    print(f"客户统计: {stats}")


async def async_usage_example():
    """异步使用示例"""
    print("=== 异步使用示例 ===")

    # 创建数据库连接（在实际项目中可能是异步连接）
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            customer_type TEXT,
            last_order_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 创建服务实例
    customer_service = CustomerService(conn)
    report_service = ReportService(conn)

    # 异步调用 - 同样的函数，但在异步上下文中
    customer_data = {
        "name": "异步测试公司",
        "phone": "13987654321",
        "email": "async@example.com",
        "customer_type": "家具板客户",
    }

    result = await customer_service.create_customer(customer_data)
    print(f"异步创建客户结果: {result}")

    stats = await customer_service.get_customer_statistics()
    print(f"异步客户统计: {stats}")

    # 生成报表
    from datetime import datetime

    now = datetime.now()
    report_file = await report_service.generate_monthly_report(now.year, now.month)
    print(f"生成报表文件: {report_file}")


def batch_processing_example():
    """批量处理示例 - 展示同步/异步的性能差异"""
    print("=== 批量处理示例 ===")

    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            customer_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    customer_service = CustomerService(conn)

    # 准备测试数据
    test_customers = [
        {
            "name": f"客户{i}",
            "phone": f"138{i:08d}",
            "email": f"customer{i}@example.com",
            "customer_type": ["生态板客户", "家具板客户", "阻燃板客户"][i % 3],
        }
        for i in range(1, 101)  # 100个客户
    ]

    # 同步批量处理
    import time

    start_time = time.time()

    for customer_data in test_customers:
        customer_service.create_customer(customer_data)

    sync_time = time.time() - start_time
    print(f"同步处理100个客户耗时: {sync_time:.2f}秒")

    # 异步批量处理
    async def async_batch():
        start_time = time.time()

        tasks = [
            customer_service.create_customer(customer_data)
            for customer_data in test_customers
        ]

        await asyncio.gather(*tasks)

        async_time = time.time() - start_time
        print(f"异步处理100个客户耗时: {async_time:.2f}秒")
        print(f"性能提升: {sync_time / async_time:.1f}倍")

    # 注意：在实际场景中，异步的优势主要体现在I/O密集型操作
    # 这个示例中由于使用的是内存数据库，差异可能不明显
    asyncio.run(async_batch())


if __name__ == "__main__":
    # 运行示例
    sync_usage_example()
    print()

    asyncio.run(async_usage_example())
    print()

    batch_processing_example()

    print("\n=== 总结 ===")
    print("✅ 统一的同步/异步接口让代码更加灵活")
    print("✅ 相同的业务逻辑可以在不同上下文中复用")
    print("✅ 性能优化可以通过选择合适的执行模式实现")
    print("✅ 代码维护成本降低，避免了重复实现")
