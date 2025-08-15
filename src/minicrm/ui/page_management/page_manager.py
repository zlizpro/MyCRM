"""
MiniCRM 核心页面管理器

实现应用程序的页面管理功能，包括：
- 页面注册和路由管理
- 页面切换和生命周期管理
- 页面历史记录和导航
- 面包屑导航支持
- 懒加载页面机制
"""

import logging
import time
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QStackedWidget, QWidget

from minicrm.core.exceptions import UIError

from .page_base import NavigationHistory, PageInfo


class PageManager(QObject):
    """
    页面管理器

    负责管理应用程序中的所有页面，提供：
    - 页面注册和动态加载
    - 页面路由和切换
    - 导航历史记录管理
    - 面包屑导航支持
    - 页面生命周期管理

    Signals:
        page_changed: 页面切换信号 (page_name: str, page_widget: QWidget)
        page_loading: 页面加载信号 (page_name: str)
        page_loaded: 页面加载完成信号 (page_name: str, page_widget: QWidget)
        page_error: 页面错误信号 (page_name: str, error_message: str)
        history_changed: 历史记录变化信号 (history: List[NavigationHistory])
        breadcrumb_changed: 面包屑变化信号 (breadcrumb: List[str])
    """

    # Qt信号定义
    page_changed = Signal(str, QWidget)
    page_loading = Signal(str)
    page_loaded = Signal(str, QWidget)
    page_error = Signal(str, str)
    history_changed = Signal(list)
    breadcrumb_changed = Signal(list)

    def __init__(self, content_stack: QStackedWidget, parent: QObject | None = None):
        """
        初始化页面管理器

        Args:
            content_stack: 内容堆栈组件
            parent: 父对象
        """
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)

        # 内容堆栈
        self._content_stack = content_stack

        # 页面注册表
        self._pages: dict[str, PageInfo] = {}

        # 已创建的页面实例
        self._page_instances: dict[str, QWidget] = {}

        # 导航历史记录
        self._history: list[NavigationHistory] = []
        self._max_history_size = 50

        # 当前页面
        self._current_page: str | None = None

        # 页面创建工厂函数
        self._page_factories: dict[str, Callable[[], QWidget]] = {}

        self._logger.debug("页面管理器初始化完成")

    def register_page(
        self,
        name: str,
        title: str,
        widget_class: type[QWidget],
        parent_page: str | None = None,
        icon: str | None = None,
        description: str | None = None,
        requires_auth: bool = False,
        lazy_load: bool = True,
        **init_kwargs: Any,
    ) -> None:
        """
        注册页面

        Args:
            name: 页面名称（唯一标识）
            title: 页面标题
            widget_class: 页面组件类
            parent_page: 父页面名称（用于面包屑导航）
            icon: 页面图标
            description: 页面描述
            requires_auth: 是否需要认证
            lazy_load: 是否懒加载
            **init_kwargs: 页面初始化参数
        """
        try:
            if name in self._pages:
                self._logger.warning(f"页面已存在，将覆盖: {name}")

            page_info = PageInfo(
                name=name,
                title=title,
                widget_class=widget_class,
                parent_page=parent_page,
                icon=icon,
                description=description,
                requires_auth=requires_auth,
                lazy_load=lazy_load,
                init_kwargs=init_kwargs,
            )

            self._pages[name] = page_info
            self._logger.debug(f"页面注册成功: {name}")

        except Exception as e:
            self._logger.error(f"页面注册失败 [{name}]: {e}")
            raise UIError(f"页面注册失败: {e}", "PageManager") from e

    def register_page_factory(
        self,
        name: str,
        title: str,
        factory_func: Callable[[], QWidget],
        parent_page: str | None = None,
        icon: str | None = None,
        description: str | None = None,
        requires_auth: bool = False,
    ) -> None:
        """
        注册页面工厂函数

        Args:
            name: 页面名称
            title: 页面标题
            factory_func: 页面创建工厂函数
            parent_page: 父页面名称
            icon: 页面图标
            description: 页面描述
            requires_auth: 是否需要认证
        """
        try:
            # 创建一个虚拟的PageInfo，使用工厂函数
            page_info = PageInfo(
                name=name,
                title=title,
                widget_class=QWidget,  # 占位符
                parent_page=parent_page,
                icon=icon,
                description=description,
                requires_auth=requires_auth,
                lazy_load=True,
            )

            self._pages[name] = page_info
            self._page_factories[name] = factory_func

            self._logger.debug(f"页面工厂注册成功: {name}")

        except Exception as e:
            self._logger.error(f"页面工厂注册失败 [{name}]: {e}")
            raise UIError(f"页面工厂注册失败: {e}", "PageManager") from e

    def navigate_to(self, page_name: str, params: dict[str, Any] | None = None) -> bool:
        """
        导航到指定页面

        Args:
            page_name: 页面名称
            params: 页面参数

        Returns:
            bool: 是否成功导航
        """
        try:
            if page_name not in self._pages:
                self._logger.error(f"页面不存在: {page_name}")
                self.page_error.emit(page_name, f"页面不存在: {page_name}")
                return False

            page_info = self._pages[page_name]

            # 检查认证要求
            if page_info.requires_auth:
                # TODO: 实现认证检查
                pass

            # 发送页面加载信号
            self.page_loading.emit(page_name)

            # 获取或创建页面实例
            page_widget = self._get_or_create_page(page_name)
            if not page_widget:
                return False

            # 切换到页面
            self._switch_to_page(page_name, page_widget, params or {})

            return True

        except Exception as e:
            self._logger.error(f"页面导航失败 [{page_name}]: {e}")
            self.page_error.emit(page_name, str(e))
            return False

    def _get_or_create_page(self, page_name: str) -> QWidget | None:
        """获取或创建页面实例"""
        try:
            # 如果页面已存在，直接返回
            if page_name in self._page_instances:
                return self._page_instances[page_name]

            # 创建新页面实例
            page_widget = self._create_page_instance(page_name)
            if page_widget:
                # 添加到内容堆栈
                self._content_stack.addWidget(page_widget)

                # 缓存页面实例
                self._page_instances[page_name] = page_widget

                # 发送页面加载完成信号
                self.page_loaded.emit(page_name, page_widget)

                self._logger.debug(f"页面创建成功: {page_name}")

            return page_widget

        except Exception as e:
            self._logger.error(f"页面创建失败 [{page_name}]: {e}")
            return None

    def _create_page_instance(self, page_name: str) -> QWidget | None:
        """创建页面实例"""
        try:
            # 使用工厂函数创建
            if page_name in self._page_factories:
                return self._page_factories[page_name]()

            # 使用类创建
            page_info = self._pages[page_name]
            widget_class = page_info.widget_class

            # 创建页面实例
            if page_info.init_kwargs:
                page_widget = widget_class(**page_info.init_kwargs)
            else:
                page_widget = widget_class()

            return page_widget

        except Exception as e:
            self._logger.error(f"页面实例创建失败 [{page_name}]: {e}")
            return None

    def _switch_to_page(
        self, page_name: str, page_widget: QWidget, params: dict[str, Any]
    ) -> None:
        """切换到指定页面"""
        try:
            # 调用当前页面的离开方法
            if self._current_page and self._current_page in self._page_instances:
                current_widget = self._page_instances[self._current_page]
                if hasattr(current_widget, "on_page_leave"):
                    current_widget.on_page_leave()

            # 切换到新页面
            self._content_stack.setCurrentWidget(page_widget)

            # 调用新页面的进入方法
            if hasattr(page_widget, "on_page_enter"):
                page_widget.on_page_enter(params)

            # 更新当前页面
            old_page = self._current_page
            self._current_page = page_name

            # 添加到历史记录
            self._add_to_history(page_name, params)

            # 更新面包屑
            self._update_breadcrumb()

            # 发送页面切换信号
            self.page_changed.emit(page_name, page_widget)

            self._logger.debug(f"页面切换成功: {old_page} -> {page_name}")

        except Exception as e:
            self._logger.error(f"页面切换失败 [{page_name}]: {e}")
            raise

    def _add_to_history(self, page_name: str, params: dict[str, Any]) -> None:
        """添加到历史记录"""
        history_item = NavigationHistory(
            page_name=page_name, timestamp=time.time(), params=params
        )

        # 避免重复记录相同页面
        if not self._history or self._history[-1].page_name != page_name:
            self._history.append(history_item)

            # 限制历史记录大小
            if len(self._history) > self._max_history_size:
                self._history.pop(0)

            # 发送历史记录变化信号
            self.history_changed.emit(self._history)

    def _update_breadcrumb(self) -> None:
        """更新面包屑导航"""
        try:
            if not self._current_page:
                return

            breadcrumb: list[str] = []
            current_page: str | None = self._current_page

            # 构建面包屑路径
            while current_page:
                page_info = self._pages.get(current_page)
                if page_info:
                    breadcrumb.insert(0, page_info.title)
                    current_page = page_info.parent_page
                else:
                    break

            # 发送面包屑变化信号
            self.breadcrumb_changed.emit(breadcrumb)

        except Exception as e:
            self._logger.error(f"面包屑更新失败: {e}")

    def go_back(self) -> bool:
        """返回上一页"""
        try:
            if len(self._history) < 2:
                return False

            # 移除当前页面
            self._history.pop()

            # 获取上一页
            if self._history:
                last_page = self._history[-1]
                return self.navigate_to(last_page.page_name, last_page.params)

            return False

        except Exception as e:
            self._logger.error(f"返回上一页失败: {e}")
            return False

    def go_forward(self) -> bool:
        """前进到下一页（如果有的话）"""
        # TODO: 实现前进功能（需要维护前进历史）
        return False

    def refresh_current_page(self) -> bool:
        """刷新当前页面"""
        try:
            if not self._current_page:
                return False

            current_widget = self._page_instances.get(self._current_page)
            if current_widget and hasattr(current_widget, "refresh"):
                current_widget.refresh()
                return True

            return False

        except Exception as e:
            self._logger.error(f"页面刷新失败: {e}")
            return False

    def get_current_page(self) -> str | None:
        """获取当前页面名称"""
        return self._current_page

    def get_current_widget(self) -> QWidget | None:
        """获取当前页面组件"""
        if self._current_page and self._current_page in self._page_instances:
            return self._page_instances[self._current_page]
        return None

    def get_page_info(self, page_name: str) -> PageInfo | None:
        """获取页面信息"""
        return self._pages.get(page_name)

    def get_all_pages(self) -> dict[str, PageInfo]:
        """获取所有页面信息"""
        return self._pages.copy()

    def get_history(self) -> list[NavigationHistory]:
        """获取导航历史记录"""
        return self._history.copy()

    def clear_history(self) -> None:
        """清空导航历史记录"""
        self._history.clear()
        self.history_changed.emit(self._history)

    def unload_page(self, page_name: str) -> bool:
        """卸载页面（释放内存）"""
        try:
            if page_name not in self._page_instances:
                return True

            page_widget = self._page_instances[page_name]

            # 如果是当前页面，不能卸载
            if page_name == self._current_page:
                self._logger.warning(f"不能卸载当前页面: {page_name}")
                return False

            # 调用页面的清理方法
            if hasattr(page_widget, "cleanup"):
                page_widget.cleanup()

            # 从内容堆栈中移除
            self._content_stack.removeWidget(page_widget)

            # 删除页面实例
            page_widget.deleteLater()
            del self._page_instances[page_name]

            self._logger.debug(f"页面卸载成功: {page_name}")
            return True

        except Exception as e:
            self._logger.error(f"页面卸载失败 [{page_name}]: {e}")
            return False

    def preload_page(self, page_name: str) -> bool:
        """预加载页面"""
        try:
            if page_name in self._page_instances:
                return True  # 已经加载

            page_widget = self._get_or_create_page(page_name)
            return page_widget is not None

        except Exception as e:
            self._logger.error(f"页面预加载失败 [{page_name}]: {e}")
            return False

    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 清理所有页面实例
            for page_widget in self._page_instances.values():
                if hasattr(page_widget, "cleanup"):
                    page_widget.cleanup()
                page_widget.deleteLater()

            self._page_instances.clear()
            self._history.clear()
            self._current_page = None

            self._logger.debug("页面管理器清理完成")

        except Exception as e:
            self._logger.error(f"页面管理器清理失败: {e}")
