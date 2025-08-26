#!/usr/bin/env python3
"""MiniCRM 错误处理和系统监控演示

演示错误处理和系统监控功能的使用方法。
"""

import time
import tkinter as tk
from tkinter import messagebox

from src.minicrm.core.diagnostic_tool import run_system_diagnosis
from src.minicrm.core.system_monitor import (
    get_system_monitor,
    start_system_monitoring,
    stop_system_monitoring,
)
from src.minicrm.core.ttk_error_handler import (
    get_ttk_error_handler,
    handle_ui_operation,
)


def demo_system_monitor():
    """演示系统监控功能"""
    print("=== 系统监控演示 ===")

    # 获取系统监控器
    monitor = get_system_monitor()

    # 显示监控状态
    status = monitor.get_monitoring_status()
    print(f"监控状态: {status}")

    # 启动监控
    print("启动系统监控...")
    start_system_monitoring()

    # 等待一段时间收集数据
    print("收集监控数据中...")
    time.sleep(3)

    # 运行健康检查
    print("运行健康检查...")
    health_results = monitor.run_health_check()

    for result in health_results:
        status_icon = {"healthy": "✓", "warning": "⚠", "critical": "✗"}[result.status]
        print(f"{status_icon} {result.check_name}: {result.message}")

    # 生成性能报告
    print("生成性能报告...")
    report = monitor.generate_performance_report(hours=1)
    print(f"报告时间范围: {report['time_range_hours']} 小时")
    print(f"数据点数量: {report['data_points']}")

    if "recommendations" in report:
        print("性能建议:")
        for recommendation in report["recommendations"]:
            print(f"  - {recommendation}")

    # 停止监控
    print("停止系统监控...")
    stop_system_monitoring()


def demo_diagnostic_tool():
    """演示诊断工具功能"""
    print("\n=== 系统诊断演示 ===")

    # 运行系统诊断
    print("运行系统诊断...")
    results = run_system_diagnosis()

    # 统计结果
    passed = len([r for r in results if r.status == "pass"])
    warnings = len([r for r in results if r.status == "warning"])
    failed = len([r for r in results if r.status == "fail"])

    print(f"诊断结果: 通过 {passed}, 警告 {warnings}, 失败 {failed}")

    # 显示失败和警告的项目
    problem_results = [r for r in results if r.status in ["warning", "fail"]]
    if problem_results:
        print("需要注意的项目:")
        for result in problem_results:
            status_icon = {"warning": "⚠", "fail": "✗"}[result.status]
            print(f"  {status_icon} {result.category}.{result.name}: {result.message}")

            if result.suggestions:
                for suggestion in result.suggestions:
                    print(f"    建议: {suggestion}")
    else:
        print("所有诊断项目都通过了！")


def demo_error_handler():
    """演示错误处理功能"""
    print("\n=== 错误处理演示 ===")

    # 获取错误处理器
    error_handler = get_ttk_error_handler()

    # 演示UI操作错误处理
    print("演示UI操作错误处理...")

    try:
        with handle_ui_operation("demo_operation", widget_type="Button"):
            # 模拟一个可能出错的UI操作
            print("执行UI操作...")
            # 这里可以放置实际的UI操作代码

    except Exception as e:
        print(f"UI操作出错: {e}")

    # 演示错误分类
    print("演示错误分类...")

    try:
        # 模拟一个验证错误
        raise ValueError("无效的输入数据")
    except Exception as e:
        error_info = error_handler.classify_error(e, {"operation": "data_validation"})
        print(f"错误类型: {error_info.error_type}")
        print(f"严重程度: {error_info.severity}")
        print(f"建议动作: {error_info.suggested_action}")

    # 显示错误统计
    stats = error_handler.get_ui_error_statistics()
    print(f"错误统计: {stats}")


def demo_with_gui():
    """演示带GUI的错误处理"""
    print("\n=== GUI错误处理演示 ===")

    try:
        # 创建一个简单的GUI窗口
        root = tk.Tk()
        root.title("错误处理演示")
        root.geometry("400x300")

        # 设置错误处理器的父窗口
        error_handler = get_ttk_error_handler(root)

        def test_validation_error():
            """测试验证错误"""
            error_handler.show_validation_error("用户名", "用户名不能为空")

        def test_business_error():
            """测试业务错误"""
            error_handler.show_business_error("保存数据", "数据库连接失败")

        def test_confirm_operation():
            """测试确认操作"""
            result = error_handler.confirm_operation("删除", "确认删除选中的项目吗？")
            if result:
                messagebox.showinfo("结果", "用户确认了操作")
            else:
                messagebox.showinfo("结果", "用户取消了操作")

        # 创建按钮
        tk.Button(root, text="测试验证错误", command=test_validation_error).pack(
            pady=10
        )
        tk.Button(root, text="测试业务错误", command=test_business_error).pack(pady=10)
        tk.Button(root, text="测试确认操作", command=test_confirm_operation).pack(
            pady=10
        )
        tk.Button(root, text="关闭", command=root.quit).pack(pady=10)

        print("GUI窗口已创建，请测试错误处理功能...")
        root.mainloop()
        root.destroy()

    except Exception as e:
        print(f"GUI演示失败: {e}")
        print("可能是在无GUI环境中运行，跳过GUI演示")


def main():
    """主函数"""
    print("MiniCRM 错误处理和系统监控演示")
    print("=" * 50)

    try:
        # 演示系统监控
        demo_system_monitor()

        # 演示诊断工具
        demo_diagnostic_tool()

        # 演示错误处理
        demo_error_handler()

        # 演示GUI错误处理（可选）
        demo_with_gui()

    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"\n演示过程中出现错误: {e}")
    finally:
        # 确保停止监控
        try:
            stop_system_monitoring()
        except:
            pass

        print("\n演示完成！")


if __name__ == "__main__":
    main()
