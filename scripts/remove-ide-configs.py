#!/usr/bin/env python3
"""
移除IDE配置文件脚本
从Git仓库中移除不应该提交的IDE配置文件夹
"""

import os
import subprocess
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 需要从Git历史中移除的IDE配置文件夹
IDE_FOLDERS_TO_REMOVE = [
    '.kiro/',
    '.codebuddy/',
    '.qoder/',
    '.trae/',
    '.mcp_cache/',
    '.rules/',
    '.vscode/',
]

def run_git_command(command, cwd=PROJECT_ROOT):
    """运行Git命令"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def remove_from_git_cache():
    """从Git缓存中移除IDE配置文件夹"""
    print("🗑️ 从Git缓存中移除IDE配置文件夹...")
    
    for folder in IDE_FOLDERS_TO_REMOVE:
        print(f"   移除: {folder}")
        success, stdout, stderr = run_git_command(f"git rm -r --cached {folder}")
        if success:
            print(f"   ✅ 成功移除: {folder}")
        else:
            if "did not match any files" in stderr:
                print(f"   ℹ️  文件夹不存在: {folder}")
            else:
                print(f"   ⚠️  移除失败: {folder} - {stderr}")

def update_gitignore():
    """确保.gitignore包含IDE配置文件夹"""
    gitignore_path = PROJECT_ROOT / '.gitignore'
    
    print("📝 检查.gitignore文件...")
    
    if not gitignore_path.exists():
        print("   ❌ .gitignore文件不存在")
        return False
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    missing_rules = []
    for folder in IDE_FOLDERS_TO_REMOVE:
        if folder not in content:
            missing_rules.append(folder)
    
    if missing_rules:
        print(f"   ⚠️  缺少规则: {missing_rules}")
        return False
    else:
        print("   ✅ .gitignore规则完整")
        return True

def check_local_folders():
    """检查本地是否存在IDE配置文件夹"""
    print("📁 检查本地IDE配置文件夹...")
    
    existing_folders = []
    for folder in IDE_FOLDERS_TO_REMOVE:
        folder_path = PROJECT_ROOT / folder.rstrip('/')
        if folder_path.exists():
            existing_folders.append(folder)
    
    if existing_folders:
        print("   📂 本地存在的IDE配置文件夹:")
        for folder in existing_folders:
            print(f"      - {folder}")
        print("   💡 这些文件夹将保留在本地，但不会被提交到Git")
    else:
        print("   ℹ️  本地没有IDE配置文件夹")

def main():
    """主函数"""
    print("🔧 IDE配置文件清理工具")
    print("=" * 50)
    
    # 检查是否在Git仓库中
    success, _, _ = run_git_command("git rev-parse --git-dir")
    if not success:
        print("❌ 当前目录不是Git仓库")
        return 1
    
    # 从Git缓存中移除IDE配置文件夹
    remove_from_git_cache()
    
    # 检查.gitignore
    update_gitignore()
    
    # 检查本地文件夹
    check_local_folders()
    
    print("\n✅ IDE配置文件清理完成！")
    print("\n💡 下一步操作:")
    print("   1. 提交更改: git add .gitignore && git commit -m 'chore: 移除IDE配置文件，保留在本地'")
    print("   2. 推送到远程: git push origin main")
    print("   3. IDE配置文件夹现在只会保留在本地，不会被提交到Git")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())