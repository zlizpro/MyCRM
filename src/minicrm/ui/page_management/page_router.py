"""
MiniCRM 页面路由器

负责处理页面路由规则和URL映射,提供:
- 路由规则管理
- 参数解析和传递
- 路由匹配和导航
- 路由历史记录
- 路由守卫和权限检查
"""

import logging
import re
from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs, urlparse


class RouteInfo:
    """路由信息"""

    def __init__(
        self,
        path: str,
        page_name: str,
        params: dict[str, Any] | None = None,
        guards: list[Callable] | None = None,
        meta: dict[str, Any] | None = None,
    ):
        self.path = path
        self.page_name = page_name
        self.params = params or {}
        self.guards = guards or []
        self.meta = meta or {}


class PageRouter:
    """
    页面路由器

    负责处理页面路由规则和URL映射,支持:
    - 静态路由和动态路由
    - 路由参数解析
    - 路由守卫和权限检查
    - 路由历史记录
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
        self._routes: dict[str, RouteInfo] = {}

        # 动态路由规则(支持参数)
        self._dynamic_routes: list[tuple[re.Pattern, RouteInfo]] = []

        # 默认路由
        self._default_route = "dashboard"

        # 错误页面路由
        self._error_route = "error"

        # 路由历史记录
        self._route_history: list[str] = []
        self._max_history_size = 50

        # 全局路由守卫
        self._global_guards: list[Callable] = []

    def add_route(
        self,
        route_path: str,
        page_name: str,
        params: dict[str, Any] | None = None,
        guards: list[Callable] | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        """
        添加路由规则

        Args:
            route_path: 路由路径(如 "/customers", "/customers/:id")
            page_name: 对应的页面名称
            params: 默认参数
            guards: 路由守卫函数列表
            meta: 路由元数据
        """
        try:
            route_info = RouteInfo(route_path, page_name, params, guards, meta)

            # 检查是否为动态路由(包含参数)
            if ":" in route_path or "*" in route_path:
                # 转换为正则表达式
                pattern = self._path_to_regex(route_path)
                self._dynamic_routes.append((pattern, route_info))
                self._logger.debug(f"添加动态路由: {route_path} -> {page_name}")
            else:
                # 静态路由
                self._routes[route_path] = route_info
                self._logger.debug(f"添加静态路由: {route_path} -> {page_name}")

        except Exception as e:
            self._logger.error(f"添加路由失败 [{route_path}]: {e}")

    def _path_to_regex(self, path: str) -> re.Pattern:
        """将路径转换为正则表达式"""
        # 替换参数占位符
        pattern = path
        pattern = re.sub(r":(\w+)", r"(?P<\1>[^/]+)", pattern)  # :id -> (?P<id>[^/]+)
        pattern = re.sub(r"\*", r".*", pattern)  # * -> .*
        pattern = f"^{pattern}$"
        return re.compile(pattern)

    def remove_route(self, route_path: str) -> None:
        """移除路由规则"""
        try:
            # 移除静态路由
            if route_path in self._routes:
                del self._routes[route_path]
                self._logger.debug(f"移除静态路由: {route_path}")
                return

            # 移除动态路由
            for i, (_, route_info) in enumerate(self._dynamic_routes):
                if route_info.path == route_path:
                    del self._dynamic_routes[i]
                    self._logger.debug(f"移除动态路由: {route_path}")
                    return

            self._logger.warning(f"路由不存在: {route_path}")

        except Exception as e:
            self._logger.error(f"移除路由失败 [{route_path}]: {e}")

    def add_global_guard(self, guard_func: Callable) -> None:
        """添加全局路由守卫"""
        self._global_guards.append(guard_func)
        self._logger.debug("添加全局路由守卫")

    def navigate(self, route_path: str, params: dict[str, Any] | None = None) -> bool:
        """
        根据路由路径导航

        Args:
            route_path: 路由路径
            params: 额外的路由参数

        Returns:
            bool: 是否成功导航
        """
        try:
            # 解析路由
            route_info, parsed_params = self._resolve_route(route_path)

            if not route_info:
                self._logger.warning(f"未找到路由: {route_path}")
                # 导航到错误页面
                return self._navigate_to_error_page(f"页面不存在: {route_path}")

            # 合并参数
            final_params = {}
            final_params.update(route_info.params)
            final_params.update(parsed_params)
            if params:
                final_params.update(params)

            # 如果没有任何参数,传递None而不是空字典
            params_to_pass = final_params if final_params else None

            # 执行路由守卫检查
            if not self._check_route_guards(route_info, final_params):
                self._logger.warning(f"路由守卫检查失败: {route_path}")
                return False

            # 添加到路由历史
            self._add_to_route_history(route_path)

            # 导航到页面
            success = self._page_manager.navigate_to(
                route_info.page_name, params_to_pass
            )

            if success:
                self._logger.debug(
                    f"路由导航成功: {route_path} -> {route_info.page_name}"
                )

            return success

        except Exception as e:
            self._logger.error(f"路由导航失败 [{route_path}]: {e}")
            return self._navigate_to_error_page(f"导航错误: {str(e)}")

    def _resolve_route(
        self, route_path: str
    ) -> tuple[RouteInfo | None, dict[str, Any]]:
        """解析路由路径"""
        try:
            # 解析URL和查询参数
            parsed_url = urlparse(route_path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)

            # 扁平化查询参数
            flat_params = {}
            for key, values in query_params.items():
                flat_params[key] = values[0] if len(values) == 1 else values

            # 首先检查静态路由
            if path in self._routes:
                return self._routes[path], flat_params

            # 检查动态路由
            for pattern, route_info in self._dynamic_routes:
                match = pattern.match(path)
                if match:
                    # 提取路径参数
                    path_params = match.groupdict()
                    # 合并路径参数和查询参数
                    all_params = {**path_params, **flat_params}
                    return route_info, all_params

            return None, flat_params

        except Exception as e:
            self._logger.error(f"路由解析失败 [{route_path}]: {e}")
            return None, {}

    def _check_route_guards(
        self, route_info: RouteInfo, params: dict[str, Any]
    ) -> bool:
        """检查路由守卫"""
        try:
            # 检查全局守卫
            for guard in self._global_guards:
                if not guard(route_info.page_name, params):
                    return False

            # 检查路由特定守卫
            for guard in route_info.guards:
                if not guard(route_info.page_name, params):
                    return False

            return True

        except Exception as e:
            self._logger.error(f"路由守卫检查失败: {e}")
            return False

    def _add_to_route_history(self, route_path: str) -> None:
        """添加到路由历史"""
        # 避免重复记录相同路由
        if not self._route_history or self._route_history[-1] != route_path:
            self._route_history.append(route_path)

            # 限制历史记录大小
            if len(self._route_history) > self._max_history_size:
                self._route_history.pop(0)

    def _navigate_to_error_page(self, error_message: str) -> bool:
        """导航到错误页面"""
        try:
            return self._page_manager.navigate_to(
                self._error_route, {"error": error_message}
            )
        except Exception:
            # 如果错误页面也导航失败,导航到默认页面
            return self._page_manager.navigate_to(self._default_route)

    def _find_matching_route(self, route_path: str) -> RouteInfo | None:
        """查找匹配的路由(支持模糊匹配)"""
        # 简单的前缀匹配
        for route_path_key, route_info in self._routes.items():
            if route_path.startswith(route_path_key):
                return route_info
        return None

    def get_route_for_page(self, page_name: str) -> str | None:
        """获取页面对应的路由路径"""
        # 检查静态路由
        for route_path, route_info in self._routes.items():
            if route_info.page_name == page_name:
                return route_path

        # 检查动态路由
        for _, route_info in self._dynamic_routes:
            if route_info.page_name == page_name:
                return route_info.path

        return None

    def get_current_route(self) -> str | None:
        """获取当前路由路径"""
        if self._route_history:
            return self._route_history[-1]
        return None

    def get_route_history(self) -> list[str]:
        """获取路由历史记录"""
        return self._route_history.copy()

    def clear_route_history(self) -> None:
        """清空路由历史记录"""
        self._route_history.clear()

    def go_back(self) -> bool:
        """返回上一个路由"""
        try:
            if len(self._route_history) < 2:
                return False

            # 移除当前路由
            self._route_history.pop()

            # 获取上一个路由
            if self._route_history:
                previous_route = self._route_history[-1]
                # 移除上一个路由,因为navigate会重新添加
                self._route_history.pop()
                return self.navigate(previous_route)

            return False

        except Exception as e:
            self._logger.error(f"返回上一路由失败: {e}")
            return False

    def navigate_to_default(self) -> bool:
        """导航到默认页面"""
        return self.navigate(f"/{self._default_route}")

    def set_default_route(self, page_name: str) -> None:
        """设置默认路由"""
        self._default_route = page_name

    def set_error_route(self, page_name: str) -> None:
        """设置错误页面路由"""
        self._error_route = page_name

    def get_all_routes(self) -> dict[str, str]:
        """获取所有路由映射"""
        routes = {}

        # 静态路由
        for path, route_info in self._routes.items():
            routes[path] = route_info.page_name

        # 动态路由
        for _, route_info in self._dynamic_routes:
            routes[route_info.path] = route_info.page_name

        return routes

    def build_url(
        self, page_name: str, params: dict[str, Any] | None = None
    ) -> str | None:
        """
        构建页面URL

        Args:
            page_name: 页面名称
            params: URL参数

        Returns:
            Optional[str]: 构建的URL,如果页面不存在则返回None
        """
        try:
            route_path = self.get_route_for_page(page_name)
            if not route_path:
                return None

            # 如果有参数,构建查询字符串
            if params:
                query_parts: list[str] = []
                for key, value in params.items():
                    if isinstance(value, list | tuple):
                        query_parts.extend(f"{key}={v}" for v in value)
                    else:
                        query_parts.append(f"{key}={value}")

                if query_parts:
                    route_path += "?" + "&".join(query_parts)

            return route_path

        except Exception as e:
            self._logger.error(f"构建URL失败 [{page_name}]: {e}")
            return None
