#!/bin/zsh
set -euo pipefail

SCRIPT_PATH="${0:A}"
SCRIPT_DIR="${SCRIPT_PATH:h}"
PROJECT_ROOT="${SCRIPT_DIR:h}"
APP_NAME="光谱训练矩阵启动台.app"
INSTALLED_APP="/Applications/$APP_NAME"

cd "$PROJECT_ROOT"

echo "光谱训练矩阵启动台：开始构建并安装"
echo "项目目录：$PROJECT_ROOT"
echo ""

./script/build_macos_launcher.sh install

echo ""
echo "已复制到：$INSTALLED_APP"
if [[ -d "$INSTALLED_APP" ]]; then
  /usr/bin/open -R "$INSTALLED_APP"
fi

echo ""
echo "完成。按回车键关闭窗口。"
read -r _ || true
