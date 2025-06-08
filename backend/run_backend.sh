#!/bin/bash

# 运行后端服务的脚本 (macOS/Linux)

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -e .

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "创建 .env 文件..."
    cp .env.example .env
    echo "请编辑 .env 文件，填入您的 AWS 凭证"
fi

# 运行后端服务
echo "启动后端服务..."
python -m src.agent.main

# 如果服务异常退出，保持终端窗口打开
echo "服务已停止。按任意键退出..."
read -n 1