# MiniCRM部署指南

## 概述

本指南详细说明了如何在不同平台上部署MiniCRM应用程序，包括构建、打包、分发和安装的完整流程。

## 部署架构

### 部署模式选择

#### 1. 单文件部署（推荐生产环境）
- **适用场景**: 最终用户部署、简化分发
- **优点**: 部署简单、无依赖问题
- **缺点**: 文件较大、启动稍慢

#### 2. 目录部署（推荐开发环境）
- **适用场景**: 开发测试、企业内部部署
- **优点**: 启动快速、便于调试
- **缺点**: 文件较多、需要完整目录

#### 3. 源码部署（仅开发环境）
- **适用场景**: 开发调试、定制化需求
- **优点**: 灵活性高、便于修改
- **缺点**: 需要Python环境和依赖

## 构建环境准备

### 开发环境要求

#### 基础要求
```bash
# Python版本
Python 3.9 或更高版本

# 必需的系统包
- tkinter (通常随Python安装)
- sqlite3 (通常随Python安装)

# 构建工具
- PyInstaller 5.0+
- uv 或 pip (包管理)
```

#### 平台特定要求

**Windows**:
```cmd
# 安装Visual C++ Redistributable
# 下载并安装Microsoft Visual C++ 2019 Redistributable

# 安装Windows SDK (可选，用于代码签名)
# 下载并安装Windows 10/11 SDK
```

**macOS**:
```bash
# 安装Xcode Command Line Tools
xcode-select --install

# 安装Homebrew (推荐)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装Python (如果使用Homebrew)
brew install python@3.11
```

**Linux**:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv python3-tk build-essential

# CentOS/RHEL
sudo yum install python3 python3-pip python3-tkinter gcc gcc-c++ make

# Fedora
sudo dnf install python3 python3-pip python3-tkinter gcc gcc-c++ make

# Arch Linux
sudo pacman -S python python-pip tk gcc make
```

### 项目环境设置

#### 1. 克隆项目
```bash
git clone https://github.com/your-org/minicrm.git
cd minicrm
```

#### 2. 创建虚拟环境
```bash
# 使用venv
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

#### 3. 安装依赖
```bash
# 使用uv (推荐)
pip install uv
uv pip install -r requirements.txt

# 或使用pip
pip install -r requirements.txt

# 安装构建依赖
pip install pyinstaller
```

#### 4. 验证环境
```bash
# 运行测试
python -m pytest tests/

# 运行应用程序
python src/minicrm/main.py
```

## 构建流程

### 自动化构建

#### 使用构建脚本

**Windows**:
```cmd
# 运行Windows构建脚本
build\build_windows.bat

# 或手动构建
cd build
python build.py
```

**macOS**:
```bash
# 运行macOS构建脚本
chmod +x build/build_macos.sh
./build/build_macos.sh

# 或手动构建
cd build
python build.py
```

**Linux**:
```bash
# 运行Linux构建脚本
chmod +x build/build_linux.sh
./build/build_linux.sh

# 或手动构建
cd build
python build.py
```

### 手动构建

#### 1. 准备构建环境
```bash
# 确保在项目根目录
cd /path/to/minicrm

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

# 创建构建目录
mkdir -p build dist
```

#### 2. 配置构建参数
```python
# 编辑 build/build_config.py
class BuildConfig:
    def __init__(self):
        # 自定义构建参数
        self.app_name = "MiniCRM"
        self.version = "1.0.0"
        # ... 其他配置
```

#### 3. 执行构建
```bash
# 单文件构建
python build/build_config.py --onefile

# 目录构建
python build/build_config.py --onedir

# 带控制台的构建（调试用）
python build/build_config.py --console
```

### 构建输出

构建完成后，输出文件位于 `dist/` 目录：

```
dist/
├── MiniCRM-v1.0.0-windows-x86_64.exe    # Windows单文件
├── MiniCRM-v1.0.0-darwin-x86_64         # macOS单文件
├── MiniCRM-v1.0.0-linux-x86_64          # Linux单文件
└── MiniCRM-v1.0.0-windows-x86_64/       # Windows目录版本
    ├── MiniCRM.exe
    ├── _internal/
    └── ...
```

## 平台特定部署

### Windows部署

#### 1. 单文件部署
```cmd
# 构建单文件版本
build\build_windows.bat

# 输出文件
dist\MiniCRM-v1.0.0-windows-x86_64.exe
```

#### 2. 创建安装程序（可选）
```cmd
# 使用NSIS创建安装程序
# 1. 安装NSIS
# 2. 创建安装脚本 installer.nsi
# 3. 编译安装程序
makensis installer.nsi
```

#### 3. 代码签名（可选）
```cmd
# 使用signtool进行代码签名
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\MiniCRM.exe
```

#### 4. 部署验证
```cmd
# 在目标系统上测试
dist\MiniCRM-v1.0.0-windows-x86_64.exe

# 检查依赖
# 确保目标系统有Visual C++ Redistributable
```

### macOS部署

#### 1. 单文件部署
```bash
# 构建单文件版本
./build/build_macos.sh

# 输出文件
dist/MiniCRM-v1.0.0-darwin-x86_64
```

#### 2. 创建应用程序包
```bash
# 创建.app包结构
mkdir -p "dist/MiniCRM.app/Contents/MacOS"
mkdir -p "dist/MiniCRM.app/Contents/Resources"

# 复制可执行文件
cp "dist/MiniCRM-v1.0.0-darwin-x86_64" "dist/MiniCRM.app/Contents/MacOS/MiniCRM"

# 创建Info.plist
cat > "dist/MiniCRM.app/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>MiniCRM</string>
    <key>CFBundleIdentifier</key>
    <string>com.minicrm.app</string>
    <key>CFBundleName</key>
    <string>MiniCRM</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
</dict>
</plist>
EOF
```

#### 3. 代码签名和公证
```bash
# 代码签名
codesign --force --deep --sign "Developer ID Application: Your Name" "dist/MiniCRM.app"

# 创建DMG
hdiutil create -volname "MiniCRM" -srcfolder "dist/MiniCRM.app" -ov -format UDZO "dist/MiniCRM-1.0.0.dmg"

# 公证DMG (需要Apple Developer账号)
xcrun notarytool submit "dist/MiniCRM-1.0.0.dmg" --keychain-profile "notarytool-profile" --wait
```

#### 4. 部署验证
```bash
# 测试应用程序
open "dist/MiniCRM.app"

# 检查签名
codesign -v "dist/MiniCRM.app"
spctl -a -v "dist/MiniCRM.app"
```

### Linux部署

#### 1. 单文件部署
```bash
# 构建单文件版本
./build/build_linux.sh

# 输出文件
dist/MiniCRM-v1.0.0-linux-x86_64
```

#### 2. 创建AppImage
```bash
# 下载AppImageTool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# 创建AppDir结构
mkdir -p "dist/MiniCRM.AppDir/usr/bin"
mkdir -p "dist/MiniCRM.AppDir/usr/share/applications"
mkdir -p "dist/MiniCRM.AppDir/usr/share/icons/hicolor/256x256/apps"

# 复制文件
cp "dist/MiniCRM-v1.0.0-linux-x86_64" "dist/MiniCRM.AppDir/usr/bin/minicrm"
cp "src/minicrm/resources/icons/app_icon.png" "dist/MiniCRM.AppDir/usr/share/icons/hicolor/256x256/apps/minicrm.png"

# 创建desktop文件
cat > "dist/MiniCRM.AppDir/usr/share/applications/minicrm.desktop" << EOF
[Desktop Entry]
Type=Application
Name=MiniCRM
Comment=板材行业客户关系管理系统
Exec=minicrm
Icon=minicrm
Categories=Office;
EOF

# 创建AppRun
cat > "dist/MiniCRM.AppDir/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "${HERE}/usr/bin/minicrm" "$@"
EOF
chmod +x "dist/MiniCRM.AppDir/AppRun"

# 创建符号链接
ln -sf "usr/share/applications/minicrm.desktop" "dist/MiniCRM.AppDir/minicrm.desktop"
ln -sf "usr/share/icons/hicolor/256x256/apps/minicrm.png" "dist/MiniCRM.AppDir/minicrm.png"

# 生成AppImage
./appimagetool-x86_64.AppImage "dist/MiniCRM.AppDir" "dist/MiniCRM-x86_64.AppImage"
```

#### 3. 创建DEB包
```bash
# 创建包结构
mkdir -p "dist/minicrm_1.0.0_amd64/DEBIAN"
mkdir -p "dist/minicrm_1.0.0_amd64/usr/bin"
mkdir -p "dist/minicrm_1.0.0_amd64/usr/share/applications"
mkdir -p "dist/minicrm_1.0.0_amd64/usr/share/icons/hicolor/256x256/apps"

# 复制文件
cp "dist/MiniCRM-v1.0.0-linux-x86_64" "dist/minicrm_1.0.0_amd64/usr/bin/minicrm"
cp "src/minicrm/resources/icons/app_icon.png" "dist/minicrm_1.0.0_amd64/usr/share/icons/hicolor/256x256/apps/minicrm.png"

# 创建control文件
cat > "dist/minicrm_1.0.0_amd64/DEBIAN/control" << EOF
Package: minicrm
Version: 1.0.0
Section: office
Priority: optional
Architecture: amd64
Depends: python3-tk
Maintainer: MiniCRM Team <support@minicrm.com>
Description: 板材行业客户关系管理系统
 MiniCRM是专为板材行业设计的客户关系管理系统，
 提供客户管理、供应商管理、报价管理等功能。
EOF

# 创建desktop文件
cp "dist/MiniCRM.AppDir/usr/share/applications/minicrm.desktop" "dist/minicrm_1.0.0_amd64/usr/share/applications/"

# 构建DEB包
dpkg-deb --build "dist/minicrm_1.0.0_amd64"
```

#### 4. 部署验证
```bash
# 测试可执行文件
./dist/MiniCRM-v1.0.0-linux-x86_64

# 测试AppImage
./dist/MiniCRM-x86_64.AppImage

# 测试DEB包安装
sudo dpkg -i dist/minicrm_1.0.0_amd64.deb
```

## 质量保证

### 构建前测试

#### 1. 运行完整测试套件
```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行部署测试
python tests/test_deployment/run_all_deployment_tests.py

# 检查代码质量
ruff check src/
mypy src/
```

#### 2. 性能基准测试
```bash
# 运行性能测试
python tests/test_deployment/test_performance_benchmarks.py

# 检查内存使用
python -m memory_profiler src/minicrm/main.py
```

#### 3. 跨平台兼容性测试
```bash
# 运行兼容性测试
python tests/test_deployment/test_cross_platform_compatibility.py
```

### 构建后验证

#### 1. 功能验证
```bash
# 启动应用程序
./dist/MiniCRM-*

# 验证基本功能
# - 应用程序正常启动
# - 数据库连接正常
# - UI界面显示正确
# - 基本CRUD操作正常
```

#### 2. 性能验证
```bash
# 测试启动时间
time ./dist/MiniCRM-*

# 测试内存使用
# 使用系统监控工具观察内存使用情况
```

#### 3. 安全验证
```bash
# 检查文件权限
ls -la dist/

# 扫描恶意软件（Windows）
# 使用Windows Defender或其他杀毒软件扫描

# 检查依赖安全性
pip-audit
```

## 分发策略

### 分发渠道

#### 1. 官方网站下载
```
https://minicrm.com/download/
├── Windows版本
├── macOS版本
└── Linux版本
```

#### 2. 应用商店分发
- **Microsoft Store** (Windows)
- **Mac App Store** (macOS)
- **Snap Store** (Linux)
- **Flathub** (Linux)

#### 3. 企业内部分发
```bash
# 创建内部分发服务器
# 1. 设置HTTP服务器
# 2. 上传构建文件
# 3. 提供下载链接
# 4. 配置自动更新检查
```

### 版本管理

#### 1. 版本号规范
```
主版本.次版本.修订版本[-预发布标识]
例如: 1.0.0, 1.1.0, 1.1.1, 2.0.0-beta.1
```

#### 2. 发布流程
```bash
# 1. 更新版本号
# 编辑 src/minicrm/core/constants.py
APP_VERSION = "1.1.0"

# 2. 更新变更日志
# 编辑 CHANGELOG.md

# 3. 创建Git标签
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0

# 4. 构建发布版本
./build/build_all_platforms.sh

# 5. 上传到分发渠道
```

### 自动更新

#### 1. 更新检查机制
```python
class UpdateChecker:
    def __init__(self):
        self.update_url = "https://api.minicrm.com/updates"
        self.current_version = APP_VERSION

    def check_for_updates(self):
        # 检查是否有新版本
        pass

    def download_update(self, update_info):
        # 下载更新文件
        pass

    def apply_update(self, update_file):
        # 应用更新
        pass
```

#### 2. 增量更新
```python
class IncrementalUpdater:
    def create_patch(self, old_version, new_version):
        # 创建增量补丁
        pass

    def apply_patch(self, patch_file):
        # 应用增量补丁
        pass
```

## 监控和维护

### 部署监控

#### 1. 应用程序监控
```python
# 集成应用程序监控
class DeploymentMonitor:
    def __init__(self):
        self.metrics = {}

    def track_startup_time(self):
        # 跟踪启动时间
        pass

    def track_crash_reports(self):
        # 跟踪崩溃报告
        pass

    def send_telemetry(self):
        # 发送遥测数据
        pass
```

#### 2. 用户反馈收集
```python
class FeedbackCollector:
    def collect_crash_report(self, exception):
        # 收集崩溃报告
        pass

    def collect_performance_data(self):
        # 收集性能数据
        pass

    def collect_user_feedback(self, feedback):
        # 收集用户反馈
        pass
```

### 维护任务

#### 1. 定期维护
```bash
# 每周任务
- 检查构建状态
- 更新依赖包
- 运行安全扫描

# 每月任务
- 分析用户反馈
- 更新文档
- 性能优化

# 每季度任务
- 主要版本发布
- 架构评估
- 安全审计
```

#### 2. 应急响应
```bash
# 紧急修复流程
1. 识别问题
2. 创建热修复分支
3. 开发和测试修复
4. 快速构建和部署
5. 通知用户更新
```

## 故障排除

### 常见构建问题

#### 1. PyInstaller问题
```bash
# 问题: 模块导入失败
# 解决: 添加隐藏导入
--hidden-import=module_name

# 问题: 资源文件缺失
# 解决: 添加数据文件
--add-data="src_path;dest_path"

# 问题: 构建文件过大
# 解决: 排除不必要的模块
--exclude-module=unused_module
```

#### 2. 平台特定问题
```bash
# Windows: DLL缺失
# 解决: 安装Visual C++ Redistributable

# macOS: 代码签名失败
# 解决: 检查开发者证书和配置

# Linux: 依赖库缺失
# 解决: 安装系统依赖包
```

### 部署问题诊断

#### 1. 启动失败
```bash
# 检查系统要求
# 检查文件权限
# 查看错误日志
# 验证依赖库
```

#### 2. 功能异常
```bash
# 检查数据库文件
# 验证配置文件
# 查看应用程序日志
# 测试网络连接
```

#### 3. 性能问题
```bash
# 监控CPU使用率
# 检查内存使用
# 分析磁盘I/O
# 优化数据库查询
```

## 最佳实践

### 构建最佳实践

1. **自动化构建**: 使用CI/CD流水线自动化构建过程
2. **版本控制**: 严格的版本号管理和发布流程
3. **质量保证**: 完整的测试覆盖和代码质量检查
4. **安全扫描**: 定期进行安全漏洞扫描
5. **性能监控**: 持续监控应用程序性能指标

### 部署最佳实践

1. **渐进式部署**: 先小范围测试，再全面推广
2. **回滚计划**: 准备快速回滚机制
3. **监控告警**: 设置完善的监控和告警系统
4. **文档维护**: 保持部署文档的及时更新
5. **用户培训**: 提供充分的用户培训和支持

### 维护最佳实践

1. **定期更新**: 及时更新依赖包和安全补丁
2. **备份策略**: 完善的数据备份和恢复策略
3. **容量规划**: 根据使用情况进行容量规划
4. **用户反馈**: 建立有效的用户反馈收集机制
5. **持续改进**: 基于监控数据持续优化系统

---

**文档版本**: v1.0.0
**最后更新**: 2024年1月
**维护者**: MiniCRM开发团队
