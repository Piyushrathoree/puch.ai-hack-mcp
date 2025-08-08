#!/usr/bin/env python3
"""
Medical Assistant MCP Server - MVP Version
Simple medical guidance for Puch.ai Hackathon 2025

Start here: Basic MCP server with essential medical tools
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Simple MCP structure (no complex dependencies for MVP)
app = FastAPI(
    title="Medical Assistant MCP Server - MVP",
    description="Simple medical guidance through MCP",
    version="0.1.0"
)

# Enable CORS for Puch.ai integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- HARDCODED MEDICAL DATA (MVP Approach) ---
BASIC_MEDICINES = {
    "fever": {
        "medicine": "Paracetamol",
        "dose": "500mg every 6-8 hours",
        "max_daily": "4g (4000mg)",
        "warning": "Don't exceed maximum daily dose"
    },
    "headache": {
        "medicine": "Paracetamol or Ibuprofen",
        "dose": "Paracetamol: 500mg OR Ibuprofen: 200-400mg",
        "frequency": "every 6-8 hours",
        "warning": "Don't take both together"
    },
    "pain": {
        "medicine": "Ibuprofen",
        "dose": "200-400mg every 6-8 hours",
        "max_daily": "1200mg",
        "warning": "Take with food to avoid stomach upset"
    }
}

HOME_REMEDIES = {
    "fever": [
        "Rest and drink plenty of fluids",
        "Cool compress on forehead",
        "Light, loose clothing",
        "Room temperature bath"
    ],
    "cough": [
        "Honey and warm water",
        "Steam inhalation",
        "Gargle with salt water",
        "Stay hydrated"
    ],
    "headache": [
        "Rest in dark, quiet room",
        "Cold or warm compress",
        "Stay hydrated",
        "Gentle neck massage"
    ],
    "cold": [
        "Rest and sleep",
        "Warm fluids (tea, soup)",
        "Saline nasal rinse",
        "Humidifier or steam"
    ]
}

EMERGENCY_KEYWORDS = [
    "chest pain", "difficulty breathing", "unconscious",
    "severe bleeding", "stroke", "heart attack", "poisoning",
    "severe headache", "high fever above 103", "seizure"
]

# --- BASIC DATA MODELS ---


class MCPRequest(BaseModel):
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: str
    version: str = "0.1.0"

# --- SIMPLE MEDICAL LOGIC ---


def analyze_symptoms_simple(symptoms: str, age: str = "adult") -> Dict[str, Any]:
    """Simple symptom analysis - MVP version"""
    symptoms_lower = symptoms.lower()

    # Emergency check first
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in symptoms_lower:
            return {
                "triage_level": "emergency",
                "message": "🚨 EMERGENCY: Call 102/108 immediately or visit nearest hospital",
                "action": "seek_immediate_help",
                "disclaimer": "This is an emergency. Get professional medical help immediately."
            }

    # Basic triage logic
    if any(word in symptoms_lower for word in ["fever", "temperature"]):
        condition = "fever"
        triage = "self_care" if "mild" in symptoms_lower else "routine"
    elif any(word in symptoms_lower for word in ["headache", "head pain"]):
        condition = "headache"
        triage = "self_care"
    elif any(word in symptoms_lower for word in ["cough", "coughing"]):
        condition = "cough"
        triage = "self_care"
    elif any(word in symptoms_lower for word in ["cold", "runny nose", "sore throat"]):
        condition = "cold"
        triage = "self_care"
    else:
        condition = "general"
        triage = "routine"

    # Get suggestions
    medicine_info = BASIC_MEDICINES.get(condition, {})
    remedies = HOME_REMEDIES.get(
        condition, ["Rest", "Stay hydrated", "Monitor symptoms"])

    return {
        "triage_level": triage,
        "condition": condition,
        "medicine_suggestion": medicine_info,
        "home_remedies": remedies,
        "follow_up": "See a doctor if symptoms worsen or persist beyond 3 days",
        "disclaimer": "This is informational only. Consult a healthcare professional for medical advice."
    }


def get_medicine_suggestion(condition: str) -> Dict[str, Any]:
    """Get OTC medicine suggestion"""
    condition_lower = condition.lower()

    # Map common terms to our medicine database
    if any(word in condition_lower for word in ["fever", "temperature"]):
        key = "fever"
    elif any(word in condition_lower for word in ["headache", "head pain"]):
        key = "headache"
    elif any(word in condition_lower for word in ["pain", "ache"]):
        key = "pain"
    else:
        return {
            "message": "Please consult a pharmacist for specific medicine recommendations",
            "general_advice": "Only use medicines as directed on the package",
            "disclaimer": "This tool only suggests common OTC medicines for basic symptoms"
        }

    medicine_info = BASIC_MEDICINES.get(key, {})
    medicine_info["disclaimer"] = "Only use as directed. Consult pharmacist if unsure."
    return medicine_info


def get_home_remedies_simple(condition: str) -> Dict[str, Any]:
    """Get home remedies for condition"""
    condition_lower = condition.lower()

    # Find matching remedies
    remedies = []
    for key, remedy_list in HOME_REMEDIES.items():
        if key in condition_lower:
            remedies.extend(remedy_list)

    if not remedies:
        remedies = [
            "Rest and stay hydrated",
            "Monitor your symptoms",
            "Seek medical advice if symptoms worsen"
        ]

    return {
        "condition": condition,
        "remedies": remedies,
        "disclaimer": "Home remedies are not a substitute for professional medical advice",
        "warning": "Seek medical help if symptoms are severe or worsen"
    }

# --- API ENDPOINTS ---


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check"""
    return HealthResponse(timestamp=datetime.now().isoformat())


@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "name": "Medical Assistant MCP Server - MVP",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "mcp": "/mcp",
            "test": "/test"
        },
        "tools": ["analyze_symptoms", "suggest_medicine", "get_remedies"]
    }


@app.get("/test")
async def test_endpoint():
    """Quick test endpoint"""
    test_result = analyze_symptoms_simple("fever and headache", "adult")
    return {
        "test": "Medical MCP Tools",
        "sample_input": "fever and headache",
        "sample_output": test_result,
        "status": "working"
    }


@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest):
    """Main MCP interface - handles tool calls from Puch.ai"""
    try:
        method = request.method
        params = request.params or {}

        # Route to appropriate tool
        if method == "analyze_symptoms":
            symptoms = params.get("symptoms", "")
            age = params.get("age", "adult")
            result = analyze_symptoms_simple(symptoms, age)

        elif method == "suggest_medicine":
            condition = params.get("condition", "")
            result = get_medicine_suggestion(condition)

        elif method == "get_remedies":
            condition = params.get("condition", "")
            result = get_home_remedies_simple(condition)

        elif method == "list_tools":
            # MCP discovery - list available tools
            result = {
                "tools": [
                    {
                        "name": "analyze_symptoms",
                        "description": "Analyze symptoms and provide basic triage",
                        "parameters": {"symptoms": "string", "age": "string (optional)"}
                    },
                    {
                        "name": "suggest_medicine",
                        "description": "Suggest safe OTC medicines",
                        "parameters": {"condition": "string"}
                    },
                    {
                        "name": "get_remedies",
                        "description": "Get home remedies for common conditions",
                        "parameters": {"condition": "string"}
                    }
                ]
            }

        else:
            result = {"error": f"Unknown method: {method}"}

        return {
            "id": request.id,
            "result": result,
            "jsonrpc": "2.0"
        }

    except Exception as e:
        return {
            "id": request.id,
            "error": {"code": -32603, "message": str(e)},
            "jsonrpc": "2.0"
        }

# --- SIMPLE LOGGING ---


def log_session(session_data: Dict[str, Any]):
    """Simple session logging to JSON file"""
    try:
        log_file = "data/sessions.json"
        os.makedirs("data", exist_ok=True)

        # Load existing logs
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = json.load(f)
        else:
            logs = []

        # Add new session
        session_data["timestamp"] = datetime.now().isoformat()
        logs.append(session_data)

        # Keep only last 100 sessions (simple cleanup)
        logs = logs[-100:]

        # Save back
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)

    except Exception as e:
        print(f"Logging error: {e}")


if __name__ == "__main__":
    print("🏥 Starting Medical Assistant MCP Server - MVP")
    print("📍 Access at: http://localhost:8000")
    print("🔍 Health check: http://localhost:8000/health")
    print("🧪 Test endpoint: http://localhost:8000/test")
    print("⚡ MCP endpoint: http://localhost:8000/mcp")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
