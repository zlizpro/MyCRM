"""测试对话框模块导入

简单的导入测试，验证所有对话框模块可以正常导入，
不依赖GUI环境，适合CI/CD环境运行。

作者: MiniCRM开发团队
"""

import os
import sys
import unittest


# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestDialogsImport(unittest.TestCase):
    """测试对话框模块导入"""

    def test_base_dialog_import(self):
        """测试基础对话框导入"""
        try:
            from src.minicrm.ui.ttk_base.base_dialog import BaseDialogTTK, DialogResult

            self.assertTrue(hasattr(BaseDialogTTK, "_setup_content"))
            self.assertTrue(hasattr(DialogResult, "OK"))
        except ImportError as e:
            self.fail(f"基础对话框导入失败: {e}")

    def test_progress_dialog_import(self):
        """测试进度对话框导入"""
        try:
            from src.minicrm.ui.ttk_base.progress_dialog_ttk import (
                ProgressDialogTTK,
                ProgressTask,
                ProgressUpdater,
            )

            self.assertTrue(hasattr(ProgressDialogTTK, "set_progress"))
            self.assertTrue(hasattr(ProgressTask, "start"))
            self.assertTrue(hasattr(ProgressUpdater, "update_progress"))
        except ImportError as e:
            self.fail(f"进度对话框导入失败: {e}")

    def test_file_dialog_import(self):
        """测试文件对话框导入"""
        try:
            from src.minicrm.ui.ttk_base.file_dialog_ttk import (
                FileDialogMode,
                FileDialogTTK,
            )

            self.assertTrue(hasattr(FileDialogTTK, "_refresh_file_list"))
            self.assertTrue(hasattr(FileDialogMode, "OPEN_FILE"))
        except ImportError as e:
            self.fail(f"文件对话框导入失败: {e}")

    def test_message_dialogs_import(self):
        """测试消息对话框导入"""
        try:
            from src.minicrm.ui.ttk_base.message_dialogs_ttk import (
                ConfirmDialogTTK,
                InputDialogTTK,
                MessageBoxTTK,
                MessageType,
            )

            # MessageBoxTTK实例才有message_type属性，类本身没有
            # 验证类有正确的方法
            self.assertTrue(hasattr(MessageBoxTTK, "_setup_content"))
            self.assertTrue(hasattr(ConfirmDialogTTK, "_on_confirm"))
            self.assertTrue(hasattr(InputDialogTTK, "get_input_value"))
            self.assertTrue(hasattr(MessageType, "INFO"))
        except ImportError as e:
            self.fail(f"消息对话框导入失败: {e}")

    def test_unified_dialogs_import(self):
        """测试统一对话框接口导入"""
        try:
            from src.minicrm.ui.ttk_base.dialogs import (
                BaseDialogTTK,
                ConfirmDialogTTK,
                DialogResult,
                FileDialogTTK,
                InputDialogTTK,
                MessageBoxTTK,
                ProgressDialogTTK,
                confirm,
                get_input,
                get_multiline_input,
                get_password,
                open_file_dialog,
                save_file_dialog,
                select_directory_dialog,
                show_error,
                show_info,
                show_progress_dialog,
                show_success,
                show_warning,
            )

            # 验证所有主要类都被导入
            self.assertIsNotNone(BaseDialogTTK)
            self.assertIsNotNone(MessageBoxTTK)
            self.assertIsNotNone(ConfirmDialogTTK)
            self.assertIsNotNone(InputDialogTTK)
            self.assertIsNotNone(ProgressDialogTTK)
            self.assertIsNotNone(FileDialogTTK)

            # 验证所有便利函数都被导入
            self.assertTrue(callable(show_info))
            self.assertTrue(callable(confirm))
            self.assertTrue(callable(get_input))
            self.assertTrue(callable(open_file_dialog))
            self.assertTrue(callable(show_progress_dialog))

        except ImportError as e:
            self.fail(f"统一对话框接口导入失败: {e}")

    def test_convenience_functions_import(self):
        """测试便利函数导入"""
        try:
            from src.minicrm.ui.ttk_base.file_dialog_ttk import (
                open_file_dialog,
                open_multiple_files_dialog,
                save_file_dialog,
                select_directory_dialog,
            )
            from src.minicrm.ui.ttk_base.message_dialogs_ttk import (
                confirm,
                get_input,
                get_multiline_input,
                get_password,
                show_error,
                show_info,
                show_message,
                show_success,
                show_warning,
            )
            from src.minicrm.ui.ttk_base.progress_dialog_ttk import show_progress_dialog

            # 验证所有便利函数都是可调用的
            convenience_functions = [
                show_message,
                show_info,
                show_warning,
                show_error,
                show_success,
                confirm,
                get_input,
                get_password,
                get_multiline_input,
                open_file_dialog,
                save_file_dialog,
                select_directory_dialog,
                open_multiple_files_dialog,
                show_progress_dialog,
            ]

            for func in convenience_functions:
                self.assertTrue(callable(func), f"{func.__name__} 不是可调用的")

        except ImportError as e:
            self.fail(f"便利函数导入失败: {e}")

    def test_module_attributes(self):
        """测试模块属性"""
        try:
            from src.minicrm.ui.ttk_base import dialogs

            # 验证模块有版本信息
            self.assertTrue(hasattr(dialogs, "__version__"))
            self.assertTrue(hasattr(dialogs, "__author__"))
            self.assertTrue(hasattr(dialogs, "__description__"))

            # 验证模块有便利函数
            self.assertTrue(hasattr(dialogs, "get_version"))
            self.assertTrue(hasattr(dialogs, "get_available_dialogs"))

            # 验证快捷别名
            self.assertTrue(hasattr(dialogs, "info"))
            self.assertTrue(hasattr(dialogs, "warning"))
            self.assertTrue(hasattr(dialogs, "error"))
            self.assertTrue(hasattr(dialogs, "success"))
            self.assertTrue(hasattr(dialogs, "ask"))

        except ImportError as e:
            self.fail(f"模块属性测试失败: {e}")

    def test_class_inheritance(self):
        """测试类继承关系"""
        try:
            from src.minicrm.ui.ttk_base.base_dialog import BaseDialogTTK
            from src.minicrm.ui.ttk_base.file_dialog_ttk import FileDialogTTK
            from src.minicrm.ui.ttk_base.message_dialogs_ttk import MessageBoxTTK
            from src.minicrm.ui.ttk_base.progress_dialog_ttk import ProgressDialogTTK

            # 验证继承关系（不实例化，只检查类关系）
            self.assertTrue(issubclass(MessageBoxTTK, BaseDialogTTK))
            self.assertTrue(issubclass(ProgressDialogTTK, BaseDialogTTK))
            self.assertTrue(issubclass(FileDialogTTK, BaseDialogTTK))

        except ImportError as e:
            self.fail(f"类继承关系测试失败: {e}")

    def test_constants_and_enums(self):
        """测试常量和枚举"""
        try:
            from src.minicrm.ui.ttk_base.base_dialog import DialogResult
            from src.minicrm.ui.ttk_base.file_dialog_ttk import FileDialogMode
            from src.minicrm.ui.ttk_base.message_dialogs_ttk import MessageType

            # 验证DialogResult常量
            self.assertEqual(DialogResult.OK, "ok")
            self.assertEqual(DialogResult.CANCEL, "cancel")
            self.assertEqual(DialogResult.YES, "yes")
            self.assertEqual(DialogResult.NO, "no")

            # 验证MessageType常量
            self.assertEqual(MessageType.INFO, "info")
            self.assertEqual(MessageType.WARNING, "warning")
            self.assertEqual(MessageType.ERROR, "error")
            self.assertEqual(MessageType.SUCCESS, "success")

            # 验证FileDialogMode常量
            self.assertEqual(FileDialogMode.OPEN_FILE, "open_file")
            self.assertEqual(FileDialogMode.SAVE_FILE, "save_file")
            self.assertEqual(FileDialogMode.SELECT_DIRECTORY, "select_directory")

        except ImportError as e:
            self.fail(f"常量和枚举测试失败: {e}")


if __name__ == "__main__":
    # 运行导入测试
    unittest.main(verbosity=2)
