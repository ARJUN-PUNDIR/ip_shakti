#!/bin/bash
# ========================================================
# IP-SAKTI Sahayak — AWS EC2 One-Time Setup Script
# Run this on a fresh Ubuntu EC2 Instance
# ========================================================
set -e

echo "📦 1. Updating packages and installing Python..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv git curl

echo "📁 2. Setting up Python Virtual Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🔑 3. Checking .env file..."
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️ Please edit .env and paste your NVIDIA_API_KEY and LANGSMITH_API_KEY!"
fi

echo "🚀 4. Setting up background systemd service..."
cat << 'EOF' | sudo tee /etc/systemd/system/ipsakti.service
[Unit]
Description=IP-SAKTI Sahayak Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/sih26
ExecStart=/home/ubuntu/sih26/venv/bin/python /home/ubuntu/sih26/prototype/backend/server.py
Restart=always
RestartSec=5
Environment=PORT=8000
Environment=HOST=0.0.0.0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ipsakti
sudo systemctl restart ipsakti

echo "🌐 5. Setting up Nginx Reverse Proxy (Port 80 -> 8000)..."
sudo apt-get install -y nginx
cat << 'EOF' | sudo tee /etc/nginx/sites-available/default
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }
}
EOF

sudo nginx -t
sudo systemctl restart nginx

echo "========================================================"
echo "✅ Setup Complete!"
echo "Server is running as a systemd service (Port 8000)."
echo "Nginx reverse proxy is active (Port 80)."
echo "You can access your prototype directly at: http://<YOUR_EC2_PUBLIC_IP>"
echo "========================================================"
