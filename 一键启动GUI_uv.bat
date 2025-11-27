@echo off
chcp 65001 >nul
title WeChatMsg 一键启动 (UV版本)

color 0A
title WeChatMsg - 微信聊天记录解析工具 (UV版本)

set UV_CMD=
uv --version >nul 2>&1
if %errorlevel% equ 0 (
    set UV_CMD=uv
    goto :run_uv_launcher
)

echo [错误] 未找到uv环境
echo.
echo 请先安装uv工具:
echo https://docs.astral.sh/uv/getting-started/installation/
echo.
echo 安装方法:
echo 1. PowerShell (推荐):
echo    irm https://astral.sh/uv/install.ps1 ^| iex
echo.
echo 2. 或者下载安装包:
echo    https://github.com/astral-sh/uv/releases
echo.
pause
exit /b 1

:run_uv_launcher
if not exist "gui\run_gui.py" (
    echo [错误] 未找到gui\run_gui.py，请确保在项目根目录运行
    pause
    exit /b 1
)

echo [信息] 正在使用uv启动WeChatMsg...
echo.

%UV_CMD% run python gui\run_gui.py