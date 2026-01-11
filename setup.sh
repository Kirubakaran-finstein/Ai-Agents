#!/bin/bash

# Gemini Multi-Agent CLI System - Quick Setup Script

echo "🚀 Setting up Gemini Multi-Agent CLI System..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv gemini-system

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source gemini-system/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "⚠️  Please edit .env and add your GEMINI_API_KEY"
        echo "   Get your API key from: https://makersuite.google.com/app/apikey"
    else
        echo "⚠️  .env.example not found. Creating basic .env file..."
        echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
        echo "⚠️  Please edit .env and add your GEMINI_API_KEY"
    fi
else
    echo "✓ .env file already exists"
fi

# Create memory directory if it doesn't exist
mkdir -p memory

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GEMINI_API_KEY"
echo "2. Activate the virtual environment: source gemini-system/bin/activate"
echo "3. Run the system: python main.py"
echo ""
echo "For detailed instructions, see SETUP.md"
