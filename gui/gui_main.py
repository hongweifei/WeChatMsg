#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File        : gui_main.py
@Description : WeChatMsg GUI主程序
@Author      : Claude Code
@Time        : 2025/1/27
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.controller import MainController
from gui.models.app_state import AppState
from gui.views.main_window import MainWindow


class WeChatMsgGUI:
    """WeChatMsg GUI主应用类"""

    def __init__(self):
        self.root = tk.Tk()
        self.app_state = AppState()
        self.controller = MainController(self.app_state)
        self.main_window = None

        self._setup_window()
        self._setup_views()

    def _setup_window(self):
        """设置主窗口"""
        self.root.title("WeChatMsg - 微信聊天记录解析工具")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # 设置图标（如果有的话）
        try:
            # self.root.iconbitmap('assets/icon.ico')
            pass
        except:
            pass

        # 设置关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_views(self):
        """设置视图组件"""
        self.main_window = MainWindow(self.root, self.controller, self.app_state)

    def _on_closing(self):
        """窗口关闭事件处理"""
        if messagebox.askokcancel("退出", "确定要退出WeChatMsg吗？"):
            self.controller.cleanup()
            self.root.destroy()

    def run(self):
        """运行应用"""
        try:
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("错误", f"应用运行出错: {str(e)}")
            raise


def main():
    """主函数"""
    # 设置多进程支持
    import multiprocessing
    multiprocessing.freeze_support()

    try:
        app = WeChatMsgGUI()
        app.run()
    except Exception as e:
        messagebox.showerror("启动错误", f"应用启动失败: {str(e)}")


if __name__ == "__main__":
    main()