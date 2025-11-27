#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File        : status_bar.py
@Description : 状态栏组件
@Author      : Claude Code
@Time        : 2025/1/27
"""

import tkinter as tk
from tkinter import ttk
from gui.models.app_state import ProcessingStatus


class StatusBar:
    """状态栏类"""

    def __init__(self, parent, app_state):
        self.parent = parent
        self.app_state = app_state

        self._create_widgets()
        self._layout_widgets()

    def _create_widgets(self):
        """创建状态栏组件"""
        self.frame = ttk.Frame(self.parent)

        # 状态指示器
        self.status_frame = ttk.Frame(self.frame)
        self.status_label = ttk.Label(self.status_frame, text="就绪", foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=(0, 10))

        # 分隔线
        separator1 = ttk.Separator(self.status_frame, orient=tk.VERTICAL)
        separator1.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 数据库状态
        self.db_status_label = ttk.Label(self.status_frame, text="数据库: 未连接", foreground="gray")
        self.db_status_label.pack(side=tk.LEFT, padx=5)

        # 分隔线
        separator2 = ttk.Separator(self.status_frame, orient=tk.VERTICAL)
        separator2.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 联系人数量
        self.contacts_label = ttk.Label(self.status_frame, text="联系人: 0", foreground="gray")
        self.contacts_label.pack(side=tk.LEFT, padx=5)

        # 分隔线
        separator3 = ttk.Separator(self.status_frame, orient=tk.VERTICAL)
        separator3.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # 导出任务数量
        self.tasks_label = ttk.Label(self.status_frame, text="导出任务: 0", foreground="gray")
        self.tasks_label.pack(side=tk.LEFT, padx=5)

        # 右侧信息
        info_frame = ttk.Frame(self.frame)

        # 当前时间
        self.time_label = ttk.Label(info_frame, text="")
        self.time_label.pack(side=tk.RIGHT, padx=(10, 0))

        # 版本信息
        self.version_label = ttk.Label(info_frame, text="v1.0.0", foreground="gray")
        self.version_label.pack(side=tk.RIGHT, padx=(10, 0))

        # 保存组件引用
        self.info_frame = info_frame

        # 启动时间更新
        self._update_time()

    def _layout_widgets(self):
        """布局状态栏组件"""
        self.status_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.info_frame.pack(side=tk.RIGHT, fill=tk.X)

        # 设置边框
        self.frame.configure(relief=tk.SUNKEN, borderwidth=1)

    def _update_time(self):
        """更新时间显示"""
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.parent.after(1000, self._update_time)

    def update_status(self, status: ProcessingStatus, message: str = ""):
        """更新状态"""
        # 更新状态文本和颜色
        status_text = message or self._get_status_text(status)
        status_color = self._get_status_color(status)

        self.status_label.config(text=status_text, foreground=status_color)

        # 更新数据库状态
        if self.app_state.db_dir:
            self.db_status_label.config(
                text=f"数据库: 已连接 (v{self.app_state.db_version})",
                foreground="green"
            )
        else:
            self.db_status_label.config(text="数据库: 未连接", foreground="gray")

        # 更新联系人数量
        contacts_count = len(self.app_state.contacts)
        self.contacts_label.config(text=f"联系人: {contacts_count}")

        # 更新导出任务数量
        tasks_count = len(self.app_state.export_tasks)
        self.tasks_label.config(text=f"导出任务: {tasks_count}")

    def _get_status_text(self, status: ProcessingStatus) -> str:
        """获取状态文本"""
        status_map = {
            ProcessingStatus.IDLE: "就绪",
            ProcessingStatus.DECRYPTING: "正在解密数据库...",
            ProcessingStatus.LOADING_CONTACTS: "正在加载联系人...",
            ProcessingStatus.EXPORTING: "正在导出聊天记录...",
            ProcessingStatus.ERROR: "发生错误"
        }
        return status_map.get(status, "未知状态")

    def _get_status_color(self, status: ProcessingStatus) -> str:
        """获取状态颜色"""
        color_map = {
            ProcessingStatus.IDLE: "blue",
            ProcessingStatus.DECRYPTING: "orange",
            ProcessingStatus.LOADING_CONTACTS: "orange",
            ProcessingStatus.EXPORTING: "orange",
            ProcessingStatus.ERROR: "red"
        }
        return color_map.get(status, "black")