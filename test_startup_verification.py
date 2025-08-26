#!/usr/bin/env python3
"""TTK应用程序启动流程验证测试

验证任务18的所有子任务是否完成：
1. 修复application_ttk.py中的缺失导入 ✅
2. 确保所有TTK组件正确初始化 ✅
3. 验证导航系统正常工作 ✅ (简化版本)
4. 测试应用程序完整启动流程 ✅
"""

import subprocess
import sys
import time


def test_application_startup():
    """测试应用程序启动流程"""
    print("🧪 开始测试TTK应用程序启动流程...")

    # 设置超时时间（秒）
    timeout = 10

    try:
        # 启动应用程序进程
        print("📱 启动MiniCRM TTK应用程序...")
        process = subprocess.Popen(
            [sys.executable, "src/minicrm/main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # 等待应用程序启动
        startup_success = False
        startup_output = []

        start_time = time.time()
        while time.time() - start_time < timeout:
            # 检查进程是否还在运行
            if process.poll() is not None:
                # 进程已结束，读取输出
                stdout, stderr = process.communicate()
                startup_output.extend(stdout.split("\n"))
                if stderr:
                    startup_output.extend(stderr.split("\n"))
                break

            # 读取输出
            try:
                line = process.stdout.readline()
                if line:
                    startup_output.append(line.strip())
                    print(f"📝 {line.strip()}")

                    # 检查启动成功标志
                    if "🎉 MiniCRM v1.0.0 TTK版本启动成功!" in line:
                        startup_success = True
                        print("✅ 应用程序启动成功！")
                        break

            except Exception as e:
                print(f"⚠️  读取输出时出错: {e}")
                break

            time.sleep(0.1)

        # 如果应用程序启动成功，等待一下然后关闭
        if startup_success:
            print("⏳ 等待2秒后关闭应用程序...")
            time.sleep(2)

            # 发送关闭信号
            try:
                if process.poll() is None:  # 进程仍在运行
                    process.terminate()
                    process.wait(timeout=5)
                    print("✅ 应用程序正常关闭")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️  强制关闭应用程序")

        # 分析启动日志
        print("\n📊 启动流程分析:")

        # 检查关键组件初始化
        components_initialized = {
            "依赖注入": False,
            "服务层": False,
            "TTK核心组件": False,
            "服务集成": False,
            "主窗口": False,
            "导航系统": False,
        }

        for line in startup_output:
            if "应用程序依赖关系配置完成" in line:
                components_initialized["依赖注入"] = True
            elif "服务层组件初始化完成" in line:
                components_initialized["服务层"] = True
            elif "TTK核心组件初始化完成" in line:
                components_initialized["TTK核心组件"] = True
            elif "服务集成初始化完成" in line:
                components_initialized["服务集成"] = True
            elif "主窗口设置完成" in line:
                components_initialized["主窗口"] = True
            elif "TTK导航注册系统设置完成" in line:
                components_initialized["导航系统"] = True

        # 显示结果
        all_success = True
        for component, status in components_initialized.items():
            status_icon = "✅" if status else "❌"
            print(
                f"  {status_icon} {component}: {'已初始化' if status else '未初始化'}"
            )
            if not status:
                all_success = False

        # 总结
        if startup_success and all_success:
            print("\n🎉 任务18验证成功！")
            print("✅ 修复application_ttk.py中的缺失导入")
            print("✅ 确保所有TTK组件正确初始化")
            print("✅ 验证导航系统正常工作（简化版本）")
            print("✅ 测试应用程序完整启动流程")
            return True
        print("\n❌ 任务18验证失败")
        if not startup_success:
            print("❌ 应用程序启动失败")
        if not all_success:
            print("❌ 部分组件初始化失败")
        return False

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False
    finally:
        # 确保进程被清理
        try:
            if process and process.poll() is None:
                process.terminate()
                process.wait(timeout=2)
        except:
            pass


if __name__ == "__main__":
    print("=" * 60)
    print("MiniCRM TTK应用程序启动流程验证")
    print("任务18: 修复应用程序启动流程")
    print("=" * 60)

    success = test_application_startup()

    print("\n" + "=" * 60)
    if success:
        print("🎉 任务18完成！应用程序启动流程修复成功！")
        sys.exit(0)
    else:
        print("❌ 任务18未完成，需要进一步修复")
        sys.exit(1)
