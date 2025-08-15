#!/usr/bin/env python3
"""
拆分 responsive_layout.py 文件

将超大的响应式布局文件拆分为符合MiniCRM模块化标准的多个文件。
"""

import re
from pathlib import Path


class ResponsiveLayoutSplitter:
    """响应式布局文件拆分器"""

    def __init__(self, source_file: str):
        self.source_file = Path(source_file)
        self.target_dir = Path("src/minicrm/ui/responsive")
        self.content = ""

    def read_source_file(self) -> None:
        """读取源文件"""
        if not self.source_file.exists():
            raise FileNotFoundError(f"源文件不存在: {self.source_file}")

        self.content = self.source_file.read_text(encoding="utf-8")
        print(f"📖 读取源文件: {self.source_file} ({len(self.content.splitlines())}行)")

    def create_target_directory(self) -> None:
        """创建目标目录"""
        self.target_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 创建目录: {self.target_dir}")

    def extract_common_imports(self) -> str:
        """提取通用导入"""
        import_lines = []
        lines = self.content.split("\n")

        for line in lines:
            if (
                line.startswith("import ")
                or line.startswith("from ")
                or line.startswith('"""')
                or line.strip() == ""
                or line.startswith("#")
            ):
                import_lines.append(line)
            else:
                break

        return "\n".join(import_lines)

    def extract_class_content(self, class_name: str) -> str:
        """提取指定类的内容"""
        pattern = rf"class {class_name}.*?(?=\n\nclass|\n\n# |$)"
        match = re.search(pattern, self.content, re.DOTALL)

        if match:
            return match.group(0)
        return ""

    def extract_enums_and_dataclasses(self) -> str:
        """提取枚举和数据类"""
        patterns = [
            r"class ScreenSize\(Enum\):.*?(?=\n\n@|\n\nclass|\n\n# |$)",
            r"@dataclass\nclass BreakPoint:.*?(?=\n\n@|\n\nclass|\n\n# |$)",
            r"@dataclass\nclass LayoutConfig:.*?(?=\n\n@|\n\nclass|\n\n# |$)",
        ]

        content_parts = []
        for pattern in patterns:
            match = re.search(pattern, self.content, re.DOTALL)
            if match:
                content_parts.append(match.group(0))

        return "\n\n".join(content_parts)

    def create_file(self, filename: str, content: str, description: str) -> None:
        """创建文件"""
        file_path = self.target_dir / filename

        # 添加文件头注释
        header = f'"""\n{description}\n\n从 responsive_layout.py 拆分而来，符合MiniCRM模块化标准。\n"""\n\n'

        full_content = header + content

        file_path.write_text(full_content, encoding="utf-8")
        lines = len(full_content.splitlines())
        print(f"✅ 创建文件: {filename} ({lines}行)")

        # 检查文件大小是否符合标准
        if lines > 400:
            print(f"⚠️  警告: {filename} 仍然较大 ({lines}行)，可能需要进一步拆分")

    def split_files(self) -> None:
        """拆分文件"""
        common_imports = self.extract_common_imports()

        # 1. 创建类型定义文件
        types_content = common_imports + "\n\n" + self.extract_enums_and_dataclasses()
        self.create_file(
            "types.py",
            types_content,
            "MiniCRM 响应式布局类型定义\n\n包含响应式布局系统使用的枚举、数据类和类型定义。",
        )

        # 2. 创建布局管理器文件
        layout_manager_content = (
            common_imports
            + "\n\nfrom .types import BreakPoint, LayoutConfig, ScreenSize\n\n"
            + self.extract_class_content("ResponsiveLayoutManager")
        )
        self.create_file(
            "layout_manager.py",
            layout_manager_content,
            "MiniCRM 响应式布局管理器\n\n负责管理应用程序的响应式布局，包括断点管理、组件尺寸自适应等。",
        )

        # 3. 创建响应式组件文件
        responsive_widgets_content = (
            common_imports
            + "\n\nfrom .types import BreakPoint\nfrom .layout_manager import ResponsiveLayoutManager\n\n"
            + self.extract_class_content("ResponsiveWidget")
            + "\n\n"
            + self.extract_class_content("AutoScaleWidget")
        )
        self.create_file(
            "responsive_widgets.py",
            responsive_widgets_content,
            "MiniCRM 响应式组件基类\n\n提供响应式布局的基础功能和自动缩放功能。",
        )

        # 4. 创建弹性布局文件
        flex_layout_content = (
            common_imports + "\n\n" + self.extract_class_content("FlexLayout")
        )
        self.create_file(
            "flex_layout.py",
            flex_layout_content,
            "MiniCRM 弹性布局\n\n类似CSS Flexbox的布局管理器，支持自动换行和对齐。",
        )

        # 5. 创建网格组件文件
        grid_widget_content = (
            common_imports
            + "\n\nfrom .types import BreakPoint\nfrom .responsive_widgets import ResponsiveWidget\n\n"
            + self.extract_class_content("ResponsiveGridWidget")
        )
        self.create_file(
            "grid_widget.py",
            grid_widget_content,
            "MiniCRM 响应式网格组件\n\n根据屏幕尺寸自动调整网格列数和布局。",
        )

        # 6. 创建自适应容器文件
        adaptive_container_content = (
            common_imports
            + "\n\nfrom .types import BreakPoint\nfrom .responsive_widgets import ResponsiveWidget\n\n"
            + self.extract_class_content("AdaptiveContainer")
        )
        self.create_file(
            "adaptive_container.py",
            adaptive_container_content,
            "MiniCRM 自适应容器\n\n根据内容和屏幕尺寸自动调整布局方式。",
        )

        # 7. 创建高DPI管理器文件
        high_dpi_content = (
            common_imports + "\n\n" + self.extract_class_content("HighDPIManager")
        )
        self.create_file(
            "high_dpi_manager.py",
            high_dpi_content,
            "MiniCRM 高DPI显示管理器\n\n负责处理高DPI显示器的适配，包括DPI检测和缩放计算。",
        )

        # 8. 创建__init__.py文件
        init_content = '''"""
MiniCRM 响应式布局系统

提供完整的响应式布局解决方案，包括：
- 响应式布局管理
- 自动缩放组件
- 弹性布局
- 网格布局
- 高DPI适配

使用示例:
    from minicrm.ui.responsive import ResponsiveLayoutManager, ResponsiveWidget

    layout_manager = ResponsiveLayoutManager()
    widget = ResponsiveWidget()
    widget.set_layout_manager(layout_manager)
"""

from .types import BreakPoint, LayoutConfig, ScreenSize
from .layout_manager import ResponsiveLayoutManager
from .responsive_widgets import ResponsiveWidget, AutoScaleWidget
from .flex_layout import FlexLayout
from .grid_widget import ResponsiveGridWidget
from .adaptive_container import AdaptiveContainer
from .high_dpi_manager import HighDPIManager

__all__ = [
    # 类型定义
    'BreakPoint',
    'LayoutConfig',
    'ScreenSize',

    # 核心组件
    'ResponsiveLayoutManager',
    'ResponsiveWidget',
    'AutoScaleWidget',

    # 布局组件
    'FlexLayout',
    'ResponsiveGridWidget',
    'AdaptiveContainer',

    # 管理器
    'HighDPIManager',
]
'''

        init_file = self.target_dir / "__init__.py"
        init_file.write_text(init_content, encoding="utf-8")
        print("✅ 创建文件: __init__.py")

    def update_original_file(self) -> None:
        """更新原文件为导入模块"""
        new_content = '''"""
MiniCRM 响应式布局系统 (兼容性导入)

⚠️ 此文件已被拆分为多个模块以符合MiniCRM模块化标准。
   请使用新的导入方式：

   旧方式: from minicrm.ui.responsive_layout import ResponsiveLayoutManager
   新方式: from minicrm.ui.responsive import ResponsiveLayoutManager
"""

# 兼容性导入 - 保持向后兼容
from .responsive import *

# 发出弃用警告
import warnings
warnings.warn(
    "responsive_layout.py 已被拆分，请使用 'from minicrm.ui.responsive import ...' 导入",
    DeprecationWarning,
    stacklevel=2
)
'''

        self.source_file.write_text(new_content, encoding="utf-8")
        print("✅ 更新原文件为兼容性导入")

    def run(self) -> None:
        """执行拆分"""
        print("🚀 开始拆分响应式布局文件")
        print("=" * 50)

        self.read_source_file()
        self.create_target_directory()
        self.split_files()
        self.update_original_file()

        print("=" * 50)
        print("✅ 文件拆分完成!")
        print(f"📁 新文件位置: {self.target_dir}")
        print("\n📋 拆分结果:")

        for file_path in self.target_dir.glob("*.py"):
            lines = len(file_path.read_text().splitlines())
            status = "✅" if lines <= 400 else "⚠️" if lines <= 600 else "❌"
            print(f"  {status} {file_path.name}: {lines}行")

        print("\n🔄 原文件已更新为兼容性导入")
        print("📝 请更新其他文件的导入语句")


def main():
    """主函数"""
    splitter = ResponsiveLayoutSplitter("src/minicrm/ui/responsive_layout.py")
    splitter.run()


if __name__ == "__main__":
    main()
