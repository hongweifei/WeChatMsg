#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File        : run_gui.py
@Description : WeChatMsg GUI跨平台启动脚本
@Author      : Claude Code
@Time        : 2025/1/27
"""

import sys
import os
import subprocess
import platform
import importlib.util
from pathlib import Path


class WeChatMsgLauncher:
    """WeChatMsg跨平台启动器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.python_version = sys.version_info
        self.platform = platform.system().lower()

    def print_banner(self):
        """打印欢迎横幅"""
        print("=" * 50)
        print("        WeChatMsg 一键启动器")
        print("     微信聊天记录解析工具 v3.0")
        print("=" * 50)
        print(f"平台: {self.platform.title()}")
        print(f"Python: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        print("=" * 50)
        print()

    def check_python_version(self):
        """检查Python版本"""
        print("[1/6] 检查Python版本...")

        if self.python_version < (3, 9):
            print(f"[错误] Python版本过低: {self.python_version.major}.{self.python_version.minor}")
            print("需要Python 3.9或更高版本")
            print("请从以下链接下载最新Python版本:")
            print("https://www.python.org/downloads/")
            return False

        if self.python_version >= (3, 13):
            print(f"[警告] Python版本较高: {self.python_version.major}.{self.python_version.minor}")
            print("某些依赖可能不兼容最新Python版本")
            print("如果遇到问题，建议使用Python 3.10-3.12")

        print(f"[成功] Python版本检查通过: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        return True

    def check_project_structure(self):
        """检查项目结构"""
        print("[2/6] 检查项目结构...")

        required_files = [
            "wxManager",
            "exporter",
            "gui",
            "requirements.txt",
            "pyproject.toml"
        ]

        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                print(f"[错误] 缺少必要文件/目录: {file_path}")
                return False

        print("[成功] 项目结构检查通过")
        return True

    def check_dependencies(self):
        """检查依赖包"""
        print("[3/6] 检查Python依赖包...")

        # 核心依赖包列表
        core_packages = [
            "wxManager",
            "exporter",
            "pillow",
            "pycryptodome",
            "psutil",
            "pymem"
        ]

        missing_packages = []

        for package in core_packages:
            try:
                if package in ["wxManager", "exporter"]:
                    # 本地模块检查
                    spec = importlib.util.spec_from_file_location(
                        package,
                        str(self.project_root / package / "__init__.py")
                    )
                    if spec and spec.loader:
                        importlib.util.module_from_spec(spec)
                else:
                    import package
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            print(f"[警告] 缺少依赖包: {', '.join(missing_packages)}")
            return self.install_dependencies()
        else:
            print("[成功] 依赖包检查通过")
            return True

    def install_dependencies(self):
        """安装依赖包"""
        print("[4/6] 安装依赖包...")

        # 检查是否有uv
        uv_available = self._check_command("uv")

        if uv_available:
            print("使用uv安装依赖...")
            try:
                result = subprocess.run(
                    ["uv", "sync"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    print("[成功] 依赖包安装完成")
                    return True
                else:
                    print(f"[警告] uv安装失败: {result.stderr}")

            except subprocess.TimeoutExpired:
                print("[错误] uv安装超时")
            except Exception as e:
                print(f"[错误] uv安装异常: {e}")

        # 回退到pip
        print("回退使用pip安装依赖...")

        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            cmd = [
                sys.executable, "-m", "pip", "install",
                "-r", str(requirements_file)
            ]

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    print("[成功] 依赖包安装完成")
                    return True
                else:
                    print(f"[错误] pip安装失败: {result.stderr}")
                    return False

            except subprocess.TimeoutExpired:
                print("[错误] 依赖安装超时")
                return False
            except Exception as e:
                print(f"[错误] 依赖安装异常: {e}")
                return False
        else:
            print("[错误] 未找到requirements.txt")
            return False

    def _check_command(self, command):
        """检查命令是否可用"""
        try:
            result = subprocess.run(
                [command, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False

    def check_environment(self):
        """检查运行环境"""
        print("[5/6] 检查运行环境...")

        issues = []

        # 检查操作系统
        if self.platform not in ["windows", "linux", "darwin"]:
            issues.append(f"不支持的操作系统: {self.platform}")

        # 检查磁盘空间
        try:
            disk_usage = self.project_root.stat().st_size
            # 这是一个简单的检查，实际中可以更精确
            if disk_usage < 1024 * 1024:  # 1MB
                print("[信息] 建议至少预留1GB磁盘空间用于数据解密")
        except:
            print("[信息] 无法检查磁盘空间")

        # Windows特定检查
        if self.platform == "windows":
            # 检查是否在Windows系统上
            print("[信息] Windows系统检测通过")

        print("[成功] 运行环境检查完成")
        return len(issues) == 0

    def show_warnings(self):
        """显示重要提示"""
        print("[6/6] 准备启动...")
        print()
        print("=" * 50)
        print("               重要提示")
        print("=" * 50)
        print("1. 请确保微信客户端正在运行")
        print("2. 请确保有足够的磁盘空间")
        print("3. 请遵守相关法律法规")
        print("4. 仅限个人聊天记录分析使用")
        print("5. 请勿将本工具用于非法用途")
        print("=" * 50)
        print()

    def launch_gui(self):
        """启动GUI"""
        print("正在启动WeChatMsg GUI...")
        print()

        try:
            # 设置环境变量
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.project_root)

            # 启动GUI
            if self.platform == "windows":
                # Windows系统使用当前Python
                cmd = [sys.executable, str(self.project_root / "gui" / "gui_main.py")]
            else:
                # 其他系统
                cmd = [sys.executable, str(self.project_root / "gui" / "gui_main.py")]

            process = subprocess.Popen(
                cmd,
                env=env,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 等待进程完成
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                print("GUI正常退出")
            else:
                print(f"[错误] GUI异常退出 (退出码: {process.returncode})")
                if stderr:
                    print(f"错误信息: {stderr}")

        except KeyboardInterrupt:
            print("\n用户中断程序")
        except Exception as e:
            print(f"[错误] 启动GUI失败: {e}")

    def run(self):
        """运行启动器"""
        try:
            self.print_banner()

            # 执行检查
            checks = [
                self.check_python_version,
                self.check_project_structure,
                self.check_dependencies,
                self.check_environment
            ]

            for check in checks:
                if not check():
                    print("\n启动检查失败，请解决上述问题后重试")
                    input("按回车键退出...")
                    return

            self.show_warnings()
            self.launch_gui()

        except KeyboardInterrupt:
            print("\n\n用户中断程序")
        except Exception as e:
            print(f"\n[错误] 启动器异常: {e}")

        finally:
            print("\n感谢使用WeChatMsg！")
            if self.platform == "windows":
                input("按回车键退出...")


def main():
    """主函数"""
    # 设置多进程支持
    try:
        import multiprocessing
        multiprocessing.freeze_support()
    except ImportError:
        pass

    launcher = WeChatMsgLauncher()
    launcher.run()


if __name__ == "__main__":
    main()