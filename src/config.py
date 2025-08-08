"""
Simple configuration for Medical MCP Server MVP
"""

import os
from typing import List

# Basic server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# API Keys (add when needed)
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

# Medical safety settings
EMERGENCY_KEYWORDS = [
    "chest pain", "difficulty breathing", "unconscious", 
    "severe bleeding", "stroke", "heart attack", "poisoning",
    "severe headache", "high fever above 103", "seizure",
    "suicide", "self harm", "overdose"
]

SAFE_OTC_MEDICINES = [
    "paracetamol", "acetaminophen", "ibuprofen", "aspirin",
    "oral rehydration salts", "ors", "antacid"
]

FORBIDDEN_KEYWORDS = [
    "antibiotic", "prescription", "steroid", "controlled substance",
    "schedule h", "rx only"
]

# Simple triage levels
TRIAGE_LEVELS = {
    "emergency": "Immediate medical attention required - Call 102/108",
    "urgent": "See a doctor within 24 hours", 
    "routine": "Schedule appointment with doctor within 1-2 weeks",
    "self_care": "Can be managed with self-care and monitoring"
}

# Data directories
DATA_DIR = "data"
SESSIONS_FILE = f"{DATA_DIR}/sessions.json"
MEDICINES_FILE = f"{DATA_DIR}/medicines.json"
REMEDIES_FILE = f"{DATA_DIR}/remedies.json"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)
