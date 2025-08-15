#!/usr/bin/env python3
"""
Python统一自动修复Hook模式切换脚本

使用方法:
python switch_fixer_mode.py [模式]

模式选项:
- fast: 快速模式
- smart: 智能模式 (默认)
- token-optimized: 节约模式
"""

import json
import os
import sys
from pathlib import Path

# 预定义的配置模板
MODES = {
    "fast": {
        "fixMode": "fast",
        "autoApplySimpleFixes": True,
        "maxTokens": 200,
        "interactiveMode": False
    },
    "smart": {
        "fixMode": "smart",
        "autoApplySimpleFixes": True,
        "maxTokens": 500,
        "interactiveMode": True
    },
    "token-optimized": {
        "fixMode": "token-optimized",
        "autoApplySimpleFixes": True,
        "maxTokens": 100,
        "interactiveMode": False
    }
}


def get_hook_file_path():
    """获取hook文件路径"""
    script_dir = Path(__file__).parent
    hook_file = script_dir.parent / "unified-python-fixer.kiro.hook"
    return hook_file


def load_hook_config():
    """加载当前hook配置"""
    hook_file = get_hook_file_path()

    if not hook_file.exists():
        print(f"❌ Hook文件不存在: {hook_file}")
        return None

    try:
        with open(hook_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 读取hook配置失败: {e}")
        return None


def save_hook_config(config):
    """保存hook配置"""
    hook_file = get_hook_file_path()

    try:
        with open(hook_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ 保存hook配置失败: {e}")
        return False


def switch_mode(mode):
    """切换修复模式"""
    if mode not in MODES:
        print(f"❌ 无效的模式: {mode}")
        print(f"可用模式: {', '.join(MODES.keys())}")
        return False

    # 加载当前配置
    config = load_hook_config()
    if config is None:
        return False

    # 更新配置
    old_mode = config.get("config", {}).get("fixMode", "unknown")
    config["config"] = MODES[mode]

    # 保存配置
    if save_hook_config(config):
        print(f"✅ 修复模式已切换: {old_mode} → {mode}")
        print(f"📋 新配置:")
        for key, value in MODES[mode].items():
            print(f"   {key}: {value}")
        return True

    return False


def show_current_mode():
    """显示当前模式"""
    config = load_hook_config()
    if config is None:
        return

    current_config = config.get("config", {})
    current_mode = current_config.get("fixMode", "unknown")

    print(f"🔧 当前修复模式: {current_mode}")
    print(f"📋 当前配置:")
    for key, value in current_config.items():
        print(f"   {key}: {value}")


def show_help():
    """显示帮助信息"""
    print("🔧 Python统一自动修复Hook模式切换工具")
    print()
    print("使用方法:")
    print("  python switch_fixer_mode.py [模式]")
    print("  python switch_fixer_mode.py status    # 查看当前模式")
    print("  python switch_fixer_mode.py help      # 显示帮助")
    print()
    print("可用模式:")
    print("  fast             快速模式 - 速度优先，基础修复")
    print("  smart            智能模式 - 质量优先，全面分析 (默认)")
    print("  token-optimized  节约模式 - 成本优先，最小token消耗")
    print()
    print("模式特点:")
    for mode, config in MODES.items():
        print(f"  {mode}:")
        print(f"    Token限制: {config['maxTokens']}")
        print(f"    交互模式: {'开启' if config['interactiveMode'] else '关闭'}")
        print(f"    自动修复: {'开启' if config['autoApplySimpleFixes'] else '关闭'}")
        print()


def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_current_mode()
        print()
        print("💡 使用 'python switch_fixer_mode.py help' 查看帮助")
        return

    command = sys.argv[1].lower()

    if command == "help":
        show_help()
    elif command == "status":
        show_current_mode()
    elif command in MODES:
        switch_mode(command)
    else:
        print(f"❌ 未知命令: {command}")
        print("💡 使用 'python switch_fixer_mode.py help' 查看帮助")


if __name__ == "__main__":
    main()
