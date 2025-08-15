"""
MiniCRM 架构验证工具

验证系统架构是否符合分层架构和SOLID原则：
- 检查依赖方向是否正确
- 验证单一职责原则
- 检查接口隔离原则
- 验证依赖倒置原则
"""

import ast
import logging
from pathlib import Path


class ArchitectureValidator:
    """
    架构验证器

    验证系统架构是否符合设计原则
    """

    def __init__(self, project_root: str):
        """
        初始化架构验证器

        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(__name__)

        # 定义层级结构
        self.layers: dict[str, dict[str, str | int]] = {
            "ui": {"path": "src/minicrm/ui", "level": 4},
            "services": {"path": "src/minicrm/services", "level": 3},
            "data": {"path": "src/minicrm/data", "level": 2},
            "models": {"path": "src/minicrm/models", "level": 1},
            "core": {"path": "src/minicrm/core", "level": 0},
        }

        # 允许的依赖关系（高层可以依赖低层）
        self.allowed_dependencies = {
            "ui": ["services", "core"],
            "services": ["data", "models", "core"],
            "data": ["models", "core"],
            "models": ["core"],
            "core": [],
        }

    def validate_architecture(self) -> dict[str, list[str]]:
        """
        验证整体架构

        Returns:
            Dict[str, List[str]]: 验证结果，包含错误和警告
        """
        results: dict[str, list[str]] = {"errors": [], "warnings": [], "info": []}

        try:
            # 1. 验证依赖方向
            dependency_errors = self._validate_dependency_direction()
            results["errors"].extend(dependency_errors)

            # 2. 验证单一职责原则
            srp_warnings = self._validate_single_responsibility()
            results["warnings"].extend(srp_warnings)

            # 3. 验证接口使用
            interface_warnings = self._validate_interface_usage()
            results["warnings"].extend(interface_warnings)

            # 4. 验证文件大小
            size_warnings = self._validate_file_sizes()
            results["warnings"].extend(size_warnings)

            if not results["errors"]:
                results["info"].append("✅ 架构验证通过 - 依赖方向正确")

            self.logger.info(
                f"架构验证完成: {len(results['errors'])} 错误, {len(results['warnings'])} 警告"
            )

        except Exception as e:
            results["errors"].append(f"架构验证失败: {e}")
            self.logger.error(f"架构验证失败: {e}")

        return results

    def _validate_dependency_direction(self) -> list[str]:
        """验证依赖方向是否正确"""
        errors = []

        for layer_name, layer_info in self.layers.items():
            layer_path = self.project_root / str(layer_info["path"])
            if not layer_path.exists():
                continue

            # 分析该层的所有Python文件
            for py_file in layer_path.rglob("*.py"):
                if py_file.name == "__init__.py":
                    continue

                try:
                    imports = self._extract_imports(py_file)
                    invalid_imports = self._check_layer_imports(layer_name, imports)

                    for invalid_import in invalid_imports:
                        errors.append(
                            f"❌ 依赖方向错误: {py_file.relative_to(self.project_root)} "
                            f"不应该导入 {invalid_import}"
                        )

                except Exception as e:
                    self.logger.warning(f"分析文件失败 {py_file}: {e}")

        return errors

    def _validate_single_responsibility(self) -> list[str]:
        """验证单一职责原则"""
        warnings = []

        for _layer_name, layer_info in self.layers.items():
            layer_path = self.project_root / str(layer_info["path"])
            if not layer_path.exists():
                continue

            for py_file in layer_path.rglob("*.py"):
                if py_file.name == "__init__.py":
                    continue

                try:
                    # 检查类的职责数量
                    classes = self._extract_classes(py_file)
                    for class_name, methods in classes.items():
                        if len(methods) > 15:  # 方法过多可能违反SRP
                            warnings.append(
                                f"⚠️ 可能违反单一职责原则: {py_file.relative_to(self.project_root)} "
                                f"中的类 {class_name} 有 {len(methods)} 个方法"
                            )

                except Exception as e:
                    self.logger.warning(f"分析类失败 {py_file}: {e}")

        return warnings

    def _validate_interface_usage(self) -> list[str]:
        """验证接口使用情况"""
        warnings = []

        # 检查Services层是否实现了接口
        services_path = self.project_root / "src/minicrm/services"
        if services_path.exists():
            for py_file in services_path.rglob("*.py"):
                if py_file.name == "__init__.py":
                    continue

                try:
                    content = py_file.read_text(encoding="utf-8")

                    # 检查是否导入了接口
                    if "from minicrm.core.interfaces" not in content:
                        warnings.append(
                            f"⚠️ 建议使用接口: {py_file.relative_to(self.project_root)} "
                            f"应该实现相应的接口"
                        )

                except Exception as e:
                    self.logger.warning(f"检查接口使用失败 {py_file}: {e}")

        return warnings

    def _validate_file_sizes(self) -> list[str]:
        """验证文件大小是否合理"""
        warnings = []

        # 文件大小限制
        size_limits = {
            "ui": 400,  # UI组件可以稍大
            "services": 300,  # 业务逻辑适中
            "data": 250,  # 数据访问较小
            "models": 200,  # 模型最小
            "core": 300,  # 核心工具适中
        }

        for layer_name, layer_info in self.layers.items():
            layer_path = self.project_root / str(layer_info["path"])
            if not layer_path.exists():
                continue

            limit = size_limits.get(layer_name, 200)

            for py_file in layer_path.rglob("*.py"):
                if py_file.name == "__init__.py":
                    continue

                try:
                    lines = len(py_file.read_text(encoding="utf-8").splitlines())
                    if lines > limit:
                        warnings.append(
                            f"⚠️ 文件过大: {py_file.relative_to(self.project_root)} "
                            f"有 {lines} 行，建议不超过 {limit} 行"
                        )

                except Exception as e:
                    self.logger.warning(f"检查文件大小失败 {py_file}: {e}")

        return warnings

    def _extract_imports(self, file_path: Path) -> list[str]:
        """提取文件中的导入语句"""
        imports = []

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

        except Exception as e:
            self.logger.warning(f"提取导入失败 {file_path}: {e}")

        return imports

    def _extract_classes(self, file_path: Path) -> dict[str, list[str]]:
        """提取文件中的类和方法"""
        classes = {}

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(item.name)
                    classes[node.name] = methods

        except Exception as e:
            self.logger.warning(f"提取类失败 {file_path}: {e}")

        return classes

    def _check_layer_imports(self, layer_name: str, imports: list[str]) -> list[str]:
        """检查层级导入是否合法"""
        invalid_imports = []
        allowed = self.allowed_dependencies.get(layer_name, [])
        current_level = int(self.layers[layer_name]["level"])

        for import_name in imports:
            if not import_name.startswith("minicrm."):
                continue

            # 确定导入的层级
            import_layer = self._get_import_layer(import_name)
            if not import_layer:
                continue

            import_level = int(self.layers[import_layer]["level"])

            # 检查是否违反依赖方向（高层不能依赖更高层）
            if import_level > current_level:
                invalid_imports.append(import_name)

            # 检查是否在允许的依赖列表中
            elif import_layer not in allowed:
                invalid_imports.append(import_name)

        return invalid_imports

    def _get_import_layer(self, import_name: str) -> str:
        """根据导入名称确定所属层级"""
        for layer_name, _layer_info in self.layers.items():
            layer_module = f"minicrm.{layer_name}"
            if import_name.startswith(layer_module):
                return layer_name
        return None

    def generate_report(self, results: dict[str, list[str]]) -> str:
        """生成架构验证报告"""
        report = []
        report.append("# MiniCRM 架构验证报告")
        report.append("")
        report.append(f"生成时间: {self._get_current_time()}")
        report.append("")

        # 错误部分
        if results["errors"]:
            report.append("## ❌ 架构错误")
            report.append("")
            for error in results["errors"]:
                report.append(f"- {error}")
            report.append("")

        # 警告部分
        if results["warnings"]:
            report.append("## ⚠️ 架构警告")
            report.append("")
            for warning in results["warnings"]:
                report.append(f"- {warning}")
            report.append("")

        # 信息部分
        if results["info"]:
            report.append("## ℹ️ 验证信息")
            report.append("")
            for info in results["info"]:
                report.append(f"- {info}")
            report.append("")

        # 总结
        report.append("## 📊 验证总结")
        report.append("")
        report.append(f"- 错误数量: {len(results['errors'])}")
        report.append(f"- 警告数量: {len(results['warnings'])}")
        report.append(f"- 信息数量: {len(results['info'])}")

        if not results["errors"]:
            report.append("")
            report.append("✅ **架构验证通过！系统遵循分层架构和SOLID原则。**")
        else:
            report.append("")
            report.append("❌ **架构验证失败！请修复上述错误。**")

        return "\n".join(report)

    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validate_architecture(project_root: str = ".") -> dict[str, list[str]]:
    """
    验证项目架构

    Args:
        project_root: 项目根目录

    Returns:
        Dict[str, List[str]]: 验证结果
    """
    validator = ArchitectureValidator(project_root)
    return validator.validate_architecture()


def generate_architecture_report(project_root: str = ".") -> str:
    """
    生成架构验证报告

    Args:
        project_root: 项目根目录

    Returns:
        str: 报告内容
    """
    validator = ArchitectureValidator(project_root)
    results = validator.validate_architecture()
    return validator.generate_report(results)


if __name__ == "__main__":
    # 运行架构验证
    results = validate_architecture()

    # 打印结果
    for error in results["errors"]:
        print(error)

    for warning in results["warnings"]:
        print(warning)

    for info in results["info"]:
        print(info)

    # 生成报告
    report = generate_architecture_report()
    with open("architecture_validation_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("\n报告已生成: architecture_validation_report.md")
    print(f"错误: {len(results['errors'])}, 警告: {len(results['warnings'])}")
