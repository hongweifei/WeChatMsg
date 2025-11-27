#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File        : run_gui.py
@Description : WeChatMsg GUI启动脚本
@Author      : Claude Code
@Time        : 2025/1/27
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main():
    """主函数"""
    try:
        from gui.gui_main import WeChatMsgGUI

        print("正在启动WeChatMsg GUI...")
        print("请确保:")
        print("1. 微信客户端正在运行")
        print("2. 有足够的磁盘空间")
        print("3. 遵守相关法律法规")
        print()

        app = WeChatMsgGUI()
        app.run()

    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保已安装所有依赖:")
        print("pip install -r requirements.txt")
        input("按回车键退出...")

    except Exception as e:
        print(f"启动GUI失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    # 设置多进程支持
    import multiprocessing
    multiprocessing.freeze_support()

    main()