#!/bin/bash
# ========================================================
# IP-SAKTI Sahayak — Fast 1-Command Update Script for EC2
# Run this on your EC2 whenever you push new changes to GitHub
# ========================================================
set -e

echo "🔄 1. Pulling latest changes from GitHub..."
git pull origin main || git pull origin master

echo "📦 2. Updating Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo "🔁 3. Restarting server service..."
sudo systemctl restart ipsakti

echo "========================================================"
echo "✅ Update successful! Your AWS EC2 is now running latest code."
echo "Check live logs: sudo journalctl -u ipsakti -f"
echo "========================================================"
