#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File        : decrypt_tab.py
@Description : 解密标签页
@Author      : Claude Code
@Time        : 2025/11/27
"""

import os
import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Optional

from gui.models.app_state import ProcessingStatus, WxAccountInfo


class DecryptTab:
    """解密数据库标签页"""

    def __init__(self, parent, controller, app_state):
        self.parent = parent
        self.controller = controller
        self.app_state = app_state
        self.scanned_accounts: List[WxAccountInfo] = []

        self._create_widgets()
        self._layout_widgets()
        self._setup_initial_state()

    def _create_widgets(self):
        """创建UI组件"""
        # 主框架
        self.frame = ttk.Frame(self.parent)

        # 标题
        title_frame = ttk.Frame(self.frame)
        self.title_label = ttk.Label(
            title_frame, text="微信数据库解密", font=("Arial", 14, "bold")
        )
        self.title_label.pack()

        # 说明文本
        desc_frame = ttk.Frame(self.frame)
        self.desc_text = tk.Text(desc_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        desc_scrollbar = ttk.Scrollbar(
            desc_frame, orient=tk.VERTICAL, command=self.desc_text.yview
        )
        self.desc_text.configure(yscrollcommand=desc_scrollbar.set)

        desc_content = """使用说明：
1. 确保微信客户端正在运行
2. 点击"扫描微信账户"按钮
3. 选择要解密的微信账户
4. 点击"开始解密"按钮
5. 等待解密完成

注意：解密过程会在当前目录创建以wxid命名的文件夹，用于存储解密后的数据库文件。"""

        self.desc_text.config(state=tk.NORMAL)
        self.desc_text.insert(tk.END, desc_content)
        self.desc_text.config(state=tk.DISABLED)

        # 控制按钮框架
        button_frame = ttk.Frame(self.frame)
        self.scan_button = ttk.Button(
            button_frame, text="扫描微信账户", command=self._scan_accounts
        )
        self.scan_button.pack(side=tk.LEFT, padx=5)

        self.refresh_button = ttk.Button(
            button_frame, text="刷新", command=self._refresh_accounts
        )
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        # 分隔线
        separator1 = ttk.Separator(self.frame, orient=tk.HORIZONTAL)

        # 账户列表框架
        list_frame = ttk.LabelFrame(self.frame, text="微信账户列表", padding="10")

        # 创建Treeview
        columns = ("wxid", "name", "version", "status")
        self.account_tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", height=8
        )

        # 设置列标题和宽度
        self.account_tree.heading("wxid", text="微信ID")
        self.account_tree.heading("name", text="昵称")
        self.account_tree.heading("version", text="版本")
        self.account_tree.heading("status", text="状态")

        self.account_tree.column("wxid", width=200)
        self.account_tree.column("name", width=150)
        self.account_tree.column("version", width=80)
        self.account_tree.column("status", width=100)

        # 添加滚动条
        tree_scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.account_tree.yview
        )
        self.account_tree.configure(yscrollcommand=tree_scrollbar.set)

        # 选中事件
        self.account_tree.bind("<<TreeviewSelect>>", self._on_account_select)

        # 账户详情框架
        detail_frame = ttk.LabelFrame(self.frame, text="账户详情", padding="10")

        # 详情标签
        self.detail_labels = {}
        details = [
            ("wxid_label", "微信ID:"),
            ("name_label", "昵称:"),
            ("version_label", "版本:"),
            ("path_label", "路径:"),
            ("key_status_label", "密钥状态:"),
            ("output_dir_label", "输出目录:"),
        ]

        for i, (key, text) in enumerate(details):
            ttk.Label(detail_frame, text=text).grid(
                row=i, column=0, sticky=tk.W, pady=2
            )
            self.detail_labels[key] = ttk.Label(detail_frame, text="--")
            self.detail_labels[key].grid(
                row=i, column=1, sticky=tk.W, pady=2, padx=(10, 0)
            )

        detail_frame.columnconfigure(1, weight=1)

        # 解密按钮框架
        decrypt_button_frame = ttk.Frame(self.frame)
        self.decrypt_button = ttk.Button(
            decrypt_button_frame,
            text="开始解密",
            command=self._start_decrypt,
            state=tk.DISABLED,
        )
        self.decrypt_button.pack(side=tk.LEFT, padx=5)

        self.open_output_button = ttk.Button(
            decrypt_button_frame,
            text="打开输出目录",
            command=self._open_output_dir,
            state=tk.DISABLED,
        )
        self.open_output_button.pack(side=tk.LEFT, padx=5)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, variable=self.progress_var, mode="indeterminate"
        )

        # 状态标签
        self.status_label = ttk.Label(self.frame, text="准备就绪", foreground="blue")

        # 保存组件引用
        self.title_frame = title_frame
        self.desc_frame = desc_frame
        self.desc_scrollbar = desc_scrollbar
        self.button_frame = button_frame
        self.separator1 = separator1
        self.list_frame = list_frame
        self.tree_scrollbar = tree_scrollbar
        self.detail_frame = detail_frame
        self.decrypt_button_frame = decrypt_button_frame

    def _layout_widgets(self):
        """布局UI组件"""
        # 垂直布局
        self.title_frame.pack(fill=tk.X, pady=(0, 10))

        self.desc_frame.pack(fill=tk.X, pady=(0, 10))
        self.desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.button_frame.pack(fill=tk.X, pady=(0, 10))

        self.separator1.pack(fill=tk.X, pady=(0, 10))

        self.list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.account_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.detail_frame.pack(fill=tk.X, pady=(0, 10))

        self.decrypt_button_frame.pack(fill=tk.X, pady=(0, 10))

        self.progress_bar.pack(fill=tk.X, pady=(0, 5))

        self.status_label.pack(fill=tk.X)

    def _setup_initial_state(self):
        """设置初始状态"""
        self._update_ui_state()

    def _scan_accounts(self):
        """扫描微信账户"""
        self.scan_button.config(state=tk.DISABLED)
        self.status_label.config(text="正在扫描微信账户...", foreground="orange")
        self.progress_bar.start()

        # 扫描账户
        self.controller.scan_wechat_accounts()

    def _refresh_accounts(self):
        """刷新账户列表"""
        self.scanned_accounts = self.app_state.wx_accounts
        self._update_account_list()
        self._update_ui_state()

    def _on_account_select(self, event):
        """账户选择事件"""
        selection = self.account_tree.selection()
        if selection:
            item = self.account_tree.item(selection[0])
            wxid = item["values"][0]

            # 查找账户信息
            account = None
            for acc in self.scanned_accounts:
                if acc.wxid == wxid:
                    account = acc
                    break

            if account:
                self._show_account_detail(account)

        self._update_ui_state()

    def _show_account_detail(self, account: WxAccountInfo):
        """显示账户详情"""
        self.detail_labels["wxid_label"].config(text=account.wxid)
        self.detail_labels["name_label"].config(text=account.name)
        self.detail_labels["version_label"].config(text=account.version.value)
        self.detail_labels["path_label"].config(text=account.wx_dir)
        self.detail_labels["key_status_label"].config(
            text="已获取" if account.key else "未获取",
            foreground="green" if account.key else "red",
        )
        self.detail_labels["output_dir_label"].config(text=account.output_dir)

    def _start_decrypt(self):
        """开始解密"""
        selection = self.account_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要解密的微信账户")
            return

        item = self.account_tree.item(selection[0])
        wxid = item["values"][0]

        # 查找账户信息
        account = None
        for acc in self.scanned_accounts:
            if acc.wxid == wxid:
                account = acc
                break

        if not account:
            messagebox.showerror("错误", "未找到选中的账户信息")
            return

        if not account.key:
            messagebox.showerror("错误", "该账户未获取到密钥，请重启微信后重试")
            return

        # 确认解密
        if not messagebox.askyesno(
            "确认解密",
            f"确定要解密账户 {account.name}({account.wxid}) 的数据库吗？\n\n"
            f"输出目录: {account.output_dir}\n\n"
            "这个过程可能需要几分钟时间。",
        ):
            return

        # 开始解密
        self.decrypt_button.config(state=tk.DISABLED)
        self.status_label.config(text="正在解密数据库...", foreground="orange")
        self.progress_bar.start()

        self.controller.decrypt_database(account)

    def _open_output_dir(self):
        """打开输出目录"""
        import os
        import subprocess

        selection = self.account_tree.selection()
        if not selection:
            return

        item = self.account_tree.item(selection[0])
        wxid = item["values"][0]

        account = None
        for acc in self.scanned_accounts:
            if acc.wxid == wxid:
                account = acc
                break

        if account and account.output_dir and os.path.exists(account.output_dir):
            try:
                subprocess.run(["explorer", account.output_dir], check=True)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开目录: {str(e)}")

    def _update_account_list(self):
        """更新账户列表"""
        # 清空现有项
        for item in self.account_tree.get_children():
            self.account_tree.delete(item)

        # 添加账户
        for account in self.scanned_accounts:
            status = "就绪"
            if account.output_dir and os.path.exists(account.output_dir):
                status = "已解密"

            self.account_tree.insert(
                "",
                tk.END,
                values=(account.wxid, account.name, account.version.value, status),
            )

    def _update_ui_state(self):
        """更新UI状态"""
        has_accounts = len(self.scanned_accounts) > 0
        has_selection = bool(self.account_tree.selection())

        self.refresh_button.config(state=tk.NORMAL if has_accounts else tk.DISABLED)
        self.decrypt_button.config(
            state=tk.NORMAL
            if has_selection and self.app_state.status != ProcessingStatus.DECRYPTING
            else tk.DISABLED
        )

        # 检查是否有已解密的账户
        selection = self.account_tree.selection()
        can_open_output = False
        if selection:
            item = self.account_tree.item(selection[0])
            wxid = item["values"][0]
            for acc in self.scanned_accounts:
                if (
                    acc.wxid == wxid
                    and acc.output_dir
                    and os.path.exists(acc.output_dir)
                ):
                    can_open_output = True
                    break

        self.open_output_button.config(
            state=tk.NORMAL if can_open_output else tk.DISABLED
        )

    def on_accounts_scanned(self, accounts: List[WxAccountInfo]):
        """账户扫描完成回调"""
        self.scanned_accounts = accounts
        self._update_account_list()

        self.scan_button.config(state=tk.NORMAL)
        self.progress_bar.stop()

        if accounts:
            self.status_label.config(
                text=f"扫描完成，找到 {len(accounts)} 个微信账户", foreground="green"
            )
        else:
            self.status_label.config(
                text="未找到微信账户，请确保微信正在运行", foreground="red"
            )

        self._update_ui_state()

    def on_database_decrypted(
        self, account: WxAccountInfo, success: bool, error_msg: str = None
    ):
        """数据库解密完成回调"""
        self.decrypt_button.config(state=tk.NORMAL)
        self.progress_bar.stop()

        if success:
            self.status_label.config(text="数据库解密成功", foreground="green")
            # 更新账户列表中的状态
            self._update_account_list()
            messagebox.showinfo(
                "成功", f"数据库解密成功！\n输出目录: {account.output_dir}"
            )
        else:
            self.status_label.config(text=f"解密失败: {error_msg}", foreground="red")
            messagebox.showerror("解密失败", error_msg)

        self._update_ui_state()
