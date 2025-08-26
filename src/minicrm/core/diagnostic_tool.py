"""MiniCRM 诊断工具

提供系统诊断和问题定位功能,包括:
- 系统环境检查
- 配置文件验证
- 数据库完整性检查
- 性能瓶颈分析
- 问题定位和修复建议

设计原则:
- 全面的系统诊断覆盖
- 智能的问题识别和分析
- 实用的修复建议
- 详细的诊断报告
"""

from datetime import datetime
import json
import os
import platform
import sqlite3
import sys
import tkinter as tk
from typing import Any, Dict, List, Optional

from .logger import get_logger
from .performance_monitor import performance_monitor
from .system_monitor import get_system_monitor


class DiagnosticResult:
    """诊断结果类"""

    def __init__(
        self,
        category: str,
        name: str,
        status: str,
        message: str,
        details: Dict[str, Any] = None,
        suggestions: List[str] = None,
    ):
        """初始化诊断结果

        Args:
            category: 诊断类别
            name: 诊断项名称
            status: 状态 ('pass', 'warning', 'fail')
            message: 诊断消息
            details: 详细信息
            suggestions: 修复建议
        """
        self.category = category
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.suggestions = suggestions or []
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "category": self.category,
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "suggestions": self.suggestions,
            "timestamp": self.timestamp.isoformat(),
        }


class DiagnosticTool:
    """系统诊断工具

    提供全面的系统诊断和问题定位功能.
    """

    def __init__(self):
        """初始化诊断工具"""
        self._logger = get_logger(__name__)
        self._results: List[DiagnosticResult] = []

        # 诊断配置
        self._config = {
            "check_system_info": True,
            "check_python_environment": True,
            "check_dependencies": True,
            "check_database": True,
            "check_configuration": True,
            "check_performance": True,
            "check_ui_components": True,
            "check_file_permissions": True,
        }

        self._logger.info("诊断工具初始化完成")

    def run_full_diagnosis(self) -> List[DiagnosticResult]:
        """运行完整的系统诊断

        Returns:
            List[DiagnosticResult]: 诊断结果列表
        """
        self._results.clear()

        self._logger.info("开始运行完整系统诊断")

        # 系统信息检查
        if self._config["check_system_info"]:
            self._check_system_info()

        # Python环境检查
        if self._config["check_python_environment"]:
            self._check_python_environment()

        # 依赖库检查
        if self._config["check_dependencies"]:
            self._check_dependencies()

        # 数据库检查
        if self._config["check_database"]:
            self._check_database()

        # 配置文件检查
        if self._config["check_configuration"]:
            self._check_configuration()

        # 性能检查
        if self._config["check_performance"]:
            self._check_performance()

        # UI组件检查
        if self._config["check_ui_components"]:
            self._check_ui_components()

        # 文件权限检查
        if self._config["check_file_permissions"]:
            self._check_file_permissions()

        self._logger.info(f"系统诊断完成,共检查 {len(self._results)} 项")

        return self._results.copy()

    def _check_system_info(self) -> None:
        """检查系统信息"""
        try:
            # 操作系统信息
            os_info = {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            }

            # 检查操作系统兼容性
            supported_systems = ["Windows", "Darwin", "Linux"]
            if os_info["system"] in supported_systems:
                self._add_result(
                    "system",
                    "os_compatibility",
                    "pass",
                    f"操作系统 {os_info['system']} 受支持",
                    details=os_info,
                )
            else:
                self._add_result(
                    "system",
                    "os_compatibility",
                    "warning",
                    f"操作系统 {os_info['system']} 可能不完全兼容",
                    details=os_info,
                    suggestions=["建议在Windows、macOS或Linux系统上运行"],
                )

            # 检查系统架构
            if platform.machine() in ["x86_64", "AMD64", "arm64"]:
                self._add_result(
                    "system",
                    "architecture",
                    "pass",
                    f"系统架构 {platform.machine()} 受支持",
                )
            else:
                self._add_result(
                    "system",
                    "architecture",
                    "warning",
                    f"系统架构 {platform.machine()} 可能存在兼容性问题",
                    suggestions=["建议使用64位系统"],
                )

        except Exception as e:
            self._add_result(
                "system",
                "system_info",
                "fail",
                f"获取系统信息失败: {e}",
                suggestions=["检查系统权限或重启应用程序"],
            )

    def _check_python_environment(self) -> None:
        """检查Python环境"""
        try:
            # Python版本检查
            python_version = sys.version_info
            version_str = (
                f"{python_version.major}.{python_version.minor}.{python_version.micro}"
            )

            if python_version >= (3, 8):
                self._add_result(
                    "python",
                    "version",
                    "pass",
                    f"Python版本 {version_str} 满足要求",
                    details={"version": version_str, "required": ">=3.8"},
                )
            else:
                self._add_result(
                    "python",
                    "version",
                    "fail",
                    f"Python版本 {version_str} 过低,要求>=3.8",
                    details={"version": version_str, "required": ">=3.8"},
                    suggestions=["升级Python到3.8或更高版本"],
                )

            # 检查Python路径
            python_path = sys.executable
            if os.path.exists(python_path):
                self._add_result(
                    "python",
                    "executable",
                    "pass",
                    f"Python可执行文件路径正常: {python_path}",
                )
            else:
                self._add_result(
                    "python",
                    "executable",
                    "fail",
                    f"Python可执行文件路径异常: {python_path}",
                    suggestions=["重新安装Python或检查环境变量"],
                )

            # 检查模块路径
            import_paths = sys.path
            self._add_result(
                "python",
                "module_paths",
                "pass",
                f"Python模块路径配置正常,共 {len(import_paths)} 个路径",
                details={"paths": import_paths[:5]},  # 只显示前5个路径
            )

        except Exception as e:
            self._add_result(
                "python",
                "environment",
                "fail",
                f"检查Python环境失败: {e}",
                suggestions=["检查Python安装或重新安装Python"],
            )

    def _check_dependencies(self) -> None:
        """检查依赖库"""
        required_modules = {
            "tkinter": "内置GUI库",
            "sqlite3": "内置数据库库",
            "logging": "内置日志库",
            "threading": "内置线程库",
            "json": "内置JSON库",
            "datetime": "内置日期时间库",
            "pathlib": "内置路径库",
            "typing": "内置类型提示库",
        }

        optional_modules = {
            "psutil": "系统监控库",
            "matplotlib": "图表绘制库",
            "reportlab": "PDF生成库",
            "docxtpl": "Word模板库",
            "openpyxl": "Excel处理库",
        }

        # 检查必需模块
        for module_name, description in required_modules.items():
            try:
                __import__(module_name)
                self._add_result(
                    "dependencies",
                    f"required_{module_name}",
                    "pass",
                    f"必需模块 {module_name} ({description}) 可用",
                )
            except ImportError as e:
                self._add_result(
                    "dependencies",
                    f"required_{module_name}",
                    "fail",
                    f"必需模块 {module_name} ({description}) 不可用: {e}",
                    suggestions=[f"安装或修复 {module_name} 模块"],
                )

        # 检查可选模块
        for module_name, description in optional_modules.items():
            try:
                __import__(module_name)
                self._add_result(
                    "dependencies",
                    f"optional_{module_name}",
                    "pass",
                    f"可选模块 {module_name} ({description}) 可用",
                )
            except ImportError:
                self._add_result(
                    "dependencies",
                    f"optional_{module_name}",
                    "warning",
                    f"可选模块 {module_name} ({description}) 不可用",
                    suggestions=[
                        f"安装 {module_name} 以获得完整功能: pip install {module_name}"
                    ],
                )

    def _check_database(self) -> None:
        """检查数据库"""
        try:
            # 测试SQLite连接
            test_conn = sqlite3.connect(":memory:")
            cursor = test_conn.cursor()

            # 测试基本SQL操作
            cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            cursor.execute("INSERT INTO test (name) VALUES (?)", ("test",))
            cursor.execute("SELECT * FROM test")
            result = cursor.fetchone()

            test_conn.close()

            if result:
                self._add_result(
                    "database", "sqlite_basic", "pass", "SQLite基本功能正常"
                )
            else:
                self._add_result(
                    "database",
                    "sqlite_basic",
                    "fail",
                    "SQLite基本功能异常",
                    suggestions=["检查SQLite安装或重新安装Python"],
                )

            # 检查数据库文件权限(如果存在)
            db_paths = ["minicrm.db", "data/minicrm.db", "src/minicrm/data/minicrm.db"]

            db_found = False
            for db_path in db_paths:
                if os.path.exists(db_path):
                    db_found = True
                    if os.access(db_path, os.R_OK | os.W_OK):
                        self._add_result(
                            "database",
                            "file_permissions",
                            "pass",
                            f"数据库文件权限正常: {db_path}",
                        )
                    else:
                        self._add_result(
                            "database",
                            "file_permissions",
                            "fail",
                            f"数据库文件权限不足: {db_path}",
                            suggestions=["检查文件权限或以管理员身份运行"],
                        )
                    break

            if not db_found:
                self._add_result(
                    "database",
                    "file_existence",
                    "warning",
                    "未找到数据库文件,将在首次运行时创建",
                    suggestions=["确保应用程序有创建文件的权限"],
                )

        except Exception as e:
            self._add_result(
                "database",
                "connectivity",
                "fail",
                f"数据库检查失败: {e}",
                suggestions=["检查SQLite安装或数据库文件权限"],
            )

    def _check_configuration(self) -> None:
        """检查配置文件"""
        config_files = [
            "config.json",
            "settings.json",
            "src/minicrm/config/config.json",
            "src/minicrm/application_config.py",
        ]

        config_found = False

        for config_file in config_files:
            if os.path.exists(config_file):
                config_found = True

                try:
                    if config_file.endswith(".json"):
                        with open(config_file, encoding="utf-8") as f:
                            json.load(f)
                        self._add_result(
                            "configuration",
                            f"config_file_{os.path.basename(config_file)}",
                            "pass",
                            f"配置文件格式正确: {config_file}",
                        )
                    elif config_file.endswith(".py"):
                        # 检查Python配置文件语法
                        with open(config_file, encoding="utf-8") as f:
                            compile(f.read(), config_file, "exec")
                        self._add_result(
                            "configuration",
                            f"config_file_{os.path.basename(config_file)}",
                            "pass",
                            f"配置文件语法正确: {config_file}",
                        )

                except (json.JSONDecodeError, SyntaxError) as e:
                    self._add_result(
                        "configuration",
                        f"config_file_{os.path.basename(config_file)}",
                        "fail",
                        f"配置文件格式错误: {config_file} - {e}",
                        suggestions=["检查配置文件语法或恢复默认配置"],
                    )
                except Exception as e:
                    self._add_result(
                        "configuration",
                        f"config_file_{os.path.basename(config_file)}",
                        "warning",
                        f"配置文件检查异常: {config_file} - {e}",
                        suggestions=["检查文件权限或配置文件完整性"],
                    )

        if not config_found:
            self._add_result(
                "configuration",
                "config_files",
                "warning",
                "未找到配置文件,将使用默认配置",
                suggestions=["创建配置文件以自定义应用程序设置"],
            )

    def _check_performance(self) -> None:
        """检查性能状态"""
        try:
            # 获取性能监控摘要
            perf_summary = performance_monitor.get_summary()

            if perf_summary["total_operations"] > 0:
                avg_duration = perf_summary["avg_duration_ms"]

                if avg_duration < 100:
                    self._add_result(
                        "performance",
                        "response_time",
                        "pass",
                        f"平均响应时间良好: {avg_duration:.1f}ms",
                        details=perf_summary,
                    )
                elif avg_duration < 500:
                    self._add_result(
                        "performance",
                        "response_time",
                        "warning",
                        f"平均响应时间较慢: {avg_duration:.1f}ms",
                        details=perf_summary,
                        suggestions=["优化数据库查询或减少UI操作复杂度"],
                    )
                else:
                    self._add_result(
                        "performance",
                        "response_time",
                        "fail",
                        f"平均响应时间过慢: {avg_duration:.1f}ms",
                        details=perf_summary,
                        suggestions=["检查系统资源使用或优化应用程序性能"],
                    )
            else:
                self._add_result(
                    "performance",
                    "monitoring_data",
                    "warning",
                    "无性能监控数据",
                    suggestions=["运行一些操作以收集性能数据"],
                )

            # 检查系统监控状态
            system_monitor = get_system_monitor()
            monitor_status = system_monitor.get_monitoring_status()

            if monitor_status["monitoring_enabled"]:
                self._add_result(
                    "performance",
                    "system_monitoring",
                    "pass",
                    "系统监控正常运行",
                    details=monitor_status,
                )
            else:
                self._add_result(
                    "performance",
                    "system_monitoring",
                    "warning",
                    "系统监控未启用",
                    suggestions=["启用系统监控以获得更好的性能分析"],
                )

        except Exception as e:
            self._add_result(
                "performance",
                "check_failed",
                "fail",
                f"性能检查失败: {e}",
                suggestions=["检查性能监控组件或重启应用程序"],
            )

    def _check_ui_components(self) -> None:
        """检查UI组件"""
        try:
            # 测试tkinter基本功能
            root = tk.Tk()
            root.withdraw()  # 隐藏窗口

            # 测试基本组件创建
            try:
                from tkinter import ttk

                frame = ttk.Frame(root)
                label = ttk.Label(frame, text="测试")
                button = ttk.Button(frame, text="测试")
                entry = ttk.Entry(frame)

                self._add_result("ui", "ttk_components", "pass", "TTK组件创建正常")

            except Exception as e:
                self._add_result(
                    "ui",
                    "ttk_components",
                    "fail",
                    f"TTK组件创建失败: {e}",
                    suggestions=["检查tkinter安装或重新安装Python"],
                )

            # 测试主题支持
            try:
                style = ttk.Style()
                themes = style.theme_names()

                if themes:
                    self._add_result(
                        "ui",
                        "themes",
                        "pass",
                        f"主题支持正常,可用主题: {', '.join(themes)}",
                        details={"available_themes": list(themes)},
                    )
                else:
                    self._add_result(
                        "ui",
                        "themes",
                        "warning",
                        "无可用主题",
                        suggestions=["检查TTK主题支持或使用默认样式"],
                    )

            except Exception as e:
                self._add_result(
                    "ui",
                    "themes",
                    "warning",
                    f"主题检查失败: {e}",
                    suggestions=["使用默认样式或检查TTK配置"],
                )

            root.destroy()

        except Exception as e:
            self._add_result(
                "ui",
                "tkinter_basic",
                "fail",
                f"tkinter基本功能检查失败: {e}",
                suggestions=["检查GUI库安装或在支持GUI的环境中运行"],
            )

    def _check_file_permissions(self) -> None:
        """检查文件权限"""
        try:
            # 检查当前目录权限
            current_dir = os.getcwd()

            if os.access(current_dir, os.R_OK):
                self._add_result(
                    "permissions",
                    "read_access",
                    "pass",
                    f"当前目录读取权限正常: {current_dir}",
                )
            else:
                self._add_result(
                    "permissions",
                    "read_access",
                    "fail",
                    f"当前目录读取权限不足: {current_dir}",
                    suggestions=["检查目录权限或更改工作目录"],
                )

            if os.access(current_dir, os.W_OK):
                self._add_result(
                    "permissions",
                    "write_access",
                    "pass",
                    f"当前目录写入权限正常: {current_dir}",
                )
            else:
                self._add_result(
                    "permissions",
                    "write_access",
                    "fail",
                    f"当前目录写入权限不足: {current_dir}",
                    suggestions=["检查目录权限或以管理员身份运行"],
                )

            # 检查临时目录权限
            import tempfile

            temp_dir = tempfile.gettempdir()

            if os.access(temp_dir, os.R_OK | os.W_OK):
                self._add_result(
                    "permissions",
                    "temp_access",
                    "pass",
                    f"临时目录权限正常: {temp_dir}",
                )
            else:
                self._add_result(
                    "permissions",
                    "temp_access",
                    "warning",
                    f"临时目录权限不足: {temp_dir}",
                    suggestions=["检查系统临时目录权限"],
                )

        except Exception as e:
            self._add_result(
                "permissions",
                "check_failed",
                "fail",
                f"文件权限检查失败: {e}",
                suggestions=["检查系统权限或重启应用程序"],
            )

    def _add_result(
        self,
        category: str,
        name: str,
        status: str,
        message: str,
        details: Dict[str, Any] = None,
        suggestions: List[str] = None,
    ) -> None:
        """添加诊断结果"""
        result = DiagnosticResult(
            category=category,
            name=name,
            status=status,
            message=message,
            details=details,
            suggestions=suggestions,
        )
        self._results.append(result)

    def get_results_by_category(self, category: str) -> List[DiagnosticResult]:
        """按类别获取诊断结果

        Args:
            category: 类别名称

        Returns:
            List[DiagnosticResult]: 该类别的诊断结果
        """
        return [r for r in self._results if r.category == category]

    def get_failed_results(self) -> List[DiagnosticResult]:
        """获取失败的诊断结果"""
        return [r for r in self._results if r.status == "fail"]

    def get_warning_results(self) -> List[DiagnosticResult]:
        """获取警告的诊断结果"""
        return [r for r in self._results if r.status == "warning"]

    def generate_summary(self) -> Dict[str, Any]:
        """生成诊断摘要

        Returns:
            Dict[str, Any]: 诊断摘要
        """
        total = len(self._results)
        passed = len([r for r in self._results if r.status == "pass"])
        warnings = len([r for r in self._results if r.status == "warning"])
        failed = len([r for r in self._results if r.status == "fail"])

        categories = {}
        for result in self._results:
            if result.category not in categories:
                categories[result.category] = {"pass": 0, "warning": 0, "fail": 0}
            categories[result.category][result.status] += 1

        return {
            "timestamp": datetime.now().isoformat(),
            "total_checks": total,
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
            "success_rate": (passed / max(total, 1)) * 100,
            "categories": categories,
            "overall_status": "fail"
            if failed > 0
            else ("warning" if warnings > 0 else "pass"),
        }

    def generate_report(self) -> str:
        """生成诊断报告

        Returns:
            str: 格式化的诊断报告
        """
        summary = self.generate_summary()

        lines = [
            "=== MiniCRM 系统诊断报告 ===",
            f"生成时间: {summary['timestamp']}",
            "",
            "=== 诊断摘要 ===",
            f"总检查项: {summary['total_checks']}",
            f"通过: {summary['passed']}",
            f"警告: {summary['warnings']}",
            f"失败: {summary['failed']}",
            f"成功率: {summary['success_rate']:.1f}%",
            f"整体状态: {summary['overall_status'].upper()}",
            "",
        ]

        # 按类别显示结果
        for category, stats in summary["categories"].items():
            lines.extend(
                [
                    f"=== {category.upper()} ===",
                    f"通过: {stats['pass']}, 警告: {stats['warning']}, 失败: {stats['fail']}",
                    "",
                ]
            )

            category_results = self.get_results_by_category(category)
            for result in category_results:
                status_icon = {"pass": "✓", "warning": "⚠", "fail": "✗"}[result.status]
                lines.append(f"{status_icon} {result.name}: {result.message}")

                if result.suggestions:
                    for suggestion in result.suggestions:
                        lines.append(f"  建议: {suggestion}")

            lines.append("")

        # 修复建议汇总
        all_suggestions = []
        for result in self._results:
            if result.status in ["warning", "fail"] and result.suggestions:
                all_suggestions.extend(result.suggestions)

        if all_suggestions:
            lines.extend(
                [
                    "=== 修复建议汇总 ===",
                ]
            )
            for i, suggestion in enumerate(set(all_suggestions), 1):
                lines.append(f"{i}. {suggestion}")

        return "\n".join(lines)

    def export_report(self, file_path: str, format: str = "txt") -> None:
        """导出诊断报告

        Args:
            file_path: 导出文件路径
            format: 导出格式 ('txt', 'json')
        """
        try:
            if format == "json":
                # JSON格式导出
                export_data = {
                    "summary": self.generate_summary(),
                    "results": [r.to_dict() for r in self._results],
                }

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            else:
                # 文本格式导出
                report_text = self.generate_report()

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(report_text)

            self._logger.info(f"诊断报告已导出到: {file_path}")

        except Exception as e:
            self._logger.error(f"导出诊断报告失败: {e}")
            raise


# 全局诊断工具实例
_diagnostic_tool: Optional[DiagnosticTool] = None


def get_diagnostic_tool() -> DiagnosticTool:
    """获取全局诊断工具实例

    Returns:
        DiagnosticTool: 诊断工具实例
    """
    global _diagnostic_tool

    if _diagnostic_tool is None:
        _diagnostic_tool = DiagnosticTool()

    return _diagnostic_tool


def run_system_diagnosis() -> List[DiagnosticResult]:
    """运行系统诊断"""
    return get_diagnostic_tool().run_full_diagnosis()


def generate_diagnostic_report() -> str:
    """生成诊断报告"""
    return get_diagnostic_tool().generate_report()
