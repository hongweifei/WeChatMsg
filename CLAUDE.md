# CLAUDE.md

这个文件为Claude Code (claude.ai/code)在处理此代码库时提供指导。

## 项目概述

留痕是一个专业的微信聊天记录解析和导出工具，支持微信4.0和3.x版本。项目采用模块化架构，提供多种格式的数据导出功能，同时集成AI分析能力。

## 开发环境设置

### Python版本要求
- **推荐版本**: Python 3.10+
- **最低版本**: Python 3.9 (由于Pillow 11.0.0依赖要求)
- **测试环境**: Python 3.10

### 依赖安装

#### 方法一: 传统 pip 方式
```bash
pip install -r requirements.txt
```

**注意**: 项目目前暂未完全支持UV依赖管理，请使用传统的pip方式安装依赖。

### 核心运行流程

```bash
# 1. 解密数据库
python example/1-decrypt.py

# 2. 查看联系人
python example/2-contact.py

# 3. 导出聊天记录
python example/3-exporter.py
```

## 项目架构

### 核心模块结构
- **wxManager/**: 核心功能模块
  - `db_main.py`: 数据库接口抽象基类 (DataBaseInterface)
  - `manager_v4.py`: 微信4.0版本数据库管理器 (DataBaseV4)
  - `manager_v3.py`: 微信3.x版本数据库管理器 (DataBaseV3)
  - `decrypt/`: 解密模块
    - `decrypt_v4.py`, `decrypt_v3.py`: 版本特定的数据库解密
    - `decrypt_dat.py`: DAT文件解密（图片等媒体文件）
    - `wxinfo.py`, `wx_info_v4.py`: 微信进程信息获取
    - `common.py`: 通用解密工具
  - `parser/`: 解析器模块
    - `wechat_v4.py`, `wechat_v3.py`: 微信版本特定解析器
    - `audio_parser.py`: 音频解析
    - `emoji_parser.py`: 表情解析
    - `file_parser.py`: 文件解析
    - `link_parser.py`: 链接解析
  - `log/`: 日志系统
  - `model/`: 数据模型
    - `message.py`: 消息类型定义 (Message, MessageType等)
    - `contact.py`: 联系人模型 (Contact, Person, Me等)
    - `db_model.py`: 数据库模型基类

- **wxManager/db_v4/**: 微信4.0数据库处理器
  - `contact.py`: 联系人数据库 (ContactDB)
  - `message.py`: 消息数据库 (MessageDB)
  - `session.py`: 会话数据库 (SessionDB)
  - `media.py`: 媒体数据库 (MediaDB)
  - `head_image.py`: 头像数据库 (HeadImageDB)
  - `hardlink.py`: 硬链接数据库 (HardLinkDB)
  - `emotion.py`: 表情数据库 (EmotionDB)
  - `biz_message.py`: 业务消息数据库 (BizMessageDB)
  - `audio2text.py`: 音频转文本数据库 (Audio2TextDB)

- **wxManager/db_v3/**: 微信3.x数据库处理器
  - `micro_msg.py`: MicroMsg.db处理器
  - `msg.py`: 消息处理器
  - `contact.py`: 联系人处理器
  - `media_msg.py`: 媒体消息处理器
  - `open_im_contact.py`: OpenIM联系人处理器
  - `open_im_media.py`: OpenIM媒体处理器
  - `open_im_msg.py`: OpenIM消息处理器
  - `hard_link_*.py`: 硬链接文件处理器

- **exporter/**: 导出器模块
  - `exporter.py`: 导出器基类 (ExporterBase) 和通用工具
  - `exporter_html.py`: HTML格式导出器 (HtmlExporter)
  - `exporter_txt.py`: TXT文本格式导出器 (TxtExporter)
  - `exporter_ai_txt.py`: AI分析文本导出器 (AiTxtExporter)
  - `exporter_docx.py`: Word文档导出器 (DocxExporter)
  - `exporter_markdown.py`: Markdown导出器 (MarkdownExporter)
  - `exporter_xlsx.py`: Excel导出器 (ExcelExporter)
  - `exporter_csv.py`: CSV导出器 (CsvExporter)
  - `exporter_json.py`: JSON导出器 (JsonExporter)
  - `config.py`: 导出配置 (FileType枚举)

- **gui/**: 图形用户界面（基于PyQt）
  - `core/`: 核心GUI组件
    - `controllers/`: 控制器层
    - `models/`: 模型层
    - `views/`: 视图层

- **MemoAI/**: AI扩展模块
  - `api_server.py`: API服务器（基于FastAPI）
  - `merge_json.py`: JSON数据合并工具
  - `qwen2-0.5b/`: Qwen2模型集成

- **example/**: 使用示例
  - `1-decrypt.py`: 数据库解密示例
  - `2-contact.py`: 联系人查询示例
  - `3-exporter.py`: 数据导出示例

### 版本兼容策略
项目使用策略模式和抽象工厂模式实现微信版本的兼容：

1. **抽象接口层**:
   - `DataBaseInterface` (wxManager/db_main.py): 定义数据库操作抽象接口
   - `DatabaseConnection` (wxManager/__init__.py): 数据库连接管理器

2. **版本实现层**:
   - `DataBaseV4` (wxManager/manager_v4.py): 微信4.0版本实现
   - `DataBaseV3` (wxManager/manager_v3.py): 微信3.x版本实现

3. **数据库处理器层**:
   - `wxManager/db_v4/*`: 微信4.0专用数据库处理器
   - `wxManager/db_v3/*`: 微信3.x专用数据库处理器

### 消息类型体系
完整支持微信各种消息类型（定义在 wxManager/model/message.py）：

- **基础消息类型**:
  - `TextMessage`: 文本消息
  - `ImageMessage`: 图片消息
  - `VideoMessage`: 视频消息
  - `AudioMessage`: 音频消息

- **特殊消息类型**:
  - `EmojiMessage`: 表情包
  - `QuoteMessage`: 引用消息
  - `MergedMessage`: 合并转发消息
  - `LinkMessage`: 链接消息
  - `PositionMessage`: 位置消息

- **系统消息类型**:
  - `FileMessage`: 文件消息
  - `SystemMsg`: 系统消息
  - 其他业务消息类型...

### 数据库架构设计

#### 微信4.0数据库结构
- **联系人与头像**: `Contact.db`, `HeadImage.db`
- **消息数据**: `Message.db` (使用zstd压缩)
- **会话管理**: `Session.db`
- **媒体文件**: `Media.db`, `HardLink.db`
- **表情数据**: `Emotion.db`
- **业务消息**: `BizMessage.db`

#### 微信3.x数据库结构
- **核心数据**: `MicroMsg.db`
- **消息数据**: `MSG.db`
- **媒体消息**: `MediaMSG.db`
- **联系人**: `WCDB_Contact.db`
- **OpenIM数据**: `OpenIMContact.wxpkg`, `OpenIMMedia.wxpkg`

## 开发指南

### 基本使用模式

#### 1. 数据库解密
```python
from wxManager.decrypt import get_info_v4, decrypt_v4

# 获取微信信息
wx_info_list = get_info_v4()
for wx_info in wx_info_list:
    # 解密数据库
    decrypt_v4.decrypt_db_files(wx_info.key, wx_info.wx_dir, output_dir)
```

#### 2. 数据库连接和查询
```python
from wxManager import DatabaseConnection

# 创建数据库连接
conn = DatabaseConnection(db_dir='./db_storage', db_version=4)
database = conn.get_interface()

# 获取联系人
contact = database.get_contact_by_username('wxid_00112233')

# 获取消息
messages = database.get_messages(
    username='wxid_00112233',
    time_range=('2024-01-01', '2024-12-31')
)
```

#### 3. 数据导出
```python
from exporter import HtmlExporter
from exporter.config import FileType

# 创建HTML导出器
exporter = HtmlExporter(
    database=database,
    contact=contact,
    output_dir='./output',
    type_=FileType.HTML,
    message_types=None,  # 导出所有类型
    time_range=None,     # 导出所有时间
    group_members=None   # 导出所有群成员
)

# 开始导出
exporter.start()
```

### 添加新的导出格式
1. 在 `exporter/` 目录下创建新的导出器类
2. 继承 `ExporterBase` 基类
3. 实现 `export()` 方法
4. 在 `exporter/config.py` 中的 `FileType` 枚举中添加新格式
5. 在使用示例中导入并使用新的导出器

```python
from exporter.exporter import ExporterBase

class CustomExporter(ExporterBase):
    def export(self):
        # 实现导出逻辑
        pass
```

### 支持新的微信版本
1. 在 `wxManager/decrypt/` 下添加版本特定的解密模块
2. 在 `wxManager/db_v*` 下创建版本特定的数据库处理器
3. 创建对应的数据库管理器（如 `manager_v5.py`）
4. 在 `DatabaseConnection` 中添加版本判断逻辑

### 扩展消息类型
1. 在 `wxManager/model/message.py` 中定义新的消息类型
2. 在对应的数据库处理器中添加解析逻辑
3. 在解析器模块中添加内容解析逻辑
4. 更新导出器以支持新消息类型的渲染

## 测试和调试

### 日志配置
项目使用loguru日志模块，配置在各个模块中：
```python
from wxManager.log import logger

logger.info("信息日志")
logger.error("错误日志")
logger.debug("调试日志")
```

### 数据文件路径
- **解密后的数据库**: 默认存储在 `{wxid}/db_storage/` 目录下（4.0版本）
- **用户信息**: `info.json` 文件包含用户基本信息
- **媒体文件**: 图片、视频等文件存储在对应子目录中

### 性能优化
- 使用多进程处理大量数据（`freeze_support()` 必要）
- 数据库查询使用索引优化
- 媒体文件处理支持并发解码

## Python版本兼容性说明

### 支持的版本范围
- **Python 3.10+**: 完全支持，推荐使用
- **Python 3.9**: 基本支持 (最低支持版本)
- **Python 3.8及以下**: 不支持

### 关键依赖版本要求
- `pywin32==308`: Windows平台必需，用于进程内存读取
- `psutil~=6.1.1`: 系统进程信息获取
- `pymem==1.14.0`: 内存操作
- `zstandard~=0.23.0`: 数据压缩解压（微信4.0）
- `pillow==11.0.0`: 图像处理
- `protobuf==4.25.1`: Protocol Buffers消息序列化
- `cryptography`: 加密解密功能
- `openpyxl==3.1.5`: Excel文件操作
- `aiofiles~=24.1.0`: 异步文件操作
- `pysilk-mod==1.6.4`: SILK音频格式处理

### 平台要求
- **操作系统**: Windows 10/11
- **不支持**: Windows 7、macOS、Linux
- **内存要求**: 建议4GB以上（处理大量聊天记录时）

## 常见问题

### 解密相关
- 如果出现 "未找到key" 错误，请重启微信后重试
- 解密失败通常是因为微信进程正在运行，请先关闭微信
- 支持多账户同时解密

### 导出相关
- 导出大量数据时建议使用SSD硬盘提高速度
- HTML导出支持引用消息跳转和合并转发展开
- 图片文件会自动解码并复制到输出目录

### 性能问题
- 处理大量聊天记录时内存占用较高
- 导出速度取决于数据量和硬件性能
- 建议分批次导出大量联系人数据

### 错误排查
1. 检查微信版本是否支持
2. 确认数据库文件完整性
3. 查看日志文件定位具体错误
4. 确认Python环境和依赖版本

## 安全和隐私

### 数据安全
- 所有数据处理均在本地进行
- 不会上传任何聊天记录到外部服务器
- 解密密钥仅从内存中读取，不进行持久化

### 使用限制
- 仅限个人聊天记录分析使用
- 禁止用于任何非法用途
- 遵守相关法律法规和微信用户协议

## AI功能集成

### MemoAI模块
项目集成了AI分析功能，支持：
- 基于ChatGLM3-6B的聊天记录分析
- FastAPI服务器提供API接口
- 支持文本嵌入和相似度计算
- 个人年度报告生成

### 使用方式
```bash
# 启动AI API服务器
python MemoAI/api_server.py
```

## 扩展开发

### 贡献指南
1. Fork 项目仓库
2. 创建功能分支
3. 提交代码变更
4. 创建Pull Request

### 代码规范
- 使用类型提示 (Type Hints)
- 遵循PEP 8代码风格
- 添加适当的文档字符串
- 编写单元测试

### 提交要求
- 确保代码通过现有测试
- 添加必要的测试用例
- 更新相关文档
- 保持向后兼容性