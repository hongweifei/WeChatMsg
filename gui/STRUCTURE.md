# GUI文件结构说明

## 目录结构

```
WeChatMsg/
├── start_gui.py              # 根目录快捷启动脚本
├── gui/                      # GUI模块根目录
│   ├── __init__.py           # GUI模块初始化
│   ├── gui_main.py           # GUI主程序入口
│   ├── run_gui.py            # GUI启动脚本（在gui目录内）
│   ├── controller.py         # 主控制器
│   ├── models/               # 数据模型层
│   │   ├── __init__.py
│   │   └── app_state.py      # 应用状态管理
│   └── views/                # 视图层
│       ├── __init__.py
│       ├── main_window.py    # 主窗口
│       ├── decrypt_tab.py    # 解密标签页
│       ├── contact_tab.py    # 联系人标签页
│       ├── export_tab.py     # 导出标签页
│       └── status_bar.py     # 状态栏
├── GUI_README.md             # GUI使用说明
└── GUI_STRUCTURE.md          # 本文件
```

## 启动方式

### 1. 推荐方式（根目录）
```bash
python start_gui.py
```

### 2. 直接启动主程序
```bash
python gui/gui_main.py
```

### 3. 通过gui目录内的脚本
```bash
cd gui
python run_gui.py
```

## 架构设计

### MVC架构
- **Model（模型）**: `gui/models/` - 数据和业务逻辑
- **View（视图）**: `gui/views/` - 用户界面组件
- **Controller（控制器）**: `gui/controller.py` - 协调模型和视图

### 核心组件

#### 1. 入口文件
- `start_gui.py`: 根目录快捷启动方式
- `gui/gui_main.py`: 主程序，创建应用和主窗口
- `gui/run_gui.py`: GUI目录内的启动脚本

#### 2. 控制器层
- `gui/controller.py`:
  - 连接视图和模型
  - 处理业务逻辑
  - 管理回调事件
  - 集成现有的wxManager和exporter模块

#### 3. 模型层
- `gui/models/app_state.py`:
  - 应用状态管理
  - 用户设置持久化
  - 数据模型定义

#### 4. 视图层
- `gui/views/main_window.py`: 主窗口和菜单
- `gui/views/decrypt_tab.py`: 数据库解密界面
- `gui/views/contact_tab.py`: 联系人管理界面
- `gui/views/export_tab.py`: 导出配置界面
- `gui/views/status_bar.py`: 状态栏组件

## 设计特点

### 1. 高维护性
- **模块化设计**: 每个功能模块独立，便于维护
- **清晰的职责分离**: 视图、控制器、模型各司其职
- **统一的编码规范**: 一致的命名和注释风格

### 2. 低耦合
- **事件驱动架构**: 使用回调机制解耦组件
- **依赖注入**: 控制器管理依赖关系
- **接口抽象**: 定义清晰的组件接口

### 3. 扩展性
- **插件化架构**: 易于添加新的导出格式
- **配置化设计**: 支持用户自定义设置
- **版本兼容**: 支持多个微信版本

## 与现有模块的集成

GUI完全基于现有的核心模块构建，无需额外依赖：

- **wxManager**: 数据库管理、联系人查询
- **exporter**: 多格式导出功能
- **decrypt**: 数据库解密功能

所有GUI操作最终都会调用这些现有模块的API。

## 配置文件

- `gui_settings.json`: 用户设置自动保存（运行时生成）
- 与项目的配置系统保持一致

## 线程安全

- 使用观察者模式确保UI线程安全
- 长时间操作在后台线程执行
- 通过回调机制更新UI状态
