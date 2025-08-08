#!/usr/bin/env python3
"""
Medical Assistant MCP Server - Interactive Demo
Shows both LLM-powered and fallback modes
"""

import json
import requests
import time
import subprocess
import os
from typing import Dict, Any


class MedicalAssistantDemo:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.server_process = None

    def start_server(self):
        """Start the MCP server"""
        print("🚀 Starting Medical Assistant MCP Server...")
        self.server_process = subprocess.Popen(
            ["python", "web_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(3)  # Give server time to start

        # Test if server is running
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Server started successfully!")
                return True
        except:
            pass
        print("❌ Failed to start server")
        return False

    def stop_server(self):
        """Stop the MCP server"""
        if self.server_process:
            self.server_process.terminate()
            print("🛑 Server stopped")

    def call_mcp_tool(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool"""
        payload = {
            "method": method,
            "params": params,
            "id": f"demo-{method}"
        }

        try:
            response = requests.post(
                f"{self.base_url}/mcp",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=10
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def demo_fever_scenario(self):
        """Demo: User says 'I have fever'"""
        print("\n" + "="*60)
        print("🏥 DEMO: Medical Assistant - 'I have fever'")
        print("="*60)

        # Analyze symptoms
        print("\n🔍 Analyzing symptoms...")
        result = self.call_mcp_tool("analyze_symptoms", {
            "symptoms": "I have fever",
            "age": "adult"
        })

        if "result" in result:
            data = result["result"]
            print(
                f"📊 Triage Level: {data.get('triage_level', 'unknown').upper()}")
            print(f"🎯 Condition: {data.get('condition', 'unknown').title()}")
            print(f"📝 Assessment: {data.get('assessment', 'N/A')}")

            # Show medicine suggestions
            if "medicine_suggestion" in data:
                med = data["medicine_suggestion"]
                print(f"\n💊 Recommended Medicine:")
                print(f"   Medicine: {med.get('medicine', 'N/A')}")
                print(f"   Dose: {med.get('dose', 'N/A')}")
                print(f"   Warning: {med.get('warning', 'N/A')}")

            # Show OTC medicines (new LLM format)
            if "otc_medicines" in data:
                print(f"\n💊 OTC Medicines:")
                for med in data["otc_medicines"]:
                    print(
                        f"   • {med.get('name', 'N/A')} - {med.get('dose', 'N/A')}")

            # Show home remedies
            if "home_remedies" in data:
                print(f"\n🏠 Home Remedies:")
                for remedy in data["home_remedies"][:3]:  # Show first 3
                    print(f"   • {remedy}")

            print(f"\n⚠️ Warning Signs to Watch:")
            for warning in data.get("warning_signs", [])[:2]:
                print(f"   • {warning}")

            print(f"\n📋 Follow-up: {data.get('follow_up', 'N/A')}")

            # Show if LLM was used or fallback
            if "llm_error" in data:
                print(f"\n🤖 Mode: Fallback (LLM unavailable)")
                print(f"   Reason: {data['llm_error'][:50]}...")
            else:
                print(f"\n🤖 Mode: LLM-Powered")

        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

    def demo_medicine_suggestion(self):
        """Demo: Medicine suggestion for specific condition"""
        print("\n" + "="*60)
        print("💊 DEMO: Medicine Suggestion - 'headache'")
        print("="*60)

        result = self.call_mcp_tool("suggest_medicine", {
            "condition": "headache",
            "age": "adult"
        })

        if "result" in result:
            data = result["result"]
            print(f"🎯 Condition: {data.get('condition', 'N/A')}")

            if "recommended_medicine" in data:
                print(
                    f"💊 Recommended: {data.get('recommended_medicine', 'N/A')}")
                print(f"📏 Dosage: {data.get('dosage', 'N/A')}")
                print(f"⏰ Frequency: {data.get('frequency', 'N/A')}")

                warnings = data.get("warnings", [])
                if warnings:
                    print(f"⚠️ Warnings:")
                    for warning in warnings:
                        print(f"   • {warning}")

            # New LLM format
            if "medicines" in data:
                print(f"💊 Suggested Medicines:")
                for med in data["medicines"]:
                    print(
                        f"   • {med.get('name', 'N/A')} - {med.get('dose', 'N/A')}")
                    if med.get('notes'):
                        print(f"     Notes: {med['notes']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

    def demo_home_remedies(self):
        """Demo: Home remedies"""
        print("\n" + "="*60)
        print("🏠 DEMO: Home Remedies - 'cold and cough'")
        print("="*60)

        result = self.call_mcp_tool("get_remedies", {
            "condition": "cold and cough"
        })

        if "result" in result:
            data = result["result"]
            print(f"🎯 Condition: {data.get('condition', 'N/A')}")

            remedies = data.get("remedies", [])
            print(f"🏠 Home Remedies:")
            for i, remedy in enumerate(remedies[:4], 1):  # Show first 4
                print(f"   {i}. {remedy}")

            tips = data.get("general_tips", [])
            if tips:
                print(f"\n💡 General Tips:")
                for tip in tips:
                    print(f"   • {tip}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

    def demo_emergency_detection(self):
        """Demo: Emergency detection"""
        print("\n" + "="*60)
        print("🚨 DEMO: Emergency Detection - 'chest pain'")
        print("="*60)

        result = self.call_mcp_tool("analyze_symptoms", {
            "symptoms": "severe chest pain and difficulty breathing",
            "age": "adult"
        })

        if "result" in result:
            data = result["result"]
            triage = data.get('triage_level', 'unknown')

            if triage == "emergency":
                print("🚨 EMERGENCY DETECTED!")
                print(f"📞 Action: {data.get('action', 'N/A')}")
                print(
                    f"🔴 Red Flags: {', '.join(data.get('detected_red_flags', []))}")

                contacts = data.get('emergency_contacts', {})
                print(f"📱 Emergency Contacts:")
                for service, number in contacts.items():
                    print(f"   {service.title()}: {number}")

            print(f"\n⚠️ {data.get('disclaimer', 'N/A')}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

    def show_available_tools(self):
        """Show available MCP tools"""
        print("\n" + "="*60)
        print("🔧 AVAILABLE MCP TOOLS")
        print("="*60)

        result = self.call_mcp_tool("list_tools", {})

        if "result" in result and "tools" in result["result"]:
            tools = result["result"]["tools"]
            for i, tool in enumerate(tools, 1):
                print(f"\n{i}. {tool['name']}")
                print(f"   Description: {tool['description']}")
                params = tool.get('parameters', {})
                if params:
                    print(f"   Parameters:")
                    for param, desc in params.items():
                        print(f"     • {param}: {desc}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

    def run_complete_demo(self):
        """Run the complete demo"""
        print("🏥 Medical Assistant MCP Server - Complete Demo")
        print("Built for Puch.ai Hackathon 2025")
        print("=" * 60)

        if not self.start_server():
            print("❌ Could not start server. Please check configuration.")
            return

        try:
            # Show available tools
            self.show_available_tools()

            # Demo scenarios
            self.demo_fever_scenario()
            self.demo_medicine_suggestion()
            self.demo_home_remedies()
            self.demo_emergency_detection()

            print("\n" + "="*60)
            print("✅ DEMO COMPLETE!")
            print("="*60)
            print("🚀 Your MCP server is ready for Puch.ai integration!")
            print("📍 Server URL: http://localhost:8000")
            print("🧪 Test page: http://localhost:8000/demo")
            print("📚 API docs: http://localhost:8000/docs")

            print("\n💡 To use with OpenAI LLM:")
            print("   1. Add your OpenAI API key to .env:")
            print("      OPENAI_API_KEY=sk-your-key-here")
            print("   2. Restart the server")
            print("   3. Responses will be dynamically generated!")

        finally:
            input("\nPress Enter to stop the server...")
            self.stop_server()


if __name__ == "__main__":
    demo = MedicalAssistantDemo()
    demo.run_complete_demo()
