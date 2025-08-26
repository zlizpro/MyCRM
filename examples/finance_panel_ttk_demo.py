#!/usr/bin/env python3
"""MiniCRM TTK财务管理面板演示

演示FinancePanelTTK和FinancialAnalysisTTK组件的功能。
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
from unittest.mock import Mock


# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from minicrm.services.finance_service import FinanceService
from minicrm.ui.ttk_base.finance_panel_ttk import FinancePanelTTK
from minicrm.ui.ttk_base.financial_analysis_ttk import FinancialAnalysisTTK


def create_mock_finance_service():
    """创建模拟的财务服务"""
    mock_service = Mock(spec=FinanceService)

    # 模拟财务汇总数据
    mock_financial_summary = {
        "total_receivables": 250000.0,
        "total_payables": 150000.0,
        "overdue_receivables": 25000.0,
        "overdue_payables": 10000.0,
        "receivables_overdue_rate": 10.0,
        "payables_overdue_rate": 6.7,
        "net_position": 100000.0,
        "generated_at": "2025-01-21T10:30:00",
    }

    mock_service.get_financial_summary.return_value = mock_financial_summary

    return mock_service


def demo_financial_analysis():
    """演示财务分析组件"""
    print("启动财务分析组件演示...")

    root = tk.Tk()
    root.title("MiniCRM TTK财务分析演示")
    root.geometry("1000x700")

    # 创建模拟服务
    finance_service = create_mock_finance_service()

    try:
        # 创建财务分析组件
        analysis_widget = FinancialAnalysisTTK(root, finance_service)
        analysis_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 添加说明标签
        info_label = ttk.Label(
            root,
            text="这是财务分析组件演示。包含财务概览、图表分析和导出功能。",
            font=("Microsoft YaHei UI", 10),
        )
        info_label.pack(side=tk.BOTTOM, pady=5)

        print("财务分析组件创建成功！")
        print("功能包括：")
        print("- 财务概览：显示关键财务指标和风险预警")
        print("- 图表分析：提供趋势图表和对比分析")
        print("- 导出设置：支持Excel、PDF、CSV格式导出")

        root.mainloop()

    except Exception as e:
        print(f"创建财务分析组件失败: {e}")
    finally:
        try:
            analysis_widget.cleanup()
        except:
            pass


def demo_finance_panel():
    """演示财务管理面板"""
    print("启动财务管理面板演示...")

    root = tk.Tk()
    root.title("MiniCRM TTK财务管理面板演示")
    root.geometry("1200x800")

    # 创建模拟服务
    finance_service = create_mock_finance_service()

    try:
        # 创建财务管理面板
        finance_panel = FinancePanelTTK(root, finance_service)
        finance_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 添加说明标签
        info_label = ttk.Label(
            root,
            text="这是财务管理面板演示。包含财务概览、应收应付账款管理和财务分析功能。",
            font=("Microsoft YaHei UI", 10),
        )
        info_label.pack(side=tk.BOTTOM, pady=5)

        print("财务管理面板创建成功！")
        print("功能包括：")
        print("- 财务概览：关键指标卡片和图表展示")
        print("- 应收账款：应收账款列表和管理功能")
        print("- 应付账款：应付账款列表和管理功能")
        print("- 财务分析：集成完整的财务分析功能")

        root.mainloop()

    except Exception as e:
        print(f"创建财务管理面板失败: {e}")
    finally:
        try:
            finance_panel.cleanup()
        except:
            pass


def main():
    """主函数"""
    print("MiniCRM TTK财务管理组件演示")
    print("=" * 50)

    if len(sys.argv) > 1:
        demo_type = sys.argv[1].lower()
    else:
        print("请选择演示类型：")
        print("1. 财务分析组件 (analysis)")
        print("2. 财务管理面板 (panel)")
        choice = input("请输入选择 (1/2 或 analysis/panel): ").strip()

        if choice in ["1", "analysis"]:
            demo_type = "analysis"
        elif choice in ["2", "panel"]:
            demo_type = "panel"
        else:
            print("无效选择，默认演示财务管理面板")
            demo_type = "panel"

    try:
        if demo_type == "analysis":
            demo_financial_analysis()
        elif demo_type == "panel":
            demo_finance_panel()
        else:
            print(f"未知的演示类型: {demo_type}")
            print("支持的类型: analysis, panel")

    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
