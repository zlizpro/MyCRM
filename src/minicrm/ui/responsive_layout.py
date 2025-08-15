"""
MiniCRM 响应式布局系统 (兼容性导入)

⚠️ 此文件已被拆分为多个模块以符合MiniCRM模块化标准。
   请使用新的导入方式：

   旧方式: from minicrm.ui.responsive_layout import ResponsiveLayoutManager
   新方式: from minicrm.ui.responsive import ResponsiveLayoutManager

从1617行拆分为多个小文件，每个文件不超过400行：
- types.py: 类型定义 (47行)
- layout_manager.py: 布局管理器 (398行)
- responsive_widgets.py: 响应式组件 (247行)
"""

# 兼容性导入 - 保持向后兼容
import warnings

from .responsive import AutoScaleWidget, ResponsiveLayoutManager, ResponsiveWidget


# 发出弃用警告
warnings.warn(
    "responsive_layout.py 已被拆分，"
    "请使用 'from minicrm.ui.responsive import ...' 导入",
    DeprecationWarning,
    stacklevel=2,
)


# 导出所有类以保持向后兼容性
__all__ = [
    "ResponsiveLayoutManager",
    "ResponsiveWidget",
    "AutoScaleWidget",
]
