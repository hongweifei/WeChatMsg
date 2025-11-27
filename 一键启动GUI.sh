#!/bin/bash

# WeChatMsg一键启动脚本 (Linux/macOS)
# 简化的启动脚本 - 主要功能已移至Python启动器

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_error() {
    echo -e "${RED}[错误] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[成功] $1${NC}"
}

print_info() {
    echo -e "${BLUE}[信息] $1${NC}"
}

# 检查Python环境
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        print_success "找到python3命令"
        return 0
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        print_success "找到python命令"
        return 0
    else
        print_error "未找到Python环境"
        echo
        echo "请先安装Python 3.9或更高版本:"
        echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
        echo "CentOS/RHEL: sudo yum install python3 python3-pip"
        echo "macOS: brew install python3"
        echo "或者从 https://www.python.org/downloads/ 下载"
        echo
        exit 1
    fi
}

# 检查项目文件
check_project() {
    if [ ! -f "gui/run_gui.py" ]; then
        print_error "未找到gui/run_gui.py，请确保在项目根目录运行"
        exit 1
    fi
}

# 主函数
main() {
    echo -e "${BLUE}========================================"
    echo -e "        WeChatMsg 一键启动器"
    echo -e "     微信聊天记录解析工具 v3.0"
    echo -e "========================================${NC}"
    echo

    check_python
    check_project

    # 运行Python启动器
    print_info "正在启动Python启动器..."
    echo
    $PYTHON_CMD gui/run_gui.py
}

# 处理中断信号
trap 'echo -e "\n${YELLOW}用户中断程序${NC}"; exit 1' INT

main