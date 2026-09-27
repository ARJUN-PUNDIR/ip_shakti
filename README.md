# 🏛️ IP-SAKTI Sahayak (SIH26045)
> **AI-Powered Multi-Agent Regulatory & IPR Intelligence Engine for the Ministry of Ayush, Government of India**

---

## 📌 Overview
**IP-SAKTI Sahayak** is an end-to-end statutory reasoning and regulatory compliance platform designed to safeguard Traditional Knowledge (TK) while unlocking ethical patenting for Ayush researchers and manufacturers.

### Key Capabilities:
- **Dual Jurisdictions**:
  - **National (India)**: Indian Patent Act 1970 (Sec 3p/3e/3d), Biological Diversity Act (Sec 6/NBA Form 3), Drugs & Cosmetics Rules 158-B, and FSSAI Ayurveda Aahara 2022.
  - **International**: WIPO GRATK Treaty 2024, CBD Nagoya Protocol ABS, EU EMA/THMPD (Directive 2004/24/EC), and US FDA Botanical Drug Guidance.
- **LLM Engine**: Powered by **NVIDIA Nemotron NIM** (`nvidia/nemotron-3-ultra-550b-a55b` & `nvidia/nemotron-3.5-lightning-30b-a3b`).
- **Observability**: Live multi-agent tracing via **LangSmith** under project `ip-sakti-sahayak`.
- **Statutory Document Synthesis**: Generates official Form 2 Patent Complete Specifications and NBA Form III approvals.

---

## 🚀 Quick Start (Local)

### 1. Clone Repository
```bash
git clone https://github.com/ARJUN-PUNDIR/ip_shakti.git
cd ip_shakti
```

### 2. Setup Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure `.env`
Copy the template and fill in your keys:
```bash
cp .env.example .env
```

### 4. Run Server
```bash
python prototype/backend/server.py
# Or use the launcher:
./run_demo.sh
```
Open **http://localhost:8000** in your browser.

---

## ☁️ Deployment on AWS EC2

Run the automated 1-line setup on an Ubuntu EC2 instance:
```bash
git clone https://github.com/ARJUN-PUNDIR/ip_shakti.git sih26
cd sih26
./deploy_ec2.sh
```

---

## 🛠️ Tech Stack
- **Backend**: FastAPI, Uvicorn, Python 3.11+
- **Agent Orchestration**: Multi-Agent StateGraph Engine with parallel fan-out/fan-in
- **Observability**: LangSmith Tracing (`@traceable`)
- **LLM NIM APIs**: NVIDIA Nemotron-3 Ultra 550B / Nemotron-3.5 Lightning 30B
- **Deployment**: AWS EC2, Nginx Reverse Proxy, Systemd, Docker
