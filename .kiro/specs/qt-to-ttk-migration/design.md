# MiniCRM Qt到TTK重构设计文档

## 概述

本设计文档详细描述了将MiniCRM系统从PySide6 (Qt)框架迁移到Python标准库tkinter/ttk框架的技术方案。设计遵循分层架构原则，确保在迁移过程中保持代码的可维护性、可扩展性和业务逻辑的完整性。

### 设计目标

- **架构一致性**：保持现有的分层架构设计
- **组件化设计**：建立可复用的TTK组件库
- **性能优化**：通过合理的设计确保系统性能
- **用户体验**：提供与Qt版本相当的用户界面体验
- **可维护性**：确保代码结构清晰，便于后续维护

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    MiniCRM TTK 架构                          │
├─────────────────────────────────────────────────────────────┤
│  UI层 (TTK)                                                 │
│  ├── ttk_base/          # TTK基础框架                       │
│  ├── components/        # 可复用UI组件                      │
│  ├── panels/           # 业务面板                           │
│  ├── dialogs/          # 对话框                             │
│  └── themes/           # 主题和样式                         │
├─────────────────────────────────────────────────────────────┤
│  适配器层 (Adapter)                                         │
│  ├── qt_to_ttk_adapter/  # Qt到TTK适配器                   │
│  ├── event_adapter/      # 事件适配器                      │
│  └── style_adapter/      # 样式适配器                      │
├─────────────────────────────────────────────────────────────┤
│  业务逻辑层 (Services) - 保持不变                           │
│  ├── customer_service/   # 客户服务                        │
│  ├── supplier_service/   # 供应商服务                      │
│  └── ...                # 其他业务服务                     │
├─────────────────────────────────────────────────────────────┤
│  数据访问层 (Data) - 保持不变                               │
│  ├── dao/               # 数据访问对象                      │
│  ├── models/            # 数据模型                          │
│  └── connection_pool/   # 数据库连接池                     │
└─────────────────────────────────────────────────────────────┘
```

### 核心设计原则

1. **分离关注点**：UI层只负责界面展示，业务逻辑保持在Services层
2. **适配器模式**：使用适配器层实现Qt到TTK的平滑过渡
3. **组件化**：构建可复用的TTK组件库
4. **配置驱动**：通过配置文件管理样式、主题和布局
5. **性能优先**：在设计中考虑性能优化策略

## 组件设计

### TTK基础框架

#### BaseWindow 类设计
```python
class BaseWindow(tk.Tk):
    """TTK基础窗口类"""

    def __init__(self, title: str = "MiniCRM", size: Tuple[int, int] = (1200, 800)):
        super().__init__()
        self.title = title
        self.geometry(f"{size[0]}x{size[1]}")
        self._setup_window()
        self._setup_styles()
        self._bind_events()

    def _setup_window(self) -> None:
        """设置窗口基础属性"""

    def _setup_styles(self) -> None:
        """设置窗口样式"""

    def _bind_events(self) -> None:
        """绑定窗口事件"""
```

#### BaseWidget 类设计
```python
class BaseWidget(ttk.Frame):
    """TTK基础组件类"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._setup_ui()
        self._bind_events()
        self._apply_styles()

    def _setup_ui(self) -> None:
        """设置UI布局 - 子类重写"""

    def _bind_events(self) -> None:
        """绑定事件 - 子类重写"""

    def _apply_styles(self) -> None:
        """应用样式 - 子类重写"""

    def cleanup(self) -> None:
        """清理资源"""
```

#### LayoutManager 类设计
```python
class LayoutManager:
    """布局管理器"""

    @staticmethod
    def create_grid_layout(parent, rows: int, cols: int) -> None:
        """创建网格布局"""

    @staticmethod
    def create_form_layout(parent, fields: List[Dict]) -> Dict[str, tk.Widget]:
        """创建表单布局"""

    @staticmethod
    def create_toolbar_layout(parent, buttons: List[Dict]) -> ttk.Frame:
        """创建工具栏布局"""
```

### 组件映射设计

#### 核心组件映射表
| Qt组件 | TTK组件 | 适配器类 | 特殊处理 |
|--------|---------|----------|----------|
| QMainWindow | tk.Tk | MainWindowAdapter | 菜单栏、状态栏集成 |
| QWidget | ttk.Frame | WidgetAdapter | 布局管理 |
| QTableWidget | ttk.Treeview | TableAdapter | 虚拟滚动、排序 |
| QLineEdit | ttk.Entry | EntryAdapter | 验证、格式化 |
| QTextEdit | tk.Text | TextAdapter | 滚动条、语法高亮 |
| QComboBox | ttk.Combobox | ComboboxAdapter | 数据绑定 |
| QTabWidget | ttk.Notebook | NotebookAdapter | 标签页管理 |
| QSplitter | ttk.PanedWindow | SplitterAdapter | 分割比例保存 |

#### 数据表格设计
```python
class DataTableTTK(BaseWidget):
    """TTK数据表格组件"""

    def __init__(self, parent, columns: List[Dict[str, Any]]):
        self.columns = columns
        self.data = []
        self.sort_column = None
        self.sort_reverse = False
        super().__init__(parent)

    def _setup_ui(self) -> None:
        """设置表格UI"""
        # 创建Treeview
        self.tree = ttk.Treeview(self, show='headings')

        # 配置列
        self._setup_columns()

        # 添加滚动条
        self._setup_scrollbars()

        # 布局
        self._setup_layout()

    def _setup_columns(self) -> None:
        """配置表格列"""
        col_ids = [col['id'] for col in self.columns]
        self.tree['columns'] = col_ids

        for col in self.columns:
            self.tree.heading(
                col['id'],
                text=col['text'],
                command=lambda c=col['id']: self._sort_by_column(c)
            )
            self.tree.column(
                col['id'],
                width=col.get('width', 100),
                anchor=col.get('anchor', 'w')
            )

    def load_data(self, data: List[Dict[str, Any]]) -> None:
        """加载数据"""
        self.data = data
        self._refresh_display()

    def _refresh_display(self) -> None:
        """刷新显示"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 排序数据
        if self.sort_column:
            self.data.sort(
                key=lambda x: x.get(self.sort_column, ''),
                reverse=self.sort_reverse
            )

        # 插入数据
        for row in self.data:
            values = [row.get(col['id'], '') for col in self.columns]
            self.tree.insert('', 'end', values=values)
```

#### 表单构建器设计
```python
class FormBuilderTTK(BaseWidget):
    """TTK表单构建器"""

    def __init__(self, parent, fields: List[Dict[str, Any]]):
        self.fields = fields
        self.widgets = {}
        self.validators = {}
        super().__init__(parent)

    def _setup_ui(self) -> None:
        """构建表单UI"""
        for i, field in enumerate(self.fields):
            self._create_field(i, field)

    def _create_field(self, row: int, field: Dict[str, Any]) -> None:
        """创建表单字段"""
        field_type = field.get('type', 'entry')
        field_id = field.get('id', f'field_{row}')
        label_text = field.get('label', '')

        # 创建标签
        label = ttk.Label(self, text=label_text)
        label.grid(row=row, column=0, sticky='w', padx=5, pady=2)

        # 创建输入组件
        widget = self._create_input_widget(field_type, field)
        widget.grid(row=row, column=1, sticky='ew', padx=5, pady=2)

        self.widgets[field_id] = widget

        # 设置验证器
        if 'validator' in field:
            self.validators[field_id] = field['validator']

    def _create_input_widget(self, field_type: str, field: Dict) -> tk.Widget:
        """创建输入组件"""
        if field_type == 'entry':
            return ttk.Entry(self)
        elif field_type == 'text':
            return tk.Text(self, height=4)
        elif field_type == 'combobox':
            return ttk.Combobox(self, values=field.get('options', []))
        elif field_type == 'checkbox':
            return ttk.Checkbutton(self)
        elif field_type == 'date':
            return DatePickerTTK(self)
        else:
            return ttk.Entry(self)

    def get_values(self) -> Dict[str, Any]:
        """获取表单值"""
        values = {}
        for field_id, widget in self.widgets.items():
            values[field_id] = self._get_widget_value(widget)
        return values

    def validate(self) -> Tuple[bool, List[str]]:
        """验证表单"""
        errors = []
        for field_id, validator in self.validators.items():
            widget = self.widgets[field_id]
            value = self._get_widget_value(widget)
            if not validator(value):
                errors.append(f"{field_id} 验证失败")
        return len(errors) == 0, errors
```

### 适配器层设计

#### Qt到TTK适配器
```python
class QtToTtkAdapter:
    """Qt到TTK适配器基类"""

    def __init__(self, qt_widget_config: Dict[str, Any]):
        self.config = qt_widget_config
        self.ttk_widget = None
        self._create_ttk_widget()
        self._apply_config()

    def _create_ttk_widget(self) -> None:
        """创建TTK组件 - 子类实现"""
        raise NotImplementedError

    def _apply_config(self) -> None:
        """应用配置"""
        if 'geometry' in self.config:
            self._apply_geometry(self.config['geometry'])
        if 'style' in self.config:
            self._apply_style(self.config['style'])

    def _apply_geometry(self, geometry: Dict) -> None:
        """应用几何配置"""
        pass

    def _apply_style(self, style: Dict) -> None:
        """应用样式配置"""
        pass
```

#### 事件适配器
```python
class EventAdapter:
    """事件适配器"""

    def __init__(self):
        self.event_mappings = {
            'clicked': '<Button-1>',
            'double_clicked': '<Double-Button-1>',
            'right_clicked': '<Button-3>',
            'key_pressed': '<KeyPress>',
            'focus_in': '<FocusIn>',
            'focus_out': '<FocusOut>',
        }

    def bind_qt_event(self, ttk_widget: tk.Widget, qt_event: str, handler: Callable) -> None:
        """绑定Qt事件到TTK组件"""
        ttk_event = self.event_mappings.get(qt_event)
        if ttk_event:
            ttk_widget.bind(ttk_event, handler)

    def convert_event_args(self, qt_event_type: str, ttk_event) -> Any:
        """转换事件参数"""
        # 根据事件类型转换参数格式
        pass
```

### 主题和样式设计

#### 主题管理器
```python
class TTKThemeManager:
    """TTK主题管理器"""

    def __init__(self):
        self.style = ttk.Style()
        self.current_theme = 'default'
        self.themes = {
            'default': DefaultTheme(),
            'dark': DarkTheme(),
            'light': LightTheme(),
            'high_contrast': HighContrastTheme(),
        }

    def apply_theme(self, theme_name: str) -> None:
        """应用主题"""
        if theme_name in self.themes:
            theme = self.themes[theme_name]
            theme.apply(self.style)
            self.current_theme = theme_name

    def get_theme_config(self, theme_name: str) -> Dict[str, Any]:
        """获取主题配置"""
        return self.themes.get(theme_name, {}).get_config()
```

#### 主题配置
```python
class BaseTheme:
    """基础主题类"""

    def __init__(self):
        self.colors = {}
        self.fonts = {}
        self.styles = {}

    def apply(self, style: ttk.Style) -> None:
        """应用主题"""
        self._configure_colors(style)
        self._configure_fonts(style)
        self._configure_styles(style)

    def _configure_colors(self, style: ttk.Style) -> None:
        """配置颜色"""
        pass

    def _configure_fonts(self, style: ttk.Style) -> None:
        """配置字体"""
        pass

    def _configure_styles(self, style: ttk.Style) -> None:
        """配置样式"""
        pass

class DefaultTheme(BaseTheme):
    """默认主题"""

    def __init__(self):
        super().__init__()
        self.colors = {
            'bg_primary': '#FFFFFF',
            'bg_secondary': '#F8F9FA',
            'text_primary': '#212529',
            'text_secondary': '#6C757D',
            'accent': '#007BFF',
            'success': '#28A745',
            'warning': '#FFC107',
            'danger': '#DC3545',
        }
        self.fonts = {
            'default': ('Microsoft YaHei UI', 9),
            'heading': ('Microsoft YaHei UI', 12, 'bold'),
            'small': ('Microsoft YaHei UI', 8),
        }
```

### 性能优化设计

#### 虚拟滚动实现
```python
class VirtualScrollMixin:
    """虚拟滚动混入类"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visible_start = 0
        self.visible_count = 50
        self.total_count = 0
        self.item_height = 25

    def setup_virtual_scroll(self, total_count: int) -> None:
        """设置虚拟滚动"""
        self.total_count = total_count
        self._update_scrollbar()
        self._render_visible_items()

    def _update_scrollbar(self) -> None:
        """更新滚动条"""
        # 计算滚动条范围
        total_height = self.total_count * self.item_height
        visible_height = self.visible_count * self.item_height

        # 更新滚动条配置
        pass

    def _render_visible_items(self) -> None:
        """渲染可见项目"""
        # 只渲染当前可见的项目
        end_index = min(self.visible_start + self.visible_count, self.total_count)
        for i in range(self.visible_start, end_index):
            self._render_item(i)

    def _on_scroll(self, event) -> None:
        """滚动事件处理"""
        # 计算新的可见范围
        # 更新显示内容
        pass
```

#### 数据缓存设计
```python
class DataCacheManager:
    """数据缓存管理器"""

    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []

    def get(self, key: str) -> Any:
        """获取缓存数据"""
        if key in self.cache:
            self._update_access_order(key)
            return self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """设置缓存数据"""
        if len(self.cache) >= self.max_size:
            self._evict_oldest()

        self.cache[key] = value
        self._update_access_order(key)

    def _evict_oldest(self) -> None:
        """淘汰最旧的数据"""
        if self.access_order:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
```

## 数据模型和接口

### 数据绑定设计
```python
class DataBinding:
    """数据绑定类"""

    def __init__(self):
        self.bindings = {}
        self.observers = {}

    def bind(self, widget: tk.Widget, data_path: str, formatter: Callable = None) -> None:
        """绑定组件到数据"""
        self.bindings[widget] = {
            'path': data_path,
            'formatter': formatter or (lambda x: x)
        }

    def update_data(self, data: Dict[str, Any]) -> None:
        """更新数据"""
        for widget, binding in self.bindings.items():
            value = self._get_nested_value(data, binding['path'])
            formatted_value = binding['formatter'](value)
            self._set_widget_value(widget, formatted_value)

    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """获取嵌套数据值"""
        keys = path.split('.')
        value = data
        for key in keys:
            value = value.get(key, '')
        return value

    def _set_widget_value(self, widget: tk.Widget, value: Any) -> None:
        """设置组件值"""
        if isinstance(widget, ttk.Entry):
            widget.delete(0, tk.END)
            widget.insert(0, str(value))
        elif isinstance(widget, tk.Text):
            widget.delete('1.0', tk.END)
            widget.insert('1.0', str(value))
        # 其他组件类型...
```

## 错误处理

### 异常处理策略
```python
class TTKErrorHandler:
    """TTK错误处理器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def handle_ui_error(self, error: Exception, context: str) -> None:
        """处理UI错误"""
        self.logger.error(f"UI错误 [{context}]: {error}")

        # 显示用户友好的错误消息
        messagebox.showerror(
            "系统错误",
            f"界面操作出现问题：{str(error)}\n\n请重试或联系技术支持。"
        )

    def handle_data_error(self, error: Exception, operation: str) -> None:
        """处理数据错误"""
        self.logger.error(f"数据错误 [{operation}]: {error}")

        messagebox.showerror(
            "数据错误",
            f"数据操作失败：{str(error)}\n\n请检查数据格式或网络连接。"
        )

    def handle_performance_warning(self, operation: str, duration: float) -> None:
        """处理性能警告"""
        if duration > 1.0:  # 超过1秒
            self.logger.warning(f"性能警告 [{operation}]: {duration:.2f}秒")
```

## 测试策略

### 单元测试设计
```python
class TestTTKComponents(unittest.TestCase):
    """TTK组件测试"""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

    def tearDown(self):
        self.root.destroy()

    def test_data_table_creation(self):
        """测试数据表格创建"""
        columns = [
            {'id': 'name', 'text': '姓名', 'width': 100},
            {'id': 'age', 'text': '年龄', 'width': 80},
        ]
        table = DataTableTTK(self.root, columns)

        # 验证表格创建成功
        self.assertIsNotNone(table.tree)
        self.assertEqual(len(table.tree['columns']), 2)

    def test_form_builder_validation(self):
        """测试表单构建器验证"""
        fields = [
            {
                'id': 'name',
                'type': 'entry',
                'label': '姓名',
                'validator': lambda x: len(x) > 0
            }
        ]
        form = FormBuilderTTK(self.root, fields)

        # 测试验证功能
        is_valid, errors = form.validate()
        self.assertFalse(is_valid)  # 空值应该验证失败
```

### 集成测试设计
```python
class TestBusinessPanelIntegration(unittest.TestCase):
    """业务面板集成测试"""

    def setUp(self):
        self.root = tk.Tk()
        self.mock_service = Mock()

    def test_customer_panel_workflow(self):
        """测试客户面板工作流程"""
        panel = CustomerPanelTTK(self.root, self.mock_service)

        # 模拟数据加载
        self.mock_service.get_all_customers.return_value = [
            {'id': 1, 'name': '测试客户', 'phone': '13800138000'}
        ]

        panel.load_data()

        # 验证数据加载
        self.mock_service.get_all_customers.assert_called_once()
        self.assertEqual(len(panel.data_table.data), 1)
```

## 部署和打包

### PyInstaller配置
```python
# build_config.py
import PyInstaller.__main__

def build_application():
    """构建应用程序"""
    PyInstaller.__main__.run([
        'src/minicrm/main.py',
        '--onefile',
        '--windowed',
        '--name=MiniCRM-TTK',
        '--icon=resources/icons/app.ico',
        '--add-data=resources;resources',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--exclude-module=PySide6',  # 排除Qt依赖
        '--optimize=2',
    ])

if __name__ == '__main__':
    build_application()
```

### 资源管理
```python
class ResourceManager:
    """资源管理器"""

    def __init__(self):
        self.base_path = self._get_base_path()

    def _get_base_path(self) -> str:
        """获取资源基础路径"""
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller打包后的路径
            return sys._MEIPASS
        else:
            # 开发环境路径
            return os.path.dirname(os.path.abspath(__file__))

    def get_icon_path(self, icon_name: str) -> str:
        """获取图标路径"""
        return os.path.join(self.base_path, 'resources', 'icons', icon_name)

    def get_theme_path(self, theme_name: str) -> str:
        """获取主题路径"""
        return os.path.join(self.base_path, 'resources', 'themes', f'{theme_name}.json')
```

这个设计文档提供了完整的技术架构和实现方案，确保Qt到TTK的迁移能够顺利进行，同时保持系统的功能完整性和性能表现。
