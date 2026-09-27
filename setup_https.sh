#!/bin/bash
# ========================================================
# IP-SAKTI Sahayak — 1-Click Genuine HTTPS Setup
# Obtains a free Let's Encrypt SSL Certificate (🔒 Padlock)
# ========================================================
set -e

echo "🔍 1. Detecting your EC2 Public IP..."
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com || curl -s https://ifconfig.me || curl -s https://api.ipify.org)

if [ -z "$PUBLIC_IP" ]; then
    echo "❌ Could not auto-detect public IP. Please enter your EC2 Public IP manually:"
    read -r PUBLIC_IP
fi

DOMAIN="${PUBLIC_IP}.sslip.io"
echo "🌐 Your Free SSL Domain: https://${DOMAIN}"

echo "📦 2. Installing Certbot and Nginx SSL tools..."
sudo apt-get update -y
sudo apt-get install -y certbot python3-certbot-nginx curl

echo "⚙️ 3. Configuring Nginx for domain ${DOMAIN}..."
cat << EOF | sudo tee /etc/nginx/sites-available/default
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN};

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }
}
EOF

sudo nginx -t
sudo systemctl restart nginx

echo "🔒 4. Requesting Official Let's Encrypt SSL Certificate..."
sudo certbot --nginx -d "${DOMAIN}" --non-interactive --agree-tos --register-unsafely-without-email --redirect

echo "=========================================================="
echo "🎉 SUCCESS! Genuine HTTPS is now active!"
echo "🔒 Your Secure PPT Link: https://${DOMAIN}"
echo "Test in your browser: You will see the secure padlock icon!"
echo "=========================================================="
