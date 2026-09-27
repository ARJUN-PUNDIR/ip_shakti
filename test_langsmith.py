#!/usr/bin/env python3
"""
Test LangSmith Connection and Tracing
Run this script to verify your LangSmith API key and project tracing.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv(".env", override=True)

api_key = (os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY") or "").strip()
project = os.getenv("LANGSMITH_PROJECT") or os.getenv("LANGCHAIN_PROJECT") or "ip-sakti-sahayak"

print("==================================================")
print("🔍 LangSmith Tracing Diagnostics")
print("==================================================")
print(f"Project Name   : {project}")

if not api_key:
    print("❌ Status         : NO API KEY FOUND IN .env")
    print("\n👉 ACTION REQUIRED:")
    print("   Open your .env file and set:")
    print('   LANGSMITH_API_KEY="lsv2_pt_your_actual_key_here"')
    print('   LANGCHAIN_API_KEY="lsv2_pt_your_actual_key_here"')
    print("\n   Then re-run this script: ./venv/bin/python test_langsmith.py")
    sys.exit(1)

masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
print(f"Detected Key   : {masked_key} (len: {len(api_key)})")

# Set standard environment variables
os.environ["LANGSMITH_API_KEY"] = api_key
os.environ["LANGCHAIN_API_KEY"] = api_key
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGSMITH_PROJECT"] = project
os.environ["LANGCHAIN_PROJECT"] = project

try:
    from langsmith import Client, traceable
    client = Client(api_key=api_key)
    # Check connection
    print("⏳ Testing connection to https://api.smith.langchain.com...")
    # List projects to verify auth
    projects = list(client.list_projects(limit=3))
    print("✅ Authenticated successfully with LangSmith API!")
    
    # Send a real trace test
    @traceable(name="IP-SAKTI-Diagnostic-Test", run_type="chain")
    def run_diagnostic_trace():
        return {
            "system": "IP-SAKTI Sahayak",
            "status": "Tracing Active",
            "message": "Test span sent successfully from SIH prototype."
        }
    
    result = run_diagnostic_trace()
    print("✅ Test trace span emitted successfully!")
    print(f"\n🎉 Check your LangSmith dashboard now:")
    print(f"   👉 https://smith.langchain.com/o/default/projects/p/{project}")
    print("==================================================")
except Exception as e:
    print(f"❌ LangSmith Error: {e}")
    sys.exit(1)
