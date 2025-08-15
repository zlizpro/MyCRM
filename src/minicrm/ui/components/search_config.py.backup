"""
MiniCRM 搜索栏配置类

定义搜索栏组件的配置选项，解决构造函数参数过多的问题。
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class SearchBarConfig:
    """
    搜索栏配置类

    用于配置SearchBar组件的各种选项，避免构造函数参数过多。
    """

    # 基础配置
    placeholder: str = "输入关键词搜索..."
    search_delay: int = 300  # 搜索延迟（毫秒）

    # 功能开关
    show_advanced: bool = True
    enable_history: bool = True
    enable_suggestions: bool = True
    enable_real_time: bool = True

    # 历史记录配置
    max_history_items: int = 20

    # 样式配置
    search_button_text: str = "🔍"
    clear_button_text: str = "✖️"
    advanced_button_text: str = "⚙️"

    # 高级搜索配置
    advanced_title: str = "高级搜索"
    apply_button_text: str = "应用筛选"
    reset_button_text: str = "重置筛选"

    @classmethod
    def create_simple(cls) -> "SearchBarConfig":
        """
        创建简单搜索配置（仅基础搜索功能）

        Returns:
            SearchBarConfig: 简单搜索配置
        """
        return cls(
            show_advanced=False,
            enable_history=False,
            enable_suggestions=False,
        )

    @classmethod
    def create_full_featured(cls) -> "SearchBarConfig":
        """
        创建全功能搜索配置

        Returns:
            SearchBarConfig: 全功能搜索配置
        """
        return cls(
            show_advanced=True,
            enable_history=True,
            enable_suggestions=True,
            enable_real_time=True,
            max_history_items=50,
        )


@dataclass
class FilterConfig:
    """
    筛选器配置类

    定义单个筛选器的配置选项。
    """

    key: str  # 筛选器键名
    title: str  # 显示标题
    filter_type: str  # 筛选器类型: combo|date|number|text|checkbox

    # 可选配置
    options: list[dict[str, Any]] | list[str] | None = None  # combo类型的选项
    default: Any = None  # 默认值
    min_value: int = 0  # number类型的最小值
    max_value: int = 999999  # number类型的最大值
    placeholder: str = ""  # text类型的占位符
    checkbox_text: str = ""  # checkbox类型的文本

    def __post_init__(self) -> None:
        """初始化后处理"""
        # 设置默认占位符
        if not self.placeholder and self.filter_type == "text":
            self.placeholder = f"筛选{self.title}..."

    @classmethod
    def create_combo(
        cls,
        key: str,
        title: str,
        options: list[dict[str, Any]] | list[str],
        default: Any = None,
    ) -> "FilterConfig":
        """
        创建下拉框筛选器配置

        Args:
            key: 筛选器键名
            title: 显示标题
            options: 选项列表
            default: 默认值

        Returns:
            FilterConfig: 下拉框筛选器配置
        """
        return cls(
            key=key,
            title=title,
            filter_type="combo",
            options=options,
            default=default,
        )

    @classmethod
    def create_date(
        cls,
        key: str,
        title: str,
        default: Any = None,
    ) -> "FilterConfig":
        """
        创建日期筛选器配置

        Args:
            key: 筛选器键名
            title: 显示标题
            default: 默认值

        Returns:
            FilterConfig: 日期筛选器配置
        """
        return cls(
            key=key,
            title=title,
            filter_type="date",
            default=default,
        )

    @classmethod
    def create_number(
        cls,
        key: str,
        title: str,
        min_value: int = 0,
        max_value: int = 999999,
        default: int | None = None,
    ) -> "FilterConfig":
        """
        创建数字筛选器配置

        Args:
            key: 筛选器键名
            title: 显示标题
            min_value: 最小值
            max_value: 最大值
            default: 默认值

        Returns:
            FilterConfig: 数字筛选器配置
        """
        return cls(
            key=key,
            title=title,
            filter_type="number",
            min_value=min_value,
            max_value=max_value,
            default=default,
        )

    @classmethod
    def create_text(
        cls,
        key: str,
        title: str,
        placeholder: str = "",
        default: str = "",
    ) -> "FilterConfig":
        """
        创建文本筛选器配置

        Args:
            key: 筛选器键名
            title: 显示标题
            placeholder: 占位符
            default: 默认值

        Returns:
            FilterConfig: 文本筛选器配置
        """
        return cls(
            key=key,
            title=title,
            filter_type="text",
            placeholder=placeholder or f"筛选{title}...",
            default=default,
        )

    @classmethod
    def create_checkbox(
        cls,
        key: str,
        title: str,
        checkbox_text: str = "",
        default: bool = False,
    ) -> "FilterConfig":
        """
        创建复选框筛选器配置

        Args:
            key: 筛选器键名
            title: 显示标题
            checkbox_text: 复选框文本
            default: 默认值

        Returns:
            FilterConfig: 复选框筛选器配置
        """
        return cls(
            key=key,
            title=title,
            filter_type="checkbox",
            checkbox_text=checkbox_text or title,
            default=default,
        )
