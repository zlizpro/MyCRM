#!/usr/bin/env python3
"""MiniCRM TTK报价管理演示

演示TTK报价管理功能的使用，包括：
- 报价比较功能
- 报价模板管理
- 报价导出功能
- 报价管理面板

这个演示展示了任务8和8.1的实现成果。
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from unittest.mock import Mock


# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.minicrm.services.quote_service import QuoteServiceRefactored
    from src.minicrm.services.quote_template_service import QuoteTemplateService
    from src.minicrm.ui.ttk_base.quote_comparison_ttk import QuoteComparisonTTK
    from src.minicrm.ui.ttk_base.quote_export_ttk import QuoteExportTTK
    from src.minicrm.ui.ttk_base.quote_panel_ttk import QuotePanelTTK
    from src.minicrm.ui.ttk_base.quote_template_ttk import QuoteTemplateTTK
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在项目根目录运行此演示")
    sys.exit(1)


class QuoteManagementDemo:
    """报价管理演示应用"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MiniCRM TTK报价管理演示")
        self.root.geometry("1200x800")

        # 创建模拟服务
        self.quote_service = self._create_mock_quote_service()
        self.template_service = self._create_mock_template_service()

        self._setup_ui()

    def _create_mock_quote_service(self):
        """创建模拟报价服务"""
        mock_service = Mock(spec=QuoteServiceRefactored)

        # 模拟报价数据
        mock_quotes = []
        for i in range(1, 6):
            quote_mock = Mock()
            quote_mock.to_dict.return_value = {
                "id": i,
                "quote_number": f"Q2024010100{i}",
                "customer_name": f"测试客户{i}",
                "contact_person": f"联系人{i}",
                "status_display": "已发送" if i % 2 == 0 else "草稿",
                "quote_type_display": "标准报价" if i % 2 == 0 else "定制报价",
                "formatted_total": f"¥{i * 10000:,}.00",
                "formatted_quote_date": "2024-01-01",
                "formatted_valid_until": "2024-01-31",
                "remaining_days": 30 - i * 5,
            }
            mock_quotes.append(quote_mock)

        mock_service.list_all.return_value = mock_quotes
        mock_service.delete.return_value = True

        # 模拟比较功能
        mock_service.compare_quotes.return_value = {
            "quotes": [mock_quotes[0].to_dict(), mock_quotes[1].to_dict()],
            "differences": {"formatted_total": {"description": "金额不同"}},
            "statistics": {
                "average_amount": "¥15,000.00",
                "max_amount": "¥20,000.00",
                "min_amount": "¥10,000.00",
            },
        }

        return mock_service

    def _create_mock_template_service(self):
        """创建模拟模板服务"""
        mock_service = Mock(spec=QuoteTemplateService)

        # 模拟模板数据
        mock_templates = [
            {
                "id": "standard",
                "name": "标准模板",
                "description": "适用于一般报价的标准模板",
                "version": "1.0",
                "is_default": True,
                "is_system": True,
                "created_at": "2024-01-01T00:00:00",
            },
            {
                "id": "professional",
                "name": "专业模板",
                "description": "适用于正式商务报价的专业模板",
                "version": "1.0",
                "is_default": False,
                "is_system": True,
                "created_at": "2024-01-01T00:00:00",
            },
            {
                "id": "custom1",
                "name": "自定义模板1",
                "description": "用户自定义的报价模板",
                "version": "1.0",
                "is_default": False,
                "is_system": False,
                "created_at": "2024-01-02T00:00:00",
            },
        ]

        mock_service.get_all_templates.return_value = mock_templates
        mock_service.get_template.return_value = mock_templates[0]
        mock_service.create_template.return_value = "new_template_id"
        mock_service.update_template.return_value = True
        mock_service.delete_template.return_value = True
        mock_service.duplicate_template.return_value = "duplicated_template_id"
        mock_service.set_default_template.return_value = True

        return mock_service

    def _setup_ui(self):
        """设置用户界面"""
        # 创建主标题
        title_label = ttk.Label(
            self.root,
            text="MiniCRM TTK报价管理演示",
            font=("Microsoft YaHei UI", 16, "bold"),
        )
        title_label.pack(pady=10)

        # 创建说明文本
        info_text = """
这个演示展示了任务8和8.1的实现成果：
• 报价比较功能 - 支持多个报价的对比分析
• 报价模板管理 - 模板创建、编辑、应用
• 报价导出功能 - 支持PDF、Excel、Word格式
• 报价管理面板 - 集成所有功能的主面板

注意：这是一个演示版本，使用模拟数据和服务。
        """

        info_label = ttk.Label(
            self.root, text=info_text.strip(), justify=tk.LEFT, foreground="gray"
        )
        info_label.pack(pady=(0, 10))

        # 创建演示按钮
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        # 报价比较演示按钮
        comparison_btn = ttk.Button(
            button_frame,
            text="📊 报价比较演示",
            command=self._show_comparison_demo,
            width=20,
        )
        comparison_btn.pack(side=tk.LEFT, padx=5)

        # 模板管理演示按钮
        template_btn = ttk.Button(
            button_frame,
            text="🎨 模板管理演示",
            command=self._show_template_demo,
            width=20,
        )
        template_btn.pack(side=tk.LEFT, padx=5)

        # 导出功能演示按钮
        export_btn = ttk.Button(
            button_frame,
            text="📤 导出功能演示",
            command=self._show_export_demo,
            width=20,
        )
        export_btn.pack(side=tk.LEFT, padx=5)

        # 完整面板演示按钮
        panel_btn = ttk.Button(
            button_frame,
            text="🏠 完整面板演示",
            command=self._show_panel_demo,
            width=20,
        )
        panel_btn.pack(side=tk.LEFT, padx=5)

        # 创建演示区域
        self.demo_frame = ttk.Frame(self.root)
        self.demo_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 默认显示完整面板
        self._show_panel_demo()

    def _clear_demo_frame(self):
        """清空演示区域"""
        for widget in self.demo_frame.winfo_children():
            widget.destroy()

    def _show_comparison_demo(self):
        """显示报价比较演示"""
        self._clear_demo_frame()

        try:
            # 创建比较组件
            comparison_widget = QuoteComparisonTTK(
                self.demo_frame,
                self.quote_service,
                comparison_mode="detailed",
                max_quotes=4,
            )
            comparison_widget.pack(fill=tk.BOTH, expand=True)

            # 自动添加一些报价进行演示
            quotes = self.quote_service.list_all()
            if len(quotes) >= 2:
                comparison_widget.add_quote_for_comparison(quotes[0].to_dict())
                comparison_widget.add_quote_for_comparison(quotes[1].to_dict())

            # 设置回调
            comparison_widget.on_comparison_completed = (
                lambda result: messagebox.showinfo(
                    "比较完成", f"比较了 {len(result.get('quotes', []))} 个报价"
                )
            )

        except Exception as e:
            messagebox.showerror("错误", f"创建比较演示失败：{e}")

    def _show_template_demo(self):
        """显示模板管理演示"""
        self._clear_demo_frame()

        try:
            # 创建模板管理组件
            template_widget = QuoteTemplateTTK(self.demo_frame, self.template_service)
            template_widget.pack(fill=tk.BOTH, expand=True)

            # 设置回调
            template_widget.on_template_applied = lambda template: messagebox.showinfo(
                "模板应用", f"已应用模板：{template.get('name', '未知')}"
            )

        except Exception as e:
            messagebox.showerror("错误", f"创建模板演示失败：{e}")

    def _show_export_demo(self):
        """显示导出功能演示"""
        self._clear_demo_frame()

        try:
            # 创建说明标签
            info_label = ttk.Label(
                self.demo_frame,
                text="导出功能演示\n\n点击下面的按钮来测试导出功能：",
                font=("Microsoft YaHei UI", 12),
                justify=tk.CENTER,
            )
            info_label.pack(pady=50)

            # 创建导出按钮
            export_btn = ttk.Button(
                self.demo_frame,
                text="📤 测试导出功能",
                command=self._test_export_function,
                width=30,
            )
            export_btn.pack(pady=20)

        except Exception as e:
            messagebox.showerror("错误", f"创建导出演示失败：{e}")

    def _test_export_function(self):
        """测试导出功能"""
        try:
            # 创建导出组件
            export_widget = QuoteExportTTK(
                self.root,
                self.template_service,
                enable_pdf=True,
                enable_excel=True,
                enable_word=True,
            )

            # 准备测试数据
            test_quotes = [
                quote.to_dict() for quote in self.quote_service.list_all()[:2]
            ]

            # 显示导出对话框
            export_widget.show_export_dialog(test_quotes, "pdf")

        except Exception as e:
            messagebox.showerror("错误", f"测试导出功能失败：{e}")

    def _show_panel_demo(self):
        """显示完整面板演示"""
        self._clear_demo_frame()

        try:
            # 创建完整的报价管理面板
            quote_panel = QuotePanelTTK(
                self.demo_frame, self.quote_service, self.template_service
            )
            quote_panel.pack(fill=tk.BOTH, expand=True)

            # 设置回调
            quote_panel.on_quote_selected = lambda quote: print(
                f"选中报价：{quote.get('quote_number')}"
            )
            quote_panel.on_quote_deleted = lambda quote_id: messagebox.showinfo(
                "删除成功", f"已删除报价 ID: {quote_id}"
            )

        except Exception as e:
            messagebox.showerror("错误", f"创建面板演示失败：{e}")

    def run(self):
        """运行演示应用"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n演示已停止")
        except Exception as e:
            print(f"演示运行错误：{e}")


def main():
    """主函数"""
    print("启动MiniCRM TTK报价管理演示...")
    print("=" * 50)
    print("任务8和8.1实现成果演示")
    print("- 报价比较功能 (QuoteComparisonTTK)")
    print("- 报价模板管理 (QuoteTemplateTTK)")
    print("- 报价导出功能 (QuoteExportTTK)")
    print("- 报价管理面板 (QuotePanelTTK)")
    print("=" * 50)

    try:
        demo = QuoteManagementDemo()
        demo.run()
    except Exception as e:
        print(f"演示启动失败：{e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
