"""跨平台兼容性测试.

测试MiniCRM应用程序在不同操作系统和环境下的兼容性。
验证资源加载、路径处理、字体显示等跨平台功能。
"""

import os
from pathlib import Path
import platform
import sys
import tempfile
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import patch


# 添加src目录到Python路径
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from minicrm.core.exceptions import MiniCRMError
from minicrm.core.resource_manager import ResourceManager


class TestCrossPlatformCompatibility(unittest.TestCase):
    """跨平台兼容性测试类."""

    def setUp(self):
        """测试准备."""
        self.platform = platform.system().lower()
        self.architecture = platform.machine().lower()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

        # 创建测试用的tkinter根窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏窗口

    def tearDown(self):
        """测试清理."""
        if hasattr(self, "root"):
            self.root.destroy()

    def test_platform_detection(self):
        """测试平台检测功能."""
        # 验证平台检测
        self.assertIn(self.platform, ["windows", "darwin", "linux"])

        # 验证架构检测
        self.assertIsInstance(self.architecture, str)
        self.assertGreater(len(self.architecture), 0)

        print(f"检测到平台: {self.platform}")
        print(f"检测到架构: {self.architecture}")
        print(f"Python版本: {self.python_version}")

    def test_resource_manager_initialization(self):
        """测试资源管理器初始化."""
        resource_manager = ResourceManager()

        # 验证基本属性
        self.assertIsInstance(resource_manager.base_path, Path)
        self.assertIsInstance(resource_manager.resource_path, Path)
        self.assertEqual(resource_manager.platform, self.platform)

        # 验证路径存在性
        self.assertTrue(resource_manager.base_path.exists())

    def test_path_handling(self):
        """测试路径处理功能."""
        resource_manager = ResourceManager()

        # 测试不同类型的路径
        test_paths = [
            "test_icon.png",
            "test_theme.json",
            "test_template.docx",
            "test_style.css",
        ]

        for path_name in test_paths:
            # 验证路径处理不会抛出异常
            try:
                if "icon" in path_name:
                    resource_manager.get_icon_path(path_name)
                elif "theme" in path_name:
                    resource_manager.get_theme_path(path_name.replace(".json", ""))
                elif "template" in path_name:
                    resource_manager.get_template_path(path_name)
                elif "style" in path_name:
                    resource_manager.get_style_path(path_name.replace(".css", ""))
            except Exception as e:
                # 资源不存在是正常的，但不应该有其他类型的错误
                self.assertIsInstance(e, (FileNotFoundError, MiniCRMError))

    def test_tkinter_compatibility(self):
        """测试tkinter兼容性."""
        # 测试基本tkinter功能
        frame = ttk.Frame(self.root)
        self.assertIsInstance(frame, ttk.Frame)

        # 测试常用组件
        components = [
            ttk.Label(frame, text="测试标签"),
            ttk.Button(frame, text="测试按钮"),
            ttk.Entry(frame),
            ttk.Combobox(frame),
            ttk.Treeview(frame),
            ttk.Progressbar(frame),
            ttk.Notebook(frame),
            ttk.PanedWindow(frame),
        ]

        for component in components:
            self.assertIsNotNone(component)
            # 验证组件可以正常配置
            try:
                component.configure(state="normal")
            except tk.TclError:
                # 某些组件可能不支持state配置，这是正常的
                pass

    def test_font_handling(self):
        """测试字体处理."""
        # 测试系统字体
        label = ttk.Label(self.root, text="测试中文字体显示")

        # 测试不同平台的默认字体
        platform_fonts = {
            "windows": ["Microsoft YaHei UI", "SimSun", "Arial"],
            "darwin": ["PingFang SC", "Helvetica Neue", "Arial"],
            "linux": ["DejaVu Sans", "Liberation Sans", "Arial"],
        }

        fonts_to_test = platform_fonts.get(self.platform, ["Arial"])

        for font_name in fonts_to_test:
            try:
                label.configure(font=(font_name, 12))
                # 如果没有抛出异常，说明字体可用
                print(f"字体 {font_name} 在 {self.platform} 平台可用")
                break
            except tk.TclError:
                continue
        else:
            # 如果所有字体都不可用，使用默认字体
            label.configure(font=("TkDefaultFont", 12))

    def test_file_system_operations(self):
        """测试文件系统操作."""
        # 创建临时目录进行测试
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 测试文件创建
            test_file = temp_path / "test_file.txt"
            test_file.write_text("测试内容", encoding="utf-8")
            self.assertTrue(test_file.exists())

            # 测试文件读取
            content = test_file.read_text(encoding="utf-8")
            self.assertEqual(content, "测试内容")

            # 测试目录创建
            test_dir = temp_path / "test_dir"
            test_dir.mkdir()
            self.assertTrue(test_dir.exists())
            self.assertTrue(test_dir.is_dir())

    def test_encoding_handling(self):
        """测试编码处理."""
        # 测试中文字符处理
        chinese_text = "MiniCRM板材行业客户关系管理系统"

        # 测试字符串编码/解码
        encoded = chinese_text.encode("utf-8")
        decoded = encoded.decode("utf-8")
        self.assertEqual(chinese_text, decoded)

        # 测试在tkinter中显示中文
        label = ttk.Label(self.root, text=chinese_text)
        self.assertEqual(label.cget("text"), chinese_text)

    def test_environment_variables(self):
        """测试环境变量处理."""
        # 测试常见环境变量
        env_vars = ["PATH", "HOME", "USER", "USERNAME", "USERPROFILE"]

        available_vars = []
        for var in env_vars:
            if var in os.environ:
                available_vars.append(var)

        # 至少应该有一个环境变量可用
        self.assertGreater(len(available_vars), 0)
        print(f"可用环境变量: {available_vars}")

    def test_pyinstaller_compatibility(self):
        """测试PyInstaller兼容性."""
        # 模拟PyInstaller环境
        with patch.object(sys, "_MEIPASS", "/fake/meipass/path", create=True):
            resource_manager = ResourceManager()

            # 验证在PyInstaller环境下的路径处理
            self.assertTrue(hasattr(sys, "_MEIPASS"))
            self.assertIn("fake", str(resource_manager.base_path))

    def test_memory_usage(self):
        """测试内存使用情况."""
        import psutil

        # 获取当前进程
        process = psutil.Process()

        # 记录初始内存使用
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 创建一些组件
        components = []
        for i in range(100):
            frame = ttk.Frame(self.root)
            label = ttk.Label(frame, text=f"测试标签 {i}")
            components.append((frame, label))

        # 记录创建组件后的内存使用
        after_creation_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 清理组件
        for frame, label in components:
            label.destroy()
            frame.destroy()

        # 记录清理后的内存使用
        after_cleanup_memory = process.memory_info().rss / 1024 / 1024  # MB

        print(f"初始内存: {initial_memory:.2f} MB")
        print(f"创建组件后内存: {after_creation_memory:.2f} MB")
        print(f"清理后内存: {after_cleanup_memory:.2f} MB")

        # 验证内存使用合理
        memory_increase = after_creation_memory - initial_memory
        self.assertLess(memory_increase, 100)  # 不应该增加超过100MB

    def test_performance_baseline(self):
        """测试性能基准."""
        import time

        # 测试组件创建性能
        start_time = time.time()

        for i in range(1000):
            label = ttk.Label(self.root, text=f"性能测试 {i}")
            label.destroy()

        end_time = time.time()
        creation_time = end_time - start_time

        print(f"创建1000个标签耗时: {creation_time:.3f} 秒")

        # 验证性能在合理范围内
        self.assertLess(creation_time, 5.0)  # 不应该超过5秒

    @unittest.skipIf(platform.system() == "Darwin", "macOS特定测试")
    def test_non_macos_specific(self):
        """非macOS平台特定测试."""
        # 这里可以添加非macOS平台的特定测试

    @unittest.skipIf(platform.system() == "Windows", "Windows特定测试")
    def test_non_windows_specific(self):
        """非Windows平台特定测试."""
        # 这里可以添加非Windows平台的特定测试

    @unittest.skipIf(platform.system() == "Linux", "Linux特定测试")
    def test_non_linux_specific(self):
        """非Linux平台特定测试."""
        # 这里可以添加非Linux平台的特定测试


class TestPlatformSpecificFeatures(unittest.TestCase):
    """平台特定功能测试."""

    def setUp(self):
        """测试准备."""
        self.platform = platform.system().lower()

    @unittest.skipUnless(platform.system() == "Windows", "需要Windows平台")
    def test_windows_specific_features(self):
        """Windows平台特定功能测试."""
        # 测试Windows路径处理
        import os

        self.assertTrue(os.path.sep == "\\")

        # 测试Windows注册表访问（如果需要）
        try:
            import winreg
            # 可以添加注册表相关测试
        except ImportError:
            self.skipTest("winreg模块不可用")

    @unittest.skipUnless(platform.system() == "Darwin", "需要macOS平台")
    def test_macos_specific_features(self):
        """macOS平台特定功能测试."""
        # 测试macOS路径处理
        import os

        self.assertTrue(os.path.sep == "/")

        # 测试macOS特定的文件系统功能
        home_dir = Path.home()
        self.assertTrue(home_dir.exists())

        # 测试应用程序包结构
        if hasattr(sys, "_MEIPASS"):
            # 在打包环境中测试
            pass

    @unittest.skipUnless(platform.system() == "Linux", "需要Linux平台")
    def test_linux_specific_features(self):
        """Linux平台特定功能测试."""
        # 测试Linux路径处理
        import os

        self.assertTrue(os.path.sep == "/")

        # 测试Linux桌面环境
        desktop_env = os.environ.get("DESKTOP_SESSION", "")
        print(f"桌面环境: {desktop_env}")

        # 测试X11显示
        display = os.environ.get("DISPLAY", "")
        if display:
            print(f"X11显示: {display}")


def run_compatibility_tests():
    """运行兼容性测试套件."""
    # 创建测试套件
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTest(unittest.makeSuite(TestCrossPlatformCompatibility))
    suite.addTest(unittest.makeSuite(TestPlatformSpecificFeatures))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    print(f"在 {platform.system()} {platform.release()} 平台运行跨平台兼容性测试")
    print(f"Python版本: {sys.version}")
    print("=" * 60)

    success = run_compatibility_tests()

    print("=" * 60)
    if success:
        print("✅ 所有兼容性测试通过")
    else:
        print("❌ 部分兼容性测试失败")

    sys.exit(0 if success else 1)
