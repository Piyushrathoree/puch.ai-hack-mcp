#!/bin/bash
# Quick setup script for Medical MCP Server MVP

echo "🏥 Setting up Medical MCP Server MVP..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "⚡ Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data

# Create basic .env file
echo "⚙️ Creating .env file..."
cat > .env << EOF
HOST=0.0.0.0
PORT=8000
DEBUG=true
GOOGLE_PLACES_API_KEY=your_api_key_here
EOF

echo ""
echo "✅ Setup complete! Next steps:"
echo ""
echo "1. Get your Google Places API key and update .env file"
echo "2. Start the server: python src/main.py"
echo "3. Test it: python test_mvp.py"
echo "4. Connect to Puch.ai using: http://localhost:8000/mcp"
echo ""
echo "🚀 Good luck with your MVP!"
