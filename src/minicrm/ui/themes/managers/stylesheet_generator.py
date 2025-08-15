"""
MiniCRM 样式表生成器

负责根据主题配置生成CSS样式表
"""

import logging
from typing import Any


class StylesheetGenerator:
    """
    样式表生成器

    负责根据主题配置生成完整的Qt样式表(QSS)。
    支持多种UI组件的样式定制，包括按钮、输入框、表格、菜单等。

    主要功能：
    - 基于主题配置生成CSS样式
    - 支持颜色、字体、间距、圆角等样式属性
    - 模块化生成各种UI组件样式
    - 提供统一的样式管理接口
    """

    def __init__(self):
        """初始化样式表生成器"""
        self._logger = logging.getLogger(__name__)

    def generate_stylesheet(self, theme_config: dict[str, Any]) -> str:
        """
        生成主题样式表

        Args:
            theme_config: 主题配置

        Returns:
            str: CSS样式表
        """
        try:
            colors = theme_config.get("colors", {})
            fonts = theme_config.get("fonts", {})
            spacing = theme_config.get("spacing", {})
            border_radius = theme_config.get("border_radius", {})

            # 生成各个组件的样式
            styles = []

            # CSS变量定义（基于设计令牌）
            styles.append(self._generate_css_variables(theme_config))

            # 基础样式
            styles.append(self._generate_base_styles(colors, fonts))

            # 按钮样式
            styles.append(
                self._generate_button_styles(colors, fonts, spacing, border_radius)
            )

            # 输入框样式
            styles.append(
                self._generate_input_styles(colors, fonts, spacing, border_radius)
            )

            # 表格样式
            styles.append(self._generate_table_styles(colors, fonts, spacing))

            # 菜单样式
            styles.append(
                self._generate_menu_styles(colors, fonts, spacing, border_radius)
            )

            # 对话框样式
            styles.append(
                self._generate_dialog_styles(colors, fonts, spacing, border_radius)
            )

            # 工具栏样式
            styles.append(self._generate_toolbar_styles(colors, fonts, spacing))

            # 滚动条样式
            styles.append(self._generate_scrollbar_styles(colors))

            # 状态样式
            styles.append(self._generate_state_styles(colors))

            return "\n\n".join(styles)

        except Exception as e:
            self._logger.error(f"生成样式表失败: {e}")
            return ""

    def _get_color_with_fallback(self, colors: dict, key: str, fallback: str) -> str:
        """获取颜色值，提供默认值作为后备"""
        return colors.get(key, fallback)

    def _get_font_with_fallback(self, fonts: dict, key: str, fallback: str) -> str:
        """获取字体值，提供默认值作为后备"""
        return fonts.get(key, fallback)

    def _get_spacing_with_fallback(self, spacing: dict, key: str, fallback: str) -> str:
        """获取间距值，提供默认值作为后备"""
        return spacing.get(key, fallback)

    def _generate_base_styles(self, colors: dict, fonts: dict) -> str:
        """
        生成基础样式

        为所有Qt组件设置基础的背景色、文字颜色、字体等属性。
        这些样式会被所有组件继承，确保整体风格统一。
        """
        return f"""
/* 基础样式 */
QWidget {{
    background-color: {self._get_color_with_fallback(colors, "background", "#FFFFFF")};
    color: {self._get_color_with_fallback(colors, "text_primary", "#212529")};
    font-family: {self._get_font_with_fallback(fonts, "family", "Microsoft YaHei UI")};
    font-size: {self._get_font_with_fallback(fonts, "size_normal", "14px")};
    font-weight: {self._get_font_with_fallback(fonts, "weight_normal", "400")};
}}

QMainWindow {{
    background-color: {self._get_color_with_fallback(colors, "background", "#FFFFFF")};
}}

QFrame {{
    background-color: {self._get_color_with_fallback(colors, "surface", "#F8F9FA")};
    border: 1px solid {self._get_color_with_fallback(colors, "border", "#DEE2E6")};
}}
"""

    def _generate_button_styles(
        self, colors: dict, fonts: dict, spacing: dict, border_radius: dict
    ) -> str:
        """生成按钮样式"""
        return f"""
/* 按钮样式 */
QPushButton {{
    background-color: {colors.get("primary", "#007BFF")};
    color: white;
    border: none;
    padding: {spacing.get("sm", "8px")} {spacing.get("md", "16px")};
    border-radius: {border_radius.get("medium", "6px")};
    font-weight: {fonts.get("weight_bold", "600")};
    min-height: 32px;
}}

QPushButton:hover {{
    background-color: {colors.get("primary", "#007BFF")};
    opacity: 0.9;
}}

QPushButton:pressed {{
    background-color: {colors.get("primary", "#007BFF")};
    opacity: 0.8;
}}

QPushButton:disabled {{
    background-color: {colors.get("disabled", "#E9ECEF")};
    color: {colors.get("text_muted", "#ADB5BD")};
}}

QPushButton[class="secondary"] {{
    background-color: {colors.get("secondary", "#6C757D")};
}}

QPushButton[class="success"] {{
    background-color: {colors.get("success", "#28A745")};
}}

QPushButton[class="warning"] {{
    background-color: {colors.get("warning", "#FFC107")};
    color: {colors.get("text_primary", "#212529")};
}}

QPushButton[class="danger"] {{
    background-color: {colors.get("danger", "#DC3545")};
}}
"""

    def _generate_input_styles(
        self, colors: dict, fonts: dict, spacing: dict, border_radius: dict
    ) -> str:
        """生成输入框样式"""
        return f"""
/* 输入框样式 */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {colors.get("card", "#FFFFFF")};
    border: 1px solid {colors.get("border", "#DEE2E6")};
    border-radius: {border_radius.get("small", "4px")};
    padding: {spacing.get("sm", "8px")};
    font-size: {fonts.get("size_normal", "14px")};
    min-height: 32px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {colors.get("focus", "#80BDFF")};
    outline: none;
}}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
    background-color: {colors.get("disabled", "#E9ECEF")};
    color: {colors.get("text_muted", "#ADB5BD")};
}}

QComboBox {{
    background-color: {colors.get("card", "#FFFFFF")};
    border: 1px solid {colors.get("border", "#DEE2E6")};
    border-radius: {border_radius.get("small", "4px")};
    padding: {spacing.get("sm", "8px")};
    min-height: 32px;
}}

QComboBox:focus {{
    border-color: {colors.get("focus", "#80BDFF")};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox::down-arrow {{
    image: url(:/icons/arrow-down.png);
    width: 12px;
    height: 12px;
}}

QSpinBox, QDoubleSpinBox {{
    background-color: {colors.get("card", "#FFFFFF")};
    border: 1px solid {colors.get("border", "#DEE2E6")};
    border-radius: {border_radius.get("small", "4px")};
    padding: {spacing.get("sm", "8px")};
    min-height: 32px;
}}

QDateEdit, QTimeEdit, QDateTimeEdit {{
    background-color: {colors.get("card", "#FFFFFF")};
    border: 1px solid {colors.get("border", "#DEE2E6")};
    border-radius: {border_radius.get("small", "4px")};
    padding: {spacing.get("sm", "8px")};
    min-height: 32px;
}}
"""

    def _generate_table_styles(self, colors: dict, fonts: dict, spacing: dict) -> str:
        """生成表格样式"""
        return f"""
/* 表格样式 */
QTableWidget {{
    background-color: {colors.get("card", "#FFFFFF")};
    border: 1px solid {colors.get("border", "#DEE2E6")};
    gridline-color: {colors.get("border_light", "#E9ECEF")};
    selection-background-color: {colors.get("primary", "#007BFF")};
    selection-color: white;
}}

QTableWidget::item {{
    padding: {spacing.get("sm", "8px")};
    border-bottom: 1px solid {colors.get("border_light", "#E9ECEF")};
}}

QTableWidget::item:selected {{
    background-color: {colors.get("primary", "#007BFF")};
    color: white;
}}

QTableWidget::item:hover {{
    background-color: {colors.get("hover", "#F8F9FA")};
}}

QHeaderView::section {{
    background-color: {colors.get("surface", "#F8F9FA")};
    border: 1px solid {colors.get("border", "#DEE2E6")};
    padding: {spacing.get("sm", "8px")};
    font-weight: {fonts.get("weight_bold", "600")};
}}

QHeaderView::section:hover {{
    background-color: {colors.get("hover", "#F8F9FA")};
}}
"""

    def _generate_menu_styles(
        self, colors: dict, fonts: dict, spacing: dict, border_radius: dict
    ) -> str:
        """生成菜单样式"""
        return f"""
/* 菜单样式 */
QMenuBar {{
    background-color: {colors.get("surface", "#F8F9FA")};
    border-bottom: 1px solid {colors.get("border", "#DEE2E6")};
    padding: {spacing.get("xs", "4px")};
}}

QMenuBar::item {{
    background-color: transparent;
    padding: {spacing.get("sm", "8px")} {spacing.get("md", "16px")};
    border-radius: {border_radius.get("small", "4px")};
}}

QMenuBar::item:selected {{
    background-color: {colors.get("hover", "#F8F9FA")};
}}

QMenu {{
    background-color: {colors.get("card", "#FFFFFF")};
    border: 1px solid {colors.get("border", "#DEE2E6")};
    border-radius: {border_radius.get("medium", "6px")};
    padding: {spacing.get("xs", "4px")};
}}

QMenu::item {{
    padding: {spacing.get("sm", "8px")} {spacing.get("md", "16px")};
    border-radius: {border_radius.get("small", "4px")};
}}

QMenu::item:selected {{
    background-color: {colors.get("primary", "#007BFF")};
    color: white;
}}

QMenu::separator {{
    height: 1px;
    background-color: {colors.get("border_light", "#E9ECEF")};
    margin: {spacing.get("xs", "4px")} 0;
}}
"""

    def _generate_dialog_styles(
        self, colors: dict, fonts: dict, spacing: dict, border_radius: dict
    ) -> str:
        """生成对话框样式"""
        return f"""
/* 对话框样式 */
QDialog {{
    background-color: {colors.get("card", "#FFFFFF")};
    border: 1px solid {colors.get("border", "#DEE2E6")};
    border-radius: {border_radius.get("large", "8px")};
}}

QMessageBox {{
    background-color: {colors.get("card", "#FFFFFF")};
}}

QGroupBox {{
    font-weight: {fonts.get("weight_bold", "600")};
    border: 2px solid {colors.get("border", "#DEE2E6")};
    border-radius: {border_radius.get("medium", "6px")};
    margin-top: {spacing.get("md", "16px")};
    padding-top: {spacing.get("md", "16px")};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: {spacing.get("md", "16px")};
    padding: 0 {spacing.get("sm", "8px")} 0 {spacing.get("sm", "8px")};
}}
"""

    def _generate_toolbar_styles(self, colors: dict, fonts: dict, spacing: dict) -> str:
        """生成工具栏样式"""
        return f"""
/* 工具栏样式 */
QToolBar {{
    background-color: {colors.get("surface", "#F8F9FA")};
    border: 1px solid {colors.get("border", "#DEE2E6")};
    padding: {spacing.get("xs", "4px")};
    spacing: {spacing.get("xs", "4px")};
}}

QToolButton {{
    background-color: transparent;
    border: none;
    padding: {spacing.get("sm", "8px")};
    border-radius: {spacing.get("xs", "4px")};
    min-width: 32px;
    min-height: 32px;
}}

QToolButton:hover {{
    background-color: {colors.get("hover", "#F8F9FA")};
}}

QToolButton:pressed {{
    background-color: {colors.get("active", "#E9ECEF")};
}}

QStatusBar {{
    background-color: {colors.get("surface", "#F8F9FA")};
    border-top: 1px solid {colors.get("border", "#DEE2E6")};
    padding: {spacing.get("xs", "4px")};
}}
"""

    def _generate_css_variables(self, theme_config: dict) -> str:
        """生成CSS变量定义"""
        try:
            from ..design_tokens import design_tokens

            return f"""
/* CSS变量定义 - 基于设计令牌 */
{design_tokens.to_css_variables()}
"""
        except ImportError:
            # 如果设计令牌不可用，生成基础变量
            colors = theme_config.get("colors", {})
            fonts = theme_config.get("fonts", {})
            spacing = theme_config.get("spacing", {})

            return f"""
/* CSS变量定义 - 基础版本 */
:root {{
    /* 颜色变量 */
    --color-primary: {colors.get("primary", "#007BFF")};
    --color-secondary: {colors.get("secondary", "#6C757D")};
    --color-success: {colors.get("success", "#28A745")};
    --color-warning: {colors.get("warning", "#FFC107")};
    --color-danger: {colors.get("danger", "#DC3545")};
    --color-background: {colors.get("background", "#FFFFFF")};
    --color-surface: {colors.get("surface", "#F8F9FA")};
    --color-text-primary: {colors.get("text_primary", "#212529")};
    --color-text-secondary: {colors.get("text_secondary", "#6C757D")};
    --color-border: {colors.get("border", "#DEE2E6")};

    /* 字体变量 */
    --font-family: {fonts.get("family", "Microsoft YaHei UI, Arial, sans-serif")};
    --font-size-normal: {fonts.get("size_normal", "14px")};
    --font-size-small: {fonts.get("size_small", "12px")};
    --font-size-large: {fonts.get("size_large", "16px")};

    /* 间距变量 */
    --spacing-xs: {spacing.get("xs", "4px")};
    --spacing-sm: {spacing.get("sm", "8px")};
    --spacing-md: {spacing.get("md", "16px")};
    --spacing-lg: {spacing.get("lg", "24px")};
}}
"""

    def _generate_scrollbar_styles(self, colors: dict) -> str:
        """生成滚动条样式"""
        return f"""
/* 滚动条样式 */
QScrollBar:vertical {{
    background-color: {colors.get("surface", "#F8F9FA")};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {colors.get("border", "#DEE2E6")};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {colors.get("border_dark", "#CED4DA")};
}}

QScrollBar::handle:vertical:pressed {{
    background-color: {colors.get("secondary", "#6C757D")};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    border: none;
    background: none;
}}

QScrollBar:horizontal {{
    background-color: {colors.get("surface", "#F8F9FA")};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {colors.get("border", "#DEE2E6")};
    border-radius: 6px;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {colors.get("border_dark", "#CED4DA")};
}}

QScrollBar::handle:horizontal:pressed {{
    background-color: {colors.get("secondary", "#6C757D")};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    border: none;
    background: none;
}}
"""

    def _generate_state_styles(self, colors: dict) -> str:
        """生成状态样式"""
        return f"""
/* 状态样式 */
.loading {{
    opacity: 0.6;
    pointer-events: none;
}}

.disabled {{
    opacity: 0.5;
    pointer-events: none;
}}

.error {{
    border-color: {colors.get("danger", "#DC3545")} !important;
    background-color: rgba(220, 53, 69, 0.1);
}}

.success {{
    border-color: {colors.get("success", "#28A745")} !important;
    background-color: rgba(40, 167, 69, 0.1);
}}

.warning {{
    border-color: {colors.get("warning", "#FFC107")} !important;
    background-color: rgba(255, 193, 7, 0.1);
}}

.info {{
    border-color: {colors.get("info", "#17A2B8")} !important;
    background-color: rgba(23, 162, 184, 0.1);
}}

/* 焦点样式 */
*:focus {{
    outline: 2px solid {colors.get("focus", "#80BDFF")};
    outline-offset: 2px;
}}

/* 选中样式 */
::selection {{
    background-color: {colors.get("primary", "#007BFF")};
    color: white;
}}
"""
