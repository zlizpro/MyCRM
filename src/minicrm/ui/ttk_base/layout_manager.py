"""TTK布局管理系统

提供统一的布局管理接口,支持多种布局方式:
- 网格布局 (GridLayout)
- 包装布局 (PackLayout)
- 表单布局 (FormLayout)
- 响应式布局助手函数

设计目标:
1. 封装tkinter复杂的几何管理器
2. 提供类似Qt的布局管理体验
3. 支持响应式和动态布局调整
4. 优化布局性能和内存使用

作者: MiniCRM开发团队
"""

from enum import Enum
import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Tuple


class LayoutType(Enum):
    """布局类型枚举"""

    GRID = "grid"
    PACK = "pack"
    FORM = "form"
    RESPONSIVE = "responsive"


class Alignment(Enum):
    """对齐方式枚举"""

    LEFT = "w"
    RIGHT = "e"
    CENTER = "center"
    TOP = "n"
    BOTTOM = "s"
    FILL = "fill"


class LayoutManager:
    """TTK布局管理器

    提供统一的布局管理接口,封装tkinter的几何管理器,
    支持多种布局方式和响应式布局功能.
    """

    def __init__(self, parent: tk.Widget):
        """初始化布局管理器

        Args:
            parent: 父容器组件
        """
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self._layouts: Dict[str, Any] = {}
        self._responsive_callbacks: List[Callable] = []

        # 绑定窗口大小变化事件,支持响应式布局
        if hasattr(parent, "bind"):
            parent.bind("<Configure>", self._on_window_configure)

    def create_grid_layout(
        self,
        rows: int,
        cols: int,
        padding: Tuple[int, int] = (5, 5),
        uniform_columns: bool = False,
        uniform_rows: bool = False,
    ) -> "GridLayoutHelper":
        """创建网格布局

        Args:
            rows: 行数
            cols: 列数
            padding: 内边距 (padx, pady)
            uniform_columns: 是否统一列宽
            uniform_rows: 是否统一行高

        Returns:
            GridLayoutHelper: 网格布局助手对象
        """
        layout = GridLayoutHelper(
            self.parent, rows, cols, padding, uniform_columns, uniform_rows
        )
        self._layouts[f"grid_{len(self._layouts)}"] = layout
        return layout

    def create_pack_layout(
        self,
        side: str = "top",
        fill: str = "none",
        expand: bool = False,
        padding: Tuple[int, int] = (5, 5),
    ) -> "PackLayoutHelper":
        """创建包装布局

        Args:
            side: 放置方向 ("top", "bottom", "left", "right")
            fill: 填充方式 ("none", "x", "y", "both")
            expand: 是否扩展
            padding: 内边距 (padx, pady)

        Returns:
            PackLayoutHelper: 包装布局助手对象
        """
        layout = PackLayoutHelper(self.parent, side, fill, expand, padding)
        self._layouts[f"pack_{len(self._layouts)}"] = layout
        return layout

    def create_form_layout(
        self,
        fields: List[Dict[str, Any]],
        label_width: int = 100,
        field_width: int = 200,
        padding: Tuple[int, int] = (5, 2),
    ) -> "FormLayoutHelper":
        """创建表单布局

        Args:
            fields: 字段配置列表
            label_width: 标签宽度
            field_width: 字段宽度
            padding: 内边距 (padx, pady)

        Returns:
            FormLayoutHelper: 表单布局助手对象
        """
        layout = FormLayoutHelper(
            self.parent, fields, label_width, field_width, padding
        )
        self._layouts[f"form_{len(self._layouts)}"] = layout
        return layout

    def add_responsive_callback(self, callback: Callable[[int, int], None]) -> None:
        """添加响应式布局回调函数

        Args:
            callback: 回调函数,接收窗口宽度和高度参数
        """
        self._responsive_callbacks.append(callback)

    def _on_window_configure(self, event) -> None:
        """窗口大小变化事件处理

        Args:
            event: 配置事件对象
        """
        if event.widget == self.parent:
            width = event.width
            height = event.height

            # 调用所有响应式回调函数
            for callback in self._responsive_callbacks:
                try:
                    callback(width, height)
                except Exception as e:
                    self.logger.error(f"响应式布局回调执行失败: {e}")

    def clear_layouts(self) -> None:
        """清理所有布局"""
        for layout in self._layouts.values():
            if hasattr(layout, "clear"):
                layout.clear()
        self._layouts.clear()


class GridLayoutHelper:
    """网格布局助手类

    提供网格布局的便捷操作接口,支持组件的网格放置、
    跨行跨列、对齐方式等功能.
    """

    def __init__(
        self,
        parent: tk.Widget,
        rows: int,
        cols: int,
        padding: Tuple[int, int],
        uniform_columns: bool,
        uniform_rows: bool,
    ):
        """初始化网格布局助手

        Args:
            parent: 父容器
            rows: 行数
            cols: 列数
            padding: 内边距
            uniform_columns: 统一列宽
            uniform_rows: 统一行高
        """
        self.parent = parent
        self.rows = rows
        self.cols = cols
        self.padding = padding
        self._widgets: Dict[Tuple[int, int], tk.Widget] = {}

        # 配置网格权重,支持自适应大小
        if uniform_columns:
            for col in range(cols):
                parent.columnconfigure(col, weight=1, uniform="col")

        if uniform_rows:
            for row in range(rows):
                parent.rowconfigure(row, weight=1, uniform="row")

    def add_widget(
        self,
        widget: tk.Widget,
        row: int,
        col: int,
        rowspan: int = 1,
        columnspan: int = 1,
        sticky: str = "w",
        padx: Optional[int] = None,
        pady: Optional[int] = None,
    ) -> None:
        """添加组件到网格

        Args:
            widget: 要添加的组件
            row: 行位置
            col: 列位置
            rowspan: 跨行数
            columnspan: 跨列数
            sticky: 对齐方式
            padx: 水平内边距
            pady: 垂直内边距
        """
        if row >= self.rows or col >= self.cols:
            raise ValueError(f"位置超出网格范围: ({row}, {col})")

        # 使用默认内边距
        if padx is None:
            padx = self.padding[0]
        if pady is None:
            pady = self.padding[1]

        widget.grid(
            row=row,
            column=col,
            rowspan=rowspan,
            columnspan=columnspan,
            sticky=sticky,
            padx=padx,
            pady=pady,
        )

        self._widgets[(row, col)] = widget

    def remove_widget(self, row: int, col: int) -> None:
        """移除指定位置的组件

        Args:
            row: 行位置
            col: 列位置
        """
        if (row, col) in self._widgets:
            widget = self._widgets[(row, col)]
            widget.grid_forget()
            del self._widgets[(row, col)]

    def get_widget(self, row: int, col: int) -> Optional[tk.Widget]:
        """获取指定位置的组件

        Args:
            row: 行位置
            col: 列位置

        Returns:
            组件对象或None
        """
        return self._widgets.get((row, col))

    def clear(self) -> None:
        """清理所有组件"""
        for widget in self._widgets.values():
            widget.grid_forget()
        self._widgets.clear()


class PackLayoutHelper:
    """包装布局助手类

    提供包装布局的便捷操作接口,支持组件的顺序放置、
    填充方式、扩展等功能.
    """

    def __init__(
        self,
        parent: tk.Widget,
        side: str,
        fill: str,
        expand: bool,
        padding: Tuple[int, int],
    ):
        """初始化包装布局助手

        Args:
            parent: 父容器
            side: 放置方向
            fill: 填充方式
            expand: 是否扩展
            padding: 内边距
        """
        self.parent = parent
        self.side = side
        self.fill = fill
        self.expand = expand
        self.padding = padding
        self._widgets: List[tk.Widget] = []

    def add_widget(
        self,
        widget: tk.Widget,
        side: Optional[str] = None,
        fill: Optional[str] = None,
        expand: Optional[bool] = None,
        padx: Optional[int] = None,
        pady: Optional[int] = None,
    ) -> None:
        """添加组件到布局

        Args:
            widget: 要添加的组件
            side: 放置方向(覆盖默认值)
            fill: 填充方式(覆盖默认值)
            expand: 是否扩展(覆盖默认值)
            padx: 水平内边距
            pady: 垂直内边距
        """
        # 使用参数或默认值
        actual_side = side or self.side
        actual_fill = fill or self.fill
        actual_expand = expand if expand is not None else self.expand
        actual_padx = padx if padx is not None else self.padding[0]
        actual_pady = pady if pady is not None else self.padding[1]

        widget.pack(
            side=actual_side,
            fill=actual_fill,
            expand=actual_expand,
            padx=actual_padx,
            pady=actual_pady,
        )

        self._widgets.append(widget)

    def remove_widget(self, widget: tk.Widget) -> None:
        """移除指定组件

        Args:
            widget: 要移除的组件
        """
        if widget in self._widgets:
            widget.pack_forget()
            self._widgets.remove(widget)

    def clear(self) -> None:
        """清理所有组件"""
        for widget in self._widgets:
            widget.pack_forget()
        self._widgets.clear()


class FormLayoutHelper:
    """表单布局助手类

    提供表单布局的便捷操作接口,自动创建标签-输入框对,
    支持多种输入组件类型和验证功能.
    """

    def __init__(
        self,
        parent: tk.Widget,
        fields: List[Dict[str, Any]],
        label_width: int,
        field_width: int,
        padding: Tuple[int, int],
    ):
        """初始化表单布局助手

        Args:
            parent: 父容器
            fields: 字段配置列表
            label_width: 标签宽度
            field_width: 字段宽度
            padding: 内边距
        """
        self.parent = parent
        self.fields = fields
        self.label_width = label_width
        self.field_width = field_width
        self.padding = padding
        self.widgets: Dict[str, tk.Widget] = {}
        self.labels: Dict[str, ttk.Label] = {}

        self._create_form()

    def _create_form(self) -> None:
        """创建表单界面"""
        for i, field in enumerate(self.fields):
            self._create_field(i, field)

    def _create_field(self, row: int, field: Dict[str, Any]) -> None:
        """创建表单字段

        Args:
            row: 行位置
            field: 字段配置
        """
        field_id = field.get("id", f"field_{row}")
        label_text = field.get("label", "")
        field_type = field.get("type", "entry")
        required = field.get("required", False)

        # 创建标签
        if required:
            label_text += " *"

        label = ttk.Label(self.parent, text=label_text, width=self.label_width)
        label.grid(
            row=row, column=0, sticky="w", padx=self.padding[0], pady=self.padding[1]
        )
        self.labels[field_id] = label

        # 创建输入组件
        widget = self._create_input_widget(field_type, field)
        widget.grid(
            row=row, column=1, sticky="ew", padx=self.padding[0], pady=self.padding[1]
        )
        self.widgets[field_id] = widget

        # 配置列权重,使输入框可以扩展
        self.parent.columnconfigure(1, weight=1)

    def _create_input_widget(self, field_type: str, field: Dict[str, Any]) -> tk.Widget:
        """创建输入组件

        Args:
            field_type: 字段类型
            field: 字段配置

        Returns:
            创建的输入组件
        """
        if field_type == "entry":
            widget = ttk.Entry(self.parent, width=self.field_width)
        elif field_type == "text":
            widget = tk.Text(self.parent, width=self.field_width, height=4)
        elif field_type == "combobox":
            widget = ttk.Combobox(self.parent, width=self.field_width)
            if "options" in field:
                widget["values"] = field["options"]
        elif field_type == "checkbox":
            widget = ttk.Checkbutton(self.parent)
        elif field_type == "spinbox":
            widget = ttk.Spinbox(self.parent, width=self.field_width)
            if "from_" in field:
                widget["from_"] = field["from_"]
            if "to" in field:
                widget["to"] = field["to"]
        else:
            # 默认使用Entry
            widget = ttk.Entry(self.parent, width=self.field_width)

        return widget

    def get_values(self) -> Dict[str, Any]:
        """获取表单所有字段的值

        Returns:
            字段值字典
        """
        values = {}
        for field_id, widget in self.widgets.items():
            values[field_id] = self._get_widget_value(widget)
        return values

    def set_values(self, values: Dict[str, Any]) -> None:
        """设置表单字段的值

        Args:
            values: 字段值字典
        """
        for field_id, value in values.items():
            if field_id in self.widgets:
                widget = self.widgets[field_id]
                self._set_widget_value(widget, value)

    def _get_widget_value(self, widget: tk.Widget) -> Any:
        """获取组件的值

        Args:
            widget: 组件对象

        Returns:
            组件的值
        """
        if isinstance(widget, (ttk.Entry, ttk.Combobox, ttk.Spinbox)):
            return widget.get()
        if isinstance(widget, tk.Text):
            return widget.get("1.0", tk.END).strip()
        if isinstance(widget, ttk.Checkbutton):
            return widget.instate(["selected"])
        return None

    def _set_widget_value(self, widget: tk.Widget, value: Any) -> None:
        """设置组件的值

        Args:
            widget: 组件对象
            value: 要设置的值
        """
        if isinstance(widget, (ttk.Entry, ttk.Combobox, ttk.Spinbox)):
            widget.delete(0, tk.END)
            widget.insert(0, str(value))
        elif isinstance(widget, tk.Text):
            widget.delete("1.0", tk.END)
            widget.insert("1.0", str(value))
        elif isinstance(widget, ttk.Checkbutton):
            if value:
                widget.state(["selected"])
            else:
                widget.state(["!selected"])

    def clear(self) -> None:
        """清理表单"""
        for widget in self.widgets.values():
            widget.grid_forget()
        for label in self.labels.values():
            label.grid_forget()
        self.widgets.clear()
        self.labels.clear()


# 响应式布局助手函数
def create_responsive_layout(
    parent: tk.Widget, breakpoints: Dict[int, Callable]
) -> Callable:
    """创建响应式布局

    Args:
        parent: 父容器
        breakpoints: 断点配置,键为宽度阈值,值为布局函数

    Returns:
        响应式布局处理函数
    """

    def handle_resize(width: int, height: int) -> None:
        """处理窗口大小变化"""
        # 找到合适的断点
        suitable_breakpoint = None
        for breakpoint_width in sorted(breakpoints.keys(), reverse=True):
            if width >= breakpoint_width:
                suitable_breakpoint = breakpoint_width
                break

        # 应用对应的布局
        if suitable_breakpoint is not None:
            layout_func = breakpoints[suitable_breakpoint]
            layout_func(parent, width, height)

    return handle_resize


def calculate_optimal_grid_size(
    item_count: int,
    container_width: int,
    item_width: int,
    min_cols: int = 1,
    max_cols: int = 10,
) -> Tuple[int, int]:
    """计算最优网格大小

    Args:
        item_count: 项目数量
        container_width: 容器宽度
        item_width: 项目宽度
        min_cols: 最小列数
        max_cols: 最大列数

    Returns:
        (行数, 列数) 元组
    """
    # 计算可容纳的列数
    cols = max(min_cols, min(max_cols, container_width // item_width))

    # 计算需要的行数
    rows = (item_count + cols - 1) // cols  # 向上取整

    return rows, cols
