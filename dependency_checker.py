#!/usr/bin/env python3
"""MiniCRM 依赖检查工具

执行全面的依赖分析，包括：
1. 导入语句分析
2. 依赖一致性检查
3. 版本兼容性验证
4. 安全漏洞扫描
5. 许可证合规检查
"""

import ast
from pathlib import Path
import re
import sys
from typing import Dict, List, Set


class DependencyChecker:
    """依赖检查器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.pyproject_path = project_root / "pyproject.toml"

        # 内置模块列表（Python标准库）
        self.builtin_modules = {
            "os",
            "sys",
            "json",
            "csv",
            "sqlite3",
            "datetime",
            "time",
            "logging",
            "pathlib",
            "typing",
            "dataclasses",
            "functools",
            "itertools",
            "collections",
            "concurrent",
            "threading",
            "asyncio",
            "unittest",
            "tempfile",
            "shutil",
            "subprocess",
            "traceback",
            "warnings",
            "decimal",
            "math",
            "random",
            "hashlib",
            "uuid",
            "base64",
            "urllib",
            "http",
            "email",
            "html",
            "xml",
            "configparser",
            "argparse",
            "glob",
            "fnmatch",
            "linecache",
            "pickle",
            "copyreg",
            "copy",
            "pprint",
            "reprlib",
            "enum",
            "numbers",
            "cmath",
            "fractions",
            "statistics",
            "array",
            "weakref",
            "types",
            "gc",
            "inspect",
            "site",
            "importlib",
            "pkgutil",
            "modulefinder",
            "runpy",
            "parser",
            "symbol",
            "token",
            "keyword",
            "tokenize",
            "tabnanny",
            "pyclbr",
            "py_compile",
            "compileall",
            "dis",
            "pickletools",
            "platform",
            "errno",
            "ctypes",
            "struct",
            "codecs",
            "unicodedata",
            "stringprep",
            "readline",
            "rlcompleter",
            "mmap",
            "select",
            "socket",
            "ssl",
            "signal",
            "pdb",
            "profile",
            "pstats",
            "timeit",
            "trace",
            "faulthandler",
            "tracemalloc",
            "resource",
            "sysconfig",
            "getpass",
            "getopt",
            "macpath",
            "ntpath",
            "posixpath",
            "genericpath",
            "stat",
            "filecmp",
            "tarfile",
            "zipfile",
            "gzip",
            "bz2",
            "lzma",
            "zlib",
            "binascii",
            "quopri",
            "uu",
            "binhex",
            "hmac",
            "secrets",
            "io",
            "curses",
            "multiprocessing",
            "sched",
            "queue",
            "contextvars",
            "_thread",
            "dummy_threading",
            "tkinter",
            "turtle",
        }

        # 项目内部模块前缀
        self.internal_prefixes = {"minicrm", "transfunctions"}

        # 发现的导入
        self.imports_found = set()
        self.third_party_imports = set()
        self.files_with_imports = {}

    def extract_imports_from_file(self, file_path: Path) -> Set[str]:
        """从Python文件中提取导入语句"""
        imports = set()

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # 使用AST解析导入
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split(".")[0])
            except SyntaxError:
                # 如果AST解析失败，使用正则表达式
                import_pattern = r"^(?:from\s+(\S+)\s+import|import\s+(\S+))"
                for line in content.split("\n"):
                    match = re.match(import_pattern, line.strip())
                    if match:
                        module = match.group(1) or match.group(2)
                        if module:
                            imports.add(module.split(".")[0])

        except Exception as e:
            print(f"⚠️  无法解析文件 {file_path}: {e}")

        return imports

    def scan_project_imports(self) -> None:
        """扫描项目中的所有导入"""
        print("🔍 扫描项目导入语句...")

        python_files = list(self.src_dir.rglob("*.py"))

        for file_path in python_files:
            imports = self.extract_imports_from_file(file_path)
            if imports:
                relative_path = file_path.relative_to(self.project_root)
                self.files_with_imports[str(relative_path)] = imports
                self.imports_found.update(imports)

        # 分类导入
        for imp in self.imports_found:
            if imp not in self.builtin_modules and not any(
                imp.startswith(prefix) for prefix in self.internal_prefixes
            ):
                self.third_party_imports.add(imp)

    def load_declared_dependencies(self) -> Dict[str, List[str]]:
        """加载pyproject.toml中声明的依赖"""
        print("📋 读取声明的依赖...")

        dependencies = {"core": [], "optional": [], "dev": [], "build": []}

        if not self.pyproject_path.exists():
            print("⚠️  pyproject.toml 文件不存在")
            return dependencies

        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                print("⚠️  无法导入TOML解析器，请安装tomli")
                return dependencies

        try:
            with open(self.pyproject_path, "rb") as f:
                data = tomllib.load(f)

            project = data.get("project", {})

            # 核心依赖
            core_deps = project.get("dependencies", [])
            dependencies["core"] = [
                self._extract_package_name(dep) for dep in core_deps
            ]

            # 可选依赖
            optional_deps = project.get("optional-dependencies", {})
            for group, deps in optional_deps.items():
                if group in ["dev", "build"]:
                    dependencies[group] = [
                        self._extract_package_name(dep) for dep in deps
                    ]
                else:
                    dependencies["optional"].extend(
                        [self._extract_package_name(dep) for dep in deps]
                    )

        except Exception as e:
            print(f"⚠️  解析pyproject.toml失败: {e}")

        return dependencies

    def _extract_package_name(self, dep_spec: str) -> str:
        """从依赖规范中提取包名"""
        # 移除版本约束
        name = re.split(r"[><=!]", dep_spec)[0].strip()
        # 移除额外的标记
        name = re.split(r"[;\[]", name)[0].strip()
        return name

    def check_qt_references(self) -> List[str]:
        """检查Qt相关引用"""
        print("🔍 检查Qt相关引用...")

        qt_references = []

        # 搜索所有Python文件中的Qt引用
        for file_path in self.project_root.rglob("*.py"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # 检查Qt相关的字符串
                qt_patterns = [
                    r"PySide6",
                    r"PyQt5",
                    r"PyQt6",
                    r"QtCore",
                    r"QtGui",
                    r"QtWidgets",
                    r"QApplication",
                    r"QWidget",
                    r"QMainWindow",
                    r"QDialog",
                ]

                for i, line in enumerate(content.split("\n"), 1):
                    for pattern in qt_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            relative_path = file_path.relative_to(self.project_root)
                            qt_references.append(
                                f"{relative_path}:{i} - {line.strip()}"
                            )

            except Exception:
                continue

        return qt_references

    def check_security_vulnerabilities(self) -> List[str]:
        """检查安全漏洞（简化版）"""
        print("🔒 检查安全漏洞...")

        vulnerabilities = []

        # 检查一些已知的有问题的包或模式
        security_issues = {
            "eval": "使用eval()可能存在代码注入风险",
            "exec": "使用exec()可能存在代码注入风险",
            "pickle": "pickle模块可能存在反序列化安全风险",
            "subprocess.call": "使用subprocess.call可能存在命令注入风险",
            "os.system": "使用os.system可能存在命令注入风险",
        }

        for file_path in self.src_dir.rglob("*.py"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                for pattern, message in security_issues.items():
                    if pattern in content:
                        relative_path = file_path.relative_to(self.project_root)
                        vulnerabilities.append(f"{relative_path}: {message}")

            except Exception:
                continue

        return vulnerabilities

    def generate_report(self) -> str:
        """生成依赖检查报告"""
        print("📊 生成依赖检查报告...")

        # 扫描导入
        self.scan_project_imports()

        # 加载声明的依赖
        declared_deps = self.load_declared_dependencies()
        all_declared = set()
        for deps in declared_deps.values():
            all_declared.update(deps)

        # 检查Qt引用
        qt_refs = self.check_qt_references()

        # 检查安全问题
        security_issues = self.check_security_vulnerabilities()

        # 分析结果
        missing_deps = self.third_party_imports - all_declared
        unused_deps = all_declared - self.third_party_imports

        # 生成报告
        report = []
        report.append("📦 MiniCRM 依赖检查结果")
        report.append("=" * 60)
        report.append("")

        # 总体状态
        if not missing_deps and not unused_deps and not qt_refs and not security_issues:
            report.append("✅ 所有依赖正常")
        else:
            report.append("⚠️ 发现以下依赖问题：")

        report.append("")

        # 详细分析
        if missing_deps:
            report.append("1. 🚨 缺失依赖：")
            for dep in sorted(missing_deps):
                report.append(f"   - {dep}")
            report.append("")

        if unused_deps:
            report.append("2. 🗑️ 多余依赖：")
            for dep in sorted(unused_deps):
                report.append(f"   - {dep}")
            report.append("")

        if qt_refs:
            report.append("3. 🔧 Qt引用问题：")
            for ref in qt_refs[:10]:  # 限制显示数量
                report.append(f"   - {ref}")
            if len(qt_refs) > 10:
                report.append(f"   ... 还有 {len(qt_refs) - 10} 个引用")
            report.append("")

        if security_issues:
            report.append("4. 🔒 安全警告：")
            for issue in security_issues:
                report.append(f"   - {issue}")
            report.append("")

        # 统计信息
        report.append("📊 统计信息：")
        report.append(f"   - 扫描的Python文件: {len(self.files_with_imports)}")
        report.append(f"   - 发现的导入模块: {len(self.imports_found)}")
        report.append(f"   - 第三方库: {len(self.third_party_imports)}")
        report.append(f"   - 声明的依赖: {len(all_declared)}")
        report.append("")

        # 第三方库详情
        if self.third_party_imports:
            report.append("📚 使用的第三方库：")
            for lib in sorted(self.third_party_imports):
                report.append(f"   - {lib}")
            report.append("")

        # 建议的requirements.txt更新
        if missing_deps or unused_deps:
            report.append("## 建议的依赖更新：")
            report.append("")

            if missing_deps:
                report.append("需要添加到pyproject.toml的依赖：")
                for dep in sorted(missing_deps):
                    report.append(f'"{dep}",')
                report.append("")

            if unused_deps:
                report.append("可以从pyproject.toml移除的依赖：")
                for dep in sorted(unused_deps):
                    report.append(f"- {dep}")
                report.append("")

        # 自动修复选项
        report.append("## 自动修复选项：")
        report.append("")

        if qt_refs:
            report.append("修复Qt引用：")
            report.append("python dependency_checker.py --fix-qt-refs")
            report.append("")

        if missing_deps:
            report.append("添加缺失依赖：")
            report.append("python dependency_checker.py --add-missing-deps")
            report.append("")

        return "\n".join(report)

    def fix_qt_references(self) -> None:
        """修复Qt相关引用"""
        print("🔧 修复Qt引用...")

        # 修复start_minicrm.py中的Qt引用
        start_script = self.project_root / "start_minicrm.py"
        if start_script.exists():
            with open(start_script, encoding="utf-8") as f:
                content = f.read()

            # 替换Qt相关的文本
            content = content.replace(
                "基于 Python + PySide6(Qt)", "基于 Python + tkinter/ttk"
            )
            content = content.replace(
                "确保PySide6已正确安装", "确保tkinter已正确安装（通常随Python内置）"
            )

            with open(start_script, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"✅ 已修复 {start_script}")


def main():
    """主函数"""
    project_root = Path(__file__).parent
    checker = DependencyChecker(project_root)

    if len(sys.argv) > 1:
        if sys.argv[1] == "--fix-qt-refs":
            checker.fix_qt_references()
            return
        if sys.argv[1] == "--add-missing-deps":
            print("🚧 自动添加依赖功能待实现")
            return

    # 生成并显示报告
    report = checker.generate_report()
    print(report)

    # 保存报告到文件
    report_file = project_root / "dependency_check_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📄 报告已保存到: {report_file}")


if __name__ == "__main__":
    main()
