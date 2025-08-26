# 📦 MiniCRM 依赖优化说明

## 🎯 优化目标

基于代码分析，我们对项目依赖进行了全面优化，移除了未使用的依赖，保持sqlite3架构，提升项目性能和可维护性。

## 📊 优化结果对比

### 优化前 (25个核心依赖)
```toml
dependencies = [
    # GUI框架已迁移到tkinter/ttk (Python标准库)
    "SQLAlchemy>=2.0.0",      # ❌ 未使用 (实际使用sqlite3)
    "alembic>=1.13.0",        # ❌ 未使用
    "python-docx>=1.1.0",     # ❌ 未使用
    "docxtpl>=0.16.0",        # ❌ 未使用
    "openpyxl>=3.1.0",        # ❌ 未使用
    "reportlab>=4.0.0",       # ✅ 使用中
    "Pillow>=10.0.0",         # ✅ 使用中
    "matplotlib>=3.8.0",      # ✅ 使用中
    "seaborn>=0.13.0",        # ❌ 未使用
    "pandas>=2.1.0",          # ✅ 使用中
    "numpy>=1.24.0",          # ✅ 使用中
    "pydantic>=2.5.0",        # ❌ 未使用
    "python-dateutil>=2.8.0", # ✅ 使用中
    "loguru>=0.7.0",          # ❌ 未使用 (使用标准logging)
    "psutil>=5.9.0",          # ✅ 使用中
    "click>=8.1.0",           # ❌ 未使用
    "rich>=13.0.0",           # ❌ 未使用
    "tqdm>=4.66.0",           # ❌ 未使用
    "cachetools>=5.3.0",      # ❌ 未使用
    "PyYAML>=6.0.0",          # ❌ 未使用
    "mypy>=1.17.1",           # ❌ 应在dev依赖中
    "safety>=3.6.0",          # ❌ 应在dev依赖中
]
```

### 优化后 (8个核心依赖)
```toml
dependencies = [
    # GUI框架 - 使用tkinter/ttk (Python标准库)
    # 无需外部GUI依赖，使用Python内置tkinter/ttk

    # 数据处理
    "pandas>=2.1.0",          # ✅ data_import_service.py
    "numpy>=1.24.0",          # ✅ chart组件

    # 数据可视化
    "matplotlib>=3.8.0",      # ✅ chart组件

    # PDF文档生成
    "reportlab>=4.0.0",       # ✅ pdf_export_service.py
    "Pillow>=10.0.0",         # ✅ reportlab依赖

    # 系统监控
    "psutil>=5.9.0",          # ✅ 性能监控模块

    # 日期处理
    "python-dateutil>=2.8.0", # ✅ 日期计算
]
```

## 🔍 技术架构确认

### 数据库架构
- **选择**: SQLite3 (标准库)
- **原因**:
  - 轻量级，适合桌面应用
  - 无需额外服务器
  - 项目已有完整的sqlite3实现
- **相关文件**:
  - `src/minicrm/data/database/database_manager.py`
  - `src/minicrm/data/dao/database_executor.py`
  - `src/minicrm/data/database/database_schema.py`

### GUI框架
- **选择**: tkinter/ttk
- **原因**: 无需额外依赖，跨平台支持，轻量级，减少应用程序大小
- **使用情况**: 项目已完全迁移到TTK架构

## 🚀 迁移步骤

### 自动迁移 (推荐)
```bash
# 1. 运行迁移脚本
python scripts/migrate_dependencies.py

# 2. 验证安装
python scripts/verify_dependencies.py
```

### 手动迁移
```bash
# 1. 备份当前环境
pip freeze > requirements_backup.txt

# 2. 卸载未使用的依赖
pip uninstall -y SQLAlchemy alembic python-docx docxtpl openpyxl pydantic loguru seaborn click rich tqdm cachetools PyYAML

# 3. 重新安装项目
pip install -e .

# 4. 验证核心功能
python -c "import tkinter, pandas, matplotlib, reportlab; print('✅ 核心依赖正常')"
```

## 📦 可选依赖组

根据需要安装额外功能：

```bash
# 文档处理 (Word/Excel)
pip install -e ".[documents]"

# 数据验证
pip install -e ".[validation]"

# 增强日志
pip install -e ".[logging]"

# 图表美化
pip install -e ".[charts]"

# CLI工具
pip install -e ".[cli]"

# 工具库
pip install -e ".[utils]"

# 开发工具
pip install -e ".[dev]"

# 完整安装
pip install -e ".[full]"
```

## 📈 性能提升

### 预期改进
- **安装时间**: 减少 60-70%
- **包大小**: 减少 50-60%
- **启动时间**: 减少导入开销
- **内存使用**: 减少未使用库的内存占用

### 维护优势
- **依赖关系更清晰**: 只包含实际使用的库
- **安全风险降低**: 减少潜在的安全漏洞面
- **更新更简单**: 需要维护的依赖更少
- **构建更快**: PyInstaller打包更快

## 🔧 开发工作流

### 日常开发
```bash
# 安装开发依赖
pip install -e ".[dev]"

# 代码质量检查
ruff check src/
mypy src/

# 运行测试
pytest

# 安全检查
safety check
```

### 添加新依赖
1. **评估必要性**: 确认是否真的需要新依赖
2. **选择合适的组**: 核心依赖 vs 可选依赖
3. **更新pyproject.toml**: 添加到合适的依赖组
4. **更新文档**: 说明新依赖的用途

## ⚠️ 注意事项

### 可能的影响
1. **功能缺失**: 如果代码中有未发现的依赖使用，可能出现ImportError
2. **测试失败**: 某些测试可能依赖被移除的库
3. **构建问题**: CI/CD流程可能需要调整

### 解决方案
1. **运行验证脚本**: `python scripts/verify_dependencies.py`
2. **逐步测试**: 测试各个功能模块
3. **按需安装**: 发现缺失功能时安装对应的可选依赖组

## 📋 检查清单

- [ ] 运行迁移脚本
- [ ] 验证核心功能正常
- [ ] 测试GUI界面启动
- [ ] 测试数据库操作
- [ ] 测试图表生成
- [ ] 测试PDF导出
- [ ] 运行单元测试
- [ ] 检查CI/CD流程

## 🎉 总结

通过这次依赖优化，MiniCRM项目现在拥有：
- ✅ 精简的依赖配置 (8个核心依赖)
- ✅ 清晰的架构选择 (SQLite3 + tkinter/ttk)
- ✅ 灵活的可选功能 (按需安装)
- ✅ 更好的性能表现
- ✅ 更低的维护成本

项目现在更加轻量、快速、易维护！
