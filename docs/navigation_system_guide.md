# MiniCRM 导航系统使用指南

## 概述

MiniCRM 导航系统是一个统一的导航解决方案，整合了左侧导航面板、页面管理、路由系统、面包屑导航和历史记录管理等功能。

## 核心组件

### 1. NavigationSystem (统一导航系统)

主要的导航管理器，整合所有导航相关功能。

```python
from src.minicrm.ui.components.navigation import NavigationSystem
import tkinter as tk
from tkinter import ttk

# 创建内容堆栈
content_stack = QStackedWidget()

# 初始化导航系统
navigation_system = NavigationSystem(content_stack)
```

### 2. NavigationPanel (导航面板)

左侧树形导航面板，提供应用程序的主要导航入口。

```python
# 获取导航面板
navigation_panel = navigation_system.get_navigation_panel()

# 添加到布局中
layout.addWidget(navigation_panel)
```

### 3. PageManager (页面管理器)

管理页面的生命周期、切换和历史记录。

### 4. PageRouter (页面路由器)

提供URL风格的页面路由功能。

## 基本使用

### 1. 注册页面

```python
# 注册简单页面
navigation_system.register_page(
    name="dashboard",
    title="数据仪表盘",
    widget_class=DashboardWidget,
    route_path="/dashboard",
    description="显示系统关键指标"
)

# 注册带父页面的页面（用于面包屑导航）
navigation_system.register_page(
    name="customer_detail",
    title="客户详情",
    widget_class=CustomerDetailWidget,
    route_path="/customers/detail",
    parent_page="customers",
    description="显示客户详细信息"
)

# 注册页面工厂函数
def create_dynamic_page():
    return MyDynamicWidget()

navigation_system.register_page_factory(
    name="dynamic_page",
    title="动态页面",
    factory_func=create_dynamic_page,
    route_path="/dynamic"
)
```

### 2. 页面导航

```python
# 通过页面名称导航
navigation_system.navigate_to("dashboard")

# 通过页面名称导航并传递参数
navigation_system.navigate_to("customer_detail", {"customer_id": 123})

# 通过路由路径导航
navigation_system.navigate_by_route("/customers/detail")

# 导航到默认页面
navigation_system.set_default_page("dashboard")
navigation_system.navigate_to_default()
```

### 3. 历史记录管理

```python
# 返回上一页
navigation_system.go_back()

# 获取导航历史
history = navigation_system.get_navigation_history()

# 清空历史记录
navigation_system.clear_history()
```

### 4. 页面状态管理

```python
# 获取当前页面
current_page = navigation_system.get_current_page()

# 获取当前页面组件
current_widget = navigation_system.get_current_widget()

# 刷新当前页面
navigation_system.refresh_current_page()

# 预加载页面
navigation_system.preload_page("heavy_page")

# 卸载页面（释放内存）
navigation_system.unload_page("unused_page")
```

### 5. 导航面板管理

```python
# 启用/禁用导航
navigation_system.set_navigation_enabled(False)

# 设置页面启用状态
navigation_system.set_page_enabled("admin_page", False)

# 添加导航徽章
navigation_system.add_navigation_badge("tasks", "5")

# 移除导航徽章
navigation_system.remove_navigation_badge("tasks")

# 切换主题
navigation_system.set_theme("dark")
```

## 页面生命周期

### 页面类实现

```python
import tkinter as tk
from tkinter import ttk

class MyPageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def on_page_enter(self, params):
        """页面进入时调用"""
        print(f"进入页面，参数: {params}")
        # 初始化页面数据
        self.load_data(params)

    def on_page_leave(self):
        """页面离开时调用"""
        print("离开页面")
        # 保存页面状态
        self.save_state()

    def refresh(self):
        """页面刷新时调用"""
        print("刷新页面")
        # 重新加载数据
        self.reload_data()

    def cleanup(self):
        """页面清理时调用"""
        print("清理页面资源")
        # 清理资源
        self.cleanup_resources()
```

## 信号处理

### 连接导航信号

```python
# 连接导航变化信号
navigation_system.navigation_changed.connect(on_navigation_changed)

# 连接页面加载信号
navigation_system.page_loading.connect(on_page_loading)
navigation_system.page_loaded.connect(on_page_loaded)
navigation_system.page_error.connect(on_page_error)

# 连接面包屑更新信号
navigation_system.breadcrumb_updated.connect(on_breadcrumb_updated)

# 连接历史记录更新信号
navigation_system.history_updated.connect(on_history_updated)

def on_navigation_changed(page_name):
    print(f"导航到页面: {page_name}")

def on_page_loading(page_name):
    print(f"正在加载页面: {page_name}")

def on_page_loaded(page_name, widget):
    print(f"页面加载完成: {page_name}")

def on_page_error(page_name, error):
    print(f"页面错误 [{page_name}]: {error}")

def on_breadcrumb_updated(breadcrumb):
    breadcrumb_text = " > ".join(breadcrumb)
    print(f"面包屑: {breadcrumb_text}")

def on_history_updated(history):
    print(f"历史记录更新: {len(history)} 项")
```

## 完整示例

```python
import sys
import tkinter as tk
from tkinter import ttk

from src.minicrm.ui.components.navigation import NavigationSystem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_navigation()
        self.register_pages()

    def setup_ui(self):
        """设置主窗口UI"""
        self.setWindowTitle("MiniCRM")
        self.setGeometry(100, 100, 1200, 800)

        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        layout = QHBoxLayout(central_widget)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # 创建内容堆栈
        self.content_stack = QStackedWidget()

        # 初始化导航系统
        self.navigation_system = NavigationSystem(self.content_stack)

        # 添加导航面板和内容区域
        navigation_panel = self.navigation_system.get_navigation_panel()
        splitter.addWidget(navigation_panel)
        splitter.addWidget(self.content_stack)

        # 设置分割器比例
        splitter.setSizes([250, 950])

    def setup_navigation(self):
        """设置导航信号"""
        self.navigation_system.navigation_changed.connect(self.on_navigation_changed)
        self.navigation_system.breadcrumb_updated.connect(self.on_breadcrumb_updated)

    def register_pages(self):
        """注册页面"""
        # 注册仪表盘页面
        self.navigation_system.register_page(
            name="dashboard",
            title="数据仪表盘",
            widget_class=lambda: QWidget(),  # 简化示例
            route_path="/dashboard"
        )

        # 注册客户管理页面
        self.navigation_system.register_page(
            name="customers",
            title="客户管理",
            widget_class=lambda: QWidget(),
            route_path="/customers"
        )

        # 设置默认页面并导航
        self.navigation_system.set_default_page("dashboard")
        self.navigation_system.navigate_to_default()

    def on_navigation_changed(self, page_name):
        """处理导航变化"""
        self.statusBar().showMessage(f"当前页面: {page_name}")

    def on_breadcrumb_updated(self, breadcrumb):
        """处理面包屑更新"""
        breadcrumb_text = " > ".join(breadcrumb)
        print(f"面包屑: {breadcrumb_text}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

## 最佳实践

### 1. 页面组织

- 使用有意义的页面名称和路由路径
- 合理设置父子页面关系以支持面包屑导航
- 为页面提供清晰的标题和描述

### 2. 性能优化

- 使用懒加载避免启动时加载所有页面
- 适时卸载不常用的页面以释放内存
- 预加载用户可能访问的页面

### 3. 用户体验

- 提供清晰的导航反馈（加载状态、错误信息）
- 保持导航状态的一致性
- 支持键盘快捷键（如 Alt+Left 返回上一页）

### 4. 错误处理

- 为页面加载失败提供友好的错误信息
- 实现页面加载超时处理
- 提供重试机制

## 测试

运行导航系统测试：

```bash
python -m pytest tests/test_navigation_system.py -v
```

运行示例程序：

```bash
python examples/navigation_system_usage.py
```

## 扩展

### 自定义导航项

可以通过修改 `navigation_config.py` 来自定义导航项的结构和样式。

### 自定义主题

可以通过修改 `navigation_styles.py` 来自定义导航面板的外观。

### 插件支持

导航系统支持通过页面工厂函数动态注册页面，便于实现插件系统。
