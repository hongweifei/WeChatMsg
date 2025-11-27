@echo off
chcp 65001 >nul
title WeChatMsg 一键启动

color 0A
title WeChatMsg - 微信聊天记录解析工具

set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :run_launcher
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto :run_launcher
)

echo [错误] 未找到Python环境
echo.
echo 请先安装Python 3.9或更高版本:
echo https://www.python.org/downloads/
echo.
echo 安装时请勾选"Add Python to PATH"选项
echo.
pause
exit /b 1

:run_launcher
if not exist "gui\run_gui.py" (
    echo [错误] 未找到gui\run_gui.py，请确保在项目根目录运行
    pause
    exit /b 1
)

%PYTHON_CMD% gui\run_gui.py