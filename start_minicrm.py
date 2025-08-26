#!/usr/bin/env python3
"""MiniCRM 启动脚本

这个脚本提供了一个简单的方法来启动MiniCRM应用程序，
会自动检测环境并选择合适的启动方式。

使用方法：
    python start_minicrm.py
"""

import os
import sys
import subprocess
from pathlib import Path


def print_banner():
    """打印启动横幅"""
    print("=" * 60)
    print("🏢 MiniCRM 客户关系管理系统")
    print("💼 基于 Python + tkinter/ttk")
    print("🚀 正在启动应用程序...")
    print("=" * 60)
    print()


def check_uv_available():
    """检查UV包管理器是否可用"""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_virtual_env():
    """检查虚拟环境是否存在"""
    venv_path = Path(".venv")
    return venv_path.exists() and venv_path.is_dir()


def run_with_uv():
    """使用UV运行应用程序"""
    print("🔧 使用 UV 包管理器启动...")
    try:
        subprocess.run(["uv", "run", "minicrm"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ UV启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在退出...")
        return True
    return True


def run_with_python_module():
    """使用Python模块方式运行"""
    print("🐍 使用 Python 模块启动...")
    try:
        subprocess.run([sys.executable, "-m", "minicrm"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Python模块启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在退出...")
        return True
    return True


def run_with_virtual_env():
    """使用虚拟环境运行"""
    print("🏠 使用虚拟环境启动...")
    
    # 确定虚拟环境中的Python解释器路径
    if sys.platform == "win32":
        python_path = Path(".venv/Scripts/python.exe")
    else:
        python_path = Path(".venv/bin/python")
    
    if not python_path.exists():
        print(f"❌ 虚拟环境Python解释器未找到: {python_path}")
        return False
    
    try:
        subprocess.run([str(python_path), "-m", "minicrm"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 虚拟环境启动失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在退出...")
        return True
    return True


def run_direct():
    """直接运行main.py"""
    print("📁 直接运行主程序文件...")
    main_py = Path("src/minicrm/main.py")
    
    if not main_py.exists():
        print(f"❌ 主程序文件未找到: {main_py}")
        return False
    
    try:
        subprocess.run([sys.executable, str(main_py)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 直接运行失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在退出...")
        return True
    return True


def main():
    """主函数"""
    # 切换到项目根目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print_banner()
    
    # 按优先级尝试不同的启动方式
    print("🔍 检测运行环境...")
    
    # 1. 首先尝试使用UV（推荐）
    if check_uv_available():
        print("✅ 检测到 UV 包管理器")
        if run_with_uv():
            return
    
    # 2. 尝试使用虚拟环境
    if check_virtual_env():
        print("✅ 检测到虚拟环境")
        if run_with_virtual_env():
            return
    
    # 3. 尝试使用Python模块方式
    print("💻 尝试使用 Python 模块方式...")
    if run_with_python_module():
        return
    
    # 4. 最后尝试直接运行
    print("📄 最后尝试直接运行主程序文件...")
    if run_direct():
        return
    
    # 所有方法都失败了
    print("\n❌ 所有启动方法都失败了！")
    print("\n🔧 请检查以下内容：")
    print("1. 确保已安装Python 3.9+")
    print("2. 确保已安装项目依赖（运行 'uv sync' 或 'pip install -e .'）")
    print("3. 确保tkinter已正确安装（通常随Python内置）")
    print("4. 检查项目路径是否正确")
    print("\n📖 更多信息请查看 README.md 文件")


if __name__ == "__main__":
    main()