#!/usr/bin/env python3
"""
MiniCRM Agent Hooks 管理脚本

这个脚本帮助管理和配置MiniCRM项目的Agent Hooks。
"""

import json
from pathlib import Path
from typing import Dict, Any


class HooksManager:
    """Agent Hooks管理器"""

    def __init__(self, hooks_dir: str = ".kiro/hooks"):
        self.hooks_dir = Path(hooks_dir)
        self.config_file = self.hooks_dir / "hooks-config.json"

    def load_config(self) -> Dict[str, Any]:
        """加载hooks配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"hooks": [], "settings": {}}

    def save_config(self, config: Dict[str, Any]) -> None:
        """保存hooks配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def list_hooks(self) -> None:
        """列出所有hooks"""
        config = self.load_config()
        print("📋 MiniCRM Agent Hooks 列表:")
        print("=" * 50)

        for hook in config.get("hooks", []):
            status = "✅ 启用" if hook.get("enabled", False) else "❌ 禁用"
            print(f"{hook['id']}: {hook['name']}")
            print(f"   状态: {status}")
            print(f"   描述: {hook['description']}")
            print(f"   优先级: {hook.get('priority', 'N/A')}")
            print(f"   触发条件: {len(hook.get('triggers', []))} 个")
            print()

    def enable_hook(self, hook_id: str) -> None:
        """启用指定的hook"""
        config = self.load_config()

        for hook in config.get("hooks", []):
            if hook["id"] == hook_id:
                hook["enabled"] = True
                self.save_config(config)
                print(f"✅ 已启用hook: {hook['name']}")
                return

        print(f"❌ 未找到hook: {hook_id}")

    def disable_hook(self, hook_id: str) -> None:
        """禁用指定的hook"""
        config = self.load_config()

        for hook in config.get("hooks", []):
            if hook["id"] == hook_id:
                hook["enabled"] = False
                self.save_config(config)
                print(f"❌ 已禁用hook: {hook['name']}")
                return

        print(f"❌ 未找到hook: {hook_id}")

    def get_hook_status(self, hook_id: str) -> None:
        """获取hook状态"""
        config = self.load_config()

        for hook in config.get("hooks", []):
            if hook["id"] == hook_id:
                status = "启用" if hook.get("enabled", False) else "禁用"
                print(f"Hook: {hook['name']}")
                print(f"状态: {status}")
                print(f"文件: {hook['file']}")
                print("触发条件:")
                for trigger in hook.get("triggers", []):
                    trigger_type = trigger['type']
                    pattern = trigger.get('pattern', 'N/A')
                    print(f"  - {trigger_type}: {pattern}")
                return

        print(f"❌ 未找到hook: {hook_id}")

    def validate_config(self) -> None:
        """验证hooks配置"""
        config = self.load_config()
        errors = []

        for hook in config.get("hooks", []):
            # 检查必需字段
            required_fields = ["id", "name", "description", "file"]
            for field in required_fields:
                if field not in hook:
                    errors.append(
                        f"Hook {hook.get('id', 'unknown')} 缺少字段: {field}")

            # 检查文件是否存在
            hook_file = self.hooks_dir / hook.get("file", "")
            if not hook_file.exists():
                errors.append(f"Hook文件不存在: {hook_file}")

        if errors:
            print("❌ 配置验证失败:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("✅ 配置验证通过")


def main():
    """主函数"""
    import sys

    manager = HooksManager()

    if len(sys.argv) < 2:
        print("用法:")
        print("  python manage-hooks.py list                  # 列出所有hooks")
        print("  python manage-hooks.py enable <hook_id>      # 启用hook")
        print("  python manage-hooks.py disable <hook_id>     # 禁用hook")
        print("  python manage-hooks.py status <hook_id>      # 查看hook状态")
        print("  python manage-hooks.py validate             # 验证配置")
        return

    command = sys.argv[1]

    if command == "list":
        manager.list_hooks()
    elif command == "enable" and len(sys.argv) > 2:
        manager.enable_hook(sys.argv[2])
    elif command == "disable" and len(sys.argv) > 2:
        manager.disable_hook(sys.argv[2])
    elif command == "status" and len(sys.argv) > 2:
        manager.get_hook_status(sys.argv[2])
    elif command == "validate":
        manager.validate_config()
    else:
        print("❌ 无效的命令或参数")


if __name__ == "__main__":
    main()
