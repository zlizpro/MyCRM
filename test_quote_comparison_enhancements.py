#!/usr/bin/env python3
"""
测试报价历史比对功能的增强

验证新增的功能：
1. Excel导出功能
2. 智能建议分析
3. 竞争力分析
4. 界面交互优化
"""

import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from datetime import datetime
from unittest.mock import Mock


def test_quote_comparison_service_enhancements():
    """测试报价比对服务的增强功能"""
    print("🧪 测试报价比对服务增强功能...")

    try:
        from minicrm.models.enums import QuoteStatus
        from minicrm.models.quote import Quote
        from minicrm.services.quote.quote_comparison_service import (
            QuoteComparisonService,
        )

        # 创建模拟的报价数据
        mock_quotes = []
        for i in range(3):
            quote = Mock(spec=Quote)
            quote.id = i + 1
            quote.quote_number = f"Q2025{i + 1:03d}"
            quote.customer_name = "测试客户"
            quote.total_amount = 100000 + i * 10000  # 递增的金额
            quote.quote_date = datetime(2025, 1, i + 1)
            quote.quote_status = QuoteStatus.DRAFT if i == 0 else QuoteStatus.SENT
            quote.items = []  # 简化，不添加具体项目
            mock_quotes.append(quote)

        # 创建服务实例
        mock_core_service = Mock()
        mock_core_service.get_by_id.side_effect = (
            lambda quote_id: mock_quotes[quote_id - 1]
            if quote_id <= len(mock_quotes)
            else None
        )

        service = QuoteComparisonService(mock_core_service)

        # 测试详细比对功能
        result = service.compare_quotes([1, 2, 3], "detailed")

        # 验证基本结构
        if "comparison_type" not in result:
            raise ValueError("结果中缺少 comparison_type 字段")
        if "intelligent_suggestions" not in result:
            raise ValueError("结果中缺少 intelligent_suggestions 字段")
        if "competitiveness_analysis" not in result:
            raise ValueError("结果中缺少 competitiveness_analysis 字段")
        if result["comparison_type"] != "detailed":
            raise ValueError(
                f"期望 comparison_type 为 'detailed'，"
                f"实际为 '{result['comparison_type']}'"
            )

        # 验证智能建议结构
        suggestions = result["intelligent_suggestions"]
        required_suggestion_fields = [
            "pricing_strategy",
            "product_optimization",
            "market_insights",
            "risk_warnings",
        ]
        for field in required_suggestion_fields:
            if field not in suggestions:
                raise ValueError(f"智能建议中缺少 {field} 字段")

        # 验证竞争力分析结构
        competitiveness = result["competitiveness_analysis"]
        required_competitiveness_fields = ["competitiveness_ranking", "insights"]
        for field in required_competitiveness_fields:
            if field not in competitiveness:
                raise ValueError(f"竞争力分析中缺少 {field} 字段")

        print("✅ 报价比对服务增强功能测试通过")
        return True

    except Exception as e:
        print(f"❌ 报价比对服务测试失败: {e}")
        return False


def test_quote_comparison_dialog_structure():
    """测试报价比对对话框的结构"""
    print("🧪 测试报价比对对话框结构...")

    try:
        from minicrm.ui.quote_comparison_dialog import QuoteComparisonDialog

        # 验证类定义存在
        required_methods = [
            "_create_suggestions_tab",
            "_create_competitiveness_tab",
            "_update_suggestions_display",
            "_update_competitiveness_display",
            "_export_comparison_to_excel",
            "_create_suggestions_sheet",
            "_create_competitiveness_sheet",
        ]

        missing_methods = [
            method_name
            for method_name in required_methods
            if not hasattr(QuoteComparisonDialog, method_name)
        ]

        if missing_methods:
            methods_str = ", ".join(missing_methods)
            raise ValueError(f"QuoteComparisonDialog 缺少以下方法: {methods_str}")

        print("✅ 报价比对对话框结构测试通过")
        return True

    except Exception as e:
        print(f"❌ 报价比对对话框结构测试失败: {e}")
        return False


def test_excel_export_dependencies():
    """测试Excel导出功能的依赖"""
    print("🧪 测试Excel导出依赖...")

    try:
        import importlib.util

        # 检查必要的库是否可用
        required_modules = [
            "openpyxl",
            "pandas",
            "openpyxl.styles",
            "openpyxl.utils.dataframe",
        ]

        missing_modules = []
        for module_name in required_modules:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                missing_modules.append(module_name)

        if missing_modules:
            print(f"⚠️ Excel导出依赖缺失: {', '.join(missing_modules)}")
            print("💡 建议安装: pip install pandas openpyxl")
            return False

        print("✅ Excel导出依赖检查通过")
        return True

    except Exception as e:
        print(f"❌ Excel导出依赖检查失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("🚀 开始测试报价历史比对功能增强...")
    print("=" * 60)

    tests = [
        test_quote_comparison_service_enhancements,
        test_quote_comparison_dialog_structure,
        test_excel_export_dependencies,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！报价历史比对功能增强完成")
    else:
        print("⚠️ 部分测试未通过，请检查相关功能")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
