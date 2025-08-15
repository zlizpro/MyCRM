"""
MiniCRM 主题定义

定义所有可用的主题配置
"""

from typing import Any


def get_theme_definitions() -> dict[str, dict[str, Any]]:
    """
    获取主题定义

    定义了MiniCRM支持的所有内置主题，包括浅色、深色和蓝色主题。
    每个主题包含完整的颜色、字体、间距和圆角配置。
    """
    return {
        "light": {
            "name": "浅色主题",
            "description": "明亮清新的浅色主题，适合日间使用",
            "colors": {
                # 主要颜色 - 品牌色和功能色
                "primary": "#007BFF",  # 主品牌色（蓝色）
                "primary_light": "#66B2FF",  # 浅色主品牌色
                "primary_dark": "#0056B3",  # 深色主品牌色
                "secondary": "#6C757D",  # 次要颜色（灰色）
                "success": "#28A745",  # 成功色（绿色）
                "warning": "#FFC107",  # 警告色（黄色）
                "danger": "#DC3545",  # 危险色（红色）
                "info": "#17A2B8",  # 信息色（青色）
                # 背景颜色 - 不同层级的背景
                "background": "#FFFFFF",  # 主背景色
                "surface": "#F8F9FA",  # 表面背景色
                "surface_variant": "#F1F3F4",  # 表面变体色
                "card": "#FFFFFF",  # 卡片背景色
                "overlay": "rgba(0, 0, 0, 0.5)",  # 遮罩层颜色
                # 文本颜色 - 不同重要性的文本
                "text_primary": "#212529",  # 主要文本色
                "text_secondary": "#6C757D",  # 次要文本色
                "text_muted": "#ADB5BD",  # 弱化文本色
                "text_disabled": "#CED4DA",  # 禁用文本色
                "text_on_primary": "#FFFFFF",  # 主色上的文本
                "text_on_dark": "#FFFFFF",  # 深色背景上的文本
                # 边框颜色 - 不同强度的边框
                "border": "#DEE2E6",  # 标准边框色
                "border_light": "#E9ECEF",  # 浅色边框
                "border_dark": "#CED4DA",  # 深色边框
                "border_focus": "#80BDFF",  # 焦点边框色
                # 状态颜色 - 交互状态
                "hover": "#F8F9FA",  # 悬停背景色
                "active": "#E9ECEF",  # 激活背景色
                "focus": "#80BDFF",  # 焦点色
                "selected": "#E3F2FD",  # 选中背景色
                "disabled": "#E9ECEF",  # 禁用背景色
                # 阴影颜色
                "shadow_light": "rgba(0, 0, 0, 0.1)",
                "shadow_medium": "rgba(0, 0, 0, 0.15)",
                "shadow_dark": "rgba(0, 0, 0, 0.2)",
            },
            "fonts": {
                "family": "Microsoft YaHei UI, 'Segoe UI', Arial, sans-serif",
                "family_monospace": "'Consolas', 'Monaco', 'Courier New', monospace",
                "size_xs": "11px",
                "size_small": "12px",
                "size_normal": "14px",
                "size_large": "16px",
                "size_xl": "18px",
                "size_heading": "20px",
                "size_title": "24px",
                "weight_light": "300",
                "weight_normal": "400",
                "weight_medium": "500",
                "weight_bold": "600",
                "weight_black": "700",
                "line_height_tight": "1.2",
                "line_height_normal": "1.5",
                "line_height_loose": "1.8",
            },
            "spacing": {
                "xs": "4px",
                "sm": "8px",
                "md": "16px",
                "lg": "24px",
                "xl": "32px",
                "xxl": "48px",
            },
            "border_radius": {
                "none": "0px",
                "small": "4px",
                "medium": "6px",
                "large": "8px",
                "xl": "12px",
                "round": "50%",
            },
            "shadows": {
                "none": "none",
                "small": "0 1px 3px rgba(0, 0, 0, 0.1)",
                "medium": "0 4px 6px rgba(0, 0, 0, 0.1)",
                "large": "0 10px 15px rgba(0, 0, 0, 0.1)",
                "xl": "0 20px 25px rgba(0, 0, 0, 0.1)",
            },
        },
        "dark": {
            "name": "深色主题",
            "description": "优雅的深色主题，减少眼部疲劳，适合夜间使用",
            "colors": {
                # 主要颜色 - 深色主题的品牌色和功能色
                "primary": "#4A9EFF",  # 主品牌色（亮蓝色）
                "primary_light": "#7BB8FF",  # 浅色主品牌色
                "primary_dark": "#2E7CE8",  # 深色主品牌色
                "secondary": "#8E9297",  # 次要颜色（亮灰色）
                "success": "#4CAF50",  # 成功色（亮绿色）
                "warning": "#FF9800",  # 警告色（橙色）
                "danger": "#F44336",  # 危险色（亮红色）
                "info": "#00BCD4",  # 信息色（亮青色）
                # 背景颜色 - 深色主题的背景层级
                "background": "#1A1A1A",  # 主背景色（深黑）
                "surface": "#2D2D2D",  # 表面背景色（深灰）
                "surface_variant": "#3A3A3A",  # 表面变体色
                "card": "#2D2D2D",  # 卡片背景色
                "overlay": "rgba(0, 0, 0, 0.7)",  # 遮罩层颜色
                # 文本颜色 - 深色主题的文本层级
                "text_primary": "#FFFFFF",  # 主要文本色（白色）
                "text_secondary": "#B3B3B3",  # 次要文本色（亮灰）
                "text_muted": "#808080",  # 弱化文本色（中灰）
                "text_disabled": "#4D4D4D",  # 禁用文本色（深灰）
                "text_on_primary": "#FFFFFF",  # 主色上的文本
                "text_on_dark": "#FFFFFF",  # 深色背景上的文本
                # 边框颜色 - 深色主题的边框
                "border": "#404040",  # 标准边框色
                "border_light": "#4D4D4D",  # 浅色边框
                "border_dark": "#333333",  # 深色边框
                "border_focus": "#4A9EFF",  # 焦点边框色
                # 状态颜色 - 深色主题的交互状态
                "hover": "#3A3A3A",  # 悬停背景色
                "active": "#4D4D4D",  # 激活背景色
                "focus": "#4A9EFF",  # 焦点色
                "selected": "#1E3A5F",  # 选中背景色
                "disabled": "#2D2D2D",  # 禁用背景色
                # 阴影颜色 - 深色主题的阴影
                "shadow_light": "rgba(0, 0, 0, 0.3)",
                "shadow_medium": "rgba(0, 0, 0, 0.4)",
                "shadow_dark": "rgba(0, 0, 0, 0.5)",
            },
            "fonts": {
                "family": "Microsoft YaHei UI, 'Segoe UI', Arial, sans-serif",
                "family_monospace": "'Consolas', 'Monaco', 'Courier New', monospace",
                "size_xs": "11px",
                "size_small": "12px",
                "size_normal": "14px",
                "size_large": "16px",
                "size_xl": "18px",
                "size_heading": "20px",
                "size_title": "24px",
                "weight_light": "300",
                "weight_normal": "400",
                "weight_medium": "500",
                "weight_bold": "600",
                "weight_black": "700",
                "line_height_tight": "1.2",
                "line_height_normal": "1.5",
                "line_height_loose": "1.8",
            },
            "spacing": {
                "xs": "4px",
                "sm": "8px",
                "md": "16px",
                "lg": "24px",
                "xl": "32px",
                "xxl": "48px",
            },
            "border_radius": {
                "none": "0px",
                "small": "4px",
                "medium": "6px",
                "large": "8px",
                "xl": "12px",
                "round": "50%",
            },
            "shadows": {
                "none": "none",
                "small": "0 1px 3px rgba(0, 0, 0, 0.3)",
                "medium": "0 4px 6px rgba(0, 0, 0, 0.4)",
                "large": "0 10px 15px rgba(0, 0, 0, 0.4)",
                "xl": "0 20px 25px rgba(0, 0, 0, 0.5)",
            },
        },
        "blue": {
            "name": "蓝色主题",
            "description": "专业的蓝色主题，营造商务氛围，适合办公环境",
            "colors": {
                # 主要颜色 - 蓝色主题的品牌色和功能色
                "primary": "#2196F3",  # 主品牌色（Material蓝）
                "primary_light": "#64B5F6",  # 浅色主品牌色
                "primary_dark": "#1976D2",  # 深色主品牌色
                "secondary": "#607D8B",  # 次要颜色（蓝灰色）
                "success": "#4CAF50",  # 成功色（绿色）
                "warning": "#FF9800",  # 警告色（橙色）
                "danger": "#F44336",  # 危险色（红色）
                "info": "#00BCD4",  # 信息色（青色）
                # 背景颜色 - 蓝色主题的背景层级
                "background": "#FAFAFA",  # 主背景色（极浅灰）
                "surface": "#F5F5F5",  # 表面背景色（浅灰）
                "surface_variant": "#ECEFF1",  # 表面变体色
                "card": "#FFFFFF",  # 卡片背景色（白色）
                "overlay": "rgba(33, 150, 243, 0.1)",  # 遮罩层颜色
                # 文本颜色 - 蓝色主题的文本层级
                "text_primary": "#212121",  # 主要文本色（深黑）
                "text_secondary": "#757575",  # 次要文本色（中灰）
                "text_muted": "#BDBDBD",  # 弱化文本色（浅灰）
                "text_disabled": "#E0E0E0",  # 禁用文本色（极浅灰）
                "text_on_primary": "#FFFFFF",  # 主色上的文本
                "text_on_dark": "#FFFFFF",  # 深色背景上的文本
                # 边框颜色 - 蓝色主题的边框
                "border": "#E0E0E0",  # 标准边框色
                "border_light": "#EEEEEE",  # 浅色边框
                "border_dark": "#BDBDBD",  # 深色边框
                "border_focus": "#64B5F6",  # 焦点边框色
                # 状态颜色 - 蓝色主题的交互状态
                "hover": "#F5F5F5",  # 悬停背景色
                "active": "#EEEEEE",  # 激活背景色
                "focus": "#64B5F6",  # 焦点色
                "selected": "#E3F2FD",  # 选中背景色
                "disabled": "#F5F5F5",  # 禁用背景色
                # 阴影颜色 - 蓝色主题的阴影
                "shadow_light": "rgba(33, 150, 243, 0.1)",
                "shadow_medium": "rgba(33, 150, 243, 0.15)",
                "shadow_dark": "rgba(33, 150, 243, 0.2)",
            },
            "fonts": {
                "family": "Microsoft YaHei UI, 'Segoe UI', Arial, sans-serif",
                "family_monospace": "'Consolas', 'Monaco', 'Courier New', monospace",
                "size_xs": "11px",
                "size_small": "12px",
                "size_normal": "14px",
                "size_large": "16px",
                "size_xl": "18px",
                "size_heading": "20px",
                "size_title": "24px",
                "weight_light": "300",
                "weight_normal": "400",
                "weight_medium": "500",
                "weight_bold": "600",
                "weight_black": "700",
                "line_height_tight": "1.2",
                "line_height_normal": "1.5",
                "line_height_loose": "1.8",
            },
            "spacing": {
                "xs": "4px",
                "sm": "8px",
                "md": "16px",
                "lg": "24px",
                "xl": "32px",
                "xxl": "48px",
            },
            "border_radius": {
                "none": "0px",
                "small": "4px",
                "medium": "6px",
                "large": "8px",
                "xl": "12px",
                "round": "50%",
            },
            "shadows": {
                "none": "none",
                "small": "0 1px 3px rgba(33, 150, 243, 0.1)",
                "medium": "0 4px 6px rgba(33, 150, 243, 0.15)",
                "large": "0 10px 15px rgba(33, 150, 243, 0.15)",
                "xl": "0 20px 25px rgba(33, 150, 243, 0.2)",
            },
        },
    }
