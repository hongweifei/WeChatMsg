#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File        : controller.py
@Description : 主控制器，连接视图和模型
@Author      : Claude Code
@Time        : 2025/11/27
"""

import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exporter import (
    AiTxtExporter,
    DocxExporter,
    ExcelExporter,
    HtmlExporter,
    MarkdownExporter,
    TxtExporter,
)
from exporter.config import FileType
from wxManager import DatabaseConnection, Me
from wxManager.decrypt import decrypt_v3, decrypt_v4, get_info_v3, get_info_v4
from wxManager.decrypt.decrypt_dat import get_decode_code_v4

from gui.models.app_state import (
    AppState,
    ContactInfo,
    ExportTask,
    ProcessingStatus,
    WeChatVersion,
    WxAccountInfo,
)


class MainController:
    """主控制器类"""

    def __init__(self, app_state: AppState):
        self.app_state = app_state
        self._db_connection: Optional[DatabaseConnection] = None
        self._database = None
        self._callbacks: Dict[str, List[Callable]] = {}

    def add_callback(self, event: str, callback: Callable):
        """添加事件回调"""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)

    def _notify_callbacks(self, event: str, *args, **kwargs):
        """通知回调函数"""
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"回调函数执行错误: {e}")

    def update_status(self, status: ProcessingStatus, message: str = ""):
        """更新应用状态"""
        self.app_state.status = status
        if message:
            self.app_state.status_message = message
        self._notify_callbacks("status_changed", status, message)

    def scan_wechat_accounts(self) -> List[WxAccountInfo]:
        """扫描微信账户"""
        self.update_status(ProcessingStatus.DECRYPTING, "正在扫描微信账户...")

        def scan_thread():
            try:
                accounts = []

                # 扫描微信4.0版本
                try:
                    wx_info_list_v4 = get_info_v4()
                    for wx_info in wx_info_list_v4:
                        me = Me()
                        me.wx_dir = wx_info.wx_dir
                        me.wxid = wx_info.wxid
                        me.name = wx_info.nick_name

                        account = WxAccountInfo(
                            wxid=wx_info.wxid,
                            name=wx_info.nick_name,
                            wx_dir=wx_info.wx_dir,
                            key=wx_info.key,
                            version=WeChatVersion.V4,
                            output_dir=wx_info.wxid,
                        )

                        if wx_info.key:
                            try:
                                account.xor_key = get_decode_code_v4(wx_info.wx_dir)
                            except Exception:
                                account.xor_key = None

                        accounts.append(account)
                except Exception as e:
                    print(f"扫描微信4.0失败: {e}")

                # 扫描微信3.x版本
                try:
                    import json

                    version_list_path = os.path.join(
                        os.path.dirname(__file__),
                        "..",
                        "wxManager",
                        "decrypt",
                        "version_list.json",
                    )
                    with open(version_list_path, "r", encoding="utf-8") as f:
                        version_list = json.loads(f.read())

                    wx_info_list_v3 = get_info_v3(version_list)
                    for wx_info in wx_info_list_v3:
                        me = Me()
                        me.wx_dir = wx_info.wx_dir
                        me.wxid = wx_info.wxid
                        me.name = wx_info.nick_name

                        account = WxAccountInfo(
                            wxid=wx_info.wxid,
                            name=wx_info.nick_name,
                            wx_dir=wx_info.wx_dir,
                            key=wx_info.key,
                            version=WeChatVersion.V3,
                            output_dir=wx_info.wxid,
                        )

                        accounts.append(account)
                except Exception as e:
                    print(f"扫描微信3.x失败: {e}")

                # 更新状态
                for account in accounts:
                    self.app_state.add_wx_account(account)

                self.update_status(
                    ProcessingStatus.IDLE, f"扫描完成，找到 {len(accounts)} 个微信账户"
                )
                self._notify_callbacks("accounts_scanned", accounts)

            except Exception as e:
                error_msg = f"扫描微信账户失败: {str(e)}"
                self.update_status(ProcessingStatus.ERROR, error_msg)
                self._notify_callbacks("error", error_msg)

        threading.Thread(target=scan_thread, daemon=True).start()
        return self.app_state.wx_accounts

    def decrypt_database(self, account: WxAccountInfo) -> bool:
        """解密数据库"""
        if not account.key:
            self._notify_callbacks("error", "未找到密钥，请重启微信后再试")
            return False

        self.update_status(
            ProcessingStatus.DECRYPTING, f"正在解密 {account.name} 的数据库..."
        )

        def decrypt_thread():
            try:
                success = False
                if account.version == WeChatVersion.V4:
                    decrypt_v4.decrypt_db_files(
                        account.key, src_dir=account.wx_dir, dest_dir=account.output_dir
                    )
                    # 微信4.0的数据库在 db_storage 文件夹下
                    db_path = os.path.join(account.output_dir, "db_storage")
                    if os.path.exists(db_path):
                        success = True
                        self.app_state.db_dir = db_path
                        self.app_state.db_version = 4

                elif account.version == WeChatVersion.V3:
                    decrypt_v3.decrypt_db_files(
                        account.key, src_dir=account.wx_dir, dest_dir=account.output_dir
                    )
                    # 微信3.x的数据库在 Msg 文件夹下
                    db_path = os.path.join(account.output_dir, "Msg")
                    if os.path.exists(db_path):
                        success = True
                        self.app_state.db_dir = db_path
                        self.app_state.db_version = 3

                if success:
                    # 保存账户信息
                    import json

                    me = Me()
                    me.wx_dir = account.wx_dir
                    me.wxid = account.wxid
                    me.name = account.name
                    info_data = me.to_json()

                    info_file = os.path.join(
                        account.output_dir,
                        "db_storage" if account.version == WeChatVersion.V4 else "Msg",
                        "info.json",
                    )
                    with open(info_file, "w", encoding="utf-8") as f:
                        json.dump(info_data, f, ensure_ascii=False, indent=4)

                    self.app_state.current_account = account
                    self.update_status(ProcessingStatus.IDLE, "数据库解密成功")
                    self._notify_callbacks("database_decrypted", account, True)
                else:
                    raise Exception("解密失败，输出目录未找到")

            except Exception as e:
                error_msg = f"解密数据库失败: {str(e)}"
                self.update_status(ProcessingStatus.ERROR, error_msg)
                self._notify_callbacks("database_decrypted", account, False, error_msg)

        threading.Thread(target=decrypt_thread, daemon=True).start()
        return True

    def load_contacts(self) -> List[ContactInfo]:
        """加载联系人列表"""
        if not self.app_state.db_dir:
            self._notify_callbacks("error", "请先解密数据库")
            return []

        self.update_status(ProcessingStatus.LOADING_CONTACTS, "正在加载联系人...")

        def load_thread():
            try:
                if not self._db_connection:
                    self._db_connection = DatabaseConnection(
                        self.app_state.db_dir, self.app_state.db_version
                    )
                    self._database = self._db_connection.get_interface()

                contacts = []
                db_contacts = self._database.get_contacts()

                for contact in db_contacts:
                    contact_info = ContactInfo(
                        wxid=contact.wxid,
                        nickname=contact.nickname or "",
                        remark=contact.remark or "",
                        is_chatroom=contact.is_chatroom,
                        member_count=0,
                    )

                    # 获取头像
                    try:
                        avatar_buffer = self._database.get_avatar_buffer(contact.wxid)
                        if avatar_buffer:
                            # 这里可以保存头像到临时文件，暂时用URL占位
                            contact_info.avatar_url = f"avatar_{contact.wxid}.jpg"
                    except Exception:
                        pass

                    # 如果是群聊，获取成员数量
                    if contact.is_chatroom:
                        try:
                            members = self._database.get_chatroom_members(contact.wxid)
                            contact_info.member_count = len(members)
                        except Exception:
                            pass

                    contacts.append(contact_info)

                self.app_state.set_contacts(contacts)
                self.update_status(
                    ProcessingStatus.IDLE, f"加载完成，共 {len(contacts)} 个联系人"
                )
                self._notify_callbacks("contacts_loaded", contacts)

            except Exception as e:
                error_msg = f"加载联系人失败: {str(e)}"
                self.update_status(ProcessingStatus.ERROR, error_msg)
                self._notify_callbacks("error", error_msg)

        threading.Thread(target=load_thread, daemon=True).start()
        return self.app_state.contacts

    def add_export_task(
        self, contact_wxid: str, export_format: str, output_dir: str = None, **kwargs
    ) -> bool:
        """添加导出任务"""
        if not self.app_state.db_dir:
            self._notify_callbacks("error", "请先解密数据库并加载联系人")
            return False

        if not output_dir:
            output_dir = self.app_state.get_setting("default_output_dir", "./output")

        task = ExportTask(
            contact_wxid=contact_wxid,
            export_format=export_format,
            output_dir=output_dir,
            message_types=kwargs.get("message_types"),
            time_range=kwargs.get("time_range"),
            group_members=kwargs.get("group_members"),
        )

        self.app_state.add_export_task(task)
        self._notify_callbacks("export_task_added", task)
        return True

    def execute_export_tasks(self) -> bool:
        """执行导出任务"""
        if not self.app_state.export_tasks:
            self._notify_callbacks("error", "没有导出任务")
            return False

        if not self._database:
            self._notify_callbacks("error", "数据库未连接")
            return False

        def export_thread():
            try:
                self.update_status(ProcessingStatus.EXPORTING, "正在导出聊天记录...")

                # 导出器映射
                exporters = {
                    "HTML": HtmlExporter,
                    "TXT": TxtExporter,
                    "AI_TXT": AiTxtExporter,
                    "MARKDOWN": MarkdownExporter,
                    "XLSX": ExcelExporter,
                    "DOCX": DocxExporter,
                }

                tasks = self.app_state.export_tasks.copy()
                self.app_state.clear_export_tasks()

                for i, task in enumerate(tasks):
                    try:
                        self.update_status(
                            ProcessingStatus.EXPORTING,
                            f"正在导出 {task.contact_wxid} ({i+1}/{len(tasks)})...",
                        )

                        # 获取联系人信息
                        contact = self._database.get_contact_by_username(
                            task.contact_wxid
                        )
                        if not contact:
                            raise Exception(f"未找到联系人: {task.contact_wxid}")

                        # 创建导出器
                        exporter_class = exporters.get(task.export_format)
                        if not exporter_class:
                            raise Exception(f"不支持的导出格式: {task.export_format}")

                        exporter = exporter_class(
                            self._database,
                            contact,
                            output_dir=task.output_dir,
                            message_types=task.message_types,
                            time_range=task.time_range
                            or [
                                self.app_state.get_setting("time_range_start"),
                                self.app_state.get_setting("time_range_end"),
                            ],
                            group_members=task.group_members,
                        )

                        # 执行导出
                        exporter.start()

                        self._notify_callbacks("export_completed", task, True, None)

                    except Exception as e:
                        error_msg = f"导出 {task.contact_wxid} 失败: {str(e)}"
                        self._notify_callbacks(
                            "export_completed", task, False, error_msg
                        )

                self.update_status(ProcessingStatus.IDLE, "所有导出任务完成")

            except Exception as e:
                error_msg = f"导出过程出错: {str(e)}"
                self.update_status(ProcessingStatus.ERROR, error_msg)
                self._notify_callbacks("error", error_msg)

        threading.Thread(target=export_thread, daemon=True).start()
        return True

    def select_output_directory(self) -> str:
        """选择输出目录"""
        from tkinter import filedialog

        directory = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=self.app_state.get_setting("default_output_dir", "./output"),
        )
        if directory:
            self.app_state.set_setting("default_output_dir", directory)
        return directory

    def cleanup(self):
        """清理资源"""
        try:
            if self._db_connection:
                # 这里可以添加数据库连接的清理代码
                pass
        except Exception:
            pass

        self.app_state.reset()
