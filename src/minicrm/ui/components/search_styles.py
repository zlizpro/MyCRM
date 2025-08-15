"""
MiniCRM 搜索栏样式管理器

管理搜索栏组件的样式定义，支持主题切换和样式定制。
"""


class SearchBarStyles:
    """搜索栏样式管理器"""

    # 默认样式主题
    DEFAULT_THEME = {
        "primary_color": "#007bff",
        "border_color": "#ced4da",
        "hover_color": "#e9ecef",
        "background_color": "white",
        "advanced_bg": "#f8f9fa",
        "advanced_border": "#dee2e6",
    }

    @classmethod
    def get_search_bar_stylesheet(cls, theme: dict[str, str] | None = None) -> str:
        """
        获取搜索栏样式表

        Args:
            theme: 主题配置，如果为None则使用默认主题

        Returns:
            str: CSS样式表字符串
        """
        if theme is None:
            theme = cls.DEFAULT_THEME

        return f"""
            QLineEdit {{
                border: 1px solid {theme["border_color"]};
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: {theme["background_color"]};
            }}
            QLineEdit:focus {{
                border-color: {theme["primary_color"]};
            }}

            QPushButton {{
                border: 1px solid {theme["border_color"]};
                border-radius: 4px;
                background-color: {theme["background_color"]};
                font-size: 14px;
                min-width: 32px;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {theme["hover_color"]};
            }}
            QPushButton:checked {{
                background-color: {theme["primary_color"]};
                color: white;
                border-color: {theme["primary_color"]};
            }}

            QFrame#advancedFrame {{
                border: 1px solid {theme["advanced_border"]};
                border-radius: 6px;
                background-color: {theme["advanced_bg"]};
                padding: 10px;
            }}

            QLabel#advancedTitle {{
                font-weight: bold;
                font-size: 14px;
                color: #495057;
                margin-bottom: 8px;
            }}

            QComboBox, QDateEdit, QSpinBox, QLineEdit {{
                border: 1px solid {theme["border_color"]};
                border-radius: 4px;
                padding: 6px;
                background-color: {theme["background_color"]};
                min-height: 24px;
            }}

            QComboBox:focus, QDateEdit:focus, QSpinBox:focus {{
                border-color: {theme["primary_color"]};
            }}
        """

    @classmethod
    def get_dark_theme(cls) -> dict[str, str]:
        """获取深色主题配置"""
        return {
            "primary_color": "#0d6efd",
            "border_color": "#495057",
            "hover_color": "#343a40",
            "background_color": "#212529",
            "advanced_bg": "#343a40",
            "advanced_border": "#495057",
        }

    @classmethod
    def get_light_theme(cls) -> dict[str, str]:
        """获取浅色主题配置"""
        return cls.DEFAULT_THEME.copy()

    @classmethod
    def get_minicrm_theme(cls) -> dict[str, str]:
        """获取MiniCRM专用主题配置"""
        return {
            "primary_color": "#28a745",  # MiniCRM绿色
            "border_color": "#ced4da",
            "hover_color": "#e9ecef",
            "background_color": "white",
            "advanced_bg": "#f8f9fa",
            "advanced_border": "#dee2e6",
        }
