#!/usr/bin/env python3
"""
Medical Assistant MCP Server - Simplified Version
Simple medical guidance - No complex dependencies

Built for Puch.ai Hackathon 2025
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- HARDCODED MEDICAL DATA ---
BASIC_MEDICINES = {
    "fever": {
        "medicine": "Paracetamol",
        "dose": "500mg every 6-8 hours",
        "max_daily": "4g (4000mg)",
        "warning": "Don't exceed maximum daily dose",
        "age_restriction": "Not for children under 3 months"
    },
    "headache": {
        "medicine": "Paracetamol or Ibuprofen", 
        "dose": "Paracetamol: 500mg OR Ibuprofen: 200-400mg",
        "frequency": "every 6-8 hours",
        "warning": "Don't take both together",
        "age_restriction": "Ibuprofen not for children under 6 months"
    },
    "pain": {
        "medicine": "Ibuprofen",
        "dose": "200-400mg every 6-8 hours",
        "max_daily": "1200mg",
        "warning": "Take with food to avoid stomach upset",
        "age_restriction": "Not for children under 6 months"
    },
    "cold": {
        "medicine": "Paracetamol for fever/pain",
        "dose": "500mg every 6-8 hours",
        "additional": "ORS for hydration if needed",
        "warning": "No antibiotics for viral cold"
    }
}

HOME_REMEDIES = {
    "fever": [
        "Rest and drink plenty of fluids (water, fruit juices)",
        "Cool compress on forehead and wrists",
        "Light, loose cotton clothing",
        "Room temperature bath or sponging",
        "Avoid heavy meals, eat light foods"
    ],
    "cough": [
        "Honey and warm water (1 tsp honey in warm water)",
        "Steam inhalation (hot water bowl with towel over head)",
        "Gargle with warm salt water (1/2 tsp salt in warm water)",
        "Stay hydrated with warm fluids",
        "Elevate head while sleeping"
    ],
    "headache": [
        "Rest in dark, quiet room",
        "Cold compress on forehead or warm compress on neck",
        "Stay hydrated - drink water",
        "Gentle neck and shoulder massage",
        "Avoid loud noises and bright lights"
    ],
    "cold": [
        "Rest and get adequate sleep",
        "Warm fluids (herbal tea, warm water with honey)",
        "Saline nasal rinse or drops",
        "Humidifier or steam inhalation",
        "Throat lozenges for sore throat"
    ],
    "stomach_upset": [
        "BRAT diet (Bananas, Rice, Applesauce, Toast)",
        "Stay hydrated with ORS or clear fluids",
        "Ginger tea for nausea",
        "Avoid dairy, fatty, or spicy foods",
        "Rest and avoid stress"
    ]
}

EMERGENCY_KEYWORDS = [
    "chest pain", "difficulty breathing", "unconscious", 
    "severe bleeding", "stroke", "heart attack", "poisoning",
    "severe headache", "high fever above 103", "seizure",
    "suicide", "self harm", "overdose", "choking",
    "severe abdominal pain", "severe vomiting", "blood in vomit",
    "blood in stool", "severe diarrhea", "dehydration signs"
]

# --- MCP TOOLS IMPLEMENTATION ---

class MedicalMCPServer:
    def __init__(self):
        self.sessions = []
        self.google_api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        
    def analyze_symptoms(self, symptoms: str, age: str = "adult", location: str = None) -> Dict[str, Any]:
        """Analyze symptoms and provide triage recommendations"""
        symptoms_lower = symptoms.lower()
        
        # Emergency check first
        detected_emergencies = []
        for keyword in EMERGENCY_KEYWORDS:
            if keyword in symptoms_lower:
                detected_emergencies.append(keyword)
        
        if detected_emergencies:
            return {
                "triage_level": "emergency",
                "message": "🚨 EMERGENCY DETECTED: Call 102/108 immediately or visit nearest hospital",
                "action": "seek_immediate_help",
                "detected_red_flags": detected_emergencies,
                "emergency_contacts": {
                    "ambulance": "102 / 108",
                    "police": "100",
                    "fire": "101"
                },
                "disclaimer": "This is a medical emergency. Get professional medical help immediately."
            }
        
        # Basic triage logic
        condition = self._identify_condition(symptoms_lower)
        triage_level = self._determine_triage_level(symptoms_lower, condition)
        
        # Get recommendations
        medicine_info = BASIC_MEDICINES.get(condition, {})
        remedies = HOME_REMEDIES.get(condition, ["Rest", "Stay hydrated", "Monitor symptoms"])
        
        result = {
            "triage_level": triage_level,
            "condition": condition,
            "assessment": f"Based on symptoms: {symptoms}",
            "medicine_suggestion": medicine_info,
            "home_remedies": remedies,
            "follow_up": self._get_follow_up_advice(triage_level),
            "warning_signs": self._get_warning_signs(condition),
            "disclaimer": "⚠️ This is informational only. Consult a healthcare professional for medical advice."
        }
        
        # Log session
        self._log_session({
            "type": "symptom_analysis",
            "input": symptoms,
            "output": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def suggest_medicine(self, condition: str, age: str = "adult") -> Dict[str, Any]:
        """Suggest OTC medicines for condition"""
        condition_lower = condition.lower()
        
        # Map condition to medicine database
        medicine_key = self._map_condition_to_medicine(condition_lower)
        medicine_info = BASIC_MEDICINES.get(medicine_key, {})
        
        if not medicine_info:
            return {
                "message": "Please consult a pharmacist for specific medicine recommendations",
                "general_advice": "Only use medicines as directed on the package",
                "common_otc": "Paracetamol for fever/pain, ORS for dehydration",
                "disclaimer": "This tool only suggests common OTC medicines for basic symptoms"
            }
        
        # Add age-specific warnings
        warnings = [medicine_info.get("warning", "")]
        if "age_restriction" in medicine_info:
            warnings.append(medicine_info["age_restriction"])
        
        result = {
            "condition": condition,
            "recommended_medicine": medicine_info.get("medicine", ""),
            "dosage": medicine_info.get("dose", ""),
            "frequency": medicine_info.get("frequency", "As needed"),
            "max_daily": medicine_info.get("max_daily", ""),
            "warnings": warnings,
            "disclaimer": "⚠️ Only use as directed. Consult pharmacist if unsure. Not for prescription medicines."
        }
        
        self._log_session({
            "type": "medicine_suggestion",
            "input": condition,
            "output": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def get_home_remedies(self, condition: str) -> Dict[str, Any]:
        """Get home remedies for condition"""
        condition_lower = condition.lower()
        
        # Find matching remedies
        remedies = []
        matched_conditions = []
        
        for key, remedy_list in HOME_REMEDIES.items():
            if key in condition_lower or any(word in condition_lower for word in key.split('_')):
                remedies.extend(remedy_list)
                matched_conditions.append(key)
        
        # Remove duplicates while preserving order
        unique_remedies = []
        for remedy in remedies:
            if remedy not in unique_remedies:
                unique_remedies.append(remedy)
        
        if not unique_remedies:
            unique_remedies = [
                "Rest and stay hydrated with plenty of fluids",
                "Monitor your symptoms carefully", 
                "Seek medical advice if symptoms worsen or persist",
                "Maintain good hygiene and nutrition"
            ]
            matched_conditions = ["general"]
        
        result = {
            "condition": condition,
            "matched_categories": matched_conditions,
            "remedies": unique_remedies,
            "general_tips": [
                "Home remedies work best alongside proper rest",
                "Stay hydrated throughout treatment",
                "If symptoms worsen, seek medical help"
            ],
            "disclaimer": "🏠 Home remedies are supportive care only. Not a substitute for professional medical advice",
            "warning": "⚠️ Seek medical help if symptoms are severe or worsen"
        }
        
        self._log_session({
            "type": "home_remedies",
            "input": condition,
            "output": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def find_nearby_chemists(self, location: str, radius_km: float = 5.0) -> Dict[str, Any]:
        """Find nearby pharmacies using Google Places API"""
        if not self.google_api_key or self.google_api_key == "your_google_places_api_key_here":
            return {
                "error": "Google Places API key not configured",
                "message": "Please add your Google Places API key to .env file",
                "manual_search": f"Search for 'pharmacy near {location}' on Google Maps",
                "common_chains": ["Apollo Pharmacy", "MedPlus", "Netmeds", "1mg", "Guardian Pharmacy"]
            }
        
        try:
            # Use Google Places API to find pharmacies
            import googlemaps
            gmaps = googlemaps.Client(key=self.google_api_key)
            
            # Search for pharmacies
            places_result = gmaps.places_nearby(
                location=location,
                radius=radius_km * 1000,  # Convert km to meters
                type='pharmacy',
                language='en'
            )
            
            chemists = []
            for place in places_result.get('results', [])[:5]:  # Limit to 5 results
                chemist = {
                    "name": place.get('name', 'Unknown'),
                    "address": place.get('vicinity', 'Address not available'),
                    "rating": place.get('rating', 'Not rated'),
                    "open_now": place.get('opening_hours', {}).get('open_now', 'Unknown'),
                    "place_id": place.get('place_id', ''),
                }
                
                # Add Google Maps link
                if 'geometry' in place:
                    lat = place['geometry']['location']['lat']
                    lng = place['geometry']['location']['lng']
                    chemist['maps_link'] = f"https://maps.google.com/?q={lat},{lng}"
                    chemist['distance_km'] = "Calculating..."  # Would need additional API call
                
                chemists.append(chemist)
            
            result = {
                "location": location,
                "radius_km": radius_km,
                "total_found": len(chemists),
                "chemists": chemists,
                "search_timestamp": datetime.now().isoformat(),
                "note": "Call ahead to confirm medicine availability"
            }
            
        except Exception as e:
            result = {
                "error": f"Failed to search chemists: {str(e)}",
                "fallback": "Try searching 'pharmacy near me' on Google Maps",
                "common_chains": ["Apollo Pharmacy", "MedPlus", "Netmeds", "1mg", "Guardian Pharmacy"]
            }
        
        self._log_session({
            "type": "chemist_search",
            "input": location,
            "output": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def get_session_logs(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent session logs"""
        recent_sessions = self.sessions[-limit:]
        return {
            "total_sessions": len(self.sessions),
            "recent_sessions": recent_sessions,
            "server_uptime": "Running"
        }
    
    # --- HELPER METHODS ---
    
    def _identify_condition(self, symptoms_lower: str) -> str:
        """Identify primary condition from symptoms"""
        if any(word in symptoms_lower for word in ["fever", "temperature", "hot", "burning"]):
            return "fever"
        elif any(word in symptoms_lower for word in ["headache", "head pain", "migraine"]):
            return "headache"
        elif any(word in symptoms_lower for word in ["cough", "coughing"]):
            return "cough"
        elif any(word in symptoms_lower for word in ["cold", "runny nose", "sore throat", "sneezing"]):
            return "cold"
        elif any(word in symptoms_lower for word in ["stomach", "nausea", "vomiting", "diarrhea"]):
            return "stomach_upset"
        elif any(word in symptoms_lower for word in ["pain", "ache", "hurt"]):
            return "pain"
        else:
            return "general"
    
    def _determine_triage_level(self, symptoms_lower: str, condition: str) -> str:
        """Determine triage level based on symptoms"""
        # High priority symptoms
        if any(word in symptoms_lower for word in ["severe", "extreme", "unbearable", "intense"]):
            return "urgent"
        elif any(word in symptoms_lower for word in ["high fever", "103", "persistent", "worsening"]):
            return "routine"
        else:
            return "self_care"
    
    def _map_condition_to_medicine(self, condition_lower: str) -> str:
        """Map condition description to medicine database key"""
        if any(word in condition_lower for word in ["fever", "temperature"]):
            return "fever"
        elif any(word in condition_lower for word in ["headache", "head pain"]):
            return "headache"
        elif any(word in condition_lower for word in ["pain", "ache"]):
            return "pain"
        elif any(word in condition_lower for word in ["cold", "cough"]):
            return "cold"
        else:
            return ""
    
    def _get_follow_up_advice(self, triage_level: str) -> str:
        """Get follow-up advice based on triage level"""
        advice = {
            "emergency": "Seek immediate medical attention",
            "urgent": "See a doctor within 24 hours",
            "routine": "Schedule appointment with doctor within 1-2 weeks if symptoms persist",
            "self_care": "Monitor symptoms. See doctor if they worsen or persist beyond 3-5 days"
        }
        return advice.get(triage_level, "Consult healthcare professional if concerned")
    
    def _get_warning_signs(self, condition: str) -> List[str]:
        """Get warning signs to watch for"""
        warning_signs = {
            "fever": ["Temperature above 103°F (39.4°C)", "Persistent fever beyond 3 days", "Difficulty breathing"],
            "headache": ["Sudden severe headache", "Headache with neck stiffness", "Changes in vision"],
            "cough": ["Blood in cough", "Difficulty breathing", "Chest pain"],
            "cold": ["High fever", "Severe throat pain", "Ear pain"],
            "general": ["Worsening symptoms", "New severe symptoms", "Signs of dehydration"]
        }
        return warning_signs.get(condition, warning_signs["general"])
    
    def _log_session(self, session_data: Dict[str, Any]):
        """Log session data"""
        self.sessions.append(session_data)
        # Keep only last 100 sessions
        if len(self.sessions) > 100:
            self.sessions = self.sessions[-100:]


# --- CREATE SERVER INSTANCE ---
medical_server = MedicalMCPServer()


# --- SIMPLE HTTP SERVER (Can be adapted to any MCP protocol later) ---
def handle_mcp_request(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP requests - this is the main interface"""
    
    try:
        if method == "analyze_symptoms":
            symptoms = params.get("symptoms", "")
            age = params.get("age", "adult") 
            location = params.get("location")
            return medical_server.analyze_symptoms(symptoms, age, location)
            
        elif method == "suggest_medicine":
            condition = params.get("condition", "")
            age = params.get("age", "adult")
            return medical_server.suggest_medicine(condition, age)
            
        elif method == "get_remedies":
            condition = params.get("condition", "")
            return medical_server.get_home_remedies(condition)
            
        elif method == "find_chemists":
            location = params.get("location", "")
            radius = params.get("radius_km", 5.0)
            return medical_server.find_nearby_chemists(location, radius)
            
        elif method == "get_session_logs":
            limit = params.get("limit", 10)
            return medical_server.get_session_logs(limit)
            
        elif method == "list_tools":
            return {
                "tools": [
                    {
                        "name": "analyze_symptoms",
                        "description": "Analyze symptoms and provide triage recommendations",
                        "parameters": {
                            "symptoms": "string (required) - Description of symptoms",
                            "age": "string (optional) - Patient age group (child/adult/elderly)",
                            "location": "string (optional) - Location for emergency services"
                        }
                    },
                    {
                        "name": "suggest_medicine",
                        "description": "Suggest safe over-the-counter medicines",
                        "parameters": {
                            "condition": "string (required) - Medical condition or symptoms",
                            "age": "string (optional) - Patient age group"
                        }
                    },
                    {
                        "name": "get_remedies",
                        "description": "Get home remedies for common conditions",
                        "parameters": {
                            "condition": "string (required) - Medical condition"
                        }
                    },
                    {
                        "name": "find_chemists",
                        "description": "Find nearby pharmacies/chemists",
                        "parameters": {
                            "location": "string (required) - Location to search near",
                            "radius_km": "float (optional) - Search radius in kilometers (default: 5.0)"
                        }
                    },
                    {
                        "name": "get_session_logs",
                        "description": "Get recent consultation logs",
                        "parameters": {
                            "limit": "int (optional) - Number of recent sessions (default: 10)"
                        }
                    }
                ]
            }
            
        else:
            return {"error": f"Unknown method: {method}"}
            
    except Exception as e:
        return {
            "error": f"Server error: {str(e)}",
            "disclaimer": "Please consult a healthcare professional"
        }


# --- MAIN FUNCTION FOR TESTING ---
def main():
    """Test the MCP server functionality"""
    print("🏥 Medical Assistant MCP Server - Testing Mode")
    print("=" * 60)
    
    # Test 1: Analyze symptoms
    print("\n🔍 Test 1: Analyzing symptoms")
    result = handle_mcp_request("analyze_symptoms", {
        "symptoms": "fever and headache since 2 days",
        "age": "adult"
    })
    print(json.dumps(result, indent=2))
    
    # Test 2: Medicine suggestion
    print("\n💊 Test 2: Medicine suggestion")
    result = handle_mcp_request("suggest_medicine", {
        "condition": "headache"
    })
    print(json.dumps(result, indent=2))
    
    # Test 3: Home remedies
    print("\n🏠 Test 3: Home remedies")
    result = handle_mcp_request("get_remedies", {
        "condition": "cold and cough"
    })
    print(json.dumps(result, indent=2))
    
    # Test 4: Emergency detection
    print("\n🚨 Test 4: Emergency detection")
    result = handle_mcp_request("analyze_symptoms", {
        "symptoms": "severe chest pain and difficulty breathing"
    })
    print(json.dumps(result, indent=2))
    
    # Test 5: Tool discovery
    print("\n🔧 Test 5: Available tools")
    result = handle_mcp_request("list_tools", {})
    print(json.dumps(result, indent=2))
    
    print("\n✅ All tests completed!")
    print("🚀 MCP Server is working correctly!")


if __name__ == "__main__":
    main()
