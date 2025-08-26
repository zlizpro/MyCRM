"""
MiniCRM 性能监控集成示例

演示如何在MiniCRM应用程序中集成性能监控hooks到关键操作。
这个示例展示了任务21.1.1的完整实现。
"""

import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.minicrm.core.performance_bootstrap import performance_bootstrap
from src.minicrm.core.performance_integration import performance_integration
from src.minicrm.data.database.database_manager import DatabaseManager
from src.minicrm.services.customer_service import CustomerService
from src.minicrm.data.dao.customer_dao import CustomerDAO


def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("performance_integration_demo.log"),
        ],
    )


def create_mock_ui_component():
    """创建模拟UI组件用于演示"""

    class MockCustomerPanel:
        def __init__(self):
            self.data = []

        def load_data(self):
            """模拟数据加载"""
            import time

            time.sleep(0.1)  # 模拟加载时间
            self.data = [f"Customer {i}" for i in range(100)]
            return self.data

        def refresh_data(self):
            """模拟数据刷新"""
            import time

            time.sleep(0.05)  # 模拟刷新时间
            return self.load_data()

        def update_display(self):
            """模拟显示更新"""
            import time

            time.sleep(0.02)  # 模拟更新时间
            print(f"显示 {len(self.data)} 条客户记录")

    return MockCustomerPanel()


def demonstrate_performance_integration():
    """演示性能监控集成的完整流程"""

    print("=== MiniCRM 性能监控集成演示 ===\n")

    # 1. 创建应用程序组件
    print("1. 创建应用程序组件...")

    # 创建数据库管理器
    db_path = Path("demo_minicrm.db")
    database_manager = DatabaseManager(db_path)

    # 创建DAO和服务
    customer_dao = CustomerDAO(database_manager)
    customer_service = CustomerService(customer_dao)

    # 创建模拟UI组件
    customer_panel = create_mock_ui_component()

    # 组装应用程序组件
    app_components = {
        "database_manager": database_manager,
        "services": {
            "customer_service": customer_service,
        },
        "ui_components": {
            "customer_panel": customer_panel,
        },
    }

    print("✓ 应用程序组件创建完成\n")

    # 2. 启动性能监控集成
    print("2. 启动性能监控集成...")

    try:
        # 加载配置
        performance_bootstrap.load_config()

        # 执行启动集成
        performance_bootstrap.bootstrap_application(app_components)

        print("✓ 性能监控集成启动完成\n")

    except Exception as e:
        print(f"✗ 性能监控集成启动失败: {e}\n")
        return

    # 3. 演示被监控的操作
    print("3. 演示被监控的操作...")

    try:
        # 初始化数据库（这会触发数据库操作监控）
        print("  - 初始化数据库...")
        database_manager.initialize_database()

        # 执行服务操作（这会触发服务方法监控）
        print("  - 执行客户服务操作...")

        # 创建测试客户数据
        test_customer_data = {
            "name": "测试客户公司",
            "phone": "13812345678",
            "customer_type": "生态板客户",
            "address": "上海市浦东新区测试路123号",
        }

        # 这些操作都会被性能监控hooks捕获
        customer_id = customer_service.create_customer(test_customer_data)
        print(f"    ✓ 创建客户成功，ID: {customer_id}")

        customer_info = customer_service.get_customer_by_id(customer_id)
        print(
            f"    ✓ 获取客户信息: {customer_info['name'] if customer_info else 'None'}"
        )

        # 执行UI操作（这会触发UI操作监控）
        print("  - 执行UI操作...")
        customer_panel.load_data()
        customer_panel.refresh_data()
        customer_panel.update_display()

        print("✓ 被监控操作演示完成\n")

    except Exception as e:
        print(f"✗ 操作演示失败: {e}\n")

    # 4. 获取性能监控报告
    print("4. 获取性能监控报告...")

    try:
        # 获取集成状态
        bootstrap_status = performance_bootstrap.get_bootstrap_status()
        print("集成状态:")
        print(f"  - 启动集成完成: {bootstrap_status['bootstrap_completed']}")
        print(f"  - 配置已加载: {bootstrap_status['config_loaded']}")
        print(f"  - 性能监控启用: {bootstrap_status['performance_enabled']}")
        print(
            f"  - 已集成服务: {bootstrap_status['integration_status']['integrated_services_count']}"
        )
        print(
            f"  - 已集成数据库组件: {bootstrap_status['integration_status']['integrated_daos_count']}"
        )
        print(
            f"  - 已集成UI组件: {bootstrap_status['integration_status']['integrated_ui_components_count']}"
        )
        print()

        # 获取性能报告
        performance_report = performance_integration.get_performance_report()

        if "performance_data" in performance_report:
            perf_data = performance_report["performance_data"]
            summary = perf_data.get("summary", {})

            print("性能监控数据:")
            print(f"  - 总操作数: {summary.get('total_operations', 0)}")
            print(f"  - 唯一操作数: {summary.get('unique_operations', 0)}")
            print(f"  - 总耗时: {summary.get('total_duration_ms', 0):.2f}ms")
            print(f"  - 平均耗时: {summary.get('avg_duration_ms', 0):.2f}ms")
            print(f"  - 当前内存使用: {summary.get('current_memory_mb', 0):.2f}MB")
            print()

            # 显示各类型操作的统计
            for category in ["database", "services", "ui"]:
                if category in perf_data:
                    cat_data = perf_data[category]
                    print(f"{category.upper()}操作统计:")
                    print(f"  - 操作数: {cat_data.get('operations_count', 0)}")
                    print(f"  - 总耗时: {cat_data.get('total_duration_ms', 0):.2f}ms")
                    print()

        # 显示优化建议
        if "recommendations" in performance_report:
            print("性能优化建议:")
            for i, rec in enumerate(performance_report["recommendations"], 1):
                print(f"  {i}. {rec}")
            print()

        print("✓ 性能监控报告获取完成\n")

    except Exception as e:
        print(f"✗ 获取性能监控报告失败: {e}\n")

    # 5. 导出性能数据
    print("5. 导出性能数据...")

    try:
        export_path = "performance_demo_export.json"
        success = performance_integration.export_performance_data(export_path)

        if success:
            print(f"✓ 性能数据导出成功: {export_path}")
        else:
            print("✗ 性能数据导出失败")

    except Exception as e:
        print(f"✗ 导出性能数据失败: {e}")

    print("\n=== 演示完成 ===")

    # 6. 生成集成报告
    print("\n6. 生成详细集成报告...")
    try:
        integration_report = performance_bootstrap.generate_integration_report()
        print("\n" + integration_report)
    except Exception as e:
        print(f"✗ 生成集成报告失败: {e}")

    # 清理
    try:
        database_manager.close()
        if db_path.exists():
            db_path.unlink()  # 删除演示数据库文件
    except Exception as e:
        print(f"清理资源时出错: {e}")


def demonstrate_manual_integration():
    """演示手动集成性能监控的方法"""

    print("\n=== 手动集成演示 ===\n")

    # 1. 手动初始化性能监控
    print("1. 手动初始化性能监控...")
    performance_integration.initialize()
    print("✓ 性能监控初始化完成\n")

    # 2. 手动集成数据库管理器
    print("2. 手动集成数据库管理器...")
    db_path = Path("manual_demo_minicrm.db")
    database_manager = DatabaseManager(db_path)
    performance_integration.integrate_database_manager(database_manager)
    print("✓ 数据库管理器集成完成\n")

    # 3. 手动集成服务
    print("3. 手动集成服务...")
    customer_dao = CustomerDAO(database_manager)
    customer_service = CustomerService(customer_dao)
    performance_integration.integrate_service(customer_service, "customer_service")
    print("✓ 客户服务集成完成\n")

    # 4. 手动集成UI组件
    print("4. 手动集成UI组件...")
    ui_component = create_mock_ui_component()
    performance_integration.integrate_ui_component(ui_component, "customer_panel")
    print("✓ UI组件集成完成\n")

    # 5. 测试集成效果
    print("5. 测试集成效果...")
    try:
        # 执行一些操作来测试监控
        database_manager.initialize_database()
        ui_component.load_data()
        ui_component.refresh_data()

        # 获取监控报告
        report = performance_integration.get_performance_report()
        summary = report.get("performance_data", {}).get("summary", {})

        print(f"  - 监控到 {summary.get('total_operations', 0)} 个操作")
        print(f"  - 总耗时: {summary.get('total_duration_ms', 0):.2f}ms")

        print("✓ 手动集成测试完成\n")

    except Exception as e:
        print(f"✗ 手动集成测试失败: {e}\n")

    # 清理
    try:
        database_manager.close()
        if db_path.exists():
            db_path.unlink()
    except Exception as e:
        print(f"清理资源时出错: {e}")


def main():
    """主函数"""
    setup_logging()

    print("MiniCRM 性能监控集成演示程序")
    print("=" * 50)

    try:
        # 演示自动集成
        demonstrate_performance_integration()

        # 演示手动集成
        demonstrate_manual_integration()

        print("\n所有演示完成！")

    except Exception as e:
        print(f"演示程序执行失败: {e}")
        logging.exception("演示程序异常")


if __name__ == "__main__":
    main()
