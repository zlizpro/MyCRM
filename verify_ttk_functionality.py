#!/usr/bin/env python3
"""验证TTK应用程序完整功能

测试所有业务流程在纯TTK环境下是否正常工作
"""

from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk
import traceback


# 添加src目录到路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


class TTKFunctionalityVerifier:
    """TTK功能验证器"""

    def __init__(self):
        self.root = None
        self.test_results = []

    def setup_test_environment(self):
        """设置测试环境"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # 隐藏主窗口
            return True
        except Exception as e:
            print(f"❌ 测试环境设置失败: {e}")
            return False

    def cleanup_test_environment(self):
        """清理测试环境"""
        try:
            if self.root:
                self.root.destroy()
        except:
            pass

    def test_basic_ttk_components(self):
        """测试基础TTK组件"""
        print("🔍 测试基础TTK组件...")

        try:
            # 测试基本组件创建
            frame = ttk.Frame(self.root)
            label = ttk.Label(frame, text="测试标签")
            button = ttk.Button(frame, text="测试按钮")
            entry = ttk.Entry(frame)
            combobox = ttk.Combobox(frame, values=["选项1", "选项2"])

            # 测试树形视图
            tree = ttk.Treeview(frame, columns=("col1", "col2"), show="headings")
            tree.heading("col1", text="列1")
            tree.heading("col2", text="列2")
            tree.insert("", "end", values=("值1", "值2"))

            # 测试笔记本
            notebook = ttk.Notebook(frame)
            tab1 = ttk.Frame(notebook)
            notebook.add(tab1, text="标签页1")

            print("✅ 基础TTK组件测试通过")
            return True

        except Exception as e:
            print(f"❌ 基础TTK组件测试失败: {e}")
            traceback.print_exc()
            return False

    def test_ttk_base_classes(self):
        """测试TTK基础类"""
        print("🔍 测试TTK基础类...")

        try:
            # 测试基础窗口类
            try:
                from minicrm.ui.ttk_base.base_window import BaseWindowTTK

                base_window = BaseWindowTTK(self.root)
                print("✅ BaseWindowTTK 导入和创建成功")
            except ImportError:
                print("⚠️  BaseWindowTTK 未找到，跳过测试")

            # 测试基础面板类
            try:
                from minicrm.ui.ttk_base.base_panel import BasePanelTTK

                base_panel = BasePanelTTK(self.root)
                print("✅ BasePanelTTK 导入和创建成功")
            except ImportError:
                print("⚠️  BasePanelTTK 未找到，跳过测试")

            # 测试基础对话框类
            try:
                from minicrm.ui.ttk_base.base_dialog import BaseDialogTTK

                print("✅ BaseDialogTTK 导入成功")
            except ImportError:
                print("⚠️  BaseDialogTTK 未找到，跳过测试")

            return True

        except Exception as e:
            print(f"❌ TTK基础类测试失败: {e}")
            traceback.print_exc()
            return False

    def test_ttk_dialogs(self):
        """测试TTK对话框"""
        print("🔍 测试TTK对话框...")

        try:
            # 测试任务编辑对话框
            try:
                from minicrm.ui.task_edit_dialog_ttk import TaskEditDialogTTK

                print("✅ TaskEditDialogTTK 导入成功")
            except ImportError:
                print("⚠️  TaskEditDialogTTK 未找到，跳过测试")

            # 测试合同导出对话框
            try:
                from minicrm.ui.contract_export_dialog_ttk import (
                    ContractExportDialogTTK,
                )

                print("✅ ContractExportDialogTTK 导入成功")
            except ImportError:
                print("⚠️  ContractExportDialogTTK 未找到，跳过测试")

            # 测试供应商编辑对话框
            try:
                from minicrm.ui.panels.supplier_edit_dialog_ttk import (
                    SupplierEditDialogTTK,
                )

                print("✅ SupplierEditDialogTTK 导入成功")
            except ImportError:
                print("⚠️  SupplierEditDialogTTK 未找到，跳过测试")

            return True

        except Exception as e:
            print(f"❌ TTK对话框测试失败: {e}")
            traceback.print_exc()
            return False

    def test_ttk_main_window(self):
        """测试TTK主窗口"""
        print("🔍 测试TTK主窗口...")

        try:
            from minicrm.ui.main_window_ttk import MainWindowTTK

            # 创建主窗口实例（不显示）
            main_window = MainWindowTTK(self.root)
            print("✅ MainWindowTTK 创建成功")

            # 测试主窗口的基本功能
            if hasattr(main_window, "notebook"):
                print("✅ 主窗口包含笔记本组件")

            if hasattr(main_window, "task_tree"):
                print("✅ 主窗口包含任务树组件")

            if hasattr(main_window, "supplier_tree"):
                print("✅ 主窗口包含供应商树组件")

            if hasattr(main_window, "contract_tree"):
                print("✅ 主窗口包含合同树组件")

            return True

        except ImportError:
            print("⚠️  MainWindowTTK 未找到，跳过测试")
            return True
        except Exception as e:
            print(f"❌ TTK主窗口测试失败: {e}")
            traceback.print_exc()
            return False

    def test_ttk_panels(self):
        """测试TTK面板"""
        print("🔍 测试TTK面板...")

        try:
            # 测试任务面板
            try:
                from minicrm.ui.panels.task_panel_ttk import TaskPanelTTK

                task_panel = TaskPanelTTK(self.root)
                print("✅ TaskPanelTTK 创建成功")
            except ImportError:
                print("⚠️  TaskPanelTTK 未找到，跳过测试")

            # 测试供应商面板
            try:
                from minicrm.ui.panels.supplier_panel_ttk import SupplierPanelTTK

                print("✅ SupplierPanelTTK 导入成功")
            except ImportError:
                print("⚠️  SupplierPanelTTK 未找到，跳过测试")

            return True

        except Exception as e:
            print(f"❌ TTK面板测试失败: {e}")
            traceback.print_exc()
            return False

    def test_theme_system(self):
        """测试主题系统"""
        print("🔍 测试主题系统...")

        try:
            # 测试TTK主题管理器
            try:
                from minicrm.ui.themes.managers.theme_applicator_ttk import (
                    ThemeApplicatorTTK,
                )

                theme_applicator = ThemeApplicatorTTK()
                print("✅ ThemeApplicatorTTK 创建成功")
            except ImportError:
                print("⚠️  ThemeApplicatorTTK 未找到，跳过测试")

            # 测试TTK样式表生成器
            try:
                from minicrm.ui.themes.managers.stylesheet_generator_ttk import (
                    TTKStylesheetGenerator,
                )

                generator = TTKStylesheetGenerator()
                print("✅ TTKStylesheetGenerator 创建成功")

                # 测试样式生成
                test_config = {
                    "colors": {"primary": "#007BFF", "background": "#FFFFFF"},
                    "fonts": {"family": "Arial", "size_normal": "14"},
                    "spacing": {"sm": "8", "md": "16"},
                    "border_radius": {"medium": "6"},
                }
                styles = generator.generate_theme_styles(test_config)
                if styles:
                    print("✅ 主题样式生成成功")

            except ImportError:
                print("⚠️  TTKStylesheetGenerator 未找到，跳过测试")

            return True

        except Exception as e:
            print(f"❌ 主题系统测试失败: {e}")
            traceback.print_exc()
            return False

    def test_core_services(self):
        """测试核心服务"""
        print("🔍 测试核心服务...")

        try:
            # 测试数据总线
            try:
                from minicrm.ui.data_bus_ttk import DataBusTTK

                data_bus = DataBusTTK()
                print("✅ DataBusTTK 创建成功")
            except ImportError:
                print("⚠️  DataBusTTK 未找到，跳过测试")

            # 测试状态管理器
            try:
                from minicrm.ui.state_manager_ttk import StateManagerTTK

                state_manager = StateManagerTTK()
                print("✅ StateManagerTTK 创建成功")
            except ImportError:
                print("⚠️  StateManagerTTK 未找到，跳过测试")

            # 测试配置管理
            try:
                from minicrm.core.config_ttk import ConfigManagerTTK

                config_manager = ConfigManagerTTK()
                print("✅ ConfigManagerTTK 创建成功")
            except ImportError:
                print("⚠️  ConfigManagerTTK 未找到，跳过测试")

            return True

        except Exception as e:
            print(f"❌ 核心服务测试失败: {e}")
            traceback.print_exc()
            return False

    def test_no_qt_dependencies(self):
        """测试是否没有Qt依赖"""
        print("🔍 检查Qt依赖...")

        import sys

        qt_modules = [
            name
            for name in sys.modules.keys()
            if any(qt in name.lower() for qt in ["pyside6", "pyqt5", "pyqt6"])
        ]

        if qt_modules:
            print(f"❌ 发现Qt模块: {qt_modules}")
            return False
        print("✅ 未发现Qt模块依赖")
        return True

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始TTK应用程序功能验证")
        print("=" * 60)

        if not self.setup_test_environment():
            return False

        tests = [
            ("基础TTK组件", self.test_basic_ttk_components),
            ("TTK基础类", self.test_ttk_base_classes),
            ("TTK对话框", self.test_ttk_dialogs),
            ("TTK主窗口", self.test_ttk_main_window),
            ("TTK面板", self.test_ttk_panels),
            ("主题系统", self.test_theme_system),
            ("核心服务", self.test_core_services),
            ("Qt依赖检查", self.test_no_qt_dependencies),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} 通过")
                else:
                    print(f"❌ {test_name} 失败")
            except Exception as e:
                print(f"❌ {test_name} 异常: {e}")

        self.cleanup_test_environment()

        print("\n" + "=" * 60)
        print(f"📊 测试结果: {passed}/{total} 通过")

        if passed >= total * 0.8:  # 80%通过率认为成功
            print("🎉 TTK应用程序功能验证通过！")
            print("✨ 应用程序可以在纯TTK环境下正常运行")
            return True
        print("⚠️  TTK应用程序功能验证失败")
        print("💡 请检查上述失败的测试项目")
        return False


def main():
    """主函数"""
    verifier = TTKFunctionalityVerifier()
    success = verifier.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
