"""
MiniCRM 指标卡片组件

实现仪表盘中的指标卡片，提供：
- 现代化卡片设计
- 图标和数值显示
- 动画效果
- 点击交互
- 多种数据格式支持
"""

import logging
from decimal import Decimal
from typing import Any

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


# 导入transfunctions格式化函数
try:
    from transfunctions.formatting import (
        format_currency,
        format_number_with_unit,
        format_percentage,
    )

    _TRANSFUNCTIONS_AVAILABLE = True
except ImportError:
    _TRANSFUNCTIONS_AVAILABLE = False


class MetricCard(QFrame):
    """
    指标卡片组件

    显示单个业务指标，包括：
    - 图标显示
    - 标题和数值
    - 变化趋势（可选）
    - 点击交互
    - 悬停效果

    Signals:
        clicked: 卡片点击信号
        value_changed: 数值变化信号 (old_value, new_value)
    """

    # Qt信号定义
    clicked = Signal()
    value_changed = Signal(object, object)

    def __init__(
        self,
        title: str,
        config: dict[str, Any] | None = None,
        parent: QWidget | None = None,
    ):
        """
        初始化指标卡片

        Args:
            title: 卡片标题
            config: 配置字典，包含icon、color、value_format、suffix等
            parent: 父组件
        """
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)

        # 默认配置
        default_config = {
            "icon": "",
            "color": "#007bff",
            "value_format": "number",
            "suffix": "",
        }

        # 合并配置
        self._config = {**default_config, **(config or {})}

        # 卡片属性
        self._title = title
        self._icon = self._config["icon"]
        self._color = self._config["color"]
        self._value_format = self._config["value_format"]
        self._suffix = self._config["suffix"]

        # 当前数值
        self._current_value: Any = 0
        self._previous_value: Any = 0

        # UI组件
        self._icon_label: QLabel | None = None
        self._title_label: QLabel | None = None
        self._value_label: QLabel | None = None
        self._trend_label: QLabel | None = None

        # 动画
        self._hover_animation: QPropertyAnimation | None = None
        self._elevation = 2

        # 设置组件
        self._setup_ui()
        self._setup_animations()
        self._apply_styles()

        self._logger.debug(f"指标卡片初始化完成: {title}")

    def _setup_ui(self) -> None:
        """设置用户界面"""
        try:
            # 设置卡片属性
            self.setFixedSize(200, 120)
            self.setFrameStyle(QFrame.Shape.Box)
            self.setCursor(Qt.CursorShape.PointingHandCursor)

            # 主布局
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(15, 15, 15, 15)
            main_layout.setSpacing(8)

            # 顶部区域（图标和标题）
            top_layout = QHBoxLayout()
            top_layout.setSpacing(10)

            # 图标标签
            if self._icon:
                self._icon_label = QLabel(self._icon)
                self._icon_label.setObjectName("iconLabel")

                icon_font = QFont()
                icon_font.setPointSize(20)
                self._icon_label.setFont(icon_font)
                self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self._icon_label.setFixedSize(40, 40)

                top_layout.addWidget(self._icon_label)

            # 标题标签
            self._title_label = QLabel(self._title)
            self._title_label.setObjectName("titleLabel")
            self._title_label.setWordWrap(True)

            title_font = QFont()
            title_font.setPointSize(10)
            title_font.setBold(False)
            self._title_label.setFont(title_font)

            top_layout.addWidget(self._title_label, 1)
            main_layout.addLayout(top_layout)

            # 数值标签
            self._value_label = QLabel("0")
            self._value_label.setObjectName("valueLabel")
            self._value_label.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom
            )

            value_font = QFont()
            value_font.setPointSize(18)
            value_font.setBold(True)
            self._value_label.setFont(value_font)

            main_layout.addWidget(self._value_label)

            # 趋势标签（可选）
            self._trend_label = QLabel("")
            self._trend_label.setObjectName("trendLabel")
            self._trend_label.setAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
            )

            trend_font = QFont()
            trend_font.setPointSize(8)
            self._trend_label.setFont(trend_font)
            self._trend_label.hide()  # 默认隐藏

            main_layout.addWidget(self._trend_label)

            # 添加弹性空间
            main_layout.addStretch()

        except Exception as e:
            self._logger.error(f"指标卡片UI设置失败: {e}")
            raise

    def _setup_animations(self) -> None:
        """设置动画效果"""
        try:
            # 悬停动画
            self._hover_animation = QPropertyAnimation(self, b"elevation")
            self._hover_animation.setDuration(200)
            self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        except Exception as e:
            self._logger.error(f"动画设置失败: {e}")

    def _apply_styles(self) -> None:
        """应用样式"""
        try:
            # 设置样式表
            self.setStyleSheet(f"""
                MetricCard {{
                    background-color: white;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    padding: 0px;
                }}

                MetricCard:hover {{
                    border-color: {self._color};
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}

                QLabel#iconLabel {{
                    color: {self._color};
                    background-color: transparent;
                    border: none;
                }}

                QLabel#titleLabel {{
                    color: #6c757d;
                    background-color: transparent;
                    border: none;
                }}

                QLabel#valueLabel {{
                    color: #212529;
                    background-color: transparent;
                    border: none;
                }}

                QLabel#trendLabel {{
                    background-color: transparent;
                    border: none;
                }}
            """)

        except Exception as e:
            self._logger.error(f"样式应用失败: {e}")

    def set_value(self, value: Any, show_trend: bool = True) -> None:
        """
        设置卡片数值

        Args:
            value: 新数值
            show_trend: 是否显示趋势
        """
        try:
            # 保存旧值
            self._previous_value = self._current_value
            self._current_value = value

            # 格式化并显示数值
            formatted_value = self._format_value(value)
            self._value_label.setText(formatted_value)

            # 显示趋势（如果启用）
            if show_trend and self._previous_value != 0:
                self._update_trend()

            # 发送数值变化信号
            self.value_changed.emit(self._previous_value, self._current_value)

        except Exception as e:
            self._logger.error(f"设置数值失败: {e}")

    def _format_value(self, value: Any) -> str:
        """
        格式化数值显示 - 使用transfunctions标准格式化函数

        Args:
            value: 要格式化的数值

        Returns:
            str: 格式化后的字符串
        """
        try:
            if value is None:
                return "N/A"

            # 使用格式化器映射
            formatters = {
                "currency": self._format_currency_value,
                "percentage": self._format_percentage_value,
                "rating": self._format_rating_value,
                "number": self._format_number_value,
            }

            formatter = formatters.get(self._value_format, self._format_number_value)
            return formatter(value)

        except Exception as e:
            self._logger.error(f"数值格式化失败: {e}")
            return f"{value}{self._suffix}"

    def _format_currency_value(self, value: Any) -> str:
        """格式化货币值"""
        if _TRANSFUNCTIONS_AVAILABLE and isinstance(value, int | float | Decimal):
            formatted = format_currency(value)
            if value >= 10000:
                return f"{formatted[1:]}万{self._suffix}".replace(",", "")
            return f"{formatted}{self._suffix}"
        else:
            if isinstance(value, int | float | Decimal):
                if value >= 10000:
                    return f"¥{value / 10000:.1f}万{self._suffix}"
                else:
                    return f"¥{value:,.0f}{self._suffix}"
            return f"¥{value}{self._suffix}"

    def _format_percentage_value(self, value: Any) -> str:
        """格式化百分比值"""
        if _TRANSFUNCTIONS_AVAILABLE and isinstance(value, int | float):
            formatted = format_percentage(value / 100 if value > 1 else value)
            return f"{formatted}{self._suffix}"
        else:
            if isinstance(value, int | float):
                return f"{value:.1f}%{self._suffix}"
            return f"{value}%{self._suffix}"

    def _format_rating_value(self, value: Any) -> str:
        """格式化评分值"""
        if _TRANSFUNCTIONS_AVAILABLE:
            return format_number_with_unit(value, self._suffix, decimal_places=1)
        else:
            if isinstance(value, int | float):
                return f"{value:.1f}{self._suffix}"
            return f"{value}{self._suffix}"

    def _format_number_value(self, value: Any) -> str:
        """格式化数字值"""
        if _TRANSFUNCTIONS_AVAILABLE and isinstance(value, int | float):
            return format_number_with_unit(value, self._suffix, thousands_sep=True)
        else:
            if isinstance(value, int | float):
                if value >= 10000:
                    return f"{value:,.0f}{self._suffix}"
                else:
                    return f"{value}{self._suffix}"
            return f"{value}{self._suffix}"

    def _update_trend(self) -> None:
        """更新趋势显示"""
        try:
            if not isinstance(self._current_value, int | float) or not isinstance(
                self._previous_value, int | float
            ):
                return

            # 计算变化
            if self._previous_value == 0:
                return

            change = self._current_value - self._previous_value
            change_percent = (change / self._previous_value) * 100

            # 设置趋势文本和颜色
            if change > 0:
                trend_text = f"↗ +{abs(change_percent):.1f}%"
                trend_color = "#28a745"  # 绿色
            elif change < 0:
                trend_text = f"↘ -{abs(change_percent):.1f}%"
                trend_color = "#dc3545"  # 红色
            else:
                trend_text = "→ 0.0%"
                trend_color = "#6c757d"  # 灰色

            # 更新趋势标签
            self._trend_label.setText(trend_text)
            self._trend_label.setStyleSheet(f"color: {trend_color};")
            self._trend_label.show()

        except Exception as e:
            self._logger.error(f"趋势更新失败: {e}")

    def set_color(self, color: str) -> None:
        """
        设置卡片主题颜色

        Args:
            color: 颜色值（十六进制）
        """
        self._color = color
        self._apply_styles()

    def set_title(self, title: str) -> None:
        """
        设置卡片标题

        Args:
            title: 新标题
        """
        self._title = title
        if self._title_label:
            self._title_label.setText(title)

    def set_icon(self, icon: str) -> None:
        """
        设置卡片图标

        Args:
            icon: 新图标
        """
        self._icon = icon
        if self._icon_label:
            self._icon_label.setText(icon)

    def get_value(self) -> Any:
        """获取当前数值"""
        return self._current_value

    def get_previous_value(self) -> Any:
        """获取前一个数值"""
        return self._previous_value

    def reset_trend(self) -> None:
        """重置趋势显示"""
        if self._trend_label:
            self._trend_label.hide()
        self._previous_value = self._current_value

    # Qt属性（用于动画）
    @property
    def elevation(self) -> int:
        """获取阴影高度"""
        return self._elevation

    @elevation.setter
    def elevation(self, value: int) -> None:
        """设置阴影高度"""
        self._elevation = value
        self.update()

    # Qt事件处理
    def mousePressEvent(self, event) -> None:  # noqa: N802
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event) -> None:  # noqa: N802
        """鼠标进入事件"""
        if self._hover_animation:
            self._hover_animation.setStartValue(self._elevation)
            self._hover_animation.setEndValue(6)
            self._hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        """鼠标离开事件"""
        if self._hover_animation:
            self._hover_animation.setStartValue(self._elevation)
            self._hover_animation.setEndValue(2)
            self._hover_animation.start()
        super().leaveEvent(event)

    def paintEvent(self, event) -> None:  # noqa: N802
        """绘制事件（用于阴影效果）"""
        super().paintEvent(event)

        # 绘制阴影效果
        if self._elevation > 2:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 设置阴影颜色和透明度
            shadow_color = QColor(0, 0, 0, 20)
            painter.setPen(QPen(shadow_color, self._elevation))

            # 绘制阴影矩形
            rect = self.rect().adjusted(2, 2, -2, -2)
            painter.drawRoundedRect(rect, 8, 8)

    def __str__(self) -> str:
        """返回卡片的字符串表示"""
        return f"MetricCard(title='{self._title}', value={self._current_value})"
