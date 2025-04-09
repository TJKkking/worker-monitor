#!/bin/bash

set -e

echo "[INFO] Installing Monitor on $(hostname)..."

# 安装基础依赖
echo "[INFO] Installing Python3 and pip..."
sudo apt update
sudo apt install -y python3 python3-pip git

# 克隆代码
echo "[INFO] Cloning from GitHub..."
MONITOR_DIR="/opt/worker-monitor"
sudo rm -rf "$MONITOR_DIR"
sudo git clone https://github.com/TJKkking/worker-monitor.git "$MONITOR_DIR"
cd "$MONITOR_DIR"

# 检查 peers.txt 是否存在
if [ ! -f "peers.txt" ]; then
  echo "[ERROR] peers.txt not found in $MONITOR_DIR"
  echo "Please create peers.txt with one IP per line (no blank lines or comments) before installing."
  exit 1
fi

# 创建 venv 虚拟环境
echo "[INFO] Creating virtual environment..."
python3 -m venv venv

# 安装依赖
echo "[INFO] Installing Python dependencies..."
./venv/bin/pip install -r requirements.txt

# 创建 systemd 服务文件
echo "[INFO] Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/worker-monitor.service"
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Monitor Service
After=network.target

[Service]
User=root
WorkingDirectory=$MONITOR_DIR
ExecStart=$MONITOR_DIR/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
echo "[INFO] Enabling and starting worker-monitor.service..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable worker-monitor
sudo systemctl restart worker-monitor

echo "[INFO] ✅ Monitor installed and running on port 8080!"
