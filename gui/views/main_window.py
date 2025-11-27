#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File        : main_window.py
@Description : 主窗口视图
@Author      : Claude Code
@Time        : 2025/11/27
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional

from gui.models.app_state import ProcessingStatus
from gui.views.contact_tab import ContactTab
from gui.views.decrypt_tab import DecryptTab
from gui.views.export_tab import ExportTab
from gui.views.status_bar import StatusBar


class MainWindow:
    """主窗口类"""

    def __init__(self, root: tk.Tk, controller, app_state):
        self.root = root
        self.controller = controller
        self.app_state = app_state

        # 注册回调函数
        self._register_callbacks()

        # 创建UI组件
        self._create_widgets()
        self._layout_widgets()
        self._setup_initial_state()

    def _register_callbacks(self):
        """注册控制器回调"""
        self.controller.add_callback("status_changed", self._on_status_changed)
        self.controller.add_callback("accounts_scanned", self._on_accounts_scanned)
        self.controller.add_callback("database_decrypted", self._on_database_decrypted)
        self.controller.add_callback("contacts_loaded", self._on_contacts_loaded)
        self.controller.add_callback("export_task_added", self._on_export_task_added)
        self.controller.add_callback("export_completed", self._on_export_completed)
        self.controller.add_callback("error", self._on_error)

    def _create_widgets(self):
        """创建UI组件"""
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)

        # 创建Notebook（标签页容器）
        self.notebook = ttk.Notebook(self.main_frame)

        # 创建标签页
        self.decrypt_tab = DecryptTab(self.notebook, self.controller, self.app_state)
        self.contact_tab = ContactTab(self.notebook, self.controller, self.app_state)
        self.export_tab = ExportTab(self.notebook, self.controller, self.app_state)

        # 添加标签页
        self.notebook.add(self.decrypt_tab.frame, text="解密数据库")
        self.notebook.add(self.contact_tab.frame, text="联系人管理")
        self.notebook.add(self.export_tab.frame, text="导出聊天记录")

        # 创建状态栏
        self.status_bar = StatusBar(self.main_frame, self.app_state)

        # 创建菜单栏
        self._create_menu()

    def _create_menu(self):
        """创建菜单栏"""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # 文件菜单
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="选择输出目录", command=self._select_output_dir)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        # 工具菜单
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="设置", command=self._show_settings)

        # 帮助菜单
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)

    def _layout_widgets(self):
        """布局UI组件"""
        # 使用grid布局
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Notebook占据大部分空间
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # 状态栏在底部
        self.status_bar.frame.pack(fill=tk.X, side=tk.BOTTOM)

    def _setup_initial_state(self):
        """设置初始状态"""
        # 设置默认输出目录
        default_output = self.app_state.get_setting("default_output_dir", "./output")
        if not tk.messagebox.askyesno(
            "确认", f"使用默认输出目录:\n{default_output}\n\n是否现在选择其他目录？"
        ):
            self.app_state.set_setting("default_output_dir", default_output)
        else:
            self._select_output_dir()

    def _select_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=self.app_state.get_setting("default_output_dir"),
        )
        if directory:
            self.app_state.set_setting("default_output_dir", directory)
            messagebox.showinfo("成功", f"输出目录已设置为: {directory}")

    def _show_settings(self):
        """显示设置对话框"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("设置")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()

        # 设置框架
        settings_frame = ttk.Frame(settings_window, padding="20")
        settings_frame.pack(fill=tk.BOTH, expand=True)

        # 默认导出格式
        ttk.Label(settings_frame, text="默认导出格式:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        format_var = tk.StringVar(
            value=self.app_state.get_setting("default_export_format", "HTML")
        )
        format_combo = ttk.Combobox(
            settings_frame,
            textvariable=format_var,
            values=["HTML", "TXT", "CSV", "DOCX", "MARKDOWN", "XLSX", "AI_TXT"],
        )
        format_combo.grid(row=0, column=1, sticky=tk.EW, pady=5)

        # 最大线程数
        ttk.Label(settings_frame, text="最大线程数:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        threads_var = tk.IntVar(value=self.app_state.get_setting("max_threads", 4))
        threads_spinbox = ttk.Spinbox(
            settings_frame, from_=1, to=16, textvariable=threads_var
        )
        threads_spinbox.grid(row=1, column=1, sticky=tk.EW, pady=5)

        # 自动检测版本
        auto_detect_var = tk.BooleanVar(
            value=self.app_state.get_setting("auto_detect_version", True)
        )
        ttk.Checkbutton(
            settings_frame, text="自动检测微信版本", variable=auto_detect_var
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)

        # 时间范围
        ttk.Label(settings_frame, text="默认开始时间:").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        start_time_var = tk.StringVar(
            value=self.app_state.get_setting("time_range_start", "2020-01-01 00:00:00")
        )
        ttk.Entry(settings_frame, textvariable=start_time_var).grid(
            row=3, column=1, sticky=tk.EW, pady=5
        )

        ttk.Label(settings_frame, text="默认结束时间:").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        end_time_var = tk.StringVar(
            value=self.app_state.get_setting("time_range_end", "2035-12-31 23:59:59")
        )
        ttk.Entry(settings_frame, textvariable=end_time_var).grid(
            row=4, column=1, sticky=tk.EW, pady=5
        )

        # 配置列权重
        settings_frame.columnconfigure(1, weight=1)

        # 按钮框架
        button_frame = ttk.Frame(settings_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        def save_settings():
            """保存设置"""
            self.app_state.set_setting("default_export_format", format_var.get())
            self.app_state.set_setting("max_threads", threads_var.get())
            self.app_state.set_setting("auto_detect_version", auto_detect_var.get())
            self.app_state.set_setting("time_range_start", start_time_var.get())
            self.app_state.set_setting("time_range_end", end_time_var.get())
            messagebox.showinfo("成功", "设置已保存")
            settings_window.destroy()

        def reset_settings():
            """重置设置"""
            if messagebox.askyesno("确认", "确定要重置所有设置吗？"):
                format_var.set("HTML")
                threads_var.set(4)
                auto_detect_var.set(True)
                start_time_var.set("2020-01-01 00:00:00")
                end_time_var.set("2035-12-31 23:59:59")

        ttk.Button(button_frame, text="保存", command=save_settings).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="重置", command=reset_settings).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="取消", command=settings_window.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def _show_about(self):
        """显示关于对话框"""
        about_text = """WeChatMsg - 微信聊天记录解析工具

版本: 1.0.0

这是一个专业的微信聊天记录解析和导出工具，支持：
- 微信4.0和3.x版本
- 多种格式导出（HTML、TXT、CSV、DOCX、Markdown、Excel等）
- 群聊和私聊记录
- 媒体文件处理
- AI分析功能

开发者: Claude Code
项目地址: https://github.com/..."

使用本工具前请确保：
1. 微信客户端正在运行
2. 有足够的磁盘空间存储解密后的数据库
3. 遵守相关法律法规，仅用于个人数据备份

注意: 本工具仅用于合法的个人数据备份目的，请勿用于非法用途。"""

        messagebox.showinfo("关于 WeChatMsg", about_text)

    # 回调函数
    def _on_status_changed(self, status: ProcessingStatus, message: str = ""):
        """状态改变回调"""
        self.status_bar.update_status(status, message)

        # 根据状态更新界面
        if status in [
            ProcessingStatus.DECRYPTING,
            ProcessingStatus.LOADING_CONTACTS,
            ProcessingStatus.EXPORTING,
        ]:
            self.root.config(cursor="watch")
        else:
            self.root.config(cursor="")

    def _on_accounts_scanned(self, accounts: List):
        """账户扫描完成回调"""
        self.decrypt_tab.on_accounts_scanned(accounts)

    def _on_database_decrypted(self, account, success: bool, error_msg: str = None):
        """数据库解密完成回调"""
        if success:
            self.decrypt_tab.on_database_decrypted(account, True)
            # 自动切换到联系人标签页
            self.notebook.select(self.contact_tab.frame)
            # 自动加载联系人
            self.controller.load_contacts()
        else:
            self.decrypt_tab.on_database_decrypted(account, False, error_msg)

    def _on_contacts_loaded(self, contacts: List):
        """联系人加载完成回调"""
        self.contact_tab.on_contacts_loaded(contacts)

    def _on_export_task_added(self, task):
        """导出任务添加回调"""
        self.export_tab.on_export_task_added(task)

    def _on_export_completed(self, task, success: bool, error_msg: str = None):
        """导出完成回调"""
        if success:
            messagebox.showinfo("成功", f"成功导出 {task.contact_wxid} 的聊天记录")
        else:
            messagebox.showerror(
                "导出失败", f"导出 {task.contact_wxid} 失败: {error_msg}"
            )

    def _on_error(self, error_msg: str):
        """错误回调"""
        messagebox.showerror("错误", error_msg)
