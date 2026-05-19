#!/bin/bash
# ============================================================
# AI 心理咨询助手 - 内测一键启动脚本
# 用法: bash start_test.sh
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "========================================"
echo "  AI 心理咨询助手 - 内测启动"
echo "========================================"

# ---- 1. 检查依赖 ----
echo ""
echo "[1/4] 检查依赖..."

if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3.11+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ 未找到 node，请先安装 Node.js 18+"
    exit 1
fi

echo "  ✓ python3: $(python3 --version)"
echo "  ✓ node:    $(node --version)"

# ---- 2. 安装依赖 ----
echo ""
echo "[2/4] 安装依赖..."

cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
echo "  ✓ 后端依赖已就绪"

cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    npm install --silent
fi
echo "  ✓ 前端依赖已就绪"

# ---- 3. 构建前端 ----
echo ""
echo "[3/4] 构建前端 H5..."

cd "$FRONTEND_DIR"
npm run build:h5
echo "  ✓ 前端构建完成 → $FRONTEND_DIR/dist/build/h5"

# ---- 4. 启动后端 ----
echo ""
echo "[4/4] 启动后端服务..."
echo ""

cd "$BACKEND_DIR"
source venv/bin/activate

# 确保 .env 存在
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  ⚠ 已从 .env.example 创建 .env，请编辑填入 DEEPSEEK_API_KEY"
fi

echo "========================================"
echo "  服务启动中..."
echo ""
echo "  测试账号（游客端自动创建，无需手动登录）："
echo "    游客/H5：  打开首页 → 点「微信一键登录」→ 自动生成账号"
echo ""
echo "  管理后台测试账号："
echo "    超级管理员：admin / admin123456"
echo "    测试咨询师：counselor_test / test123456"
echo ""
echo "  本地访问：http://localhost:8000"
echo "  外网访问：用 ngrok/cloudflared 暴露 8000 端口"
echo "    ngrok:    ngrok http 8000"
echo "    cloudfl:  cloudflared tunnel --url http://localhost:8000"
echo "========================================"

exec uvicorn main:app --host 0.0.0.0 --port 8000
