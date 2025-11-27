#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File        : contact_tab.py
@Description : 联系人标签页
@Author      : Claude Code
@Time        : 2025/11/27
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from gui.models.app_state import ContactInfo, ProcessingStatus


class ContactTab:
    """联系人管理标签页"""

    def __init__(self, parent, controller, app_state):
        self.parent = parent
        self.controller = controller
        self.app_state = app_state
        self.contacts: List[ContactInfo] = []

        self._create_widgets()
        self._layout_widgets()
        self._setup_initial_state()

    def _create_widgets(self):
        """创建UI组件"""
        # 主框架
        self.frame = ttk.Frame(self.parent)

        # 标题框架
        title_frame = ttk.Frame(self.frame)
        self.title_label = ttk.Label(
            title_frame, text="联系人管理", font=("Arial", 14, "bold")
        )
        self.title_label.pack()

        # 控制按钮框架
        control_frame = ttk.Frame(self.frame)
        self.refresh_button = ttk.Button(
            control_frame, text="刷新联系人", command=self._refresh_contacts
        )
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        self.select_all_button = ttk.Button(
            control_frame, text="全选", command=self._select_all
        )
        self.select_all_button.pack(side=tk.LEFT, padx=5)

        self.clear_selection_button = ttk.Button(
            control_frame, text="清空选择", command=self._clear_selection
        )
        self.clear_selection_button.pack(side=tk.LEFT, padx=5)

        self.export_selected_button = ttk.Button(
            control_frame, text="导出选中", command=self._export_selected
        )
        self.export_selected_button.pack(side=tk.LEFT, padx=5)

        # 搜索框架
        search_frame = ttk.Frame(self.frame)
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._filter_contacts)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 统计信息框架
        stats_frame = ttk.Frame(self.frame)
        self.stats_label = ttk.Label(
            stats_frame, text="总计: 0 个联系人 | 已选择: 0 个"
        )
        self.stats_label.pack()

        # 分隔线
        separator = ttk.Separator(self.frame, orient=tk.HORIZONTAL)

        # 联系人列表框架
        list_frame = ttk.LabelFrame(self.frame, text="联系人列表", padding="5")

        # 创建Treeview
        columns = ("selected", "wxid", "nickname", "remark", "type", "member_count")
        self.contact_tree = ttk.Treeview(
            list_frame, columns=columns, show="tree headings", height=15
        )

        # 设置列标题和宽度
        self.contact_tree.heading("#0", text="头像")
        self.contact_tree.heading("selected", text="选择")
        self.contact_tree.heading("wxid", text="微信ID")
        self.contact_tree.heading("nickname", text="昵称")
        self.contact_tree.heading("remark", text="备注")
        self.contact_tree.heading("type", text="类型")
        self.contact_tree.heading("member_count", text="成员数")

        self.contact_tree.column("#0", width=50)
        self.contact_tree.column("selected", width=60)
        self.contact_tree.column("wxid", width=200)
        self.contact_tree.column("nickname", width=150)
        self.contact_tree.column("remark", width=150)
        self.contact_tree.column("type", width=80)
        self.contact_tree.column("member_count", width=80)

        # 添加滚动条
        tree_scrollbar_v = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.contact_tree.yview
        )
        tree_scrollbar_h = ttk.Scrollbar(
            list_frame, orient=tk.HORIZONTAL, command=self.contact_tree.xview
        )
        self.contact_tree.configure(
            yscrollcommand=tree_scrollbar_v.set, xscrollcommand=tree_scrollbar_h.set
        )

        # 绑定事件
        self.contact_tree.bind("<Double-1>", self._on_double_click)
        self.contact_tree.bind("<Button-3>", self._show_context_menu)

        # 创建右键菜单
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="查看详情", command=self._view_details)
        self.context_menu.add_command(
            label="选择此联系人", command=self._select_current
        )
        self.context_menu.add_command(
            label="导出此联系人", command=self._export_current
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(label="复制微信ID", command=self._copy_wxid)

        # 详情框架
        detail_frame = ttk.LabelFrame(self.frame, text="联系人详情", padding="5")
        self.detail_text = tk.Text(
            detail_frame, height=6, wrap=tk.WORD, state=tk.DISABLED
        )
        detail_scrollbar = ttk.Scrollbar(
            detail_frame, orient=tk.VERTICAL, command=self.detail_text.yview
        )
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, variable=self.progress_var, mode="indeterminate"
        )

        # 状态标签
        self.status_label = ttk.Label(
            self.frame, text="请先解密数据库", foreground="blue"
        )

        # 保存组件引用
        self.title_frame = title_frame
        self.control_frame = control_frame
        self.search_frame = search_frame
        self.stats_frame = stats_frame
        self.separator = separator
        self.list_frame = list_frame
        self.tree_scrollbar_v = tree_scrollbar_v
        self.tree_scrollbar_h = tree_scrollbar_h
        self.detail_frame = detail_frame
        self.detail_scrollbar = detail_scrollbar

    def _layout_widgets(self):
        """布局UI组件"""
        # 垂直布局
        self.title_frame.pack(fill=tk.X, pady=(0, 10))
        self.control_frame.pack(fill=tk.X, pady=(0, 5))
        self.search_frame.pack(fill=tk.X, pady=(0, 5))
        self.stats_frame.pack(fill=tk.X, pady=(0, 10))
        self.separator.pack(fill=tk.X, pady=(0, 10))

        # 联系人列表区域
        self.list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.contact_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)

        # 详情区域
        self.detail_frame.pack(fill=tk.X, pady=(0, 10))
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        self.status_label.pack(fill=tk.X)

    def _setup_initial_state(self):
        """设置初始状态"""
        self._update_ui_state()

    def _refresh_contacts(self):
        """刷新联系人列表"""
        if not self.app_state.db_dir:
            messagebox.showwarning("警告", "请先解密数据库")
            return

        self.refresh_button.config(state=tk.DISABLED)
        self.status_label.config(text="正在加载联系人...", foreground="orange")
        self.progress_bar.start()

        self.controller.load_contacts()

    def _select_all(self):
        """全选联系人"""
        for contact in self.contacts:
            self.app_state.add_selected_contact(contact.wxid)
        self._update_contact_list()
        self._update_stats()

    def _clear_selection(self):
        """清空选择"""
        self.app_state.clear_selected_contacts()
        self._update_contact_list()
        self._update_stats()

    def _export_selected(self):
        """导出选中的联系人"""
        selected_contacts = self.app_state.selected_contacts
        if not selected_contacts:
            messagebox.showwarning("警告", "请先选择要导出的联系人")
            return

        # 切换到导出标签页
        self.parent.parent.parent.notebook.select(2)  # 导出标签页索引

    def _filter_contacts(self, *args):
        """过滤联系人"""
        search_text = self.search_var.get().lower()
        self._update_contact_list(search_text)

    def _on_double_click(self, event):
        """双击事件"""
        self._view_details()

    def _show_context_menu(self, event):
        """显示右键菜单"""
        item = self.contact_tree.identify("item", event.x, event.y)
        if item:
            self.contact_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _view_details(self):
        """查看联系人详情"""
        selection = self.contact_tree.selection()
        if not selection:
            return

        item = self.contact_tree.item(selection[0])
        wxid = item["values"][0]

        contact = None
        for c in self.contacts:
            if c.wxid == wxid:
                contact = c
                break

        if contact:
            self._show_contact_detail(contact)

    def _show_contact_detail(self, contact: ContactInfo):
        """显示联系人详情"""
        detail_text = f"""微信ID: {contact.wxid}
昵称: {contact.nickname}
备注: {contact.remark}
类型: {'群聊' if contact.is_chatroom else '个人'}
{f'成员数量: {contact.member_count}' if contact.is_chatroom else ''}"""

        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(tk.END, detail_text)
        self.detail_text.config(state=tk.DISABLED)

    def _select_current(self):
        """选择当前联系人"""
        selection = self.contact_tree.selection()
        if not selection:
            return

        item = self.contact_tree.item(selection[0])
        wxid = item["values"][0]

        if wxid in self.app_state.selected_contacts:
            self.app_state.remove_selected_contact(wxid)
        else:
            self.app_state.add_selected_contact(wxid)

        self._update_contact_list()
        self._update_stats()

    def _export_current(self):
        """导出当前联系人"""
        selection = self.contact_tree.selection()
        if not selection:
            return

        item = self.contact_tree.item(selection[0])
        wxid = item["values"][0]

        # 添加到导出任务
        export_format = self.app_state.get_setting("default_export_format", "HTML")
        output_dir = self.app_state.get_setting("default_output_dir", "./output")

        if self.controller.add_export_task(wxid, export_format, output_dir):
            # 切换到导出标签页
            self.parent.parent.parent.notebook.select(2)

    def _copy_wxid(self):
        """复制微信ID"""
        selection = self.contact_tree.selection()
        if not selection:
            return

        item = self.contact_tree.item(selection[0])
        wxid = item["values"][0]

        self.frame.clipboard_clear()
        self.frame.clipboard_append(wxid)
        messagebox.showinfo("成功", f"微信ID {wxid} 已复制到剪贴板")

    def _update_contact_list(self, search_text: str = ""):
        """更新联系人列表"""
        # 清空现有项
        for item in self.contact_tree.get_children():
            self.contact_tree.delete(item)

        # 添加联系人
        for contact in self.contacts:
            # 过滤
            if search_text:
                if (
                    search_text not in contact.wxid.lower()
                    and search_text not in contact.nickname.lower()
                    and search_text not in contact.remark.lower()
                ):
                    continue

            # 选中状态
            selected = "✓" if contact.wxid in self.app_state.selected_contacts else ""

            # 类型
            contact_type = "群聊" if contact.is_chatroom else "个人"

            # 成员数
            member_count = (
                str(contact.member_count)
                if contact.is_chatroom and contact.member_count > 0
                else ""
            )

            self.contact_tree.insert(
                "",
                tk.END,
                values=(
                    contact.wxid,
                    selected,
                    contact.wxid,
                    contact.nickname,
                    contact.remark,
                    contact_type,
                    member_count,
                ),
            )

    def _update_stats(self):
        """更新统计信息"""
        total = len(self.contacts)
        selected = len(self.app_state.selected_contacts)
        self.stats_label.config(text=f"总计: {total} 个联系人 | 已选择: {selected} 个")

    def _update_ui_state(self):
        """更新UI状态"""
        has_database = bool(self.app_state.db_dir)
        has_contacts = len(self.contacts) > 0
        has_selected = len(self.app_state.selected_contacts) > 0

        self.refresh_button.config(state=tk.NORMAL if has_database else tk.DISABLED)
        self.select_all_button.config(state=tk.NORMAL if has_contacts else tk.DISABLED)
        self.clear_selection_button.config(
            state=tk.NORMAL if has_selected else tk.DISABLED
        )
        self.export_selected_button.config(
            state=tk.NORMAL if has_selected else tk.DISABLED
        )

    def on_contacts_loaded(self, contacts: List[ContactInfo]):
        """联系人加载完成回调"""
        self.contacts = contacts
        self._update_contact_list()
        self._update_stats()

        self.refresh_button.config(state=tk.NORMAL)
        self.progress_bar.stop()

        if contacts:
            self.status_label.config(
                text=f"加载完成，共 {len(contacts)} 个联系人", foreground="green"
            )
        else:
            self.status_label.config(text="未找到联系人", foreground="orange")

        self._update_ui_state()
