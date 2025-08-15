# MiniCRM 分支保护规则配置指南

## 概述

为了确保代码质量，需要在GitHub仓库中设置分支保护规则，要求所有代码质量检查通过后才能合并到主分支。

## 配置步骤

### 1. 访问仓库设置

1. 进入GitHub仓库页面
2. 点击 "Settings" 标签
3. 在左侧菜单中选择 "Branches"

### 2. 添加分支保护规则

#### 主分支保护 (main)

创建针对 `main` 分支的保护规则：

**基本设置:**
- Branch name pattern: `main`
- Restrict pushes that create files larger than 100 MB: ✅

**Pull Request要求:**
- Require a pull request before merging: ✅
  - Require approvals: ✅ (至少1个审批)
  - Dismiss stale PR approvals when new commits are pushed: ✅
  - Require review from code owners: ✅ (如果有CODEOWNERS文件)

**状态检查要求:**
- Require status checks to pass before merging: ✅
- Require branches to be up to date before merging: ✅

**必需的状态检查:**
- `代码质量检查 (code-quality)` - 来自code-quality.yml工作流
- `安全扫描 (security-scan)` - 来自code-quality.yml工作流
- `依赖安全检查 (dependency-check)` - 来自code-quality.yml工作流

**其他限制:**
- Restrict pushes that create files larger than 100 MB: ✅
- Do not allow bypassing the above settings: ✅
- Allow force pushes: ❌
- Allow deletions: ❌

#### 开发分支保护 (develop)

创建针对 `develop` 分支的保护规则：

**基本设置:**
- Branch name pattern: `develop`

**Pull Request要求:**
- Require a pull request before merging: ✅
- Require approvals: ✅ (至少1个审批)

**状态检查要求:**
- Require status checks to pass before merging: ✅
- 必需的状态检查同main分支

### 3. 创建CODEOWNERS文件

在仓库根目录创建 `.github/CODEOWNERS` 文件：

```
# MiniCRM 代码所有者配置

# 全局代码审查者
* @your-username

# 核心架构文件
src/minicrm/core/ @your-username @senior-dev
src/minicrm/models/ @your-username @senior-dev

# UI组件
src/minicrm/ui/ @ui-team-lead

# 业务逻辑
src/minicrm/services/ @business-logic-team

# 数据访问层
src/minicrm/data/ @database-team

# 配置文件
*.toml @your-username
*.ini @your-username
.github/ @your-username

# 文档
*.md @doc-team
docs/ @doc-team
```

### 4. 质量门禁配置

#### 自动化质量检查

工作流会自动运行以下检查：

1. **Ruff代码质量检查**
   - 代码风格检查
   - 代码格式化检查
   - 潜在问题检测

2. **MyPy类型检查**
   - 静态类型分析
   - 类型注解验证

3. **文件大小检查**
   - 基于文件类型的智能大小限制
   - 模块化架构验证

4. **Transfunctions使用检查**
   - 重复代码检测
   - 可复用函数使用验证

5. **安全扫描**
   - Bandit安全漏洞检测
   - 依赖安全检查

#### 质量标准

所有检查必须通过以下标准：

- **Ruff检查**: 无错误，允许少量警告
- **MyPy检查**: 无类型错误
- **文件大小**: 符合分层大小限制
- **Transfunctions**: 无重复实现
- **安全扫描**: 无高危漏洞

### 5. 紧急情况处理

#### 临时绕过保护

在紧急情况下，仓库管理员可以：

1. 临时禁用分支保护
2. 直接推送修复
3. 立即重新启用保护

#### 热修复流程

对于生产环境的紧急修复：

1. 创建 `hotfix/` 分支
2. 应用最小化修复
3. 运行快速质量检查
4. 直接合并到main（如果已配置hotfix例外）

### 6. 监控和报告

#### 质量指标监控

- 每日质量报告
- 趋势分析
- 团队质量评分

#### 失败处理

当质量检查失败时：

1. 自动在PR中评论详细报告
2. 阻止合并直到问题解决
3. 提供修复建议和指导

## 实施检查清单

- [ ] 设置main分支保护规则
- [ ] 设置develop分支保护规则
- [ ] 创建CODEOWNERS文件
- [ ] 配置必需的状态检查
- [ ] 测试质量门禁流程
- [ ] 培训团队成员
- [ ] 建立紧急处理流程

## 维护

定期检查和更新：

- 每月审查分支保护规则
- 根据团队反馈调整质量标准
- 更新CODEOWNERS文件
- 优化CI/CD工作流性能
