"""
MiniCRM 页面路由器

负责处理页面路由规则和URL映射
"""

import logging
from typing import Any


class PageRouter:
    """
    页面路由器

    负责处理页面路由规则和URL映射
    """

    def __init__(self, page_manager):
        """
        初始化页面路由器

        Args:
            page_manager: 页面管理器实例
        """
        self._page_manager = page_manager
        self._logger = logging.getLogger(__name__)

        # 路由规则映射
        self._routes: dict[str, str] = {}

        # 默认路由
        self._default_route = "dashboard"

        # 错误页面路由
        self._error_route = "error"

    def add_route(self, route_path: str, page_name: str) -> None:
        """
        添加路由规则

        Args:
            route_path: 路由路径（如 "/customers", "/customers/list"）
            page_name: 对应的页面名称
        """
        self._routes[route_path] = page_name
        self._logger.debug(f"添加路由: {route_path} -> {page_name}")

    def remove_route(self, route_path: str) -> None:
        """移除路由规则"""
        if route_path in self._routes:
            del self._routes[route_path]
            self._logger.debug(f"移除路由: {route_path}")

    def navigate(self, route_path: str, params: dict[str, Any] | None = None) -> bool:
        """
        根据路由路径导航

        Args:
            route_path: 路由路径
            params: 路由参数

        Returns:
            bool: 是否成功导航
        """
        try:
            # 查找对应的页面名称
            page_name = self._routes.get(route_path)

            if not page_name:
                # 尝试模糊匹配
                page_name = self._find_matching_route(route_path)

            if not page_name:
                self._logger.warning(f"未找到路由: {route_path}")
                # 导航到错误页面
                return self._page_manager.navigate_to(
                    self._error_route, {"error": f"页面不存在: {route_path}"}
                )

            # 导航到页面
            return self._page_manager.navigate_to(page_name, params)

        except Exception as e:
            self._logger.error(f"路由导航失败 [{route_path}]: {e}")
            return False

    def _find_matching_route(self, route_path: str) -> str | None:
        """查找匹配的路由（支持模糊匹配）"""
        # 简单的前缀匹配
        for route, page_name in self._routes.items():
            if route_path.startswith(route):
                return page_name
        return None

    def get_route_for_page(self, page_name: str) -> str | None:
        """获取页面对应的路由路径"""
        for route, name in self._routes.items():
            if name == page_name:
                return route
        return None

    def get_all_routes(self) -> dict[str, str]:
        """获取所有路由规则"""
        return self._routes.copy()

    def set_default_route(self, page_name: str) -> None:
        """设置默认路由"""
        self._default_route = page_name

    def navigate_to_default(self) -> bool:
        """导航到默认页面"""
        return self._page_manager.navigate_to(self._default_route)
