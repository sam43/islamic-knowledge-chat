"""
Launch script for the Gradio web interface
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Main launch function for enhanced interface"""
    print("🕌 Enhanced Islamic AI Fine-tuning Platform")
    print("=" * 50)
    print("🤖 Features: AI-powered content filtering & smart Q&A extraction")
    print()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OpenAI API key not found!")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        print("   Training features will be disabled without API key.")
        print()
    
    # Import and launch Enhanced Gradio app
    try:
        from gradio_app import create_gradio_interface
        
        print("🚀 Starting Enhanced Gradio interface...")
        print("🤖 AI-powered content filtering enabled")
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
        print(f"❌ Failed to start Enhanced Gradio interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()