"""
Test script to verify all imports work correctly
"""

def test_imports():
    """Test all required imports"""
    import_tests = [
        ("gradio", "gradio"),
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("openai", "openai"), 
        ("colorama", "colorama"),
        ("tabulate", "tabulate"),
        ("pandas", "pandas"),
        ("pathlib", "pathlib"),
        ("json", "json"),
        ("os", "os"),
        ("time", "time"),
        ("datetime", "datetime")
    ]
    
    print("🧪 Testing imports...")
    print("=" * 40)
    
    failed_imports = []
    
    for package_name, import_name in import_tests:
        try:
            __import__(import_name)
            print(f"✅ {package_name:15} -> {import_name}")
        except ImportError as e:
            print(f"❌ {package_name:15} -> {import_name} : {e}")
            failed_imports.append((package_name, import_name))
    
    print("=" * 40)
    
    if failed_imports:
        print(f"❌ {len(failed_imports)} imports failed:")
        for pkg, imp in failed_imports:
            print(f"   - {pkg} ({imp})")
        print("\n📦 Install missing packages:")
        missing_packages = [pkg for pkg, _ in failed_imports if pkg not in ['pathlib', 'json', 'os', 'time', 'datetime']]
        if missing_packages:
            print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("🎉 All imports successful!")
        return True

if __name__ == "__main__":
    success = test_imports()
    if not success:
        exit(1)
    
    print("\n🚀 Ready to launch Gradio interface!")
    print("Run: python3 launch_gradio.py")
