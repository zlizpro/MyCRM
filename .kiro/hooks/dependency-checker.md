# 依赖检查Hook

## Hook配置

**触发条件**: 当修改导入语句或requirements.txt时
**执行频率**: 每次保存相关文件
**适用文件**: `*.py`, `requirements.txt`, `setup.py`

## Hook描述

这个hook会在您修改代码导入或依赖文件时，自动检查依赖的一致性、安全性和版本兼容性。

## 执行任务

1. **导入语句分析**
   - 扫描所有Python文件的导入语句
   - 识别第三方库的使用
   - 检查未使用的导入

2. **依赖一致性检查**
   - 比较代码中使用的库与requirements.txt
   - 识别缺失的依赖
   - 发现多余的依赖声明

3. **版本兼容性验证**
   - 检查依赖库的版本兼容性
   - 识别可能的版本冲突
   - 验证Python版本要求

4. **安全漏洞扫描**
   - 检查已知的安全漏洞
   - 建议安全版本升级
   - 警告过时的依赖

5. **许可证合规检查**
   - 验证依赖库的许可证
   - 检查许可证兼容性
   - 生成许可证报告

## 检查项目

### 必需依赖
- tkinter (内置)
- pandas, numpy (数据处理)
- matplotlib (图表)
- python-docx, docxtpl (文档)
- sqlite3 (内置)

### 开发依赖
- black, flake8, mypy (代码质量)
- pytest (测试)
- PyInstaller (打包)

### 可选依赖
- Pillow (图像处理)
- reportlab (PDF生成)

## 输出格式

```
📦 依赖检查结果：

✅ 所有依赖正常

或

⚠️ 发现以下依赖问题：

1. 缺失依赖：
   - 代码中使用了 'openpyxl' 但未在 requirements.txt 中声明
   - 建议添加：openpyxl>=3.0.0

2. 多余依赖：
   - requirements.txt 中的 'requests' 未在代码中使用
   - 建议移除或确认是否需要

3. 版本冲突：
   - pandas 1.5.0 与 numpy 1.20.0 可能不兼容
   - 建议升级 numpy 到 1.21.0+

4. 安全警告：
   - Pillow 8.0.0 存在已知安全漏洞 CVE-2021-xxxxx
   - 建议升级到 Pillow 9.0.0+

5. 许可证问题：
   - 依赖库 'some-lib' 使用 GPL 许可证
   - 可能与项目许可证不兼容，请确认

## 建议的 requirements.txt 更新：

```txt
# 添加缺失依赖
openpyxl>=3.0.0

# 更新版本解决冲突
numpy>=1.21.0
Pillow>=9.0.0

# 移除未使用依赖
# requests>=2.28.0  # 已移除
```

## 自动修复选项

### 立即可执行的修复
1. **自动添加缺失依赖**
   ```bash
   # 自动执行
   echo "openpyxl>=3.0.0" >> requirements.txt
   pip install openpyxl>=3.0.0
   ```

2. **自动移除未使用的导入**
   ```python
   # 自动删除未使用的导入语句
   # import requests  # 已自动移除
   ```

3. **自动更新到安全版本**
   ```bash
   # 自动更新requirements.txt
   sed -i 's/Pillow>=8.0.0/Pillow>=9.0.0/g' requirements.txt
   pip install --upgrade Pillow>=9.0.0
   ```

4. **生成依赖锁定文件**
   ```bash
   # 自动生成
   pip freeze > requirements.lock
   ```

### 交互式修复选项
```
🔧 依赖自动修复选项：

发现4个可修复问题：
✅ 添加缺失依赖 openpyxl>=3.0.0
✅ 移除未使用依赖 requests
✅ 升级不安全版本 Pillow 8.0.0 → 9.0.0  
⚠️ 版本冲突需要确认 numpy 1.20.0 → 1.21.0

[🚀 全部自动修复] [🔍 逐项确认] [📋 仅生成报告]

选择：全部自动修复

正在执行修复...
✅ 已添加 openpyxl>=3.0.0 到 requirements.txt
✅ 已从 requirements.txt 移除 requests  
✅ 已升级 Pillow 到 9.0.0
✅ 已升级 numpy 到 1.21.0
✅ 已重新安装所有依赖
✅ 已生成 requirements.lock

修复完成！所有依赖问题已解决。
```
```
