# MiniCRM 平台适配说明

## 概述

MiniCRM 主题系统提供了完整的跨平台适配支持，确保应用程序在不同操作系统上都能提供原生的用户体验。

## 支持的平台

### macOS
- **字体适配**: 使用 `-apple-system` 系统字体族
- **圆角设计**: 采用更大的圆角半径（8px, 12px）匹配 macOS 设计语言
- **系统主题检测**: 自动检测 macOS 的深色/浅色模式
- **高DPI支持**: 自动适配 Retina 显示器

### Windows
- **字体适配**: 使用 `Segoe UI` 作为主要字体
- **圆角设计**: 采用较小的圆角半径（4px, 6px）匹配 Windows 设计语言
- **系统主题检测**: 通过注册表检测 Windows 主题设置
- **高DPI支持**: 自动适配高分辨率显示器

### Linux（基础支持）
- **字体适配**: 使用通用的 sans-serif 字体族
- **默认主题**: 使用浅色主题作为默认
- **高DPI支持**: 基础的高DPI适配

## 自动适配功能

### 1. 系统主题检测
```python
# 自动检测系统主题
theme_manager = ThemeManager.get_instance()
theme_manager.set_auto_theme_mode(True)  # 启用自动主题模式
```

### 2. 高DPI适配
- 自动检测设备像素比
- 字体大小增加 20%
- 间距增加 20%
- 保持界面元素的视觉比例

### 3. 平台特定样式
- **macOS**: 更大的圆角、系统字体、原生滚动条样式
- **Windows**: 较小的圆角、Segoe UI 字体、Windows 风格的控件
- **Linux**: 通用样式，兼容性优先

## 使用示例

### 获取平台信息
```python
theme_manager = ThemeManager.get_instance()
platform_info = theme_manager.get_platform_info()

print(f"平台: {platform_info['platform']}")
print(f"高DPI: {platform_info['is_high_dpi']}")
print(f"系统主题: {platform_info['system_theme']}")
```

### 应用平台适配的主题
```python
# 主题管理器会自动应用平台适配
theme_manager.set_theme("light")  # 自动应用平台特定的调整
```

### 手动获取适配后的配置
```python
# 获取经过平台适配的主题配置
theme_config = theme_manager.get_theme_config()
adjusted_config = theme_manager._apply_platform_adjustments(theme_config)
```

## 技术实现

### 平台检测
```python
import platform
self._platform = platform.system().lower()  # 'darwin', 'windows', 'linux'
```

### 高DPI检测
```python
from PySide6.QtWidgets import QApplication
app = QApplication.instance()
device_pixel_ratio = app.devicePixelRatio()
self._is_high_dpi = device_pixel_ratio > 1.0
```

### 系统主题检测

#### macOS
```python
import subprocess
result = subprocess.run(
    ["defaults", "read", "-g", "AppleInterfaceStyle"],
    capture_output=True, text=True
)
return "dark" if result.stdout.strip() == "Dark" else "light"
```

#### Windows
```python
import winreg
key = winreg.OpenKey(
    winreg.HKEY_CURRENT_USER,
    r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
)
apps_use_light_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
return "light" if apps_use_light_theme else "dark"
```

## 配置选项

### 主题模式
- `ThemeMode.LIGHT`: 强制浅色主题
- `ThemeMode.DARK`: 强制深色主题
- `ThemeMode.AUTO`: 自动跟随系统主题

### 平台适配开关
```python
# 可以通过配置禁用特定的平台适配
theme_manager._apply_platform_adjustments = lambda config: config  # 禁用平台适配
```

## 最佳实践

1. **使用自动主题模式**: 让应用程序自动适配系统主题
2. **测试多平台**: 在不同平台上测试界面效果
3. **考虑高DPI**: 确保在高分辨率显示器上的显示效果
4. **遵循平台规范**: 尊重各平台的设计语言和用户习惯

## 故障排除

### 字体显示问题
- 确保系统字体可用
- 检查字体回退机制
- 验证字体大小适配

### 主题检测失败
- 检查系统权限
- 验证注册表访问（Windows）
- 确认系统命令可用（macOS）

### 高DPI显示异常
- 检查设备像素比检测
- 验证缩放计算
- 测试不同分辨率设备

## 扩展支持

如需添加新平台支持，请：

1. 在 `_detect_system_theme()` 中添加平台检测逻辑
2. 在 `_apply_platform_adjustments()` 中添加平台特定调整
3. 更新平台信息获取方法
4. 添加相应的测试用例

## 参考资料

- [macOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/macos)
- [Windows Design Guidelines](https://docs.microsoft.com/en-us/windows/apps/design/)
- [Qt High DPI Support](https://doc.qt.io/qt-6/highdpi.html)
