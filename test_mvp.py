#!/usr/bin/env python3
"""
Quick test script for Medical MCP Server MVP
Run this to verify your server is working
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_basic_functionality():
    """Test basic MCP tools"""
    print("🧪 Testing basic MCP tools...")

    # Test analyze_symptoms
    test_data = {
        "method": "analyze_symptoms",
        "params": {"symptoms": "fever and headache", "age": "adult"},
        "id": "test-1"
    }

    response = requests.post(f"{BASE_URL}/mcp", json=test_data)
    print(f"Analyze Symptoms - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

    # Test suggest_medicine
    test_data = {
        "method": "suggest_medicine",
        "params": {"condition": "headache"},
        "id": "test-2"
    }

    response = requests.post(f"{BASE_URL}/mcp", json=test_data)
    print(f"Suggest Medicine - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

    # Test get_remedies
    test_data = {
        "method": "get_remedies",
        "params": {"condition": "cold"},
        "id": "test-3"
    }

    response = requests.post(f"{BASE_URL}/mcp", json=test_data)
    print(f"Get Remedies - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_emergency_detection():
    """Test emergency detection"""
    print("🚨 Testing emergency detection...")

    test_data = {
        "method": "analyze_symptoms",
        "params": {"symptoms": "severe chest pain and difficulty breathing"},
        "id": "test-emergency"
    }

    response = requests.post(f"{BASE_URL}/mcp", json=test_data)
    print(f"Emergency Test - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_tool_discovery():
    """Test MCP tool discovery"""
    print("🔍 Testing tool discovery...")

    test_data = {
        "method": "list_tools",
        "params": {},
        "id": "test-discovery"
    }

    response = requests.post(f"{BASE_URL}/mcp", json=test_data)
    print(f"Tool Discovery - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


if __name__ == "__main__":
    print("🏥 Medical MCP Server MVP - Test Suite")
    print("=" * 50)

    try:
        test_health()
        test_basic_functionality()
        test_emergency_detection()
        test_tool_discovery()

        print("✅ All tests completed!")
        print("🚀 Your MVP is working! Ready for Puch.ai integration.")

    except requests.exceptions.ConnectionError:
        print("❌ Server not running! Start it with: python src/main.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")
