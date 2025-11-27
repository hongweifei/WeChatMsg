#!/bin/bash

# WeChatMsg一键启动脚本 (UV版本 - Linux/macOS)
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

# 检查uv环境
check_uv() {
    if command -v uv &> /dev/null; then
        UV_CMD="uv"
        print_success "找到uv命令"
        return 0
    else
        print_error "未找到uv环境"
        echo
        echo "请先安装uv工具:"
        echo "Ubuntu/Debian: curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo "CentOS/RHEL: curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo "macOS: brew install uv"
        echo "或者从 https://docs.astral.sh/uv/getting-started/installation/ 下载"
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
    echo -e "        WeChatMsg 一键启动器 (UV版本)"
    echo -e "     微信聊天记录解析工具 v3.0"
    echo -e "========================================${NC}"
    echo

    check_uv
    check_project

    # 运行Python启动器
    print_info "正在使用uv启动Python启动器..."
    echo
    $UV_CMD run python gui/run_gui.py
}

# 处理中断信号
trap 'echo -e "\n${YELLOW}用户中断程序${NC}"; exit 1' INT

main