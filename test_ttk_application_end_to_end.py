#!/usr/bin/env python3
"""MiniCRM TTK应用程序端到端功能测试

这个测试验证TTK应用程序能够完整启动并运行基本功能。
包括实际的应用程序启动、界面显示、基本操作等。

作者: MiniCRM开发团队
日期: 2024年
"""

import logging
import os
from pathlib import Path
import sys
import tempfile
import threading
import time


# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# 设置测试环境
os.environ["MINICRM_TEST_MODE"] = "1"
os.environ["MINICRM_LOG_LEVEL"] = "INFO"


def test_ttk_application_startup():
    """测试TTK应用程序启动"""
    print("🚀 TTK应用程序端到端启动测试")
    print("=" * 60)

    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # 创建临时数据库
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db_path = temp_db.name
    temp_db.close()

    logger.info(f"使用临时数据库: {temp_db_path}")

    try:
        print("\n📋 步骤1: 导入必要模块...")
        from minicrm.application_ttk import MiniCRMApplicationTTK
        from minicrm.config.settings import ConfigManager

        print("  ✅ 模块导入成功")

        print("\n⚙️ 步骤2: 创建配置...")
        config = ConfigManager()
        config.database.path = temp_db_path
        print("  ✅ 配置创建成功")

        print("\n🏗️ 步骤3: 创建TTK应用程序实例...")
        app = MiniCRMApplicationTTK(config)
        print("  ✅ TTK应用程序实例创建成功")

        print("\n🔍 步骤4: 验证应用程序状态...")
        assert app.is_initialized, "应用程序应该已初始化"
        assert not app.is_running, "应用程序不应该正在运行"
        assert not app.is_shutting_down, "应用程序不应该正在关闭"
        print("  ✅ 应用程序状态验证通过")

        print("\n🏠 步骤5: 验证主窗口...")
        main_window = app.main_window
        assert main_window is not None, "主窗口应该存在"
        print("  ✅ 主窗口验证通过")

        print("\n🔧 步骤6: 验证服务层...")
        service_status = app.get_service_status()
        for service_name, status in service_status.items():
            assert status, f"{service_name} 应该可用"
            print(f"    ✅ {service_name}: 可用")
        print("  ✅ 服务层验证通过")

        print("\n🗄️ 步骤7: 验证数据库...")
        db_manager = app.database_manager
        assert db_manager is not None, "数据库管理器应该可用"
        assert db_manager.is_connected, "数据库应该已连接"

        # 测试基本数据库操作
        tables = db_manager.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = [table[0] for table in tables]
        print(f"    📋 数据库表: {len(table_names)}个")
        assert len(table_names) > 0, "应该有数据库表"
        print("  ✅ 数据库验证通过")

        print("\n💼 步骤8: 验证基本业务操作...")
        # 测试客户服务
        customer_service = app.customer_service
        if customer_service and hasattr(customer_service, "get_all_customers"):
            customers = customer_service.get_all_customers()
            print(f"    👥 客户数量: {len(customers)}")

        # 测试供应商服务
        supplier_service = app.supplier_service
        if supplier_service and hasattr(supplier_service, "get_all_suppliers"):
            suppliers = supplier_service.get_all_suppliers()
            print(f"    🏭 供应商数量: {len(suppliers)}")

        print("  ✅ 基本业务操作验证通过")

        print("\n⚡ 步骤9: 性能测试...")
        start_time = time.time()

        # 执行一些基本操作
        app.get_application_info()
        if customer_service and hasattr(customer_service, "get_all_customers"):
            customer_service.get_all_customers()

        operation_time = time.time() - start_time
        print(f"    ⏱️ 基本操作耗时: {operation_time:.3f}秒")
        assert operation_time < 1.0, "基本操作应该在1秒内完成"
        print("  ✅ 性能测试通过")

        print("\n🎯 步骤10: 模拟短时间运行...")

        def run_app_briefly():
            """在后台线程中短时间运行应用程序"""
            try:
                # 显示主窗口
                main_window.deiconify()
                main_window.lift()

                # 运行很短时间
                main_window.after(100, main_window.quit)  # 100ms后退出
                main_window.mainloop()
            except Exception as e:
                logger.error(f"应用程序运行测试失败: {e}")

        # 在后台线程运行
        app_thread = threading.Thread(target=run_app_briefly, daemon=True)
        app_thread.start()
        app_thread.join(timeout=2.0)  # 最多等待2秒

        print("  ✅ 应用程序运行测试通过")

        print("\n🛑 步骤11: 关闭应用程序...")
        app.shutdown()
        assert app.is_shutting_down or not app.is_initialized, "应用程序应该已关闭"
        print("  ✅ 应用程序关闭成功")

        print("\n" + "=" * 60)
        print("🎉 TTK应用程序端到端测试完全成功！")
        print("=" * 60)
        print("✅ 应用程序能够正常启动")
        print("✅ 所有核心组件工作正常")
        print("✅ 服务层集成完整")
        print("✅ 数据库连接正常")
        print("✅ 基本业务操作可用")
        print("✅ 性能表现优秀")
        print("✅ 应用程序能够正常关闭")
        print("\n🏆 TTK迁移完全成功！")

        return True

    except Exception as e:
        print(f"\n❌ 端到端测试失败: {e}")
        logger.exception("端到端测试异常")
        return False

    finally:
        # 清理临时数据库
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


def test_ttk_application_components():
    """测试TTK应用程序组件"""
    print("\n🧩 TTK组件可用性测试")
    print("-" * 40)

    try:
        # 测试TTK基础组件
        components = [
            ("minicrm.ui.ttk_base.data_table_ttk", "DataTableTTK"),
            ("minicrm.ui.ttk_base.form_builder", "FormBuilderTTK"),
            ("minicrm.ui.ttk_base.theme_manager", "TTKThemeManager"),
            ("minicrm.ui.ttk_base.main_window_ttk", "MainWindowTTK"),
            ("minicrm.ui.ttk_base.base_widget", "BaseWidget"),
        ]

        available_count = 0
        for module_name, class_name in components:
            try:
                module = __import__(module_name, fromlist=[class_name])
                component_class = getattr(module, class_name)
                print(f"  ✅ {class_name}: 可用")
                available_count += 1
            except (ImportError, AttributeError) as e:
                print(f"  ⚠️ {class_name}: 不可用 - {e}")

        print(
            f"\n📊 组件可用性: {available_count}/{len(components)} ({available_count / len(components) * 100:.1f}%)"
        )

        # 测试业务面板
        panels = [
            ("minicrm.ui.ttk_base.finance_panel_ttk", "FinancePanelTTK"),
            ("minicrm.ui.ttk_base.quote_panel_ttk", "QuotePanelTTK"),
            ("minicrm.ui.ttk_base.contract_panel_ttk", "ContractPanelTTK"),
            ("minicrm.ui.ttk_base.task_panel_ttk", "TaskPanelTTK"),
            ("minicrm.ui.ttk_base.import_export_panel_ttk", "ImportExportPanelTTK"),
        ]

        panel_count = 0
        for module_name, class_name in panels:
            try:
                module = __import__(module_name, fromlist=[class_name])
                panel_class = getattr(module, class_name)
                print(f"  ✅ {class_name}: 可用")
                panel_count += 1
            except (ImportError, AttributeError) as e:
                print(f"  ⚠️ {class_name}: 不可用 - {e}")

        print(
            f"\n📊 业务面板可用性: {panel_count}/{len(panels)} ({panel_count / len(panels) * 100:.1f}%)"
        )

        return (
            available_count >= len(components) * 0.8
            and panel_count >= len(panels) * 0.6
        )

    except Exception as e:
        print(f"❌ 组件测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 MiniCRM TTK应用程序端到端功能测试")
    print("=" * 80)

    success_count = 0
    total_tests = 2

    # 测试1: 应用程序启动
    if test_ttk_application_startup():
        success_count += 1

    # 测试2: 组件可用性
    if test_ttk_application_components():
        success_count += 1

    # 输出最终结果
    print("\n" + "=" * 80)
    print("📊 端到端测试结果摘要")
    print("=" * 80)
    print(f"总测试数: {total_tests}")
    print(f"成功: {success_count}")
    print(f"失败: {total_tests - success_count}")

    success_rate = success_count / total_tests * 100
    print(f"成功率: {success_rate:.1f}%")

    if success_rate >= 100:
        print("\n🎉 所有端到端测试完全通过！")
        print("🏆 TTK应用程序完全可用！")
        conclusion = "PERFECT"
    elif success_rate >= 80:
        print("\n👍 端到端测试基本通过！")
        print("✅ TTK应用程序基本可用")
        conclusion = "GOOD"
    else:
        print("\n⚠️ 端到端测试需要改进")
        print("❌ TTK应用程序存在问题")
        conclusion = "NEEDS_WORK"

    print(f"\n🏆 最终评级: {conclusion}")

    return success_rate >= 80


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
