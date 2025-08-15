#!/usr/bin/env python3
"""
MiniCRM 分支保护规则自动化设置脚本

使用GitHub API自动配置分支保护规则，确保代码质量门禁生效。
"""

import os
import sys
from typing import Any


try:
    import requests  # type: ignore[import-untyped]
except ImportError:
    print("❌ 需要安装requests库: pip install requests")
    sys.exit(1)


class GitHubBranchProtection:
    """GitHub分支保护规则管理器"""

    def __init__(self, token: str, owner: str, repo: str):
        """
        初始化GitHub API客户端

        Args:
            token: GitHub个人访问令牌
            owner: 仓库所有者
            repo: 仓库名称
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

    def create_branch_protection(
        self, branch: str, protection_config: dict[str, Any]
    ) -> bool:
        """
        创建分支保护规则

        Args:
            branch: 分支名称
            protection_config: 保护规则配置

        Returns:
            是否创建成功
        """
        url = (
            f"{self.base_url}/repos/{self.owner}/{self.repo}"
            f"/branches/{branch}/protection"
        )

        try:
            response = requests.put(url, headers=self.headers, json=protection_config)

            if response.status_code == 200:
                print(f"✅ 成功为分支 '{branch}' 设置保护规则")
                return True
            else:
                print(f"❌ 设置分支 '{branch}' 保护规则失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False

        except Exception as e:
            print(f"❌ 设置分支保护规则时出错: {e}")
            return False

    def get_main_branch_protection(self) -> dict[str, Any]:
        """获取主分支保护规则配置"""
        return {
            "required_status_checks": {
                "strict": True,
                "contexts": [
                    "代码质量检查 (code-quality)",
                    "安全扫描 (security-scan)",
                    "依赖安全检查 (dependency-check)",
                ],
            },
            "enforce_admins": True,
            "required_pull_request_reviews": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews": True,
                "require_code_owner_reviews": True,
                "require_last_push_approval": False,
            },
            "restrictions": None,
            "allow_force_pushes": False,
            "allow_deletions": False,
            "block_creations": False,
            "required_conversation_resolution": True,
        }

    def get_develop_branch_protection(self) -> dict[str, Any]:
        """获取开发分支保护规则配置"""
        return {
            "required_status_checks": {
                "strict": True,
                "contexts": [
                    "代码质量检查 (code-quality)",
                    "安全扫描 (security-scan)",
                    "依赖安全检查 (dependency-check)",
                ],
            },
            "enforce_admins": False,
            "required_pull_request_reviews": {
                "required_approving_review_count": 1,
                "dismiss_stale_reviews": True,
                "require_code_owner_reviews": False,
                "require_last_push_approval": False,
            },
            "restrictions": None,
            "allow_force_pushes": False,
            "allow_deletions": False,
            "block_creations": False,
            "required_conversation_resolution": True,
        }

    def setup_all_protections(self) -> bool:
        """设置所有分支保护规则"""
        success = True

        # 设置主分支保护
        main_config = self.get_main_branch_protection()
        if not self.create_branch_protection("main", main_config):
            success = False

        # 设置开发分支保护
        develop_config = self.get_develop_branch_protection()
        if not self.create_branch_protection("develop", develop_config):
            success = False

        return success

    def verify_protection(self, branch: str) -> bool:
        """验证分支保护规则是否生效"""
        url = (
            f"{self.base_url}/repos/{self.owner}/{self.repo}"
            f"/branches/{branch}/protection"
        )

        try:
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                protection = response.json()
                print(f"✅ 分支 '{branch}' 保护规则已生效")

                # 检查关键配置
                if protection.get("required_status_checks"):
                    contexts = protection["required_status_checks"].get("contexts", [])
                    print(f"   必需状态检查: {len(contexts)} 个")
                    for context in contexts:
                        print(f"     - {context}")

                if protection.get("required_pull_request_reviews"):
                    reviews = protection["required_pull_request_reviews"]
                    count = reviews.get("required_approving_review_count", 0)
                    print(f"   必需审批数: {count}")

                return True
            else:
                print(f"❌ 分支 '{branch}' 没有保护规则")
                return False

        except Exception as e:
            print(f"❌ 验证分支保护规则时出错: {e}")
            return False


def create_codeowners_file():
    """创建CODEOWNERS文件"""
    codeowners_content = """# MiniCRM 代码所有者配置

# 全局代码审查者
* @minicrm-maintainer

# 核心架构文件
src/minicrm/core/ @minicrm-maintainer @senior-dev
src/minicrm/models/ @minicrm-maintainer @senior-dev

# UI组件
src/minicrm/ui/ @ui-team-lead

# 业务逻辑
src/minicrm/services/ @business-logic-team

# 数据访问层
src/minicrm/data/ @database-team

# Transfunctions库
src/transfunctions/ @minicrm-maintainer

# 配置文件
*.toml @minicrm-maintainer
*.ini @minicrm-maintainer
.github/ @minicrm-maintainer
.pre-commit-config.yaml @minicrm-maintainer

# 脚本文件
scripts/ @minicrm-maintainer

# 文档
*.md @doc-team
docs/ @doc-team

# 测试文件
tests/ @qa-team
"""

    os.makedirs(".github", exist_ok=True)
    with open(".github/CODEOWNERS", "w", encoding="utf-8") as f:
        f.write(codeowners_content)

    print("✅ 已创建 .github/CODEOWNERS 文件")


def main():
    """主函数"""
    print("🔧 MiniCRM 分支保护规则设置工具")
    print("=" * 50)

    # 检查环境变量
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ 请设置GITHUB_TOKEN环境变量")
        print("   获取令牌: https://github.com/settings/tokens")
        print("   需要权限: repo (完整仓库访问)")
        sys.exit(1)

    # 获取仓库信息
    owner = input("请输入仓库所有者 (例: your-username): ").strip()
    if not owner:
        print("❌ 仓库所有者不能为空")
        sys.exit(1)

    repo = input("请输入仓库名称 (例: minicrm): ").strip()
    if not repo:
        print("❌ 仓库名称不能为空")
        sys.exit(1)

    # 创建GitHub客户端
    github = GitHubBranchProtection(token, owner, repo)

    print(f"\n🚀 开始为仓库 {owner}/{repo} 设置分支保护规则...")

    # 创建CODEOWNERS文件
    create_codeowners_file()

    # 设置分支保护规则
    if github.setup_all_protections():
        print("\n✅ 所有分支保护规则设置完成")

        # 验证设置
        print("\n🔍 验证分支保护规则...")
        github.verify_protection("main")
        github.verify_protection("develop")

        print("\n📋 后续步骤:")
        print("1. 提交并推送 .github/CODEOWNERS 文件")
        print("2. 在GitHub仓库设置中确认分支保护规则")
        print("3. 测试PR流程确保质量门禁生效")
        print("4. 培训团队成员了解新的工作流程")

    else:
        print("\n❌ 部分分支保护规则设置失败")
        print("请检查GitHub令牌权限和仓库访问权限")
        sys.exit(1)


if __name__ == "__main__":
    main()
