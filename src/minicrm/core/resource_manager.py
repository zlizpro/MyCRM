"""跨平台资源管理器.

提供统一的资源访问接口,支持开发环境和PyInstaller打包环境.
处理不同操作系统的路径差异,确保资源文件的正确访问.
"""

from __future__ import annotations

import logging
from pathlib import Path
import platform
import sys

from minicrm.core.exceptions import MiniCRMError


logger = logging.getLogger(__name__)


class ResourceNotFoundError(MiniCRMError):
    """资源文件未找到错误."""


class ResourceManager:
    """跨平台资源管理器.

    负责管理应用程序的所有资源文件,包括图标、主题、模板等.
    自动处理开发环境和打包环境的路径差异.
    """

    def __init__(self) -> None:
        """初始化资源管理器."""
        self._base_path = self._get_base_path()
        self._resource_path = self._get_resource_path()
        self._platform = platform.system().lower()
        self._cache: dict[str, Path] = {}

        logger.info("资源管理器初始化完成,基础路径: %s", self._base_path)
        logger.info("资源路径: %s", self._resource_path)
        logger.info("运行平台: %s", self._platform)

    def _get_base_path(self) -> Path:
        """获取应用程序基础路径.

        Returns:
            应用程序基础路径
        """
        if hasattr(sys, "_MEIPASS"):
            # PyInstaller打包后的路径
            base_path = Path(sys._MEIPASS)
            logger.debug("检测到PyInstaller环境,使用路径: %s", base_path)
        else:
            # 开发环境路径
            # 从当前文件向上查找到项目根目录
            current_file = Path(__file__).resolve()
            # 向上查找到src目录的父目录
            base_path = current_file.parent.parent.parent.parent
            logger.debug("开发环境,使用路径: %s", base_path)

        return base_path

    def _get_resource_path(self) -> Path:
        """获取资源文件路径.

        Returns:
            资源文件路径
        """
        if hasattr(sys, "_MEIPASS"):
            # PyInstaller环境下,资源文件在根目录
            return self._base_path / "resources"
        # 开发环境下,资源文件在src/minicrm/resources
        return self._base_path / "src" / "minicrm" / "resources"

    def get_icon_path(self, icon_name: str) -> Path:
        """获取图标文件路径.

        Args:
            icon_name: 图标文件名(包含扩展名)

        Returns:
            图标文件完整路径

        Raises:
            ResourceNotFoundError: 图标文件不存在
        """
        cache_key = f"icon_{icon_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        icon_path = self._resource_path / "icons" / icon_name

        if not icon_path.exists():
            # 尝试常见的图标格式
            for ext in [".png", ".ico", ".svg", ".jpg", ".jpeg"]:
                if not icon_name.endswith(ext):
                    alt_path = self._resource_path / "icons" / f"{icon_name}{ext}"
                    if alt_path.exists():
                        icon_path = alt_path
                        break
            else:
                msg = f"图标文件未找到: {icon_name}"
                raise ResourceNotFoundError(msg)

        self._cache[cache_key] = icon_path
        logger.debug("获取图标路径: %s -> %s", icon_name, icon_path)
        return icon_path

    def get_theme_path(self, theme_name: str) -> Path:
        """获取主题文件路径.

        Args:
            theme_name: 主题名称

        Returns:
            主题文件完整路径

        Raises:
            ResourceNotFoundError: 主题文件不存在
        """
        cache_key = f"theme_{theme_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 尝试不同的主题文件格式
        for ext in [".json", ".yaml", ".yml"]:
            theme_path = self._resource_path / "themes" / f"{theme_name}{ext}"
            if theme_path.exists():
                self._cache[cache_key] = theme_path
                logger.debug("获取主题路径: %s -> %s", theme_name, theme_path)
                return theme_path

        msg = f"主题文件未找到: {theme_name}"
        raise ResourceNotFoundError(msg)

    def get_template_path(self, template_name: str) -> Path:
        """获取模板文件路径.

        Args:
            template_name: 模板文件名

        Returns:
            模板文件完整路径

        Raises:
            ResourceNotFoundError: 模板文件不存在
        """
        cache_key = f"template_{template_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 尝试不同的模板文件格式和位置
        template_dirs = ["templates", "templates/custom"]
        extensions = [".docx", ".html", ".txt", ".json"]

        for template_dir in template_dirs:
            for ext in extensions:
                if template_name.endswith(ext):
                    template_path = self._resource_path / template_dir / template_name
                else:
                    template_path = (
                        self._resource_path / template_dir / f"{template_name}{ext}"
                    )

                if template_path.exists():
                    self._cache[cache_key] = template_path
                    logger.debug("获取模板路径: %s -> %s", template_name, template_path)
                    return template_path

        msg = f"模板文件未找到: {template_name}"
        raise ResourceNotFoundError(msg)

    def get_style_path(self, style_name: str) -> Path:
        """获取样式文件路径.

        Args:
            style_name: 样式文件名

        Returns:
            样式文件完整路径

        Raises:
            ResourceNotFoundError: 样式文件不存在
        """
        cache_key = f"style_{style_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 尝试不同的样式文件格式
        for ext in [".css", ".tcl", ".json"]:
            style_path = self._resource_path / "styles" / f"{style_name}{ext}"
            if style_path.exists():
                self._cache[cache_key] = style_path
                logger.debug("获取样式路径: %s -> %s", style_name, style_path)
                return style_path

        msg = f"样式文件未找到: {style_name}"
        raise ResourceNotFoundError(msg)

    def get_resource_path_by_type(self, resource_type: str) -> Path:
        """根据资源类型获取资源目录路径.

        Args:
            resource_type: 资源类型 (icons, themes, templates, styles)

        Returns:
            资源目录路径

        Raises:
            ValueError: 不支持的资源类型
        """
        valid_types = ["icons", "themes", "templates", "styles"]
        if resource_type not in valid_types:
            msg = f"不支持的资源类型: {resource_type},支持的类型: {valid_types}"
            raise ValueError(msg)

        return self._resource_path / resource_type

    def list_resources(self, resource_type: str) -> list[str]:
        """列出指定类型的所有资源文件.

        Args:
            resource_type: 资源类型

        Returns:
            资源文件名列表
        """
        resource_dir = self.get_resource_path_by_type(resource_type)

        if not resource_dir.exists():
            logger.warning("资源目录不存在: %s", resource_dir)
            return []

        resources = [
            file_path.name
            for file_path in resource_dir.iterdir()
            if file_path.is_file()
        ]

        logger.debug("列出%s资源: %d个文件", resource_type, len(resources))
        return sorted(resources)

    def resource_exists(self, resource_type: str, resource_name: str) -> bool:
        """检查资源文件是否存在.

        Args:
            resource_type: 资源类型
            resource_name: 资源文件名

        Returns:
            资源文件是否存在
        """
        try:
            if resource_type == "icons":
                self.get_icon_path(resource_name)
            elif resource_type == "themes":
                self.get_theme_path(resource_name)
            elif resource_type == "templates":
                self.get_template_path(resource_name)
            elif resource_type == "styles":
                self.get_style_path(resource_name)
            else:
                return False
        except ResourceNotFoundError:
            return False
        else:
            return True

    def get_platform_specific_resource(
        self, base_name: str, resource_type: str
    ) -> Path:
        """获取平台特定的资源文件.

        优先查找平台特定版本,如果不存在则返回通用版本.

        Args:
            base_name: 基础文件名(不含平台后缀)
            resource_type: 资源类型

        Returns:
            资源文件路径
        """
        # 尝试平台特定版本
        platform_name = f"{base_name}_{self._platform}"

        try:
            if resource_type == "icons":
                return self.get_icon_path(platform_name)
            if resource_type == "themes":
                return self.get_theme_path(platform_name)
            if resource_type == "templates":
                return self.get_template_path(platform_name)
            if resource_type == "styles":
                return self.get_style_path(platform_name)
        except ResourceNotFoundError:
            pass

        # 回退到通用版本
        if resource_type == "icons":
            return self.get_icon_path(base_name)
        if resource_type == "themes":
            return self.get_theme_path(base_name)
        if resource_type == "templates":
            return self.get_template_path(base_name)
        if resource_type == "styles":
            return self.get_style_path(base_name)
        msg = f"不支持的资源类型: {resource_type}"
        raise ValueError(msg)

    def clear_cache(self) -> None:
        """清空资源路径缓存."""
        self._cache.clear()
        logger.debug("资源路径缓存已清空")

    def get_cache_info(self) -> dict[str, int]:
        """获取缓存信息.

        Returns:
            缓存统计信息
        """
        return {
            "cached_items": len(self._cache),
            "cache_size_bytes": sys.getsizeof(self._cache),
        }

    @property
    def base_path(self) -> Path:
        """获取基础路径."""
        return self._base_path

    @property
    def resource_path(self) -> Path:
        """获取资源路径."""
        return self._resource_path

    @property
    def platform(self) -> str:
        """获取当前平台."""
        return self._platform


# 全局资源管理器实例
_resource_manager: ResourceManager | None = None


def get_resource_manager() -> ResourceManager:
    """获取全局资源管理器实例.

    Returns:
        资源管理器实例
    """
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager


def initialize_resource_manager() -> ResourceManager:
    """初始化资源管理器.

    Returns:
        资源管理器实例
    """
    global _resource_manager
    _resource_manager = ResourceManager()
    return _resource_manager


def cleanup_resource_manager() -> None:
    """清理资源管理器."""
    global _resource_manager
    if _resource_manager is not None:
        _resource_manager.clear_cache()
        _resource_manager = None
        logger.info("资源管理器已清理")
