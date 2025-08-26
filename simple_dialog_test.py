#!/usr/bin/env python3
"""简单的TTK对话框测试

测试TTK对话框的基本功能，避免GUI阻塞问题
"""

from pathlib import Path
import sys


# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


def test_imports():
    """测试导入是否正常"""
    try:
        from minicrm.ui.task_edit_dialog_ttk import TaskEditDialogTTK

        print("✓ TaskEditDialogTTK 导入成功")

        from minicrm.ui.contract_export_dialog_ttk import ContractExportDialogTTK

        print("✓ ContractExportDialogTTK 导入成功")

        from minicrm.ui.panels.supplier_edit_dialog_ttk import SupplierEditDialogTTK

        print("✓ SupplierEditDialogTTK 导入成功")

        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False


def test_dialog_creation():
    """测试对话框创建（不显示GUI）"""
    try:
        import tkinter as tk

        # 创建隐藏的根窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口

        from minicrm.ui.task_edit_dialog_ttk import TaskEditDialogTTK

        # 测试任务对话框创建
        task_dialog = TaskEditDialogTTK(root)
        print("✓ TaskEditDialogTTK 创建成功")
        task_dialog.destroy()

        # 测试合同导出对话框创建
        from minicrm.ui.contract_export_dialog_ttk import ContractExportDialogTTK

        contract_dialog = ContractExportDialogTTK(root, contracts=[])
        print("✓ ContractExportDialogTTK 创建成功")
        contract_dialog.destroy()

        # 测试供应商对话框创建
        from minicrm.ui.panels.supplier_edit_dialog_ttk import SupplierEditDialogTTK

        supplier_dialog = SupplierEditDialogTTK(root)
        print("✓ SupplierEditDialogTTK 创建成功")
        supplier_dialog.destroy()

        root.destroy()
        return True

    except Exception as e:
        print(f"✗ 对话框创建失败: {e}")
        return False


def test_base_dialog_inheritance():
    """测试BaseDialogTTK继承"""
    try:
        import tkinter as tk

        from minicrm.ui.ttk_base.base_dialog import BaseDialogTTK

        root = tk.Tk()
        root.withdraw()

        from minicrm.ui.contract_export_dialog_ttk import ContractExportDialogTTK
        from minicrm.ui.task_edit_dialog_ttk import TaskEditDialogTTK

        # 检查继承关系
        assert issubclass(TaskEditDialogTTK, BaseDialogTTK), (
            "TaskEditDialogTTK 应该继承 BaseDialogTTK"
        )
        print("✓ TaskEditDialogTTK 正确继承 BaseDialogTTK")

        assert issubclass(ContractExportDialogTTK, BaseDialogTTK), (
            "ContractExportDialogTTK 应该继承 BaseDialogTTK"
        )
        print("✓ ContractExportDialogTTK 正确继承 BaseDialogTTK")

        (
            assss(SuppliialogTTK, BaseDialogTTK),
            "SupplierEditDialogTTK 应该继承 BaseDialogTTK",
        )
        print("✓ SupplierEditDialogTTK 正确继承 BaseDialogTTK")

        root.destroy()
        return True

    except Exception as e:
        print(f"✗ 继承关系检查失败: {e}")
        return False


def main():
    """主测试函数"""
    print("开始TTK对话框测试...")
    print("=" * 50)

    # 测试导入
    if not test_imports():
        return False

    print()

    # 测试对话框创建
    if not test_dialog_creation():
        return False

    print()

    # 测试继承关系
    if not test_base_dialog_inheritance():
        return False

    print()
    print("=" * 50)
    print("✓ 所有测试通过！TTK对话框迁移成功完成")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
