"""
Launch script for the Gradio web interface
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_requirements():
    """Check if all required packages are installed"""
    # Package name -> import name mapping
    required_packages = {
        'gradio': 'gradio',
        'requests': 'requests', 
        'beautifulsoup4': 'bs4',  # This is the key fix!
        'openai': 'openai',
        'colorama': 'colorama',
        'tabulate': 'tabulate',
        'pandas': 'pandas'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name} found")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name} missing")
    
    if missing_packages:
        print("\n❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print("pip install " + " ".join(missing_packages))
        return False
    
    return True

def main():
    """Main launch function"""
    print("🕌 Islamic AI Fine-tuning Platform")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OpenAI API key not found!")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        print("   Training features will be disabled without API key.")
        print()
    
    # Import and launch Gradio app
    try:
        from gradio_app import create_gradio_interface
        
        print("🚀 Starting Gradio interface...")
        print("📱 The web interface will open in your browser")
        print("🌐 Local URL: http://localhost:7860")
        print("🛑 Press Ctrl+C to stop the server")
        print()
        
        interface = create_gradio_interface()
        interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=False,
            show_error=True
        )
        
    except Exception as e:
        print(f"❌ Failed to start Gradio interface: {e}")
        print(f"Error details: {type(e).__name__}: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()