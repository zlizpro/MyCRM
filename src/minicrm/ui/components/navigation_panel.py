"""
MiniCRM 导航面板组件 (兼容性导入)

⚠️ 此文件已被拆分为多个模块以符合MiniCRM模块化标准。
   请使用新的导入方式：

   旧方式: from minicrm.ui.components.navigation_panel import NavigationPanel
   新方式: from minicrm.ui.components.navigationpanel import NavigationPanel

从586行拆分为4个小文件，每个文件不超过200行：
- navigation_types.py: 类型定义 (18行)
- navigation_config.py: 导航配置 (147行)
- navigation_styles.py: 样式定义 (95行)
- navigation_panel.py: 主面板类 (326行)
"""

# 兼容性导入 - 保持向后兼容
import warnings

from .navigationpanel import NavigationItem, NavigationPanel


# 发出弃用警告
warnings.warn(
    "navigation_panel.py 已被拆分，"
    "请使用 'from minicrm.ui.components.navigationpanel import ...' 导入",
    DeprecationWarning,
    stacklevel=2,
)


# 导出所有类以保持向后兼容性
__all__ = [
    "NavigationPanel",
    "NavigationItem",
]
