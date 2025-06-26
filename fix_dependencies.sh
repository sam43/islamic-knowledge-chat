#!/bin/bash

echo "🔧 Fixing Dependencies for Islamic AI Fine-tuning"
echo "================================================"

# Make sure we're in the right environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected"
    echo "   Consider activating your virtual environment first"
fi

# Install/reinstall all required packages
echo "📦 Installing required packages..."

pip install --upgrade pip

# Install packages one by one with verbose output
packages=(
    "colorama>=0.4.4"
    "tabulate>=0.9.0" 
    "openai>=1.0.0"
    "gradio>=4.0.0"
    "requests>=2.28.0"
    "beautifulsoup4>=4.11.0"
    "pandas>=1.5.0"
    "lxml"  # Additional parser for BeautifulSoup
)

for package in "${packages[@]}"; do
    echo "Installing $package..."
    pip install "$package"
done

echo ""
echo "🧪 Testing imports..."

# Test each import
python3 -c "
import sys
packages = {
    'gradio': 'gradio',
    'requests': 'requests', 
    'beautifulsoup4': 'bs4',
    'openai': 'openai',
    'colorama': 'colorama',
    'tabulate': 'tabulate',
    'pandas': 'pandas'
}

all_good = True
for pkg_name, import_name in packages.items():
    try:
        __import__(import_name)
        print(f'✅ {pkg_name} -> {import_name}')
    except ImportError as e:
        print(f'❌ {pkg_name} -> {import_name}: {e}')
        all_good = False

if all_good:
    print('\n🎉 All packages imported successfully!')
else:
    print('\n❌ Some packages failed to import')
    sys.exit(1)
"

echo ""
echo "✅ Dependency fix complete!"
echo "🚀 Try running: python3 launch_gradio.py"
