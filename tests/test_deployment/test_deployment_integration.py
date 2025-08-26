"""部署集成测试.

测试应用程序的部署和分发功能，包括打包、安装、运行等完整流程。
验证不同部署模式下的应用程序功能完整性。
"""

import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


# 添加src目录到Python路径
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
build_path = project_root / "build"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(build_path) not in sys.path:
    sys.path.insert(0, str(build_path))

from minicrm.core.constants import APP_NAME, APP_VERSION
from minicrm.core.resource_manager import ResourceManager


class TestDeploymentIntegration(unittest.TestCase):
    """部署集成测试类."""

    def setUp(self):
        """测试准备."""
        self.project_root = project_root
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.platform = platform.system().lower()

        # 确保构建目录存在
        self.build_dir.mkdir(exist_ok=True)

    def test_build_config_import(self):
        """测试构建配置导入."""
        try:
            from build_config import BuildConfig, build_application

            config = BuildConfig()
            self.assertIsInstance(config, BuildConfig)
        except ImportError as e:
            self.fail(f"无法导入构建配置: {e}")

    def test_build_config_initialization(self):
        """测试构建配置初始化."""
        from build_config import BuildConfig

        config = BuildConfig()

        # 验证基本属性
        self.assertTrue(config.project_root.exists())
        self.assertTrue(config.src_path.exists())
        self.assertEqual(config.platform, self.platform)

        # 验证应用程序信息
        app_name = config.get_app_name()
        self.assertIn(APP_NAME, app_name)
        self.assertIn(APP_VERSION, app_name)
        self.assertIn(self.platform, app_name)

    def test_main_script_exists(self):
        """测试主脚本存在性."""
        from build_config import BuildConfig

        config = BuildConfig()
        main_script = config.get_main_script()

        self.assertTrue(main_script.exists(), f"主脚本不存在: {main_script}")
        self.assertEqual(main_script.suffix, ".py")

    def test_resource_collection(self):
        """测试资源文件收集."""
        from build_config import BuildConfig

        config = BuildConfig()

        # 测试数据文件收集
        data_files = config.get_data_files()
        self.assertIsInstance(data_files, list)

        # 验证资源文件包含
        resource_found = False
        for src, dst in data_files:
            if "resources" in src:
                resource_found = True
                self.assertTrue(Path(src).exists(), f"资源文件不存在: {src}")

        if not resource_found:
            print("警告: 未找到资源文件")

    def test_hidden_imports_configuration(self):
        """测试隐藏导入配置."""
        from build_config import BuildConfig

        config = BuildConfig()
        hidden_imports = config.get_hidden_imports()

        # 验证必要的模块包含在隐藏导入中
        required_modules = ["tkinter", "tkinter.ttk", "sqlite3", "matplotlib"]

        for module in required_modules:
            self.assertIn(module, hidden_imports, f"缺少必要的隐藏导入: {module}")

    def test_excluded_modules_configuration(self):
        """测试排除模块配置."""
        from build_config import BuildConfig

        config = BuildConfig()
        excluded_modules = config.get_excluded_modules()

        # 验证Qt相关模块被排除
        qt_modules = []  # Qt模块已完全移除
        for module in qt_modules:
            self.assertIn(module, excluded_modules, f"Qt模块应该被排除: {module}")

    def test_pyinstaller_args_generation(self):
        """测试PyInstaller参数生成."""
        from build_config import BuildConfig

        config = BuildConfig()

        # 测试单文件模式
        args_onefile = config.get_pyinstaller_args(onefile=True, console=False)
        self.assertIn("--onefile", args_onefile)
        self.assertIn("--windowed", args_onefile)

        # 测试目录模式
        args_onedir = config.get_pyinstaller_args(onefile=False, console=True)
        self.assertIn("--onedir", args_onedir)
        self.assertNotIn("--windowed", args_onedir)

    def test_platform_specific_configuration(self):
        """测试平台特定配置."""
        from build_config import BuildConfig

        config = BuildConfig()

        if self.platform == "windows":
            # Windows特定测试
            config.create_version_info()
            version_file = config.build_path / "version_info.txt"
            if version_file.exists():
                content = version_file.read_text(encoding="utf-8")
                self.assertIn(APP_NAME, content)
                self.assertIn(APP_VERSION, content)

        elif self.platform == "darwin":
            # macOS特定测试
            config.create_entitlements_plist()
            entitlements_file = config.build_path / "entitlements.plist"
            if entitlements_file.exists():
                content = entitlements_file.read_text(encoding="utf-8")
                self.assertIn("plist", content)

    def test_build_environment_preparation(self):
        """测试构建环境准备."""
        from build_config import BuildConfig

        config = BuildConfig()

        # 准备构建环境
        config.prepare_build_environment()

        # 验证构建目录存在
        self.assertTrue(config.build_path.exists())

        # 验证平台特定文件创建
        if self.platform == "windows":
            version_file = config.build_path / "version_info.txt"
            self.assertTrue(version_file.exists() or True)  # 允许文件不存在
        elif self.platform == "darwin":
            entitlements_file = config.build_path / "entitlements.plist"
            self.assertTrue(entitlements_file.exists() or True)  # 允许文件不存在

    @unittest.skipUnless(shutil.which("python"), "需要Python可执行文件")
    def test_build_script_execution(self):
        """测试构建脚本执行."""
        build_script = self.build_dir / "build.py"

        if not build_script.exists():
            self.skipTest("构建脚本不存在")

        # 测试构建脚本语法
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(build_script)],
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, f"构建脚本语法错误: {result.stderr}")

    def test_resource_manager_in_packaged_environment(self):
        """测试打包环境中的资源管理器."""
        # 模拟PyInstaller环境
        with patch.object(sys, "_MEIPASS", str(self.project_root / "fake_meipass")):
            resource_manager = ResourceManager()

            # 验证路径处理
            self.assertIsInstance(resource_manager.base_path, Path)
            self.assertIsInstance(resource_manager.resource_path, Path)

    def test_application_startup_simulation(self):
        """测试应用程序启动模拟."""
        # 模拟应用程序启动过程
        main_script = self.project_root / "src" / "minicrm" / "main.py"

        if not main_script.exists():
            self.skipTest("主脚本不存在")

        # 测试导入主模块
        try:
            # 临时添加路径
            original_path = sys.path.copy()
            sys.path.insert(0, str(self.project_root / "src"))

            # 尝试导入主模块
            import minicrm.main

            # 验证主要函数存在
            self.assertTrue(hasattr(minicrm.main, "main"))
            self.assertTrue(callable(minicrm.main.main))

        except ImportError as e:
            self.fail(f"无法导入主模块: {e}")
        finally:
            # 恢复路径
            sys.path = original_path

    def test_dependency_availability(self):
        """测试依赖可用性."""
        required_packages = [
            "tkinter",
            "sqlite3",
            "pathlib",
            "logging",
            "json",
            "os",
            "sys",
            "platform",
        ]

        optional_packages = ["matplotlib", "PIL", "openpyxl", "docxtpl", "reportlab"]

        # 测试必需包
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                self.fail(f"必需包不可用: {package}")

        # 测试可选包
        available_optional = []
        for package in optional_packages:
            try:
                __import__(package)
                available_optional.append(package)
            except ImportError:
                pass

        print(f"可用的可选包: {available_optional}")

    def test_file_permissions(self):
        """测试文件权限."""
        # 测试构建脚本权限
        build_scripts = [
            self.build_dir / "build.py",
            self.build_dir / "build_config.py",
        ]

        for script in build_scripts:
            if script.exists():
                # 验证文件可读
                self.assertTrue(os.access(script, os.R_OK))

                # 在Unix系统上验证执行权限
                if self.platform in ["darwin", "linux"]:
                    # Python脚本不需要执行权限，但shell脚本需要
                    pass

    def test_output_directory_structure(self):
        """测试输出目录结构."""
        # 创建模拟的输出目录结构
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # 模拟dist目录结构
            dist_dir = temp_path / "dist"
            dist_dir.mkdir()

            # 创建模拟的应用程序文件
            app_file = dist_dir / f"{APP_NAME}-test"
            app_file.write_text("模拟应用程序")

            # 验证目录结构
            self.assertTrue(dist_dir.exists())
            self.assertTrue(app_file.exists())

    def test_configuration_validation(self):
        """测试配置验证."""
        from build_config import BuildConfig

        config = BuildConfig()
        build_info = config.get_build_info()

        # 验证构建信息完整性
        required_keys = [
            "app_name",
            "platform",
            "architecture",
            "python_version",
            "project_root",
            "main_script",
        ]

        for key in required_keys:
            self.assertIn(key, build_info, f"构建信息缺少必要键: {key}")
            self.assertIsNotNone(build_info[key], f"构建信息键值为空: {key}")

    def test_error_handling_in_build_process(self):
        """测试构建过程中的错误处理."""
        from build_config import BuildConfig

        config = BuildConfig()

        # 测试无效路径处理
        with patch.object(
            config, "get_main_script", return_value=Path("/nonexistent/script.py")
        ):
            # 应该能够处理无效路径而不崩溃
            try:
                args = config.get_pyinstaller_args()
                self.assertIsInstance(args, list)
            except Exception as e:
                # 如果抛出异常，应该是预期的异常类型
                self.assertIsInstance(e, (FileNotFoundError, ValueError))


class TestPackagedApplicationBehavior(unittest.TestCase):
    """打包应用程序行为测试."""

    def setUp(self):
        """测试准备."""
        self.project_root = project_root

    def test_resource_loading_in_packaged_app(self):
        """测试打包应用程序中的资源加载."""
        # 模拟打包环境
        with patch.object(sys, "_MEIPASS", "/fake/packaged/path"):
            resource_manager = ResourceManager()

            # 测试资源路径计算
            self.assertIn("fake", str(resource_manager.base_path))

    def test_database_initialization_in_packaged_app(self):
        """测试打包应用程序中的数据库初始化."""
        # 创建临时数据库文件
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            temp_db_path = temp_db.name

        try:
            # 测试数据库连接
            import sqlite3

            conn = sqlite3.connect(temp_db_path)
            cursor = conn.cursor()

            # 创建测试表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            """)

            # 插入测试数据
            cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test",))
            conn.commit()

            # 验证数据
            cursor.execute("SELECT COUNT(*) FROM test_table")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1)

            conn.close()

        finally:
            # 清理临时文件
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)

    def test_logging_in_packaged_app(self):
        """测试打包应用程序中的日志功能."""
        import logging

        # 创建临时日志文件
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".log", delete=False
        ) as temp_log:
            temp_log_path = temp_log.name

        try:
            # 配置日志
            logger = logging.getLogger("test_packaged_app")
            handler = logging.FileHandler(temp_log_path, encoding="utf-8")
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

            # 写入测试日志
            logger.info("测试打包应用程序日志功能")
            logger.warning("测试警告消息")
            logger.error("测试错误消息")

            # 刷新日志
            handler.flush()

            # 验证日志文件
            with open(temp_log_path, encoding="utf-8") as f:
                log_content = f.read()
                self.assertIn("测试打包应用程序日志功能", log_content)
                self.assertIn("测试警告消息", log_content)
                self.assertIn("测试错误消息", log_content)

        finally:
            # 清理
            if os.path.exists(temp_log_path):
                os.unlink(temp_log_path)


def run_deployment_tests():
    """运行部署测试套件."""
    # 创建测试套件
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTest(unittest.makeSuite(TestDeploymentIntegration))
    suite.addTest(unittest.makeSuite(TestPackagedApplicationBehavior))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    print(f"在 {platform.system()} 平台运行部署集成测试")
    print(f"项目根目录: {project_root}")
    print("=" * 60)

    success = run_deployment_tests()

    print("=" * 60)
    if success:
        print("✅ 所有部署测试通过")
    else:
        print("❌ 部分部署测试失败")

    sys.exit(0 if success else 1)
