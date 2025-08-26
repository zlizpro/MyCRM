"""MiniCRM TTK虚拟滚动混入类

提供TTK组件的虚拟滚动功能,用于优化大数据集的显示性能.
支持:
- 虚拟滚动渲染
- 动态项目高度
- 平滑滚动
- 内存优化
- 性能监控
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import math
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class VirtualScrollConfig:
    """虚拟滚动配置"""

    item_height: int = 25  # 默认项目高度
    buffer_size: int = 5  # 缓冲区大小(额外渲染的项目数)
    scroll_sensitivity: float = 1.0  # 滚动灵敏度
    enable_smooth_scroll: bool = True  # 启用平滑滚动
    enable_dynamic_height: bool = False  # 启用动态高度
    min_visible_items: int = 10  # 最小可见项目数
    max_visible_items: int = 100  # 最大可见项目数


@dataclass
class VirtualScrollState:
    """虚拟滚动状态"""

    total_items: int = 0
    visible_start: int = 0
    visible_end: int = 0
    scroll_position: float = 0.0
    container_height: int = 0
    total_height: int = 0
    rendered_items: Dict[int, tk.Widget] = None

    def __post_init__(self):
        if self.rendered_items is None:
            self.rendered_items = {}


class VirtualScrollMixin(ABC):
    """TTK虚拟滚动混入类

    为TTK组件提供虚拟滚动功能,优化大数据集的显示性能.
    """

    def __init__(self, *args, **kwargs):
        """初始化虚拟滚动混入"""
        super().__init__(*args, **kwargs)

        self._logger = logging.getLogger(__name__)

        # 虚拟滚动配置和状态
        self._virtual_config = VirtualScrollConfig()
        self._virtual_state = VirtualScrollState()

        # 数据源
        self._data_source: List[Any] = []
        self._item_renderer: Optional[Callable] = None
        self._item_height_calculator: Optional[Callable] = None

        # UI组件
        self._scroll_container: Optional[tk.Frame] = None
        self._scroll_canvas: Optional[tk.Canvas] = None
        self._scrollbar: Optional[ttk.Scrollbar] = None
        self._content_frame: Optional[tk.Frame] = None

        # 性能监控
        self._render_count = 0
        self._last_render_time = 0.0

        # 事件绑定标志
        self._events_bound = False

        self._logger.debug("虚拟滚动混入初始化完成")

    def setup_virtual_scroll(
        self,
        parent: tk.Widget,
        data_source: List[Any],
        item_renderer: Callable[[tk.Widget, Any, int], tk.Widget],
        config: Optional[VirtualScrollConfig] = None,
    ) -> None:
        """设置虚拟滚动

        Args:
            parent: 父组件
            data_source: 数据源
            item_renderer: 项目渲染器函数
            config: 虚拟滚动配置
        """
        try:
            # 更新配置
            if config:
                self._virtual_config = config

            # 设置数据源和渲染器
            self._data_source = data_source
            self._item_renderer = item_renderer

            # 创建UI组件
            self._create_scroll_ui(parent)

            # 计算初始状态
            self._calculate_virtual_state()

            # 绑定事件
            self._bind_scroll_events()

            # 初始渲染
            self._render_visible_items()

            self._logger.info(f"虚拟滚动设置完成,数据项: {len(data_source)}")

        except Exception as e:
            self._logger.error(f"设置虚拟滚动失败: {e}")
            raise

    def _create_scroll_ui(self, parent: tk.Widget) -> None:
        """创建滚动UI组件"""
        # 主容器
        self._scroll_container = tk.Frame(parent)
        self._scroll_container.pack(fill=tk.BOTH, expand=True)

        # 画布和滚动条
        self._scroll_canvas = tk.Canvas(self._scroll_container, highlightthickness=0)

        self._scrollbar = ttk.Scrollbar(
            self._scroll_container,
            orient=tk.VERTICAL,
            command=self._on_scrollbar_scroll,
        )

        # 内容框架
        self._content_frame = tk.Frame(self._scroll_canvas)

        # 布局
        self._scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 配置画布
        self._canvas_window = self._scroll_canvas.create_window(
            0, 0, anchor=tk.NW, window=self._content_frame
        )

        # 配置滚动条
        self._scroll_canvas.configure(yscrollcommand=self._scrollbar.set)

    def _bind_scroll_events(self) -> None:
        """绑定滚动事件"""
        if self._events_bound:
            return

        # 鼠标滚轮事件
        self._scroll_canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self._scroll_canvas.bind("<Button-4>", self._on_mouse_wheel)
        self._scroll_canvas.bind("<Button-5>", self._on_mouse_wheel)

        # 键盘事件
        self._scroll_canvas.bind("<Key-Up>", self._on_key_scroll)
        self._scroll_canvas.bind("<Key-Down>", self._on_key_scroll)
        self._scroll_canvas.bind("<Key-Prior>", self._on_key_scroll)
        self._scroll_canvas.bind("<Key-Next>", self._on_key_scroll)

        # 大小变化事件
        self._scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        self._content_frame.bind("<Configure>", self._on_content_configure)

        # 焦点事件
        self._scroll_canvas.bind(
            "<Button-1>", lambda e: self._scroll_canvas.focus_set()
        )

        self._events_bound = True

    def _calculate_virtual_state(self) -> None:
        """计算虚拟滚动状态"""
        # 更新总项目数
        self._virtual_state.total_items = len(self._data_source)

        # 计算总高度
        if self._virtual_config.enable_dynamic_height and self._item_height_calculator:
            total_height = 0
            for i, item in enumerate(self._data_source):
                height = self._item_height_calculator(item, i)
                total_height += height
            self._virtual_state.total_height = total_height
        else:
            self._virtual_state.total_height = (
                self._virtual_state.total_items * self._virtual_config.item_height
            )

        # 获取容器高度
        if self._scroll_canvas:
            self._virtual_state.container_height = self._scroll_canvas.winfo_height()

        # 计算可见范围
        self._calculate_visible_range()

    def _calculate_visible_range(self) -> None:
        """计算可见项目范围"""
        if self._virtual_state.total_items == 0:
            self._virtual_state.visible_start = 0
            self._virtual_state.visible_end = 0
            return

        container_height = self._virtual_state.container_height
        if container_height <= 0:
            container_height = 400  # 默认高度

        # 计算可见项目数量
        items_per_screen = max(
            self._virtual_config.min_visible_items,
            min(
                self._virtual_config.max_visible_items,
                math.ceil(container_height / self._virtual_config.item_height),
            ),
        )

        # 计算起始位置
        scroll_ratio = self._virtual_state.scroll_position
        max_start = max(0, self._virtual_state.total_items - items_per_screen)
        start_index = int(scroll_ratio * max_start)

        # 添加缓冲区
        buffer_size = self._virtual_config.buffer_size
        actual_start = max(0, start_index - buffer_size)
        actual_end = min(
            self._virtual_state.total_items,
            start_index + items_per_screen + buffer_size,
        )

        self._virtual_state.visible_start = actual_start
        self._virtual_state.visible_end = actual_end

    def _render_visible_items(self) -> None:
        """渲染可见项目"""
        if not self._item_renderer or not self._content_frame:
            return

        try:
            start_time = tk.time.time() if hasattr(tk, "time") else 0

            # 清理不再可见的项目
            self._cleanup_invisible_items()

            # 渲染新的可见项目
            for i in range(
                self._virtual_state.visible_start, self._virtual_state.visible_end
            ):
                if i not in self._virtual_state.rendered_items:
                    self._render_item(i)

            # 更新布局
            self._update_item_positions()

            # 更新滚动条
            self._update_scrollbar()

            # 性能统计
            self._render_count += 1
            if hasattr(tk, "time"):
                self._last_render_time = tk.time.time() - start_time

            self._logger.debug(
                f"渲染完成: 项目 {self._virtual_state.visible_start}-{self._virtual_state.visible_end}, "
                f"耗时: {self._last_render_time:.3f}s"
            )

        except Exception as e:
            self._logger.error(f"渲染可见项目失败: {e}")

    def _render_item(self, index: int) -> None:
        """渲染单个项目"""
        if index >= len(self._data_source):
            return

        try:
            data_item = self._data_source[index]

            # 调用项目渲染器
            widget = self._item_renderer(self._content_frame, data_item, index)

            if widget:
                self._virtual_state.rendered_items[index] = widget

        except Exception as e:
            self._logger.error(f"渲染项目 {index} 失败: {e}")

    def _cleanup_invisible_items(self) -> None:
        """清理不可见的项目"""
        visible_range = set(
            range(self._virtual_state.visible_start, self._virtual_state.visible_end)
        )

        items_to_remove = []
        for index in self._virtual_state.rendered_items:
            if index not in visible_range:
                items_to_remove.append(index)

        for index in items_to_remove:
            widget = self._virtual_state.rendered_items.pop(index)
            if widget and widget.winfo_exists():
                widget.destroy()

    def _update_item_positions(self) -> None:
        """更新项目位置"""
        for index, widget in self._virtual_state.rendered_items.items():
            if widget and widget.winfo_exists():
                # 计算Y位置
                if (
                    self._virtual_config.enable_dynamic_height
                    and self._item_height_calculator
                ):
                    y_pos = self._calculate_dynamic_y_position(index)
                else:
                    y_pos = index * self._virtual_config.item_height

                # 设置位置
                widget.place(x=0, y=y_pos, relwidth=1.0)

    def _calculate_dynamic_y_position(self, index: int) -> int:
        """计算动态Y位置"""
        if not self._item_height_calculator:
            return index * self._virtual_config.item_height

        y_pos = 0
        for i in range(index):
            if i < len(self._data_source):
                height = self._item_height_calculator(self._data_source[i], i)
                y_pos += height

        return y_pos

    def _update_scrollbar(self) -> None:
        """更新滚动条"""
        if not self._scroll_canvas or not self._scrollbar:
            return

        try:
            # 设置内容框架大小
            self._content_frame.configure(height=self._virtual_state.total_height)

            # 更新画布滚动区域
            self._scroll_canvas.configure(
                scrollregion=(0, 0, 0, self._virtual_state.total_height)
            )

            # 计算滚动位置
            if self._virtual_state.total_height > 0:
                scroll_top = self._virtual_state.scroll_position * max(
                    0,
                    self._virtual_state.total_height
                    - self._virtual_state.container_height,
                )
                self._scroll_canvas.yview_moveto(
                    scroll_top / self._virtual_state.total_height
                )

        except Exception as e:
            self._logger.error(f"更新滚动条失败: {e}")

    def _on_scrollbar_scroll(self, *args) -> None:
        """滚动条滚动事件处理"""
        try:
            if args[0] == "moveto":
                # 滚动到指定位置
                position = float(args[1])
                self._virtual_state.scroll_position = position

            elif args[0] in ("scroll", "units"):
                # 按单位滚动
                delta = int(args[1])
                step_size = 1.0 / max(1, self._virtual_state.total_items - 1)
                new_position = self._virtual_state.scroll_position + (delta * step_size)
                self._virtual_state.scroll_position = max(0.0, min(1.0, new_position))

            # 重新计算和渲染
            self._calculate_visible_range()
            self._render_visible_items()

        except Exception as e:
            self._logger.error(f"滚动条事件处理失败: {e}")

    def _on_mouse_wheel(self, event) -> None:
        """鼠标滚轮事件处理"""
        try:
            # 计算滚动增量
            if event.delta:
                delta = -event.delta / 120  # Windows
            elif event.num == 4:
                delta = -1  # Linux向上
            elif event.num == 5:
                delta = 1  # Linux向下
            else:
                return

            # 应用滚动灵敏度
            delta *= self._virtual_config.scroll_sensitivity

            # 计算新位置
            step_size = 3.0 / max(1, self._virtual_state.total_items)
            new_position = self._virtual_state.scroll_position + (delta * step_size)
            self._virtual_state.scroll_position = max(0.0, min(1.0, new_position))

            # 重新计算和渲染
            self._calculate_visible_range()
            self._render_visible_items()

        except Exception as e:
            self._logger.error(f"鼠标滚轮事件处理失败: {e}")

    def _on_key_scroll(self, event) -> None:
        """键盘滚动事件处理"""
        try:
            key = event.keysym

            if key in ("Up", "Down"):
                delta = 1 if key == "Down" else -1
                step_size = 1.0 / max(1, self._virtual_state.total_items)

            elif key in ("Prior", "Next"):  # Page Up/Down
                delta = 10 if key == "Next" else -10
                step_size = 1.0 / max(1, self._virtual_state.total_items)

            else:
                return

            # 计算新位置
            new_position = self._virtual_state.scroll_position + (delta * step_size)
            self._virtual_state.scroll_position = max(0.0, min(1.0, new_position))

            # 重新计算和渲染
            self._calculate_visible_range()
            self._render_visible_items()

        except Exception as e:
            self._logger.error(f"键盘滚动事件处理失败: {e}")

    def _on_canvas_configure(self, event) -> None:
        """画布大小变化事件处理"""
        try:
            # 更新容器高度
            self._virtual_state.container_height = event.height

            # 更新画布窗口大小
            self._scroll_canvas.itemconfig(self._canvas_window, width=event.width)

            # 重新计算可见范围
            self._calculate_visible_range()
            self._render_visible_items()

        except Exception as e:
            self._logger.error(f"画布配置事件处理失败: {e}")

    def _on_content_configure(self, event) -> None:
        """内容框架配置事件处理"""
        try:
            # 更新滚动区域
            self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all"))

        except Exception as e:
            self._logger.error(f"内容配置事件处理失败: {e}")

    # 公共接口方法

    def update_data_source(self, data_source: List[Any]) -> None:
        """更新数据源

        Args:
            data_source: 新的数据源
        """
        try:
            self._data_source = data_source

            # 清理所有渲染的项目
            for widget in self._virtual_state.rendered_items.values():
                if widget and widget.winfo_exists():
                    widget.destroy()
            self._virtual_state.rendered_items.clear()

            # 重新计算状态
            self._calculate_virtual_state()

            # 重新渲染
            self._render_visible_items()

            self._logger.info(f"数据源已更新,新项目数: {len(data_source)}")

        except Exception as e:
            self._logger.error(f"更新数据源失败: {e}")

    def scroll_to_item(self, index: int) -> None:
        """滚动到指定项目

        Args:
            index: 项目索引
        """
        try:
            if 0 <= index < self._virtual_state.total_items:
                # 计算滚动位置
                if self._virtual_state.total_items > 1:
                    position = index / (self._virtual_state.total_items - 1)
                else:
                    position = 0.0

                self._virtual_state.scroll_position = position

                # 重新计算和渲染
                self._calculate_visible_range()
                self._render_visible_items()

                self._logger.debug(f"滚动到项目: {index}")

        except Exception as e:
            self._logger.error(f"滚动到项目失败: {e}")

    def get_visible_range(self) -> Tuple[int, int]:
        """获取当前可见范围

        Returns:
            Tuple[int, int]: (起始索引, 结束索引)
        """
        return (self._virtual_state.visible_start, self._virtual_state.visible_end)

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息

        Returns:
            Dict[str, Any]: 性能统计信息
        """
        return {
            "total_items": self._virtual_state.total_items,
            "visible_items": self._virtual_state.visible_end
            - self._virtual_state.visible_start,
            "rendered_items": len(self._virtual_state.rendered_items),
            "render_count": self._render_count,
            "last_render_time": self._last_render_time,
            "scroll_position": self._virtual_state.scroll_position,
            "container_height": self._virtual_state.container_height,
            "total_height": self._virtual_state.total_height,
        }

    def set_item_height_calculator(self, calculator: Callable[[Any, int], int]) -> None:
        """设置项目高度计算器(用于动态高度)

        Args:
            calculator: 高度计算函数,接收(数据项, 索引),返回高度
        """
        self._item_height_calculator = calculator
        self._virtual_config.enable_dynamic_height = True

        # 重新计算状态
        self._calculate_virtual_state()
        self._render_visible_items()

    def configure_virtual_scroll(self, **kwargs) -> None:
        """配置虚拟滚动参数

        Args:
            **kwargs: 配置参数
        """
        for key, value in kwargs.items():
            if hasattr(self._virtual_config, key):
                setattr(self._virtual_config, key, value)

        # 重新计算状态
        self._calculate_virtual_state()
        self._render_visible_items()

    @abstractmethod
    def create_item_widget(self, parent: tk.Widget, data: Any, index: int) -> tk.Widget:
        """创建项目组件(子类必须实现)

        Args:
            parent: 父组件
            data: 数据项
            index: 项目索引

        Returns:
            tk.Widget: 创建的组件
        """


class VirtualListBox(tk.Frame, VirtualScrollMixin):
    """虚拟列表框实现示例"""

    def __init__(self, parent, **kwargs):
        """初始化虚拟列表框"""
        super().__init__(parent, **kwargs)

        # 设置默认项目渲染器
        self._setup_default_renderer()

    def _setup_default_renderer(self) -> None:
        """设置默认项目渲染器"""

        def default_renderer(parent, data, index):
            return self.create_item_widget(parent, data, index)

        self._item_renderer = default_renderer

    def create_item_widget(self, parent: tk.Widget, data: Any, index: int) -> tk.Widget:
        """创建列表项组件"""
        # 创建项目框架
        item_frame = tk.Frame(
            parent,
            relief=tk.FLAT,
            borderwidth=1,
            height=self._virtual_config.item_height,
        )

        # 创建标签显示数据
        label = tk.Label(item_frame, text=str(data), anchor=tk.W, padx=5, pady=2)
        label.pack(fill=tk.BOTH, expand=True)

        # 绑定选择事件
        def on_click(event):
            self._on_item_selected(index, data)

        item_frame.bind("<Button-1>", on_click)
        label.bind("<Button-1>", on_click)

        return item_frame

    def _on_item_selected(self, index: int, data: Any) -> None:
        """项目选择事件处理"""
        # 可以在子类中重写此方法
        self._logger.debug(f"选择项目: {index}, 数据: {data}")

    def set_data(self, data: List[Any]) -> None:
        """设置列表数据"""
        if not hasattr(self, "_scroll_container") or not self._scroll_container:
            # 如果还没有设置虚拟滚动,先设置
            self.setup_virtual_scroll(
                parent=self, data_source=data, item_renderer=self._item_renderer
            )
        else:
            # 更新数据源
            self.update_data_source(data)
