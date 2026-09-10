#!/bin/bash
# IP-SAKTI Sahayak Demo Launch Script
# Ministry of Ayush | SIH26045

cd "$(dirname "$0")"
export PYTHONPATH=prototype/backend
echo "=========================================================="
echo "🏛️ IP-SAKTI Sahayak — Ministry of Ayush (SIH26045)"
echo "🤖 LLM: NVIDIA Nemotron-3 Ultra (nvidia/nemotron-3-ultra-550b-a55b)"
echo "🌐 Starting Local Server on http://localhost:8000"
echo "=========================================================="
./venv/bin/python prototype/backend/server.py
