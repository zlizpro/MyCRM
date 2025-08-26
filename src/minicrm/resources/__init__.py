"""
MiniCRM 资源模块

管理应用程序的静态资源,包括:
- 图标文件
- 样式表
- 模板文件
- 其他静态资源
"""

from pathlib import Path


# 资源目录路径
RESOURCES_DIR = Path(__file__).parent
ICONS_DIR = RESOURCES_DIR / "icons"
STYLES_DIR = RESOURCES_DIR / "styles"
TEMPLATES_DIR = RESOURCES_DIR / "templates"

# 确保目录存在
ICONS_DIR.mkdir(exist_ok=True)
STYLES_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)


def get_icon_path(icon_name: str) -> Path:
    """
    获取图标文件路径

    Args:
        icon_name: 图标文件名(包含扩展名)

    Returns:
        Path: 图标文件的完整路径
    """
    return ICONS_DIR / icon_name


def get_style_path(style_name: str) -> Path:
    """
    获取样式文件路径

    Args:
        style_name: 样式文件名(包含扩展名)

    Returns:
        Path: 样式文件的完整路径
    """
    return STYLES_DIR / style_name


def get_template_path(template_name: str) -> Path:
    """
    获取模板文件路径

    Args:
        template_name: 模板文件名(包含扩展名)

    Returns:
        Path: 模板文件的完整路径
    """
    return TEMPLATES_DIR / template_name
