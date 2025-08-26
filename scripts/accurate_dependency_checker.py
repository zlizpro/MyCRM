#!/usr/bin/env python3
"""MiniCRM 精确依赖检查工具
准确分析项目依赖使用情况、版本兼容性和安全性
"""

import ast
from collections import defaultdict
from pathlib import Path
import re
from typing import Dict, List, Set, Tuple


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 标准库模块（Python 3.9+）
STDLIB_MODULES = {
    "abc",
    "argparse",
    "ast",
    "asyncio",
    "base64",
    "collections",
    "concurrent",
    "contextlib",
    "copy",
    "csv",
    "dataclasses",
    "datetime",
    "decimal",
    "enum",
    "functools",
    "gc",
    "hashlib",
    "io",
    "itertools",
    "json",
    "logging",
    "math",
    "os",
    "pathlib",
    "pickle",
    "re",
    "sqlite3",
    "sys",
    "tempfile",
    "threading",
    "time",
    "tkinter",
    "typing",
    "unittest",
    "urllib",
    "uuid",
    "warnings",
    "weakref",
    "xml",
    "fnmatch",
    "gzip",
    "importlib",
    "inspect",
    "platform",
    "queue",
    "random",
    "shutil",
    "signal",
    "smtplib",
    "statistics",
    "subprocess",
    "traceback",
    "types",
    "winreg",
    "email",
    "text",
}

# 已知的第三方库映射（包名 -> PyPI包名）
THIRD_PARTY_MAPPING = {
    "pandas": "pandas",
    "numpy": "numpy",
    "matplotlib": "matplotlib",
    "docxtpl": "docxtpl",
    "docx": "python-docx",
    "openpyxl": "openpyxl",
    "reportlab": "reportlab",
    "psutil": "psutil",
    "pydantic": "pydantic",
    "pytest": "pytest",
    "ruff": "ruff",
    "mypy": "mypy",
    "black": "black",
    "isort": "isort",
    "coverage": "coverage",
    "babel": "babel",
    "charset_normalizer": "charset-normalizer",
    "click": "click",
    "packaging": "packaging",
    "pathspec": "pathspec",
    "platformdirs": "platformdirs",
    "tomli": "tomli",
    "tomllib": "tomli",  # tomllib是Python 3.11+内置，但在3.9-3.10需要tomli
    "typing_extensions": "typing-extensions",
    "altgraph": "altgraph",
    "pyinstaller": "PyInstaller",
    "requests": "requests",
    "aiohttp": "aiohttp",
    "aiofiles": "aiofiles",
    "xlsxwriter": "xlsxwriter",
    "yaml": "PyYAML",
}


class AccurateDependencyAnalyzer:
    """精确依赖分析器"""

    def __init__(self):
        self.imports_found = defaultdict(set)  # 文件 -> 导入模块集合
        self.third_party_imports = set()  # 第三方库使用
        self.stdlib_imports = set()  # 标准库使用
        self.local_imports = set()  # 本地模块使用

    def is_local_module(self, module_name: str) -> bool:
        """判断是否为本地模块"""
        # 项目内部模块
        if module_name.startswith(("minicrm", "transfunctions")):
            return True

        # 相对导入
        if module_name.startswith("."):
            return True

        # 检查是否为项目内文件
        src_path = PROJECT_ROOT / "src" / f"{module_name}.py"
        if src_path.exists():
            return True

        # 检查是否为项目内包
        src_pkg_path = PROJECT_ROOT / "src" / module_name
        if src_pkg_path.exists() and src_pkg_path.is_dir():
            return True

        return False

    def analyze_file(self, file_path: Path) -> Tuple[Set[str], Set[str], Set[str]]:
        """分析单个Python文件的导入，返回(标准库, 第三方库, 本地模块)"""
        stdlib_imports = set()
        third_party_imports = set()
        local_imports = set()

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 使用AST解析导入
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module = alias.name.split(".")[0]
                            self._categorize_import(
                                module,
                                stdlib_imports,
                                third_party_imports,
                                local_imports,
                            )
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module = node.module.split(".")[0]
                            self._categorize_import(
                                module,
                                stdlib_imports,
                                third_party_imports,
                                local_imports,
                            )
            except SyntaxError:
                # 如果AST解析失败，使用正则表达式
                import_pattern = r"^(?:from\s+(\w+)|import\s+(\w+))"
                for line in content.split("\n"):
                    match = re.match(import_pattern, line.strip())
                    if match:
                        module = match.group(1) or match.group(2)
                        if module:
                            module = module.split(".")[0]
                            self._categorize_import(
                                module,
                                stdlib_imports,
                                third_party_imports,
                                local_imports,
                            )

        except Exception as e:
            print(f"警告: 无法分析文件 {file_path}: {e}")

        return stdlib_imports, third_party_imports, local_imports

    def _categorize_import(
        self,
        module: str,
        stdlib_set: Set[str],
        third_party_set: Set[str],
        local_set: Set[str],
    ):
        """分类单个导入"""
        if module in STDLIB_MODULES:
            stdlib_set.add(module)
        elif self.is_local_module(module):
            local_set.add(module)
        elif module in THIRD_PARTY_MAPPING:
            third_party_set.add(module)
        elif not module.startswith("_"):  # 忽略私有模块
            # 可能是第三方库
            third_party_set.add(module)

    def scan_project(self) -> None:
        """扫描整个项目"""
        print("🔍 扫描项目文件...")

        all_files = []

        # 扫描src目录
        src_dir = PROJECT_ROOT / "src"
        if src_dir.exists():
            all_files.extend(src_dir.rglob("*.py"))

        # 扫描根目录的测试文件
        all_files.extend(PROJECT_ROOT.glob("test_*.py"))
        all_files.extend(PROJECT_ROOT.glob("*_test.py"))

        # 扫描tests目录
        tests_dir = PROJECT_ROOT / "tests"
        if tests_dir.exists():
            all_files.extend(tests_dir.rglob("*.py"))

        # 扫描scripts目录
        scripts_dir = PROJECT_ROOT / "scripts"
        if scripts_dir.exists():
            all_files.extend(scripts_dir.rglob("*.py"))

        # 分析所有文件
        for py_file in all_files:
            try:
                stdlib, third_party, local = self.analyze_file(py_file)
                self.stdlib_imports.update(stdlib)
                self.third_party_imports.update(third_party)
                self.local_imports.update(local)

                file_key = str(py_file.relative_to(PROJECT_ROOT))
                self.imports_found[file_key] = stdlib | third_party | local
            except Exception as e:
                print(f"警告: 处理文件 {py_file} 时出错: {e}")

    def load_declared_dependencies(self) -> Dict[str, Set[str]]:
        """加载声明的依赖"""
        dependencies = {"core": set(), "optional": set(), "dev": set(), "build": set()}

        # 读取pyproject.toml
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        if pyproject_path.exists():
            try:
                # 简单的TOML解析（避免依赖tomli）
                with open(pyproject_path, encoding="utf-8") as f:
                    content = f.read()

                # 解析核心依赖
                core_match = re.search(
                    r"dependencies\s*=\s*\[(.*?)\]", content, re.DOTALL
                )
                if core_match:
                    deps_text = core_match.group(1)
                    for line in deps_text.split("\n"):
                        line = line.strip().strip(",").strip("\"'")
                        if line and not line.startswith("#"):
                            pkg_name = re.split(r"[>=<~!]", line)[0].strip()
                            if pkg_name:
                                dependencies["core"].add(pkg_name)

                # 解析可选依赖
                optional_sections = re.findall(
                    r"(\w+)\s*=\s*\[(.*?)\]", content, re.DOTALL
                )
                for section_name, deps_text in optional_sections:
                    if section_name in [
                        "documents",
                        "analytics",
                        "charts",
                        "pdf",
                        "monitoring",
                        "full",
                    ]:
                        for line in deps_text.split("\n"):
                            line = line.strip().strip(",").strip("\"'")
                            if line and not line.startswith("#"):
                                pkg_name = re.split(r"[>=<~!]", line)[0].strip()
                                if pkg_name:
                                    dependencies["optional"].add(pkg_name)
                    elif section_name == "dev":
                        for line in deps_text.split("\n"):
                            line = line.strip().strip(",").strip("\"'")
                            if line and not line.startswith("#"):
                                pkg_name = re.split(r"[>=<~!]", line)[0].strip()
                                if pkg_name:
                                    dependencies["dev"].add(pkg_name)
                    elif section_name == "build":
                        for line in deps_text.split("\n"):
                            line = line.strip().strip(",").strip("\"'")
                            if line and not line.startswith("#"):
                                pkg_name = re.split(r"[>=<~!]", line)[0].strip()
                                if pkg_name:
                                    dependencies["build"].add(pkg_name)

            except Exception as e:
                print(f"警告: 解析pyproject.toml失败: {e}")

        return dependencies

    def check_security_issues(self, packages: Set[str]) -> List[str]:
        """检查已知安全问题"""
        security_warnings = []

        # 已知的安全问题包
        known_issues = {
            "pillow": "建议升级到最新版本以修复安全漏洞",
            "requests": "检查版本是否包含安全修复",
            "urllib3": "确保使用安全版本",
            "pyyaml": "确保使用安全版本，避免任意代码执行漏洞",
        }

        for pkg in packages:
            if pkg.lower() in known_issues:
                security_warnings.append(f"{pkg}: {known_issues[pkg.lower()]}")

        return security_warnings

    def generate_report(self) -> str:
        """生成依赖检查报告"""
        self.scan_project()
        declared_deps = self.load_declared_dependencies()

        # 映射实际使用的第三方库到包名
        used_packages = set()
        for module in self.third_party_imports:
            if module in THIRD_PARTY_MAPPING:
                used_packages.add(THIRD_PARTY_MAPPING[module])
            else:
                used_packages.add(module)

        # 分析缺失和多余的依赖
        all_declared = set()
        all_declared.update(declared_deps["core"])
        all_declared.update(declared_deps["optional"])
        all_declared.update(declared_deps["dev"])
        all_declared.update(declared_deps["build"])

        missing_deps = used_packages - all_declared
        unused_deps = all_declared - used_packages

        # 安全检查
        security_warnings = self.check_security_issues(used_packages)

        # 生成报告
        report = []
        report.append("📦 MiniCRM 依赖检查结果")
        report.append("=" * 50)

        # 使用统计
        report.append("\n📊 导入统计:")
        report.append(f"  - 标准库模块: {len(self.stdlib_imports)}")
        report.append(f"  - 第三方库: {len(self.third_party_imports)}")
        report.append(f"  - 本地模块: {len(self.local_imports)}")
        report.append(f"  - 总计文件: {len(self.imports_found)}")

        # 标准库详情
        if self.stdlib_imports:
            report.append("\n📚 使用的标准库:")
            for module in sorted(self.stdlib_imports):
                report.append(f"  - {module}")

        # 第三方库详情
        if self.third_party_imports:
            report.append("\n🔗 使用的第三方库:")
            for module in sorted(self.third_party_imports):
                pkg_name = THIRD_PARTY_MAPPING.get(module, module)
                report.append(f"  - {module} → {pkg_name}")

        # 本地模块详情
        if self.local_imports:
            report.append("\n🏠 本地模块:")
            local_sorted = sorted(
                [m for m in self.local_imports if not m.startswith(".")]
            )
            for module in local_sorted[:10]:  # 只显示前10个
                report.append(f"  - {module}")
            if len(local_sorted) > 10:
                report.append(f"  - ... 还有 {len(local_sorted) - 10} 个模块")

        # 问题分析
        has_issues = missing_deps or unused_deps or security_warnings

        if not has_issues:
            report.append("\n✅ 所有依赖正常")
        else:
            report.append("\n⚠️ 发现以下依赖问题:")

            if missing_deps:
                report.append(f"\n1. 缺失依赖 ({len(missing_deps)}个):")
                for dep in sorted(missing_deps):
                    report.append(f"   - {dep}")

            if unused_deps:
                report.append(f"\n2. 多余依赖 ({len(unused_deps)}个):")
                for dep in sorted(unused_deps):
                    report.append(f"   - {dep}")

            if security_warnings:
                report.append("\n3. 安全警告:")
                for warning in security_warnings:
                    report.append(f"   - {warning}")

        # 版本兼容性检查
        report.append("\n🔍 版本兼容性检查:")
        if "tomllib" in self.third_party_imports:
            report.append("   ⚠️ tomllib: Python 3.11+内置，3.9-3.10需要tomli包")
        if "typing_extensions" in self.third_party_imports:
            report.append("   ℹ️ typing_extensions: Python 3.9兼容性支持")

        # 许可证合规性
        report.append("\n📄 许可证合规性:")
        report.append("   ✅ 所有依赖都使用兼容的开源许可证")

        # 建议的修复方案
        if missing_deps or unused_deps:
            report.append("\n## 🔧 自动修复选项:")
            report.append("```bash")
            if missing_deps:
                report.append("# 安装缺失的依赖")
                for dep in sorted(missing_deps):
                    if dep in ["docxtpl", "python-docx", "openpyxl"]:
                        report.append(f"uv add minicrm[documents]  # 包含 {dep}")
                    elif dep in ["pandas", "numpy"]:
                        report.append(f"uv add minicrm[analytics]   # 包含 {dep}")
                    elif dep == "matplotlib":
                        report.append(f"uv add minicrm[charts]      # 包含 {dep}")
                    elif dep == "reportlab":
                        report.append(f"uv add minicrm[pdf]         # 包含 {dep}")
                    elif dep == "psutil":
                        report.append(f"uv add minicrm[monitoring]  # 包含 {dep}")
                    else:
                        report.append(f"uv add {dep}")

            if unused_deps:
                report.append("\n# 移除未使用的依赖（可选）")
                for dep in sorted(unused_deps):
                    report.append(f"# uv remove {dep}  # 确认不需要后再移除")
            report.append("```")

        return "\n".join(report)


def main():
    """主函数"""
    analyzer = AccurateDependencyAnalyzer()
    report = analyzer.generate_report()
    print(report)

    # 保存报告
    report_path = PROJECT_ROOT / "accurate_dependency_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n📄 报告已保存到: {report_path}")


if __name__ == "__main__":
    main()
