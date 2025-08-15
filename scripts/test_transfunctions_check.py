#!/usr/bin/env python3
"""
测试transfunctions检查脚本的功能
"""

import subprocess
import sys
from pathlib import Path


def test_transfunctions_checker():
    """测试transfunctions检查器"""
    print("🧪 测试transfunctions检查脚本...")

    # 创建临时测试文件
    test_content = '''#!/usr/bin/env python3
"""测试文件"""

def format_phone(phone: str) -> str:
    """重复实现的format_phone函数"""
    return phone

def format_currency(amount: float) -> str:
    """重复实现的format_currency函数"""
    return f"¥{amount}"

def some_other_function():
    """这个函数不应该被检测到"""
    pass
'''

    # 创建临时目录和文件
    temp_dir = Path("src/temp_test")
    temp_dir.mkdir(exist_ok=True)
    test_file = temp_dir / "test_violations.py"

    try:
        # 写入测试文件
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)

        # 运行检查脚本
        result = subprocess.run(
            [sys.executable, "scripts/check_transfunctions_usage.py"],
            capture_output=True,
            text=True,
        )

        # 检查结果
        if result.returncode == 1:
            print("✅ 检查脚本正确检测到违规")
            print("📋 检测到的违规:")
            for line in result.stderr.split("\n"):
                if "temp_test" in line:
                    print(f"   {line}")
        else:
            print("❌ 检查脚本未能检测到违规")
            print(f"返回码: {result.returncode}")
            print(f"输出: {result.stderr}")

        # 清理测试文件
        test_file.unlink()
        temp_dir.rmdir()

        # 再次运行检查，应该返回0
        result2 = subprocess.run(
            [sys.executable, "scripts/check_transfunctions_usage.py"],
            capture_output=True,
            text=True,
        )

        if result2.returncode == 0:
            print("✅ 清理后检查脚本正确返回0")
            return True
        else:
            print("❌ 清理后检查脚本未返回0")
            print(f"返回码: {result2.returncode}")
            print(f"输出: {result2.stderr}")
            return False

    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        # 清理
        if test_file.exists():
            test_file.unlink()
        if temp_dir.exists():
            temp_dir.rmdir()
        return False


if __name__ == "__main__":
    success = test_transfunctions_checker()
    sys.exit(0 if success else 1)
