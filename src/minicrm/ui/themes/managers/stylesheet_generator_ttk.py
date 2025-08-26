"""TTK样式表生成器

为TTK组件生成主题样式配置.
"""

import logging
from typing import Any, Dict


logger = logging.getLogger(__name__)


class TTKStylesheetGenerator:
    """TTK样式表生成器"""

    def __init__(self):
        """初始化样式表生成器"""
        self._logger = logger

    def generate_theme_styles(self, theme_config: Dict[str, Any]) -> Dict[str, Any]:
        """生成完整的TTK主题样式配置

        Args:
            theme_config: 主题配置字典

        Returns:
            Dict[str, Any]: TTK样式配置字典
        """
        try:
            colors = theme_config.get("colors", {})
            fonts = theme_config.get("fonts", {})
            spacing = theme_config.get("spacing", {})
            border_radius = theme_config.get("border_radius", {})

            # 合并所有样式配置
            styles = {}
            styles.update(self._generate_base_styles(colors, fonts))
            styles.update(self._generate_button_styles(colors, fonts, spacing))
            styles.update(self._generate_entry_styles(colors, fonts, spacing))
            styles.update(self._generate_frame_styles(colors, spacing))
            styles.update(self._generate_label_styles(colors, fonts))
            styles.update(self._generate_treeview_styles(colors, fonts))
            styles.update(self._generate_notebook_styles(colors, fonts))
            styles.update(self._generate_combobox_styles(colors, fonts))
            styles.update(self._generate_scrollbar_styles(colors))

            return styles

        except Exception as e:
            self._logger.error(f"生成主题样式失败: {e}")
            return self._get_default_styles()

    def _generate_base_styles(self, colors: Dict, fonts: Dict) -> Dict[str, Any]:
        """生成基础样式"""
        return {
            "TFrame": {
                "configure": {
                    "background": self._get_color_with_fallback(
                        colors, "background", "#FFFFFF"
                    ),
                    "relief": "flat",
                    "borderwidth": 0,
                }
            },
            "Card.TFrame": {
                "configure": {
                    "background": self._get_color_with_fallback(
                        colors, "surface", "#F8F9FA"
                    ),
                    "relief": "raised",
                    "borderwidth": 1,
                }
            },
        }

    def _generate_button_styles(
        self, colors: Dict, fonts: Dict, spacing: Dict
    ) -> Dict[str, Any]:
        """生成按钮样式"""
        return {
            "TButton": {
                "configure": {
                    "background": colors.get("primary", "#007BFF"),
                    "foreground": "white",
                    "borderwidth": 0,
                    "focuscolor": colors.get("primary", "#007BFF"),
                    "font": (
                        fonts.get("family", "Microsoft YaHei UI"),
                        int(str(fonts.get("size_normal", "14")).replace("px", "")),
                        "normal",
                    ),
                    "padding": (
                        int(str(spacing.get("md", "16")).replace("px", "")),
                        int(str(spacing.get("sm", "8")).replace("px", "")),
                    ),
                },
                "map": {
                    "background": [
                        ("active", colors.get("primary_hover", "#0056B3")),
                        ("pressed", colors.get("primary_active", "#004085")),
                        ("disabled", colors.get("disabled", "#E9ECEF")),
                    ],
                    "foreground": [("disabled", colors.get("text_muted", "#ADB5BD"))],
                },
            },
            "Secondary.TButton": {
                "configure": {
                    "background": colors.get("secondary", "#6C757D"),
                    "foreground": "white",
                },
                "map": {
                    "background": [
                        ("active", colors.get("secondary_hover", "#545B62")),
                        ("pressed", colors.get("secondary_active", "#3D4142")),
                    ]
                },
            },
            "Success.TButton": {
                "configure": {
                    "background": colors.get("success", "#28A745"),
                    "foreground": "white",
                },
                "map": {
                    "background": [
                        ("active", colors.get("success_hover", "#218838")),
                        ("pressed", colors.get("success_active", "#1E7E34")),
                    ]
                },
            },
            "Warning.TButton": {
                "configure": {
                    "background": colors.get("warning", "#FFC107"),
                    "foreground": colors.get("text_primary", "#212529"),
                },
                "map": {
                    "background": [
                        ("active", colors.get("warning_hover", "#E0A800")),
                        ("pressed", colors.get("warning_active", "#D39E00")),
                    ]
                },
            },
            "Danger.TButton": {
                "configure": {
                    "background": colors.get("danger", "#DC3545"),
                    "foreground": "white",
                },
                "map": {
                    "background": [
                        ("active", colors.get("danger_hover", "#C82333")),
                        ("pressed", colors.get("danger_active", "#BD2130")),
                    ]
                },
            },
        }

    def _generate_entry_styles(
        self, colors: Dict, fonts: Dict, spacing: Dict
    ) -> Dict[str, Any]:
        """生成输入框样式"""
        return {
            "TEntry": {
                "configure": {
                    "fieldbackground": self._get_color_with_fallback(
                        colors, "surface", "#FFFFFF"
                    ),
                    "bordercolor": self._get_color_with_fallback(
                        colors, "border", "#DEE2E6"
                    ),
                    "lightcolor": self._get_color_with_fallback(
                        colors, "border_light", "#E9ECEF"
                    ),
                    "darkcolor": self._get_color_with_fallback(
                        colors, "border_dark", "#ADB5BD"
                    ),
                    "insertcolor": self._get_color_with_fallback(
                        colors, "text_primary", "#212529"
                    ),
                    "font": (
                        fonts.get("family", "Microsoft YaHei UI"),
                        int(str(fonts.get("size_normal", "14")).replace("px", "")),
                    ),
                    "padding": (
                        int(str(spacing.get("sm", "8")).replace("px", "")),
                        int(str(spacing.get("xs", "4")).replace("px", "")),
                    ),
                },
                "map": {
                    "bordercolor": [
                        ("focus", colors.get("primary", "#007BFF")),
                        ("invalid", colors.get("danger", "#DC3545")),
                    ],
                    "lightcolor": [
                        ("focus", colors.get("primary", "#007BFF")),
                        ("invalid", colors.get("danger", "#DC3545")),
                    ],
                    "darkcolor": [
                        ("focus", colors.get("primary", "#007BFF")),
                        ("invalid", colors.get("danger", "#DC3545")),
                    ],
                },
            }
        }

    def _generate_frame_styles(self, colors: Dict, spacing: Dict) -> Dict[str, Any]:
        """生成框架样式"""
        return {
            "TFrame": {
                "configure": {
                    "background": self._get_color_with_fallback(
                        colors, "background", "#FFFFFF"
                    ),
                    "relief": "flat",
                }
            },
            "Card.TFrame": {
                "configure": {
                    "background": self._get_color_with_fallback(
                        colors, "surface", "#F8F9FA"
                    ),
                    "relief": "raised",
                    "borderwidth": 1,
                }
            },
            "Toolbar.TFrame": {
                "configure": {
                    "background": self._get_color_with_fallback(
                        colors, "surface", "#F8F9FA"
                    ),
                    "relief": "flat",
                    "borderwidth": 0,
                }
            },
        }

    def _generate_label_styles(self, colors: Dict, fonts: Dict) -> Dict[str, Any]:
        """生成标签样式"""
        return {
            "TLabel": {
                "configure": {
                    "background": self._get_color_with_fallback(
                        colors, "background", "#FFFFFF"
                    ),
                    "foreground": self._get_color_with_fallback(
                        colors, "text_primary", "#212529"
                    ),
                    "font": (
                        fonts.get("family", "Microsoft YaHei UI"),
                        int(str(fonts.get("size_normal", "14")).replace("px", "")),
                    ),
                }
            },
            "Title.TLabel": {
                "configure": {
                    "font": (
                        fonts.get("family", "Microsoft YaHei UI"),
                        int(str(fonts.get("size_large", "18")).replace("px", "")),
                        "bold",
                    )
                }
            },
            "Subtitle.TLabel": {
                "configure": {
                    "font": (
                        fonts.get("family", "Microsoft YaHei UI"),
                        int(str(fonts.get("size_medium", "16")).replace("px", "")),
                        "bold",
                    )
                }
            },
            "Muted.TLabel": {
                "configure": {
                    "foreground": self._get_color_with_fallback(
                        colors, "text_muted", "#6C757D"
                    )
                }
            },
        }

    def _generate_treeview_styles(self, colors: Dict, fonts: Dict) -> Dict[str, Any]:
        """生成树形视图样式"""
        return {
            "Treeview": {
                "configure": {
                    "background": self._get_color_with_fallback(
                        colors, "surface", "#FFFFFF"
                    ),
                    "foreground": self._get_color_with_fallback(
                        colors, "text_primary", "#212529"
                    ),
                    "fieldbackground": self._get_color_with_fallback(
                        colors, "surface", "#FFFFFF"
                    ),
                    "bordercolor": self._get_color_with_fallback(
                        colors, "border", "#DEE2E6"
                    ),
                    "lightcolor": self._get_color_with_fallback(
                        colors, "border_light", "#E9ECEF"
                    ),
                    "darkcolor": self._get_color_with_fallback(
                        colors, "border_dark", "#ADB5BD"
                    ),
                    "font": (
                        fonts.get("family", "Microsoft YaHei UI"),
                        int(str(fonts.get("size_normal", "14")).replace("px", "")),
                    ),
                },
                "map": {
                    "background": [("selected", colors.get("primary", "#007BFF"))],
                    "foreground": [("selected", "white")],
                },
            },
            "Treeview.Heading": {
                "configure": {
                    "background": self._get_color_with_fallback(
                        colors, "surface", "#F8F9FA"
                    ),
                    "foreground": self._get_color_with_fallback(
                        colors, "text_primary", "#212529"
                    ),
                    "font": (
                        fonts.get("family", "Microsoft YaHei UI"),
                        int(str(fonts.get("size_normal", "14")).replace("px", "")),
                        "bold",
                    ),
                }
            },
        }

    def _generate_notebook_styles(self, colors: Dict, fonts: Dict) -> Dict[str, Any]:
        """生成笔记本标签页样式"""
        return {
            "TNotebook": {
                "configure": {
                    "background": self._get_color_with_fallback(
                        colors, "background", "#FFFFFF"
                    ),
                    "bordercolor": self._get_color_with_fallback(
                        colors, "border", "#DEE2E6"
                    ),
                }
            },
            "TNotebook.Tab": {
                "configure": {
                    "background": self._get_color_with_fallback(
                        colors, "surface", "#F8F9FA"
                    ),
                    "foreground": self._get_color_with_fallback(
                        colors, "text_primary", "#212529"
                    ),
                    "font": (
                        fonts.get("family", "Microsoft YaHei UI"),
                        int(str(fonts.get("size_normal", "14")).replace("px", "")),
                    ),
                    "padding": (12, 8),
                },
                "map": {
                    "background": [
                        ("selected", colors.get("primary", "#007BFF")),
                        ("active", colors.get("primary_hover", "#0056B3")),
                    ],
                    "foreground": [("selected", "white"), ("active", "white")],
                },
            },
        }

    def _generate_combobox_styles(self, colors: Dict, fonts: Dict) -> Dict[str, Any]:
        """生成下拉框样式"""
        return {
            "TCombobox": {
                "configure": {
                    "fieldbackground": self._get_color_with_fallback(
                        colors, "surface", "#FFFFFF"
                    ),
                    "bordercolor": self._get_color_with_fallback(
                        colors, "border", "#DEE2E6"
                    ),
                    "arrowcolor": self._get_color_with_fallback(
                        colors, "text_primary", "#212529"
                    ),
                    "font": (
                        fonts.get("family", "Microsoft YaHei UI"),
                        int(str(fonts.get("size_normal", "14")).replace("px", "")),
                    ),
                },
                "map": {"bordercolor": [("focus", colors.get("primary", "#007BFF"))]},
            }
        }

    def _generate_scrollbar_styles(self, colors: Dict) -> Dict[str, Any]:
        """生成滚动条样式"""
        return {
            "Vertical.TScrollbar": {
                "configure": {
                    "background": self._get_color_with_fallback(
                        colors, "surface", "#F8F9FA"
                    ),
                    "troughcolor": self._get_color_with_fallback(
                        colors, "background", "#FFFFFF"
                    ),
                    "bordercolor": self._get_color_with_fallback(
                        colors, "border", "#DEE2E6"
                    ),
                    "arrowcolor": self._get_color_with_fallback(
                        colors, "text_muted", "#6C757D"
                    ),
                    "darkcolor": self._get_color_with_fallback(
                        colors, "border_dark", "#ADB5BD"
                    ),
                    "lightcolor": self._get_color_with_fallback(
                        colors, "border_light", "#E9ECEF"
                    ),
                }
            },
            "Horizontal.TScrollbar": {
                "configure": {
                    "background": self._get_color_with_fallback(
                        colors, "surface", "#F8F9FA"
                    ),
                    "troughcolor": self._get_color_with_fallback(
                        colors, "background", "#FFFFFF"
                    ),
                    "bordercolor": self._get_color_with_fallback(
                        colors, "border", "#DEE2E6"
                    ),
                    "arrowcolor": self._get_color_with_fallback(
                        colors, "text_muted", "#6C757D"
                    ),
                    "darkcolor": self._get_color_with_fallback(
                        colors, "border_dark", "#ADB5BD"
                    ),
                    "lightcolor": self._get_color_with_fallback(
                        colors, "border_light", "#E9ECEF"
                    ),
                }
            },
        }

    def _get_color_with_fallback(self, colors: Dict, key: str, fallback: str) -> str:
        """获取颜色值,如果不存在则使用回退值"""
        return colors.get(key, fallback)

    def _get_font_with_fallback(self, fonts: Dict, key: str, fallback: str) -> str:
        """获取字体值,如果不存在则使用回退值"""
        return fonts.get(key, fallback)

    def _get_default_styles(self) -> Dict[str, Any]:
        """获取默认样式配置"""
        return {
            "TFrame": {"configure": {"background": "#FFFFFF", "relief": "flat"}},
            "TLabel": {
                "configure": {
                    "background": "#FFFFFF",
                    "foreground": "#212529",
                    "font": ("Microsoft YaHei UI", 14),
                }
            },
            "TButton": {
                "configure": {
                    "background": "#007BFF",
                    "foreground": "white",
                    "font": ("Microsoft YaHei UI", 14),
                }
            },
            "TEntry": {
                "configure": {
                    "fieldbackground": "#FFFFFF",
                    "bordercolor": "#DEE2E6",
                    "font": ("Microsoft YaHei UI", 14),
                }
            },
        }

    def apply_styles_to_ttk(self, style_obj, styles: Dict[str, Any]) -> None:
        """将样式配置应用到TTK Style对象

        Args:
            style_obj: TTK Style对象
            styles: 样式配置字典
        """
        try:
            for style_name, style_config in styles.items():
                if "configure" in style_config:
                    style_obj.configure(style_name, **style_config["configure"])

                if "map" in style_config:
                    for option, state_values in style_config["map"].items():
                        style_obj.map(style_name, **{option: state_values})

        except Exception as e:
            self._logger.error(f"应用TTK样式失败: {e}")
