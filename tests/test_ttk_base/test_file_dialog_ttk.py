"""测试TTK文件对话框

测试FileDialogTTK类的功能，包括：
- 文件对话框创建和显示
- 文件选择、保存、目录选择模式
- 文件类型筛选
- 路径导航功能
- 多文件选择
- 便利函数

作者: MiniCRM开发团队
"""

import os
import shutil
import tempfile
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from src.minicrm.ui.ttk_base.file_dialog_ttk import (
    FileDialogMode,
    FileDialogTTK,
    open_file_dialog,
    open_multiple_files_dialog,
    save_file_dialog,
    select_directory_dialog,
)


class TestFileDialogTTK(unittest.TestCase):
    """测试FileDialogTTK类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口

        # 创建临时测试目录
        self.test_dir = tempfile.mkdtemp()

        # 创建测试文件和目录
        self.test_files = ["test1.txt", "test2.py", "test3.jpg"]
        self.test_dirs = ["subdir1", "subdir2"]

        for filename in self.test_files:
            with open(os.path.join(self.test_dir, filename), "w") as f:
                f.write("test content")

        for dirname in self.test_dirs:
            os.makedirs(os.path.join(self.test_dir, dirname))

    def tearDown(self):
        """测试清理"""
        try:
            shutil.rmtree(self.test_dir)
            self.root.destroy()
        except:
            pass

    def test_open_file_dialog_creation(self):
        """测试打开文件对话框创建"""
        dialog = FileDialogTTK(
            parent=self.root,
            title="打开文件",
            mode=FileDialogMode.OPEN_FILE,
            initial_dir=self.test_dir,
            file_types=[("文本文件", "*.txt"), ("所有文件", "*.*")],
        )

        # 验证基本属性
        self.assertEqual(dialog.mode, FileDialogMode.OPEN_FILE)
        self.assertEqual(dialog.current_dir, self.test_dir)
        self.assertEqual(len(dialog.file_types), 2)

        # 验证UI组件
        self.assertIsNotNone(dialog.path_frame)
        self.assertIsNotNone(dialog.file_frame)
        self.assertIsNotNone(dialog.filter_frame)
        self.assertIsNotNone(dialog.name_frame)
        self.assertIsNotNone(dialog.file_tree)

        # 验证按钮
        self.assertIn("打开", dialog.buttons)
        self.assertIn("取消", dialog.buttons)

        dialog.destroy()

    def test_save_file_dialog_creation(self):
        """测试保存文件对话框创建"""
        dialog = FileDialogTTK(
            parent=self.root,
            mode=FileDialogMode.SAVE_FILE,
            initial_dir=self.test_dir,
            initial_file="new_file.txt",
            default_extension=".txt",
        )

        # 验证属性
        self.assertEqual(dialog.mode, FileDialogMode.SAVE_FILE)
        self.assertEqual(dialog.initial_file, "new_file.txt")
        self.assertEqual(dialog.default_extension, ".txt")

        # 验证按钮
        self.assertIn("保存", dialog.buttons)

        dialog.destroy()

    def test_select_directory_dialog_creation(self):
        """测试选择目录对话框创建"""
        dialog = FileDialogTTK(
            parent=self.root,
            mode=FileDialogMode.SELECT_DIRECTORY,
            initial_dir=self.test_dir,
        )

        # 验证属性
        self.assertEqual(dialog.mode, FileDialogMode.SELECT_DIRECTORY)

        # 验证UI组件（目录选择模式不应该有文件类型筛选和文件名输入）
        self.assertIsNone(dialog.filter_frame)
        self.assertIsNone(dialog.name_frame)

        # 验证按钮
        self.assertIn("选择", dialog.buttons)

        dialog.destroy()

    def test_multiple_file_selection(self):
        """测试多文件选择"""
        dialog = FileDialogTTK(
            parent=self.root,
            mode=FileDialogMode.OPEN_MULTIPLE,
            initial_dir=self.test_dir,
            multiple_selection=True,
        )

        # 验证属性
        self.assertTrue(dialog.multiple_selection)
        self.assertEqual(dialog.file_tree.cget("selectmode"), "extended")

        dialog.destroy()

    def test_file_list_refresh(self):
        """测试文件列表刷新"""
        dialog = FileDialogTTK(parent=self.root, initial_dir=self.test_dir)

        # 刷新文件列表
        dialog._refresh_file_list()

        # 验证文件和目录被加载
        items = dialog.file_tree.get_children()
        self.assertGreater(len(items), 0)

        # 检查是否包含测试文件和目录
        item_texts = []
        for item in items:
            text = dialog.file_tree.item(item)["text"]
            item_texts.append(text)

        # 应该包含目录（带📁图标）
        dir_items = [text for text in item_texts if text.startswith("📁")]
        self.assertGreater(len(dir_items), 0)

        # 应该包含文件（带📄图标）
        file_items = [text for text in item_texts if text.startswith("📄")]
        self.assertGreater(len(file_items), 0)

        dialog.destroy()

    def test_file_type_filtering(self):
        """测试文件类型筛选"""
        dialog = FileDialogTTK(
            parent=self.root,
            initial_dir=self.test_dir,
            file_types=[("文本文件", "*.txt"), ("Python文件", "*.py")],
        )

        # 测试显示txt文件
        dialog.filter_combo.current(0)  # 选择文本文件
        dialog._on_filter_changed()

        # 验证筛选结果
        items = dialog.file_tree.get_children()
        file_items = []
        for item in items:
            text = dialog.file_tree.item(item)["text"]
            if text.startswith("📄"):
                filename = text[2:]  # 移除图标
                file_items.append(filename)

        # 应该只显示txt文件
        txt_files = [f for f in file_items if f.endswith(".txt")]
        self.assertGreater(len(txt_files), 0)

        dialog.destroy()

    def test_path_navigation(self):
        """测试路径导航"""
        dialog = FileDialogTTK(parent=self.root, initial_dir=self.test_dir)

        original_dir = dialog.current_dir

        # 测试上级目录
        dialog._go_up_directory()
        self.assertNotEqual(dialog.current_dir, original_dir)

        # 测试主目录
        dialog._go_home_directory()
        self.assertEqual(dialog.current_dir, os.path.expanduser("~"))

        dialog.destroy()

    def test_path_entry_navigation(self):
        """测试路径输入框导航"""
        dialog = FileDialogTTK(parent=self.root, initial_dir=self.test_dir)

        # 测试有效路径
        new_path = os.path.dirname(self.test_dir)
        dialog.path_var.set(new_path)
        dialog._on_path_changed()

        self.assertEqual(dialog.current_dir, os.path.abspath(new_path))

        # 测试无效路径
        with patch.object(dialog, "show_error") as mock_error:
            dialog.path_var.set("/nonexistent/path")
            dialog._on_path_changed()
            mock_error.assert_called()

        dialog.destroy()

    def test_file_selection_handling(self):
        """测试文件选择处理"""
        dialog = FileDialogTTK(parent=self.root, initial_dir=self.test_dir)

        # 刷新文件列表
        dialog._refresh_file_list()

        # 模拟选择文件
        items = dialog.file_tree.get_children()
        if items:
            # 选择第一个文件项
            for item in items:
                text = dialog.file_tree.item(item)["text"]
                if text.startswith("📄"):
                    dialog.file_tree.selection_set(item)
                    dialog._on_file_select()

                    # 验证文件名被设置
                    filename = text[2:]  # 移除图标
                    self.assertEqual(dialog.name_var.get(), filename)
                    break

        dialog.destroy()

    def test_directory_double_click(self):
        """测试目录双击进入"""
        dialog = FileDialogTTK(parent=self.root, initial_dir=self.test_dir)

        # 刷新文件列表
        dialog._refresh_file_list()

        original_dir = dialog.current_dir

        # 模拟双击目录
        items = dialog.file_tree.get_children()
        for item in items:
            text = dialog.file_tree.item(item)["text"]
            if text.startswith("📁"):
                dialog.file_tree.selection_set(item)
                dialog._on_file_double_click()

                # 验证进入了子目录
                self.assertNotEqual(dialog.current_dir, original_dir)
                break

        dialog.destroy()

    def test_save_file_validation(self):
        """测试保存文件验证"""
        dialog = FileDialogTTK(
            parent=self.root,
            mode=FileDialogMode.SAVE_FILE,
            initial_dir=self.test_dir,
            default_extension=".txt",
        )

        # 测试空文件名
        dialog.name_var.set("")
        with patch.object(dialog, "show_error") as mock_error:
            result = dialog._validate_input()
            self.assertFalse(result)
            mock_error.assert_called()

        # 测试有效文件名
        dialog.name_var.set("new_file")
        result = dialog._validate_input()
        self.assertTrue(result)

        # 验证默认扩展名被添加
        self.assertEqual(dialog.name_var.get(), "new_file.txt")

        dialog.destroy()

    def test_open_file_validation(self):
        """测试打开文件验证"""
        dialog = FileDialogTTK(
            parent=self.root, mode=FileDialogMode.OPEN_FILE, initial_dir=self.test_dir
        )

        # 测试空文件名
        dialog.name_var.set("")
        with patch.object(dialog, "show_error") as mock_error:
            result = dialog._validate_input()
            self.assertFalse(result)
            mock_error.assert_called()

        # 测试不存在的文件
        dialog.name_var.set("nonexistent.txt")
        with patch.object(dialog, "show_error") as mock_error:
            result = dialog._validate_input()
            self.assertFalse(result)
            mock_error.assert_called()

        # 测试存在的文件
        dialog.name_var.set("test1.txt")
        result = dialog._validate_input()
        self.assertTrue(result)

        dialog.destroy()

    def test_directory_selection_validation(self):
        """测试目录选择验证"""
        dialog = FileDialogTTK(
            parent=self.root,
            mode=FileDialogMode.SELECT_DIRECTORY,
            initial_dir=self.test_dir,
        )

        # 测试空目录名
        dialog.name_var.set("")
        with patch.object(dialog, "show_error") as mock_error:
            result = dialog._validate_input()
            self.assertFalse(result)
            mock_error.assert_called()

        # 测试有效目录
        dialog.name_var.set("subdir1")
        result = dialog._validate_input()
        self.assertTrue(result)

        dialog.destroy()

    def test_file_overwrite_confirmation(self):
        """测试文件覆盖确认"""
        dialog = FileDialogTTK(
            parent=self.root, mode=FileDialogMode.SAVE_FILE, initial_dir=self.test_dir
        )

        # 测试覆盖现有文件 - 用户确认
        dialog.name_var.set("test1.txt")
        with patch.object(dialog, "confirm", return_value=True):
            result = dialog._validate_input()
            self.assertTrue(result)

        # 测试覆盖现有文件 - 用户拒绝
        dialog.name_var.set("test1.txt")
        with patch.object(dialog, "confirm", return_value=False):
            result = dialog._validate_input()
            self.assertFalse(result)

        dialog.destroy()

    def test_result_data_generation(self):
        """测试结果数据生成"""
        # 测试单文件选择
        dialog = FileDialogTTK(
            parent=self.root, mode=FileDialogMode.OPEN_FILE, initial_dir=self.test_dir
        )
        dialog.name_var.set("test1.txt")

        result_data = dialog._get_result_data()
        expected_path = os.path.join(self.test_dir, "test1.txt")
        self.assertEqual(result_data, expected_path)

        dialog.destroy()

        # 测试目录选择
        dialog = FileDialogTTK(
            parent=self.root,
            mode=FileDialogMode.SELECT_DIRECTORY,
            initial_dir=self.test_dir,
        )
        dialog.name_var.set("subdir1")

        result_data = dialog._get_result_data()
        expected_path = os.path.join(self.test_dir, "subdir1")
        self.assertEqual(result_data, expected_path)

        dialog.destroy()

    def test_file_size_formatting(self):
        """测试文件大小格式化"""
        dialog = FileDialogTTK(parent=self.root)

        # 测试不同大小的格式化
        self.assertEqual(dialog._format_size(500), "500 B")
        self.assertEqual(dialog._format_size(1536), "1.5 KB")
        self.assertEqual(dialog._format_size(1572864), "1.5 MB")
        self.assertEqual(dialog._format_size(1610612736), "1.5 GB")

        dialog.destroy()

    def test_hidden_files_handling(self):
        """测试隐藏文件处理"""
        # 创建隐藏文件
        hidden_file = os.path.join(self.test_dir, ".hidden_file")
        with open(hidden_file, "w") as f:
            f.write("hidden content")

        # 测试不显示隐藏文件
        dialog = FileDialogTTK(
            parent=self.root, initial_dir=self.test_dir, show_hidden=False
        )
        dialog._refresh_file_list()

        items = dialog.file_tree.get_children()
        item_texts = [dialog.file_tree.item(item)["text"] for item in items]
        hidden_items = [text for text in item_texts if ".hidden_file" in text]
        self.assertEqual(len(hidden_items), 0)

        dialog.destroy()

        # 测试显示隐藏文件
        dialog = FileDialogTTK(
            parent=self.root, initial_dir=self.test_dir, show_hidden=True
        )
        dialog._refresh_file_list()

        items = dialog.file_tree.get_children()
        item_texts = [dialog.file_tree.item(item)["text"] for item in items]
        hidden_items = [text for text in item_texts if ".hidden_file" in text]
        self.assertGreater(len(hidden_items), 0)

        dialog.destroy()


class TestFileDialogConvenienceFunctions(unittest.TestCase):
    """测试文件对话框便利函数"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """测试清理"""
        try:
            self.root.destroy()
        except:
            pass

    def test_open_file_dialog_function(self):
        """测试open_file_dialog函数"""
        with patch(
            "src.minicrm.ui.ttk_base.file_dialog_ttk.FileDialogTTK"
        ) as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.show_dialog.return_value = ("ok", "/path/to/file.txt")
            mock_dialog_class.return_value = mock_dialog

            result = open_file_dialog(
                parent=self.root, title="测试打开", file_types=[("文本文件", "*.txt")]
            )

            # 验证对话框被创建
            mock_dialog_class.assert_called_once()

            # 验证返回结果
            self.assertEqual(result, "/path/to/file.txt")

    def test_save_file_dialog_function(self):
        """测试save_file_dialog函数"""
        with patch(
            "src.minicrm.ui.ttk_base.file_dialog_ttk.FileDialogTTK"
        ) as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.show_dialog.return_value = ("ok", "/path/to/save.txt")
            mock_dialog_class.return_value = mock_dialog

            result = save_file_dialog(
                parent=self.root,
                title="测试保存",
                initial_file="test.txt",
                default_extension=".txt",
            )

            # 验证对话框被创建
            mock_dialog_class.assert_called_once()

            # 验证返回结果
            self.assertEqual(result, "/path/to/save.txt")

    def test_select_directory_dialog_function(self):
        """测试select_directory_dialog函数"""
        with patch(
            "src.minicrm.ui.ttk_base.file_dialog_ttk.FileDialogTTK"
        ) as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.show_dialog.return_value = ("ok", "/path/to/directory")
            mock_dialog_class.return_value = mock_dialog

            result = select_directory_dialog(parent=self.root, title="选择目录")

            # 验证对话框被创建
            mock_dialog_class.assert_called_once()

            # 验证返回结果
            self.assertEqual(result, "/path/to/directory")

    def test_open_multiple_files_dialog_function(self):
        """测试open_multiple_files_dialog函数"""
        with patch(
            "src.minicrm.ui.ttk_base.file_dialog_ttk.FileDialogTTK"
        ) as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.show_dialog.return_value = (
                "ok",
                ["/path/to/file1.txt", "/path/to/file2.txt"],
            )
            mock_dialog_class.return_value = mock_dialog

            result = open_multiple_files_dialog(parent=self.root, title="选择多个文件")

            # 验证对话框被创建
            mock_dialog_class.assert_called_once()

            # 验证返回结果
            self.assertEqual(len(result), 2)
            self.assertIn("/path/to/file1.txt", result)
            self.assertIn("/path/to/file2.txt", result)

    def test_cancelled_dialog_functions(self):
        """测试取消对话框的便利函数"""
        with patch(
            "src.minicrm.ui.ttk_base.file_dialog_ttk.FileDialogTTK"
        ) as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.show_dialog.return_value = ("cancel", None)
            mock_dialog_class.return_value = mock_dialog

            # 测试取消的情况
            result = open_file_dialog(self.root)
            self.assertIsNone(result)

            result = save_file_dialog(self.root)
            self.assertIsNone(result)

            result = select_directory_dialog(self.root)
            self.assertIsNone(result)

            result = open_multiple_files_dialog(self.root)
            self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
