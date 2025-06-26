#!/bin/bash

# Islamic AI Fine-Tuning Project Setup Script
# echo "🕌 Setting up Islamic AI Fine-Tuning Project..."

# # Create project directory
# mkdir -p ilm-ai-finetuning
# cd ilm-ai-finetuning

# # Create project structure
# mkdir -p {data,src,tests,config,logs,models}

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv ilm-ai-env

# Activate virtual environment (Linux/Mac)
source ilm-ai-env/bin/activate

# For Windows users, use: ilm-ai-env\Scripts\activate

echo "✅ Virtual environment created and activated"
echo "🔧 Project structure created successfully"

# Create requirements.txt file
cat > requirements.txt << 'EOF'
openai>=1.0.0
python-dotenv>=1.0.0
pandas>=2.0.0
jsonlines>=3.1.0
requests>=2.31.0
tqdm>=4.65.0
colorama>=0.4.6
tabulate>=0.9.0
EOF
# Set permissions
chmod +x setup.sh
# Install requirements
echo "📥 Installing Python packages..."
pip install -r requirements.txt

echo "✅ All packages installed successfully"
echo ""
echo "🎉 Setup complete! Next steps:"
echo "1. Add your OpenAI API key to config/.env"
echo "2. Run: python src/main.py"
echo "3. Follow the interactive prompts"