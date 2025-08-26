"""
诊断工具测试

测试诊断工具的各项功能，包括：
- 系统环境检查
- 配置文件验证
- 数据库完整性检查
- 性能瓶颈分析
"""

import unittest
from unittest.mock import Mock, mock_open, patch

from src.minicrm.core.diagnostic_tool import (
    DiagnosticResult,
    DiagnosticTool,
    generate_diagnostic_report,
    get_diagnostic_tool,
    run_system_diagnosis,
)


class TestDiagnosticResult(unittest.TestCase):
    """诊断结果数据类测试"""

    def test_diagnostic_result_creation(self):
        """测试诊断结果创建"""
        result = DiagnosticResult(
            category="test_category",
            name="test_name",
            status="pass",
            message="测试通过",
            details={"key": "value"},
            suggestions=["建议1", "建议2"],
        )

        self.assertEqual(result.category, "test_category")
        self.assertEqual(result.name, "test_name")
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.message, "测试通过")
        self.assertEqual(result.details, {"key": "value"})
        self.assertEqual(result.suggestions, ["建议1", "建议2"])
        self.assertIsNotNone(result.timestamp)

    def test_diagnostic_result_defaults(self):
        """测试诊断结果默认值"""
        result = DiagnosticResult(
            category="test", name="test", status="pass", message="测试"
        )

        self.assertEqual(result.details, {})
        self.assertEqual(result.suggestions, [])

    def test_diagnostic_result_to_dict(self):
        """测试诊断结果转换为字典"""
        result = DiagnosticResult(
            category="test_category",
            name="test_name",
            status="pass",
            message="测试通过",
            details={"key": "value"},
            suggestions=["建议1"],
        )

        dict_result = result.to_dict()

        self.assertEqual(dict_result["category"], "test_category")
        self.assertEqual(dict_result["name"], "test_name")
        self.assertEqual(dict_result["status"], "pass")
        self.assertEqual(dict_result["message"], "测试通过")
        self.assertEqual(dict_result["details"], {"key": "value"})
        self.assertEqual(dict_result["suggestions"], ["建议1"])
        self.assertEqual(dict_result["timestamp"], result.timestamp.isoformat())


class TestDiagnosticTool(unittest.TestCase):
    """诊断工具测试类"""

    def setUp(self):
        """测试准备"""
        self.diagnostic_tool = DiagnosticTool()
        self.diagnostic_tool._logger = Mock()

    def test_initialization(self):
        """测试初始化"""
        tool = DiagnosticTool()

        self.assertIsNotNone(tool._logger)
        self.assertIsInstance(tool._results, list)
        self.assertIsInstance(tool._config, dict)
        self.assertEqual(len(tool._results), 0)

    def test_add_result(self):
        """测试添加诊断结果"""
        self.diagnostic_tool._add_result(
            category="test",
            name="test_check",
            status="pass",
            message="测试通过",
            details={"key": "value"},
            suggestions=["建议"],
        )

        self.assertEqual(len(self.diagnostic_tool._results), 1)
        result = self.diagnostic_tool._results[0]
        self.assertEqual(result.category, "test")
        self.assertEqual(result.name, "test_check")
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.message, "测试通过")

    @patch("platform.system")
    @patch("platform.release")
    @patch("platform.version")
    @patch("platform.machine")
    @patch("platform.processor")
    def test_check_system_info_supported_os(
        self, mock_processor, mock_machine, mock_version, mock_release, mock_system
    ):
        """测试系统信息检查 - 支持的操作系统"""
        mock_system.return_value = "Windows"
        mock_release.return_value = "10"
        mock_version.return_value = "10.0.19041"
        mock_machine.return_value = "x86_64"
        mock_processor.return_value = (
            "Intel64 Family 6 Model 142 Stepping 10, GenuineIntel"
        )

        self.diagnostic_tool._check_system_info()

        # 应该有两个结果：操作系统兼容性和系统架构
        results = [r for r in self.diagnostic_tool._results if r.category == "system"]
        self.assertEqual(len(results), 2)

        # 检查操作系统兼容性结果
        os_result = next(r for r in results if r.name == "os_compatibility")
        self.assertEqual(os_result.status, "pass")
        self.assertIn("Windows", os_result.message)

        # 检查系统架构结果
        arch_result = next(r for r in results if r.name == "architecture")
        self.assertEqual(arch_result.status, "pass")
        self.assertIn("x86_64", arch_result.message)

    @patch("platform.system")
    @patch("platform.machine")
    def test_check_system_info_unsupported_os(self, mock_machine, mock_system):
        """测试系统信息检查 - 不支持的操作系统"""
        mock_system.return_value = "UnknownOS"
        mock_machine.return_value = "unknown_arch"

        self.diagnostic_tool._check_system_info()

        results = [r for r in self.diagnostic_tool._results if r.category == "system"]

        # 检查操作系统兼容性结果
        os_result = next(r for r in results if r.name == "os_compatibility")
        self.assertEqual(os_result.status, "warning")

        # 检查系统架构结果
        arch_result = next(r for r in results if r.name == "architecture")
        self.assertEqual(arch_result.status, "warning")

    @patch("sys.version_info", (3, 9, 0))
    @patch("sys.executable", "/usr/bin/python3")
    @patch("os.path.exists")
    def test_check_python_environment_good_version(self, mock_exists):
        """测试Python环境检查 - 良好版本"""
        mock_exists.return_value = True

        self.diagnostic_tool._check_python_environment()

        results = [r for r in self.diagnostic_tool._results if r.category == "python"]

        # 检查版本结果
        version_result = next(r for r in results if r.name == "version")
        self.assertEqual(version_result.status, "pass")

        # 检查可执行文件结果
        exec_result = next(r for r in results if r.name == "executable")
        self.assertEqual(exec_result.status, "pass")

    @patch("sys.version_info", (3, 7, 0))
    def test_check_python_environment_old_version(self):
        """测试Python环境检查 - 旧版本"""
        self.diagnostic_tool._check_python_environment()

        results = [r for r in self.diagnostic_tool._results if r.category == "python"]
        version_result = next(r for r in results if r.name == "version")
        self.assertEqual(version_result.status, "fail")
        self.assertIn("过低", version_result.message)

    def test_check_dependencies_required_modules(self):
        """测试依赖检查 - 必需模块"""
        self.diagnostic_tool._check_dependencies()

        results = [
            r for r in self.diagnostic_tool._results if r.category == "dependencies"
        ]

        # 检查必需模块结果
        required_results = [r for r in results if r.name.startswith("required_")]
        self.assertTrue(len(required_results) > 0)

        # tkinter应该可用
        tkinter_result = next(
            (r for r in required_results if "tkinter" in r.name), None
        )
        self.assertIsNotNone(tkinter_result)
        self.assertEqual(tkinter_result.status, "pass")

    @patch("sqlite3.connect")
    def test_check_database_success(self, mock_connect):
        """测试数据库检查 - 成功"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1, "test")
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        self.diagnostic_tool._check_database()

        results = [r for r in self.diagnostic_tool._results if r.category == "database"]
        basic_result = next(r for r in results if r.name == "sqlite_basic")
        self.assertEqual(basic_result.status, "pass")

    @patch("sqlite3.connect")
    def test_check_database_failure(self, mock_connect):
        """测试数据库检查 - 失败"""
        mock_connect.side_effect = Exception("数据库连接失败")

        self.diagnostic_tool._check_database()

        results = [r for r in self.diagnostic_tool._results if r.category == "database"]
        connectivity_result = next(r for r in results if r.name == "connectivity")
        self.assertEqual(connectivity_result.status, "fail")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
    def test_check_configuration_valid_json(self, mock_file, mock_exists):
        """测试配置检查 - 有效JSON"""
        mock_exists.side_effect = lambda path: path == "config.json"

        self.diagnostic_tool._check_configuration()

        results = [
            r for r in self.diagnostic_tool._results if r.category == "configuration"
        ]
        config_result = next((r for r in results if "config.json" in r.name), None)
        self.assertIsNotNone(config_result)
        self.assertEqual(config_result.status, "pass")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="invalid json")
    def test_check_configuration_invalid_json(self, mock_file, mock_exists):
        """测试配置检查 - 无效JSON"""
        mock_exists.side_effect = lambda path: path == "config.json"

        self.diagnostic_tool._check_configuration()

        results = [
            r for r in self.diagnostic_tool._results if r.category == "configuration"
        ]
        config_result = next((r for r in results if "config.json" in r.name), None)
        self.assertIsNotNone(config_result)
        self.assertEqual(config_result.status, "fail")

    @patch("src.minicrm.core.diagnostic_tool.performance_monitor")
    def test_check_performance_good(self, mock_perf_monitor):
        """测试性能检查 - 良好性能"""
        mock_perf_monitor.get_summary.return_value = {
            "total_operations": 100,
            "avg_duration_ms": 50.0,
        }

        self.diagnostic_tool._check_performance()

        results = [
            r for r in self.diagnostic_tool._results if r.category == "performance"
        ]
        response_result = next(r for r in results if r.name == "response_time")
        self.assertEqual(response_result.status, "pass")

    @patch("src.minicrm.core.diagnostic_tool.performance_monitor")
    def test_check_performance_slow(self, mock_perf_monitor):
        """测试性能检查 - 慢性能"""
        mock_perf_monitor.get_summary.return_value = {
            "total_operations": 100,
            "avg_duration_ms": 600.0,
        }

        self.diagnostic_tool._check_performance()

        results = [
            r for r in self.diagnostic_tool._results if r.category == "performance"
        ]
        response_result = next(r for r in results if r.name == "response_time")
        self.assertEqual(response_result.status, "fail")

    @patch("tkinter.Tk")
    @patch("tkinter.ttk.Style")
    def test_check_ui_components_success(self, mock_style, mock_tk):
        """测试UI组件检查 - 成功"""
        mock_root = Mock()
        mock_root.withdraw = Mock()
        mock_root.destroy = Mock()
        mock_tk.return_value = mock_root

        mock_style_instance = Mock()
        mock_style_instance.theme_names.return_value = ("default", "clam")
        mock_style.return_value = mock_style_instance

        self.diagnostic_tool._check_ui_components()

        results = [r for r in self.diagnostic_tool._results if r.category == "ui"]

        # 检查TTK组件结果
        ttk_result = next(r for r in results if r.name == "ttk_components")
        self.assertEqual(ttk_result.status, "pass")

        # 检查主题结果
        themes_result = next(r for r in results if r.name == "themes")
        self.assertEqual(themes_result.status, "pass")

    @patch("os.access")
    @patch("os.getcwd")
    @patch("tempfile.gettempdir")
    def test_check_file_permissions_success(
        self, mock_gettempdir, mock_getcwd, mock_access
    ):
        """测试文件权限检查 - 成功"""
        mock_getcwd.return_value = "/test/dir"
        mock_gettempdir.return_value = "/tmp"
        mock_access.return_value = True

        self.diagnostic_tool._check_file_permissions()

        results = [
            r for r in self.diagnostic_tool._results if r.category == "permissions"
        ]

        # 检查读取权限
        read_result = next(r for r in results if r.name == "read_access")
        self.assertEqual(read_result.status, "pass")

        # 检查写入权限
        write_result = next(r for r in results if r.name == "write_access")
        self.assertEqual(write_result.status, "pass")

        # 检查临时目录权限
        temp_result = next(r for r in results if r.name == "temp_access")
        self.assertEqual(temp_result.status, "pass")

    def test_run_full_diagnosis(self):
        """测试运行完整诊断"""
        # 模拟各个检查方法
        self.diagnostic_tool._check_system_info = Mock()
        self.diagnostic_tool._check_python_environment = Mock()
        self.diagnostic_tool._check_dependencies = Mock()
        self.diagnostic_tool._check_database = Mock()
        self.diagnostic_tool._check_configuration = Mock()
        self.diagnostic_tool._check_performance = Mock()
        self.diagnostic_tool._check_ui_components = Mock()
        self.diagnostic_tool._check_file_permissions = Mock()

        results = self.diagnostic_tool.run_full_diagnosis()

        # 验证所有检查方法都被调用
        self.diagnostic_tool._check_system_info.assert_called_once()
        self.diagnostic_tool._check_python_environment.assert_called_once()
        self.diagnostic_tool._check_dependencies.assert_called_once()
        self.diagnostic_tool._check_database.assert_called_once()
        self.diagnostic_tool._check_configuration.assert_called_once()
        self.diagnostic_tool._check_performance.assert_called_once()
        self.diagnostic_tool._check_ui_components.assert_called_once()
        self.diagnostic_tool._check_file_permissions.assert_called_once()

        self.assertIsInstance(results, list)

    def test_get_results_by_category(self):
        """测试按类别获取结果"""
        # 添加测试结果
        self.diagnostic_tool._add_result("category1", "test1", "pass", "消息1")
        self.diagnostic_tool._add_result("category2", "test2", "fail", "消息2")
        self.diagnostic_tool._add_result("category1", "test3", "warning", "消息3")

        category1_results = self.diagnostic_tool.get_results_by_category("category1")
        self.assertEqual(len(category1_results), 2)

        category2_results = self.diagnostic_tool.get_results_by_category("category2")
        self.assertEqual(len(category2_results), 1)

    def test_get_failed_results(self):
        """测试获取失败结果"""
        self.diagnostic_tool._add_result("test", "test1", "pass", "消息1")
        self.diagnostic_tool._add_result("test", "test2", "fail", "消息2")
        self.diagnostic_tool._add_result("test", "test3", "warning", "消息3")
        self.diagnostic_tool._add_result("test", "test4", "fail", "消息4")

        failed_results = self.diagnostic_tool.get_failed_results()
        self.assertEqual(len(failed_results), 2)

        for result in failed_results:
            self.assertEqual(result.status, "fail")

    def test_get_warning_results(self):
        """测试获取警告结果"""
        self.diagnostic_tool._add_result("test", "test1", "pass", "消息1")
        self.diagnostic_tool._add_result("test", "test2", "fail", "消息2")
        self.diagnostic_tool._add_result("test", "test3", "warning", "消息3")
        self.diagnostic_tool._add_result("test", "test4", "warning", "消息4")

        warning_results = self.diagnostic_tool.get_warning_results()
        self.assertEqual(len(warning_results), 2)

        for result in warning_results:
            self.assertEqual(result.status, "warning")

    def test_generate_summary(self):
        """测试生成摘要"""
        # 添加测试结果
        self.diagnostic_tool._add_result("category1", "test1", "pass", "消息1")
        self.diagnostic_tool._add_result("category1", "test2", "fail", "消息2")
        self.diagnostic_tool._add_result("category2", "test3", "warning", "消息3")
        self.diagnostic_tool._add_result("category2", "test4", "pass", "消息4")

        summary = self.diagnostic_tool.generate_summary()

        self.assertEqual(summary["total_checks"], 4)
        self.assertEqual(summary["passed"], 2)
        self.assertEqual(summary["warnings"], 1)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["success_rate"], 50.0)
        self.assertEqual(summary["overall_status"], "fail")  # 因为有失败项

        # 检查类别统计
        self.assertIn("category1", summary["categories"])
        self.assertIn("category2", summary["categories"])
        self.assertEqual(summary["categories"]["category1"]["pass"], 1)
        self.assertEqual(summary["categories"]["category1"]["fail"], 1)
        self.assertEqual(summary["categories"]["category2"]["warning"], 1)
        self.assertEqual(summary["categories"]["category2"]["pass"], 1)

    def test_generate_report(self):
        """测试生成报告"""
        # 添加测试结果
        self.diagnostic_tool._add_result("test_category", "test1", "pass", "测试通过")
        self.diagnostic_tool._add_result(
            "test_category",
            "test2",
            "fail",
            "测试失败",
            suggestions=["修复建议1", "修复建议2"],
        )

        report = self.diagnostic_tool.generate_report()

        self.assertIsInstance(report, str)
        self.assertIn("MiniCRM 系统诊断报告", report)
        self.assertIn("诊断摘要", report)
        self.assertIn("TEST_CATEGORY", report)
        self.assertIn("测试通过", report)
        self.assertIn("测试失败", report)
        self.assertIn("修复建议汇总", report)
        self.assertIn("修复建议1", report)
        self.assertIn("修复建议2", report)

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_export_report_json(self, mock_json_dump, mock_file):
        """测试导出JSON格式报告"""
        self.diagnostic_tool._add_result("test", "test1", "pass", "测试")

        self.diagnostic_tool.export_report("test_report.json", format="json")

        mock_file.assert_called_once_with("test_report.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    def test_export_report_txt(self, mock_file):
        """测试导出文本格式报告"""
        self.diagnostic_tool._add_result("test", "test1", "pass", "测试")

        self.diagnostic_tool.export_report("test_report.txt", format="txt")

        mock_file.assert_called_once_with("test_report.txt", "w", encoding="utf-8")
        # 验证写入了报告内容
        written_content = "".join(
            call.args[0] for call in mock_file().write.call_args_list
        )
        self.assertIn("MiniCRM 系统诊断报告", written_content)


class TestGlobalFunctions(unittest.TestCase):
    """测试全局函数"""

    def test_get_diagnostic_tool(self):
        """测试获取诊断工具"""
        tool1 = get_diagnostic_tool()
        tool2 = get_diagnostic_tool()

        # 应该返回同一个实例
        self.assertIs(tool1, tool2)
        self.assertIsInstance(tool1, DiagnosticTool)

    @patch("src.minicrm.core.diagnostic_tool.get_diagnostic_tool")
    def test_run_system_diagnosis(self, mock_get_tool):
        """测试运行系统诊断"""
        mock_tool = Mock()
        mock_results = [Mock(), Mock()]
        mock_tool.run_full_diagnosis.return_value = mock_results
        mock_get_tool.return_value = mock_tool

        results = run_system_diagnosis()

        self.assertEqual(results, mock_results)
        mock_tool.run_full_diagnosis.assert_called_once()

    @patch("src.minicrm.core.diagnostic_tool.get_diagnostic_tool")
    def test_generate_diagnostic_report(self, mock_get_tool):
        """测试生成诊断报告"""
        mock_tool = Mock()
        mock_report = "测试报告内容"
        mock_tool.generate_report.return_value = mock_report
        mock_get_tool.return_value = mock_tool

        report = generate_diagnostic_report()

        self.assertEqual(report, mock_report)
        mock_tool.generate_report.assert_called_once()


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_full_diagnosis_integration(self):
        """测试完整诊断集成"""
        tool = DiagnosticTool()

        # 运行完整诊断
        results = tool.run_full_diagnosis()

        # 验证有结果返回
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)

        # 验证结果包含各个类别
        categories = set(r.category for r in results)
        expected_categories = {
            "system",
            "python",
            "dependencies",
            "database",
            "configuration",
            "performance",
            "ui",
            "permissions",
        }

        # 至少应该包含大部分类别
        self.assertTrue(len(categories.intersection(expected_categories)) >= 6)

        # 生成摘要
        summary = tool.generate_summary()
        self.assertIn("total_checks", summary)
        self.assertIn("overall_status", summary)

        # 生成报告
        report = tool.generate_report()
        self.assertIsInstance(report, str)
        self.assertTrue(len(report) > 100)  # 报告应该有一定长度


if __name__ == "__main__":
    unittest.main()
