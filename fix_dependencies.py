#!/usr/bin/env python3
"""
依赖修复脚本
提供交互式的依赖问题修复选项
"""

import subprocess
import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

def run_command(command: str, description: str) -> bool:
    """运行命令并显示结果"""
    print(f"🔧 {description}...")
    print(f"执行: {command}")
    
    try:
        result = subprocess.run(
            command.split(),
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {description}成功")
            if result.stdout.strip():
                print(f"输出: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description}失败")
            if result.stderr.strip():
                print(f"错误: {result.stderr.strip()}")
            return False
            
    except FileNotFoundError:
        print(f"❌ 命令未找到: {command.split()[0]}")
        return False
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        return False

def check_uv_installed() -> bool:
    """检查UV是否已安装"""
    try:
        result = subprocess.run(['uv', '--version'], capture_output=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_uv() -> bool:
    """安装UV包管理器"""
    print("📦 UV包管理器未安装，正在安装...")
    
    # 尝试使用pip安装
    success = run_command("pip install uv", "安装UV")
    
    if not success:
        print("💡 请手动安装UV:")
        print("   macOS: brew install uv")
        print("   或访问: https://docs.astral.sh/uv/getting-started/installation/")
        return False
    
    return True

def sync_dependencies() -> bool:
    """同步依赖"""
    return run_command("uv sync", "同步项目依赖")

def install_full_dependencies() -> bool:
    """安装完整功能依赖"""
    return run_command("uv add minicrm[full]", "安装完整功能依赖")

def install_dev_dependencies() -> bool:
    """安装开发依赖"""
    return run_command("uv add --dev ruff mypy black pytest", "安装开发依赖")

def run_code_quality_checks() -> bool:
    """运行代码质量检查"""
    print("🔍 运行代码质量检查...")
    
    checks = [
        ("uv run ruff check src/", "Ruff代码检查"),
        ("uv run mypy src/minicrm", "MyPy类型检查"),
    ]
    
    all_passed = True
    for command, description in checks:
        if not run_command(command, description):
            all_passed = False
    
    return all_passed

def show_menu():
    """显示修复选项菜单"""
    print("\n" + "="*50)
    print("🔧 MiniCRM 依赖修复工具")
    print("="*50)
    print("1. 检查并安装UV包管理器")
    print("2. 同步项目依赖 (uv sync)")
    print("3. 安装完整功能依赖 (minicrm[full])")
    print("4. 安装开发依赖 (dev tools)")
    print("5. 运行代码质量检查")
    print("6. 执行完整修复流程")
    print("7. 显示项目状态")
    print("0. 退出")
    print("="*50)

def show_project_status():
    """显示项目状态"""
    print("\n📊 项目状态:")
    print("-" * 30)
    
    # 检查UV
    if check_uv_installed():
        print("✅ UV包管理器: 已安装")
    else:
        print("❌ UV包管理器: 未安装")
    
    # 检查pyproject.toml
    if (PROJECT_ROOT / "pyproject.toml").exists():
        print("✅ pyproject.toml: 存在")
    else:
        print("❌ pyproject.toml: 不存在")
    
    # 检查uv.lock
    if (PROJECT_ROOT / "uv.lock").exists():
        print("✅ uv.lock: 存在")
    else:
        print("⚠️ uv.lock: 不存在 (需要运行 uv sync)")
    
    # 检查src目录
    if (PROJECT_ROOT / "src").exists():
        print("✅ src目录: 存在")
    else:
        print("❌ src目录: 不存在")

def full_repair_workflow():
    """执行完整修复流程"""
    print("\n🚀 开始完整修复流程...")
    
    steps = [
        (lambda: check_uv_installed() or install_uv(), "检查/安装UV"),
        (sync_dependencies, "同步依赖"),
        (install_full_dependencies, "安装完整功能"),
        (install_dev_dependencies, "安装开发工具"),
        (run_code_quality_checks, "代码质量检查")
    ]
    
    for i, (step_func, step_name) in enumerate(steps, 1):
        print(f"\n步骤 {i}/{len(steps)}: {step_name}")
        if not step_func():
            print(f"❌ 步骤 {i} 失败，修复流程中断")
            return False
    
    print("\n🎉 完整修复流程执行完成！")
    return True

def main():
    """主函数"""
    while True:
        show_menu()
        
        try:
            choice = input("\n请选择操作 (0-7): ").strip()
            
            if choice == "0":
                print("👋 再见！")
                break
            elif choice == "1":
                if check_uv_installed():
                    print("✅ UV已安装")
                else:
                    install_uv()
            elif choice == "2":
                sync_dependencies()
            elif choice == "3":
                install_full_dependencies()
            elif choice == "4":
                install_dev_dependencies()
            elif choice == "5":
                run_code_quality_checks()
            elif choice == "6":
                full_repair_workflow()
            elif choice == "7":
                show_project_status()
            else:
                print("❌ 无效选择，请输入0-7")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")
        
        input("\n按Enter键继续...")

if __name__ == "__main__":
    main()