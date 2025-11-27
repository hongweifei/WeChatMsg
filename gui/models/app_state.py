#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@File        : app_state.py
@Description : 应用状态管理
@Author      : Claude Code
@Time        : 2025/11/27
"""

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ProcessingStatus(Enum):
    """处理状态枚举"""

    IDLE = "idle"
    DECRYPTING = "decrypting"
    LOADING_CONTACTS = "loading_contacts"
    EXPORTING = "exporting"
    ERROR = "error"


class WeChatVersion(Enum):
    """微信版本枚举"""

    V3 = "3.x"
    V4 = "4.0"
    UNKNOWN = "unknown"


@dataclass
class WxAccountInfo:
    """微信账户信息"""

    wxid: str
    name: str = ""
    wx_dir: str = ""
    key: Optional[str] = None
    xor_key: Optional[str] = None
    version: WeChatVersion = WeChatVersion.UNKNOWN
    output_dir: str = ""


@dataclass
class ContactInfo:
    """联系人信息"""

    wxid: str
    nickname: str = ""
    remark: str = ""
    avatar_url: str = ""
    is_chatroom: bool = False
    member_count: int = 0


@dataclass
class ExportTask:
    """导出任务信息"""

    contact_wxid: str
    export_format: str
    output_dir: str
    message_types: Optional[List[str]] = None
    time_range: Optional[List[str]] = None
    group_members: Optional[List[str]] = None
    status: str = "pending"


class AppState:
    """应用状态管理类"""

    def __init__(self):
        # 当前处理状态
        self._status = ProcessingStatus.IDLE
        self._status_message = "就绪"

        # 微信账户信息
        self._wx_accounts: List[WxAccountInfo] = []
        self._current_account: Optional[WxAccountInfo] = None

        # 数据库连接信息
        self._db_dir: Optional[str] = None
        self._db_version: Optional[int] = None

        # 联系人信息
        self._contacts: List[ContactInfo] = []
        self._selected_contacts: List[str] = []

        # 导出任务
        self._export_tasks: List[ExportTask] = []

        # 设置
        self._settings: Dict[str, Any] = {
            "default_output_dir": "./output",
            "default_export_format": "HTML",
            "auto_detect_version": True,
            "max_threads": 4,
            "time_range_start": "2020-01-01 00:00:00",
            "time_range_end": "2035-12-31 23:59:59",
        }

        # 加载设置
        self._load_settings()

    @property
    def status(self) -> ProcessingStatus:
        return self._status

    @status.setter
    def status(self, value: ProcessingStatus):
        self._status = value

    @property
    def status_message(self) -> str:
        return self._status_message

    @status_message.setter
    def status_message(self, value: str):
        self._status_message = value

    @property
    def wx_accounts(self) -> List[WxAccountInfo]:
        return self._wx_accounts.copy()

    def add_wx_account(self, account: WxAccountInfo):
        """添加微信账户"""
        # 检查是否已存在
        for existing in self._wx_accounts:
            if existing.wxid == account.wxid:
                # 更新现有账户
                self._wx_accounts.remove(existing)
                break
        self._wx_accounts.append(account)

    @property
    def current_account(self) -> Optional[WxAccountInfo]:
        return self._current_account

    @current_account.setter
    def current_account(self, account: Optional[WxAccountInfo]):
        self._current_account = account

    @property
    def db_dir(self) -> Optional[str]:
        return self._db_dir

    @db_dir.setter
    def db_dir(self, value: Optional[str]):
        self._db_dir = value

    @property
    def db_version(self) -> Optional[int]:
        return self._db_version

    @db_version.setter
    def db_version(self, value: Optional[int]):
        self._db_version = value

    @property
    def contacts(self) -> List[ContactInfo]:
        return self._contacts.copy()

    def set_contacts(self, contacts: List[ContactInfo]):
        """设置联系人列表"""
        self._contacts = contacts
        self._selected_contacts = []

    @property
    def selected_contacts(self) -> List[str]:
        return self._selected_contacts.copy()

    def add_selected_contact(self, wxid: str):
        """添加选中的联系人"""
        if wxid not in self._selected_contacts:
            self._selected_contacts.append(wxid)

    def remove_selected_contact(self, wxid: str):
        """移除选中的联系人"""
        if wxid in self._selected_contacts:
            self._selected_contacts.remove(wxid)

    def clear_selected_contacts(self):
        """清空选中的联系人"""
        self._selected_contacts = []

    @property
    def export_tasks(self) -> List[ExportTask]:
        return self._export_tasks.copy()

    def add_export_task(self, task: ExportTask):
        """添加导出任务"""
        self._export_tasks.append(task)

    def remove_export_task(self, index: int):
        """移除导出任务"""
        if 0 <= index < len(self._export_tasks):
            del self._export_tasks[index]

    def clear_export_tasks(self):
        """清空导出任务"""
        self._export_tasks = []

    @property
    def settings(self) -> Dict[str, Any]:
        return self._settings.copy()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """获取设置项"""
        return self._settings.get(key, default)

    def set_setting(self, key: str, value: Any):
        """设置配置项"""
        self._settings[key] = value
        self._save_settings()

    def _load_settings(self):
        """加载设置"""
        try:
            settings_file = "gui_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                    self._settings.update(loaded_settings)
        except Exception:
            # 如果加载失败，使用默认设置
            pass

    def _save_settings(self):
        """保存设置"""
        try:
            settings_file = "gui_settings.json"
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=2)
        except Exception:
            # 如果保存失败，忽略错误
            pass

    def reset(self):
        """重置状态"""
        self._status = ProcessingStatus.IDLE
        self._status_message = "就绪"
        self._current_account = None
        self._db_dir = None
        self._db_version = None
        self._contacts = []
        self._selected_contacts = []
        self._export_tasks = []
