#!/usr/bin/env python3
"""
Medical Assistant MCP Server - Quick Demo
Your prompt: "I have fever" - Complete response
"""

import json
import requests
import time
import subprocess
import os

def start_server():
    """Start the MCP server"""
    print("🚀 Starting Medical Assistant MCP Server...")
    server = subprocess.Popen(
        ["python", "web_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(3)
    return server

def call_mcp_tool(method, params):
    """Call an MCP tool"""
    payload = {
        "method": method,
        "params": params,
        "id": f"demo-{method}"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/mcp",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def demo_fever():
    """Demo: 'I have fever' - Complete response"""
    print("\n" + "="*60)
    print("🏥 MEDICAL ASSISTANT DEMO: 'I have fever'")
    print("="*60)
    
    # Your prompt: "I have fever"
    print("\n👤 User: 'I have fever'")
    print("\n🤖 Medical Assistant analyzing...")
    
    result = call_mcp_tool("analyze_symptoms", {
        "symptoms": "I have fever",
        "age": "adult"
    })
    
    if "result" in result:
        data = result["result"]
        
        print(f"\n📊 TRIAGE: {data.get('triage_level', 'unknown').upper()}")
        print(f"🎯 CONDITION: {data.get('condition', 'unknown').title()}")
        
        # Medicine suggestion
        if "medicine_suggestion" in data:
            med = data["medicine_suggestion"]
            print(f"\n💊 RECOMMENDED MEDICINE:")
            print(f"   • {med.get('medicine', 'N/A')}")
            print(f"   • Dose: {med.get('dose', 'N/A')}")
            print(f"   • Max daily: {med.get('max_daily', 'N/A')}")
            print(f"   • Warning: {med.get('warning', 'N/A')}")
        
        # Home remedies
        print(f"\n🏠 HOME REMEDIES:")
        for i, remedy in enumerate(data.get("home_remedies", [])[:3], 1):
            print(f"   {i}. {remedy}")
        
        # Warning signs
        print(f"\n⚠️ WARNING SIGNS:")
        for warning in data.get("warning_signs", []):
            print(f"   • {warning}")
        
        print(f"\n📋 FOLLOW-UP: {data.get('follow_up', 'N/A')}")
        
        # Show mode
        if "llm_error" in data:
            print(f"\n🤖 MODE: Fallback (hardcoded responses)")
        else:
            print(f"\n🤖 MODE: LLM-Powered (dynamic responses)")
        
        print(f"\n📝 DISCLAIMER: {data.get('disclaimer', 'N/A')}")
        
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    print("🏥 Medical Assistant MCP Server - Demo")
    print("Built for Puch.ai Hackathon 2025")
    
    server = start_server()
    
    try:
        # Test server
        health = requests.get("http://localhost:8000/health", timeout=5)
        if health.status_code == 200:
            print("✅ Server running!")
            demo_fever()
            
            print("\n" + "="*60)
            print("✅ DEMO COMPLETE!")
            print("🚀 Your MCP server is ready!")
            print("📍 Server: http://localhost:8000")
            print("🧪 Test page: http://localhost:8000/demo")
        else:
            print("❌ Server not responding")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    finally:
        server.terminate()
        print("\n🛑 Server stopped")
