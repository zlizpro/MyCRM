"""TTK图表组件系统

提供matplotlib图表与TTK界面的集成功能,包括:
- ChartContainerTTK类,集成matplotlib到TTK界面
- 支持柱状图、折线图、饼图、散点图等图表类型
- 实现图表交互功能:缩放、平移、数据点提示
- 与TTK主题系统集成
- 图表数据管理和更新

设计目标:
1. 提供简单易用的图表API
2. 支持多种图表类型和交互功能
3. 与TTK主题系统无缝集成
4. 确保良好的性能表现

作者: MiniCRM开发团队
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional, Tuple, Union


# matplotlib相关导入
try:
    import matplotlib

    matplotlib.use("TkAgg")  # 设置matplotlib使用tkinter后端

    from matplotlib import patches
    from matplotlib.animation import FuncAnimation
    from matplotlib.backends.backend_tkagg import (
        FigureCanvasTkAgg,
        NavigationToolbar2Tk,
    )
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    import numpy as np

    MATPLOTLIB_AVAILABLE = True
except ImportError as e:
    MATPLOTLIB_AVAILABLE = False
    logging.getLogger(__name__).warning(f"matplotlib不可用: {e}")

from .base_widget import BaseWidget
from .style_manager import get_global_style_manager


class ChartType(Enum):
    """图表类型枚举"""

    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    BOX = "box"
    AREA = "area"


@dataclass
class ChartData:
    """图表数据类"""

    x_data: List[Any]
    y_data: List[Any]
    labels: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None


@dataclass
class ChartStyle:
    """图表样式配置"""

    # 颜色配置
    background_color: str = "#FFFFFF"
    text_color: str = "#212529"
    grid_color: str = "#E9ECEF"
    accent_color: str = "#007BFF"

    # 字体配置
    font_family: str = "Microsoft YaHei UI"
    font_size: int = 9
    title_font_size: int = 12

    # 布局配置
    figure_size: Tuple[float, float] = (8, 6)
    dpi: int = 100
    tight_layout: bool = True

    # 网格配置
    show_grid: bool = True
    grid_alpha: float = 0.3

    # 图例配置
    show_legend: bool = True
    legend_location: str = "best"


class ChartInteractionHandler:
    """图表交互处理器"""

    def __init__(self, canvas: "FigureCanvasTkAgg", figure: Figure):
        """初始化交互处理器

        Args:
            canvas: matplotlib画布
            figure: matplotlib图形对象
        """
        self.canvas = canvas
        self.figure = figure
        self.logger = logging.getLogger(__name__)

        # 交互状态
        self._pan_active = False
        self._zoom_active = False
        self._last_mouse_pos = None

        # 数据点提示
        self._tooltip_active = True
        self._tooltip_annotation = None

        # 绑定事件
        self._bind_events()

    def _bind_events(self) -> None:
        """绑定交互事件"""
        # 鼠标事件
        self.canvas.mpl_connect("button_press_event", self._on_mouse_press)
        self.canvas.mpl_connect("button_release_event", self._on_mouse_release)
        self.canvas.mpl_connect("motion_notify_event", self._on_mouse_move)
        self.canvas.mpl_connect("scroll_event", self._on_scroll)

        # 键盘事件
        self.canvas.mpl_connect("key_press_event", self._on_key_press)
        self.canvas.mpl_connect("key_release_event", self._on_key_release)

    def _on_mouse_press(self, event) -> None:
        """鼠标按下事件处理"""
        if event.inaxes is None:
            return

        self._last_mouse_pos = (event.x, event.y)

        # 中键或Ctrl+左键开启平移
        if event.button == 2 or (event.button == 1 and event.key == "ctrl"):
            self._pan_active = True
            self.canvas.get_tk_widget().config(cursor="fleur")

    def _on_mouse_release(self, event) -> None:
        """鼠标释放事件处理"""
        self._pan_active = False
        self._zoom_active = False
        self.canvas.get_tk_widget().config(cursor="")

    def _on_mouse_move(self, event) -> None:
        """鼠标移动事件处理"""
        if event.inaxes is None:
            return

        # 处理平移
        if self._pan_active and self._last_mouse_pos:
            dx = event.x - self._last_mouse_pos[0]
            dy = event.y - self._last_mouse_pos[1]
            self._pan_view(dx, dy)
            self._last_mouse_pos = (event.x, event.y)

        # 处理数据点提示
        if self._tooltip_active:
            self._update_tooltip(event)

    def _on_scroll(self, event) -> None:
        """滚轮事件处理(缩放)"""
        if event.inaxes is None:
            return

        # 缩放因子
        scale_factor = 1.1 if event.step > 0 else 1 / 1.1

        # 以鼠标位置为中心缩放
        self._zoom_at_point(event.xdata, event.ydata, scale_factor)

    def _on_key_press(self, event) -> None:
        """键盘按下事件处理"""
        if event.key == "r":
            # R键重置视图
            self.reset_view()
        elif event.key == "g":
            # G键切换网格显示
            self.toggle_grid()

    def _on_key_release(self, event) -> None:
        """键盘释放事件处理"""

    def _pan_view(self, dx: float, dy: float) -> None:
        """平移视图

        Args:
            dx: X方向偏移
            dy: Y方向偏移
        """
        for ax in self.figure.get_axes():
            # 获取当前视图范围
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()

            # 计算偏移量
            x_range = xlim[1] - xlim[0]
            y_range = ylim[1] - ylim[0]

            x_offset = -dx * x_range / self.canvas.get_tk_widget().winfo_width()
            y_offset = dy * y_range / self.canvas.get_tk_widget().winfo_height()

            # 应用偏移
            ax.set_xlim(xlim[0] + x_offset, xlim[1] + x_offset)
            ax.set_ylim(ylim[0] + y_offset, ylim[1] + y_offset)

        self.canvas.draw_idle()

    def _zoom_at_point(self, x: float, y: float, scale_factor: float) -> None:
        """在指定点缩放

        Args:
            x: 缩放中心X坐标
            y: 缩放中心Y坐标
            scale_factor: 缩放因子
        """
        for ax in self.figure.get_axes():
            # 获取当前视图范围
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()

            # 计算新的范围
            x_range = (xlim[1] - xlim[0]) * scale_factor
            y_range = (ylim[1] - ylim[0]) * scale_factor

            # 以指定点为中心
            new_xlim = (x - x_range / 2, x + x_range / 2)
            new_ylim = (y - y_range / 2, y + y_range / 2)

            ax.set_xlim(new_xlim)
            ax.set_ylim(new_ylim)

        self.canvas.draw_idle()

    def _update_tooltip(self, event) -> None:
        """更新数据点提示

        Args:
            event: 鼠标事件
        """
        # 这里实现数据点提示逻辑
        # 具体实现取决于图表类型和数据结构

    def reset_view(self) -> None:
        """重置视图到原始状态"""
        for ax in self.figure.get_axes():
            ax.relim()
            ax.autoscale()
        self.canvas.draw_idle()

    def toggle_grid(self) -> None:
        """切换网格显示"""
        for ax in self.figure.get_axes():
            # 获取当前网格状态并切换
            current_grid = ax.get_xgridlines() or ax.get_ygridlines()
            if current_grid:
                # 如果有网格线,检查第一条线的可见性
                is_visible = current_grid[0].get_visible() if current_grid else False
                ax.grid(not is_visible)
            else:
                # 如果没有网格线,启用网格
                ax.grid(True)
        self.canvas.draw_idle()

    def enable_tooltip(self, enabled: bool = True) -> None:
        """启用/禁用数据点提示

        Args:
            enabled: 是否启用
        """
        self._tooltip_active = enabled


class BaseChartRenderer(ABC):
    """基础图表渲染器抽象类"""

    def __init__(self, figure: Figure, style: ChartStyle):
        """初始化渲染器

        Args:
            figure: matplotlib图形对象
            style: 图表样式配置
        """
        self.figure = figure
        self.style = style
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def render(self, data: ChartData, ax: plt.Axes) -> None:
        """渲染图表

        Args:
            data: 图表数据
            ax: matplotlib轴对象
        """

    def apply_style(self, ax: plt.Axes) -> None:
        """应用样式到轴对象

        Args:
            ax: matplotlib轴对象
        """
        # 设置背景色
        ax.set_facecolor(self.style.background_color)
        self.figure.patch.set_facecolor(self.style.background_color)

        # 设置文本颜色
        ax.tick_params(colors=self.style.text_color)
        ax.xaxis.label.set_color(self.style.text_color)
        ax.yaxis.label.set_color(self.style.text_color)
        ax.title.set_color(self.style.text_color)

        # 设置网格
        if self.style.show_grid:
            ax.grid(True, color=self.style.grid_color, alpha=self.style.grid_alpha)

        # 设置字体
        plt.rcParams["font.family"] = self.style.font_family
        plt.rcParams["font.size"] = self.style.font_size


class BarChartRenderer(BaseChartRenderer):
    """柱状图渲染器"""

    def render(self, data: ChartData, ax: plt.Axes) -> None:
        """渲染柱状图"""
        colors = data.colors or [self.style.accent_color] * len(data.y_data)

        bars = ax.bar(data.x_data, data.y_data, color=colors)

        # 设置标题和标签
        if data.title:
            ax.set_title(data.title, fontsize=self.style.title_font_size)
        if data.x_label:
            ax.set_xlabel(data.x_label)
        if data.y_label:
            ax.set_ylabel(data.y_label)

        # 应用样式
        self.apply_style(ax)

        return bars


class LineChartRenderer(BaseChartRenderer):
    """折线图渲染器"""

    def render(self, data: ChartData, ax: plt.Axes) -> None:
        """渲染折线图"""
        color = data.colors[0] if data.colors else self.style.accent_color

        line = ax.plot(data.x_data, data.y_data, color=color, linewidth=2, marker="o")

        # 设置标题和标签
        if data.title:
            ax.set_title(data.title, fontsize=self.style.title_font_size)
        if data.x_label:
            ax.set_xlabel(data.x_label)
        if data.y_label:
            ax.set_ylabel(data.y_label)

        # 应用样式
        self.apply_style(ax)

        return line


class PieChartRenderer(BaseChartRenderer):
    """饼图渲染器"""

    def render(self, data: ChartData, ax: plt.Axes) -> None:
        """渲染饼图"""
        colors = data.colors or plt.cm.Set3(np.linspace(0, 1, len(data.y_data)))
        labels = data.labels or [f"项目{i + 1}" for i in range(len(data.y_data))]

        wedges, texts, autotexts = ax.pie(
            data.y_data, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90
        )

        # 设置标题
        if data.title:
            ax.set_title(data.title, fontsize=self.style.title_font_size)

        # 应用样式
        self.apply_style(ax)

        return wedges, texts, autotexts


class ScatterChartRenderer(BaseChartRenderer):
    """散点图渲染器"""

    def render(self, data: ChartData, ax: plt.Axes) -> None:
        """渲染散点图"""
        colors = data.colors or [self.style.accent_color] * len(data.x_data)

        scatter = ax.scatter(data.x_data, data.y_data, c=colors, alpha=0.7)

        # 设置标题和标签
        if data.title:
            ax.set_title(data.title, fontsize=self.style.title_font_size)
        if data.x_label:
            ax.set_xlabel(data.x_label)
        if data.y_label:
            ax.set_ylabel(data.y_label)

        # 应用样式
        self.apply_style(ax)

        return scatter


class ChartContainerTTK(BaseWidget):
    """TTK图表容器组件

    集成matplotlib图表到TTK界面,支持多种图表类型和交互功能.
    """

    def __init__(self, parent: tk.Widget, **kwargs):
        """初始化图表容器

        Args:
            parent: 父容器组件
            **kwargs: 其他参数
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib不可用,无法创建图表组件")

        # 图表相关属性
        self.figure: Optional[Figure] = None
        self.canvas: Optional[FigureCanvasTkAgg] = None
        self.toolbar: Optional[NavigationToolbar2Tk] = None
        self.interaction_handler: Optional[ChartInteractionHandler] = None

        # 图表数据和样式
        self.chart_data: Optional[ChartData] = None
        self.chart_style: ChartStyle = ChartStyle()
        self.chart_type: ChartType = ChartType.BAR

        # 渲染器映射
        self.renderers = {
            ChartType.BAR: BarChartRenderer,
            ChartType.LINE: LineChartRenderer,
            ChartType.PIE: PieChartRenderer,
            ChartType.SCATTER: ScatterChartRenderer,
        }

        super().__init__(parent, **kwargs)

        # 应用主题样式
        self._apply_theme_style()

    def _setup_ui(self) -> None:
        """设置UI布局"""
        # 创建matplotlib图形和画布
        self.figure = Figure(
            figsize=self.chart_style.figure_size,
            dpi=self.chart_style.dpi,
            facecolor=self.chart_style.background_color,
        )

        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # 创建工具栏(可选)
        self._create_toolbar()

        # 创建交互处理器
        self.interaction_handler = ChartInteractionHandler(self.canvas, self.figure)

        # 初始化空图表
        self._create_empty_chart()

    def _create_toolbar(self) -> None:
        """创建图表工具栏"""
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # 创建自定义工具栏按钮
        ttk.Button(toolbar_frame, text="重置视图", command=self.reset_view).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Button(toolbar_frame, text="保存图表", command=self.save_chart).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Button(toolbar_frame, text="切换网格", command=self.toggle_grid).pack(
            side=tk.LEFT, padx=2
        )

        # 图表类型选择
        self.chart_type_var = tk.StringVar(value=self.chart_type.value)
        chart_type_combo = ttk.Combobox(
            toolbar_frame,
            textvariable=self.chart_type_var,
            values=[ct.value for ct in ChartType],
            state="readonly",
            width=10,
        )
        chart_type_combo.pack(side=tk.LEFT, padx=2)
        chart_type_combo.bind("<<ComboboxSelected>>", self._on_chart_type_changed)

    def _create_empty_chart(self) -> None:
        """创建空图表"""
        ax = self.figure.add_subplot(111)
        ax.text(
            0.5,
            0.5,
            "暂无数据",
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes,
            fontsize=14,
            color=self.chart_style.text_color,
        )
        ax.set_facecolor(self.chart_style.background_color)

        if self.canvas:
            self.canvas.draw()

    def _apply_theme_style(self) -> None:
        """应用TTK主题样式到图表"""
        style_manager = get_global_style_manager()
        current_theme = style_manager.get_current_theme()

        if current_theme:
            # 从TTK主题获取颜色配置
            colors = current_theme.colors
            fonts = current_theme.fonts

            # 更新图表样式
            self.chart_style.background_color = colors.bg_primary
            self.chart_style.text_color = colors.text_primary
            self.chart_style.grid_color = colors.border_primary
            self.chart_style.accent_color = colors.primary

            # 更新字体配置
            if "default" in fonts:
                default_font = fonts["default"]
                self.chart_style.font_family = default_font.family
                self.chart_style.font_size = default_font.size

            if "heading" in fonts:
                heading_font = fonts["heading"]
                self.chart_style.title_font_size = heading_font.size

    def set_data(self, data: ChartData) -> None:
        """设置图表数据

        Args:
            data: 图表数据对象
        """
        self.chart_data = data
        self.refresh_chart()

    def set_chart_type(self, chart_type: Union[ChartType, str]) -> None:
        """设置图表类型

        Args:
            chart_type: 图表类型
        """
        if isinstance(chart_type, str):
            chart_type = ChartType(chart_type)

        self.chart_type = chart_type
        self.chart_type_var.set(chart_type.value)
        self.refresh_chart()

    def set_style(self, style: ChartStyle) -> None:
        """设置图表样式

        Args:
            style: 图表样式配置
        """
        self.chart_style = style
        self.refresh_chart()

    def refresh_chart(self) -> None:
        """刷新图表显示"""
        if not self.chart_data:
            self._create_empty_chart()
            return

        # 清除现有图表
        self.figure.clear()

        # 创建新的轴
        ax = self.figure.add_subplot(111)

        # 获取对应的渲染器
        renderer_class = self.renderers.get(self.chart_type)
        if not renderer_class:
            self.logger.warning(f"不支持的图表类型: {self.chart_type}")
            return

        # 创建渲染器并渲染图表
        renderer = renderer_class(self.figure, self.chart_style)
        renderer.render(self.chart_data, ax)

        # 应用紧凑布局
        if self.chart_style.tight_layout:
            self.figure.tight_layout()

        # 重绘画布
        if self.canvas:
            self.canvas.draw()

    def _on_chart_type_changed(self, event) -> None:
        """图表类型变化事件处理"""
        new_type = self.chart_type_var.get()
        self.set_chart_type(new_type)

    def reset_view(self) -> None:
        """重置视图"""
        if self.interaction_handler:
            self.interaction_handler.reset_view()

    def toggle_grid(self) -> None:
        """切换网格显示"""
        if self.interaction_handler:
            self.interaction_handler.toggle_grid()

    def save_chart(self, filename: Optional[str] = None, **kwargs) -> bool:
        """保存图表

        Args:
            filename: 保存文件名,None则弹出对话框
            **kwargs: 保存选项

        Returns:
            是否保存成功
        """
        if not filename:
            from tkinter import filedialog

            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("PDF files", "*.pdf"),
                    ("SVG files", "*.svg"),
                    ("All files", "*.*"),
                ],
            )

        if filename and self.figure:
            try:
                # 默认保存选项
                save_options = {
                    "dpi": 300,
                    "bbox_inches": "tight",
                    "facecolor": self.chart_style.background_color,
                    "edgecolor": "none",
                }
                save_options.update(kwargs)

                self.figure.savefig(filename, **save_options)
                self.logger.info(f"图表已保存: {filename}")
                return True
            except Exception as e:
                self.logger.error(f"保存图表失败: {e}")
                return False
        return False

    def export_chart_batch(
        self, base_filename: str, formats: List[str] = None
    ) -> Dict[str, bool]:
        """批量导出图表为多种格式

        Args:
            base_filename: 基础文件名(不含扩展名)
            formats: 导出格式列表,默认为['png', 'pdf', 'svg']

        Returns:
            各格式导出结果字典
        """
        if formats is None:
            formats = ["png", "pdf", "svg"]

        results = {}
        for fmt in formats:
            filename = f"{base_filename}.{fmt}"
            success = self.save_chart(filename)
            results[fmt] = success

        return results

    def print_chart(self) -> None:
        """打印图表"""
        try:
            # 在Windows上可以使用默认打印机
            import os
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                self.save_chart(tmp_file.name)

                # 尝试使用系统默认程序打开文件进行打印
                if os.name == "nt":  # Windows
                    os.startfile(tmp_file.name, "print")
                elif os.name == "posix":  # macOS/Linux
                    os.system(f'lpr "{tmp_file.name}"')

        except Exception as e:
            self.logger.error(f"打印图表失败: {e}")

    def apply_theme_style(self, theme_name: str) -> None:
        """应用指定主题样式

        Args:
            theme_name: 主题名称
        """
        style_manager = get_global_style_manager()
        if style_manager.apply_theme(theme_name):
            self._apply_theme_style()
            self.refresh_chart()

    def create_custom_style(self, **style_options) -> ChartStyle:
        """创建自定义样式

        Args:
            **style_options: 样式选项

        Returns:
            自定义样式对象
        """
        current_style = self.chart_style
        custom_style = ChartStyle(
            background_color=style_options.get(
                "background_color", current_style.background_color
            ),
            text_color=style_options.get("text_color", current_style.text_color),
            grid_color=style_options.get("grid_color", current_style.grid_color),
            accent_color=style_options.get("accent_color", current_style.accent_color),
            font_family=style_options.get("font_family", current_style.font_family),
            font_size=style_options.get("font_size", current_style.font_size),
            title_font_size=style_options.get(
                "title_font_size", current_style.title_font_size
            ),
            figure_size=style_options.get("figure_size", current_style.figure_size),
            dpi=style_options.get("dpi", current_style.dpi),
            show_grid=style_options.get("show_grid", current_style.show_grid),
            show_legend=style_options.get("show_legend", current_style.show_legend),
        )
        return custom_style

    def export_data(self) -> Optional[Dict[str, Any]]:
        """导出图表数据

        Returns:
            图表数据字典
        """
        if not self.chart_data:
            return None

        return {
            "chart_type": self.chart_type.value,
            "x_data": self.chart_data.x_data,
            "y_data": self.chart_data.y_data,
            "labels": self.chart_data.labels,
            "title": self.chart_data.title,
            "x_label": self.chart_data.x_label,
            "y_label": self.chart_data.y_label,
        }

    def cleanup(self) -> None:
        """清理资源"""
        try:
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
            if self.figure:
                plt.close(self.figure)
        except Exception as e:
            self.logger.error(f"清理图表资源失败: {e}")

        super().cleanup()


# 便利函数
def create_chart_data(
    x_data: List[Any],
    y_data: List[Any],
    labels: Optional[List[str]] = None,
    title: Optional[str] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    colors: Optional[List[str]] = None,
) -> ChartData:
    """创建图表数据对象

    Args:
        x_data: X轴数据
        y_data: Y轴数据
        labels: 数据标签
        title: 图表标题
        x_label: X轴标签
        y_label: Y轴标签
        colors: 颜色列表

    Returns:
        图表数据对象
    """
    return ChartData(
        x_data=x_data,
        y_data=y_data,
        labels=labels,
        title=title,
        x_label=x_label,
        y_label=y_label,
        colors=colors,
    )


def create_chart_style(**kwargs) -> ChartStyle:
    """创建图表样式对象

    Args:
        **kwargs: 样式参数

    Returns:
        图表样式对象
    """
    return ChartStyle(**kwargs)


# 预定义图表主题
class ChartThemes:
    """预定义图表主题集合"""

    @staticmethod
    def get_business_theme() -> ChartStyle:
        """商务主题"""
        return ChartStyle(
            background_color="#FFFFFF",
            text_color="#2C3E50",
            grid_color="#ECF0F1",
            accent_color="#3498DB",
            font_family="Arial",
            font_size=10,
            title_font_size=14,
            show_grid=True,
            grid_alpha=0.3,
        )

    @staticmethod
    def get_dark_theme() -> ChartStyle:
        """深色主题"""
        return ChartStyle(
            background_color="#2B2B2B",
            text_color="#FFFFFF",
            grid_color="#555555",
            accent_color="#E74C3C",
            font_family="Arial",
            font_size=10,
            title_font_size=14,
            show_grid=True,
            grid_alpha=0.4,
        )

    @staticmethod
    def get_colorful_theme() -> ChartStyle:
        """彩色主题"""
        return ChartStyle(
            background_color="#F8F9FA",
            text_color="#495057",
            grid_color="#DEE2E6",
            accent_color="#FF6B6B",
            font_family="Arial",
            font_size=10,
            title_font_size=14,
            show_grid=True,
            grid_alpha=0.2,
        )

    @staticmethod
    def get_minimal_theme() -> ChartStyle:
        """简约主题"""
        return ChartStyle(
            background_color="#FFFFFF",
            text_color="#333333",
            grid_color="#F0F0F0",
            accent_color="#666666",
            font_family="Arial",
            font_size=9,
            title_font_size=12,
            show_grid=False,
            show_legend=False,
        )

    @staticmethod
    def get_presentation_theme() -> ChartStyle:
        """演示主题"""
        return ChartStyle(
            background_color="#FFFFFF",
            text_color="#1A1A1A",
            grid_color="#E8E8E8",
            accent_color="#007ACC",
            font_family="Arial",
            font_size=12,
            title_font_size=16,
            figure_size=(10, 7),
            dpi=150,
            show_grid=True,
            grid_alpha=0.3,
        )


class ChartStylePresets:
    """图表样式预设"""

    # 颜色调色板
    COLOR_PALETTES = {
        "default": ["#007BFF", "#28A745", "#FFC107", "#DC3545", "#17A2B8"],
        "pastel": ["#FFB3BA", "#BAFFC9", "#BAE1FF", "#FFFFBA", "#FFDFBA"],
        "vibrant": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],
        "professional": ["#2C3E50", "#3498DB", "#E74C3C", "#F39C12", "#9B59B6"],
        "earth": ["#8B4513", "#228B22", "#DAA520", "#CD853F", "#A0522D"],
        "ocean": ["#006994", "#0085C3", "#00A6FB", "#7DD3FC", "#B8E6FF"],
        "sunset": ["#FF6B35", "#F7931E", "#FFD23F", "#06FFA5", "#118AB2"],
    }

    @staticmethod
    def get_color_palette(name: str) -> List[str]:
        """获取颜色调色板

        Args:
            name: 调色板名称

        Returns:
            颜色列表
        """
        return ChartStylePresets.COLOR_PALETTES.get(
            name, ChartStylePresets.COLOR_PALETTES["default"]
        )

    @staticmethod
    def apply_color_palette(chart_data: ChartData, palette_name: str) -> ChartData:
        """应用颜色调色板到图表数据

        Args:
            chart_data: 图表数据
            palette_name: 调色板名称

        Returns:
            应用调色板后的图表数据
        """
        colors = ChartStylePresets.get_color_palette(palette_name)
        data_length = len(chart_data.y_data)

        # 循环使用颜色
        chart_colors = [colors[i % len(colors)] for i in range(data_length)]

        # 创建新的图表数据对象
        new_data = ChartData(
            x_data=chart_data.x_data,
            y_data=chart_data.y_data,
            labels=chart_data.labels,
            colors=chart_colors,
            title=chart_data.title,
            x_label=chart_data.x_label,
            y_label=chart_data.y_label,
        )

        return new_data


class ChartExportManager:
    """图表导出管理器"""

    def __init__(self, chart_container: ChartContainerTTK):
        """初始化导出管理器

        Args:
            chart_container: 图表容器
        """
        self.chart_container = chart_container
        self.logger = logging.getLogger(__name__)

    def export_with_watermark(
        self, filename: str, watermark_text: str = "MiniCRM"
    ) -> bool:
        """导出带水印的图表

        Args:
            filename: 文件名
            watermark_text: 水印文字

        Returns:
            是否导出成功
        """
        try:
            # 添加水印
            fig = self.chart_container.figure
            fig.text(
                0.99,
                0.01,
                watermark_text,
                fontsize=8,
                color="gray",
                alpha=0.5,
                ha="right",
                va="bottom",
            )

            # 保存图表
            success = self.chart_container.save_chart(filename)

            # 移除水印(恢复原状)
            for text in fig.texts:
                if text.get_text() == watermark_text:
                    text.remove()
                    break

            return success

        except Exception as e:
            self.logger.error(f"导出带水印图表失败: {e}")
            return False

    def export_high_quality(self, filename: str) -> bool:
        """导出高质量图表

        Args:
            filename: 文件名

        Returns:
            是否导出成功
        """
        return self.chart_container.save_chart(
            filename,
            dpi=600,
            bbox_inches="tight",
            pad_inches=0.2,
            facecolor="white",
            edgecolor="none",
        )

    def export_for_web(self, filename: str) -> bool:
        """导出适合网页的图表

        Args:
            filename: 文件名

        Returns:
            是否导出成功
        """
        return self.chart_container.save_chart(
            filename,
            dpi=96,
            bbox_inches="tight",
            pad_inches=0.1,
            format="png",
            optimize=True,
        )

    def export_for_print(self, filename: str) -> bool:
        """导出适合打印的图表

        Args:
            filename: 文件名

        Returns:
            是否导出成功
        """
        return self.chart_container.save_chart(
            filename, dpi=300, bbox_inches="tight", pad_inches=0.3, format="pdf"
        )


# 工具函数扩展
def create_themed_chart_data(
    x_data: List[Any], y_data: List[Any], theme_name: str = "default", **kwargs
) -> ChartData:
    """创建带主题的图表数据

    Args:
        x_data: X轴数据
        y_data: Y轴数据
        theme_name: 主题名称
        **kwargs: 其他参数

    Returns:
        图表数据对象
    """
    chart_data = create_chart_data(x_data, y_data, **kwargs)
    return ChartStylePresets.apply_color_palette(chart_data, theme_name)


def create_business_chart(
    chart_type: ChartType, data: Dict[str, Any], title: str = "", **style_options
) -> Tuple[ChartData, ChartStyle]:
    """创建商务图表

    Args:
        chart_type: 图表类型
        data: 数据字典,包含x_data和y_data
        title: 图表标题
        **style_options: 样式选项

    Returns:
        (图表数据, 图表样式) 元组
    """
    # 创建图表数据
    chart_data = ChartData(
        x_data=data.get("x_data", []),
        y_data=data.get("y_data", []),
        labels=data.get("labels"),
        title=title,
        x_label=data.get("x_label", ""),
        y_label=data.get("y_label", ""),
    )

    # 应用商务主题颜色
    chart_data = ChartStylePresets.apply_color_palette(chart_data, "professional")

    # 创建商务样式
    style = ChartThemes.get_business_theme()

    # 应用自定义样式选项
    for key, value in style_options.items():
        if hasattr(style, key):
            setattr(style, key, value)

    return chart_data, style
