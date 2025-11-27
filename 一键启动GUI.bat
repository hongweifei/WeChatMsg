@echo off
chcp 65001 >nul
title WeChatMsg 一键启动

:: 设置控制台颜色
color 0A
title WeChatMsg - 微信聊天记录解析工具

:: 显示欢迎信息
cls
echo ========================================
echo        WeChatMsg 一键启动器
echo     微信聊天记录解析工具 v3.0
echo ========================================
echo.

:: 检查Python环境
echo [1/4] 检查Python环境...

:: 首先尝试python命令
set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo [成功] 找到python命令
    goto :python_found
)

echo [警告] python命令不可用，尝试py命令...

:: 尝试py命令
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    echo [成功] 找到py命令
    goto :python_found
)

:: 如果都不可用，显示详细信息
echo [错误] 未找到Python环境
echo.
echo 正在检查Python安装情况...
echo.

echo 检查python命令：
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo python命令存在但可能无法正常执行
    where python
) else (
    echo python命令不存在
)

echo.
echo 检查py命令：
where py >nul 2>&1
if %errorlevel% equ 0 (
    echo py命令存在但可能无法正常执行
    where py
) else (
    echo py命令不存在
)

echo.
echo 请先安装Python 3.10或更高版本:
echo https://www.python.org/downloads/
echo.
echo 安装时请勾选"Add Python to PATH"选项
echo.
pause
exit /b 1

:python_found
:: 获取Python版本信息
for /f "tokens=*" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [成功] Python版本: %PYTHON_VERSION% (使用 %PYTHON_CMD% 命令)

:: 检查项目文件
echo [2/4] 检查项目文件...
if not exist "gui/run_gui.py" (
    echo [错误] 未找到run_gui.py，请确保在项目根目录运行
    pause
    exit /b 1
)
echo [成功] 项目文件检查通过

:: 检查依赖包
echo [3/4] 检查依赖包...
%PYTHON_CMD% -c "import wxManager" >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 检测到缺少依赖包，正在自动安装...
    echo.

    :: 尝试安装依赖
    if exist "requirements.txt" (
        :: 根据Python命令选择对应的pip命令
        if "%PYTHON_CMD%"=="py" (
            py -m pip install -r requirements.txt
        ) else (
            pip install -r requirements.txt
        )
    ) else (
        echo [错误] 未找到requirements.txt文件
        pause
        exit /b 1
    )

    :: 再次检查
    %PYTHON_CMD% -c "import wxManager" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [错误] 依赖包安装失败，请手动运行:
        if "%PYTHON_CMD%"=="py" (
            echo py -m pip install -r requirements.txt
        ) else (
            echo pip install -r requirements.txt
        )
        pause
        exit /b 1
    )
    echo [成功] 依赖包安装完成
) else (
    echo [成功] 依赖包检查通过
)

:: 显示使用提示
echo [4/4] 准备启动...
echo.
echo ========================================
echo               重要提示
echo ========================================
echo 1. 请确保微信客户端正在运行
echo 2. 请确保有足够的磁盘空间
echo 3. 请遵守相关法律法规
echo 4. 仅限个人聊天记录分析使用
echo ========================================
echo.

:: 启动GUI
echo 正在启动GUI界面...
echo.

%PYTHON_CMD% gui/run_gui.py

:: 处理退出情况
if %errorlevel% neq 0 (
    echo.
    echo [错误] 程序异常退出
    echo.
    echo 可能的原因:
    echo - Python版本不兼容 (需要3.10+)
    echo - 缺少必要的依赖包
    echo - 微信客户端未运行
    echo - 权限不足
    echo.
)

echo.
echo 感谢使用WeChatMsg！
pause