#!/usr/bin/env python3
"""
Start Medical Assistant MCP Server with LLM Integration
Instructions for setting up your OpenAI API key
"""

import os
import sys
import subprocess
from dotenv import load_dotenv


def check_openai_key():
    """Check if OpenAI API key is properly configured"""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key == "your_openai_api_key_here":
        return False, "Not configured"

    if not api_key.startswith("sk-"):
        return False, "Invalid format"

    return True, "Valid"


def main():
    print("🏥 Medical Assistant MCP Server - LLM Setup")
    print("=" * 50)

    # Check OpenAI configuration
    is_valid, status = check_openai_key()

    print(f"\n🔑 OpenAI API Key Status: {status}")

    if not is_valid:
        print("""
❌ OpenAI API Key not configured properly!

📝 To enable LLM features:

1. Edit your .env file:
   nano ../.env

2. Replace this line:
   OPENAI_API_KEY=your_openai_api_key_here
   
   With your real key:
   OPENAI_API_KEY=sk-your-actual-key-here

3. Save and restart the server

🔄 Alternative - Set temporarily for this session:
   export OPENAI_API_KEY="sk-your-key-here"
   python web_server.py

💡 Without OpenAI key, server will use hardcoded medical data (still works!)
        """)
    else:
        print("✅ OpenAI API Key configured correctly!")

    print(
        f"\n🚀 Starting server (LLM {'enabled' if is_valid else 'disabled - using fallback'})...")

    try:
        # Start the server
        subprocess.run([sys.executable, "web_server.py"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")


if __name__ == "__main__":
    main()
