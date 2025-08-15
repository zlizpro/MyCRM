#!/usr/bin/env python3
"""
MiniCRM 架构约束检查脚本

验证项目是否遵循分层架构原则：
- UI层 → Services层 → Data层 → Models层 → Core层
- 只能向下层依赖，禁止跨层或向上依赖
- 检查循环依赖
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set


class ArchitectureChecker:
    """架构约束检查器"""

    def __init__(self, src_path: Path):
        self.src_path = src_path
        self.layers = {"ui": 5, "services": 4, "data": 3, "models": 2, "core": 1}
        self.dependencies: Dict[str, Set[str]] = {}
        self.violations: List[str] = []
        # 应用程序入口点，可以依赖任何层
        self.entry_points = {"minicrm.main", "minicrm.application"}

    def check_architecture(self) -> bool:
        """检查架构约束"""
        print("🔍 开始架构约束检查...")

        # 扫描所有Python文件
        self._scan_dependencies()

        # 检查分层约束
        self._check_layer_constraints()

        # 检查循环依赖
        self._check_circular_dependencies()

        # 输出结果
        self._print_results()

        return len(self.violations) == 0

    def _scan_dependencies(self):
        """扫描依赖关系"""
        minicrm_path = self.src_path / "minicrm"

        for py_file in minicrm_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            module_path = self._get_module_path(py_file)
            self.dependencies[module_path] = set()

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith("minicrm"):
                            self.dependencies[module_path].add(node.module)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.startswith("minicrm"):
                                self.dependencies[module_path].add(alias.name)

            except Exception as e:
                print(f"⚠️  解析文件失败: {py_file} - {e}")

    def _get_module_path(self, file_path: Path) -> str:
        """获取模块路径"""
        relative_path = file_path.relative_to(self.src_path)
        module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
        return ".".join(module_parts)

    def _get_layer(self, module: str) -> int:
        """获取模块所属层级"""
        parts = module.split(".")
        if len(parts) >= 2 and parts[0] == "minicrm":
            layer_name = parts[1]
            return self.layers.get(layer_name, 0)
        return 0

    def _check_layer_constraints(self):
        """检查分层约束"""
        print("📋 检查分层约束...")

        for module, deps in self.dependencies.items():
            # 跳过入口点模块的检查
            if module in self.entry_points:
                continue

            module_layer = self._get_layer(module)

            for dep in deps:
                dep_layer = self._get_layer(dep)

                # 只能向下层依赖
                if dep_layer > module_layer:
                    violation = f"违反分层约束: {module} (层级{module_layer}) 依赖了 {dep} (层级{dep_layer})"
                    self.violations.append(violation)

    def _check_circular_dependencies(self):
        """检查循环依赖"""
        print("🔄 检查循环依赖...")

        visited = set()
        rec_stack = set()

        def has_cycle(module: str) -> bool:
            if module in rec_stack:
                return True
            if module in visited:
                return False

            visited.add(module)
            rec_stack.add(module)

            for dep in self.dependencies.get(module, set()):
                if has_cycle(dep):
                    return True

            rec_stack.remove(module)
            return False

        for module in self.dependencies:
            if module not in visited:
                if has_cycle(module):
                    self.violations.append(f"检测到循环依赖，涉及模块: {module}")

    def _print_results(self):
        """输出检查结果"""
        print("\n" + "=" * 60)
        print("📊 架构检查结果")
        print("=" * 60)

        if not self.violations:
            print("✅ 架构检查通过！所有约束都得到遵守。")
        else:
            print(f"❌ 发现 {len(self.violations)} 个架构违规:")
            for i, violation in enumerate(self.violations, 1):
                print(f"  {i}. {violation}")

        print(f"\n📈 统计信息:")
        print(f"  - 扫描模块数: {len(self.dependencies)}")
        print(
            f"  - 依赖关系数: {sum(len(deps) for deps in self.dependencies.values())}"
        )
        print(f"  - 违规数量: {len(self.violations)}")


def main():
    """主函数"""
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    src_path = project_root / "src"

    if not src_path.exists():
        print("❌ 找不到src目录")
        sys.exit(1)

    # 执行架构检查
    checker = ArchitectureChecker(src_path)
    success = checker.check_architecture()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
