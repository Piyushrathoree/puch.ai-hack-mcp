#!/usr/bin/env python3
"""
Medical Assistant MCP Server - Web Interface
FastAPI wrapper for the medical MCP server

Built for Puch.ai Hackathon 2025
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

# Import our MCP server logic
from simple_mcp import handle_mcp_request, medical_server

# Create FastAPI app
app = FastAPI(
    title="Medical Assistant MCP Server",
    description="Simple medical guidance through MCP protocol",
    version="1.0.0"
)

# Enable CORS for Puch.ai integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API ENDPOINTS ---

@app.get("/")
async def root():
    """Root endpoint with server info"""
    return {
        "name": "Medical Assistant MCP Server",
        "version": "1.0.0",
        "status": "running",
        "description": "Simple medical guidance through MCP protocol",
        "endpoints": {
            "health": "/health",
            "mcp": "/mcp (POST)",
            "test": "/test",
            "docs": "/docs"
        },
        "available_tools": [
            "analyze_symptoms",
            "suggest_medicine", 
            "get_remedies",
            "find_chemists",
            "get_session_logs"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "mcp_server": "active",
            "medical_tools": "active",
            "session_logging": "active"
        }
    }

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Main MCP interface endpoint"""
    try:
        # Parse request body
        body = await request.body()
        if body:
            data = json.loads(body)
        else:
            raise HTTPException(status_code=400, detail="Empty request body")
        
        # Extract MCP request components
        method = data.get("method", "")
        params = data.get("params", {})
        request_id = data.get("id", f"req_{datetime.now().timestamp()}")
        
        if not method:
            return {
                "id": request_id,
                "error": {"code": -32601, "message": "Method required"},
                "jsonrpc": "2.0"
            }
        
        # Handle the MCP request
        result = handle_mcp_request(method, params)
        
        # Return MCP-compliant response
        return {
            "id": request_id,
            "result": result,
            "jsonrpc": "2.0"
        }
        
    except json.JSONDecodeError:
        return {
            "id": None,
            "error": {"code": -32700, "message": "Parse error"},
            "jsonrpc": "2.0"
        }
    except Exception as e:
        return {
            "id": request_id if 'request_id' in locals() else None,
            "error": {"code": -32603, "message": str(e)},
            "jsonrpc": "2.0"
        }

@app.get("/test")
async def test_endpoint():
    """Quick test endpoint to verify functionality"""
    test_cases = [
        {
            "name": "Basic Symptom Analysis",
            "method": "analyze_symptoms",
            "params": {"symptoms": "fever and headache", "age": "adult"}
        },
        {
            "name": "Medicine Suggestion",
            "method": "suggest_medicine", 
            "params": {"condition": "headache"}
        },
        {
            "name": "Home Remedies",
            "method": "get_remedies",
            "params": {"condition": "cold"}
        },
        {
            "name": "Emergency Detection",
            "method": "analyze_symptoms",
            "params": {"symptoms": "severe chest pain"}
        }
    ]
    
    results = {}
    for test in test_cases:
        try:
            result = handle_mcp_request(test["method"], test["params"])
            results[test["name"]] = {
                "status": "success",
                "result": result
            }
        except Exception as e:
            results[test["name"]] = {
                "status": "error", 
                "error": str(e)
            }
    
    return {
        "server": "Medical Assistant MCP Server",
        "test_timestamp": datetime.now().isoformat(),
        "test_results": results,
        "summary": f"Completed {len(test_cases)} tests"
    }

@app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    return handle_mcp_request("list_tools", {})

@app.get("/logs")
async def get_logs(limit: int = 10):
    """Get recent session logs"""
    return handle_mcp_request("get_session_logs", {"limit": limit})

# --- DEMO INTERFACE ---
@app.get("/demo", response_class=HTMLResponse)
async def demo_interface():
    """Simple demo interface for testing"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Medical Assistant MCP Server - Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .tool-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            input, textarea, select { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
            button { background-color: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
            button:hover { background-color: #2980b9; }
            .result { background-color: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 4px; white-space: pre-wrap; }
            .emergency { background-color: #e74c3c; color: white; }
            .disclaimer { background-color: #f39c12; color: white; padding: 10px; border-radius: 4px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 Medical Assistant MCP Server</h1>
            <div class="disclaimer">
                ⚠️ <strong>Medical Disclaimer:</strong> This is for informational purposes only. 
                Not a substitute for professional medical advice. For emergencies, call 102/108.
            </div>
            
            <div class="tool-section">
                <h3>🔍 Analyze Symptoms</h3>
                <textarea id="symptoms" placeholder="Describe your symptoms (e.g., fever and headache since 2 days)"></textarea>
                <select id="age">
                    <option value="adult">Adult</option>
                    <option value="child">Child</option>
                    <option value="elderly">Elderly</option>
                </select>
                <button onclick="analyzeSymptoms()">Analyze Symptoms</button>
                <div id="symptomsResult" class="result" style="display:none;"></div>
            </div>
            
            <div class="tool-section">
                <h3>💊 Medicine Suggestion</h3>
                <input type="text" id="condition" placeholder="Enter condition (e.g., headache, fever)">
                <button onclick="suggestMedicine()">Get Medicine Suggestion</button>
                <div id="medicineResult" class="result" style="display:none;"></div>
            </div>
            
            <div class="tool-section">
                <h3>🏠 Home Remedies</h3>
                <input type="text" id="remedyCondition" placeholder="Enter condition for home remedies">
                <button onclick="getRemedies()">Get Home Remedies</button>
                <div id="remediesResult" class="result" style="display:none;"></div>
            </div>
            
            <div class="tool-section">
                <h3>🏪 Find Chemists</h3>
                <input type="text" id="location" placeholder="Enter your location">
                <button onclick="findChemists()">Find Nearby Chemists</button>
                <div id="chemistsResult" class="result" style="display:none;"></div>
            </div>
        </div>
        
        <script>
            async function callMCP(method, params) {
                try {
                    const response = await fetch('/mcp', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            method: method,
                            params: params,
                            id: Date.now().toString()
                        })
                    });
                    return await response.json();
                } catch (error) {
                    return { error: { message: error.message } };
                }
            }
            
            async function analyzeSymptoms() {
                const symptoms = document.getElementById('symptoms').value;
                const age = document.getElementById('age').value;
                const resultDiv = document.getElementById('symptomsResult');
                
                if (!symptoms) {
                    alert('Please enter symptoms');
                    return;
                }
                
                const response = await callMCP('analyze_symptoms', { symptoms, age });
                
                if (response.result && response.result.triage_level === 'emergency') {
                    resultDiv.className = 'result emergency';
                } else {
                    resultDiv.className = 'result';
                }
                
                resultDiv.style.display = 'block';
                resultDiv.textContent = JSON.stringify(response.result || response.error, null, 2);
            }
            
            async function suggestMedicine() {
                const condition = document.getElementById('condition').value;
                const resultDiv = document.getElementById('medicineResult');
                
                if (!condition) {
                    alert('Please enter a condition');
                    return;
                }
                
                const response = await callMCP('suggest_medicine', { condition });
                resultDiv.style.display = 'block';
                resultDiv.textContent = JSON.stringify(response.result || response.error, null, 2);
            }
            
            async function getRemedies() {
                const condition = document.getElementById('remedyCondition').value;
                const resultDiv = document.getElementById('remediesResult');
                
                if (!condition) {
                    alert('Please enter a condition');
                    return;
                }
                
                const response = await callMCP('get_remedies', { condition });
                resultDiv.style.display = 'block';
                resultDiv.textContent = JSON.stringify(response.result || response.error, null, 2);
            }
            
            async function findChemists() {
                const location = document.getElementById('location').value;
                const resultDiv = document.getElementById('chemistsResult');
                
                if (!location) {
                    alert('Please enter a location');
                    return;
                }
                
                const response = await callMCP('find_chemists', { location });
                resultDiv.style.display = 'block';
                resultDiv.textContent = JSON.stringify(response.result || response.error, null, 2);
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# --- STARTUP ---
if __name__ == "__main__":
    print("🏥 Starting Medical Assistant MCP Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🔍 Health check: http://localhost:8000/health")
    print("🧪 Test endpoint: http://localhost:8000/test")
    print("🎮 Demo interface: http://localhost:8000/demo")
    print("⚡ MCP endpoint: http://localhost:8000/mcp")
    print("📚 API docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "web_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
