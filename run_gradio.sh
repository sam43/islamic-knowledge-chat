#!/bin/bash

# Islamic AI Fine-tuning Gradio Launch Script

echo "🕌 Islamic AI Fine-tuning Platform"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "islamic_ai_env" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv islamic_ai_env
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source islamic_ai_env/bin/activate  # On Windows: islamic_ai_env\Scripts\activate

# Install/update requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OpenAI API key not found!"
    echo "   Set it with: export OPENAI_API_KEY='your-key-here'"
    echo "   Training features will be disabled without API key."
    echo ""
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs models scraped_content

# Launch Gradio app
echo "🚀 Launching Gradio interface..."
python launch_gradio.py
