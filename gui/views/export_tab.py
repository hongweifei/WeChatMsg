#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File        : export_tab.py
@Description : 导出标签页
@Author      : Claude Code
@Time        : 2025/11/27
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Optional

from exporter.config import FileType

from gui.models.app_state import ExportTask, ProcessingStatus


class ExportTab:
    """导出聊天记录标签页"""

    def __init__(self, parent, controller, app_state):
        self.parent = parent
        self.controller = controller
        self.app_state = app_state
        self.export_tasks: List[ExportTask] = []

        self._create_widgets()
        self._layout_widgets()
        self._setup_initial_state()

    def _create_widgets(self):
        """创建UI组件"""
        # 主框架
        self.frame = ttk.Frame(self.parent)

        # 标题框架
        self.title_frame = ttk.Frame(self.frame)
        self.title_label = ttk.Label(
            self.title_frame, text="导出聊天记录", font=("Arial", 14, "bold")
        )
        self.title_label.pack()

        # 导出配置框架
        config_frame = ttk.LabelFrame(self.frame, text="导出配置", padding="10")

        # 导出格式
        ttk.Label(config_frame, text="导出格式:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.format_var = tk.StringVar(
            value=self.app_state.get_setting("default_export_format", "HTML")
        )
        self.format_combo = ttk.Combobox(
            config_frame,
            textvariable=self.format_var,
            values=["HTML", "TXT", "CSV", "DOCX", "MARKDOWN", "XLSX", "AI_TXT"],
        )
        self.format_combo.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))

        # 输出目录
        ttk.Label(config_frame, text="输出目录:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        output_dir_frame = ttk.Frame(config_frame)
        self.output_dir_var = tk.StringVar(
            value=self.app_state.get_setting("default_output_dir", "./output")
        )
        self.output_dir_entry = ttk.Entry(
            output_dir_frame, textvariable=self.output_dir_var
        )
        self.output_dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.browse_button = ttk.Button(
            output_dir_frame, text="浏览", command=self._browse_output_dir
        )
        self.browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        output_dir_frame.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(10, 0))

        # 时间范围
        time_frame = ttk.LabelFrame(config_frame, text="时间范围 (可选)", padding="5")
        ttk.Label(time_frame, text="开始时间:").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        self.start_time_var = tk.StringVar(
            value=self.app_state.get_setting("time_range_start", "2020-01-01 00:00:00")
        )
        self.start_time_entry = ttk.Entry(
            time_frame, textvariable=self.start_time_var, width=25
        )
        self.start_time_entry.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(10, 0))

        ttk.Label(time_frame, text="结束时间:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        self.end_time_var = tk.StringVar(
            value=self.app_state.get_setting("time_range_end", "2035-12-31 23:59:59")
        )
        self.end_time_entry = ttk.Entry(
            time_frame, textvariable=self.end_time_var, width=25
        )
        self.end_time_entry.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(10, 0))

        # 消息类型过滤
        msg_types_frame = ttk.LabelFrame(
            config_frame, text="消息类型过滤 (可选)", padding="5"
        )
        self.msg_type_vars = {}
        msg_types = [
            ("文本消息", "TextMessage", True),
            ("图片消息", "ImageMessage", True),
            ("语音消息", "AudioMessage", False),
            ("视频消息", "VideoMessage", False),
            ("表情包", "EmojiMessage", False),
            ("文件消息", "FileMessage", False),
            ("链接消息", "LinkMessage", True),
            ("位置消息", "PositionMessage", False),
        ]

        for i, (label, value, default) in enumerate(msg_types):
            var = tk.BooleanVar(value=default)
            self.msg_type_vars[value] = var
            ttk.Checkbutton(msg_types_frame, text=label, variable=var).grid(
                row=i // 2, column=i % 2, sticky=tk.W, pady=2, padx=5
            )

        # 配置列权重
        config_frame.columnconfigure(1, weight=1)

        # 快速添加框架
        quick_add_frame = ttk.LabelFrame(
            self.frame, text="快速添加导出任务", padding="10"
        )

        # 添加选中联系人
        add_selected_frame = ttk.Frame(quick_add_frame)
        self.add_selected_button = ttk.Button(
            add_selected_frame,
            text="添加选中的联系人",
            command=self._add_selected_contacts,
        )
        self.add_selected_button.pack(side=tk.LEFT, padx=(0, 5))
        selected_count_label = ttk.Label(
            add_selected_frame, text="(已在联系人标签页选择)"
        )
        selected_count_label.pack(side=tk.LEFT)
        add_selected_frame.pack(fill=tk.X, pady=5)

        # 添加指定联系人
        add_specific_frame = ttk.Frame(quick_add_frame)
        ttk.Label(add_specific_frame, text="添加指定微信ID:").pack(side=tk.LEFT)
        self.specific_wxid_var = tk.StringVar()
        self.specific_wxid_entry = ttk.Entry(
            add_specific_frame, textvariable=self.specific_wxid_var
        )
        self.specific_wxid_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.add_specific_button = ttk.Button(
            add_specific_frame, text="添加", command=self._add_specific_contact
        )
        self.add_specific_button.pack(side=tk.LEFT)
        add_specific_frame.pack(fill=tk.X, pady=5)

        # 任务列表框架
        task_frame = ttk.LabelFrame(self.frame, text="导出任务列表", padding="5")

        # 任务列表
        columns = ("contact", "format", "output_dir", "status")
        self.task_tree = ttk.Treeview(
            task_frame, columns=columns, show="headings", height=8
        )

        self.task_tree.heading("contact", text="联系人")
        self.task_tree.heading("format", text="格式")
        self.task_tree.heading("output_dir", text="输出目录")
        self.task_tree.heading("status", text="状态")

        self.task_tree.column("contact", width=150)
        self.task_tree.column("format", width=100)
        self.task_tree.column("output_dir", width=300)
        self.task_tree.column("status", width=80)

        # 滚动条
        task_scrollbar = ttk.Scrollbar(
            task_frame, orient=tk.VERTICAL, command=self.task_tree.yview
        )
        self.task_tree.configure(yscrollcommand=task_scrollbar.set)

        # 任务控制按钮
        task_control_frame = ttk.Frame(task_frame)
        self.remove_task_button = ttk.Button(
            task_control_frame, text="移除选中任务", command=self._remove_selected_task
        )
        self.remove_task_button.pack(side=tk.LEFT, padx=5)
        self.clear_tasks_button = ttk.Button(
            task_control_frame, text="清空任务", command=self._clear_tasks
        )
        self.clear_tasks_button.pack(side=tk.LEFT, padx=5)

        # 导出按钮
        export_frame = ttk.Frame(self.frame)
        self.export_button = ttk.Button(
            export_frame,
            text="开始导出",
            command=self._start_export,
            style="Accent.TButton",
        )
        self.export_button.pack(side=tk.LEFT, padx=5)
        self.export_button.config(width=20)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, variable=self.progress_var, mode="indeterminate"
        )

        # 状态标签
        self.status_label = ttk.Label(
            self.frame, text="请先解密数据库并加载联系人", foreground="blue"
        )

        # 保存组件引用
        self.config_frame = config_frame
        self.time_frame = time_frame
        self.msg_types_frame = msg_types_frame
        self.quick_add_frame = quick_add_frame
        self.task_frame = task_frame
        self.task_scrollbar = task_scrollbar
        self.task_control_frame = task_control_frame
        self.export_frame = export_frame

    def _layout_widgets(self):
        """布局UI组件"""
        # 垂直布局
        self.title_frame.pack(fill=tk.X, pady=(0, 10))

        self.config_frame.pack(fill=tk.X, pady=(0, 10))
        self.time_frame.grid(
            row=2, column=0, columnspan=2, sticky=tk.EW, pady=10, padx=(10, 0)
        )
        self.msg_types_frame.grid(
            row=3, column=0, columnspan=2, sticky=tk.EW, pady=10, padx=(10, 0)
        )

        self.quick_add_frame.pack(fill=tk.X, pady=(0, 10))

        self.task_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.task_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_control_frame.pack(fill=tk.X, pady=(5, 0))

        self.export_frame.pack(fill=tk.X, pady=(0, 10))

        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        self.status_label.pack(fill=tk.X)

    def _setup_initial_state(self):
        """设置初始状态"""
        self._update_ui_state()

    def _browse_output_dir(self):
        """浏览输出目录"""
        directory = self.controller.select_output_directory()
        if directory:
            self.output_dir_var.set(directory)

    def _add_selected_contacts(self):
        """添加选中的联系人"""
        selected_contacts = self.app_state.selected_contacts
        if not selected_contacts:
            messagebox.showwarning("警告", "请在联系人标签页先选择要导出的联系人")
            return

        export_format = self.format_var.get()
        output_dir = self.output_dir_var.get()

        message_types = self._get_selected_message_types()
        time_range = self._get_time_range()

        added_count = 0
        for wxid in selected_contacts:
            if self.controller.add_export_task(
                wxid,
                export_format,
                output_dir,
                message_types=message_types,
                time_range=time_range,
            ):
                added_count += 1

        if added_count > 0:
            messagebox.showinfo("成功", f"已添加 {added_count} 个导出任务")
            # 切换回联系人标签页清空选择
            # self.parent.parent.parent.notebook.select(1)

    def _add_specific_contact(self):
        """添加指定联系人"""
        wxid = self.specific_wxid_var.get().strip()
        if not wxid:
            messagebox.showwarning("警告", "请输入微信ID")
            return

        export_format = self.format_var.get()
        output_dir = self.output_dir_var.get()
        message_types = self._get_selected_message_types()
        time_range = self._get_time_range()

        if self.controller.add_export_task(
            wxid,
            export_format,
            output_dir,
            message_types=message_types,
            time_range=time_range,
        ):
            messagebox.showinfo("成功", f"已添加联系人 {wxid} 的导出任务")
            self.specific_wxid_var.set("")
        else:
            messagebox.showerror("错误", f"添加联系人 {wxid} 的导出任务失败")

    def _remove_selected_task(self):
        """移除选中的任务"""
        selection = self.task_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要移除的任务")
            return

        item = self.task_tree.item(selection[0])
        contact_wxid = item["values"][0]

        # 查找并移除任务
        for i, task in enumerate(self.export_tasks):
            if task.contact_wxid == contact_wxid:
                self.app_state.remove_export_task(i)
                self._update_task_list()
                messagebox.showinfo("成功", f"已移除联系人 {contact_wxid} 的导出任务")
                return

    def _clear_tasks(self):
        """清空所有任务"""
        if not self.export_tasks:
            messagebox.showinfo("提示", "没有导出任务")
            return

        if messagebox.askyesno("确认", "确定要清空所有导出任务吗？"):
            self.app_state.clear_export_tasks()
            self._update_task_list()
            messagebox.showinfo("成功", "已清空所有导出任务")

    def _start_export(self):
        """开始导出"""
        if not self.export_tasks:
            messagebox.showwarning("警告", "请先添加导出任务")
            return

        if not messagebox.askyesno(
            "确认导出",
            f"确定要导出 {len(self.export_tasks)} 个联系人的聊天记录吗？\n\n"
            "这个过程可能需要较长时间，请耐心等待。",
        ):
            return

        self.export_button.config(state=tk.DISABLED)
        self.status_label.config(text="正在导出聊天记录...", foreground="orange")
        self.progress_bar.start()

        self.controller.execute_export_tasks()

    def _get_selected_message_types(self):
        """获取选中的消息类型"""
        selected_types = []
        for msg_type, var in self.msg_type_vars.items():
            if var.get():
                selected_types.append(msg_type)
        return selected_types if selected_types else None

    def _get_time_range(self):
        """获取时间范围"""
        start_time = self.start_time_var.get().strip()
        end_time = self.end_time_var.get().strip()
        return [start_time, end_time] if start_time and end_time else None

    def _update_task_list(self):
        """更新任务列表"""
        # 清空现有项
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        # 添加任务
        self.export_tasks = self.app_state.export_tasks
        for task in self.export_tasks:
            self.task_tree.insert(
                "",
                tk.END,
                values=(
                    task.contact_wxid,
                    task.export_format,
                    task.output_dir,
                    task.status,
                ),
            )

    def _update_ui_state(self):
        """更新UI状态"""
        has_database = bool(self.app_state.db_dir)
        has_contacts = len(self.app_state.contacts) > 0
        has_tasks = len(self.export_tasks) > 0
        has_selected_contacts = len(self.app_state.selected_contacts) > 0

        is_busy = self.app_state.status in [ProcessingStatus.EXPORTING]

        self.add_selected_button.config(
            state=tk.NORMAL if has_selected_contacts and not is_busy else tk.DISABLED
        )
        self.add_specific_button.config(
            state=tk.NORMAL if has_database and not is_busy else tk.DISABLED
        )
        self.remove_task_button.config(
            state=tk.NORMAL if has_tasks and not is_busy else tk.DISABLED
        )
        self.clear_tasks_button.config(
            state=tk.NORMAL if has_tasks and not is_busy else tk.DISABLED
        )
        self.export_button.config(
            state=tk.NORMAL if has_tasks and not is_busy else tk.DISABLED
        )

    def on_export_task_added(self, task: ExportTask):
        """导出任务添加回调"""
        self._update_task_list()
        self._update_ui_state()
        self.status_label.config(
            text=f"已添加 {task.contact_wxid} 的导出任务", foreground="green"
        )

    def on_export_completed(self, task, success: bool, error_msg: str = None):
        """导出完成回调"""
        self.export_button.config(state=tk.NORMAL)
        self.progress_bar.stop()

        if success:
            self.status_label.config(text="导出完成", foreground="green")
        else:
            self.status_label.config(text=f"导出失败: {error_msg}", foreground="red")

        self._update_ui_state()
