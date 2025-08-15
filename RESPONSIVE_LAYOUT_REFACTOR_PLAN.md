# responsive_layout.py 重构计划

## 当前问题
- 文件大小: 1613行 (超出标准101%)
- 包含多个独立的类，违反单一职责原则
- 难以维护和测试

## 拆分方案

### 1. 核心响应式管理 (300行)
**文件**: `src/minicrm/ui/responsive/responsive_manager.py`
**包含类**:
- ResponsiveLayoutManager
- BreakPoint (dataclass)
- LayoutConfig (dataclass)
- ScreenSize (enum)

### 2. 响应式组件基类 (200行)
**文件**: `src/minicrm/ui/responsive/responsive_widgets.py`
**包含类**:
- ResponsiveWidget
- AutoScaleWidget

### 3. 布局组件 (250行)
**文件**: `src/minicrm/ui/responsive/layout_components.py`
**包含类**:
- FlexLayout
- ResponsiveGridWidget

### 4. 自适应容器 (200行)
**文件**: `src/minicrm/ui/responsive/adaptive_containers.py`
**包含类**:
- AdaptiveContainer

### 5. 高DPI管理 (300行)
**文件**: `src/minicrm/ui/responsive/highdpi_manager.py`
**包含类**:
- HighDPIManager

### 6. 响应式模块入口 (50行)
**文件**: `src/minicrm/ui/responsive/__init__.py`
**功能**: 导出所有公共类和函数

## 重构步骤

1. 创建 `src/minicrm/ui/responsive/` 目录
2. 按照上述方案拆分文件
3. 更新导入语句
4. 测试功能完整性
5. 删除原始文件

## 预期效果

- 每个文件不超过300行
- 职责清晰，易于维护
- 符合MiniCRM模块化标准
- 提高代码可读性和可测试性
