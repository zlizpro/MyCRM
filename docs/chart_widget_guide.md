# ChartWidget 图表组件使用指南

## 概述

ChartWidget 是 MiniCRM 系统中的核心数据可视化组件，基于 matplotlib 和 tkinter/ttk 构建，提供了丰富的图表类型和交互功能。

## 特性

### 支持的图表类型

- **折线图 (line)**: 适用于显示趋势数据
- **柱状图 (bar)**: 适用于比较不同类别的数据
- **饼图 (pie)**: 适用于显示数据的组成比例
- **堆叠柱状图 (stacked_bar)**: 适用于显示多系列数据的组成
- **面积图 (area)**: 适用于显示数据的累积效果
- **散点图 (scatter)**: 适用于显示两个变量之间的关系
- **直方图 (histogram)**: 适用于显示数据的分布情况

### 交互功能

- **数据点点击**: 点击数据点获取详细信息
- **鼠标悬停**: 悬停显示数据点的值
- **缩放功能**: 使用滚轮进行图表缩放
- **重置缩放**: 一键恢复原始视图
- **数据导出**: 支持 PNG、PDF、SVG 格式导出

### 数据更新

- **静态更新**: 一次性更新所有数据
- **动画更新**: 平滑的数据变化动画
- **实时更新**: 动态添加新数据点

## 基本使用

### 创建图表组件

```python
from minicrm.ui.components.chart_widget import ChartWidget

# 创建折线图
chart = ChartWidget(
    title="客户增长趋势",
    chart_type="line",
    width=400,
    height=300
)
```

### 更新数据

```python
# 准备数据
labels = ["1月", "2月", "3月", "4月", "5月", "6月"]
data = [120, 135, 148, 162, 178, 195]

# 更新图表数据
chart.update_data(labels, data)
```

### 多系列数据

```python
# 多系列数据（用于堆叠柱状图等）
labels = ["产品A", "产品B", "产品C", "产品D"]
data = [
    [120, 150, 80, 90],   # 第一季度
    [140, 160, 95, 85],   # 第二季度
    [130, 170, 100, 95]   # 第三季度
]

chart.update_data(labels, data)
```

## 高级功能

### 动画更新

```python
# 启用动画效果更新数据
new_data = [150, 165, 180, 195, 210, 225]
chart.update_data(labels, new_data, animate=True)
```

### 实时数据添加

```python
# 添加新的数据点
chart.update_data_realtime("7月", 210)
```

### 自定义颜色

```python
# 使用自定义颜色
colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
chart.update_data(labels, data, colors=colors)
```

### 图表类型切换

```python
# 动态切换图表类型
chart.set_chart_type("bar")  # 切换为柱状图
chart.set_chart_type("pie")  # 切换为饼图
```

## 信号和事件

### 数据点点击事件

```python
def on_data_point_clicked(index, value):
    print(f"点击了第 {index} 个数据点，值为 {value}")

# 连接信号
chart.data_point_clicked.connect(on_data_point_clicked)
```

### 图表导出事件

```python
def on_chart_exported(file_path):
    print(f"图表已导出到: {file_path}")

# 连接信号
chart.chart_exported.connect(on_chart_exported)
```

## 样式和主题

### 中文字体支持

组件自动检测操作系统并设置合适的中文字体：

- **macOS**: PingFang SC, Hiragino Sans GB
- **Windows**: Microsoft YaHei, SimHei
- **Linux**: WenQuanYi Micro Hei

### 颜色方案

默认提供了一套现代化的颜色方案：

```python
default_colors = [
    "#007bff",  # 蓝色
    "#28a745",  # 绿色
    "#ffc107",  # 黄色
    "#dc3545",  # 红色
    "#6f42c1",  # 紫色
    "#17a2b8",  # 青色
    "#fd7e14",  # 橙色
    "#20c997",  # 青绿色
    "#6c757d",  # 灰色
    "#e83e8c",  # 粉色
]
```

## 性能优化

### 数据点限制

实时数据更新时，组件会自动限制数据点数量（默认50个），避免性能问题：

```python
# 可以通过修改源码调整限制
max_points = 100  # 在 update_data_realtime 方法中修改
```

### 动画性能

动画更新使用了优化的插值算法，确保流畅的视觉效果：

```python
# 动画参数可调整
steps = 20      # 动画步数
interval = 50   # 每帧间隔（毫秒）
```

## 最佳实践

### 1. 选择合适的图表类型

- 趋势数据 → 折线图或面积图
- 分类比较 → 柱状图
- 比例关系 → 饼图
- 多维数据 → 散点图
- 数据分布 → 直方图

### 2. 数据预处理

```python
# 确保数据类型正确
data = [float(x) for x in raw_data if isinstance(x, (int, float))]

# 处理空值
data = [x if x is not None else 0 for x in raw_data]
```

### 3. 合理使用动画

```python
# 只在数据变化较大时使用动画
if max(new_data) - max(old_data) > threshold:
    chart.update_data(labels, new_data, animate=True)
else:
    chart.update_data(labels, new_data)
```

### 4. 内存管理

```python
# 定期清理大量历史数据
if len(chart._labels) > 1000:
    chart.clear()
    # 重新加载必要数据
```

## 故障排除

### 常见问题

1. **中文字体显示为方框**
   - 确保系统安装了中文字体
   - 检查 matplotlib 字体缓存

2. **图表不显示数据**
   - 检查数据格式是否正确
   - 确保标签和数据长度匹配

3. **动画效果卡顿**
   - 减少动画步数
   - 增加帧间隔时间

4. **导出功能失败**
   - 检查文件路径权限
   - 确保磁盘空间充足

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查图表数据
print(chart.get_data())

# 验证图表状态
print(f"图表类型: {chart._chart_type}")
print(f"数据点数: {len(chart._labels)}")
```

## 扩展开发

### 添加新图表类型

1. 在 `set_chart_type` 方法中添加新类型
2. 实现对应的 `_draw_xxx_chart` 方法
3. 更新支持的类型列表

### 自定义交互功能

```python
# 继承 ChartWidget 并重写事件方法
class CustomChartWidget(ChartWidget):
    def _on_canvas_click(self, event):
        # 自定义点击处理逻辑
        super()._on_canvas_click(event)
        # 添加额外功能
```

## 示例代码

完整的使用示例请参考 `examples/chart_widget_usage.py` 文件。
