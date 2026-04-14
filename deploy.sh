#!/bin/bash
# =============================================================
# skills-chat 一键部署脚本
# 服务器：Ubuntu，用户：ubuntu
# 运行方式：bash deploy.sh
# =============================================================
set -e

REPO="https://github.com/szynpcs/skills-chat.git"
APP_DIR="/home/ubuntu/skills-chat"
DASHSCOPE_API_KEY="sk-546f6b18b8744d54b89301882840fe70"

echo "======================================"
echo " skills-chat 部署开始"
echo "======================================"

# ── 1. 安装系统依赖 ───────────────────────────────────────────
echo "[1/6] 安装系统依赖..."
sudo apt-get update -q
sudo apt-get install -y -q git python3 python3-pip python3-venv nodejs npm nginx curl

# ── 2. 克隆 / 更新代码 ────────────────────────────────────────
echo "[2/6] 拉取代码..."
if [ -d "$APP_DIR" ]; then
  cd "$APP_DIR" && git pull
else
  git clone "$REPO" "$APP_DIR"
  cd "$APP_DIR"
fi

# ── 3. 配置后端 ───────────────────────────────────────────────
echo "[3/6] 配置 Python 后端..."
cd "$APP_DIR/backend"

# 写入 .env
cat > .env <<EOF
DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
RATE_LIMIT=20
EOF

# 创建虚拟环境并安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
deactivate

# ── 4. 构建前端 ───────────────────────────────────────────────
echo "[4/6] 构建前端..."
cd "$APP_DIR/frontend"
npm install --silent
npm run build

# ── 5. 配置 systemd 后端服务 ──────────────────────────────────
echo "[5/6] 配置系统服务..."
sudo tee /etc/systemd/system/skills-backend.service > /dev/null <<EOF
[Unit]
Description=Skills Chat FastAPI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=${APP_DIR}/backend
Environment="PATH=${APP_DIR}/backend/venv/bin"
ExecStart=${APP_DIR}/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable skills-backend
sudo systemctl restart skills-backend

# ── 6. 配置 Nginx ─────────────────────────────────────────────
echo "[6/6] 配置 Nginx..."
sudo tee /etc/nginx/sites-available/skills-chat > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    # 前端静态文件
    root ${APP_DIR}/frontend/dist;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        # SSE 流式响应支持
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
        chunked_transfer_encoding on;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/skills-chat /etc/nginx/sites-enabled/skills-chat
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx

# ── 完成 ──────────────────────────────────────────────────────
echo ""
echo "======================================"
echo " 部署完成！"
echo " 访问地址：http://118.195.195.46"
echo " 后端健康检查：http://118.195.195.46/api/health"
echo "======================================"
